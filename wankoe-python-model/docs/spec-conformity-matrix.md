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
| 2026-08-11 | DT-001 ISSUED — first technical dossier (dossiers/DT-001/): zone 1 complete, 11 machine datasheets at the client-validated inputs (250 t/h, measured curve, dry, 1A/2A), with hypotheses table, vendor-gap list, open-question list, engine provenance commit 679330f and replayable extraction script. Dossier register created (dossiers/REGISTER.md). All 11 datasheets client-validated in chat before issuance | the client |
| 2026-08-11 | Expert book issues logged for a clarification note (NOT yet sent): (1) imperfection convention mixed — ch.2 formula/values in spec convention (I_doc = 1 − I_ours; dry 0.60 ⇔ ours 0.40) but ch.7 rain statement in ours; ch.13 'calé' 0.9006 ⇔ ours 0.0994 vs the Q1-arbitrated 0.15 — grits yield 33.5 % (book) vs 26.5 % (model) hangs on this; (2) book's CR.5009 worked example uses F80 120 mm vs measured 180.6 (66 vs 106 kW net); (3) ML.26 S_att: book 0.206 (Houben) vs shipped 0.171 (Thiere refit), both within 0.14-0.32; (4) CR.5011 capacity: spec 125 superseded by machine-doc 75-90 | assistant analysis — client to route to experts |

| 2026-08-12 | Zone-1 calculation-sheet document issued (docs/calc-notes/zone1/, thesis-grade PDF, 3 machines + zone balance + weekly translation) for external design review. Weekly frame fixed: KFS 85 000/52 = 1 634.6 t/week (kiln continuous), 5 × 8-h shifts Mon–Fri, +8.7 t margin, annual overrun 2 069 vs 2 000 h restated | the client |
| 2026-08-12 | Zone-1.2 document question round (8 questions, expert-prepared): Q1 reclaim 100 t/h wet · Q2 mode 2A fully computed, 2B as mass identity, 2C qualitative · Q3 reclaim PSD = zone-1 photo 0/20 curve at validated settings · Q4 dry photo computed, rain = forced 2B (physical rule), seasons 75/25, rain screen sizing shown · Q5 hours driven by zone-1.3 FeedLime demand with AgLime produced up to its 135 kt cap, zero surplus (c2: 2 971 eff h/y — the client explicitly considered and rejected surplus variant c1 and AgLime-abandon variant c3) · Q6 reclaim moisture = belt 7 % (declared hypothesis) · Q7 weekly ceiling presented as 21 × 8 h = 168 h with maintenance reserve 23.8 h/wk broken out (net 144.2 h/wk) · Q8 AgLime acceptance criterion ADOPTED: >= 95 % passing 1.7 mm (max_out_of_cut_tol_pct = 5; was null — first numeric AgLime spec) | the client |

