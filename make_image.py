#!/usr/bin/env python3
"""Render entry.png: one page that sums up the world news of Tuesday 24 November 2026.

Drawn entirely with PIL (no photos, no network): a broadsheet front page with a
masthead, the date in a red band, one lead story with a drawn sea-battle panel,
six secondary stories with drawn icons, and a ticker line at the foot.

Run:  python3 make_image.py   ->   writes ./entry.png (1024 x 1024)
The image is deterministic: same code, same bytes.
"""

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
MARGIN = 36
RIGHT = W - MARGIN

PAPER = (247, 243, 233)
INK = (22, 21, 17)
SOFT_INK = (74, 70, 62)
RED = (178, 34, 27)
RED_DARK = (148, 26, 20)
WHITE = (252, 250, 244)

FONT_DIR = "/usr/share/fonts/truetype/noto/"
FACES = {
    "black": "NotoSans-Black.ttf",
    "bold": "NotoSans-Bold.ttf",
    "regular": "NotoSans-Regular.ttf",
    "italic": "NotoSans-Italic.ttf",
    "cond": "NotoSans-Condensed.ttf",
    "condbold": "NotoSans-CondensedBold.ttf",
}


def font(kind, size):
    return ImageFont.truetype(FONT_DIR + FACES[kind], size)


def text_w(d, s, f):
    return d.textlength(s, font=f)


def wrap(d, s, f, width):
    """Greedy word wrap to lines that fit width."""
    lines, cur = [], ""
    for word in s.split():
        trial = word if not cur else cur + " " + word
        if text_w(d, trial, f) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(d, s, kind, size, width, max_lines, min_size=18):
    """Shrink the font from size until s wraps into at most max_lines lines."""
    while size > min_size:
        f = font(kind, size)
        lines = wrap(d, s, f, width)
        if len(lines) <= max_lines:
            return f, lines, size
        size -= 2
    f = font(kind, size)
    return f, wrap(d, s, f, width), size


def fit_one_line(d, s, kind, size, width, min_size=13):
    """Largest font, stepping 1px at a time, that keeps s on a single line."""
    while size > min_size and text_w(d, s, font(kind, size)) > width:
        size -= 1
    return font(kind, size)


def centered(d, cx, y, s, f, fill=INK):
    d.text((cx - text_w(d, s, f) / 2, y), s, font=f, fill=fill)


def spaced_centered(d, cx, y, s, f, fill=INK, tracking=6):
    """Draw s centered with extra letter tracking (for the small header line)."""
    widths = [text_w(d, ch, f) for ch in s]
    total = sum(widths) + tracking * (len(s) - 1)
    x = cx - total / 2
    for ch, w in zip(s, widths):
        d.text((x, y), ch, font=f, fill=fill)
        x += w + tracking


def rule(d, y, x0=MARGIN, x1=RIGHT, fill=INK, width=3):
    d.line([(x0, y), (x1, y)], fill=fill, width=width)


# ---------------------------------------------------------------- lead panel

