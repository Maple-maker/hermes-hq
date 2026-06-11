---
name: start-gun
description: Run at the start of every Claude Code session. Pulls tasks from the AEGIS task queue (Google Drive), picks up where the last session left off via handoff files, and begins working. This is the entry point for all coding sessions.
triggers:
  - "start"
  - "begin session"
  - "what should I work on"
  - "new session"
  - "start gun"
  - "startgun"
  - "/start-gun"
---

# /start-gun — Session Bootstrap Skill

## Purpose

This is the **first thing Claude Code runs** at the start of every coding session. It:

1. Checks the AEGIS task queue (Google Drive CSV) for pending tasks
2. Reads the latest handoff file for context
3. Checks recent git history for the project
4. Identifies what to work on and begins

The name "start gun" = the starter's pistol. When this fires, the session begins.

---

## Session Startup Protocol

Run these steps **in order** at the start of every session:

### Step 1: Check the Task Queue

```bash
cd /opt/data/hermes-hq/scripts

# List all pending tasks
python3 task_reader.py list

# If there are pending tasks, get the highest priority one
python3 task_reader.py next
```

The `next` command returns a JSON object:
```json
{
  "id": "3",
  "project": "BET",
  "title": "BET - Automated Evaluation and Repair Organizer",
  "description": "Searchable fault-finding database for soldiers...",
  "status": "pending",
  "priority": "1",
  "assigned_to": "claude",
  "drive_folder_id": "",
  "created_at": "2026-06-11",
  "completed_at": "",
  "output_notes": "",
  "handoff_file": ""
}
```

### Step 2: Read the Handoff File

Every project has a handoff file at:
```
/opt/data/hermes-hq/handoffs/<project>-handoff.md
```

Read it. It contains:
- What was done in the last session
- What's next (prioritized)
- Blockers
- Key decisions
- Files modified
- Environment state
- Last commit hash

### Step 3: Check Git Status

```bash
# Navigate to the project repo (see Project Registry in handoffs/SOP.md)
cd /opt/data/nofomo  # or wherever the project lives

# Check recent activity
git log --oneline -5
git status

# If there are uncommitted changes from last session, review them
git diff --stat HEAD
```

### Step 4: Claim the Task

```bash
# Claim the task so no duplicate work happens
cd /opt/data/hermes-hq/scripts
python3 task_reader.py claim --id <task-id>
```

### Step 5: Begin Work

Now start working on the task. Read AGENTS.md in the project repo for conventions. Follow the project's established patterns.

---

## Project Startup (New Project)

If starting a **brand new project** (no repo exists yet):

### Step 1: Create the Project Repo

```bash
mkdir -p /opt/data/<project-name>
cd /opt/data/<project-name>
git init

# Create initial structure
echo "# <project-name>" > README.md
git add .
git commit -m "init: project scaffold"
```

### Step 2: Create AGENTS.md

Every project needs an AGENTS.md at its root. Template:

```markdown
# <Project Name> — Repo Context

> Loaded into every Claude Code session. Keep terse. Source of truth for stack, mission, and conventions.

## Mission

[One paragraph: what this project does and why]

## Stack

| Layer | Tech |
|---|---|
| [Layer] | [Tech] |

## File map

```
[Key files and their purposes]
```

## Conventions

- [Convention 1]
- [Convention 2]

## Verification

- **Build:** [build command]
- **Test:** [test command]

## Active tasks

See AEGIS task queue: https://drive.google.com/file/d/1LQzsv8Vk7VRLMY1jO1OwJ-_S3hIf2Pog/view
```

### Step 3: Initialize from Task Description

The task description in the queue is the feature brief. Read it carefully. If it references external documents (spec PDFs, design files), check:

1. The project's Google Drive folder: `AEGIS_Workspace/Projects/<name>/`
2. `/opt/data/cache/documents/` for uploaded files
3. `/opt/data/tasks/` for detailed specs

### Step 4: Plan Before Building

Before writing any code:

1. Read the existing codebase (if any)
2. Read the task description and any linked specs
3. Write a brief plan in your own words
4. If the task is complex, break it into sub-tasks
5. Begin with the smallest testable piece

---

## During Work — Session Discipline

### File Uploads to Google Drive

If you generate reference files, reports, or outputs, upload them:

```bash
# Upload to the project's Drive folder
rclone copy /path/to/file gdrive:/AEGIS_Workspace/Projects/<name>/

# Get folder ID if needed
python3 -c "
import json
with open('/opt/data/cache/gdrive_folder_map.json') as f:
    print(json.load(f).get('<project-key>'))
"
```

### Progress Updates

For long-running tasks, update the task periodically:

```bash
cd /opt/data/hermes-hq/scripts
python3 task_writer.py update --id <task-id> --status in_progress
```

### Keep a Running Notes File

During the session, keep notes in:
```
/opt/data/tasks/<project>-<task>-notes.md
```

Log:
- Decisions made and why
- Errors encountered and fixes
- Files created/modified
- What's blocked and why

---

## Session End Protocol

Before finishing a session, **always** do these steps:

### Step 1: Complete All Git Work

```bash
cd /opt/data/<project-name>

# Commit all changes with a descriptive message
git add .
git commit -m "<type>: <description>

<what was done>
<why it matters>"

# Push if remote exists
git push origin main 2>/dev/null
```

### Step 2: Update the Handoff File

Write/update `/opt/data/hermes-hq/handoffs/<project>-handoff.md`:

```markdown
# AEGIS Handoff — <Project>
## Date: <YYYY-MM-DD>

## What Was Done This Session
- [ ] Task — what was accomplished, files changed
- [ ] Task — what was accomplished, files changed

Last commit:
```
<hash> — <message>
```

## What's Next (Priority Order)
1. **First priority** — specific next step with files to touch
2. **Second priority** — specific next step
3. **Third priority** — specific next step

## Blockers
- None / **Blocker** — what and what's needed

## Key Decisions
- **Decision:** [what] → **Reason:** [why]

## Files Modified
| File | Change |
|---|---|
| path/to/ext | What changed |

## Environment / Context
- **Branch:** main
- **Servers:** [status]
- **Dependencies:** [new installs]
```

### Step 3: Complete the Task

```bash
cd /opt/data/hermes-hq/scripts

# If the task is fully done
python3 task_reader.py complete \
  --id <task-id> \
  --output "<summary of what was done>" \
  --handoff-file "/opt/data/hermes-hq/handoffs/<project>-handoff.md"

# If partially done (more work needed next session)
python3 task_writer.py update \
  --id <task-id> \
  --status pending  # reset to pending for next session
```

### Step 4: Commit Handoff

```bash
cd /opt/data/hermes-hq
git add handoffs/<project>-handoffs.md
git commit -m "handoff: <project> — <date> — <summary>"
```

---

## No Pending Tasks

If `task_reader.py next` returns `NO_PENDING_TASKS`:

1. Check if you're in the right project directory
2. Ask Hermes (via Telegram) for new work:
   - "No pending tasks in the queue. What should I work on?"
3. Wait for a new task to be relayed

---

## Errors and Troubleshooting

| Error | Fix |
|---|---|
| 403 from Drive API | Rate limited. Wait 30s, retry. |
| `task_reader.py` not found | `cd /opt/data/hermes-hq/scripts` |
| Token expired | Hermes needs to run `rclone config reconnect gdrive:` |
| No handoff file | First session for this project — create from template |
| Git push fails | Check remote: `git remote -v` |
| Project folder not on Drive | Hermes needs to create it and update folder_map.json |

---

## Key Reference

| Resource | Location |
|---|---|
| Task Queue (Google Drive CSV) | `gdrive:AEGIS_Workspace/AEGIS_Task_Queue.csv` |
| Task Queue (direct link) | `https://drive.google.com/file/d/1LQzsv8Vk7VRLMY1jO1OwJ-_S3hIf2Pog/view` |
| Task Reader Script | `/opt/data/hermes-hq/scripts/task_reader.py` |
| Task Writer Script | `/opt/data/hermes-hq/scripts/task_writer.py` |
| Folder Map | `/opt/data/cache/gdrive_folder_map.json` |
| Handoff Files | `/opt/data/hermes-hq/handoffs/<project>-handoff.md` |
| Handoff Template | `/opt/data/hermes-hq/handoffs/HANDOFF_TEMPLATE.md` |
| Project SOP | `/opt/data/hermes-hq/handoffs/SOP.md` |
| Project Registry | In SOP.md — maps project names → repos |
