#!/usr/bin/env python3
"""
gov_contracts_scraper.py — Federal Contract Award Scanner

Monitors SAM.gov / USASpending.gov for government contract awards that
involve watchlist companies. Government contracts are filed BEFORE any
press release — pure primary-source alpha.

Sources (free, no API key):
  - USASpending.gov API: https://api.usaspending.gov/
  - SAM.gov public search

Usage:
    python3 backend/gov_contracts_scraper.py --tickers PLTR NVDA
    python3 backend/gov_contracts_scraper.py --all-mega-caps
    python3 backend/gov_contracts_scraper.py --days 30
    python3 backend/gov_contracts_scraper.py --json
"""

import argparse
import json
import os
import re
import sqlite3
import sys
import time
from datetime import datetime, timedelta, timezone

import requests

USER_AGENT = "NoFomo Research (research@nofomo.app)"
HEADERS = {"User-Agent": USER_AGENT, "Content-Type": "application/json"}

MEGA_CAP_TICKERS = [
    "NVDA","AMD","AVGO","MRVL","MU","TSM","INTC",
    "MSFT","AMZN","GOOGL","META","AAPL","ORCL","CRM",
    "NOW","SNOW","IBM","TSLA","PLTR","LLY",
]

# ─── Company name → ticker mapping (for USASpending results) ──────────────

COMPANY_NAMES = {
    "NVIDIA": "NVDA", "NVIDIA CORP": "NVDA",
    "AMD": "AMD", "ADVANCED MICRO DEVICES": "AMD",
    "BROADCOM": "AVGO",
    "MARVELL": "MRVL",
    "MICRON": "MU",
    "INTEL": "INTC",
    "MICROSOFT": "MSFT",
    "AMAZON": "AMZN", "AMAZON WEB SERVICES": "AMZN", "AWS": "AMZN",
    "ALPHABET": "GOOGL", "GOOGLE": "GOOGL",
    "META": "META",
    "APPLE": "AAPL",
    "ORACLE": "ORCL",
    "SALESFORCE": "CRM",
    "SERVICENOW": "NOW",
    "SNOWFLAKE": "SNOW",
    "IBM": "IBM",
    "TESLA": "TSLA",
    "PALANTIR": "PLTR",
    "ELI LILLY": "LLY", "LILLY": "LLY",
}

# Build reverse: keyword → ticker
_LOOKUP: list[tuple[str, str]] = []
for name, ticker in COMPANY_NAMES.items():
    _LOOKUP.append((name.lower(), ticker))


# ─── Cache ────────────────────────────────────────────────────────────────

CACHE_DB = os.path.join(os.path.dirname(__file__), "cache", "alpha_cache.db")

def save_to_cache(contracts: list[dict]):
    if not contracts:
        return 0
    conn = sqlite3.connect(CACHE_DB)
    saved = 0
    for c in contracts:
        try:
            conn.execute("""
                INSERT OR IGNORE INTO gov_contracts
                (ticker, award_date, agency, department, contract_value,
                 contract_type, description, piid, raw_data)
                VALUES (?,?,?,?,?,?,?,?,?)
            """, (
                c["ticker"], c.get("award_date",""), c.get("agency",""),
                c.get("department",""), c.get("contract_value",0),
                c.get("contract_type",""), c.get("description",""),
                c.get("piid",""), json.dumps(c),
            ))
            saved += 1

            # Alpha signal for large contracts
            value = c.get("contract_value", 0) or 0
            if value > 1_000_000:
                conn.execute("""
                    INSERT OR IGNORE INTO alpha_signals
                    (ticker, scraper, signal_date, signal_type, title, score, detail)
                    VALUES (?,?,?,?,?,?,?)
                """, (
                    c["ticker"], "gov_contracts", c.get("award_date",""),
                    "contract_award",
                    f"${value/1e6:.0f}M {c.get('contract_type','')} contract with {c.get('agency','USG')}",
                    min(100, int(value / 25_000)),
                    json.dumps(c),
                ))
        except Exception:
            pass
    conn.commit()
    conn.close()
    return saved


# ─── USASpending.gov API ─────────────────────────────────────────────────

