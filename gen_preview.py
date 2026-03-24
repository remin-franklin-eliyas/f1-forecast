#!/usr/bin/env python3
"""Generate preview.png (1200x630) for F1 Strategy Battle OG meta tag."""

import os
import struct
import zlib

W, H = 1200, 630


def pack_png(pixels):
    """Minimal PNG encoder — no external deps."""

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    raw = b""
    for row in pixels:
        raw += b"\x00" + bytes([v for rgb in row for v in rgb])

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    idat = zlib.compress(raw, 9)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


# ── Colour palette ────────────────────────────────────────────────────────────
BG = hex_to_rgb("#080810")
PURPLE1 = hex_to_rgb("#7c3aed")
PURPLE2 = hex_to_rgb("#a78bfa")
ORANGE = hex_to_rgb("#FF6B35")
GOLD = hex_to_rgb("#FFD700")
MUTED = hex_to_rgb("#3a3a55")
WHITE = hex_to_rgb("#f0f0f0")
DIM = hex_to_rgb("#888899")
GRID_C = (14, 14, 22)

# ── Build pixel buffer ────────────────────────────────────────────────────────
pixels = [[BG] * W for _ in range(H)]


def fill_rect(x0, y0, x1, y1, color):
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            pixels[y][x] = color


def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def gradient_rect(x0, y0, x1, y1, c1, c2, horizontal=True):
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            t = (x - x0) / max(1, x1 - x0) if horizontal else (y - y0) / max(1, y1 - y0)
            pixels[y][x] = lerp_color(c1, c2, t)


# Grid lines
for x in range(0, W, 40):
    for y in range(0, H):
        r, g, b = pixels[y][x]
        pixels[y][x] = (min(255, r + 6), min(255, g + 6), min(255, b + 8))
for y in range(0, H, 40):
    for x in range(0, W):
        r, g, b = pixels[y][x]
        pixels[y][x] = (min(255, r + 6), min(255, g + 6), min(255, b + 8))

# Top accent bar (gradient)
gradient_rect(0, 0, W, 5, PURPLE1, PURPLE2)

# Bottom accent bar
fill_rect(0, H - 4, W, H, MUTED)

# Left vertical accent stripe
gradient_rect(0, 5, 5, H - 4, PURPLE1, PURPLE2, horizontal=False)

