#!/usr/bin/env python3
"""
insider_scraper.py — SEC Form 4 Insider Trading Scanner

Tracks insider purchases (open-market buys by executives/directors).
Cluster-buying (2+ insiders within 7 days) = strongest alpha signal.

Sources:
  - SEC EDGAR submissions API (free, no key, 10 req/s limit)
  - Direct Form 4 XML parsing from SEC Archives

Usage:
    python3 backend/insider_scraper.py --tickers NVDA PLTR
    python3 backend/insider_scraper.py --tickers NVDA --days 60
    python3 backend/insider_scraper.py --tickers NVDA --json
    python3 backend/insider_scraper.py --all-mega-caps           # scan watchlist
    python3 backend/insider_scraper.py --recent                  # scan all mega-caps last 7 days
"""

import argparse
import json
import os
import re
import sqlite3
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from typing import Optional

import requests

USER_AGENT = "NoFomo Research (research@nofomo.app)"
HEADERS = {"User-Agent": USER_AGENT, "Accept": "application/json"}

# Mega-cap AI/compute watchlist
MEGA_CAP_TICKERS = [
    "NVDA","AMD","AVGO","MRVL","MU","TSM","INTC",
    "MSFT","AMZN","GOOGL","META","AAPL","ORCL","CRM",
    "NOW","SNOW","IBM","TSLA","PLTR","LLY",
]

# SEC CIK cache
_CIK_MAP: dict[str, str] = {}

def _load_cik():
    global _CIK_MAP
    if _CIK_MAP:
        return
    try:
        r = requests.get("https://www.sec.gov/files/company_tickers.json", headers=HEADERS, timeout=30)
        if r.ok:
            _CIK_MAP = {v["ticker"].upper(): str(v["cik_str"]).zfill(10) for v in r.json().values()}
    except Exception:
        pass


def cik_for(t: str) -> str | None:
    _load_cik()
    return _CIK_MAP.get(t.upper())


# ─── Fetch Form 4 filings ────────────────────────────────────────────────

def get_form4_filings(ticker: str, days: int = 30) -> list[dict]:
    """Fetch Form 4 filings for a ticker from SEC EDGAR."""
    cik = cik_for(ticker)
    if not cik:
        return []

    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    r = requests.get(url, headers=HEADERS, timeout=30)
    if not r.ok:
        return []

    data = r.json()
    recent = data.get("filings", {}).get("recent", {})
    if not recent:
        return []

    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    forms, dates, accessions = recent.get("form", []), recent.get("filingDate", []), recent.get("accessionNumber", [])
    primary_docs = recent.get("primaryDocument", [])

    filings = []
    for i in range(len(forms)):
        if dates[i] < cutoff:
            continue
        if forms[i].upper().strip() != "4":
            continue

        acc = accessions[i] if i < len(accessions) else ""
        acc_clean = acc.replace("-", "")
        doc = primary_docs[i] if i < len(primary_docs) else ""

        filings.append({
            "ticker": ticker.upper(),
            "cik": cik,
            "filed_at": dates[i],
            "accession": acc,
            "primary_doc": doc,
            "text_url": f"https://www.sec.gov/Archives/edgar/data/{cik.lstrip('0')}/{acc_clean}/{doc}",
            "html_url": f"https://www.sec.gov/Archives/edgar/data/{cik.lstrip('0')}/{acc_clean}/index.htm",
            "xml_url": None,  # resolved by _find_xml_url
        })
    return filings


