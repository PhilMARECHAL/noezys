# Machine-Selection Error Hunt — Adversarial Verification Report

**by NOEZYS** — 2026-08-15

## 1. Purpose

Client challenge (2026-08-15): *"It is impossible that there is no error in the
calculation. [...] The objective is to buy the right machines that will do the
job in all circumstances. We have no right to error."*

The client is right. The 2026-08-14 confidence program covered **zone 1.1
only**; everything built after it (two-mode planning, auto mode-1B, OPEX,
FMECA, the 13 purchase datasheets, the soft-rock and rain studies) was built
fast and had never been adversarially verified. This hunt targets exactly one
question: **is every one of the 13 purchase machines sized for its true worst
case, across ALL circumstances?**

## 2. Method

Four independent adversarial auditors, each instructed to FIND errors (not to
certify) and forbidden to claim anything without executing the engine:

1. **Worst-case duty audit** — 24-run full mode matrix (dry/rain × 1A/1B ×
   2A/2B/2C × G/F) + rain-week moistures (12/15/11 %) + soft-rock envelope
   (UCS 15–30) + adopted quarry-target curve + RC.2 gap-drift sweep.
2. **Independent planning re-derivation** — every hour and tonnage of
   `run_required_hours` re-derived by hand from per-mode engine rates.
3. **Datasheet traceability audit** — every number of the 13 sheets traced to
   its engine source; evidence JSON regenerated and diffed (zero numeric drift).
4. **Physics/numerics audit** — hand anchors on M1–M8, unit checks (Bond
   µm, JKMRC v in m/s), mass/water conservation to machine precision, loop
   convergence residuals, grid-refinement sweeps.

Every headline finding was then **counter-verified by a fifth, independent
reproduction** before entering this report (reproduction script:
`counter_verify.py`, session scratchpad; all commands below re-runnable).

## 3. What is CONFIRMED SOUND (so the findings below are read in context)

- The **current purchase basis at the adopted reference point reproduces by
  hand to the tonne**: all zone hours (1 366.6 / 2 428.3 / 3 610.5 h), the 2C
  campaign 67 856 t, landfill 13 816 t, KFS Yield 24.88 % / required 25.93 % —
  independently re-derived from per-mode engine rates. No arithmetic error in
  the adopted plan.
- **Transcription fidelity is excellent**: the evidence JSON regenerates
  byte-identical (except provenance stamp); all 60 quoted FMECA rows match the
  register; every duty number on the sheets traces to its source.
- **The physics is implemented as specified**: Bond exact in microns (no
  mm/µm slip), JKMRC `Ecs = v²/7200` dimensionally exact for v = 30 m/s,
  M1 monotone/truncation exact, dryer water closure at 2.6e-15, per-unit dry
  mass conserved exactly, loop non-convergence DOES alert (no silent exit).

**The errors are not in the arithmetic. They are in WHICH circumstance each
machine was sized on.** The sizing rules ("worst engine mode + 25 %" areas,
"worst absorbed × 1.15" motors) were applied over **dry-weather,
measured-curve, 1A-upstream photos only** — while the client's own same-day
rulings (rain set, soft rock, quarry-target curve) and cross-zone couplings
(1B upstream) move the worst case for at least six machines.

## 4. Findings — CHANGES-PURCHASE-DECISION

