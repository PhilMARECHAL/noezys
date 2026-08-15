# PURCHASE TECHNICAL DATASHEET — CR.5011

**Impact crusher, zone-1.1 closing loop (HAZEMAG AP-S 1010 class)**
Issued 2026-08-15 (client order of the same day: purchase datasheets for the 13 major process machines) — produced by NOEZYS.

## 1. Identification and role

| Item | Value |
|---|---|
| Tag | CR.5011 |
| Type | Impact crusher (reference class: HAZEMAG AP-S 1010 — Q8 closed 2026-08-11 on machine documents) |
| Zone / duty | 1.1 — closes the 0/20 loop (20/40 recycle re-crushing); without it zone 1.1 cannot make spec 0/20 |
| Operating modes | 1A; 1B (0/20 stock campaigns at the 90 t/h wet limit) |
| Annual running hours (defaults) | 1 366.6 h effective |
| Criticality | Chain-critical single unit |

## 2. Process duty (engine runs, 2026-08-15)

| Quantity | Mode 1A | Mode 1B |
|---|---|---|
| Throughput, wet (vendor basis) | 74.5 t/h (**83 % of the 90 t/h limit**) | **83.2 t/h measured curve / 89.7 t/h quarry-target curve — binding case, 0.3 t/h under the guarantee** (re-bisected feed 172.0 t/h, client 2026-08-15) |
| Throughput, dry solids | 69.3 t/h | 77.4 t/h (measured curve) |
| Feed F80 | 63.0 mm | 55.6 mm |
| Product P80 | 29.3 mm | 17.7 mm |
| CSS (x80 setting) | 30 mm | **18 mm** (mode-1B setting, client 2026-08-14) |
| Specific energy W | 0.233 kWh/t | 0.412 kWh/t |
| Absorbed power (P_net / eta_m 0.75) | 21.5 kW | 42.5 kW (measured curve, feed 172.0) |
| Installed motor (vendor docs) | 132 kW | 132 kW |

## 3. Settings and required adjustability

| Parameter | Unit | Range required | Reference setting |
|---|---|---|---|
| Rotor speed v | m/s | 30 - 60 | **30** (client 2026-08-14 — minimum speed, landfill headroom) |
| CSS (x80) | mm | 10 - 30 | 30 (mode 1A) / **18 (mode 1B)** — operations switch CSS with the mode |

The CSS must be changeable between 30 and 18 mm as a ROUTINE OPERATION (mode changeover), not a workshop intervention.

## 4. Capacity and sizing requirements (client-decided)

- **Capacity 90 t/h WET, vendor as-fed basis** (client-decided rating; audit 2026-08-14: vendor tonnages are wet). Nominal 100 t/h, real 75-90 t/h on limestone per the AP-S 1010 documents — the purchase must GUARANTEE **90 t/h wet sustained at CSS 18 mm** (the mode-1B operating point; client decision 2026-08-15, error-hunt PD-1: the 1B line feed is bisected on the ADOPTED QUARRY-TARGET CURVE at 172.0 t/h wet, putting this machine at 89.7 t/h wet on the quarry curve / 83.2 on the measured curve, grid-robust x2-x4 — the guarantee holds in all circumstances; supersedes the 186.1 t/h measured-curve bisection, which exceeded the guarantee at 97.1 t/h on the quarry curve).
- Max feed size 400 mm class (recycle 20/40 — large margin); capacity bound by the rotor, not the motor.
- **Motor**: 132 kW per the reference machine documents; worst-mode absorbed 42.5 kW (1B, measured curve; ~46 kW-class at the quarry-curve binding point) — the 132 kW rating is amply confirmed.

## 5. FMECA-derived purchase requirements

| FM (RPN) | Failure mode | Purchase requirement |
|---|---|---|
| CR.5011-FM2 (144) | Blow bar breakage / detachment | **Blow-bar metallurgy specified for limestone with tramp risk** (no zone-1.1 metal detection exists today — see the EM.09-adjacent design recommendation on CR.5009): bar grade with crack-tolerant backing; bar fixation system torque-checkable; dye-check compatible bar geometry |
| CR.5011-FM4 (140) | Main bearing failure | Bearing temperature + vibration monitoring provision (quarterly route); grease schedule; dynamic loads stated for the 90 t/h wet 1B duty |
| CR.5011-FM3 (120) | Rotor imbalance / disc wear | **Rotor balance specification**: vendor balancing grade stated; on-site balancing acceptance after every bar change must be possible (provision for trim weights or bar-set matching by weight); annual rotor inspection access |
| CR.5011-FM1 (105) | Blow bar wear | Bar rotation/turning pattern documented; **2 full bar sets** in the initial spares; wear gauging datum marks |
| CR.5011-FM5 (96) | Apron / liner wear | Liner thickness check points; liners exchangeable with bar campaigns |

## 6. Open [H] items the vendor must close

- **Capacity at CSS 18**: the 90 t/h wet real capacity is documented at standard settings — the vendor must CONFIRM it at the mode-1B CSS 18 mm (open purchase item; the auto-mode-1B rule depends on it).
- **[H] Vendor product curves**: gradation tables at CSS 10-30 mm and v 30-60 m/s on WANKOE limestone, as value tables with declared interpolation mode (golden rule 3) — confirms the M5 (t10/Ecs) model and the expert-book CR.5011 capacity question.
- **[H] A = 60 / b = 0.80** breakage parameters pending drop-weight tests — vendor to state its own basis for power/gradation guarantees.

## 7. Acceptance tests and QC criteria

1. **Capacity test at the 1B point**: 90 t/h wet sustained 2 h at CSS 18, v 30 — no rotor stall, product P80 consistent with 17.7 mm (engine reference).
2. **Mode-changeover demonstration**: CSS 30 -> 18 -> 30 within the vendor-stated changeover time.
3. **Gradation acceptance**: product curve at CSS 30 / v 30 within vendor table tolerance; downstream QC tie-in = the 0/20 product spec (loop closure at 20 mm).
4. **Balance acceptance**: vibration below the vendor grade after a witnessed bar change.
5. Absorbed-power check against the guarantee (engine references 21.5 kW 1A / 42.5 kW 1B at feed 172.0).

---
*Engine provenance: commit 5dc5b53, run 2026-08-15, `wankoe_model.scenario.run_scenario` (per-mode photos 1A / forced 1B, weather dry), data `data/default_parameters.json`. Replay: `PYTHONPATH=src python scripts/purchase_datasheet_evidence.py` -> `docs/purchase/purchase-engine-evidence.json`. Produced by NOEZYS.*
