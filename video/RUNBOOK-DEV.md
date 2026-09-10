# RUNBOOK DÉVELOPPEUR — Projet vidéos NOEZYS

Comment récupérer tous les fichiers et **tout reproduire depuis n'importe quelle
machine** (Linux / macOS ; Windows via WSL recommandé).

Le projet mélange deux mondes :
1. **Pipeline local déterministe** : animations HTML pilotées par `window.seek(t)`,
   capturées image par image avec Chromium (Playwright), encodées en MP4 (ffmpeg).
   → 0 coût, 100 % reproductible.
2. **Générations IA** (images / clips animés / voix) via **Higgsfield** (CLI).
   → coûte des crédits, compte requis.

---

## 0. Pré-requis

| Outil | Version testée | Installation |
|---|---|---|
| git | 2.43+ | système |
| Node.js | 22.x | https://nodejs.org (ou nvm) |
| Python | 3.11+ | système (pour la synthèse audio numpy) |
| Compte Higgsfield | plan **Plus** | https://higgsfield.ai (pour les générations IA) |

Rien d'autre à installer globalement : **ffmpeg** et **Chromium** sont tirés
par `npm install` (paquets `ffmpeg-static` et `playwright`).

---

## 1. Récupérer tous les fichiers

```bash
git clone https://github.com/PhilMARECHAL/noezys.git
cd noezys
git checkout claude/noezys-30sec-video-0m1k07   # la branche de travail
cd video
```

Tout le projet vit dans le dossier `video/`.

---

## 2. Installer les dépendances du pipeline local

```bash
cd video
npm install                       # playwright + ffmpeg-static
npx playwright install chromium   # télécharge le navigateur de rendu
```

> **Spécificité de l'environnement cloud d'origine** : Chromium y était
> pré-installé sous `/opt/pw-browsers/` et les scripts pointent vers
> `.../chromium_headless_shell-1194/chrome-linux/headless_shell`.
> **Sur une machine de dev classique**, remplacez cet `executablePath` par le
> Chromium de Playwright : soit en supprimant la ligne `executablePath` (Playwright
> prend celui de `npx playwright install`), soit en la pointant vers le binaire
> installé. Les fichiers concernés : `render-*.mjs`, `hf/hf.mjs`.

Test rapide du pipeline local (aucun crédit) :

```bash
node render-pub.mjs      # → noezys-pub-<lang>.mp4 (recompose la pub validée)
```

---

## 3. Configurer Higgsfield (pour les générations IA)

```bash
npm install -g @higgsfield/cli
higgsfield auth login          # ouvre un lien OAuth ; se connecter au compte NOEZYS
higgsfield workspace list      # récupérer l'id du workspace "plus"
higgsfield workspace set 05160f30-247f-4180-a828-9b7fc67dd1ad
higgsfield account status      # doit afficher : plus plan, <solde> credits
```

