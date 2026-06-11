# Claude Design Prompt — /handoff Instagram Carousel

**Output:** 7 slide images, 1080×1080px, PNG or high-quality JPG
**Style:** Dark, sleek, pipeline/editorial design. Think logistics/supply chain meets developer tool branding. Conveyor belt / package delivery metaphor.
**Consistency rules across all slides:**
- Same background color on every slide: #0D0D0D (near-black)
- Same font family throughout: Inter or Space Grotesk (bold for headlines, regular for body)
- The amber baton icon appears on every slide as a recurring visual thread
- Accent color for highlights, callouts, and the baton: amber #F5A623
- Each slide has a thin amber rule line separating the headline from the body
- Bottom-right corner of every slide: small "@jaidenrabatin" in 60% opacity white

---

## SLIDE 1 — Hook

**Composition:** A dark warehouse / command center. Three stations are visible in a pipeline: a Telegram icon (left), a Google Drive icon (center), and a Claude Code terminal (right). A glowing amber baton is mid-air between the first and second station. The pipeline stretches left to right with subtle motion lines.

**Headline (top third, large, bold white):**
"You have an idea. Here's how it becomes code."

**Subhead (below headline, smaller, amber #F5A623):**
"Without you re-explaining it to three different tools."

**Body text (bottom third, white, regular weight, smaller):**
You share an idea on Telegram. Hermes structures it, writes it to a Google Drive task queue, and Claude Code picks it up — with full context, zero re-explaining. The handoff is the baton. If the baton is sloppy, the whole relay fails.

**Bottom tag (small, centered, 50% opacity white):**
↓ The idea-to-code pipeline ↓

---

## SLIDE 2 — What is /handoff?

**Composition:** Top-down view of a three-station pipeline. Station 1: Telegram chat bubble with an idea inside. Station 2: Google Drive spreadsheet (the queue). Station 3: Claude Code terminal with a cursor blinking. Arrows connect them left to right. A glowing amber baton sits at each arrow junction.

**Headline:**
"/handoff is the baton pass from AEGIS to Claude Code."

**Subhead (amber):**
"Idea in Telegram → structured task in Google Drive → Claude Code builds it."

**Pipeline diagram (centered, code-style monospace font):**

💬 TELEGRAM → 📋 GOOGLE DRIVE → 💻 CLAUDE CODE
idea shared → task queued → code written
Hermes writes → Drive CSV → /start-gun picks up

**Small annotation below pipeline (60% opacity white):**
No re-explaining. No scrolling chat history. No "what was I building again?"

**Callout box (amber border, dark fill, positioned bottom-left):**
"The handoff is the baton. If the baton is sloppy, the whole relay fails."

---

## SLIDE 3 — The 5 Steps

**Composition:** Five horizontal "package tracking" cards — like a shipping tracker. Each card has a step number, an icon, and a one-line description. The cards are connected by a thin amber line running behind them left to right. Each card lights up in sequence.

**Headline:**
"5 steps. Zero ambiguity."

**Card 1 (amber accent):**
1️⃣ ACKNOWLEDGE
Hermes reads your idea. Asks 2-3 clarifying questions if vague. Never just says "relayed."

**Card 2 (amber accent):**
2️⃣ CONFIRM
"Do you want to hand this off to Claude Code?" — always asks before writing.

**Card 3 (amber accent):**
3️⃣ WRITE TASK
Writes to Google Drive CSV: title, description, priority, project, acceptance criteria.

**Card 4 (amber accent):**
4️⃣ CREATE ASSETS
Handoff file, Google Drive folder, spec document — whatever the project needs.

**Card 5 (amber accent):**
5️⃣ CONFIRM & REPORT
Tells you: task ID, priority, where it lives, what happens next.

---

## SLIDE 4 — Baton Quality

**Composition:** Side-by-side comparison. Left: a crumpled, broken baton with red X — labeled "Bad handoff." Right: a clean, glowing amber baton with green checkmark — labeled "Good handoff." Below each, a code-style block showing what the task looks like.

**Headline:**
"A good handoff task has 5 things. A bad one has none."

**Bad handoff (left, red-tinted):**
```
Title: "New feature"
Description: "Build something cool"
Priority: (blank)
Project: (blank)
Context: (none)
```

**Good handoff (right, green-tinted):**
```
Title: "AERO — Army Equipment Readiness Optimizer"
Description: "Searchable database of equipment
faults with NSN output. End vision: AR mobile
app for real-time fault identification."
Priority: 1 (High)
Project: AERO
Context: See handoffs/aero-handoff.md
```

**Bottom quote (amber, italic):**
"Claude can't build what it can't understand. The handoff IS the spec."

---

## SLIDE 5 — The Full Flow

**Composition:** A circular diagram — the complete daily cycle. Four nodes in a ring: Telegram → Google Drive → Claude Code → Working Code → back to Telegram. The amber baton travels along the ring. At the Claude Code node, a small "/relay" badge appears.

**Headline:**
"The full flow: idea to code in one loop."

**Flow nodes (clockwise from top):**
💬 Jaiden shares idea on Telegram
↓
🤖 Hermes (/handoff) structures + queues it
↓
📋 Google Drive task queue + handoff file
↓
🔫 Claude Code (/start-gun) picks it up
↓
🏃 /relay builds it (4-leg multi-model)
↓
✅ Working code (git + Drive)
↓
💬 Jaiden reviews → new idea → repeat

**Bottom quote (white, centered):**
"Every idea gets tracked. Every task gets context. Nothing falls through the cracks."

---

## SLIDE 6 — What Claude Sees

**Composition:** A Claude Code terminal mockup. The terminal shows the /start-gun bootstrap sequence: reading the task queue, reading the handoff file, checking git status, claiming the task. The terminal has a dark background with subtle scan lines. The cursor blinks.

**Headline:**
"Here's what Claude sees when it picks up your idea."

**Terminal mockup (centered, monospace, green text on dark background):**
```
> /start-gun

📋 Reading task queue...
→ Task #3: AERO — Fault-finding DB
→ Priority: 1 (High)
→ Status: pending

📄 Reading handoff file...
→ Project: AERO
→ Context: West Point AERO paper
→ Acceptance: searchable DB, NSN output

🔍 Checking git status...
→ Branch: main
→ Clean working tree

✅ Claiming task #3...
→ Status: in_progress
→ Ready to build.
```

**Bottom quote (amber, italic):**
"No re-explaining. No scrolling. No 'what was I building?' Just load and go."

---

## SLIDE 7 — CTA / Start Handing Off

**Composition:** Split layout. Left 60%: a clean Telegram chat mockup showing a user sending an idea, and Hermes responding "Do you want to hand this off?" Right 40%: a preview of the Notion page with the full documentation. Instagram handle "@jaidenrabatin" at the bottom.

**Headline:**
"Start handing off."

**Subhead (amber):**
"Every idea deserves a clean handoff."

**Telegram mockup (left side):**
```
You: I want to build a searchable database
for army equipment faults. Soldiers could
look up any fault by name or NSN.

Hermes: That's a great idea. A few questions:
- What's the primary data source?
- Who's the end user — soldiers or mechanics?
- Any tech preferences?

You: TM manuals as source. Soldiers.
No tech preference.

Hermes: Got it. Do you want to hand this off
to Claude Code?

You: Yes.

Hermes: ✅ Handed off: 'BET — Automated
Evaluation and Repair Organizer' (Task #3,
Priority 1). Claude will pick it up at the
next session via /start-gun.
```

**Trigger phrases (below mockup, smaller white text):**
"hand this off" · "relay: [idea]" · "I want to build X" · "add this to the queue"

**Notion preview card (right side):**
[Stylized card: "/handoff — Baton Pass from AEGIS to Claude Code" with blurred content lines]

**Bottom (full width, centered):**
@jaidenrabatin · Full docs: [Notion link] · AEGIS toolchain

---

## Additional Design Specifications

**Color Reference Card:**
| Element | Hex |
|---------|-----|
| Background | #0D0D0D |
| White text | #FAFAFA |
| Amber accent (baton, highlights) | #F5A623 |
| Telegram blue | #0088CC |
| Drive green | #34A853 |
| Claude orange | #D97757 |
| Subtle text / rules | #FFFFFF at 40-60% opacity |

**Typography:**
- Headline: 48-56pt, bold (700), white #FAFAFA, tracking -0.5
- Subhead: 28-32pt, semibold (600), amber #F5A623
- Body: 18-22pt, regular (400), white #FAFAFA or 80% opacity, line height 1.4
- Code/monospace: 16-18pt, JetBrains Mono or Fira Code, green #22C55E on #1A1A1A background
- Small labels: 14pt, 50-60% opacity white, uppercase tracking +1

**Grid / Layout:**
- 48px safe margins on all sides
- Headline area: top 25% of slide
- Body area: middle 50%
- Footer/tag area: bottom 15%
- Thin horizontal amber rule (1px, 40% opacity) between headline and body on every slide

**Visual Motifs (recurring across all slides):**
1. The amber baton — appears on every slide, positioned differently but always present
2. Pipeline/conveyor lines — thin lines connecting stages left to right
3. The amber rule line separating headline from body
4. Small @jaidenrabatin in bottom-right corner, every slide
