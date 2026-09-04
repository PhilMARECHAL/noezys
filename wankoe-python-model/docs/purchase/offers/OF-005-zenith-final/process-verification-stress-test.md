# OF-005 pre-order process verification — full stress test (2026-09-04)

**by NOEZYS** — client mission 2026-09-04 ("complete process
verification: will this machine generate the quality for every
envisaged scenario?"), test matrix approved by the client (option 1),
executed same day. Evidence: [stress-test-evidence.json](stress-test-evidence.json)
(37 engine runs), replay: `PYTHONPATH=src python scripts/of005_stress_test.py`.
Machines under test, as printed in OF-005: **2PG-1216CT** (400 t/h max,
feed 0–300 mm, 2×180 kW) and **S5X2760-2** (2 decks, 16.2 m²/deck).

## 1. Verdict on the client's question

**Quality: YES — engine-proven on every scenario.** The KFS 30/55/15
envelope is COMPLIANT in all 20 envelope-bearing runs, spanning: both
quarry-band edges (45.5 % and 40.1 % < 20 mm) and beyond (homothetic
k 0.70 fine / k 1.60 coarse extremes), the full 20–60 mm setting
window, the entire plausible product-shape range of the crusher
(n 1.0 → 1.8), the soft-rock coefficient scenario, and the rain week.
Worst envelope seen: 21.2 % below / 78.8 % in cut / 0.1 % above
(g = 20 mm, quarry curve) — still inside 30/55/15. The quality is
structurally protected by the screen; the crusher's product-shape
uncertainty does not break it anywhere.

**The purchased machines pass every machine-side gate in every run:**
crusher throughput 250 t/h wet ≤ 400 (62 % worst); absorbed power
max 226.9 kW (at g = 20, coarse curve) ≤ 360 kW installed (63 % worst
— the drive covers even the tightest setting); screen required areas
max 9.2 m²/deck under RAIN derating ≤ 16.2 offered (57 % worst).

**The stress limit found is NOT in the Zenith machines — it is the
existing CR.5011 loop crusher rating (90 t/h wet), in mode-1B
worst-case crossings** (see §3).

## 2. Results by family (37 runs)

| Family | Runs | Result |
|---|---|---|
| S1 reference 1A (measured, g60) | 1 | PASS — env 8.8/82.3/8.9, loop 74.1/90 |
| S2 mode 1B (172 t/h, CSS 18) | 2 | PASS — loop 82.5 (measured) / **89.1 (quarry) = 99 % of rating, razor-thin** |
| S3 quarry-target 1A (40.1 % < 20) | 1 | PASS — env 8.8/83.2/8.0 |
| S4 granulometric extremes k 0.70 / 1.60 | 3 | 1A both PASS; **1B at k 1.60 FAIL: loop 91.9/90** (beyond the ruled quarry band — the acceptance band 40.1/45.5 protects it) |
| S5 setting window g 20/30/40/50/60 × 2 curves | 10 | **ALL PASS** incl. quality — every point of the 20–60 window is operable and in-envelope; power max 226.9 kW at g20 |
| S6 crusher shape n 1.0–1.8 × 2 curves (1A) | 10 | **ALL PASS** — envelope robust to the machine's real gradation; loop rises with n (86.3/90 at n 1.8 quarry) |
| S7 soft-rock scenario (1A ×2, 1B) | 3 | PASS — loads DROP (loop 68.6–82.9) |
| S8 rain week (12 % feed, wet screening) | 1 | PASS — derated areas 8.6/9.2 ≤ 16.2 |
| S10 worst-case crossings (added in-run, honesty supplement) | 6 | **1B × adverse shape FAILS the loop**: n 1.8 measured → 91.6; n 1.6 quarry → 95.4; n 1.8 quarry → 99.6 (vs 90). Rain×n1.8 1A PASS; soft 1B PASS |

## 3. The one real finding — and what it means for THIS order

In stock-campaign mode 1B, everything (including the 20/35 cut) goes
round the CR.5011 loop. If the 2PG's REAL product curve is flatter than
our n = 1.35 hypothesis (more uniform product, less fines), the loop
load rises: above n ≈ 1.55 on quarry-coarse feed, the CR.5011 90 t/h
wet vendor rating is exceeded at the ruled 172 t/h 1B feed.

- This is **not a defect of the Zenith machines** — they pass their own
  gates in every run. It is the known tightness of the loop machine
  (the PD-1 re-bisection logic), now quantified against the crusher's
  shape uncertainty.
- **Mechanical mitigation exists and is already ruled**: the auto-1B
  feed is a parameter — re-bisect it downward (or raise CSS) once the
  real curve is known. Cost: slower 1B campaigns, zero quality impact.
- **Consequence for the order**: the vendor's CONTRACTUAL GRADATION
  CURVE (clarification Q2) is not paperwork — it is the input that
  decides the 1B operating point. It must be a hard deliverable.

## 4. Analytical machine-limit gates (S9)

| Gate | Verdict |
|---|---|
| Setting window 20–60 mm vs printed "40–800" | **FAIL AS PRINTED — condition precedent.** S5 proves the duty uses the window and the drive covers it; the vendor must confirm 20–60 in writing (or correct the sheet) before any order |
| Feed top size: H-FEED-2 tail ~2.9 % > 300 mm (top 320) vs printed "0–300" | **CONTRACTUAL/OPERATIONAL** — vendor accepts 320 mm in writing, OR the quarry primary guarantees 0–300 (grizzly/setting). To be settled before order |
| Power 2×180 kW vs Bond ~97 kW (reference) | PASS — ~3.7× margin |
| Screen mesh range 2–70 vs decks 35/20 | Covered, but supplied apertures nowhere stated — the order must specify 35/20 with certified tolerance |

## 5. Conditions precedent to the order (the GO-holding list)

1. Written confirmation of the **20–60 mm discharge-setting window** at
   duty (or corrected spec sheet).
2. **Contractual product gradation curve** at 60 mm setting (± tolerance),
   witnessed at FAT — it fixes the real n and hence the 1B feed.
3. Written acceptance of **320 mm top size** (or quarry-side 0–300 guarantee).
4. Screen delivered with **35/20 mm certified apertures** (panel type,
   tolerance, spare set per the priced option).
5. **FAT protocol defined** (the 30 % milestone now depends on it):
   2-h run at duty, gradation + efficiency sampling, acceptance criteria.
6. **VERTEX payment security**: contract names the payee, bank details
   verified through an independent channel.
7. Ndola frame: retention surviving to the SITE performance test — to be
   negotiated, or explicitly waived by the client (his call, registered).

Registration note: executing this test exposed stale zone-1.1 tags in
docs/design/soft-rock/*.json scenario INPUT files (CR.5009/SR.5007
survived the 2026-08-17 retag); the three scenario inputs were
retagged; the historical engine-evidence file was left untouched.

---
*All figures engine-computed (commit in the evidence provenance);
assistant-compiled prose. The verdict format (GO/NO-GO with conditions)
follows the panel recommendation pending the client's explicit framing
choice. Produced by NOEZYS.*
