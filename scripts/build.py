#!/usr/bin/env python3
"""Generate the static HTML for wf2f.in.

GitHub Pages serves the generated .html directly — no build step at deploy time.
This script exists so the shared chrome is defined once, not copy-pasted five times.

Run:  /usr/bin/python3 scripts/build.py
"""
import html, json, pathlib

SITE = "https://wf2f.in"
ROOT = pathlib.Path(__file__).resolve().parent.parent
DIMS = json.loads((ROOT / "scripts" / "dims.json").read_text())
LOGODIMS = json.loads((ROOT / "scripts" / "logodims.json").read_text())

NAV = [("products.html", "Products"), ("capabilities.html", "Capabilities"),
       ("about.html", "About")]

CLIENTS = [("Cloth &amp; Co", "Australia"), ("La-Eva", "United Kingdom"),
           ("Loft &amp; Daughter", "United Kingdom"), ("House of Wandering Silk", "India"),
           ("Uvaacha Studio", "India"), ("Arohi", "India"), ("Tatsat", "India"),
           ("Pyjama Project", "Australia"), ("Swiatlo", "India"),
           ("Baya Labels", "India"), ("Mosambae", "India")]

MARKETS = [("USA", "Export orders shipped door to door"),
           ("Europe", "Including the United Kingdom"),
           ("Australia &amp; NZ", "Long-standing accounts"),
           ("Middle East", "Including Dubai and the UAE"),
           ("India", "Domestic labels and studios")]

def pic(name, alt, ratio=None, eager=False, sizes="100vw"):
    w, h = DIMS[name]
    load = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'
    style = ' style="aspect-ratio:%s"' % ratio if ratio else ''
    return ('<picture><source srcset="assets/img/%s.webp" type="image/webp">'
            '<img src="assets/img/%s.jpg" alt="%s" width="%d" height="%d" sizes="%s" %s '
            'decoding="async"%s></picture>' % (name, name, html.escape(alt), w, h, sizes, load, style))

def slides(items):
    out = []
    for name, alt in items:
        out.append('<div class="slide">%s</div>' % pic(name, alt, sizes="(min-width:980px) 26vw, 78vw"))
    return "".join(out)

def gallery(items):
    out = []
    for name, alt in items:
        w, h = DIMS[name]
        out.append('<a href="assets/img/%s.jpg" data-w="%d" data-h="%d" data-cap="%s">%s</a>'
                   % (name, w, h, html.escape(alt),
                      pic(name, alt, sizes="(min-width:820px) 24vw, 48vw")))
    return "".join(out)

LOGO_FILES = {"Cloth &amp; Co":"cloth-and-co","La-Eva":"la-eva",
 "Loft &amp; Daughter":"loft-and-daughter","Uvaacha Studio":"uvaacha","Arohi":"arohi",
 "House of Wandering Silk":"wandering-silk","Tatsat":"tatsat","Mosambae":"mosambae",
 "Pyjama Project":"pyjama-project","Baya Labels":"baya","Swiatlo":"swiatlo"}

def logoband():
    """Auto-scrolling client band. Real logo files where we have them, set
    wordmarks for the rest, all silhouetted to ink so the row reads as one."""
    items = []
    for name, _country in CLIENTS:
        f = LOGO_FILES.get(name)
        if f:
            w, h = LOGODIMS[f]
            # explicit dimensions reserve the box so the band never shifts as
            # logos arrive; the band sits high enough to load eagerly
            items.append('<img src="assets/img/clients/%s.png" alt="%s" width="%d" height="%d" '
                         'loading="eager" decoding="async">'
                         % (f, name.replace("&amp;", "and"), w, h))
        else:
            items.append('<span class="wordmark">%s</span>' % name)
    run = "".join(items)
    # duplicated once so translateX(-50%) loops seamlessly; the copy is hidden
    # from assistive tech so the list is not announced twice
    return ('<div class="marquee logoband marquee--tint"><div class="marquee__track">'
            '%s<span aria-hidden="true" style="display:contents">%s</span>'
            '</div></div>') % (run, run)

def prodband(items):
    figs = "".join('<figure>%s</figure>' % pic(n, a, sizes="260px") for n, a in items)
    return ('<div class="marquee prodband"><div class="marquee__track">'
            '%s<span aria-hidden="true" style="display:contents">%s</span>'
            '</div></div>') % (figs, figs)

IG = "https://www.instagram.com/wftofashion/"
LI = "https://www.linkedin.com/in/women-fiber-to-fashion-107574148/"

