# /brand-new-day — Deep Planning + Brainstorm Session

> **Plug-and-play skill for Claude Code.** Copy this file into your project's `.claude/skills/` directory and reference it in your AGENTS.md.

---

## Purpose

Before any code gets written, `/brand-new-day` forces a brainstorming and planning session that produces a clear, actionable plan. It reads yesterday's `/finish-line` snapshot, assesses where things stand, and produces the day's battle plan.

**The rule: no code gets written until the plan is approved.**

This is the steering wheel — it sets intent before any code is written.

---

## The Protocol

### Step 1: Read the Latest Snapshot

```bash
# Find the most recent finish-line for the project
ls -t handoffs/snapshots/<project>-*-finish-line.md | head -1
```

If no snapshot exists, read the handoff file instead:
```bash
cat handoffs/<project>-handoff.md
```

If neither exists, this is a brand-new project — skip to Step 3.

### Step 2: Assess the Current State

Based on the snapshot, answer:

1. **Project health:** 🟢 Green / 🟡 Yellow / 🔴 Red
2. **Biggest risk right now:** Technical? Scope? Dependency? Motivation?
3. **Highest-leverage next action:** What single thing, done today, would make everything else easier?

### Step 3: Deep Brainstorm

**If continuing an existing project:**
- Review P0/P1/P1 actions from the snapshot
- Is this still the right priority?
- Can any be combined or batched?
- Is there a faster path to the same outcome?

**If starting something new or pivoting:**

1. **Define the target:** What does "great" look like for today's session?
2. **Explore 3 ways to get there:**
   - **Path A:** The safe, incremental approach
   - **Path B:** The ambitious approach (higher risk, higher reward)
   - **Path C:** The creative/left-field approach
3. **Evaluate each path:** Time? Risks? What does it unlock?
4. **Pick a path and defend it.**

### Step 4: Produce the Day's Battle Plan

Write a structured plan to `handoffs/plans/<project>-<date>-plan.md`:

```markdown
# 🌅 /brand-new-day — <Project Name>
**Date:** <YYYY-MM-DD>

## Current State Assessment
- **Project health:** 🟢 Green / 🟡 Yellow / 🔴 Red
- **Biggest risk:** <what could derail progress>

## Brainstorm: Paths Forward

### Path A — Safe / Incremental
<description> | Pros | Cons | Effort

### Path B — Ambitious
<description> | Pros | Cons | Effort

### Path C — Creative / Left-Field
<description> | Pros | Cons | Effort

## Selected Path: <A | B | C>
**Why:** <reasoning>

## Today's Battle Plan
1. **<task>** — <file path> — <effort> — <acceptance criteria>
2. **<task>** — <file path> — <effort> — <acceptance criteria>

## What I Need from Jaiden
- None / **<specific ask>** — <why it's needed today>

## Risks + Mitigations
- **<risk>** — <mitigation>

## Definition of Done for Today
<[specific, testable criteria]>
```

### Step 5: Review with Human

Present the plan concisely:

> "Here's what I'm thinking for today:"
> **Target:** [one sentence]
> **Approach:** [which path, and why]
> **Today's tasks:** [3 specific tasks]
> **What I need from you:** [anything requiring input]
> **Risk:** [biggest derailer]
> "Sound good? Want to adjust anything?"

**Wait for approval before proceeding.**

### Step 6: Execute

Once approved, run `/start-gun` to begin the coding session.

---

## The Daily Cycle

```
/brand-new-day (plan)
    ↓ Human approves
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

Each cycle tightens the feedback loop. The plan gets better because it's based on real snapshots, not guesses.

---

## Common Pitfalls

1. **Skipping the brainstorm.** Going straight to "do the next P0" is lazy. Think first.
2. **Planning in a vacuum.** Base the plan on the `/finish-line` snapshot — real state, not assumed.
3. **No human checkpoint.** Always present the plan and wait for approval.
4. **Overplanning.** The plan should take 10-15 minutes, not 2 hours.
5. **No flexibility.** If the session discovers something that invalidates the plan, note it and adjust.

## Shortcut: Quick Start

If you want to skip deep planning and just continue:
> "Skip the brainstorm — just pick up where we left off."

In this case: read the latest `/finish-line`, take the P0 action, begin `/start-gun` immediately.

---

*Part of the AEGIS toolchain. Built by @jaidenrabatin.*
