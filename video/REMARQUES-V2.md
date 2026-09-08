# Remarques pour la version suivante — vidéo porte-parole « La confession »

Retours de Philippe, session du 8 septembre 2026 (fin de journée).
À traiter en priorité avant toute nouvelle production.

## 1. Transitions entre les plans — trop brutes

- Les coupes entre les 3 clips (aveu → travail → retournement), la pause et la
  carte de fin sont **trop sèches**. Manque de **synchronisation / continuité**
  entre les plans.
- Pistes à travailler pour la V2 :
  - Ajouter des **fondus enchaînés courts** (crossfade vidéo ~0,3–0,5 s) entre
    les clips plutôt que des coupes franches.
  - **Lisser l'audio** aux jonctions : crossfade audio (afade/acrossfade) pour
    éviter la rupture de voix entre deux clips.
  - Harmoniser le **cadrage / la position de la porte-parole** d'un clip à
    l'autre (elle bouge légèrement entre les générations Seedance → léger saut).
    Envisager de régénérer les clips depuis une **image de départ commune** pour
    une continuité parfaite du visage et de la posture.
  - Vérifier le **raccord de la fenêtre interactive** : son apparition/sortie
    doit être calée sur les transitions vidéo, pas indépendante.

## 2. Prononciation anglaise de « NOEZYS » — à corriger absolument

- Dans la voix actuelle (Skye / ElevenLabs), « NOEZYS » est **mal prononcé**.
- **Prononciation cible** : comme le mot anglais **« noises »**, en **insistant
  sur le "e"** final (son « -zes »). Répéter mentalement : « noises », « noises »,
  « noises ».
- Pistes pour la V2 :
  - Dans le **script TTS**, écrire le mot phonétiquement là où il est prononcé,
    p. ex. **« noises »** ou « NOY-zes », au lieu de « NOEZYS », pour forcer la
    bonne diction (le mot écrit à l'écran reste « NOEZYS »).
  - Générer **plusieurs essais** du seul mot pour valider la diction à l'oreille
    (coût ~0,15 crédit/essai) **avant** de refaire les clips vidéo.
  - Tester aussi le champ **« Voice details »** via l'interface web Higgsfield
    (indication d'accent/diction non exposée par le CLI).

## 3. Ton trop sérieux / formel — amener plus de fun

- La V1 est **trop sérieuse, trop formelle**. Il faut **plus de fun** dans
  l'interaction porte-parole ↔ fenêtre interactive. Sujet à retravailler
  ensemble (« on va revenir sur le sujet »).
- Pistes à explorer pour la V2 (à valider avec Philippe) :
  - **Complicité porte-parole ↔ interface** : elle interagit vraiment avec la
    fenêtre — un clin d'œil, elle « pousse » une bulle du doigt, la coche
    apparaît quand elle claque des doigts, elle réagit avec un petit sourire
    quand le site se génère. L'IA joue avec sa propre démo.
  - **Micro-humour dans le script** : garder le concept « La confession » mais
    y glisser une pointe d'autodérision assumée d'IA (p. ex. « Yes, I'm an AI —
    and even I think you deserve your evenings back. »). Léger, pas comique.
  - **Rythme plus vif** : coupes plus dynamiques, un zoom rapide ou un « punch »
    visuel sur un mot clé, une réaction expressive (sourcil levé, sourire).
  - **Sound design ludique** : petits « pop / whoosh / ding » quand les services
    se cochent ou que le site apparaît (au lieu de la seule nappe grave).
  - **Expressions plus variées** de la porte-parole entre les plans (prompts
    Seedance : « playful », « amused smile », « raises an eyebrow »).
  - Garder l'émotion de la pause finale — le fun est pour le **corps** de la
    vidéo, la **chute reste sincère** (« human connection comes first »).

## Rappels de contexte (à conserver)

- Concept validé : **« La confession »** (porte-parole générée assumée).
- Voix retenue : **Skye** (ElevenLabs, voix E) — jeune, vive, non « mielleuse ».
- Décor : image originale de Philippe (rotonde de verre, N néon), réutilisée
  telle quelle via `--image-references`.
- Pipeline : Higgsfield CLI (auth OAuth, workspace Plus), `seedance_2_5` mode
  `omni_reference` (image + audio → clip synchronisé), assemblage local ffmpeg
  (`node_modules/ffmpeg-static`), fenêtres/sous-titres/carte de fin en HTML→PNG.
- Formats livrés en V1 : 16:9 (`noezys-porte-parole-en-stfr.mp4`) et carré
  1080×1080 (`noezys-porte-parole-carre-en.mp4`).
- Crédits consommés en V1 : ~225. Solde ≈ 975 / 1200.
- Règle : annoncer le coût avant chaque génération ; valider la voix à l'oreille
  avant de dépenser sur la vidéo.
