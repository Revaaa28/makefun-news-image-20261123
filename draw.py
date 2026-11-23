#!/usr/bin/env python3
"""THE MONDAY LEDGER — renderer for make.fun news-image-20261123.

Draws one page summing up Monday 23 November 2026's world news, following the
broadsheet grammar dissected from the ni22 winner (jolly-stork-27): count-claim
band, date masthead, strapline, six-stat strip, region bar, UTC timeline, three
illustrated heroes, twelve pictured cards, dotted world map with numbered pins,
numbered ALSO list, DATE CHECK box, sources + certainty legend, ledger close.

The page is drawn at 2048x2048 and downscaled to 1024x1024 with Lanczos
(2x supersampling) so small type stays clean. All story data below was gathered
from the named wires on 23 Nov 2026; see news-notes.md for the source trail.
"""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = 2                      # supersampling factor
W = 1024 * S               # canvas, final-px units are multiplied by S
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

FONT_DIR = "/usr/share/fonts/truetype/noto"
DEJA_DIR = "/usr/share/fonts/truetype/dejavu"


def font(path, size):
    return ImageFont.truetype(path, int(size * S))


def F_DISPLAY(size):
    return font(f"{FONT_DIR}/NotoSerifDisplay-Black.ttf", size)


def F_SERIF(size, bold=False, italic=False):
    if bold and italic:
        name = "NotoSerif-BoldItalic.ttf"
    elif bold:
        name = "NotoSerif-Bold.ttf"
    elif italic:
        name = "NotoSerif-Italic.ttf"
    else:
        name = "NotoSerif-Regular.ttf"
    return font(f"{FONT_DIR}/{name}", size)


def F_SANS(size, bold=False):
    name = "NotoSans-Bold.ttf" if bold else "NotoSans-Regular.ttf"
    return font(f"{FONT_DIR}/{name}", size)


def F_MONO(size, bold=False):
    name = "DejaVuSansMono-Bold.ttf" if bold else "DejaVuSansMono.ttf"
    return font(f"{DEJA_DIR}/{name}", size)


# ---------------------------------------------------------------- palette
PAPER = (247, 242, 231)
PAPER_DARK = (238, 231, 214)
INK = (22, 22, 20)
GREEN = (16, 84, 52)          # ledger green (our identity accent)
GREEN_DARK = (10, 58, 36)
GREEN_PALE = (214, 230, 218)
RED = (178, 34, 40)
RED_DARK = (140, 24, 30)
GOLD = (196, 148, 44)
GREY = (96, 94, 88)
HAIRLINE = (178, 170, 152)

REGION_COLORS = {
    "EUROPE": (58, 92, 140),
    "MIDDLE EAST": (178, 120, 40),
    "AMERICAS": (140, 52, 52),
    "ASIA-PACIFIC": (16, 84, 52),
    "AFRICA": (120, 84, 160),
    "OCEANIA": (44, 128, 140),
    "WORLD": (70, 70, 70),
}

# ---------------------------------------------------------------- data
# status: REPORTED / CLAIM / FORECAST — used honestly per story.
HEROES = [
    {
        "n": 1, "region": "EUROPE", "scene": "kyiv",
        "label": "APARTMENT BLOCK HIT", "chip": "9 DEAD · 11 STILL SOUGHT",
        "kicker": "DYMER, KYIV REGION, UKRAINE · WAR", "status": "REPORTED",
        "headline": "Drone strike flattens a Kyiv-region apartment block",
        "summary": (
            "A Russian drone tore through a five-storey block in Dymer, "
            "north of Kyiv, early on Sunday. On Monday the town's toll rose "
            "to nine dead, with 11 people \u2014 two of them children \u2014 still "
            "unaccounted for, and a second strike at a Vyshneve supermarket "
            "took the region's dead to 12. A boy was pulled alive from the "
            "rubble on Sunday evening."
        ),
        "source": "Kyiv region officials via AFP · AP",
        "pin": (31.0, 50.6),
    },
    {
        "n": 2, "region": "WORLD", "scene": "cop31",
        "label": "NO PACT IN ANTALYA", "chip": "194 DELEGATIONS",
        "kicker": "ANTALYA, TÜRKIYE · CLIMATE SUMMIT", "status": "REPORTED",
        "headline": "The longest climate summit ends with no pact at all",
        "summary": (
            "COP31 closed after two weeks and two days of overtime with no "
            "overarching decision, after countries rejected the Antalya Pact "
            "for dropping any mention of fossil fuels. On Monday the UN chief "
            "said there was \u201cno ambiguity in the science\u201d, and Australia's "
            "PM called the failure a sign of difficult geopolitical times."
        ),
        "source": "UN News · AFP · Le Monde",
        "pin": (30.7, 36.9),
    },
    {
        "n": 3, "region": "ASIA-PACIFIC", "scene": "markets",
        "label": "MARKETS IN FREEFALL", "chip": "KOSPI -4%",
        "kicker": "SEOUL · SHANGHAI · SYDNEY · MARKETS", "status": "REPORTED",
        "headline": "Asia's AI rout deepens; Seoul readies a rescue fund",
        "summary": (
            "Asian shares slid again on Monday as the AI sell-off spread from "
            "Wall Street's worst week in six years: Seoul's Kospi fell about "
            "4%, Shanghai dipped below 3,500 and emerging markets headed for "
            "an eighth straight fall. Seoul readied its first stabilisation "
            "fund since 2008; gold jumped to $3,603 an ounce."
        ),
        "source": "Yonhap · CNBC TV18 · market wires",
        "pin": (127.0, 37.5),
    },
]

