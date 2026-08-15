# Preventive maintenance plan — prioritized by FMECA (RPN)

**Date: 2026-08-15 — deliverable (b) of the client's 5 arbitrated choices of
the same day** (see the decision-log row in `docs/spec-conformity-matrix.md`
and the method in `fmeca-register.md`). Every task below traces to a scored
failure mode of `fmeca-register.json` (38 equipment items, 147 modes); the
plan is **sorted by RPN**: CRITICAL (>= 200) first, then WATCH (100-199),
then the BASE routine program (< 100). Frequencies are given in calendar
terms with running-hour equivalents where the machine's actual annual hours
make the conversion meaningful (engine hours, defaults scenario).

## Maintenance windows — the plan fits WITHOUT production loss

Engine planning (`run_required_hours`, commit eac91cb): the zones run far
below their ceilings, so every planned task below fits in existing idle
windows — **no maintenance-driven production loss at the reference
operating point**.

| Zone | Regime / ceiling | Utilization (defaults) | Utilization (quarry target) | Natural windows |
|---|---|---:|---:|---|
| 1.1 | Saturday regime: 1 shift x 6 d/7, 2 400 h clock (client Q7, 2026-08-13) | 71.2 % (1 708 h clock) | 62.7 % | ~16 non-shift hours EVERY day + Sundays; ~690-900 h/y of in-regime slack |
| 1.2 | 7 500 h clock ceiling | 40.5 % | 36.0 % | ~4 460-4 800 h/y idle; schedule loop work outside the 2A blocks and 2C campaigns |
| 1.3 | 7 500 h clock ceiling | 60.2 % | 60.2 % | ~2 985 h/y idle; schedule between mode-G and mode-F blocks |

Window types used in the tables:

- **W1** — zone-1.1 idle window (any non-shift hours / Sunday).
- **W2** — zone-1.2 idle window (outside 2A / 2C blocks; the 0/20 and
  FeedLime stockpiles buffer zones 1.1 and 1.3 meanwhile).
- **W3** — zone-1.3 idle window (between G/F campaign blocks; the dryer must
  be cold for internal work — plan cooldown into the window).
- **W4** — ANNUAL SHUTDOWN (~1-2 weeks, all zones): dryer internals,
  refractory, structural NDT, silo and vent work. Fits inside any zone's
  slack; place it in the rain season when zone-1.2 loop hours are least
  valuable.
- **Mode-window** — work possible while the line PRODUCES in the other mode
  (e.g. BC.22 is idle during mode-F campaigns; BC.5013 idle in mode 1B).

Running-hour note: with zone 1.1 at 1 367 h/y, a "monthly" zone-1.1 task
~ every 115 running h; zone-1.2 loop (2 428 h/y) ~ every 200 running h;
zone 1.3 (3 610 h/y) ~ every 300 running h.

## A. CRITICAL band (RPN >= 200) — priority actions

Five failure modes score CRITICAL. Four of the five are resolved **at the
design/purchase stage** (the line is under construction — the cheapest
maintenance is the one engineered out now); the residual tasks then drop
the mode into the watch band.

