/* Women Fiber to Fashion — wf2f.in
   Progressive enhancement throughout: every page, including the enquiry form
   and the product carousels, works with JavaScript disabled. */

const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ------------------------------ mobile nav ------------------------------ */
const burger = document.querySelector('.burger');
const nav = document.querySelector('.nav');
if (burger && nav) {
  const setOpen = open => {
    nav.dataset.open = String(open);
    burger.setAttribute('aria-expanded', String(open));
    document.body.style.overflow = open ? 'hidden' : '';
  };
  burger.addEventListener('click', () => setOpen(nav.dataset.open !== 'true'));
  nav.addEventListener('click', e => { if (e.target.tagName === 'A') setOpen(false); });
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && nav.dataset.open === 'true') { setOpen(false); burger.focus(); }
  });
}

/* --------------------------- sticky mobile CTA -------------------------- */
const dock = document.querySelector('.dock');
if (dock) {
  const contact = document.getElementById('contact-cta');
  const update = () => {
    const past = scrollY > 620;
    let overlapping = false;
    if (contact) {
      const r = contact.getBoundingClientRect();
      overlapping = r.top < innerHeight && r.bottom > 0;
    }
    dock.dataset.show = String(past && !overlapping);
  };
  addEventListener('scroll', update, { passive: true });
  update();
}

/* ------------------------------ reveal ---------------------------------- */
const rise = document.querySelectorAll('[data-rise]');
if (rise.length) {
  if (reduced || !('IntersectionObserver' in window)) {
    rise.forEach(el => el.classList.add('is-in'));
  } else {
    const io = new IntersectionObserver((es, obs) => {
      es.forEach(en => {
        if (!en.isIntersecting) return;
        en.target.classList.add('is-in');
        obs.unobserve(en.target);
      });
    }, { rootMargin: '0px 0px -6% 0px', threshold: 0.04 });
    rise.forEach((el, i) => {
      // Anything already at or above the fold — a restored scroll position, an
      // anchor link, a short page — is shown at once rather than waiting for an
      // intersection event that has already been and gone.
      if (el.getBoundingClientRect().top < innerHeight) {
        el.classList.add('is-in');
        return;
      }
      el.style.transitionDelay = `${Math.min(i % 5, 4) * 55}ms`;
      io.observe(el);
    });
  }
}

/* ------------------------------ product tabs ---------------------------- */
document.querySelectorAll('[data-tabs]').forEach(group => {
  const tabs = [...group.querySelectorAll('[role="tab"]')];
  const select = tab => {
    tabs.forEach(t => {
      const on = t === tab;
      t.setAttribute('aria-selected', String(on));
      t.tabIndex = on ? 0 : -1;
      const panel = document.getElementById(t.getAttribute('aria-controls'));
      if (panel) panel.hidden = !on;
    });
  };
  tabs.forEach((tab, i) => {
    tab.addEventListener('click', () => select(tab));
    tab.addEventListener('keydown', e => {
      const d = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
      if (!d) return;
      e.preventDefault();
      const next = tabs[(i + d + tabs.length) % tabs.length];
      next.focus(); select(next);
    });
  });
});

/* ------------------------------ carousels -------------------------------
   Auto-advance pauses on hover, focus, touch and tab-away, and stops for good
   once the visitor takes control. Disabled entirely under reduced-motion.  */
