#!/usr/bin/env python3
"""Draw entry.png: one image that sums up the world news of Tuesday 17 November 2026.

The picture is a broadsheet front page. A masthead names the day, a wide hero
panel carries the day's biggest story (the U.S.-Iran war in the Strait of
Hormuz), and five smaller panels cover the rest of the day across regions and
beats: the Shenzhen Xi-Trump-Putin summit, Ukraine's Kerch Bridge strike,
Gaza's aid and shelter crisis, the COP31 draft deal in Antalya, and the
Nvidia-led market fall with tightened U.S. AI-chip rules. A footer line adds
two more of the day's stories (U.S. measles status, the U-19 Asia Cup final).

Everything is drawn with Pillow primitives -- flat shapes, no photographs --
so the text stays crisp and the scenes read at thumbnail size. The output is
deterministic: entry.png in this repository is exactly what this script draws.

Run:  python3 make_image.py [output-path]
"""

import sys

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- palette
PAPER = (247, 242, 231)
INK = (20, 33, 61)
ACCENT = (176, 42, 32)
MUTED = (96, 104, 122)
PANEL_LINE = (20, 33, 61)

SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

W = 1024
MARGIN = 28
CW = W - 2 * MARGIN  # content width


def font(path, size):
    return ImageFont.truetype(path, size)


def centered(draw, cx, y, text, fnt, fill):
    w = draw.textlength(text, font=fnt)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)
    return w


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def panel(draw, box, fill):
    draw.rounded_rectangle(box, radius=10, fill=fill, outline=PANEL_LINE, width=3)


def label_bar(draw, box, text, size=27):
    """Dark bar across the bottom of a panel with the story's short label."""
    x0, y0, x1, y1 = box
    fnt = font(SANS_BOLD, size)
    lines = wrap(draw, text, fnt, (x1 - x0) - 24)
    bar_h = 16 + len(lines) * (size + 6)
    draw.rounded_rectangle([x0, y1 - bar_h, x1, y1], radius=10, fill=INK)
    draw.rectangle([x0, y1 - bar_h, x1, y1 - bar_h + 12], fill=INK)
    ty = y1 - bar_h + 8
    for line in lines:
        centered(draw, (x0 + x1) / 2, ty, line, fnt, (250, 248, 240))
        ty += size + 6
    return bar_h


# ---------------------------------------------------------------- scenes
def scene_hormuz(draw, box):
    """Hero: a burning tanker in the Strait of Hormuz, headlands either side."""
    x0, y0, x1, y1 = box
    sky = (250, 214, 165)
    sea = (38, 92, 118)
    draw.rectangle([x0, y0, x1, y1], fill=sky)
    draw.rectangle([x0, y0 + 150, x1, y1], fill=sea)
    # low sun
    draw.ellipse([x0 + 620, y0 + 26, x0 + 700, y0 + 106], fill=(238, 127, 44))
    # headlands: Iran side left, Oman side right
    draw.polygon([(x0, y0 + 96), (x0 + 190, y0 + 96), (x0 + 120, y0 + 168), (x0, y0 + 190)], fill=(94, 74, 58))
    draw.polygon([(x1, y0 + 104), (x1 - 170, y0 + 104), (x1 - 96, y0 + 172), (x1, y0 + 196)], fill=(94, 74, 58))
    # distant second tanker, small fire
    draw.polygon([(x0 + 690, y0 + 158), (x0 + 806, y0 + 158), (x0 + 788, y0 + 176), (x0 + 704, y0 + 176)], fill=(52, 58, 66))
    draw.rectangle([x0 + 716, y0 + 146, x0 + 742, y0 + 158], fill=(52, 58, 66))
    flame(draw, x0 + 762, y0 + 158, 15, 30)
    # main tanker
    hull_y = y0 + 196
    draw.polygon([(x0 + 236, hull_y), (x0 + 640, hull_y), (x0 + 606, hull_y + 38), (x0 + 272, hull_y + 38)], fill=(30, 32, 38))
    draw.rectangle([x0 + 236, hull_y + 30, x0 + 620, hull_y + 38], fill=(150, 44, 34))
    draw.rectangle([x0 + 560, hull_y - 40, x0 + 612, hull_y], fill=(225, 226, 228))  # superstructure
    draw.rectangle([x0 + 574, hull_y - 58, x0 + 598, hull_y - 40], fill=(52, 58, 66))
    for i, c in enumerate([(70, 110, 150), (178, 120, 52), (84, 128, 92), (150, 70, 60)]):
        draw.rectangle([x0 + 292 + i * 62, hull_y - 26, x0 + 344 + i * 62, hull_y], fill=c)
    # the fire amidships and its smoke, drifting up and to the left
    flame(draw, x0 + 452, hull_y - 24, 46, 96)
    flame(draw, x0 + 500, hull_y - 24, 30, 62)
    for i in range(7):
        cx = x0 + 446 - i * 13
        cy = hull_y - 108 - i * 11
        r = 20 + i * 4
        draw.ellipse([cx - r, cy - r * 0.62, cx + r, cy + r * 0.62], fill=(105, 105, 110))
    # a small drone at the end of its dotted approach path
    for t in range(0, 9):
        px = x0 + 110 + t * 20
        py = y0 + 44 + t * 3
        draw.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(70, 70, 76))
    dx, dy = x0 + 292, y0 + 76
    draw.line([dx - 13, dy - 9, dx + 13, dy + 9], fill=(52, 54, 60), width=4)
    draw.line([dx - 13, dy + 9, dx + 13, dy - 9], fill=(52, 54, 60), width=4)
    draw.rectangle([dx - 6, dy - 4, dx + 6, dy + 4], fill=(52, 54, 60))


