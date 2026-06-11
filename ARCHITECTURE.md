# 🏗️ AEGIS-HQ — Sync Architecture (v2)

## The Problem We're Solving

Right now, context lives in scattered places:
- **Claude Code** only knows what's in the current session
- **GitHub** has handoffs, skills, and config — but Claude has to `git pull` manually
- **Your Obsidian vault** exists but isn't connected to anything
- **Google Drive** has files but no structure
- **Hermes** (me) holds context in memory, but it resets every session

The goal: **one unified operating system** where every agent, every session, and every tool reads from the same source of truth.

## The Architecture

```
                         ┌──────────────────────────┐
                         │    YOUR MAC (local)       │
                         │                          │
                         │  ~/aegis-hq/             │
                         │  ├── .obsidian/          │  ← Obsidian config
                         │  ├── 00-Inbox/           │
                         │  ├── 01-Projects/        │
                         │  │   ├── NoFomo/         │
                         │  │   ├── BET/            │
                         │  │   └── Thesis/         │
                         │  ├── 02-Areas/           │
                         │  ├── 03-Resources/       │
                         │  │   ├── Skills/         │  ← Claude Code skills
                         │  │   ├── Templates/      │
                         │  │   └── Content/        │  ← Carousel prompts, etc.
                         │  ├── 04-Archive/         │
                         │  ├── Handoffs/           │  ← Session snapshots
                         │  ├── 99-Framework/       │
                         │  │   ├── AGENTS.md       │  ← Agent architecture
                         │  │   ├── PROJECTS.md     │
                         │  │   ├── Priorities.md   │
                         │  │   └── MEMORY.md        │
                         │  └── Attic/              │  ← Old sessions
                         │                          │
                         └──────────┬───────────────┘
                                    │
                          rclone bisync (bidirectional)
                          or Obsidian Git plugin
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
            Google Drive     GitHub (private)    VPS (Hermes)
            (cloud backup)   (source of truth)   (runtime)
```

## Why This Structure

- **`~/aegis-hq/`** is the single vault folder on your Mac. Obsidian points here.
- **GitHub** is the sync hub. When Claude Code commits a handoff, GitHub Actions pushes it to Drive.
- **Google Drive** is the transport layer — gets files from GitHub to your Mac.
- **Hermes (VPS)** clones from GitHub, reads/writes handoffs, commits back.
- **Claude Code** clones from GitHub, reads context, writes output, commits back.

## The Sync Chain (3 paths)

### Path 1: Claude Code → GitHub → Drive → Your Mac
```
Claude Code commits handoff
    ↓ git push to hermes-hq
GitHub Action triggers
    ↓ rclone copy to Drive
rclone bisync on your Mac
    ↓ pulls from Drive
Obsidian sees the update
```

### Path 2: Your Mac → GitHub → VPS (Hermes)
```
You create a note in Obsidian
    ↓ git commit to aegis-hq (via Obsidian Git plugin)
GitHub receives push
    ↓ Hermes pulls at session start
Hermes reads your new context
```

### Path 3: Hermes → GitHub → Claude Code
```
Hermes writes a handoff / task
    ↓ git push to hermes-hq
Claude Code pulls at /sync
    ↓ reads latest handoff
Context is loaded
```

## What Moves Where

| Content Type | Lives In | Synced To |
|---|---|---|
| Session handoffs | `/Handoffs/` | Drive, VPS |
| Skills (for Claude Code) | `/03-Resources/Skills/` | Drive, VPS |
| Project wikis | `/01-Projects/` | Drive |
| Daily notes | `/00-Inbox/` | Drive |
| Priorities / tasks | `/99-Framework/` | Drive, VPS |
| Agent config | `/99-Framework/AGENTS.md` | Drive, VPS |
| Content (carousels, etc.) | `/03-Resources/Content/` | Drive |
| Claude Code builds | `/01-Projects/NoFomo/` etc. | GitHub (dedicated repos) |

## Key Design Decisions

**Why not put project repos inside the vault?**
- Project repos (NoFomo, BET) have their own git history, CI/CD, and deploy pipelines
- The vault stores the *context about* projects, not the project code itself
- This keeps the vault lightweight and avoids nested git conflicts

**Why GitHub as the hub instead of Drive?**
- GitHub has Actions (automation), PRs (review), and granular permissions
- Drive is a file store — no automation, no versioning conflicts resolved cleanly
- Git merge > file overwrite

**Why not just use Obsidian Git plugin alone?**
- The Obsidian Git plugin syncs your Mac ↔ GitHub. That handles 2 of 3 paths.
- But Claude Code on the VPS can't use the Obsidian Git plugin — it needs `git pull` + `rclone`.
- So we need both: Obsidian Git (Mac ↔ GitHub) + rclone (GitHub ↔ Drive ↔ VPS)

## Migration Path (Safe, No Breaking)

### Step 1: Set up the local vault (your Mac)
```bash
# On your Mac:
mkdir -p ~/aegis-hq
cd ~/aegis-hq
git init
git remote add origin git@github.com:Maple-maker/hermes-hq.git  # or use the existing repo
```

### Step 2: Set up Obsidian
1. Open Obsidian → "Open folder as vault" → select `~/aegis-hq/`
2. Install the "Obsidian Git" community plugin
3. Configure: auto-pull every 5 min, auto-push on save

### Step 3: Set up the folder structure
```
~/aegis-hq/
├── .obsidian/             ← Obsidian config (auto-created)
├── 00-Inbox/
├── 01-Projects/
├── 02-Areas/
├── 03-Resources/
│   ├── Skills/
│   ├── Templates/
│   └── Content/
├── 04-Archive/
├── Handoffs/
└── 99-Framework/
    ├── AGENTS.md
    ├── PROJECTS.md
    ├── Priorities.md
    └── MEMORY.md
```

### Step 4: Migrate existing content (non-breaking)
- Copy `handoffs/` from `hermes-hq` → `~/aegis-hq/handoffs/`
- Copy `content/` → `~/aegis-hq/03-Resources/Content/`
- Copy `skills/` → `~/aegis-hq/03-Resources/Skills/`
- Copy context files → `~/aegis-hq/99-Framework/`

### Step 5: Set up GitHub Action
The Action we already built pushes to Drive. No change needed.

### Step 6: Set up rclone on your Mac
```bash
brew install rclone
rclone config  # set up gdrive: once, same as on the VPS
```

Then a simple sync script:
```bash
#!/bin/bash
# ~/aegis-hq/sync.sh
rclone bisync gdrive:1H4QDzKCq7lN_6PS4WHKDCRBcpjBSra2d/ ~/aegis-hq/ --create-empty-src-dirs -v
```

## What Could Break (and How to Avoid It)

| Risk | Mitigation |
|---|---|
| Git conflicts from simultaneous edits | Obsidian Git has conflict handling; Claude Code commits to different paths |
| Drive sync overwriting changes | Use `rclone bisync` (two-way) not `rclone copy` (one-way) |
| Obsidian plugin corrupting files | `.obsidian/` is gitignored by default; vault files are plain markdown |
| VPS and Mac editing the same file | Handoffs are append-only from VPS; Mac edits are framework/priorities |
| GitHub Action failing silently | Action logs are visible; `/finish-line` on VPS also does a direct rclone push |

## The Two rclone Remotes

Right now on the VPS we have one Drive remote: `gdrive:`. For the full architecture, the Mac needs its own rclone config. The folder IDs are the same — but each machine authenticates separately.

Want me to generate a step-by-step guide for your Mac setup?
