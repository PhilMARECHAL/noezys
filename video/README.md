# Noezys — vidéos 30 s

> **📘 Voir `MODE-OPERATOIRE.md`** pour le mode opératoire complet :
> régénération à l'identique, charte verrouillée, points d'ajustement du
> contenu, bande-son et contrôle qualité.

Vidéo « kinetic typography » (1920×1080, 30 fps, 30 s) pour www.noezys.com,
générée à partir d'une animation HTML rendue image par image.

## Fichiers

- `scene.html` — l'animation complète, pilotée par `window.seek(t)` (déterministe)
- `render.mjs` — capture les 900 frames avec Chromium puis encode en MP4 (ffmpeg)
- `noezys-30s.mp4` — le rendu final
- `photos/photo1.png … photo3.png` — photos affichées dans la séquence des valeurs
  (Authenticity / Creativity / Impact)
- `fonts/` — police Outfit (woff2, chargée en local pour un rendu reproductible)

## Remplacer les photos

Écraser simplement `photos/photo1.png`, `photo2.png`, `photo3.png`
(idéalement format paysage, ≥ 1200 px de large), puis relancer le rendu :

```bash
cd video
npm install        # une seule fois
node render.mjs    # → noezys-30s.mp4
```

## Timeline

| Temps | Scène |
|---|---|
| 0–3.3 s | « Technology should serve **people**. » (mots percutants, fond navy) |
| 3.3–6.5 s | « Not the other way around. » + logo N qui tombe en rotation (fond clair) |
| 6.5–10 s | « AI that works for you, even *while* you sleep. » (texte lumineux) |
| 10–14 s | Clin d'œil méta : « PROBLEM! Nobody said who we are yet. Let me fix that.. » |
| 14–17.3 s | Révélation du logo NOEZYS + AI Innovation Lab |
| 17.3–21.8 s | Valeurs en cuts rapides : Authenticity / Creativity / Impact + photos |
| 21.8–25.8 s | Mission : « Transforming everyday life with sustainable digital solutions. » |
| 25.8–30 s | Carte finale : logo, www.noezys.com, particules |
