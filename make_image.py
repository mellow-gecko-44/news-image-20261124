#!/usr/bin/env python3
"""Render entry.png (v2): Tuesday 24 November 2026 as a visual poster.

Redesign of the v1 broadsheet for a vision-model judge that compares images
pairwise at thumbnail scale. Same facts as v1, same program contract (PIL
only, offline, deterministic bytes, 1024 x 1024, written to ./entry.png),
but laid out as a poster instead of a text-dense newspaper:

- slim masthead, then a tall red band with the date in very large type;
- one big hero scene (about half the page): Ukrainian sea drones sinking a
  Russian warship off Libya at dusk, drawn with gradients, a glowing
  explosion and smoke; the headline sits over the sky in extra-large type;
- the other stories compressed into four big tiles, each a drawn icon scene
  plus ONE bold short title (no small body text -- it is noise at scale);
- one ticker line at the foot.

Run:  python3 make_image.py   ->   writes ./entry.png (1024 x 1024)
The image is deterministic: same code, same bytes.
"""

import math

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
MARGIN = 32
RIGHT = W - MARGIN
CW = RIGHT - MARGIN  # 960

PAPER = (247, 243, 233)
INK = (22, 21, 17)
RED = (178, 34, 27)
WHITE = (252, 250, 244)
GOLD = (255, 205, 105)

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
    while size > min_size:
        f = font(kind, size)
        lines = wrap(d, s, f, width)
        if len(lines) <= max_lines:
            return f, lines, size
        size -= 2
    f = font(kind, size)
    return f, wrap(d, s, f, width), size


def fit_one_line(d, s, kind, size, width, min_size=13):
    while size > min_size and text_w(d, s, font(kind, size)) > width:
        size -= 1
    return font(kind, size)


def centered(d, cx, y, s, f, fill=INK):
    d.text((cx - text_w(d, s, f) / 2, y), s, font=f, fill=fill)


def rule(d, y, x0=MARGIN, x1=RIGHT, fill=INK, width=3):
    d.line([(x0, y), (x1, y)], fill=fill, width=width)


def vgrad(d, x0, y0, x1, y1, top, bot, step=4):
    """Vertical gradient in horizontal bands (banding keeps the PNG small)."""
    h = y1 - y0
    for yy in range(y0, y1, step):
        t = (yy - y0) / h
        col = tuple(int(top[c] + (bot[c] - top[c]) * t) for c in range(3))
        d.rectangle([x0, yy, x1, min(yy + step, y1)], fill=col)


def starburst(cx, cy, r_out, r_in, n=16, squash=0.82):
    pts = []
    for i in range(2 * n):
        ang = math.pi * i / n
        r = r_out if i % 2 == 0 else r_in
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang) * squash))
    return pts


# ---------------------------------------------------------------- hero scene

