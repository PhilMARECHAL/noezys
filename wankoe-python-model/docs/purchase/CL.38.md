# PURCHASE TECHNICAL DATASHEET — CL.38

**Static cyclone (UltraFin recovery) — zone 1.3**
Issued 2026-08-15 (client order of the same day: purchase datasheets for the 13 major process machines) — produced by NOEZYS.

## 1. Identification and role

| Item | Value |
|---|---|
| Tag | CL.38 |
| Type | Static cyclone (no drive of its own) — UltraFin fine-product recovery in the SP.36 classifier air circuit |
| Zone / duty | 1.3 — recovers the UltraFin 0/0.1 mm product from the classifier air stream |
| Operating modes | G, F |
| Annual running hours (defaults) | 3 610.5 h effective |
| Criticality | Wear part in the classifier air circuit; UltraFin recovery and downstream dust loading depend on it |

## 2. Process duty (engine runs, 2026-08-15)

| Quantity | Mode G | Mode F |
|---|---|---|
| Cut point d50 (engine, Barth/Stokes model) | 4.23 um | 4.23 um |
| Air circuit | SP.36 circuit: 133.1 m3/h (G) / 207.2 m3/h (F) | — |
| UltraFin context | 0.067 t/h (G) / 0.104 t/h (F) at current defaults, 284 t/y planned (error-hunt fix 2026-08-15: 0.99 t/h was the pre-C1 as-built figure) | — |

## 3. Settings and required adjustability

| Parameter | Unit | Range required | Reference setting |
|---|---|---|---|
| Inlet velocity v_in | m/s | 10 - 20 (step 1) | 15 |

Inlet-velocity adjustability (damper or geometry inserts) across the stated range — the d50 follows v_in and Q_air; nothing hardcoded (client rule 1).

## 4. Capacity and sizing requirements

- Sized for the SP.36 worst-mode circuit air flow (engine reference 207.2 m3/h in mode F) plus the vendor circuit margin; geometry consistent with a ~4 um d50 at v_in 15 m/s (engine reference).
- Abrasive fine limestone duty at 3 610 h/y — wear allowance is the sizing driver, not capacity.

## 5. FMECA-derived purchase requirements

| FM (RPN) | Failure mode | Purchase requirement |
|---|---|---|
| CL.38-FM1 (150) | Wear-liner perforation (cone / apex) | **Replaceable wear liners in cone and apex** (ceramic or equivalent stated for fine limestone); **thickness-inspection ports** so the annual liner check does not require dismantling; guaranteed liner life at the stated duty; carryover trend usable as the wear indicator |
| CL.38-FM2 (48) | Blockage (apex / inlet) | **Differential-pressure tapping points across the cyclone** (dP monitoring is the detection); apex access for the clearing procedure without hot work |

## 6. Open [H] items the vendor must close

- **Grade-efficiency curve** of the offered cyclone at the circuit operating points, delivered as a value table with declared interpolation mode (golden rule 3) — confirms the engine's d50 4.23 um and the UltraFin recovery balance.
- **Design-review adjacency (expert book 2026-08-11): the polishing bag filter for the sub-4 um cyclone TAIL is MISSING from the flowsheet** — the cyclone vendor must state the tail dust loading (g/m3) at duty so the filter design gap can be closed; this datasheet flags the item, the filter itself is a separate design action.
- UltraFin recovery figures depend on the SP.36 cut certification (Phi(<cut) unmeasured) — shared open item with SP.36.

## 7. Acceptance tests and QC criteria

1. **Recovery acceptance**: UltraFin collected product meets the 0/0.1 mm spec; recovery consistent with the vendor grade-efficiency table at the commissioning operating point.
2. **dP baseline**: clean-condition differential pressure recorded at both mode operating points (133 / 207 m3/h circuit references).
3. Liner thickness baseline at commissioning (the annual inspection datum).
4. Tail dust loading measured at commissioning — the input to the missing-bag-filter design item.

---
*Engine provenance: commit 5dc5b53, run 2026-08-15, `wankoe_model.scenario.run_scenario` (per-mode photos G / F, weather dry), data `data/default_parameters.json`. Replay: `PYTHONPATH=src python scripts/purchase_datasheet_evidence.py` -> `docs/purchase/purchase-engine-evidence.json`. Produced by NOEZYS.*
