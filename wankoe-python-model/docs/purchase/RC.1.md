# PURCHASE TECHNICAL DATASHEET — RC.1

**Smooth double-roll crusher, stage 1 — zone 1.3 (C1 reference configuration)**
Issued 2026-08-15 (client order of the same day: purchase datasheets for the 13 major process machines) — produced by NOEZYS.

## 1. Identification and role

| Item | Value |
|---|---|
| Tag | RC.1 |
| Type | Smooth double-roll crusher, stage 1 (C1 adopted 2026-08-14; replaces ML.26) |
| Zone / duty | 1.3 — first crushing stage of the dry FeedLime 6/20 (post-dryer) |
| Operating modes | G (grits), F (fines campaign) |
| Annual running hours (defaults) | 3 610.5 h effective (2 466 h G + 1 144 h F) |
| Criticality | **Single unit — chain-critical** for the whole zone-1.3 dry chain |

## 2. Process duty (engine runs, 2026-08-15)

Zone 1.3 rates are DRY basis (post-dryer, 0.5 % outlet moisture; capacity basis "dry" per the 2026-08-14 audit).

| Quantity | Mode G | Mode F |
|---|---|---|
| Throughput | 29.2 t/h (**91.3 % of the 32 t/h rating**) | 22.8 t/h (71.3 %) |
| Feed F80 | 16.4 mm | 16.4 mm |
| Product P80 | 7.7 mm | 7.7 mm |
| Specific energy W | 0.448 kWh/t | 0.448 kWh/t |
| Absorbed power (P_net / eta_m 0.75) | 17.4 kW | 13.6 kW |

## 3. Settings and required adjustability

| Parameter | Unit | Range required | Reference setting |
|---|---|---|---|
| Gap g | mm | 6.0 - 10.0 (step 0.5) | 8.0 |
| Compression lambda | - | 1.8 - 2.8 | 2.2 **[H]** |
| RR slope n_comp | - | 1.5 - 2.2 | 1.8 **[H]** |
| Attrition S_att | - | 0.03 - 0.10 | 0.06 **[H]** |

lambda / n_comp / S_att are MODEL coefficients [H], not machine settings — they are what the vendor gradation test fixes (section 6).

## 4. Capacity and sizing requirements (client-decided)

- **Capacity 32 t/h dry — CLIENT PURCHASE SPEC (2026-08-14)**, closing the D4 quarry-feed finding: covers the full-dryer extension on BOTH feed curves (measured 28.9 t/h, quarry-target 29.7 t/h; panel sizing was 29 t/h and was exceeded on the quarry variant). Mode G already runs at 91.3 % of this rating — the 32 t/h figure is firm, not negotiable downward.
- **Motor**: worst-mode absorbed 17.4 kW; recommended minimum installed rating **22 kW** (x1.15 allowance [H], next IEC size; vendor to confirm). `installed_power_kW` null in the data — vendor value closes it.
- Extension provision (D1): sizing for the deferred 2nd-RC.2/BC.22 retrofit is a design-basis recommendation — vendor to state the machine's margin above 32 t/h.

## 5. FMECA-derived purchase requirements

| FM (RPN) | Failure mode | Purchase requirement |
|---|---|---|
| RC.1-FM1 (144) | Roll surface wear / corrugation | **Roll surface wear specification**: shell material/hardness stated for abrasive dry limestone, guaranteed surface life or regrind interval at the 29.2 t/h duty; rolls regrindable ON SITE or exchangeable as cartridges (mode G leaves only 8.7 % capacity margin — wear directly erodes the chain rate) |
| RC.1-FM3 (140) | Roll bearing failure (single-unit chain stop) | **Bearing temperature + vibration monitoring wired at purchase** (trend alarms; quarterly route); grease schedule; bearing life stated at 91.3 % load, 3 610 h/y |
| RC.1-FM2 (100) | Gap drift / setting failure | **Gap-drift instrumentation**: position feedback on the movable roll, readable setting repeatable to 0.5 mm, drift alarm; weekly gap verification without dismantling |
| RC.1-FM4 (72) | Drive / coupling failure | Spare coupling element; yearly gearbox service access |
| (EM.09 chain) | Tramp metal reaching smooth rolls | The dryer-feed metal detector + belt magnet EM.09 PROTECTS this machine (hidden-failure class, FMECA EM.09-FM1 RPN 196): the RC.1 purchase must state the max tolerable tramp size/hardness so the EM.09 detection threshold can be set; roll-gap overload release (spring/hydraulic) required as the last line of defense |

## 6. Open [H] items the vendor must close — VENDOR GRADATION TEST (REQUIREMENT)

- **The smooth-roll gradation test on WANKOE 6/20 is a PURCHASE REQUIREMENT, not an option** (golden rule 2 — vendor curve slot `product_curve_table` is null): it **fixes n_comp and S_att [H]**, on which hang (a) the grits D6 envelope margin of only **0.8 pt**, and (b) the whole C1 mass balance. Deliverable: product PSD value tables at gaps 6-10 mm WITH the declared interpolation mode, on the real 6/20 dried material.
- **[H] lambda 2.2 / n_comp 1.8 / S_att 0.06** — replaced by the test above.
- **[H] Motor sizing allowance x1.15** — vendor drive selection governs.
- Installed power and roll dimensions (data slots null).

## 7. Acceptance tests and QC criteria

1. **Gradation acceptance = the vendor test of section 6**, witnessed, on WANKOE material; model re-fit follows (data-first: coefficients land in `data/default_parameters.json`, engine replays the C1 balance before shipment is accepted).
2. **Capacity test**: 32 t/h dry sustained 2 h at gap 8.0 — no overload-release actuation, product P80 consistent with 7.7 mm.
3. **Downstream QC tie-in**: grits D6 envelope (< 2 mm <= 15 %, > 4 mm <= 5 %) and fines 0/1.5 spec measured at SC.B after the loop — the RC.1 product curve must keep both reachable.
4. Bearing temperature/vibration baselines; gap-instrumentation calibration; overload-release function test.

---
*Engine provenance: commit 5dc5b53, run 2026-08-15, `wankoe_model.scenario.run_scenario` (per-mode photos G / F, weather dry), data `data/default_parameters.json`. Replay: `PYTHONPATH=src python scripts/purchase_datasheet_evidence.py` -> `docs/purchase/purchase-engine-evidence.json`. Produced by NOEZYS.*
