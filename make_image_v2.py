# make_image_v2.py -- draws entry.png for news-image-20261117.
#
# A dense one-page broadsheet summing up the world news of Tuesday
# 17 November 2026: giant date masthead, a story-count strip, 12 numbered
# illustrated cards, a pinned world map, a date-check box, a by-the-numbers
# strip, 32 one-line briefs and a faithfulness footer. Everything is drawn
# with Pillow shapes and font-rendered text (no AI imagery), so every word
# is exactly the word intended.
#
# Story selection follows the wire consensus for the day (see STORIES.md):
# the Kerch Bridge span falling leads; contested claims are hedged in the
# headline itself; Thursday's Shenzhen summit is labelled NEXT, not news.

from PIL import Image, ImageDraw, ImageFont

W = 1024
PAPER = (247, 242, 231)
CARD_BG = (255, 253, 246)
INK = (20, 38, 74)
NAVY = (16, 32, 64)
RED = (179, 51, 44)
GREY = (90, 96, 110)
LINE = (198, 188, 164)
WHITE = (255, 255, 255)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANSB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def F(path, size):
    return ImageFont.truetype(path, size)


def fit(draw, text, path, size, max_w, min_size=9):
    """Largest font (<= size) that fits text on one line."""
    s = size
    while s > min_size:
        f = F(path, s)
        if draw.textlength(text, font=f) <= max_w:
            return f
        s -= 1
    return F(path, min_size)


def center(draw, cx, y, text, font, fill):
    w = draw.textlength(text, font=font)
    draw.text((cx - w / 2, y), text, font=font, fill=fill)


def wrap(draw, text, font, max_w):
    """Greedy word-wrap of text (newlines honoured) to lines <= max_w."""
    lines = []
    for para in text.split("\n"):
        cur = ""
        for wd in para.split():
            trial = (cur + " " + wd).strip()
            if draw.textlength(trial, font=font) <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
    return lines


# ---------------------------------------------------------------- stories
# Each card: (region tag for counting, kicker, illustration key, headline,
# sub-deck). Headlines/sub-decks carry hard figures and hedge what is
# contested, exactly as reported on the day.

CARDS = [
    ("EUROPE", "EUROPE · UKRAINE WAR", "bridge",
     "KERCH BRIDGE ROAD SPAN\nFALLS IN SECOND STRIKE",
     "Ukraine hits the Crimea link a second day; the span drops\nand the bridge is closed to all traffic."),
    ("MIDDLE EAST", "MIDDLE EAST · GULF", "drone",
     "IRAN DRONES TARGET U.S.\nRADAR IN BAHRAIN",
     "U.S. jets strike Qeshm missile sites. Iran says tankers\nhit mines in Hormuz — unverified."),
    ("ASIA", "ASIA · DIPLOMACY", "quad",
     "TRUMP'S FIRST QUAD\nSUMMIT, IN MANILA",
     "Leaders of the U.S., Japan, India and Australia sign\ncritical-minerals deals."),
    ("ASIA", "ASIA · NEXT · DIPLOMACY", "calendar",
     "NEXT: XI–TRUMP–PUTIN\nSUMMIT SET FOR THURSDAY",
     "The first three-way summit is due Thursday in Shenzhen,\non the APEC sidelines. It has not happened yet."),
    ("AFRICA", "AFRICA · HEALTH", "virus",
     "EBOLA TOPS 11,000 CASES\nIN DR CONGO",
     "About 5,400 dead in the latest count, reported Tuesday;\naid teams plead for vaccine stocks."),
    ("AMERICAS", "AMERICAS · HEALTH", "shield",
     "U.S. LOSES MEASLES\nELIMINATION STATUS",
     "PAHO strips the U.S., Mexico and Bolivia of measles-free\nstatus — a first for the U.S. since 2000."),
    ("WORLD", "WORLD · MARKETS", "chip",
     "NVIDIA REVENUE DOUBLES\nTO $115.8BN QUARTER",
     "Record quarter on AI-chip demand; the Dow still falls\n849 points on the day."),
    ("EUROPE", "EUROPE · POLITICS", "parliament",
     "SERBIA SEATS 140\nSTUDENT MPS",
     "The student movement takes 140 of 250 seats after a year\nof anti-corruption protests."),
    ("MIDDLE EAST", "MIDDLE EAST · POLITICS", "ballot",
     "KNESSET ELECTS KAHANA\nSPEAKER, 66–52",
     "Kahana wins Tuesday's ballot by 66 votes to 52 and takes\nthe speaker's chair."),
    ("ASIA", "ASIA · LABOUR", "factory",
     "DHAKA GARMENT\nWORKERS TEAR-GASSED",
     "Police fire tear gas at garment workers rallying in\nDhaka, in the industry's latest unrest."),
    ("ASIA", "ASIA · DISASTER", "plane",
     "SIBERIA PLANE CRASH\nKILLS 19",
     "An An-12 cargo plane comes down in Siberia; all 19\npeople aboard are killed."),
    ("WORLD", "WORLD · CLIMATE", "globe",
     "COP31 SPLIT OVER DRAFT\nFOSSIL-FUEL PHASE-OUT",
     "Antalya talks deadlock on the 18-page draft; it seeks\n$120bn a year for adaptation — nothing is agreed."),
]

