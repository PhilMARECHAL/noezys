# PURCHASE TECHNICAL DATASHEET — CR.5113

**Impact crusher, AgLime loop — zone 1.2**
Issued 2026-08-15 (client order of the same day: purchase datasheets for the 13 major process machines) — produced by NOEZYS.

## 1. Identification and role

| Item | Value |
|---|---|
| Tag | CR.5113 (ex-CR.5107, renamed 2026-08-12 per PFD REV18) |
| Type | Impact crusher, fine-grinding duty |
| Zone / duty | 1.2 — AgLime loop crusher (open SR.5111 + closed loop with SR.5115) |
| Operating modes | 2A (co-production), 2C (AgLime campaigns, 678.6 h/y at defaults) |
| Annual running hours (defaults) | 2 428.3 h effective |
| Criticality | **SINGLE POINT of the AgLime loop** (135 kt/y served incl. 2C campaigns) |

## 2. Process duty (engine runs, 2026-08-15)

Total-flow rule: wet basis primary (wet = dry x 1.07527).

| Quantity | Mode 2A | Mode 2C |
|---|---|---|
| Throughput, wet | 30.2 t/h | **92.5 t/h** (loop equilibrium 86.0 t/h dry) |
| Throughput, dry solids | 28.1 t/h | 86.0 t/h |
| Feed F80 | 5.2 mm | 14.6 mm |
| Product P80 | 0.95 mm | 0.95 mm |
| Specific energy W | 2.34 kWh/t | 3.04 kWh/t |
| Absorbed power (P_net / eta_m 0.75) | 87.4 kW | **348.1 kW** |

## 3. Settings and required adjustability

| Parameter | Unit | Range required | Reference setting |
|---|---|---|---|
| Rotor speed v | m/s | 30 - 60 | 40 |
| CSS (x80) | mm | 1.0 - 3.0 (step 0.1) | 1.0 |

## 4. Capacity and sizing requirements — MOTOR FINDING (CRITICAL)

**Engine standing finding (OPEX 2026-08-15, FMECA rank 3, RPN 224): the 2C campaign duty absorbs ~348 kW — 4x the 2A duty (~87 kW).** A motor sized on the 2A class would run in continuous overload for every 2C hour. The purchase must adopt ONE of the two branches, stated explicitly in the offer:

1. **Motor sized for the 2C campaign duty**: worst-mode absorbed 348.1 kW; recommended minimum installed rating **450 kW** (x1.15 service allowance [H], next IEC size — vendor to confirm from its drive selection and its own power estimate at the stated duty); or
2. **Capped campaign rate**: the 2C loop rate is limited so absorbed power stays within a smaller installed motor, and the vendor states the guaranteed continuous t/h at that rating — planning then re-derives the campaign hours (2C hours increase; the engine can replay the trade-off before ordering).

`installed_power_kW` is currently null in the data — the vendor value closes it. Throughput rating: 92.5 t/h wet continuous (branch 1) at the loop equilibrium.

## 5. FMECA-derived purchase requirements

| FM (RPN) | Failure mode | Purchase requirement |
|---|---|---|
| CR.5113-FM1 (**224 — CRITICAL**) | Motor overload / winding burnout in 2C | Motor per section 4 branch 1 or 2; **winding temperature sensors (PT100/PTC) in all phases wired to trend alarms**; thermal image relay; annual insulation-test point; motor thermal class stated for 678.6 h/y campaign duty |
| CR.5113-FM3 (150) | Rotor imbalance / bar breakage | Rotor balance grade stated; vibration acceptance after every bar change possible on site; annual rotor inspection access |
| CR.5113-FM4 (150) | Main bearing failure | **Bearing temperature + vibration monitoring wired at purchase** (trend alarms — dynamic loads at the 86 t/h 2C equilibrium); grease schedule |
| CR.5113-FM2 (120) | Blow bar wear (fine-grinding duty) | Bar metallurgy for fine limestone grinding; bar gauging at every campaign changeover; **2 bar sets** in initial spares; motor-current trend usable as wear proxy (current signal exposed to the control system) |

## 6. Open [H] items the vendor must close

- **Installed motor rating** (section 4) — the single most important open item of this purchase.
- **[H] Vendor product/power curves** at CSS 1-3 mm on WANKOE limestone 0/6-0/20 feed, as value tables with declared interpolation (golden rule 3) — the ~348 kW engine figure (M5 t10/Ecs + Bond family) must be confronted with the vendor's own estimate before the motor is fixed.
- **[H] A = 60 / b = 0.80** breakage parameters pending drop-weight tests.

## 7. Acceptance tests and QC criteria

1. **2C duty test**: sustained loop-equilibrium duty (92.5 t/h wet, CSS 1.0, v 40) for 4 h — winding temperatures within class, absorbed power ≤ guarantee.
2. **Product acceptance**: crusher product P80 consistent with 0.95 mm; end criterion = AgLime >= 95 % < 1.7 mm at the loop output (SR.5115 undersize + SR.5111 undersize).
3. **Balance acceptance** after a witnessed bar change.
4. Baselines: bearing vibration/temperature, motor current signature at both duty points (2A and 2C).

---
*Engine provenance: commit 5dc5b53, run 2026-08-15, `wankoe_model.scenario.run_scenario` (per-mode photos 2A / 2C, weather dry), data `data/default_parameters.json`. Replay: `PYTHONPATH=src python scripts/purchase_datasheet_evidence.py` -> `docs/purchase/purchase-engine-evidence.json`. Motor x1.15 allowance is an assistant-stated sizing hypothesis [H]. Produced by NOEZYS.*
