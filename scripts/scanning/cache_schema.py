#!/usr/bin/env python3
"""
cache_schema.py — Shared SQLite Cache for all NoFomo scrapers.

Every scraper writes its results here. Subagents read from here.
Dedup key: (ticker, date) per scraper.

Usage:
    python3 backend/cache_schema.py                  # create tables
    python3 backend/cache_schema.py --drop           # drop + recreate
    python3 backend/cache_schema.py --stats          # show row counts
    python3 backend/cache_schema.py --query insider --tickers NVDA PLTR
"""

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone

CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
CACHE_DB = os.path.join(CACHE_DIR, "alpha_cache.db")


def get_conn() -> sqlite3.Connection:
    os.makedirs(CACHE_DIR, exist_ok=True)
    conn = sqlite3.connect(CACHE_DB)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


# ─── Table definitions ────────────────────────────────────────────────────

SCHEMA_SQL = """
-- Master index: every alpha signal across all scraper types
CREATE TABLE IF NOT EXISTS alpha_signals (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker          TEXT NOT NULL,
    scraper         TEXT NOT NULL,        -- 'insider', 'short_flow', 'gov_contracts', etc.
    signal_date     TEXT NOT NULL,         -- YYYY-MM-DD
    signal_type     TEXT NOT NULL,         -- 'insider_buy', 'short_spike', 'contract_award', etc.
    title           TEXT,                  -- human-readable summary
    score           REAL DEFAULT 0,        -- 0-100 alpha confidence
    detail          TEXT,                  -- JSON blob with scraper-specific data
    discovered_at   TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(ticker, scraper, signal_date, signal_type)
);

-- Insider trading (Form 4)
CREATE TABLE IF NOT EXISTS insider_trades (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker          TEXT NOT NULL,
    filing_date     TEXT NOT NULL,         -- YYYY-MM-DD
    owner_name      TEXT,
    owner_title     TEXT,
    trade_type       TEXT,                 -- 'P' = purchase, 'S' = sale
    shares          REAL,
    price           REAL,
    value           REAL,
    shares_owned    REAL,
    is_ceo          INTEGER DEFAULT 0,
    is_cfo          INTEGER DEFAULT 0,
    is_director     INTEGER DEFAULT 0,
    is_direct       INTEGER DEFAULT 0,    -- true if >10% owner
    is_ten_percent  INTEGER DEFAULT 0,
    raw_data        TEXT,                  -- full JSON from SEC
    discovered_at   TEXT DEFAULT (datetime('now')),
    UNIQUE(ticker, filing_date, owner_name, trade_type, shares)
);

-- Short interest & borrow data
CREATE TABLE IF NOT EXISTS short_flow (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker          TEXT NOT NULL,
    date            TEXT NOT NULL,         -- YYYY-MM-DD
    short_pct_float REAL,                  -- % of float shorted
    short_shares    REAL,
    avg_volume      REAL,
    days_to_cover   REAL,
    borrow_rate     REAL,                  -- current borrow fee %
    borrow_available INTEGER DEFAULT -1,   -- shares available to borrow
    short_ratio     REAL,
    put_call_ratio  REAL,
    cboe_data       TEXT,                  -- raw CBOE options data if available
    discovered_at   TEXT DEFAULT (datetime('now')),
    UNIQUE(ticker, date)
);

-- Government contracts (SAM.gov / USASpending)
CREATE TABLE IF NOT EXISTS gov_contracts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker          TEXT NOT NULL,
    award_date      TEXT NOT NULL,         -- YYYY-MM-DD
    agency          TEXT,
    department      TEXT,
    contract_value  REAL,                  -- dollar amount
    contract_type   TEXT,                  -- 'Firm Fixed Price', 'IDIQ', etc.
    description     TEXT,
    place_of_perf   TEXT,
    piid            TEXT,                  -- Procurement Instrument ID
    raw_data        TEXT,
    discovered_at   TEXT DEFAULT (datetime('now')),
    UNIQUE(piid)
);

-- 13F filings (institutional holdings)
CREATE TABLE IF NOT EXISTS f13_holdings (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker          TEXT NOT NULL,
    filing_date     TEXT NOT NULL,
    cik             TEXT,
    institution     TEXT,
    shares          REAL,
    value           REAL,
    shares_change   REAL,                  -- delta from prior quarter
    pct_portfolio   REAL,
    raw_data        TEXT,
    discovered_at   TEXT DEFAULT (datetime('now')),
    UNIQUE(ticker, cik, filing_date)
);

-- FDA calendar
CREATE TABLE IF NOT EXISTS fda_calendar (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker          TEXT NOT NULL,
    event_date      TEXT NOT NULL,         -- YYYY-MM-DD
    event_type      TEXT,                  -- 'PDUFA', 'AdCom', 'Trial Readout', etc.
    drug_name       TEXT,
    indication      TEXT,
    catalyst_type   TEXT,                  -- 'approval', 'rejection', 'delay'
    confidence      REAL,                  -- analyst consensus 0-100
    raw_url         TEXT,
    discovered_at   TEXT DEFAULT (datetime('now')),
    UNIQUE(ticker, event_date, event_type, drug_name)
);

-- Spinoff / corporate action tracker
CREATE TABLE IF NOT EXISTS spinoffs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_ticker   TEXT NOT NULL,
    child_name      TEXT,
    child_ticker    TEXT,
    announcement_date TEXT,
    ex_date         TEXT,
    record_date     TEXT,
    distribution_date TEXT,
    ratio           REAL,                  -- shares received per parent share
    status          TEXT,                  -- 'proposed', 'approved', 'completed'
    source          TEXT,
    raw_data        TEXT,
    discovered_at   TEXT DEFAULT (datetime('now')),
    UNIQUE(parent_ticker, child_name, announcement_date)
);

-- Patents
CREATE TABLE IF NOT EXISTS patents (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker          TEXT NOT NULL,
    patent_number   TEXT,
    patent_date     TEXT,
    title           TEXT,
    abstract        TEXT,
    assignee        TEXT,
    patent_type     TEXT,                  -- 'utility', 'design', 'provisional'
    ipc_class       TEXT,
    raw_data        TEXT,
    discovered_at   TEXT DEFAULT (datetime('now')),
    UNIQUE(patent_number)
);

-- Congress trading
CREATE TABLE IF NOT EXISTS congress_trades (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker          TEXT NOT NULL,
    trade_date      TEXT,
    disclosure_date TEXT,
    member_name     TEXT,
    chamber         TEXT,                  -- 'House', 'Senate'
    party           TEXT,
    state           TEXT,
    trade_desc      TEXT,                  -- 'Purchase', 'Sale'
    amount_range    TEXT,
    price           REAL,
    raw_data        TEXT,
    discovered_at   TEXT DEFAULT (datetime('now')),
    UNIQUE(ticker, member_name, trade_date, trade_desc)
);

-- Analyst coverage
CREATE TABLE IF NOT EXISTS analyst_coverage (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker          TEXT NOT NULL,
    date            TEXT NOT NULL,
    analyst_firm    TEXT,
    action          TEXT,                  -- 'initiate', 'upgrade', 'downgrade', 'pt_raise', 'pt_lower'
    rating          TEXT,
    price_target    REAL,
    prior_target    REAL,
    raw_data        TEXT,
    discovered_at   TEXT DEFAULT (datetime('now')),
    UNIQUE(ticker, date, analyst_firm, action)
);

-- Social sentiment (Reddit / StockTwits)
CREATE TABLE IF NOT EXISTS social_sentiment (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker          TEXT NOT NULL,
    date            TEXT NOT NULL,
    source          TEXT,                  -- 'reddit', 'stocktwits'
    mentions        INTEGER DEFAULT 0,
    sentiment_score REAL,                  -- -1.0 to 1.0
    top_keywords    TEXT,
    raw_data        TEXT,
    discovered_at   TEXT DEFAULT (datetime('now')),
    UNIQUE(ticker, date, source)
);

-- Indexes for fast subagent queries
CREATE INDEX IF NOT EXISTS idx_alpha_ticker ON alpha_signals(ticker);
CREATE INDEX IF NOT EXISTS idx_alpha_scraper ON alpha_signals(scraper);
CREATE INDEX IF NOT EXISTS idx_alpha_date ON alpha_signals(signal_date);
CREATE INDEX IF NOT EXISTS idx_insider_ticker ON insider_trades(ticker);
CREATE INDEX IF NOT EXISTS idx_short_ticker ON short_flow(ticker);
CREATE INDEX IF NOT EXISTS idx_contract_ticker ON gov_contracts(ticker);
CREATE INDEX IF NOT EXISTS idx_f13_ticker ON f13_holdings(ticker);
CREATE INDEX IF NOT EXISTS idx_fda_ticker ON fda_calendar(ticker);
CREATE INDEX IF NOT EXISTS idx_congress_ticker ON congress_trades(ticker);
CREATE INDEX IF NOT EXISTS idx_patent_ticker ON patents(ticker);
CREATE INDEX IF NOT EXISTS idx_social_ticker ON social_sentiment(ticker);
"""