# Briefs: (region tag, one line). All first reported on 17 November 2026.
BRIEFS = [
    ("EUROPE", "RUSSIAN STRIKE ON ZAPORIZHZHIA: TOLL 40"),
    ("EUROPE", "AID CENTRE ATTACK KILLS 26, UKRAINE"),
    ("EUROPE", "DEPARDIEU ADMITS ASSAULT, DROPS APPEAL"),
    ("EUROPE", "GERMANY THRASH NETHERLANDS 5–0"),
    ("MIDDLE EAST", "IRAN SAYS 4TH TANKER HIT HORMUZ MINE"),
    ("MIDDLE EAST", "OMAN EVACUATES 24 FROM GAS TANKER"),
    ("MIDDLE EAST", "HOUTHIS ADVANCE; YEMEN ARMY TO ADEN"),
    ("MIDDLE EAST", "ISRAELI STRIKES HIT SOUTH LEBANON"),
    ("MIDDLE EAST", "FOUR POWERS URGE OPEN GAZA CROSSINGS"),
    ("MIDDLE EAST", "GAZA RAINS FLOOD TENTS, AID SHORT"),
    ("MIDDLE EAST", "UK AGENCY: TANKER ABLAZE OFF OMAN"),
    ("MIDDLE EAST", "HOUTHIS CLAIM SAUDI PIPELINE DRONES"),
    ("MIDDLE EAST", "DUBAI AIRPORT TRAFFIC DOWN 28%"),
    ("MIDDLE EAST", "DUBAI JOB-LOSS PAYOUTS TOP AED 250M"),
    ("ASIA", "JAPAN JETS SCRAMBLE ON RUSSIAN JETS"),
    ("ASIA", "CYCLONE AKVAN HEADS FOR ANDHRA"),
    ("ASIA", "MONGOLIA PRESIDENT TO RESIGN"),
    ("ASIA", "PAKISTAN CUTS FUEL PRICES RS2/LITRE"),
    ("ASIA", "INDIA BEAT PAKISTAN 2–1, SAFF FINAL"),
    ("ASIA", "INDIA WIN U-19 ASIA CUP BY 1 WICKET"),
    ("AMERICAS", "TRUMP: 'DIRTY BOMB' REPORT UNVERIFIED"),
    ("AMERICAS", "OUTAGES HIT BANKS, AIRPORTS, TECH"),
    ("AMERICAS", "NSA SYSTEM DOWN; 'NOT CYBERATTACK'"),
    ("AMERICAS", "IRISH ACTIVIST CHARGED OVER C-130"),
    ("AMERICAS", "WAYMO PULLS ROBOTAXIS OFF FREEWAYS"),
    ("AMERICAS", "FLORIDA FLOODS AS STORM MOVES IN"),
    ("AMERICAS", "APPLE SERVICES BACK AFTER OUTAGES"),
    ("AMERICAS", "TIGER WOODS RETURNS TO GOLF"),
    ("AMERICAS", "TRUMP FLIES TO CHINA FOR SUMMIT"),
    ("WORLD", "VOYAGER 1 NEARS ONE LIGHT-DAY"),
    ("WORLD", "NAT GEO: 2026 PICTURES OF THE YEAR"),
    ("WORLD", "COP31 DRAFT TEXT RUNS 18 PAGES"),
]