def socials(cls="", uid="a"):
    """Instagram and LinkedIn in their own brand colours, at the same square
    size, side by side. The gradient needs a unique id per instance because the
    block appears twice on the contact page."""
    ig = ('<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
          '<defs><radialGradient id="ig-%(u)s" cx="0.32" cy="1.02" r="1.28">'
          '<stop offset="0" stop-color="#FED576"/><stop offset=".26" stop-color="#F47133"/>'
          '<stop offset=".61" stop-color="#BC3081"/><stop offset="1" stop-color="#4C63D2"/>'
          '</radialGradient></defs>'
          '<rect width="24" height="24" rx="5.6" fill="url(#ig-%(u)s)"/>'
          '<rect x="5.7" y="5.7" width="12.6" height="12.6" rx="3.8" fill="none" '
          'stroke="#fff" stroke-width="1.55"/>'
          '<circle cx="12" cy="12" r="3.25" fill="none" stroke="#fff" stroke-width="1.55"/>'
          '<circle cx="17.05" cy="6.95" r="1.05" fill="#fff"/></svg>') % {"u": uid}
    li = ('<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
          '<rect width="24" height="24" rx="3.2" fill="#0A66C2"/>'
          '<path fill="#fff" d="M8.34 18.2H5.72V9.76h2.62V18.2zM7.03 8.61a1.52 1.52 0 1 1 0-3.04 '
          '1.52 1.52 0 0 1 0 3.04zM18.28 18.2h-2.61v-4.11c0-.98-.02-2.24-1.37-2.24-1.37 0-1.58 '
          '1.07-1.58 2.17v4.18H10.1V9.76h2.51v1.15h.04c.35-.66 1.2-1.36 2.48-1.36 2.65 0 3.14 '
          '1.74 3.14 4.01v4.64z"/></svg>')
    return ('<ul class="social %s">'
            '<li><a href="%s" rel="noopener" aria-label="Women Fiber to Fashion on Instagram">%s</a></li>'
            '<li><a href="%s" rel="noopener" aria-label="Women Fiber to Fashion on LinkedIn">%s</a></li>'
            '</ul>') % (cls, IG, ig, LI, li)

def clientwall():
    # 12 cells keeps the grid whole at 2, 3 and 4 columns — no orphan gap
    cells = ['<div class="client"><b>%s</b><span>%s</span></div>' % (n, c) for n, c in CLIENTS]
    cells.append('<a class="client client--cta" href="contact.html">'
                 '<b>Your label next</b><span>Start an enquiry</span></a>')
    return "".join(cells)

def marketgrid():
    return "".join('<div class="market"><b>%s</b><span>%s</span></div>' % (n, d) for n, d in MARKETS)

def prodgrid(items, label):
    """Static, browsable grid. Clicking opens the showcase viewer; the href is
    the plain image so it still works with JavaScript off."""
    out=[]
    for name,alt in items:
        w,h=DIMS[name]
        out.append('<a href="assets/img/%s.jpg" data-w="%d" data-h="%d" data-cap="%s">%s</a>'
                   % (name,w,h,html.escape(alt),
                      pic(name,alt,sizes="(min-width:980px) 24vw, (min-width:620px) 46vw, 92vw")))
    # Home & Accessories mixes landscape linen with portrait bags, so it gets
    # square tiles; the garment tabs stay 3:4.
    wide = " gal--wide" if "Home" in label else ""
    return ('<div class="gal gal--prod%s" data-showcase data-set="products" data-label="%s">%s</div>'
            % (wide, label, "".join(out)))

def carousel(cid, items):
    return ('<div class="carousel" data-carousel>'
            '<div class="track">%s</div>'
            '<div class="carousel__bar">'
            '<div class="dots" role="tablist" aria-label="Slides"></div>'
            '<button class="cbtn" type="button" data-playtoggle aria-label="Pause slideshow">'
            '<svg width="14" height="14" viewBox="0 0 12 12" fill="currentColor">'
            '<rect x="1.5" y="1" width="3" height="10" rx="1"/>'
            '<rect x="7.5" y="1" width="3" height="10" rx="1"/></svg></button>'
            '<button class="cbtn" type="button" data-prev aria-label="Previous">'
            '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="2"><path d="M15 5l-7 7 7 7"/></svg></button>'
            '<button class="cbtn" type="button" data-next aria-label="Next">'
            '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="2"><path d="M9 5l7 7-7 7"/></svg></button>'
            '</div></div>' % slides(items))

SCHEMA_EXTRA = {
    "index.html": {"@type": "Organization"},
}

