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

## Engineering state (see docs/ for detail)

- docs/spec-conformity-matrix.md: requirement-by-requirement traceability
  + dated decision log. docs/model-science-review.md: formula provenance,
  grades A/B/C (ML.26 = the C, spec under-defined it).
- 12-question client arbitration round IN PROGRESS (2026-08-10). Decided:
  Q1 dry imperfection I = 0.15 (literature) — KFS envelope holds, but
  zone 1.1 needs 2069 h > 2000 h ceiling: the 85 kt firm KFS commitment
  is AT RISK at defaults until the securing lever (Q7) is chosen.
  Still open: Wi metric 13.8 vs 12.54 (Q2), I-remap ratification (Q3),
  KFS tolerance vs envelope (Q4), spec 9.3 fines figure (Q5), SP.36 cut
  65 vs 100 um (Q6), KFS securing lever (Q7), CR.5011 datasheet (Q8),
  repo location (Q10), b_j soft limestone (Q12). Q9 hosting: DONE
  (Render). Q11 French UI: rejected — English everywhere.
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
- TRACEABILITY RULE (client, 2026-08-11): every datasheet/dossier carries
  an engine-run footer (commit, functions, date); assistant-computed
  figures (not from an engine execution) must be flagged as such; dossier
  extraction scripts are archived in the repo for replay without the
  assistant. Rationale: the client must be able to VERIFY, not trust.
- INCOMING (announced 2026-08-11): a substantial expert
  technological/scientific document with mathematical models for
  hardness-dependent machine calculations. On receipt: full read,
  machine-by-machine gap table vs current M1-M8, quantified impact on
  issued datasheets, data-first integration, dated decision-log rows,
  re-issue affected datasheets for client validation.
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
