# MODE OPÉRATOIRE — Vidéos Noezys 30 s

> Document de référence pour régénérer **à l'identique** les vidéos publicitaires
> Noezys, puis appliquer des ajustements de contenu **sans jamais toucher à
> l'identité visuelle**. Rédigé après la production validée du 6 août 2026
> (commit `e6cd1a6`, branche `claude/noezys-30sec-video-0m1k07`).

---

## 1. Vue d'ensemble du pipeline

Le pipeline est 100 % reproductible et déterministe — aucun outil externe de
génération vidéo, aucune dépendance cloud :

```
pub.html (animation HTML/CSS/JS pilotée par window.seek(t))
   │  Chromium headless capture 900 frames (30 s × 30 fps, 1920×1080)
   ▼
frames/f0000.png … f0899.png
   │  ffmpeg → H.264 CRF 18, yuv420p, faststart
   ▼
noezys-pub-<lang>.mp4 (muet)
   │  + music-pub.wav (synthèse numpy, déterministe, seed 42)
   │  ffmpeg mux → AAC 192k
   ▼
noezys-pub-<lang>.mp4 (final avec son)
```

**Trois vidéos existent** :

| Fichier | Contenu | Scène source | Musique |
|---|---|---|---|
| `noezys-pub-fr.mp4` | Pub génération de clients, FR | `pub.html?lang=fr` | `music-pub.wav` |
| `noezys-pub-en.mp4` | Pub génération de clients, EN | `pub.html?lang=en` | `music-pub.wav` |
| `noezys-30s.mp4` | Vidéo de marque (valeurs, gag méta) | `scene.html` | `music-brand.wav` |

---

## 2. Charte graphique — VERROUILLÉE, ne jamais modifier

Ces valeurs viennent du site www.noezys.com (`style.css` à la racine du repo).
Tout ajustement de contenu doit les conserver strictement.

| Élément | Valeur |
|---|---|
| Fond sombre principal | `#0A0E1A` (`--bg-deep`), variante `#0D1225` (`--bg-mid`) |
| Accent cyan | `#00D4FF` |
| Accent violet | `#8B5CF6` |
| Dégradé de marque | `linear-gradient(90deg, #00D4FF, #8B5CF6)` (classe `.grad-text`) |
| Texte principal | `#F0F3FA` — texte secondaire `#8A96B4` — tertiaire `#4A5570` |
| Fond clair (scènes light) | `linear-gradient(160deg, #F2F4F8, #DDE2EC)`, encre `#0B0F1E` |
| Police | **Outfit** exclusivement (300→800, woff2 **locaux** dans `video/fonts/`) |
| Logo | `assets/noezys-n-mark.png` (ne jamais recréer/redessiner) |
| Nom | Toujours `NOEZYS` en capitales, poids 600 |
| Signature | `AI INNOVATION LAB` en lettres espacées (letter-spacing ~14 px) |
| URL | `www.noezys.com` toujours en `.grad-text` |
| Format | 1920×1080, 30 fps, 30.0 s exactement |

**ADN visuel du style** (hérité de la vidéo de référence « Romain Torres ») :
- Mots qui « claquent » un par un : scale 1.9→1 + blur 10→0 px, easing `outExpo`, ~0,32 s par mot
- Logo N qui **tombe en rotation** avec rebond (`outBack`) sur la scène claire
- Texte « lumineux » (text-shadow blanc + halo cyan/violet) sur fond quasi noir
- Cuts francs entre scènes (pas de fondus enchaînés)
- Carte finale avec particules dérivantes (42 points, positions déterministes)
- Un seul mot ou groupe clé en dégradé cyan→violet par scène, jamais plus

---

## 3. Prérequis environnement

À exécuter une fois par session/machine neuve :

```bash
# 1. ffmpeg (absent par défaut)
apt-get update && apt-get install -y ffmpeg

# 2. dépendances node du dossier video/ (playwright-core)
cd video && npm install

# 3. numpy pour la musique
pip3 install numpy
```

**Chromium** : déjà présent dans l'environnement Claude Code remote.
`render-pub.mjs` cherche dans l'ordre :
`/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell`
puis `/opt/pw-browsers/chromium-1194/chrome-linux/chrome`. Si la version
change, adapter ces deux chemins (lister `/opt/pw-browsers/`).

**Polices** : les woff2 d'Outfit sont **committés** dans `video/fonts/` —
ne pas les re-télécharger, c'est ce qui garantit un rendu identique au pixel.

---

## 4. Régénérer les vidéos à l'identique

