# PURCHASE TECHNICAL DATASHEET — SP.36

**Air classifier + fan (65 um cut) — zone 1.3**
Issued 2026-08-15 (client order of the same day: purchase datasheets for the 13 major process machines) — produced by NOEZYS.

## 1. Identification and role

| Item | Value |
|---|---|
| Tag | SP.36 |
| Type | Air classifier + fan (UltraFin classification of the fines stream) |
| Zone / duty | 1.3 — fines / UltraFin split at d50c = 65 um (Q6 closed 2026-08-11: 0.65 x d97, expert book ch.11 Stokes equilibrium) |
| Operating modes | G, F |
| Annual running hours (defaults) | 3 610.5 h effective |
| Criticality | Fines/UltraFin split; **cut NOT CERTIFIED** (standing planning alert: Phi(<cut) unmeasured) |

## 2. Process duty (engine runs, 2026-08-15)

| Quantity | Mode G | Mode F |
|---|---|---|
| Air flow Q_air (engine, cut lever) | 133.1 m3/h | **207.2 m3/h** |
| Phi(<cut) of the feed | 0.0065 (modelled, NOT certified) | 0.0059 (modelled, NOT certified) |
| Fines throughput context | 13.6 t/h to BE.40 | 23.2 t/h to BE.40 |

## 3. Settings and required adjustability

| Parameter | Unit | Range required | Reference setting |
|---|---|---|---|
| Cut size d50c | um | 45 - 150 (step 5) | 65 |
| Extraction efficiency eta_cl | - | 0.60 - 0.85 | 0.75 **[H]** — literature midpoint, flagged OPTIMISTIC (real quarry classifiers recover 50-65 % at finer cuts) |

The cut must be adjustable in operation (air-flow and/or rotor-speed lever) across the full 45-150 um range — Q_air is the engine's cut lever and the mode changes it by ~55 % (133 -> 207 m3/h).

## 4. Capacity and sizing requirements

- Continuous duty on the full fines stream in mode F (23.2 t/h fines context) at 3 610 h/y.
- **Fan capacity >= 420 m3/h with damper/VFD turndown — CLIENT DECISION 2026-08-15 (error-hunt PD-3, option 1)**: the fan is purchased for the FULL client-ruled soft-rock envelope, not the default calibration. Engine air demands: 207.2 m3/h (default calibration, mode F), 332.3 m3/h at the ruled UCS 20 reference, ~416 m3/h at the UCS 15 envelope edge (soft rock doubles the sub-65-um ultrafines). Turndown to ~130 m3/h (mode G, hard calibration) required — a VFD covers the full range. The vendor adds its own circuit-loss margin on top; the engine figures are process-model references, not a fan datasheet.
- `max_airflow_m3h` = 420 encoded in the data (was null — finding PD-3: no alert could ever fire on air demand); the engine now raises a fan bottleneck alert beyond it. The vendor fan curve refines it (value table, declared interpolation — golden rule 3).

## 5. FMECA-derived purchase requirements

| FM (RPN) | Failure mode | Purchase requirement |
|---|---|---|
| SP.36-FM1 (150) | Classifier wheel / vane wear (cut drift off 65 um) | **Wear liners / hard-facing on wheel and vanes stated for abrasive limestone at 3 610 h/y**; internals inspectable annually without full dismantling; guaranteed wear life or exchange interval |
| SP.36-FM2 (96) | Fan bearing failure | **Fan bearing condition monitoring** (vibration measurement points minimum, sensors preferred); spare bearing set in initial spares |
| SP.36-FM3 (80) | Air-circuit leakage / duct wear | Wear-resistant bends, gasket quality stated; **Q_air measurement instrument in the circuit** (the cut lever must be verifiable against the photo reference at the 6-monthly check) |

## 6. Open [H] items the vendor must close

- **Cut certification**: Phi(<cut) is UNMEASURED (standing alert) — the vendor acceptance test must include **sieve/laser sizing of both classifier products**, which simultaneously certifies the cut and closes the alert (the FMECA quarterly lab-sizing task then maintains it).
- **[H] eta_cl = 0.75** (flagged optimistic): the vendor must GUARANTEE the extraction efficiency at d50c 65 um on WANKOE fines — if the guarantee lands in the literature band (50-65 %), the UltraFin balance (0.067 t/h mode G / 0.104 t/h mode F at current defaults — error-hunt fix 2026-08-15: the previously quoted 0.99 t/h was the pre-C1 as-built figure) must be re-run by the engine before contract.
- Fan curve to be provided by the vendor (refines the encoded 420 m3/h rating; the soft-rock duty band 332-416 m3/h must sit on the stable part of the curve).
- Design-review adjacency (expert book 2026-08-11): a **polishing bag filter for the sub-4 um cyclone tail is MISSING from the flowsheet** — the SP.36/CL.38 vendor must state its air-circuit tail-dust loading so that design gap can be closed coherently.

## 7. Acceptance tests and QC criteria

1. **Cut acceptance**: d50c = 65 um +/- vendor tolerance, verified by laser/sieve sizing of both products at the mode-F duty; efficiency >= the vendor guarantee.
2. **Adjustability test**: cut swept across 45-150 um by the operating lever, verified at two extra points.
3. **UltraFin quality tie-in**: UltraFin product 0/0.1 mm spec; fines stream must retain its 0/1.5 spec and redirect eligibility after classification.
4. Fan vibration baseline; Q_air instrument calibrated against the reference operating points (133 / 207 m3/h engine references).

---
*Engine provenance: commit 5dc5b53, run 2026-08-15, `wankoe_model.scenario.run_scenario` (per-mode photos G / F, weather dry), data `data/default_parameters.json`. Replay: `PYTHONPATH=src python scripts/purchase_datasheet_evidence.py` -> `docs/purchase/purchase-engine-evidence.json`. Produced by NOEZYS.*
