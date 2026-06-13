# /reel-to-carousel — Instagram Reel Transcript → Carousel Templates

> **Use when:** You paste an Instagram reel transcript, caption, or describe a reel's hook pattern.
> **Output:** Structured carousel templates that replicate the hook style for NoFomo/Thesis.

---

## Purpose

Instagram reels can't be scraped directly (JS-rendered SPA). This skill works around that by:

1. You paste the transcript/caption (copy from Instagram → paste here)
2. The skill extracts the **hook structure** (the pattern that makes it work)
3. The skill generates **carousel templates** using that exact hook style
4. Output is ready for Claude Design or Canva

---

## The Workflow

### Step 1: Receive the Transcript

When Jaiden pastes a reel transcript, caption, or description, capture it exactly.

**What to look for:**
- The **hook** (first 1-3 seconds — the pattern interrupt)
- The **structure** (how the information is organized)
- The **CTA** (how it closes — comment trigger, follow, etc.)
- The **tone** (provocative, educational, humorous, direct)

### Step 2: Extract the Hook Structure

Identify the pattern. Common hook structures:

| Pattern | Example | Why It Works |
|---------|---------|--------------|
| **Tier-ranking** | "S-tier habits" / "F-tier mistakes" | Creates curiosity through contrast |
| **How-to** | "How to spot alpha before everyone else" | Promises specific knowledge |
| **Myth-bust** | "Stop doing X. Do Y instead." | Challenges assumptions |
| **List** | "3 things that separate pros from amateurs" | Scannable, promise of value |
| **Provocation** | "Most people are doing this wrong." | Triggers ego/defensiveness |
| **Story** | "I lost $10K doing this. Here's what I learned." | Emotional hook |
| **Contrast** | "F-tier vs S-tier" | Binary framing creates engagement |

### Step 3: Generate Carousel Templates

Using the extracted hook structure, generate 3 variations for NoFomo and 3 for Thesis.

**Each template includes:**
- **Slide 1 (Hook):** The pattern interrupt — must stop the scroll
- **Slide 2 (Info):** 2 short bullets with the key information
- **Slide 3 (CTA):** App value prop + comment trigger word

### Step 4: Output Format

Output in this exact format for each template:

```
## [App] — Variation [N]: "[Hook phrase]"

**Slide 1 (Hook):**
> [Hook text]

**Slide 2 (Info):**
> → [Bullet 1]
> → [Bullet 2]

**Slide 3 (CTA):**
> [One-line value prop]
> **Comment "[TRIGGER WORD]" and I'll send you the app.**
```

---

## Example: S-Tier Hook (from @levelup.withliam)

**Input (transcript):**
> "S-tier habits. Most people do F-tier habits and wonder why they're not successful. Here are the S-tier habits you need to adopt..."

**Extracted structure:**
- Hook: "S-tier [topic]" — tier-ranking creates contrast
- Pattern: Rank things into tiers (S = good, F = bad)
- Tone: Direct, slightly provocative, no fluff

**Output:** See `content/s-tier-hook-templates.md` for the full 6 variations.

---

## Example: "How to be good at X" (from Max Johnson)

**Input (transcript):**
> "How to be good at spotting alpha. Most people find out when CNBC covers it. By then, the move is already done. Here's what you need to know..."

**Extracted structure:**
- Hook: "How to be good at X" — promises specific knowledge
- Pattern: Hook → 2 info bullets → CTA
- Tone: Educational, direct, slightly provocative

**Output:** See `content/nofomo-thesis-carousel-templates.md` for the full 6 variations.

---

## Rules

1. **Always extract the hook structure first.** Don't just copy the content — understand the pattern.
2. **Generate 3 NoFomo + 3 Thesis variations** per hook style.
3. **Keep slides scannable.** Max 2 bullets per info slide. Short sentences.
4. **CTA must include a comment trigger word.** This is the engagement mechanic.
5. **Match the tone of the original hook.** If it's provocative, be provocative. If it's educational, be educational.
6. **Output is paste-ready for Claude Design.** No explanation needed — just the templates.

---

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `/handoff` | If the reel contains an idea worth building, hand it off |
| `/vault-check` | File the transcript + templates in the vault for future reference |
| `/brand-new-day` | Use templates in content planning |

---

*Part of the AEGIS content pipeline. Built by @jaidenrabatin.*