def schema():
    d = {
      "@context": "https://schema.org", "@type": "Organization",
      "name": "Women Fiber to Fashion", "alternateName": "WFTF",
      "url": SITE + "/", "logo": SITE + "/assets/img/logo-960.png",
      "image": SITE + "/assets/img/og-image.jpg",
      "email": "sales@wf2f.in",
      "description": ("Garment manufacturer in New Delhi, India. Womenswear, menswear, home "
                      "linen and accessories for brands in the USA, Europe, Australia, New "
                      "Zealand, the Middle East and India. 100-piece minimums, 12,000-15,000 pieces a month."),
      "address": {"@type": "PostalAddress", "addressLocality": "New Delhi", "addressCountry": "IN"},
      "contactPoint": {"@type": "ContactPoint", "contactType": "sales", "email": "sales@wf2f.in",
                       "availableLanguage": ["en", "hi"], "areaServed": ["US", "GB", "AU", "NZ", "AE", "IN"]},
      "areaServed": [{"@type": "Country", "name": n} for n in
                     ["United States", "United Kingdom", "Australia", "New Zealand",
                      "United Arab Emirates", "India"]],
      "knowsAbout": ["Garment manufacturing", "Womenswear manufacturing", "Menswear manufacturing",
                     "Home linen", "Tote bags and accessories", "Private label apparel",
                     "Low MOQ clothing manufacturing"],
      "sameAs": ["https://www.instagram.com/wftofashion/",
                 "https://www.linkedin.com/in/women-fiber-to-fashion-107574148/"]
    }
    return json.dumps(d, indent=2)

def page(slug, title, desc, body, pswp=False):
    parts = []
    for h, t in NAV:
        cur = ' aria-current="page"' if h == slug else ''
        parts.append('<a href="%s"%s>%s</a>' % (h, cur, t))
    nav = "".join(parts)
    canon = SITE + "/" + ("" if slug == "index.html" else slug)
    pswp_css = ""
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
<link rel="canonical" href="%(canon)s">
<meta name="theme-color" content="#F7F4EF">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Women Fiber to Fashion">
<meta property="og:locale" content="en_IN">
<meta property="og:url" content="%(canon)s">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(desc)s">
<meta property="og:image" content="%(site)s/assets/img/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="%(title)s">
<meta name="twitter:description" content="%(desc)s">
<meta name="twitter:image" content="%(site)s/assets/img/og-image.jpg">
<link rel="icon" href="favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="assets/img/favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="assets/img/favicon-180.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700;800&family=Karla:wght@400;500&display=swap" rel="stylesheet">
%(pswp)s
<script>document.documentElement.classList.add('js')</script>
<link rel="stylesheet" href="assets/css/styles.css">
<script type="application/ld+json">
%(schema)s
</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>

<header class="hdr">
  <div class="hdr__in">
    <a class="hdr__logo" href="index.html">
      <img src="assets/img/mark.png" alt="" width="35" height="96">
      <b>Women Fiber to Fashion</b>
    </a>
    <nav class="nav" id="nav" aria-label="Main">%(nav)s</nav>
    <a class="hdr__cta" href="contact.html">Contact us</a>
    <button class="burger" aria-label="Menu" aria-expanded="false" aria-controls="nav">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9">
        <path d="M3 6h18M3 12h18M3 18h18"/></svg>
    </button>
  </div>
</header>

<main id="main">
%(body)s
</main>

<footer class="ftr">
  <div class="wrap">
    <a class="ftr__mark" href="index.html">
      <img src="assets/img/mark-light.png" alt="" width="35" height="96">
      <b>Women Fiber to Fashion</b>
    </a>
    <div class="g2" style="align-items:start">
      <div>
        <h4>What we do</h4>
        <p style="max-width:38ch">Garment manufacturing in New Delhi, India. Womenswear,
        menswear, home linen and accessories &mdash; made to order, shipped worldwide.</p>
      </div>
      <div>
        <h4>Get in touch</h4>
        <ul>
          <li><a href="mailto:sales@wf2f.in">sales@wf2f.in</a></li>
          <li><a href="contact.html">Send an enquiry</a></li>
        </ul>
        %(socials)s
      </div>
    </div>
    <div class="ftr__base">
      <span>&copy; 2026 Women Fiber to Fashion. All rights reserved.</span>
      <span>New Delhi, India &middot; Shipping worldwide</span>
    </div>
  </div>
</footer>

<div class="dock" aria-hidden="false">
  <a class="btn" href="contact.html">Request a quote</a>
  <a class="btn btn--ghost" href="mailto:sales@wf2f.in">Email</a>
</div>