```bash
cd video

# Pub FR + EN (≈ 3-4 min chacune)
node render-pub.mjs fr        # → noezys-pub-fr.mp4 (muet)
node render-pub.mjs en        # → noezys-pub-en.mp4 (muet)

# Vidéo de marque
node render.mjs               # → noezys-30s.mp4 (muet)

# Bandes-son (déterministes — mêmes fichiers à l'octet près, seed 42)
python3 make-music.py music-pub.wav   "0,4,7.5,11,15,19,25" 11 19
python3 make-music.py music-brand.wav "0,3.3,6.5,10,14,17.3,21.8,25.8" 17.3 21.8

# Mux audio (remplace les mp4 en place)
for v in noezys-pub-fr noezys-pub-en; do
  ffmpeg -y -loglevel error -i $v.mp4 -i music-pub.wav -map 0:v -map 1:a \
    -c:v copy -c:a aac -b:a 192k -shortest $v-new.mp4 && mv $v-new.mp4 $v.mp4
done
ffmpeg -y -loglevel error -i noezys-30s.mp4 -i music-brand.wav -map 0:v -map 1:a \
  -c:v copy -c:a aac -b:a 192k -shortest tmp.mp4 && mv tmp.mp4 noezys-30s.mp4
```

Les arguments de `make-music.py` : liste des frontières de scènes en secondes
(impacts/accords calés dessus), puis fenêtre d'énergie (héritage, la montée est
progressive). **Si un timing de scène change dans pub.html, reporter la même
valeur dans la liste des frontières.**

---

## 5. Timeline et contenu actuels (script v3 « flyers », validé scène par scène)

Script construit avec le client à partir de ses **deux flyers** (recto « L'IA,
intégrée à votre métier » + verso « Bonjour, ») : ouverture par la promesse,
puis le verso déroulé dans l'ordre, révisé par un panel d'experts pour sonner
humain (zéro tiret à l'écran, anglais natif, pas de tournures « IA »).

| Scène | Temps | FR | EN |
|---|---|---|---|
| S1 ouverture | 0–4 s | **L'intelligence artificielle,** intégrée à votre métier. | **Artificial intelligence,** built into your business. |
| S2 mission | 4–7,5 s | Gagner du temps. Faire grandir votre **chiffre d'affaires**. | Save time. Grow your **revenue**. |
| S3 logo | 7,5–11 s | NOEZYS · AI INNOVATION LAB | idem |
| S4 carte 01 | 11–15 s | Des solutions **sur mesure** pour vous. / Site web, logiciel, applications mobiles, avec le meilleur de l'IA. | Solutions built around **you**. / Websites, software and mobile apps that put AI to work for you. |
| S4 carte 02 | 15–19 s | Pas seulement une IA. / Une **vraie équipe** qui vous écoute et vous accompagne. | Not just AI. / A **real team** that listens and stays by your side. |
| S5 équipe | 19–25 s | L'ÉQUIPE NOEZYS · Authenticité. Impact. Créativité. · **Le contact humain avant tout.** | THE NOEZYS TEAM · Authenticity. Impact. Creativity. · **Human connection comes first.** |
| S6 finale | 25–30 s | 30 minutes. Un plan d'action concret. Sans engagement. + www.noezys.com + ligne verte SOLUTIONS DIGITALES DURABLES · IA RESPONSABLE | 30 minutes. A clear action plan. No strings attached. + SUSTAINABLE DIGITAL SOLUTIONS · RESPONSIBLE AI |

Nouveauté charte : la ligne signature finale est **verte** (`#55B97E`, var
`--green`), reprise de la ligne écologique du flyer — seule entorse autorisée
au duo cyan/violet. Les frontières musicales suivent ces timings
(`0,4,7.5,11,15,19,25`).

---

## 6. Où faire les ajustements de contenu

**Tous les textes** de la pub sont dans **un seul endroit** : l'objet `COPY`
en tête du `<script>` de `video/pub.html` (clés `fr:` et `en:` côte à côte).

| Pour changer… | Modifier |
|---|---|
| L'ouverture (S1) | `COPY.<lang>.s1` — tableau de lignes ; chaque ligne = tableau de `["mot "]` (garder l'espace final) ; `["mot ",true]` = mot en dégradé |
| La mission (S2) | `COPY.<lang>.s2` — même format que s1 |
| Les 2 cartes | `COPY.<lang>.cases` — `{head, sub}` ×2, HTML autorisé (`<span class="grad-text">` pour un mot en dégradé) |
| La scène équipe | `COPY.<lang>.label` (petit titre espacé), `values` (3 mots qui claquent), `sig` (ligne en dégradé) |
| Le CTA final | `COPY.<lang>.cta` |
| La ligne verte finale | `COPY.<lang>.eco` |
| Un timing de scène | Tableau `scenes` (champs `a`/`b`) — **reporter les nouvelles frontières dans l'appel `make-music.py`** |
| Des photos/visuels | Ajouter un bloc dans la scène concernée sur le modèle `.photocard` de `scene.html` (cadre blanc 16 px, radius 14, rotation ±5°, pop `outBack`) |

