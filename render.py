#!/usr/bin/env python3
"""Render the news-image entry for Wednesday 25 November 2026.

Build-time only: draws entry.png (1024x1024) with Pillow. The submitted
entrypoint (main.py) never imports this file and never runs Pillow; it only
copies the rendered PNG and checks its SHA-256.
"""
import random
from datetime import datetime, timezone

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

# Palette: midnight teal base, amber accent, cream text.
TEAL_DARK = (11, 43, 51)
TEAL_PANEL = (14, 58, 68)
TEAL_PANEL2 = (16, 63, 74)
TEAL_SKY_TOP = (9, 34, 44)
TEAL_SKY_BOT = (18, 66, 76)
AMBER = (232, 163, 61)
CREAM = (245, 239, 227)
MUTED = (176, 198, 192)
FAINT = (140, 168, 162)
STEEL = (111, 179, 201)
SAGE = (155, 197, 180)
BRICK = (208, 123, 84)
WHITE = (255, 255, 255)
ROCKET_BODY = (238, 236, 228)
ROCKET_BAND = (200, 84, 60)
FLAME_Y = (245, 190, 60)
FLAME_O = (235, 120, 40)

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(draw, box, top, bottom):
    x0, y0, x1, y1 = box
    span = max(1, y1 - y0)
    for y in range(y0, y1):
        draw.line([(x0, y), (x1, y)], fill=lerp(top, bottom, (y - y0) / span))


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def chip(draw, x, y, label, fill, fnt):
    tw = draw.textlength(label, font=fnt)
    pad_x, h = 12, 28
    draw.rounded_rectangle([x, y, x + tw + 2 * pad_x, y + h], radius=6, fill=fill)
    draw.text((x + pad_x, y + 5), label, font=fnt, fill=TEAL_DARK)


def draw_stars(draw, box, n, seed):
    rng = random.Random(seed)
    x0, y0, x1, y1 = box
    for _ in range(n):
        x = rng.randint(x0, x1)
        y = rng.randint(y0, y1)
        r = rng.choice([1, 1, 2])
        a = rng.randint(90, 200)
        draw.ellipse([x - r, y - r, x + r, y + r],
                     fill=(CREAM[0], CREAM[1], CREAM[2]) if a > 150 else FAINT)


def draw_rocket(draw, cx, top, scale=1.0):
    """Simple vertical rocket with flame, centred at cx, nose at top."""
    bw = int(58 * scale)          # body width
    bh = int(190 * scale)         # body height
    x0, x1 = cx - bw // 2, cx + bw // 2
    y0, y1 = top, top + bh
    # flame (behind body bottom)
    fy0 = y1 - 6
    flame = [(cx - int(26 * scale), fy0 + int(10 * scale)),
             (cx + int(26 * scale), fy0 + int(10 * scale)),
             (cx, fy0 + int(78 * scale))]
    draw.polygon(flame, fill=FLAME_O)
    inner = [(cx - int(13 * scale), fy0 + int(8 * scale)),
             (cx + int(13 * scale), fy0 + int(8 * scale)),
             (cx, fy0 + int(52 * scale))]
    draw.polygon(inner, fill=FLAME_Y)
    # fins
    draw.polygon([(x0, y1 - int(46 * scale)), (x0 - int(22 * scale), y1 + int(6 * scale)),
                  (x0, y1)], fill=ROCKET_BAND)
    draw.polygon([(x1, y1 - int(46 * scale)), (x1 + int(22 * scale), y1 + int(6 * scale)),
                  (x1, y1)], fill=ROCKET_BAND)
    # body
    draw.rounded_rectangle([x0, y0 + int(30 * scale), x1, y1], radius=int(10 * scale),
                           fill=ROCKET_BODY)
    # nose cone
    draw.polygon([(x0, y0 + int(32 * scale)), (x1, y0 + int(32 * scale)),
                  (cx, y0)], fill=ROCKET_BODY)
    draw.polygon([(x0, y0 + int(32 * scale)), (x1, y0 + int(32 * scale)),
                  (cx, y0 + int(14 * scale))], fill=ROCKET_BAND)
    # window
    wr = int(13 * scale)
    wy = y0 + int(78 * scale)
    draw.ellipse([cx - wr, wy - wr, cx + wr, wy + wr], fill=STEEL,
                 outline=TEAL_DARK, width=2)
    # band near base
    draw.rectangle([x0, y1 - int(26 * scale), x1, y1 - int(14 * scale)],
                   fill=ROCKET_BAND)
    # exhaust smoke dots
    for i, r in enumerate([7, 10, 13, 9]):
        sx = cx + (i - 1) * int(26 * scale) + (6 if i % 2 else -4)
        sy = fy0 + int(86 * scale) + i * 4
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(120, 140, 138))