<script type="module" src="assets/js/main.js"></script>
</body>
</html>
""" % {"title": html.escape(title), "desc": html.escape(desc), "canon": canon,
       "site": SITE, "pswp": pswp_css, "schema": schema(), "nav": nav, "body": body, "socials": socials("social--ftr", "f")}

# ------------------------------------------------------------------ content

APPAREL = [("ap-01","Black midi dress with gathered sleeves"), ("ap-10","Striped waistcoat and matching trousers"),
 ("ap-12","Long-line stone trench coat"), ("ap-13","White cotton shirt with open back detail"),
 ("ap-03","Oversized white cotton shirt"), ("ap-11","Black cotton midi sundress"),
 ("ap-06","Indigo belted jacket and shorts co-ord"), ("ap-05","Sleeveless white overshirt"),
 ("ap-08","Black cotton dress with puff sleeves"), ("ap-09","Oversized linen blazer"),
 ("ap-04","White shirt worn with straight-leg denim"), ("ap-02","Tailored black blazer and trousers"),
 ("ap-07","Denim workwear jacket and jeans"),
 ("re-02","Ikat print kaftan dress"),
 ("re-03","Ikat print shirt, flat lay"),
 ("re-04","Ikat print co-ord photographed outdoors"),
 ("ap-14","Olive linen jumpsuit with button placket"), ("ap-15","Pink oversized shirt with wide cuffs"),
 ("ap-16","Red linen shirt and shorts co-ord"), ("ap-17","Teal cami top and trousers set"),
 ("ap-18","Block-print pyjama trousers with a white tee"), ("ap-19","Block-print lounge set"),
 ("ap-20","Gathered-waist dress in stone cotton"), ("ap-21","Block-print tunic")]
HOME = [("hm-07","Tan cotton tote bag"),
 ("hm-05","Tasselled scarves in natural and blush"),
 ("hm-03","Stack of fringed throws"),
 ("hm-04","Fringed cushion covers, stacked"),
 ("hm-06","Block-print table linen with paisley border"),
 ("hm-02","Neutral textured cushion covers"),
 ("hm-01","Cushion covers in assorted weaves and prints"),
 ("product-tote-bag","Olive green cotton tote bag"),
 ("product-drawstring-bag","Natural cotton drawstring bag")]

FACTORY_GAL = [("fac-floor-1","Stitching floor at the New Delhi unit"),
 ("fac-machinist","Machinist at work on an industrial sewing machine"),
 ("fac-cutting","Pattern cutting on the cutting table"),
 ("fac-qc","Final quality inspection of a finished garment"),
 ("fac-hands","Hand finishing detail"),("fac-fitting","Checking a finished garment on the form"),
 ("fac-machine-1","Industrial sewing machine in operation"),
 ("fac-floor-2","Wide view of the production floor")]

STEPS = [("Sampling","Pattern development and prototyping from your tech pack or a reference sample."),
 ("Fabric sourcing","Expert in sourcing both artisanal and mill-made fabrics &mdash; or we work to your nominated mill."),
 ("Stitching","Production across womenswear, menswear, home linen and accessories."),
 ("Finishing","Pressing, trims, labelling and the detail work that decides how a garment hangs."),
 ("Quality control","Inline, mid-line and final inspection. Every piece checked before packing."),
 ("Packing &amp; export","Custom labels, hang tags and export-ready packing. Shipped door to door.")]

def steplist():
    return "".join("<li><h3>%s</h3><p>%s</p></li>" % (t, d) for t, d in STEPS)

SPEC = [("Minimum order","100 pieces and above"),("Monthly capacity","12,000&ndash;15,000 pieces"),
 ("Machines","50+ sewing machines"),("Turnaround","Fast turnaround"),
 ("Quality control","Inline, mid-line &amp; final &mdash; 100% checked"),
 ("Fabric","Sourcing available in-house"),
 ("Categories","Woven &amp; knitted, home linen, accessories"),
 ("Export","Export capability, international shipping")]

def speclist():
    return "".join("<li><b>%s</b><span>%s</span></li>" % (a, b) for a, b in SPEC)

KEYS = ('<div class="keys" data-rise>'
 '<div class="key"><b>100</b><span>Piece MOQ</span></div>'
 '<div class="key"><b>12&ndash;15k</b><span>Pieces per month</span></div>'
 '<div class="key"><b>50+</b><span>Sewing machines</span></div>'
 '<div class="key"><b>5</b><span>Markets served</span></div></div>')

TABS_TPL = ('<div data-tabs>'
 '<div class="tabs" role="tablist" aria-label="Product categories">'
 '<button class="tab" role="tab" id="t-ap" aria-controls="p-ap" aria-selected="true">Apparel</button>'
 '<button class="tab" role="tab" id="t-hm" aria-controls="p-hm" aria-selected="false" tabindex="-1">Home &amp; Accessories</button>'
 '</div>'
 '<div class="panel" id="p-ap" role="tabpanel" aria-labelledby="t-ap">%s</div>'
 '<div class="panel" id="p-hm" role="tabpanel" aria-labelledby="t-hm" hidden>%s</div>'
 '</div>')

TABS = TABS_TPL % (prodgrid(APPAREL, "Apparel"), prodgrid(HOME, "Home &amp; Accessories"))
TABS_BAND = TABS_TPL.replace('id="t-ap"','id="b-ap"').replace('aria-controls="p-ap"','aria-controls="q-ap"')\
    .replace('id="t-hm"','id="b-hm"').replace('aria-controls="p-hm"','aria-controls="q-hm"')\
    .replace('id="p-ap" role="tabpanel" aria-labelledby="t-ap"','id="q-ap" role="tabpanel" aria-labelledby="b-ap"')\
    .replace('id="p-hm" role="tabpanel" aria-labelledby="t-hm"','id="q-hm" role="tabpanel" aria-labelledby="b-hm"')\
    % (prodband(APPAREL), prodband(HOME))

CTA = ('<section class="section section--ink" id="contact-cta">'
 '<div class="wrap"><span class="eyebrow">Start a conversation</span>'
 '<h2 style="max-width:16ch">Tell us what<br>you are making</h2>'
 '<p class="muted" style="max-width:48ch;margin-top:1.4rem">Send your tech pack, quantities and '
 'timings. We will come back with an honest answer on whether we are the right unit for it.</p>'
 '<div class="btns"><a class="btn" href="contact.html" '
 'style="background:#F7F4EF;color:#1F1E1C;border-color:#F7F4EF">Request a quote</a>'
 '<a class="btn" href="mailto:sales@wf2f.in" '
 'style="background:transparent;color:#fff;border-color:rgba(255,255,255,.5)">sales@wf2f.in</a>'
 '</div></div></section>')

HOME_PAGE = """
<section class="hero">
  %(hero)s
  <div class="hero__scrim"></div>
  <div class="wrap hero__in">
    <span class="eyebrow">New Delhi, India &middot; Shipping worldwide</span>
    <h1>Garment<br>manufacturing<br>for brands<br>worldwide</h1>
    <p class="lede">Womenswear, menswear, home linen and accessories &mdash; woven and
    knitted, made to order with flexible MOQs.</p>
    <div class="btns">
      <a class="btn btn--light" href="contact.html">Request a quote</a>
      <a class="btn btn--onphoto" href="capabilities.html">Our capabilities</a>
    </div>
  </div>
