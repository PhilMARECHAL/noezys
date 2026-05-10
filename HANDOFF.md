# LiegaCal — Handoff complet

> Document de reprise pour migrer la session vers **Claude Code Desktop**.
> Tout ce qu'il faut savoir pour comprendre, reprendre, déployer et faire évoluer le projet.

---

## 1. Contexte projet

**LiegaCal** — page de démo annonçant l'arrivée d'un nouveau fournisseur de granulats calcaires en région liégeoise. Page web ultra-premium, monumentale, cinématographique. Positionnement : renaissance du calcaire liégeois, fusion industrie lourde + luxe minéral + responsabilité environnementale.

**Statut actuel** : single-page complète, en français, déployable telle quelle. Branche pushée sur GitHub. Maquettes PNG générées.

---

## 2. Repo & branche

| Élément | Valeur |
|---|---|
| **Repo** | `PhilMARECHAL/noezys` (anciennement projet "Noezys" recyclé) |
| **Branche de travail** | `claude/liegacal-demo-site-gGcs1` |
| **Dernier commit** | `1caebfd` — « docs: swap PDF mockups for PNG (mobile-friendly) » |
| **Commits clés** | `5caebc7` (rebuild LiegaCal), `0adbbc6` (PDFs), `1caebfd` (PNGs) |
| **Working dir local** | `/home/user/noezys/` (sandbox web) — à recloner sur Desktop |

```bash
# Pour reprendre en local
git clone <url-du-repo> noezys
cd noezys
git checkout claude/liegacal-demo-site-gGcs1
```

---

## 3. Architecture des fichiers

```
noezys/
├── index.html                       # Page complète (FR, 6 sections)
├── style.css                        # Design system + responsive
├── main.js                          # Reveal, parallax, dust canvas
├── favicon.svg                      # Mark "L" copper sur fond pierre
├── render.yaml                      # Config Render (service "liegacal")
├── HANDOFF.md                       # ← ce fichier
├── liegacal-mockup-desktop.png      # Vue desktop full-page (1.9 MB)
├── liegacal-mockup-mobile.png       # Vue mobile full-page (4.8 MB)
└── liegacal-0[1-6]-*.png            # Captures par section (mobile)
```

Pas de build step. Site statique pur, ouvre `index.html` dans un navigateur.

---

## 4. Brief original (cahier des charges)

> Préservé verbatim pour que tout futur agent ait le contexte créatif intact.

**Projet** : LiegaCal — *« Le futur du calcaire liégeois commence ici. »*

**Objectif global** : créer une page internet ultra-premium, spectaculaire et émotionnelle annonçant l'arrivée d'un nouveau fournisseur de granulats calcaires en région liégeoise. Effet WOW immédiat ; sentiment de puissance ; émerveillement visuel ; fierté industrielle liégeoise ; perception haut de gamme ; crédibilité technique ; confiance environnementale.

**ADN émotionnel** : majesté de la roche, profondeur géologique, puissance minérale, beauté de la pierre bleue, patrimoine industriel liégeois, durabilité, fiabilité, noblesse du calcaire. Ton : cinématographique, monumental, spectaculaire, émotionnel, territorial, premium, militant local et durable.

**Inspirations** : Carmeuse, Lhoist, publicité automobile premium, documentaire nature cinématographique, esthétique monumentale industrielle.

**Structure narrative imposée** :
1. **Hero** — image fixe ultra-premium, falaise calcaire au lever du soleil, lumière dorée, aucun humain, aucun camion, aucune pollution. Titre : « Le futur du calcaire liégeois commence ici. » Sous-texte : « Une nouvelle référence du granulat durable arrive en région liégeoise. » CTA unique : « Demander un devis ».
2. **Fierté liégeoise** — « Une pierre née du berceau industriel liégeois. » Ancrage local, circuit court, savoir-faire régional.
3. **Durabilité** — « Construire durablement commence à la source. » CO₂ optimisé, biodiversité, intégration paysagère, logistique de proximité.
4. **Qualité** — « La qualité totale comme standard. » BENOR, constance granulométrique, fiabilité, chiffres clés.
5. **Gamme produits** — « Une gamme complète pour construire l'avenir. » 4/10, 10/20, 20/40, 80mm, sable, ballast, fillers, graves, gabions, pierre déco, enrochements.
6. **CTA final** — « Rejoignez la nouvelle génération du calcaire liégeois. » Bouton : « Demander un devis ».

