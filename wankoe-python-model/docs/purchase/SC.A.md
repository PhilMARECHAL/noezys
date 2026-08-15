# PURCHASE TECHNICAL DATASHEET — SC.A

**Double-deck 8 / 3.75 mm recycle screen — zone 1.3**
Issued 2026-08-15 (client order of the same day: purchase datasheets for the 13 major process machines) — produced by NOEZYS.

## 1. Identification and role

| Item | Value |
|---|---|
| Tag | SC.A |
| Type | Double-deck vibrating screen, apertures 8 / 3.75 mm (C1 "2+2" arrangement, client 2026-08-14: recycle cuts on SC.A, product cuts on SC.B) |
| Zone / duty | 1.3 — recycle node: deck 1 oversize -> RC.1, deck 2 oversize -> RC.2, undersize -> SC.B |
| Operating modes | G, F |
| Annual running hours (defaults) | 3 610.5 h effective |
| Criticality | Single screen of the zone-1.3 recycle node (chain stop if down) |

## 2. Process duty (engine runs, 2026-08-15)

Dry basis (zone 1.3).

| Quantity | Mode G | Mode F |
|---|---|---|
| Screen feed | 92.2 t/h | 90.1 t/h |
| Required area — deck 1 (8 mm) | 4.47 m2 | **4.77 m2** |
| Required area — deck 2 (3.75 mm) | 4.56 m2 | **5.59 m2** |

## 3. Settings and required adjustability

| Parameter | Unit | Range required | Reference setting |
|---|---|---|---|
| Deck-1 aperture a1 (recycle cut to RC.1) | mm | 6.0 - 10.0 (step 0.5) | 8.0 |
| Deck-2 aperture a2 (recycle cut to RC.2) | mm | 3.5 - 4.5 (step 0.05) | 3.75 |

## 4. Capacity and sizing requirements

Sized on the WORST mode (F) plus a **+25 % purchase margin [H]**:

| Deck | Worst-mode required area (engine) | **Purchase area (x1.25)** |
|---|---|---|
| Deck 1 (8 mm) | 4.77 m2 (F) | **>= 6.0 m2** |
| Deck 2 (3.75 mm) | 5.59 m2 (F) | **>= 7.0 m2** |

Feed basis for the vendor check: ~92 t/h dry recycle-loop feed (RC.1 + RC.2 products + fresh dried 6/20), abrasive dry limestone at 3 610 h/y.

## 5. FMECA-derived purchase requirements

| FM (RPN) | Failure mode | Purchase requirement |
|---|---|---|
| SC.A-FM1 (150) | Deck panel wear / aperture growth | **Quick-change modular panels + one full spare panel set per deck**; **aperture-gauging access** (monthly gauging + loop-balance check: cut drift coarsens the RC.2 feed while RC.2 is at 100 % in F) |
| SC.A-FM3 (140) | Exciter bearing failure (single-screen chain stop) | **Exciter condition-monitoring provision**; **spare exciter cartridge SHARED with SC.B** — the two zone-1.3 screens must be quoted as a common family with interchangeable cartridges |
| SC.A-FM2 (72) | Blinding / pegging (3.75 mm dry) | Anti-pegging panel option on deck 2; deck cleaning access at planned stops |
| SC.A-FM4 (80) | Support spring failure | Springs replaceable in sets; corner stroke measurement points |

## 6. Open [H] items the vendor must close

- **[H] +25 % area margin**: vendor bed-depth verification at the stated duty (value table + declared interpolation, golden rule 3).
- Screening efficiency guarantee on both decks (dry 8 / 3.75 mm cuts) — the loop balance (RC.1 at 91.3 %, RC.2 at 100 % in F) has no slack for misrouted recycle.
- `installed_area_m2` null — closed by the purchased deck areas.

## 7. Acceptance tests and QC criteria

1. **Cut-integrity acceptance**: three-stream sieve analysis at duty — deck-1 and deck-2 cuts within the vendor efficiency guarantee; loop mass balance closed.
2. **Loop stability tie-in**: 4 h mode-F run with stable RC.2 circulating load (SC.A misrouting is the loop's main disturbance input).
3. Exciter vibration + stroke baselines at commissioning; panel quick-change demonstration; cartridge interchange demonstration with SC.B.

---
*Engine provenance: commit 5dc5b53, run 2026-08-15, `wankoe_model.scenario.run_scenario` (per-mode photos G / F, weather dry), data `data/default_parameters.json`. Replay: `PYTHONPATH=src python scripts/purchase_datasheet_evidence.py` -> `docs/purchase/purchase-engine-evidence.json`. The +25 % area margin is an assistant-stated sizing hypothesis [H]. Produced by NOEZYS.*