def draw_lead_panel(d, x0, y0, x1, y1):
    """Sea battle off Benghazi: seven drone boats close on a warship at dusk."""
    sky = (186, 199, 209)
    sea_top = (52, 74, 92)
    sea_bot = (30, 46, 62)
    silhouette = (23, 25, 29)

    d.rectangle([x0, y0, x1, y1], fill=sky)
    horizon = y0 + int((y1 - y0) * 0.52)
    # sea as horizontal bands, darker towards the bottom
    bands = 14
    for i in range(bands):
        t = i / bands
        col = tuple(int(sea_top[c] + (sea_bot[c] - sea_top[c]) * t) for c in range(3))
        by0 = horizon + int((y1 - horizon) * i / bands)
        by1 = horizon + int((y1 - horizon) * (i + 1) / bands)
        d.rectangle([x0, by0, x1, by1], fill=col)
    # low sun and its reflection
    sun_cx, sun_cy, sun_r = x0 + int((x1 - x0) * 0.66), horizon - 16, 30
    d.ellipse([sun_cx - sun_r, sun_cy - sun_r, sun_cx + sun_r, sun_cy + sun_r], fill=(233, 164, 92))
    for i in range(5):
        ry = horizon + 14 + i * 16
        rw = 44 - i * 6
        d.line([(sun_cx - rw, ry), (sun_cx + rw, ry)], fill=(233, 164, 92), width=3)
    # clouds
    for cx, cy, s in ((x0 + 70, y0 + 34, 1.0), (x0 + 250, y0 + 22, 0.7), (x1 - 90, y0 + 46, 0.85)):
        d.ellipse([cx - 44 * s, cy - 13 * s, cx + 44 * s, cy + 13 * s], fill=(214, 221, 226))
        d.ellipse([cx - 24 * s, cy - 20 * s, cx + 26 * s, cy + 10 * s], fill=(214, 221, 226))

    # warship, right of centre, riding the horizon
    ship_x = x0 + int((x1 - x0) * 0.60)
    ship_y = horizon + 26
    hull = [(ship_x - 118, ship_y), (ship_x + 128, ship_y), (ship_x + 104, ship_y + 26),
            (ship_x - 88, ship_y + 26)]
    d.polygon(hull, fill=silhouette)
    d.rectangle([ship_x - 62, ship_y - 26, ship_x + 30, ship_y], fill=silhouette)      # superstructure
    d.rectangle([ship_x - 30, ship_y - 44, ship_x + 6, ship_y - 26], fill=silhouette)   # bridge
    d.rectangle([ship_x + 44, ship_y - 18, ship_x + 78, ship_y], fill=silhouette)       # funnel block
    d.line([(ship_x - 8, ship_y - 44), (ship_x - 8, ship_y - 78)], fill=silhouette, width=5)   # mast
    d.line([(ship_x - 30, ship_y - 70), (ship_x + 16, ship_y - 70)], fill=silhouette, width=3)
    d.rectangle([ship_x - 108, ship_y - 12, ship_x - 84, ship_y], fill=silhouette)      # aft turret
    d.line([(ship_x - 108, ship_y - 9), (ship_x - 128, ship_y - 13)], fill=silhouette, width=4)  # gun
    # bow wake
    d.line([(ship_x + 126, ship_y + 22), (ship_x + 168, ship_y + 30)], fill=(226, 233, 236), width=3)
    d.line([(ship_x - 116, ship_y + 22), (ship_x - 152, ship_y + 30)], fill=(226, 233, 236), width=3)

    # explosion where a drone struck, at the ship's port bow
    ex, ey = ship_x - 128, ship_y - 2
    import math
    pts = []
    for i in range(16):
        ang = math.pi * i / 8
        r = 34 if i % 2 == 0 else 14
        pts.append((ex + r * math.cos(ang), ey + r * math.sin(ang) * 0.8))
    d.polygon(pts, fill=(238, 128, 40))
    pts2 = [(ex + (px - ex) * 0.55, ey + (py - ey) * 0.55) for px, py in pts]
    d.polygon(pts2, fill=(247, 199, 74))

    # helicopter above the stern (the Ka-27 that was destroyed)
    hx, hy = ship_x - 66, y0 + 52
    d.ellipse([hx - 26, hy - 10, hx + 26, hy + 12], fill=silhouette)
    d.polygon([(hx + 20, hy), (hx + 52, hy - 6), (hx + 52, hy + 3), (hx + 22, hy + 6)], fill=silhouette)
    d.line([(hx - 34, hy - 16), (hx + 34, hy - 16)], fill=silhouette, width=4)   # main rotor
    d.line([(hx, hy - 10), (hx, hy - 16)], fill=silhouette, width=3)
    d.line([(hx + 52, hy - 12), (hx + 52, hy + 2)], fill=silhouette, width=3)    # tail rotor

    # seven unmanned drone boats sweeping in from the left, each with a V wake
    drones = [(0.06, 0.66), (0.13, 0.78), (0.20, 0.62), (0.27, 0.80),
              (0.33, 0.68), (0.40, 0.84), (0.47, 0.72)]
    pw, ph = x1 - x0, y1 - y0
    for fx, fy in drones:
        cx, cy = x0 + pw * fx, y0 + ph * fy
        d.polygon([(cx - 16, cy + 5), (cx + 18, cy + 5), (cx + 10, cy - 4), (cx - 8, cy - 4)],
                  fill=(15, 17, 19))
        d.line([(cx - 14, cy + 8), (cx - 34, cy + 18)], fill=(226, 233, 236), width=2)
        d.line([(cx - 6, cy + 9), (cx - 16, cy + 22)], fill=(226, 233, 236), width=2)

    d.rectangle([x0, y0, x1, y1], outline=INK, width=3)