def flame(draw, cx, base_y, w, h):
    draw.polygon([(cx - w, base_y), (cx + w, base_y), (cx + w * 0.3, base_y - h * 0.62), (cx, base_y - h), (cx - w * 0.34, base_y - h * 0.55)], fill=(232, 106, 32))
    draw.polygon([(cx - w * 0.55, base_y), (cx + w * 0.55, base_y), (cx + w * 0.14, base_y - h * 0.42), (cx, base_y - h * 0.66), (cx - w * 0.18, base_y - h * 0.4)], fill=(246, 178, 44))
    draw.polygon([(cx - w * 0.24, base_y), (cx + w * 0.24, base_y), (cx, base_y - h * 0.34)], fill=(252, 232, 160))


def flag_cn(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(206, 44, 36))
    for dx, dy, r in [(10, 8, 5), (24, 5, 3), (28, 12, 3), (28, 20, 3), (24, 27, 3)]:
        draw.ellipse([x + dx - r, y + dy - r, x + dx + r, y + dy + r], fill=(246, 205, 60))


def flag_us(draw, x, y, w, h):
    stripe = h / 7
    for i in range(7):
        draw.rectangle([x, y + i * stripe, x + w, y + (i + 1) * stripe], fill=(178, 44, 52) if i % 2 == 0 else (244, 244, 244))
    draw.rectangle([x, y, x + w * 0.44, y + stripe * 4], fill=(44, 58, 120))
    for r in range(3):
        for c in range(4):
            cx, cy = x + 6 + c * 11, y + 5 + r * 9
            draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(255, 255, 255))


def flag_ru(draw, x, y, w, h):
    third = h / 3
    draw.rectangle([x, y, x + w, y + third], fill=(244, 244, 244))
    draw.rectangle([x, y + third, x + w, y + 2 * third], fill=(46, 84, 160))
    draw.rectangle([x, y + 2 * third, x + w, y + h], fill=(196, 44, 40))


