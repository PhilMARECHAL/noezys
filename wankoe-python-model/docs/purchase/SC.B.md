# PURCHASE TECHNICAL DATASHEET — SC.B

**Double-deck 2 / 1.5 mm product screen — zone 1.3**
Issued 2026-08-15 (client order of the same day: purchase datasheets for the 13 major process machines) — produced by NOEZYS.

## 1. Identification and role

| Item | Value |
|---|---|
| Tag | SC.B |
| Type | Double-deck vibrating screen, apertures 2.0 / 1.5 mm (C1 "2+2": deck 1 = grits bottom cut, D6-critical; deck 2 = fines top cut). Deck-1 oversize feeds the GRITS DIVERTER (mode G/F); deck-2 oversize is the SLIVER (reground via RC.2, diverter keeps "extract" selectable) |
| Zone / duty | 1.3 — makes BOTH dry product cuts (grits 2/3.75, fines 0/1.5) |
| Operating modes | G, F |
| Annual running hours (defaults) | 3 610.5 h effective |
| Criticality | **QUALITY-CRITICAL — carries the highest RPN of the whole equipment park** (deck-2.0 panel wear, RPN 252): the D6 grits envelope margin is only **0.8 pt** |

## 2. Process duty (engine runs, 2026-08-15)

Dry basis (zone 1.3).

| Quantity | Mode G | Mode F |
|---|---|---|
| Screen feed | 40.8 t/h | **50.0 t/h** |
| Required area — deck 1 (2.0 mm) | 4.01 m2 | **5.19 m2** |
| Required area — deck 2 (1.5 mm) | 2.64 m2 | **4.51 m2** |

## 3. Settings and required adjustability

| Parameter | Unit | Range required | Reference setting |
|---|---|---|---|
| Deck-1 aperture a1 (grits bottom cut) | mm | 1.8 - 2.5 (step 0.1) | 2.0 (protects D6 < 2 mm <= 15 %) |
| Deck-2 aperture a2 (fines top cut) | mm | 1.2 - 1.8 (step 0.1) | 1.5 (protects the 0/1.5 fines spec + redirect eligibility) |

## 4. Capacity and sizing requirements

Sized on the WORST mode (F) plus a **+25 % purchase margin [H]**:

| Deck | Worst-mode required area (engine) | **Purchase area (x1.25)** |
|---|---|---|
| Deck 1 (2.0 mm) | 5.19 m2 (F) | **>= 6.5 m2** |
| Deck 2 (1.5 mm) | 4.51 m2 (F) | **>= 5.6 m2** |

These are the finest process decks of the line at 3 610 h/y dry duty; the vendor sizing must state its near-mesh assumption (heavy 1.5-2 mm near-mesh fraction in mode F, 44 t/h circulating regrind loop upstream at gap 1.5 — error-hunt fix 2026-08-15: 147 t/h was the gap-2.8 runaway, not the operating duty).

## 5. FMECA-derived purchase requirements

| FM (RPN) | Failure mode | Purchase requirement |
|---|---|---|
| SC.B-FM1 (**252 — TOP RPN of the park**) | Deck-2.0 panel wear / aperture growth (D6 breach at 0.8 pt margin) | **Quick-change panel system with certified aperture tolerance on delivery** (each panel batch delivered with a measured-aperture certificate); **TWO spare panel sets for deck 1**; **aperture-gauging access designed in** (monthly gauging + fortnightly grits PSD is the maintenance plan — the purchase must make both fast); panel compound with a stated aperture-growth rate |
| SC.B-FM2 (180) | Deck-1.5 panel wear | Same quick-change system deck 2; one spare set; gauging access |
| SC.B-FM4 (140) | Exciter bearing failure | Exciter condition-monitoring provision; **spare cartridge SHARED with SC.A** (common family requirement) |
| SC.B-FM3 (105) | Blinding / pegging (1.5-2 mm dry) | **Anti-pegging provision** (ball-deck or equivalent) at least as a retrofit-ready option — FMECA design note; mode-F visual access |
| SC.B-FM5 (80) | Support spring failure | Springs in sets; stroke points — cut sharpness degrades exactly where the D6 margin is thinnest, so stroke drift must be measurable |

## 6. Open [H] items the vendor must close

- **Screening sharpness at 2.0 mm vs the D6 envelope**: the engine's as-built check FAILED D6 (15.4 % < 2 mm) and C1 passes with **0.8 pt margin** — the vendor must guarantee an imperfection/sharpness at the mode-G duty that PRESERVES that margin, and state the aperture at which its real cut point (d50) sits (the RC.1/RC.2 vendor gradation test feeds the same margin — the two purchases are coupled).
- **[H] +25 % area margin**: vendor bed-depth verification at 50 t/h (mode F) with the near-mesh statement (golden rule 3 value tables).
- `installed_area_m2` null — closed by the purchased deck areas.

## 7. Acceptance tests and QC criteria

1. **D6 envelope acceptance (grits)**: deck-1 oversize (2/3.75 grits) sieve-verified **< 2 mm <= 15 % and > 4 mm <= 5 %** at the mode-G duty — the firm 40 kt/y product.
2. **Fines acceptance**: deck-2 undersize meets the 0/1.5 fines spec AND the redirect eligibility criterion (>= 95 % < 1.7 mm — naming rule: "redirect eligibility", never "AgLime spec", for zone-1.3 streams).
3. **Mode-F endurance**: 4 h at 50 t/h with stable sliver routing (deck-2 oversize to RC.2) and no pegging collapse.
4. Aperture certificates checked panel-by-panel at delivery; gauging-access demonstration (monthly round executable within the vendor-stated time).
5. Exciter vibration + stroke baselines; diverter interface verified (grits diverter + sliver diverter tightness are separate FMECA items DV.GF/DV.SL riding on this screen's streams).

---
*Engine provenance: commit 5dc5b53, run 2026-08-15, `wankoe_model.scenario.run_scenario` (per-mode photos G / F, weather dry), data `data/default_parameters.json`. Replay: `PYTHONPATH=src python scripts/purchase_datasheet_evidence.py` -> `docs/purchase/purchase-engine-evidence.json`. The +25 % area margin is an assistant-stated sizing hypothesis [H]. Produced by NOEZYS.*
