# /relay — 4×100 Multi-Model Build Pipeline

> **Plug-and-play skill for Claude Code.** Copy this file into your project's `.claude/skills/` directory and reference it in your AGENTS.md.

---

## Purpose

Relay turns a raw idea into working code through a 4-leg relay race. Each leg is a different model with a specific role. The baton between legs is a structured file — if the baton drops, the race stops.

```
🔫 HAIKU  →  🟡 SONNET  →  🟢 SONNET  →  🔵 OPUS  →  🟣 FABLE 5
  scaffold     grill+spec    design crew   build it     review+secure
  $1/$5        $3/$15        $3/$15        $5/$25       $10/$50
```

**The closer only matters if the runners before it set the race up right.**

---

## Critical Constraint: Model Ceiling

**The main Claude Code session MUST run on Fable 5.**

Why: sub-agents cannot exceed the cost tier of the session that launched them. If the main session runs on Sonnet and you dispatch "Opus" for Leg 3, you silently get Sonnet. No error. No warning. Just expensive-model pricing with mid-model output.

**Rule: Start every relay session on Fable 5. All legs stay below the ceiling.**

---

## When to Use

Use `/relay` when:
- A task has been handed off and is ready to build
- Someone says "run relay on [project]"
- `/start-gun` picks up a new task from the queue
- Starting a new build after scope is locked

**Do NOT use when:**
- Scope is not yet locked (run Leg 1 first)
- The task is a quick fix (< 30 min — just do it directly)
- Human checkpoint hasn't approved the spec

---

## The Baton Artifacts

Each leg produces a specific file that the next leg consumes:

| Baton | Produced By | Consumed By | Location |
|---|---|---|---|
| `project-spec.md` | Leg 1 (Sonnet) | Leg 2, Human gate | `relay/projects/<id>/01-spec/` |
| `agents/*.md` + `build-plan.md` | Leg 2 (Sonnet) | Leg 3 | `relay/projects/<id>/02-agents/` |
| Working code + `build-log.md` | Leg 3 (Opus) | Leg 4 | `relay/projects/<id>/03-build/` |
| `review-report.md` | Leg 4 (Fable 5) | Human checkpoint | `relay/projects/<id>/04-review/` |

If any baton is missing or malformed, the next leg must stop and request clarification.

---

## The Exchange Zones (Human Checkpoints)

There are exactly **two** points where a human must look up:

1. **After Leg 1** — Review the spec + value matrix + GO/NO-GO score. If NO-GO, the race ends here (cheap).
2. **After Leg 4** — Review the review report before anything merges to a real repo.

No human is needed during Leg 2 or Leg 3.

---

### Leg 1: Scope + Value Matrix (Sonnet)

**Model:** Sonnet (strong reasoning, cheap enough for interrogation)
**Role:** Grill the idea. Don't accept vagueness.

**What Leg 1 does:**
1. Reads the task description from the queue
2. Reads the handoff file for context
3. Conducts a structured interrogation:
   - What problem are you solving? For who?
   - What does "done" look like? (specific acceptance criteria)
   - What are the constraints?
   - What are the risks?
   - How do you measure success?
4. Produces `project-spec.md` with value matrix and GO/NO-GO score

**GO/NO-GO Gate:**
| Score | Verdict |
|---|---|
| ≥ 18/25 | **GO** → proceed |
| 12–17 | **RESCOPE** → shrink it |
| < 12 | **NO-GO** → kill it here |

A NO-GO costs < 3,000 tokens. A bad idea pushed through costs 20,000+.

---

### Leg 2: Sub-Agent Team Design (Sonnet)

**Model:** Sonnet (same runner, new leg)
**Role:** Design the build team. Don't build — design the builders.

**What Leg 2 does:**
1. Reads `project-spec.md` (the baton from Leg 1)
2. Does NOT re-litigate scope (it's locked)
3. Decomposes the spec into sub-tasks
4. For each sub-task, designs a sub-agent with name, role, model, and I/O contract
5. Produces `build-plan.md`

**Lane Discipline:** "Do not re-litigate scope. The spec is locked."

---

### Leg 3: Build (Opus + Helpers)

**Model:** Opus (strongest builder)
**Role:** Build the thing. Follow the plan.

**What Leg 3 does:**
1. Reads `build-plan.md` and `agents/*.md`
2. Does NOT re-litigate scope or redesign the plan
3. Dispatches sub-agents with their specific model pinned
4. Monitors output, catches errors, retries once per sub-agent
5. Assembles all outputs into working code
6. Produces `build-log.md` with: what was built, decisions, errors, token costs

**Mixed Team Strategy:**
- Opus handles: architecture, complex logic, integration
- Sonnet handles: boilerplate, tests, docs, routine CRUD

**Lane Discipline:** "Do not re-litigate scope or redesign agents. If the plan has a flaw, document it but don't redesign mid-build."

---

### Leg 4: Review + Security (Fable 5)

**Model:** Fable 5 (inherits from main session — strongest eyes)
**Role:** Review, debug, security-check. Don't rebuild — patch.

**What Leg 4 does:**
1. Reads `project-spec.md` and `build-log.md`
2. Reviews every file against the spec
3. Security review: hardcoded secrets, injection, auth gaps, dependency risks
4. Runs the code (build, test)
5. Produces `review-report.md`: spec compliance, code quality, security findings, recommendation (APPROVE / NEEDS_WORK)

**MERGE Gate:** Human reviews report. APPROVE → merge. NEEDS_WORK → back to Leg 3.

**Lane Discipline:** "Do not rebuild. Only review and patch."

---

## Workspace Structure

```
relay/projects/<project-id>/
├── intake/           # Raw handoff + task description
├── 01-spec/          # Leg 1 output: project-spec.md
├── 02-agents/        # Leg 2 output: build-plan.md + agent definitions
├── 03-build/         # Leg 3 output: build-log.md
└── 04-review/        # Leg 4 output: review-report.md
```

## The 5 Design Principles

1. **Leg 1 is a real gate.** Bad ideas die cheap. Strong ideas justify Opus build time.
2. **Two human checkpoints, no more.** After Leg 1 and after Leg 4.
3. **Enforce lane discipline.** No re-litigating scope. No redesigning agents. No rebuilding.
4. **Log split times.** Token costs per leg. Find bottlenecks after 10 runs.
5. **Walk before sprint.** Get Leg 1 → gate → Leg 4 working manually before automating everything.

---

*Part of the AEGIS toolchain. Built by @jaidenrabatin.*
