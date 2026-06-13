# /transcribe — Instagram Reel to Transcript

> Download any Instagram reel and transcribe it to text using Whisper. Captures the hook structure, key points, and CTA.

---

## Purpose

Instagram reels are JS-rendered — no API gives you the transcript. This skill:
1. Downloads the reel video using yt-dlp
2. Extracts the audio
3. Runs OpenAI Whisper to transcribe
4. Parses the transcript for hook structure, key points, and CTA
5. Saves to the vault as a structured content asset

---

## Requirements

```bash
# Install yt-dlp
pip install yt-dlp

# Install Whisper
pip install openai-whisper

# Or use the faster Whisper API (if key is set)
# Uses OpenAI's Whisper API instead of local model
```

---

## Usage

```bash
python3 /opt/data/scripts/transcribe_reel.py "https://www.instagram.com/reel/SHORTCODE/"
```

Or from Hermes:
> "Transcribe this reel: [URL]"

---

## What It Returns

```
TRANSCRIPT — @levelup.withliam — DZTC1XwBgpm
================================================

[Full transcript text...]

HOOK STRUCTURE:
  Type: [S-tier / F-tier / "How to" / List / Question]
  Hook line: "[exact hook text]"
  Hook word count: N

KEY POINTS:
  1. [Point 1]
  2. [Point 2]
  3. [Point 3]

CTA: "[Call to action text]"
CTA trigger: [Comment word / action]

CONTENT TYPE: [Educational / Promotional / List / Story]
TOPIC: [e.g., habits, trading, productivity]
```

---

## Storage

Transcripts are saved to:
```
/opt/data/home/aegis_vault/03-Resources/Clippings/
  instagram-[SHORTCODE]-[username]-[date].md
```

And synced to GitHub → Drive vault automatically.

---

## Hook Structure Templates

After transcription, Hermes extracts the hook format so it can be reused:

| Pattern | Example | Use for |
|---------|---------|---------|
| S-tier / F-tier | "S-tier habits" / "F-tier mistakes" | NoFomo signals, trading habits |
| "How to be good at X" | "How to spot alpha" | NoFomo features |
| List | "3 things I wish I knew" | Any feature |
| Question | "Why are you still...?" | Engagement bait |
| Mistake | "Stop doing this" | F-tier inversion |

---

## Notes

- Works with any public Instagram reel URL
- Private reels require login (not supported)
- Whisper accuracy: ~95% for clear English audio
- If the reel has background music, transcription may be less accurate
- Videos >5 minutes may need chunking
