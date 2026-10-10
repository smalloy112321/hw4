"""Build the four Home-page "Shop by collection" tiles from the data pack's product photos.

Each tile is one catalogue photo with its black side bars and frame lines trimmed off, centered
on a white square so the whole garment shows. Product photos are not stored in the repo, so run
this once after placing the data pack:

    .venv/bin/python scripts/build_collection_tiles.py

Output goes to frontend/public/collections/ (git-ignored). If the tiles are missing, the Home
page falls back to the original product photos, so the site still works without this step.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
PRODUCTS = ROOT / "data" / "products"
OUT = ROOT / "frontend" / "public" / "collections"

# Tile name -> product photo. Keep in sync with COLLECTIONS in frontend/src/pages/Home.tsx.
TILES = {
    "hoodies": "district-vit-hoodie-vintage-bulldog",
    "crewnecks": "champion-mens-triumph-raglan-crew",
    "t-shirts": "district-tri-blend-t-shirt-vintage-shield",
    "quarter-zips": "branford-1-4-zip",
}
SIZE = 800  # output pixels per side
MARGIN = 0.07  # white space around the garment, as a share of the tile
INSET = 6  # ignore this many pixels at each edge (thin frame lines in some photos)


def garment_box(im: Image.Image) -> tuple[int, int, int, int]:
    """Bounding box of pixels that are neither near-white background nor near-black side bars."""
    px = im.load()
    w, h = im.size
    xs, ys = [], []
    for y in range(INSET, h - INSET, 2):
        for x in range(INSET, w - INSET, 2):
            r, g, b = px[x, y]
            if max(r, g, b) < 28 or min(r, g, b) > 238:
                continue
            xs.append(x)
            ys.append(y)
    if not xs:
        return (0, 0, w, h)
    return (min(xs), min(ys), max(xs) + 2, max(ys) + 2)


def main() -> int:
    if not PRODUCTS.is_dir():
        print(f"Product photos not found at {PRODUCTS}. Place the data pack first (see README).")
        return 1
    OUT.mkdir(parents=True, exist_ok=True)
    for name, product_id in TILES.items():
        src = PRODUCTS / f"{product_id}.jpg"
        if not src.exists():
            print(f"  skipped {name}: {src.name} is missing")
            continue
        im = Image.open(src).convert("RGB")
        garment = im.crop(garment_box(im))
        side = int(max(garment.size) / (1 - 2 * MARGIN))
        canvas = Image.new("RGB", (side, side), "white")
        canvas.paste(garment, ((side - garment.width) // 2, (side - garment.height) // 2))
        canvas.resize((SIZE, SIZE), Image.LANCZOS).save(OUT / f"{name}.jpg", quality=85, optimize=True, progressive=True)
        print(f"  wrote frontend/public/collections/{name}.jpg")
    return 0


if __name__ == "__main__":
    sys.exit(main())
