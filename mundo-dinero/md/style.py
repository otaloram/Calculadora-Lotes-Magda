"""Identidad visual MUNDO DINERO: paleta, tipografías y helpers de dibujo."""
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1920, 1080
FPS = 25
FONTS = Path(__file__).resolve().parent.parent / "fonts"

# Paleta institucional
CARBON = (14, 15, 17)
ANTHRACITE = (27, 29, 33)
LINE = (46, 49, 54)
GREY = (138, 141, 146)
GREY_LIGHT = (190, 192, 195)
BONE = (237, 232, 223)
GREEN = (118, 185, 0)       # verde tecnológico (Nvidia) — usar con moderación
RED = (214, 69, 69)         # rojo contenido: pérdidas y riesgo
GOLD = (201, 162, 39)       # acento de marca MUNDO DINERO
BLUE = (52, 104, 186)       # azul profundo (acento secundario por episodio)

ACCENTS = {"green": GREEN, "blue": BLUE, "red": RED, "gold": GOLD, "white": BONE, None: GOLD}

MARGIN = 140


@lru_cache(maxsize=None)
def font(kind: str, size: int) -> ImageFont.FreeTypeFont:
    files = {
        "serif": "Caladea-Bold.ttf",            # titulares editoriales
        "serif-regular": "Caladea-Regular.ttf",
        "serif-italic": "Caladea-Italic.ttf",
        "sans": "Inter-Regular.otf",            # texto informativo
        "sans-light": "Inter-Light.otf",
        "sans-medium": "Inter-Medium.otf",
        "sans-semibold": "Inter-SemiBold.otf",
        "sans-bold": "Inter-Bold.otf",
        "sans-black": "Inter-Black.otf",        # cifras
    }
    return ImageFont.truetype(str(FONTS / files[kind]), size)


def ease(x: float) -> float:
    """easeOutCubic acotado a [0, 1]."""
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def ease_io(x: float) -> float:
    x = min(max(x, 0.0), 1.0)
    return 3 * x * x - 2 * x * x * x


def appear(t: float, start: float, dur: float = 0.6) -> float:
    return ease((t - start) / dur) if dur > 0 else float(t >= start)


@lru_cache(maxsize=4)
def background(tint: tuple = CARBON) -> Image.Image:
    """Fondo carbón con viñeta suave y grano fino (calculado una sola vez)."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W * 0.5) / (W * 0.75)) ** 2 + ((yy - H * 0.45) / (H * 0.85)) ** 2)
    v = np.clip(1.0 - 0.55 * d ** 2, 0.35, 1.0)
    rng = np.random.default_rng(7)
    grain = rng.normal(0, 2.2, (H, W)).astype(np.float32)
    base = np.array(tint, np.float32) + 8
    img = base[None, None, :] * v[..., None] + grain[..., None]
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB")


def mix(c1, c2, a):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * a) for i in range(3))


def text(img, xy, s, fnt, color=BONE, alpha=1.0, anchor="la", dy=0.0, spacing=8, align="left"):
    """Dibuja texto con opacidad `alpha` y desplazamiento vertical de entrada `dy`."""
    if alpha <= 0.01 or not s:
        return
    x, y = xy[0], xy[1] + dy
    d = ImageDraw.Draw(img)
    if alpha >= 0.995:
        d.multiline_text((x, y), s, font=fnt, fill=color, anchor=anchor, spacing=spacing, align=align)
        return
    box = d.multiline_textbbox((x, y), s, font=fnt, anchor=anchor, spacing=spacing, align=align)
    x0, y0, x1, y1 = int(box[0]) - 4, int(box[1]) - 4, int(box[2]) + 4, int(box[3]) + 4
    patch = Image.new("L", (max(1, x1 - x0), max(1, y1 - y0)), 0)
    ImageDraw.Draw(patch).multiline_text((x - x0, y - y0), s, font=fnt, fill=int(255 * alpha),
                                         anchor=anchor, spacing=spacing, align=align)
    img.paste(Image.new("RGB", patch.size, color), (x0, y0), patch)


def tracked(s: str) -> str:
    """Espaciado amplio para etiquetas en versalitas."""
    return " ".join(s.upper())


def wrap(s: str, fnt, max_w: int) -> str:
    words, lines, cur = s.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if fnt.getlength(test) <= max_w or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return "\n".join(lines)


def rect(img, box, fill=None, outline=None, width=1, alpha=1.0, radius=0):
    if alpha <= 0.01:
        return
    if alpha >= 0.995:
        ImageDraw.Draw(img).rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)
        return
    x0, y0, x1, y1 = [int(v) for v in box]
    pad = width + 2
    patch = Image.new("L", (x1 - x0 + 2 * pad, y1 - y0 + 2 * pad), 0)
    pd = ImageDraw.Draw(patch)
    a = int(255 * alpha)
    if fill is not None:
        pd.rounded_rectangle((pad, pad, pad + x1 - x0, pad + y1 - y0), radius=radius, fill=a)
        img.paste(Image.new("RGB", patch.size, fill), (x0 - pad, y0 - pad), patch)
    if outline is not None:
        patch = Image.new("L", patch.size, 0)
        ImageDraw.Draw(patch).rounded_rectangle((pad, pad, pad + x1 - x0, pad + y1 - y0), radius=radius,
                                                outline=a, width=width)
        img.paste(Image.new("RGB", patch.size, outline), (x0 - pad, y0 - pad), patch)


def glow(img, box, color, strength=0.5, radius=40):
    """Halo difuso detrás de un elemento (para cifras clave)."""
    x0, y0, x1, y1 = [int(v) for v in box]
    pad = radius * 2
    m = Image.new("L", (x1 - x0 + 2 * pad, y1 - y0 + 2 * pad), 0)
    ImageDraw.Draw(m).rectangle((pad, pad, pad + x1 - x0, pad + y1 - y0), fill=int(255 * strength))
    m = m.filter(ImageFilter.GaussianBlur(radius))
    img.paste(Image.new("RGB", m.size, color), (x0 - pad, y0 - pad), m)


def fmt_int(n: float) -> str:
    """Formato es-AR: 10.000"""
    return f"{int(round(n)):,}".replace(",", ".")