NUMBERS = [
    ("11,000+", "Ebola cases, DR Congo"),
    ("$115.8bn", "Nvidia quarterly revenue"),
    ("−849", "Dow points on Tuesday"),
    ("66–52", "Knesset speaker vote"),
    ("140/250", "Serbia seats to students"),
    ("40", "dead in Zaporizhzhia strike"),
]

DATE_CHECK = [
    "Vulcan rocket's lost satellites — 15 Nov",
    "ECO 'Vision 2035' adopted — Monday",
    "Alaska Senate call — lands Wednesday",
]

# Map pins for the 12 cards: (lon, lat) in card order.
PINS = [
    (36.6, 45.3),    # 1 Kerch
    (50.6, 26.2),    # 2 Bahrain
    (121.0, 14.6),   # 3 Manila
    (114.1, 22.5),   # 4 Shenzhen
    (23.0, -2.0),    # 5 DR Congo
    (-77.0, 38.9),   # 6 Washington
    (-122.0, 37.4),  # 7 Silicon Valley
    (20.5, 44.8),    # 8 Belgrade
    (35.2, 31.8),    # 9 Jerusalem
    (90.4, 23.8),    # 10 Dhaka
    (105.0, 62.0),   # 11 Siberia
    (30.7, 36.9),    # 12 Antalya
]

REGION_ORDER = ["EUROPE", "MIDDLE EAST", "ASIA", "AFRICA", "AMERICAS", "WORLD"]
REGION_COLORS = {
    "EUROPE": (38, 84, 150),
    "MIDDLE EAST": (178, 108, 32),
    "ASIA": (30, 128, 110),
    "AFRICA": (146, 64, 140),
    "AMERICAS": (52, 130, 62),
    "WORLD": (96, 96, 120),
}


# ------------------------------------------------------------- world map
# Land spans per row of a 62 x 24 dot grid (col 0 ~ -180 deg, row 0 ~ 78 N).
LAND = {
    0: [(2, 5), (23, 26), (40, 58)],
    1: [(1, 6), (8, 19), (23, 26), (37, 60)],
    2: [(1, 6), (7, 20), (23, 25), (34, 61)],
    3: [(2, 5), (7, 19), (23, 24), (27, 27), (30, 61)],
    4: [(7, 18), (29, 29), (30, 38), (39, 61)],
    5: [(6, 17), (29, 37), (38, 58)],
    6: [(6, 17), (29, 36), (37, 42), (47, 55), (56, 57)],
    7: [(6, 16), (30, 36), (37, 41), (43, 45), (47, 53), (54, 54), (55, 56)],
    8: [(7, 11), (28, 38), (38, 42), (43, 46), (47, 52)],
    9: [(8, 10), (28, 39), (43, 45), (47, 51)],
    10: [(12, 15), (28, 39), (48, 51)],
    11: [(13, 17), (29, 38), (47, 55)],
    12: [(13, 18), (29, 37), (48, 56), (57, 59)],
    13: [(14, 18), (30, 37)],
    14: [(14, 18), (30, 36)],
    15: [(14, 17), (31, 36)],
    16: [(14, 17), (31, 35), (49, 57)],
    17: [(15, 17), (32, 35), (49, 56)],
    18: [(15, 16), (32, 34), (50, 55)],
    19: [(15, 16), (36, 36), (51, 54)],
    20: [(15, 15), (59, 60)],
    21: [(15, 15)],
}