</section>

<section class="wrap">%(keys)s</section>

<section class="section">
  <div class="wrap">
    <span class="eyebrow" data-rise>Our products</span>
    <h2 data-rise style="margin-bottom:1.8rem">What we make</h2>
  </div>
  <div class="wrap" style="padding-inline:0">%(tabsband)s</div>
  <div class="wrap"><div class="btns"><a class="btn btn--ghost" href="products.html">See the full range</a></div></div>
</section>

<section class="section section--tint">
  <div class="wrap">
    <span class="eyebrow" data-rise>Trusted by</span>
    <h2 data-rise style="margin-bottom:1.8rem">Brands we<br>manufacture for</h2>
  </div>
  <div class="wrap" style="padding-inline:0;margin-bottom:2.25rem">%(logoband)s</div>
  <div class="wrap">
    <div class="clients" data-rise>%(clients)s</div>
    <span class="eyebrow" data-rise style="margin-top:var(--s-m)">Where we ship</span>
    <div class="markets" data-rise>%(markets)s</div>
    <p class="muted" data-rise style="font-size:.9rem;margin-top:1.2rem">Export capability with
    international shipping, door to door.</p>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <span class="eyebrow" data-rise>How we work</span>
    <h2 data-rise style="margin-bottom:2rem">From tech pack<br>to packed carton</h2>
    <ul class="steps" data-rise>%(steps)s</ul>
    <div class="btns"><a class="btn btn--ghost" href="capabilities.html">Full capabilities</a></div>
  </div>
</section>

<section class="section section--tint">
  <div class="wrap">
    <span class="eyebrow" data-rise>Inside the unit</span>
    <h2 data-rise style="margin-bottom:2rem">Where it<br>is made</h2>
    <div class="gal" data-showcase data-set="unit" data-label="Inside the unit" data-rise>%(gal)s</div>
  </div>