**Règles d'or lors d'un ajustement :**
1. Ne toucher qu'au **contenu** (textes, cas d'usage, photos) — jamais aux
   styles CSS, couleurs, police, easings, ni à la mécanique `seek(t)`.
2. Textes courts : max ~2 lignes affichées par scène ; si un texte déborde,
   réduire le texte, pas la taille de police.
3. Toujours prévisualiser avant le rendu complet (§7).
4. FR et EN doivent rester synchronisés (même sens, même scène).

---

## 7. Contrôle qualité avant livraison

Prévisualiser des images clés sans rendre les 900 frames — créer un script
jetable sur ce modèle (déjà utilisé en production) :

```js
// preview.mjs (jetable, ne pas committer)
import { chromium } from 'playwright-core';
import fs from 'node:fs'; import path from 'node:path'; import { fileURLToPath } from 'node:url';
const DIR = path.dirname(fileURLToPath(import.meta.url));
const exe = ['/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell',
             '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'].find(p=>fs.existsSync(p));
const browser = await chromium.launch({ executablePath: exe });
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
await page.goto('file://' + path.join(DIR, 'pub.html') + '?lang=fr');
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(400);
for (const t of [2.5, 6.0, 9.5, 13.0, 16.5, 19.5, 22.5, 25.5, 29.3]) {
  await page.evaluate(t => window.seek(t), t);
  await page.screenshot({ path: path.join(DIR, `pp-${t}.png`) });
}
await browser.close();
```

Checklist visuelle sur ces captures :
- [ ] Aucun texte tronqué ni débordant, espaces entre mots corrects
- [ ] Mots en dégradé = uniquement ceux voulus
- [ ] Logo N net, jamais déformé ni recoloré
- [ ] FR et EN vérifiés tous les deux

Checklist finale sur les mp4 :
- [ ] `ffprobe` : durée 30.000000, piste audio aac présente
- [ ] Extraire 2-3 frames (`ffmpeg -ss <t> -frames:v 1`) pour vérification
- [ ] Volume : `ffmpeg -af volumedetect` → mean ≈ −14 dB, max > −1,5 dB

---

## 8. Bande-son — paramètres du caractère validé

Style validé par le client : **dynamique, percutant, montée en puissance
« symphonique »** (la v1 ambiante a été rejetée comme trop calme).

Caractéristiques dans `make-music.py` :
- **120 BPM** (`BEAT = 0.5`), kick 4/4 dès la seconde 0
- Progression **Am9 → Fmaj9 → Cmaj9 → Gadd9**, résolution Cmaj9 sur la fin
- Montée par paliers : `ramp = [0.7, 0.78, 0.86, 0.94, 1.0]` sur les frontières
- Couches entrantes : basse pulsée (t0) → arpèges 16èmes (frontière 1) →
  claps (frontière 2) → hats 16èmes + lead (pleine puissance)
- Roulements + risers avant les frontières majeures (indices 3, 4 et dernière) ;
  **climax tenu** sur la carte finale (pas de retombée), impact final à 29 s
- Mastering : `tanh(mix*2.1)`, normalisation 0,92, mean ≈ −14 dB
- **Déterministe** : seed 42 — même WAV à chaque exécution

Ajustements possibles sans changer le caractère : tempo (`BEAT`), niveaux des
couches (coefficients `0.30` kick, `0.16` clap, `0.075` hats, `0.05` arp/lead),
courbe `ramp`. Pour un morceau du commerce : remplacer le WAV et relancer le mux.

---

## 9. Livraison

1. Committer **les sources et les mp4 finaux** (les `frames/` et
   `node_modules/` sont gitignorés), pousser sur la branche de travail.
2. Envoyer les mp4 au client via le canal de la session.
3. Les fichiers `music-*.wav` et les previews `pp-*.png` sont des
   intermédiaires : ne pas les committer (régénérables à l'identique).

## 10. Déclinaisons prévues (non produites à ce jour)

- **9:16 (1080×1920)** pour Reels/TikTok : dupliquer `pub.html`, adapter
  `html,body`/`#stage` à 1080×1920, re-centrer les scènes (empiler
  verticalement la scène S5 : numéro au-dessus du texte), textes ~20 % plus gros.
- **1:1 (1080×1080)** pour feed : même approche.
- Le viewport de `render-pub.mjs` doit suivre les nouvelles dimensions.
- La bande-son est réutilisable telle quelle si les timings ne changent pas.
