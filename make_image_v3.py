#!/usr/bin/env python3
"""news-image-20261117 entry, v3: 'Tuesday 17 November 2026' as one broadsheet page.

Drawn from scratch with Pillow: 15 numbered illustrated cards, a pinned world
map, 35 numbered briefs (50 stories in all), a by-the-numbers strip, a
per-region count bar computed from the story data, a DATE CHECK strip naming
the tempting stories left out because they are not Tuesday's, and a
faithfulness footer. Every contested claim is attributed in its headline or
sub-deck; the one future event is labelled NEXT.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")
W = H = 1024

# ---------------------------------------------------------------- palette ---
PAPER = (246, 241, 229)
PAPER_DARK = (238, 230, 211)
INK = (20, 26, 43)
NAVY = (18, 38, 74)
RED = (172, 44, 38)
GREY = (92, 96, 104)
CARD_LINE = (196, 186, 160)
SEA = (198, 216, 228)
LAND = (168, 178, 148)
LAND_EDGE = (128, 140, 108)

REGION_COLORS = {
    "EUROPE": (32, 81, 143),
    "MIDDLE EAST": (163, 62, 32),
    "ASIA": (110, 62, 148),
    "AFRICA": (34, 120, 74),
    "AMERICAS": (178, 44, 92),
    "OCEANIA": (28, 128, 138),
    "WORLD": (84, 92, 108),
}

# ------------------------------------------------------------------ fonts ---
def _font(candidates, size):
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

SERIF_B = ["/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
           "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"]
SERIF_R = ["/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
           "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"]
SANS_R = ["/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
          "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
SANS_B = ["/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
          "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
NUM_B = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
         "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"]

def serif_b(size): return _font(SERIF_B, size)
def serif_r(size): return _font(SERIF_R, size)
def sans_r(size): return _font(SANS_R, size)
def sans_b(size): return _font(SANS_B, size)
def num_b(size): return _font(NUM_B, size)

# ---------------------------------------------------------------- helpers ---
def tw(draw, text, font):
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0]

def wrap(draw, text, font, width):
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if tw(draw, trial, font) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines

def fit_lines(draw, text, start_size, width, max_lines, font_fn, min_size=10):
    """Shrink a serif headline until it wraps into at most max_lines lines."""
    size = start_size
    while size > min_size:
        font = font_fn(size)
        lines = wrap(draw, text, font, width)
        if len(lines) <= max_lines:
            return font, lines
        size -= 1
    font = font_fn(min_size)
    return font, wrap(draw, text, font, width)

def badge(draw, cx, cy, r, number, color):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
    font = num_b(int(r * 1.05))
    label = str(number)
    w = tw(draw, label, font)
    draw.text((cx - w / 2, cy - int(r * 0.58)), label, font=font, fill=(255, 255, 255))

# ------------------------------------------------------------------- data ---
# region, kicker, headline, sub-deck, illustration key, lon, lat
CARDS = [
    ("EUROPE", "EUROPE · UKRAINE WAR",
     "Ukraine says a Crimean Bridge span fell into the sea",
     "Second strike in two days; Zelenskyy hails an \u201cunprecedented operation\u201d.",
     "bridge", 37.0, 45.3),
    ("MIDDLE EAST", "MIDDLE EAST · GULF",
     "Iran sends drones at a US radar in Bahrain; US hits back",
     "Bahrain and the US say all were downed; US jets then strike Qeshm. "
     "Iran says tankers hit mines in Hormuz.",
     "gulf", 50.6, 26.2),
    ("ASIA", "ASIA · DIPLOMACY",
     "Trump holds his first Quad summit, in Manila",
     "The four unveil critical-minerals deals; Putin reaches Shenzhen for "
     "Thursday's talks with Trump and Xi.",
     "quad", 121.0, 14.6),
    ("ASIA", "NEXT · DIPLOMACY",
     "Trump, Xi, Putin set to meet Thursday",
     "All three capitals confirm it. It has not happened yet.",
     "next", 114.1, 22.5),
    ("AFRICA", "AFRICA · HEALTH",
     "Ebola cases top 11,000 in DR Congo",
     "WHO: cases doubled in three months; about 5,400 dead.",
     "ebola", 22.5, -2.8),
    ("MIDDLE EAST", "MIDDLE EAST · GAZA",
     "Gaza truce at risk of collapse, UN is told",
     "Board of Peace told; 1.4m face acute hunger, UN says.",
     "tents", 34.3, 31.4),
    ("AMERICAS", "AMERICAS · HEALTH",
     "US, Mexico, Bolivia lose measles-free status",
     "PAHO cites a year of spread; US counts 5,700+ cases.",
     "measles", -98.0, 39.0),
    ("AMERICAS", "US · BUSINESS",
     "Nvidia's sales double to $115.8bn",
     "Posted after the close; earlier the Dow fell 849 points (\u22121.6%).",
     "chart", -122.0, 37.4),
    ("AFRICA", "AFRICA · CONFLICT",
     "UN verifies 2,230 civilian deaths in Sudan",
     "January\u2013October 2026; 1,630+ were killed by drones.",
     "drone", 30.2, 15.5),
    ("ASIA", "ASIA · POLITICS",
     "Mongolia's president says he will resign",
     "Denies a $25m graft claim; parliament must accept.",
     "doc", 106.8, 47.9),
    ("EUROPE", "EUROPE · POLITICS",
     "Serbia's student-led majority takes its seats",
     "140 of 250 seats; Vu\u010di\u0107's party goes into opposition.",
     "hemicycle", 20.5, 44.8),
    ("MIDDLE EAST", "MIDDLE EAST · POLITICS",
     "Knesset elects Kahana speaker, 66\u201352",
     "Eisenkot's ally wins the ballot with Arab-bloc backing.",
     "gavel", 35.2, 31.8),
    ("ASIA", "ASIA · LABOUR",
     "Bangladesh police tear-gas garment workers",
     "Wage demand Tk 30,000 vs 12,500; 37 factories shut.",
     "factory", 90.4, 23.8),
    ("EUROPE", "RUSSIA · AIR CRASH",
     "An-12 crash in Siberia kills all 19",
     "The transport came down near Kemerovo; fault suspected.",
     "crash", 86.1, 54.7),
    ("WORLD", "GLOBAL · CLIMATE",
     "COP31 divided over a fossil-fuel phase-out",
     "Nations weigh the first draft; the Antalya talks end Friday.",
     "globe", 30.7, 36.9),
]

# text, region, lon, lat (lon/lat None = no dot on the map)
BRIEFS = [
    ("Kyiv: Russian missiles hit two Dnipro bridges", "EUROPE", 30.5, 50.4),
    ("Prague: two trains collide; 46 people injured", "EUROPE", 14.4, 50.1),
    ("France: public-sector strike; 146,000 march", "EUROPE", 2.3, 48.9),
    ("Poland: Tusk survives no-confidence vote, 242\u2013200", "EUROPE", 21.0, 52.2),
    ("Moldova: airspace shut as a drone crosses Chi\u0219in\u0103u", "EUROPE", 28.8, 47.0),
    ("Turkey: police seize opposition broadcaster S\u00f6zc\u00fc TV", "EUROPE", 29.0, 41.0),
    ("UK: sanctions on 8 settlement firms and Tzav 9", "EUROPE", -0.1, 51.5),
    ("Vatican: Pope Leo XIV back from South America", "EUROPE", 12.5, 41.9),
    ("Kuwait: air defences engage drones overnight", "MIDDLE EAST", 47.9, 29.4),
    ("West Bank: settlers kill a woman, 72, near Jericho", "MIDDLE EAST", 35.3, 32.2),
    ("Oman: Iran's Araghchi holds shipping-safety talks", "MIDDLE EAST", 58.4, 23.6),
    ("Yemen: Houthis say a Saudi strike killed 7 in Hudaydah", "MIDDLE EAST", 42.9, 14.8),
    ("Gaza: floods ruin food stores as aid runs short", "MIDDLE EAST", 33.6, 30.6),
    ("India: Cyclone Akvan strengthens; Odisha evacuates", "ASIA", 86.0, 20.3),
    ("India: bus plunges into an Uttarakhand gorge; 8 dead", "ASIA", 79.3, 30.1),
    ("Japan: jets scrambled over a suspected Russian incursion", "ASIA", 130.6, 32.7),
    ("China\u2013Canada: tariff relief widens after Carney\u2013Xi talks", "ASIA", 106.0, 34.0),
    ("Malaysia: Macron's visit seals a strategic partnership", "ASIA", 101.7, 3.1),
    ("Football: India beat Pakistan 2\u20131 in the SAFF final", "ASIA", 78.0, 21.0),
    ("Mozambique: Mondlane's trial opens in Maputo", "AFRICA", 32.6, -25.9),
    ("Kenya: WFP feeds 30,000 who fled Ethiopia clashes", "AFRICA", 39.0, 3.5),
    ("Guinea: 224 jailed over illegal gold mining", "AFRICA", -9.2, 11.4),
    ("DR Congo: 2.3m more people in crisis hunger, WFP says", "AFRICA", 25.0, -4.0),
    ("Football: Togo beat Algeria 3\u20130 in an AFCON qualifier", "AFRICA", 1.2, 6.2),
    ("Haiti: Aristide's party fields no candidates", "AMERICAS", -72.3, 18.5),
    ("US Senate: Van Hollen challenges Schumer for leader", "AMERICAS", -77.0, 38.9),
    ("JPMorgan: software bug, \u201cnot cyber\u201d, hit Zelle payments", "AMERICAS", -73.0, 40.0),
    ("Apple: Pay, iCloud and App Store outage; \u201cnot a hack\u201d", "AMERICAS", -120.0, 35.5),
    ("Ecuador: fishermen sue the US over a boat strike", "AMERICAS", -80.0, -1.0),
    ("Australia: eases planned backpacker visa curbs", "OCEANIA", 134.0, -25.0),
    ("Cook Islands: Cyclone Xavier reaches Category 3", "OCEANIA", -160.0, -21.2),
    ("PNG: Auckland flights resume after 26 years", "OCEANIA", 147.0, -6.3),
    ("WHO: superbugs could kill 39m people by 2050", "WORLD", 6.1, 46.2),
    ("Space: Voyager 1 nears one light-day from Earth", "WORLD", None, None),
    ("UNESCO: AI models bend climate facts to please", "WORLD", 4.0, 47.0),
]

NUMBERS = [
    ("11,000+", "Ebola cases in DR Congo"),
    ("$115.8bn", "Nvidia's quarterly sales"),
    ("\u2212849", "Dow points lost on the day"),
    ("1,441", "drones Russia says it downed"),
    ("2,230", "Sudan deaths verified by UN"),
    ("140/250", "Serbia seats won by students"),
]

REGION_ORDER = ["EUROPE", "MIDDLE EAST", "ASIA", "AFRICA", "AMERICAS", "OCEANIA", "WORLD"]

# ---------------------------------------------------------- illustrations ---
def _sky(draw, x, y, w, h, top=(214, 226, 236), bottom=(232, 238, 243)):
    for i in range(h):
        t = i / max(h - 1, 1)
        c = tuple(int(top[j] + (bottom[j] - top[j]) * t) for j in range(3))
        draw.line([(x, y + i), (x + w, y + i)], fill=c)

def _smoke(draw, cx, cy, r, color=(105, 108, 112)):
    for dx, dy, rr in ((-r, 0, int(r * 0.7)), (0, -int(r * 0.5), r),
                       (r, 0, int(r * 0.75)), (int(r * 0.4), int(r * 0.3), int(r * 0.6))):
        draw.ellipse([cx + dx - rr, cy + dy - rr, cx + dx + rr, cy + dy + rr], fill=color)

def _burst(draw, cx, cy, r, color=(232, 148, 38)):
    pts = []
    for i in range(16):
        ang = math.pi * i / 8
        rad = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    draw.polygon(pts, fill=color)

def _flag_us(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(255, 255, 255), outline=INK, width=1)
    stripe = h / 7
    for i in range(0, 7, 2):
        draw.rectangle([x, y + i * stripe, x + w, y + (i + 1) * stripe], fill=(178, 34, 52))
    cw, ch = w * 0.45, stripe * 4
    draw.rectangle([x, y, x + cw, y + ch], fill=(38, 48, 110))
    for r in range(3):
        for c in range(4):
            px, py = x + 3 + c * (cw - 5) / 3, y + 3 + r * (ch - 5) / 2
            draw.ellipse([px - 1, py - 1, px + 1, py + 1], fill=(255, 255, 255))

def _flag_in(draw, x, y, w, h):
    t = h / 3
    draw.rectangle([x, y, x + w, y + t], fill=(240, 140, 50))
    draw.rectangle([x, y + t, x + w, y + 2 * t], fill=(255, 255, 255))
    draw.rectangle([x, y + 2 * t, x + w, y + h], fill=(30, 130, 60))
    draw.ellipse([x + w / 2 - 3, y + h / 2 - 3, x + w / 2 + 3, y + h / 2 + 3],
                 outline=(38, 48, 140), width=1)
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=1)

def _flag_jp(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(255, 255, 255), outline=INK, width=1)
    r = h * 0.26
    draw.ellipse([x + w / 2 - r, y + h / 2 - r, x + w / 2 + r, y + h / 2 + r],
                 fill=(188, 0, 45))

def _flag_au(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(28, 44, 120), outline=INK, width=1)
    draw.rectangle([x, y, x + w * 0.45, y + h * 0.5], fill=(178, 34, 52))
    draw.rectangle([x, y, x + w * 0.45, y + h * 0.5], outline=(255, 255, 255), width=1)
    for dx, dy in ((0.65, 0.25), (0.8, 0.55), (0.6, 0.75), (0.85, 0.85), (0.72, 0.42)):
        px, py = x + w * dx, y + h * dy
        draw.ellipse([px - 1.5, py - 1.5, px + 1.5, py + 1.5], fill=(255, 255, 255))

def _flag_cn(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(222, 41, 16), outline=INK, width=1)
    draw.ellipse([x + 3, y + 3, x + 9, y + 9], fill=(255, 222, 0))
    for dx, dy in ((13, 3), (15, 7), (15, 11), (13, 15)):
        draw.ellipse([x + dx - 1.5, y + dy - 1.5, x + dx + 1.5, y + dy + 1.5],
                     fill=(255, 222, 0))

def _flag_ru(draw, x, y, w, h):
    t = h / 3
    draw.rectangle([x, y, x + w, y + t], fill=(255, 255, 255))
    draw.rectangle([x, y + t, x + w, y + 2 * t], fill=(30, 60, 160))
    draw.rectangle([x, y + 2 * t, x + w, y + h], fill=(200, 30, 40))
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=1)

def ill_bridge(draw, x, y, w, h):
    _sky(draw, x, y, w, h)
    sea_y = y + int(h * 0.72)
    draw.rectangle([x, sea_y, x + w, y + h], fill=(120, 160, 190))
    for i in range(3):
        draw.line([(x + 8 + i * 40, sea_y + 5 + i * 4), (x + 30 + i * 40, sea_y + 5 + i * 4)],
                  fill=(170, 200, 220), width=2)
    deck = y + int(h * 0.52)
    # two standing spans with arches, middle span fallen
    for sx in (x + 6, x + w - 66):
        draw.rectangle([sx, deck, sx + 60, deck + 5], fill=(70, 78, 92))
        draw.arc([sx + 6, deck - 12, sx + 54, deck + 22], 180, 360, fill=(70, 78, 92), width=4)
        draw.rectangle([sx + 4, deck + 5, sx + 9, sea_y + 4], fill=(70, 78, 92))
        draw.rectangle([sx + 51, deck + 5, sx + 56, sea_y + 4], fill=(70, 78, 92))
    fx, fy = x + w // 2 - 26, deck + 3
    draw.polygon([(fx, fy), (fx + 52, fy), (fx + 62, fy + 20), (fx + 12, fy + 16)],
                 fill=(70, 78, 92))
    _burst(draw, x + w // 2 + 6, deck - 6, 11)
    _smoke(draw, x + w // 2 + 16, deck - 20, 10)
    draw.line([(x + 14, y + 6), (x + 60, y + 16), (x + 96, y + 12)], fill=INK, width=2)
    draw.polygon([(x + 96, y + 12), (x + 88, y + 8), (x + 90, y + 17)], fill=INK)

def ill_gulf(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=SEA)
    arabia = [(x, y + h), (x, y + int(h * 0.30)), (x + int(w * 0.20), y + int(h * 0.34)),
              (x + int(w * 0.30), y + int(h * 0.52)), (x + int(w * 0.38), y + int(h * 0.86)),
              (x + int(w * 0.30), y + h)]
    draw.polygon(arabia, fill=LAND)
    iran = [(x + int(w * 0.34), y), (x + w, y), (x + w, y + int(h * 0.30)),
            (x + int(w * 0.66), y + int(h * 0.34)), (x + int(w * 0.44), y + int(h * 0.22)),
            (x + int(w * 0.38), y + int(h * 0.06))]
    draw.polygon(iran, fill=LAND)
    font = sans_b(9)
    draw.text((x + int(w * 0.55), y + 3), "IRAN", font=font, fill=INK)
    draw.text((x + 4, y + int(h * 0.36)), "BAHRAIN", font=font, fill=INK)
    draw.text((x + int(w * 0.60), y + h - 12), "HORMUZ", font=font, fill=INK)
    bx, by = x + int(w * 0.335), y + int(h * 0.47)
    draw.pieslice([bx - 9, by - 9, bx + 9, by + 9], 180, 360, fill=(240, 240, 240),
                  outline=INK, width=1)
    draw.rectangle([bx - 9, by, bx + 9, by + 3], fill=(150, 150, 150))
    for ang in (-0.5, 0.1, 0.7):
        ex, ey = bx + 26 * math.cos(ang), by - 8 + 16 * math.sin(ang)
        draw.line([(bx, by - 4), (ex, ey)], fill=RED, width=1)
    qx, qy = x + int(w * 0.52), y + int(h * 0.30)
    for i in range(6):
        px = bx + 14 + i * (qx - bx - 20) / 5
        py = by - 6 - i * (by - qy - 4) / 5
        draw.ellipse([px - 1.5, py - 1.5, px + 1.5, py + 1.5], fill=RED)
    _burst(draw, qx, qy, 8)
    tx, ty = x + int(w * 0.80), y + int(h * 0.66)
    draw.polygon([(tx, ty), (tx + 34, ty), (tx + 30, ty + 7), (tx + 4, ty + 7)],
                 fill=(60, 60, 70))
    draw.rectangle([tx + 12, ty - 5, tx + 20, ty], fill=(60, 60, 70))
    _smoke(draw, tx + 26, ty - 9, 6, color=(90, 90, 96))

def ill_quad(draw, x, y, w, h):
    _sky(draw, x, y, w, h, top=(226, 232, 238), bottom=(240, 242, 240))
    table_y = y + int(h * 0.78)
    draw.rectangle([x + 8, table_y, x + w - 8, table_y + 7], fill=(110, 78, 48))
    flags = [_flag_us, _flag_in, _flag_jp, _flag_au]
    labels = ["US", "INDIA", "JAPAN", "AUSTRALIA"]
    fw, fh = int(w * 0.19), int(h * 0.52)
    font = sans_b(9)
    for i, (fn, lab) in enumerate(zip(flags, labels)):
        fx = x + int(w * (0.06 + i * 0.245))
        draw.line([(fx + fw // 2, y + 6), (fx + fw // 2, table_y)], fill=(90, 90, 90), width=2)
        fn(draw, fx, y + 6, fw, fh)
        lw = tw(draw, lab, font)
        draw.text((fx + fw / 2 - lw / 2, table_y + 9), lab, font=font, fill=INK)
    draw.polygon([(x + w - 30, y + 8), (x + w - 18, y + 14), (x + w - 30, y + 20)],
                 fill=(200, 160, 40))

def ill_next(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(238, 240, 244))
    cal_w, cal_h = int(w * 0.32), h - 8
    cx0, cy0 = x + 5, y + 4
    draw.rectangle([cx0, cy0, cx0 + cal_w, cy0 + cal_h], fill=(255, 255, 255),
                   outline=INK, width=1)
    draw.rectangle([cx0, cy0, cx0 + cal_w, cy0 + 10], fill=RED)
    f1 = sans_b(8)
    draw.text((cx0 + cal_w / 2 - tw(draw, "NOV", f1) / 2, cy0 + 1), "NOV", font=f1,
              fill=(255, 255, 255))
    f2 = num_b(13 if h < 50 else 17)
    draw.text((cx0 + cal_w / 2 - tw(draw, "19", f2) / 2, cy0 + 12), "19", font=f2, fill=INK)
    f3 = sans_b(7)
    draw.text((cx0 + cal_w / 2 - tw(draw, "THURSDAY", f3) / 2, cy0 + cal_h - 9),
              "THURSDAY", font=f3, fill=GREY)
    flags = [_flag_us, _flag_cn, _flag_ru]
    names = ["TRUMP", "XI", "PUTIN"]
    fw, fh = int(w * 0.17), int(h * 0.5)
    font = sans_b(8)
    for i, (fn, nm) in enumerate(zip(flags, names)):
        fx = x + int(w * 0.44) + i * int(w * 0.19)
        fn(draw, fx, y + int(h * 0.14), fw, fh)
        draw.text((fx + fw / 2 - tw(draw, nm, font) / 2, y + int(h * 0.14) + fh + 3),
                  nm, font=font, fill=INK)

def ill_ebola(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(240, 238, 230))
    base = y + h - 12
    bw = int(w * 0.16)
    x1 = x + int(w * 0.10)
    draw.rectangle([x1, base - int(h * 0.34), x1 + bw, base], fill=(150, 150, 150))
    x2 = x + int(w * 0.34)
    draw.rectangle([x2, base - int(h * 0.78), x2 + bw, base], fill=RED)
    font = sans_b(9)
    draw.text((x1 - 2, base + 1), "AUG", font=font, fill=GREY)
    f2 = num_b(13)
    draw.text((x2 - 4, base - int(h * 0.78) - 16), "11,000+", font=f2, fill=RED)
    draw.text((x2 + 2, base + 1), "NOW", font=font, fill=INK)
    tx = x + int(w * 0.62)
    ty = y + int(h * 0.30)
    draw.polygon([(tx, ty + 16), (tx + 22, ty), (tx + 44, ty + 16)], fill=(230, 230, 225),
                 outline=INK)
    draw.rectangle([tx + 4, ty + 16, tx + 40, ty + 30], fill=(245, 245, 242), outline=INK)
    draw.rectangle([tx + 19, ty + 19, tx + 25, ty + 27], fill=RED)
    draw.rectangle([tx + 16, ty + 21, tx + 28, ty + 24], fill=RED)

def ill_tents(draw, x, y, w, h):
    _sky(draw, x, y, w, h, top=(206, 216, 224), bottom=(228, 230, 224))
    ground = y + int(h * 0.86)
    draw.rectangle([x, ground, x + w, y + h], fill=(196, 182, 148))
    for i, tx in enumerate((x + 8, x + int(w * 0.30), x + int(w * 0.52))):
        tw_ = int(w * 0.20)
        draw.polygon([(tx, ground), (tx + tw_ // 2, ground - int(h * 0.58)),
                      (tx + tw_, ground)], fill=(236, 232, 218), outline=INK)
        draw.polygon([(tx + tw_ // 2 - 6, ground), (tx + tw_ // 2, ground - int(h * 0.22)),
                      (tx + tw_ // 2 + 6, ground)], fill=(90, 84, 70))
    bx = x + int(w * 0.78)
    bw2 = int(w * 0.18)
    top2 = ground - int(h * 0.40)
    mid2 = (top2 + ground) // 2
    draw.rectangle([bx, top2, bx + bw2, ground], fill=(240, 240, 238), outline=INK)
    draw.rectangle([bx + bw2 // 2 - 2, top2 + 3, bx + bw2 // 2 + 2, ground - 3], fill=RED)
    draw.rectangle([bx + 3, mid2 - 2, bx + bw2 - 3, mid2 + 2], fill=RED)

def ill_measles(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(238, 240, 242))
    fw, fh = int(w * 0.20), int(h * 0.44)
    fy = y + int(h * 0.10)
    _flag_us(draw, x + 6, fy, fw, fh)
    mx = x + int(w * 0.30)
    t = fh / 3
    draw.rectangle([mx, fy, mx + fw, fy + t], fill=(30, 130, 90))
    draw.rectangle([mx, fy + t, mx + fw, fy + 2 * t], fill=(255, 255, 255))
    draw.rectangle([mx, fy + 2 * t, mx + fw, fy + fh], fill=(200, 30, 40))
    draw.rectangle([mx, fy, mx + fw, fy + fh], outline=INK, width=1)
    bx = x + int(w * 0.54)
    t2 = fh / 3
    draw.rectangle([bx, fy, bx + fw, fy + t2], fill=(213, 0, 50))
    draw.rectangle([bx, fy + t2, bx + fw, fy + 2 * t2], fill=(250, 200, 40))
    draw.rectangle([bx, fy + 2 * t2, bx + fw, fy + fh], fill=(0, 120, 70))
    draw.rectangle([bx, fy, bx + fw, fy + fh], outline=INK, width=1)
    if h >= 50:
        font = sans_b(9)
        for fx, lab in ((x + 6, "US"), (mx, "MEXICO"), (bx, "BOLIVIA")):
            draw.text((fx + fw / 2 - tw(draw, lab, font) / 2, fy + fh + 3), lab,
                      font=font, fill=INK)
    vr = max(7, int(h * 0.24))
    vx, vy = x + int(w * 0.87), y + int(h * 0.30)
    draw.ellipse([vx - vr, vy - vr, vx + vr, vy + vr], fill=(196, 60, 130))
    for i in range(8):
        ang = math.pi * i / 4
        draw.line([(vx, vy), (vx + (vr + 4) * math.cos(ang), vy + (vr + 4) * math.sin(ang))],
                  fill=(196, 60, 130), width=2)
    bar_y = y + h - 13
    draw.rectangle([x + 6, bar_y, x + w - 6, bar_y + 12], fill=RED)
    f2 = sans_b(10)
    label = "MEASLES-FREE STATUS LOST"
    draw.text((x + w / 2 - tw(draw, label, f2) / 2, bar_y + 1), label, font=f2,
              fill=(255, 255, 255))

def ill_chart(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(24, 30, 40))
    base = y + h - 8
    vals = (0.30, 0.42, 0.55, 0.78)
    bw = int(w * 0.11)
    for i, v in enumerate(vals):
        bx = x + int(w * 0.07) + i * int(w * 0.15)
        draw.rectangle([bx, base - int(h * v), bx + bw, base], fill=(118, 200, 80))
    pts = [(x + int(w * 0.08), base - int(h * 0.34)), (x + int(w * 0.23), base - int(h * 0.46)),
           (x + int(w * 0.38), base - int(h * 0.60)), (x + int(w * 0.53), base - int(h * 0.82))]
    draw.line(pts, fill=(240, 200, 60), width=2)
    draw.polygon([(pts[-1][0], pts[-1][1]), (pts[-1][0] - 7, pts[-1][1] + 1),
                  (pts[-1][0] - 1, pts[-1][1] + 7)], fill=(240, 200, 60))
    font = num_b(13)
    draw.text((x + w - 5 - tw(draw, "$115.8bn", font), y + int(h * 0.14)), "$115.8bn",
              font=font, fill=(255, 255, 255))
    f2 = sans_b(10)
    draw.text((x + w - 5 - tw(draw, "DOW \u2212849", f2), y + int(h * 0.52)), "DOW \u2212849", font=f2,
              fill=(240, 120, 110))
    tx = x + int(w * 0.62)
    draw.polygon([(tx, y + int(h * 0.78)), (tx + 12, y + int(h * 0.78)),
                  (tx + 6, y + int(h * 0.78) + 8)], fill=(240, 120, 110))

def ill_drone(draw, x, y, w, h):
    _sky(draw, x, y, w, h, top=(216, 220, 226), bottom=(234, 232, 224))
    gy = y + h - 4
    for i, (bx, bh) in enumerate(((0.02, 0.34), (0.16, 0.46), (0.30, 0.30), (0.42, 0.40))):
        px = x + int(w * bx)
        draw.rectangle([px, gy - int(h * bh), px + int(w * 0.12), gy], fill=(120, 110, 96))
        draw.polygon([(px, gy - int(h * bh)), (px + int(w * 0.06), gy - int(h * bh) - 5),
                      (px + int(w * 0.12), gy - int(h * bh))], fill=(100, 92, 80))
    dx, dy = x + int(w * 0.30), y + int(h * 0.22)
    draw.ellipse([dx - 12, dy - 5, dx + 12, dy + 5], fill=(40, 42, 48))
    for sx, sy in ((-20, -10), (20, -10), (-20, 8), (20, 8)):
        draw.line([(dx, dy), (dx + sx, dy + sy)], fill=(40, 42, 48), width=2)
        draw.ellipse([dx + sx - 5, dy + sy - 2, dx + sx + 5, dy + sy + 2],
                     outline=(40, 42, 48), width=1)
    draw.ellipse([dx - 3, dy + 4, dx + 3, dy + 9], fill=RED)
    font = num_b(16)
    tx = x + int(w * 0.58)
    draw.text((tx, y + int(h * 0.10)), "2,230", font=font, fill=INK)
    f2 = sans_b(8)
    draw.text((tx, y + int(h * 0.50)), "DEATHS", font=f2, fill=GREY)
    draw.text((tx, y + int(h * 0.64)), "VERIFIED", font=f2, fill=GREY)
    draw.text((tx, y + int(h * 0.78)), "JAN\u2013OCT", font=f2, fill=GREY)

def ill_doc(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(238, 238, 234))
    fw, fh = int(w * 0.30), int(h * 0.72)
    fx, fy = x + int(w * 0.08), y + int(h * 0.14)
    t = fw / 3
    draw.rectangle([fx, fy, fx + t, fy + fh], fill=(200, 30, 50))
    draw.rectangle([fx + t, fy, fx + 2 * t, fy + fh], fill=(30, 60, 140))
    draw.rectangle([fx + 2 * t, fy, fx + fw, fy + fh], fill=(200, 30, 50))
    draw.rectangle([fx + 3, fy + 6, fx + 9, fy + 20], fill=(250, 200, 40))
    draw.rectangle([fx, fy, fx + fw, fy + fh], outline=INK, width=1)
    px, py = x + int(w * 0.48), y + int(h * 0.10)
    pw, ph = int(w * 0.44), int(h * 0.80)
    draw.rectangle([px, py, px + pw, py + ph], fill=(255, 255, 255), outline=INK, width=1)
    font = sans_b(8)
    draw.text((px + 5, py + 5), "RESIGNATION", font=font, fill=INK)
    for i in range(3):
        ly = py + 20 + i * 8
        draw.line([(px + 6, ly), (px + pw - 8, ly)], fill=(170, 170, 170), width=2)
    draw.ellipse([px + pw - 20, py + ph - 18, px + pw - 8, py + ph - 6], outline=RED, width=2)

def ill_hemicycle(draw, x, y, w, h):
    cx, cy = x + w // 2, y + int(h * 0.92)
    R = int(min(w * 0.44, h * 0.86))
    counts = (140, 103, 7)
    colors = ((178, 34, 52), (38, 64, 140), (170, 170, 170))
    total = sum(counts)
    for ring in range(4):
        r = R - ring * int(R * 0.20)
        start = 180.0
        for count, color in zip(counts, colors):
            sweep = 180.0 * count / total
            steps = max(int(sweep / 7), 1)
            for s in range(steps + 1):
                ang = math.radians(start + sweep * s / steps)
                px, py = cx + r * math.cos(ang), cy - r * math.sin(ang)
                draw.ellipse([px - 2.4, py - 2.4, px + 2.4, py + 2.4], fill=color)
            start += sweep
    f1, f2 = num_b(14), sans_b(8)
    draw.text((x + 6, y + 3), "140", font=f1, fill=(178, 34, 52))
    draw.text((x + 6, y + 20), "STUDENTS", font=f2, fill=GREY)
    label = "103"
    draw.text((x + w - 6 - tw(draw, label, f1), y + 3), label, font=f1, fill=(38, 64, 140))
    label2 = "VU\u010cI\u0106 BLOC"
    draw.text((x + w - 6 - tw(draw, label2, f2), y + 20), label2, font=f2, fill=GREY)

def ill_gavel(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(240, 238, 230))
    gx, gy = x + int(w * 0.16), y + int(h * 0.20)
    draw.line([(gx, gy + 26), (gx + 34, gy)], fill=(120, 82, 40), width=5)
    draw.rectangle([gx + 26, gy - 8, gx + 44, gy + 6], fill=(146, 100, 48), outline=INK)
    draw.rectangle([gx + 30, gy - 11, gx + 40, gy + 9], fill=(120, 82, 40))
    base_y = y + int(h * 0.74)
    draw.rectangle([x + int(w * 0.06), base_y, x + int(w * 0.42), base_y + 5],
                   fill=(120, 82, 40))
    font = num_b(20)
    draw.text((x + int(w * 0.52), y + int(h * 0.16)), "66\u201352", font=font, fill=INK)
    f2 = sans_b(9)
    draw.text((x + int(w * 0.52), y + int(h * 0.52)), "SPEAKER VOTE", font=f2, fill=GREY)
    draw.rectangle([x + int(w * 0.52), y + int(h * 0.68), x + int(w * 0.52) + 44,
                    y + int(h * 0.68) + 6], fill=(38, 64, 140))
    draw.rectangle([x + int(w * 0.52), y + int(h * 0.68) + 9, x + int(w * 0.52) + 35,
                    y + int(h * 0.68) + 15], fill=(170, 170, 170))

def ill_factory(draw, x, y, w, h):
    _sky(draw, x, y, w, h, top=(210, 218, 226), bottom=(232, 230, 222))
    gy = y + h - 3
    fx = x + int(w * 0.06)
    draw.rectangle([fx, gy - int(h * 0.52), fx + int(w * 0.52), gy], fill=(110, 104, 96))
    for i in range(2):
        cx0 = fx + 8 + i * int(w * 0.16)
        draw.rectangle([cx0, gy - int(h * 0.78), cx0 + 9, gy - int(h * 0.52)],
                       fill=(90, 84, 78))
        _smoke(draw, cx0 + 5, gy - int(h * 0.82), 5, color=(150, 150, 150))
    for i in range(4):
        wx = fx + 8 + i * int(w * 0.12)
        draw.rectangle([wx, gy - int(h * 0.36), wx + 8, gy - int(h * 0.24)],
                       fill=(240, 214, 130))
    font = sans_b(10)
    draw.text((fx + int(w * 0.56), gy - int(h * 0.66)), "Tk 30,000", font=font, fill=INK)
    draw.text((fx + int(w * 0.56), gy - int(h * 0.48)), "MINIMUM", font=sans_b(8), fill=GREY)
    for i in range(9):
        px = x + int(w * 0.08) + i * int(w * 0.075)
        py = gy - 9 - (i % 3) * 2
        draw.ellipse([px - 2.6, py - 2.6, px + 2.6, py + 2.6], fill=(50, 52, 60))
        draw.line([(px, py + 3), (px, py + 7)], fill=(50, 52, 60), width=2)
    _smoke(draw, x + int(w * 0.66), gy - int(h * 0.30), 8, color=(196, 200, 204))
    _smoke(draw, x + int(w * 0.78), gy - int(h * 0.22), 6, color=(206, 210, 214))

def ill_crash(draw, x, y, w, h):
    _sky(draw, x, y, w, h, top=(208, 218, 228), bottom=(230, 234, 236))
    peaks = [(x, y + h), (x + int(w * 0.16), y + int(h * 0.48)),
             (x + int(w * 0.30), y + int(h * 0.72)), (x + int(w * 0.46), y + int(h * 0.40)),
             (x + int(w * 0.62), y + int(h * 0.70)), (x + int(w * 0.78), y + int(h * 0.52)),
             (x + w, y + int(h * 0.78)), (x + w, y + h)]
    draw.polygon(peaks, fill=(148, 158, 168))
    for px, py in ((x + int(w * 0.16), y + int(h * 0.48)), (x + int(w * 0.46), y + int(h * 0.40))):
        draw.polygon([(px - 7, py + 8), (px, py), (px + 7, py + 8)], fill=(245, 248, 250))
    sx, sy = x + int(w * 0.10), y + int(h * 0.16)
    ex, ey = x + int(w * 0.58), y + int(h * 0.60)
    for i in range(9):
        t = i / 8
        px = sx + (ex - sx) * t
        py = sy + (ey - sy) * t + 14 * math.sin(t * math.pi * 0.7)
        draw.ellipse([px - 1.6, py - 1.6, px + 1.6, py + 1.6], fill=(120, 60, 40))
    px, py = x + int(w * 0.34), y + int(h * 0.34)
    draw.polygon([(px, py), (px + 34, py + 7), (px + 30, py + 13), (px + 4, py + 9)],
                 fill=(70, 76, 84))
    draw.polygon([(px + 2, py), (px - 6, py - 9), (px + 8, py + 2)], fill=(70, 76, 84))
    draw.polygon([(px + 30, py + 7), (px + 42, py + 1), (px + 38, py + 10)],
                 fill=(70, 76, 84))
    _burst(draw, ex, ey, 10)
    _smoke(draw, ex + 10, ey - 14, 9, color=(96, 98, 102))

def ill_globe(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(226, 236, 240))
    cx, cy, r = x + int(w * 0.34), y + int(h * 0.52), int(h * 0.40)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(120, 170, 205), outline=INK, width=1)
    blobs = [(-0.55, -0.30, 0.30, 0.20), (-0.30, 0.18, 0.20, 0.28), (0.08, -0.34, 0.34, 0.18),
             (0.16, 0.02, 0.22, 0.20), (0.52, 0.30, 0.20, 0.14)]
    for dx, dy, bw, bh in blobs:
        draw.ellipse([cx + (dx - bw / 2) * 2 * r * 0.5, cy + (dy - bh / 2) * 2 * r * 0.5,
                      cx + (dx + bw / 2) * 2 * r * 0.5, cy + (dy + bh / 2) * 2 * r * 0.5],
                     fill=(110, 160, 100))
    tx = x + int(w * 0.66)
    draw.rectangle([tx, y + int(h * 0.16), tx + 9, y + int(h * 0.62)], outline=INK, width=1)
    draw.rectangle([tx, y + int(h * 0.30), tx + 9, y + int(h * 0.62)], fill=RED)
    draw.ellipse([tx - 4, y + int(h * 0.60), tx + 13, y + int(h * 0.60) + 15],
                 outline=INK, fill=(240, 120, 90))
    font = sans_b(9)
    draw.text((x + int(w * 0.60), y + int(h * 0.06)), "DRAFT", font=font, fill=INK)

ILLUSTRATIONS = {
    "bridge": ill_bridge, "gulf": ill_gulf, "quad": ill_quad, "next": ill_next,
    "ebola": ill_ebola, "tents": ill_tents, "measles": ill_measles,
    "chart": ill_chart, "drone": ill_drone, "doc": ill_doc,
    "hemicycle": ill_hemicycle, "gavel": ill_gavel, "factory": ill_factory,
    "crash": ill_crash, "globe": ill_globe,
}

# ---------------------------------------------------------------- map data --
# Coarse continent outlines in (lon, lat); deliberately schematic.
LAND_POLYS = [
    # North & Central America
    [(-168, 66), (-155, 71), (-140, 70), (-128, 70), (-116, 72), (-104, 72),
     (-94, 72), (-88, 70), (-84, 68), (-80, 66), (-84, 61), (-90, 58), (-95, 58),
     (-94, 55), (-90, 52), (-86, 50), (-88, 48), (-84, 46), (-79, 43), (-76, 44),
     (-71, 44), (-66, 44), (-60, 46), (-64, 44), (-69, 42), (-73, 41), (-75, 38),
     (-76, 35), (-79, 32), (-81, 30), (-80, 26), (-82, 24), (-84, 28), (-88, 29),
     (-92, 29), (-96, 28), (-97, 25), (-97, 21), (-95, 18), (-92, 15), (-88, 14),
     (-85, 12), (-83, 9), (-79, 9), (-82, 8), (-86, 12), (-90, 14), (-94, 16),
     (-97, 17), (-101, 18), (-104, 20), (-107, 23), (-110, 24), (-112, 29),
     (-115, 32), (-119, 34), (-122, 37), (-124, 42), (-124, 47), (-127, 51),
     (-132, 55), (-138, 59), (-150, 59), (-156, 57), (-162, 60), (-166, 61)],
    # Greenland
    [(-46, 60), (-42, 64), (-40, 68), (-32, 68), (-22, 69), (-19, 73), (-24, 77),
     (-33, 79), (-46, 78), (-54, 75), (-55, 70), (-53, 65), (-51, 61)],
    # South America
    [(-79, 9), (-76, 10), (-71, 12), (-64, 11), (-59, 8), (-52, 5), (-48, 2),
     (-44, -2), (-37, -5), (-35, -8), (-38, -13), (-39, -17), (-41, -22),
     (-46, -24), (-50, -27), (-55, -31), (-58, -35), (-62, -39), (-65, -42),
     (-66, -47), (-68, -51), (-69, -54), (-71, -55), (-73, -50), (-73, -44),
     (-72, -38), (-71, -31), (-70, -24), (-70, -19), (-74, -15), (-77, -11),
     (-80, -5), (-81, -1), (-79, 3), (-77, 6)],
    # Europe mainland
    [(-9, 37), (-9, 43), (-6, 44), (-2, 45), (-1, 47), (-5, 48), (-1, 50),
     (3, 52), (7, 54), (8, 57), (12, 57), (18, 57), (21, 56), (24, 58), (26, 60),
     (30, 61), (31, 64), (28, 67), (23, 67), (19, 64), (17, 60), (18, 57),
     (21, 55), (24, 54), (28, 50), (30, 47), (33, 46), (36, 45), (33, 42),
     (29, 41), (28, 40), (30, 38), (36, 36), (31, 36), (27, 37), (23, 36),
     (20, 38), (19, 40), (16, 38), (15, 40), (13, 42), (10, 44), (7, 44),
     (3, 43), (2, 41), (0, 39), (0, 37), (-2, 37)],
    # Italy
    [(8, 44), (11, 44), (14, 42), (17, 40), (18, 40), (16, 38), (15, 39),
     (14, 41), (11, 43)],
    # Britain & Ireland
    [(-5, 50), (-3, 51), (-2, 53), (-3, 55), (-5, 57), (-4, 58), (-7, 58),
     (-8, 56), (-6, 53), (-6, 51)],
    [(-10, 52), (-8, 52), (-6, 53), (-6, 55), (-8, 55), (-10, 54)],
    # Arabia & the Levant
    [(26, 38), (30, 41), (33, 42), (36, 40), (40, 38), (44, 38), (48, 34),
     (50, 30), (49, 29), (51, 26), (54, 25), (56, 24), (59, 22), (58, 19),
     (55, 17), (51, 14), (45, 12), (43, 12), (42, 18), (41, 24), (39, 28),
     (36, 31), (34, 31), (35, 34), (33, 36), (29, 36)],
    # Persia, Central & South & South-East Asia
    [(44, 38), (48, 37), (52, 37), (54, 38), (58, 40), (64, 40), (70, 42),
     (78, 43), (86, 44), (94, 44), (102, 42), (110, 40), (118, 38), (124, 38),
     (127, 37), (130, 35), (127, 33), (122, 31), (121, 28), (118, 25),
     (114, 22), (110, 20), (109, 16), (108, 12), (107, 9), (104, 6), (101, 7),
     (99, 10), (97, 14), (94, 17), (92, 16), (90, 21), (88, 21), (86, 20),
     (83, 17), (80, 14), (78, 9), (76, 10), (74, 14), (72, 19), (70, 22),
     (67, 24), (63, 25), (59, 25), (56, 26), (53, 27), (51, 29), (50, 30),
     (48, 34)],
    # Siberia & the Russian far east
    [(31, 64), (38, 65), (45, 66), (52, 68), (60, 69), (68, 70), (76, 71),
     (84, 72), (92, 73), (100, 74), (108, 74), (116, 74), (124, 73), (132, 72),
     (140, 72), (148, 71), (156, 70), (164, 69), (172, 67), (178, 66), (179, 64),
     (172, 61), (166, 60), (161, 58), (157, 53), (152, 51), (146, 49), (142, 47),
     (141, 44), (139, 40), (136, 36), (133, 34), (130, 33), (127, 35), (124, 38),
     (118, 38), (110, 40), (102, 42), (94, 44), (86, 44), (78, 43), (70, 42),
     (64, 40), (58, 40), (54, 38), (50, 40), (46, 42), (42, 44), (38, 46),
     (35, 45), (33, 43), (31, 47), (30, 52), (29, 57), (30, 61)],
    # Africa
    [(-6, 35), (-2, 35), (0, 36), (9, 37), (11, 34), (19, 32), (25, 32),
     (30, 31), (32, 30), (33, 27), (34, 24), (35, 22), (37, 20), (38, 18),
     (40, 15), (43, 12), (48, 11), (51, 11), (48, 5), (44, 0), (41, -4),
     (40, -9), (40, -14), (39, -19), (37, -21), (35, -24), (33, -26), (31, -29),
     (27, -33), (22, -35), (19, -35), (18, -32), (16, -28), (15, -24), (14, -18),
     (13, -13), (12, -9), (12, -5), (9, -1), (9, 3), (6, 4), (0, 5), (-5, 5),
     (-8, 5), (-12, 8), (-15, 11), (-17, 13), (-17, 15), (-16, 19), (-16, 23),
     (-15, 27), (-13, 28), (-10, 31), (-6, 33)],
    # Madagascar
    [(44, -13), (47, -13), (49, -15), (50, -17), (48, -21), (47, -24), (45, -25),
     (44, -22), (43, -18), (44, -15)],
    # Australia
    [(113, -22), (113, -26), (114, -30), (115, -33), (117, -35), (121, -34),
     (126, -32), (130, -32), (132, -32), (134, -33), (136, -35), (137, -35),
     (139, -37), (141, -38), (145, -38), (147, -38), (149, -37), (150, -36),
     (152, -33), (153, -30), (153, -26), (151, -24), (149, -21), (146, -19),
     (144, -16), (142, -13), (142, -11), (141, -14), (140, -18), (139, -19),
     (137, -16), (136, -15), (136, -12), (134, -12), (132, -11), (130, -12),
     (128, -14), (125, -16), (122, -17), (119, -19), (117, -20)],
    # Papua
    [(131, -1), (135, -2), (139, -2.5), (142, -3), (142, -6), (138, -7),
     (134, -5), (131, -3.5)],
]

ISLANDS = [  # lon, lat, rx(deg), ry(deg), tilt
    (130.5, 31.5, 1.1, 2.0, -0.5), (133.0, 34.0, 1.6, 0.9, 0.3),
    (137.5, 35.2, 1.7, 0.9, 0.2), (139.5, 37.5, 1.2, 1.8, -0.3),
    (140.8, 39.8, 1.1, 1.8, -0.2), (141.8, 42.8, 1.9, 1.5, 0.4),
    (102.0, 0.0, 5.5, 1.9, -0.6), (114.0, 1.0, 4.2, 3.2, 0.0),
    (108.0, -7.0, 4.8, 1.2, 0.05), (120.0, -1.5, 2.3, 2.3, 0.0),
    (120.0, 14.0, 1.2, 2.4, 0.2), (122.5, 8.0, 1.4, 1.9, 0.0),
    (80.7, 7.8, 0.9, 1.3, 0.0), (146.8, -42.0, 1.6, 1.1, 0.0),
    (172.7, -40.5, 1.1, 2.1, 0.6), (167.5, -45.5, 1.3, 2.3, 0.6),
    (147.0, -42.5, 0.0, 0.0, 0.0),
]

def _proj(lon, lat, box):
    mx, my, mw, mh = box
    return (mx + (lon + 180) / 360 * mw, my + (80 - lat) / 142 * mh)

def draw_map(draw, box):
    mx, my, mw, mh = box
    draw.rectangle([mx, my, mx + mw, my + mh], fill=(206, 222, 233))
    for poly in LAND_POLYS:
        pts = [_proj(lon, lat, box) for lon, lat in poly]
        draw.polygon(pts, fill=LAND, outline=LAND_EDGE)
    for lon, lat, rx, ry, tilt in ISLANDS:
        if rx == 0:
            continue
        cx, cy = _proj(lon, lat, box)
        pts = []
        for i in range(14):
            ang = 2 * math.pi * i / 14
            ex, ey = rx * math.cos(ang), ry * math.sin(ang)
            rx2 = ex * math.cos(tilt) - ey * math.sin(tilt)
            ry2 = ex * math.sin(tilt) + ey * math.cos(tilt)
            pts.append(_proj(lon + rx2, lat + ry2, box))
        draw.polygon(pts, fill=LAND, outline=LAND_EDGE)
    # graticule hints
    for lon in (-120, -60, 0, 60, 120):
        gx, _ = _proj(lon, 0, box)
        draw.line([(gx, my), (gx, my + mh)], fill=(188, 206, 220), width=1)

# ----------------------------------------------------------------- layout ---
def draw_card(draw, card, number, x, y, w, h, big):
    region, kicker, headline, sub, illus, lon, lat = card
    color = REGION_COLORS[region]
    draw.rectangle([x, y, x + w, y + h], fill=(253, 251, 245), outline=CARD_LINE, width=1)
    illus_h = 64 if big else 38
    draw.rectangle([x + 1, y + 1, x + w - 1, y + 1 + illus_h], fill=(240, 244, 246))
    ILLUSTRATIONS[illus](draw, x + 1, y + 1, w - 2, illus_h)
    draw.rectangle([x, y, x + w, y + 3], fill=color)
    badge(draw, x + 13, y + 13, 10, number, color)
    tx = x + 7
    ty = y + illus_h + 6
    kfont = sans_b(11 if big else 9)
    draw.text((tx, ty), kicker, font=kfont, fill=color)
    ty += 16 if big else 12
    hfont, hlines = fit_lines(draw, headline, 21 if big else 14, w - 14,
                              2 if big else 3, serif_b, min_size=12)
    lh = 24 if big else 16
    for line in hlines:
        draw.text((tx, ty), line, font=hfont, fill=INK)
        ty += lh
    ty += 2
    # shrink the sub until it fits on two lines — never clip a sentence
    ssize = 12 if big else 10
    while ssize > 8:
        sfont = sans_r(ssize)
        slines = wrap(draw, sub, sfont, w - 14)
        if len(slines) <= 2:
            break
        ssize -= 0.5
    slh = 15 if big else 12
    for line in slines[:2]:
        draw.text((tx, ty), line, font=sfont, fill=(52, 56, 66))
        ty += slh

def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    total = len(CARDS) + len(BRIEFS)
    counts = {r: 0 for r in REGION_ORDER}
    for card in CARDS:
        counts[card[0]] += 1
    for brief in BRIEFS:
        counts[brief[1]] += 1
    assert total == 50, total

    # top strip
    f = sans_b(13)
    draw.text((14, 10), "THE WORLD'S NEWS IN ONE PICTURE", font=f, fill=RED)
    right = f"{total} STORIES \u00b7 7 REGIONS \u00b7 ALL FROM TUESDAY"
    draw.text((W - 14 - tw(draw, right, f), 10), right, font=f, fill=INK)
    draw.line([(14, 32), (W - 14, 32)], fill=INK, width=1)

    # masthead
    mfont, _ = fit_lines(draw, "Tuesday 17 November 2026", 88, W - 28, 1, serif_b,
                         min_size=40)
    label = "Tuesday 17 November 2026"
    draw.text(((W - tw(draw, label, mfont)) / 2, 38), label, font=mfont, fill=NAVY)
    draw.rectangle([14, 116, W - 14, 119], fill=INK)
    draw.line([(14, 122), (W - 14, 122)], fill=INK, width=1)

    # by-the-numbers strip
    ny = 130
    cell_w = (W - 28) / 6
    for i, (num, cap) in enumerate(NUMBERS):
        cx = 14 + i * cell_w
        nf = num_b(23)
        draw.text((cx + cell_w / 2 - tw(draw, num, nf) / 2, ny), num, font=nf, fill=NAVY)
        cf = sans_r(10)
        lines = wrap(draw, cap, cf, cell_w - 8)
        ly = ny + 27
        for line in lines[:2]:
            draw.text((cx + cell_w / 2 - tw(draw, line, cf) / 2, ly), line, font=cf,
                      fill=GREY)
            ly += 12
        if i:
            draw.line([(cx, ny + 2), (cx, ny + 44)], fill=CARD_LINE, width=1)
    draw.line([(14, 182), (W - 14, 182)], fill=CARD_LINE, width=1)

    # per-region count bar (widths proportional to the true counts)
    by = 188
    bh = 20
    inner = W - 28
    widths, used = [], 0
    for r in REGION_ORDER:
        wdt = max(58, round(inner * counts[r] / total))
        widths.append(wdt)
        used += wdt
    widths[widths.index(max(widths))] += inner - used
    bx = 14
    bf = sans_b(11)
    for r, wdt in zip(REGION_ORDER, widths):
        draw.rectangle([bx, by, bx + wdt - 2, by + bh], fill=REGION_COLORS[r])
        label = f"{r} {counts[r]}"
        draw.text((bx + (wdt - 2) / 2 - tw(draw, label, bf) / 2, by + 4), label,
                  font=bf, fill=(255, 255, 255))
        bx += wdt

    # cards: top row of 3, then two rows of 6
    margin, gap = 14, 10
    row_a_y, row_a_h = 218, 180
    cw3 = (W - 2 * margin - 2 * gap) / 3
    for i in range(3):
        draw_card(draw, CARDS[i], i + 1, margin + i * (cw3 + gap), row_a_y, cw3,
                  row_a_h, big=True)
    cw6 = (W - 2 * margin - 5 * 8) / 6
    for row, y0 in enumerate((406, 542)):
        for col in range(6):
            idx = 3 + row * 6 + col
            draw_card(draw, CARDS[idx], idx + 1, margin + col * (cw6 + 8), y0, cw6,
                      128, big=False)

    # bottom band: map (left) + briefs (right)
    band_y = 684
    hf = sans_b(13)
    draw.text((14, band_y), "WHERE IT HAPPENED", font=hf, fill=INK)
    draw.text((472, band_y), "ALSO ON TUESDAY \u2014 35 MORE STORIES IN BRIEF", font=hf,
              fill=INK)
    map_box = (14, band_y + 22, 444, 238)
    draw_map(draw, map_box)
    capf = sans_r(10)
    draw.text((14, band_y + 264), "Numbered pins: the 15 cards \u00b7 small dots: the briefs",
              font=capf, fill=GREY)
    drawn = []
    pin_offsets = {4: (-5, -4), 3: (5, 4), 6: (-6, 3), 12: (7, -3), 15: (-5, -5)}
    for i, card in enumerate(CARDS):
        px, py = _proj(card[5], card[6], map_box)
        dx, dy = pin_offsets.get(i + 1, (0, 0))
        badge(draw, px + dx, py + dy, 8, i + 1, REGION_COLORS[card[0]])
        drawn.append((px + dx, py + dy))
    for brief in BRIEFS:
        if brief[2] is None:
            continue
        px, py = _proj(brief[2], brief[3], map_box)
        if any((px - qx) ** 2 + (py - qy) ** 2 < 64 for qx, qy in drawn):
            continue
        r = 2.6
        draw.ellipse([px - r, py - r, px + r, py + r], fill=REGION_COLORS[brief[1]])
        drawn.append((px, py))

    # briefs in two columns, numbered from 16
    brief_items = list(enumerate(BRIEFS, start=len(CARDS) + 1))
    col_x = (472, 744)
    col_w = 258
    chosen = None
    for size in (11, 10.5, 10, 9.5):
        font = sans_r(int(size * 2) // 2) if size % 1 else sans_r(int(size))
        font = sans_r(size)
        units = []
        for num, brief in brief_items:
            lines = wrap(draw, brief[0], font, col_w - 20)
            units.append((num, brief, lines))
        half = (len(units) + 1) // 2
        # balance by line count
        total_lines = sum(len(u[2]) for u in units)
        acc, split = 0, half
        for i, u in enumerate(units):
            if acc >= total_lines / 2:
                split = i
                break
            acc += len(u[2])
        rows = max(sum(len(u[2]) for u in units[:split]),
                   sum(len(u[2]) for u in units[split:]))
        lh = (946 - (band_y + 24)) / rows
        if lh >= 12.2:
            chosen = (font, units, split, lh)
            break
    if chosen is None:
        font = sans_r(9.5)
        units = [(num, brief, wrap(draw, brief[0], font, col_w - 20))
                 for num, brief in brief_items]
        total_lines = sum(len(u[2]) for u in units)
        acc, split = 0, len(units) // 2
        for i, u in enumerate(units):
            if acc >= total_lines / 2:
                split = i
                break
            acc += len(u[2])
        rows = max(sum(len(u[2]) for u in units[:split]),
                   sum(len(u[2]) for u in units[split:]))
        chosen = (font, units, split, (946 - (band_y + 24)) / rows)
    font, units, split, lh = chosen
    nfont = sans_b(font.size)
    for col, group in enumerate((units[:split], units[split:])):
        yy = band_y + 24
        for num, brief, lines in group:
            color = REGION_COLORS[brief[1]]
            draw.text((col_x[col], yy), str(num), font=nfont, fill=color)
            for j, line in enumerate(lines):
                draw.text((col_x[col] + 20, yy + j * lh), line, font=font, fill=INK)
            yy += len(lines) * lh

    # DATE CHECK strip
    dy = 958
    draw.rectangle([14, dy, W - 14, dy + 26], fill=(250, 233, 226))
    dtext = ("DATE CHECK \u2014 left out on purpose, they happened before Tuesday: "
             "a Vulcan rocket lost 40 Amazon satellites (15 Nov) \u00b7 ECO \u2018Vision 2035\u2019 "
             "adopted (Monday) \u00b7 Alaska's Senate race is called on Wednesday")
    dfont, _ = fit_lines(draw, dtext, 12, W - 44, 1, sans_r, min_size=9)
    draw.text((22, dy + 6), dtext, font=dfont, fill=(120, 32, 26))

    # footer
    ff = sans_r(10)
    draw.text((14, 990),
              "Every story happened or was first reported on Tuesday 17 November 2026. "
              "Contested claims are marked as claims.",
              font=ff, fill=GREY)
    src = "Sources: Reuters \u00b7 AP \u00b7 AFP \u00b7 BBC \u00b7 Al Jazeera \u00b7 WHO \u00b7 PAHO \u00b7 UN News \u00b7 Original drawings"
    draw.text((W - 14 - tw(draw, src, ff), 1004), src, font=ff, fill=GREY)

    img.save(OUT, optimize=True)
    print("wrote", OUT, os.path.getsize(OUT), "bytes; region counts:", counts)

if __name__ == "__main__":
    main()