</section>

<section class="section">
  <div class="wrap g2">
    <div data-rise>
      <span class="eyebrow">At a glance</span>
      <h2>Production<br>specification</h2>
      <p class="muted" style="margin-top:1.4rem;max-width:40ch">If your programme sits outside
      these numbers, tell us anyway. We would rather say so honestly than over-promise.</p>
      <div class="btns"><a class="btn" href="contact.html">Discuss your programme</a></div>
    </div>
    <ul class="spec" data-rise>%(spec)s</ul>
  </div>
</section>
%(cta)s
""" % {"hero": pic("hero","Cutting and marking fabric at the Women Fiber to Fashion unit in New Delhi",
                   eager=True, sizes="100vw"),
       "keys": KEYS, "logoband": logoband(), "tabsband": TABS_BAND,
       "clients": clientwall(), "markets": marketgrid(), "steps": steplist(),
       "gal": gallery(FACTORY_GAL), "spec": speclist(), "cta": CTA}

PRODUCTS_PAGE = """
<section class="section">
  <div class="wrap">
    <span class="eyebrow" data-rise>Our products</span>
    <h1 data-rise style="font-size:clamp(1.9rem,5vw,3.6rem)">What we make</h1>
    <p class="lede" data-rise style="margin-top:1.3rem">Woven and knitted garments for women and
    men, alongside home linen and accessories. Everything below was produced at our New Delhi unit.</p>
  </div>
</section>

<section class="wrap" style="padding-bottom:var(--s-l)">
  <div data-rise>%(tabs)s</div>
</section>

<section class="section section--tint">
  <div class="wrap">
    <span class="eyebrow" data-rise>Categories</span>
    <div class="cards" style="margin-top:1.5rem">
      <article class="card" data-rise><h3>Womenswear</h3><p>Shirting, dresses, co-ord sets,
        tailoring, denim and outerwear in woven and knitted fabrics.</p></article>
      <article class="card" data-rise><h3>Menswear</h3><p>Shirting and casual separates,
        woven and knitted.</p></article>
      <article class="card" data-rise><h3>Home linen</h3><p>Cushion covers, table, kitchen and
        bedroom linen made to specification.</p></article>
      <article class="card" data-rise><h3>Accessories</h3><p>Tote bags, drawstring bags, pouches
        and scarves &mdash; frequently made from production offcuts.</p></article>
    </div>
    <div class="btns"><a class="btn" href="contact.html">Request the full catalogue</a></div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <span class="eyebrow" data-rise>Trusted by</span>
    <div class="clients" data-rise>%(clients)s</div>
  </div>
</section>
%(cta)s
""" % {"tabs": TABS, "clients": clientwall(), "cta": CTA}

CAPS_PAGE = """
<section class="section">
  <div class="wrap">
    <span class="eyebrow" data-rise>Capabilities</span>
    <h1 data-rise style="font-size:clamp(1.9rem,5vw,3.6rem)">Built for<br>small batches</h1>
    <p class="lede" data-rise style="margin-top:1.3rem">100-piece minimums, 12,000&ndash;15,000
    pieces a month, and quality checked at three stages rather than one.</p>
  </div>
</section>

<section class="wrap">%(keys)s</section>

<section class="section section--tint">
  <div class="wrap">
    <span class="eyebrow" data-rise>Process</span>
    <h2 data-rise style="margin-bottom:2rem">From tech pack<br>to packed carton</h2>
    <ul class="steps" data-rise>%(steps)s</ul>
  </div>
</section>

<section class="section">
  <div class="wrap g2">
    <div data-rise>%(qcimg)s</div>
    <div data-rise>
      <span class="eyebrow">Quality control</span>
      <h2>Checked three<br>times over</h2>
      <hr class="rule" style="margin-top:1.4rem">
      <p>Many units inspect only at the end, when a fault means reworking an entire run. We check
      <strong>inline</strong> as pieces are sewn, <strong>mid-line</strong> as they come together,
      and <strong>final</strong> before packing.</p>
      <p class="muted">Catching a problem at the machine costs minutes. Catching it in the carton
      costs a delivery window.</p>
    </div>
  </div>
</section>

<section class="section section--tint">
  <div class="wrap g2">
    <div data-rise>
      <span class="eyebrow">Specification</span>
      <h2>What we can<br>take on</h2>
      <div class="btns"><a class="btn" href="contact.html">Discuss your programme</a></div>
    </div>
    <ul class="spec" data-rise>%(spec)s</ul>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <span class="eyebrow" data-rise>Inside the unit</span>
    <div class="gal" data-showcase data-set="unit" data-label="Inside the unit" data-rise style="margin-top:1.5rem">%(gal)s</div>
  </div>
