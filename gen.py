#!/usr/bin/env python3
"""Render 'The World in One Day' - Sunday 22 November 2026.

Draws a dense newspaper front page (1024x1024) summarising the day's
world news. Two layouts: A = dense front page + map, B = visual-led.
Deterministic: fixed palette, fixed seed, no clock, no network.
"""
import argparse
import hashlib
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (250, 244, 230)
INK = (24, 22, 20)
RED = (158, 24, 24)
RED_LT = (196, 52, 44)
BLUE = (32, 64, 110)
TEAL = (18, 96, 92)
GOLD = (176, 128, 28)
GREY = (110, 104, 94)
LINE = (200, 190, 172)
SKY = (214, 228, 238)
SEA = (168, 196, 214)

FD = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FD, name), size)


F_MAST = font("DejaVuSerif-Bold.ttf", 46)
F_DATE = font("DejaVuSans-Bold.ttf", 30)
F_SUB = font("DejaVuSans.ttf", 13)
F_SUB_B = font("DejaVuSans-Bold.ttf", 13)
F_LEAD_H = font("DejaVuSerif-Bold.ttf", 37)
F_LEAD_S = font("DejaVuSans-Bold.ttf", 20)
F_BODY = font("DejaVuSans.ttf", 15)
F_BODY2 = font("DejaVuSans.ttf", 14)
F_CARD_H = font("DejaVuSans-Bold.ttf", 19)
F_CARD_S = font("DejaVuSans.ttf", 13)
F_CARD_H2 = font("DejaVuSans-Bold.ttf", 18)
F_CARD_H3 = font("DejaVuSans-Bold.ttf", 17)
F_CARD_H4 = font("DejaVuSans-Bold.ttf", 15)
F_CARD_S2 = font("DejaVuSans.ttf", 12)
F_SHORT = font("DejaVuSans.ttf", 12)
F_SHORT_B = font("DejaVuSans-Bold.ttf", 12)
F_FOOT = font("DejaVuSans.ttf", 11)
F_FOOT_B = font("DejaVuSans-Bold.ttf", 11)
F_MAP_T = font("DejaVuSans-Bold.ttf", 13)
F_NUM = font("DejaVuSans-Bold.ttf", 12)


