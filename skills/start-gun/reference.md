# start-gun — Quick Reference

## Task Queue Commands

```bash
cd /opt/data/hermes-hq/scripts

# List all pending tasks
python3 task_reader.py list

# List pending tasks for a specific project
python3 task_reader.py list --project NoFomo

# Get highest priority pending task (returns JSON)
python3 task_reader.py next

# Claim a task (marks in_progress)
python3 task_reader.py claim --id 3

# Mark task complete with notes
python3 task_reader.py complete --id 3 --output "Built the feature"

# Mark complete with handoff file reference
python3 task_reader.py complete --id 3 \
  --output "Built the feature" \
  --handoff-file "/opt/data/hermes-hq/handoffs/nofomo-handoff.md"

# Block a task
python3 task_reader.py block --id 3 --reason "Waiting for API key"
```

## Hermes Commands (for reference)

```bash
# Add a new task
python3 task_writer.py add \
  --project NoFomo \
  --title "Feature name" \
  --description "Detailed description" \
  --priority 1

# Update task status
python3 task_writer.py update --id 3 --status in_progress
python3 task_writer.py update --id 3 --status done --output "Done"

# List all tasks
python3 task_writer.py list --status pending
```

## Google Drive Folder IDs

See `/opt/data/cache/gdrive_folder_map.json` for the full map.

Key folders:
- `AEGIS_Workspace/` — root
- `AEGIS_Workspace/Projects/NoFomo/` — NoFomo project files
- `AEGIS_Workspace/Projects/BET/` — BET project files
- `AEGIS_Workspace/Handoffs/` — handoff documents
- `AEGIS_Workspace/Outputs/` — scan outputs, reports

## Project Registry

| Project | Repo | Handoff |
|---|---|---|
| NoFomo | `/opt/data/nofomo/` | `handoffs/nofomo-handoff.md` |
| BET | (TBD) | `handoffs/bet-handoff.md` |
| Thesis | (TBD) | `handoffs/thesis-handoff.md` |
| Name That Fault | (TBD) | `handoffs/name-that-fault-handoff.md` |

## Rate Limiting

Drive API: 5-second gap between calls enforced by scripts.
If 403: wait 30 seconds, retry.
