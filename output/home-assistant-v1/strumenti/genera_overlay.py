"""Genera gli overlay luce (uno per stanza) per la planimetria Home Assistant.

Scrive in livelli/<piano>/. Ogni overlay e' un PNG RGBA 1500x1049 allineato al pixel con le illustrazioni v2.
Il contenuto della stanza accesa deriva dall'illustrazione originale (gia' calda),
con un leggero alone caldo centrato sul punto della stanza: la geometria resta
identica perche' nessun pixel viene ridisegnato o spostato.

Uso:  python genera_overlay.py            (dalla cartella strumenti o da qualsiasi cartella)
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent          # output/home-assistant-v1
FEATHER = 5            # sfumatura del bordo stanza, in pixel
WARM = np.array([255, 196, 128], dtype=np.float32)     # tinta ~2800 K


def room_labels(floor, size):
    """Mappa etichette: ogni pixel appartiene al massimo a una stanza (l'ultima dipinta vince)."""
    lab = Image.new("L", size, 0)
    d = ImageDraw.Draw(lab)
    for i, room in enumerate(floor["rooms"], start=1):
        d.polygon([tuple(p) for p in room["polygon"]], fill=i)
    return np.asarray(lab)


def build_overlay(src, labels, idx, room):
    h, w = labels.shape
    mask = Image.fromarray(((labels == idx) * 255).astype(np.uint8))
    mask = np.asarray(mask.filter(ImageFilter.GaussianBlur(FEATHER)), dtype=np.float32) / 255

    xs = np.array([p[0] for p in room["polygon"]], dtype=np.float32)
    ys = np.array([p[1] for p in room["polygon"]], dtype=np.float32)
    radius = 0.5 * float(np.hypot(xs.max() - xs.min(), ys.max() - ys.min()))
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cx, cy = room["hotspot"]
    pool = np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (radius ** 2)) * 1.6)

    lit = src * (1.0 + 0.16 * pool[..., None]) + WARM * (0.07 * pool[..., None])
    lit = np.clip(lit, 0, 255)
    alpha = np.clip(mask * (0.88 + 0.12 * pool), 0, 1)

    rgba = np.zeros((h, w, 4), dtype=np.uint8)
    rgba[..., :3] = np.where(alpha[..., None] > 0.004, lit, 0).astype(np.uint8)
    rgba[..., 3] = np.round(alpha * 255).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA")


def main():
    cfg = json.loads((ROOT / "strumenti" / "stanze.json").read_text(encoding="utf-8"))
    size = (cfg["canvas"]["width"], cfg["canvas"]["height"])
    layers = ROOT / "livelli"
    for floor in cfg["floors"]:
        src_img = Image.open((ROOT / floor["source"]).resolve()).convert("RGB")
        assert src_img.size == size, f"{floor['id']}: dimensioni inattese {src_img.size}"
        src = np.asarray(src_img, dtype=np.float32)
        labels = room_labels(floor, size)
        for idx, room in enumerate(floor["rooms"], start=1):
            out = layers / floor["id"] / f"luce-{room['id'].split('_')[0]}.png"
            build_overlay(src, labels, idx, room).save(out, optimize=True)
            print("scritto", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
