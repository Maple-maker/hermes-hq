#!/usr/bin/env python3
"""
downstream_analyzer.py — Downstream Supply Chain Alpha Finder

Takes a ticker and finds the hidden downstream plays:
1. Who supplies them (supply chain)
2. Who partners with them (from SEC filings, earnings calls)
3. Analyzes each downstream company for asymmetric bet potential
4. User can also submit their own ticker to analyze

Usage:
    python3 backend/downstream_analyzer.py NVDA           # find downstream of NVDA
    python3 backend/downstream_analyzer.py NVDA --deep    # use all scanners
    python3 backend/downstream_analyzer.py NVDA --json
"""

import argparse
import json
import os
import re
import sqlite3
import sys
import time
from datetime import datetime, timezone

import yfinance as yf

USER_AGENT = "NoFomo Research (research@nofomo.app)"

# ─── Known supply chain maps ──────────────────────────────────────────────
# These are curated public-company relationships that the scanners may not catch.
# Each entry: megacap → [(downstream_ticker, role, confidence)]

SUPPLY_CHAIN_MAP = {
    "NVDA": [
        ("MRVL", "Custom AI chip partner (NVLink Fusion)", "high"),
        ("AVGO", "Networking silicon partner", "high"),
        ("MU", "HBM memory supplier", "high"),
        ("TSM", "Primary chip manufacturer", "high"),
        ("AMAT", "Semiconductor equipment supplier", "medium"),
        ("LRCX", "Etch/deposition equipment", "medium"),
        ("KLAC", "Wafer inspection equipment", "medium"),
        ("MRVL", "Silicon photonics collaboration", "high"),
    ],
    "MSFT": [
        ("NVDA", "AI infrastructure partner (Azure GPUs)", "high"),
        ("AMD", "Alternative AI chip provider", "medium"),
        ("ORCL", "Cloud interconnect partner", "medium"),
        ("SNOW", "Data cloud integration", "medium"),
    ],
    "AMZN": [
        ("NVDA", "AWS AI chip partner", "high"),
        ("AMD", "AWS alternative compute", "medium"),
        ("CRM", "AWS enterprise partner", "medium"),
        ("SNOW", "Data cloud on AWS", "medium"),
    ],
    "GOOGL": [
        ("NVDA", "Google Cloud GPU partner", "high"),
        ("PLTR", "Google Cloud AI partnership (expanded 2026)", "high"),
        ("CRM", "Google Cloud enterprise", "medium"),
    ],
    "TSLA": [
        ("MU", "Memory supplier for AI compute", "low"),
        ("NVDA", "AI training hardware", "medium"),
    ],
    "PLTR": [
        ("IBM", "IBM watsonx partnership", "medium"),
        ("GOOGL", "Google Cloud AI partnership (expanded 2026)", "high"),
    ],
    "AAPL": [
        ("TSM", "Primary chip manufacturer (A-series, M-series)", "high"),
        ("MU", "Memory supplier", "medium"),
        ("AVGO", "Wireless components", "high"),
    ],
    "META": [
        ("NVDA", "AI infrastructure partner", "high"),
        ("AMD", "Alternative AI chip provider", "medium"),
        ("MU", "Memory supplier for AI servers", "medium"),
    ],
    "SOFI": [
        ("LC", "Peer lending ecosystem partner", "medium"),
        ("UPST", "AI lending platform competitor/vendor", "medium"),
        ("AFRM", "BNPL ecosystem comparison", "low"),
    ],
    "LLY": [
        ("RXRX", "AI drug discovery partnership", "medium"),
        ("CRSP", "Gene editing therapy collaboration", "low"),
    ],
    "CRM": [
        ("NOW", "Enterprise AI platform integration", "medium"),
        ("SNOW", "Data cloud for CRM analytics", "medium"),
    ],
}

# ─── Cache path ───────────────────────────────────────────────────────────

CACHE_DB = os.path.join(os.path.dirname(__file__), "cache", "alpha_cache.db")