# ── Text rendering via bitmap font ────────────────────────────────────────────
# 5×7 bitmask font for ASCII 32–126
FONT5 = {
    " ": [0x00, 0x00, 0x00, 0x00, 0x00],
    "A": [0x7C, 0x12, 0x12, 0x12, 0x7C],
    "B": [0x7E, 0x4A, 0x4A, 0x4A, 0x34],
    "C": [0x3C, 0x42, 0x42, 0x42, 0x24],
    "D": [0x7E, 0x42, 0x42, 0x24, 0x18],
    "E": [0x7E, 0x4A, 0x4A, 0x4A, 0x42],
    "F": [0x7E, 0x0A, 0x0A, 0x0A, 0x02],
    "G": [0x3C, 0x42, 0x42, 0x52, 0x34],
    "H": [0x7E, 0x08, 0x08, 0x08, 0x7E],
    "I": [0x42, 0x42, 0x7E, 0x42, 0x42],
    "J": [0x20, 0x40, 0x42, 0x3E, 0x00],
    "K": [0x7E, 0x08, 0x14, 0x22, 0x40],
    "L": [0x7E, 0x40, 0x40, 0x40, 0x40],
    "M": [0x7E, 0x04, 0x08, 0x04, 0x7E],
    "N": [0x7E, 0x04, 0x08, 0x10, 0x7E],
    "O": [0x3C, 0x42, 0x42, 0x42, 0x3C],
    "P": [0x7E, 0x12, 0x12, 0x12, 0x0C],
    "Q": [0x3C, 0x42, 0x52, 0x22, 0x5C],
    "R": [0x7E, 0x12, 0x32, 0x52, 0x0C],
    "S": [0x24, 0x4A, 0x4A, 0x4A, 0x30],
    "T": [0x02, 0x02, 0x7E, 0x02, 0x02],
    "U": [0x3E, 0x40, 0x40, 0x40, 0x3E],
    "V": [0x1E, 0x20, 0x40, 0x20, 0x1E],
    "W": [0x7E, 0x20, 0x10, 0x20, 0x7E],
    "X": [0x62, 0x14, 0x08, 0x14, 0x62],
    "Y": [0x06, 0x08, 0x70, 0x08, 0x06],
    "Z": [0x62, 0x52, 0x4A, 0x46, 0x42],
    "0": [0x3C, 0x46, 0x4A, 0x62, 0x3C],
    "1": [0x40, 0x42, 0x7E, 0x40, 0x40],
    "2": [0x64, 0x52, 0x52, 0x52, 0x4C],
    "3": [0x24, 0x42, 0x4A, 0x4A, 0x34],
    "4": [0x0E, 0x08, 0x08, 0x7E, 0x08],
    "5": [0x2E, 0x4A, 0x4A, 0x4A, 0x32],
    "6": [0x3C, 0x4A, 0x4A, 0x4A, 0x30],
    "7": [0x02, 0x62, 0x12, 0x0A, 0x06],
    "8": [0x34, 0x4A, 0x4A, 0x4A, 0x34],
    "9": [0x0C, 0x52, 0x52, 0x52, 0x3C],
    ".": [0x00, 0x60, 0x60, 0x00, 0x00],
    ",": [0x00, 0x50, 0x30, 0x00, 0x00],
    ":": [0x00, 0x36, 0x36, 0x00, 0x00],
    "!": [0x00, 0x00, 0x5E, 0x00, 0x00],
    "?": [0x04, 0x02, 0x52, 0x0A, 0x04],
    "-": [0x08, 0x08, 0x08, 0x08, 0x08],
    "·": [0x00, 0x18, 0x18, 0x00, 0x00],
    "_": [0x40, 0x40, 0x40, 0x40, 0x40],
    "#": [0x14, 0x7F, 0x14, 0x7F, 0x14],
    "/": [0x20, 0x10, 0x08, 0x04, 0x02],
    "\\": [0x02, 0x04, 0x08, 0x10, 0x20],
    "(": [0x00, 0x3E, 0x41, 0x00, 0x00],
    ")": [0x00, 0x00, 0x41, 0x3E, 0x00],
    "+": [0x08, 0x08, 0x3E, 0x08, 0x08],
    "=": [0x14, 0x14, 0x14, 0x14, 0x14],
    "@": [0x3C, 0x42, 0x5A, 0x56, 0x1C],
    "&": [0x34, 0x4A, 0x34, 0x60, 0x50],
}


def draw_char(ch, cx, cy, color, scale=1):
    bits = FONT5.get(ch.upper(), FONT5[" "])
    for col in range(5):
        byte = bits[col]
        for row in range(7):
            if byte & (1 << row):
                for sy in range(scale):
                    for sx in range(scale):
                        px = cx + col * scale + sx
                        py = cy + row * scale + sy
                        if 0 <= px < W and 0 <= py < H:
                            pixels[py][px] = color


def draw_text(text, x, y, color, scale=1, spacing=1):
    cx = x
    for ch in text:
        draw_char(ch, cx, y, color, scale)
        cx += (5 + spacing) * scale
    return cx  # returns end x


def text_width(text, scale=1, spacing=1):
    return len(text) * (5 + spacing) * scale


# ── Layout ─────────────────────────────────────────────────────────────────────

