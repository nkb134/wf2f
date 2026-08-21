---
name: image-qa
description: Audit the site's photography for the defects that have actually shipped on this project — baked-in edge bands, crushed or blown tones, dims.json drift, orphaned files and oversized WebP. Use after adding, replacing or reprocessing anything in assets/img/, and before any commit that touches imagery.
---

# Image QA

Run the gate:

```bash
/usr/bin/python3 scripts/image_qa.py
```

Add `--budget` to also print every image's dimensions and WebP weight.

Exit 0 = clean. Exit 1 = problems. **Problems block a commit; notes do not.**

## Why these checks and not others

Every check here exists because the corresponding defect shipped to production at
least once.

**Edge bands.** WhatsApp-supplied sources arrive with baked-in borders. The rule
that works: *a real border is a thin uniform strip that **ends***. Two failures to
avoid repeating —

- A dark-only threshold missed a mid-tone (tone 94) border on `fac-team`.
  The detector must be tone-agnostic; it keys on uniformity plus a boundary jump.
- Raising the scan cap then flagged `product-tote-bag`, a seamless studio
  backdrop. A uniform run that reaches the cap is the *backdrop*, not a band —
  hence `d >= BAND_CAP` is an explicit non-finding.
- It also once flagged 219px on `ap-01` that was the black dress and its shadow.
  Falloff there was gradual (106→48), so the jump test rejects it. **Always look
  at a flagged crop before cropping it** — the detector is a prompt, not a verdict.

**Clipping.** `ImageEnhance.Contrast` subtracts a fraction of the mean, so at
1.08 it crushed 13–16% of the factory monochromes to pure black. Use
`ImageOps.autocontrast(cutoff=0.2, preserve_tone=True)` instead. A plain global
tone shift with no highlight rolloff separately blew 9.2% of a cream product to
white; multiply the shift by `1 - lum**3`.

**dims.json.** Every `<img>` carries width/height from `scripts/dims.json`. If it
drifts from the file on disk, cumulative layout shift comes straight back — and
stale entries for deleted files linger silently. Both directions are checked.

**WebP companions.** The markup uses `<picture>` with WebP first. Copying only
the `.jpg` leaves the browser serving a stale WebP — this is exactly how a
monochrome hero survived a colour migration. Sync both, always.

**Orphans and weight.** Files nothing references still ship in the Pages
deploy. `fac-hero` sat there at 632KB after the hero moved to `hero.jpg`.

## Fixing what it reports

Reprocess with PIL and **`/usr/bin/python3`** — homebrew's python has no PIL on
this machine. After any change to an image's pixels or size:

1. update `scripts/dims.json`
2. re-emit the `.webp` (binary-search quality down to the 140KB budget rather
   than picking a fixed number)
3. `/usr/bin/python3 scripts/build.py`
4. re-run this gate

Do not reach for super-resolution on textiles. DRCT scored +52% on a
high-frequency metric while smoothing cotton weave into a vinyl surface — the
metric reads edge energy, not texture. Judge at a 1:1 crop.

## Thresholds

Live at the top of `scripts/image_qa.py`. If you loosen one, say so in the
commit message and why — each value has a specific image behind it.