def parse_form4_xml(text: str, ticker: str) -> list[dict]:
    """Parse Form 4 XML to extract insider transactions."""
    trades = []
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        return trades

    ns = {"": "http://www.sec.gov/edgar/common", "ns2": "http://www.sec.gov/edgar/thirteenfiler"}
    # Try common namespace patterns
    root_tag = root.tag
    # SEC XML is namespace-heavy — use wildcard search
    namespaces = {
        "edgar": "http://www.sec.gov/edgar/common",
        "nonDeriv": "http://www.sec.gov/edgar/nonderivativetransaction",
        "deriv": "http://www.sec.gov/edgar/derivativetransaction",
    }

    # Find issuer
    issuer = root.find(".//issuerName", namespaces)
    issuer_name = issuer.text if issuer is not None else ticker

    # Find reporting owner
    rpt_owner = root.find(".//reportingOwner/reportingOwnerId/rptOwnerName")
    owner_name = rpt_owner.text.strip() if rpt_owner is not None and rpt_owner.text else "Unknown"
    # SEC XML wraps in <value> sometimes
    if not owner_name or owner_name == "Unknown":
        v_el = root.find(".//reportingOwner/reportingOwnerId/rptOwnerName/value")
        if v_el is not None and v_el.text:
            owner_name = v_el.text.strip()

    rel = root.find(".//reportingOwner/reportingOwnerRelationship")
    is_director = 1 if rel is not None and rel.find("isDirector") is not None and rel.find("isDirector").text and "1" in rel.find("isDirector").text else 0
    is_officer = 1 if rel is not None and rel.find("isOfficer") is not None and rel.find("isOfficer").text and "1" in rel.find("isOfficer").text else 0
    is_ten_pct = 1 if rel is not None and rel.find("isTenPercentOwner") is not None and rel.find("isTenPercentOwner").text and "1" in rel.find("isTenPercentOwner").text else 0
    title_el = rel.find("officerTitle") if rel is not None else None
    title = title_el.text.strip() if title_el is not None and title_el.text else ""

    # Parse each non-derivative transaction
    for trans in root.findall(".//nonDerivativeTransaction"):
        try:
            # SEC Form 4 XML — values can be direct text or in <value> child
            def v(el, path):
                found = el.find(path)
                if found is not None:
                    # Try direct text first
                    if found.text and found.text.strip():
                        return found.text.strip()
                    # Fall back to <value> child
                    v_el = found.find("value")
                    if v_el is not None and v_el.text:
                        return v_el.text.strip()
                return None

            code = v(trans, "transactionCoding/transactionCode")
            shares_str = v(trans, "transactionAmounts/transactionShares")
            price_str = v(trans, "transactionAmounts/transactionPricePerShare")
            holdings_str = v(trans, "postTransactionAmounts/sharesOwnedFollowingTransaction")
            date_val = v(trans, "transactionDate")

            if not code:
                continue

            share_val = float(shares_str) if shares_str else 0
            price_val = float(price_str) if price_str else 0
            holdings_val = float(holdings_str) if holdings_str else 0
            date_text = date_val or ""

            # Only open-market purchases (P) or sales (S)
            if code not in ("P", "S"):
                continue

            trade = {
                "ticker": ticker.upper(),
                "owner_name": owner_name,
                "owner_title": title,
                "trade_type": code,
                "shares": share_val,
                "price": price_val if price_val else 0,
                "value": round(share_val * price_val, 2) if price_val else 0,
                "shares_owned": holdings_val,
                "is_ceo": 1 if "CEO" in title.upper() or "CHIEF EXECUTIVE" in title.upper() else 0,
                "is_cfo": 1 if "CFO" in title.upper() or "CHIEF FINANCIAL" in title.upper() else 0,
                "is_director": is_director,
                "is_ten_percent": is_ten_pct,
                "filing_date": date_text,
            }
            trades.append(trade)
        except (ValueError, AttributeError) as e:
            continue

    return trades


