# /sync — Pull Latest Context at Session Start

> Run this at the beginning of every Claude Code session to pull the latest context from both GitHub and the AEGIS Vault.

---

## Purpose

Before doing anything else, `/sync` ensures Claude Code has the latest:
1. **AGENTS.md, skills, SOP** from GitHub (`hermes-hq`)
2. **Handoffs, project wikis, priorities** from the AEGIS Vault (Google Drive)

This replaces the manual "read the handoff file" step with a single command.

---

## The Sync Protocol

### Step 1: Pull Latest from GitHub

```bash
cd /opt/data/hermes-hq
git pull origin main
```

This updates: `AGENTS.md`, `skills/`, `SOP.md`, `PROJECTS.md`, `content/`

### Step 2: Pull Latest from AEGIS Vault

```bash
# Sync handoffs
rclone sync gdrive:1H4QDzKCq7lN_6PS4WHKDCRBcpjBSra2d/Handoffs/ /opt/data/hermes-hq/handoffs/ --metadata -v

# Sync framework files
rclone sync gdrive:1H4QDzKCq7lN_6PS4WHKDCRBcpjBSra2d/Vault/99-Framework/ /opt/data/hermes-hq/handoffs/99-Framework/ --metadata -v
```

This updates: session handoffs, project wikis, priorities, memory files

### Step 3: Verify

```bash
echo "=== Latest handoff ===" && ls -t /opt/data/hermes-hq/handoffs/*-session-*-handoff.md | head -1
echo "=== Latest commit ===" && cd /opt/data/hermes-hq && git log --oneline -1
echo "=== Vault priorities ===" && head -20 /opt/data/hermes-hq/handoffs/99-Framework/Priorities.md
```

---

## When to Run

- **Every session start** — before `/start-gun`
- **After long breaks** — if it's been >8 hours since last session
- **When switching projects** — to load the right project wiki

---

## Integration with /start-gun

`/sync` is a prerequisite for `/start-gun`. The full session start sequence:

```
/sync          → Pull latest from GitHub + Vault
/start-gun     → Read task queue + handoff, claim task
/brand-new-day → Plan the day (if starting fresh)
/relay         → Build (if task warrants full relay)
```

---

*Part of the AEGIS operating system. Built by @jaidenrabatin.*