| # | RPN | Equipment | Failure mode | Immediate action (design/purchase) | Recurring task | Frequency | Shutdown / window |
|---:|---:|---|---|---|---|---|---|
| 1 | 252 | SC.B | Deck-2.0 panel wear / aperture growth | Panel-change criterion set from the D6 envelope margin (0.8 pt, client): replace WELL before wear limit | Grits PSD lab check vs D6 envelope + deck-2.0 aperture gauging | PSD fortnightly; gauging monthly (~300 h) | PSD on samples (no stop); gauging in W3 |
| 2 | 245 | BE.40 | Chain/bucket wear at 116 % of rating | **Uprate/confirm BE.40 vs the 23.2 t/h mode-F duty (engine) — purchase file, with BC.22 (108 %)** | Hatch inspection: chain tension, bucket fixations, boot wear | Monthly (~300 h) until uprated, then quarterly | W3 |
| 3 | 224 | CR.5113 | Motor overload/burnout in 2C (348 kW absorbed vs 87 kW 2A — STANDING FINDING) | **Verify/uprate the installed motor against the 2C duty; until then cap the 2C campaign rate** | Winding thermal sensor trend + annual insulation (megger) test | Trend continuous; test yearly | Test in W2 |
| 4 | 210 | SR.5007 | Panel wear (35 mm) — KFS envelope | Panel stock + change criterion tied to the KFS envelope | KFS PSD spot check vs envelope + panel aperture gauging | Monthly (~115 h) | PSD on samples; gauging in W1 |
| 5 | 210 | SR.5111 | Panel wear (1.7 mm) at 155 % loop overload in 2C | **Resize the zone-1.2 loop (60 t/h rating vs 93 t/h 2C duty) — same file as CR.5113** | AgLime PSD check vs >= 95 % < 1.7 spec + panel gauging | Monthly (~200 h); weekly during 2C campaigns | PSD on samples; gauging in W2 |

## B. WATCH band (RPN 100-199) — reinforced preventive program

71 modes. Grouped by program; each line cites the highest-RPN mode it
addresses (full trace in `fmeca-register.json`).

### B.1 Condition-monitoring routes (create at commissioning)

| Top RPN | Route | Covers | Frequency | Window |
|---:|---|---|---|---|
| 196 | **Protection-function tests**: EM.09 test-piece pass (logged) | EM.09 hidden failure -> RC.1/RC.2 roll destruction | Weekly | On line (test piece) |
| 160 | **Dryer mechanical route**: girth-gear mesh + thermography, ring/roller temperatures | DY.03 drive 160, ring/roller 120 | Quarterly (~900 h); alignment survey 6-monthly | Running (thermography) + W3 |
| 192 | **Shell thermography scan** (refractory hot spots) | DY.03 refractory 192 | Monthly (~300 h) | Running |
| 150 | **Vibration route A (zone 1.3)**: SC.A/SC.B exciters, RC.1/RC.2 bearings (unit-to-unit comparison), BU.04 fan, FI/FN ID fan, SP.36 fan, BE.40 head+boot | exciters 140, RC.1 bearings 140, ID fan 140, BE.40 boot 150 | Quarterly (~900 h) | Running where safe + W3 |
| 140 | **Vibration route B (zones 1.1/1.2)**: SR.5007 exciters, CR.5009/CR.5011 bearings + gearboxes, SR.5105/5111/5115 exciters, CR.5113 bearings | SR.5111 exciter 150, CR.5113 bearing 150, CR.5009 bearing 140 | Quarterly (~115-200 h zone hours) | Running + W1/W2 |
| 150 | **PSD quality round** (lab): grits vs D6 (task A.1), KFS, AgLime, fines, UltraFin/fines split at SP.36 (closes the NOT-CERTIFIED alert), diverter-tightness cross-check | SC.A panels 150, SP.36 vanes 150, DV.GF leakage 150 | Fortnightly grits; monthly others; quarterly SP.36 lab sizing | On samples, no stop |
| 144 | **Motor-current trend alarms**: CR.5113 (2C), BE.40, BC.22, CR.5011 loop, feeder drives | overload family 144-224 | Continuous (control system) — review monthly | None |

### B.2 Screens program (all vibrating screens)

| Top RPN | Task | Screens | Frequency | Window |
|---:|---|---|---|---|
| 210 | Panel aperture gauging + change on criterion | SR.5007, SR.5105, SR.5111, SR.5115, SC.A, SC.B | Monthly (zone-hours equivalent above) | W1/W2/W3 |
| 105-120 | Blinding/pegging visual + wash-down (wet screens) / cleaning (dry screens); anti-blinding panel type at next re-panel for SR.5105/5111/5115 and SC.B | all | Shift-wise visual; wash-down at every planned stop | Rounds + W1/W2/W3 |
| 140-150 | Exciter service: grease per vendor; SHARED spare exciter cartridges (one per screen class: zone-1.2 trio, SC.A/SC.B pair) | all | Grease per vendor schedule; cartridge exchange on vibration verdict | W1/W2/W3 |
| 100-144 | Stroke/orbit measurement (springs, structure); annual structural NDT with panels lifted (SR.5111 priority — 155 % overload) | all | Stroke 6-monthly; NDT yearly | W1/W2/W3, NDT in W4 |