def init_db(drop: bool = False):
    """Create all tables."""
    conn = get_conn()
    if drop:
        conn.executescript("""
            DROP TABLE IF EXISTS alpha_signals;
            DROP TABLE IF EXISTS insider_trades;
            DROP TABLE IF EXISTS short_flow;
            DROP TABLE IF EXISTS gov_contracts;
            DROP TABLE IF EXISTS f13_holdings;
            DROP TABLE IF EXISTS fda_calendar;
            DROP TABLE IF EXISTS spinoffs;
            DROP TABLE IF EXISTS patents;
            DROP TABLE IF EXISTS congress_trades;
            DROP TABLE IF EXISTS analyst_coverage;
            DROP TABLE IF EXISTS social_sentiment;
        """)
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    return conn


def get_stats() -> dict:
    """Return row counts for all tables."""
    conn = get_conn()
    tables = [
        "alpha_signals", "insider_trades", "short_flow", "gov_contracts",
        "f13_holdings", "fda_calendar", "spinoffs", "patents",
        "congress_trades", "analyst_coverage", "social_sentiment",
    ]
    stats = {}
    for t in tables:
        row = conn.execute(f"SELECT COUNT(*) as c FROM {t}").fetchone()
        stats[t] = row["c"]
    conn.close()
    return stats