def search_usaspending(keywords: list[str], days: int = 365) -> list[dict]:
    """
    Search USASpending.gov for recent contract awards matching keywords.
    Uses the free public API (no key required).
    """
    contracts = []
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")

    for keyword in keywords[:10]:  # Limit to 10 keywords to avoid rate limits
        try:
            url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
            payload = {
                "filters": {
                    "time_period": [{"start_date": since, "end_date": "2026-12-31"}],
                    "keywords": [keyword],
                    "award_type_codes": ["A", "B", "C", "D"],
                },
                "fields": [
                    "Award ID", "Recipient Name", "Recipient DUNS",
                    "Prime Award Type", "Award Amount", "Awarding Agency",
                    "Award Date", "Description",
                ],
                "limit": 5,
            }
            r = requests.post(url, json=payload, headers=HEADERS, timeout=60)
            if not r.ok:
                continue

            data = r.json()
            results = data.get("results", []) if isinstance(data, dict) else []

            for award in results:
                rec_name = award.get("Recipient Name", "") or ""

                # Check if recipient matches our watchlist
                ticker = None
                for name_lower, t in _LOOKUP:
                    if name_lower in rec_name.lower():
                        ticker = t
                        break

                if not ticker:
                    # Check if keyword matches company name directly
                    kw_lower = keyword.lower()
                    for name_lower, t in _LOOKUP:
                        if kw_lower == name_lower or kw_lower[:5] == name_lower[:5]:
                            ticker = t
                            break

                if ticker:
                    award_amount = award.get("Award Amount", 0) or 0
                    award_date = award.get("Award Date", "") or since[:10]
                    if isinstance(award_date, list):
                        award_date = award_date[0] if award_date else since[:10]
                    agency = award.get("Awarding Agency", "") or ""
                    desc = award.get("Description", f"{ticker} USG contract") or ""
                    piid = award.get("Award ID", "") or ""

                    contracts.append({
                        "ticker": ticker,
                        "award_date": str(award_date)[:10],
                        "agency": agency if isinstance(agency, str) else str(agency),
                        "department": agency if isinstance(agency, str) else str(agency),
                        "contract_value": float(award_amount) if award_amount else 0,
                        "contract_type": award.get("Prime Award Type", "Contract") or "Contract",
                        "description": str(desc)[:500],
                        "piid": str(piid),
                    })

            time.sleep(0.5)

        except Exception:
            continue

    return contracts


# ─── SAM.gov direct search (fallback) ─────────────────────────────────────

def search_sam_direct(ticker: str, days: int = 30) -> list[dict]:
    """
    Direct SAM.gov search as fallback for specific tickers.
    Uses SAM.gov's public API.
    """
    contracts = []
    try:
        url = "https://sam.gov/api/prod/opp/v2/search/opportunities"
        params = {
            "q": ticker,
            "postedFrom": (datetime.now() - timedelta(days=days)).strftime("%m/%d/%Y"),
            "postedTo": datetime.now().strftime("%m/%d/%Y"),
        }
        r = requests.get(url, params=params, headers=HEADERS, timeout=30)
        if r.ok:
            data = r.json()
            for item in data.get("results", data.get("data", []))[:5]:
                if isinstance(item, dict):
                    contracts.append({
                        "ticker": ticker,
                        "award_date": item.get("postedDate", "")[:10],
                        "agency": item.get("agency", ""),
                        "department": item.get("office", ""),
                        "contract_value": item.get("value", 0) or 0,
                        "contract_type": item.get("type", "Opportunity"),
                        "description": item.get("title", f"{ticker} SAM.gov opportunity")[:500],
                        "piid": item.get("solicitationNumber", ""),
                    })
    except Exception:
        pass
    return contracts


# ─── Scan ──────────────────────────────────────────────────────────────────

def scan(tickers: list[str], days: int = 30) -> dict:
    """Scan for government contract awards."""
    results = {
        "scanned_at": datetime.now(timezone.utc).isoformat(),
        "tickers_monitored": len(tickers),
        "lookback_days": days,
        "contracts_found": 0,
        "contracts": [],
        "saved": 0,
        "errors": [],
    }

    # Use USASpending for keyword searches
    keywords = list(set(
        [t for t in tickers] +
        [name for name, _ in _LOOKUP]
    ))

    contracts = search_usaspending(keywords, days=days)
    results["contracts"] = contracts
    results["contracts_found"] = len(contracts)
    results["saved"] = save_to_cache(contracts)

    return results


def format_terminal(results: dict) -> str:
    lines = [
        f"\n{'='*60}",
        f"📋 GOV CONTRACT SCANNER — {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}",
        f"{'='*60}",
        f"  Tickers monitored: {results['tickers_monitored']}",
        f"  Contracts found:   {results['contracts_found']}",
        f"  Saved to cache:    {results['saved']}",
        f"  Lookback:          {results['lookback_days']}d",
    ]

    if results["errors"]:
        lines.append(f"\n  ⚠️ Errors: {len(results['errors'])}")

    if not results["contracts"]:
        lines.append(f"\n  No contracts found in this window.")
        lines.append(f"  (USASpending API may have limited coverage for recent awards.)")
    else:
        lines.append(f"\n{'─'*60}")
        lines.append(f"  CONTRACT AWARDS")
        lines.append(f"{'─'*60}")
        for c in sorted(results["contracts"], key=lambda x: x.get("contract_value", 0), reverse=True)[:15]:
            val = c.get("contract_value", 0) or 0
            val_str = f"${val/1e6:.1f}M" if val > 0 else "value N/A"
            lines.append(
                f"\n  ${c['ticker']:<6} {val_str:>12} | {c.get('agency','')[:40]:<40}"
            )
            if c.get("description"):
                lines.append(f"         {c['description'][:100]}")

    lines.append(f"\n{'='*60}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Government Contract Award Scanner")
    parser.add_argument("--tickers", nargs="*", help="Tickers to scan")
    parser.add_argument("--all-mega-caps", action="store_true", help="Scan all mega-cap AI tickers")
    parser.add_argument("--days", type=int, default=30, help="Lookback days")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    tickers = args.tickers or (MEGA_CAP_TICKERS if args.all_mega_caps else ["PLTR", "NVDA"])
    results = scan(tickers=tickers, days=args.days)

    if args.json:
        print(json.dumps(results, indent=2, default=str))
    else:
        print(format_terminal(results))


if __name__ == "__main__":
    main()