def draw_map(d, x, y, w, h):
    """Dotted world map with the 12 numbered card pins."""
    cols, rows = 62, 24
    dx = w / cols
    dy = h / rows
    land_col = (150, 168, 196)
    for r, spans in LAND.items():
        for c0, c1 in spans:
            for c in range(c0, c1 + 1):
                cx = x + (c + 0.5) * dx
                cy = y + (r + 0.5) * dy
                d.ellipse([cx - 1.6, cy - 1.6, cx + 1.6, cy + 1.6], fill=land_col)
    fnum = F(SANSB, 10)
    # small pixel nudges so clustered pins (Crimea / Balkans / Levant /
    # Gulf) stay separately legible
    nudge = {1: (7, -9), 8: (-11, -7), 12: (-9, 5), 9: (10, 9), 2: (4, 3)}
    for i, (lon, lat) in enumerate(PINS, start=1):
        c = (lon + 180) / 5.87
        r = (78 - lat) / 5.75
        cx = x + (c + 0.5) * dx
        cy = y + (r + 0.5) * dy
        if i in nudge:
            cx += nudge[i][0]
            cy += nudge[i][1]
        rad = 8.5
        d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=RED,
                  outline=WHITE, width=1)
        t = str(i)
        tw = d.textlength(t, font=fnum)
        d.text((cx - tw / 2, cy - 6), t, font=fnum, fill=WHITE)


# ---------------------------------------------------------- illustrations
# Each takes (draw, x, y, w, h) for the card's illustration band.

def illo_bridge(d, x, y, w, h):
    d.rectangle([x, y + h - 7, x + w, y + h], fill=(64, 110, 160))
    deck = y + h - 16
    d.rectangle([x + 8, deck, x + w * 0.40, deck + 4], fill=INK)
    d.rectangle([x + w * 0.62, deck, x + w - 8, deck + 4], fill=INK)
    for px in (x + 30, x + w - 34):
        d.rectangle([px, y + 3, px + 5, deck], fill=INK)
        d.line([px + 2, y + 5, px - 16, deck], fill=GREY, width=1)
        d.line([px + 2, y + 5, px + 20, deck], fill=GREY, width=1)
    # fallen span, tilted down into the water
    d.polygon([(x + w * 0.41, deck + 1), (x + w * 0.615, deck + 11),
               (x + w * 0.615, deck + 17), (x + w * 0.41, deck + 7)], fill=RED)


def illo_drone(d, x, y, w, h):
    cx, cy = x + w * 0.34, y + h * 0.52
    for sx, sy in ((-26, -9), (26, -9), (-26, 9), (26, 9)):
        d.line([cx, cy, cx + sx, cy + sy], fill=INK, width=2)
        d.ellipse([cx + sx - 8, cy + sy - 3, cx + sx + 8, cy + sy + 3],
                  outline=INK, width=2)
    d.ellipse([cx - 8, cy - 6, cx + 8, cy + 6], fill=RED)
    for r in (8, 15, 22):
        d.arc([x + w * 0.68 - r, y + h - 6 - r, x + w * 0.68 + r,
               y + h - 6 + r], start=200, end=320, fill=(178, 108, 32), width=2)
    d.polygon([(x + w * 0.68, y + h - 4), (x + w * 0.60, y + h),
               (x + w * 0.76, y + h)], fill=INK)


def illo_quad(d, x, y, w, h):
    codes = [("US", (58, 84, 160)), ("JP", (196, 60, 60)),
             ("IN", (220, 130, 40)), ("AU", (30, 110, 70))]
    fw = w / 4
    f = F(SANSB, 11)
    for i, (code, col) in enumerate(codes):
        px = x + i * fw + fw * 0.18
        d.line([px, y + 2, px, y + h - 2], fill=INK, width=2)
        d.rectangle([px, y + 3, px + fw * 0.62, y + 15], fill=col)
        tw = d.textlength(code, font=f)
        d.text((px + (fw * 0.62 - tw) / 2, y + 3), code, font=f, fill=WHITE)


