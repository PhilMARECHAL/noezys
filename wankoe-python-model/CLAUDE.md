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

## Total-flow rule (client, 2026-08-14, load-bearing)

Every line feed rate is the TOTAL flow — WET basis (dry solids + water),
as belt-weighed: zone 1.1 = 250 t/h wet, zone 1.2 reclaim = 100 t/h
wet, zone-1.3 feedlime wet too. Engine converts to dry at each zone
boundary; PRESENTED rates are quoted in total (wet) flow unless
explicitly labeled dry.

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
PRIORITY & ZERO-WASTE RULES (client, 2026-08-12/13): FIRM products KFS
85 kt + grits 40 kt are the absolute priority. Fines sold up to their
60 kt market cap; the FINES SURPLUS IS REDIRECTED INTO THE AGLIME
CHANNEL (0/1.5 fits the >=95% <1.7 spec); the AgLime loop only makes
the complement to the 135 kt cap — NO AgLime objective or campaigns.
planning.py implements this (sales_t view). Zero unsellable product at
defaults; 0/20 stock grows ~76.8 kt/y (yard sizing watch). Grits 80 kt
= documented EXTENSION CASE only (not feasible on current line).
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

## Reference configuration (client, 2026-08-13 — the operating point)

Zone-1 settings g = 60 / CSS = 30 / v = 30 (v 35 -> 30 client
2026-08-14, last settings headroom vs landfill; KFS compliant); dryer
limit 30 t/h AT OUTLET = 32.1 t/h wet feed (encoded); grits planning
target 44 400 t/y (firm floor 40 000); Saturday regime zone 1 (2 400 h).
Sales: KFS 85 000 + grits 44 400 + fines 60 000 + AgLime exactly
135 000 (zero-waste redirect). 0/20 EXCESS = LANDFILL, a NET LOSS
(client final ruling 2026-08-13: NO crude market exists;
commercial_rules.excess_020_to_landfill, alerted, minimized — 18.5 kt/y
at grits 40 kt; 12.2 at 44.4 kt; 8.9 at dryer-flat-out 46.7 kt). Zones 74.1 / 43.0 / 95.0 %. Mode 1B unusable at 250 t/h with
CSS 30 (no longer needed). Ch.9 tests pin all spec-era settings.
AUTO MODE-1B RULE (client 2026-08-14): KFS is NEVER over-produced —
if the 0/20 demand would drive zone 1.1 beyond the KFS-target hours,
the deficit is made in dedicated mode-1B hours (feed 186.1 t/h wet,
CSS 18, CR.5011 at its 90 t/h wet limit;
commercial_rules.zone_1_1_auto_mode_1B, no-op at current defaults).

## Zone-1.3 redesign (2026-08-14 — C1 ADOPTED)