def scene_shenzhen(draw, box):
    """Three flags over a summit table, Shenzhen skyline behind."""
    x0, y0, x1, y1 = box
    draw.rectangle([x0, y0, x1, y1], fill=(196, 220, 235))
    # skyline silhouettes
    towers = [(6, 66, 30), (44, 44, 24), (76, 84, 20), (330, 58, 26), (366, 38, 22), (398, 70, 30), (434, 48, 24)]
    for dx, h, w in towers:
        draw.rectangle([x0 + dx, y1 - 96 - h, x0 + dx + w, y1 - 96], fill=(120, 148, 168))
    draw.polygon([(x0 + 236, y1 - 96 - 118), (x0 + 252, y1 - 96), (x0 + 220, y1 - 96)], fill=(104, 134, 156))
    # flag poles and flags
    mid = (x0 + x1) / 2
    for i, draw_flag in enumerate([flag_cn, flag_us, flag_ru]):
        px = int(mid + (i - 1) * 118)
        draw.line([px, y0 + 26, px, y1 - 104], fill=(60, 64, 72), width=5)
        draw_flag(draw, px + 4, y0 + 26, 84, 52)
    # summit table and three seated figures, kept clear of the label bar
    draw.pieslice([mid - 150, y1 - 158, mid + 150, y1 - 62], 0, 180, fill=(112, 78, 48))
    draw.rectangle([mid - 150, y1 - 108, mid + 150, y1 - 92], fill=(112, 78, 48))
    for i in range(3):
        cx = int(mid + (i - 1) * 96)
        draw.ellipse([cx - 17, y1 - 152, cx + 17, y1 - 118], fill=(38, 42, 54))
        draw.pieslice([cx - 30, y1 - 128, cx + 30, y1 - 76], 180, 360, fill=(38, 42, 54))


def scene_bridge(draw, box):
    """The Kerch Bridge with a span down, smoke over the strait."""
    x0, y0, x1, y1 = box
    draw.rectangle([x0, y0, x1, y1], fill=(178, 192, 204))
    draw.rectangle([x0, y1 - 74, x1, y1], fill=(58, 96, 128))
    deck_y = y0 + 108
    # pylons
    draw.rectangle([x0 + 66, deck_y - 64, x0 + 80, y1 - 74], fill=(88, 94, 104))
    draw.rectangle([x1 - 92, deck_y - 64, x1 - 78, y1 - 74], fill=(88, 94, 104))
    draw.line([x0 + 73, deck_y - 64, x0 + 190, deck_y], fill=(88, 94, 104), width=3)
    draw.line([x1 - 85, deck_y - 64, x1 - 196, deck_y], fill=(88, 94, 104), width=3)
    # standing deck, then the gap, then the fallen span
    draw.rectangle([x0 + 8, deck_y, x0 + 196, deck_y + 12], fill=(70, 76, 86))
    draw.rectangle([x1 - 204, deck_y, x1 - 8, deck_y + 12], fill=(70, 76, 86))
    draw.polygon([(x0 + 210, deck_y + 4), (x0 + 268, deck_y + 44), (x0 + 258, deck_y + 56), (x0 + 202, deck_y + 16)], fill=(70, 76, 86))
    # splash and smoke
    for dx in (216, 238, 258):
        draw.arc([x0 + dx - 14, y1 - 92, x0 + dx + 14, y1 - 58], 180, 360, fill=(230, 238, 244), width=3)
    for i in range(5):
        cx, cy, r = x0 + 226 + i * 10, deck_y - 26 - i * 13, 17 + i * 5
        draw.ellipse([cx - r, cy - r * 0.62, cx + r, cy + r * 0.62], fill=(110, 112, 118))
    flame(draw, x0 + 214, deck_y + 2, 17, 40)


def scene_gaza(draw, box):
    """Tents in the rain and an aid truck: the shelter and aid crisis."""
    x0, y0, x1, y1 = box
    draw.rectangle([x0, y0, x1, y1], fill=(168, 182, 194))
    draw.rectangle([x0, y1 - 56, x1, y1], fill=(122, 110, 92))
    # rain
    for i in range(26):
        rx = x0 + 12 + (i * 37) % (box[2] - box[0] - 20)
        ry = y0 + 8 + (i * 23) % 74
        draw.line([rx, ry, rx - 6, ry + 16], fill=(90, 120, 150), width=3)
    # tents: wide, low triangles with guy ropes
    for i, tx in enumerate([10, 92, 174]):
        base = y1 - 62
        apex = (x0 + tx + 38, y0 + 66)
        draw.polygon([(x0 + tx, base), apex, (x0 + tx + 76, base)], fill=(208, 198, 170) if i != 1 else (190, 180, 158), outline=(96, 88, 70))
        draw.polygon([(x0 + tx + 29, base), (x0 + tx + 38, y0 + 90), (x0 + tx + 47, base)], fill=(90, 82, 66))
        draw.line([(x0 + tx + 2, base), apex], fill=(96, 88, 70), width=2)
        draw.line([(x0 + tx + 74, base), apex], fill=(96, 88, 70), width=2)
    # puddles
    for dx in (30, 120, 210):
        draw.ellipse([x0 + dx, y1 - 46, x0 + dx + 52, y1 - 34], fill=(140, 160, 178))
    # aid truck, lifted clear of the label bar
    tx, ty = x1 - 118, y1 - 122
    draw.rectangle([tx, ty, tx + 74, ty + 48], fill=(244, 244, 242), outline=(70, 76, 86), width=2)
    draw.polygon([(tx + 74, ty + 14), (tx + 96, ty + 26), (tx + 96, ty + 48), (tx + 74, ty + 48)], fill=(210, 214, 218), outline=(70, 76, 86))
    fnt = font(SANS_BOLD, 21)
    draw.text((tx + 12, ty + 12), "AID", font=fnt, fill=(176, 42, 32))
    for wx in (tx + 16, tx + 78):
        draw.ellipse([wx - 10, ty + 42, wx + 10, ty + 62], fill=(40, 42, 48))


