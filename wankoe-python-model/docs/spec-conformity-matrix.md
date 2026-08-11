# Specification conformity matrix

Traceability of every requirement of the WANKOE specification (cahier des
charges, v. 2026-08-08, 9 chapters + preamble) to its implementation, its
tests, and its status. **This document is the contract's backbone for an
EVOLVING project**: when a requirement changes, find its row, change the
data or code it points to, and the listed tests guard the rest.

Statuses: ✅ conforming · 🧪 conforming with fitted [H] hypothesis ·
📌 client arbitration (dated) · 📏 awaiting a field measurement.

## Preamble

| Requirement | Implementation | Tests | Status |
|---|---|---|---|
| Static deterministic flowsheet; each run = one scenario "photo" | `run_scenario` (pure function, no state) | whole suite | ✅ |
| Engine never optimizes alone, imposes no operating choice | sweeps/planning are explicit user-configured calls; out-of-range settings warn, never block | `test_parameters`, `test_optimize` | ✅ |
| Web interface | `webapp.py` + `web/index.html` (stdlib-only, self-contained) | `test_webapp` (8) | ✅ |
| Auto-calibration on measurements | `fit.py` + `scripts/fit_calibration.py` | `test_fit` (4) | ✅ |
| Golden rule 1: undefined symbol → question, never guessed | questions asked & arbitrated: `comp_lam` role, KFS 30/55/15 envelope, CR.5009 x80=f(gap), M3 semantics | decision log below | ✅ |
| Golden rule 2: vendor curves as value tables + interpolation mode | feed curves are {mesh: %} tables, log-linear interpolation | `test_review_fixes` | ✅ |
| Golden rule 3: data separated from code | `data/default_parameters.json`; 2 dedicated audits (2026-08-08) | `test_parameters` (17) | ✅ |
| Acceptance: automatic mass + water closure, strict tolerance | per-zone dry-solids + water balances every run; inter-zone stockpile closure in the period balance | `test_reference`, `test_review_fixes` | ✅ |
| Acceptance: reproduce reference cases (ch. 9) | see chapter 9 below | `test_reference` (6) | ✅ |
| Acceptance: automated tests shipped with the code | 108 tests, all green | — | ✅ |

## Chapter 1 — conventions

| Requirement | Implementation | Status |
|---|---|---|
| Units (t/h, mm, kW, % mass, t/m³, kWh/t, °C, h) | throughout; result keys suffixed (`_tph`, `_kW`, `_mm`) | ✅ |
| Reference mesh series (29 meshes 0.063–200 mm) | `mesh_series_mm` + engine extension meshes | ✅ |
| Curve = cumulative % passing, log mesh axis | `grid.PSD`; UI chart semi-log | ✅ |
| Moisture wet-basis; conserved quantity = dry solids; water only removed at the dryer | streams carry dry t/h + moisture; vapor at DY.03 only | ✅ |

## Chapter 2 — machine codification

All 13 codes used verbatim (`CR.5003`, `SR.5007`, `CR.5009`, `CR.5011`,
`DV-5099`, `BF.5101`, `SR.5105`, `CR.5107`, `SR.5115`, `DY.03`, `SN.21`,
`ML.26`, `SP.36`, `CL.38`). `ML.30`/`DV.10` absent as required (deleted by
the spec). `DV-5099`/`BF.5101`: routing/transfer, no process influence
(spec §4). `CR.5003`: upstream of the pivot feed point (spec §5) — its
parameters feed the reference-curve calibration script only (documented in
the data). Status: ✅

## Chapter 3 — models M1–M8 (`models.py`)

