---
name: relay
description: "Use when Claude Code should build a project idea using a 4-leg multi-model relay race. Leg 1 (Sonnet) grills scope and produces a spec. Leg 2 (Sonnet) designs sub-agent team and build plan. Leg 3 (Opus + helpers) builds the code. Leg 4 (Fable) reviews, security-checks, and patches. Requires: main session on Fable, Google Drive task queue, start-gun session start."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [relay, multi-model, build-pipeline, sub-agents, claude-code]
    related_skills: [handoff, start-gun, subagent-driven-development]
---

# /relay — 4×100 Multi-Model Build Pipeline

## Purpose

Relay turns a raw idea into working code through a 4-leg relay race. Each leg is a different model with a specific role. The baton between legs is a structured file — if the baton drops, the race stops.

```
Leg 1 (Sonnet) → project-spec.md (scope, value matrix, GO/NO-GO gate)
Leg 2 (Sonnet) → agents/ folder + build plan (sub-agent team design)
Leg 3 (Opus)   → working code + build log (the actual build)
Leg 4 (Fable)  → review-report.md + applied fixes (quality anchor)
```

## Critical Constraint: Model Ceiling

**The main Claude Code session MUST run on Fable (the most expensive model).**

Why: sub-agents cannot exceed the cost tier of the session that launched them. If the main session runs on Sonnet and you dispatch "Opus" for Leg 3, you silently get Sonnet. No error. No warning. Just expensive-model pricing with mid-model output.

**Rule: Start every relay session on Fable. All legs stay below the ceiling.**

## When to Use

Trigger when:
- A task has been handed off and is ready to build
- Jaiden says "run relay on [project]"
- `/start-gun` picks up a new task from the queue
- Starting a new build after scope is locked

**Do NOT use when:**
- Scope is not yet locked (run Leg 1 first)
- The task is a quick fix (< 30 min of work — just do it directly)
- Human checkpoint hasn't approved the spec

## The Baton Artifacts

Each leg produces a specific file that the next leg consumes. These are the batons:

| Baton | Produced By | Consumed By | Location |
|---|---|---|---|
| `project-spec.md` | Leg 1 (Sonnet) | Leg 2, Human gate | `relay/projects/<id>/01-spec/` |
| `agents/*.md` + `build-plan.md` | Leg 2 (Sonnet) | Leg 3 | `relay/projects/<id>/02-agents/` |
| Working code + `build-log.md` | Leg 3 (Opus) | Leg 4 | `relay/projects/<id>/03-build/` |
| `review-report.md` | Leg 4 (Fable) | Human checkpoint | `relay/projects/<id>/04-review/` |

If any baton is missing or malformed, the next leg must stop and request clarification. No leg may proceed on assumptions.

## The Exchange Zones (Human Checkpoints)

There are exactly **two** points where a human must look up:

1. **After Leg 1** — Jaiden reviews the spec + value matrix + GO/NO-GO score. If NO-GO, the race ends here (cheap).
2. **After Leg 4** — Jaiden reviews the review report before anything merges to a real repo.

No human is needed during Leg 2 or Leg 3. That's the point.

## The Complete Track

### Pre-Race: /start-gun

Before relay begins, Claude Code must:

1. Run `/start-gun` to pick up the task from the Google Drive queue
2. Read the handoff file for context
3. Check git status
4. Claim the task

### Leg 1: Scope + Value Matrix (Sonnet)

**Model:** Sonnet (strong reasoning, cheap enough for interrogation)
**Role:** Grill the idea. Don't accept vagueness. Push on contradictions.

**What Leg 1 does:**
1. Reads the task description from the queue
2. Reads the handoff file for context
3. Conducts a structured interrogation of the idea:
   - What problem are you solving? For who?
   - What does "done" look like? (specific acceptance criteria)
   - What are the constraints? (tech, time, resources)
   - What are the risks? What could make this fail?
   - How do you measure success? (metrics, not vibes)
4. Produces `project-spec.md` with:
   - Problem statement (1 paragraph)
   - Target user / client archetype
   - Scope (in scope / out of scope)
   - Acceptance criteria (testable, specific)
   - Constraints (tech, time, budget)
   - Value matrix (weighted criteria scored 1-10)
   - Risks and mitigations
   - GO/NO-GO recommendation with score

