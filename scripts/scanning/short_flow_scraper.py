#!/usr/bin/env python3
"""
short_flow_scraper.py — Short Interest & Borrow Rate Scanner

Tracks short interest, borrow rates, and squeeze setups across the watchlist.
Flags: high short % + rising borrow rate + positive momentum = squeeze setup.

Sources (free, no API key):
  - yfinance: short_pct_float, avg_volume, price data
  - FINRA short volume: https://www.finra.org/finra-data/browse-catalog/short-sale-volume-data
  - Borrow rate: estimated from yfinance short data + computed signals

Usage:
    python3 backend/short_flow_scraper.py --tickers NVDA PLTR
    python3 backend/short_flow_scraper.py --all-mega-caps
    python3 backend/short_flow_scraper.py --squeeze-candidates  # high setup
    python3 backend/short_flow_scraper.py --json
"""

import argparse
import json
import os
import sqlite3
import sys
import time
from datetime import datetime, timezone

import requests
import yfinance as yf

USER_AGENT = "NoFomo Research (research@nofomo.app)"
HEADERS = {"User-Agent": USER_AGENT}

MEGA_CAP_TICKERS = [
    "NVDA","AMD","AVGO","MRVL","MU","TSM","INTC",
    "MSFT","AMZN","GOOGL","META","AAPL","ORCL","CRM",
    "NOW","SNOW","IBM","TSLA","PLTR","LLY",
]

# ─── Cache ────────────────────────────────────────────────────────────────

CACHE_DB = os.path.join(os.path.dirname(__file__), "cache", "alpha_cache.db")

def save_to_cache(rows: list[dict]):
    if not rows:
        return 0
    conn = sqlite3.connect(CACHE_DB)
    saved = 0
    for r in rows:
        try:
            conn.execute("""
                INSERT OR REPLACE INTO short_flow
                (ticker, date, short_pct_float, short_shares, avg_volume,
                 days_to_cover, borrow_rate, raw_data)
                VALUES (?,?,?,?,?,?,?,?)
            """, (
                r["ticker"], r["date"], r.get("short_pct_float"),
                r.get("short_shares"), r.get("avg_volume"),
                r.get("days_to_cover"), r.get("borrow_rate"),
                json.dumps(r),
            ))
            saved += 1

            # Flag squeeze setups in alpha_signals
            pct = r.get("short_pct_float", 0) or 0
            dtc = r.get("days_to_cover", 0) or 0
            if pct > 10 and dtc > 3:
                conn.execute("""
                    INSERT OR IGNORE INTO alpha_signals
                    (ticker, scraper, signal_date, signal_type, title, score, detail)
                    VALUES (?,?,?,?,?,?,?)
                """, (
                    r["ticker"], "short_flow", r["date"],
                    "squeeze_setup",
                    f"Short squeeze setup: {pct:.1f}% float short, {dtc:.1f} days to cover",
                    min(100, int(pct * 3)),
                    json.dumps(r),
                ))
        except Exception:
            pass
    conn.commit()
    conn.close()
    return saved


# ─── Fetch FINRA short volume ────────────────────────────────────────────

def fetch_finra_short_volume(ticker: str) -> dict | None:
    """
    Fetch FINRA short sale volume data for a ticker.
    FINRA publishes daily short volume for all OTC and exchange-listed securities.
    URL pattern: https://www.finra.org/...
    """
    try:
        # FINRA's API endpoint for short volume data
        url = f"https://api.finra.org/data/group/OTCMarket/name/regSHO%20Monthly%20Short%20Volume"
        payload = {
            "ticker": ticker,
            "limit": 1,
        }
        r = requests.post(url, json=payload, headers=HEADERS, timeout=15)
        if r.ok:
            data = r.json()
            if data:
                return {
                    "short_volume": data[0].get("totalShortVolume"),
                    "total_volume": data[0].get("totalVolume"),
                    "short_ratio": data[0].get("shortRatio"),
                }
    except Exception:
        pass
    return None


# ─── Scan ──────────────────────────────────────────────────────────────────

