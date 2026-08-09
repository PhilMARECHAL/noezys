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
- Known open arbitrations (morning questionnaire pending): imperfection
  remap ratification, KFS 15% tolerance vs envelope, SP.36 cut 65 vs 100
  um, spec 9.3 fines figure inconsistency, CR.5011 37 kW meaning,
  hosting/deployment, repo location, French UI exception.
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
