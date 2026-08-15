# PURCHASE TECHNICAL DATASHEET — SR.5115

**Closed-loop 1.7 mm screen, AgLime loop — zone 1.2**
Issued 2026-08-15 (client order of the same day: purchase datasheets for the 13 major process machines) — produced by NOEZYS.

## 1. Identification and role

| Item | Value |
|---|---|
| Tag | SR.5115 |
| Type | Single-deck fine-cut vibrating screen, 1.7 mm, CLOSED loop with CR.5113 (undersize joins AgLime, oversize recycles to the crusher) |
| Zone / duty | 1.2 — closes the AgLime loop; its passing IS the loop AgLime product |
| Operating modes | 2A, 2C |
| Annual running hours (defaults) | 2 428.3 h effective |
| Criticality | Quality-critical (AgLime >= 95 % < 1.7 mm, 135 kt/y commitment) |

## 2. Process duty (engine runs, 2026-08-15)

Total-flow rule: wet basis primary (wet = dry x 1.07527).

| Quantity | Mode 2A | Mode 2C |
|---|---|---|
| Screen feed, wet | 30.2 t/h | **92.5 t/h** |
| Screen feed, dry solids | 28.1 t/h | 86.0 t/h |
| Required area (engine) | 4.99 m2 | **15.28 m2** |
| Imperfection used | 0.15 [H] | 0.15 [H] |

## 3. Settings and required adjustability

| Parameter | Unit | Range required | Reference setting |
|---|---|---|---|
| Aperture a | mm | 1.5 - 2.0 (step 0.1) | 1.7 |
| Imperfection I | - | — | 0.15 **[H]** (vendor efficiency guarantee replaces it) |

## 4. Capacity and sizing requirements

**Mode 2C is the sizing case — it triples the area demand** (the whole CR.5113 product passes here at the loop equilibrium):

| Deck | Worst-mode required area (engine) | **Purchase area (x1.25)** |
|---|---|---|
| 1.7 mm deck | 15.28 m2 (2C) | **>= 19.1 m2 — RETAINED as the client-decided floor (error-hunt M-1 disposition 2026-08-15)** |

M-1 disclosure: the full VSMA factor method (`scripts/vsma_factor_sizing.py`) gives a LOWER worst duty here — 10.61 m2 (quarry curve, 1B upstream, 2C) → 13.3 m2 with margin — because this deck's ~78 % oversize feed earns a high VSMA oversize factor. Rule applied: an issued purchase floor is never weakened without a dedicated client arbitration, so **19.1 m2 stands** (it also covers the audit's M-2 note that the model worst 15.72 × 1.25 = 19.65 slightly exceeded the old basis). The vendor bed-depth sizing at the 2C bed load governs.

This is the LARGEST screen area requirement of the line — a screen bought on the 2A duty (5 m2 class) would be undersized 3:1 for campaigns. Feed basis for the vendor check: 92.5 t/h wet of CR.5113 product (P80 0.95 mm) at the 1.7 mm cut; part of the same resize file as SR.5111 and the CR.5113 motor.

## 5. FMECA-derived purchase requirements

| FM (RPN) | Failure mode | Purchase requirement |
|---|---|---|
| SR.5115-FM1 (180) | Panel wear / aperture growth (1.7 mm) | **Quick-change fine-mesh panel system + TWO spare panel sets**; **aperture-gauging access** for the monthly check (shared PSD round with SR.5111); wear-resistant fine-mesh compound |
| SR.5115-FM3 (120) | Exciter bearing failure | Exciter condition-monitoring provision; **cartridge interchangeable with SR.5105 / SR.5111** (shared spare across the zone-1.2 screen family) |
| SR.5115-FM2 (105) | Blinding / pegging at 1.7 mm | Anti-blinding panel type for near-mesh fines; campaign-time visual access |
| SR.5115-FM4 (80) | Support spring failure | Springs replaceable in sets; stroke measurement points |

## 6. Open [H] items the vendor must close

- **[H] Imperfection I = 0.15** (literature, client arbitration 2026-08-10): vendor efficiency guarantee at the 2C duty — loop convergence and AgLime quality both depend on it.
- **[H] +25 % area margin**: vendor to verify the 19.1 m2 purchase area by its own bed-depth method at 92.5 t/h wet (value table + declared interpolation, golden rule 3).
- `installed_area_m2` null — closed by the purchased deck area.

## 7. Acceptance tests and QC criteria

1. **AgLime spec acceptance**: undersize >= 95 % passing 1.7 mm at the 2C duty point, sieve-verified (the loop product joins SR.5111 undersize into the AgLime chain).
2. **Loop convergence test**: stable circulating load at the 2C equilibrium (86.0 t/h dry through the crusher) over 4 h — no runaway recirculation.
3. Efficiency/imperfection at duty ≤ vendor guarantee (three-stream mass balance).
4. Exciter vibration + stroke baselines; fine-panel quick-change demonstration.

---
*Engine provenance: commit 5dc5b53, run 2026-08-15, `wankoe_model.scenario.run_scenario` (per-mode photos 2A / 2C, weather dry), data `data/default_parameters.json`. Replay: `PYTHONPATH=src python scripts/purchase_datasheet_evidence.py` -> `docs/purchase/purchase-engine-evidence.json`. The +25 % area margin is an assistant-stated sizing hypothesis [H]. Produced by NOEZYS.*
