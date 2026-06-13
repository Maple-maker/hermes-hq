# 🎬 Reel-to-Transcript Skill

> **Purpose:** Convert Instagram reels into usable transcripts for content creation, analysis, and vault storage.

---

## The Problem

Instagram is a JS-rendered SPA. Server-side scraping returns zero content. There's no public API for reel transcripts.

## What Actually Works

### Method 1: yt-dlp with Browser Cookies (Automated)

**One-time setup (on your Mac):**
1. Install Chrome extension: **"Get cookies.txt LOCALLY"**
2. Go to instagram.com while logged in
3. Click extension → Export → save to `~/.instagram_cookies.txt`

**Usage:**
```bash
python3 scripts/reel_transcript.py "https://www.instagram.com/reel/XXXXX/" --cookies ~/.instagram_cookies.txt
```

**Output:** JSON file with transcript, metadata, and extracted hooks.

### Method 2: Manual Copy-Paste (Simplest)

1. Open reel in browser
2. Turn on CC (auto-captions) if available
3. Copy transcript text
4. Save to `00-Inbox/reel-transcript-TITLE.md` or paste to Hermes

### Method 3: Whisper Transcription (No Cookies Needed)

If you can download the video file:
```bash
# Download video (works without cookies for public reels)
yt-dlp -o "reel.mp4" "URL"

# Transcribe with Whisper
whisper "reel.mp4" --model medium --language en
```

---

## Output Format

Every transcript is saved as:

```markdown
# 🎬 Reel Transcript

**Source:** [URL]
**Creator:** @handle
**Date:** YYYY-MM-DD
**Topic:** [brief description]

## Transcript

[Full transcript text]

## Key Hooks & Ideas

- [Hook 1 — the pattern interrupt]
- [Hook 2 — the claim]
- [Hook 3 — the CTA]

## Content Ideas

- [Idea 1 — how this applies to NoFomo/Thesis]
- [Idea 2 — carousel template based on this hook]
- [Idea 3 — security/protocol insight]

## Vault Placement

- **Folder:** 03-Resources/Clippings/
- **Tags:** #reel #content-idea #[topic]
```

---

## Integration with Content Pipeline

1. **Dump** → Share reel URL with Hermes
2. **Transcript** → Hermes extracts transcript (or you paste it)
3. **Analyze** → Hermes identifies hooks, ideas, and applications
4. **File** → Saved to `03-Resources/Clippings/` with tags
5. **Create** → Carousel templates generated from hook patterns
6. **Build** → Content created in Claude Design or Canva

---

## Folder Structure

```
03-Resources/Clippings/
├── reel-security-22k-bill.md          ← This file
├── reel-s-tier-habits.md             ← @levelup.withliam
├── reel-how-to-be-good-at-x.md       ← Template pattern
└── ...
```

---

*Part of the AEGIS content pipeline. Created: 2026-06-12.*