# Top label
label = "F1 STRATEGY BATTLE"
lw = text_width(label, scale=4, spacing=2)
draw_text(label, (W - lw) // 2, 60, PURPLE2, scale=4, spacing=2)

# Separator line
gradient_rect((W - 480) // 2, 100, (W + 480) // 2, 102, PURPLE1, PURPLE2)

# Subtitle
sub = "SILVERSTONE GP  ·  2026"
sw = text_width(sub, scale=2, spacing=2)
draw_text(sub, (W - sw) // 2, 118, DIM, scale=2, spacing=2)

# Big "VS REMIN" text
vs1 = "YOU"
vs2 = "VS"
vs3 = "REMIN"
v1w = text_width(vs1, scale=6, spacing=2)
v2w = text_width(vs2, scale=4, spacing=2)
v3w = text_width(vs3, scale=6, spacing=2)
spacing_h = 40
total_vs = v1w + spacing_h + v2w + spacing_h + v3w
sx = (W - total_vs) // 2
draw_text(vs1, sx, 180, WHITE, scale=6, spacing=2)
sx += v1w + spacing_h
draw_text(vs2, sx, 192, DIM, scale=4, spacing=2)
sx += v2w + spacing_h
draw_text(vs3, sx, 180, ORANGE, scale=6, spacing=2)

# Divider
gradient_rect((W - 600) // 2, 290, (W + 600) // 2, 292, MUTED, PURPLE1)

# Three columns: Strategies, Score, Challenge
col_labels = ["YOUR STRATEGY", "STRATEGY IQ", "BEAT REMIN?"]
col_x = [180, 520, 860]
col_vals = ["S → M → H", "UP TO 100", "CHALLENGE\nFRIENDS"]

for i, (lbl, val, cx) in enumerate(zip(col_labels, col_vals, col_x)):
    lw2 = text_width(lbl, scale=1, spacing=1)
    draw_text(lbl, cx - lw2 // 2, 318, DIM, scale=1, spacing=1)
    lines = val.split("\n")
    for li, line in enumerate(lines):
        vw = text_width(line, scale=3, spacing=2)
        clr = [GOLD, PURPLE2, hex_to_rgb("#34d399")][i]
        draw_text(line, cx - vw // 2, 340 + li * 36, clr, scale=3, spacing=2)

# Bottom divider
gradient_rect((W - 600) // 2, 445, (W + 600) // 2, 447, PURPLE1, MUTED)


# Tyre compound circles (decorative)
def dot(cx, cy, r, color, border=None):
    r2 = r * r
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r2:
                if 0 <= cx + dx < W and 0 <= cy + dy < H:
                    pixels[cy + dy][cx + dx] = color
    if border:
        br = (r - 1) ** 2
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                d2 = dx * dx + dy * dy
                if br < d2 <= r2:
                    if 0 <= cx + dx < W and 0 <= cy + dy < H:
                        pixels[cy + dy][cx + dx] = border


tyre_y = 490
dot(W // 2 - 60, tyre_y, 22, hex_to_rgb("#1a1a2e"), hex_to_rgb("#E8002D"))
dot(W // 2, tyre_y, 22, hex_to_rgb("#1a1a2e"), hex_to_rgb("#FFD700"))
dot(W // 2 + 60, tyre_y, 22, hex_to_rgb("#1a1a2e"), hex_to_rgb("#888888"))

compound_labels = [("S", W // 2 - 60), ("M", W // 2), ("H", W // 2 + 60)]
for ch, cx in compound_labels:
    cw = text_width(ch, scale=2, spacing=1)
    draw_text(ch, cx - cw // 2, tyre_y - 8, WHITE, scale=2, spacing=1)

# Bottom tagline
tag = "remin-franklin-eliyas.github.io/f1-forecast"
tw = text_width(tag, scale=1, spacing=1)
draw_text(tag, (W - tw) // 2, 548, MUTED, scale=1, spacing=1)

# ── Write PNG ─────────────────────────────────────────────────────────────────
out = os.path.join(os.path.dirname(__file__), "preview.png")
with open(out, "wb") as f:
    f.write(pack_png(pixels))

print(f"Written {out}  ({os.path.getsize(out) // 1024} KB)")
