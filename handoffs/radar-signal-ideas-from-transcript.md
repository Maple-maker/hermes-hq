# 📡 NoFomo Radar — Signal Ideas from Market Analysis Transcript

> **Source:** Instagram reel transcript (market analysis content)
> **Core theme:** Separating real bargains from value traps in a market where fear is rising but speculation is still alive
> **Application:** These become radar signals, scoring factors, and content angles for NoFomo

---

## 1. The "Beaten Down" Signal Framework

**Core idea:** When sentiment flips quickly, the first question isn't "what's falling?" — it's "which stocks are falling because the business is broken vs. which are falling because the market is nervous?"

**Radar application:**
- Track drawdowns from 52-week highs (20%, 30%, 40%+ thresholds)
- Cross-reference with fundamentals trajectory (revenue growth, FCF, margins)
- Score: "beaten down + fundamentals intact" = high potential; "beaten down + fundamentals broken" = value trap

**Signal types to add:**
- `drawdown_from_high` — % off 52-week high, categorized by severity
- `sentiment_flip_velocity` — how fast sentiment shifted (fear & greed index delta)
- `retail_participation_spike` — retail volume as % of total (high = potential reversal setup)

---

## 2. The "Valuation Reset" Signal

**Core idea:** A stock being down 40% doesn't mean it's cheap. Sometimes the valuation was insane. Sometimes the business is slowing. Sometimes it creates the exact opportunity long-term investors wait for.

**Radar application:**
- Compare current forward P/E to 5-year average (discount %)
- Compare price-to-sales to historical norm
- Reverse DCF: what growth rate is the market pricing in? (negative = extreme pessimism)

**Signal types to add:**
- `pe_vs_5yr_avg` — forward P/E discount to 5-year average
- `ps_vs_5yr_avg` — price-to-sales discount to 5-year average
- `reverse_dcf_implied_growth` — implied growth rate from current price (negative = potential opportunity)
- `margin_of_safety` — DCF fair value vs current price

---

## 3. The "Crowding vs. Opportunity" Signal

**Core idea:** When retail participation is high (20% of volume, double 2010 levels), it creates big moves in both directions. High retail + high sentiment = crowded trade = late. Low retail + high fundamentals = overlooked = opportunity.

**Radar application:**
- Track retail flow data (where available)
- Cross-reference with social mention count and news volume
- High crowding = penalty on score (existing crowdedness penalty in V2 spec)

**Signal types to add:**
- `retail_flow_zscore` — retail buying/selling vs 90-day baseline
- `social_mention_velocity` — social media mentions vs baseline
- `news_volume_spike` — article count vs baseline

---

## 4. The "IPO Cycle Warning" Signal

**Core idea:** Massive IPO cycles (like SpaceX at $2.1T) can be a warning signal for the broader market. When companies raise enormous amounts at enormous valuations, demand is strong — but supply usually follows. When the market stops absorbing new equity supply, risk/reward changes.

**Radar application:**
- Track IPO and secondary offering volume vs market cap
- High IPO volume + high valuations = caution flag (regime annotation, not filter)

**Signal types to add:**
- `ipo_secondary_volume` — total IPO + secondary offering volume (monthly)
- `ipo_valuation_extreme` — flag IPOs with revenue multiples >50x
- `equity_supply_pressure` — net new equity issuance vs market cap

---

## 5. The "Narrow Market" Signal

**Core idea:** The market is being driven by a narrow set of forces (AI investment + upper income consumer). If you strip out AI enablers, the rest of the market looks much weaker. This creates fragility.

**Radar application:**
- Track AI-enabler performance vs broad market
- Divergence = concentration risk flag
- When narrow leadership breaks, beaten-down non-AI stocks may be the opportunity

**Signal types to add:**
- `ai_enabler_vs_breadth` — AI winners performance vs equal-weight S&P 500
- `market_breadth_divergence` — % of stocks above 200-day MA
- `sector_concentration_risk` — HHI index of sector contribution to index returns

---

## 6. The "Great Company vs. Great Investment" Signal

**Core idea:** A company can be incredible, the founder can be incredible, the opportunity can be incredible — but if the valuation is too extreme, future returns can still disappoint. The question is never "is it a great company?" — it's "what am I paying today?"

**Radar application:**
- Revenue multiple comparison to peers (e.g., SpaceX at 125x revenue vs Alphabet at 12x)
- Flag stocks where revenue multiple is >2x sector median
- This is a sizing annotation (reduce size) not a filter