def illo_calendar(d, x, y, w, h):
    pw, ph = w * 0.30, h - 2
    px, py = x + (w - pw) / 2, y + 1
    d.rectangle([px, py, px + pw, py + ph], outline=INK, width=2, fill=WHITE)
    d.rectangle([px, py, px + pw, py + 10], fill=RED)
    fn = F(SANSB, 8)
    t0 = "NOV"
    tw0 = d.textlength(t0, font=fn)
    d.text((px + (pw - tw0) / 2, py + 1), t0, font=fn, fill=WHITE)
    f1 = F(SANSB, 13)
    t = "THU 19"
    tw = d.textlength(t, font=f1)
    d.text((px + (pw - tw) / 2, py + 13), t, font=f1, fill=INK)
    # three small flags either side: the three capitals coming to Shenzhen
    for i, col in enumerate([(58, 84, 160), (196, 60, 60), (30, 128, 110)]):
        for base in (x + w * 0.10 + i * w * 0.075, x + w * 0.90 - i * w * 0.075):
            d.line([base, y + 8, base, y + h - 4], fill=INK, width=1)
            d.rectangle([base, y + 8, base + 13, y + 15], fill=col)


def illo_virus(d, x, y, w, h):
    import math
    cx, cy = x + w * 0.42, y + h / 2
    r = h * 0.30
    for k in range(8):
        a = k * math.pi / 4
        x2 = cx + (r + 6) * math.cos(a)
        y2 = cy + (r + 6) * math.sin(a)
        d.line([cx, cy, x2, y2], fill=(146, 64, 140), width=2)
        d.ellipse([x2 - 3, y2 - 3, x2 + 3, y2 + 3], fill=(146, 64, 140))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(146, 64, 140))
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=WHITE)
    # red-cross badge
    bx, by = x + w * 0.70, cy
    d.ellipse([bx - 10, by - 10, bx + 10, by + 10], fill=WHITE,
              outline=RED, width=2)
    d.rectangle([bx - 2, by - 6, bx + 2, by + 6], fill=RED)
    d.rectangle([bx - 6, by - 2, bx + 6, by + 2], fill=RED)


def illo_shield(d, x, y, w, h):
    cx = x + w * 0.5
    top, bot = y + 1, y + h - 1
    hw = 24
    d.polygon([(cx - hw, top), (cx + hw, top), (cx + hw, top + 15),
               (cx, bot), (cx - hw, top + 15)], outline=INK, width=2)
    d.line([cx - 7, top + 5, cx + 3, top + 14, cx - 3, top + 20,
            cx + 5, top + 26], fill=RED, width=2)
    f = F(SANSB, 11)
    d.text((x + w * 0.10, y + h * 0.34), "US", font=f, fill=GREY)
    d.text((x + w * 0.82, y + h * 0.34), "MX", font=f, fill=GREY)
    d.text((x + w * 0.10, y + h * 0.62), "BO", font=f, fill=GREY)
    d.text((x + w * 0.82, y + h * 0.62), "PAHO", font=f, fill=GREY)


def illo_chip(d, x, y, w, h):
    s = h - 8
    px, py = x + w / 2 - s / 2, y + 4
    for i in range(3):
        off = 8 + i * (s - 16) / 2
        d.line([px - 6, py + off, px, py + off], fill=INK, width=2)
        d.line([px + s, py + off, px + s + 6, py + off], fill=INK, width=2)
        d.line([px + off, py - 5, px + off, py], fill=INK, width=2)
        d.line([px + off, py + s, px + off, py + s + 5], fill=INK, width=2)
    d.rectangle([px, py, px + s, py + s], fill=(30, 128, 110))
    f = F(SANSB, 13)
    t = "AI"
    tw = d.textlength(t, font=f)
    d.text((px + (s - tw) / 2, py + s / 2 - 8), t, font=f, fill=WHITE)


