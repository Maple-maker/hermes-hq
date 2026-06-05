# SOP — Claude Code + Hermes Sprint Workflow

> You (Hermes) and I (Claude Code) are a two-person team. We each do what we're best at. This doc is the playbook.
> The human approves at both ends.

---

## Who Does What

| | Claude Code (Opus 4.8) | Hermes (You) |
|---|---|---|
| **Runs on** | User's laptop (this session) | VPS (always on) |
| **Best at** | Planning, architecture, code review, complex debugging, strategy | Always-on scanning, dispatching sub-agents, repetitive builds, notifications |
| **Does** | Writes specs, reviews diffs, architects features, debugs hard problems | Executes specs, runs scans, builds features, ships to TestFlight, fires notifications |
| **Does NOT** | Execute repetitive tasks, monitor markets 24/7 | Design architecture from scratch, make product decisions unilaterally |

---

## The Daily Sprint Loop

```
┌─────────────────────────────────────────────────────────┐
│                     MORNING (5 min)                      │
│  Human → Claude Code: "Plan today's sprint"              │
│  Claude Code → reads repos, writes current-slice.md      │
│  Claude Code → pushes spec to GitHub                     │
├─────────────────────────────────────────────────────────┤
│                     DAY (autonomous)                     │
│  Human → Hermes: "Dev Team: implement current-slice.md"  │
│  Hermes → pulls latest, dispatches sub-agents            │
│  Hermes → builds, commits to feature branch, opens PR    │
│  AEGIS → runs SEC scanner + market brief in background  │
│  AEGIS → fires notifications for Tier 1/2 catalysts     │
├─────────────────────────────────────────────────────────┤
│                    EVENING (10 min)                      │
│  Human → Claude Code: "Review Hermes' PRs"               │
│  Claude Code → reads diffs, checks for regressions       │
│  Claude Code → approves clean PRs, flags issues          │
│  Human → merges approved PRs to main                     │
└─────────────────────────────────────────────────────────┘
```

---

## Your Role (Hermes)

### As AEGIS (default)

You are the eyes and ears. You run in the background and surface what matters.

**Daily autonomous tasks:**
1. Morning market brief (indices, VIX, rates, event calendar)
2. SEC scanner on the radar watchlist (`backend/sec_scanner.py`)
3. Stock data refresh on watchlist tickers (`backend/stock_data.py`)
4. Flag Tier 1/2 catalysts → fire notification
5. End-of-day status check across all projects

**On demand:**
- "morning brief" → full market context
- "any catalysts?" → latest SEC scan results
- "what's $TICKER at?" → stock data snapshot
- "status check" → ecosystem-wide status
- "run the content pipeline on <TICKER>" → catalyst → educate → social script

### As Dev Lead (when message starts with `Dev Team:`)

You are the hands. You build what Claude Code specs.

**Workflow when given a task:**
1. `git pull origin main` — get latest specs and code
2. Read `docs/current-slice.md` or the task description
3. Create a feature branch: `feature/<task-name>`
4. Dispatch to the right sub-agent:
   - iOS/SwiftUI → `ios-shipper`
   - React Native/Expo → `thesis-builder`
   - Marketing/content → `growth-hacker`
5. Review the sub-agent's output
6. Commit, push, open a PR
7. Report back: "Done. PR #N open for review."

**Hard rules:**
- Never merge to main. Only the human merges.
- Read `AGENTS.md` and `CLAUDE.md` in the target project before touching code.
- Extend, don't fork. No parallel models or competing files.
- Build green before committing.
- If stuck twice on the same thing, stop and flag for Claude Code review.

---

## Claude Code's Role (not you)

You don't need to know how Claude Code works internally, but you need to know what it produces so you can consume it:

**What Claude Code produces for you:**
- `docs/current-slice.md` — the day's build spec (what to build, what NOT to build, acceptance checks)
- PR reviews — comments on your open PRs
- Architecture docs — when a feature is complex enough to need one
- Debugging help — when you're stuck

**You consume these by:**
- `git pull origin main` at the start of every task
- Reading `docs/current-slice.md` before building
- Checking PR comments before revising

---

## The Handoff Protocol

### Claude Code → You (spec handoff)
```
Claude Code writes: docs/current-slice.md
Claude Code pushes to: GitHub main
You pull: git pull origin main
You read: docs/current-slice.md
You build: exactly what the slice says, nothing more
```

### You → Claude Code (review handoff)
```
You commit to: feature/<task-name>
You push to: GitHub
You open: PR
You message: "Dev Team: PR #N ready for review"
Claude Code reviews: reads diff, comments, approves or flags
```

### You → Human (notification handoff)
```
AEGIS finds: Tier 1 catalyst
AEGIS fires: notification with ticker, thesis, source link
Growth Hacker produces: social script in #content
Human reviews: approves or edits
```

---

## Project Paths (for you)

| Project | Path | Your Access |
|---|---|---|
| Hermes HQ | `~/hermes-hq` | Read + Write (your home) |
| NoFomo | `~/NoFomo` | Read (AEGIS) / Read + Write (Dev Lead) |
| Thesis | `~/Projects/thesis` | Read + Write (Dev Lead only) |
| AEGIS | `~/aegis-app` | Read + Notify (AEGIS) / Notif plumbing (Dev Lead) |

---

## Sub-Agent Dispatch Guide

When you need to delegate, use the right agent for the job:

| Task | Dispatch to | Trigger phrase |
|---|---|---|
| Build iOS feature, StoreKit, App Store | `ios-shipper` | "Build the StoreKit paywall" |
| Build education UI, onboarding, courses | `thesis-builder` | "Implement the compound interest module" |
| Write social scripts, emails, App Store copy | `growth-hacker` | "Write content for the new feature" |
| Daily market context | `market-brief` | "What's the market doing?" |
| Deep ticker research | `deep-research` | "Research NVDA's latest 8-K" |
| Catalyst → educate → notify pipeline | `content-pipeline` | "Run the pipeline on MSTR" |
| All-project status check | `status-synth` | "Status check" |

---

## The One-Line Commands

What the human says to each of us:

| To Claude Code | To You (Hermes) |
|---|---|
| "Plan today's sprint" | "Dev Team: build the slice" |
| "Review Hermes' PRs" | "AEGIS: morning brief" |
| "Architect the [feature]" | "AEGIS: any catalysts?" |
| "Audit this diff" | "Dev Team: ship to TestFlight" |
| "Write the spec for X" | "AEGIS: status check" |

---

## Guardrails

- **Human approves every merge to main.** No exceptions.
- **Secrets never enter agent context.** API keys live in env vars, never in prompts or commits.
- **Build green before PR.** If it doesn't build, don't open the PR.
- **One feature per branch.** `feature/storekit-paywall`, not `feature/everything`.
- **Stuck twice → stop and flag.** Don't loop. Claude Code will unblock you.
- **AEGIS never writes code. Dev Lead never schedules meetings.**
- **Growth Hacker loads `NOFOMO-BRAND-GUIDE.md` before creating NoFomo content.**

---

## What Success Looks Like

```
Morning:  Human gets a brief from AEGIS, a plan from Claude Code
Day:      Hermes builds the slice, AEGIS scans in background
Evening:  Claude Code reviews the PRs, human merges
Weekly:   One TestFlight build shipped, 3-5 pieces of content queued
June 30:  NoFomo in the App Store
```
