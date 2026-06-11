---
name: brand-new-day
description: "Run at the start of a new day or new planning session. Reads the latest /finish-line snapshot, does deep brainstorming and planning, and produces a structured plan of action for the day's Claude Code session. This is the steering wheel — it sets intent before any code is written."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [brand-new-day, planning, brainstorm, daily-plan, deep-work]
    related_skills: [finish-line, start-gun, relay, handoff]
---

# /brand-new-day — Deep Planning + Brainstorm Session

## Purpose

This is a **planning-first skill**. Before any code gets written, `/brand-new-day` forces a brainstorming and planning session that produces a clear, actionable plan. It reads yesterday's `/finish-line` snapshot, assesses where things stand, and produces the day's battle plan.

The rule: **no code gets written until the plan is approved.** This is how you steer rather than drift.

## When to Use

Trigger when:
- Starting a new day of work
- Jaiden says "new day" or "plan the day"
- Jaiden says "what should we work on today"
- After reading a `/finish-line` snapshot, before starting `/start-gun`
- Jaiden wants to brainstorm a new feature or pivot direction

## The Protocol

### Step 1: Read the Latest Snapshot

```bash
# Find the most recent finish-line for the project
ls -t /opt/data/hermes-hq/handoffs/snapshots/<project>-*-finish-line.md | head -1

# Read it
cat /opt/data/hermes-hq/handoffs/snapshots/<project>-<date>-finish-line.md
```

If no snapshot exists, read the handoff file instead:
```bash
cat /opt/data/hermes-hq/handoffs/<project>-handoff.md
```

If neither exists, this is a brand-new project — skip to Step 3.

### Step 2: Assess the Current State

Based on the snapshot, answer:

1. **What's the overall project health?** (green / yellow / red)
   - Green: on track, no blockers, building steadily
   - Yellow: some blockers or technical debt accumulating
   - Red: stuck, major blocker, or direction unclear

2. **What's the biggest risk right now?**
   - Technical risk (hard problem ahead)
   - Scope risk (creeping or unclear)
   - Dependency risk (waiting on something external)
   - Motivation risk (grind phase, need a win)

3. **What's the highest-leverage next action?**
   - What single thing, done today, would make everything else easier?
   - Not always the P0 from last session — sometimes the priority shifts.

### Step 3: Deep Brainstorm (The Planning Session)

This is the core of `/brand-new-day`. Spend real time here.

**If continuing an existing project:**

Review the P0/P1/P1 actions from the snapshot. For each:
- Is this still the right priority? Has anything changed?
- Can any of these be combined or batched?
- Is there a faster path to the same outcome?
- What did we learn since yesterday that changes the approach?

**If starting something new or pivoting:**

Run a structured brainstorm:

1. **Define the target:** What does "great" look like for today's session? Not the whole project — just today's slice.

2. **Explore 3 ways to get there:**
   - Path A: The safe, incremental approach
   - Path B: The ambitious approach (higher risk, higher reward)
   - Path C: The creative/left-field approach (what would someone totally different do?)

3. **Evaluate each path:**
   - How long will it take?
   - What could go wrong?
   - What does it unlock for tomorrow?
   - Does it require anything from Jaiden? (Get approvals early)

4. **Pick a path and defend it:** Why this one, today, given everything?

**If blocked:**

