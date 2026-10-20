"""Renderizadores de escena. Cada uno dibuja el fotograma del instante `t` (segundos)."""
import math
from datetime import date
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from .style import (ACCENTS, ANTHRACITE, BONE, CARBON, GOLD, GREEN, GREY, GREY_LIGHT, H, LINE,
                    MARGIN, RED, W, appear, background, ease, ease_io, fmt_int, font, glow, mix,
                    rect, text, tracked, wrap)

MONTHS = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


class Ctx:
    """Contexto de una escena: duración, palabras temporizadas, datos y raíz del episodio."""

    def __init__(self, dur, words, data, root, chapter_label, chapter_num, scene):
        self.dur, self.words, self.data, self.root = dur, words, data, root
        self.chapter_label, self.chapter_num, self.scene = chapter_label, chapter_num, scene
        self.tag = None      # "ILUSTRACIÓN", "RECREACIÓN", etc.
        self.note = None     # fuente o aclaración al pie

    def word_time(self, needle, default):
        """Momento en que la voz pronuncia `needle` (para sincronizar apariciones)."""
        n = needle.lower().strip("¿?¡!.,:;")
        for w in self.words:
            if w["text"].lower().strip("¿?¡!.,:;\"'") .startswith(n[:6]):
                return w["start"]
        return default


# ───────────────────────────── chrome común ─────────────────────────────

def chrome(img, ctx, t):
    a = appear(t, 0.0, 0.5)
    text(img, (MARGIN, 70), tracked(f"{ctx.chapter_num:02d}  ·  {ctx.chapter_label}"), font("sans-medium", 20), GREY, a)
    text(img, (W - MARGIN, 70), tracked("Mundo Dinero"), font("sans-bold", 20), GOLD, a, anchor="ra")
    if ctx.tag:
        f = font("sans-semibold", 18)
        s = tracked(ctx.tag)
        tw = f.getlength(s)
        rect(img, (W - MARGIN - tw - 28, 108, W - MARGIN, 144), outline=GREY, width=1, alpha=a * 0.9, radius=3)
        text(img, (W - MARGIN - 14, 126), s, f, GREY_LIGHT, a, anchor="rm")
    if ctx.note:
        text(img, (MARGIN, H - 64), ctx.note, font("sans", 20), GREY, a * 0.95, anchor="ls")


# ───────────────────────────── tipografía ─────────────────────────────

def r_title(img, t, s, ctx):
    acc = ACCENTS.get(s.get("accent"), GOLD)
    cx, cy = W // 2, H // 2 - 20
    a1, a2, a3 = appear(t, 0.1), appear(t, 0.35, 0.8), appear(t, 0.9, 0.8)
    text(img, (cx, cy - 120), tracked(s.get("kicker", "")), font("sans-semibold", 26), acc, a1, anchor="mm")
    hl = wrap(s["headline"], font("serif", 120), W - 2 * MARGIN - 100)
    text(img, (cx, cy + 10), hl, font("serif", 120), BONE, a2, anchor="mm", dy=(1 - a2) * 30, align="center")
    lw = 260 * ease((t - 0.6) / 1.0)
    if lw > 1:
        rect(img, (cx - lw / 2, cy + 120 + (hl.count("\n") * 60), cx + lw / 2, cy + 123 + (hl.count("\n") * 60)), fill=acc)
    if s.get("sub"):
        text(img, (cx, cy + 175 + hl.count("\n") * 60), s["sub"], font("serif-italic", 44), GREY_LIGHT, a3, anchor="mm")