### B.3 Crushers program

| Top RPN | Task | Frequency | Window |
|---:|---|---|---|
| 168 | CR.5009 tooth-profile gauging + belt-cut PSD trend (the plant's ONLY measurement point — already specified); segment change on template | Monthly (~115 h) | W1 |
| 175 | Tramp risk: **DESIGN RECOMMENDATION — magnet/metal detector on the zone-1.1 pivot feed + rip-detection on BC.5007** (nothing protects zone 1.1 today; EM.09 guards only zone 1.3) | Decision at purchase stage | — |
| 168 | RC.2 roll-surface inspection BOTH units; staggered regrind campaigns (one unit always fresh); RC.1 roll inspection + regrind from PSD trend | Monthly (~300 h); regrind on criterion | W3 (RC.2 single-unit work possible at reduced rate in G: 22 of 33.2 t/h) |
| 144 | Gap checks vs reference settings: CR.5009 g = 60 (weekly), RC.1/RC.2 gaps incl. mode-F 1.5 mm min-gap (weekly); CR.5011/CR.5113 blow-bar gauging + dye-check at every planned stop, 2 bar sets stocked each | Weekly / per stop | W1/W2/W3 |
| 150 | Impactor rotor care: vibration acceptance after EVERY bar change (CR.5011, CR.5113); annual rotor inspection | Per bar change / yearly | W1/W2 |

### B.4 Dryer train program (DY.03 + BU.04 + FI.05/FN.06)

| Top RPN | Task | Frequency | Window |
|---:|---|---|---|
| 192 | Refractory: monthly shell thermography (B.1); internal refractory inspection | Thermography monthly; internal at W4 | Running / W4 |
| 180 | Internal flights + shell inspection; outlet-moisture trend as early indicator (spec lever at the 30 t/h limit) | Internal at W4; moisture trend continuous | W4 |
| 162 | Bag filter: dP trend review monthly; bag-condition sampling yearly; **DESIGN: broken-bag detector on the stack**; pulse-valve function check monthly; hopper discharge check weekly | As stated | Running + W3 |
| 150 | Dew-point discipline: preheat/purge at every light-off; annual internal casing thickness spots | Per light-off / yearly | Procedures / W4 |
| 144 | **SAFETY-CRITICAL (S = 9-10, outside RPN logic — never deprioritized): full flame-safety chain proof test yearly; purge interlocks never bypassed; daily fuel-train visual; annual fuel-system pressure test; burner-tip cleaning + combustion check (O2/CO) quarterly** | As stated | Proof test in W3/W4 |
| 108-112 | Dryer seals visual monthly, exchange at W4; combustion-air fan on vibration route A | Monthly | Rounds / W4 |

### B.5 Handling program (belts, feeders, elevator, silos)

| Top RPN | Task | Frequency | Window |
|---:|---|---|---|
| 245/144 | BE.40 + BC.22: see CRITICAL A.2 (uprate) — until then monthly hatch/belt inspections, backstop function test at every planned stop (BE.40), boot-level switch (design provision) | Monthly | W3; **BC.22 is serviceable DURING mode-F campaigns (idle in F) — zero production impact** |
| 120 | All belts: monthly belt + splice visual, yearly cover-thickness check; splice kits + one spare drive per standardized frame size | Monthly / yearly | W1/W2/W3; BC.5013 also idle in mode 1B |
| 100 | Idler/pulley thermal-acoustic round; scraper service | Monthly | Running (rounds) |
| 90 | BF.5101+5102: alternate feeder duty to equalize wear; quarterly belt inspection per feeder; **safe stockpile-clearing procedure (bridging) — no entry under hung material** | Quarterly + procedure | W2 (one feeder at a time — redundancy) |
| 96 | Silos BI.60/70/80: flow-aid function check monthly; vent-filter service quarterly; level-chain verification vs weighed inflow 6-monthly; high-high alarm test yearly; **never enter a silo** | As stated | W3 / W4 |

### B.6 Diverters and instruments

| Top RPN | Task | Frequency | Window |
|---:|---|---|---|
| 150 | DV.GF + DV.SL: function/exercise test at EVERY mode changeover (logged); blade/seat inspection yearly; tightness verified through the grits PSD round (B.1) | Per changeover / yearly | Mode changeovers (no extra stop) |
| 96 | BC.02 belt-weigher: monthly zero/span, quarterly material calibration (protects the 32.1 t/h wet dryer limit and moisture spec) | Monthly / quarterly | W3 (short) |
| 60 | EM.09 sensitivity audit at annual calibration (weekly test in B.1) | Yearly | W3 |

## C. BASE band (RPN < 100) — routine program

71 modes: standard lubrication, gearbox oil services (yearly, oil analysis
on the larger units — CR.5009 6-monthly), alignment checks, tracking and
housekeeping rounds, spring-set replacements on stroke verdict, cyclone
CL.38 dP monitoring + annual liner thickness, structural touch-ups. All
these live in the same W1/W2/W3 windows; none requires extra downtime.

**ML.26 (as-built variant only — inactive at the c1 reference)**: lay-up
preservation only — quarterly hand-rotation + greasing, covers/desiccant,
annual megger test — OR formal retirement of the unit (client decision to
take; the register carries it at S = 3).

## Spares strategy implied by the register

- Shared spare exciter cartridges per screen class (zone-1.2 trio,
  SC.A/SC.B pair, SR.5007 dedicated — largest frame).
- 2 blow-bar sets each for CR.5011 and CR.5113; roll-regrind capacity
  contract for RC.1/RC.2 (staggered campaigns).
- One spare drive per standardized belt frame size; splice kits; spare
  coupling elements (CR.5009, RC.1).
- Bag-filter media: one full set of bags + pulse-valve diaphragms.
- CR.5113 spare motor decision follows the uprate finding (A.3).

## Standing findings restated (maintenance cannot fix design)

1. **CR.5113 motor vs 2C duty (348 kW absorbed)** — purchase-file action.
2. **BE.40 at 116 % / BC.22 at 108 % of their handling ratings** —
   purchase-file action.
3. **Zone-1.2 loop rated 60 t/h vs 93 t/h in 2C (155 %)** — loop resize.
4. **No tramp-metal protection in zone 1.1** — add magnet/detector +
   BC.5007 rip detection.
5. **No capacity slack on the dry chain** (DY.03 at 100 % of its outlet
   limit in G, RC.1 at 91.3 %, RC.2 at 100 % in F) — condition-based
   maintenance is the only protection of the dry-products program; the
   civil reserve for a 2nd RC.2 / BC.22 retrofit (extension provision,
   open item) is also a reliability lever.

---
*Engine run: `wankoe_model.planning.run_required_hours` +
`wankoe_model.scenario.run_scenario` (per-mode photos 1A/1B/2A/2C/G/F),
engine commit eac91cb, run date 2026-08-15, data
`data/default_parameters.json`. Load-factor evidence:
`docs/design/maintenance/fmeca-engine-evidence.json` (replay:
`PYTHONPATH=src python scripts/fmeca_engine_evidence.py`). Task frequencies
and S/O/D cotations are expert judgment [H] (assistant-computed, not engine
output), to be recalibrated on CMMS failure history once the line runs.
This software is created **by NOEZYS**.*