# scene, chip, region, place/kicker, headline, summary, source, status, pin(lon,lat)
CARDS = [
    (4, "hormuz", "14 TANKERS", "MIDDLE EAST", "STRAIT OF HORMUZ · SHIPPING",
     "Iran threatens to run the Hormuz blockade",
     "Three tankers struck; traffic 65% below pre-war levels.",
     "UKMTO via AP", "REPORTED", (56.3, 26.6)),
    (5, "benghazi", "CORVETTE CAPSIZED", "AFRICA", "BENGHAZI, LIBYA · NAVAL WAR",
     "Sea drones cripple a Russian corvette",
     "Suspected Ukrainian drones; she capsized, 10 hurt.",
     "AP · Reuters · BBC Verify", "REPORTED", (20.1, 32.1)),
    (6, "fire", "24 BODY BAGS", "ASIA-PACIFIC", "CIKANDE, BANTEN · DISASTER",
     "Factory fire: 24 body bags recovered",
     "Search for dozens of missing workers went on Monday.",
     "Indonesian rescuers via wires", "REPORTED", (106.4, -6.3)),
    (7, "house", "258 SEATS", "AMERICAS", "WASHINGTON, USA · POLITICS",
     "Democrats reach 258 House seats",
     "Recount confirms a 330-vote win in North Carolina.",
     "AP via CBS News", "REPORTED", (-79.0, 35.8)),
    (8, "westbank", "12 VEHICLES TORCHED", "MIDDLE EAST", "RAMALLAH, WEST BANK",
     "Settlers torch 12 Palestinian vehicles",
     "Cars burned in four villages; ex-minister condemns.",
     "Reuters", "REPORTED", (35.2, 31.9)),
    (9, "khartoum", "UN BUILDING HIT", "AFRICA", "KHARTOUM, SUDAN · WAR",
     "Drone strikes hit Khartoum and a UN site",
     "A UN facility was damaged; three killed in Omdurman.",
     "AFP", "REPORTED", (32.5, 15.6)),
    (10, "southsudan", "24 CIVILIANS DEAD", "AFRICA", "SOUTH SUDAN · VIOLENCE",
     "24 civilians killed in fresh violence",
     "SPLA-IO attack deals a new blow to the peace deal.",
     "AFP, Juba", "REPORTED", (30.2, 7.2)),
    (11, "tennis", "FIRST ATP FINALS TITLE", "EUROPE", "TURIN, ITALY · TENNIS",
     "Alcaraz wins his first ATP Finals crown",
     "Beat Zverev in Turin for the season-ending title.",
     "ATP via the wires", "REPORTED", (7.7, 45.1)),
    (12, "football", "TEN-MAN UNITED BEATEN", "EUROPE", "ANFIELD, ENGLAND · FOOTBALL",
     "Liverpool beat ten-man Man United",
     "Ten-man United beaten in Sunday's league fixture.",
     "BBC Sport", "REPORTED", (-3.0, 53.4)),
    (13, "fifa", "DECISION DUE MONDAY", "EUROPE", "ZURICH · WOMEN'S WORLD CUP",
     "UK set to land the 2035 World Cup",
     "Confirmation due Monday — a UK first since 1966.",
     "FIFA via the wires", "FORECAST", (8.5, 47.4)),
    (14, "castle", "SEVEN YEARS ON", "ASIA-PACIFIC", "OKINAWA, JAPAN · HERITAGE",
     "Shuri Castle's hall reopens at last",
     "Restored hall opens Monday, 7 years after the fire.",
     "Okinawa officials via wires", "REPORTED", (127.8, 26.2)),
    (15, "smog", "AQI 538", "ASIA-PACIFIC", "LAHORE, PAKISTAN · AIR",
     "Lahore again the world's smoggiest city",
     "AQI hit 538 — hazardous air over the second city.",
     "IQAir via Dawn", "REPORTED", (74.3, 31.6)),
]

ALSO = [
    (16, "EUROPE", "Poland: Russia plotted to kill rapper", "wires"),
    (17, "EUROPE", "Thousands march in Lisbon on costs", "wires"),
    (18, "EUROPE", "EU debates a technology tax", "wires"),
    (19, "MIDDLE EAST", "Saudi coalition downs Houthi missile", "AFP"),
    (20, "MIDDLE EAST", "Netanyahu–Eisenkot talks fail", "AFP"),
    (21, "AMERICAS", "Bolsonaro 'stable' in intensive care", "AFP"),
    (22, "AMERICAS", "Army to burn bomb chemicals in Iowa", "wires"),
    (23, "AMERICAS", "Trump reposts TrumpCare pitch", "WaPo"),
    (24, "AMERICAS", "Intel chief: Putin 'not our friend'", "Reuters"),
    (25, "ASIA-PACIFIC", "Kim: N. Korea seeks security", "AFP"),
    (26, "ASIA-PACIFIC", "Myanmar junta objects to ASEAN", "wires"),
    (27, "ASIA-PACIFIC", "Modi to meet Nepal PM in Delhi", "ANI"),
    (28, "ASIA-PACIFIC", "India, China hold border talks", "wires"),
    (29, "AFRICA", "35 Fulani killed in Nigeria attacks", "AFP"),
    (30, "AFRICA", "WHO pleads for calm in Ebola Congo", "AFP"),
    (31, "OCEANIA", "Albanese: COP31 'difficult times'", "AFP"),
    (32, "OCEANIA", "ASX erases losses; gold miners up", "AAP"),
    (33, "ASIA-PACIFIC", "Samsung Securities data-leak hack", "Yonhap"),
    (34, "ASIA-PACIFIC", "Nghi Son refinery crude set to Jan", "wires"),
    (35, "AMERICAS", "Thitikul: third straight LPGA title", "wires"),
    (36, "EUROPE", "Price ends wait for a darts major", "wires"),
]

STATS = [
    ("258", "HOUSE SEATS FOR THE\nDEMOCRATS — MOST SINCE 1992"),
    ("$3,603", "SPOT GOLD, AN OUNCE —\nUP NEARLY 2% MONDAY"),
    ("-4%", "SEOUL'S KOSPI AT ITS\nMONDAY LOW"),
    ("\u00a5499.5bn", "CASH INJECTED BY CHINA'S\nCENTRAL BANK MONDAY"),
    ("24", "BODY BAGS RECOVERED AT\nTHE BANTEN FACTORY"),
    ("194", "DELEGATIONS AT COP31 —\nAND STILL NO PACT"),
]

TIMELINE = [
    ("00:00", "JUBA — AFP: 24 CIVILIANS DEAD IN SOUTH SUDAN"),
    ("01:00", "SEOUL — KIM: SECURITY, NOT SUPREMACY"),
    ("01:39", "SHANGHAI — TECH INDEX DOWN 3% AS ROUT DEEPENS"),
    ("01:49", "SEOUL — GULF UNIT MOVE 'NOT IRAN INVOLVEMENT'"),
    ("01:56", "MARKETS — GOLD EXTENDS GAINS TOWARD $3,603"),
    ("02:00", "SYDNEY — PM: COP31 FAILURE 'DIFFICULT TIMES'"),
]

DATE_CHECK = (
    "Left out as other days' news: BepiColombo's arrival in Mercury orbit "
    "(Sat 21 Nov) \u00b7 the Gaza aid-vehicle strike (Sat 21 Nov) \u00b7 Verstappen's "
    "Las Vegas Grand Prix win (Sat night) \u00b7 Wall Street's Friday crash "
    "(20 Nov) \u2014 the rout Asia inherited, not Monday's news. What is printed "
    "above is Monday's: first reported on 23 November 2026, or Monday's "
    "development in a running story."
)

SOURCES_LINE = (
    "Sources: Reuters, AP, AFP, BBC, Al Jazeera, UN News, Yonhap, ANI, Dawn, "
    "CBS News, Le Monde and the wires named with each story. "
    "Pictures and map: original, drawn in code."
)
LEGEND = (
    "HOW TO READ THE TAGS \u2014 REPORTED = carried by Monday's wires \u00b7 "
    "CLAIM = one side's account, labelled as such \u00b7 FORECAST = still to "
    "happen when this page was drawn."
)


# ---------------------------------------------------------------- helpers
FIT_ERRORS = []


def u(v):
    """final-px units -> canvas units"""
    return v * S


def vgrad(size, top, bottom):
    """vertical gradient image of (w,h) in canvas units"""
    w, h = size
    grad = Image.new("RGB", (1, h))
    for i in range(h):
        t = i / max(1, h - 1)
        grad.putpixel((0, i), tuple(
            int(top[c] + (bottom[c] - top[c]) * t) for c in range(3)))
    return grad.resize((w, h))