document.querySelectorAll('[data-carousel]').forEach(root => {
  const track = root.querySelector('.track');
  const slides = [...track.children];
  const dotsWrap = root.querySelector('.dots');
  const prev = root.querySelector('[data-prev]');
  const next = root.querySelector('[data-next]');
  const toggle = root.querySelector('[data-playtoggle]');
  if (!track || slides.length < 2) return;

  let timer = null, stopped = reduced, paused = false;

  const dots = slides.map((_, i) => {
    const b = document.createElement('button');
    b.className = 'dot';
    b.type = 'button';
    b.setAttribute('aria-label', `Go to item ${i + 1}`);
    b.addEventListener('click', () => { halt(); scrollToIndex(i); });
    dotsWrap && dotsWrap.appendChild(b);
    return b;
  });

  const current = () => {
    const x = track.scrollLeft;
    let best = 0, dist = Infinity;
    slides.forEach((s, i) => {
      const d = Math.abs(s.offsetLeft - track.offsetLeft - x);
      if (d < dist) { dist = d; best = i; }
    });
    return best;
  };
  const sync = () => {
    const c = current();
    dots.forEach((d, i) => d.setAttribute('aria-current', String(i === c)));
  };
  const scrollToIndex = i => {
    const s = slides[(i + slides.length) % slides.length];
    track.scrollTo({ left: s.offsetLeft - track.offsetLeft, behavior: reduced ? 'auto' : 'smooth' });
  };
  const advance = () => {
    const c = current();
    scrollToIndex(c >= slides.length - 1 ? 0 : c + 1);
  };

  const start = () => { if (stopped || paused || timer) return; timer = setInterval(advance, 5000); };
  const pause = () => { clearInterval(timer); timer = null; };
  const halt = () => { stopped = true; pause(); if (toggle) toggle.hidden = true; };

  track.addEventListener('scroll', () => requestAnimationFrame(sync), { passive: true });
  ['mouseenter', 'focusin'].forEach(ev => root.addEventListener(ev, () => { paused = true; pause(); }));
  ['mouseleave', 'focusout'].forEach(ev => root.addEventListener(ev, () => { paused = false; start(); }));
  track.addEventListener('pointerdown', halt, { once: true });
  track.addEventListener('wheel', halt, { once: true, passive: true });
  document.addEventListener('visibilitychange', () => document.hidden ? pause() : start());

  prev && prev.addEventListener('click', () => { halt(); scrollToIndex(current() - 1); });
  next && next.addEventListener('click', () => { halt(); scrollToIndex(current() + 1); });
  if (toggle) {
    if (reduced) toggle.hidden = true;
    toggle.addEventListener('click', () => {
      if (timer) { pause(); stopped = true; toggle.setAttribute('aria-label', 'Play slideshow'); }
      else { stopped = false; start(); toggle.setAttribute('aria-label', 'Pause slideshow'); }
    });
  }
  sync();
  start();
});

/* ------------------------------ smooth scroll --------------------------- */
if (!reduced) {
  import('https://cdn.jsdelivr.net/npm/lenis@1.1.20/+esm').then(({ default: Lenis }) => {
    const lenis = new Lenis({ duration: 1.05, smoothWheel: true });
    const raf = t => { lenis.raf(t); requestAnimationFrame(raf); };
    requestAnimationFrame(raf);
    document.querySelectorAll('a[href^="#"]').forEach(a => {
      a.addEventListener('click', e => {
        const t = document.querySelector(a.getAttribute('href'));
        if (t) { e.preventDefault(); lenis.scrollTo(t, { offset: -80 }); }
      });
    });
  }).catch(() => {});
}

/* ------------------------------ lightbox -------------------------------- */
if (document.querySelector('[data-pswp]')) {
  import('https://cdn.jsdelivr.net/npm/photoswipe@5.4.4/dist/photoswipe-lightbox.esm.min.js')
    .then(({ default: PhotoSwipeLightbox }) => {
      new PhotoSwipeLightbox({
        gallery: '[data-pswp]', children: 'a', bgOpacity: 0.96,
        pswpModule: () => import('https://cdn.jsdelivr.net/npm/photoswipe@5.4.4/dist/photoswipe.esm.min.js')
      }).init();
    }).catch(() => {});
}

/* ------------------------------ enquiry form ---------------------------- */
const form = document.getElementById('enquiry');
if (form) {
  const status = document.getElementById('formstatus');
  const btn = form.querySelector('button[type="submit"]');
  form.addEventListener('submit', async e => {
    e.preventDefault();
    const label = btn.textContent;
    btn.disabled = true; btn.textContent = 'Sending…';
    status.removeAttribute('data-state');
    try {
      const res = await fetch('https://api.web3forms.com/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(Object.fromEntries(new FormData(form)))
      });
      const data = await res.json();
      if (!data.success) throw new Error(data.message || 'failed');
      status.dataset.state = 'ok';
      status.textContent = 'Thank you — your enquiry has reached us. We usually reply within two working days.';
      form.reset();
    } catch {
      status.dataset.state = 'err';
      status.innerHTML = 'Something went wrong sending that. Please email us directly at ' +
        '<a href="mailto:sales@wf2f.in">sales@wf2f.in</a>.';
    } finally {
      btn.disabled = false; btn.textContent = label;
    }
  });
}