**Signal types to add:**
- `revenue_multiple_vs_peers` — stock's P/S vs sector median
- `story_vs_fundamentals_gap` — narrative strength (news/social) vs fundamentals trajectory
- `valuation_extreme_flag` — revenue multiple >3x sector median = caution

---

## 7. The "Fear & Greed Flip" Signal

**Core idea:** When sentiment flips quickly (greed to fear in one month), it creates dislocations. The fear & greed index dropping to 33 from greed = early-stage fear. This is when the best opportunities start appearing — but also when value traps are most dangerous.

**Radar application:**
- Track fear & greed index level and velocity
- Rapid flip = increase scanning frequency
- Cross-reference with beaten-down signals above

**Signal types to add:**
- `fear_greed_level` — current index value (0-100)
- `fear_greed_velocity` — 30-day change (rapid flip = flag)
- `sentiment_dislocation` — fear level + fundamentals mismatch (high fear + strong fundamentals = opportunity)

---

## 8. The "Software Sector Reset" Pattern

**Core idea:** The entire software sector is experiencing a massive valuation reset. Forward P/E ratios collapsing (Adobe from 28→9, Salesforce from 28→12, Intuit from 30→4). This creates a basket of potential opportunities — but also genuine business risk from AI disruption.

**Radar application:**
- Track software sector valuation reset as a basket
- Score individual software stocks on: valuation reset % + AI disruption risk + FCF trajectory
- High reset + low AI risk + strong FCF = top opportunities

**Signal types to add:**
- `software_valuation_reset` — sector-wide forward P/E compression %
- `ai_disruption_risk` — LLM classifier: is this software company's core product at risk from AI?
- `fcf_trajectory` — free cash flow growth trend (improving = positive)

---

## 9. The "Cleanest Risk/Reward" Ranking Methodology

**Core idea:** The #1 pick wasn't the one with the biggest upside — it was the one with the cleanest risk/reward. Mastercard: not the flashiest, but highest margins, network effects, long growth runway, and the market doesn't need heroic assumptions.

**Radar application:**
- Score stocks on "clean risk/reward" = margin of safety + business quality + growth consistency + low assumptions needed
- This becomes the primary ranking factor in the app

**Composite score factors:**
- Margin of safety (DCF vs price)
- Business quality (gross margin, FCF consistency, moat)
- Growth consistency (revenue growth stability, not just level)
- Assumptions reasonableness (reverse DCF implied growth vs historical)

---

## 10. Content Angles for NoFomo

From the transcript, here are content hooks that map to NoFomo's value prop:

| Hook | NoFomo Angle |
|------|-------------|
| "Is this stock cheap or a value trap?" | NoFomo's scoring engine separates broken businesses from market overreactions |
| "The market is being driven by AI — what about everything else?" | NoFomo scans 28 signal types, not just AI narratives |
| "Retail is 20% of volume — when they panic, opportunity appears" | NoFomo's crowding penalty identifies when retail panic creates mispricing |
| "Great company ≠ great investment" | NoFomo shows you the valuation, not just the story |
| "The software sector just reset — here's what's actually cheap" | NoFomo's sector-agnostic scoring finds value anywhere |
| "Fear is rising but speculation is still alive" | NoFomo's regime flags annotate without filtering — you see the full picture |

---

## Implementation Priority

**For Radar V2 build (R1-R4):**
1. Add `drawdown_from_high` signal (R1 — uses existing price data)
2. Add `pe_vs_5yr_avg` and `ps_vs_5yr_avg` (R2 — uses FMP fundamentals)
3. Add `reverse_dcf_implied_growth` (R2 — computed from DCF)
4. Add `fear_greed_level` and `fear_greed_velocity` (R1 — free API)
5. Add `ai_disruption_risk` classifier (R4 — LLM-based)
6. Add `software_valuation_reset` basket tracker (R2 — computed)
7. Add `ipo_secondary_volume` tracker (R2 — free data)
8. Add `market_breadth_divergence` (R2 — computed from market data)

**For content pipeline:**
- Use the 10 content angles above for Instagram carousels
- "Value trap vs. real bargain" is the strongest hook format
- "The market is doing X, but here's what the data says" is the second strongest

---

*Added to AEGIS: 2026-06-12. Source: Instagram reel transcript — market analysis, beaten-down stocks, valuation methodology.*