| ID | Machine | Finding (engine-verified, counter-verified) |
|----|---------|---------------------------------------------|
| **PD-1** | **CR.5011** | Mode-1B feed 186.1 t/h wet was bisected on the MEASURED curve. On the **adopted quarry-target curve** the loop hits **97.1 t/h wet > the 90 t/h wet vendor guarantee point** (+7.9 %). Alert fires in-engine. Either the 1B feed is re-bisected for the quarry curve (~172 t/h) or the purchase capacity is restated. Repro: quarry curve + `zone_1_1_mode: 1B`. |
| **PD-2** | **SR.5007** | Purchase minima (≥ 8.5 / 8.9 m²) were computed on DRY photos. In **rain** — a normal circumstance (25 % season, and the client ruled the line RUNS through rain weeks) — required areas are **9.07 / 9.53 m²** (7 % moisture) and **8.58 / 9.02 m²** (12 % rain-week set): **above the purchase minima on both decks**. The +25 % margin is fully consumed by the 1/0.75 wet derating. A screen bought at the sheet minimum is undersized. |
| **PD-3** | **SP.36 fan (CL.38 circuit)** | Datasheet fan reference 207.2 m³/h (mode F, defaults). Under the **client-ruled soft-rock envelope** the engine gives **332.3 m³/h (central UCS 20)** up to **~416 m³/h (UCS 15)** — soft rock doubles the natural fines below the 65 µm cut. No engine cap exists (`max_airflow_m3h` null), so no alert can fire. A fan bought on 207 m³/h is undersized across most of the ruled envelope. |
| **PD-4** | **RC.2** | The mode-F operating point (feed 25.05 t/h wet, load 43.99 vs 2×22 = 44 installed) is encoded at **exactly 100 % of capacity on the ×2 grid** — and the ×2 grid is NOT converged for THIS output: ×3 → 44.3, ×4 → 44.4 t/h (**bottleneck alert fires on finer grids**). The grid-convergence criterion (KFS Yield < 0.05 pt) checked the wrong output. On top: zero gap-drift allowance (gap 1.6 mm → 44.95 t/h, over spec at the first 0.1 mm of drift), 1B-upstream coupling → 44.2 t/h, and ±10 % on the untested `comp_lam` [H] swings the load ±7.5 %. The point needs headroom or a lower mode-F feed. |
| **PD-5** | **CR.5113** | The sheet's 450 kW motor branch omits the same-day soft-rock ruling **"hold the motor order"** (soft-rock study: 2C absorbed 348 → 211 kW at UCS 20, rec 450 → 250 kW). Also, its stated "worst 2C absorbed" 348.1 kW is not the worst: **359.5 kW** on the quarry curve (450 kW still covers). An order placed off the sheet risks an ~80 % oversized drive. |
| **PD-6** | **CR.5009** | Standing nip finding worsens on the adopted quarry curve: **F80 251 mm > 150 mm max nip** (was 181 on the measured curve). The quarry works spec, as encoded, INCREASES the top size this purchase must resolve. (The sheet also claimed UCS 20–80 MPa — corrected this commit to the ruled 15–30.) |

## 5. Findings — MATERIAL (margin erosion / corrupted sensitivity branches)

| ID | Where | Finding |
|----|-------|---------|
| M-1 | SC.B (+ SR.5111/SR.5115 fine cuts) | Model M4 omits every VSMA feed-composition factor (half-size, oversize, deck position); the fitted f0 = 0.347 happens to match at SR.5007-like feeds but SC.B's 17–20 % half-size feeds demand **~30 % more area by the standard factor method** (5.4/3.5 m² vs modeled 4.0/2.6). The +25 % [H] purchase margin is entirely consumed by this bias on the RPN-252 critical screen. |
| M-2 | SR.5115 | Stated minimum 19.1 m² was computed on a non-worst circumstance; worst 2C case (quarry curve + 1B upstream) gives 15.72 m² → ×1.25 = **19.65 m²** > 19.1 (~3 % under its own sizing rule). |
| M-3 | planning.py rain-capped branch | When a zone-1.2 capacity cap binds, zone-1.3 hours are recomputed with the mode-G rate only: the plan then reports **100 284 t of product from 84 780 t of dry feed** (mass-impossible) with an internally contradictory hours split. Does NOT fire at the adopted reference point; corrupts any capped sensitivity scenario used for margin studies. No test covers the branch. |
| M-4 | planning.py 2C seasonality | 2C hours are checked against the FULL-YEAR ceiling, but 2C (1.7 mm loop) is dry-season-only (rain forces 2B — client physics ruling). Demonstrated: a scenario with the dry season saturated still schedules 452 h of 2C and reports the AgLime market served. Fine at defaults (2 428 h < 4 500 h dry cap); silently wrong in sizing scenarios. |
| M-5 | planning.py alert propagation | Only DRY-photo alerts reach the plan: the 2C conveyor overload (100 > 60 t/h wet) and the 1B CR.5011 bottleneck are invisible in the planning deliverable for exactly the hours it schedules (679 h/y 2C). Corroborated elsewhere, but the plan document contradicts the standing findings. |
| M-6 | DY.03 burner [PLAUSIBLE — vendor rating needed] | Engine burner duty at rain-week moistures: **5.2–6.7 MW** vs the ~3.7 MW class assumed in `electrical_loads`. `installed_burner_kW` is null so no alert can fire. If the acquired burner is 3.7 MW-class, the rain-week throughput claims are thermally unreachable. Machine is already acquired (not in the 13) — but rain-week conclusions depend on its real rating. |

## 6. Findings — COSMETIC (objective errors, FIXED IN THIS COMMIT)

