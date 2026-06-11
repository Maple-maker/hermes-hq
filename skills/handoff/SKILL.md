---
name: handoff
description: "Use when Jaiden shares an idea on Telegram that should become a task for Claude Code. Prompts 'Do you want to hand this off?' and writes the task to the Google Drive task queue. This is the baton pass from AEGIS (Hermes) to Claude Code."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [handoff, task-queue, relay, claude-code, google-drive]
    related_skills: [start-gun, relay]
---

# /handoff — Baton Pass from AEGIS to Claude Code

## Purpose

This is the **first leg of the relay**. When Jaiden shares an idea on Telegram, Hermes (AEGIS) picks it up, structures it, and hands it off to the Google Drive task queue. Claude Code picks it up via `/start-gun` and runs the `/relay` to build it.

The handoff is the baton. If the baton is sloppy, the whole relay fails.

## When to Use

Trigger when Jaiden:
- Shares a new idea or feature request
- Says "I want to build X"
- Describes a problem that needs solving
- Shares a document/spec that implies work to be done
- Says "Relay: [idea]" or "Hand this off"

## The Handoff Protocol

### Step 1: Acknowledge and Clarify

When Jaiden shares an idea, respond with enthusiasm and ask clarifying questions if needed. Don't just say "relayed" — make sure you understand the idea well enough to write a good task.

Ask at most 2-3 quick questions if the idea is vague:
- "What's the core problem you're solving?"
- "Who's the end user?"
- "Any tech preferences or constraints?"

If the idea is already clear, skip to Step 2.

### Step 2: Confirm the Handoff

Always ask before writing:

> "Do you want to hand this off to Claude Code?"

or

> "I can hand this off to the relay. Want me to?"

Wait for confirmation. Don't auto-handoff.

### Step 3: Write the Task

Once confirmed, write to the Google Drive task queue:

```bash
cd /opt/data/hermes-hq/scripts

python3 task_writer.py add \
  --project "<project-name>" \
  --title "<concise title>" \
  --description "<detailed description with context, requirements, and acceptance criteria>" \
  --priority <1|2|3> \
  --assigned-to claude
```

**Priority guide:**
- `1` = High — core features, blockers, time-sensitive
- `2` = Medium — improvements, nice-to-haves
- `3` = Low — exploratory, future work

### Step 4: Create Supporting Assets

For complex ideas, also create:

1. **Handoff file** at `/opt/data/hermes-hq/handoffs/<project>-handoff.md`
2. **Google Drive folder** if new project (update `gdrive_folder_map.json`)
3. **Spec document** at `/opt/data/tasks/<project>-<feature>-spec.md` if the idea needs detailed requirements

### Step 5: Confirm and Report

Tell Jaiden:
- Task ID and title
- Priority level
- Where it lives (Drive link if applicable)
- What happens next (Claude picks it up via `/start-gun` → `/relay`)

Example:
> "✅ Handed off: 'BET - Automated Evaluation and Repair Organizer' (Task #3, Priority 1). Claude will pick it up at the next session start via /start-gun."

## Baton Quality Standards

A good handoff task has:

| Element | Standard |
|---|---|
| **Title** | Concise, action-oriented. "Build X" not "X idea" |
| **Description** | Detailed enough for Claude to start without asking Jaiden anything. Include: what, why, constraints, acceptance criteria |
| **Priority** | Honest assessment of urgency |
| **Context** | Link to any reference documents, specs, or prior work |
| **Project** | Must match an existing project in the registry |

A bad handoff task:
- Vague title like "New feature"
- One-line description
- No context about what "done" looks like
- Wrong project assignment

## Project Registry

Before handing off, check if the project exists:

| Project | Repo | Drive Folder Key |
|---|---|---|
| NoFomo | `/opt/data/nofomo/` | `nofomo` |
| BET | (TBD) | `bet` |
| Thesis | (TBD) | `thesis` |
| Name That Fault | (TBD) | `name_that_fault` |

If the project doesn't exist, create the folder structure first (see `/start-gun` skill).

## Google Drive Folder Map

See `/opt/data/cache/gdrive_folder_map.json` for folder IDs.

## Error Handling

| Error | Fix |
|---|---|
| 403 from Drive API | Rate limited. Wait 30s, retry. |
| Token expired | Run `rclone config reconnect gdrive:` |
| Project not in registry | Create project folder + update registry |
| `task_writer.py` not found | `cd /opt/data/hermes-hq/scripts` |

## The Full Flow

```
Jaiden (Telegram)
    ↓ shares idea
Hermes (/handoff)
    ↓ asks "Hand this off?"
    ↓ writes task to Google Drive CSV
    ↓ creates handoff file
Google Drive (task queue + handoffs)
    ↓
Claude Code (/start-gun)
    ↓ reads task + handoff
    ↓ claims task
    ↓ runs /relay (4-leg multi-model build)
    ↓ completes task + updates handoff
    ↓
Working Code (git + Drive)
```
