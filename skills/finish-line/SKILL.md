---
name: finish-line
description: "Run at the end of every Claude Code session. Creates a comprehensive session snapshot — what was done, where things stand, what's next by priority. Instant replay / save point for the next session to pick up context without re-reading everything. Saves tokens by distilling the session into structured markdown."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [finish-line, session-snapshot, handoff, save-point, daily-save]
    related_skills: [brand-new-day, start-gun, handoff, relay]
---

# /finish-line — Daily Save Point + Session Snapshot

## Purpose

This is the **last thing Claude Code runs** before ending a session. It creates a structured snapshot — an instant replay of everything that happened — so the next session can pick up context instantly without re-reading files, scrolling chat, or guessing where things left off.

Think of it as the save point in a video game. When you load back in, you know exactly where you are, what you were doing, and what to do next.

## When to Use

**Always** — at the end of every Claude Code session, no exceptions.

Also trigger when:
- Jaiden says "save point" or "finish line"
- Jaiden says "wrap up" or "end session"
- Significant work has been done and needs to be preserved
- Switching between projects mid-session (save point for the first project)

## The Snapshot Protocol

Run these steps **in order** at session end:

### Step 1: Capture What Was Done

Review the entire session and distill:

```bash
# Get recent commits from this session
cd /path/to/project
git log --oneline -10
git diff --stat HEAD~5 HEAD  # last 5 commits of changes
```

Answer these questions concisely:
- What tasks were worked on? (reference task IDs from the queue)
- What was completed vs left in-progress?
- What files were created, modified, or deleted?
- What technical decisions were made and why?
- What errors were encountered and how were they fixed?

### Step 2: Assess Where Things Stand

For each active project/task, record:

- **Status:** `complete` / `in-progress` / `blocked` / `not-started`
- **Progress:** percentage or milestone reached (e.g., "API built, frontend 50%")
- **Current state:** what's the last working state of the code?
- **Immediate blocker:** if blocked, what exactly is needed to unblock?

### Step 3: Define What Comes Next (Prioritized)

List the next 5-10 actions in priority order. Be specific — include file paths, function names, exact next steps. Not "work on frontend" but "wire up FeedView.swift to APIService response handler in NoFomo/Services/APIService.swift line 47."

Priority format:
```
P0 (Do next session): [specific action + file + line if applicable]
P1 (Soon): [specific action]
P2 (When ready): [specific action]
P3 (Backlog): [specific action]
```

### Step 4: Record Environment State

```
- Branch: [current branch]
- Last commit: [hash + message]
- Server status: [running/down, ports, PM2 status]
- Dependencies: [any new installs or version changes]
- API keys: [any that need attention]
- Database: [any migrations or schema changes pending]
```

### Step 5: Token + Cost Log

Record for the session:
- Estimated tokens consumed
- Models used (if relay: which legs ran)
- Approximate cost (if tracked)
- Time spent (wall clock)

This data feeds into the split-time tracking for the relay system.

### Step 6: Write the Snapshot File

Save to: `/opt/data/hermes-hq/handoffs/snapshots/<project>-<date>-finish-line.md`

Use the template below.

### Step 7: Update the Task Queue

```bash
cd /opt/data/hermes-hq/scripts

# Complete tasks that are done
python3 task_reader.py complete --id <id> --output "<what was done>"

# Update in-progress tasks with current status
python3 task_writer.py update --id <id> --status in_progress

# Add any new tasks discovered during the session
python3 task_writer.py add --project <name> --title "..." --priority <1|2|3>
```

### Step 8: Commit Everything

```bash
cd /opt/data/hermes-hq
git add handoffs/snapshots/
git commit -m "finish-line: <project> — <date> — <1-line summary>"

# Also commit any project changes
cd /path/to/project
git add .
git commit -m "<type>: <description>"
git push origin main 2>/dev/null
```

---

## Snapshot Template

```markdown
# 🏁 /finish-line — <Project Name>
**Date:** <YYYY-MM-DD>
**Session:** <session identifier or time range>
**Model(s):** <models used>

---

## Session Summary
<2-3 sentence overview of what this session accomplished>

## What Was Done
- [x] **<task>** — <brief description of what was completed>
  - Files: `<path/to/file>` — <change>
  - Commit: `<hash>` — <message>
- [x] **<task>** — <brief description>
- [ ] **<task>** — <started but not finished, current state>

## Where Things Stand

| Task | Status | Progress | Notes |
|------|--------|----------|-------|
| <task-name> | complete | 100% | Done, tested, committed |
| <task-name> | in-progress | 60% | API done, frontend wiring next |
| <task-name> | blocked | 30% | Waiting for Supabase key |
| <task-name> | not-started | 0% | Not yet begun |

## Code State
- **Branch:** `<branch>`
- **Last commit:** `<hash>` — `<message>`
- **Working tree:** clean / dirty (N uncommitted files)
- **Servers:** [status]
- **Build:** passing / failing / not tested

## Next Actions (Prioritized)

### P0 — Do Next Session
1. **<specific action>** — `<file path>:<line>` — <why>
2. **<specific action>** — `<file path>` — <why>

### P1 — Soon
3. **<specific action>** — <context>
4. **<specific action>** — <context>

### P2 — When Ready
5. **<specific action>** — <context>

### P3 — Backlog
- **<action>** — <context>

## Blockers
- None / **<blocker>** — <what's needed to unblock>

## Key Decisions Made
- **<decision>** — <reason>
- **<decision>** — <reason>

## Errors + Fixes
- **<error>** — <how it was fixed>
- **<error>** — <how it was fixed>

## Token Usage
- **Estimated tokens:** <number>
- **Models used:** <list>
- **Wall clock:** <duration>

## Files Changed
| File | Change |
|------|--------|
| `path/to/file.ext` | What changed |
| `path/to/file2.ext` | What changed |

## Notes for Next Session
<Anything the next session should know before starting>
<Gotchas, quirks, things to watch out for>
<Links to relevant docs or references>
```

---

## Snapshot Storage

All snapshots live in:
```
/opt/data/hermes-hq/handoffs/snapshots/
├── nofomo-2026-06-11-finish-line.md
├── bet-2026-06-12-finish-line.md
├── thesis-2026-06-13-finish-line.md
└── ...
```

The most recent snapshot for each project is the "current state." Older snapshots are history.

## Integration with Other Skills

| Skill | Relationship |
|---|---|
| `/brand-new-day` | Reads the latest `/finish-line` snapshot to plan the new session |
| `/start-gun` | Reads the latest `/finish-line` snapshot for context at session start |
| `/handoff` | May trigger `/finish-line` if the handoff ends a session |
| `/relay` | Each leg completion is a mini finish-line; session end is the full snapshot |

## Error Handling

| Error | Fix |
|---|---|
| Git commit fails | `git status` → resolve conflicts → retry |
| Task queue update fails | Wait 30s (rate limit), retry |
| Snapshot directory missing | `mkdir -p /opt/data/hermes-hq/handoffs/snapshots/` |
| Can't determine what was done | Run `git log --oneline -10` and `git diff --stat` |

## Common Pitfalls

1. **Writing vague snapshots.** "Worked on the API" is useless. "Built POST /radar endpoint in radar.ts, tested with curl, returns tier+score JSON" is useful.
2. **Skipping the priority list.** The next session needs to know exactly what to do first. Don't make it guess.
3. **Not committing.** The snapshot is useless if it's only in the working tree. Always commit.
4. **Forgetting to update the task queue.** If a task is done, mark it done. Don't leave stale state.
5. **Not recording blockers.** If you're stuck, say exactly why and what's needed. The next session (or Jaiden) can unblock it.