</section>
%(cta)s
""" % {"keys": KEYS, "steps": steplist(),
       "qcimg": pic("fac-stitch-detail","Close inspection of stitching during production",
                    sizes="(min-width:860px) 46vw, 100vw"),
       "spec": speclist(), "gal": gallery(FACTORY_GAL), "cta": CTA}

ABOUT_PAGE = """
<section class="section">
  <div class="wrap">
    <span class="eyebrow" data-rise>About</span>
    <h1 data-rise style="font-size:clamp(1.9rem,5vw,3.6rem)">A garment<br>unit in<br>New Delhi</h1>
    <p class="lede" data-rise style="margin-top:1.3rem">We manufacture womenswear, menswear, home
    linen and accessories for independent labels and established brands across five markets.</p>
  </div>
</section>

<section class="wrap">
  <div data-rise>%(hero)s</div>
</section>

<section class="section section--tint">
  <div class="wrap g2">
    <div data-rise>
      <span class="eyebrow">How we operate</span>
      <h2>A trained,<br>stable floor</h2>
    </div>
    <div data-rise>
      <hr class="rule">
      <p>Every machinist completes more than 160 hours of formal training before working on bulk
      production, and we have trained over 300 people to date.</p>
      <p>Retention runs at around 70%% &mdash; high for this industry, and the reason our stitch
      quality stays consistent across repeat orders. A stable floor is a commercial advantage
      before it is anything else.</p>
      <p class="muted">We operate a transparent supply chain and fair employment practices, which
      matters to the brands we work with when they report on their own sourcing.</p>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <span class="eyebrow" data-rise>By the numbers</span>
    <div class="keys" data-rise style="margin-top:1.5rem">
      <div class="key"><b>300+</b><span>People trained</span></div>
      <div class="key"><b>70%%</b><span>Retention rate</span></div>
      <div class="key"><b>160+</b><span>Training hours each</span></div>
      <div class="key"><b>100%%</b><span>Quality checked</span></div>
    </div>
  </div>
</section>

<section class="section section--tint">
  <div class="wrap">
    <span class="eyebrow" data-rise>Trusted by</span>
    <h2 data-rise style="margin-bottom:2rem">Brands we<br>manufacture for</h2>
    <div class="clients" data-rise>%(clients)s</div>
    <span class="eyebrow" data-rise style="margin-top:var(--s-m)">Where we ship</span>
    <div class="markets" data-rise>%(markets)s</div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="gal" data-showcase data-set="unit" data-label="Inside the unit" data-rise>%(gal)s</div>
  </div>
</section>
%(cta)s
""" % {"hero": pic("fac-team","The team at the Women Fiber to Fashion unit", sizes="100vw"),
       "clients": clientwall(), "markets": marketgrid(),
       "gal": gallery(FACTORY_GAL[:4]), "cta": CTA}

CONTACT_PAGE = """
<section class="section">
  <div class="wrap">
    <span class="eyebrow" data-rise>Contact</span>
    <h1 data-rise style="font-size:clamp(1.9rem,5vw,3.6rem)">Request<br>a quote</h1>
    <p class="lede" data-rise style="margin-top:1.3rem">Tell us what you are making. Categories,
    quantities and timings help us answer properly first time.</p>
  </div>
</section>

