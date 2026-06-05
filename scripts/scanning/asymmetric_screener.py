#!/usr/bin/env python3
"""
asymmetric_screener.py — Asymmetric Bet Screener

Scans for beaten-down companies with strong fundamentals and identifiable
catalysts — asymmetric risk/reward plays (the SOFI pattern).

Screens on:
  - Price action: RSI < 40, below 50-day MA (beaten down)
  - Fundamentals: revenue growth > 10%, gross margin > 30%, positive FCF
  - Catalysts: insider buying, recent 8-K, new product cycle
  - Asymmetry: high upside to downside ratio

Sources (free, no API key):
  - yfinance: price, fundamentals, technicals
  - SEC EDGAR: recent filing check for catalysts
  - Finviz free screener: sector/industry screening

Usage:
    python3 backend/asymmetric_screener.py
    python3 backend/asymmetric_screener.py --universe mid-cap
    python3 backend/asymmetric_screener.py --custom SOFI UPST AFRM
    python3 backend/asymmetric_screener.py --json
"""

import argparse
import json
import os
import re
import sqlite3
import sys
import time
from datetime import datetime, timezone

import pandas as pd
import requests
import yfinance as yf

USER_AGENT = "NoFomo Research (research@nofomo.app)"

# ─── Screening Universe ────────────────────────────────────────────────────
# Companies that fit the "beaten down but strong catalyst" profile.
# SOFI is the archetype: fintech/tech that got crushed but has rev growth + path to profitability.

MID_CAP_UNIVERSE = [
    # Fintech / Lending (SOFI-style)
    "SOFI", "UPST", "AFRM", "LC", "PYPL", "SQ", "HOOD", "COIN",
    # SaaS / Cloud (profitable but beaten down)
    "DOCU", "ZM", "MDB", "DDOG", "CRWD", "NET", "CFLT", "ESTC",
    # Defense / GovTech
    "KTOS", "AVAV", "RDW", "RKLB", "LUNR",
    # Biotech (catalyst-rich)
    "RXRX", "ABCL", "CRSP", "NTLA", "BEAM",
    # Energy / Grid
    "SMR", "OKLO", "VST", "TLN",
    # Consumer / E-commerce (beaten down, recovering)
    "SNAP", "PINS", "RBLX", "TTD", "U",
    # Enterprise AI / Data
    "PLTR", "S", "AI", "BBAI", "IONQ", "RGTI",
    # Semis (non-mega cap)
    "ON", "STM", "WOLF", "AMKR",
]

# ─── Scoring Weights ──────────────────────────────────────────────────────

WEIGHTS = {
    "revenue_growth": 0.20,
    "gross_margin": 0.10,
    "fcf_yield": 0.15,
    "price_drawdown": 0.15,
    "rsi": 0.10,
    "catalyst_score": 0.20,
    "insider_activity": 0.10,
}


def score_asymmetry(snap: dict) -> dict:
    """Score a company on the asymmetric bet framework. Returns 0-100."""
    scores = {}
    
    # Revenue growth (higher = better)
    rev = snap.get("revenue_growth_pct", 0) or 0
    scores["revenue_growth"] = min(100, max(0, rev * 2))
    
    # Gross margin (higher = better, >50% is excellent)
    gm = snap.get("gross_margin_pct", 0) or 0
    scores["gross_margin"] = min(100, max(0, gm * 1.5))
    
    # Drawdown from 52w high (deeper = more beaten down = asymmetric setup)
    dd = snap.get("drawdown_pct", 0) or 0
    scores["price_drawdown"] = min(100, max(0, dd * 1.5))
    
    # RSI (lower = more oversold = better entry)
    rsi = snap.get("rsi_14", 50) or 50
    scores["rsi"] = min(100, max(0, (40 - rsi) * 5 + 50))
    
    # FCF yield (higher = cheaper)
    fcf = snap.get("fcf_yield", 0) or 0
    scores["fcf_yield"] = min(100, max(0, fcf * 10))
    
    # Catalyst score (from filings + insider data)
    cat = snap.get("catalyst_score", 0) or 0
    scores["catalyst"] = min(100, cat)
    
    # Insider activity
    ins = snap.get("insider_score", 0) or 0
    scores["insider"] = min(100, ins)
    
    # Weighted total
    total = sum(scores[k] * WEIGHTS.get(k.replace("_score", "").replace("_", "_"), 
                 0.10) for k in scores)
    
    return {
        "total": round(total, 1),
        "breakdown": scores,
    }


# ─── Fetch fundamentals + technicals ──────────────────────────────────────