**Identité visuelle** :
- Couleurs principales : bleu pierre bleue, gris minéral, noir profond, blanc pur.
- Couleurs secondaires : cuivre, doré discret.
- Typo : Montserrat / Helvetica Now / Inter / Neue Haas Grotesk. Titres grands, espacés, monumentaux.

**Animations** : parallaxe légère, mouvements lents, fade cinematic, transitions douces, glow discret, scrolling fluide. **Jamais d'effets cheap.**

**Interdictions** : stock photos bas de gamme, humains, trop de texte, surcharge visuelle, couleurs flashy, carrière sale, style corporate banal.

**SEO cible** : granulats calcaires Liège, carrière Liège, pierre bleue, granulat BENOR, calcaire durable, agrégats Wallonie, gravier calcaire Liège.

**Émotion finale visée** : *« LiegaCal n'est pas une carrière classique. C'est la renaissance du calcaire liégeois. »*

---

## 5. Décisions de design prises

### Palette implémentée (CSS variables dans `style.css`)
```css
--black-deep:    #06090C;   /* fond le plus profond */
--stone-night:   #0F1A22;   /* fond section 1 transition */
--stone-deep:    #16222C;   /* fond section produits */
--stone-blue:    #2D4A5C;   /* pierre bleue - accents */
--mineral-grey:  #6B7785;   /* texte secondaire */
--mineral-light: #B8BEC8;   /* texte courant */
--bone:          #E8E6E0;   /* texte fort, titres */
--copper:        #B87333;   /* accent cuivre */
--copper-light:  #D9B27A;   /* accent doré clair (CTA, marqueurs) */
--copper-pale:   #F0DCB6;   /* highlights */
```

### Typographies (Google Fonts)
- **Montserrat** (200, 300, 400, 500, 600) — display, titres, UI
- **Inter** (300, 400, 500, 600) — corps de texte
- **Cormorant Garamond** italique (400, 500) — italiques d'accent ("liégeois", "standard", "la source"...)

### Architecture animation
- **Hero** — SVG ViewBox 1600×900, 6 couches : sky gradient, sun glow + bloom, cliff far / mid / near, rim-light cuivre, strates calcaires fines, grain SVG. Parallaxe scroll en JS (vitesses différenciées par couche).
- **Mineral dust canvas** (`#dust`) — ~70 motes warm/cool dérivant lentement vers le haut, flicker sinusoïdal, opacity 0.5.
- **Reveal** — IntersectionObserver, threshold 0.15, stagger 0.09s entre enfants `[data-stagger]`.
- **Reduced-motion** — fallback complet (animations off, dust off, transitions instantanées).

### Choix UX
- **CTA unique** "Demander un devis" — répété nav + hero + final, tous pointent vers `#contact` (formulaire en bas).
- **Pas de menu de navigation** — single-page, scroll narratif, le seul élément cliquable du nav est le CTA.
- **Formulaire** — 5 champs (nom/entreprise, email, calibre, tonnage, message), `onsubmit` inline qui ajoute `.quote-form--sent` → confirmation visuelle. **Pas de backend** — démo seulement.

### Hero visuel — le compromis
Le brief demande **« image fixe ultra-premium »** photoréaliste d'une falaise calcaire au lever du soleil. **L'environnement de génération n'avait pas accès à un générateur d'images** → composition SVG vectorielle de remplacement (couches de falaises stylisées + soleil + grain). C'est élégant mais pas photoréaliste. **Pour la production réelle**, remplacer par une vraie photo (shoot dédié ou IA générative type Midjourney/Flux) placée comme `background-image` sur `.hero__scene`, et masquer/supprimer le SVG actuel.

