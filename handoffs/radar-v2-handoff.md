# NoFomo — Radar V2 Signal Engine

> **Status:** 📋 Spec complete, ready for Claude Code build sessions (R1 → R4)
> **Location:** `backend/radar_v2/` (parallel-safe with beta sprint — zero iOS changes for R1-R3)
> **Full spec:** See `RADAR_V2_SIGNAL_ENGINE_SPEC.md` and `TRADING_AGENT_PROTOCOL.md` in this directory

---

## What It Is

A unified signal engine replacing the current scattered scraper-per-lane radar. Four pillars:

1. **One Signal schema** — every data source emits the same `Signal` object (one dataclass, many adapters)
2. **Deterministic scoring** — decay → category fusion → confluence multiplier → crowdedness penalty → 0-100 RadarScore (cheap filter first, expensive AI second)
3. **AI Council as researcher** — verifies evidence, argues bull/bear, outputs falsifiable thesis with invalidation conditions (not a voter)
4. **Backtest harness** — per-signal-type historical drift curves powering the live Reprice Gap metric

## Key Innovation: Reprice Gap

```
reprice_gap_pct = expected_drift_remaining − realized_move_since_event
```

"Events like this historically drifted +9% over 3 months; this has moved +1% in 6 days."

This is the "before the market reprices" value proposition turned into an auditable number.

## Signal Catalog (28 signal types, 8 categories)

| Category | Signals | Weight |
|----------|---------|--------|
| INSIDER_SMART_MONEY | Form 4 clusters, 13F adds, activist stakes, buybacks | 0.22 |
| GOVERNMENT_REGULATORY | Contracts, FDA/FAA/FCC, grants, export licenses | 0.18 |
| FUNDAMENTALS_INFLECTION | Revenue accel, earnings surprise, guidance, estimate revisions | 0.18 |
| COMMERCIAL_DEALS | Partnerships, hyperscaler flow-through, supply chain | 0.16 |
| STREET_POSITIONING | Analyst actions, coverage init, short interest | 0.12 |
| PRICE_VOLUME_STRUCTURE | Momentum, volume anomaly, valuation gap, overreaction reversal | 0.10 |
| NARRATIVE_SENTIMENT | News velocity, social buzz (weight-capped, fast decay) | 0.04 |
| CONTEXT_REGIME | VIX, Fed, macro (flags only — weight 0.0, never filters) | 0.00 |

## Architecture

```
ADAPTERS (one per source) → Signal schema → ENGINE (score.py) → gate ≥ 75 → AI COUNCIL → Supabase → feed/push
                                                              ↓
                                                    BACKTEST (offline) → drift curves → Reprice Gap
```

## Build Sessions

| Session | Scope | Parallel-safe? |
|---------|-------|----------------|
| R1 | Schema + free adapters (SEC EDGAR, Form 4, FMP earnings, USAspending) | ✅ Yes |
| R2 | Scoring engine + remaining adapters | ✅ Yes |
| R3 | Backtest harness + drift curves + Reprice Gap | ✅ Yes |
| R4 | Council explainability + Supabase migration + route wiring | ⚠️ Post-beta |

## House Rules

1. Regime flags annotate, never filter or rank (weight 0.0)
2. Narrative sentiment is weight-capped at 0.04 (stories follow signals, not vice versa)
3. Bear cases are sizing annotations, never ranking inputs
4. No backtest numbers ship without the harness producing them
5. LLM never types an order (trading agent protocol)

## Files

| File | Purpose |
|------|---------|
| `RADAR_V2_SIGNAL_ENGINE_SPEC.md` | Full 485-line architecture spec |
| `TRADING_AGENT_PROTOCOL.md` | Trading agent formula, sizing, exits, journal |

## Integration with Existing Code

- **Existing:** `backend/stock_data.py` (yfinance), `backend/sec_scanner.py` (SEC EDGAR)
- **New:** `backend/radar_v2/` (all new code — nothing in the beta path breaks)
- **Porting:** `sec_scraper.py` → `radar_v2/signals/adapters/sec_8k.py`; `supply_chain_mapper.py` → `radar_v2/signals/adapters/supply_chain.py`
- **Supabase:** New tables (`radar_opportunities` jsonb columns) — migration in R4 only
- **iOS:** Zero changes for R1-R3. R4 adds backward-compatible jsonb fields.

## Next Step

Drop `RADAR_V2_SIGNAL_ENGINE_SPEC.md` into the NoFomo repo root and run Session R1.