def glow(base, cx, cy, radius, color, peak=110):
    """radial glow composited onto base (canvas coords)"""
    r = int(radius)
    layer = Image.new("L", (r * 2, r * 2), 0)
    d = ImageDraw.Draw(layer)
    for i in range(r, 0, -2):
        a = int(peak * (1 - i / r) ** 1.6)
        d.ellipse([r - i, r - i, r + i, r + i], fill=a)
    tint = Image.new("RGB", (r * 2, r * 2), color)
    base.paste(tint, (int(cx - r), int(cy - r)), layer)


def text_w(draw, s, fnt):
    return draw.textlength(s, font=fnt)


def wrap(draw, s, fnt, max_w):
    """word-wrap s to lines of at most max_w canvas units; returns lines"""
    words = s.split()
    lines, cur = [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if text_w(draw, trial, fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def block(draw, xy, s, fnt, fill, max_w, lh, max_lines=None, tag=""):
    """draw wrapped text; record a fit error if it exceeds max_lines"""
    x, y = xy
    lines = wrap(draw, s, fnt, max_w)
    if max_lines is not None and len(lines) > max_lines:
        FIT_ERRORS.append(f"{tag}: needs {len(lines)} lines, slot has {max_lines}")
    for i, ln in enumerate(lines):
        draw.text((x, y + i * lh), ln, font=fnt, fill=fill)
    return y + len(lines) * lh


def chip(draw, xy, s, fnt, bg, fg, pad_x=5, pad_y=2):
    x, y = xy
    w_ = text_w(draw, s, fnt) + u(pad_x) * 2
    h_ = fnt.size + u(pad_y) * 2
    draw.rectangle([x, y, x + w_, y + h_], fill=bg)
    draw.text((x + u(pad_x), y + u(pad_y) - S), s, font=fnt, fill=fg)
    return w_


def spaced(draw, xy, s, fnt, fill, tracking=2):
    """letterspaced uppercase text; returns width used"""
    x, y = xy
    total = 0
    for ch in s:
        draw.text((x + total, y), ch, font=fnt, fill=fill)
        total += text_w(draw, ch, fnt) + u(tracking)
    return total - u(tracking)


def spaced_w(draw, s, fnt, tracking=2):
    return sum(text_w(draw, ch, fnt) for ch in s) + u(tracking) * (len(s) - 1)


# ---------------------------------------------------------------- scenes
# Each painter draws into box (x0,y0,x1,y1) canvas units on img, clipped by caller.
def scene_base(img, box, top, bottom):
    x0, y0, x1, y1 = box
    tile = vgrad((int(x1 - x0), int(y1 - y0)), top, bottom)
    img.paste(tile, (int(x0), int(y0)))
    return ImageDraw.Draw(img, "RGBA")


def sc_kyiv(img, box):
    x0, y0, x1, y1 = box
    d = scene_base(img, box, (26, 34, 66), (96, 84, 84))
    w_, h_ = x1 - x0, y1 - y0
    glow(img, x0 + w_ * 0.70, y0 + h_ * 0.78, w_ * 0.30, (255, 122, 40), 130)
    d = ImageDraw.Draw(img, "RGBA")
    # moon
    d.ellipse([x0 + w_ * 0.06, y0 + h_ * 0.08, x0 + w_ * 0.13, y0 + h_ * 0.30],
              fill=(238, 236, 214, 255))
    # intact block
    bx, bw = x0 + w_ * 0.10, w_ * 0.30
    d.rectangle([bx, y0 + h_ * 0.30, bx + bw, y1], fill=(38, 38, 48, 255))
    for r in range(4):
        for c in range(4):
            wx = bx + u(4) + c * (bw - u(8)) / 4
            wy = y0 + h_ * 0.36 + r * h_ * 0.15
            lit = (r * 4 + c) % 3 != 0
            d.rectangle([wx, wy, wx + (bw - u(8)) / 4 - u(3), wy + h_ * 0.09],
                        fill=(255, 196, 92, 255) if lit else (70, 72, 86, 255))
    # collapsed block: leaning slab + rubble
    cx = x0 + w_ * 0.52
    d.polygon([(cx, y0 + h_ * 0.34), (cx + w_ * 0.30, y0 + h_ * 0.52),
               (cx + w_ * 0.30, y1), (cx, y1)], fill=(52, 48, 52, 255))
    for r in range(3):  # broken window rows still visible on the slab
        for c in range(3):
            wx = cx + w_ * 0.05 + c * w_ * 0.085
            wy = y0 + h_ * (0.44 + r * 0.13) + c * h_ * 0.028
            d.rectangle([wx, wy, wx + w_ * 0.05, wy + h_ * 0.07],
                        fill=(16, 16, 20, 255))
    rng = random.Random(11)
    for _ in range(46):
        rx = cx + rng.uniform(0, w_ * 0.42)
        ry = y0 + h_ * rng.uniform(0.72, 0.97)
        rs = rng.uniform(u(1.5), u(4.5))
        d.rectangle([rx, ry, rx + rs, ry + rs * 0.7],
                    fill=(rng.randint(70, 120),) * 3 + (255,))
    # crane arm + searchlight beams
    d.line([x0 + w_ * 0.86, y1, x0 + w_ * 0.60, y0 + h_ * 0.20],
           fill=(220, 200, 120, 255), width=int(u(2)))
    d.line([x0 + w_ * 0.60, y0 + h_ * 0.20, x0 + w_ * 0.60, y0 + h_ * 0.44],
           fill=(220, 200, 120, 200), width=int(u(1.2)))
    d.polygon([(x0 + w_ * 0.60, y0 + h_ * 0.44), (x0 + w_ * 0.46, y1),
               (x0 + w_ * 0.74, y1)], fill=(255, 240, 180, 46))
    # smoke
    for i in range(5):
        sx = cx + w_ * 0.16 + i * u(3)
        sy = y0 + h_ * (0.30 - i * 0.045)
        d.ellipse([sx, sy, sx + u(16 - i), sy + u(9 - i)],
                  fill=(150, 148, 150, 60))


def sc_cop31(img, box):
    x0, y0, x1, y1 = box
    d = scene_base(img, box, (250, 176, 96), (120, 60, 60))
    w_, h_ = x1 - x0, y1 - y0
    glow(img, x0 + w_ * 0.5, y0 + h_ * 0.42, w_ * 0.42, (255, 214, 130), 120)
    d = ImageDraw.Draw(img, "RGBA")
    # sun disc, high left, clearing the dome
    d.ellipse([x0 + w_ * 0.10, y0 + h_ * 0.08, x0 + w_ * 0.20, y0 + h_ * 0.34],
              fill=(255, 226, 150, 255))
    # sea band
    d.rectangle([x0, y0 + h_ * 0.66, x1, y1], fill=(64, 96, 116, 255))
    for i in range(7):
        yy = y0 + h_ * (0.70 + i * 0.04)
        d.line([x0 + w_ * (0.05 + 0.07 * (i % 3)), yy,
                x0 + w_ * (0.30 + 0.07 * (i % 3)), yy],
               fill=(170, 205, 220, 160), width=int(u(1)))
    # conference dome + skyline (Antalya): wide flat dome, two minaret towers
    d.rectangle([x0 + w_ * 0.08, y0 + h_ * 0.52, x0 + w_ * 0.92, y0 + h_ * 0.66],
                fill=(44, 44, 52, 255))
    d.pieslice([x0 + w_ * 0.30, y0 + h_ * 0.24, x0 + w_ * 0.70, y0 + h_ * 0.80],
               180, 360, fill=(52, 52, 62, 255))
    for tx in (0.16, 0.80):
        d.rectangle([x0 + w_ * tx, y0 + h_ * 0.22, x0 + w_ * (tx + 0.025),
                     y0 + h_ * 0.52], fill=(44, 44, 52, 255))
        d.polygon([(x0 + w_ * (tx - 0.008), y0 + h_ * 0.22),
                   (x0 + w_ * (tx + 0.033), y0 + h_ * 0.22),
                   (x0 + w_ * (tx + 0.0125), y0 + h_ * 0.12)],
                  fill=(44, 44, 52, 255))
    # empty chairs row (the missing consensus)
    for i in range(6):
        cx = x0 + w_ * (0.16 + i * 0.115)
        cy = y0 + h_ * 0.80
        d.rectangle([cx, cy, cx + w_ * 0.07, cy + h_ * 0.05], fill=(240, 234, 220, 230))
        d.rectangle([cx, cy + h_ * 0.05, cx + u(2), cy + h_ * 0.16], fill=(240, 234, 220, 230))
    # heat shimmer columns
    for i in range(4):
        sx = x0 + w_ * (0.2 + i * 0.18)
        d.line([sx, y0 + h_ * 0.60, sx + u(2), y0 + h_ * 0.34],
               fill=(255, 240, 210, 90), width=int(u(2.4)))


def sc_markets(img, box):
    x0, y0, x1, y1 = box
    d = scene_base(img, box, (16, 22, 34), (30, 16, 22))
    w_, h_ = x1 - x0, y1 - y0
    # grid
    for i in range(1, 6):
        yy = y0 + h_ * i / 6
        d.line([x0, yy, x1, yy], fill=(70, 84, 104, 120), width=S)
    for i in range(1, 8):
        xx = x0 + w_ * i / 8
        d.line([xx, y0, xx, y1], fill=(70, 84, 104, 90), width=S)
    # falling candles
    rng = random.Random(7)
    level = 0.22
    for i in range(9):
        cx = x0 + w_ * (0.05 + i * 0.095)
        cw = w_ * 0.05
        drop = rng.uniform(0.02, 0.075)
        top = y0 + h_ * level
        bot = y0 + h_ * (level + drop + rng.uniform(0.03, 0.09))
        col = (224, 64, 60, 255) if i != 8 else (70, 200, 120, 255)
        if i == 8:  # one green candle: the gold-driven bounce at the end
            top = y0 + h_ * (level - 0.055)
            bot = y0 + h_ * level
        d.rectangle([cx, top, cx + cw, bot], fill=col)
        d.line([cx + cw / 2, top - h_ * 0.03, cx + cw / 2, bot + h_ * 0.03],
               fill=col, width=int(u(1.4)))
        level += drop
    # trend arrow down
    d.line([x0 + w_ * 0.06, y0 + h_ * 0.16, x0 + w_ * 0.80, y0 + h_ * 0.78],
           fill=(255, 92, 84, 255), width=int(u(2.6)))
    d.polygon([(x0 + w_ * 0.80, y0 + h_ * 0.78), (x0 + w_ * 0.72, y0 + h_ * 0.76),
               (x0 + w_ * 0.785, y0 + h_ * 0.685)], fill=(255, 92, 84, 255))
    # gold glow rising at right
    glow(img, x0 + w_ * 0.90, y0 + h_ * 0.30, w_ * 0.16, (255, 196, 64), 150)
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([x0 + w_ * 0.855, y0 + h_ * 0.20, x0 + w_ * 0.945, y0 + h_ * 0.40],
              fill=(255, 205, 84, 255), outline=(170, 120, 30, 255), width=int(u(1.4)))
    d.text((x0 + w_ * 0.885, y0 + h_ * 0.245), "$", font=F_SANS(13, bold=True),
           fill=(90, 60, 8, 255))


SCENE_HERO = {"kyiv": sc_kyiv, "cop31": sc_cop31, "markets": sc_markets}


CARD_SCENE_STYLE = {
    # scene: (sky top, sky bottom, ground)
    "hormuz": ((52, 84, 120), (150, 178, 200), (40, 70, 105)),
    "benghazi": ((40, 52, 84), (110, 110, 128), (44, 60, 92)),
    "fire": ((70, 40, 40), (170, 90, 50), (40, 30, 30)),
    "house": ((70, 96, 140), (168, 188, 214), (88, 92, 100)),
    "westbank": ((46, 44, 60), (130, 110, 100), (52, 46, 44)),
    "khartoum": ((120, 84, 60), (206, 164, 110), (96, 74, 54)),
    "southsudan": ((96, 110, 70), (188, 196, 140), (80, 88, 58)),
    "tennis": ((60, 110, 80), (140, 190, 130), (44, 110, 66)),
    "football": ((52, 96, 60), (130, 180, 120), (40, 116, 58)),
    "fifa": ((70, 80, 140), (160, 160, 200), (90, 84, 120)),
    "castle": ((90, 120, 170), (200, 210, 225), (110, 120, 130)),
    "smog": ((110, 104, 92), (178, 168, 148), (92, 86, 76)),
}


def card_scene(img, box, scene):
    x0, y0, x1, y1 = box
    top, mid, ground = CARD_SCENE_STYLE[scene]
    d = scene_base(img, box, top, mid)
    w_, h_ = x1 - x0, y1 - y0
    gy = y0 + h_ * 0.72
    d.rectangle([x0, gy, x1, y1], fill=ground + (255,))
    cx, cy = x0 + w_ * 0.5, y0 + h_ * 0.44

    def ship(cx_, cy_, s_, col=(30, 30, 36, 255)):
        d.polygon([(cx_ - 26 * s_, cy_ + 8 * s_), (cx_ + 26 * s_, cy_ + 8 * s_),
                   (cx_ + 18 * s_, cy_ + 16 * s_), (cx_ - 18 * s_, cy_ + 16 * s_)],
                  fill=col)
        d.rectangle([cx_ - 12 * s_, cy_, cx_ + 8 * s_, cy_ + 8 * s_], fill=col)
        d.rectangle([cx_ + 12 * s_, cy_ - 8 * s_, cx_ + 17 * s_, cy_ + 8 * s_], fill=col)

    def drone(cx_, cy_, s_):
        d.ellipse([cx_ - 5 * s_, cy_ - 3 * s_, cx_ + 5 * s_, cy_ + 3 * s_],
                  fill=(24, 24, 28, 255))
        for dx, dy in ((-14, -7), (14, -7), (-14, 7), (14, 7)):
            d.ellipse([cx_ + (dx - 5) * s_, cy_ + (dy - 2) * s_,
                       cx_ + (dx + 5) * s_, cy_ + (dy + 2) * s_],
                      outline=(24, 24, 28, 255), width=int(u(1.2)))

    def flame(cx_, cy_, s_, col=(255, 130, 40, 255)):
        d.polygon([(cx_ - 10 * s_, cy_ + 14 * s_), (cx_ - 3 * s_, cy_ - 2 * s_),
                   (cx_, cy_ - 16 * s_), (cx_ + 4 * s_, cy_ - 3 * s_),
                   (cx_ + 10 * s_, cy_ + 14 * s_)], fill=col)
        d.polygon([(cx_ - 5 * s_, cy_ + 14 * s_), (cx_, cy_ - 4 * s_),
                   (cx_ + 5 * s_, cy_ + 14 * s_)], fill=(255, 196, 80, 255))

    def waves(y_, col=(220, 235, 245, 200)):
        for i in range(3):
            xx = x0 + w_ * (0.08 + i * 0.3)
            d.arc([xx, y_, xx + w_ * 0.2, y_ + h_ * 0.16], 0, 180,
                  fill=col, width=int(u(1.4)))

    if scene == "hormuz":
        ship(cx - w_ * 0.14, cy, S * 0.9)
        ship(cx + w_ * 0.22, cy + h_ * 0.10, S * 0.6, (52, 52, 60, 255))
        flame(cx + w_ * 0.22, cy - h_ * 0.05, S * 0.7)
        waves(gy + h_ * 0.04)
    elif scene == "benghazi":
        ship(cx, cy + h_ * 0.10, S * 1.05)
        drone(cx - w_ * 0.24, y0 + h_ * 0.20, S * 0.8)
        d.polygon([(cx - w_ * 0.24, y0 + h_ * 0.26), (cx - w_ * 0.05, gy),
                   (cx + w_ * 0.06, gy)], fill=(255, 240, 190, 40))
        waves(gy + h_ * 0.04)
    elif scene == "fire":
        d.rectangle([cx - w_ * 0.30, gy - h_ * 0.34, cx + w_ * 0.30, gy],
                    fill=(36, 30, 30, 255))
        for i in range(4):
            flame(cx - w_ * 0.22 + i * w_ * 0.14, gy - h_ * 0.36, S * (0.9 + (i % 2) * 0.3))
        d.rectangle([cx - w_ * 0.30, gy - h_ * 0.40, cx + w_ * 0.30, gy - h_ * 0.34],
                    fill=(24, 22, 22, 255))
    elif scene == "house":
        d.rectangle([cx - w_ * 0.32, cy - h_ * 0.26, cx + w_ * 0.32, cy - h_ * 0.16],
                    fill=(238, 234, 224, 255))
        d.polygon([(cx - w_ * 0.38, cy - h_ * 0.26), (cx + w_ * 0.38, cy - h_ * 0.26),
                   (cx, cy - h_ * 0.44)], fill=(238, 234, 224, 255))
        for i in range(4):
            xx = cx - w_ * 0.27 + i * w_ * 0.17
            d.rectangle([xx, cy - h_ * 0.16, xx + w_ * 0.07, gy], fill=(238, 234, 224, 255))
        d.rectangle([cx - w_ * 0.34, gy, cx + w_ * 0.34, gy + h_ * 0.05],
                    fill=(238, 234, 224, 255))
    elif scene == "westbank":
        d.rectangle([cx - w_ * 0.26, cy + h_ * 0.02, cx + w_ * 0.26, cy + h_ * 0.20],
                    fill=(28, 28, 32, 255))
        d.rectangle([cx - w_ * 0.16, cy - h_ * 0.14, cx + w_ * 0.12, cy + h_ * 0.02],
                    fill=(28, 28, 32, 255))
        flame(cx - w_ * 0.05, cy - h_ * 0.30, S * 0.85)
        flame(cx + w_ * 0.14, cy - h_ * 0.24, S * 0.6, (255, 100, 40, 255))
    elif scene == "khartoum":
        d.rectangle([cx - w_ * 0.30, cy - h_ * 0.10, cx - w_ * 0.05, gy], fill=(70, 56, 44, 255))
        d.rectangle([cx + w_ * 0.04, cy - h_ * 0.22, cx + w_ * 0.30, gy], fill=(80, 64, 50, 255))
        d.rectangle([cx + w_ * 0.10, cy - h_ * 0.10, cx + w_ * 0.24, cy + h_ * 0.02],
                    fill=(240, 240, 240, 255))
        d.rectangle([cx + w_ * 0.155, cy - h_ * 0.10, cx + w_ * 0.185, cy + h_ * 0.02],
                    fill=(200, 40, 40, 255))
        d.rectangle([cx + w_ * 0.10, cy - h_ * 0.045, cx + w_ * 0.24, cy - h_ * 0.015],
                    fill=(200, 40, 40, 255))
        drone(cx - w_ * 0.22, y0 + h_ * 0.16, S * 0.7)
    elif scene == "southsudan":
        d.ellipse([cx - w_ * 0.16, y0 + h_ * 0.10, cx - w_ * 0.04, y0 + h_ * 0.34],
                  fill=(255, 220, 120, 255))
        for i, fx in enumerate((0.20, 0.46, 0.70)):
            xx = x0 + w_ * fx
            d.polygon([(xx, gy), (xx + w_ * 0.07, gy - h_ * 0.30),
                       (xx + w_ * 0.14, gy)], fill=(60, 70, 44, 255))
        d.rectangle([cx - w_ * 0.03, cy - h_ * 0.06, cx + w_ * 0.03, cy + h_ * 0.16],
                    fill=(240, 240, 235, 255))
        d.rectangle([cx - w_ * 0.09, cy + h_ * 0.015, cx + w_ * 0.09, cy + h_ * 0.075],
                    fill=(240, 240, 235, 255))
    elif scene == "tennis":
        d.line([x0 + w_ * 0.1, gy + h_ * 0.02, x1 - w_ * 0.1, gy + h_ * 0.02],
               fill=(240, 240, 240, 220), width=int(u(1.6)))
        d.ellipse([cx + w_ * 0.10, y0 + h_ * 0.14, cx + w_ * 0.24, y0 + h_ * 0.36],
                  fill=(205, 230, 90, 255))
        d.arc([cx + w_ * 0.10, y0 + h_ * 0.14, cx + w_ * 0.24, y0 + h_ * 0.36],
              60, 300, fill=(250, 250, 250, 255), width=int(u(1.2)))
        d.line([cx - w_ * 0.28, cy + h_ * 0.18, cx + w_ * 0.05, cy - h_ * 0.10],
               fill=(30, 30, 30, 255), width=int(u(2.2)))
        d.ellipse([cx - w_ * 0.36, cy - h_ * 0.30, cx - w_ * 0.20, cy - h_ * 0.02],
                  outline=(30, 30, 30, 255), width=int(u(2)))
    elif scene == "football":
        d.ellipse([cx - w_ * 0.13, cy - h_ * 0.26, cx + w_ * 0.13, cy + h_ * 0.26],
                  fill=(245, 245, 245, 255))
        d.polygon([(cx - w_ * 0.045, cy - h_ * 0.09), (cx + w_ * 0.045, cy - h_ * 0.09),
                   (cx + w_ * 0.07, cy + h_ * 0.03), (cx, cy + h_ * 0.10),
                   (cx - w_ * 0.07, cy + h_ * 0.03)], fill=(26, 26, 26, 255))
        d.rectangle([x0 + w_ * 0.06, gy - h_ * 0.30, x0 + w_ * 0.10, gy], fill=(245, 245, 245, 200))
        d.rectangle([x1 - w_ * 0.10, gy - h_ * 0.30, x1 - w_ * 0.06, gy], fill=(245, 245, 245, 200))
        d.line([x0 + w_ * 0.06, gy - h_ * 0.30, x1 - w_ * 0.06, gy - h_ * 0.30],
               fill=(245, 245, 245, 200), width=int(u(1.4)))
    elif scene == "fifa":
        d.rectangle([cx - u(1.5), cy - h_ * 0.05, cx + u(1.5), cy + h_ * 0.16],
                    fill=(255, 205, 84, 255))
        d.rectangle([cx - w_ * 0.10, cy + h_ * 0.16, cx + w_ * 0.10, cy + h_ * 0.22],
                    fill=(255, 205, 84, 255))
        d.arc([cx - w_ * 0.20, cy - h_ * 0.30, cx - w_ * 0.02, cy + h_ * 0.02],
              270, 90, fill=(255, 205, 84, 255), width=int(u(2)))
        d.arc([cx + w_ * 0.02, cy - h_ * 0.30, cx + w_ * 0.20, cy + h_ * 0.02],
              90, 270, fill=(255, 205, 84, 255), width=int(u(2)))
        d.rectangle([cx - w_ * 0.075, cy - h_ * 0.32, cx + w_ * 0.075, cy - h_ * 0.05],
                    fill=(255, 205, 84, 255))
    elif scene == "castle":
        d.rectangle([cx - w_ * 0.30, gy - h_ * 0.16, cx + w_ * 0.30, gy], fill=(150, 60, 48, 255))
        d.rectangle([cx - w_ * 0.22, gy - h_ * 0.34, cx + w_ * 0.22, gy - h_ * 0.16],
                    fill=(238, 234, 226, 255))
        d.polygon([(cx - w_ * 0.28, gy - h_ * 0.34), (cx + w_ * 0.28, gy - h_ * 0.34),
                   (cx + w_ * 0.16, gy - h_ * 0.48), (cx - w_ * 0.16, gy - h_ * 0.48)],
                  fill=(150, 60, 48, 255))
        d.polygon([(cx - w_ * 0.16, gy - h_ * 0.48), (cx + w_ * 0.16, gy - h_ * 0.48),
                   (cx, gy - h_ * 0.58)], fill=(120, 48, 40, 255))
    elif scene == "smog":
        for i, fx in enumerate((0.16, 0.44, 0.70)):
            xx = x0 + w_ * fx
            d.rectangle([xx, gy - h_ * 0.34, xx + w_ * 0.05, gy], fill=(70, 64, 58, 255))
            for j in range(3):
                d.ellipse([xx - w_ * 0.02 + j * w_ * 0.03, gy - h_ * (0.42 + j * 0.10),
                           xx + w_ * 0.07 + j * w_ * 0.03, gy - h_ * (0.32 + j * 0.10)],
                          fill=(200, 194, 178, 110))
        d.rectangle([x0, y0 + h_ * 0.52, x1, y0 + h_ * 0.66], fill=(226, 218, 196, 90))
    return d


# ---------------------------------------------------------------- world map
# Coarse dotted land grid, authored for this page as row runs on an 88 x 36
# equirectangular grid (col from longitude, row from latitude).
MAP_RUNS = {
    1: [(50, 80)],
    2: [(4, 16), (27, 31), (47, 80)],
    3: [(4, 19), (27, 31), (44, 49), (50, 82)],
    4: [(5, 20), (43, 50), (51, 82)],
    5: [(6, 21), (43, 51), (52, 81)],
    6: [(7, 22), (43, 52), (53, 79)],
    7: [(8, 23), (44, 52), (53, 78), (80, 81)],
    8: [(9, 24), (44, 53), (54, 77), (79, 81)],
    9: [(9, 24), (44, 52), (54, 76), (79, 80)],
    10: [(10, 25), (44, 51), (52, 55), (56, 76)],
    11: [(10, 25), (44, 50), (52, 58), (59, 75)],
    12: [(11, 25), (44, 53), (54, 59), (60, 75)],
    13: [(11, 24), (44, 54), (55, 59), (63, 74)],
    14: [(14, 20), (45, 55), (63, 66), (69, 72)],
    15: [(15, 20), (45, 55), (63, 65), (69, 71)],
    16: [(16, 20), (46, 55), (63, 64), (68, 71)],
    17: [(19, 22), (46, 55)],
    18: [(20, 23), (24, 27), (47, 54)],
    19: [(24, 31), (47, 54)],
    20: [(24, 33), (47, 53), (66, 69), (70, 74)],
    21: [(25, 34), (48, 53), (69, 73), (74, 75), (77, 81)],
    22: [(25, 34), (48, 52), (69, 73)],
    23: [(26, 33), (48, 52), (71, 77)],
    24: [(26, 32), (49, 51), (70, 78)],
    25: [(27, 31), (49, 51), (70, 78)],
    26: [(27, 30), (49, 51), (54, 54), (71, 77)],
    27: [(27, 30), (49, 50), (71, 76)],
    28: [(28, 30), (49, 50), (72, 75)],
    29: [(28, 29), (49, 50)],
    30: [(28, 29), (84, 85)],
    31: [(28, 29), (85, 86)],
    32: [(28, 28)],
    33: [(28, 28)],
    34: [(28, 28)],
}
MAP_W = 88
MAP_H = 36
LAT_TOP, LAT_BOT = 80.0, -58.0

LAND = set()
for _r, _runs in MAP_RUNS.items():
    for _c0, _c1 in _runs:
        for _c in range(_c0, _c1 + 1):
            LAND.add((_r, _c))


def pin_xy(lon, lat, box):
    x0, y0, x1, y1 = box
    fx = (lon + 180.0) / 360.0
    fy = (LAT_TOP - lat) / (LAT_TOP - LAT_BOT)
    return x0 + fx * (x1 - x0), y0 + fy * (y1 - y0)


def draw_map(img, box, pins):
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img, "RGBA")
    cw = (x1 - x0) / MAP_W
    ch = (y1 - y0) / MAP_H
    r = max(u(1.1), cw * 0.30)
    for (ri, ci) in LAND:
        cx = x0 + (ci + 0.5) * cw
        cy = y0 + (ri + 0.5) * ch
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(120, 116, 104, 255))
    pf = F_SANS(7.5, bold=True)
    for n, lon, lat in pins:
        cx, cy = pin_xy(lon, lat, box)
        pr = u(6.5)
        d.ellipse([cx - pr, cy - pr, cx + pr, cy + pr], fill=RED,
                  outline=(255, 255, 255, 255), width=int(u(1.2)))
        s = str(n)
        tw = text_w(d, s, pf)
        d.text((cx - tw / 2, cy - pf.size / 2 - S), s, font=pf,
               fill=(255, 255, 255, 255))