| ID | Where | Error → fix |
|----|-------|-------------|
| C-1 | RC.2.md (×3), SC.B.md | The 147 t/h runaway circulating load was attributed to **gap 1.5** ("engine-proven; at 2.8 mm the loop runs away") — **INVERTED**. Engine: gap 1.5 → 44.0 t/h; gap 2.8 → 172.8 t/h runaway (147 was the old 21.3 t/h-feed figure). A vendor would have priced wear guarantees at 3.3× the real duty. Fixed. |
| C-2 | SR.5111.md, INDEX.md, evidence script | Loop overload stated as **155 %** = DRY ratio (93/60) mislabeled as wet; the engine's own alert is WET: 100/60 = **167 %** (client total-flow rule). Script fixed, evidence regenerated, sheets corrected. This was the exact wet/dry blind-spot class the 2026-08-14 audit fixed on CR.5011, reintroduced. |
| C-3 | SP.36.md, CL.38.md | Stale UltraFin duty 0.99 t/h (pre-C1 as-built) → actual 0.067 (G) / 0.104 (F) t/h. Fixed. |
| C-4 | CR.5009.md | "UCS 20–80 MPa" vs client-ruled envelope 15–30 (ref 20). Fixed. |
| C-5 | scenario.py:455 | Mode-F period photos book FeedLime consumption at the mode-G rate (+28 % phantom stockpile draw in single photos; annual plan unaffected — planning handles the split correctly). Fix scheduled with M-3/M-4. |
| C-6 | Various | RC.1 quarry-curve duty 30.12 t/h (doc says 29.7; 32 t/h rating still covers, margin 5.9 % not 7.2 %); CR.5011 1B bisected point sits at 90.02 t/h on the ×2 grid (89.99 converged) so its own alert fires at the design point; two purchase minima rounded DOWN (SR.5007 bottom 8.9 vs 8.94, SC.B deck-2 5.6 vs 5.64); test_planning tautological stock-balance assertions; stale test comments. |

## 7. Verified clean (worst duty vs purchase rating, all circumstances tested)

SR.5105 (max 3.38 m² < 3.8; never runs in rain — 2B bypasses it), SC.A
(4.79/5.60 < 6.0/7.0 everywhere), SC.B areas vs its own model (mass-pinned
mode-F case verified, subject to M-1), RC.2 motors (24.3 < 30 kW/unit),
RC.1 rating (covers all circumstances tested), CL.38 d50 (geometry-invariant),
CR.5113 450 kW branch (covers 359.5 kW worst), 2B-fed zone 1.3 (LOWERS all
zone-1.3 duties — not a hidden worst case).

## 8. Consequence for the purchase — honest summary

- **No machine of the 13 was bought wrong at the adopted reference point** —
  the reference arithmetic is error-free and reproduces by hand.
- **Six machines (PD-1…PD-6) have a circumstance, already ruled by the client,
  in which the sheet as written under-buys or mis-buys**: CR.5011 (quarry
  curve × 1B), SR.5007 (rain), SP.36 fan (soft rock), RC.2 (grid bias + drift
  + comp_lam at a 100 %-encoded point), CR.5113 (soft-rock hold omitted),
  CR.5009 (quarry curve top size).
- The sensitivity machinery (planning capped branches) has bugs (M-3/M-4/M-5)
  that must be fixed before any further margin study is trusted.
- The external tests already registered remain the arbiters where flagged:
  drop-weight A·b (PD-3, PD-5), vendor gradation (PD-4 comp_lam), absorption
  test (M-6 moistures), sieve test (M-1 imperfection).

## 9. Client arbitrations required (to be asked one at a time)

1. **PD-1 / CR.5011**: re-bisect the 1B feed on the quarry curve (~172 t/h,
   longer 1B hours) — or raise the purchased capacity point — or gate on the
   vendor gradation test.
2. **PD-2 / SR.5007**: raise the purchase minima to the rain duty
   (9.1/9.6 m² before margin) — or accept a derated rain throughput.
3. **PD-3 / SP.36 fan**: buy the fan for the soft-rock envelope (~420 m³/h
   with damper turndown) — or hold for the drop-weight test.
4. **PD-4 / RC.2**: add a capacity step (e.g. 2 × 25 t/h) — or lower the
   mode-F feed (~24.5 t/h wet, longer F campaigns) — re-bisect on ×4 grid
   either way.
5. **M-1 / SC.B family**: re-quote fine-screen areas with the full VSMA
   factor string — or enlarge the margin explicitly.
6. **M-3/M-4/M-5/C-5 code fixes**: no arbitration needed — scheduled next.

---
*Engine-run provenance: wankoe_model @ e6541dd + this commit,
`data/default_parameters.json` defaults unless stated; grid refinements ×2/×3/×4
as noted; 4 independent audit agents + 1 counter-verification pass, 2026-08-15.
All reproduction overrides quoted inline. 144/144 repo tests pass — none of the
findings above were covered by an existing test (that is itself finding-grade
input to the test plan).*