def draw_hero(img, x0, y0, x1, y1):
    """Dusk sea battle off Benghazi: seven drone boats swarm a warship.

    Drawn on the base image; the explosion glow and smoke go on an RGBA
    overlay composited in the middle, so the burst core stays crisp.
    """
    d = ImageDraw.Draw(img)
    pw, ph = x1 - x0, y1 - y0
    horizon = y0 + int(ph * 0.60)

    # dusk sky: deep indigo up top melting into burnt orange at the horizon
    vgrad(d, x0, y0, x1, horizon, (34, 28, 62), (226, 104, 48), step=4)
    # sea: dark steel blue down to near black
    vgrad(d, x0, horizon, x1, y1, (36, 52, 70), (8, 13, 22), step=4)

    # low sun, right of centre, half sunk into the horizon
    sun_cx, sun_cy, sun_r = x0 + int(pw * 0.71), horizon - 6, 56
    d.ellipse([sun_cx - sun_r, sun_cy - sun_r, sun_cx + sun_r, sun_cy + sun_r],
              fill=(255, 178, 84))
    d.ellipse([sun_cx - sun_r + 10, sun_cy - sun_r + 10,
               sun_cx + sun_r - 10, sun_cy + sun_r - 10], fill=(255, 205, 105))
    # sun path on the water: broken orange dashes under the sun
    for i in range(6):
        ry = horizon + 16 + i * 22
        rw = 74 - i * 8
        d.line([(sun_cx - rw, ry), (sun_cx + rw, ry)], fill=(214, 116, 52), width=4)

    # dark cloud silhouettes (right side only -- the headline owns the left)
    cloud = (52, 38, 66)
    for cx, cy, s in ((x1 - 120, y0 + 84, 0.9), (x1 - 330, y0 + 52, 0.65)):
        d.ellipse([cx - 52 * s, cy - 15 * s, cx + 52 * s, cy + 15 * s], fill=cloud)
        d.ellipse([cx - 28 * s, cy - 24 * s, cx + 30 * s, cy + 12 * s], fill=cloud)

    # warship, big, right of centre, riding the horizon (silhouette)
    sil = (10, 11, 14)
    ship_x = x0 + int(pw * 0.66)
    ship_y = horizon + 30
    hull = [(ship_x - 178, ship_y), (ship_x + 192, ship_y), (ship_x + 158, ship_y + 38),
            (ship_x - 132, ship_y + 38)]
    d.polygon(hull, fill=sil)
    d.rectangle([ship_x - 92, ship_y - 38, ship_x + 46, ship_y], fill=sil)        # superstructure
    d.rectangle([ship_x - 44, ship_y - 64, ship_x + 10, ship_y - 38], fill=sil)   # bridge
    d.rectangle([ship_x + 66, ship_y - 26, ship_x + 116, ship_y], fill=sil)       # funnel block
    d.line([(ship_x - 12, ship_y - 64), (ship_x - 12, ship_y - 114)], fill=sil, width=7)  # mast
    d.line([(ship_x - 44, ship_y - 102), (ship_x + 24, ship_y - 102)], fill=sil, width=4)
    d.rectangle([ship_x - 160, ship_y - 17, ship_x - 124, ship_y], fill=sil)      # aft turret
    d.line([(ship_x - 160, ship_y - 13), (ship_x - 190, ship_y - 19)], fill=sil, width=6)  # gun
    # bow and stern wakes
    d.line([(ship_x + 188, ship_y + 32), (ship_x + 250, ship_y + 44)], fill=(206, 216, 220), width=4)
    d.line([(ship_x - 174, ship_y + 32), (ship_x - 226, ship_y + 44)], fill=(206, 216, 220), width=4)

    # helicopter high on the right (the Ka-27 that was destroyed)
    hx, hy = x0 + int(pw * 0.86), y0 + int(ph * 0.30)
    d.ellipse([hx - 38, hy - 15, hx + 38, hy + 17], fill=sil)
    d.polygon([(hx + 30, hy - 2), (hx + 76, hy - 10), (hx + 76, hy + 4), (hx + 32, hy + 9)],
              fill=sil)
    d.line([(hx - 50, hy - 24), (hx + 50, hy - 24)], fill=sil, width=6)   # main rotor
    d.line([(hx, hy - 15), (hx, hy - 24)], fill=sil, width=4)
    d.line([(hx + 76, hy - 18), (hx + 76, hy + 4)], fill=sil, width=4)    # tail rotor

    # seven unmanned drone boats sweeping in from the left, each with a V wake
    drones = [(0.05, 0.70), (0.12, 0.82), (0.19, 0.66), (0.26, 0.85),
              (0.33, 0.72), (0.40, 0.88), (0.47, 0.76)]
    for fx, fy in drones:
        cx, cy = x0 + pw * fx, y0 + ph * fy
        d.polygon([(cx - 24, cy + 7), (cx + 27, cy + 7), (cx + 15, cy - 6), (cx - 12, cy - 6)],
                  fill=(6, 7, 9))
        d.rectangle([cx - 4, cy - 12, cx + 8, cy - 6], fill=(6, 7, 9))
        d.line([(cx - 20, cy + 11), (cx - 50, cy + 26)], fill=(206, 216, 220), width=3)
        d.line([(cx - 8, cy + 13), (cx - 24, cy + 32)], fill=(206, 216, 220), width=3)

    # explosion point: port bow of the ship
    ex, ey = ship_x - 192, ship_y - 4

    # ---- glow + smoke overlay (soft, translucent) ----
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for i in range(14, 0, -1):
        r = i * 12
        od.ellipse([ex - r, ey - r * 0.82, ex + r, ey + r * 0.82], fill=(255, 138, 42, 13))
    # smoke plume: a tight column of grey puffs rising from the burst
    for i, (dx, dy, r) in enumerate(((0, -38, 20), (-6, -68, 26), (-14, -98, 32),
                                     (-24, -126, 38))):
        od.ellipse([ex + dx - r, ey + dy - r * 0.78, ex + dx + r, ey + dy + r * 0.78],
                   fill=(58, 54, 58, 150 - i * 18))
    img.alpha_composite(ov)
    d = ImageDraw.Draw(img)

    # tracer streak from the nearest drone to the impact point
    tx, ty = x0 + pw * 0.47, y0 + ph * 0.76
    d.line([(tx + 20, ty - 8), (ex + 10, ey + 2)], fill=(255, 214, 130), width=4)

    # explosion core: layered starbursts, orange -> yellow -> white hot
    d.polygon(starburst(ex, ey, 84, 34), fill=(240, 116, 32))
    d.polygon(starburst(ex, ey, 58, 24), fill=(249, 178, 62))
    d.polygon(starburst(ex, ey, 34, 14), fill=(255, 226, 150))
    d.ellipse([ex - 13, ey - 11, ex + 13, ey + 11], fill=(255, 248, 224))
    # spray at the waterline
    for dx, ln in ((-30, 26), (-12, 38), (8, 34), (26, 22)):
        d.line([(ex + dx, ey + 16), (ex + dx - 6, ey + 16 - ln)], fill=(226, 233, 236), width=4)

    d.rectangle([x0, y0, x1, y1], outline=INK, width=3)


# --------------------------------------------------------------------- icons
# Reused from v1 (same drawn motifs, rendered larger by the caller via s).