def query_cache_partners(ticker: str) -> list[dict]:
    """Query the cache for downstream partners of a ticker."""
    partners = []
    try:
        conn = sqlite3.connect(CACHE_DB)

        # Check alpha_signals for deals involving this ticker
        signals = conn.execute(
            "SELECT * FROM alpha_signals WHERE ticker=? AND scraper IN ('deal_scanner', 'downstream_scanner', 'primary_scanner')",
            [ticker]
        ).fetchall()

        for s in signals:
            try:
                detail = json.loads(s["detail"]) if isinstance(s["detail"], str) else {}
            except Exception:
                detail = {}

            # Try to find a partner name in the detail
            if "partner_name" in detail:
                partners.append({
                    "ticker": detail["partner_ticker"] or detail["partner_name"],
                    "name": detail["partner_name"],
                    "source": s["scraper"],
                    "signal": s["signal_type"],
                    "date": s["signal_date"],
                    "confidence": "medium",
                })

        conn.close()
    except Exception:
        pass
    return partners


# ─── Fetch downstream analysis ─────────────────────────────────────────────

def analyze_downstream_company(ticker: str, upstream: str, relationship: str) -> dict | None:
    """Run full asymmetric analysis on a downstream company."""
    try:
        t = yf.Ticker(ticker)
        info = t.info
        hist = t.history(period="1y")

        if hist.empty or hist["Close"].dropna().empty:
            return None

        close = hist["Close"].dropna()
        current = float(close.iloc[-1])
        high_52w = hist["High"].max()
        low_52w = hist["Low"].min()

        drawdown = max(0, round((high_52w - current) / high_52w * 100, 1))

        # RSI
        delta = close.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = (-delta).where(delta < 0, 0.0)
        avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
        rs = avg_gain / avg_loss
        rsi_14 = round(float((100 - (100 / (1 + rs))).dropna().iloc[-1]), 1) if not rs.dropna().empty else 50

        revenue_growth = round((info.get("revenueGrowth", 0) or 0) * 100, 1)
        gross_margin = round((info.get("grossMargins", 0) or 0) * 100, 1)
        pe_forward = info.get("forwardPE")
        ps_ttm = info.get("priceToSalesTrailing12Months")
        market_cap = info.get("marketCap", 0)

        # Asymmetry score components
        # Beaten-down factor (higher drawdown = more asymmetric)
        beaten_down_score = min(100, drawdown * 1.2)

        # Fundamentals factor
        fund_score = 0
        if revenue_growth > 20:
            fund_score += 40
        elif revenue_growth > 10:
            fund_score += 25
        elif revenue_growth > 5:
            fund_score += 10

        if gross_margin > 60:
            fund_score += 30
        elif gross_margin > 40:
            fund_score += 20
        elif gross_margin > 20:
            fund_score += 10

        if pe_forward and pe_forward < 25:
            fund_score += 20
        if ps_ttm and ps_ttm < 5:
            fund_score += 10

        # Total asymmetry score
        asym_score = round((beaten_down_score * 0.35) + (fund_score * 0.45) + 20, 1)

        # Market cap label
        def fmt_cap(c):
            if c is None: return "N/A"
            if c >= 1e12: return f"${c/1e12:.2f}T"
            if c >= 1e9: return f"${c/1e9:.1f}B"
            return f"${c/1e6:.0f}M"

        return {
            "ticker": ticker.upper(),
            "company": info.get("shortName", info.get("longName", ticker)),
            "upstream_ticker": upstream.upper(),
            "relationship": relationship,
            "sector": info.get("sector", ""),
            "industry": info.get("industry", ""),
            "market_cap_fmt": fmt_cap(market_cap),
            "market_cap": market_cap,
            "price": current,
            "drawdown_pct": drawdown,
            "rsi_14": rsi_14,
            "revenue_growth_pct": revenue_growth,
            "gross_margin_pct": gross_margin,
            "pe_forward": pe_forward,
            "ps_ttm": ps_ttm,
            "asymmetry_score": asym_score,
            "is_asymmetric": (
                drawdown > 25 and
                revenue_growth > 10 and
                gross_margin > 30
            ),
        }
    except Exception:
        return None


