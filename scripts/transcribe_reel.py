#!/usr/bin/env python3
"""
transcribe_reel.py — Download Instagram reel and transcribe with Whisper.

Usage:
    python3 transcribe_reel.py <instagram_url> [--output-dir <dir>] [--model tiny|base|small|medium]

Requirements:
    pip install yt-dlp openai-whisper
    # OR set OPENAI_API_KEY to use Whisper API (faster, more accurate)
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

VAULT_CLIPPINGS = Path("/opt/data/home/aegis_vault/03-Resources/Clippings")
SCRIPTS_DIR = Path(__file__).parent


def extract_shortcode(url: str) -> str:
    """Extract the shortcode from an Instagram reel URL."""
    m = re.search(r"/reel/([A-Za-z0-9_-]+)", url)
    if m:
        return m.group(1)
    raise ValueError(f"Could not extract shortcode from URL: {url}")


def download_reel(url: str, output_dir: Path) -> Path:
    """Download the reel video using yt-dlp. Returns path to video file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    template = str(output_dir / "%(id)s.%(ext)s")

    cmd = [
        "yt-dlp",
        "--no-playlist",
        "-o", template,
        "-f", "mp4",
        "--no-check-certificates",
        url,
    ]

    print(f"[download] Running yt-dlp for {url}...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"[error] yt-dlp failed:\n{result.stderr[:500]}", file=sys.stderr)
        sys.exit(1)

    # Find the downloaded video
    videos = list(output_dir.glob("*.mp4"))
    if not videos:
        print("[error] No video file found after download", file=sys.stderr)
        sys.exit(1)

    return videos[0]


def extract_audio(video_path: Path) -> Path:
    """Extract audio from video as WAV for Whisper."""
    audio_path = video_path.with_suffix(".wav")
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vn",                    # no video
        "-acodec", "pcm_s16le",  # 16-bit PCM
        "-ar", "16000",           # 16kHz (Whisper optimal)
        "-ac", "1",               # mono
        str(audio_path),
    ]
    print(f"[audio] Extracting audio from {video_path.name}...")
    subprocess.run(cmd, capture_output=True, text=True)
    return audio_path


def transcribe_with_api(audio_path: Path) -> str:
    """Use OpenAI Whisper API (fast, accurate). Requires OPENAI_API_KEY."""
    import openai
    client = openai.OpenAI()
    with open(audio_path, "rb") as f:
        resp = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="text",
        )
    return resp.strip()


def transcribe_with_local(audio_path: Path, model_name: str = "base") -> str:
    """Use local Whisper model (slower, no API key needed)."""
    import whisper
    print(f"[whisper] Loading {model_name} model (this may take a moment)...")
    model = whisper.load_model(model_name)
    result = model.transcribe(str(audio_path), language="en")
    return result["text"].strip()


def transcribe(audio_path: Path, model: str = "base") -> str:
    """Transcribe audio using API (preferred) or local Whisper."""
    if os.environ.get("OPENAI_API_KEY"):
        try:
            return transcribe_with_api(audio_path)
        except Exception as e:
            print(f"[warn] API transcription failed ({e}), falling back to local...")
    return transcribe_with_local(audio_path, model)