> **Connexion sans navigateur local** (cas d'un serveur distant) : lancer
> `higgsfield auth login --port 8765`, ouvrir le lien affiché sur un poste où
> l'on est connecté à Higgsfield, valider, puis coller l'URL de callback
> `http://localhost:8765/callback?code=...` dans un `curl` vers ce port sur le
> serveur (le récepteur tourne sur la machine qui a lancé `auth login`).

### Règles de travail Higgsfield (impératives)

- **Annoncer le coût en crédits AVANT chaque génération** :
  `higgsfield generate cost <model> [params]` (gratuit, ne lance rien).
- **Valider la voix à l'oreille avant de dépenser sur la vidéo.**
- Ne jamais valider un paiement ni un changement de plan à la place du client.
- Un job en échec est **remboursé automatiquement** (vérifier
  `higgsfield account transactions`).

---

## 4. Les identifiants de référence Higgsfield (à réutiliser)

Ces `media id` servent de référence (`--image-references` / `--audio-references`)
pour rester « on-model » d'une génération à l'autre.

| Élément | media id |
|---|---|
| **Noe** (personnage officiel, robot-mascotte) | `a65e8fe4-fa08-4231-ba3f-878b3607fc74` |
| Décor rotonde N néon (image originale de Philippe) | `ebe66414-d540-454a-bedc-a3cf8850a432` |
| Scène porte-parole (femme dans le décor) | `3f79991c-7f20-4276-af53-1044265e1d09` |
| Voix **Skye** (ElevenLabs, `text2speech_v2`) — `voice_id` | `1fb253b8-928b-4d29-a349-f242a71eaddf` |

Un fichier local peut aussi servir directement de référence (il est uploadé
automatiquement) : `--image-references ./chemin/image.png`.

---

## 5. Reproduire chaque livrable

### 5.1 Vidéo porte-parole « La confession » (16:9 + carré)

Chaîne complète (détails dans `PORTE-PAROLE.md`) :

1. **Décor + porte-parole** (image) — `gpt_image_2`, référence = décor original.
2. **Voix** — `text2speech_v2 --variant elevenlabs --voice_type preset
   --voice_id 1fb253b8-...` (voix Skye), une piste par plan. **Écouter et valider.**
3. **Clips parlants** — `seedance_2_5 --mode omni_reference
   --image-references <scène> --audio-references <voix> --duration 8 --resolution 720p`
   (lip-sync image+audio en une étape ; ~7 min/clip).
4. **Fenêtres interactives + sous-titres + carte de fin** — HTML → PNG :
   `overlay-clip1|2|3.html`, `subs-fr.html`, `endcard.html`, rendus via
   `render-overlay.mjs` / `render-endcard.mjs`.
5. **Assemblage** — ffmpeg (`node_modules/ffmpeg-static/ffmpeg`) : overlay des
   PNG sur les clips, concat des 5 segments, mux audio.
6. **Carré 1080×1080** — `square-bg.html` + `square-subs.html` (rendus
   `render-square-bg.mjs` / `render-square-subs.mjs`) recomposés autour de la
   vidéo 16:9.

Livrables : `noezys-porte-parole-en-stfr.mp4`, `noezys-porte-parole-carre-en.mp4`.

### 5.2 Personnage Noe (super-héros) — projet en cours

Voir `CONCEPT-FUN.md` (concept, storyboard « Noe à la rescousse »).

- Design officiel : `hf-noe/NOE-OFFICIEL.jpg` (= `noe-B.png`).
- Fiche de poses : `hf-noe/noe-robot-sheet.png`. Tenue héros : `hf-noe/noe-hero.png`.
- Régénérer une image de Noe (garder le look) :
  ```bash
  higgsfield generate create gpt_image_2 --aspect_ratio 1:1 --quality high --resolution 2k \
    --image-references a65e8fe4-fa08-4231-ba3f-878b3607fc74 \
    --prompt "<action de Noe> ... keep the character EXACTLY on model ..." --wait
  ```
- Animer un plan de Noe (~26-32 crédits selon durée) :
  ```bash
  higgsfield generate create seedance_2_5 --mode omni_reference \
    --image-references a65e8fe4-fa08-4231-ba3f-878b3607fc74 \
    --duration 5 --resolution 720p --generate_audio false \
    --prompt "<mouvement> ... keep the character EXACTLY on model ..." --wait
  ```

### 5.3 Bande-son (synthèse numpy, 0 crédit)

```bash
python3 make-music.py music-pub.wav "0,2,5,11.2,17.2,23.2,28.2" 11.2 23.2 34.5
python3 make-music-anniv.py music-anniv.wav          # version festival
```

---

## 6. Règle d'encodage (compatibilité décodeurs matériels) — NE PAS DÉVIER

À **chaque** écriture d'un MP4 (rendu ET mux audio) :

```
-c:v libx264 -preset slow -crf 18 -profile:v high -level:v 4.0 \
  -x264-params ref=4:bframes=3 -pix_fmt yuv420p -movflags +faststart
-c:a aac -b:a 192k -ar 48000
```

- `+faststart` obligatoire à chaque réécriture du conteneur.
- **Level 4.0** impératif : le level 5.0 (preset slow → 8 ref frames) casse les
  décodeurs matériels (la vidéo affiche la 1re image puis se fige). Cf.
  `MODE-OPERATOIRE.md` §12.

---

## 7. Carte des fichiers

| Type | Fichiers |
|---|---|
| Docs | `RUNBOOK-DEV.md` (ce fichier), `MODE-OPERATOIRE.md`, `PORTE-PAROLE.md`, `CONCEPT-FUN.md`, `REMARQUES-V2.md`, `kit-linkedin.md`, `README.md` |
| Animations HTML | `pub.html`, `pub-square.html`, `scene.html`, `anniv.html`, `overlay-clip*.html`, `subs-fr.html`, `endcard.html`, `square-*.html`, `player.html`, `affiches.html` |
| Rendu (Node) | `render*.mjs` |
| Audio (Python) | `make-music.py`, `make-music-anniv.py` |
| Higgsfield (pilotage) | `hf/hf.mjs`, `hf/*.mjs` |
| Personnage Noe | `hf-noe/` |
| Livrables MP4 | `noezys-*.mp4` |
| Assets | `fonts/`, `photos/`, `../assets/noezys-n-mark.png` |

---

## 8. Notes importantes

- **Environnement cloud éphémère** : la machine d'origine est recréée à chaque
  session ; **seul ce qui est commité + poussé sur GitHub survit**. Toujours
  committer les livrables.
- **Dossiers ignorés** (`.gitignore`) : `node_modules/`, `frames*/`, `hf-shots/`,
  `hf-profile/`, `music-*.wav`, etc. — ce sont des intermédiaires régénérables.
  Les images/clips Noe et vidéos finales importantes ont été **forcés** dans le
  dépôt (`git add -f`).
- **Générations brutes Higgsfield** : également accessibles sur higgsfield.ai
  → section « Generations » du compte, et via `higgsfield generate list`.
- **Attribution des commits** : voir la convention en tête des commits du dépôt.
