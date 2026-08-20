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
        if al.min() == 255:                      # opaque file: derive alpha from ink
            rgb = a[..., :3].astype(np.int16)
            d = 255 - rgb.min(axis=2)
            al = np.clip(d * 255 / 40, 0, 255).astype(np.uint8)
            al[al < 14] = 0
        # silhouette: colour comes from INK, shape from alpha, so white-on-
        # transparent artwork works exactly like black-on-transparent
        out = np.dstack([np.full(al.shape, c, np.uint8) for c in INK_RGB] + [al])
        im2 = Image.fromarray(out)
        cut = CROP_LEFT.get(slug)
        if cut:
            im2 = im2.crop((int(im2.width * cut), 0, im2.width, im2.height))
        bb = im2.getbbox()
        if bb: im2 = im2.crop(bb)
        ar = im2.width / im2.height
        h = K / math.sqrt(ar); w = h * ar
        s = min(MAXW / w, MAXH / h, 1.0)
        cw, chh = max(1, round(w * s)), max(1, round(h * s))
        im2.resize((cw * 2, chh * 2), Image.LANCZOS).save(OUT / f"{slug}.png", optimize=True)
        dims[slug] = [cw, chh]
        print(f"  {slug:<20}{cw}x{chh} css   ar={ar:5.1f}   {(OUT / (slug + '.png')).stat().st_size // 1024}KB")
    (ROOT / "scripts" / "logodims.json").write_text(json.dumps(dims, indent=1))
    areas = [round(math.sqrt(w * h)) for w, h in dims.values()]
    print(f"  {len(dims)} logos | optical spread {min(areas)}-{max(areas)} | "
          f"{sum(f.stat().st_size for f in OUT.glob('*.png')) // 1024}KB total")

if __name__ == "__main__":
    main()