def parse_hook_structure(transcript: str) -> dict:
    """Extract hook pattern, key points, and CTA from transcript."""
    lines = [l.strip() for l in transcript.split("\n") if l.strip()]

    # Detect hook type
    hook_type = "Unknown"
    hook_line = ""
    if lines:
        first = lines[0]
        if re.search(r"\b[SABCDF]-tier\b", first, re.IGNORECASE):
            hook_type = "S-tier / F-tier"
            hook_line = first
        elif re.search(r"how to be good at", first, re.IGNORECASE):
            hook_type = "How to be good at X"
            hook_line = first
        elif re.search(r"^\d+\s+(things|ways|reasons|tips|habits)", first, re.IGNORECASE):
            hook_type = "List"
            hook_line = first
        elif "?" in first:
            hook_type = "Question"
            hook_line = first
        elif re.search(r"stop (doing|buying|selling)", first, re.IGNORECASE):
            hook_type = "Mistake / Stop doing"
            hook_line = first
        else:
            hook_line = first

    # Detect CTA
    cta = ""
    cta_patterns = [
        r"comment\s+[\"']?(\w+)[\"']?",
        r"follow\s+for\s+more",
        r"link\s+in\s+bio",
        r"save\s+this",
        r"share\s+this",
    ]
    for line in reversed(lines):  # CTA is usually at the end
        for pat in cta_patterns:
            m = re.search(pat, line, re.IGNORECASE)
            if m:
                cta = line
                break
        if cta:
            break

    # Extract key points (sentences with numbers, arrows, or short punchy lines)
    key_points = []
    for line in lines[1:]:  # skip hook
        if re.match(r"^\d+[\.\)]", line) or line.startswith("→") or line.startswith("-"):
            key_points.append(line.lstrip("→- ").strip())
        elif len(line) < 80 and any(kw in line.lower() for kw in ["is the", "means", "because", "when you", "most people"]):
            key_points.append(line)

    return {
        "hook_type": hook_type,
        "hook_line": hook_line,
        "hook_word_count": len(hook_line.split()),
        "key_points": key_points[:5],  # max 5
        "cta": cta,
    }


def save_transcript(shortcode: str, username: str, transcript: str, analysis: dict, url: str) -> Path:
    """Save transcript and analysis to vault."""
    VAULT_CLIPPINGS.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    filename = f"instagram-{shortcode}-{username}-{today}.md"
    path = VAULT_CLIPPINGS / filename

    content = f"""# 📱 Instagram Reel Transcript

> **URL:** {url}
> **Shortcode:** {shortcode}
> **Creator:** @{username}
> **Transcribed:** {today}

---

## Transcript

{transcript}

---

## Hook Structure

| Field | Value |
|-------|-------|
| **Type** | {analysis['hook_type']} |
| **Hook line** | "{analysis['hook_line']}" |
| **Hook word count** | {analysis['hook_word_count']} |
| **CTA** | {analysis['cta'] or '(none detected)'} |

## Key Points

"""
    for i, point in enumerate(analysis["key_points"], 1):
        content += f"{i}. {point}\n"

    content += f"""
---

## Raw Transcript

```
{transcript}
```

---

*Transcribed by AEGIS /transcribe skill. Source: Instagram reel.*
"""

    path.write_text(content)
    print(f"[save] Transcript saved to {path}")
    return path


def main():
    parser = argparse.ArgumentParser(description="Transcribe Instagram reel")
    parser.add_argument("url", help="Instagram reel URL")
    parser.add_argument("--output-dir", default="/tmp/reels", help="Temp download directory")
    parser.add_argument("--model", default="base", choices=["tiny", "base", "small", "medium"],
                        help="Whisper model size (default: base)")
    parser.add_argument("--keep-video", action="store_true", help="Don't delete downloaded video")
    args = parser.parse_args()

    shortcode = extract_shortcode(args.url)
    output_dir = Path(args.output_dir)

    # Download
    video_path = download_reel(args.url, output_dir)

    # Extract audio
    audio_path = extract_audio(video_path)

    # Transcribe
    transcript = transcribe(audio_path, args.model)
    print(f"\n[transcript]\n{transcript}\n")

    # Analyze
    analysis = parse_hook_structure(transcript)

    # Try to extract username from yt-dlp output or URL
    username = "unknown"
    try:
        result = subprocess.run(
            ["yt-dlp", "--print", "uploader", "--no-download", args.url],
            capture_output=True, text=True, timeout=30
        )
        if result.stdout.strip():
            username = result.stdout.strip().replace("@", "")
    except Exception:
        pass

    # Save
    path = save_transcript(shortcode, username, transcript, analysis, args.url)

    # Cleanup
    if not args.keep_video:
        video_path.unlink(missing_ok=True)
        audio_path.unlink(missing_ok=True)

    print(f"\n✅ Done. Transcript: {path}")
    print(f"   Hook type: {analysis['hook_type']}")
    print(f"   Key points: {len(analysis['key_points'])}")
    print(f"   CTA: {analysis['cta'] or '(none)'}")


if __name__ == "__main__":
    main()