---

## 6. Composants clés — où regarder

| Besoin | Fichier:lignes |
|---|---|
| Tokens couleur, typo, easings | `style.css:7-35` |
| Hero SVG (6 couches) | `index.html:51-92` |
| Animation soleil + parallaxe | `style.css:181-198`, `main.js:84-115` |
| Carte minimaliste de Liège | `index.html:131-156` |
| 4 piliers durabilité | `index.html:165-200` |
| Stats BENOR / ISO 9001 | `index.html:208-232` |
| Cartes produits + textures granulaires CSS | `index.html:241-307`, `style.css:430-475` |
| Formulaire devis + état envoyé | `index.html:317-358`, `style.css:565-620` |
| Mineral dust canvas | `main.js:13-65` |
| Reveal observer + stagger | `main.js:130-150` |
| Responsive (1024 / 720 / 480) | `style.css:705-770` |

---

## 7. Maquettes visuelles générées

Captures Playwright (Chromium headless) au commit `1caebfd` :

| Fichier | Format | Poids |
|---|---|---|
| `liegacal-mockup-desktop.png` | 1440×~7800 | 1.9 MB |
| `liegacal-mockup-mobile.png` | 390×~8400 @2x | 4.8 MB |
| `liegacal-01-hero.png` | iPhone hero | 662 KB |
| `liegacal-02-heritage.png` | iPhone héritage | 437 KB |
| `liegacal-03-sustainable.png` | iPhone durabilité | 201 KB |
| `liegacal-04-quality.png` | iPhone qualité | 155 KB |
| `liegacal-05-products.png` | iPhone gamme | 2.8 MB |
| `liegacal-06-cta-form.png` | iPhone CTA + form | 563 KB |

Pour régénérer après modifications, le script utilisé est `/tmp/render-png.js` (à recréer si besoin — voir section 9 « Scripts utilitaires »).

---

## 8. Gaps connus & roadmap suggérée

### Bloquants pour une mise en prod
- [ ] **Photo hero réelle** — remplacer la composition SVG par une photo professionnelle de falaise calcaire au lever du soleil (le brief était explicite là-dessus)
- [ ] **Backend formulaire** — actuellement `onsubmit` JS qui ne fait rien, il faut wirer un endpoint (Formspree, Netlify Forms, API custom...)
- [ ] **Mentions légales / RGPD** — page séparée + lien footer + bandeau cookies si analytics
- [ ] **Coordonnées réelles** — adresse, téléphone, email pro, n° d'entreprise (BCE)

### Améliorations qualité
- [ ] **OG image** dédiée (actuellement tags OG présents sans image associée)
- [ ] **Sitemap.xml + robots.txt**
- [ ] **Analytics** (Plausible recommandé pour cohérence "premium + sobre")
- [ ] **Tests Lighthouse** — viser 95+ partout (probable mais non vérifié dans le sandbox)
- [ ] **Test sur vrais devices** — pas pu être fait (pas de browser GUI dispo dans le sandbox de génération)

### Évolutions de contenu envisageables
- [ ] Section "Calendrier" — date prévisionnelle d'ouverture
- [ ] Page produits dédiée avec fiches techniques téléchargeables (PDF)
- [ ] Espace presse / contact commercial dédié
- [ ] Version néerlandaise (Wallonie ↔ Flandre)

### Évolutions techniques envisageables
- [ ] **Vraie image hero** + lazy loading + format AVIF/WebP avec fallback
- [ ] **Préchargement** des fonts critiques (`<link rel="preload">`)
- [ ] **Service worker** pour cache offline (optionnel)
- [ ] Migration vers Astro/11ty si le site grandit (multi-pages)

---

## 9. Scripts utilitaires utilisés

### Régénération des PNG (Playwright + Chromium headless)

