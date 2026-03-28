/* ═══════════════════════════════════════════════════════════
   NOEZYS — main.js
   V2 · Cyan→Purple cosmos + scroll interactions
   ═══════════════════════════════════════════════════════════ */

(function () {
  'use strict';

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ── 1. CANVAS — Cosmos background ──────────────────────── */

  const canvas = document.getElementById('cosmos');
  const ctx = canvas.getContext('2d');
  let W, H;
  let animationId;

  function resize() {
    W = canvas.width = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }
  resize();
  window.addEventListener('resize', resize);

  // Particles — cyan and purple palette
  const PARTICLE_COUNT = 90;
  const particles = [];

  function createParticle() {
    const isPurple = Math.random() < 0.4;
    const cx = W * 0.5;
    const cy = H * 0.48;
    const angle = Math.random() * Math.PI * 2;
    const radiusX = 80 + Math.random() * (W * 0.45);
    const radiusY = 60 + Math.random() * (H * 0.38);
    return {
      cx, cy,
      angle,
      radiusX, radiusY,
      speed: (0.0001 + Math.random() * 0.0003) * (Math.random() < 0.5 ? 1 : -1),
      size: 0.5 + Math.random() * 1.5,
      opacity: 0.08 + Math.random() * 0.25,
      color: isPurple
        ? `rgba(139, 92, 246, VAR_OPACITY)`
        : `rgba(0, 212, 255, VAR_OPACITY)`,
    };
  }

  for (let i = 0; i < PARTICLE_COUNT; i++) {
    particles.push(createParticle());
  }

  // Energy lines flowing toward center
  const LINE_COUNT = 14;
  const energyLines = [];

  function createEnergyLine() {
    const side = Math.floor(Math.random() * 4);
    let startX, startY;
    switch (side) {
      case 0: startX = Math.random() * W; startY = 0; break;
      case 1: startX = W; startY = Math.random() * H; break;
      case 2: startX = Math.random() * W; startY = H; break;
      case 3: startX = 0; startY = Math.random() * H; break;
    }
    const isCyan = Math.random() < 0.6;
    return {
      startX, startY,
      endX: W * 0.5 + (Math.random() - 0.5) * 100,
      endY: H * 0.48 + (Math.random() - 0.5) * 60,
      progress: Math.random(),
      speed: 0.0004 + Math.random() * 0.0006,
      opacity: 0.02 + Math.random() * 0.04,
      rotationOffset: Math.random() * Math.PI * 2,
      rotationSpeed: (0.00005 + Math.random() * 0.0001) * (Math.random() < 0.5 ? 1 : -1),
      r: isCyan ? 0 : 139,
      g: isCyan ? 212 : 92,
      b: isCyan ? 255 : 246,
    };
  }

  for (let i = 0; i < LINE_COUNT; i++) {
    energyLines.push(createEnergyLine());
  }

  // Horizon line at 48%
  let horizonPulse = 0;
  const horizonSpeed = 0.003;

  // Center shimmer
  let shimmerPhase = 0;
  const shimmerSpeed = 0.004;

  function drawCosmos(time) {
    ctx.clearRect(0, 0, W, H);

    // Radial gradient background — deep navy with subtle blue core
    const grad = ctx.createRadialGradient(W * 0.5, H * 0.48, 0, W * 0.5, H * 0.48, Math.max(W, H) * 0.7);
    grad.addColorStop(0, '#111B3A');
    grad.addColorStop(0.4, '#0D1225');
    grad.addColorStop(1, '#0A0E1A');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, W, H);

    // Energy lines — cyan and purple
    for (const line of energyLines) {
      line.progress += line.speed;
      line.rotationOffset += line.rotationSpeed;
      if (line.progress > 1) line.progress = 0;

      const cx = W * 0.5;
      const cy = H * 0.48;
      const cos = Math.cos(line.rotationOffset);
      const sin = Math.sin(line.rotationOffset);

      const dx = line.startX - cx;
      const dy = line.startY - cy;
      const rx = cx + dx * cos - dy * sin;
      const ry = cy + dx * sin + dy * cos;

      const lineGrad = ctx.createLinearGradient(rx, ry, line.endX, line.endY);
      lineGrad.addColorStop(0, `rgba(${line.r}, ${line.g}, ${line.b}, 0)`);
      lineGrad.addColorStop(Math.max(0, line.progress - 0.15), `rgba(${line.r}, ${line.g}, ${line.b}, 0)`);
      lineGrad.addColorStop(line.progress, `rgba(${line.r}, ${line.g}, ${line.b}, ${line.opacity})`);
      lineGrad.addColorStop(Math.min(1, line.progress + 0.05), `rgba(${line.r}, ${line.g}, ${line.b}, 0)`);

      ctx.beginPath();
      ctx.moveTo(rx, ry);
      ctx.lineTo(line.endX, line.endY);
      ctx.strokeStyle = lineGrad;
      ctx.lineWidth = 0.5;
      ctx.stroke();
    }

    // Horizon line — cyan→purple gradient
    horizonPulse += horizonSpeed;
    const horizonY = H * 0.48;
    const horizonOpacity = 0.06 + Math.sin(horizonPulse) * 0.03;
    const horizonGrad = ctx.createLinearGradient(W * 0.15, horizonY, W * 0.85, horizonY);
    horizonGrad.addColorStop(0, 'rgba(0, 212, 255, 0)');
    horizonGrad.addColorStop(0.25, `rgba(0, 212, 255, ${horizonOpacity * 0.6})`);
    horizonGrad.addColorStop(0.5, `rgba(80, 150, 255, ${horizonOpacity})`);
    horizonGrad.addColorStop(0.75, `rgba(139, 92, 246, ${horizonOpacity * 0.6})`);
    horizonGrad.addColorStop(1, 'rgba(139, 92, 246, 0)');

    ctx.beginPath();
    ctx.moveTo(W * 0.15, horizonY);
    ctx.lineTo(W * 0.85, horizonY);
    ctx.strokeStyle = horizonGrad;
    ctx.lineWidth = 1;
    ctx.stroke();

    // Center shimmer — dual glow (cyan + purple)
    shimmerPhase += shimmerSpeed;
    const shimmerOpacity = 0.04 + Math.sin(shimmerPhase) * 0.025;

    const shimmerCyan = ctx.createRadialGradient(W * 0.48, H * 0.48, 0, W * 0.48, H * 0.48, 100);
    shimmerCyan.addColorStop(0, `rgba(0, 212, 255, ${shimmerOpacity * 0.7})`);
    shimmerCyan.addColorStop(1, 'rgba(0, 212, 255, 0)');
    ctx.fillStyle = shimmerCyan;
    ctx.fillRect(W * 0.48 - 100, H * 0.48 - 100, 200, 200);

    const shimmerPurple = ctx.createRadialGradient(W * 0.52, H * 0.47, 0, W * 0.52, H * 0.47, 120);
    shimmerPurple.addColorStop(0, `rgba(139, 92, 246, ${shimmerOpacity * 0.5})`);
    shimmerPurple.addColorStop(1, 'rgba(139, 92, 246, 0)');
    ctx.fillStyle = shimmerPurple;
    ctx.fillRect(W * 0.52 - 120, H * 0.47 - 120, 240, 240);

    // Particles
    for (const p of particles) {
      p.angle += p.speed;
      const x = p.cx + Math.cos(p.angle) * p.radiusX;
      const y = p.cy + Math.sin(p.angle) * p.radiusY;

      const col = p.color.replace('VAR_OPACITY', p.opacity.toString());
      ctx.beginPath();
      ctx.arc(x, y, p.size, 0, Math.PI * 2);
      ctx.fillStyle = col;
      ctx.fill();
    }

    animationId = requestAnimationFrame(drawCosmos);
  }

  if (!prefersReducedMotion) {
    drawCosmos(0);
  } else {
    // Static fallback
    resize();
    const grad = ctx.createRadialGradient(W * 0.5, H * 0.48, 0, W * 0.5, H * 0.48, Math.max(W, H) * 0.7);
    grad.addColorStop(0, '#111B3A');
    grad.addColorStop(0.4, '#0D1225');
    grad.addColorStop(1, '#0A0E1A');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, W, H);
  }

  /* ── 2. HERO LOAD ANIMATION ─────────────────────────────── */

  const heroElements = document.querySelectorAll('.anim-hero');

  window.addEventListener('load', () => {
    heroElements.forEach((el) => {
      const delay = parseFloat(el.dataset.delay) || 0;
      const isTitle = el.classList.contains('hero__title');
      el.style.setProperty('--anim-delay', `${delay}s`);
      el.style.setProperty('--anim-duration', isTitle ? '1.4s' : '1.2s');
      el.classList.add('visible');
    });
  });

  /* ── 3. HERO PARALLAX ON SCROLL ─────────────────────────── */

  const heroContent = document.querySelector('.hero__content');
  let ticking = false;

  function onScroll() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      const scrollY = window.scrollY;
      const heroH = window.innerHeight;

      if (scrollY < heroH && heroContent) {
        const progress = scrollY / heroH;
        const translateY = scrollY * 0.22;
        const opacity = 1 - progress * 1.5;
        heroContent.style.transform = `translateY(${translateY}px)`;
        heroContent.style.opacity = Math.max(0, opacity);
      }

      ticking = false;
    });
  }

  if (!prefersReducedMotion) {
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* ── 4. SCROLL REVEAL — IntersectionObserver ────────────── */

  if (!prefersReducedMotion) {
    const revealObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            revealObserver.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12 }
    );

    document.querySelectorAll('.reveal').forEach((el) => {
      revealObserver.observe(el);
    });
  } else {
    document.querySelectorAll('.reveal').forEach((el) => {
      el.classList.add('visible');
    });
  }

})();
