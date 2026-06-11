# /vault-check — Periodic Vault Curation

> Run weekly (or on demand). Hermes reviews the AEGIS Vault and prompts Jaiden to: delete stale files, revive old ideas, or find new uses for existing information.

---

## Purpose

The vault accumulates files over time. Without curation:
- Old handouts pile up with no action
- Project wikis go stale
- Ideas get captured but never revisited
- Duplicate or outdated information creates noise

`/vault-check` is the periodic review that keeps the vault sharp.

---

## When to Use

- **Weekly** — every Sunday, as part of the weekly scan
- **On demand** — when Jaiden says "clean up the vault" or "what's in the vault"
- **Before major planning** — before `/brand-new-day` for a new project

---

## The Curation Protocol

### Step 1: Inventory the Vault

```bash
cd /opt/data/home/aegis_vault

# List all files with ages
find . -name "*.md" -not -path "./.obsidian/*" -printf "%T@ %Tc %p\n" | sort -n

# Count by folder
for d in */; do echo "$d: $(find "$d" -name "*.md" | wc -l) files"; done
```

### Step 2: Classify Each File

For each file, determine:

| Category | Action |
|----------|--------|
| **Stale** — >30 days old, project complete or abandoned | Prompt: "Delete or archive?" |
| **Dormant** — >14 days old, idea not acted on | Prompt: "Still interested? Want to schedule this?" |
| **Outdated** — superseded by newer version | Prompt: "Replace with newer version?" |
| **Orphaned** — references a project/task that no longer exists | Prompt: "Delete orphan?" |
| **Active** — <14 days old or actively being worked | No action needed |
| **Evergreen** — reference material, templates, skills | No action needed |

### Step 3: Generate the Curation Report

Present to Jaiden:

```
🔍 Vault Curation Report — [DATE]

📊 Overview:
- Total files: 47
- Active: 23
- Stale: 8
- Dormant: 5
- Outdated: 3
- Orphaned: 2
- Evergreen: 6

⚠️ Needs Attention:

1. [STALE] handoffs/nofomo-session-1-handoff.md (45 days old)
   → Session 1 is complete. Archive or delete?
   
2. [DORMANT] 00-Inbox/ai-debate-club-idea.md (21 days old)
   → You wanted to build a multi-LLM debate prototype. Still interested?
   → Suggestion: Add to next /brand-new-day planning.

3. [OUTDATED] 01-Projects/NoFomo-Wiki.md (superseded by session-2-handoff)
   → Wiki is 2 sessions behind. Update or delete?

4. [ORPHANED] 03-Resources/old-radar-spec.md
   → References radar v1 which was rebuilt. Delete?

💡 Suggestions:
- The AERO handoff hasn't been touched in 12 days. Want to schedule a build session?
- You have 3 content ideas in 00-Inbox that could become Instagram carousels.
- The SIGNAL_EXPANSION_TODO.md has 7 unchecked items. Worth a focused session?

Reply with: DELETE [file], ARCHIVE [file], REVIVE [file], UPDATE [file], or IGNORE.
```

### Step 4: Execute Jaiden's Decisions

```bash
# Delete
rm /opt/data/home/aegis_vault/path/to/file.md

# Archive
mkdir -p /opt/data/home/aegis_vault/04-Archive/
mv /opt/data/home/aegis_vault/path/to/file.md /opt/data/home/aegis_vault/04-Archive/

# Revive — move to project folder and create a task
mv /opt/data/home/aegis_vault/00-Inbox/idea.md /opt/data/home/aegis_vault/01-Projects/Idea-Name/
# Then create a task in the queue

# Update — flag for next session
echo "NEEDS UPDATE: $(date)" >> /opt/data/home/aegis_vault/path/to/file.md
```

### Step 5: Sync Changes

```bash
cd /opt/data/hermes-hq
git add -A
git commit -m "vault curation: [date] — [summary of changes]"
git push origin main

# Sync to Drive
rclone sync /opt/data/home/aegis_vault/ gdrive:1H4QDzKCq7lN_6PS4WHKDCRBcpjBSra2d/Vault/ --metadata -v
```

---

## Smart Prompts (Beyond Cleanup)

The curation isn't just about deleting. It's about **surfacing value**:

### "Still interested?"
For dormant ideas:
> "You captured this idea 3 weeks ago: [idea summary]. Still want to build it? I can schedule it for the next /brand-new-day."

### "New use for old info"
For existing content:
> "Your West Point AERO paper has a section on AR repair guidance. The NoFomo radar could use a similar 'overlay' pattern for displaying match results. Want me to explore this?"

### "Combine these"
For related files:
> "You have 3 separate notes about push notifications (NoFomo primer, thesis notify hook, APNs token storage). Want me to consolidate into one reference doc?"

### "Time to let go"
For stale projects:
> "The [project name] handoff is 60 days old with no activity. Archive it or schedule a revival session?"

---

## Integration with Weekly Scan

`/vault-check` runs as part of the weekly AI scan:

```
/weekly-scan
    ├── Market scan (existing)
    ├── Project status check (existing)
    ├── Vault curation (this skill) ← NEW
    └── Content pipeline check (existing)
```

---

## Scheduling

Add to cron for automatic weekly runs:

```
Every Sunday at 15:00 UTC (18:00 Amman):
/vault-check → generate report → send to Jaiden via Telegram
```

---

*Part of the AEGIS operating system. Built by @jaidenrabatin.*