| Model | Requirement | Status & notes |
|---|---|---|
| M1 | truncated Rosin-Rammler product, fines pass unchanged | ✅ `m1_crusher_product`; trunc factor 1.7 is a parameter |
| M2 | Bond law, P80/F80 in µm, η_m net→installed | ✅ `m2_bond_power` (hand-checked in tests) |
| M3 | Karra partition, d50c = a·k_d, sharpness from I | 📌 **arbitration 2026-08-08 (option A)**: spec formula contradicted its narrative; I is a classic imperfection → `s = ln9/ln(1/(1−I))`; defaults remapped `I_new = 1−I_old` (dry 0.4 ≡ original sharpness 4.30; rain 0.9 degraded). 📏 real screen imperfection to measure (KFS sieve test) |
| M4 | VSMA screen area, f0 fitted on SR.5007 | ✅ `m4_screen_area`; installed areas = data keys (null until provided) |
| M5 | impact t10 → n, x80 = CSS | ✅ `m5_impact_uniformity` (hand-checked) |
| M6 | drying water+heat balance | ✅ `m6_drying`, matches ch. 9.3 exactly; clamps if feed already dry |
| M7 | ML.26 compression + bed attrition | 🧪 `m7_bed_mill_pass`; `comp_lam` role unspecified by the spec → hypothesis H-M7-1 (max reduction per pass); attrition fines → H-M7-2 (RR x80/n params). Refit 2026-08-08 hits ch. 9.3 exactly, all coefficients inside bounds. To confirm by plant trial |
| M8 | air classifier + Lapple cyclone | ✅ `m8_air_classification` (mass-exact per interval, measured-Phi reconciliation); cyclone d50 awaiting inlet width `b_cyclone` 📏 |

## Chapter 4 — flowsheet

Zones 1.1 / 1.2 / 1.3 wired exactly as §4.1–4.3: grizzly-blended pivot →
CR.5009 → SR.5007 with CR.5011 closed loop (modes 1A/1B); reclaim →
SR.5105 (modes 2A/2B/2C, rain forces 2B — disengageable parameter) →
SR.5115/CR.5107 AgLime loop; dryer → SN.21 with ML.26 closed loop → grits;
0-1.5 → SP.36 + CL.38 → UltraFin. Fixed-point loops with convergence
criteria in the data; unknown modes fail fast. Status: ✅ (`flowsheet.py`,
`test_reference`, `test_review_fixes`)

## Chapter 5 — feed product

Pivot curve = REAL belt-cut measurement 2026-08-08 (d50 32 / d80 180 mm,
moisture 7 %), reproduced by the model at 32.3 / 180.6 mm. Two documented
completion hypotheses: H-FEED-1 (fine tail < 19 mm — reference-curve shape
renormalized) 📏 and H-FEED-2 (top size → 100 % at 320 mm). Rock-type
cases (UCS, friability): reserved data slots for the DP9442 geology. A
finding to act on: feed F80 181 mm exceeds CR.5009's 150 mm nip limit
(alert fires as specified). Status: ✅ + 📏

## Chapter 6 — output products

Five products with data-driven cuts, wet/dry states and tolerances. KFS
"30/55/15" envelope: 📌 interpretation validated 2026-08-08 = three
%-passing thresholds (max below cut / min in cut / max above cut), all
parameters. Compliance evaluated on every run, shown in the UI. Status: ✅

## Chapter 7 — production targets

| Requirement | Implementation | Status |
|---|---|---|
| Firm KFS 85 kt & grits 40 kt; AgLime market cap 135 kt; flexible fines; UltraFin capped by natural content | `production_targets` (data, incl. product mapping) | ✅ |
| Time basis = parameter (day/week/month/year) | `time_basis` + `engine.time_basis_fractions` | ✅ |
| Weather = parameter, never imposed | `weather` scenario parameter | ✅ |
| Hours + availability per zone | 📌 **client rule 2026-08-08: hours follow the targets, never the reverse** → `run_required_hours` (regimes = capacity ceilings) | ✅ |
| Expose the mechanical 0/20 surplus | planning stockpile rows: ~58 kt/yr at current settings | ✅ |

## Chapter 8 — arbitration rule

"Meet firm targets, minimize unsellable surplus": encoded as the default
sweep objective (firm shortfall ≫ surplus, phantom-stockpile penalized);
all weights adjustable per study. The engine itself still never chooses.
Status: ✅ (`optimize.py`, `test_optimize`)

