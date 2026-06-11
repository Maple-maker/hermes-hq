# Claude Design Prompt — /relay Instagram Carousel

**Output:** 7 slide images, 1080×1080px, PNG or high-quality JPG
**Style:** Dark, sleek, sports-inspired editorial design. Think Nike running campaigns meets developer tool branding. See attached images as reference.
**Consistency rules across all slides:**
- Same background color on every slide: #0D0D0D (near-black)
- Same font family throughout: Inter or Space Grotesk (bold for headlines, regular for body)
- The amber baton icon appears on every slide as a recurring visual thread
- Model lane colors are sacred — never deviate: Haiku=slate #64748B, Sonnet=green #22C55E, Opus=blue #3B82F6, Fable 5=purple #A855F7
- Accent color for highlights, callouts, and the baton: amber #F5A623
- Each slide has a thin amber rule line separating the headline from the body
- Bottom-right corner of every slide: small "@jaidenrabatin" in 60% opacity white

---

## SLIDE 1 — Hook

**Composition:** Five vertical track lanes recede into the distance in perspective. Four lanes are dimly lit. The fifth lane (purple, Fable 5) is brightly lit — newly activated. The lanes are painted on a dark asphalt texture. At the bottom of the frame, in the foreground at the start line, an amber-glowing relay baton rests horizontally.

**Headline (top third, large, bold white):**
"Fable 5 just dropped."

**Subhead (below headline, smaller, amber #F5A623):**
"Here's how to get the most out of it — and every other model in the lineup."

**Body text (bottom third, white, regular weight, smaller):**
Claude Code gives you four models at different price points. The mistake? Throwing every task at the most expensive one. The unlock? A relay. Each model runs the leg it's actually best at. Fable 5 anchors — review, security, the merge gate. Nothing ships without it.

**Bottom tag (small, centered, 50% opacity white):**
↓ The 4×100 build pipeline ↓

---

## SLIDE 2 — What is RELAY?

**Composition:** Overhead/top-down view of a four-lane running track (like a drone shot). Five runners are positioned in their lanes, staggered — relay race formation. Each runner is a silhouette in their model color. A glowing amber baton is mid-air between the first and second runner — mid-handoff. Below the track, a horizontal bar shows the pipeline with model names and prices.

**Headline:**
"RELAY runs your idea through five Claude models in sequence."

**Subhead (amber):**
"Each does the job it's best at, for the cost it deserves."

**Pipeline diagram (centered, code-style monospace font, each segment color-coded):**

🔫 HAIKU → 🟡 SONNET → 🟢 SONNET → 🔵 OPUS → 🟣 FABLE 5
scaffold / grill+spec / design crew / build it / review+secure
$1/$5 / $3/$15 / $3/$15 / $5/$25 / $10/$50

**Small annotation below pipeline (60% opacity white):**
Input/output per million tokens. Cheap models front-loaded. Expensive models only on vetted ideas.

**Callout box (amber border, dark fill, positioned bottom-left):**
"Fable 5 isn't the star. It's the closer."

---

## SLIDE 3 — The Lineup

**Composition:** Five "athlete cards" arranged horizontally across the slide — sports trading card style. Each card has: a colored top border matching the model lane color, the model name in large bold text, the leg number and job title, and a one-line description. The Fable 5 card (rightmost) has a subtle purple glow behind it. Cards are slightly overlapped or connected by a thin amber line running behind them.

**Headline:**
"Every model has a job. None do what another can do cheaper."

**Card 1 (Haiku, slate top border):**
🔫 GUN · Haiku 4.5
Pulls flagged idea from Google Sheets, scaffolds project folder. Dumb, fast, cheap — zero thinking.

**Card 2 (Sonnet, green top border):**
🟡 LEG 1 · Sonnet 4.6
Interviews you. Grills on scope, problem, constraints. Writes locked spec. Issues GO / NO-GO.

**Card 3 (Sonnet, green top border):**
🟢 LEG 2 · Sonnet 4.6
Reads the locked spec. Designs the build crew of sub-agents. Writes the build plan. No re-scoping.

**Card 4 (Opus, blue top border):**
🔵 LEG 3 · Opus 4.8
Executes the build plan. Writes code. Best code generation — but only on ideas that survived the gates.

**Card 5 (Fable 5, purple top border, subtle glow behind):**
🟣 LEG 4 · Fable 5
Reviews against spec. Debugs. Full security pass. Issues MERGE verdict. Nothing ships without it.

---

## SLIDE 4 — Why Fable 5 Anchors

**Composition:** A single runner in the purple lane, in sharp focus, crossing the finish line. The runner's form is powerful — chest forward, arms driving. The finish tape is amber. Behind the runner, fading into the background, are the other four lanes (now empty — they've finished their legs). Overlaid on the right side of the image: a semi-transparent dark panel with a checklist.

