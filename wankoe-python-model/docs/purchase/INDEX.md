# PURCHASE TECHNICAL DATASHEETS — INDEX

**13 major process machines — client order 2026-08-15** — produced by NOEZYS.
Scope: the process machines of the confirmed line design (C1 reference configuration). **DY.03 rotary dryer EXCLUDED — already acquired.** Belts, feeders, elevators and silos are handled in the FMECA/uprate files (BC.22 108 % and BE.40 116 % rating findings remain OPEN purchase-adjacent items on the handling side).

**VENDOR CANDIDATES (client order 2026-08-16):** [vendor-candidates.md](vendor-candidates.md) — five real catalog candidates per machine + best-adapted pick, from the public catalogs of the major manufacturers (catalog-level matches, not offers; acceptance tests in these datasheets remain the gates).

**CR.5009 SELECTION DOSSIER (10-expert panel, 10 client arbitrations 2026-08-16):** [CR.5009-selection-dossier.md](CR.5009-selection-dossier.md) — RFQ frame from the ten decisions, 10 candidates (5 Western + 5 Chinese premium), 6-bidder shortlist, comparability core (contractual curve + witnessed tests), documentation-asymmetry honesty section.

**RFQ PACKAGE (client order 2026-08-16 — "draft everything, my final word"; STATUS: DRAFT, SENDING SUSPENDED):** [rfq/00-common-conditions.md](rfq/00-common-conditions.md) (Ndola-derived contractual frame + common evaluation grid) + 12 machine RFQs `rfq/01…12` (CR.5009, SR.5007, CR.5011, SR.5105, SR.5111, CR.5113, SR.5115, RC.1, RC.2, SC.A, SC.B, SP.36). CL.38 withdrawn; DY.03 out of scope. No document leaves the project without an explicit client order.

**BUDGET ESTIMATE (client order 2026-08-16 — ~10 price points per machine, consolidated global budget):** [budget/budget-estimate.md](budget/budget-estimate.md) — 12 machine bands from ~105 real public price-evidence points (5 parallel cost-research teams, full sourced annexes in budget/evidence/), consolidated equipment total ≈ 0.97 / **2.26** / 3.62 M€ (LOW/CENTRAL/HIGH, new ex-works), global machine-supply budget ≈ **2.8 M€ CENTRAL** (+ spares/freight/commissioning [H]), carried with +25–30 % contingency ≈ 3.5 M€ provision. Class 4/5 budgetary accuracy declared (−30/+50 % per machine); the path to ±10 % = sending the drafted RFQs (suspended).

Every datasheet consolidates: (1) PROCESS DUTY from fresh engine runs (per-mode photos 1A / forced 1B / 2A / 2C / G / F, commit 5dc5b53, 2026-08-15 — replay `PYTHONPATH=src python scripts/purchase_datasheet_evidence.py`, evidence `purchase-engine-evidence.json`); (2) FMECA-derived purchase requirements (docs/design/maintenance/fmeca-register.json); (3) open [H] items the vendor must close, acceptance tests and QC criteria tied to the product specs (KFS envelope 30/55/15, D6 grits envelope, fines 0/1.5 + redirect eligibility >= 95 % < 1.7 mm, AgLime >= 95 % < 1.7 mm).

## Zone 1.1 — crushing/screening block (KFS + 0/20)

| Datasheet | Machine | Headline purchase requirements |
|---|---|---|
| [CR.5009.md](CR.5009.md) | Toothed double-roll primary crusher | Max nip vs the MEASURED F80 181 mm > 150 mm (standing alert — resolve vs the quarry top size); zone-1.1 tramp-metal protection (EM.09-adjacent, FMECA design rec); motor >= 132 kW rec. [H]; bearing temperature/vibration provision |
| [SR.5007.md](SR.5007.md) | Double-deck 35/20 screen | **Areas >= 9.1 / 9.6 m2 — RAIN duty is the sizing case (client decision 2026-08-15, error-hunt PD-2**; the former dry-basis 8.5/8.9 was undersized in rain); quick-change panels + spare sets + gauging access (KFS envelope, RPN 210); exciter bearing monitoring; imperfection guarantee replaces I = 0.15 [H] |
| [CR.5011.md](CR.5011.md) | Impact crusher (AP-S 1010 class) | 90 t/h WET vendor-basis capacity GUARANTEED at the mode-1B CSS 18 mm; blow-bar wear metallurgy + 2 spare sets; rotor balance spec + bar-change balancing acceptance |

## Zone 1.2 — reclaim / FeedLime / AgLime loop