def analyze(ticker: str, deep: bool = False) -> dict:
    """Find and analyze downstream companies for a ticker."""
    ticker = ticker.upper()

    results = {
        "scanned_at": datetime.now(timezone.utc).isoformat(),
        "upstream_ticker": ticker,
        "upstream_name": "",
        "downstream_count": 0,
        "asymmetric_downstream": [],
        "all_downstream": [],
        "errors": [],
    }

    # Get upstream company name
    try:
        t = yf.Ticker(ticker)
        info = t.info
        results["upstream_name"] = info.get("shortName", info.get("longName", ticker))
    except Exception:
        results["upstream_name"] = ticker

    # Gather downstream partners
    downstream_list = []

    # 1. From supply chain map
    if ticker in SUPPLY_CHAIN_MAP:
        for d_ticker, rel, conf in SUPPLY_CHAIN_MAP[ticker]:
            downstream_list.append({
                "ticker": d_ticker,
                "relationship": rel,
                "confidence": conf,
                "source": "supply_chain_map",
            })

    # 2. From cache (deal_scanner / primary_scanner findings)
    if deep:
        cached = query_cache_partners(ticker)
        for c in cached:
            downstream_list.append({
                "ticker": c["ticker"],
                "relationship": c["name"],
                "confidence": c.get("confidence", "low"),
                "source": c["source"],
            })

    # Deduplicate
    seen = set()
    deduped = []
    for d in downstream_list:
        if d["ticker"] not in seen:
            seen.add(d["ticker"])
            deduped.append(d)

    # Analyze each downstream company
    for d in deduped:
        try:
            analysis = analyze_downstream_company(d["ticker"], ticker, d["relationship"])
            if analysis:
                analysis["relationship"] = d["relationship"]
                analysis["confidence"] = d["confidence"]
                analysis["source"] = d["source"]

                results["all_downstream"].append(analysis)
                results["downstream_count"] += 1

                if analysis["is_asymmetric"]:
                    results["asymmetric_downstream"].append(analysis)

            time.sleep(0.4)
        except Exception as e:
            results["errors"].append(f"{d['ticker']}: {e}")

    # Sort by asymmetry score
    results["asymmetric_downstream"].sort(key=lambda x: x["asymmetry_score"], reverse=True)
    results["all_downstream"].sort(key=lambda x: x["asymmetry_score"], reverse=True)

    return results


def format_terminal(results: dict) -> str:
    lines = [
        f"\n{'='*60}",
        f"🔗 DOWNSTREAM ANALYZER — {results['upstream_ticker']} ({results.get('upstream_name','')})",
        f"{'='*60}",
        f"  Downstream companies found: {results['downstream_count']}",
        f"  Asymmetric candidates:      {len(results['asymmetric_downstream'])}",
    ]

    if results["errors"]:
        lines.append(f"\n  ⚠️ Errors: {len(results['errors'])}")

    if results["asymmetric_downstream"]:
        lines.append(f"\n{'─'*60}")
        lines.append(f"  🎯 ASYMMETRIC DOWNSTREAM — Hidden Alpha")
        lines.append(f"{'─'*60}")
        for d in results["asymmetric_downstream"]:
            lines.append(
                f"\n  ${d['ticker']:<6} Score: {d['asymmetry_score']:>5.1f}  "
                f"Price: ${d['price']:<8.2f}  Cap: {d.get('market_cap_fmt','')}"
            )
            lines.append(
                f"       📎 {d['relationship']}"
            )
            lines.append(
                f"       Drawdown: {d['drawdown_pct']:>5.1f}%  "
                f"RSI: {d['rsi_14']:>5.1f}  "
                f"Rev: {d['revenue_growth_pct']:>5.1f}%  "
                f"Margin: {d['gross_margin_pct']:>5.1f}%"
            )

    if results["all_downstream"]:
        lines.append(f"\n{'─'*60}")
        lines.append(f"  Full downstream analysis ({len(results['all_downstream'])})")
        lines.append(f"{'─'*60}")
        for d in results["all_downstream"]:
            asym = "🎯" if d["is_asymmetric"] else "  "
            lines.append(
                f"  {asym} ${d['ticker']:<6} Score: {d['asymmetry_score']:>5.1f}  "
                f"↓{d['drawdown_pct']:>5.1f}%  "
                f"Rev: {d['revenue_growth_pct']:>5.1f}%  "
                f"Mgn: {d['gross_margin_pct']:>5.1f}%  "
                f"| {d['relationship'][:40]}"
            )

    lines.append(f"\n{'='*60}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Downstream Supply Chain Alpha Finder")
    parser.add_argument("ticker", help="Ticker to analyze (e.g. NVDA, SOFI, PLTR)")
    parser.add_argument("--deep", action="store_true", help="Also query cache for more partners")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    results = analyze(args.ticker, deep=args.deep)

    if args.json:
        print(json.dumps(results, indent=2, default=str))
    else:
        print(format_terminal(results))


if __name__ == "__main__":
    main()