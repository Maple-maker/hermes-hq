#!/usr/bin/env python3
"""
NoFomo TikTok Slideshow Generator
Pixel-perfect brand slides compiled into a TikTok-ready video.

Usage:
    ./generate_slides.py --ticker CRVO [--output-dir ./output]
"""

import argparse
import json
import math
import os
import subprocess
import textwrap
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ─── Brand Constants (from NOFOMO-BRAND-GUIDE.md) ──────────────────────────

BG       = (10, 10, 15)       # #0A0A0F
CARD     = (18, 18, 26)       # #12121A
ELEVATED = (26, 26, 38)       # #1A1A26
BULL     = (0, 255, 136)      # #00FF88
BEAR     = (255, 59, 92)      # #FF3B5C
TIER1    = (255, 215, 0)      # #FFD700
TIER2    = (0, 191, 255)      # #00BFFF
ACCENT   = (123, 97, 255)     # #7B61FF
TEXT_PRI = (255, 255, 255)    # #FFFFFF
TEXT_SEC = (136, 136, 170)    # #8888AA
TEXT_MUT = (86, 86, 118)      # #565676
BORDER   = (255, 255, 255, 15) # 6% opacity

# Canvas
W, H = 1080, 1920  # TikTok portrait

# ─── Sample Data ─────────────────────────────────────────────────────────

OPPORTUNITIES = {
    "CRVO": {
        "ticker": "CRVO",
        "company": "Corvus Therapeutics",
        "sector": "Biotech · Oncology",
        "score": 91,
        "tier": 1,
        "triple_signal": True,
        "bluf": "FDA granted accelerated approval for CRV-431 in hepatocellular carcinoma. Two insiders bought $4.1M of stock 9 days prior. Market has not repriced the label expansion.",
        "price": 38.42,
        "upside_pct": 142,
        "market_cap": "$1.2B",
        "probability": 78,
        "catalyst": "FDA accelerated approval",
        "council": {"Gemini": "BULL", "DeepSeek": "BULL", "CIO": "BULL"},
        "buy_zones": {"Aggressive": 41.20, "Base": 37.80, "Conservative": 33.50},
        "source": "SEC Form 8-K filed 04/15/2026, insider Form 4 filings 04/06-04/10/2026",
        "hook": "This 8-K dropped at 4:01pm and nobody noticed.",
    },
    "HDRN": {
        "ticker": "HDRN",
        "company": "Hadrian Defense Systems",
        "sector": "Defense · Autonomy",
        "score": 84,
        "tier": 2,
        "triple_signal": False,
        "bluf": "Awarded $890M IDIQ ceiling on the Army's counter-UAS program. Backlog now exceeds 3x trailing revenue. Street models still anchor to the pre-award run rate.",
        "price": 62.18,
        "upside_pct": 64,
        "market_cap": "$4.8B",
        "probability": 71,
        "catalyst": "Government contract award",
        "council": {"Gemini": "BULL", "DeepSeek": "BULL", "CIO": "BULL"},
        "buy_zones": {"Aggressive": 66.00, "Base": 60.50, "Conservative": 54.00},
        "source": "DoD contract announcement 05/01/2026",
        "hook": "One filing. $890M ceiling. Zero headlines.",
    },
    "MRDN": {
        "ticker": "MRDN",
        "company": "Meridian Energy",
        "sector": "Energy · Grid Storage",
        "score": 88,
        "tier": 1,
        "triple_signal": True,
        "bluf": "DOE loan guarantee closed on a 4-state grid-storage buildout. CEO and CFO bought a combined $6.8M in the open market the same week.",
        "price": 21.07,
        "upside_pct": 96,
        "market_cap": "$2.9B",
        "probability": 74,
        "catalyst": "DOE loan + insider cluster",
        "council": {"Gemini": "BULL", "DeepSeek": "BULL", "CIO": "BULL"},
        "buy_zones": {"Aggressive": 22.40, "Base": 20.10, "Conservative": 17.60},
        "source": "DOE LPO announcement 05/12/2026, insider Form 4 filings",
        "hook": "CEO and CFO bought $6.8M the same week the DOE closed.",
    },
}


# ─── Drawing Helpers ─────────────────────────────────────────────────────