def r_statement(img, t, s, ctx):
    acc = ACCENTS.get(s.get("accent"), BONE)
    size = 118 if s.get("big") else 96
    f = font("serif", size)
    body = wrap(s["text"], f, W - 2 * MARGIN - 120)
    a = appear(t, 0.1, 0.9)
    cy = H // 2 - (40 if s.get("sub") else 0)
    color = acc if s.get("accent") == "red" or s.get("big") else BONE
    text(img, (W // 2, cy), body, f, color, a, anchor="mm", dy=(1 - a) * 24, align="center", spacing=14)
    lines = body.count("\n") + 1
    if s.get("sub"):
        text(img, (W // 2, cy + lines * size * 0.6 + 70), s["sub"], font("serif-italic", 46), GREY_LIGHT,
             appear(t, 0.9, 0.8), anchor="mm")
    if s.get("accent") in ("red", "green"):
        lw = 180 * ease((t - 0.5) / 0.8)
        y = cy - lines * size * 0.6 - 50
        if lw > 1:
            rect(img, (W // 2 - lw / 2, y, W // 2 + lw / 2, y + 4), fill=ACCENTS[s["accent"]])


def r_definition(img, t, s, ctx):
    x = MARGIN + 60
    a1, a2, a3 = appear(t, 0.1, 0.7), appear(t, 0.6, 0.7), appear(t, 1.2, 0.8)
    text(img, (x, 330), s["term"], font("sans-black", 210), BONE, a1, dy=(1 - a1) * 30)
    rect(img, (x, 600, x + 140 * a2, 605), fill=GREEN)
    text(img, (x, 640), tracked(s["full"]), font("sans-semibold", 28), GREEN, a2)
    text(img, (x, 710), wrap(s["meaning"], font("serif-regular", 58), 1300), font("serif-regular", 58), GREY_LIGHT, a3,
         spacing=12)


# ───────────────────────────── cifras ─────────────────────────────

def r_invest(img, t, s, ctx):
    ctx.note = s.get("note")
    ctx.tag = "Simulación"
    p = ease_io((t - 1.2) / max(1.0, ctx.dur * 0.55))
    val = s["from"] + (s["to"] - s["from"]) * p
    x0 = MARGIN + 60
    text(img, (x0, 250), tracked(s["label_from"]), font("sans-semibold", 26), GREY, appear(t, 0.1))
    text(img, (x0, 290), f"US$ {fmt_int(s['from'])}", font("sans-black", 96), BONE, appear(t, 0.2))
    a = appear(t, 0.8)
    text(img, (x0, 520), tracked(s["label_to"]), font("sans-semibold", 26), GREY, a)
    col = mix(BONE, RED, p)
    if p > 0.6:
        glow(img, (x0, 580, x0 + 600, 690), RED, 0.18 * (p - 0.6) / 0.4, 50)
    text(img, (x0, 560), f"US$ {fmt_int(val)}", font("sans-black", 150), col, a)
    # barras proporcionales
    bx, bw, by = 1180, 520, 300
    full_h = 520
    rect(img, (bx, by + full_h - full_h, bx + 200, by + full_h), fill=LINE, alpha=appear(t, 0.3))
    h2 = full_h * (val / s["from"])
    rect(img, (bx + 280, by + full_h - h2, bx + 480, by + full_h), fill=col, alpha=a)
    text(img, (bx + 100, by + full_h + 30), "Máximo", font("sans-medium", 24), GREY, appear(t, 0.3), anchor="ma")
    text(img, (bx + 380, by + full_h + 30), "Mínimo", font("sans-medium", 24), GREY, a, anchor="ma")
    pct = (1 - s["to"] / s["from"]) * 100 * p
    if p > 0.05:
        text(img, (bx + 380, by + full_h - h2 - 20), f"−{pct:.1f} %".replace(".", ","), font("sans-bold", 34), RED,
             a, anchor="ms")


def r_counter(img, t, s, ctx):
    acc = ACCENTS.get(s.get("accent"), GREEN)
    p = ease((t - 0.3) / max(1.0, ctx.dur * 0.6))
    v = s["value"] * p
    f = font("sans-black", 190)
    label = f"{s.get('prefix', '')}{fmt_int(v)}"
    text(img, (W // 2, H // 2 - 40), label, f, BONE, appear(t, 0.1), anchor="mm")
    text(img, (W // 2, H // 2 + 100), tracked(s.get("suffix", "").strip()), font("sans-semibold", 34), acc, appear(t, 0.4),
         anchor="mm")
    text(img, (W // 2, H // 2 + 180), s["label"], font("serif-italic", 44), GREY_LIGHT, appear(t, 0.8), anchor="mm")


def r_checklist(img, t, s, ctx):
    acc = ACCENTS.get(s.get("accent"), GOLD)
    items = s["items"]
    n = len(items)
    f = font("serif", 64 if n <= 3 else 52)
    step = 120 if n <= 3 else 92
    y0 = H // 2 - (n - 1) * step / 2
    span = max(1.0, ctx.dur * 0.75)
    for i, it in enumerate(items):
        st = ctx.word_time(it.split()[0], 0.3 + i * span / n) - 0.1
        a = appear(t, st, 0.5)
        y = y0 + i * step
        rect(img, (MARGIN + 160, y - 6, MARGIN + 172, y + 6), fill=acc, alpha=a)
        text(img, (MARGIN + 210, y), it, f, BONE, a, anchor="lm", dy=(1 - a) * 16)


def r_calendar(img, t, s, ctx):
    a0, a1 = s["from"], s["to"]
    p = ease_io((t - 0.4) / max(1.0, ctx.dur * 0.7))
    yr = a0 + (a1 - a0) * p
    text(img, (W // 2, 250), tracked(s["label"]), font("sans-semibold", 28), GREY, appear(t, 0.1), anchor="mm")
    text(img, (W // 2, H // 2 - 40), str(int(yr)), font("sans-black", 260), BONE, appear(t, 0.1), anchor="mm")
    # regla de años
    n = a1 - a0
    x0, x1, y = MARGIN + 100, W - MARGIN - 100, 760
    rect(img, (x0, y, x1, y + 2), fill=LINE)
    rect(img, (x0, y - 1, x0 + (x1 - x0) * p, y + 3), fill=RED)
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / max(1, n)
        on = p * n >= i - 0.01
        rect(img, (x - 5, y - 5, x + 5, y + 7), fill=RED if on else GREY)
        text(img, (x, y + 30), str(a0 + i), font("sans-medium", 24), BONE if on else GREY, 1, anchor="ma")
    ev = s.get("events") or {}
    for k, v in ev.items():
        k = int(k)
        if yr >= k:
            x = x0 + (x1 - x0) * (k - a0) / max(1, n)
            text(img, (x, y - 30), v, font("sans", 22), GREY_LIGHT, appear(yr, k, 0.6), anchor="ms")
    if p > 0.97 and s.get("result"):
        text(img, (W // 2, 900), s["result"], font("serif", 64), RED, appear(t, 0.4 + ctx.dur * 0.7, 0.5), anchor="mm")


def r_runway(img, t, s, ctx):
    ctx.note = s.get("note")
    text(img, (W // 2, 260), tracked(s["label"]), font("sans-semibold", 28), GREY, appear(t, 0.1), anchor="mm")
    x0, size, gap = (W - (12 * 100 + 11 * 18)) // 2, 100, 18
    p = ease((t - 0.4) / 1.8)
    for i in range(12):
        x = x0 + i * (size + gap)
        on = i == 0
        fade = 1 - p if not on else 1
        rect(img, (x, 430, x + size, 530), fill=RED if on else ANTHRACITE, outline=None if on else LINE, width=2,
             alpha=max(0.12, fade) if not on else appear(t, 0.2))
        text(img, (x + size / 2, 560), MONTHS[i], font("sans-medium", 22), GREY, 1, anchor="ma")
    text(img, (W // 2, 720), s["value"], font("serif", 86), BONE, appear(t, 1.6, 0.8), anchor="mm")


# ───────────────────────────── tiempo y lugar ─────────────────────────────

def r_timeline(img, t, s, ctx):
    acc = ACCENTS.get(s.get("accent"), GOLD)
    items = s["items"]
    n = len(items)
    x0, x1, y = MARGIN + 120, W - MARGIN - 120, H // 2 + 20
    p = ease((t - 0.2) / 1.4)
    rect(img, (x0, y - 1, x0 + (x1 - x0) * p, y + 1), fill=GREY)
    for i, (yr, lab) in enumerate(items):
        x = x0 + (x1 - x0) * (i / max(1, n - 1))
        a = appear(t, 0.3 + i * 0.35)
        foc = i == s.get("focus")
        c = acc if foc else GREY_LIGHT
        r = 14 if foc else 8
        rect(img, (x - r, y - r, x + r, y + r), fill=c, alpha=a, radius=r)
        text(img, (x, y - 50), yr, font("sans-black" if foc else "sans-bold", 64 if foc else 44), BONE if foc else GREY_LIGHT,
             a, anchor="ms")
        text(img, (x, y + 50), wrap(lab, font("sans-medium", 30), 360), font("sans-medium", 30), c, a, anchor="ma",
             align="center")


CALIFORNIA = [(-124.2, 42.0), (-120.0, 42.0), (-120.0, 39.0), (-114.6, 35.1), (-114.5, 32.7), (-117.1, 32.5),
              (-117.4, 33.3), (-118.4, 33.8), (-119.2, 34.1), (-120.6, 34.5), (-120.9, 35.4), (-121.9, 36.6),
              (-122.0, 37.0), (-122.5, 37.6), (-122.5, 37.9), (-123.0, 38.3), (-123.8, 39.0), (-123.8, 39.8),
              (-124.4, 40.4), (-124.1, 41.0), (-124.2, 42.0)]


def r_location(img, t, s, ctx):
    ctx.tag = "Mapa esquemático"
    # proyección simple lon/lat → píxeles
    def P(lon, lat):
        return 1050 + (lon + 124.5) * 70, 140 + (42.2 - lat) * 80
    p = ease((t - 0.1) / 1.5)
    pts = [P(*c) for c in CALIFORNIA]
    k = max(2, int(len(pts) * p))
    layer = Image.new("L", (W, H), 0)
    ld = ImageDraw.Draw(layer)
    if p > 0.98:
        ld.polygon(pts, fill=40)
    img.paste(Image.new("RGB", (W, H), GREY), (0, 0), layer)
    ImageDraw.Draw(img).line(pts[:k], fill=GREY_LIGHT, width=3, joint="curve")
    px, py = P(-121.89, 37.34)
    a = appear(t, 1.2)
    pulse = (math.sin(t * 3) + 1) / 2
    rr = 14 + 18 * pulse
    rect(img, (px - rr, py - rr, px + rr, py + rr), outline=GOLD, width=2, alpha=a * (1 - pulse * 0.7), radius=int(rr))
    rect(img, (px - 9, py - 9, px + 9, py + 9), fill=GOLD, alpha=a, radius=9)
    text(img, (px - 30, py), "San José", font("sans-semibold", 30), BONE, a, anchor="rm")
    x = MARGIN + 40
    text(img, (x, 360), tracked(s["date"]), font("sans-semibold", 30), GOLD, appear(t, 0.3))
    text(img, (x, 410), wrap(s["place"], font("serif", 96), 760), font("serif", 96), BONE, appear(t, 0.5))
    text(img, (x, 650), s.get("coords", ""), font("sans-light", 28), GREY, appear(t, 0.9))


def r_people(img, t, s, ctx):
    names, roles = s["names"], s.get("roles", [""] * len(s["names"]))
    n = len(names)
    cw, gap = 440, 60
    x0 = (W - (n * cw + (n - 1) * gap)) // 2
    text(img, (W // 2, 240), tracked(s.get("caption", "")), font("sans-semibold", 26), GREY, appear(t, 0.1), anchor="mm")
    photos = s.get("photos") or [None] * n
    for i, nm in enumerate(names):
        st = ctx.word_time(nm.split()[0], 0.3 + i * 0.6) - 0.15
        a = appear(t, st, 0.6)
        x = x0 + i * (cw + gap)
        rect(img, (x, 320, x + cw, 820), fill=ANTHRACITE, alpha=a, radius=6)
        ph = photos[i] and (ctx.root / photos[i])
        cx, cy = x + cw // 2, 500
        if ph and ph.exists():
            im = Image.open(ph).convert("RGB")
            im = _cover(im, 300, 300)
            m = Image.new("L", (300, 300), 0)
            ImageDraw.Draw(m).ellipse((0, 0, 300, 300), fill=int(255 * a))
            img.paste(im, (cx - 150, cy - 150), m)
        else:
            initials = "".join(p[0] for p in nm.split()[:2])
            rect(img, (cx - 120, cy - 120, cx + 120, cy + 120), outline=GOLD, width=3, alpha=a, radius=120)
            text(img, (cx, cy), initials, font("serif", 110), GOLD, a, anchor="mm")
        text(img, (cx, 700), nm, font("serif", 46), BONE, a, anchor="mm")
        text(img, (cx, 760), tracked(roles[i]), font("sans-medium", 20), GREY, a, anchor="mm")


# ───────────────────────────── producto ─────────────────────────────

def _cover(im, w, h):
    r = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def _chip(img, cx, cy, size, label, a, t):
    """Ilustración esquemática de un chip (no es una foto del producto)."""
    s2 = size // 2
    for i in range(14):
        off = -s2 + 30 + i * (size - 60) / 13
        for (x0, y0, x1, y1) in [(cx + off - 4, cy - s2 - 40, cx + off + 4, cy - s2),
                                 (cx + off - 4, cy + s2, cx + off + 4, cy + s2 + 40),
                                 (cx - s2 - 40, cy + off - 4, cx - s2, cy + off + 4),
                                 (cx + s2, cy + off - 4, cx + s2 + 40, cy + off + 4)]:
            rect(img, (x0, y0, x1, y1), fill=(120, 110, 80), alpha=a)
    rect(img, (cx - s2, cy - s2, cx + s2, cy + s2), fill=(34, 36, 40), outline=LINE, width=3, alpha=a, radius=10)
    rect(img, (cx - s2 + 50, cy - s2 + 50, cx + s2 - 50, cy + s2 - 50), outline=(60, 63, 68), width=2, alpha=a, radius=6)
    sweep = (t * 0.25) % 1.0
    yy = cy - s2 + 50 + (size - 100) * sweep
    rect(img, (cx - s2 + 52, yy, cx + s2 - 52, yy + 2), fill=(70, 74, 80), alpha=a)
    text(img, (cx, cy), label, font("sans-bold", int(size * 0.17)), GREY_LIGHT, a, anchor="mm")


def r_product(img, t, s, ctx):
    ph = s.get("image") and (ctx.root / s["image"])
    a = appear(t, 0.1, 0.8)
    if ph and ph.exists():
        im = Image.open(ph).convert("RGB")
        z = 1.0 + 0.06 * (t / max(ctx.dur, 0.1))       # Ken Burns suave
        tw, th = int(880 * z), int(660 * z)
        im = _cover(im, tw, th).crop(((tw - 880) // 2, (th - 660) // 2, (tw - 880) // 2 + 880, (th - 660) // 2 + 660))
        m = Image.new("L", im.size, int(255 * a))
        img.paste(im, (W - MARGIN - 880, 220), m)
        ctx.note = s.get("credit")
    else:
        ctx.tag = "Ilustración"
        _chip(img, W - MARGIN - 420, H // 2 + 10, 460, s["name"], a, t)
    x = MARGIN + 40
    text(img, (x, 360), tracked(s.get("year", "")), font("sans-semibold", 30), GREEN, appear(t, 0.2))
    text(img, (x, 410), s["name"], font("sans-black", 130), BONE, appear(t, 0.35), dy=(1 - appear(t, 0.35)) * 20)
    text(img, (x, 580), wrap(s.get("detail", ""), font("serif-italic", 44), 700), font("serif-italic", 44), GREY_LIGHT,
         appear(t, 0.8))


# ───────────────────────────── gráfico bursátil ─────────────────────────────

def _series(ctx, start, end):
    key = ctx.scene["visual"].get("series") or next(k for k in ctx.data if not k.endswith("_source") and k != "note")
    rows = [r for r in ctx.data[key] if start <= r[0][:7] <= end]
    return rows


def _month_idx(rows, ym):
    for i, r in enumerate(rows):
        if r[0][:7] >= ym:
            return i
    return len(rows) - 1


def r_chart(img, t, s, ctx):
    key = s.get("series") or next(k for k in ctx.data if not k.endswith("_source") and k != "note")
    ctx.note = " · ".join(x for x in (ctx.data.get(key + "_source"), s.get("note") or ctx.data.get("note")) if x)
    rows = _series(ctx, s["start"], s["end"])
    vals = np.array([r[1] for r in rows], dtype=float)
    logy = s.get("log", False)
    yv = np.log10(vals) if logy else vals
    lo, hi = yv.min(), yv.max()
    padv = (hi - lo) * 0.12
    lo, hi = lo - padv, hi + padv
    X0, X1, Y0, Y1 = MARGIN + 40, W - MARGIN - 40, 220, 880
    n = len(rows)

    def X(i):
        return X0 + (X1 - X0) * i / max(1, n - 1)

    def Y(v):
        return Y1 - (Y1 - Y0) * (v - lo) / (hi - lo)

    pts = [(X(i), Y(v)) for i, v in enumerate(yv)]
    # rejilla y años
    d = ImageDraw.Draw(img)
    for k in range(5):
        y = Y0 + (Y1 - Y0) * k / 4
        d.line((X0, y, X1, y), fill=(32, 34, 38), width=1)
    years = sorted({r[0][:4] for r in rows})
    stepy = max(1, len(years) // 9)
    last_x = -1e9
    for yy in years[::stepy]:
        i = _month_idx(rows, yy + "-01")
        if rows[i][0][:4] == yy and X(i) - last_x > 90:
            text(img, (X(i), Y1 + 24), yy, font("sans-medium", 22), GREY, 1, anchor="ma")
            last_x = X(i)
    text(img, (X0, Y0 - 40), tracked(s.get("label", "")), font("sans-semibold", 24), GREY_LIGHT, appear(t, 0.0))
    if logy:
        text(img, (X1, Y0 - 40), "escala logarítmica", font("sans", 20), GREY, 1, anchor="ra")

    # zonas sombreadas (períodos bajo el máximo)
    for a_, b_ in s.get("shade", []):
        ia, ib = _month_idx(rows, a_), _month_idx(rows, b_)
        al = appear(t, 1.2, 0.8)
        rect(img, (X(ia), Y0, X(ib), Y1), fill=(60, 26, 26), alpha=al * 0.8)

    # revelado progresivo de la línea
    reveal_end = max(1.2, min(ctx.dur * 0.6, 4.5))
    p = ease_io((t - 0.2) / reveal_end)
    k = p * (n - 1)
    ki = int(k)
    shown = pts[:ki + 1]
    if ki < n - 1:
        fx = k - ki
        shown = shown + [(pts[ki][0] + (pts[ki + 1][0] - pts[ki][0]) * fx, pts[ki][1] + (pts[ki + 1][1] - pts[ki][1]) * fx)]
    # tramo en rojo si hay caída
    drop = s.get("drop")
    if len(shown) >= 2:
        layer = Image.new("L", (W, H), 0)
        ImageDraw.Draw(layer).polygon(shown + [(shown[-1][0], Y1), (shown[0][0], Y1)], fill=28)
        img.paste(Image.new("RGB", (W, H), BONE), (0, 0), layer)
        d.line(shown, fill=BONE, width=4, joint="curve")
        if drop:
            ia, ib = _month_idx(rows, drop["from"]), _month_idx(rows, drop["to"])
            seg = pts[ia:min(ib + 1, ki + 1)]
            if len(seg) >= 2:
                d.line(seg, fill=RED, width=6, joint="curve")
        hx, hy = shown[-1]
        rect(img, (hx - 7, hy - 7, hx + 7, hy + 7), fill=BONE, radius=7)

    # línea horizontal del máximo previo
    if s.get("hline"):
        ih = _month_idx(rows, s["hline"])
        yh = pts[ih][1]
        ah = appear(t, 0.6)
        x = X(ih)
        while x < X1:
            rect(img, (x, yh - 1, min(x + 14, X1), yh + 1), fill=GREY_LIGHT, alpha=ah * 0.8)
            x += 26

    # marcas
    for m in s.get("marks", []):
        i = _month_idx(rows, m["date"])
        if i > k + 0.01:
            continue
        col = ACCENTS.get(m.get("color"), BONE)
        a = appear(t, 0.2 + reveal_end * (i / max(1, n - 1)), 0.5)
        x, y = pts[i]
        rect(img, (x - 11, y - 11, x + 11, y + 11), outline=col, width=3, alpha=a, radius=11)
        nb = [pts[j][1] for j in (i - 2, i + 2) if 0 <= j < n] or [y]
        above = y <= sum(nb) / len(nb) or y > Y1 - 60      # máximos: arriba · mínimos: abajo
        if y < Y0 + 90:
            above = False
        ty = y - 34 if above else y + 40
        anchor = "ms" if above else "ma"
        tx = min(max(x, X0 + 150), X1 - 150)
        text(img, (tx, ty), m["text"], font("sans-semibold", 28), col, a, anchor=anchor)

    # etiqueta de caída
    if drop:
        ib = _month_idx(rows, drop["to"])
        if k >= ib:
            a = appear(t, 0.2 + reveal_end * (ib / max(1, n - 1)) + 0.2, 0.6)
            ia = _month_idx(rows, drop["from"])
            x = (X(ia) + X(ib)) / 2 + 60
            y = (pts[ia][1] + pts[ib][1]) / 2
            glow(img, (x - 10, y - 50, x + 330, y + 50), RED, 0.15 * a, 40)
            text(img, (x, y), drop["text"], font("sans-black", 110), RED, a, anchor="lm")


# ───────────────────────────── diagramas ─────────────────────────────

def r_diagram(img, t, s, ctx):
    kind = s["kind"]
    ctx.tag = "Esquema"
    if s.get("label"):
        text(img, (W // 2, H - 150), s["label"], font("serif-italic", 42), GREY_LIGHT, appear(t, 0.6), anchor="mm")
    DIAGRAMS[kind](img, t, s, ctx)


def d_datacenter(img, t, s, ctx):
    cols, rws = 14, 6
    w, h, gx, gy = 96, 64, 18, 22
    x0 = (W - (cols * w + (cols - 1) * gx)) // 2
    y0 = 230
    total = cols * rws
    lit = ease((t - 0.2) / max(1.0, ctx.dur * 0.7)) * total
    rng = np.random.default_rng(3)
    order = rng.permutation(total)
    rank = np.empty(total, int)
    rank[order] = np.arange(total)
    for r in range(rws):
        for c in range(cols):
            i = r * cols + c
            x, y = x0 + c * (w + gx), y0 + r * (h + gy)
            on = rank[i] < lit
            rect(img, (x, y, x + w, y + h), fill=ANTHRACITE, outline=LINE, width=2, radius=4)
            for j in range(3):
                ly = y + 16 + j * 16
                rect(img, (x + 12, ly, x + w - 30, ly + 4), fill=(48, 51, 56))
                blink = on and (math.sin(t * 5 + i * 1.7 + j) > -0.3)
                rect(img, (x + w - 20, ly - 1, x + w - 12, ly + 5), fill=GREEN if blink else (50, 52, 56))


def d_crowd(img, t, s, ctx):
    ctx.note = s.get("note")
    cols, rws = 12, 4
    w, gx = 110, 26
    x0 = (W - (cols * w + (cols - 1) * gx)) // 2
    rng = np.random.default_rng(11)
    for r in range(rws):
        for c in range(cols):
            i = r * cols + c
            a = appear(t, 0.1 + i * 0.03, 0.4)
            x, y = x0 + c * (w + gx), 240 + r * (w + 36)
            shade = 0.45 + 0.5 * rng.random()
            rect(img, (x, y, x + w, y + w), fill=mix(CARBON, (70, 74, 80), shade), outline=LINE, alpha=a, radius=6)
            text(img, (x + w / 2, y + w / 2), "?", font("serif", 44), GREY, a * 0.7, anchor="mm")


def d_fork(img, t, s, ctx):
    d = ImageDraw.Draw(img)
    sx, sy = 360, 560
    p = ease((t - 0.2) / 1.6)
    ex1, ey1 = 1100, 360
    ex2, ey2 = 1100, 760
    rect(img, (sx - 12, sy - 12, sx + 12, sy + 12), fill=BONE, radius=12)
    text(img, (sx, sy + 50), "Gráficos 3D en PC · 1995", font("sans-medium", 26), GREY, appear(t, 0.1), anchor="ma")
    # camino ganador
    d.line((sx, sy, sx + (ex1 - sx) * p, sy + (ey1 - sy) * p), fill=BONE, width=6)
    # camino de NV1 (se apaga)
    p2 = ease((t - 0.4) / 1.6)
    fade = 1 - 0.6 * ease((t - 2.4) / 1.0)
    col2 = mix(CARBON, RED, fade)
    d.line((sx, sy, sx + (ex2 - sx) * p2 * 0.8, sy + (ey2 - sy) * p2 * 0.8), fill=col2, width=6)
    a = appear(t, 1.6)
    text(img, (ex1 + 40, ey1 - 6), s["right"], font("sans-bold", 40), BONE, a, anchor="ls")
    text(img, (ex1 + 40, ey1 + 22), "El camino que eligió el mercado", font("sans", 26), GREEN, a, anchor="la")
    xa = sx + (ex2 - sx) * 0.8
    ya = sy + (ey2 - sy) * 0.8
    text(img, (xa + 40, ya), s["left"], font("sans-bold", 40), col2, appear(t, 2.0), anchor="lm")
    ax = appear(t, 2.6, 0.4)
    if ax > 0:
        d.line((xa - 22, ya - 22, xa + 22, ya + 22), fill=RED, width=6)
        d.line((xa - 22, ya + 22, xa + 22, ya - 22), fill=RED, width=6)


def d_fabless(img, t, s, ctx):
    boxes = [tuple(b) for b in s.get("boxes", [])] or [("NVIDIA", "Diseña el chip"), ("TSMC", "Fabrica el chip"),
                                                       ("SOCIOS", "Arman placas y equipos"), ("MERCADO", "PC, consolas, servidores")]
    nb = len(boxes)
    bw, bh, gap = (340, 220, 90) if nb >= 4 else (420, 220, 120)
    x0 = (W - (nb * bw + (nb - 1) * gap)) // 2
    y = 330
    d = ImageDraw.Draw(img)
    for i, (nm, sub) in enumerate(boxes):
        st = ctx.word_time(s.get("sync", "socios"), 1.5) if i >= 1 else 0.2
        st = st + (i - 1) * 0.4 if i >= 1 else st
        a = appear(t, st, 0.6)
        x = x0 + i * (bw + gap)
        col = GREEN if i == 0 else GREY_LIGHT
        rect(img, (x, y, x + bw, y + bh), fill=ANTHRACITE, outline=col if i == 0 else LINE, width=3, alpha=a, radius=8)
        text(img, (x + bw / 2, y + 80), nm, font("sans-black", 46), col, a, anchor="mm")
        text(img, (x + bw / 2, y + 150), sub, font("sans", 26), GREY_LIGHT, a, anchor="mm")
        if i < nb - 1:
            aa = appear(t, st + 0.5, 0.5)
            if aa > 0:
                ax0, ax1 = x + bw + 12, x + bw + 12 + (gap - 24) * aa
                d.line((ax0, y + bh / 2, ax1, y + bh / 2), fill=GREY, width=4)
                d.polygon([(ax1, y + bh / 2 - 10), (ax1 + 14, y + bh / 2), (ax1, y + bh / 2 + 10)], fill=GREY)
    text(img, (W // 2, 660), s.get("caption", "Modelo «fabless»: diseñar sin fabricar"), font("sans-semibold", 30), GOLD, appear(t, 2.5),
         anchor="mm")


def d_moat(img, t, s, ctx):
    cx, cy = W // 2, 500
    rings = [(110, "CHIPS", GREEN), (210, "SOFTWARE", GREY_LIGHT), (310, "DESARROLLADORES", GREY)]
    for i, (r, lab, col) in enumerate(reversed(rings)):
        a = appear(t, 0.3 + (2 - i) * 0.6, 0.7)
        rect(img, (cx - r, cy - r, cx + r, cy + r), outline=col, width=3, alpha=a, radius=r)
    for i, (r, lab, col) in enumerate(rings):
        a = appear(t, 0.3 + i * 0.6, 0.7)
        y = cy if i == 0 else cy - r + 50
        text(img, (cx, y), lab, font("sans-bold", 30 if i else 38), col, a, anchor="mm")


def d_science(img, t, s, ctx):
    labels = ["Clima", "Física", "Biología", "Finanzas", "Imágenes médicas", "Energía"]
    cols = 3
    bw, bh = 420, 200
    x0 = (W - (cols * bw + 2 * 40)) // 2
    for i, lab in enumerate(labels):
        a = appear(t, 0.2 + i * 0.35, 0.5)
        x = x0 + (i % cols) * (bw + 40)
        y = 240 + (i // cols) * (bh + 40)
        rect(img, (x, y, x + bw, y + bh), fill=ANTHRACITE, outline=LINE, width=2, alpha=a, radius=6)
        # mini matriz de cálculo
        for gx in range(16):
            for gy in range(5):
                v = (math.sin(t * 2.4 + gx * 0.7 + gy * 1.3 + i) + 1) / 2
                c = mix(ANTHRACITE, GREEN, v * 0.8 * a)
                px, py = x + 24 + gx * 23, y + 24 + gy * 20
                rect(img, (px, py, px + 15, py + 12), fill=c)
        text(img, (x + 24, y + bh - 28), lab, font("sans-semibold", 30), BONE, a, anchor="ls")


def d_parallel(img, t, s, ctx):
    # CPU: 8 núcleos grandes procesando en serie; GPU: 1024 núcleos simultáneos
    a = appear(t, 0.1)
    text(img, (480, 230), "CPU", font("sans-black", 56), BONE, a, anchor="mm")
    text(img, (480, 280), "pocos núcleos potentes", font("sans", 26), GREY, a, anchor="mm")
    for i in range(8):
        x, y = 300 + (i % 4) * 95, 340 + (i // 4) * 95
        active = int(t * 4) % 8 == i
        rect(img, (x, y, x + 80, y + 80), fill=GOLD if active else ANTHRACITE, outline=LINE, width=2, alpha=a, radius=6)
    a2 = appear(t, ctx.word_time("paralelo", 1.0) - 0.4, 0.6)
    text(img, (1380, 230), "GPU", font("sans-black", 56), GREEN, a2, anchor="mm")
    text(img, (1380, 280), "miles de núcleos en paralelo", font("sans", 26), GREY, a2, anchor="mm")
    cols, rws, c = 48, 22, 13
    xg, yg = 1380 - cols * c // 2, 340
    wave = (t - 1.0) * 1.2
    for gx in range(cols):
        for gy in range(rws):
            v = (math.sin(wave * 3 + gx * 0.25 + gy * 0.4) + 1) / 2
            col = mix(ANTHRACITE, GREEN, (0.35 + 0.65 * v) * a2)
            x, y = xg + gx * c, yg + gy * c
            ImageDraw.Draw(img).rectangle((x, y, x + c - 3, y + c - 3), fill=col)


def d_network(img, t, s, ctx):
    layers = [5, 8, 8, 6, 3]
    d = ImageDraw.Draw(img)
    xs = [380 + i * 290 for i in range(len(layers))]
    pos = [[(xs[i], 540 + (j - (n - 1) / 2) * 82) for j in range(n)] for i, n in enumerate(layers)]
    a = appear(t, 0.1, 0.8)
    for i in range(len(layers) - 1):
        for p0 in pos[i]:
            for p1 in pos[i + 1]:
                d.line((p0, p1), fill=mix(CARBON, LINE, a), width=1)
    # pulsos de activación que recorren la red
    phase = (t * 0.6) % 1.0
    li = phase * (len(layers) - 1)
    k = int(li)
    f = li - k
    for p0 in pos[k]:
        for j, p1 in enumerate(pos[k + 1]):
            x = p0[0] + (p1[0] - p0[0]) * f
            y = p0[1] + (p1[1] - p0[1]) * f
            rect(img, (x - 3, y - 3, x + 3, y + 3), fill=GREEN, alpha=a * 0.8, radius=3)
    for i, col in enumerate(pos):
        for (x, y) in col:
            on = abs(i - li) < 0.5
            rect(img, (x - 16, y - 16, x + 16, y + 16), fill=GREEN if on else ANTHRACITE, outline=GREY, width=2,
                 alpha=a, radius=16)
    text(img, (xs[0], 200), "Datos", font("sans-semibold", 26), GREY, a, anchor="mm")
    text(img, (xs[-1], 200), "Predicción", font("sans-semibold", 26), GREY, a, anchor="mm")


def _box(img, x, y, w, h, title, sub, col, a, title_size=44):
    rect(img, (x, y, x + w, y + h), fill=ANTHRACITE, outline=col, width=3, alpha=a, radius=8)
    text(img, (x + w / 2, y + h / 2 - (18 if sub else 0)), title, font("sans-black", title_size), col, a, anchor="mm")
    if sub:
        text(img, (x + w / 2, y + h / 2 + 34), sub, font("sans", 24), GREY_LIGHT, a, anchor="mm")


def _arrow(img, x0, y0, x1, y1, a, col=GREY, width=4):
    if a <= 0:
        return
    d = ImageDraw.Draw(img)
    xe, ye = x0 + (x1 - x0) * a, y0 + (y1 - y0) * a
    d.line((x0, y0, xe, ye), fill=col, width=width)
    ang = math.atan2(ye - y0, xe - x0)
    pts = [(xe + 14 * math.cos(ang), ye + 14 * math.sin(ang)),
           (xe + 10 * math.cos(ang + 2.3), ye + 10 * math.sin(ang + 2.3)),
           (xe + 10 * math.cos(ang - 2.3), ye + 10 * math.sin(ang - 2.3))]
    d.polygon(pts, fill=col)


def d_secondsource(img, t, s, ctx):
    """Un gran comprador con dos proveedores: la lógica del segundo proveedor."""
    buyer = s.get("buyer", "IBM")
    a0 = appear(t, 0.2)
    _box(img, W // 2 - 220, 230, 440, 160, buyer, s.get("buyer_sub", "Comprador"), BONE, a0, 64)
    sup = s.get("suppliers", [["Intel", "Proveedor original"], ["AMD", "Segunda fuente"]])
    versus = s.get("versus", False)
    for i, (nm, sub) in enumerate(sup):
        x = 360 + i * 820
        st = ctx.word_time(nm, 0.8 + i * 0.8) - 0.1
        a = appear(t, st, 0.6)
        col = (RED if versus else ACCENTS["green"]) if i == 1 else (RED if versus else GREY_LIGHT)
        _box(img, x, 600, 380, 160, nm, sub, col, a, 56)
        if versus:
            text(img, (x + 190, 520), "VS", font("sans-black", 40), GREY, appear(t, st + 0.3, 0.5), anchor="mm")
        else:
            _arrow(img, x + 190, 595, W // 2 + (i * 2 - 1) * 120, 400, appear(t, st + 0.4, 0.6), col)


def d_amd64(img, t, s, ctx):
    """x86 de 32 bits contenido dentro de AMD64: extensión compatible."""
    cx, cy = W // 2, 500
    p = ease((t - 0.2) / 1.2)
    a2 = appear(t, ctx.word_time("sesenta", 1.6) - 0.2, 0.8)
    ow, oh = 560 + 520 * a2, 230 + 230 * a2
    rect(img, (cx - ow / 2, cy - oh / 2, cx + ow / 2, cy + oh / 2), outline=ACCENTS["green"], width=4, alpha=a2, radius=10)
    text(img, (cx - ow / 2 + 30, cy - oh / 2 + 26), "AMD64 · 64 bits", font("sans-black", 44), ACCENTS["green"], a2)
    rect(img, (cx - 260, cy - 95, cx + 260, cy + 95), fill=ANTHRACITE, outline=GREY_LIGHT, width=3, alpha=p, radius=8)
    text(img, (cx, cy - 18), "x86 · 32 bits", font("sans-black", 54), BONE, p, anchor="mm")
    text(img, (cx, cy + 42), "programas existentes", font("sans", 26), GREY_LIGHT, p, anchor="mm")
    a3 = appear(t, ctx.word_time("compatibilidad", 3.0) - 0.2, 0.6)
    text(img, (cx, cy + oh / 2 + 60), "✓ Los programas de 32 bits siguen funcionando", font("sans-semibold", 32), BONE, a3,
         anchor="mm")


def d_fusion(img, t, s, ctx):
    """CPU + GPU en un mismo chip (la visión detrás de la compra de ATI)."""
    p = ease_io((t - 0.6) / max(1.2, ctx.dur * 0.45))
    cy = 500
    r = 150
    xl = 560 + (W // 2 - 90 - 560) * p
    xr = W - 560 - (W - 560 - (W // 2 + 90)) * p
    a = appear(t, 0.1)
    rect(img, (xl - r, cy - r, xl + r, cy + r), outline=BONE, width=4, alpha=a, radius=r)
    text(img, (xl, cy), "CPU", font("sans-black", 64), BONE, a, anchor="mm")
    text(img, (xl, cy + r + 40), "AMD", font("sans-medium", 28), GREY, a * (1 - p), anchor="mm")
    rect(img, (xr - r, cy - r, xr + r, cy + r), outline=ACCENTS["red"] if s.get("red") else ACCENTS["blue"], width=4,
         alpha=a, radius=r)
    text(img, (xr, cy), "GPU", font("sans-black", 64), BONE, a, anchor="mm")
    text(img, (xr, cy + r + 40), "ATI", font("sans-medium", 28), GREY, a * (1 - p), anchor="mm")
    if p > 0.95:
        text(img, (W // 2, cy + r + 70), s.get("result", "Un solo chip"), font("serif", 52), ACCENTS["green"],
             appear(t, 0.6 + max(1.2, ctx.dur * 0.45), 0.6), anchor="mm")


def d_split(img, t, s, ctx):
    """Una empresa integrada que se divide en diseño y fabricación."""
    p = ease_io((t - 1.0) / 1.4)
    cy = 470
    a = appear(t, 0.1)
    w, h = 520, 220
    xl = W // 2 - w / 2 - 330 * p
    xr = W // 2 - w / 2 + 330 * p
    title = s.get("from", "AMD 2008")
    if p < 0.05:
        _box(img, W // 2 - w / 2, cy - h / 2, w, h, title, "Diseño + fábricas propias", BONE, a, 60)
        return
    _box(img, xl, cy - h / 2, w, h, s.get("left", "AMD"), s.get("left_sub", "Diseño de chips"), ACCENTS["green"], 1, 60)
    _box(img, xr, cy - h / 2, w, h, s.get("right", "GlobalFoundries"), s.get("right_sub", "Fábricas (2009)"), GREY_LIGHT,
         1, 52)
    text(img, (W // 2, cy + h / 2 + 80), s.get("caption", ""), font("sans-semibold", 30), GOLD, appear(t, 2.4), anchor="mm")


def d_models(img, t, s, ctx):
    """Modelo tercerizado (AMD) frente a modelo integrado (Intel)."""
    rows_ = s.get("rows", [["AMD", [["Diseño", "AMD"], ["Fabricación", "TSMC"], ["Producto", "Ryzen · EPYC"]]],
                            ["Intel", [["Diseño + fabricación", "Fábricas propias"], ["Producto", "Core · Xeon"]]]])
    for ri, (nm, steps) in enumerate(rows_):
        y = 250 + ri * 320
        st = ctx.word_time(nm, 0.3 + ri * 1.6) - 0.2
        a = appear(t, st, 0.6)
        col = ACCENTS["green"] if ri == 0 else GREY_LIGHT
        text(img, (MARGIN + 20, y + 80), nm, font("sans-black", 56), col, a, anchor="lm")
        n = len(steps)
        bw, gap = (330, 80) if n == 3 else (560, 80)
        x0 = MARGIN + 320
        for i, (t1, t2) in enumerate(steps):
            ai = appear(t, st + 0.3 + i * 0.35, 0.5)
            x = x0 + i * (bw + gap)
            _box(img, x, y, bw, 160, t1, t2, col, ai, 36)
            if i < n - 1:
                _arrow(img, x + bw + 10, y + 80, x + bw + gap - 14, y + 80, appear(t, st + 0.55 + i * 0.35, 0.4))


DIAGRAMS = {"datacenter": d_datacenter, "crowd": d_crowd, "fork": d_fork, "fabless": d_fabless, "moat": d_moat,
            "science": d_science, "parallel": d_parallel, "network": d_network,
            "secondsource": d_secondsource, "amd64": d_amd64, "fusion": d_fusion, "split": d_split, "models": d_models}


# ───────────────────────────── imagen de archivo ─────────────────────────────

def r_image(img, t, s, ctx):
    """Material auténtico aportado por el productor (con crédito obligatorio)."""
    ph = ctx.root / s["file"]
    im = Image.open(ph).convert("RGB")
    z = 1.04 + 0.06 * (t / max(ctx.dur, 0.1))
    dx = (s.get("pan", 0)) * 40 * (t / max(ctx.dur, 0.1))
    tw, th = int(W * z), int(H * z)
    im = _cover(im, tw, th)
    ox, oy = int((tw - W) / 2 + dx), (th - H) // 2
    img.paste(im.crop((ox, oy, ox + W, oy + H)), (0, 0))
    shade = Image.new("L", (W, H), 0)
    ImageDraw.Draw(shade).rectangle((0, 0, W, 170), fill=150)
    ImageDraw.Draw(shade).rectangle((0, H - 140, W, H), fill=150)
    img.paste(Image.new("RGB", (W, H), CARBON), (0, 0), shade)
    ctx.note = s.get("credit")
    if s.get("recreation"):
        ctx.tag = "Recreación"
    if s.get("caption"):
        text(img, (MARGIN, H - 120), s["caption"], font("serif", 52), BONE, appear(t, 0.4), anchor="ls")


def r_brand(img, t, s, ctx):
    a = appear(t, 0.1, 0.9)
    text(img, (W // 2, H // 2 - 30), "MUNDO", font("sans-black", 150), BONE, a, anchor="ms")
    text(img, (W // 2, H // 2 + 120), "DINERO", font("sans-black", 150), GOLD, appear(t, 0.35, 0.9), anchor="ms")
    lw = 520 * ease((t - 0.5) / 1.0)
    if lw > 1:
        rect(img, (W // 2 - lw / 2, H // 2 + 160, W // 2 + lw / 2, H // 2 + 163), fill=GREY)
    text(img, (W // 2, H // 2 + 220), tracked("Empresas · Mercados · Dinero"), font("sans-medium", 24), GREY,
         appear(t, 1.0), anchor="mm")


def r_bars(img, t, s, ctx):
    """Comparación proporcional de cifras (p. ej. ingresos anuales)."""
    ctx.note = s.get("note")
    items = s["items"]
    vmax = max(i["value"] for i in items)
    text(img, (MARGIN + 40, 230), tracked(s.get("title", "")), font("sans-semibold", 28), GREY_LIGHT, appear(t, 0.1))
    x0, x1 = MARGIN + 340, W - MARGIN - 320
    n = len(items)
    step = min(190, 560 / max(1, n))
    y0 = 330 + (560 - step * n) / 2
    for k, it in enumerate(items):
        st = ctx.word_time(str(it.get("sync", it["label"])), 0.4 + k * 0.9) - 0.15
        p = ease((t - st) / 1.3)
        y = y0 + k * step
        col = ACCENTS.get(it.get("color"), BONE)
        text(img, (MARGIN + 40, y + 45), it["label"], font("sans-black", 64), BONE, appear(t, st, 0.4), anchor="lm")
        rect(img, (x0, y + 10, x1, y + 80), fill=(26, 28, 32), alpha=appear(t, st, 0.4))
        wv = (x1 - x0) * it["value"] / vmax * p
        if wv > 2:
            rect(img, (x0, y + 10, x0 + wv, y + 80), fill=col)
        text(img, (x0 + wv + 24, y + 45), it.get("display", ""), font("sans-bold", 44), col, appear(t, st + 0.4, 0.5),
             anchor="lm")
    if s.get("result"):
        text(img, (W // 2, 930), s["result"], font("serif-italic", 46), GREY_LIGHT,
             appear(t, ctx.word_time(s.get("result_sync", "zzzz"), ctx.dur * 0.6), 0.6), anchor="mm")


RENDERERS = {"title": r_title, "statement": r_statement, "definition": r_definition, "invest": r_invest,
             "counter": r_counter, "checklist": r_checklist, "calendar": r_calendar, "runway": r_runway,
             "timeline": r_timeline, "location": r_location, "people": r_people, "product": r_product,
             "chart": r_chart, "diagram": r_diagram, "image": r_image, "brand": r_brand, "bars": r_bars}


def render_frame(spec, t, ctx, fade_in=0.0, fade_out=0.0):
    img = background().copy()
    v = spec["visual"]
    ctx.tag, ctx.note = v.get("tag"), v.get("note") if v.get("type") != "diagram" else None
    RENDERERS[v["type"]](img, t, v, ctx)
    if v["type"] not in ("brand",):
        chrome(img, ctx, t)
    # fundido a negro solo en cambios de capítulo
    k = 1.0
    if fade_in and t < fade_in:
        k = ease_io(t / fade_in)
    if fade_out and t > ctx.dur - fade_out:
        k = min(k, ease_io((ctx.dur - t) / fade_out))
    if k < 1.0:
        img = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), img, k)
    return img