**Headline:**
"Fable 5 closes the race."

**Subhead (amber):**
"Nothing hits a real repo until it signs off."

**Checklist panel (right side, white text, amber checkmarks):**
✓ Spec match verified
✓ Secrets exposed? Scanned
✓ Auth gaps? Checked
✓ Injection vectors? Tested
✓ Unsafe dependencies? Flagged
✓ MERGE verdict issued

**Four bullet points below the image (white, smaller):**
→ Gets better the longer the task runs — "The longer and more complex the task, the larger Fable 5's lead" (Anthropic, June 2026)
→ Self-improving via memory — persistent file-based memory boosts its performance 3× more than Opus 4.8. Every baton, spec, and build log feeds that loop.
→ Mythos-class context window — stays focused across millions of tokens. Holds the entire spec, agent files, build output, and every baton in one pass.
→ The MERGE gate — writes review report (CRITICAL → LOW, file:line). Full security pass. You approve. Then it merges. Not before.

**Bottom quote (amber, italic):**
"Opus builds it. Fable 5 decides if it ships."

---

## SLIDE 5 — The Gates

**Composition:** A horizontal timeline across the slide. Five dots representing the five legs, connected by a line. Two of the dots are enlarged into "gate" markers — Leg 1 (amber checkpoint flag) and Leg 4 (purple checkpoint flag). Below the timeline, a simple bar chart showing relative token cost per leg — Haiku is a tiny sliver, Sonnet legs are small, Opus is medium, Fable 5 is the largest bar. A red dashed line cuts across between Leg 1 and Leg 2, labeled "Most ideas stop here."

**Headline:**
"Two gates. One at the start, one at the finish."

**Gate 1 panel (left side, amber accent):**
🟡 GO / NO-GO · Leg 1, Sonnet 4.6
Value matrix: Impact · Effort · Urgency · Strategic Fit · Reversibility

≥ 18/25 → GO
12–17 → RESCOPE
< 12 → NO-GO (kill it here, cheap)

**Gate 2 panel (right side, purple accent):**
🟣 MERGE · Leg 4, Fable 5
Spec match? Security clean? No scope drift?
Fable 5 issues the final verdict.
Nothing merges until you approve.

**Bottom quote (white, centered):**
"Two models say no before code ships: Sonnet at the idea stage, Fable 5 at the merge stage."

---

## SLIDE 6 — Lane Discipline

**Composition:** Top-down track view again, but this time the focus is on the exchange zones between lanes. Each runner is looking ONLY forward — their gaze is a thin colored line projecting straight ahead. The baton exchange zones are highlighted in amber. Between lanes 1→2 and 2→3 and 3→4 and 4→5, a structured handoff block is shown as a small glowing code panel. Arrows between lanes flow one direction only — never backward.

**Headline:**
"Every leg writes a baton. The next leg reads ONLY that baton."

**Code block (centered, monospace, amber text on dark background, with border):**
```
CONTEXT HANDOFF — Leg 1 → Leg 2
─────────────────────────────
Project: PROJ-004
Locked decisions: scope, archetype, constraints
Verdict: GO (score 20/25)
DO NOT: do not re-scope; the spec is locked.
─────────────────────────────
```

