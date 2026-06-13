# 🧠 Second Brain Protocol — LLM-Maintained Wiki

> **Source:** Karpathy's pattern (via @av1dlive, June 2026)
> **Core idea:** Not an app. A pattern. Let an LLM maintain a wiki of your notes. You dump sources, it reads them, links them, files them. Knowledge compounds like interest.

---

## The Pattern

```
You dump sources (links, notes, docs, transcripts)
    ↓
LLM reads them
    ↓
LLM links them to existing knowledge
    ↓
LLM files them in the right place in your wiki
    ↓
Knowledge compounds like interest
```

## How This Works in AEGIS

### Current State
- **AEGIS Vault** = the wiki (Obsidian on Drive, synced from GitHub)
- **Hermes** = the LLM that maintains it
- **You** = the source dumper

### The Protocol

**Step 1: Dump**
Share anything with Hermes — links, documents, transcripts, screenshots, voice memos, ideas.

**Step 2: Hermes Processes**
For each dump, Hermes:
1. Reads/extracts the content
2. Identifies what it is (idea, reference, task, spec, etc.)
3. Links it to existing vault content (related projects, prior notes, relevant skills)
4. Files it in the right vault folder
5. Updates the relevant project wiki or handoff

**Step 3: Vault Stays Current**
The vault becomes a compounding knowledge base. Every new piece of information makes the whole system smarter.

### Vault Folders for This

| Folder | What goes here |
|--------|----------------|
| `00-Inbox/` | Raw dumps — unprocessed links, quick notes, voice memo transcripts |
| `03-Resources/Research/` | Processed research — articles, papers, analysis |
| `03-Resources/Clippings/` | Web clippings, social posts, quotes |
| `01-Projects/` | Project-specific knowledge (NoFomo, AERO, Thesis) |
| `99-Framework/` | System-level knowledge (skills, SOPs, architecture) |

### The Compounding Effect

```
Week 1: 10 notes → 0 links
Week 4: 40 notes → 12 links (new notes connect to old)
Week 12: 120 notes → 60 links (knowledge graph emerges)
Week 26: 260 notes → 180 links (second brain is alive)
```

Each new note is more valuable because it connects to everything before it.

---

## Integration with Existing Skills

| Skill | Role in Second Brain |
|-------|---------------------|
| `/handoff` | Dumps ideas into the vault as structured tasks |
| `/vault-check` | Weekly curation — prunes stale, revives dormant, combines related |
| `/brand-new-day` | Reads vault snapshots to plan the day |
| `/sync` | Keeps GitHub ↔ Vault in sync |
| `/finish-line` | Saves session knowledge to the vault |

---

## The Claude Code Plugin

The X post mentions someone built this as a free Claude Code plugin. The pattern is:
- You dump sources into a folder
- Claude Code reads them on session start
- It links and files them automatically
- Your wiki stays current without manual organization

**This is exactly what `/sync` + `/vault-check` do in AEGIS.** The difference: our system is already built and integrated with your existing workflow.

---

## Action Items

- [ ] Set up the `00-Inbox/` folder as the default dump location
- [ ] When sharing links/notes with Hermes, say "file this" to trigger the second brain protocol
- [ ] Run `/vault-check` weekly to maintain the knowledge graph
- [ ] Review `03-Resources/Clippings/` monthly for content ideas

---

*Added to AEGIS file system: 2026-06-12. Source: @av1dlive tweet about Karpathy's second brain pattern.*