Design basis D1-D8 frozen (docs/design/zone13-redesign/design-basis.md).
C1 FORMALLY ADOPTED as the reference configuration (client 2026-08-14):
zone_1_3_variant "c1" IS the default (feed 22.27 t/h wet; as-built
selectable for history; ch.9 + ML.26 epoch tests pin as-built):
RC.1/RC.2 smooth rolls + two double-deck screens (client 2026-08-14,
"2+2"): SC.A 8/3.75 recycle cuts, SC.B 2/1.5 product cuts (linking
conveyor 39.9 t/h of 0/3.75). SLIVER ARBITRATION (client, option B):
SC.B deck-2 oversize REGROUND through RC.2 (SC.B.sliver_routing,
"extract" stays selectable — diverter in the design). FINES OBJECTIVE + TWO-MODE CONFIG (client 2026-08-14, supersedes the
throttled single-unit base): fines 60 kt/y is a PRODUCTION OBJECTIVE;
new GRITS DIVERTER (SC.B deck-1 oversize) gives mode G (grits) /
mode F (fines campaign: 2/3.75 + sliver reground in RC.2 at the
mode-F gap 1.5 mm — 2.8 mm circulates 147 t/h, engine-proven). TWO
RC.2 UNITS installed (purchase spec: min gap 1.5, vendor to confirm).
Operating points: mode G = full dryer 32.1 (grits 16.22 t/h, RC.2
33.2/44); mode F = 25.05 t/h (fines 23.2 t/h, units at capacity).
Two-mode planning: z1.3 = 2 466 h G + 1 144 h F (60.2 %); all four
markets served exactly; LANDFILL 13.8 kt/y; KFS Yield required
25.93 % vs realized 24.88 (gap 1.05 pt). D6 envelope encoded on
FeedLime grits — AS-BUILT FAILS IT (15.4 % < 2 mm).
NAMING RULE (client): zone 1.3 = DRY products only (grits, fines,
UltraFin); AgLime is a WET zone-1.2 product — the fines-surplus
redirect is a SALES routing at loadout, say "redirect eligibility",
never "AgLime spec", for zone-1.3 streams.
RC.1 purchase spec = 32 t/h (client 2026-08-14, closes the D4
quarry-feed finding). COMMERCIAL CASCADE OF ADOPTION: fines fall to
31.5 kt (60 kt market), redirect = 0. AGLIME 2C CAMPAIGNS WIRED
(client lever 1, commercial_rules.aglime_2c_campaigns): AgLime = 2A
49.2 + 2C 85.8 = 135 kt served; LANDFILL 144.2 -> 58.4 kt/y.
KFS YIELD indicator (client 2026-08-14, 4-question definition): whole
KFS stream / wet pivot feed, real PSD attached, dynamic
required-for-zero-landfill target (KFS/(KFS + 0/20 demand)) — in
scenario results.indicators + planning kfs_yield + alert; realized
24.88 % vs required 28.41 % on the X2 CONVERGED GRID (client
2026-08-14: engine.computation_grid_refinement 2; spec sieves stay the
presentation format; C1 base point re-bisected: feed 21.29 t/h wet,
grits 10.76 t/h, single-unit max 64 554 t/y; internal confidence
program docs/design/zone11-verification/ COMPLETE, actions 1-6,
meta-score 74 -> 94 = internal ceiling; residual 6 pts external:
vendor curves, drop-weight, sieve test, repeat belt-cuts, NACO
reconciliation. Audit fixes 2026-08-14: M7 bypass pinned at gap in
capped regime; capacity_basis per machine; M6 zero duty on
no-drying).
QUARRY WORKS SPEC ADOPTED (client 2026-08-14): 40.1 % < 20 mm at the
zone-1 inlet (rescale k 1.426; supersedes 38.1 and 41 % history) =
zero landfill WITH a 20 % AgLime-market flex buffer (AgLime baseline
108 kt, 27 kt held open as shock absorber; explicit cost -27 kt/y
baseline sales). docs/design/zone13-redesign/
quarry-works-specification.md (control point 20 mm, acceptance bands
40.1/45.5, KFS-Yield live monitor). At target: yield 28.26 %
self-consistent, zones 62.7/36.0/60.2. OTHER OPEN: extension provision
(civil reserve for 2nd RC.2 + BC.22 retrofit deferred); final machine
codification (SN.2x/CR.2x proposal to NACO); installed screen areas &
motor sizes (recommend sizing for the extension per D1); linking
conveyor rating; docs re-issue (zone-1.3 calc doc, DT-001 revision,
web-UI zone-1.3 topology);
C2 escalation / C4 comparator in reserve; vendor gradation test fixes
n_comp & S_att [H]. Block diagram (draw.io, as-built + C1):
docs/design/zone13-redesign/zone13-block-diagram.drawio.

## OPEX energy model (client arbitrations 2026-08-15)

scripts/opex_electricity.py + data "electrical_loads" (data-first):
electricity-only kWh — perimeter excludes the fuel-fired dryer burner
(illuminating paraffin, ~1 043 t/y ~ 1.30 ML/y, reported apart); ABSORBED
power (engine P_net/eta_m or typical ratings [H] x 0.72 [H]); hours =
run_required_hours per mode bucket; both scenarios (defaults / quarry
target + AgLime 108 kt). Totals 1 276.9 / 1 192.8 MWh/y. CASCADED
ZONE-EXIT COST (same day): MASS allocation (every outgoing tonne of a
zone carries the same kWh/t; zone-1.3 mass-shrink convention: vapor
carries no energy, all kWh on the outgoing product tonnes) x
115 EUR/MWh [H] (Western-Europe industrial average, awaiting the
client's contract) -> EUR/t defaults/quarry: KFS 0.073/0.080, AgLime +
FeedLime 6/20 0.321/0.318, dry products 0.960/0.957. Report:
docs/design/opex/electricity-opex.md + .json.

## FMECA maintenance plan (client arbitrations 2026-08-15)

Full-park FMECA (5 client choices: 35 electrical_loads consumers +
process machines + diverters/silos = 38 items, 147 modes; RPN = SxOxD,
>=200 critical / 100-199 watch; severity anchor mixed; occurrence =
generic classes [H] x engine load factors). docs/design/maintenance/:
fmeca-register.json (authoritative) + .md, preventive-maintenance-plan.md
(RPN-sorted, fits idle windows — zero production loss), evidence replay
scripts/fmeca_engine_evidence.py. Top-3 RPN: SC.B deck-2.0 panel wear
252, BE.40 bucket wear 245 (116 % of rating), CR.5113 2C motor overload
224 (standing finding). 4 of 5 critical modes = design/purchase fixes
(CR.5113 motor, BE.40/BC.22 uprate, zone-1.2 loop resize at 155 % in 2C).

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
