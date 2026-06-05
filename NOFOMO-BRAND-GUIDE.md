# NoFomo — Brand Style Guide

> Every social post, email, and landing page should feel like it came from the same app.
> Dark. Sharp. Data-dense. Financial but not Wall Street. AI-native but not sci-fi.

---

## 1. Color Palette

```
Background:   #0A0A0F    Deep void black — the canvas
Card:         #12121A    Subtle lift from background
Elevated:     #1A1A26    Hover/active surfaces

Bull/Mint:    #00FF88    Electric mint — upside, buy, green
Bear/Red:     #FF3B5C    Clean red — downside, sell, risk
Tier 1:       #FFD700    Gold — exceptional, rare, 10x+
Tier 2:       #00BFFF    Electric blue — high conviction
AI/Accent:    #7B61FF    Purple — intelligence, AI, the council

Text Primary: #FFFFFF    White
Text Second:  #8888AA    Muted lavender-gray
Text Muted:   #565676    Deeper gray — captions, labels

Border:       #FFFFFF @ 6% opacity    Barely there
Border Strong:#FFFFFF @ 14% opacity   Section dividers
```

**Rule:** backgrounds are never pure black, they're `#0A0A0F` (blue-tinted black). Cards are never outlined — depth comes from the 8% brightness lift (`#12121A` vs `#0A0A0F`). Borders are 6% opacity white — seen, not read.

---

## 2. Typography

| Context | Font | Weight | Example |
|---|---|---|---|
| Ticker symbols | SF Mono | Semibold | `NVDA` `MSTR` `CRVO` |
| Financial numbers | SF Mono | Semibold | `$311.23` `+142%` `91/100` |
| Headlines | SF Pro | Bold | "No Fomo" |
| Body / BLUF | SF Pro | Regular, 15pt | Thesis paragraphs |
| Labels / captions | SF Pro | Medium, 10-12pt | "BUY ZONES" "COUNCIL" |
| Uppercase labels | SF Pro | Medium, tracking +0.6 | "BLUF · BOTTOM LINE UP FRONT" |

**Rule:** financial figures are **always monospaced**. It signals "this is data, not opinion." Ticker symbols are monospaced uppercase without a `$` prefix in titles (`NVDA` not `$NVDA`), but get `$` in body text and metrics.

---

## 3. Visual Language — The Component Vocabulary

### Cards
- Radius: 18pt
- Inner padding: 17pt (regular) / 14pt (compact)
- Background: `#12121A`
- Border: 0.5px, `#FFFFFF` at 6% opacity
- No shadow — depth comes from color lift, not drop shadows
- Press state: scale to 0.992x over 120ms

### Badges & Chips
- Tier 1: gold background at 14% opacity, gold border at 35%, text "T1 EXCEPTIONAL"
- Tier 2: blue background at 14% opacity, blue border at 35%, text "T2 HIGH CONVICTION"
- Triple Signal: gold bolt icon + "TRIPLE SIGNAL" in mono
- Verdict chips: green/red dot + model name + BULL/BEAR in mono
- Radius: 6-7pt. Height: 22-26pt. Background always semi-transparent color.

### Score Gauge
- Circular ring: tier-colored arc (gold/blue), gray track ring at 7% opacity
- Center: score number in mono, e.g. `91`
- Bars style alternative: just the number, tier-colored, no arc

### Buy Zones
- Three equal-width cards: Aggressive · Base · Conservative
- Each: label in uppercase muted, price in mono white
- Background: `#1A1A26` elevated. Border: standard 0.5px.
- Locked state: 7px blur + 55% opacity + green "Unlock buy zones" pill overlay

### AI Council Row
- "COUNCIL" label in uppercase muted
- Three model chips: Gemini · DeepSeek · CIO
- Each chip: color dot + name, colored border at 22% opacity

### Metrics Strip
- 4-column grid: Price · Upside · Mkt Cap · Prob
- Upside in mint green. Probability in purple.
- Numbers mono, labels uppercase 9.5pt tracking +0.6
- Background: `#1A1A26`, corner radius 10pt

### BLUF Section
- "BLUF · BOTTOM LINE UP FRONT" — 10.5pt, muted, tracking +0.6
- Body text: 16pt, white, line spacing 4pt
- This is the most important text on the card — the entire thesis in 2-3 sentences

### Detail Sheet
- Drawer-style with grabber capsule at top
- Ticker in mono 26pt with `+XX%` upside in mint
- Expandable sections with chevron rotation
- Bull/Bear case blocks: 2px colored left border, verdict chip, body text
- Bear case: red flags as bullet list, invalidation trigger in red-tinted box