def draw_station(draw, x, y, w):
    """Small Tiangong silhouette: central module + two solar wings."""
    mh = max(10, w // 7)
    mw = w // 3
    cx = x + w // 2
    # solar wings
    draw.rectangle([x, y + mh // 3, x + (w - mw) // 2, y + mh // 3 + mh // 2],
                   fill=(70, 110, 122), outline=AMBER, width=1)
    draw.rectangle([cx + mw // 2, y + mh // 3, x + w, y + mh // 3 + mh // 2],
                   fill=(70, 110, 122), outline=AMBER, width=1)
    # central module
    draw.rounded_rectangle([cx - mw // 2, y, cx + mw // 2, y + mh], radius=mh // 3,
                           fill=(200, 205, 198))
    draw.ellipse([cx - 4, y + mh // 2 - 4, cx + 4, y + mh // 2 + 4], fill=AMBER)


def draw_bars(draw, box, values, color):
    x0, y0, x1, y1 = box
    n = len(values)
    gap = 14
    bw = (x1 - x0 - gap * (n + 1)) // n
    vmax = max(values)
    base = y1 - 8
    for i, v in enumerate(values):
        bh = int((y1 - y0 - 20) * v / vmax)
        bx0 = x0 + gap + i * (bw + gap)
        draw.rounded_rectangle([bx0, base - bh, bx0 + bw, base], radius=4,
                               fill=color if i < n - 1 else AMBER)
    draw.line([(x0 + 4, base), (x1 - 4, base)], fill=MUTED, width=2)


def draw_fall_line(draw, box, color):
    x0, y0, x1, y1 = box
    pts = [(x0 + 10, y0 + 14), (x0 + 70, y0 + 30), (x0 + 130, y0 + 26),
           (x0 + 190, y0 + 62), (x0 + 250, y0 + 86), (x1 - 12, y1 - 16)]
    draw.line(pts, fill=color, width=6, joint="curve")
    # arrowhead at the end
    ex, ey = pts[-1]
    draw.polygon([(ex, ey), (ex - 18, ey - 4), (ex - 6, ey - 18)], fill=color)
    for px, py in pts:
        draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=CREAM)


def draw_storm(draw, box):
    x0, y0, x1, y1 = box
    cx = (x0 + x1) // 2
    cy = y0 + 58
    # cloud: overlapping ellipses
    cloud = (150, 175, 182)
    for dx, dy, rx, ry in [(-70, 6, 52, 30), (-30, -14, 58, 36), (20, -10, 56, 34),
                           (62, 8, 48, 28)]:
        draw.ellipse([cx + dx - rx, cy + dy - ry, cx + dx + rx, cy + dy + ry],
                     fill=cloud)
    draw.rectangle([cx - 118, cy - 6, cx + 108, cy + 30], fill=cloud)
    # lightning bolt
    bolt = [(cx + 8, cy + 26), (cx - 14, cy + 74), (cx + 2, cy + 74),
            (cx - 10, cy + 116), (cx + 26, cy + 58), (cx + 8, cy + 58)]
    draw.polygon(bolt, fill=AMBER)
    # rain lines
    for dx in (-104, -82, 84, 104):
        draw.line([(cx + dx, cy + 44), (cx + dx - 8, cy + 74)], fill=STEEL, width=4)
    # ground line
    draw.line([(x0 + 14, y1 - 12), (x1 - 14, y1 - 12)], fill=MUTED, width=2)


def main():
    img = Image.new("RGB", (W, H), TEAL_DARK)
    d = ImageDraw.Draw(img)

    f_mast = font(BOLD, 62)
    f_date = font(BOLD, 24)
    f_lead_big = font(BOLD, 54)
    f_lead_sub = font(BOLD, 29)
    f_lead_head = font(BOLD, 42)
    f_lead_deck = font(REG, 23)
    f_chip = font(BOLD, 17)
    f_grid_head = font(BOLD, 25)
    f_grid_deck = font(REG, 20)
    f_strip = font(REG, 21)
    f_strip_lab = font(BOLD, 21)
    f_foot = font(REG, 19)

    # ---- Masthead ----
    d.text((W // 2, 30), "THE WORLD TODAY", font=f_mast, fill=CREAM, anchor="ma")
    d.line([(24, 106), (1000, 106)], fill=AMBER, width=4)

    # ---- Date line ----
    now_utc = datetime.now(timezone.utc)
    date_line = ("WEDNESDAY, 25 NOVEMBER 2026 \u00b7 AS OF %02d:%02d UTC"
                 % (now_utc.hour, now_utc.minute))
    d.text((W // 2, 122), date_line, font=f_date, fill=AMBER, anchor="ma")

    # ---- Lead hero ----
    lx0, ly0, lx1, ly1 = 24, 150, 1000, 520
    d.rounded_rectangle([lx0, ly0, lx1, ly1], radius=10, fill=TEAL_PANEL)
    vgrad(d, (lx0 + 2, ly0 + 2, lx1 - 2, ly1 - 2), TEAL_SKY_TOP, TEAL_SKY_BOT)
    draw_stars(d, (lx0 + 8, ly0 + 8, lx1 - 8, ly1 - 8), 46, seed=25)
    draw_rocket(d, 175, 196, scale=1.05)
    draw_station(d, 800, 172, 170)

    tx = 330
    chip(d, tx, 176, "SPACE", AMBER, f_chip)
    d.text((tx, 216), "SHENZHOU-24", font=f_lead_big, fill=AMBER)
    d.text((tx, 282), "CHINA \u00d7 PAKISTAN", font=f_lead_sub, fill=CREAM)
    d.text((tx, 330), "CHINA LAUNCHES FIRST", font=f_lead_head, fill=CREAM)
    d.text((tx, 380), "PAKISTANI INTO ORBIT", font=f_lead_head, fill=CREAM)
    d.text((tx, 438), "Shenzhou-24 lifts off with Muhammad Zeeshan Ali,", font=f_lead_deck, fill=MUTED)
    d.text((tx, 466), "bound for Tiangong", font=f_lead_deck, fill=MUTED)

    # ---- Grid row: 3 panels ----
    gy0, gy1 = 520, 884
    gw = 317
    gx = [24, 353, 682]
    panels = [
        dict(chip="ECONOMY", chip_fill=STEEL, scene="bars",
             head="Australia inflation runs hot at 4.9%",
             deck="CPI beats forecasts; trimmed mean 3.8%"),
        dict(chip="ECONOMY", chip_fill=STEEL, scene="fall",
             head="Asian stocks slide on tariff threat",
             deck="Korea -5.3% \u00b7 Taiwan -5.1%, Nikkei -2.9%"),
        dict(chip="WEATHER", chip_fill=SAGE, scene="storm",
             head="Storms threaten Thanksgiving travel",
             deck="Rain, wind hit East Coast"),
    ]
    for x, p in zip(gx, panels):
        d.rounded_rectangle([x, gy0, x + gw, gy1], radius=10, fill=TEAL_PANEL)
        # illustration strip
        ix0, iy0, ix1, iy1 = x + 10, gy0 + 10, x + gw - 10, gy0 + 152
        d.rounded_rectangle([ix0, iy0, ix1, iy1], radius=8, fill=TEAL_PANEL2)
        if p["scene"] == "bars":
            draw_bars(d, (ix0 + 12, iy0 + 14, ix1 - 12, iy1 - 10),
                      [3.1, 3.6, 4.3, 4.9], AMBER)
        elif p["scene"] == "fall":
            draw_fall_line(d, (ix0 + 8, iy0 + 10, ix1 - 8, iy1 - 10), BRICK)
        else:
            draw_storm(d, (ix0 + 8, iy0 + 8, ix1 - 8, iy1 - 8))
        chip(d, x + 16, gy0 + 166, p["chip"], p["chip_fill"], f_chip)
        lines = wrap(d, p["head"], f_grid_head, gw - 32)
        y = gy0 + 204
        for ln in lines[:2]:
            d.text((x + 16, y), ln, font=f_grid_head, fill=CREAM)
            y += 32
        dlines = wrap(d, p["deck"], f_grid_deck, gw - 32)
        y = gy0 + 284
        for ln in dlines[:2]:
            d.text((x + 16, y), ln, font=f_grid_deck, fill=MUTED)
            y += 27

    # ---- Strip ----
    sy0, sy1 = 884, 952
    d.rounded_rectangle([24, sy0, 1000, sy1], radius=10, fill=TEAL_PANEL)
    for lab, lab_fill, text, ly in [
            ("QUAKE", BRICK, "M5.9 quake strikes remote Southern Ocean \u2014 no damage reported", 893),
            ("US DATA", AMBER, "Inflation and growth data due 13:30 GMT \u00b7 DUE LATER", 921)]:
        d.text((40, ly), lab, font=f_strip_lab, fill=lab_fill)
        lw = d.textlength(lab, font=f_strip_lab)
        d.text((40 + lw + 12, ly), text, font=f_strip, fill=CREAM)

    # ---- Footer ----
    d.text((W // 2, 972),
           "All stories from Wednesday, 25 November 2026 \u2014 Sources: Reuters \u00b7 USGS",
           font=f_foot, fill=FAINT, anchor="ma")

    img.save("entry.png", optimize=True)
    print("saved entry.png", img.size)


if __name__ == "__main__":
    main()