def icon_missile(d, x, y, s):
    """Missile arcing down onto rooftops, burst at the impact point."""
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
    """Satellite: small body, wide blue-grey solar panels, beacons."""
    w = max(3, s // 14)
    cx, cy = x + s * 0.5, y + s * 0.42
    panel_fill = (150, 176, 204)
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
    d.rectangle([x + s * 0.40, y + s * 0.40, x + s * 0.60, y + s * 0.60], fill=(178, 34, 27))
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
    d.ellipse([x + s * 0.66, y + s * 0.38, x + s * 0.78, y + s * 0.50], fill=(178, 34, 27))
    d.ellipse([x + s * 0.78, y + s * 0.54, x + s * 0.90, y + s * 0.66], outline=INK, width=w)


# --------------------------------------------------------------------- page

# Four secondary stories: (one-line bold title, tile tint, icon). Titles are
# the v1 headlines compressed to a single line; the facts are unchanged.
BLOCKS = [
    ("STRIKES KILL 12 NEAR KYIV", (238, 208, 198), icon_missile),
    ("NATO VOWS SPACE DEFENCE", (206, 222, 238), icon_satellite),
    ("HUANG BACK AS NVIDIA CEO", (208, 232, 212), icon_chip),
    ("GTA VI HACKER JAILED 7 YEARS", (240, 228, 192), icon_gamepad),
]

CAPTION = ("Seven unmanned boats strike the corvette Merkury near Benghazi "
           "— a Ka-27 helicopter is destroyed")
TICKER = ("ALSO TODAY — THOUSANDS EVACUATED FROM A UK CONCERT AFTER "
          "AN UNKNOWN SUBSTANCE WAS RELEASED")


def main():
    img = Image.new("RGB", (W, H), PAPER).convert("RGBA")
    d = ImageDraw.Draw(img)

    # masthead (slim -- the date band and hero carry the page now)
    centered(d, W / 2, 14, "THE WORLD IN ONE PICTURE", font("black", 42))
    rule(d, 66, width=4)

    # date band: taller than v1, date in much larger type
    d.rectangle([MARGIN, 78, RIGHT, 178], fill=RED)
    f_date = fit_one_line(d, "TUESDAY 24 NOVEMBER 2026", "black", 66, CW - 40, min_size=30)
    centered(d, W / 2, 96, "TUESDAY 24 NOVEMBER 2026", f_date, fill=WHITE)

    # hero scene: about half the page
    hx0, hy0, hx1, hy1 = MARGIN, 194, RIGHT, 678
    draw_hero(img, hx0, hy0, hx1, hy1)
    d = ImageDraw.Draw(img)

    # headline over the sky, top-left, soft dark shadow for contrast
    tx = hx0 + 26
    d.text((tx, hy0 + 18), "UKRAINE WAR  •  OFF THE LIBYAN COAST",
           font=font("bold", 27), fill=GOLD)
    f_head, head_lines, _ = fit_lines(
        d, "SEA DRONES SINK RUSSIAN WARSHIP", "black", 104, hx1 - tx - 330, 2, min_size=44)
    hy = hy0 + 56
    for line in head_lines:
        d.text((tx + 3, hy + 3), line, font=f_head, fill=(20, 12, 24))
        d.text((tx, hy), line, font=f_head, fill=WHITE)
        hy += int(f_head.size * 1.02)

    # one factual line along the foot of the hero, on the dark sea
    f_cap = fit_one_line(d, CAPTION, "bold", 23, hx1 - hx0 - 52, min_size=15)
    d.text((hx0 + 26, hy1 - 40), CAPTION, font=f_cap, fill=(238, 240, 238))

    # four story tiles, 2 x 2: big icon tile + one bold title line, no body text
    grid_top = 694
    row_h = 122
    gap = 12
    col_w = (CW - gap) // 2
    for i, (title, tint, icon) in enumerate(BLOCKS):
        bx = MARGIN + (i % 2) * (col_w + gap)
        by = grid_top + (i // 2) * (row_h + gap)
        d.rectangle([bx, by, bx + col_w, by + row_h], fill=(253, 251, 245), outline=INK, width=2)
        tile = 104
        d.rectangle([bx + 9, by + 9, bx + 9 + tile, by + 9 + tile], fill=tint)
        icon(d, bx + 17, by + 17, tile - 16)
        txx = bx + 9 + tile + 18
        tw = bx + col_w - 12 - txx
        f_t = fit_one_line(d, title, "condbold", 37, tw, min_size=21)
        asc, desc = f_t.getmetrics()
        ty = by + (row_h - (asc + desc)) // 2
        d.text((txx, ty), title, font=f_t, fill=INK)

    # footer ticker, one line
    rule(d, 968, width=3)
    f_tick = fit_one_line(d, TICKER, "bold", 24, CW, min_size=13)
    centered(d, W / 2, 978, TICKER, f_tick, fill=INK)

    img.convert("RGB").save("entry.png", optimize=True)
    print("wrote entry.png")


if __name__ == "__main__":
    main()