| Datasheet | Machine | Headline purchase requirements |
|---|---|---|
| [SR.5105.md](SR.5105.md) | Single-deck 6 mm FeedLime screen | 100 t/h wet single point of zone 1.2; area >= 3.8 m2 (+25 % [H]); anti-blinding wet 6 mm cut; exciter cartridge common with SR.5111/5115 |
| [SR.5111.md](SR.5111.md) | Open 1.7 mm screen (AgLime loop) | **RESIZE: 2C duty = 167 % of the 60 t/h loop rating (wet basis) — rate the screen (and BC.5110/16 belts) for 100 t/h wet**; quick-change fine panels + 2 spare sets (RPN 210); deck structure per the resized duty; area >= 2.1 m2 (VSMA factor method, M-1 2026-08-15; vendor bed-depth sizing at 100 t/h wet governs) |
| [CR.5113.md](CR.5113.md) | Impact crusher (AgLime loop) | **Motor sized for the 2C campaign duty ~348 kW absorbed (450 kW rec. [H]) OR a capped campaign rate — vendor to state the branch**; winding temperature sensors + trend alarms (RPN 224); bearing monitoring; bar metallurgy for fine grinding |
| [SR.5115.md](SR.5115.md) | Closed-loop 1.7 mm screen | **Largest screen area of the line: >= 19.1 m2 RETAINED as the client-decided floor (M-1 disposition 2026-08-15: the VSMA factor method gives 13.3 — a published floor is never weakened without arbitration**; a 2A-sized screen would be undersized 3:1); fine-panel quick-change + spares; shared exciter cartridge |

## Zone 1.3 — dry products (C1: RC.1 + 2 x RC.2 + SC.A/SC.B "2+2")

| Datasheet | Machine | Headline purchase requirements |
|---|---|---|
| [RC.1.md](RC.1.md) | Smooth-roll crusher stage 1 | **32 t/h dry — client purchase spec 2026-08-14 (D4 closure)**; VENDOR GRADATION TEST = requirement (fixes n_comp/S_att [H], D6 margin 0.8 pt); roll surface wear spec; bearing temp/vibration monitoring; gap-drift instrumentation |
| [RC.2.md](RC.2.md) | Smooth-roll crusher stage 2 (2 units) | **2 x 25 t/h dry (raised from 2 x 22, client decision 2026-08-15, error-hunt PD-4: ~12 % headroom over the converged mode-F duty) with gap range 3.4 down to 1.5 mm — the 1.5 mm min-gap capability is a vendor-confirmation gate (mode F infeasible without it)**; gradation test requirement; gap-drift instrumentation 0.1 mm; per-unit bearing monitoring |
| [SC.A.md](SC.A.md) | Double-deck 8/3.75 recycle screen | Areas >= 6.0 / 7.0 m2 (worst mode F + 25 % [H]); quick-change panels + gauging access (loop-balance guard); exciter cartridge common with SC.B |
| [SC.B.md](SC.B.md) | Double-deck 2/1.5 product screen | **TOP RPN of the park (deck-2.0 wear 252): certified-aperture quick-change panels, 2 spare sets, designed-in gauging access — D6 margin only 0.8 pt**; sharpness guarantee at 2.0 mm; anti-pegging provision; **areas >= 7.4 / 7.5 m2 — full VSMA factor method (client decision 2026-08-15, error-hunt M-1**; the former 6.5/5.6 lacked the composition factors) |
| [SP.36.md](SP.36.md) | **FULL-STREAM dynamic classifier 65 um (re-specified 2026-08-16, benchmark Q4 option 2)** | Ingests the whole 0/1.5 stream (13.6–23.3 t/h; Ventoplex C25V class, INTERNAL fan — the PD-3 external fan is CANCELLED); honesty ceiling ~430 t/y UltraFin (natural sub-65 content 0.6 %); cut certification by sieve/laser; eta guarantee; wear liners; vent bag filter (ePTFE, RCS-scoped) |
| [CL.38.md](CL.38.md) | Static cyclone — **⚠ WITHDRAWN 2026-08-16** | Superseded by the full-stream classifier's internal recirculation (Q4 option 2); sheet kept as engineering record; the polishing bag filter survives as the circuit vent |

## Cross-cutting requirements (all 13 offers)

1. **Nothing hardcoded** (client rule 1): every stated setting range must be adjustable without reprogramming or mechanical rework.
2. **Vendor curves as VALUE TABLES with the interpolation mode declared** (golden rule 3): gradation, capacity, efficiency and fan/grade-efficiency curves.
3. **[H] closure**: each datasheet lists the open [H] hypotheses its vendor must replace by guarantees or witnessed tests; re-fitted values land data-first in `data/default_parameters.json` and the engine replays the line balance before acceptance.
4. **Condition monitoring at purchase, not retrofit**: bearing temperature/vibration provisions per the FMECA (quarterly routes exist for all these machines in the preventive plan).
5. **Screen family standardization**: SR.5105/5111/5115 one exciter-cartridge class; SC.A/SC.B one class; quick-change panel systems + spare panel sets everywhere a cut is quality-critical.
6. **Sizing margins stated, not silent**: screen areas = worst engine mode + 25 % [H]; motors = worst-mode absorbed x 1.15 [H] rounded to IEC — both flagged hypotheses the vendor verifies by its own method.

---
*Engine provenance: commit 5dc5b53, run 2026-08-15, `wankoe_model.scenario.run_scenario` per-mode photos, data `data/default_parameters.json`; evidence file `docs/purchase/purchase-engine-evidence.json` (replayable without the assistant). Produced by NOEZYS.*