```js
// render-png.js
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch({ args: ['--no-sandbox'] });
  const fileUrl = 'file://' + path.resolve('index.html');

  const PRINT_CSS = `
    *, *::before, *::after { animation: none !important; transition: none !important; }
    .reveal, [data-stagger], .anim-hero { opacity: 1 !important; transform: none !important; }
    .nav { background: rgba(6,9,12,.72) !important; backdrop-filter: blur(14px); }
    #dust { display: none !important; }
  `;

  // Desktop
  const ctxD = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const pageD = await ctxD.newPage();
  await pageD.goto(fileUrl, { waitUntil: 'networkidle' });
  await pageD.addStyleTag({ content: PRINT_CSS });
  await pageD.waitForTimeout(600);
  await pageD.screenshot({ path: 'liegacal-mockup-desktop.png', fullPage: true });

  // Mobile + sections
  const ctxM = await browser.newContext({
    viewport: { width: 390, height: 844 },
    deviceScaleFactor: 2, isMobile: true,
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15'
  });
  const pageM = await ctxM.newPage();
  await pageM.goto(fileUrl, { waitUntil: 'networkidle' });
  await pageM.addStyleTag({ content: PRINT_CSS });
  await pageM.waitForTimeout(600);
  await pageM.screenshot({ path: 'liegacal-mockup-mobile.png', fullPage: true });

  const sections = [
    ['#hero', '01-hero'],
    ['.section--heritage', '02-heritage'],
    ['.section--sustainable', '03-sustainable'],
    ['.section--quality', '04-quality'],
    ['.section--products', '05-products'],
    ['.section--cta', '06-cta-form']
  ];
  for (const [sel, name] of sections) {
    const el = await pageM.$(sel);
    if (el) {
      await el.scrollIntoViewIfNeeded();
      await pageM.waitForTimeout(150);
      await el.screenshot({ path: `liegacal-${name}.png` });
    }
  }
  await browser.close();
})();
```

Pré-requis sur Desktop :
```bash
npm i -D playwright
npx playwright install chromium
node render-png.js
```

---

## 10. Pour reprendre dans Claude Code Desktop

### Bootstrap rapide
1. Cloner le repo, checkout de la branche `claude/liegacal-demo-site-gGcs1`.
2. Ouvrir le dossier dans Claude Code Desktop.
3. Donner ce fichier `HANDOFF.md` à l'agent comme premier message ou `/init` si vous voulez une nouvelle CLAUDE.md générée.
4. Pour voir le rendu : ouvrir `index.html` directement dans un navigateur (pas de serveur requis), ou `npx serve .` pour un vrai HTTP local.

### Prompts utiles à donner
- *"Lis HANDOFF.md, j'ai besoin de remplacer le hero SVG par une vraie photo. Voici l'image : [path]. Adapte l'intégration."*
- *"Lis HANDOFF.md, ajoute un endpoint formulaire via Formspree. Mon ID : xxxx."*
- *"Lis HANDOFF.md et déploie sur Render via le `render.yaml` existant."*
- *"Lis HANDOFF.md, génère la version néerlandaise dans `index.nl.html` avec le même design system."*

### Commandes git utiles
```bash
git checkout claude/liegacal-demo-site-gGcs1   # branche actuelle
git log --oneline -10                          # derniers commits
git diff main..HEAD -- '*.html' '*.css' '*.js' # voir tout le rebuild
```

---

## 11. Vues complètes des derniers commits

```
1caebfd  docs: swap PDF mockups for PNG (mobile-friendly)
0adbbc6  docs: add visual PDF mockups (desktop + mobile)         [supprimé par 1caebfd]
5caebc7  feat: rebuild as LiegaCal — premium limestone quarry landing
9144a12  feat: use original PNG logo, remove eyebrow, bigger section labels   [Noezys, base]
1c1a90f  feat: initial Noezys single-page experience              [origine du repo]
```

`5caebc7` est le commit critique : 8 fichiers modifiés, +1386 / -895, refonte complète Noezys → LiegaCal, suppression de ~2.7 MB d'assets vidéo Noezys obsolètes.

---

*Document généré en fin de session sandbox web. Tout le code est dans le repo, ce fichier est la "carte" pour s'y retrouver.*
