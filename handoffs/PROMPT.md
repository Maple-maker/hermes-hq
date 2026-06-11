# AEGIS Handoff Prompt

Copy and paste this at the end of every coding session. Fill in the bracketed sections.

---

Create a handoff file for the [PROJECT NAME] project at:
`/opt/data/hermes-hq/handoffs/[project-name]-handoff.md`

Use the template at `/opt/data/hermes-hq/handoffs/HANDOFF_TEMPLATE.md`

Fill in:
1. **What Was Done** — list every task completed this session with files changed
2. **Last Commit** — run `git log -1 --oneline` in the project repo
3. **What's Next** — 3 prioritized next steps with specific files to touch
4. **Blockers** — anything stuck and what's needed to unblock
5. **Key Decisions** — any architectural or design decisions made
6. **Files Modified** — table of files changed with brief descriptions
7. **Environment/Context** — branch, server status, API keys, dependencies
8. **Notes** — gotchas, quirks, things the next session should know

Also check for any OTHER projects that have handoff files and note if this session affected them.

Save the file. Confirm the path when done.