def wrap(draw, text, fnt, width):
    """Wrap text to fit width; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit(draw, text, fnt, width, max_lines=None):
    """Wrap and, if needed, trim with an ellipsis to max_lines."""
    lines = wrap(draw, text, fnt, width)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and draw.textlength(lines[-1] + " ...", font=fnt) > width:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1].rstrip() + " ..."
    return lines


def trunc(draw, text, fnt, width):
    if draw.textlength(text, font=fnt) <= width:
        return text
    while text and draw.textlength(text + " ...", font=fnt) > width:
        text = text[:-1]
    return text.rstrip() + " ..."

# ---------------------------------------------------------------- stories
# Every story was verified against live sources on Mon 23 Nov 2026.
# Items marked (SAT) happened Saturday 21 Nov and are labelled as such
# in the image; (FRI) Friday 20 Nov. Everything else is 22 Nov 2026.
# Sources: Reuters, AP, CNN, BBC, The Times, WSJ, Euronews, AFP.

LEAD = {
    "n": 1,
    "kicker": "CLIMATE  •  ANTALYA, TURKEY",
    "head": "COP31 COLLAPSES",
    "sub": "No deal in Antalya",
    "body": ("The EU, Britain and island states refuse a pact that never "
             "mentions fossil fuels. The longest summit ends with no deal."),
    "scene": "cop",
    "loc": (30.7, 36.9),
}

# Illustrated cards 2..14 (variant A) / 2..11 (variant B subset)
CARDS = [
    {"n": 2, "kicker": "UKRAINE  •  DYMER",
     "head": "14 missing as drone flattens flats",
     "sub": "186 drones launched overnight; 161 downed. Rescuers dig "
            "through a collapsed block.",
     "sub2": "186 drones launched; 161 downed. Rescuers dig on.",
     "scene": "flats", "loc": (30.3, 50.8)},
    {"n": 3, "kicker": "LIBYA  •  BENGHAZI",
     "head": "Russian warship sunk at its berth",
     "sub": "Merkury capsizes after a suspected Ukrainian sea-drone "
            "strike. Ten hurt; SBU blamed.",
     "sub2": "Merkury capsizes after a sea-drone strike. Ten hurt.",
     "scene": "warship", "loc": (20.1, 32.1)},
    {"n": 4, "kicker": "BALTIC  •  GULF OF FINLAND",
     "head": "Burning cargo ship towed out of Finnish waters",
     "sub": "Towed out on Sunday after Saturday's drone hit. All 16 "
            "crew safe.",
     "sub2": "Towed out Sunday. All 16 crew safe.",
     "scene": "shipfire", "loc": (24.0, 59.8)},
    {"n": 5, "kicker": "GULF  •  BAHRAIN",
     "head": "Two hurt as Iran strikes US bases",
     "sub": "A Sitra factory burns; Tehran claims two Patriot radars hit. "
            "Iran starts rolling blackouts.",
     "sub2": "Sitra factory burns. Iran starts blackouts.",
     "scene": "radar", "loc": (50.6, 26.2)},
    {"n": 6, "kicker": "UKRAINE  •  KRYVYI RIH",
     "head": "Double-tap strike kills a boy of 7",
     "head2": "Double-tap strike kills a boy of 7",
     "sub": "A missile, then jet drones, hit the president's home city. "
            "Two dead, about 60 wounded.",
     "sub2": "Missile, then jet drones. Two dead, about 60 hurt.",
     "scene": "strike", "loc": (33.4, 47.9)},
    {"n": 7, "kicker": "TRADE  •  BRUSSELS  (SAT)",
     "head": "EU and Indonesia sign landmark trade deal",
     "head2": "EU-Indonesia sign trade deal",
     "sub": "After ten years of talks, tariffs fall on up to 98.5% of "
            "goods.",
     "sub2": "Ten years of talks end; tariffs fall on 98.5%.",
     "scene": "trade", "loc": (4.4, 50.8)},
    {"n": 8, "kicker": "MARKETS  •  NEW YORK  (FRI)",
     "head": "AI sell-off drags Wall Street into correction",
     "head2": "Wall Street falls into correction",
     "sub": "S&P 500 falls 3.7%, Nasdaq 5.3%; Nikkei drops 5.1%. Nvidia "
            "faces an SEC inquiry.",
     "sub2": "S&P -3.7%, Nasdaq -5.3%; Nikkei -5.1%.",
     "scene": "chart", "loc": (-74.0, 40.7)},
    {"n": 9, "kicker": "FOOTBALL  •  ANFIELD",
     "head": "Liverpool rout United 4-0",
     "head2": "Liverpool rout United 4-0",
     "sub": "Szoboszlai and Wirtz strike early. Hull stun Brighton 2-0 "
            "with two late goals.",
     "sub2": "Szoboszlai, Wirtz strike early. Hull stun Brighton.",
     "scene": "football", "loc": (-3.0, 53.4)},
    {"n": 10, "kicker": "INDONESIA  •  CIKANDE",
     "head": "Candy factory fire: 3 dead, 36 missing",
     "head2": "Factory fire: 3 dead, 36 missing",
     "sub": "Rescuers search the ruins west of Jakarta as families wait "
            "for news.",
     "sub2": "Rescuers search ruins west of Jakarta.",
     "scene": "factory", "loc": (106.3, -6.2)},
    {"n": 11, "kicker": "SPACE  •  MERCURY  (SAT)",
     "head": "BepiColombo slips into orbit around Mercury",
     "head2": "Probe orbits Mercury",
     "sub": "The ESA-JAXA probe ends an eight-year cruise to the smallest "
            "planet.",
     "sub2": "ESA-JAXA probe ends eight-year cruise.",
     "scene": "mercury", "loc": (8.6, 49.9)},
    {"n": 12, "kicker": "MEXICO  •  SINALOA  (SAT)",
     "head": "Cartel boss 'El Chapo Isidro' captured",
     "head2": "'El Chapo Isidro' captured",
     "sub": "Special forces seize the Sinaloa leader; 11 die, four of "
            "them soldiers.",
     "sub2": "Sinaloa leader seized; 11 die, four soldiers.",
     "scene": "badge", "loc": (-107.4, 24.8)},
    {"n": 13, "kicker": "EUROPE  •  WARSAW",
     "head": "NATO vows to defend 'every inch' of Poland",
     "head2": "NATO vows to defend Poland",
     "sub": "After Russian missiles fall on Polish soil, allies condemn "
            "the violations.",
     "sub2": "Allies condemn violations of Polish airspace.",
     "scene": "shield", "loc": (21.0, 52.2)},
    {"n": 14, "kicker": "NFL  •  SUNDAY",
     "head": "Cowboys pile up 51 in Dallas rout",
     "head2": "Cowboys pile up 51 in Dallas rout",
     "sub": "Dallas 51, Tennessee 30. Chiefs 34-7. Bills 26-9. Lions 31-21.",
     "sub2": "Dallas 51-30. Chiefs 34-7. Bills 26-9.",
     "scene": "nfl", "loc": (-96.8, 32.8)},
]

# Short one-line stories (variant A: 15..38; variant B: 15..34)
SHORTS = [
    (15, "Russia fired ~3,000 drones this week"),
    (16, "Trump posts photo of 'friends'"),
    (17, "Iran unveils dual missile launcher"),
    (18, "14 Iran tankers mass at Kharg Island"),
    (19, "Two tankers hit near Oman (SAT)"),
    (20, "Makkah alert; Houthis deny threat"),
    (21, "EU proposes 45bn euro loan (SAT)"),
    (22, "UN killer-robot treaty talks collapse"),
    (23, "Denmark ratifies Arctic deal (SAT)"),
    (24, "Anthropic slides; CoreWeave debt fears"),
    (25, "EU-Mexico cut 95% farm tariffs (SAT)"),
    (26, "France-Malaysia sign pact (SAT)"),
    (27, "Deutsche Bank falls on leaks (SAT)"),
    (28, "Leeds 4-1 Chelsea; Arsenal 2-2 (SAT)"),
    (29, "Panthers 35, Ravens 33; Eagles 19-16"),
    (30, "Gaza: 3 killed in drone strike (SAT)"),
    (31, "Peru quake 6.7: 1 dead, 16 hurt (FRI)"),
    (32, "UN chief: 'no ambiguity in science'"),
    (33, "Finland reimposes Gulf flight curbs"),
    (34, "Ella Langley wins CMA Entertainer (SAT)"),
    (35, "Assadi wins fiction Book Award (SAT)"),
    (36, "COP32: Addis Ababa, 8-19 Nov 2027"),
    (37, "Thanksgiving Thu; PCE data due Wed"),
    (38, "Beaver Moon supermoon peaks Mon-Tue"),
]

MAP_DOTS = [  # (story no, lon, lat) — 11 is in space, no Earth dot
    (1, 30.7, 36.9), (2, 30.3, 50.8), (3, 20.1, 32.1), (4, 24.0, 59.8),
    (5, 50.6, 26.2), (6, 33.4, 47.9), (7, 4.4, 50.8), (8, -74.0, 40.7),
    (9, -3.0, 53.4), (10, 106.3, -6.2), (12, -107.4, 24.8),
    (13, 21.0, 52.2), (14, -96.8, 32.8),
]
# Pixel nudges so the crowded Europe dots do not overlap; a thin
# leader line joins each nudged dot to its true position.
DOT_OFFSETS = {6: (18, -16), 13: (-16, 10), 9: (-12, -8), 7: (0, 8),
               4: (0, -10)}

# ---------------------------------------------------------------- scenes
def scene(draw, kind, x, y, w, h):
    """Flat editorial illustration inside box (x, y, w, h)."""
    if kind == "cop":
        draw.rectangle([x, y, x + w, y + h], fill=(38, 54, 78))
        scx, scy, sr = x + w * 0.77, y + h * 0.35, h * 0.27
        draw.ellipse([scx - sr, scy - sr, scx + sr, scy + sr],
                     fill=(214, 84, 44))
        gx0, gy0 = x + w * 0.10, y + h * 0.28
        gx1, gy1 = x + w * 0.40, y + h * 0.88
        draw.ellipse([gx0, gy0, gx1, gy1], fill=(168, 196, 214))
        for fy in (0.42, 0.58):
            draw.line([gx0 + 4, y + h * fy, gx1 - 4, y + h * fy],
                      fill=(120, 150, 175), width=2)
        draw.line([x + w * 0.25, gy0 + 4, x + w * 0.25, gy1 - 4],
                  fill=(120, 150, 175), width=2)
        draw.line([x + w * 0.16, y + h * 0.38, x + w * 0.24, y + h * 0.52,
                   x + w * 0.19, y + h * 0.64, x + w * 0.28, y + h * 0.78],
                  fill=RED, width=4)
        draw.rectangle([x, y + h * 0.88, x + w, y + h], fill=(24, 40, 58))
        for i in range(5):
            cx = x + w * (0.12 + i * 0.19)
            draw.rectangle([cx, y + h * 0.74, cx + 14, y + h * 0.88],
                           fill=(90, 104, 122))
    elif kind == "flats":
        draw.rectangle([x, y, x + w, y + h], fill=SKY)
        draw.rectangle([x + w * 0.08, y + h * 0.25, x + w * 0.55, y + h],
                       fill=(120, 116, 108))
        draw.rectangle([x + w * 0.55, y + h * 0.45, x + w * 0.92, y + h],
                       fill=(146, 140, 130))
        draw.polygon([(x + w * 0.55, y + h * 0.45), (x + w * 0.92, y + h * 0.45),
                      (x + w * 0.92, y + h * 0.72), (x + w * 0.74, y + h * 0.60)],
                     fill=(90, 86, 78))
        for r in range(3):
            for c in range(3):
                draw.rectangle([x + w * (0.14 + c * 0.12), y + h * (0.32 + r * 0.20),
                                x + w * (0.20 + c * 0.12), y + h * (0.44 + r * 0.20)],
                               fill=(250, 220, 130))
        draw.line([x + w * 0.60, y + h * 0.10, x + w * 0.70, y + h * 0.45],
                  fill=RED_LT, width=4)
        draw.ellipse([x + w * 0.78, y + h * 0.12, x + w * 0.94, y + h * 0.28],
                     fill=(250, 244, 230))
    elif kind == "warship":
        draw.rectangle([x, y, x + w, y + h], fill=SEA)
        draw.polygon([(x + w * 0.15, y + h * 0.55), (x + w * 0.85, y + h * 0.55),
                      (x + w * 0.78, y + h * 0.72), (x + w * 0.22, y + h * 0.72)],
                     fill=(70, 76, 84))
        draw.polygon([(x + w * 0.15, y + h * 0.55), (x + w * 0.55, y + h * 0.42),
                      (x + w * 0.85, y + h * 0.55)], fill=(52, 58, 66))
        draw.rectangle([x + w * 0.42, y + h * 0.28, x + w * 0.48, y + h * 0.45],
                       fill=(52, 58, 66))
        draw.ellipse([x + w * 0.60, y + h * 0.08, x + w * 0.78, y + h * 0.30],
                     fill=(214, 84, 44))
        draw.ellipse([x + w * 0.66, y + h * 0.18, x + w * 0.86, y + h * 0.42],
                     fill=(120, 116, 108))
        for i in range(3):
            draw.arc([x + w * (0.10 + i * 0.28), y + h * 0.78,
                      x + w * (0.30 + i * 0.28), y + h * 0.98],
                     180, 360, fill=(250, 244, 230), width=3)
    elif kind == "shipfire":
        draw.rectangle([x, y, x + w, y + h], fill=(46, 78, 104))
        draw.rectangle([x + w * 0.12, y + h * 0.55, x + w * 0.88, y + h * 0.72],
                       fill=(158, 24, 24))
        draw.rectangle([x + w * 0.20, y + h * 0.38, x + w * 0.80, y + h * 0.55],
                       fill=(120, 116, 108))
        for i, cx in enumerate((0.28, 0.45, 0.62, 0.76)):
            draw.rectangle([x + w * cx, y + h * 0.42, x + w * (cx + 0.08),
                            y + h * 0.52], fill=(250, 220, 130))
        draw.polygon([(x + w * 0.42, y + h * 0.38), (x + w * 0.50, y + h * 0.10),
                      (x + w * 0.58, y + h * 0.38)], fill=(240, 140, 40))
        draw.polygon([(x + w * 0.55, y + h * 0.38), (x + w * 0.63, y + h * 0.16),
                      (x + w * 0.70, y + h * 0.38)], fill=(214, 84, 44))
        draw.ellipse([x + w * 0.30, y + h * 0.02, x + w * 0.44, y + h * 0.18],
                     fill=(90, 96, 102))
        for i in range(3):
            draw.arc([x + w * (0.08 + i * 0.30), y + h * 0.80,
                      x + w * (0.28 + i * 0.30), y + h * 1.00],
                     180, 360, fill=(250, 244, 230), width=3)
    elif kind == "radar":
        draw.rectangle([x, y, x + w, y + h], fill=(58, 44, 40))
        draw.ellipse([x + w * 0.55, y + h * 0.15, x + w * 0.90, y + h * 0.55],
                     fill=(250, 244, 230))
        draw.rectangle([x + w * 0.62, y + h * 0.52, x + w * 0.83, y + h * 0.62],
                       fill=(120, 116, 108))
        draw.rectangle([x + w * 0.08, y + h * 0.55, x + w * 0.45, y + h],
                       fill=(90, 86, 78))
        draw.polygon([(x + w * 0.14, y + h * 0.55), (x + w * 0.22, y + h * 0.28),
                      (x + w * 0.30, y + h * 0.55)], fill=(240, 140, 40))
        draw.polygon([(x + w * 0.26, y + h * 0.55), (x + w * 0.34, y + h * 0.18),
                      (x + w * 0.42, y + h * 0.55)], fill=(214, 84, 44))
        draw.line([x + w * 0.10, y + h * 0.10, x + w * 0.45, y + h * 0.30],
                  fill=(250, 220, 130), width=3)
    elif kind == "strike":
        draw.rectangle([x, y, x + w, y + h], fill=(40, 40, 48))
        draw.rectangle([x + w * 0.10, y + h * 0.45, x + w * 0.50, y + h],
                       fill=(120, 116, 108))
        draw.rectangle([x + w * 0.50, y + h * 0.60, x + w * 0.90, y + h],
                       fill=(146, 140, 130))
        draw.line([x + w * 0.85, y + h * 0.05, x + w * 0.55, y + h * 0.45],
                  fill=(240, 140, 40), width=5)
        draw.ellipse([x + w * 0.48, y + h * 0.38, x + w * 0.62, y + h * 0.55],
                     fill=(214, 84, 44))
        draw.ellipse([x + w * 0.58, y + h * 0.30, x + w * 0.74, y + h * 0.48],
                     fill=(120, 116, 108))
        for r in range(2):
            for c in range(2):
                draw.rectangle([x + w * (0.16 + c * 0.14), y + h * (0.52 + r * 0.22),
                                x + w * (0.23 + c * 0.14), y + h * (0.64 + r * 0.22)],
                               fill=(250, 220, 130))
    elif kind == "trade":
        draw.rectangle([x, y, x + w, y + h], fill=(32, 64, 110))
        for i in range(12):
            import math
            a = math.radians(i * 30)
            cx = x + w * 0.30 + 26 * math.cos(a)
            cy = y + h * 0.50 + 26 * math.sin(a)
            draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(250, 220, 130))
        draw.rectangle([x + w * 0.58, y + h * 0.20, x + w * 0.92, y + h * 0.80],
                       fill=(250, 244, 230))
        draw.rectangle([x + w * 0.58, y + h * 0.20, x + w * 0.92, y + h * 0.50],
                       fill=(196, 52, 44))
        draw.line([x + w * 0.50, y + h * 0.50, x + w * 0.58, y + h * 0.50],
                  fill=(250, 244, 230), width=4)
    elif kind == "chart":
        draw.rectangle([x, y, x + w, y + h], fill=(250, 244, 230))
        for i in range(5):
            yy = y + h * (0.15 + i * 0.17)
            draw.line([x + w * 0.08, yy, x + w * 0.92, yy], fill=LINE, width=1)
        pts = [(0.08, 0.18), (0.22, 0.30), (0.36, 0.26), (0.50, 0.48),
               (0.64, 0.44), (0.78, 0.68), (0.92, 0.82)]
        for a, b in zip(pts, pts[1:]):
            draw.line([x + w * a[0], y + h * a[1], x + w * b[0], y + h * b[1]],
                      fill=RED, width=4)
        draw.polygon([(x + w * 0.86, y + h * 0.82), (x + w * 0.92, y + h * 0.82),
                      (x + w * 0.92, y + h * 0.74)], fill=RED)
        draw.text((x + 6, y + 4), "-3.7%", font=F_CARD_H, fill=RED)
    elif kind == "football":
        draw.rectangle([x, y, x + w, y + h], fill=(18, 96, 60))
        for i in range(6):
            draw.line([x, y + h * i / 5, x + w, y + h * i / 5],
                      fill=(24, 116, 74), width=2)
        draw.ellipse([x + w * 0.38, y + h * 0.30, x + w * 0.62, y + h * 0.70],
                     fill=(250, 244, 230))
        draw.polygon([(x + w * 0.46, y + h * 0.32), (x + w * 0.54, y + h * 0.32),
                      (x + w * 0.58, y + h * 0.44), (x + w * 0.50, y + h * 0.50),
                      (x + w * 0.42, y + h * 0.44)], fill=INK)
        draw.rectangle([x + w * 0.06, y + h * 0.08, x + w * 0.44, y + h * 0.26],
                       fill=INK)
        draw.text((x + w * 0.10, y + h * 0.10), "4 - 0", font=F_CARD_H,
                  fill=(250, 244, 230))
    elif kind == "factory":
        draw.rectangle([x, y, x + w, y + h], fill=(214, 200, 170))
        draw.rectangle([x + w * 0.10, y + h * 0.45, x + w * 0.70, y + h],
                       fill=(120, 116, 108))
        draw.rectangle([x + w * 0.72, y + h * 0.15, x + w * 0.84, y + h * 0.55],
                       fill=(90, 86, 78))
        draw.polygon([(x + w * 0.72, y + h * 0.15), (x + w * 0.78, y + h * 0.02),
                      (x + w * 0.84, y + h * 0.15)], fill=(90, 86, 78))
        draw.polygon([(x + w * 0.30, y + h * 0.45), (x + w * 0.38, y + h * 0.20),
                      (x + w * 0.46, y + h * 0.45)], fill=(240, 140, 40))
        draw.polygon([(x + w * 0.44, y + h * 0.45), (x + w * 0.52, y + h * 0.28),
                      (x + w * 0.60, y + h * 0.45)], fill=(214, 84, 44))
        draw.ellipse([x + w * 0.76, y + h * 0.02, x + w * 0.92, y + h * 0.18],
                     fill=(120, 116, 108))
    elif kind == "mercury":
        draw.rectangle([x, y, x + w, y + h], fill=(16, 18, 34))
        for px, py, r in ((0.15, 0.2, 2), (0.3, 0.1, 2), (0.8, 0.15, 2),
                          (0.9, 0.4, 3), (0.1, 0.6, 2), (0.65, 0.08, 2)):
            draw.ellipse([x + w * px - r, y + h * py - r,
                          x + w * px + r, y + h * py + r],
                         fill=(250, 244, 230))
        draw.ellipse([x + w * 0.25, y + h * 0.25, x + w * 0.75, y + h * 0.85],
                     fill=(168, 148, 128))
        for cx, cy, cr in ((0.42, 0.45, 8), (0.58, 0.60, 6), (0.50, 0.35, 5)):
            draw.ellipse([x + w * cx - cr, y + h * cy - cr,
                          x + w * cx + cr, y + h * cy + cr],
                         fill=(140, 122, 104))
        draw.polygon([(x + w * 0.78, y + h * 0.30), (x + w * 0.88, y + h * 0.34),
                      (x + w * 0.78, y + h * 0.40)], fill=(250, 220, 130))
        draw.rectangle([x + w * 0.70, y + h * 0.32, x + w * 0.78, y + h * 0.38],
                       fill=(120, 116, 108))
    elif kind == "badge":
        draw.rectangle([x, y, x + w, y + h], fill=(32, 64, 110))
        draw.ellipse([x + w * 0.28, y + h * 0.18, x + w * 0.72, y + h * 0.68],
                     fill=(250, 220, 130))
        draw.polygon([(x + w * 0.50, y + h * 0.24), (x + w * 0.56, y + h * 0.38),
                      (x + w * 0.70, y + h * 0.40), (x + w * 0.59, y + h * 0.49),
                      (x + w * 0.63, y + h * 0.63), (x + w * 0.50, y + h * 0.55),
                      (x + w * 0.37, y + h * 0.63), (x + w * 0.41, y + h * 0.49),
                      (x + w * 0.30, y + h * 0.40), (x + w * 0.44, y + h * 0.38)],
                     fill=(158, 24, 24))
        draw.rectangle([x + w * 0.30, y + h * 0.72, x + w * 0.70, y + h * 0.84],
                       fill=(250, 244, 230))
    elif kind == "shield":
        draw.rectangle([x, y, x + w, y + h], fill=(32, 64, 110))
        draw.polygon([(x + w * 0.50, y + h * 0.12), (x + w * 0.82, y + h * 0.22),
                      (x + w * 0.82, y + h * 0.55), (x + w * 0.50, y + h * 0.88),
                      (x + w * 0.18, y + h * 0.55), (x + w * 0.18, y + h * 0.22)],
                     fill=(250, 244, 230))
        draw.polygon([(x + w * 0.50, y + h * 0.22), (x + w * 0.74, y + h * 0.30),
                      (x + w * 0.74, y + h * 0.52), (x + w * 0.50, y + h * 0.78),
                      (x + w * 0.26, y + h * 0.52), (x + w * 0.26, y + h * 0.30)],
                     fill=BLUE)
        draw.text((x + w * 0.44, y + h * 0.36), "N", font=F_CARD_H, fill=(250, 244, 230))
    elif kind == "nfl":
        draw.rectangle([x, y, x + w, y + h], fill=(58, 44, 40))
        draw.ellipse([x + w * 0.15, y + h * 0.30, x + w * 0.85, y + h * 0.70],
                     fill=(120, 72, 32))
        draw.line([x + w * 0.30, y + h * 0.50, x + w * 0.70, y + h * 0.50],
                  fill=(250, 244, 230), width=3)
        for fx in (0.38, 0.46, 0.54, 0.62):
            draw.line([x + w * fx, y + h * 0.42, x + w * fx, y + h * 0.58],
                      fill=(250, 244, 230), width=2)
        draw.rectangle([x + w * 0.06, y + h * 0.08, x + w * 0.50, y + h * 0.26],
                       fill=INK)
        draw.text((x + w * 0.10, y + h * 0.10), "51 - 30", font=F_CARD_H,
                  fill=(250, 244, 230))

# ---------------------------------------------------------------- map
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 68), (-95, 69), (-85, 66),
     (-80, 73), (-75, 62), (-65, 60), (-55, 52), (-60, 47), (-70, 42),
     (-75, 35), (-80, 32), (-81, 26), (-84, 30), (-90, 21), (-97, 26),
     (-105, 20), (-95, 16), (-83, 9), (-79, 9), (-86, 13), (-92, 15),
     (-97, 16), (-105, 20), (-110, 23), (-114, 29), (-120, 34), (-124, 40),
     (-124, 48), (-130, 54), (-140, 60), (-155, 58), (-165, 60)],
    [(-79, 9), (-72, 12), (-64, 10), (-52, 5), (-50, 0), (-44, -3),
     (-35, -8), (-40, -20), (-48, -28), (-57, -38), (-65, -45), (-68, -52),
     (-70, -55), (-73, -50), (-73, -37), (-70, -18), (-75, -15), (-80, -6),
     (-81, 0), (-80, 7)],
    [(-10, 36), (-9, 43), (-2, 48), (-4, 50), (0, 53), (3, 58), (8, 57),
     (10, 59), (18, 56), (21, 55), (24, 59), (30, 60), (28, 55), (24, 50),
     (19, 46), (15, 44), (12, 44), (8, 44), (3, 42), (0, 40), (-2, 37),
     (-9, 37)],
    [(-6, 35), (10, 37), (20, 32), (32, 31), (34, 28), (37, 22), (40, 15),
     (43, 11), (48, 11), (51, 12), (44, 5), (41, -2), (40, -10), (36, -18),
     (33, -26), (28, -33), (20, -35), (17, -29), (14, -17), (12, -6),
     (9, 4), (4, 6), (-8, 5), (-13, 8), (-17, 15), (-17, 21), (-15, 27),
     (-10, 31)],
    [(30, 60), (40, 68), (55, 69), (70, 72), (90, 75), (110, 74), (130, 72),
     (150, 70), (170, 66), (178, 65), (170, 60), (162, 56), (158, 52),
     (142, 50), (140, 45), (135, 43), (130, 38), (127, 35), (122, 31),
     (120, 25), (110, 20), (108, 12), (105, 9), (100, 8), (97, 16),
     (92, 21), (89, 22), (86, 20), (80, 13), (77, 8), (73, 20), (66, 25),
     (61, 25), (57, 26), (52, 28), (50, 30), (48, 30), (44, 29), (40, 31),
     (36, 36), (30, 36), (27, 40), (24, 45), (22, 50), (25, 55)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (129, -32), (132, -32),
     (137, -35), (140, -38), (145, -38), (150, -37), (153, -32), (153, -27),
     (150, -23), (146, -19), (142, -15), (142, -11), (137, -12), (135, -15),
     (132, -12), (130, -13), (126, -14), (122, -17), (118, -20)],
]
ISLANDS = [(95, 5, 14, 6), (110, -2, 16, 6), (114, -4, 12, 5), (118, -2, 10, 5),
           (138, -4, 16, 6), (147, -6, 10, 5), (103, -8, 14, 4)]


def draw_map(draw, x, y, w, h):
    """Equirectangular world map, lon -180..180, lat -60..85."""
    def px(lon, lat):
        return (x + (lon + 180) / 360.0 * w, y + (85 - lat) / 145.0 * h)
    draw.rectangle([x, y, x + w, y + h], fill=(222, 234, 240))
    for poly in CONTINENTS:
        draw.polygon([px(lo, la) for lo, la in poly], fill=(196, 188, 168),
                     outline=(120, 112, 96))
    for lo, la, rw, rh in ISLANDS:
        cx, cy = px(lo, la)
        draw.ellipse([cx - rw, cy - rh, cx + rw, cy + rh],
                     fill=(196, 188, 168))
    # UK + Japan markers
    for lo, la in ((-2, 54), (139, 37)):
        cx, cy = px(lo, la)
        draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(196, 188, 168))
    labels = [("N. AMERICA", -100, 52), ("S. AMERICA", -58, -8),
              ("EUROPE", 15, 52), ("AFRICA", 18, 8), ("ASIA", 90, 50),
              ("AUSTRALIA", 134, -26)]
    for txt, lo, la in labels:
        cx, cy = px(lo, la)
        draw.text((cx - draw.textlength(txt, font=F_FOOT) / 2, cy - 5),
                  txt, font=F_FOOT, fill=(90, 84, 74))
    for n, lo, la in MAP_DOTS:
        cx, cy = px(lo, la)
        ox, oy = DOT_OFFSETS.get(n, (0, 0))
        if (ox, oy) != (0, 0):
            draw.line([cx, cy, cx + ox, cy + oy], fill=RED, width=1)
            cx, cy = cx + ox, cy + oy
        r = 10
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED,
                     outline=(250, 244, 230), width=2)
        t = str(n)
        tw = draw.textlength(t, font=F_NUM)
        draw.text((cx - tw / 2, cy - 6), t, font=F_NUM, fill=(255, 255, 255))
    return px


# ---------------------------------------------------------------- layout
def masthead(draw, sub=None):
    draw.text((W / 2 - draw.textlength("THE WORLD IN ONE DAY", font=F_MAST) / 2,
               10), "THE WORLD IN ONE DAY", font=F_MAST, fill=INK)
    draw.line([16, 66, W - 16, 66], fill=RED, width=3)
    t = "SUNDAY 22 NOVEMBER 2026"
    draw.text((W / 2 - draw.textlength(t, font=F_DATE) / 2, 72), t,
              font=F_DATE, fill=RED)
    if sub is None:
        sub = "38 STORIES  •  6 REGIONS  •  14 ILLUSTRATED  •  ALL TIMES UTC"
    draw.text((W / 2 - draw.textlength(sub, font=F_SUB) / 2, 108), sub,
              font=F_SUB, fill=GREY)


def footer(draw, y):
    draw.line([16, y, W - 16, y], fill=INK, width=2)
    t = ("DATE CHECK: EVERY STORY IS 22 NOV 2026 UNLESS MARKED SAT / FRI  •  "
         "SOURCES: REUTERS  •  AP  •  CNN  •  BBC  •  THE TIMES  •  WSJ  •  "
         "CHECKED MON 23 NOV 2026")
    draw.text((16, y + 6), t, font=F_FOOT, fill=GREY)


def lead_panel(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=2)
    scene(draw, LEAD["scene"], x + 2, y + 2, w - 4, 104)
    ty = y + 112
    draw.text((x + 10, ty), LEAD["kicker"], font=F_SUB_B, fill=RED)
    ty += 18
    for ln in fit(draw, LEAD["head"], F_LEAD_H, w - 20, 2):
        draw.text((x + 10, ty), ln, font=F_LEAD_H, fill=INK)
        ty += 40
    for ln in fit(draw, LEAD["sub"], F_LEAD_S, w - 20, 1):
        draw.text((x + 10, ty), ln, font=F_LEAD_S, fill=RED)
        ty += 24
    for ln in fit(draw, LEAD["body"], F_BODY2, w - 20, 3):
        draw.text((x + 10, ty), ln, font=F_BODY2, fill=INK)
        ty += 18


def card_top(draw, c, x, y, w, h, head_font=F_CARD_H, sub_font=F_CARD_S,
             scene_h=52, sub_lines=2, head_lines=2, head_step=22,
             sub_step=16, short_sub=False):
    """Illustrated card with picture band on top."""
    draw.rectangle([x, y, x + w, y + h], outline=LINE, width=1)
    scene(draw, c["scene"], x + 1, y + 1, w - 2, scene_h)
    ty = y + scene_h + 6
    draw.text((x + 8, ty), trunc(draw, c["kicker"], F_FOOT_B, w - 16),
              font=F_FOOT_B, fill=RED)
    ty += 15
    head = c.get("head2") if w < 260 and "head2" in c else c["head"]
    for ln in fit(draw, f"{c['n']}. {head}", head_font, w - 16, head_lines):
        draw.text((x + 8, ty), ln, font=head_font, fill=INK)
        ty += head_step
    sub = c.get("sub2", c["sub"]) if short_sub else c["sub"]
    for ln in fit(draw, sub, sub_font, w - 16, sub_lines):
        draw.text((x + 8, ty), ln, font=sub_font, fill=INK)
        ty += sub_step


def card_side(draw, c, x, y, w, h):
    """Illustrated card with thumbnail at left, text at right."""
    draw.rectangle([x, y, x + w, y + h], outline=LINE, width=1)
    scene(draw, c["scene"], x + 1, y + 1, 96, h - 2)
    tx = x + 104
    ty = y + 5
    draw.text((tx, ty), trunc(draw, c["kicker"], F_FOOT_B, w - 112),
              font=F_FOOT_B, fill=RED)
    ty += 14
    head = c.get("head2", c["head"])
    for ln in fit(draw, f"{c['n']}. {head}", F_CARD_H2, w - 112, 2):
        draw.text((tx, ty), ln, font=F_CARD_H2, fill=INK)
        ty += 21
    for ln in fit(draw, c.get("sub2", c["sub"]), F_CARD_S2, w - 112, 2):
        draw.text((tx, ty), ln, font=F_CARD_S2, fill=INK)
        ty += 15


def shorts_block(draw, items, x, y, cols, rows, col_w, row_h):
    for i, (n, txt) in enumerate(items):
        cx = x + (i // rows) * col_w
        cy = y + (i % rows) * row_h
        draw.text((cx, cy), f"{n}.", font=F_SHORT_B, fill=RED)
        nw = draw.textlength(f"{n}. ", font=F_SHORT_B)
        draw.text((cx + nw, cy), trunc(draw, txt, F_SHORT, col_w - nw - 4),
                  font=F_SHORT, fill=INK)


def build(variant):
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    if variant == "A":
        masthead(draw)
        # Lead (left) + cards 2-5 (2x2, top picture) on the right.
        lead_panel(draw, 16, 126, 330, 296)
        cw, ch = 321, 143
        for i, c in enumerate(CARDS[:4]):
            cx = 356 + (i % 2) * (cw + 10)
            cy = 126 + (i // 2) * (ch + 10)
            card_top(draw, c, cx, cy, cw, ch)
        # Cards 6-14: 3 cols x 3 rows, side thumbnails.
        cw, ch = 322, 90
        for i, c in enumerate(CARDS[4:]):
            cx = 16 + (i % 3) * (cw + 10)
            cy = 432 + (i // 3) * (ch + 8)
            card_side(draw, c, cx, cy, cw, ch)
        # Map strip.
        draw.text((16, 720), "WHERE IT HAPPENED  —  NUMBERED TO THE STORIES",
                  font=F_MAP_T, fill=INK)
        draw_map(draw, 16, 740, 992, 112)
        # Short stories 15-38: 3 cols x 8 rows, wide enough to avoid cuts.
        shorts_block(draw, SHORTS, 16, 864, 3, 8, 330, 15)
        footer(draw, 990)
    else:
        # Variant B: visual-led. Wide lead, then 10 big cards, 20 shorts.
        masthead(draw, "31 STORIES  •  6 REGIONS  •  11 ILLUSTRATED  •  "
                        "ALL TIMES UTC")
        draw.rectangle([16, 126, 1008, 376], outline=INK, width=2)
        scene(draw, LEAD["scene"], 18, 128, 400, 246)
        tx = 432
        draw.text((tx, 140), LEAD["kicker"], font=F_SUB_B, fill=RED)
        ty = 164
        for ln in fit(draw, LEAD["head"], F_LEAD_H, 560, 1):
            draw.text((tx, ty), ln, font=F_LEAD_H, fill=INK)
            ty += 44
        for ln in fit(draw, LEAD["sub"], F_LEAD_S, 560, 1):
            draw.text((tx, ty), ln, font=F_LEAD_S, fill=RED)
            ty += 28
        for ln in fit(draw, LEAD["body"], F_BODY, 560, 5):
            draw.text((tx, ty), ln, font=F_BODY, fill=INK)
            ty += 20
        cw, ch = 190, 162
        for i, c in enumerate(CARDS[:10]):
            cx = 16 + (i % 5) * (cw + 10)
            cy = 384 + (i // 5) * (ch + 8)
            card_top(draw, c, cx, cy, cw, ch, head_font=F_CARD_H4,
                     sub_font=F_CARD_S2, scene_h=44, sub_lines=2,
                     head_lines=3, head_step=19, sub_step=15,
                     short_sub=True)
        draw.text((16, 722), "WHERE IT HAPPENED  —  NUMBERED TO THE STORIES",
                  font=F_MAP_T, fill=INK)
        draw_map(draw, 16, 740, 992, 112)
        shorts_block(draw, SHORTS[:20], 16, 864, 3, 7, 330, 16)
        footer(draw, 990)
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", choices=["A", "B"], default="A")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    img = build(args.variant)
    img.save(args.out, format="PNG", optimize=True)
    data = open(args.out, "rb").read()
    print(args.out, len(data), "bytes",
          hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()