# ---------------------------------------------------------------- assembly
MX = 18.0            # side margin, final px
CW = 1024.0 - 2 * MX


def build():
    img = Image.new("RGB", (W, W), PAPER)
    d = ImageDraw.Draw(img, "RGBA")

    def box(x, y, w_, h_):
        return (u(x), u(y), u(x + w_), u(y + h_))

    # ---- top band (ledger green, full bleed)
    d.rectangle(box(0, 0, 1024, 28), fill=GREEN)
    f_band = F_SANS(10, bold=True)
    spaced(d, (u(MX), u(8)), "ONE PAGE · THE WHOLE DAY · SET IN TYPE BEFORE THE WIRES CLOSE",
           f_band, (240, 246, 240), tracking=1)
    right = "MONDAY EDITION"
    rw = spaced_w(d, right, f_band, tracking=1)
    spaced(d, (u(1024 - MX) - rw, u(8)), right, f_band, (240, 246, 240), tracking=1)

    # ---- masthead
    title = "THE MONDAY LEDGER"
    f_title = F_DISPLAY(55)
    tw = text_w(d, title, f_title)
    d.text(((W - tw) / 2, u(34)), title, font=f_title, fill=INK)
    f_spell = F_SERIF(14.5, italic=True)
    spell = "Monday, the twenty-third of November, two thousand and twenty-six"
    tw = text_w(d, spell, f_spell)
    d.text(((W - tw) / 2, u(96)), spell, font=f_spell, fill=GREEN_DARK)
    claim = "36 STORIES · 7 REGIONS · EVERY ONE DATED MONDAY 23 NOVEMBER 2026"
    f_claim = F_SANS(11, bold=True)
    cw_claim = spaced_w(d, claim, f_claim, tracking=2)
    spaced(d, ((W - cw_claim) / 2, u(116)), claim, f_claim, GREEN, tracking=2)
    d.line([u(MX), u(126), u(1024 - MX), u(126)], fill=INK, width=int(u(1.6)))
    d.line([u(MX), u(129), u(1024 - MX), u(129)], fill=INK, width=int(u(0.7)))

    # ---- strapline
    strap = ("A Kyiv suburb digs for its missing \u00b7 Antalya ends with no pact "
             "\u00b7 Asia's rout meets a rescue fund")
    f_strap = F_SERIF(14, italic=True)
    tw = text_w(d, strap, f_strap)
    d.text(((W - tw) / 2, u(133)), strap, font=f_strap, fill=RED_DARK)

    # ---- stat strip
    sy = 152.0
    cell_w = CW / 6
    f_num = F_SERIF(25, bold=True)
    f_cap = F_SANS(8.5, bold=True)
    for i, (num, cap) in enumerate(STATS):
        cx = MX + i * cell_w
        tw = text_w(d, num, f_num)
        d.text((u(cx + (cell_w - tw / S) / 2), u(sy + 4)), num, font=f_num, fill=GREEN)
        for j, ln in enumerate(cap.split("\n")):
            lw = text_w(d, ln, f_cap)
            d.text((u(cx + (cell_w - lw / S) / 2), u(sy + 40 + j * 11)), ln,
                   font=f_cap, fill=GREY)
        if i:
            d.line([u(cx), u(sy + 6), u(cx), u(sy + 62)], fill=HAIRLINE, width=S)
    d.line([u(MX), u(222), u(1024 - MX), u(222)], fill=HAIRLINE, width=S)

    # ---- region bar
    counts = {}
    for h in HEROES:
        counts[h["region"]] = counts.get(h["region"], 0) + 1
    for c in CARDS:
        counts[c[3]] = counts.get(c[3], 0) + 1
    for a in ALSO:
        counts[a[1]] = counts.get(a[1], 0) + 1
    total = sum(counts.values())
    assert total == 36, f"story count {total} != 36"
    order = ["EUROPE", "ASIA-PACIFIC", "AMERICAS", "AFRICA", "MIDDLE EAST",
             "OCEANIA", "WORLD"]
    ry = 224.0
    x = MX
    f_reg = F_SANS(9.5, bold=True)
    # proportional widths with a 46px minimum so every label fits inside
    widths = {reg: CW * counts[reg] / total for reg in order}
    deficit = sum(max(0.0, 46.0 - w_) for w_ in widths.values())
    widest = max(order, key=lambda r_: widths[r_])
    for reg in order:
        widths[reg] = max(46.0, widths[reg])
    widths[widest] -= deficit
    for reg in order:
        wseg = widths[reg]
        d.rectangle(box(x, ry, wseg, 24), fill=REGION_COLORS[reg])
        label = f"{reg} {counts[reg]}"
        lw = text_w(d, label, f_reg)
        d.text((u(x + (wseg - lw / S) / 2), u(ry + 5)), label, font=f_reg,
               fill=(255, 255, 255))
        x += wseg

    # ---- UTC timeline strip
    uy = 250.0
    d.rectangle(box(0, uy, 1024, 26), fill=(18, 18, 18))
    f_utc = F_MONO(9.5, bold=True)
    spaced(d, (u(MX), u(uy + 3)), "THE DAY IN UTC", F_SANS(9.5, bold=True),
           (255, 255, 255), tracking=1)
    items = [f"{t} {s}" for t, s in TIMELINE]
    for row_i in range(2):
        yy = uy + 2 + row_i * 12
        xx = MX + (150 if row_i == 0 else 0)
        for it in items[row_i * 3:(row_i + 1) * 3]:
            d.text((u(xx), u(yy)), it, font=f_utc, fill=(235, 232, 220))
            xx += text_w(d, it, f_utc) / S + 16

    # ---- heroes
    hy = 276.0
    hw = (CW - 24) / 3
    f_kick = F_SANS(10.5, bold=True)
    f_head = F_SERIF(16.5, bold=True)
    f_sum = F_SERIF(11.5)
    f_src = F_SANS(9, bold=True)
    pins = []
    for i, h in enumerate(HEROES):
        hx = MX + i * (hw + 12)
        SCENE_HERO[h["scene"]](img, box(hx, hy, hw, 108))
        d = ImageDraw.Draw(img, "RGBA")
        chip(d, (u(hx + 6), u(hy + 6)), h["label"], F_SANS(10, bold=True),
             RED, (255, 255, 255))
        cw_ = text_w(d, h["chip"], F_SANS(10, bold=True)) + u(10)
        chip(d, (u(hx + hw) - cw_, u(hy + 6)), h["chip"], F_SANS(10, bold=True),
             (18, 18, 18), (255, 255, 255))
        ky = hy + 114
        num = f"{h['n']}  "
        d.text((u(hx), u(ky)), num, font=F_SERIF(13, bold=True), fill=RED)
        nw = text_w(d, num, F_SERIF(13, bold=True))
        spaced(d, (u(hx) + nw, u(ky + 2)), h["kicker"], f_kick, INK, tracking=1)
        st_w = text_w(d, h["status"], F_SANS(9, bold=True)) + u(10)
        chip(d, (u(hx + hw) - st_w, u(ky + 1)), h["status"], F_SANS(9, bold=True),
             GREEN, (255, 255, 255))
        block(d, (u(hx), u(hy + 132)), h["headline"], f_head, INK, u(hw),
              u(20), max_lines=2, tag=f"hero{i+1} headline")
        block(d, (u(hx), u(hy + 176)), h["summary"], f_sum, (40, 40, 38),
              u(hw), u(14.5), max_lines=6, tag=f"hero{i+1} summary")
        spaced(d, (u(hx), u(hy + 268)), h["source"].upper(), f_src, GREY, tracking=1)
        pins.append((h["n"], h["pin"][0], h["pin"][1]))
        if i:
            d.line([u(hx - 6), u(hy + 114), u(hx - 6), u(hy + 282)],
                   fill=HAIRLINE, width=S)
    d.line([u(MX), u(564), u(1024 - MX), u(564)], fill=HAIRLINE, width=S)

    # ---- cards: 6 across x 2 rows
    cy0 = 568.0
    card_w = (CW - 5 * 8) / 6
    card_h = 102.0
    f_ckick = F_SANS(8.5, bold=True)
    f_chead = F_SERIF(12.5, bold=True)
    f_csum = F_SANS(9.5)
    for idx, c in enumerate(CARDS):
        (n, scene, chip_t, region, kicker, headline, summary, source,
         status, pin) = c
        r, col = divmod(idx, 6)
        cx = MX + col * (card_w + 8)
        cy = cy0 + r * (card_h + 4)
        card_scene(img, box(cx, cy, card_w, 34), scene)
        d = ImageDraw.Draw(img, "RGBA")
        chip(d, (u(cx + 4), u(cy + 4)), chip_t, F_SANS(8.5, bold=True),
             RED, (255, 255, 255), pad_x=4, pad_y=1.5)
        if status != "REPORTED":
            sw_ = text_w(d, status, F_SANS(8.5, bold=True)) + u(8)
            chip(d, (u(cx + card_w) - sw_, u(cy + 4)), status,
                 F_SANS(8.5, bold=True), GREEN, (255, 255, 255),
                 pad_x=4, pad_y=1.5)
        spaced(d, (u(cx), u(cy + 38)), f"{n} · {kicker}", f_ckick, GREEN_DARK,
               tracking=0)
        block(d, (u(cx), u(cy + 49)), headline, f_chead, INK, u(card_w),
              u(14.5), max_lines=2, tag=f"card{n} headline")
        block(d, (u(cx), u(cy + 79)), summary, f_csum, (52, 52, 50),
              u(card_w), u(11.5), max_lines=2, tag=f"card{n} summary")
        pins.append((n, pin[0], pin[1]))

    # ---- map + ALSO
    my = 776.0
    d.line([u(MX), u(my - 4), u(1024 - MX), u(my - 4)], fill=HAIRLINE, width=S)
    spaced(d, (u(MX), u(my + 2)), "WHERE IT HAPPENED — PINS = STORY NUMBERS",
           F_SANS(10, bold=True), INK, tracking=1)
    draw_map(img, box(MX, my + 18, 350, 128), pins)
    d = ImageDraw.Draw(img, "RGBA")
    ax = MX + 366
    aw = 1024 - MX - ax
    spaced(d, (u(ax), u(my + 2)), f"ALSO ON MONDAY 23 NOVEMBER — {len(ALSO)} MORE STORIES",
           F_SANS(10, bold=True), INK, tracking=1)
    f_also = F_SANS(10)
    f_also_b = F_SANS(10, bold=True)
    col_w = (aw - 14) / 2
    for j, (n, region, text_, source) in enumerate(ALSO):
        col = 0 if j < 11 else 1
        row = j if j < 11 else j - 11
        xx = ax + col * (col_w + 14)
        yy = my + 20 + row * 13
        num = f"{n} "
        d.text((u(xx), u(yy)), num, font=f_also_b, fill=RED)
        nw = text_w(d, num, f_also_b)
        line = f"{text_} — {region.title()} · {source}"
        if text_w(d, line, f_also) / S > col_w - nw / S:
            FIT_ERRORS.append(f"also{n}: line too wide "
                              f"({text_w(d, line, f_also)/S:.0f} > {col_w - nw/S:.0f})")
        d.text((u(xx) + nw, u(yy)), line, font=f_also, fill=(40, 40, 38))

    # ---- DATE CHECK
    dy = 934.0
    d.rectangle(box(MX, dy, CW, 46), outline=RED, width=int(u(1.6)))
    d.rectangle(box(MX, dy, 118, 15), fill=RED)
    d.text((u(MX + 6), u(dy + 2)), "DATE CHECK", font=F_SANS(10, bold=True),
           fill=(255, 255, 255))
    block(d, (u(MX + 126), u(dy + 3)), DATE_CHECK, F_SERIF(10.5), (52, 40, 38),
          u(CW - 134), u(13), max_lines=3, tag="datecheck")

    # ---- sources + legend
    f_leg = F_SANS(9.5)
    lw = text_w(d, SOURCES_LINE, f_leg)
    if lw / S > CW:
        FIT_ERRORS.append("sources line too wide")
    d.text((u(MX), u(984)), SOURCES_LINE, font=f_leg, fill=GREY)
    lw = text_w(d, LEGEND, f_leg)
    if lw / S > CW:
        FIT_ERRORS.append("legend line too wide")
    d.text((u(MX), u(996)), LEGEND, font=f_leg, fill=GREY)

    # ---- footer band
    d.rectangle(box(0, 1004, 1024, 20), fill=GREEN)
    f_foot = F_SANS(9.5, bold=True)
    spaced(d, (u(MX), u(1009)), "THE LEDGER LINE — 36 STORIES · 7 REGIONS · 5 LEFT OUT AS OTHER DAYS",
           f_foot, (240, 246, 240), tracking=1)
    right = "WIRES READ TO 05:00 UTC · MONDAY 23 NOVEMBER 2026"
    rw = spaced_w(d, right, f_foot, tracking=1)
    spaced(d, (u(1024 - MX) - rw, u(1009)), right, f_foot, (240, 246, 240),
           tracking=1)

    return img


def main():
    img = build()
    if FIT_ERRORS:
        print("FIT ERRORS:")
        for e in FIT_ERRORS:
            print(" -", e)
    small = img.resize((1024, 1024), Image.LANCZOS)
    small.save(OUT, optimize=True)
    size = os.path.getsize(OUT)
    print(f"saved {OUT}: {small.size}, {size} bytes")
    if size > 1048576:
        print("OVER 1 MiB — quantizing to a 256-colour palette")
        q = small.quantize(colors=256, method=Image.MEDIANCUT)
        q.save(OUT, optimize=True)
        print(f"quantized: {os.path.getsize(OUT)} bytes")


if __name__ == "__main__":
    main()