## Chapter 9 — reference case

| Quantity | Expected | Achieved | Status |
|---|---|---|---|
| 9.1 KFS | 59.3 t/h (23.7 %) | 59.7 t/h (23.9 %) | ✅ |
| 9.1 0/20 | 190.7 t/h | 190.3 t/h | ✅ |
| 9.1 P CR.5009 | ~116 kW | 107 kW | ✅ (−8 %, curve-calibration bound) |
| 9.1 P CR.5011 | ~37 kW | 18 kW at loop equilibrium / ~45 kW net at the 125 t/h nameplate | 📌 reconciled: the spec figure is a nameplate evaluation; both reported |
| 9.2 AgLime | 55.0 t/h | 55.1 t/h | ✅ |
| 9.3 vapor / burner | ~2.3 t/h / ~3.8 MW | 2.26 / 3.83 | ✅ |
| 9.3 grits / UltraFin | 10.1 / ~1.3 t/h | 10.1 / 1.31 | ✅ exact after M3 remap |
| 9.3 FeedLime fines | 19.9 t/h | 16.2 t/h | ⚠ the spec's own 9.3 table cannot close mass (10.1+19.9+1.3 = 31.3 t/h out of 27.6 t/h dry feed); the model enforces closure — QUESTION PENDING to the client on the 19.9 figure |
| 9.4 annual balance | ~328.7 kt in, 273 kt 0/20, 8.7 kt vapor | not reproduced | ⚠ 9.4 was authored with the hypothetical rock and pre-arbitration settings; the planning module gives the live equivalent (58 kt 0/20 surplus at current settings) — flagged, not silently claimed |

Honest caveats: (1) the feed curve behind ch. 9 was never measured, so the
reference curve is back-fitted to these figures and the ML.26 coefficients
were then fitted on that curve — the validation is doubly circular by
construction and validates the model's MATHEMATICS, not the plant; (2) the
ML.26 fit is under-determined (4 free coefficients for 2 observations):
the fitted values are one plausible solution, to be replaced by vendor
data (the `product_curve_table` slot). Real grounding rests on the
measured belt cuts.

## Project purpose & measurement policy (client framing 2026-08-08)

The line is a **new process under construction**: the model's ultimate goal
is to **confirm the line design and the machine selection**. The only
recurring plant data will be belt-cut PSD analyses at the primary crusher
outlet (format of `data/feed_measurements/2026-08-08-belt-cut.json`); no
downstream measurement will ever exist — downstream behavior rests on the
validated engineering models (M1–M8) and their documented hypotheses.
Implementation: `feed.py` (measurement ingestion, H-FEED-1/2 completion),
`design.py` (computed duties vs installed limits, worst case across all
stored measurements), installed-limit data keys per machine. Tests:
`test_design.py`. Status: ✅ (limits to fill from vendor data 📏)

## Decision log (dated — the project's memory)

The "decided by" column separates what THE CLIENT arbitrated from what was
delegated or expert-proposed; expert proposals await his ratification.