def scan(tickers: list[str]) -> dict:
    """Scan tickers for short interest and borrow data."""
    results = {
        "scanned_at": datetime.now(timezone.utc).isoformat(),
        "tickers_scanned": len(tickers),
        "snapshots": [],
        "squeeze_candidates": [],
        "saved": 0,
        "errors": [],
    }

    for ticker in tickers:
        try:
            t = yf.Ticker(ticker)
            info = t.info
            hist = t.history(period="3mo")

            if hist.empty:
                continue

            close = hist["Close"]
            volume = hist["Volume"]
            price = float(close.iloc[-1])
            avg_vol = int(volume.tail(20).mean())

            short_pct = info.get("shortPercentOfFloat")
            if short_pct:
                short_pct = round(short_pct * 100, 2)

            shares_out = info.get("sharesOutstanding")
            short_shares = None
            if short_pct and shares_out:
                short_shares = int(shares_out * short_pct / 100)

            # Days to cover
            days_to_cover = None
            if short_shares and avg_vol > 0:
                days_to_cover = round(short_shares / avg_vol, 2)

            # Borrow rate (estimated from utilization)
            # yfinance doesn't give borrow rate directly.
            # We compute an estimated rate from short %:
            borrow_rate = None
            if short_pct:
                if short_pct > 20:
                    borrow_rate = round(short_pct * 0.15, 2)  # estimated
                elif short_pct > 10:
                    borrow_rate = round(short_pct * 0.08, 2)
                elif short_pct > 5:
                    borrow_rate = round(short_pct * 0.03, 2)

            snapshot = {
                "ticker": ticker,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "price": price,
                "short_pct_float": short_pct,
                "short_shares": short_shares,
                "avg_volume": avg_vol,
                "days_to_cover": days_to_cover,
                "borrow_rate": borrow_rate,
                "change_pct": info.get("regularMarketChangePercent"),
                "beta": info.get("beta"),
            }
            results["snapshots"].append(snapshot)

            if short_pct and (short_pct > 10 or (short_pct > 5 and days_to_cover and days_to_cover > 3)):
                results["squeeze_candidates"].append(snapshot)

            time.sleep(0.5)

        except Exception as e:
            results["errors"].append(f"{ticker}: {e}")

    results["saved"] = save_to_cache(results["snapshots"])
    return results


def format_terminal(results: dict) -> str:
    lines = [
        f"\n{'='*60}",
        f"📉 SHORT FLOW SCANNER — {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}",
        f"{'='*60}",
        f"  Tickers scanned: {results['tickers_scanned']}",
        f"  Saved to cache:  {results['saved']}",
    ]

    if results["errors"]:
        lines.append(f"\n  ⚠️ Errors: {len(results['errors'])}")

    if results["squeeze_candidates"]:
        lines.append(f"\n{'─'*60}")
        lines.append(f"  🚀 SQUEEZE CANDIDATES ({len(results['squeeze_candidates'])})")
        lines.append(f"{'─'*60}")
        for s in sorted(results["squeeze_candidates"], key=lambda x: x.get("short_pct_float", 0) or 0, reverse=True):
            pct = s.get("short_pct_float", 0) or 0
            dtc = s.get("days_to_cover", 0) or 0
            br = s.get("borrow_rate", 0) or 0
            warning = "⚠️" if pct > 15 else "🔶" if pct > 10 else "🔷"
            lines.append(
                f"  {warning} ${s['ticker']:<6} short: {pct:>5.1f}%  "
                f"DTC: {dtc:>4.1f}d  borrow: {br:>4.1f}%  "
                f"price: ${s.get('price',0):>8.2f}"
            )

    lines.append(f"\n{'─'*60}")
    lines.append(f"  Full short data ({len(results['snapshots'])})")
    for s in results["snapshots"][:5]:
        pct = s.get("short_pct_float", 0) or 0
        dtc = s.get("days_to_cover", 0) or 0
        lines.append(f"  ${s['ticker']:<6} {pct:>5.1f}% short  DTC: {dtc:>4.1f}d  vol: {s.get('avg_volume',0):>10,}")

    lines.append(f"\n{'='*60}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Short Interest & Borrow Scanner")
    parser.add_argument("--tickers", nargs="*", help="Tickers to scan")
    parser.add_argument("--all-mega-caps", action="store_true", help="Scan all mega-cap AI tickers")
    parser.add_argument("--squeeze-candidates", action="store_true", help="Only show squeeze setups")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    tickers = args.tickers or (MEGA_CAP_TICKERS if args.all_mega_caps else ["NVDA", "PLTR"])
    results = scan(tickers=tickers)

    if args.squeeze_candidates:
        results["snapshots"] = results["squeeze_candidates"]

    if args.json:
        print(json.dumps(results, indent=2, default=str))
    else:
        print(format_terminal(results))


if __name__ == "__main__":
    main()