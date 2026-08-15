# PURCHASE TECHNICAL DATASHEET — SR.5105

**Single-deck 6 mm FeedLime screen — zone 1.2**
Issued 2026-08-15 (client order of the same day: purchase datasheets for the 13 major process machines) — produced by NOEZYS.

## 1. Identification and role

| Item | Value |
|---|---|
| Tag | SR.5105 |
| Type | Single-deck vibrating screen, aperture 6 mm (PFD REV18: FeedLime = 6/20 oversize, undersize 0/6 to the AgLime loop) |
| Zone / duty | 1.2 — reclaim screening of the 0/20 stockpile |
| Operating modes | 2A (FeedLime + AgLime co-production); **inactive in 2C** (campaigns bypass it: full reclaim to the loop) |
| Annual running hours (defaults) | 2 428.3 h effective (zone 1.2) |
| Criticality | **SINGLE POINT of zone 1.2** — makes the FeedLime 6/20 cut feeding the whole dry-products chain |

## 2. Process duty (engine runs, 2026-08-15)

Total-flow rule: wet basis primary (wet = dry x 1.07527; 100 t/h wet reclaim).

| Quantity | Mode 2A |
|---|---|
| Screen feed, wet | **100.0 t/h** |
| Screen feed, dry solids | 93.0 t/h |
| Required area (6 mm deck) | 3.01 m2 |

## 3. Settings and required adjustability

| Parameter | Unit | Range required | Reference setting |
|---|---|---|---|
| Aperture a | mm | 4 - 8 (step 0.5) | 6 |

## 4. Capacity and sizing requirements

Sized on the worst (only) active mode 2A plus a **+25 % purchase margin [H]**:

| Deck | Worst-mode required area (engine) | **Purchase area (x1.25)** |
|---|---|---|
| 6 mm deck | 3.01 m2 (2A) | **>= 3.8 m2** |

Feed basis for the vendor sizing check: 100 t/h wet reclaimed 0/20 at 7 % moisture (a WET 6 mm cut — the most blinding-prone duty of zone 1.2; the vendor's sizing must state the moisture assumption).

## 5. FMECA-derived purchase requirements

| FM (RPN) | Failure mode | Purchase requirement |
|---|---|---|
| SR.5105-FM1 (180) | Panel wear / aperture growth (6 mm) | **Quick-change modular panels + one full spare panel set**; **aperture-gauging access** for the monthly check (both zone-1.2 product qualities depend on this single cut) |
| SR.5105-FM2 (105) | Blinding / pegging (wet 6 mm cut) | **Anti-blinding panel type** (or heated/flexible-mat option) demonstrated on wet sticky minus-20 mm limestone; wash-down access at planned stops |
| SR.5105-FM3 (120) | Exciter bearing failure | Exciter condition-monitoring provision; **exciter cartridge INTERCHANGEABLE with SR.5111 / SR.5115** (same class — the FMECA spares plan shares one cartridge across the three zone-1.2 screens); vendor to quote the three screens as a common family |
| SR.5105-FM4 (80) | Support spring failure | Springs replaceable in sets; stroke measurement points |

## 6. Open [H] items the vendor must close

- **[H] +25 % area margin**: vendor to verify the area by its own method at the stated wet-feed PSD (value table + declared interpolation, golden rule 3).
- Screening efficiency on the WET 6 mm cut: no imperfection parameter is exposed for this screen in the model — the vendor efficiency guarantee at 100 t/h wet is the missing datum.
- `installed_area_m2` null in the data — closed by the purchased deck area.

## 7. Acceptance tests and QC criteria

1. **FeedLime 6/20 cut acceptance**: oversize PSD spot check — the 6/20 stream feeds the dryer chain; cut integrity at 100 t/h wet feed.
2. **AgLime channel protection**: undersize 0/6 stream verified free of aperture-wear oversize (ties into the AgLime >= 95 % < 1.7 mm end spec after the loop).
3. **Blinding endurance**: 4 h sustained wet-feed run without effective-open-area collapse (vendor anti-blinding demonstration).
4. Exciter vibration + stroke baselines at commissioning; panel quick-change demonstration.

---
*Engine provenance: commit 5dc5b53, run 2026-08-15, `wankoe_model.scenario.run_scenario` (per-mode photos 2A / 2C, weather dry), data `data/default_parameters.json`. Replay: `PYTHONPATH=src python scripts/purchase_datasheet_evidence.py` -> `docs/purchase/purchase-engine-evidence.json`. The +25 % area margin is an assistant-stated sizing hypothesis [H]. Produced by NOEZYS.*