| 2026-08-12 | Three NACO/Carmeuse PFDs received and archived (docs/pfd/): zone 1.1 REV15, zone 1.2 REV18, zone 1.3 DBR. AUTHORITY RULING (the client): PFDs prevail over the spec v2026-08-08 wherever they diverge, EXCEPT zone 1.3 where DV.10 + ML.30 "Unirotor" have been DELETED — the model's zone-1.3 topology is confirmed current. Zone 1.1: topology confirmed, tags differ (CR.5006/SR.5008/DV.5009), design rates diverge (KFS 80 tph design vs 51.35 computed — new central question), scenario B at 150 t/h. Zone 1.2: topology DIFFERENT (FeedLime = 6/20 via single-deck 6 mm SR.5105; AgLime loop = open SR.5111 + CR.5113 + closed SR.5115, rated 60 t/h; stocks: Feed 6 000 t, AG 28 000 t) — model REBUILD required; the 2026-08-12 zone-1.2 calc document is WITHDRAWN pending re-issue; full gap table in docs/pfd/gap-register.md | the client |
| 2026-08-12 | ZONE 1.2 REBUILT to PFD REV18 (client go): SR.5105 single-deck 6 mm (FeedLime = 6/20), open SR.5111 + CR.5113 + closed-loop SR.5115 (crusher renamed from CR.5107), loop rating 60 t/h wired as an alert, PFD stockpile capacities recorded as data. Planning generalized to the strict c2 rule: dry-2A hours = min(AgLime-cap hours, FeedLime-demand hours), rain-2B completes any shortfall. Ch.9 figures authored on the spec topology are SUPERSEDED and re-baselined (AgLime 55 -> 42.2 t/h, grits 10.1 -> 9.34, ML.26 45 -> 61.2 kW; dated comments in tests). Web UI updated. 110 tests + 556-run stress green | the client (PFD authority) + engine |
| 2026-08-12 | REBUILD FINDINGS (measured curve, 100 t/h reclaim, 2A): FeedLime 59.4 / AgLime 40.6 t/h wet — INVERTED vs the PFD design table (42/58): the design curve assumes ~58 % of the 0/20 finer than 6 mm, the measured zone-1 product gives ~41 % (same family as the KFS 80-vs-51 gap; expert question). Two-stage closing nearly eliminates recirculation (0.3 t/h vs 82 % before). PLANNING: FeedLime demand now binds — AgLime lands at ~112.8 kt/y, BELOW its 135 kt market cap (commercial finding, client to arbitrate); zone 1.2 at 3 471 h (46 %), rain complement 0 h, FeedLime stock balanced; zone 1.3 rises to 6 870 h (91.6 %) on the coarser 6/20 FeedLime; fines surplus worsens to ~51.9 kt | engine (client arbitration pending on the AgLime shortfall) |
| 2026-08-12 | PRIORITY RULE (client): the FIRM contracts — KFS 20/35 and FeedLime grits — are the absolute priority; AgLime is a CAMPAIGN product (produced in separate campaigns whenever convenient, mode A or C); everything else secondary. This CLOSES the S1/S2 storage arbitration and the AgLime-shortfall question: FeedLime runs mode B weekly at the demand rate (39.6 clock h/week year-round, rain included — the 6 000 t stock is a weekly buffer, ample), AgLime campaigns fill the 135 kt market at leisure (e.g. mode C at the 60 t/h loop rating = 2 250 eff h). Remaining binding constraints: zone-1 KFS hours (103.5 %, Q7) and the tightened grits margin (zone 1.3 at 91.6 %) | the client |
| 2026-08-13 | Q7/12 CLOSED — KFS securing lever = SATURDAY EXTENSION: zone 1.1 goes to 1 shift x 6 d/7 (ceiling 2000 -> 2400 h/y; feed stays 250 t/h). Verified across all three zones in one run: zone 1.1 at 2 069 h = 86.2 % (feasible, 331 h annual slack, Saturday ~1 shift/week of buffer), zones 1.2/1.3 unchanged (46.3 % / 91.6 %), design verdict targets_reachable TRUE for the first time, KFS envelope compliant, balances closed. The 260 t/h feed-rate alternative was computed (99.5 %, thin margin + conveyor rating question) and set aside by the client. Tests re-baselined (feasibility flip documented) | the client |
| 2026-08-13 | FeedLime fines 0/1.5 market DEFINED by the client: max 60 000 t/y sellable (production_targets updated: nature 'market cap', was 'flexible 56 000'). At the decided operating point the line produces 107 865 t/y of fines -> unsellable surplus 47 865 t/y — the line's structural co-product issue (grew with the PFD 6 mm FeedLime cut, which sends more sub-6 material through zone 1.3's fines stream) | the client |
| 2026-08-13 | Grits 80 kt/y recorded as an EXTENSION CASE (client option 2; the 40 kt firm target stands). Engine-verified prerequisites at current yields: zone-1.3 chain ~55 t/h (dryer doubled; ~43 t/h if I=0.10 confirmed), zone 1 needs >2 925 h AND more 0/20 (555 kt/y vs 329 produced), fines co-product would reach ~216 kt/y. Not feasible on the current line; to reopen with NACO if the extension firms up | the client |
| 2026-08-13 | ZERO-WASTE PRODUCT RULE (client): objectives = KFS 85 kt + grits 40 kt (firm) + fines sold up to their 60 kt market; the FINES SURPLUS IS REDIRECTED INTO THE AGLIME SALES CHANNEL (fines 0/1.5 sit inside the AgLime >=95% <1.7 mm spec); the AgLime loop only produces the complement up to the 135 kt cap; NO AgLime production objective or campaign. Implemented in planning.py (loop target = cap − fines redirect; mode-B complement; new sales_t view). Result at defaults: fines 60 000 sold + 47 865 redirected, AgLime loop 87 135, total AgLime sold exactly 135 000 — ZERO unsellable product; zone 1.2 drops to 3 150 h (42 %); side effect: 0/20 stock growth rises to ~76.8 kt/y (intermediate reserve, not waste — yard sizing to watch) | the client |
| 2026-08-13 | DY.03 capacity DEFINED by the client: 30 t/h AT THE DRYER OUTLET (its hard limit) = 32.1 t/h wet feed at 7 % -> 0.5 %. Encoded (max_capacity_tph 32.1, max_outlet_tph 30); default zone-1.3 feed raised 30 -> 32.1 t/h (the model previously fed 30 at the INLET — the outlet basis grants +7 % chain capacity). The 38-40 t/h closure package is DEAD. Optimization result at the true limit (optimal zone-1 settings g60/CSS30/v35): max grits 46 716 t/y at z1.3 = 100 % -> residual 0/20 stock +8 881 t/y; at 95 % margin: grits 44 404, residual +12 178. STRICT zero 0/20 surplus is unreachable with this dryer — residual closure needs a crude-0/20 outlet (~10 kt/y) or the extension-case dryer investment | the client + engine |
| 2026-08-13 | REFERENCE CONFIGURATION ADOPTED (client, closing the 0/20-balance optimization campaign): zone-1 settings CR.5009 g = 60 mm, CR.5011 CSS = 30 mm / v = 35 m/s (KFS yield 20.5 -> 23.9 %, envelope compliant, in-cut 85.2 %); grits planning target 44 400 t/y (firm floor stays 40 000; 5 % zone-1.3 margin at the dryer limit); residual 0/20 accumulation ~12.2 kt/y kept as STRATEGIC RESERVE (~2 months of zone-1.2 feed). Result: KFS 85 000 + grits 44 400 + fines 60 000 + AgLime exactly 135 000 sold (59 759 t of fines redirected), zero unsellable; zones at 74.1 / 43.0 / 95.0 %. Side effects: mode 1B unusable at 250 t/h with CSS 30 (irrelevant — no stock campaigns needed); ch.9 reference tests pin the spec-era settings. Tests re-baselined | the client |
| 2026-08-13 | ZERO-RESIDUAL RULE (client): the 0/20 residual must be ZERO in ALL configurations. Implemented as a commercial rule (commercial_rules.crude_020_balancing_sales, data-toggleable): any 0/20 produced beyond the downstream reclaim is SOLD as CRUDE 0-20 — the product the NACO PFD zone-1.1 scenario table lists — making crude the swing variable of the balance. At the reference configuration: 12 183 t/y of crude sold, 0/20 net to stock = 0. This supersedes the 'strategic reserve' treatment adopted earlier the same day. Total sales rise to ~336.6 kt/y; every gram of feed now leaves as a sold product or dryer vapor | the client |
| 2026-08-13 | Grits target back to the FIRM 40 000 t/y (client — the 44 400 optimization variant stays available as a scenario); UltraFin added to the sales view (5 476 t/y at reference; the PFD packing plant lists FLUF ~6 000 t/y — consistent). Consolidated balance re-presented with explicit bases: conservation checked on DRY SOLIDS, each product reported in its commercial basis | the client |
| 2026-08-13 | 0/20 EXCESS RULING CORRECTED (client, supersedes the same-day crude-sales rule): there is NO market for crude 0/20 — the excess beyond the downstream reclaim goes to LANDFILL and is a NET FINANCIAL LOSS. Reported as a loss line with an alert, never a sale (commercial_rules.excess_020_to_landfill). At reference: 18 455 t/y wet to landfill. The financial lever table: grits 40 000 -> 18 455 t landfilled; grits 44 400 -> 12 183; grits 46 700 (dryer flat out) -> 8 904. Every extra grits tonne sold avoids ~1.4 t of landfill — the optimization campaign now has a direct financial reading | the client |
| 2026-08-14 | ZONE 1.3 REDESIGN LAUNCHED (client: zone judged badly dimensioned; from-scratch machine selection & sizing). DESIGN BASIS frozen element by element (docs/design/zone13-redesign/design-basis.md): D1 one machine park for 40 AND 80 kt/y grits (sizing case 80 kt, only rates/settings/hours differ); D2 dryer DY.03 acquired = the single drying line; D3 fines/grits <= 1.25 FIRM (capacity condition for 80 kt through the single dryer), <= 1.0 objective; D4 sized on measured chain + verified on quarry-target variant; D5 7 500 h / 80 %; D6 grits spec adopted (>4 mm <= 5 %, <2 mm <= 15 %); D7 fines sellable, UltraFin optional; D8 full-line commercial frame. Quarry target-curve decision still PENDING separately | the client |
| 2026-08-14 | C1 VALIDATED AS LEAD CANDIDATE (client, panel round 1) and WIRED INTO THE ENGINE as a selectable STUDY variant (default_scenario.zone_1_3_variant: "as-built" default / "c1"): 2-stage smooth double rolls RC.1 (g 8 mm, 29 t/h) + RC.2 (g 3.4 mm, 2 x 22 t/h, phase 1 runs 1 unit) + SC.A triple deck 8/3.75/2 (immediate 2-4 relief) + SC.B 1.5 mm sliver screen (sliver NOT reground, disposition pending). New machine sheets in data (n_comp 1.8 / comp_lam 2.2 / S_att 0.06, all [H] pending the vendor gradation test); flowsheet zone_1_3_c1 shares the DY.03 + SP.36/CL.38 blocks (D2). ENGINE RESULTS at the 30 t/h dryer outlet, measured chain: grits 14.58 t/h (48.6 %), total-fines/grits ratio 1.05 (D3 FIRM 1.25 met, as-built was 2.83), grits QC <2 mm 5.2 % / >4 mm 3.0 % (D6 met), recirculation 50.5 t/h, powers RC.1 17.6 / RC.2 20.3 kW installed, SC.A 3.7+3.3+2.5 m2, SC.B 2.2 m2; hours 2 744 h at 40 kt (45.7 %) and 5 489 h at 80 kt (91.5 % of the 6 000 h ceiling) — 80 kt FEASIBLE through the single dryer (as-built needed 10 275 h, impossible). D4 verification on the quarry-target feed (41 % < 20 mm): results within 0.3 % EXCEPT RC.1 load 29.7 > 29 t/h (alerted) — RC.1 purchase spec to be raised to ~32 t/h, client arbitration pending. Sliver 1.5/2 added to output_products (4.0 t/h); tests test_zone13_c1.py, suite 117 green | the client (C1 selection) + engine (results) |
| 2026-08-14 | SLIVER 1.5/2 ARBITRATION (client, option B): the SC.B oversize is REGROUND through RC.2 — the sliver disappears as a product. Encoded data-first as SC.B.oversize_routing ("regrind" default / "extract" selectable; the plant design carries a two-position diverter so the choice is reversible in operation). Context: the 1.5-2 mm band is a spec no-man's-land (grits bottom cut 2.0 protects D6, fines top cut 1.5 protects the 0/1.5 fines product spec + its redirect eligibility); the panel's "never regrind" rule was calibrated on the toothed ML.26 (S_att 0.171) — with smooth rolls (S_att 0.06) the engine counterfactual showed regrind WINS: ratio 0.79 (D3 objective <= 1.0 met, vs 1.05 extract), grits 16.66 t/h (55.5 %), D6 still met at 13.6 % < 2 mm (margin 1.4 pts, vendor gradation test to confirm), fines eligibility criterion 97.3 % < 1.7. Costs: BOTH RC.2 units in service (31.7 t/h, redundancy lost at phase 1), recirculation 60.6 t/h, and BC.22 grits conveyor OVERLOADED (16.7 vs 15 t/h PFD rating — retrofit ~20 t/h flagged); BE.40 fines conveyor returns WITHIN rating (13.1 t/h vs 21.0 as-built overload). Hours: 40 kt = 2 401 h (40.0 %), 80 kt = 4 802 h (80.0 %) | the client (routing) + engine (results) |
| 2026-08-14 | D6 GRITS ENVELOPE ENCODED on output product FeedLime grits (max_below_cut 15 % / max_above_cut 5 %) — and the AS-BUILT circuit FAILS it: 15.4 % < 2 mm. The redesign driver is now quantified on QUALITY as well as capacity; design-check verdict quality_holds re-baselined to False at the as-built default (dated test comment) | the client (D6 spec) + engine (finding) |
| 2026-08-14 | STREAM NAMING RULE (client): zone 1.3 produces DRY products ONLY — FeedLime grits 2/4, FeedLime fines 0/1.5, UltraFin. AgLime is a WET zone-1.2 product (0/1.7); zone 1.3 NEVER produces AgLime. The zero-waste redirect of the FeedLime-fines surplus into the AgLime SALES channel is a COMMERCIAL routing at loadout (planning sales view), never a production stream — presented tables must say "redirect eligibility (>= 95 % < 1.7 mm)" and never "AgLime spec" for zone-1.3 streams. RATIFIED by the client (naming table validated, option 1); engine label sweep done — planning sales line renamed "Fines surplus redirected to the AgLime sales channel", all other AgLime references confirmed zone-1.2/commercial | the client |
| 2026-08-14 | OPEN QUESTION (screens arrangement, client arbitration pending): the four decks 8 / 3.75 / 2 / 1.5 mm could live in ONE quad-deck machine, the current 3+1 (SC.A + SC.B), or TWO double-deck machines (8/3.75 recycle cuts + 2/1.5 product cuts — engineer-recommended). Engine results are IDENTICAL in all three (same Karra cascade, I = 0.15 per deck); the choice is mechanical: 1.5 mm deck efficiency and access at the bottom of a 4-stack, single point of failure, vs footprint and cost. Required areas 4.4 / 4.5 / 3.8 / 2.6 m2 | pending the client |
| 2026-08-14 | SCREEN ARRANGEMENT DECIDED (client, option 1): 2+2 — SC.A double deck 8/3.75 mm carries the RECYCLE cuts, SC.B double deck 2/1.5 mm carries the PRODUCT cuts (the two quality-critical decks each in favorable position); linking conveyor SC.A undersize -> SC.B at 39.9 t/h of 0/3.75. Engine results IDENTICAL by construction (verified: grits 16.658 t/h, ratio 0.792, balances closed). Data restructured (SC.A a1/a2, SC.B a1/a2); routing parameter renamed oversize_routing -> sliver_routing (on a 2-deck product screen the deck-1 oversize is the GRITS — naming-convention hygiene). Suite 118 green | the client |
| 2026-08-14 | BASE SCENARIO ADOPTED (client): SINGLE RC.2 unit (RC.2 n_units 2 -> 1), sliver regrind kept, dryer throttled to 22.27 t/h wet (69 % of its 32.1 capacity) so the unit runs exactly at its 22 t/h loop limit — MAX GRITS CAPACITY 69 300 t/y at the 6 000 h ceiling (engine, bisection on the RC.2 constraint; flows scale linearly). At the base point: grits 11.56 t/h (55.8 %), ratio 0.79, D6 met, RC.1 20.0/29 t/h, recirculation 42.0 t/h, BC.22 back WITHIN its 15 t/h rating (11.6), 40 kt/y in 3 461 h (57.7 %). EXTENSION provision: layout reserves the 2nd RC.2 slot (full-dryer regrind 16.66 t/h, 80 kt in 4 802 h — BC.22 retrofit needed then); phase-1 stopgap alternative documented: diverter on 'extract' allows full dryer on one unit (14.6 t/h, 87.5 kt/y max, 98.5 % unit load, 4 t/h sliver product). Tests re-baselined (full-flow bottleneck now EXPECTED, base-point test added), 119 green | the client |
| 2026-08-14 | RC.1 PURCHASE SPEC = 32 t/h (client, option 1; panel sizing was 29). Closes the D4 quarry-feed finding (29.7 t/h load on the quarry-target curve exceeded the 29 spec) and covers the full-dryer extension on both feed curves with ~8 % margin | the client |
| 2026-08-14 | C1 FORMALLY ADOPTED as the reference configuration (client, option 1): default_scenario.zone_1_3_variant = "c1", zone_1_3_feedlime = 22.27 t/h (base scenario); as-built stays selectable; [H] coefficients (n_comp, S_att) remain flagged pending the vendor gradation test. Epoch tests pinned to as-built (ch.9 suite, ML.26 vendor-curve/coefficient/fit tests); RC.2 single-source coefficient test added; suite 120 green. ANNUAL PLANNING CONSEQUENCES (engine, run_required_hours — the commercial cascade of making 2.8x fewer fines): zones 74.1 / 21.0 / 57.7 % (zone 1.3 relaxes from 91.6 %); fines production falls to 31 531 t (below its 60 kt market; redirect = 0); AgLime = loop-only 49 189 t in mode 2A vs the 135 kt market (the strict-c2 rule caps zone 1.2 at the collapsed FeedLime demand of 77 kt); 0/20 LANDFILL EXPLODES 18.5 -> 144.2 kt/y (only 126 kt reclaimed of 270 produced). CLIENT ARBITRATION PENDING on the cascade — identified levers: dedicated mode-2C AgLime campaigns (absorb up to ~86 kt of 0/20 toward the AgLime market), quarry target-curve recomputation (coarser feed reduces 0/20 at the source), fines-driven zone-1.3 hours (co-produces grits beyond target). Docs re-issue also pending: zone-1.3 calc document, DT-001 revision, web-UI zone-1.3 topology | the client (adoption) + engine (cascade) |
| 2026-08-14 | AGLIME 2C CAMPAIGNS WIRED into the planning (client order, lever 1 only — quarry curve NOT recomputed): commercial_rules.aglime_2c_campaigns (toggleable) — when the 2A co-production + fines redirect leave the AgLime market unserved, zone 1.2 runs dedicated mode-2C campaign hours (2C photo rate, hours counted against the zone ceiling, capped with alert). ENGINE RESULT at defaults: AgLime = 49 189 (2A) + 85 811 (2C, 858 h) = exactly 135 000 t sold; 0/20 reclaimed rises to 212 kt; LANDFILL 144.2 -> 58.4 kt/y (-60 %); zone 1.2 at 35.3 %. The RESIDUAL 58.4 kt/y stays a net loss — remaining levers (client arbitration pending): grits sales toward the 69.3 kt base capacity (arithmetic: landfill ~1.8 kt at 69.3 kt sold) and/or the quarry target-curve recomputation. Tests: planning re-baselined + toggle test, suite 121 green | the client (rule) + engine (results) |

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