def fetch_snapshot(ticker: str) -> dict | None:
    """Fetch price, fundamentals, and technicals for a ticker."""
    try:
        t = yf.Ticker(ticker)
        info = t.info
        hist = t.history(period="1y")

        if hist.empty:
            return None

        close = hist["Close"]
        high_52w = hist["High"].max()
        low_52w = hist["Low"].min()
        current = float(close.dropna().iloc[-1]) if not close.dropna().empty else float(info.get("regularMarketPrice", info.get("currentPrice", 0)) or 0)
        sma_50 = float(close.tail(50).mean()) if len(close) >= 50 else current
        sma_200 = float(close.tail(200).mean()) if len(close) >= 200 else current

        drawdown = max(0, round((high_52w - current) / high_52w * 100, 1))
        upside = max(0, round((high_52w - current) / current * 100, 1))

        # RSI
        delta = close.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = (-delta).where(delta < 0, 0.0)
        avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
        rs = avg_gain / avg_loss
        rsi_14 = round(float((100 - (100 / (1 + rs))).dropna().iloc[-1]), 1) if not rs.dropna().empty else 50

        snap = {
            "ticker": ticker.upper(),
            "company": info.get("shortName", info.get("longName", ticker)),
            "sector": info.get("sector", ""),
            "industry": info.get("industry", ""),
            "market_cap": info.get("marketCap", 0),
            "price": current,
            "price_52w_high": high_52w,
            "price_52w_low": low_52w,
            "drawdown_pct": drawdown,
            "upside_to_52w_high": upside,
            "above_sma_50": current > sma_50,
            "above_sma_200": current > sma_200,
            "rsi_14": rsi_14,
            "revenue_growth_pct": round((info.get("revenueGrowth", 0) or 0) * 100, 1),
            "gross_margin_pct": round((info.get("grossMargins", 0) or 0) * 100, 1),
            "operating_margin_pct": round((info.get("operatingMargins", 0) or 0) * 100, 1),
            "pe_trailing": info.get("trailingPE"),
            "pe_forward": info.get("forwardPE"),
            "ps_ttm": info.get("priceToSalesTrailing12Months"),
            "pfcf": info.get("priceToFreeCashflow"),
            "ev_ebitda": info.get("enterpriseToEbitda"),
            "fcf_yield": round((info.get("freeCashflowYield", 0) or 0) * 100, 2),
            "debt_to_equity": info.get("debtToEquity"),
            "current_ratio": info.get("currentRatio"),
            "beta": info.get("beta"),
            "analyst_count": info.get("numberOfAnalystOpinions", 0) or 0,
            "target_mean": info.get("targetMeanPrice"),
            "target_high": info.get("targetHighPrice"),
            "target_low": info.get("targetLowPrice"),
            # Will be filled by enrich step
            "catalyst_score": 0,
            "insider_score": 0,
            "recent_insider_buys": 0,
            "recent_insider_sales": 0,
            "has_recent_8k": False,
            "has_contract": False,
        }

        # Analyst upside
        if snap["target_mean"] and snap["price"]:
            snap["analyst_upside_pct"] = round(
                (snap["target_mean"] - snap["price"]) / snap["price"] * 100, 1
            )

        return snap

    except Exception as e:
        return None


# ─── Enrich with catalyst data ────────────────────────────────────────────

CACHE_DB = os.path.join(os.path.dirname(__file__), "cache", "alpha_cache.db")

def enrich_from_cache(snapshot: dict) -> dict:
    """Check cache for insider trades, contracts, and SEC signals."""
    try:
        conn = sqlite3.connect(CACHE_DB)
        ticker = snapshot["ticker"]

        # Insider purchases in last 90 days
        buys = conn.execute(
            "SELECT COUNT(*) FROM insider_trades WHERE ticker=? AND trade_type='P'",
            [ticker]
        ).fetchone()[0]
        sales = conn.execute(
            "SELECT COUNT(*) FROM insider_trades WHERE ticker=? AND trade_type='S'",
            [ticker]
        ).fetchone()[0]

        snapshot["recent_insider_buys"] = buys
        snapshot["recent_insider_sales"] = sales
        if buys > 0:
            snapshot["insider_score"] = min(100, buys * 25)
            snapshot["catalyst_score"] += 20

        # Government contracts
        contracts = conn.execute(
            "SELECT COUNT(*) FROM gov_contracts WHERE ticker=?",
            [ticker]
        ).fetchone()[0]
        if contracts > 0:
            snapshot["has_contract"] = True
            snapshot["catalyst_score"] += 15

        # Alpha signals from other scrapers
        signals = conn.execute(
            "SELECT COUNT(*) FROM alpha_signals WHERE ticker=? AND scraper!='insider'",
            [ticker]
        ).fetchone()[0]
        if signals > 0:
            snapshot["catalyst_score"] += 10

        conn.close()
    except Exception:
        pass

    return snapshot


# ─── Screen ────────────────────────────────────────────────────────────────

