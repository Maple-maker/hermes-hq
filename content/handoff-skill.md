# /handoff — Baton Pass from AEGIS to Claude Code

> **Plug-and-play skill for Claude Code.** Copy this file into your project's `.claude/skills/` directory and reference it in your AGENTS.md.

---

## Purpose

When you share an idea on Telegram (or any chat), Hermes picks it up, structures it, and hands it off to the Google Drive task queue. Claude Code picks it up via `/start-gun` and runs `/relay` to build it.

The handoff is the baton. If the baton is sloppy, the whole relay fails.

---

## The Handoff Protocol

### Step 1: Acknowledge and Clarify

When an idea is shared, ask 2-3 quick questions if vague:
- "What's the core problem you're solving?"
- "Who's the end user?"
- "Any tech preferences or constraints?"

If the idea is clear, skip to Step 2.

### Step 2: Confirm the Handoff

**Always ask before writing:**

> "Do you want to hand this off to Claude Code?"

Wait for confirmation. Don't auto-handoff.

### Step 3: Write the Task

Once confirmed, write to the task queue:

```bash
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
1. **Handoff file** at `handoffs/<project>-handoff.md`
2. **Project folder** if new project
3. **Spec document** if the idea needs detailed requirements

### Step 5: Confirm and Report

Tell the user:
- Task ID and title
- Priority level
- Where it lives
- What happens next (Claude picks it up via `/start-gun` → `/relay`)

---

## Baton Quality Standards

A good handoff task has:

| Element | Standard |
|---|---|
| **Title** | Concise, action-oriented. "Build X" not "X idea" |
| **Description** | Detailed enough for Claude to start without asking anything. Include: what, why, constraints, acceptance criteria |
| **Priority** | Honest assessment of urgency |
| **Context** | Link to any reference documents, specs, or prior work |
| **Project** | Must match an existing project in the registry |

---

## The Full Flow

```
You (Telegram)
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

---

## Integration with Other Skills

| Skill | Relationship |
|---|---|
| `/start-gun` | Picks up the task you handed off |
| `/relay` | Builds the task you handed off |
| `/brand-new-day` | May generate new ideas to hand off |
| `/finish-line` | Ends the session that built your handoff |

---

*Part of the AEGIS toolchain. Built by @jaidenrabatin.*