def illo_parliament(d, x, y, w, h):
    base = y + h - 3
    d.polygon([(x + w * 0.14, y + 9), (x + w * 0.52, y + 9),
               (x + w * 0.33, y + 1)], fill=INK)
    for i in range(4):
        px = x + w * (0.17 + 0.09 * i)
        d.rectangle([px, y + 11, px + 5, base - 4], fill=INK)
    d.rectangle([x + w * 0.13, base - 4, x + w * 0.53, base], fill=INK)
    f = F(SANSB, 17)
    d.text((x + w * 0.60, y + h * 0.22), "140", font=f, fill=RED)
    f2 = F(SANS, 9)
    d.text((x + w * 0.60, y + h * 0.62), "of 250 seats", font=f2, fill=GREY)


def illo_ballot(d, x, y, w, h):
    bx, by = x + w * 0.22, y + h * 0.52
    bw, bh = w * 0.34, h * 0.42
    d.rectangle([bx, by, bx + bw, by + bh], outline=INK, width=2)
    d.rectangle([bx + bw * 0.2, by - 2, bx + bw * 0.8, by + 1], fill=INK)
    d.rectangle([bx + bw * 0.28, by - 13, bx + bw * 0.72, by - 2],
                outline=INK, width=1, fill=WHITE)
    f = F(SANSB, 15)
    d.text((x + w * 0.62, y + h * 0.28), "66–52", font=f, fill=RED)


def illo_factory(d, x, y, w, h):
    base = y + h - 4
    d.rectangle([x + w * 0.30, y + 12, x + w * 0.78, base], fill=(110, 120, 140))
    for cx0 in (x + w * 0.36, x + w * 0.62):
        d.rectangle([cx0, y + 2, cx0 + 8, y + 12], fill=INK)
        d.ellipse([cx0 + 1, y - 2, cx0 + 12, y + 5], fill=(200, 200, 205))
    for i in range(6):
        wx = x + w * (0.34 + 0.07 * i)
        d.rectangle([wx, y + 18, wx + 6, y + 24], fill=(250, 220, 130))
    # the crowd: a row of heads along the front of the factory
    for i in range(13):
        cx0 = x + w * (0.27 + 0.042 * i)
        d.ellipse([cx0, base - 6, cx0 + 6, base], fill=RED)
    d.line([x + w * 0.24, base, x + w * 0.84, base], fill=INK, width=1)


def illo_plane(d, x, y, w, h):
    # crash-site scene (a plane silhouette will not read in a 10:1 band):
    # Siberian peaks, a dashed descent path, impact star, smoke plume.
    base = y + h - 3
    d.line([x + 4, base, x + w - 4, base], fill=INK, width=1)
    for x0, x1, top in ((0.04, 0.34, 0.18), (0.24, 0.52, 0.34)):
        d.polygon([(x + w * x0, base), (x + w * (x0 + x1) / 2, y + h * top),
                   (x + w * x1, base)], fill=(110, 125, 150))
        peak = x + w * (x0 + x1) / 2
        d.polygon([(peak - 5, y + h * top + 6), (peak, y + h * top),
                   (peak + 5, y + h * top + 6)], fill=WHITE)
    # dashed descent path
    import math
    for t in (0.08, 0.24, 0.40, 0.56, 0.72, 0.86):
        sx = x + w * (0.52 + 0.20 * t)
        sy = y + h * (0.10 + 0.62 * t * t)
        d.ellipse([sx - 1.6, sy - 1.6, sx + 1.6, sy + 1.6], fill=GREY)
    # impact star
    ix, iy = x + w * 0.735, base - 3
    for a in (0, 45, 90, 135):
        r = math.radians(a)
        d.line([ix - 6 * math.cos(r), iy - 6 * math.sin(r),
                ix + 6 * math.cos(r), iy + 6 * math.sin(r)], fill=RED, width=2)
    # smoke plume drifting up and right
    for fx, fy, r in ((0.755, 0.58, 3.5), (0.79, 0.42, 5), (0.84, 0.26, 6.5),
                      (0.90, 0.16, 8)):
        cx, cy = x + w * fx, y + h * fy
        d.ellipse([cx - r, cy - r * 0.7, cx + r, cy + r * 0.7],
                  fill=(168, 170, 176))