def parse_form4_htext(text: str, ticker: str) -> list[dict]:
    """
    Parse Form 4 from SEC HTML text (fallback when XML parsing fails).
    Extracts insider transactions using regex patterns on the raw document text.
    """
    trades = []
    lines = text.split("\n")

    # Find ownership blocks
    owner_name = "Unknown"
    for line in lines:
        m = re.search(r'<rptOwnerName[^>]*>\s*<!\[CDATA\[(.+?)\]\]>', line)
        if m:
            owner_name = m.group(1).strip()
            break

    # Find officer title
    title = ""
    for line in lines:
        m = re.search(r'<officerTitle[^>]*>\s*<!\[CDATA\[(.+?)\]\]>', line)
        if m:
            title = m.group(1).strip()
            break

    is_director = 1 if any('isDirector>1<' in l for l in lines) else 0

    # Find non-derivative tables
    # Look for transaction blocks
    in_table = False
    for i, line in enumerate(lines):
        if 'nonDerivativeTable' in line:
            in_table = True
        if in_table and 'derivativeTable' in line:
            break
        if not in_table:
            continue

        # Parse individual transactions
        if 'transactionCode' in line:
            m = re.search(r'<transactionCode[^>]*>\s*<!\[CDATA\[([PS])\]\]>', line)
            if m:
                code = m.group(1)
                # Find the rest of this transaction (shares, price, date)
                shares, price, holdings, date_val = 0, 0, 0, ""
                for j in range(i, min(i + 30, len(lines))):
                    sm = re.search(r'<transactionShares[^>]*>\s*<!\[CDATA\[([\d.]+)\]\]>', lines[j])
                    if sm:
                        shares = float(sm.group(1))
                    pm = re.search(r'<transactionPricePerShare[^>]*>\s*<!\[CDATA\[([\d.]+)\]\]>', lines[j])
                    if pm:
                        price = float(pm.group(1))
                    hm = re.search(r'<sharesOwnedFollowingTransaction[^>]*>\s*<!\[CDATA\[([\d.]+)\]\]>', lines[j])
                    if hm:
                        holdings = float(hm.group(1))
                    dm = re.search(r'<transactionDate[^>]*>\s*<!\[CDATA\[([\d\-]+)\]\]>', lines[j])
                    if dm:
                        date_val = dm.group(1)

                if shares > 0:
                    trade = {
                        "ticker": ticker.upper(),
                        "owner_name": owner_name,
                        "owner_title": title,
                        "trade_type": code,
                        "shares": shares,
                        "price": price,
                        "value": round(shares * price, 2),
                        "shares_owned": holdings,
                        "is_ceo": 1 if "CEO" in title.upper() or "CHIEF EXECUTIVE" in title.upper() else 0,
                        "is_cfo": 1 if "CFO" in title.upper() or "CHIEF FINANCIAL" in title.upper() else 0,
                        "is_director": is_director,
                        "is_ten_percent": 0,
                        "filing_date": date_val,
                    }
                    trades.append(trade)

    return trades


# ─── Cache integration ────────────────────────────────────────────────────

CACHE_DB = os.path.join(os.path.dirname(__file__), "cache", "alpha_cache.db")

