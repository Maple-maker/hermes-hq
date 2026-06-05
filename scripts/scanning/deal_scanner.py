#!/usr/bin/env python3
"""
deal_scanner.py — Partnership & Deal Flow Scanner

Polls free RSS feeds (Google News) for partnership, deal, and supply-chain
announcements involving mega-cap companies. Detects downstream partners and
flags them as opportunities.

Usage:
    python3 backend/deal_scanner.py                          # scan all
    python3 backend/deal_scanner.py --json                   # JSON output
    python3 backend/deal_scanner.py --hours 6                # look back 6h
    python3 backend/deal_scanner.py --watchlist NVDA PLTR    # focused scan
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from typing import Optional

import feedparser
import requests
from bs4 import BeautifulSoup

# ─── Configuration ────────────────────────────────────────────────────────

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
HEADERS = {"User-Agent": USER_AGENT}

# ─── Mega-cap AI & Compute Watchlist ─────────────────────────────────────

# Companies aggressive in the AI buildout — large caps + private giants
WATCHLIST = {
    # AI chip / compute infrastructure
    "NVDA": {"name": "NVIDIA", "aliases": ["nvidia", "nvidia corporation"]},
    "AMD": {"name": "AMD", "aliases": ["amd", "advanced micro devices", "advanced micro"]},
    "AVGO": {"name": "Broadcom", "aliases": ["broadcom", "broadcom inc"]},
    "MRVL": {"name": "Marvell", "aliases": ["marvell", "marvell technology"]},
    "MU": {"name": "Micron", "aliases": ["micron technology", "micron", " micron "], "exclude": ["municipal", "community", "museum"]},
    "TSM": {"name": "TSMC", "aliases": ["tsmc", "taiwan semiconductor"]},
    "INTC": {"name": "Intel", "aliases": ["intel", "intel corporation"]},
    # Hyperscalers / cloud
    "MSFT": {"name": "Microsoft", "aliases": ["microsoft", "microsoft corp"]},
    "AMZN": {"name": "Amazon", "aliases": ["amazon", "amazon.com", "amazon web services", "aws"]},
    "GOOGL": {"name": "Google/Alphabet", "aliases": ["google", "alphabet", "google cloud", "gcp"]},
    "META": {"name": "Meta", "aliases": ["meta", "meta platforms", "facebook"]},
    "AAPL": {"name": "Apple", "aliases": ["apple", "apple inc"]},
    "ORCL": {"name": "Oracle", "aliases": ["oracle", "oracle corp", "oci"]},
    # Auto / robotics
    "TSLA": {"name": "Tesla", "aliases": ["tesla", "tesla inc"]},
    # Defense / government
    "PLTR": {"name": "Palantir", "aliases": ["palantir", "palantir technologies"]},
    # Human longevity / biotech
    "LLY": {"name": "Eli Lilly", "aliases": ["eli lilly", "lilly", "eli lilly and company"]},
    # Enterprise AI
    "CRM": {"name": "Salesforce", "aliases": ["salesforce", "salesforce.com"]},
    "NOW": {"name": "ServiceNow", "aliases": ["servicenow"]},
    "SNOW": {"name": "Snowflake", "aliases": ["snowflake", "snowflake inc"]},
    "IBM": {"name": "IBM", "aliases": ["ibm", "international business machines"]},
}

# Private giants to monitor (no ticker, but their partners are signal)
PRIVATE_GIANT_ALIASES = [
    "openai", "open ai", "chatgpt",
    "anthropic", "claude ai",
    "spacex", "space exploration",
    "databricks",
    "anduril",
    "scale ai",
    "coreweave",
    "xai", "x ai",
    "perplexity",
    "cohere",
    "mistral ai", "mistral",
]

# Build reverse lookup: alias → ticker
_ALIAS_TO_TICKER: dict[str, str] = {}
for ticker, info in WATCHLIST.items():
    for alias in info["aliases"]:
        _ALIAS_TO_TICKER[alias.lower().strip()] = ticker
    _ALIAS_TO_TICKER[ticker.lower()] = ticker
    _ALIAS_TO_TICKER[info["name"].lower()] = ticker

for alias in PRIVATE_GIANT_ALIASES:
    _ALIAS_TO_TICKER[alias.lower().strip()] = "PRIVATE"

# Exclusion words per ticker
_EXCLUDES: dict[str, list[str]] = {}
for ticker, info in WATCHLIST.items():
    if "exclude" in info:
        _EXCLUDES[ticker] = info["exclude"]


def is_excluded(ticker: str, text: str) -> bool:
    """Check if a match should be excluded based on context."""
    text_lower = text.lower()
    for ex in _EXCLUDES.get(ticker, []):
        if ex.lower() in text_lower:
            return True
    return False


# ─── Deal keywords ────────────────────────────────────────────────────────

DEAL_KEYWORDS = [
    "partnership", "partner", "strategic alliance", "collaboration",
    "supply agreement", "joint venture", "team up", "teaming",
    "selected", "chooses", "choose", "expands partnership",
    "awarded contract", "named exclusive", "design win",
    "framework agreement", "memorandum of understanding", "mou",
    "invests in", "acquire", "acquisition", "to acquire",
    "merger", "merge with",
    "deployment", "implement", "rolls out",
    "deepens relationship", "renewed agreement",
    "qualified supplier", "approved supplier",
]

DEAL_KEYWORDS_PATTERN = re.compile("|".join(re.escape(k) for k in DEAL_KEYWORDS), re.IGNORECASE)

# ─── RSS Sources (Free, No API Key) ───────────────────────────────────────

RSS_FEEDS = [
    {
        "name": "Business — Deals & Partnerships",
        "url": "https://news.google.com/rss/search?q=partnership+OR+acquisition+OR+%22supply+agreement%22+OR+%22strategic+alliance%22+OR+%22joint+venture%22+OR+%22qualified+supplier%22+OR+%22design+win%22&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "AI & Compute Infrastructure",
        "url": "https://news.google.com/rss/search?q=AI+OR+%22artificial+intelligence%22+OR+%22data+center%22+OR+%22cloud+computing%22+OR+%22semiconductor%22+partnership+OR+deploy&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "Defense & Government AI",
        "url": "https://news.google.com/rss/search?q=defense+OR+%22government+contract%22+OR+%22department+of+defense%22+OR+DARPA+OR+%22national+security%22+AI+OR+autonomous+contract+OR+award&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "Biotech & Longevity",
        "url": "https://news.google.com/rss/search?q=FDA+OR+biotech+OR+%22drug+approval%22+OR+%22clinical+trial%22+OR+longevity+OR+%22gene+therapy%22+OR+%22cell+therapy%22+approval+OR+partnership&hl=en-US&gl=US&ceid=US:en",
    },
    # Per-company feeds for our watchlist
    {
        "name": "NVIDIA deals",
        "url": "https://news.google.com/rss/search?q=NVIDIA+partnership+OR+partner+OR+acquisition+OR+%22supply+agreement%22&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "Microsoft partnerships",
        "url": "https://news.google.com/rss/search?q=Microsoft+partnership+OR+%22strategic+alliance%22+OR+acquires&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "Amazon/AWS deals",
        "url": "https://news.google.com/rss/search?q=Amazon+AWS+OR+%22Amazon+Web+Services%22+partnership+OR+%22cloud+deal%22+OR+%22infrastructure+agreement%22&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "Palantir contracts",
        "url": "https://news.google.com/rss/search?q=Palantir+contract+OR+partner+OR+%22government+contract%22+OR+%22AI+partnership%22&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "Google Cloud deals",
        "url": "https://news.google.com/rss/search?q=%22Google+Cloud%22+OR+%22Google+AI%22+partnership+OR+%22enterprise+AI%22+OR+%22cloud+migration%22&hl=en-US&gl=US&ceid=US:en",
    },
]

# ─── Company Extraction ────────────────────────────────────────────────────

def extract_mentioned_companies(text: str) -> list[tuple[Optional[str], str, str]]:
    """Extract company names from text that match our watchlist."""
    found = []
    text_lower = text.lower()

    # Also check the raw text for dot-prefixed tickers like $NVDA
    dollar_tickers = re.findall(r'\$([A-Z]{1,5})\b', text)
    for dt in dollar_tickers:
        if dt in WATCHLIST:
            found.append((dt, WATCHLIST[dt]["name"], f"${dt}"))

    for alias, ticker in _ALIAS_TO_TICKER.items():
        if alias in text_lower:
            if ticker == "PRIVATE":
                found.append((None, alias.title(), alias))
            elif not is_excluded(ticker, text):
                company_name = WATCHLIST[ticker]["name"]
                found.append((ticker, company_name, alias))

    # Deduplicate
    seen = set()
    deduped = []
    for item in found:
        key = (item[0], item[1])
        if key not in seen:
            seen.add(key)
            deduped.append(item)
    return deduped


def resolve_downstream_pair(title: str, summary: str, found_companies: list) -> list[dict]:
    """Given a press release and known companies, identify the *other* company."""
    combined = f"{title} {summary}"
    pairs = []

    partner_patterns = [
        r"(?:partners?\s+(?:with\s+)?)\"?'?([A-Z][A-Za-z0-9.\s&]+?)\"?'?(?:\s+for|\s+to|\s+in|\s+on|$|\.)",
        r"(?:selected|chosen|chooses?)\s+['\"]?([A-Z][A-Za-z0-9.\s&]+?)['\"]?(?:\s+for|\s+as|\s+to|$|\.)",
        r"(?:acquires?|to acquire)\s+(?:of\s+)?['\"]?([A-Z][A-Za-z0-9.\s&]+?)['\"]?",
        r"(?:agreement|contract)\s+(?:with\s+)?['\"]?([A-Z][A-Za-z0-9.\s&]+?)['\"]?",
    ]

    for pattern in partner_patterns:
        for match in re.finditer(pattern, combined, re.IGNORECASE):
            partner_name = match.group(1).strip()
            if len(partner_name) > 3 and len(partner_name) < 80:
                partner_lower = partner_name.lower()
                is_known = any(
                    cname and cname.lower() in partner_lower
                    for _, cname, _ in found_companies
                )
                if not is_known:
                    pairs.append({
                        "downstream_name": partner_name,
                        "resolved_ticker": None,
                        "is_private": None,
                    })

    return pairs


# ─── SEC Ticker Lookup ─────────────────────────────────────────────────────

_SEC_TICKER_CACHE: dict[str, str] = {}

def _load_sec_tickers():
    """Load SEC company_tickers.json for ticker resolution."""
    global _SEC_TICKER_CACHE
    if _SEC_TICKER_CACHE:
        return
    try:
        resp = requests.get(
            "https://www.sec.gov/files/company_tickers.json",
            headers=HEADERS, timeout=15
        )
        if resp.ok:
            data = resp.json()
            for v in data.values():
                _SEC_TICKER_CACHE[v["ticker"].upper()] = v.get("title", "")
    except Exception:
        pass


def resolve_ticker(company_name: str) -> Optional[str]:
    """Try to find a ticker for an unknown company name."""
    if not company_name or len(company_name) < 2:
        return None

    name_lower = company_name.lower().strip()

    if name_lower in _ALIAS_TO_TICKER:
        val = _ALIAS_TO_TICKER[name_lower]
        return None if val == "PRIVATE" else val

    _load_sec_tickers()
    for ticker, sec_name in _SEC_TICKER_CACHE.items():
        if sec_name and name_lower in sec_name.lower():
            return ticker

    # Try the name as a ticker directly
    ticker_candidate = re.sub(r'[^A-Za-z]', '', company_name).upper()[:5]
    if ticker_candidate and len(ticker_candidate) <= 5 and ticker_candidate in _SEC_TICKER_CACHE:
        return ticker_candidate

    return None


# ─── Feed Parsing ──────────────────────────────────────────────────────────

def parse_rss_entry(entry, source_name: str) -> dict | None:
    """Parse an RSS entry and filter for deals."""
    title = entry.get("title", "")
    summary = entry.get("summary", "") or entry.get("description", "") or ""
    link = entry.get("link", "")
    
    if isinstance(link, dict):
        link = link.get("href", "")

    published = entry.get("published", "") or entry.get("updated", "") or ""
    summary_text = BeautifulSoup(summary, "html.parser").get_text() if summary else ""
    combined = f"{title} {summary_text}".lower()

    if not DEAL_KEYWORDS_PATTERN.search(combined):
        return None
    if len(title) < 20:
        return None

    return {
        "source": source_name,
        "title": title,
        "summary": summary_text[:500],
        "url": link,
        "published": published,
    }


# ─── Main Scan ─────────────────────────────────────────────────────────────

def scan(hours: int = 24) -> dict:
    """Run the deal scanner across all RSS feeds."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    results = {
        "scanned_at": datetime.now(timezone.utc).isoformat(),
        "lookback_hours": hours,
        "feeds_polled": 0,
        "entries_found": 0,
        "deals_detected": 0,
        "deals": [],
        "errors": [],
    }

    for feed_config in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_config["url"])
            if feed.bozo and not feed.entries:
                results["errors"].append(f"Bad feed: {feed_config['name']}")
                continue

            results["feeds_polled"] += 1

            for entry in feed.entries:
                parsed = parse_rss_entry(entry, feed_config["name"])
                if not parsed:
                    continue

                results["entries_found"] += 1
                title = parsed["title"]
                summary = parsed["summary"]

                mentioned = extract_mentioned_companies(f"{title} {summary}")
                downstream = resolve_downstream_pair(title, summary, mentioned)

                if mentioned or downstream:
                    deal = {
                        "title": title,
                        "summary": summary[:400],
                        "url": parsed["url"],
                        "source": parsed["source"],
                        "published": parsed["published"],
                        "companies_found": [
                            {"ticker": t, "name": n} for t, n, _ in mentioned
                        ],
                        "downstream_partners": [],
                    }

                    for dp in downstream:
                        ticker = resolve_ticker(dp["downstream_name"])
                        is_private = None
                        if ticker is None:
                            if dp["downstream_name"].lower() in PRIVATE_GIANT_ALIASES:
                                is_private = True
                        deal["downstream_partners"].append({
                            "name": dp["downstream_name"],
                            "resolved_ticker": ticker,
                            "is_private": is_private,
                        })

                    results["deals"].append(deal)
                    results["deals_detected"] += 1

            time.sleep(0.5)

        except Exception as e:
            results["errors"].append(f"Feed '{feed_config['name']}': {e}")

    results["deals"].sort(key=lambda d: sum(
        1 for p in d["downstream_partners"] if p["resolved_ticker"]
    ), reverse=True)

    return results


