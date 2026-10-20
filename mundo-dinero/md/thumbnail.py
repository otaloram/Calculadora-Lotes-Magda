"""Miniatura de YouTube 1280x720 con la identidad MUNDO DINERO."""
from PIL import Image

from .style import BONE, GOLD, GREY_LIGHT, H, RED, W, background, font, text, tracked, wrap


def make_thumbnail(ep, path):
    th = ep.get("thumbnail", {})
    img = background().copy()
    big = th.get("big", "−90 %")
    line1 = th.get("line1", "NVIDIA")
    line2 = th.get("line2", "Dos derrumbes")
    text(img, (140, 150), tracked("Mundo Dinero"), font("sans-bold", 40), GOLD)
    text(img, (140, 260), line1, font("sans-black", 200), BONE)
    text(img, (140, 500), wrap(line2, font("serif", 110), 1000), font("serif", 110), GREY_LIGHT)
    text(img, (W - 140, H - 140), big, font("sans-black", 300), RED, anchor="rs")
    img.resize((1280, 720), Image.LANCZOS).save(path, quality=92)
