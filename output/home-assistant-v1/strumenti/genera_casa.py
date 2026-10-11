"""Compone i due piani in un'unica immagine (vista esplosa: mansarda sopra il primo piano).

Legge gli asset per piano (livelli/<piano>/) prodotti da genera_overlay.py e scrive
www/floorplan/casa/: base-giorno.png, base-notte.png e luce-<stanza>.png (uno per stanza),
tutti sulla stessa tela definita in stanze.json -> casa.

Ogni piano viene ritagliato dallo sfondo con una maschera morbida (casa + ombra portata).
La mansarda sta davanti: gli overlay del primo piano sono mascherati dove la mansarda li copre.

Uso:  python genera_casa.py   (dopo genera_overlay.py)
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
WWW = ROOT / "www" / "floorplan"
LAYERS = ROOT / "livelli"            # asset per piano prodotti da genera_overlay.py


def floor_mask(src):
    """Maschera 0..1 di tutto cio' che non e' sfondo uniforme (casa e ombra), bordi morbidi."""
    a = np.asarray(src, dtype=np.float32)
    bg = a[:60, :60].reshape(-1, 3).mean(0)
    m = (np.abs(a - bg).max(2) > 9).astype(np.uint8) * 255
    im = Image.fromarray(m).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MinFilter(9))
    im = im.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(3))
    return np.asarray(im, dtype=np.float32) / 255


def place(arr, offset, size):
    """Copia arr (h,w,...) sulla tela size=(W,H) all'offset (x,y), tagliando i bordi."""
    W, H = size
    ox, oy = offset
    out = np.zeros((H, W) + arr.shape[2:], dtype=arr.dtype)
    h, w = arr.shape[:2]
    x0, y0 = max(0, ox), max(0, oy)
    x1, y1 = min(W, ox + w), min(H, oy + h)
    out[y0:y1, x0:x1] = arr[y0 - oy:y1 - oy, x0 - ox:x1 - ox]
    return out


def main():
    cfg = json.loads((ROOT / "strumenti" / "stanze.json").read_text(encoding="utf-8"))
    casa = cfg["casa"]
    size = tuple(casa["size"])
    order = casa["order"]                      # dal fondo al davanti
    out_dir = WWW / "casa"
    out_dir.mkdir(parents=True, exist_ok=True)
    Image.new("RGBA", size, (0, 0, 0, 0)).save(out_dir / "trasparente.png", optimize=True)

    masks = {}
    for fid in order:
        floor = next(f for f in cfg["floors"] if f["id"] == fid)
        src = Image.open((ROOT / floor["source"]).resolve()).convert("RGB")
        masks[fid] = place(floor_mask(src), casa["offsets"][fid], size)

    for mode in ("giorno", "notte"):
        first = np.asarray(Image.open(LAYERS / order[0] / f"base-{mode}.png").convert("RGB"), dtype=np.float32)
        bg = first[:60, :60].reshape(-1, 3).mean(0)
        canvas = np.empty((size[1], size[0], 3), dtype=np.float32)
        canvas[:] = bg
        for fid in order:
            img = np.asarray(Image.open(LAYERS / fid / f"base-{mode}.png").convert("RGB"), dtype=np.float32)
            img = place(img, casa["offsets"][fid], size)
            a = masks[fid][..., None]
            canvas = canvas * (1 - a) + img * a
        Image.fromarray(np.clip(canvas, 0, 255).astype(np.uint8)).save(out_dir / f"base-{mode}.png", optimize=True)
        print("scritto", (out_dir / f"base-{mode}.png").relative_to(ROOT))

    for i, fid in enumerate(order):
        floor = next(f for f in cfg["floors"] if f["id"] == fid)
        cover = np.zeros((size[1], size[0]), dtype=np.float32)   # piani davanti a questo
        for front in order[i + 1:]:
            cover = np.maximum(cover, masks[front])
        for room in floor["rooms"]:
            ov = np.asarray(Image.open(LAYERS / fid / f"luce-{room['id'].split('_')[0]}.png").convert("RGBA"))
            ov = place(ov, casa["offsets"][fid], size).astype(np.float32)
            ov[..., 3] *= masks[fid] * (1 - cover)
            ov[..., :3] *= (ov[..., 3:] > 1)
            out = out_dir / f"luce-{room['id'].replace('_', '-')}.png"
            Image.fromarray(np.round(ov).astype(np.uint8), "RGBA").save(out, optimize=True)
            print("scritto", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