| Date | Decision | Decided by |
|---|---|---|
| 2026-08-08 | CR.5009: x80 = gap (explicit x80 overrides when set) | the client |
| 2026-08-08 | comp_lam unspecified → hypotheses H-M7-1/H-M7-2, parameterized, fitted | delegated (his "je ne sais pas" authorized hypotheses) |
| 2026-08-08 | Reference feed curve calibrated on ch. 9 pending measurement | the client |
| 2026-08-08 | KFS 30/55/15 = three %-passing thresholds | the client (thresholds inferred from an example — values to confirm in use) |
| 2026-08-08 | KFS 15 % out-of-cut tolerance nulled, superseded by the envelope | assistant — QUESTION PENDING |
| 2026-08-08 | Measured belt-cut adopted as default feed (H-FEED-1/2) | the client (H-FEED completions delegated) |
| 2026-08-08 | Operating hours follow production targets, never the reverse | the client |
| 2026-08-08 | M3 option A: narrative wins, s = ln9/ln(1/(1−I)) | the client |
| 2026-08-08 | Imperfection defaults remapped I_new = 1−I_old | expert review — RATIFICATION PENDING |
| 2026-08-08 | Purpose = design confirmation; only feed belt-cut measurements will ever exist | the client |
| 2026-08-08 | Web UI labels in French (operator usability) despite the English-deliverables rule | assistant — QUESTION PENDING |
| 2026-08-08 | SP.36 cut default 100 µm kept although §3.0-M8 suggests ≈0.65·d97 ≈ 65 µm | spec-internal tension — QUESTION PENDING |
| 2026-08-08 | CR.5011 ~37 kW read as a nameplate-capacity evaluation; both powers reported | assistant hypothesis — QUESTION PENDING |
| 2026-08-08 | Spec 9.3 fines 19.9 t/h cannot close mass; model enforces closure | spec-internal inconsistency — QUESTION PENDING |
| 2026-08-09 | Web UI language: ENGLISH everywhere — the French-labels exception is REJECTED; all deliverables English, no exception | the client |
| 2026-08-09 | Web UI carries the NOEZYS visual identity (www.noezys.com deep-navy/cyan/violet); operating modes explained in the UI and the selected mode's route colored on the flowsheet | the client |
| 2026-08-09 | UI primary flow = annual production targets as inputs; operating hours COMPUTED from them and displayed (hours removed as inputs), seasonal balance evaluated at the computed hours | the client (reaffirming the 2026-08-08 hours-follow-targets rule) |
| 2026-08-09 | design.py fixed to tolerate machines absent from the photo (zone stopped by mode, e.g. 2C) — regression test added | assistant (bug fix, UI review) |
| 2026-08-10 | Q1/12 — dry screen imperfection I = 0.15 adopted from literature (was 0.4 spec-derived). KFS envelope 30/55/15 now COMPLIANT; KFS yield drops to 51.4 t/h so zone 1.1 needs 2069 h > 2000 h ceiling (85 kt firm commitment at risk — securing lever = Q7/12). Ch.9 reference tests pin the spec-era I = 0.4 to keep validating the model against ch.9 under ch.9's own calibration | the client |
| 2026-08-11 | Working interface changes: simulations are now run and presented IN CHAT (same engine, identical precision); the web app becomes optional. New protocol: zone 1 recomputed step by step — inputs validated by the client first, then one machine datasheet at a time (feed PSD, product PSD, calculation, settings, power); on the client order "verser au dossier technique" a numbered technical dossier (DT-nnn) is produced by a dedicated agent and tracked in a dossier register referencing hypotheses and zone | the client |
| 2026-08-11 | Step-1 inputs VALIDATED: feed 250 t/h wet (232.5 t/h dry, 7 % moisture) + measured 2026-08-08 belt-cut curve completed by H-FEED-1/2 (F80 180.6 mm) | the client |
| 2026-08-11 | Rock hardness (UCS 20-80 MPa per client; spec ch.9 reference rock says ~325 MPa — inconsistency noted): UCS confirmed as a case discriminator only (spec §5.2), never a formula input; hardness enters via Wi (M2) and A_j·b_j (M5). Client commissioned an expert technological/scientific note on hardness-dependent machine calculations; Q2 (Wi 12.54 vs 13.8) and Q12 (b_j soft limestone) are ON HOLD pending that note — current values 12.54 and 60×0.8 stay in force meanwhile | the client (expert note pending) |
| 2026-08-11 | TRACEABILITY RULE: every machine datasheet and every technical dossier DT-nnn carries an engine-run provenance footer (commit hash, functions called, run date); any figure NOT produced by an engine execution (e.g. a linear sensitivity scaling) must be explicitly flagged as assistant-computed; dossier extraction scripts are archived in the repo so any engineer can replay the numbers without the assistant | the client |
| 2026-08-11 | Expert book received and archived (docs/WANKOE-ouvrage-modeles-machines-v2026-08-08.pdf, 23 pp, 22 refs): first-principles derivations of M1-M8 with provenance statuses [ref.]/[H]/[F]. It CONFIRMS the implemented architecture (RR truncation 1.7·x80 + sub-x80 bypass, Karra s = ln9/ln(1/I), VSMA f0 = 0.347, Ecs = v²/7200, DY.03 energy balance incl. solid sensible heat, ML.26 λ = 4.11, CR.5107 v = 40 / CSS 1.0) | the client (via expert book) |
| 2026-08-11 | Q2/12 CLOSED — Wi stays 12.54 kWh/t, now [ref.] (Fontaine, Belgian limestone; consistent with Todorovic 12.6-13.9). The kWh/short-ton 13.8 hypothesis is REJECTED; spec ch.9 ~116 kW remains a spec-side artefact. Site Bond test remains a calibration trigger | the client (expert book ch.13) |
| 2026-08-11 | Q8/12 CLOSED — CR.5011 = HAZEMAG AP-S 1010 machine documents (Ochse 2026-07-17): 100 t/h nominal, 75-90 t/h real on limestone (max_capacity_tph 125 -> 90), max feed 400 mm, motor 132 kW (installed_power_kW null -> 132); capacity is rotor-bound. NEW operational constraint: mode 1B line feed ~130 t/h max (not engine-enforced; noted in machine sheet) | the client (expert book ch.4) |
| 2026-08-11 | Q6/12 CLOSED — SP.36 cut 100 -> 65 um (d50c = 0.65·d97, Stokes equilibrium, expert book ch.11). Default-scenario impact: UltraFin 1.50 -> 0.99 t/h (5.3 kt/y at computed hours, target 4 kt), Q_air 2998 -> 1980 m3/h, Phi_cut 9.75 -> 6.44 % (still NOT CERTIFIED until measured). Ch.9 reference tests pin the spec-era 100 um | the client (expert book ch.11) |
| 2026-08-11 | CL.38 geometry adopted as design assumption: b_cyclone null -> 0.14 m (D = 0.7 m, b = 0.2D Stairmand, Ne = 5, v_in = 15) -> d50 = 4.23 um now computed. Sub-4 um tail needs a polishing BAG FILTER — equipment absent from the flowsheet, to raise at design review. Vendor drawing still to confirm | expert book ch.12 — vendor confirmation pending |
| 2026-08-11 | Expert book issues logged for a clarification note (NOT yet sent): (1) imperfection convention mixed — ch.2 formula/values in spec convention (I_doc = 1 − I_ours; dry 0.60 ⇔ ours 0.40) but ch.7 rain statement in ours; ch.13 'calé' 0.9006 ⇔ ours 0.0994 vs the Q1-arbitrated 0.15 — grits yield 33.5 % (book) vs 26.5 % (model) hangs on this; (2) book's CR.5009 worked example uses F80 120 mm vs measured 180.6 (66 vs 106 kW net); (3) ML.26 S_att: book 0.206 (Houben) vs shipped 0.171 (Thiere refit), both within 0.14-0.32; (4) CR.5011 capacity: spec 125 superseded by machine-doc 75-90 | assistant analysis — client to route to experts |

## How this project absorbs future changes

- **A number changes** (setting, tolerance, target, hours): edit
  `data/default_parameters.json` — no code, tests guard the physics.
- **A new measurement arrives** (feed curve, Phi, screen imperfection):
  paste it into the data (or `feed_measurement_*.json` + rebuild script);
  the [H] coefficients refit with `scripts/fit_calibration.py`.
- **A formula or the flowsheet changes**: one model = one pure function in
  `models.py` / one zone function in `flowsheet.py`; the reference tests
  and 85-test suite catch regressions; this matrix gets a new decision row.
- **A new product or machine**: open collections in the data; machine
  sheets follow one schema; the result shape is stable for the web UI.
- **Any doubt**: the expert-panel review (process, numerics, API, data,
  tests, performance + adversarial verification) is repeatable on demand.