def save_to_cache(trades: list[dict]):
    """Save insider trades to SQLite cache."""
    if not trades:
        return 0

    conn = sqlite3.connect(CACHE_DB)
    saved = 0
    for t in trades:
        try:
            conn.execute("""
                INSERT OR IGNORE INTO insider_trades
                (ticker, filing_date, owner_name, owner_title, trade_type,
                 shares, price, value, shares_owned, is_ceo, is_cfo,
                 is_director, is_ten_percent, raw_data)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                t["ticker"], t.get("filing_date",""), t["owner_name"], t["owner_title"],
                t["trade_type"], t["shares"], t["price"], t["value"], t["shares_owned"],
                t["is_ceo"], t["is_cfo"], t["is_director"], t["is_ten_percent"],
                json.dumps(t),
            ))
            saved += 1

            # Also write to alpha_signals if it's a notable trade
            if t["value"] > 50000 or t["is_ceo"] or t["is_cfo"]:
                conn.execute("""
                    INSERT OR IGNORE INTO alpha_signals
                    (ticker, scraper, signal_date, signal_type, title, score, detail)
                    VALUES (?,?,?,?,?,?,?)
                """, (
                    t["ticker"], "insider", t.get("filing_date",""),
                    f"insider_{t['trade_type'].lower()}",
                    f"{t['owner_name']} {'bought' if t['trade_type']=='P' else 'sold'} {t['shares']:,.0f} shares @ ${t['price']:.2f} ({'${:,.0f}'.format(t['value'])})",
                    min(100, int(t["value"] / 1000)),  # Score based on size
                    json.dumps(t),
                ))
        except Exception:
            pass

    conn.commit()
    conn.close()
    return saved


# ─── Scan ──────────────────────────────────────────────────────────────────

def scan(tickers: list[str], days: int = 30, fetch_xml: bool = True) -> dict:
    """Scan tickers for insider Form 4 filings."""
    results = {
        "scanned_at": datetime.now(timezone.utc).isoformat(),
        "tickers_scanned": len(tickers),
        "lookback_days": days,
        "form4_filings": 0,
        "trades_found": 0,
        "trades_saved": 0,
        "purchases": 0,
        "sales": 0,
        "clusters": [],  # 2+ insiders buying in 7-day window
        "trades": [],
        "errors": [],
    }

    all_trades = []

    for ticker in tickers:
        try:
            filings = get_form4_filings(ticker, days=days)
            results["form4_filings"] += len(filings)

            for f in filings[:5]:  # Limit to 5 per ticker (recent ones)
                # Resolve the raw XML URL (strips XSLT path)
                xml_url = f["text_url"]
                if "xslF" in xml_url or "/xsl" in xml_url.lower():
                    parts = xml_url.split("/")
                    # Remove the XSLT directory part
                    cleaned = [p for p in parts if not p.startswith("xsl") and not p.startswith("XSL")]
                    xml_url = "/".join(cleaned)
                
                try:
                    headers = {**HEADERS, "Accept": "text/xml,application/xml"}
                    r = requests.get(xml_url, headers=headers, timeout=30)
                    if not r.ok:
                        r = requests.get(f["text_url"], headers=headers, timeout=30)
                    if not r.ok:
                        continue

                    # Try XML parse first, fall back to HTML regex
                    trades = parse_form4_xml(r.text, ticker)
                    if not trades:
                        trades = parse_form4_htext(r.text, ticker)

                    for t in trades:
                        all_trades.append(t)
                        results["trades_found"] += 1
                        if t["trade_type"] == "P":
                            results["purchases"] += 1
                        else:
                            results["sales"] += 1

                except Exception as e:
                    results["errors"].append(f"{ticker} text fetch: {e}")

            time.sleep(0.15)

        except Exception as e:
            results["errors"].append(f"{ticker}: {e}")

    # Save to cache
    results["trades_saved"] = save_to_cache(all_trades)
    results["trades"] = all_trades

    return results


def format_terminal(results: dict) -> str:
    lines = [
        f"\n{'='*60}",
        f"📊 INSIDER TRADING SCANNER — {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}",
        f"{'='*60}",
        f"  Tickers scanned:  {results['tickers_scanned']}",
        f"  Form 4 filings:   {results['form4_filings']}",
        f"  Trades extracted: {results['trades_found']}",
        f"  Purchases:        {results['purchases']}",
        f"  Sales:            {results['sales']}",
        f"  Saved to cache:   {results['trades_saved']}",
    ]

    if results["errors"]:
        lines.append(f"\n  ⚠️ Errors: {len(results['errors'])}")

    purchases = [t for t in results["trades"] if t["trade_type"] == "P"]
    if purchases:
        lines.append(f"\n{'─'*60}")
        lines.append(f"  🔴 INSIDER PURCHASES ({len(purchases)})")
        lines.append(f"{'─'*60}")
        for t in sorted(purchases, key=lambda x: x["value"], reverse=True)[:10]:
            signal = "⭐" if t["is_ceo"] or t["is_cfo"] else ""
            lines.append(
                f"  ${t['ticker']:<6} {signal} {t['owner_name'][:25]:<25} "
                f"bought {t['shares']:>8,.0f} sh @ ${t['price']:<7.2f} "
                f"= ${t['value']:>9,.0f}"
            )

    sales = [t for t in results["trades"] if t["trade_type"] == "S"]
    if sales:
        lines.append(f"\n{'─'*60}")
        lines.append(f"  🟢 INSIDER SALES ({len(sales)})")
        lines.append(f"{'─'*60}")
        for t in sorted(sales, key=lambda x: x["value"], reverse=True)[:5]:
            lines.append(
                f"  ${t['ticker']:<6} {t['owner_name'][:25]:<25} "
                f"sold {t['shares']:>8,.0f} sh @ ${t['price']:<7.2f} "
                f"= ${t['value']:>9,.0f}"
            )

    lines.append(f"\n{'='*60}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="SEC Form 4 Insider Trading Scanner")
    parser.add_argument("--tickers", nargs="*", help="Tickers to scan")
    parser.add_argument("--days", type=int, default=30, help="Lookback days")
    parser.add_argument("--all-mega-caps", action="store_true", help="Scan all mega-cap AI tickers")
    parser.add_argument("--recent", action="store_true", help="Quick scan last 7 days on mega-caps")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    tickers = args.tickers or (MEGA_CAP_TICKERS if args.all_mega_caps else None) or ["NVDA", "PLTR"]
    days = 7 if args.recent else args.days

    results = scan(tickers=tickers, days=days)

    if args.json:
        print(json.dumps(results, indent=2, default=str))
    else:
        print(format_terminal(results))


if __name__ == "__main__":
    main()