**Four benefit bullets (white, two columns):**
• Opus can't "just add one more feature" — scope locked at Leg 1
• Fable 5 reviews against the spec, not against vibes
• Every decision traceable to a specific leg
• If Fable 5 catches a bug, Leg 3's build log is the source of truth

**Bottom quote (amber, italic):**
"Lane discipline is what separates a relay from a group chat."

---

## SLIDE 7 — CTA / Fire the Gun

**Composition:** Split layout. Left 60%: a clean terminal mockup showing `> fire the gun` with the relay pipeline animating beneath it. The terminal has a dark background with subtle scan lines. The cursor blinks. Below the terminal, the trigger phrases listed cleanly. Right 40%: a preview of the Notion page — a stylized "page" card with the RELAY title visible, and a QR code below it. Instagram handle "@jaidenrabatin" is prominent at the bottom.

**Headline:**
"Fire the gun."

**Subhead (amber):**
"Fable 5 is the anchor. Here's how you start the race."

**Terminal mockup (left side):**
```
> fire the gun

🔫 Haiku:    project scaffolded  ✓
🟡 Sonnet:   spec locked  ✓
🟢 Sonnet:   crew designed  ✓
🔵 Opus:     build complete  ✓
🟣 Fable 5:  review passed · MERGE ready
```

**Trigger phrases (below terminal, smaller white text):**
"fire the gun" · "start a relay" · "run relay on [idea]"
"grill me on this idea" · "pressure-test this before we build"
"take this through the legs"

**Notion preview card (right side):**
[Stylized card showing a page icon, "RELAY — The 4×100 Build Pipeline" title, and a few blurred lines of content. QR code below it linking to the Notion page.]

**Bottom (full width, centered):**
@jaidenrabatin · Full docs: grape-odometer-92e.notion.site · AEGIS toolchain

---

## Additional Design Specifications

**Color Reference Card:**
| Element | Hex |
|---------|-----|
| Background | #0D0D0D |
| White text | #FAFAFA |
| Amber accent (baton, highlights, amber text) | #F5A623 |
| Haiku lane / card border | #64748B |
| Sonnet lane / card border | #22C55E |
| Opus lane / card border | #3B82F6 |
| Fable 5 lane / card border | #A855F7 |
| Subtle text / rules | #FFFFFF at 40-60% opacity |

**Typography:**
- Headline: 48-56pt, bold (700), white #FAFAFA, tracking -0.5
- Subhead: 28-32pt, semibold (600), amber #F5A623
- Body: 18-22pt, regular (400), white #FAFAFA or 80% opacity, line height 1.4
- Code/monospace: 16-18pt, JetBrains Mono or Fira Code, amber #F5A623 on #1A1A1A background
- Small labels: 14pt, 50-60% opacity white, uppercase tracking +1

**Grid / Layout:**
- 48px safe margins on all sides
- Headline area: top 25% of slide
- Body area: middle 50%
- Footer/tag area: bottom 15%
- Thin horizontal amber rule (1px, 40% opacity) between headline and body on every slide

**Visual Motifs (recurring across all slides):**
1. The amber baton — appears on every slide, positioned differently but always present
2. Lane lines — thin colored lines (one per model color) that run horizontally or in perspective
3. The amber rule line separating headline from body
4. Small @jaidenrabatin in bottom-right corner, every slide

**Animation Notes (for Instagram Stories version):**
- Slide transitions: baton passes right-to-left or left-to-right between slides
- Slide 1: Fable 5's purple lane illuminates with a subtle glow animation
- Slide 3: Cards slide in one by one from the right, staggered 100ms
- Slide 4: Checklist items appear one by one with amber checkmarks animating in
- Slide 5: Gate markers pulse once on load
- Slide 7: Terminal cursor blinks, pipeline steps appear sequentially