def query_scraper(scraper: str, tickers: list[str] | None = None, limit: int = 20) -> list[dict]:
    """Query alpha_signals by scraper type, optionally filtered by tickers."""
    conn = get_conn()
    if tickers:
        placeholders = ",".join("?" for _ in tickers)
        rows = conn.execute(
            f"SELECT * FROM alpha_signals WHERE scraper=? AND ticker IN ({placeholders}) ORDER BY signal_date DESC LIMIT ?",
            [scraper] + tickers + [limit]
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM alpha_signals WHERE scraper=? ORDER BY signal_date DESC LIMIT ?",
            [scraper, limit]
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def main():
    parser = argparse.ArgumentParser(description="Alpha cache schema manager")
    parser.add_argument("--drop", action="store_true", help="Drop and recreate tables")
    parser.add_argument("--stats", action="store_true", help="Show row counts")
    parser.add_argument("--query", help="Query alpha signals by scraper name")
    parser.add_argument("--tickers", nargs="*", help="Filter by tickers")
    args = parser.parse_args()

    if args.drop or not os.path.exists(CACHE_DB):
        init_db(drop=args.drop)
        print(f"✅ Cache initialized: {CACHE_DB}")

    if args.stats:
        stats = get_stats()
        print(f"\n📊 Alpha Cache Stats")
        print(f"{'─'*40}")
        for table, count in sorted(stats.items()):
            print(f"  {table:<25} {count:>6} rows")
        print(f"\n  DB size: {os.path.getsize(CACHE_DB) // 1024} KB")

    if args.query:
        rows = query_scraper(args.query, tickers=args.tickers)
        print(f"\n🔍 {len(rows)} signals from '{args.query}'")
        for r in rows[:10]:
            print(f"  ${r['ticker']:<6} {r['signal_date']} [{r['signal_type']}] {r['title']}")

    if not any([args.drop, args.stats, args.query]):
        print("No action specified. Use --stats to view cache, --drop to reset.")


if __name__ == "__main__":
    main()