def illo_globe(d, x, y, w, h):
    cx, cy = x + w * 0.36, y + h / 2
    r = h * 0.46
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(90, 140, 190))
    d.polygon([(cx - 12, cy - 8), (cx - 4, cy - 12), (cx - 2, cy - 4),
               (cx - 8, cy + 1)], fill=(90, 170, 90))
    d.polygon([(cx + 3, cy - 10), (cx + 12, cy - 7), (cx + 10, cy + 1),
               (cx + 4, cy + 2)], fill=(90, 170, 90))
    d.polygon([(cx - 3, cy + 5), (cx + 4, cy + 6), (cx + 1, cy + 13)],
              fill=(90, 170, 90))
    tx = x + w * 0.66
    d.rectangle([tx, y + 4, tx + 7, y + h - 6], outline=INK, width=2)
    d.rectangle([tx + 1, y + h * 0.45, tx + 6, y + h - 7], fill=RED)
    d.ellipse([tx - 3, y + h - 12, tx + 10, y + h + 1], outline=INK, width=2)
    d.ellipse([tx - 1, y + h - 10, tx + 8, y + h - 1], fill=RED)


ILLOS = {
    "bridge": illo_bridge, "drone": illo_drone, "quad": illo_quad,
    "calendar": illo_calendar, "virus": illo_virus, "shield": illo_shield,
    "chip": illo_chip, "parliament": illo_parliament, "ballot": illo_ballot,
    "factory": illo_factory, "plane": illo_plane, "globe": illo_globe,
}


# ---------------------------------------------------------------- layout

def draw_card(d, x, y, w, h, num, card):
    region, kicker, illo, head, sub = card
    d.rectangle([x, y, x + w, y + h], fill=CARD_BG, outline=LINE, width=1)
    # number badge
    cx, cy, r = x + 17, y + 15, 11
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=NAVY)
    fnum = F(SANSB, 13)
    t = str(num)
    tw = d.textlength(t, font=fnum)
    d.text((cx - tw / 2, cy - 8), t, font=fnum, fill=WHITE)
    # kicker
    fk = fit(d, kicker, SANSB, 13, w - 44, 10)
    d.text((x + 34, y + 7), kicker, font=fk, fill=REGION_COLORS[region])
    # illustration band
    bx, by, bw, bh = x + 8, y + 27, w - 16, 32
    d.rectangle([bx, by, bx + bw, by + bh], fill=(238, 240, 244))
    ILLOS[illo](d, bx, by, bw, bh)
    # headline (hand-set two lines, shrunk if a line ever runs wide)
    for i, line in enumerate(head.split("\n")):
        fh = fit(d, line, SANSB, 16, w - 20, 11)
        d.text((x + 10, y + 63 + i * 19), line, font=fh, fill=INK)
    # sub-deck: auto-wrapped to the card, shrunk until it fits two lines
    size = 11
    while size > 8:
        fs = F(SANS, size)
        lines = wrap(d, sub.replace("\n", " "), fs, w - 20)
        if len(lines) <= 2:
            break
        size -= 0.5
    for i, line in enumerate(lines[:2]):
        d.text((x + 10, y + 102 + i * 12), line, font=fs, fill=(40, 44, 54))


