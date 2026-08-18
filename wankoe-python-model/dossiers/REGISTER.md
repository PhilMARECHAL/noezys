# Technical Dossier Register — WANKOE limestone processing line

Every technical dossier (DT-nnn) issued for this project is recorded here.
A dossier is a frozen, numbered, client-facing snapshot of validated model
output. The register row states what it covers, at which inputs, under
which parameter state (git commit), and its lifecycle status.

Rules (client, 2026-08-11):
- Dossiers are created only on the client's explicit order ("verser au
  dossier technique") and are numbered sequentially.
- Each dossier references: the zone(s) concerned, the validated input
  data, every calculation hypothesis with its status, and the engine-run
  provenance (commit, functions, date).
- Each dossier folder archives its own extraction script; re-running it
  at the recorded commit must reproduce every figure to the decimal.
- All dossier content is in ENGLISH (project language rule).

| Dossier | Date | Title | Zone(s) | Operating point | Engine commit | Status |
|---|---|---|---|---|---|---|
| DT-001 | 2026-08-11 | Zone 1 complete machine datasheets at validated inputs | 1.1 + 1.2 + 1.3 | 250 t/h wet feed (measured 2026-08-08 belt-cut curve, 7 % moisture), dry weather, modes 1A/2A, reclaim 100 t/h, FeedLime 30 t/h, KFS target 85 000 t/y | `679330f` | ISSUED |
| DT-002 | 2026-08-17 | Zone 1.1 complete sizing note, model-exchange edition (engine vs Metso Bruno): full-chain PSD tables (% passing) modes 1A+1B, replay kit, M1-M5 derivations, annual capacity, PFD REV15 adequacy confrontation; PFD inserted + archived PDF | 1.1 | Modes 1A (250 t/h wet) + 1B (172.0 t/h wet, CSS 18), measured belt-cut curve, dry, reference settings g60/CSS30/v30; REV15 tags (CR.5006/SR.5008 post-retag) | `27a64f0` (REV A) / see REV B commit | REV B 2026-08-18 — FINAL for the Bruno exchange: regenerated at the Q12-ratified calibration (A_j 65 / b_j 1.5); REV A recycle-confrontation misprint (324 vs real 74 t/h) corrected (extraction-script stream-selector fix); EXCHANGE FORMAT = the simple self-contained HTML edition DT-002-Zone11-Sizing-Note.html (client order 2026-08-18: the Word edition judged unreadable; render_dt002_html.py, calc-notes house style, zero hand-typed figures) |