<section class="section" style="padding-top:0" id="contact-cta">
  <div class="wrap g2" style="align-items:start">
    <form class="form" id="enquiry" data-rise method="POST" action="https://api.web3forms.com/submit">
      <input type="hidden" name="access_key" value="48c77ab1-c491-4169-bc4b-0513c3d228cf">
      <input type="hidden" name="subject" value="New enquiry from wf2f.in">
      <input type="hidden" name="from_name" value="Women Fiber to Fashion website">
      <input type="checkbox" name="botcheck" class="hp" tabindex="-1" autocomplete="off">
      <div class="form__row">
        <div class="field"><label for="name">Your name</label>
          <input id="name" name="name" type="text" required autocomplete="name"></div>
        <div class="field"><label for="company">Brand or company</label>
          <input id="company" name="company" type="text" autocomplete="organization"></div>
      </div>
      <div class="form__row">
        <div class="field"><label for="email">Email</label>
          <input id="email" name="email" type="email" required autocomplete="email"></div>
        <div class="field"><label for="country">Country</label>
          <input id="country" name="country" type="text" autocomplete="country-name"></div>
      </div>
      <div class="form__row">
        <div class="field"><label for="enquiry_type">What do you need?</label>
          <select id="enquiry_type" name="enquiry_type">
            <option>Production enquiry</option><option>Sampling only</option>
            <option>Request the catalogue</option><option>Partnership or press</option>
            <option>Something else</option></select></div>
        <div class="field"><label for="quantity">Approximate quantity</label>
          <input id="quantity" name="quantity" type="text" placeholder="e.g. 500 pieces"></div>
      </div>
      <div class="field"><label for="message">About your programme</label>
        <textarea id="message" name="message" required></textarea>
        <small>Minimum order is 100 pieces. Fabric sourcing is available in-house.</small></div>
      <div class="status" id="formstatus" role="status" aria-live="polite"></div>
      <div><button class="btn" type="submit">Send enquiry</button></div>
      <p class="muted" style="font-size:.85rem">We use your details only to reply to this enquiry.</p>
    </form>

    <div data-rise>
      <hr class="rule">
      <h3>Women Fiber to Fashion</h3>
      <p class="muted">New Delhi, India<br>Shipping worldwide</p>
      <span class="eyebrow" style="margin-top:2rem">Email</span>
      <p><a href="mailto:sales@wf2f.in">sales@wf2f.in</a></p>
      <span class="eyebrow" style="margin-top:2rem">Markets</span>
      <p class="muted">USA &middot; Europe &middot; Australia &amp; New Zealand &middot; Middle East &middot; India</p>
      <span class="eyebrow" style="margin-top:2rem">Elsewhere</span>
      SOCIALBLOCK
      <span class="eyebrow" style="margin-top:2rem">Response time</span>
      <p class="muted">Usually within two working days.</p>
    </div>
  </div>
</section>
"""

CONTACT_PAGE = CONTACT_PAGE.replace("SOCIALBLOCK", socials("", "c"))

NOTFOUND = """
<section class="section" style="min-height:54vh">
  <div class="wrap">
    <span class="eyebrow">404</span>
    <h1 style="font-size:clamp(1.9rem,5vw,3.6rem)">Page not<br>found</h1>
    <p class="lede" style="margin-top:1.3rem">That page has moved, or never existed.</p>
    <div class="btns"><a class="btn" href="/">Back to home</a>
      <a class="btn btn--ghost" href="/contact.html">Contact us</a></div>
  </div>
</section>
"""

PAGES = [
 ("index.html","Garment Manufacturer in New Delhi | Women Fiber to Fashion",
  "Garment manufacturer in New Delhi producing womenswear, menswear, home linen and accessories for brands in the USA, Europe, Australia, the Middle East and India. 100-piece minimums, 12,000-15,000 pieces a month.",HOME_PAGE,True),
 ("products.html","Products | Womenswear, Menswear, Home Linen & Accessories",
  "Woven and knitted garments, home linen, tote bags and accessories manufactured at our New Delhi unit for brands worldwide.",PRODUCTS_PAGE,False),
 ("capabilities.html","Capabilities | Low MOQ Garment Manufacturing, New Delhi",
  "100-piece minimums, 12,000-15,000 pieces a month, 50+ machines, inline mid-line and final quality control, in-house fabric sourcing and export shipping.",CAPS_PAGE,True),
 ("about.html","About | Garment Manufacturing in New Delhi",
  "A garment manufacturing unit in New Delhi with a trained, stable workforce and a transparent supply chain, serving brands across five markets.",ABOUT_PAGE,True),
 ("contact.html","Contact | Request a Quote",
  "Request a manufacturing quote from our New Delhi unit. Minimum order 100 pieces, fast turnaround, international shipping.",CONTACT_PAGE,False),
 ("404.html","Page not found","Page not found.",NOTFOUND,False),
]

if __name__ == "__main__":
    for slug,title,desc,body,pswp in PAGES:
        (ROOT/slug).write_text(page(slug,title,desc,body,pswp),encoding="utf-8")
        print("  wrote", slug)
    sm=['<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for slug,_,_,_,_ in PAGES:
        if slug=="404.html": continue
        loc=SITE+"/"+("" if slug=="index.html" else slug)
        pri="1.0" if slug=="index.html" else "0.8"
        sm.append('  <url><loc>%s</loc><changefreq>monthly</changefreq><priority>%s</priority></url>'%(loc,pri))
    sm.append("</urlset>")
    (ROOT/"sitemap.xml").write_text("\n".join(sm)+"\n",encoding="utf-8")
    print("  wrote sitemap.xml")