# ─── Output Formatting ──────────────────────────────────────────────────────

def format_terminal(results: dict) -> str:
    """Pretty-print results for terminal."""
    lines = [
        f"\n{'='*60}",
        f"🔍 DEAL SCANNER — {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}",
        f"{'='*60}",
        f"  Feeds polled:  {results['feeds_polled']}",
        f"  Entries read:  {results['entries_found']}",
        f"  Deals found:   {results['deals_detected']}",
        f"  Lookback:      {results['lookback_hours']}h",
    ]

    if results["errors"]:
        lines.append(f"\n  ⚠️ Errors:")
        for e in results["errors"]:
            lines.append(f"     {e}")

    if not results["deals"]:
        lines.append(f"\n  No deals detected in this window.")
        return "\n".join(lines)

    # Show top deals with resolved downstream partners first
    downstream_deals = [d for d in results["deals"] if any(p["resolved_ticker"] for p in d["downstream_partners"])]
    known_deals = [d for d in results["deals"] if any(c["ticker"] for c in d["companies_found"])]
    other_deals = [d for d in results["deals"] if d not in downstream_deals and d not in known_deals]

    if downstream_deals:
        lines.append(f"\n{'─'*60}")
        lines.append(f"  ⭐ DOWNSTREAM PARTNERS DETECTED ({len(downstream_deals)})")
        lines.append(f"{'─'*60}")
        for deal in downstream_deals[:10]:
            known_str = ", ".join(f"${c['ticker']}" for c in deal["companies_found"] if c["ticker"])
            downstream_str = ", ".join(
                f"{p['name']} → ${p['resolved_ticker']}" for p in deal["downstream_partners"]
                if p["resolved_ticker"]
            )
            lines.append(f"\n  📰 {deal['title'][:90]}")
            lines.append(f"     Known: {known_str}")
            lines.append(f"     🔗 Downstream: {downstream_str}")
            lines.append(f"     {deal['url'][:100]}")

    if known_deals:
        lines.append(f"\n{'─'*60}")
        lines.append(f"  🏢 KNOWN COMPANIES IN DEALS ({len(known_deals)})")
        lines.append(f"{'─'*60}")
        for deal in known_deals[:10]:
            known_str = ", ".join(f"${c['ticker']}" for c in deal["companies_found"] if c["ticker"])
            private_str = ", ".join(c["name"] for c in deal["companies_found"] if not c["ticker"])
            tags = known_str
            if private_str:
                tags += f" + private: {private_str}"
            lines.append(f"\n  📰 {deal['title'][:90]}")
            lines.append(f"     {tags}")
            lines.append(f"     {deal['url'][:100]}")

    if other_deals:
        lines.append(f"\n{'─'*60}")
        lines.append(f"  📡 Other ({len(other_deals)}) — no resolved tickers")
        lines.append(f"{'─'*60}")

    lines.append(f"\n{'='*60}")
    return "\n".join(lines)


# ─── CLI ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Partnership & Deal Flow Scanner")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--hours", type=int, default=24, help="Lookback hours (default: 24)")
    args = parser.parse_args()

    results = scan(hours=args.hours)

    if args.json:
        print(json.dumps(results, indent=2, default=str))
    else:
        print(format_terminal(results))

    return results


if __name__ == "__main__":
    main()