# --------------------------------------------------------------------- icons

def icon_missile(d, x, y, s):
    """Missile arcing down onto rooftops, burst at the impact point."""
    import math
    d.polygon([(x, y + s), (x, y + s * 0.74), (x + s * 0.30, y + s * 0.60),
               (x + s * 0.62, y + s * 0.74), (x + s * 0.62, y + s)], fill=INK)
    d.polygon([(x + s * 0.62, y + s), (x + s * 0.62, y + s * 0.74), (x + s, y + s * 0.60),
               (x + s, y + s)], fill=INK)
    bx, by = x + s * 0.68, y + s * 0.44
    d.line([(x + s * 0.14, y + s * 0.14), (bx - s * 0.08, by - s * 0.06)],
           fill=INK, width=max(4, s // 9))
    d.polygon([(x + s * 0.02, y + s * 0.10), (x + s * 0.16, y + s * 0.00),
               (x + s * 0.22, y + s * 0.16)], fill=RED)
    pts = []
    for i in range(12):
        ang = math.pi * i / 6
        r = s * 0.19 if i % 2 == 0 else s * 0.085
        pts.append((bx + r * math.cos(ang), by + r * math.sin(ang)))
    d.polygon(pts, fill=RED)


def icon_satellite(d, x, y, s):
    """Satellite: small body, wide blue-grey solar panels, beacon below."""
    w = max(3, s // 14)
    cx, cy = x + s * 0.5, y + s * 0.42
    panel_fill = (176, 196, 214)
    for side in (-1, 1):
        px0 = cx + side * s * 0.14
        px1 = cx + side * s * 0.48
        lo, hi = min(px0, px1), max(px0, px1)
        d.rectangle([lo, cy - s * 0.19, hi, cy + s * 0.19], fill=panel_fill, outline=INK, width=w)
        third = (hi - lo) / 3
        for k in (1, 2):
            d.line([(lo + third * k, cy - s * 0.19), (lo + third * k, cy + s * 0.19)], fill=INK, width=2)
        d.line([(lo, cy), (hi, cy)], fill=INK, width=2)
        d.line([(cx + side * s * 0.09, cy), (cx + side * s * 0.14, cy)], fill=INK, width=w)
    d.rectangle([cx - s * 0.09, cy - s * 0.16, cx + s * 0.09, cy + s * 0.16], fill=INK)
    d.line([(cx, cy - s * 0.16), (cx, cy - s * 0.30)], fill=INK, width=w)
    d.ellipse([cx - s * 0.045, cy - s * 0.36, cx + s * 0.045, cy - s * 0.27], fill=RED)
    d.line([(cx, cy + s * 0.16), (cx, cy + s * 0.30)], fill=INK, width=w)
    d.ellipse([cx - s * 0.05, cy + s * 0.28, cx + s * 0.05, cy + s * 0.38], fill=RED)
    for sx, sy in ((x + s * 0.08, y + s * 0.04), (x + s * 0.92, y + s * 0.06)):
        d.line([(sx - 5, sy), (sx + 5, sy)], fill=INK, width=3)
        d.line([(sx, sy - 5), (sx, sy + 5)], fill=INK, width=3)


def icon_chip(d, x, y, s):
    """AI chip with pins."""
    w = max(3, s // 13)
    x0, y0, x1, y1 = x + s * 0.24, y + s * 0.24, x + s * 0.76, y + s * 0.76
    d.rectangle([x0, y0, x1, y1], outline=INK, width=w)
    d.rectangle([x + s * 0.40, y + s * 0.40, x + s * 0.60, y + s * 0.60], fill=RED)
    for t in (0.36, 0.5, 0.64):
        d.line([(x + s * t, y + s * 0.08), (x + s * t, y0)], fill=INK, width=w)
        d.line([(x + s * t, y1), (x + s * t, y + s * 0.92)], fill=INK, width=w)
        d.line([(x + s * 0.08, y + s * t), (x0, y + s * t)], fill=INK, width=w)
        d.line([(x1, y + s * t), (x + s * 0.92, y + s * t)], fill=INK, width=w)


def icon_gamepad(d, x, y, s):
    """Game controller."""
    w = max(3, s // 13)
    d.rounded_rectangle([x + s * 0.04, y + s * 0.28, x + s * 0.96, y + s * 0.74], radius=s * 0.20, outline=INK, width=w)
    cx, cy = x + s * 0.30, y + s * 0.51
    d.line([(cx - s * 0.11, cy), (cx + s * 0.11, cy)], fill=INK, width=w + 1)
    d.line([(cx, cy - s * 0.11), (cx, cy + s * 0.11)], fill=INK, width=w + 1)
    d.ellipse([x + s * 0.66, y + s * 0.38, x + s * 0.78, y + s * 0.50], fill=RED)
    d.ellipse([x + s * 0.78, y + s * 0.54, x + s * 0.90, y + s * 0.66], outline=INK, width=w)


def icon_globe_ai(d, x, y, s):
    """Globe with circuit nodes: world governance meets AI."""
    w = max(3, s // 14)
    cx, cy, r = x + s * 0.46, y + s * 0.54, s * 0.36
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=w)
    d.ellipse([cx - r * 0.45, cy - r, cx + r * 0.45, cy + r], outline=INK, width=2)
    d.line([(cx - r, cy), (cx + r, cy)], fill=INK, width=2)
    for nx, ny in ((x + s * 0.90, y + s * 0.16), (x + s * 0.94, y + s * 0.52), (x + s * 0.86, y + s * 0.88)):
        d.line([(cx + r * 0.7, cy - r * 0.4), (nx, ny)], fill=INK, width=2)
        d.ellipse([nx - 5, ny - 5, nx + 5, ny + 5], fill=RED)


def icon_shield(d, x, y, s):
    """Shield with a star: a defence deal."""
    import math
    cx = x + s * 0.5
    pts = [(cx, y + s * 0.04), (x + s * 0.86, y + s * 0.16), (x + s * 0.86, y + s * 0.48),
           (cx, y + s * 0.97), (x + s * 0.14, y + s * 0.48), (x + s * 0.14, y + s * 0.16)]
    d.polygon(pts, outline=INK, width=max(3, s // 13))
    scx, scy = cx, y + s * 0.44
    star = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        r = s * 0.17 if i % 2 == 0 else s * 0.075
        star.append((scx + r * math.cos(ang), scy + r * math.sin(ang)))
    d.polygon(star, fill=RED)


# --------------------------------------------------------------------- page

STORIES = [
    ("KYIV REGION", "Russian strikes kill at least 12 near Kyiv",
     "Overnight attacks hit the capital region.", icon_missile),
    ("SPACE", "NATO vows space defence over nuclear satellite fears",
     "Nuclear satellite launch feared within weeks.", icon_satellite),
    ("TECHNOLOGY", "Nvidia reinstates Jensen Huang as CEO after 11 days",
     "Trump's push reverses his exit after 11 days.", icon_chip),
    ("COURTS", "GTA VI hacker jailed for seven years in London",
     "Kurtaj, 21, sentenced for the Rockstar breach.", icon_gamepad),
    ("UNITED NATIONS", "UN chief demands global AI risk rules within a year",
     "A worldwide framework on a one-year clock.", icon_globe_ai),
    ("ASIA-PACIFIC", "Trump offers Philippines $2.4bn for self-defence",
     "Washington backs Manila's own defences.", icon_shield),
]


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # header line and masthead
    spaced_centered(d, W / 2, 20, "ONE DAY • ONE IMAGE • THE WHOLE WORLD", font("bold", 22), fill=SOFT_INK, tracking=5)
    centered(d, W / 2, 46, "THE WORLD IN ONE PICTURE", font("black", 60))
    rule(d, 122, width=5)
    rule(d, 130, width=2)

    # date band
    d.rectangle([MARGIN, 142, RIGHT, 202], fill=RED)
    centered(d, W / 2, 152, "TUESDAY 24 NOVEMBER 2026", font("bold", 44), fill=WHITE)

    # lead story
    d.text((MARGIN, 220), "UKRAINE WAR  •  OFF THE LIBYAN COAST", font=font("bold", 25), fill=RED_DARK)
    f_head, head_lines, _ = fit_lines(
        d, "SEA DRONES SINK RUSSIAN WARSHIP OFF LIBYA", "condbold", 62, 560, 3)
    y = 250
    for line in head_lines:
        d.text((MARGIN, y), line, font=f_head, fill=INK)
        y += int(f_head.size * 1.04)
    f_sum = font("regular", 28)
    summary = ("Seven unmanned boats struck the corvette Merkury near Benghazi, "
               "destroying a Ka-27 helicopter and hitting the cargo ship MV Angara.")
    sy = y + 8
    for line in wrap(d, summary, f_sum, 560):
        d.text((MARGIN, sy), line, font=f_sum, fill=INK)
        sy += 38
    draw_lead_panel(d, 620, 220, RIGHT, 542)
    f_cap, cap_lines, _ = fit_lines(
        d, "The swarm closes on the Merkury.", "italic", 21, RIGHT - 620, 1, min_size=15)
    d.text((620, 550), cap_lines[0], font=f_cap, fill=SOFT_INK)
    rule(d, 606, width=3)

    # secondary grid, two columns by three rows
    grid_top = 622
    row_h = 116
    col_x = [MARGIN, 524]
    col_w = 464
    for i, (kicker, head, summ, icon) in enumerate(STORIES):
        cx = col_x[i % 2]
        cy = grid_top + (i // 2) * row_h
        if i >= 2:
            rule(d, cy - 6, x0=cx, x1=cx + col_w, width=1, fill=(196, 189, 172))
        icon(d, cx, cy + 10, 84)
        tx = cx + 102
        tw = col_w - 102
        d.text((tx, cy), kicker, font=font("bold", 19), fill=RED_DARK)
        f_h, h_lines, _ = fit_lines(d, head, "condbold", 31, tw, 2, min_size=23)
        hy = cy + 21
        for line in h_lines:
            d.text((tx, hy), line, font=f_h, fill=INK)
            hy += int(f_h.size * 0.98)
        f_s = fit_one_line(d, summ, "regular", 19, tw)
        d.text((tx, cy + 88), summ, font=f_s, fill=SOFT_INK)

    # footer ticker
    rule(d, 970, width=3)
    f_tick, tick_lines, _ = fit_lines(
        d, "ALSO TODAY — Thousands evacuated from a UK concert after an unknown substance was released",
        "bold", 22, RIGHT - MARGIN, 1, min_size=14)
    centered(d, W / 2, 980, tick_lines[0], f_tick, fill=INK)

    img.save("entry.png", optimize=True)
    print("wrote entry.png")


if __name__ == "__main__":
    main()