def scene_cop(draw, box):
    """COP31: a warming globe, a leaf, a thermometer."""
    x0, y0, x1, y1 = box
    draw.rectangle([x0, y0, x1, y1], fill=(186, 224, 196))
    cx, cy, r = x0 + 108, y0 + 92, 66
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(66, 122, 178))
    for pts in [[(cx - 44, cy - 30), (cx - 12, cy - 40), (cx - 4, cy - 14), (cx - 30, cy - 2), (cx - 48, cy - 12)],
                [(cx + 8, cy + 6), (cx + 40, cy - 2), (cx + 48, cy + 22), (cx + 22, cy + 36), (cx + 6, cy + 24)],
                [(cx - 20, cy + 30), (cx + 2, cy + 26), (cx + 4, cy + 46), (cx - 16, cy + 50)]]:
        draw.polygon(pts, fill=(84, 148, 84))
    # leaf: a pointed oval with a vein
    leaf = [(cx + 30, cy - 26), (cx + 44, cy - 56), (cx + 78, cy - 64), (cx + 88, cy - 34), (cx + 62, cy - 8), (cx + 36, cy - 12)]
    draw.polygon(leaf, fill=(52, 140, 66))
    draw.line([cx + 36, cy - 14, cx + 82, cy - 58], fill=(34, 104, 48), width=4)
    # thermometer
    tx = x1 - 56
    draw.rounded_rectangle([tx, y0 + 22, tx + 20, y1 - 66], radius=9, fill=(244, 244, 242), outline=(90, 96, 108), width=2)
    draw.rectangle([tx + 6, y0 + 44, tx + 14, y1 - 76], fill=(206, 60, 44))
    draw.ellipse([tx - 6, y1 - 92, tx + 26, y1 - 60], fill=(206, 60, 44))


def scene_markets(draw, box):
    """An AI chip and a falling market line."""
    x0, y0, x1, y1 = box
    draw.rectangle([x0, y0, x1, y1], fill=(26, 34, 54))
    # grid
    for gx in range(x0 + 24, x1 - 10, 34):
        draw.line([gx, y0 + 12, gx, y1 - 14], fill=(52, 66, 92), width=1)
    for gy in range(y0 + 16, y1 - 10, 30):
        draw.line([x0 + 12, gy, x1 - 12, gy], fill=(52, 66, 92), width=1)
    # chip, kept clear of the label bar
    chx, chy, s = x0 + 34, y0 + 28, 88
    for i in range(4):
        draw.line([chx + 14 + i * 22, chy - 12, chx + 14 + i * 22, chy], fill=(170, 178, 190), width=5)
        draw.line([chx + 14 + i * 22, chy + s, chx + 14 + i * 22, chy + s + 12], fill=(170, 178, 190), width=5)
        draw.line([chx - 12, chy + 14 + i * 22, chx, chy + 14 + i * 22], fill=(170, 178, 190), width=5)
        draw.line([chx + s, chy + 14 + i * 22, chx + s + 12, chy + 14 + i * 22], fill=(170, 178, 190), width=5)
    draw.rounded_rectangle([chx, chy, chx + s, chy + s], radius=8, fill=(38, 120, 92), outline=(190, 220, 200), width=3)
    fnt = font(SANS_BOLD, 40)
    tw = draw.textlength("AI", font=fnt)
    draw.text((chx + (s - tw) / 2, chy + 24), "AI", font=fnt, fill=(240, 250, 244))
    # falling line with arrowhead
    pts = [(x0 + 146, y0 + 30), (x0 + 192, y0 + 52), (x0 + 220, y0 + 42), (x0 + 256, y0 + 80), (x1 - 28, y0 + 108)]
    draw.line(pts, fill=(232, 84, 60), width=6)
    draw.polygon([(x1 - 28, y0 + 108), (x1 - 54, y0 + 102), (x1 - 36, y0 + 82)], fill=(232, 84, 60))