def _make_font(size, bold=False):
    """Try to load a reasonable mono/sans font, fall back to default."""
    family = "DejaVuSansMono-Bold" if bold else "DejaVuSansMono"
    if bold:
        paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
    else:
        paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def _make_font_sans(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def _draw_rounded_rect(draw, xy, radius, fill=None, outline=None, width=1):
    """Draw a rounded rectangle."""
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def _draw_pill_badge(draw, x, y, text, fg_color, bg_color, font=None):
    """Draw a pill-shaped badge centered at (x, y)."""
    if font is None:
        font = _make_font(24, bold=True)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    pad_x, pad_y = 16, 6
    bw = tw + pad_x * 2
    bh = th + pad_y * 2
    _draw_rounded_rect(draw, (x - bw // 2, y - bh // 2, x + bw // 2, y + bh // 2),
                       radius=bh // 2, fill=bg_color)
    draw.text((x - tw // 2, y - th // 2), text, fill=fg_color, font=font)
    return bh


def _wrap_text(text, max_width, font, draw):
    """Wrap text to fit within max_width pixels."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = current + " " + word if current else word
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# ─── Slide Builders ──────────────────────────────────────────────────────

def create_slide_hook(data):
    """Slide 1: Hook + NoFomo wordmark"""
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    
    # Large hook text
    hook_font = _make_font_sans(56, bold=True)
    hook_lines = _wrap_text(data["hook"], W - 160, hook_font, draw)
    
    y = 500
    for line in hook_lines:
        bbox = draw.textbbox((0, 0), line, font=hook_font)
        draw.text(((W - (bbox[2] - bbox[0])) // 2, y), line, fill=TEXT_PRI, font=hook_font)
        y += 72
    
    # Hook subtitle
    sub_font = _make_font_sans(28)
    sub = f"{data['ticker']} · {data['company']}"
    bbox = draw.textbbox((0, 0), sub, font=sub_font)
    draw.text(((W - (bbox[2] - bbox[0])) // 2, y + 20), sub, fill=TEXT_SEC, font=sub_font)
    
    # NoFomo wordmark at bottom
    mark_font = _make_font_sans(32, bold=True)
    mark = "N O F O M O"
    bbox = draw.textbbox((0, 0), mark, font=mark_font)
    draw.text(((W - (bbox[2] - bbox[0])) // 2, H - 120), mark, fill=ACCENT, font=mark_font)
    
    # Accent line
    for i in range(3):
        line_h = H - 90
        draw.rectangle([(W // 2 - 60 + i * 50, line_h), (W // 2 - 30 + i * 50, line_h + 3)], fill=BULL if i == 1 else BORDER)
    
    return img


def create_slide_ticker(data):
    """Slide 2: Ticker in mono, tier badge, score gauge"""
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    
    # Score gauge (circular arc)
    cx, cy = W // 2, 480
    radius = 160
    score = data["score"]
    tier_color = TIER1 if data["tier"] == 1 else TIER2
    
    # Draw gauge arc
    angle = (score / 100) * 270 - 135  # Start at -135, sweep 270 deg
    for deg in range(-135, int(-135 + (score / 100) * 270)):
        rad = math.radians(deg)
        x = int(cx + radius * math.cos(rad))
        y = int(cy + radius * math.sin(rad))
        # Arc thickness
        for r in range(radius - 8, radius + 4):
            rx = int(cx + r * math.cos(rad))
            ry = int(cy + r * math.sin(rad))
            draw.point((rx, ry), fill=tier_color)
    
    # Track ring (background arc)
    for deg in range(-135, 135):
        rad = math.radians(deg)
        for r in range(radius - 6, radius + 2):
            rx = int(cx + r * math.cos(rad))
            ry = int(cy + r * math.sin(rad))
            if img.getpixel((rx, ry)) == BG:
                draw.point((rx, ry), fill=(255, 255, 255, 18))
    
    # Score number
    score_font = _make_font(96, bold=True)
    score_text = str(score)
    bbox = draw.textbbox((0, 0), score_text, font=score_font)
    draw.text((cx - (bbox[2] - bbox[0]) // 2, cy - (bbox[3] - bbox[1]) // 2),
              score_text, fill=TEXT_PRI, font=score_font)
    
    # "/100" label
    label_font = _make_font(28)
    label_text = "/100"
    bbox = draw.textbbox((0, 0), label_text, font=label_font)
    draw.text((cx - (bbox[2] - bbox[0]) // 2, cy + 30), label_text, fill=TEXT_SEC, font=label_font)
    
    # Ticker
    ticker_font = _make_font(72, bold=True)
    bbox = draw.textbbox((0, 0), data["ticker"], font=ticker_font)
    draw.text(((W - (bbox[2] - bbox[0])) // 2, 680), data["ticker"], fill=TEXT_PRI, font=ticker_font)
    
    # Company name
    company_font = _make_font(32)
    bbox = draw.textbbox((0, 0), data["company"], font=company_font)
    draw.text(((W - (bbox[2] - bbox[0])) // 2, 770), data["company"], fill=TEXT_SEC, font=company_font)
    
    # Tier badge
    tier_text = "T1 EXCEPTIONAL" if data["tier"] == 1 else "T2 HIGH CONVICTION"
    badge_bg = (*tier_color[:3], 36) if data["tier"] == 1 else (*tier_color[:3], 36)
    _draw_pill_badge(draw, W // 2, 850, tier_text, tier_color, (*tier_color[:3], 36))
    
    # Triple signal indicator
    if data.get("triple_signal"):
        ts_font = _make_font(26, bold=True)
        ts_text = "⚡ TRIPLE SIGNAL"
        bbox = draw.textbbox((0, 0), ts_text, font=ts_font)
        draw.text(((W - (bbox[2] - bbox[0])) // 2, 900), ts_text, fill=TIER1, font=ts_font)
    
    # Upside
    upside_font = _make_font(48, bold=True)
    upside_text = f"+{data['upside_pct']}%"
    bbox = draw.textbbox((0, 0), upside_text, font=upside_font)
    draw.text(((W - (bbox[2] - bbox[0])) // 2, 980), upside_text, fill=BULL, font=upside_font)
    
    upside_label = "UPSIDE TARGET"
    label_font = _make_font(24)
    bbox = draw.textbbox((0, 0), upside_label, font=label_font)
    draw.text(((W - (bbox[2] - bbox[0])) // 2, 1035), upside_label, fill=TEXT_MUT, font=label_font)
    
    # Sector
    sector_font = _make_font(24)
    bbox = draw.textbbox((0, 0), data["sector"], font=sector_font)
    draw.text(((W - (bbox[2] - bbox[0])) // 2, 1120), data["sector"], fill=TEXT_SEC, font=sector_font)
    
    return img


def create_slide_bluf(data):
    """Slide 3: BLUF — what happened in 2-3 sentences"""
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    
    # BLUF label
    label_font = _make_font(24, bold=True)
    label_text = "BLUF · BOTTOM LINE UP FRONT"
    bbox = draw.textbbox((0, 0), label_text, font=label_font)
    draw.text(((W - (bbox[2] - bbox[0])) // 2, 350), label_text, fill=TEXT_MUT, font=label_font)
    
    # Separator
    draw.rectangle([(W // 2 - 30, 390), (W // 2 + 30, 393)], fill=ACCENT)
    
    # BLUF body
    body_font = _make_font_sans(36)
    body_lines = _wrap_text(data["bluf"], W - 160, body_font, draw)
    
    y = 460
    for line in body_lines:
        bbox = draw.textbbox((0, 0), line, font=body_font)
        draw.text(((W - (bbox[2] - bbox[0])) // 2, y), line, fill=TEXT_PRI, font=body_font)
        y += 52
    
    # Bottom note
    note_font = _make_font(22)
    note_text = f"The market is not pricing this in."
    bbox = draw.textbbox((0, 0), note_text, font=note_font)
    draw.text(((W - (bbox[2] - bbox[0])) // 2, H - 180), note_text, fill=ACCENT, font=note_font)
    
    return img


def create_slide_metrics(data):
    """Slide 4: Metrics strip — Price · Upside · Mkt Cap · Prob"""
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    
    # Section title
    title_font = _make_font_sans(28, bold=True)
    title_text = "KEY METRICS"
    bbox = draw.textbbox((0, 0), title_text, font=title_font)
    draw.text(((W - (bbox[2] - bbox[0])) // 2, 350), title_text, fill=TEXT_MUT, font=title_font)
    draw.rectangle([(W // 2 - 20, 395), (W // 2 + 20, 398)], fill=ACCENT)
    
    # Metrics card background
    card_x, card_y, card_w, card_h = 80, 460, W - 160, 340
    _draw_rounded_rect(draw, (card_x, card_y, card_x + card_w, card_y + card_h),
                       radius=18, fill=CARD)
    
    # 4-column grid
    metrics = [
        ("PRICE", f"${data['price']:.2f}", TEXT_PRI),
        ("UPSIDE", f"+{data['upside_pct']}%", BULL),
        ("MKT CAP", data["market_cap"], TEXT_PRI),
        ("PROB", f"{data['probability']}%", ACCENT),
    ]
    
    col_w = card_w // 4
    for i, (label, value, color) in enumerate(metrics):
        cx = card_x + col_w * i + col_w // 2
        
        # Value
        val_font = _make_font(40, bold=True)
        bbox = draw.textbbox((0, 0), value, font=val_font)
        draw.text((cx - (bbox[2] - bbox[0]) // 2, card_y + 35), value, fill=color, font=val_font)
        
        # Label
        lbl_font = _make_font(18)
        bbox = draw.textbbox((0, 0), label, font=lbl_font)
        draw.text((cx - (bbox[2] - bbox[0]) // 2, card_y + 85), label, fill=TEXT_MUT, font=lbl_font)
        
        # Vertical divider (not after last)
        if i < 3:
            dx = card_x + col_w * (i + 1)
            draw.rectangle([(dx, card_y + 30), (dx + 1, card_y + card_h - 30)], fill=BORDER)
    
    # Price reference
    ref_font = _make_font(26)
    ref_text = f"Price reference: ${data['price']:.2f} · Target range: ${data['buy_zones']['Aggressive']:.2f} - ${data['buy_zones']['Conservative']:.2f}"
    ref_lines = _wrap_text(ref_text, W - 160, ref_font, draw)
    y = 860
    for line in ref_lines:
        bbox = draw.textbbox((0, 0), line, font=ref_font)
        draw.text(((W - (bbox[2] - bbox[0])) // 2, y), line, fill=TEXT_SEC, font=ref_font)
        y += 36
    
    return img


def create_slide_council(data):
    """Slide 5: AI Council — 3 models, verdicts"""
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    
    # Title
    title_font = _make_font_sans(28, bold=True)
    draw.text(((W - draw.textbbox((0, 0), "AI COUNCIL", font=title_font)[2]) // 2, 350),
              "AI COUNCIL", fill=TEXT_MUT, font=title_font)
    draw.rectangle([(W // 2 - 20, 395), (W // 2 + 20, 398)], fill=ACCENT)
    
    # Subtitle
    sub_font = _make_font_sans(24)
    sub_text = "4 models debated this opportunity. Here's the verdict."
    bbox = draw.textbbox((0, 0), sub_text, font=sub_font)
    draw.text(((W - (bbox[2] - bbox[0])) // 2, 430), sub_text, fill=TEXT_SEC, font=sub_font)
    
    # Council chips
    models = list(data["council"].items())
    card_w = 240
    card_h = 180
    total_w = len(models) * card_w + (len(models) - 1) * 20
    start_x = (W - total_w) // 2
    
    for i, (model_name, verdict) in enumerate(models):
        cx = start_x + i * (card_w + 20)
        cy = 560
        
        # Card
        _draw_rounded_rect(draw, (cx, cy, cx + card_w, cy + card_h), radius=14, fill=CARD,
                          outline=(*TEXT_SEC, 15), width=1)
        
        # Verdict dot + name
        verdict_color = BULL if verdict == "BULL" else BEAR
        dot_r = 8
        draw.ellipse([(cx + 30 - dot_r, cy + 30 - dot_r), (cx + 30 + dot_r, cy + 30 + dot_r)],
                     fill=verdict_color)
        
        name_font = _make_font_sans(22, bold=True)
        draw.text((cx + 50, cy + 18), model_name, fill=TEXT_PRI, font=name_font)
        
        # Verdict text
        v_font = _make_font(38, bold=True)
        bbox = draw.textbbox((0, 0), verdict, font=v_font)
        draw.text((cx + (card_w - (bbox[2] - bbox[0])) // 2, cy + 70), verdict, fill=verdict_color, font=v_font)
        
        # Verdict chip border
        chip_h = 30
        draw.rounded_rectangle(
            [cx + 50, cy + card_h - 45, cx + card_w - 50, cy + card_h - 15],
            radius=6, fill=None, outline=(*verdict_color, 56), width=1
        )
    
    # Summary at bottom
    bull_count = sum(1 for v in data["council"].values() if v == "BULL")
    summary_font = _make_font_sans(28)
    summary_text = f"{bull_count} of {len(models)} models agree: BULL"
    bbox = draw.textbbox((0, 0), summary_text, font=summary_font)
    draw.text(((W - (bbox[2] - bbox[0])) // 2, 820), summary_text, fill=TEXT_PRI, font=summary_font)
    
    if bull_count == len(models):
        sig_font = _make_font(26, bold=True)
        sig_text = "UNANIMOUS BULL ⚡"
        bbox = draw.textbbox((0, 0), sig_text, font=sig_font)
        draw.text(((W - (bbox[2] - bbox[0])) // 2, 870), sig_text, fill=TIER1, font=sig_font)
    
    return img


def create_slide_catalyst(data):
    """Slide 6: What to watch — catalyst + date"""
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    
    # Title
    title_font = _make_font_sans(28, bold=True)
    draw.text(((W - draw.textbbox((0, 0), "WHAT TO WATCH", font=title_font)[2]) // 2, 350),
              "WHAT TO WATCH", fill=TEXT_MUT, font=title_font)
    draw.rectangle([(W // 2 - 20, 395), (W // 2 + 20, 398)], fill=ACCENT)
    
    # Catalyst card
    card_x, card_y, card_w, card_h = 120, 480, W - 240, 200
    _draw_rounded_rect(draw, (card_x, card_y, card_x + card_w, card_y + card_h),
                       radius=18, fill=CARD)
    
    # Catalyst icon/label
    cat_label = "CATALYST"
    l_font = _make_font(22)
    bbox = draw.textbbox((0, 0), cat_label, font=l_font)
    draw.text((card_x + 30, card_y + 30), cat_label, fill=TEXT_MUT, font=l_font)
    
    # Catalyst name
    cat_font = _make_font(42, bold=True)
    cat_text = data["catalyst"].upper()
    bbox = draw.textbbox((0, 0), cat_text, font=cat_font)
    draw.text((card_x + 30, card_y + 70), cat_text, fill=ACCENT, font=cat_font)
    
    # Buy zones
    bz_font = _make_font(24, bold=True)
    bz_y = 750
    draw.text(((W - draw.textbbox((0, 0), "BUY ZONES", font=bz_font)[2]) // 2, bz_y),
              "BUY ZONES", fill=TEXT_MUT, font=bz_font)
    
    zone_w = 260
    zone_gap = 20
    zone_start = (W - (zone_w * 3 + zone_gap * 2)) // 2
    zone_y = bz_y + 50
    zone_h = 140
    
    for i, (zone_name, zone_price) in enumerate(data["buy_zones"].items()):
        zx = zone_start + i * (zone_w + zone_gap)
        _draw_rounded_rect(draw, (zx, zone_y, zx + zone_w, zone_y + zone_h),
                          radius=14, fill=ELEVATED)
        
        # Zone label
        zl_font = _make_font(20)
        bbox = draw.textbbox((0, 0), zone_name.upper(), font=zl_font)
        draw.text((zx + (zone_w - (bbox[2] - bbox[0])) // 2, zone_y + 20),
                  zone_name.upper(), fill=TEXT_MUT, font=zl_font)
        
        # Zone price
        zp_font = _make_font(38, bold=True)
        zp_text = f"${zone_price:.2f}"
        bbox = draw.textbbox((0, 0), zp_text, font=zp_font)
        draw.text((zx + (zone_w - (bbox[2] - bbox[0])) // 2, zone_y + 55),
                  zp_text, fill=TEXT_PRI, font=zp_font)
    
    return img


def create_slide_source(data):
    """Slide 7: Source citation"""
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    
    # Title
    title_font = _make_font_sans(28, bold=True)
    draw.text(((W - draw.textbbox((0, 0), "SOURCE", font=title_font)[2]) // 2, 400),
              "SOURCE", fill=TEXT_MUT, font=title_font)
    draw.rectangle([(W // 2 - 20, 445), (W // 2 + 20, 448)], fill=ACCENT)
    
    # Source text
    src_font = _make_font_sans(30)
    src_text = data["source"]
    src_lines = _wrap_text(src_text, W - 200, src_font, draw)
    
    y = 540
    for line in src_lines:
        bbox = draw.textbbox((0, 0), line, font=src_font)
        draw.text(((W - (bbox[2] - bbox[0])) // 2, y), line, fill=TEXT_SEC, font=src_font)
        y += 44
    
    # Disclaimers
    disc_font = _make_font(22)
    disclaimers = [
        "SEC filings, insider Form 4s, and public disclosures.",
        "Data-driven. Verifiable. Transparent.",
    ]
    y = 700
    for disc in disclaimers:
        bbox = draw.textbbox((0, 0), disc, font=disc_font)
        draw.text(((W - (bbox[2] - bbox[0])) // 2, y), disc, fill=TEXT_MUT, font=disc_font)
        y += 36
    
    # Disclaimer
    disc_font2 = _make_font(18)
    disc2 = "Not financial advice. Educational content only."
    bbox = draw.textbbox((0, 0), disc2, font=disc_font2)
    draw.text(((W - (bbox[2] - bbox[0])) // 2, H - 160), disc2, fill=TEXT_MUT, font=disc_font2)
    
    return img


def create_slide_cta(data):
    """Slide 8: CTA — Free weekly catalyst report"""
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    
    # Hook reminder
    hook_font = _make_font_sans(44, bold=True)
    hook_text = "See this before the crowd."
    bbox = draw.textbbox((0, 0), hook_text, font=hook_font)
    draw.text(((W - (bbox[2] - bbox[0])) // 2, 500), hook_text, fill=TEXT_PRI, font=hook_font)
    
    # Subtitle
    sub_font = _make_font_sans(28)
    sub_text = "Join 0+ investors who get the weekly catalyst report."
    bbox = draw.textbbox((0, 0), sub_text, font=sub_font)
    draw.text(((W - (bbox[2] - bbox[0])) // 2, 590), sub_text, fill=TEXT_SEC, font=sub_font)
    
    # CTA Button outline
    btn_w, btn_h = 400, 70
    btn_x = (W - btn_w) // 2
    btn_y = 720
    _draw_rounded_rect(draw, (btn_x, btn_y, btn_x + btn_w, btn_y + btn_h),
                       radius=35, fill=None, outline=BULL, width=2)
    
    cta_font = _make_font_sans(28, bold=True)
    cta_text = "FREE REPORT → LINK IN BIO"
    bbox = draw.textbbox((0, 0), cta_text, font=cta_font)
    draw.text(((W - (bbox[2] - bbox[0])) // 2, btn_y + (btn_h - (bbox[3] - bbox[1])) // 2),
              cta_text, fill=BULL, font=cta_font)
    
    # NoFomo wordmark
    mark_font = _make_font_sans(36, bold=True)
    mark_text = "N O F O M O"
    bbox = draw.textbbox((0, 0), mark_text, font=mark_font)
    draw.text(((W - (bbox[2] - bbox[0])) // 2, H - 160), mark_text, fill=ACCENT, font=mark_font)
    
    # Disclaimer
    disc_font = _make_font(18)
    disc_text = "Not financial advice. Educational content only."
    bbox = draw.textbbox((0, 0), disc_text, font=disc_font)
    draw.text(((W - (bbox[2] - bbox[0])) // 2, H - 100), disc_text, fill=TEXT_MUT, font=disc_font)
    
    return img


# ─── Main ────────────────────────────────────────────────────────────────

def generate_slideshow(ticker, output_dir="/tmp/nofomo_slideshow"):
    """Generate all slides for a given ticker."""
    data = OPPORTUNITIES.get(ticker.upper())
    if not data:
        print(f"Unknown ticker: {ticker}")
        print(f"Available: {', '.join(OPPORTUNITIES.keys())}")
        return []
    
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    
    slides = [
        ("01_hook", create_slide_hook),
        ("02_ticker", create_slide_ticker),
        ("03_bluf", create_slide_bluf),
        ("04_metrics", create_slide_metrics),
        ("05_council", create_slide_council),
        ("06_catalyst", create_slide_catalyst),
        ("07_source", create_slide_source),
        ("08_cta", create_slide_cta),
    ]
    
    paths = []
    for name, func in slides:
        img = func(data)
        path = out / f"{name}_{ticker.lower()}.png"
        img.save(str(path))
        paths.append(str(path))
        print(f"  ✓ {path.name}")
    
    return paths


def compile_video(slide_paths, output_path="/tmp/nofomo_slideshow/output.mp4"):
    """Compile slides into a TikTok slideshow video with crossfade transitions."""
    if not slide_paths:
        return None
    
    # Generate ffmpeg concat file with crossfade
    # Each slide displays for 2.5 seconds with 0.5s crossfade
    duration = 2.5
    transition = 0.5
    
    # First, create individual slide videos with proper timing
    input_files = []
    filter_parts = []
    
    for i, path in enumerate(slide_paths):
        name = f"s{i}"
        input_files.append(f"-loop 1 -t {duration} -i \"{path}\"")
        if i == 0:
            filter_parts.append(f"[{i}:v]format=yuva420p[v{i}]")
        else:
            filter_parts.append(f"[{i}:v]format=yuva420p[v{i}]")
    
    # Build crossfade filter
    # Start with first slide, crossfade each subsequent one
    filter_complex = ""
    for i in range(1, len(slide_paths)):
        offset = (i * duration) - transition
        if i == 1:
            filter_complex += f"[0:v][{i}:v]xfade=transition=fade:duration={transition}:offset={offset}[v{i}]"
        else:
            filter_complex += f";[v{i-1}][{i}:v]xfade=transition=fade:duration={transition}:offset={offset}[v{i}]"
    
    # For the last filter output
    last = len(slide_paths) - 1
    
    cmd = (
        f"ffmpeg -y "
        + " ".join(input_files)
        + f" -filter_complex \"{filter_complex}\""
        + f" -map \"[v{last}]\""
        + f" -c:v libx264 -pix_fmt yuv420p -r 30"
        + f" -preset fast -crf 22"
        + f" \"{output_path}\""
    )
    
    print(f"\nCompiling video...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        print(f"ffmpeg stderr: {result.stderr[:500]}")
        # Fallback: simple concat without transitions
        print("Falling back to simple concat...")
        concat_path = "/tmp/concat_list.txt"
        with open(concat_path, "w") as f:
            for path in slide_paths:
                f.write(f"file '{path}'\n")
                f.write(f"duration {duration}\n")
        
        cmd2 = (
            f"ffmpeg -y -f concat -safe 0 -i \"{concat_path}\""
            f" -c:v libx264 -pix_fmt yuv420p -r 30"
            f" -preset fast -crf 22"
            f" \"{output_path}\""
        )
        subprocess.run(cmd2, shell=True, capture_output=True, text=True, timeout=120)
    
    print(f"  ✓ Video: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Generate NoFomo TikTok slideshow")
    parser.add_argument("--ticker", default="CRVO", help="Ticker to feature")
    parser.add_argument("--output-dir", default="/tmp/nofomo_slideshow", help="Output directory")
    parser.add_argument("--video", action="store_true", default=True, help="Compile video")
    args = parser.parse_args()
    
    print(f"🎬 Generating NoFomo slideshow for {args.ticker}...\n")
    paths = generate_slideshow(args.ticker, args.output_dir)
    
    if args.video and paths:
        video_path = os.path.join(args.output_dir, f"nofomo_{args.ticker.lower()}.mp4")
        compile_video(paths, video_path)
    
    print(f"\n✅ Done! {len(paths)} slides generated.")
    return paths


if __name__ == "__main__":
    main()