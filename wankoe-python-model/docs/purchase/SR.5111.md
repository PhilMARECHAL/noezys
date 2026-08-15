# PURCHASE TECHNICAL DATASHEET — SR.5111

**Open 1.7 mm screen, AgLime loop — zone 1.2**
Issued 2026-08-15 (client order of the same day: purchase datasheets for the 13 major process machines) — produced by NOEZYS.

## 1. Identification and role

| Item | Value |
|---|---|
| Tag | SR.5111 |
| Type | Single-deck fine-cut vibrating screen, 1.7 mm, OPEN circuit (PFD REV18: undersize = AgLime direct, oversize -> CR.5113) |
| Zone / duty | 1.2 — first cut of the AgLime loop |
| Operating modes | 2A, 2C (AgLime campaigns) |
| Annual running hours (defaults) | 2 428.3 h effective (2A 1 749.7 h + 2C 678.6 h) |
| Criticality | Quality-critical: its undersize goes STRAIGHT to AgLime (>= 95 % < 1.7 mm spec, 135 kt/y commitment) |

## 2. Process duty (engine runs, 2026-08-15)

Total-flow rule: wet basis primary (wet = dry x 1.07527).

| Quantity | Mode 2A | Mode 2C |
|---|---|---|
| Screen feed, wet | 38.4 t/h | **100.0 t/h** |
| Screen feed, dry solids | 35.7 t/h | 93.0 t/h |
| Loop rating check (60 t/h conveyors BC.5110/BC.5116, PFD REV18) | 64 % | **155 % — STANDING FINDING: loop overload in 2C** |
| Required area (engine, cut-duty based) | 1.42 m2 | 1.42 m2 |
| Imperfection used | 0.15 [H] | 0.15 [H] |

## 3. Settings and required adjustability

| Parameter | Unit | Range required | Reference setting |
|---|---|---|---|
| Aperture a | mm | 1.5 - 2.0 (step 0.1) | 1.7 |
| Imperfection I | - | — | 0.15 **[H]** (vendor efficiency guarantee replaces it) |

## 4. Capacity and sizing requirements — RESIZE REQUIRED

**The 2C campaign duty is the sizing case and it EXCEEDS the present loop rating: 100 t/h wet across a 60 t/h-rated loop = 155 % (engine standing finding, FMECA rank 5).** The purchase must NOT reproduce the 60 t/h rating:

- **Screen rated for the 2C duty: 100 t/h wet (93 t/h dry) continuous feed** at the 1.7 mm cut — same file as the CR.5113 motor finding and the BC.5110/BC.5116 conveyor uprate.
- Engine required area is 1.42 m2 in both modes (cut-duty based — the engine area formula follows the undersize duty, not the bed load); with the **+25 % margin [H]** the minimum is **1.8 m2**, BUT the vendor must verify the deck area for the FULL 100 t/h wet bed load at 1.7 mm by its own bed-depth method — a fine wet cut at this tonnage will realistically need substantially more area than the cut-duty minimum. The vendor sizing at 100 t/h wet GOVERNS over the engine minimum.
- Deck structure rated for the 2C bed mass (FMECA FM4: structural fatigue at 155 % was scored on the CURRENT rating — the resize is the root-cause fix).

## 5. FMECA-derived purchase requirements

| FM (RPN) | Failure mode | Purchase requirement |
|---|---|---|
| SR.5111-FM1 (**210 — CRITICAL**) | Panel wear / aperture growth (1.7 mm) | **Quick-change fine-mesh panel system + TWO spare panel sets** (fine panels are consumables at this duty); **aperture-gauging access**; wear-resistant fine-mesh compound stated |
| SR.5111-FM4 (144) | Structural fatigue (overloaded deck) | Deck frame designed for the 100 t/h wet 2C duty (resize above); vendor fatigue calculation supplied; panels liftable for annual NDT |
| SR.5111-FM3 (150) | Exciter bearing failure | **Exciter bearing condition-monitoring provision** (2C overload hours accelerate fatigue); cartridge interchangeable with SR.5105 / SR.5115 (shared spare) |
| SR.5111-FM2 (105) | Blinding / pegging at 1.7 mm | Anti-blinding panel type for near-mesh wet fines; shift-wise visual access in campaign |

## 6. Open [H] items the vendor must close

- **[H] Imperfection I = 0.15** (literature): vendor to guarantee imperfection/efficiency at BOTH duties (38.4 and 100 t/h wet) — the AgLime spec depends on it directly.
- **[H] +25 % area margin / cut-duty area**: vendor bed-depth verification at 100 t/h wet GOVERNS (section 4).
- `installed_area_m2` null — closed by the purchased deck area.

## 7. Acceptance tests and QC criteria

1. **AgLime spec acceptance**: undersize stream >= 95 % passing 1.7 mm at BOTH duty points (2A and the full 2C 100 t/h wet), sieve-verified.
2. **2C endurance**: 4 h sustained at 100 t/h wet without efficiency collapse, blinding, or structural alarm.
3. Efficiency/imperfection measured at duty ≤ vendor guarantee (three-stream mass balance).
4. Exciter vibration + stroke baselines; fine-panel quick-change demonstration.

---
*Engine provenance: commit 5dc5b53, run 2026-08-15, `wankoe_model.scenario.run_scenario` (per-mode photos 2A / 2C, weather dry), data `data/default_parameters.json`. Replay: `PYTHONPATH=src python scripts/purchase_datasheet_evidence.py` -> `docs/purchase/purchase-engine-evidence.json`. The +25 % area margin is an assistant-stated sizing hypothesis [H]. Produced by NOEZYS.*