# ---------------------------------------------------------------- page
def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    img = Image.new("RGB", (W, W), PAPER)
    draw = ImageDraw.Draw(img)

    # masthead
    # masthead: shrink the date until it fits the content width
    date_fnt = font(SERIF_BOLD, 66)
    while draw.textlength("TUESDAY 17 NOVEMBER 2026", font=date_fnt) > CW and date_fnt.size > 30:
        date_fnt = font(SERIF_BOLD, date_fnt.size - 2)
    centered(draw, W / 2, 22, "T H E   W O R L D   I N   O N E   I M A G E", font(SANS_BOLD, 25), MUTED)
    centered(draw, W / 2, 54, "TUESDAY 17 NOVEMBER 2026", date_fnt, INK)
    draw.rectangle([MARGIN, 138, W - MARGIN, 144], fill=ACCENT)

    # hero panel: Hormuz
    hero = (MARGIN, 158, W - MARGIN, 452)
    panel(draw, hero, (250, 214, 165))
    scene_hormuz(draw, hero)
    label_bar(draw, hero, "U.S.-IRAN WAR: TANKERS BURN IN THE STRAIT OF HORMUZ", 29)

    # row of two
    r2y0, r2y1 = 468, 706
    half = (CW - 16) // 2
    left = (MARGIN, r2y0, MARGIN + half, r2y1)
    right = (MARGIN + half + 16, r2y0, W - MARGIN, r2y1)
    panel(draw, left, (196, 220, 235))
    scene_shenzhen(draw, left)
    label_bar(draw, left, "SHENZHEN: XI, TRUMP, PUTIN - FIRST THREE-WAY SUMMIT", 24)
    panel(draw, right, (178, 192, 204))
    scene_bridge(draw, right)
    label_bar(draw, right, "UKRAINE: KERCH BRIDGE STRUCK, KYIV BRIDGES HIT", 24)

    # row of three
    r3y0, r3y1 = 722, 946
    third = (CW - 28) // 3
    boxes = [(MARGIN + i * (third + 14), r3y0, MARGIN + i * (third + 14) + third, r3y1) for i in range(3)]
    panel(draw, boxes[0], (168, 182, 194))
    scene_gaza(draw, boxes[0])
    label_bar(draw, boxes[0], "GAZA: AID CALL AS RAINS FLOOD TENTS", 22)
    panel(draw, boxes[1], (186, 224, 196))
    scene_cop(draw, boxes[1])
    label_bar(draw, boxes[1], "COP31 DEAL: PHASE OUT FOSSIL FUELS, $120BN FUND", 22)
    panel(draw, boxes[2], (26, 34, 54))
    scene_markets(draw, boxes[2])
    label_bar(draw, boxes[2], "STOCKS FALL AS NVIDIA REPORTS; CHIP RULES TIGHTEN", 22)

    # footer: two more of the day's stories, wrapped to fit
    draw.line([MARGIN, 958, W - MARGIN, 958], fill=MUTED, width=2)
    foot = font(SANS_BOLD, 20)
    lines = wrap(draw, "ALSO TODAY: U.S. LOSES MEASLES ELIMINATION STATUS - INDIA EDGE PAKISTAN IN U-19 ASIA CUP FINAL THRILLER", foot, CW - 20)
    ty = 966
    for line in lines[:2]:
        centered(draw, W / 2, ty, line, foot, INK)
        ty += 26

    img.save(out, "PNG", optimize=True)
    print("wrote", out)


if __name__ == "__main__":
    main()
