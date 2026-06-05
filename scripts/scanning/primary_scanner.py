#!/usr/bin/env python3
"""
primary_scanner.py — Primary-Source Alpha Scanner

Scans what companies file THEMSELVES on SEC EDGAR — before news reports.
Extracts partnership counterparties, contract awards, and earnings call
mentions of downstream partners directly from the raw SEC filings.

Sources:
  - 8-K Item 1.01: Entry into Material Definitive Agreement (partnerships)
  - 8-K Item 2.02: Earnings call transcripts (CEO mentions partners)
  - 8-K Item 7.01: Regulation FD (material press releases)
  - 8-K Item 5.02: Management changes (insider movement signals)

Usage:
    python3 backend/primary_scanner.py                         # scan watchlist
    python3 backend/primary_scanner.py --tickers NVDA PLTR     # specific
    python3 backend/primary_scanner.py --days 30               # lookback
    python3 backend/primary_scanner.py --json --deep           # JSON + full text
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from typing import Optional

import requests
from bs4 import BeautifulSoup

USER_AGENT = "NoFomo Research (research@nofomo.app)"
HEADERS = {"User-Agent": USER_AGENT, "Accept": "application/json"}

# ─── Watchlist (same as deal_scanner) ─────────────────────────────────────

WATCHLIST = {
    "NVDA": "NVIDIA", "AMD": "AMD", "AVGO": "Broadcom", "MRVL": "Marvell",
    "MU": "Micron", "TSM": "TSMC", "INTC": "Intel",
    "MSFT": "Microsoft", "AMZN": "Amazon", "GOOGL": "Alphabet/Google",
    "META": "Meta", "AAPL": "Apple", "ORCL": "Oracle", "CRM": "Salesforce",
    "NOW": "ServiceNow", "SNOW": "Snowflake", "IBM": "IBM",
    "TSLA": "Tesla", "PLTR": "Palantir", "LLY": "Eli Lilly",
}

# 8-K items that carry alpha signals
ALPHA_ITEMS = {
    "1.01": "Material Definitive Agreement",      # Partnerships, contracts
    "2.02": "Results of Operations",               # Earnings (CEO mentions partners)
    "7.01": "Regulation FD Disclosure",            # Press releases filed as 8-K
    "8.01": "Other Events",                        # Catch-all for material events
}

# Cached CIK mapping
_CIK_MAP: dict[str, str] = {}

def _load_cik_map():
    global _CIK_MAP
    if _CIK_MAP:
        return
    try:
        resp = requests.get("https://www.sec.gov/files/company_tickers.json",
                           headers=HEADERS, timeout=30)
        if resp.ok:
            _CIK_MAP = {v["ticker"].upper(): str(v["cik_str"]).zfill(10)
                       for v in resp.json().values()}
    except Exception:
        pass


def cik_for(ticker: str) -> str | None:
    _load_cik_map()
    return _CIK_MAP.get(ticker.upper())


# ─── Fetch filings list ────────────────────────────────────────────────────

def get_recent_filings(ticker: str, days: int = 30) -> list[dict]:
    """Fetch recent 8-K filings for a ticker. Only 8-K forms."""
    cik = cik_for(ticker)
    if not cik:
        return []

    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    if not resp.ok:
        return []

    data = resp.json()
    recent = data.get("filings", {}).get("recent", {})
    if not recent:
        return []

    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    forms, dates, items = recent.get("form", []), recent.get("filingDate", []), recent.get("items", [])
    accessions, primary_docs = recent.get("accessionNumber", []), recent.get("primaryDocument", [])

    filings = []
    for i in range(len(forms)):
        if dates[i] < cutoff:
            continue
        form = forms[i].upper().strip()
        if form not in ("8-K", "8-K/A"):
            continue

        items_str = str(items[i]) if i < len(items) else ""
        acc = accessions[i] if i < len(accessions) else ""
        acc_clean = acc.replace("-", "")

        filing = {
            "ticker": ticker.upper(),
            "cik": cik,
            "form_type": form,
            "filed_at": dates[i],
            "items": items_str,
            "accession": acc,
            "primary_doc": primary_docs[i] if i < len(primary_docs) else "",
            "text_url": f"https://www.sec.gov/Archives/edgar/data/{cik.lstrip('0')}/{acc_clean}/{acc}.txt",
            "html_url": f"https://www.sec.gov/Archives/edgar/data/{cik.lstrip('0')}/{acc_clean}/index.htm",
        }
        filings.append(filing)

    return filings


def fetch_filing_text(text_url: str) -> str | None:
    """Fetch the full text of an SEC filing (the TXT file) and clean it."""
    try:
        headers = {**HEADERS, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}
        resp = requests.get(text_url, headers=headers, timeout=60)
        if resp.ok:
            text = resp.text
            # Strip HTML tags (SEC files are HTML-in-XML monstrosities)
            soup = BeautifulSoup(text, "html.parser")
            clean = soup.get_text(separator="\n")
            # Decode common HTML entities
            clean = clean.replace("&#8482;", "™").replace("&amp;", "&")
            clean = clean.replace("&nbsp;", " ").replace("&#160;", " ")
            # Collapse excessive blank lines
            clean = re.sub(r'\n{3,}', '\n\n', clean)
            return clean[:50000]  # Cap at 50K chars
    except Exception:
        pass
    return None


# ─── Extract partnership details from 8-K text ───────────────────────────

def extract_agreement_partner(text: str, ticker: str) -> list[dict]:
    """
    Parse 8-K filing text to find the counterparty in a Material Definitive Agreement.
    Returns list of detected partners with confidence.
    """
    partners = []
    lines = text.split("\n")

    # Item 1.01 marker
    in_item_101 = False
    item_text = ""

    for i, line in enumerate(lines):
        # Detect Item 1.01 section
        if re.search(r'item\s+1\.01|item\s+101', line, re.IGNORECASE):
            in_item_101 = True
            item_text = line + "\n"
            continue
        # Detect next item boundary
        if in_item_101 and re.search(r'item\s+\d+\.\d+', line, re.IGNORECASE):
            break
        if in_item_101:
            item_text += line + "\n"

    if not item_text:
        return partners

    # Partner extraction patterns
    patterns = [
        r'(?:entered\s+into|enters\s+into)\s+(?:a\s+)?(?:definitive\s+)?'
        r'(?:agreement|contract|partnership|license|supply|development)\s+'
        r'(?:with\s+)?["\']?([A-Z][A-Za-z0-9\s.,&]+?)["\']?\s',
        r'(?:with\s+)(["\']?[A-Z][A-Za-z0-9\s.,&]+?)(?:["\']?)\s+'
        r'(?:dated|pursuant|whereby|under|for|to)',
        r'(?:partnership|collaboration|alliance)\s+(?:agreement\s+)?'
        r'(?:with\s+)?["\']?([A-Z][A-Za-z0-9\s.,&]+?)["\']?\s',
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, item_text[:10000], re.IGNORECASE):
            partner = match.group(1).strip()
            # Clean up trailing punctuation/articles
            partner = re.sub(r'\s+(and|or|the|a|an|in|for|to|of)\s+$', '', partner, flags=re.IGNORECASE)
            partner = re.sub(r'[.,;:)]+$', '', partner).strip()
            if len(partner) > 2 and partner.upper() != ticker:
                # Avoid matching the company itself
                ticker_lower = WATCHLIST.get(ticker, "").lower()
                if ticker_lower and ticker_lower not in partner.lower():
                    partners.append({
                        "partner_name": partner,
                        "context": item_text[:500],
                    })

    return partners


def extract_earnings_mentions(text: str, ticker: str) -> list[dict]:
    """
    Parse earnings press releases and conference call transcripts
    for mentions of partner companies, suppliers, and customers.
    """
    mentions = []
    
    # Phrases that introduce partner/supplier/customer mentions
    partner_phrases = [
        r"(?:strategic\s+)?partnership\s+(?:with\s+)?['\"]?([A-Z][A-Za-z0-9\s.,&]+?)['\"]?(?:\s+via|\s+for|\s+to|\s+in|\.|$)",
        r"(?:partnered|partnering|teamed|collaborating)\s+(?:with\s+)?['\"]?([A-Z][A-Za-z0-9\s.,&]+?)['\"]?",
        r"(?:supply|supplier|vendor)\s+(?:agreement|chain|partner)\s+(?:with\s+)?['\"]?([A-Z][A-Za-z0-9\s.,&]+?)['\"]?",
        r"(?:deploying|deployed|implementation)\s+(?:with\s+)?['\"]?([A-Z][A-Za-z0-9\s.,&]+?)['\"]?",
        r"(?:customer|client)\s+(?:includes?\s+|such\s+as\s+)?['\"]?([A-Z][A-Za-z0-9\s.,&]+?)['\"]?",
        r"expanded\s+(?:partnership|collaboration|relationship)\s+(?:with\s+)?['\"]?([A-Z][A-Za-z0-9\s.,&]+?)['\"]?",
    ]

    for phrase in partner_phrases:
        for match in re.finditer(phrase, text, re.IGNORECASE):
            company = match.group(1).strip()
            company = re.sub(r'[.,;:)]+$', '', company).strip()
            if len(company) > 3:
                start = max(0, match.start() - 120)
                end = min(len(text), match.end() + 120)
                context = text[start:end].strip()
                mentions.append({
                    "company_name": company,
                    "context": context,
                })

    return mentions


# ─── SEC Ticker Resolution ─────────────────────────────────────────────────

_SEC_TICKERS: dict[str, str] = {}

def _load_sec_tickers():
    global _SEC_TICKERS
    if _SEC_TICKERS:
        return
    try:
        resp = requests.get("https://www.sec.gov/files/company_tickers.json",
                           headers=HEADERS, timeout=15)
        if resp.ok:
            for v in resp.json().values():
                _SEC_TICKERS[v["ticker"].upper()] = v.get("title", "")
    except Exception:
        pass


def resolve_ticker(name: str) -> str | None:
    """Try to resolve a company name to a ticker via SEC data."""
    _load_sec_tickers()
    name_lower = name.lower()
    # Direct ticker check
    if name.upper() in _SEC_TICKERS:
        return name.upper()
    # SEC company name match
    for ticker, sec_name in _SEC_TICKERS.items():
        if sec_name and name_lower in sec_name.lower():
            return ticker
    return None


# ─── Main Scan ─────────────────────────────────────────────────────────────

def scan(tickers: list[str] | None = None, days: int = 30, deep: bool = False) -> dict:
    """Scan tickers for primary-source SEC filings and extract alpha signals."""
    if tickers is None:
        tickers = list(WATCHLIST.keys())

    results = {
        "scanned_at": datetime.now(timezone.utc).isoformat(),
        "lookback_days": days,
        "tickers_scanned": len(tickers),
        "filings_found": 0,
        "signals": [],
        "errors": [],
    }

    for ticker in tickers:
        try:
            filings = get_recent_filings(ticker, days=days)
            results["filings_found"] += len(filings)

            for filing in filings:
                signal = {
                    "ticker": filing["ticker"],
                    "filed_at": filing["filed_at"],
                    "form_type": filing["form_type"],
                    "items": filing["items"],
                    "url": filing["html_url"],
                    "alpha_type": None,
                    "partners": [],
                    "earnings_mentions": [],
                }

                items_str = filing["items"].lower()

                # Item 1.01 — Material Definitive Agreement (partnerships!)
                if "1.01" in items_str:
                    signal["alpha_type"] = "Partnership/Contract (8-K Item 1.01)"
                    if deep:
                        text = fetch_filing_text(filing["text_url"])
                        if text:
                            partners = extract_agreement_partner(text, ticker)
                            signal["partners"] = partners
                            # Try to resolve each partner to a ticker
                            for p in signal["partners"]:
                                ticker_match = resolve_ticker(p["partner_name"])
                                if ticker_match:
                                    p["resolved_ticker"] = ticker_match

                # Item 2.02 — Earnings (CEO talking)
                if "2.02" in items_str:
                    signal["alpha_type"] = "Earnings (8-K Item 2.02)"
                    if deep:
                        text = fetch_filing_text(filing["text_url"])
                        if text:
                            mentions = extract_earnings_mentions(text, ticker)
                            signal["earnings_mentions"] = mentions
                            for m in signal["earnings_mentions"]:
                                ticker_match = resolve_ticker(m["company_name"])
                                if ticker_match:
                                    m["resolved_ticker"] = ticker_match

                # Item 7.01 — Regulation FD (material press releases)
                if "7.01" in items_str:
                    signal["alpha_type"] = "Press Release (8-K Item 7.01)"
                    if deep:
                        text = fetch_filing_text(filing["text_url"])
                        if text:
                            partners = extract_agreement_partner(text, ticker)
                            signal["partners"] = partners

                results["signals"].append(signal)

            time.sleep(0.15)  # Rate limit: ~6 req/s

        except Exception as e:
            results["errors"].append(f"{ticker}: {e}")

    # Sort: most recent first
    results["signals"].sort(key=lambda s: s["filed_at"], reverse=True)
    return results


# ─── Output ────────────────────────────────────────────────────────────────

def format_terminal(results: dict) -> str:
    lines = [
        f"\n{'='*60}",
        f"📄 PRIMARY-SOURCE ALPHA — {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}",
        f"{'='*60}",
        f"  Tickers scanned: {results['tickers_scanned']}",
        f"  8-K filings found: {results['filings_found']}",
        f"  Alpha signals: {len(results['signals'])}",
        f"  Lookback: {results['lookback_days']}d",
    ]

    if results["errors"]:
        lines.append(f"\n  ⚠️ Errors: {len(results['errors'])}")

    # Group signals by type
    agreements = [s for s in results["signals"] if s["alpha_type"] and "Partnership" in s["alpha_type"]]
    earnings = [s for s in results["signals"] if s["alpha_type"] and "Earnings" in s["alpha_type"]]
    others = [s for s in results["signals"] if s not in agreements and s not in earnings]

    if agreements:
        lines.append(f"\n{'─'*60}")
        lines.append(f"  📝 MATERIAL AGREEMENTS — {len(agreements)}")
        lines.append(f"{'─'*60}")
        for s in agreements[:15]:
            lines.append(f"\n  ${s['ticker']:<6} 📅 {s['filed_at']}")
            if s.get("partners"):
                for p in s["partners"]:
                    tick = f" → ${p['resolved_ticker']}" if p.get("resolved_ticker") else ""
                    lines.append(f"         Partner: {p['partner_name'][:70]}{tick}")
            lines.append(f"         {s['url']}")

    if earnings:
        lines.append(f"\n{'─'*60}")
        lines.append(f"  🎙️ EARNINGS / CEO MENTIONS — {len(earnings)}")
        lines.append(f"{'─'*60}")
        for s in earnings[:10]:
            lines.append(f"\n  ${s['ticker']:<6} 📅 {s['filed_at']}")
            if s.get("earnings_mentions"):
                for m in s["earnings_mentions"][:5]:
                    tick = f" → ${m['resolved_ticker']}" if m.get("resolved_ticker") else ""
                    ctx = m["context"][:120].replace("\n", " ")
                    lines.append(f"         📢 {m['company_name']}{tick}")
                    lines.append(f"            \"{ctx}...\"")
            lines.append(f"         {s['url']}")

    if others:
        lines.append(f"\n{'─'*60}")
        lines.append(f"  🔔 Other signals — {len(others)}")
        lines.append(f"{'─'*60}")

    lines.append(f"\n{'='*60}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Primary-Source Alpha Scanner")
    parser.add_argument("--tickers", nargs="*", help="Tickers to scan")
    parser.add_argument("--days", type=int, default=30, help="Lookback (default: 30)")
    parser.add_argument("--deep", action="store_true", help="Fetch filing text (slower)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    results = scan(tickers=args.tickers, days=args.days, deep=args.deep)

    if args.json:
        print(json.dumps(results, indent=2, default=str))
    else:
        print(format_terminal(results))


if __name__ == "__main__":
    main()