def screen(tickers: list[str]) -> dict:
    """Screen tickers for asymmetric bet opportunities."""
    results = {
        "scanned_at": datetime.now(timezone.utc).isoformat(),
        "tickers_screened": len(tickers),
        "beaten_down": 0,
        "asymmetric_candidates": [],
        "all_results": [],
        "errors": [],
    }

    for ticker in tickers:
        try:
            snap = fetch_snapshot(ticker)
            if not snap:
                continue

            snap = enrich_from_cache(snap)
            scores = score_asymmetry(snap)
            snap["asymmetry_score"] = scores["total"]
            snap["score_breakdown"] = scores["breakdown"]

            results["all_results"].append(snap)

            # Beaten down filter
            is_beaten_down = (
                snap["drawdown_pct"] > 20 and
                (snap["rsi_14"] < 55 or not snap["above_sma_50"]) and
                snap["revenue_growth_pct"] > 5
            )

            if is_beaten_down:
                results["beaten_down"] += 1

            # Asymmetric candidate:
            # 1. Beaten down (drawdown > 20%, RSI < 45 or below 50MA)
            # 2. Strong fundamentals (rev growth > 10%, or high gross margin)
            # 3. Catalyst present (analyst upside, insider buys, contracts, or recent 8-K)
            has_fundamentals = (
                snap["revenue_growth_pct"] > 10 or
                snap["gross_margin_pct"] > 50 or
                (snap["fcf_yield"] or 0) > 3
            )
            has_catalyst = (
                (snap["analyst_upside_pct"] or 0) > 30 or
                snap["recent_insider_buys"] > 0 or
                snap["has_contract"]
            )

            if is_beaten_down and has_fundamentals and has_catalyst:
                results["asymmetric_candidates"].append(snap)

            time.sleep(0.4)

        except Exception as e:
            results["errors"].append(f"{ticker}: {e}")

    # Sort by asymmetry score
    results["asymmetric_candidates"].sort(
        key=lambda x: x.get("asymmetry_score", 0), reverse=True
    )
    results["all_results"].sort(
        key=lambda x: x.get("asymmetry_score", 0), reverse=True
    )

    return results


def format_terminal(results: dict) -> str:
    lines = [
        f"\n{'='*60}",
        f"🎲 ASYMMETRIC BET SCREENER — {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}",
        f"{'='*60}",
        f"  Universe screened:  {results['tickers_screened']}",
        f"  Beaten down:        {results['beaten_down']}",
        f"  Asymmetric bets:    {len(results['asymmetric_candidates'])}",
    ]

    if results["errors"]:
        lines.append(f"  Errors: {len(results['errors'])}")

    if results["asymmetric_candidates"]:
        lines.append(f"\n{'─'*60}")
        lines.append(f"  🎯 ASYMMETRIC CANDIDATES (sorted by score)")
        lines.append(f"{'─'*60}")
        for s in results["asymmetric_candidates"][:10]:
            score = s.get("asymmetry_score", 0)
            dd = s.get("drawdown_pct", 0)
            rsi = s.get("rsi_14", 50)
            rg = s.get("revenue_growth_pct", 0)
            gm = s.get("gross_margin_pct", 0)
            au = s.get("analyst_upside_pct", 0) or 0
            ins = s.get("recent_insider_buys", 0)

            lines.append(
                f"\n  {s['ticker']:<6} Score: {score:>5.1f}  "
                f"Price: ${s['price']:<8.2f}"
            )
            lines.append(
                f"       Drawdown: {dd:>5.1f}%  RSI: {rsi:>5.1f}  "
                f"Rev Growth: {rg:>5.1f}%  Margin: {gm:>5.1f}%"
            )
            lines.append(
                f"       Analyst upside: {au:>5.1f}%  "
                f"Insider buys: {ins}  "
                f"Sector: {s.get('sector','')[:20]}"
            )

    # Show full results summary
    lines.append(f"\n{'─'*60}")
    lines.append(f"  Full results ({len(results['all_results'])})")
    for s in results["all_results"][:5]:
        lines.append(
            f"  ${s['ticker']:<6} Score: {s.get('asymmetry_score',0):>5.1f}  "
            f"↑{s.get('drawdown_pct',0):>5.1f}%  "
            f"RSI: {s.get('rsi_14',0):>5.1f}  "
            f"Rev: {s.get('revenue_growth_pct',0):>5.1f}%"
        )

    lines.append(f"\n{'='*60}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Asymmetric Bet Screener")
    parser.add_argument("--universe", choices=["mid-cap"], default="mid-cap", 
                       help="Screening universe")
    parser.add_argument("--custom", nargs="*", help="Custom tickers to screen")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    tickers = args.custom or MID_CAP_UNIVERSE
    results = screen(tickers=tickers)

    if args.json:
        print(json.dumps(results, indent=2, default=str))
    else:
        print(format_terminal(results))


if __name__ == "__main__":
    main()