Brainstorm unblocking strategies:
1. What exactly is the blocker?
2. Is there a workaround that avoids the blocker entirely?
3. Can we work on something unblocked while waiting?
4. Does Jaiden need to act to unblock? (Tell him specifically what's needed.)

### Step 4: Produce the Day's Battle Plan

Write a structured plan to:
```
/opt/data/hermes-hq/handoffs/plans/<project>-<date>-plan.md
```

Use the template below.

### Step 5: Review with Jaiden

Present the plan. Not a wall of text — a concise summary:

> "Here's what I'm thinking for today:"
>
> **Target:** [one sentence]
>
> **Approach:** [which path from the brainstorm, and why]
>
> **Today's tasks:**
> 1. [specific task] — [estimated effort]
> 2. [specific task] — [estimated effort]
> 3. [specific task] — [estimated effort]
>
> **What I need from you:** [anything requiring Jaiden's input or approval]
>
> **Risk:** [the biggest thing that could derail today]
>
> "Sound good? Want to adjust anything?"

Wait for approval before proceeding to `/start-gun`.

### Step 6: Execute

Once approved, run `/start-gun` to begin the coding session. The plan becomes the session's north star. If the session goes off-plan, note why in the next `/finish-line`.

---

## Battle Plan Template

```markdown
# 🌅 /brand-new-day — <Project Name>
**Date:** <YYYY-MM-DD>
**Based on snapshot:** <path to finish-line>

---

## Current State Assessment
- **Project health:** 🟢 Green / 🟡 Yellow / 🔴 Red
- **Last session:** <1-line summary of what was done>
- **Biggest risk:** <what could derail progress>
- **Momentum:** building / steady / stalled

## Brainstorm: Paths Forward

### Path A — Safe / Incremental
<description>
- Pros: <list>
- Cons: <list>
- Estimated effort: <time>
- Unlocks: <what this enables next>

### Path B — Ambitious
<description>
- Pros: <list>
- Cons: <list>
- Estimated effort: <time>
- Unlocks: <what this enables next>

### Path C — Creative / Left-Field
<description>
- Pros: <list>
- Cons: <list>
- Estimated effort: <time>
- Unlocks: <what this enables next>

## Selected Path: <A | B | C>
**Why:** <reasoning>
**Trade-offs accepted:** <what you're giving up>

## Today's Battle Plan

### Primary Objective
<One sentence: what "win" looks like at end of today>

### Tasks (Ordered)
1. **<task>** — `<file path>:<line>` — <estimated effort>
   - Acceptance: <how you'll know it's done>
2. **<task>** — `<file path>` — <estimated effort>
   - Acceptance: <how you'll know it's done>
3. **<task>** — `<file path>` — <estimated effort>
   - Acceptance: <how you'll know it's done>

### Stretch Goals (if time allows)
- **<task>** — <context>
- **<task>** — <context>

## What I Need from Jaiden
- None / **<specific ask>** — <why it's needed today>

## Risks + Mitigations
- **<risk>** — <mitigation>
- **<risk>** — <mitigation>

## Definition of Done for Today
<[specific, testable criteria for a successful day]>
```

---

## Plan Storage

All plans live in:
```
/opt/data/hermes-hq/handoffs/plans/
├── nofomo-2026-06-11-plan.md
├── bet-2026-06-12-plan.md
├── thesis-2026-06-13-plan.md
└── ...
```

Plans are committed to git and visible to both Hermes and Claude.

## The Feedback Loop

The complete daily cycle:

```
/brand-new-day (plan)
    ↓ Jaiden approves
/start-gun (bootstrap)
    ↓ picks up task
/relay or direct work (build)
    ↓ code gets written
/finish-line (snapshot)
    ↓ saves state
/brand-new-day (next day, reads snapshot)
    ↓ plans based on reality
    → repeat
```

Each cycle tightens the feedback loop. The plan gets better because it's based on real snapshots, not guesses. The work gets more focused because it's based on a plan, not drift.

## Integration with Other Skills

| Skill | Relationship |
|---|---|
| `/finish-line` | `/brand-new-day` reads its output as input |
| `/start-gun` | Runs after `/brand-new-day` approves the plan |
| `/relay` | May be triggered by the plan if the task warrants a full relay |
| `/handoff` | New ideas from Jaiden feed into `/brand-new-day` planning |

## Common Pitfalls

1. **Skipping the brainstorm.** Going straight to "do the next P0" is lazy. The next P0 might not be the right move today. Think first.

2. **Planning in a vacuum.** The plan must be based on the `/finish-line` snapshot — real state, not assumed state.

3. **No Jaiden checkpoint.** Always present the plan and wait for approval. This is the steering wheel — Jaiden decides direction, decides priority.

4. **Overplanning.** The plan should take 10-15 minutes to make, not 2 hours. It's a battle plan, not a spec document.

5. **No flexibility.** If the session discovers something that invalidates the plan, note it in the `/finish-line` and adjust. Plans are hypotheses, not contracts.

6. **Forgetting stretch goals.** If the primary objectives finish early, what's next? Always have a backup.

## Shortcut: Quick Start

If Jaiden wants to skip deep diving and just start:

> "Skip the brainstorm — just pick up where we left off."

In this case:
1. Read the latest `/finish-line`
2. Take the P0 action as today's objective
3. Begin `/start-gun` immediately
4. Document in the `/finish-line` that planning was skipped

This is fine for routine continuation. Use the full brainstorm when starting something new, pivoting, or after a long break.
