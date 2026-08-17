# PURCHASE TECHNICAL DATASHEET — SR.5007

**⚠ TAG EQUIVALENCE (2026-08-17):** this machine is now tagged
**SR.5008** in the model and all new documents, per the NACO PFD
11-01-PFD REV15 (client retag decision). Pre-existing documents keep
the spec-era tag SR.5007; the two tags designate the SAME machine.

**Double-deck 35/20 mm vibrating screen — zone 1.1**
Issued 2026-08-15 (client order of the same day: purchase datasheets for the 13 major process machines) — produced by NOEZYS.

## 1. Identification and role

| Item | Value |
|---|---|
| Tag | SR.5007 |
| Type | Double-deck vibrating screen, apertures 35 / 20 mm |
| Zone / duty | 1.1 — makes the KFS 20/35 product and the 0/20 undersize; **largest screen duty of the line** |
| Operating modes | 1A, 1B |
| Annual running hours (defaults) | 1 366.6 h effective |
| Criticality | QUALITY-CRITICAL: single screen making the KFS envelope (firm 85 kt/y) |

## 2. Process duty (engine runs, 2026-08-15)

Total-flow rule: wet basis primary (wet = dry x 1.07527).

| Quantity | Mode 1A | Mode 1B |
|---|---|---|
| Screen feed, wet | **324.5 t/h** | 276.1 t/h |
| Screen feed, dry solids | 301.8 t/h | 256.8 t/h |
| Required area — top deck (35 mm) | 6.80 m2 | 6.17 m2 |
| Required area — bottom deck (20 mm) | 7.15 m2 | 7.08 m2 |

## 3. Settings and required adjustability

| Parameter | Unit | Range required | Reference setting |
|---|---|---|---|
| Top deck aperture a1 | mm | 20 - 50 | 35 |
| Bottom deck aperture a2 | mm | 10 - 30 | 20 |
| Imperfection I (efficiency class) | - | — | 0.15 **[H]** (client arbitration 2026-08-10, literature value — the vendor efficiency guarantee replaces it) |

Aperture changes are made by PANEL EXCHANGE — see the FMECA requirements below; the vendor must confirm panel availability across the full aperture ranges.

## 4. Capacity and sizing requirements (screen areas)

**CLIENT DECISION 2026-08-15 (error-hunt PD-2, option 1): the purchase minima are the RAIN duty — the true worst circumstance.** Rain is a normal operating condition for this screen (25 % of the season, and the line runs through rain weeks by client ruling); wet screening at 20/35 mm stays feasible but derated by the wet capacity factor 0.75, which consumes the entire former +25 % dry-basis margin. A screen bought on the previous dry-basis minima (8.5/8.9 m2) would be undersized in rain — corrected here.

| Deck | Dry duty (1A) | **RAIN duty (1A-rain) — sizing case** | **Purchase minimum (client-decided)** |
|---|---|---|---|
| Top deck (35 mm) | 6.80 m2 | 9.07 m2 | **>= 9.1 m2** |
| Bottom deck (20 mm) | 7.15 m2 | 9.53 m2 | **>= 9.6 m2** |

No further margin is stacked on the rain case; the +25 % [H] allowance survives as natural DRY-weather headroom (~33 % over the dry duty). Vendor to verify by its own bed-depth / V-factor method at BOTH duty points.

Feed basis for the vendor's sizing check: 324.5 t/h wet (301.8 t/h dry) at 7 % moisture, feed PSD = CR.5009 product curve (engine reference P80 42.7 mm); rain case = same feed with the vendor's wet-screening derating (engine reference factor 0.75 [H], to be confirmed by the vendor for these apertures).

## 5. FMECA-derived purchase requirements

| FM (RPN) | Failure mode | Purchase requirement |
|---|---|---|
| SR.5007-FM1 (**210 — CRITICAL**) | Panel wear / aperture growth (KFS envelope breach) | **Quick-change modular panel system** on both decks; **one full spare panel set per deck** in the initial spares; **safe aperture-gauging access** (walkway/door allowing monthly gauging without full stripping); wear-resistant panel compound stated for 300+ t/h limestone duty |
| SR.5007-FM3 (140) | Exciter bearing failure | **Exciter bearing condition-monitoring provision** (mounting pads or built-in sensors for the quarterly vibration route); spare exciter cartridge in the spares list; grease schedule stated |
| SR.5007-FM5 (126) | Structural crack | Bolted (not welded) deck-frame construction at the known hot spots or vendor fatigue calculation supplied; panels liftable for the annual NDT |
| SR.5007-FM2 (120) | Blinding / pegging (wet 20 mm deck) | Anti-blinding panel option (or demonstrated self-cleaning geometry) for the wet sticky 250 t/h feed; wash-down access |
| SR.5007-FM4 (100) | Support spring / mount failure | Springs replaceable in sets; corner stroke/orbit measurement points |

## 6. Open [H] items the vendor must close

- **[H] Imperfection I = 0.15** (literature): the vendor must guarantee a screening efficiency / imperfection at the stated duty, backed by its sizing method; a KFS product sieve test at commissioning re-fits the model value.
- **[H] +25 % area margin**: vendor to verify areas by its own method (value table with declared interpolation mode — golden rule 3) at the stated feed PSD and moisture.
- `installed_area_m2` is null in the data — the purchased deck areas close it.

## 7. Acceptance tests and QC criteria

1. **KFS envelope acceptance**: screen product 20/35 must meet the KFS envelope — max 30 % below cut, min 55 % in cut, max 15 % above cut — at 324.5 t/h wet feed (engine-verified compliant at the reference settings, in-cut 82.7 % on the converged grid).
2. **Efficiency test**: measured imperfection at duty ≤ the vendor guarantee (sieve analysis of all three streams, mass balance closed).
3. **Capacity**: sustained worst-mode feed with no bed-depth alarm and no quality drift over 2 h.
4. Stroke/orbit baseline on four corners + exciter vibration baseline at commissioning.
5. Panel change demonstration: one panel exchanged within the vendor-stated time using the quick-change system.

---
*Engine provenance: commit 5dc5b53, run 2026-08-15, `wankoe_model.scenario.run_scenario` (per-mode photos 1A / forced 1B, weather dry), data `data/default_parameters.json`. Replay: `PYTHONPATH=src python scripts/purchase_datasheet_evidence.py` -> `docs/purchase/purchase-engine-evidence.json`. The +25 % area margin is an assistant-stated sizing hypothesis [H]. Produced by NOEZYS.*
