# Porte-parole NOEZYS — Kit de production Higgsfield

Vidéo « porte-parole en incrustation » : la publicité validée (noezys-pub-en, 34,5 s)
reste la vidéo principale ; une porte-parole générée commente dans un médaillon,
en anglais, sous-titrée en français. Script v2 validé par Philippe le 8 septembre 2026
(basé exclusivement sur les flyers anglais).

## Décisions verrouillées

| Point | Choix |
|---|---|
| Architecture | Médaillon incrusté sur la vidéo pub validée (34,5 s) |
| Persona | Femme, 30-35 ans, professionnelle premium, univers charte NOEZYS |
| Langue | Anglais parlé, sous-titres français incrustés (pipeline local) |
| Voix | Anglais fluide, léger accent français élégant |
| Présence | 3 interventions ; le médaillon disparaît entre deux |
| Transparence | Libellé discret « AI Spokesperson » sous le médaillon à sa 1re apparition |

## Script validé (v2, flyers)

### Intervention 1 — 2,0 → 9,0 s (accroche + bulles)
EN : "We put AI to work for your business: saving you time and growing your
revenue. Stop wasting hours on repetitive tasks."
Sous-titres FR :
1. « Nous mettons l'IA au travail pour votre entreprise : gain de temps, revenus en hausse. »
2. « Arrêtez de perdre des heures sur des tâches répétitives. »

### Intervention 2 — 13,0 → 20,0 s (chatbot + génération du site)
EN : "Website, software, mobile app, AI: we design custom solutions with you,
and build AI in where it truly creates value."
Sous-titres FR :
1. « Site web, logiciel, application mobile, IA : des solutions sur mesure, conçues avec vous. »
2. « L'IA intégrée là où elle crée vraiment de la valeur. »

### Intervention 3 — 27,0 → 34,5 s (carte de fin)
EN : "Not just an AI: a real team that listens and supports you. Thirty minutes,
a concrete action plan, no commitment. Human connection comes first."
Sous-titres FR :
1. « Pas seulement une IA : une vraie équipe qui vous écoute et vous accompagne. »
2. « 30 minutes, un plan d'action concret, sans engagement. Le contact humain avant tout. »

## Étape 1 — Portrait de la porte-parole (GPT Image 2)

`/ai/image`, modèle GPT Image 2. Annoncer le coût affiché avant de cliquer Generate.
Prompt (copier tel quel) :

> Professional corporate portrait photograph of a French businesswoman in her
> early thirties, warm confident smile, looking straight into the camera,
> shoulders-up framing, elegant dark navy blazer over a simple top, subtle cyan
> and violet rim lighting, deep navy studio background with a soft glow, premium
> tech-brand aesthetic, photorealistic, sharp focus on the eyes, soft cinematic
> lighting, plain uncluttered background suitable for a small video overlay.

Générer, faire choisir le visage par Philippe, puis **toujours réutiliser cette
image en Reference** pour toute variation — c'est elle qui garantit le même
visage sur les trois clips.

## Étape 2 — Trois clips vidéo (Kling 2.6, Enhance OFF)

`/ai/video`, Create Video, Kling 2.6, durée **10 s** par clip (l'audio fait 7 à
7,5 s ; la vidéo source doit être plus longue, sinon Seedance tronque).
Charger le portrait validé. Même prompt pour les trois clips :

> The woman speaks calmly and confidently straight to the camera, natural subtle
> head movements, professional presenter energy, steady eye contact, relaxed
> shoulders, the background stays perfectly static, no camera movement, no zoom.

Ne pas se soucier de la voix produite par Kling : elle sera remplacée.
Annoncer le coût affiché avant chaque Generate.

## Étape 3 — Trois pistes audio (Seed Audio 1.0, ~1 crédit chacune)

`/audio`, Text to Speech, Seed Audio 1.0. Une génération par intervention.

Champ Script (une piste à la fois) :
- Piste 1 : `[S1] We put AI to work for your business: saving you time and growing your revenue. Stop wasting hours on repetitive tasks.`
- Piste 2 : `[S1] Website, software, mobile app, AI: we design custom solutions with you, and build AI in where it truly creates value.`
- Piste 3 : `[S1] Not just an AI: a real team that listens and supports you. Thirty minutes, a concrete action plan, no commitment. Human connection comes first.`

Champ Voice details (identique pour les trois pistes, c'est lui qui fixe l'accent) :

> A French businesswoman in her early thirties, native French speaker delivering
> fluent professional English with a light, elegant French accent, warm and
> confident, smiling delivery, medium-low pitch, clear articulation, calm
> premium-brand presenter energy. Not an American accent, not a British accent:
> educated French speaker's English.

**Validation obligatoire par Philippe des trois pistes avant l'étape 4**
(Claude ne peut pas entendre). À ~1 crédit la piste, itérer ici coûte presque
rien ; itérer à l'étape 4 coûte 46 crédits.

## Étape 4 — Synchronisation labiale (Seedance 2.5 Edit, 46 crédits × 3)

`/ai/video/edit`, Edit Video, Seedance 2.5 Edit. Pour chaque paire clip/piste :
- Add a video to edit → Video Generations → le clip Kling correspondant.
- Add elements or references → icône note de musique → Audio Generations → la piste.
- Prompt :

> Replace the entire soundtrack with the attached audio reference. Keep the
> image exactly as it is, do not change the framing or the background, only
> re-animate the woman's mouth and jaw so her lips match the attached audio.

Coût : 46 crédits et 5-7 minutes par passage. Trois passages = 138 crédits.
Annoncer avant chaque clic.

## Étape 5 — Assemblage local (pipeline NOEZYS, 0 crédit)

Philippe télécharge les trois clips synchronisés et les dépose dans la session
(ou le dépôt). Ensuite, en local :
1. Recadrage du médaillon (cercle ou arrondi, liseré dégradé cyan→violet charte).
2. Incrustation sur noezys-pub-en.mp4 aux fenêtres 2,0-9,0 / 13,0-20,0 / 27,0-34,5 s,
   apparition/disparition en fondu 300 ms, position bas-droite (hors zones de texte).
3. Libellé « AI Spokesperson » sous le médaillon (1re apparition).
4. Sous-titres français incrustés, police Outfit, blanc #F0F3FA sur bandeau
   translucide navy, timing calé sur la voix.
5. Mixage : voix au premier plan, musique existante baissée (~-8 dB, sidechain doux)
   pendant les interventions.
6. Encodage compatibilité : H.264 High@4.0, ref=4:bframes=3, yuv420p,
   faststart à chaque réécriture du conteneur (cf. MODE-OPERATOIRE.md §12).

## Budget estimé

| Poste | Crédits |
|---|---|
| Portrait GPT Image 2 (1-2 essais) | selon UI (faible) |
| 3 clips Kling 2.6 10 s | selon UI |
| 3 pistes Seed Audio (+ itérations) | ~3-6 |
| 3 lipsyncs Seedance 2.5 Edit | 138 |
| Assemblage local | 0 |

Total attendu : ~150-170 crédits sur les 1 200 mensuels du plan Plus.

## Rappels de conduite

- Annoncer le coût en crédits avant CHAQUE clic sur Generate.
- Ne jamais valider un paiement ni un changement de plan.
- Fenêtres promo : « Skip Special Offer » en haut à droite ; les comptes à
  rebours sont permanents et factices.
- Piloter le navigateur par actions groupées (browser_batch) ; après une
  expiration à 180 s, reprendre par une capture d'écran avant de recliquer.
