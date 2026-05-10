/* ═══════════════════════════════════════════════════════════
   LIEGACAL — main.js
   Cinematic reveal · slow parallax · mineral light dust
   ═══════════════════════════════════════════════════════════ */

(function () {
  'use strict';

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ─────────────────────────────────────────────────────────
     1. MINERAL DUST CANVAS — slow drifting warm motes
     ───────────────────────────────────────────────────────── */
  const canvas = document.getElementById('dust');
  if (canvas && !reduceMotion) {
    const ctx = canvas.getContext('2d');
    let W, H, dpr;

    const resize = () => {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      W = window.innerWidth;
      H = window.innerHeight;
      canvas.width = W * dpr;
      canvas.height = H * dpr;
      canvas.style.width = W + 'px';
      canvas.style.height = H + 'px';
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    resize();
    window.addEventListener('resize', resize);

    const COUNT = Math.min(70, Math.floor((W * H) / 22000));
    const motes = [];
    for (let i = 0; i < COUNT; i++) {
      motes.push({
        x: Math.random() * W,
        y: Math.random() * H,
        vx: (Math.random() - 0.5) * 0.12,
        vy: -(0.04 + Math.random() * 0.18),
        r: 0.4 + Math.random() * 1.6,
        a: 0.08 + Math.random() * 0.32,
        warm: Math.random() < 0.6,
        pulse: Math.random() * Math.PI * 2,
      });
    }

    const tick = () => {
      ctx.clearRect(0, 0, W, H);
      for (const m of motes) {
        m.x += m.vx;
        m.y += m.vy;
        m.pulse += 0.012;

        if (m.y < -10) { m.y = H + 10; m.x = Math.random() * W; }
        if (m.x < -10) m.x = W + 10;
        if (m.x > W + 10) m.x = -10;

        const flicker = 0.6 + Math.sin(m.pulse) * 0.4;
        const alpha = m.a * flicker;
        const color = m.warm
          ? `rgba(217, 178, 122, ${alpha})`
          : `rgba(184, 190, 200, ${alpha * 0.7})`;

        ctx.beginPath();
        ctx.arc(m.x, m.y, m.r, 0, Math.PI * 2);
        ctx.fillStyle = color;
        ctx.fill();

        if (m.r > 1) {
          const g = ctx.createRadialGradient(m.x, m.y, 0, m.x, m.y, m.r * 5);
          g.addColorStop(0, m.warm ? `rgba(217,178,122,${alpha * 0.35})` : `rgba(184,190,200,${alpha * 0.2})`);
          g.addColorStop(1, 'rgba(0,0,0,0)');
          ctx.fillStyle = g;
          ctx.fillRect(m.x - m.r * 5, m.y - m.r * 5, m.r * 10, m.r * 10);
        }
      }
      requestAnimationFrame(tick);
    };
    tick();
  }

  /* ─────────────────────────────────────────────────────────
     2. HERO LOAD ANIMATION
     ───────────────────────────────────────────────────────── */
  const heroElements = document.querySelectorAll('.anim-hero');
  const triggerHero = () => {
    heroElements.forEach((el) => {
      const delay = parseFloat(el.dataset.delay) || 0;
      el.style.setProperty('--anim-delay', `${delay}s`);
      el.classList.add('visible');
    });
  };

  if (document.readyState === 'complete') {
    triggerHero();
  } else {
    window.addEventListener('load', triggerHero);
  }

  /* ─────────────────────────────────────────────────────────
     3. HERO PARALLAX — layered cliff + content
     ───────────────────────────────────────────────────────── */
  const heroContent = document.querySelector('.hero__content');
  const heroFar = document.querySelector('.hero__layer--far');
  const heroMid = document.querySelector('.hero__layer--mid');
  const heroNear = document.querySelector('.hero__layer--near');
  const heroSun = document.querySelector('.hero__sun');
  const heroHaze = document.querySelector('.hero__haze');

  let ticking = false;

  const onScroll = () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      const y = window.scrollY;
      const heroH = window.innerHeight;

      if (y < heroH * 1.2) {
        const p = y / heroH;

        if (heroContent) {
          heroContent.style.transform = `translateY(${y * 0.3}px)`;
          heroContent.style.opacity = String(Math.max(0, 1 - p * 1.4));
        }
        if (heroSun)  heroSun.setAttribute('transform',  `translate(0 ${y * 0.18})`);
        if (heroFar)  heroFar.setAttribute('transform',  `translate(0 ${y * 0.08})`);
        if (heroMid)  heroMid.setAttribute('transform',  `translate(0 ${y * 0.04})`);
        if (heroNear) heroNear.setAttribute('transform', `translate(0 ${y * -0.02})`);
        if (heroHaze) heroHaze.style.opacity = String(Math.min(1, 0.5 + p * 0.6));
      }

      // Nav background after scroll
      const nav = document.getElementById('nav');
      if (nav) nav.classList.toggle('is-scrolled', y > 30);

      ticking = false;
    });
  };

  if (!reduceMotion) {
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  } else {
    const nav = document.getElementById('nav');
    if (nav) nav.classList.add('is-scrolled');
  }

  /* ─────────────────────────────────────────────────────────
     4. SCROLL REVEAL — cinematic, with stagger
     ───────────────────────────────────────────────────────── */
  if (!reduceMotion && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          const staggerKids = entry.target.querySelectorAll('[data-stagger]');
          staggerKids.forEach((child, i) => {
            child.style.transitionDelay = `${0.08 + i * 0.09}s`;
            child.classList.add('visible');
          });
          entry.target.classList.add('visible');
          io.unobserve(entry.target);
        });
      },
      { threshold: 0.15, rootMargin: '0px 0px -60px 0px' }
    );
    document.querySelectorAll('.reveal').forEach((el) => io.observe(el));
  } else {
    document.querySelectorAll('.reveal, [data-stagger]').forEach((el) => {
      el.classList.add('visible');
    });
  }

  /* ─────────────────────────────────────────────────────────
     5. SMOOTH SCROLL — anchor links
     ───────────────────────────────────────────────────────── */
  document.querySelectorAll('a[href^="#"]').forEach((a) => {
    a.addEventListener('click', (e) => {
      const id = a.getAttribute('href');
      if (id === '#' || id.length < 2) return;
      const target = document.querySelector(id);
      if (!target) return;
      e.preventDefault();
      target.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'start' });
    });
  });

})();
