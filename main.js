/* ═══════════════════════════════════════════════════════════
   NOEZYS — main.js
   V3 · Intelligence Canvas — mouse-reactive particle network
   Inspired by Anthropic/Vercel/Linear hero patterns
   ═══════════════════════════════════════════════════════════ */

(function () {
  'use strict';

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ── 1. INTELLIGENCE CANVAS — Interactive particle network ── */

  const canvas = document.getElementById('cosmos');
  const ctx = canvas.getContext('2d');
  let W, H, dpr;

  // Mouse state with smooth lerp
  const mouse = { x: -9999, y: -9999, targetX: -9999, targetY: -9999, active: false };
  const MOUSE_RADIUS = 200;
  const MOUSE_REPEL = 0.03;
  const CONNECTION_DIST = 140;
  const MOUSE_CONNECTION_DIST = 220;

  function resize() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = window.innerWidth;
    H = window.innerHeight;
    canvas.width = W * dpr;
    canvas.height = H * dpr;
    canvas.style.width = W + 'px';
    canvas.style.height = H + 'px';
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }
  resize();
  window.addEventListener('resize', resize);

  // Mouse tracking
  document.addEventListener('mousemove', (e) => {
    mouse.targetX = e.clientX;
    mouse.targetY = e.clientY;
    mouse.active = true;
  });
  document.addEventListener('mouseleave', () => {
    mouse.active = false;
  });

  // ── Nodes (particles) ──
  const NODE_COUNT = 80;
  const nodes = [];

  function createNode(i) {
    const t = i / NODE_COUNT;
    const isCyan = t < 0.55;
    return {
      x: Math.random() * W,
      y: Math.random() * H,
      vx: (Math.random() - 0.5) * 0.3,
      vy: (Math.random() - 0.5) * 0.3,
      baseVx: (Math.random() - 0.5) * 0.3,
      baseVy: (Math.random() - 0.5) * 0.3,
      size: 1 + Math.random() * 2,
      baseSize: 1 + Math.random() * 2,
      opacity: 0.15 + Math.random() * 0.4,
      r: isCyan ? 0 : 139,
      g: isCyan ? 212 : 92,
      b: isCyan ? 255 : 246,
      pulseOffset: Math.random() * Math.PI * 2,
      pulseSpeed: 0.005 + Math.random() * 0.01,
    };
  }

  for (let i = 0; i < NODE_COUNT; i++) {
    nodes.push(createNode(i));
  }

  // ── Floating energy ribbons ──
  const RIBBON_COUNT = 5;
  const ribbons = [];

  for (let i = 0; i < RIBBON_COUNT; i++) {
    const isCyan = i < 3;
    ribbons.push({
      points: Array.from({ length: 6 }, () => ({
        x: Math.random() * W,
        y: Math.random() * H,
        vx: (Math.random() - 0.5) * 0.15,
        vy: (Math.random() - 0.5) * 0.1,
      })),
      r: isCyan ? 0 : 139,
      g: isCyan ? 212 : 92,
      b: isCyan ? 255 : 246,
      opacity: 0.015 + Math.random() * 0.02,
      width: 1 + Math.random() * 1.5,
    });
  }

  // ── Ambient glow orbs ──
  const orbs = [
    { x: 0.3, y: 0.4, r: 0, g: 212, b: 255, radius: 250, opacity: 0.03, phase: 0, speed: 0.002 },
    { x: 0.7, y: 0.35, r: 139, g: 92, b: 246, radius: 300, opacity: 0.025, phase: Math.PI, speed: 0.0015 },
    { x: 0.5, y: 0.6, r: 60, g: 150, b: 255, radius: 200, opacity: 0.02, phase: Math.PI * 0.5, speed: 0.0025 },
  ];

  // ── Main render loop ──
  let time = 0;

  function draw() {
    time++;
    ctx.clearRect(0, 0, W, H);

    // Smooth mouse lerp
    if (mouse.active) {
      mouse.x += (mouse.targetX - mouse.x) * 0.08;
      mouse.y += (mouse.targetY - mouse.y) * 0.08;
    } else {
      mouse.x += (-9999 - mouse.x) * 0.02;
      mouse.y += (-9999 - mouse.y) * 0.02;
    }

    // ── Background gradient ──
    const bgGrad = ctx.createRadialGradient(W * 0.5, H * 0.45, 0, W * 0.5, H * 0.45, Math.max(W, H) * 0.75);
    bgGrad.addColorStop(0, '#111B3A');
    bgGrad.addColorStop(0.35, '#0D1225');
    bgGrad.addColorStop(1, '#0A0E1A');
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, W, H);

    // ── Ambient glow orbs (pulsing) ──
    for (const orb of orbs) {
      orb.phase += orb.speed;
      const pulse = 0.6 + Math.sin(orb.phase) * 0.4;
      const ox = orb.x * W + Math.sin(orb.phase * 0.7) * 30;
      const oy = orb.y * H + Math.cos(orb.phase * 0.5) * 20;
      const g = ctx.createRadialGradient(ox, oy, 0, ox, oy, orb.radius);
      g.addColorStop(0, `rgba(${orb.r}, ${orb.g}, ${orb.b}, ${orb.opacity * pulse})`);
      g.addColorStop(1, `rgba(${orb.r}, ${orb.g}, ${orb.b}, 0)`);
      ctx.fillStyle = g;
      ctx.fillRect(ox - orb.radius, oy - orb.radius, orb.radius * 2, orb.radius * 2);
    }

    // ── Energy ribbons (flowing curves) ──
    for (const ribbon of ribbons) {
      for (const pt of ribbon.points) {
        pt.x += pt.vx;
        pt.y += pt.vy;
        if (pt.x < -50 || pt.x > W + 50) pt.vx *= -1;
        if (pt.y < -50 || pt.y > H + 50) pt.vy *= -1;
      }

      ctx.beginPath();
      ctx.moveTo(ribbon.points[0].x, ribbon.points[0].y);
      for (let i = 1; i < ribbon.points.length - 1; i++) {
        const cpx = (ribbon.points[i].x + ribbon.points[i + 1].x) / 2;
        const cpy = (ribbon.points[i].y + ribbon.points[i + 1].y) / 2;
        ctx.quadraticCurveTo(ribbon.points[i].x, ribbon.points[i].y, cpx, cpy);
      }
      ctx.strokeStyle = `rgba(${ribbon.r}, ${ribbon.g}, ${ribbon.b}, ${ribbon.opacity})`;
      ctx.lineWidth = ribbon.width;
      ctx.stroke();
    }

    // ── Update nodes ──
    for (const node of nodes) {
      // Pulse animation
      node.pulseOffset += node.pulseSpeed;
      const pulse = 0.7 + Math.sin(node.pulseOffset) * 0.3;

      // Mouse interaction — soft repel + size boost
      const dx = node.x - mouse.x;
      const dy = node.y - mouse.y;
      const dist = Math.sqrt(dx * dx + dy * dy);

      if (dist < MOUSE_RADIUS && dist > 0) {
        const force = (1 - dist / MOUSE_RADIUS) * MOUSE_REPEL;
        node.vx += (dx / dist) * force;
        node.vy += (dy / dist) * force;
        node.size = node.baseSize * (1 + (1 - dist / MOUSE_RADIUS) * 1.5);
      } else {
        node.size += (node.baseSize - node.size) * 0.05;
      }

      // Drift back to base velocity
      node.vx += (node.baseVx - node.vx) * 0.01;
      node.vy += (node.baseVy - node.vy) * 0.01;

      // Apply velocity with damping
      node.x += node.vx;
      node.y += node.vy;
      node.vx *= 0.99;
      node.vy *= 0.99;

      // Wrap around edges
      if (node.x < -20) node.x = W + 20;
      if (node.x > W + 20) node.x = -20;
      if (node.y < -20) node.y = H + 20;
      if (node.y > H + 20) node.y = -20;

      // Draw node with glow
      const nodeOpacity = node.opacity * pulse;
      ctx.beginPath();
      ctx.arc(node.x, node.y, node.size, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${node.r}, ${node.g}, ${node.b}, ${nodeOpacity})`;
      ctx.fill();

      // Glow halo for larger nodes
      if (node.baseSize > 2) {
        const glow = ctx.createRadialGradient(node.x, node.y, 0, node.x, node.y, node.size * 4);
        glow.addColorStop(0, `rgba(${node.r}, ${node.g}, ${node.b}, ${nodeOpacity * 0.3})`);
        glow.addColorStop(1, `rgba(${node.r}, ${node.g}, ${node.b}, 0)`);
        ctx.fillStyle = glow;
        ctx.fillRect(node.x - node.size * 4, node.y - node.size * 4, node.size * 8, node.size * 8);
      }
    }

    // ── Connections between close nodes ──
    ctx.lineWidth = 0.5;
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const a = nodes[i];
        const b = nodes[j];
        const dx = a.x - b.x;
        const dy = a.y - b.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < CONNECTION_DIST) {
          const alpha = (1 - dist / CONNECTION_DIST) * 0.12;
          // Blend colors between the two nodes
          const r = (a.r + b.r) / 2;
          const g = (a.g + b.g) / 2;
          const bl = (a.b + b.b) / 2;
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
          ctx.strokeStyle = `rgba(${r}, ${g}, ${bl}, ${alpha})`;
          ctx.stroke();
        }
      }
    }

    // ── Mouse glow cursor ──
    if (mouse.active && mouse.x > 0 && mouse.x < W) {
      // Cursor attraction lines to nearby nodes
      for (const node of nodes) {
        const dx = node.x - mouse.x;
        const dy = node.y - mouse.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < MOUSE_CONNECTION_DIST) {
          const alpha = (1 - dist / MOUSE_CONNECTION_DIST) * 0.08;
          ctx.beginPath();
          ctx.moveTo(mouse.x, mouse.y);
          ctx.lineTo(node.x, node.y);
          ctx.strokeStyle = `rgba(0, 212, 255, ${alpha})`;
          ctx.lineWidth = 0.4;
          ctx.stroke();
        }
      }

      // Cursor glow
      const cursorGlow = ctx.createRadialGradient(mouse.x, mouse.y, 0, mouse.x, mouse.y, 120);
      cursorGlow.addColorStop(0, 'rgba(0, 212, 255, 0.06)');
      cursorGlow.addColorStop(0.5, 'rgba(139, 92, 246, 0.02)');
      cursorGlow.addColorStop(1, 'rgba(0, 0, 0, 0)');
      ctx.fillStyle = cursorGlow;
      ctx.fillRect(mouse.x - 120, mouse.y - 120, 240, 240);
    }

    // ── Horizon line (subtle) ──
    const horizonY = H * 0.48;
    const hOpacity = 0.04 + Math.sin(time * 0.003) * 0.02;
    const horizonGrad = ctx.createLinearGradient(W * 0.1, horizonY, W * 0.9, horizonY);
    horizonGrad.addColorStop(0, 'rgba(0, 212, 255, 0)');
    horizonGrad.addColorStop(0.3, `rgba(0, 212, 255, ${hOpacity * 0.5})`);
    horizonGrad.addColorStop(0.5, `rgba(80, 150, 255, ${hOpacity})`);
    horizonGrad.addColorStop(0.7, `rgba(139, 92, 246, ${hOpacity * 0.5})`);
    horizonGrad.addColorStop(1, 'rgba(139, 92, 246, 0)');
    ctx.beginPath();
    ctx.moveTo(W * 0.1, horizonY);
    ctx.lineTo(W * 0.9, horizonY);
    ctx.strokeStyle = horizonGrad;
    ctx.lineWidth = 0.8;
    ctx.stroke();

    requestAnimationFrame(draw);
  }

  if (!prefersReducedMotion) {
    draw();
  } else {
    // Static fallback — gradient + a few static nodes
    resize();
    const grad = ctx.createRadialGradient(W * 0.5, H * 0.45, 0, W * 0.5, H * 0.45, Math.max(W, H) * 0.75);
    grad.addColorStop(0, '#111B3A');
    grad.addColorStop(0.35, '#0D1225');
    grad.addColorStop(1, '#0A0E1A');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, W, H);

    // Draw static nodes
    for (const node of nodes) {
      ctx.beginPath();
      ctx.arc(node.x, node.y, node.size, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${node.r}, ${node.g}, ${node.b}, ${node.opacity * 0.5})`;
      ctx.fill();
    }
  }

  /* ── 2. VIDEO BACKGROUND — robust autoplay ────────────────── */

  const bgVideo = document.getElementById('bg-video');
  if (bgVideo) {
    function tryPlay() {
      bgVideo.muted = true; // Ensure muted for autoplay policy
      const p = bgVideo.play();
      if (p) p.catch(() => {});
    }

    // Try immediately
    tryPlay();

    // Retry when video data is ready
    bgVideo.addEventListener('canplay', tryPlay, { once: true });
    bgVideo.addEventListener('loadeddata', tryPlay, { once: true });

    // Retry on first user interaction (some browsers need this)
    function playOnInteraction() {
      tryPlay();
      document.removeEventListener('click', playOnInteraction);
      document.removeEventListener('scroll', playOnInteraction);
      document.removeEventListener('mousemove', playOnInteraction);
    }
    document.addEventListener('click', playOnInteraction, { once: true });
    document.addEventListener('scroll', playOnInteraction, { once: true, passive: true });
    document.addEventListener('mousemove', playOnInteraction, { once: true });

    // Retry after page fully loads
    window.addEventListener('load', tryPlay);

    bgVideo.addEventListener('error', () => {
      bgVideo.parentElement.classList.add('video-hidden');
    });

    // Pause video when tab not visible
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        bgVideo.pause();
      } else {
        tryPlay();
      }
    });
  }

  /* ── 3. HERO LOAD ANIMATION ─────────────────────────────── */

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

  /* ── 4. HERO PARALLAX ON SCROLL ─────────────────────────── */

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

  /* ── 5. SCROLL REVEAL — staggered IntersectionObserver ───── */

  if (!prefersReducedMotion) {
    const revealObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            // Stagger children with data-stagger attribute
            const staggerChildren = entry.target.querySelectorAll('[data-stagger]');
            if (staggerChildren.length > 0) {
              staggerChildren.forEach((child, i) => {
                child.style.transitionDelay = `${i * 0.12}s`;
                child.classList.add('visible');
              });
            }
            entry.target.classList.add('visible');
            revealObserver.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
    );

    document.querySelectorAll('.reveal').forEach((el) => {
      revealObserver.observe(el);
    });
  } else {
    document.querySelectorAll('.reveal, [data-stagger]').forEach((el) => {
      el.classList.add('visible');
    });
  }

})();
