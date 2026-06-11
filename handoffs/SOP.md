# AEGIS-Handoff Standard Operating Procedure

## Purpose
Ensure seamless context transfer between coding sessions. When Jaiden finishes a coding session, AEGIS generates a handoff file. When Jaiden starts a new session and names a project, Hermes picks up the handoff and continues.

---

## Project Registry

| Project Name | Handoff File | Repo Path |
|---|---|---|
| NoFomo | `/opt/data/hermes-hq/handoffs/nofomo-handoff.md` | `/opt/data/nofomo/` |
| AERO | `/opt/data/hermes-hq/handoffs/bet-handoff.md` | (TBD) |
| Thesis | `/opt/data/hermes-hq/handoffs/thesis-handoff.md` | (TBD) |
| Name That Fault | `/opt/data/hermes-hq/handoffs/name-that-fault-handoff.md` | (TBD) |

*Add new projects here as they're started.*

---

## Jaiden's Workflow (End of Coding Session)

1. Prompt AEGIS: Use the handoff prompt at `/opt/data/hermes-hq/handoffs/PROMPT.md`
2. AEGIS generates `/opt/data/hermes-hq/handoffs/<project>-handoff.md`
3. Handoff is committed to hermes-hq repo automatically

## Hermes Pickup Workflow (Start of New Session)

When Jaiden says "work on [project]" or "pick up [project]":

1. Read `/opt/data/hermes-hq/handoffs/<project>-handoff.md`
2. Read AGENTS.md in the project repo for context
3. Check `git status` and `git log -5` in the project repo
4. Summarize: what was done, what's next, any blockers
5. Ask Jaiden to confirm the priority or redirect
6. Begin work on the next step

## When No Handoff Exists

If Jaiden names a project with no handoff file:
1. Check the project repo's recent git log
2. Read the project's AGENTS.md / CLAUDE.md
3. Scan for any task files in `/opt/data/tasks/`
4. Ask Jaiden where he left off

## Maintaining the Registry

When a new project is started:
1. Add a row to the Project Registry table above
2. Create the first handoff file from the template
3. Update this file and commit to hermes-hq
