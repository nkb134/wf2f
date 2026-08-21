#!/usr/bin/env python3
"""Quality gate for the site's imagery.

Checks every image in assets/img/ for the defects that have actually shipped
on this project, plus the bookkeeping that silently breaks layout.

Run:  /usr/bin/python3 scripts/image_qa.py [--budget]

Exit 0 = clean, 1 = problems found.
"""
import glob, json, os, re, sys
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "assets", "img")

# --- thresholds, all learned the hard way on this repo -----------------------
BAND_CAP      = 120   # a uniform run reaching this is the backdrop, not a band
BAND_UNIFORM  = 30    # std below this = uniform enough to be a border
BAND_JUMP     = 25    # tonal step at the boundary that marks a real edge
CLIP_LO       = 8.0   # % pure black tolerated
CLIP_HI       = 6.0   # % pure white tolerated
WEBP_BUDGET   = 140   # KB, per gallery image
# Full-bleed images earn a higher ceiling — they are rendered at viewport width,
# so the gallery budget would force real detail loss. Chasing a flat number is
# how re-04 ended up re-encoded at quality 50.
BUDGET_OVER   = {"hero": 240, "re-04": 210}
SKIP          = ("og-image",)

def edge_bands(gray):
    """A real border is a THIN uniform strip that ENDS with a sharp jump.
    A seamless studio backdrop is also uniform but runs to the cap — that is
    not a defect, and treating it as one produced false positives before."""
    H, W = gray.shape
    found = []
    edges = (("left",   lambda i: gray[:, i],        W),
             ("right",  lambda i: gray[:, W - 1 - i], W),
             ("top",    lambda i: gray[i],            H),
             ("bottom", lambda i: gray[H - 1 - i],    H))
    for name, line, limit in edges:
        d = 0
        while d < min(BAND_CAP, limit) and line(d).std() <= BAND_UNIFORM:
            d += 1
        if d == 0 or d >= BAND_CAP:
            continue
        inner = line(min(d + 2, limit - 1))
        if abs(line(d - 1).mean() - inner.mean()) > BAND_JUMP:
            found.append(f"{name} {d}px (tone {line(0).mean():.0f})")
    return found

def main():
    show_budget = "--budget" in sys.argv
    problems = []
    notes = []

    dims_path = os.path.join(ROOT, "scripts", "dims.json")
    dims = json.load(open(dims_path))

    # what the built pages and stylesheet actually reference
    html = "".join(open(os.path.join(ROOT, f)).read()
                   for f in os.listdir(ROOT) if f.endswith(".html"))
    css = open(os.path.join(ROOT, "assets", "css", "styles.css")).read()
    referenced = set(re.findall(r'assets/img/([\w./-]+?)\.(?:jpg|webp|png)', html + css))

    jpgs = sorted(f for f in glob.glob(os.path.join(IMG, "*.jpg"))
                  if not any(s in f for s in SKIP))
    print(f"scanning {len(jpgs)} images in assets/img/\n")

    total_webp = 0
    for path in jpgs:
        slug = os.path.splitext(os.path.basename(path))[0]
        im = Image.open(path)
        gray = np.array(im.convert("L")).astype(float)
        g8 = gray.astype(np.uint8)

        for b in edge_bands(gray):
            problems.append(f"{slug}: edge band — {b}")

        lo = (g8 <= 3).mean() * 100
        hi = (g8 >= 252).mean() * 100
        if lo > CLIP_LO:
            problems.append(f"{slug}: {lo:.1f}% crushed to pure black")
        if hi > CLIP_HI:
            problems.append(f"{slug}: {hi:.1f}% blown to pure white")

        webp = path[:-4] + ".webp"
        if not os.path.exists(webp):
            problems.append(f"{slug}: no .webp companion — <picture> serves WebP first")
        else:
            kb = os.path.getsize(webp) // 1024
            total_webp += kb
            budget = BUDGET_OVER.get(slug, WEBP_BUDGET)
            if kb > budget:
                notes.append(f"{slug}: webp {kb}KB over the {budget}KB budget")
            if show_budget:
                print(f"  {slug:<26}{im.width}x{im.height:<6} {kb:>4}KB webp")

        if slug in dims:
            if list(im.size) != list(dims[slug]):
                problems.append(f"{slug}: dims.json says {dims[slug]}, file is "
                                f"{list(im.size)} — layout shift returns")
        elif slug in referenced:
            problems.append(f"{slug}: referenced but missing from dims.json")

        if slug not in referenced and not slug.startswith(("logo", "favicon", "mark")):
            notes.append(f"{slug}: not referenced by any page or the stylesheet")

    for slug in dims:
        if not os.path.exists(os.path.join(IMG, slug + ".jpg")):
            problems.append(f"{slug}: in dims.json but the file is gone")

    if notes:
        print("\nnotes")
        for n in sorted(notes):
            print(f"  - {n}")
    if problems:
        print("\nPROBLEMS")
        for p in sorted(problems):
            print(f"  ! {p}")
        print(f"\n{len(problems)} problem(s), {len(notes)} note(s)")
        return 1
    print(f"\nclean — 0 problems, {len(notes)} note(s), {total_webp}KB webp total")
    return 0

if __name__ == "__main__":
    sys.exit(main())
