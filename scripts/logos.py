#!/usr/bin/env python3
"""Normalise client logos into assets/img/clients/.

Every logo is silhouetted to a single ink colour and scaled to constant
optical area, so a 13:1 wordmark and a 2:1 mark carry equal visual weight
in the band. Source artwork lives in "assets/Website images/Brand Logos"
(local only — not committed).

Run:  /usr/bin/python3 scripts/logos.py [#RRGGBB]
"""
import json, math, os, pathlib, sys
import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "Website images" / "Brand Logos"
OUT = ROOT / "assets" / "img" / "clients"
INK = sys.argv[1] if len(sys.argv) > 1 else "#1F1E1C"
INK_RGB = tuple(int(INK.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))

K, MAXW, MAXH = 62, 230, 58          # target sqrt(area), and clamps, in CSS px

# source file -> output slug
FILES = {
    "cloth-and-co.png": "cloth-and-co",
    "la-eva.png": "la-eva",
    "loft-and-daughter.png": "loft-and-daughter",
    "uvaacha.png": "uvaacha",
    "arohi.png": "arohi",
    "house of wandering silk.avif": "wandering-silk",
    "tatsat.avif": "tatsat",
    "mosambae_logo_final.avif": "mosambae",
    "Pyjama-Project-logo-charcoal_400x.webp": "pyjama-project",
    "BAYA-Logo-Black-PNG-1-1-300x245.png": "baya",
    "6a113e62bbb645db86cae79a_brand_logo_CLMJBDPK8W_2026-05-27.webp": "swiatlo",
}

# Some supplied artwork pairs a dense pictorial mark with a light wordmark.
# Silhouetted, the mark becomes a heavy blob beside neighbouring wordmarks, so
# we keep only the wordmark. Values are fractions of the source width.
CROP_LEFT = {"wandering-silk": 0.141}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    dims = {}
    for fname, slug in FILES.items():
        p = SRC / fname
        if not p.exists():
            print("  missing source:", fname); continue
        im = Image.open(p).convert("RGBA")
        a = np.array(im); al = a[..., 3]
        opaque = al.min() == 255
        if opaque:                               # no alpha channel: ink is the dark pixels
            rgb = a[..., :3].astype(np.int16)
            mask = (255 - rgb.min(axis=2)) > 24
        else:
            mask = al > 24
        ys, xs = np.where(mask)
        if len(xs) == 0:
            print("  no ink found:", fname); continue
        x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        cut = CROP_LEFT.get(slug)
        if cut:
            x0 = max(x0, int(im.width * cut))
        im = im.crop((x0, y0, x1, y1))

        ar = im.width / im.height
        h = K / math.sqrt(ar); w = h * ar
        sc = min(MAXW / w, MAXH / h, 1.0)
        cw, chh = max(1, round(w * sc)), max(1, round(h * sc))

        # Resize the artwork FIRST, then derive the silhouette at final size.
        # Silhouetting first and downscaling averages the alpha channel, which
        # dissolves thin strokes into semi-transparency — the logos came out
        # washed out and hollow, worst on the most heavily scaled marks.
        im = im.resize((cw * 2, chh * 2), Image.LANCZOS)
        a = np.array(im)
        if opaque:
            rgb = a[..., :3].astype(np.int16)
            alpha = np.clip((255 - rgb.min(axis=2)) * 255.0 / 90, 0, 255)
        else:
            alpha = a[..., 3].astype(np.float32)
            peak = alpha.max()
            if peak > 0:
                alpha = np.clip(alpha * (255.0 / peak), 0, 255)
        alpha[alpha < 12] = 0
        alpha = alpha.astype(np.uint8)
        out = np.dstack([np.full(alpha.shape, c, np.uint8) for c in INK_RGB] + [alpha])
        Image.fromarray(out).save(OUT / f"{slug}.png", optimize=True)
        dims[slug] = [cw, chh]
        print(f"  {slug:<20}{cw}x{chh} css   ar={ar:5.1f}   {(OUT / (slug + '.png')).stat().st_size // 1024}KB")
    (ROOT / "scripts" / "logodims.json").write_text(json.dumps(dims, indent=1))
    areas = [round(math.sqrt(w * h)) for w, h in dims.values()]
    print(f"  {len(dims)} logos | optical spread {min(areas)}-{max(areas)} | "
          f"{sum(f.stat().st_size for f in OUT.glob('*.png')) // 1024}KB total")

if __name__ == "__main__":
    main()
