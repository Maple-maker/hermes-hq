---
name: aegis-task-queue
description: Use the AEGIS task queue system to pick up work tasks from Google Drive, work them, and update status. Run at the start of every coding session.
triggers:
  - "work on"
  - "coding session"
  - "pick up task"
  - "what's next"
  - "task queue"
---

# AEGIS Task Queue — Skill

## Purpose

The AEGIS task queue is a CSV file stored on Google Drive that acts as a shared task board between Hermes (the always-on assistant) and Claude Code (the coding agent). Hermes writes tasks. Claude picks them up, works them, and marks them complete.

## System Overview

```
Hermes writes tasks  →  Google Drive CSV  ↓
                                       ↓
Claude reads tasks   ←  Google Drive CSV  ↓
     ↓                                       ↓
Claude works & updates status  →  Google Drive CSV
```

### Key Files

| File | Purpose |
|---|---|
| `gdrive:AEGIS_Workspace/AEGIS_Task_Queue.csv` | The task queue (single source of truth) |
| `/opt/data/hermes-hq/scripts/task_reader.py` | CLI to read/claim/complete tasks |
| `/opt/data/hermes-hq/scripts/task_writer.py` | CLI to add/update tasks |
| `/opt/data/cache/gdrive_folder_map.json` | Maps project names → Google Drive folder IDs |
| `gdrive:AEGIS_Workspace/Projects/<name>/` | Per-project file storage |
| `gdrive:AEGIS_Workspace/Handoffs/` | Handoff documents |

### Task Schema

```
id, project, title, description, status, priority, assigned_to,
drive_folder_id, created_at, completed_at, output_notes, handoff_file
```

**Status values:** `pending`, `in_progress`, `blocked`, `done`, `cancelled`

**Priority:** `1` = high, `2` = medium, `3` = low

**Assigned to:** `claude`, `dev_team`, `hermes`

---

## Claude's Session Protocol

### At Session Start — Check for Tasks

```bash
# Check what's pending for your project
cd /opt/data/hermes-hq/scripts
python3 task_reader.py list --project <project-name>

# Get the highest priority task
python3 task_reader.py next
```

The `next` command outputs a JSON object with the full task. Parse it and begin work.

### Claim Before Working

```bash
python3 task_reader.py claim --id <task-id>
```

This marks the task as `in_progress` so no duplicate work happens.

### During Work — Upload Reference Files

If the task requires reference materials (specs, designs, data), upload them to the project's Drive folder:

```bash
# Get the folder ID from the folder map
python3 -c "
import json
with open('/opt/data/cache/gdrive_folder_map.json') as f:
    print(json.load(f).get('<project-key>'))
"

# Upload files via rclone
rclone copy /path/to/file gdrive:/AEGIS_Workspace/Projects/<name>/
```

### At Session End — Complete & Handoff

```bash
# Mark done with output notes
python3 task_reader.py complete --id <task-id> --output "Summary of what was done"

# If a handoff file was created
python3 task_reader.py complete --id <task-id> \
  --output "..." \
  --handoff-file "/opt/data/hermes-hq/handoffs/<project>-handoff.md"
```

Create a handoff file at `/opt/data/hermes-hq/handoffs/<project>-handoff.md` with:
1. What was done (every task, every file changed)
2. Last commit hash
3. Next 3 priorities
4. Blockers
5. Key decisions
6. Files modified table
7. Environment state

### If Blocked

```bash
python3 task_reader.py block --id <task-id> --reason "<what's blocking>"
```

---

## Hermes's Protocol (for reference)

Hermes uses `task_writer.py` to manage the queue:

```bash
# Add a task
python3 task_writer.py add --project <name> --title "..." --description "..." --priority 1

# Update status
python3 task_writer.py update --id <id> --status in_progress
python3 task_writer.py update --id <id> --status done --output "..."

# List all pending
python3 task_writer.py list --status pending
```

---

## Google Drive Folder Structure

```
AEGIS_Workspace/
├── AEGIS_Task_Queue.csv          ← task queue
├── Projects/
│   ├── NoFomo/                   ← NoFomo project files
│   ├── Thesis/                   ← Thesis project files
│   └── Name_That_Fault/          ← NTF project files
├── Handoffs/                     ← session handoff documents
└── Outputs/                      ← scan outputs, reports
```

---

## Rate Limiting

The Google Drive API has quota limits. Both scripts enforce a 5-second gap between API calls. Don't bypass this. If you get a 403, wait 30 seconds and retry.

---

## Error Handling

| Error | Fix |
|---|---|
| 403 Forbidden | Rate limited. Wait 30s, retry. |
| 404 File not found | Wrong file ID. Check `gdrive_folder_map.json`. |
| Token expired | Run `rclone config reconnect gdrive:` to refresh. |
| NO_PENDING_TASKS | No work to do. Ask Hermes for new tasks. |
