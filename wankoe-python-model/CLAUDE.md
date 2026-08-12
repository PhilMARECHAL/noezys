# Wankoe project memory (for any future engineer or assistant session)

The durable working rules of this project, so nothing load-bearing lives
only in a past conversation. Keep this file updated with every new client
rule or arbitration.

## The client and the mission

- Client: NOEZYS (never name any individual in produced results — brand rule 2026-08-08: this software is created by NOEZYS). Conversation language: FRENCH. All
  deliverables (code, data, docs, WEB UI): ENGLISH — the French-UI
  exception was rejected by the client on 2026-08-09; no exception.
- Web UI (client rules 2026-08-09): NOEZYS visual identity from
  www.noezys.com (deep navy #070a22/#0a0f2e/#101a4a, cyan #22d3ee,
  violet #a855f7, indigo #6366f1, Inter); operating modes 1A/1B/2A/2B/2C
  explained in the UI and the selected mode's route COLORED on the
  flowsheet; annual production targets are the toolbar inputs and the
  operating hours are computed from them (hours are never inputs).
- Deployed on Render (2026-08-09): https://wankoe-model.onrender.com —
  blueprint render.yaml on this branch, HTTP Basic Auth via
  WANKOE_ACCESS_KEY (value set by the client in the Render dashboard),
  auto-deploys on every push to wankoe-python-model.
- THE RESULT IS THE MATHEMATICAL MODEL, never a document. Documents are
  printouts of model output. This confusion happened once; never again.
- The line is a NEW process under construction. Ultimate purpose: CONFIRM
  the line design and the machine selection.
- The ONLY plant data that will ever exist: belt-cut PSD analyses at the
  primary crusher outlet (format: data/feed_measurements/*.json). Never
  request downstream measurements.
- The project is EVOLVING, never frozen. Every change lands through
  data/default_parameters.json first, code second; each arbitration gets a
  dated row in docs/spec-conformity-matrix.md (decision log) stating WHO
  decided (the client / delegated hypothesis / expert proposal pending
  ratification).

## Client vocabulary (2026-08-11, load-bearing)

When the client says "zone 1" he means the CRUSHING/SCREENING BLOCK ONLY
— model sub-zone 1.1 (pivot -> CR.5009 -> SR.5007 -> CR.5011 loop; KFS +
0/20). Zones 1.2 and 1.3 are separate scopes he names explicitly. A past
misunderstanding came from reading "zone 1" as the whole line; never
assume the wider scope again — when in doubt, ask.

## The client's standing rules (verbatim intent)

1. Nothing hardcoded — every parameter adjustable without reprogramming.
2. Operating hours are SET BY the production targets, never the reverse
   (planning.py). Shift regimes are capacity ceilings.
3. Golden rules of the spec: undefined symbol -> question, never guessed;
   vendor curves as value tables WITH declared interpolation mode; data
   separated from code.
4. Maximum rigor and honesty ("ne me faites pas plaisir"). He asks for
   expert panels and adversarial verification for significant steps.
5. He answers best to ONE question at a time with 2-4 proposed answers.
6. He is not a developer: phone-first, web UI, never ran code. A GitHub
   repo alone does not reach him.

## PFD authority (2026-08-12, load-bearing)

Three NACO/Carmeuse PFDs in docs/pfd/ PREVAIL over the spec wherever
they diverge — EXCEPT zone 1.3, where the PFD's DV.10 + ML.30 Unirotor
were deleted from the design (client ruling): the model's zone-1.3
topology stands. Zone 1.2 REBUILT to PFD REV18 (DONE 2026-08-12):
FeedLime = 6/20 at single-deck 6 mm SR.5105; AgLime loop = open SR.5111
+ CR.5113 (ex-CR.5107) + closed-loop SR.5115; 60 t/h loop rating alert;
planning = strict c2 (min of AgLime-cap / FeedLime-demand hours).
PRIORITY RULE (client 2026-08-12): FIRM products KFS + grits are the
absolute priority; AgLime is a CAMPAIGN product (separate campaigns,
mode A or C, whenever convenient); everything else secondary. FeedLime
runs mode B weekly at demand rate; storage/shortfall questions CLOSED.
KEY FINDINGS: AgLime co-product ~112.8 kt/y in mode A (campaigns top up
the 135 kt market at leisure); FeedLime/AgLime split 59/41 INVERTED vs PFD design
42/58 (design curve finer than measured — expert question, same family
as KFS 80-vs-51); recirculation now ~0 (two-stage closing); zone 1.3 at
91.6 % hours on coarser FeedLime. Ch.9 zone-1.2/1.3 figures superseded,
tests re-baselined with dated comments. Zone 1.1 retags (CR.5006/
SR.5008/DV.5009) + scenario-B 150 t/h still TO DO. Conformity-matrix
chapters 2/4/9 partially outdated (decision log rows are authoritative).
Zone-1.2 calc document still WITHDRAWN — re-issue next.
Gap table: docs/pfd/gap-register.md.

## Engineering state (see docs/ for detail)

- docs/spec-conformity-matrix.md: requirement-by-requirement traceability
  + dated decision log. docs/model-science-review.md: formula provenance,
  grades A/B/C (ML.26 = the C, spec under-defined it).
- 12-question client arbitration round IN PROGRESS (2026-08-10). Decided:
  Q1 dry imperfection I = 0.15 (literature) — KFS envelope holds, but
  zone 1.1 needs 2069 h > 2000 h ceiling: the 85 kt firm KFS commitment
  was AT RISK until Q7 was CLOSED 2026-08-13: Saturday extension,
  zone 1.1 = 1 shift x 6d/7, ceiling 2400 h -> 86.2 % utilization,
  targets_reachable TRUE. Remaining watch: zone 1.3 at 91.6 %.
  CLOSED 2026-08-11 via the expert book: Q2 (Wi stays 12.54 [ref.],
  13.8 rejected), Q6 (SP.36 cut = 65 um; UltraFin 0.99 t/h at defaults),
  Q8 (AP-S 1010 machine docs: 75-90 t/h real, 132 kW, mode-1B line feed
  ~130 t/h). Q9 hosting: DONE (Render). Q11 French UI: rejected.
  Still open: I-remap ratification (Q3 — now tied to the expert
  clarification note), KFS tolerance vs envelope (Q4), spec 9.3 fines
  figure (Q5), repo location (Q10), b_j soft
  limestone (Q12 — book documents calcite A 62-69 / b 1.3-3.0 but keeps
  A=60/b=0.80 [H] pending drop-weight tests).
- NEW WORKING MODE (client, 2026-08-11): the client found the web app too
  complicated — simulations now run IN CHAT (same engine, identical
  numbers), app optional. Protocol: step-by-step zone 1 review — inputs
  validated first (DONE 2026-08-11: 250 t/h wet + measured belt-cut
  curve), then one machine datasheet at a time in chat (feed PSD, product
  PSD, calculation, settings, power; CR.5009 sheet presented, awaiting
  validation). On "verser au dossier technique": a dedicated agent
  produces numbered technical dossier DT-nnn + maintains a dossier
  register (references hypotheses, zone, validated inputs). Chat replies
  French, ALL presented results/tables/dossiers English.
- TECHNICAL DOSSIERS (client protocol, 2026-08-11): dossiers/ holds
  numbered client-facing dossiers (DT-nnn) + REGISTER.md; each dossier
  folder archives its extraction script + raw JSON + canonical .md +
  branded .docx (noezys-report skill, English, no individual named).
  DT-001 = zone 1 complete (11 datasheets) at the validated inputs.
  New dossiers ONLY on the client's explicit "verser au dossier
  technique" order.
- TRACEABILITY RULE (client, 2026-08-11): every datasheet/dossier carries
  an engine-run footer (commit, functions, date); assistant-computed
  figures (not from an engine execution) must be flagged as such; dossier
  extraction scripts are archived in the repo for replay without the
  assistant. Rationale: the client must be able to VERIFY, not trust.
- EXPERT BOOK (received & integrated 2026-08-11):
  docs/WANKOE-ouvrage-modeles-machines-v2026-08-08.pdf — first-principles
  derivations of every machine model, provenance table ([ref.]/[H]/[F]),
  Fontaine→Metso→literature hierarchy. It VALIDATES the implemented
  M1-M8 and closed Q2/Q6/Q8 (see decision log). Four issues await an
  expert clarification note (imperfection convention mix & value 0.10 vs
  0.15 — drives grits yield 33.5 vs 26.5 %; book's CR.5009 example F80
  120 vs measured 180.6; S_att 0.206 vs 0.171; CR.5011 capacity). A
  polishing bag filter for the sub-4 um cyclone tail is MISSING from the
  flowsheet (design review item). Remaining calibration triggers: site
  Bond test, A/b drop-weight, λ piston press, belt sample (S_att + fine
  tail).
- Rock hardness: client rock is UCS 20-80 MPa (vs spec ch.9 reference
  ~325 MPa — inconsistency). UCS = case discriminator only, never a
  formula input; hardness lives in Wi (M2) and A_j·b_j (M5). An expert
  technological note on hardness-dependent machine calculations was
  commissioned by the client (2026-08-11); Q2 and Q12 ON HOLD until it
  arrives — when submitted, confront it with models M1-M8 and land any
  change data-first.
- Validation is circular by construction (chapter 9 was estimated, the
  reference curve back-fitted): the model validates against the spec's
  mathematics; real grounding comes only from feed measurements.
- Run everything: python -m pytest tests/ -q ; stress:
  python scripts/stress_test.py ; UI: python -m wankoe_model.webapp

## Repository caution

The model lives on branch wankoe-python-model of the PhilMARECHAL/noezys
repository, whose root render.yaml publishes the tree statically: NEVER
merge this branch into the deployed branch — the client spec and data
would become world-readable. Repo relocation is an open question for the client.