**Leg 1 Prompt Template:**
```
You are the Leg 1 runner in a 4×100 relay. Your job: produce a locked spec.

Task: <task description>
Context: <handoff file content>

Conduct a rigorous scope interview. Ask hard questions:
- What's the real problem? Not the surface symptom.
- Who is the end user? What's their skill level?
- What does "done" look like in specific, testable terms?
- What are you NOT building? (out of scope)
- What could make this fail?
- How do you measure success?

Produce project-spec.md with:
1. Problem Statement
2. Client Archetype (who, skill level, context)
3. Scope (in / out)
4. Acceptance Criteria (testable)
5. Constraints
6. Value Matrix (criteria × weight × score)
7. Risks + Mitigations
8. GO/NO-GO with numeric score (0-100)

If the idea scores below 50, recommend NO-GO. Don't sugarcoat.
```

**Baton output:** `relay/projects/<id>/01-spec/project-spec.md`

**Gate:** Human reviews spec. GO → Leg 2. NO-GO → race ends (cheaply).

### Leg 2: Sub-Agent Team Design (Sonnet)

**Model** (same runner, new leg)
**Role:** Design the build team. Don't build — design the builders.

**What Leg 2 does:**
1. Reads `project-spec.md` (the baton from Leg 1)
2. Does NOT re-litigate scope (it's locked)
3. Decomposes the spec into sub-tasks
4. For each sub-task, designs a sub-agent:
   - Name and role
   - System prompt with lane discipline
   - Model assignment (opson for hard architecture, sonnet for routine)
   - Input/output contract
5. Produces `build-plan.md` with:
   - Execution order (what runs in parallel vs sequential)
   - Dependencies between sub-agents
   - Estimated token budget per leg
   - Risk mitigation for the build

**Lane Discipline Instruction (critical):**
Tell Leg 2 explicitly: "Do not re-litigate scope. The spec is locked. Your job is to design agents that implement the spec, not question it."

**Baton output:**
- `relay/projects/<id>/02-agents/build-plan.md`
- `relay/projects/<id>/02-agents/<agent-name>.md` (one per sub-agent)

### Leg 3: Build (Opus + Helpers)

**Model:** Opus (strongest builder)
**Role:** Build the thing. Follow the plan.

**What Leg 3 does:**
1. Reads `build-plan.md` and `agents/*.md` (the baton from Leg 2)
2. Does NOT re-litigate scope or redesign the plan
3. For each sub-agent in the plan:
   - Dispatches the sub-agent with its specific model pinned
   - Monitors output
   - Catches errors and retries (once per sub-agent)
4. Assembles all sub-agent outputs into working code
5. Runs verification (build, lint, test if applicable)
6. Produces `build-log.md`:
   - What was built (every file, every change)
   - Decisions made and why
   - Errors encountered and fixes
   - Token costs per sub-agent
   - Wall-clock time per sub-agent

**Lane Discipline Instruction:**
Tell Leg 3 explicitly: "Do not re-litigate scope or redesign agents. The plan is locked. Your job is to build what the plan specifies. If the plan has a flaw, document it in the build log but don't redesign mid-build."

**Mixed Team Strategy:**
- Opus handles: architecture, complex logic, integration
- Sonnet handles: boilerplate, tests, docs, routine CRUD
- This is faster and cheaper than Opus doing everything

**Baton output:**
- Working code in the project repo
- `relay/projects/<id>/03-build/build-log.md`

### Leg 4: Review + Security (Fable)

**Model:** Fable (inherits from main session — strongest eyes)
**Role:** Review, debug, security-check. Don't rebuild — patch.

**What Leg 4 does:**
1. Reads `project-spec.md` and `build-log.md` (the baton from Leg 3)
2. Reviews every file in the build output against the spec
3. Security review:
   - Hardcoded secrets?
   - Injection vulnerabilities?
   - Auth/access control gaps?
   - Dependency risks?
4. Runs the code (build, test if applicable)
5. Produces `review-report.md`:
   - Spec compliance (did it build what was specified?)
   - Code quality assessment
   - Security findings (critical / warning / info)
   - Bugs found and fixed
   - Remaining issues (if any)
   - Recommendation: APPROVE / NEEDS_WORK

**Lane Discipline Instruction:**
Tell Leg 4 explicitly: "Do not rebuild. Only review and patch. If something needs major rewrite, document it as a finding — don't do it yourself."

**Baton output:**
- `relay/projects/<id>/04-review/review-report.md`
- Patched files (if minor fixes)

**Gate:** Human reviews report. APPROVE → merge to repo. NEEDS_WORK → back to Leg 3.

## Sub-Agent Definitions

Sub-agents live in `.claude/agents/` and are Markdown files with YAML frontmatter:

```yaml
---
name: relay-leg1-scope
description: "Leg 1 of relay. Grills scope, produces project-spec.md with value matrix and GO/NO-GO gate."
model: claude-sonnet-4-20250514
tools: [Read, Write, Glob]
---

You are Leg 1 of a 4×100 relay. <system prompt continues...>
```

**Important:** The `model:` field is the primary pin. Also name the model explicitly when dispatching (belt and suspenders).

## Workspace Structure

Each project gets its own relay workspace:

```
relay/projects/<project-id>/
├── intake/           # Raw handoff + task description
├── 01-spec/          # Leg 1 output: project-spec.md
├── 02-agents/        # Leg 2 output: build-plan.md + agent definitions
├── 03-build/         # Leg 3 output: build-log.md
└── 04-review/        # Leg 4 output: review-report.md
```

## Split Time Logging

After each leg, log costs back to the Google Drive sheet:

| Column | Value |
|---|---|
| `leg1_cost` | Token cost of Leg 1 |
| `leg2_cost` | Token cost of Leg 2 |
| `leg3_cost` | Token cost of Leg 3 |
| `leg4_cost` | Token cost of Leg 4 |
| `total_legs` | Sum of all legs |

This data tells you where relay is slow or expensive after 10+ runs.

## The 5 Levers (Design Principles)

1. **Leg 1 is a real gate, not just intake.** Bad ideas die cheap (Sonnet tokens). Strong ideas justify Opus build time.
2. **Two human checkpoints, no more.** After Leg 1 (spec approval) and after Leg 4 (review approval). Nothing else stops the track.
3. **Enforce lane discipline.** Leg 2 can't re-litigate scope. Leg 3 can't redesign agents. Leg 4 can't rebuild. Every leg stays in its lane.
4. **Log split times.** Token costs per leg. After 10 runs you'll know exactly where the bottlenecks are.
5. **Walk before you sprint.** Get Leg 1 → gate → Leg 4 working manually before automating the full 4×100. Solid batons before fast runners.

## Staged Rollout

**Stage 1 (now):** Gun + Leg 1 + Gate
- Manual trigger from task queue
- Leg 1 produces spec with GO/NO-GO
- Human approves
- Manual build (Claude Code directly)
- Leg 4 reviews

**Stage 2 (next):** Add Leg 2 + Leg 3
- Automated sub-agent dispatch
- Mixed team (Opus + Sonnet)
- Automated build log

**Stage 3 (future):** Full automation
- Automated trigger from queue
- Scheduled runs
- Continuous relay board

## Error Handling

| Error | Fix |
|---|---|
| Sub-agent model falls back to parent | Ensure main session is on FABLE |
| Leg produces poor baton | Retry with stronger prompt; if still bad, NO-GO |
| Rate limit on Drive API | Wait 30s, retry. 5s gap enforced by scripts. |
| Scope creep in Leg 3 | Reject. Document in build log. Stick to plan. |
| Human rejects spec at gate | Kill race. Cheap lesson. Log why in task notes. |

## Key Reference

| Resource | Location |
|---|---| 
| Task Queue | `gdrive:AEGIS_Workspace/AEGIS_Task_Queue.csv` |
| Task Reader | `/opt/data/hermes-hq/scripts/task_reader.py` |
| Task Writer | `/opt/data/hermes-hq/scripts/task_writer.py` |
| Folder Map | `/opt/data/cache/gdrive_folder_map.json` |
| Handoff Skill | `skills/handoff/SKILL.md` |
| Start-gun Skill | `skills/start-gun/SKILL.md` |