def main():
    img = Image.new("RGB", (W, W), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead
    center(d, W / 2, 8, "THE WORLD IN ONE IMAGE", F(SANSB, 15), GREY)
    fdate = fit(d, "TUESDAY 17 NOVEMBER 2026", SERIF, 68, 984, 30)
    center(d, W / 2, 28, "TUESDAY 17 NOVEMBER 2026", fdate, INK)
    d.rectangle([0, 100, W, 103], fill=RED)
    d.rectangle([0, 105, W, 106], fill=INK)

    # ---- story-count strip (counted from the data, so it cannot lie)
    counts = {}
    for region, *_ in CARDS:
        counts[region] = counts.get(region, 0) + 1
    for region, _line in BRIEFS:
        counts[region] = counts.get(region, 0) + 1
    total = sum(counts.values())
    parts = " · ".join(f"{r} {counts[r]}" for r in REGION_ORDER)
    strip = f"{total} STORIES · {parts} · ALL FROM TUESDAY"
    d.rectangle([0, 110, W, 138], fill=NAVY)
    fs = fit(d, strip, SANSB, 15, 1000, 10)
    center(d, W / 2, 117, strip, fs, WHITE)

    # ---- cards, 3 x 4
    mx, gap, cw, chh = 16, 10, 324, 128
    y0 = 148
    for i, card in enumerate(CARDS):
        cx = mx + (i % 3) * (cw + gap)
        cy = y0 + (i // 3) * (chh + 9)
        draw_card(d, cx, cy, cw, chh, i + 1, card)

    # ---- middle band: map | date check | by the numbers
    by = 696
    bh = 142
    d.rectangle([16, by, 500, by + bh], fill=CARD_BG, outline=LINE, width=1)
    d.text((26, by + 6), "WHERE IT HAPPENED — THE 12 CARDS, PINNED",
           font=F(SANSB, 13), fill=INK)
    draw_map(d, 28, by + 30, 460, 102)

    d.rectangle([510, by, 752, by + bh], fill=CARD_BG, outline=LINE, width=1)
    d.text((520, by + 6), "DATE CHECK — LEFT OUT", font=F(SANSB, 13), fill=RED)
    d.text((520, by + 26), "Tempting, but not Tuesday's news:",
           font=F(SANS, 10.5), fill=GREY)
    fy = by + 44
    for item in DATE_CHECK:
        f = F(SANS, 11)
        words, lines, cur = item.split(), [], ""
        for wd in words:
            trial = (cur + " " + wd).strip()
            if d.textlength(trial, font=f) <= 218:
                cur = trial
            else:
                lines.append(cur)
                cur = wd
        lines.append(cur)
        for j, line in enumerate(lines):
            prefix = "✗ " if j == 0 else "   "
            d.text((520, fy + j * 13), prefix + line, font=f, fill=(40, 44, 54))
        fy += len(lines) * 13 + 5

    d.rectangle([762, by, 1008, by + bh], fill=CARD_BG, outline=LINE, width=1)
    d.text((772, by + 6), "TUESDAY BY THE NUMBERS", font=F(SANSB, 13),
           fill=INK)
    ny = by + 32
    for fig, label in NUMBERS:
        ff = F(SANSB, 16)
        d.text((772, ny), fig, font=ff, fill=RED)
        fw = d.textlength(fig, font=ff)
        fl = fit(d, label, SANS, 10.5, 1008 - 772 - fw - 14, 8)
        d.text((772 + fw + 7, ny + 4), label, font=fl, fill=(40, 44, 54))
        ny += 17.5

    # ---- briefs, 4 columns x 8
    hy = 848
    d.text((16, hy), f"ALSO ON TUESDAY — {len(BRIEFS)} MORE STORIES IN BRIEF",
           font=F(SANSB, 15), fill=INK)
    d.rectangle([16, hy + 20, 1008, hy + 21], fill=RED)
    colx = [16, 266, 516, 766]
    colw = 240
    for i, (_region, line) in enumerate(BRIEFS):
        cx = colx[i // 8]
        cy = hy + 28 + (i % 8) * 12.6
        f = fit(d, "› " + line, SANS, 11, colw, 9)
        d.text((cx, cy), "› " + line, font=f, fill=(40, 44, 54))

    # ---- footer
    d.rectangle([16, 980, 1008, 981], fill=LINE)
    center(d, W / 2, 988,
           "Every story happened or was first reported on Tuesday 17 November "
           "2026. Disputed claims are attributed in the text.",
           F(SANS, 11.5), INK)
    center(d, W / 2, 1004,
           "Sources: Reuters · AP · AFP · BBC · Al Jazeera · UN News · PAHO · "
           "Dawn — Original drawings; no photographs.",
           F(SANS, 11), GREY)

    import hashlib
    import os
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out)
    data = open(out, "rb").read()
    print(f"wrote {out}: {len(data)} bytes, sha256 {hashlib.sha256(data).hexdigest()}")


if __name__ == "__main__":
    main()