---

## 4. Layout Principles

### Depth, Not Lines
Cards are separated by the 8% brightness difference between `#12121A` and `#0A0A0F`, not by borders. When a border is needed, it's white at 6% opacity — "visible if you look, invisible if you scan."

### Data Density
Every card carries: tier badge, triple-signal indicator, ticker, company name, sector, score gauge, BLUF thesis, 4-metric strip, AI council row (3 models), and 3 buy zone prices. That's ~20 data points in a ~350pt card. The design works because:
- Hierarchy is strict: badges → ticker → thesis → metrics → council → buy zones
- Color carries meaning: gold = exceptional, mint = upside, red = risk, purple = AI
- Mono vs sans-serif separates data from labels
- Uppercase tracking on labels makes them recede

### Spacing Scale
- Screen padding: 20pt
- Card padding: 17pt
- Compact padding: 14pt
- Card gap: 14pt
- Chip/section gap: 7-8pt
- Divider padding: 16pt vertical

---

## 5. Content Voice

### The NoFomo Tone
- **Confident, not cocky.** "We found it. Here's the evidence." Not "THIS WILL 10X."
- **Data-first.** Every claim has a number. Every number has a source.
- **Educational, not advisory.** "The market appears to be missing X" not "You should buy Y."
- **Calm urgency.** The catalyst is real, the opportunity is real — but panic sells nothing.
- **AI-native, not AI-hype.** "4 models debated this. 3 voted bull." Not "AI-powered stock picks!!"

### Hook Formulas
All hooks use tension + specificity + curiosity gap:

```
"This 8-K dropped at 4:01pm and nobody noticed."
"One filing. $4.1M in insider buys. Zero headlines."
"3 AIs said bull. 1 said bear. Here's the tiebreaker."
"We scanned 12,400 filings today. 3 cleared the 75/100 bar."
"Similar catalysts moved this stock 8% last time. Pro users saw it first."
```

### The "Cite Your Source" Rule
Every claim about a stock or catalyst must reference a primary source: SEC filing URL, earnings transcript, insider Form 4. This is both legal cover ("educational, not advice") and a trust signal. The app does it. The content should too.

---

## 6. Marketing Asset Templates

### Social Carousel (6-10 slides)
```
Slide 1:  Hook + NoFomo wordmark
Slide 2:  Ticker in mono, tier badge, score gauge
Slide 3:  "What happened" — BLUF in 2-3 sentences
Slide 4:  Metrics strip (Price · Upside · Mkt Cap · Prob)
Slide 5:  AI Council row (3 models, verdicts)
Slide 6:  "What to watch" — catalyst + date
Slide 7:  Source citation (SEC filing link)
Slide 8:  CTA — "Free weekly catalyst report, link in bio"
```

Background: `#0A0A0F`. All text matches app typography (SF Mono for numbers, SF Pro for body). Tier badges and verdict chips match app colors exactly.

### Email Template
```
Subject: <TICKER> — <one-line thesis>

Header: NoFomo wordmark
Section 1: Tier badge + ticker + score gauge
Section 2: BLUF thesis (full paragraph)
Section 3: Metrics grid
Section 4: AI Council verdict (3 model chips)
Section 5: Source citation
Footer: "Not financial advice. Educational content only."
        Unsubscribe link
```

### Landing Page Sections
1. Hero: "Catalysts before the crowd." Dark background, animated score gauge.
2. How it works: 3 steps — scan → debate → verdict (icon + 1 line each)
3. Sample card: Annotated screenshot with callouts to key elements
4. AI Council visual: 3 model chips with verdict dots
5. Pricing: Free / Pro / Annual cards with feature comparison
6. Footer: "Not financial advice" disclaimer

---

## 7. Quick Reference Checklist

When creating any NoFomo content:

- [ ] Background is `#0A0A0F`, not pure black
- [ ] Financial numbers use mono font
- [ ] Mint green (`#00FF88`) = upside/bull, red (`#FF3B5C`) = risk/bear
- [ ] Gold (`#FFD700`) = Tier 1 only, blue (`#00BFFF`) = Tier 2 only
- [ ] Purple (`#7B61FF`) = AI/council/intelligence
- [ ] Cards have 18pt radius, no drop shadows
- [ ] Every data claim has a source citation
- [ ] "Not financial advice" appears somewhere
- [ ] Hook uses tension + specificity, not hype
- [ ] One CTA per piece, not five
