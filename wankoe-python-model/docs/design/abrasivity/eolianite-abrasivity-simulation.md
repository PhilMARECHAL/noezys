# Eolianite Abrasivity Simulation

**by NOEZYS** — 2026-08-16. Client order (CR.5009 panel Q4 follow-up): no
measured abrasivity figures exist — simulate with aeolian-limestone figures:
a soft porous calcite matrix cementing **well-rounded ~200 µm quartz
grains**, which make an otherwise soft limestone genuinely abrasive.

**REV A — 2026-08-16 (same day):** the client supplied a real figure —
**5 % silica at the zone-1 feed** — superseding the assistant's 20 % [H]
central. Every table below is recomputed at quartz 5 % (confirmation band
[3–8 %] until XRF). Product tonnages, PSD band contents and machine annual
throughputs are ENGINE results; the quartz split and severity factors
remain the hypothesis model (`eolianite-abrasivity-scenario.json`; replay
`scripts/abrasivity_simulation.py`).

## 1. Rock model

Soft porous calcite matrix (UCS 15–30, porosity ~20 % — consistent with the
2026-08-15 soft-rock and moisture rulings) + **quartz 5 % (CLIENT DATUM
2026-08-16, confirmation band [3–8 %])**, well-rounded grains d50 ≈ 200 µm
(band 100–400 µm).
Quartz (HV ~1100) is the only phase harder than any tool steel
(HV 400–800): **wear is quartz-governed**; the rounded shape shifts
two-body cutting toward three-body rolling — less metal cutting (−20 %
applied), more polishing wear on teeth and severe wear on POLYMER media and
high-velocity surfaces.

## 2. Simulated abrasivity set (the RFQ annex until real tests land)

| Index | Central (REV A, quartz 5 %) | Band | Class / note |
|---|---|---|---|
| Equivalent quartz content (Rosiwal) | 7.9 % | 5.9–10.8 % | quartz 1.0, calcite 0.03 |
| **LCPC ABR** (the governing test for soft rock + hard grains) | **310 g/t** | 250–420 | upper half of "not very abrasive" (0–500) — **still 1.5–3× a clean limestone (~100–200)**; roundness allowance −20 % applied |
| LCPC BR | — | — | very breakable (rippable, consistent) |
| Cerchar CAI | 0.6 | 0.4–0.9 | slightly abrasive; **UNRELIABLE at UCS < 25** (pin ploughs the matrix) — quoted for completeness, LCPC governs |
| Bond abrasion index Ai | 0.04 | 0.02–0.08 | limestone 0.01–0.03, quartz sandstone 0.3–0.6 |

Headline for vendors: *"soft rock" does NOT mean "low wear" here* — the
matrix is soft, the grains are not.

## 3. Where the quartz goes — product purity table (engine streams, quartz 5 % client datum)

Liberated grains (100–400 µm) travel with each stream's 0.1–0.4 mm band;
embedded grains with the lumps (liberation ladder [H]: 25 % after CR.5009,
40 % in the 0/20 loop, 90 % after the 1.7 mm / fines trains).

| Product | t/y | Quartz % (sim, REV A) | CaCO₃-basis value vs pure |
|---|---|---|---|
| KFS 20/35 (kiln feed) | 85 000 | 3.0 % (model) — **realistically ≈ bulk 5 %**, intact lumps keep their embedded grains | **~95–97 %** |
| AgLime 0/1.7 | 135 000 | **8.1 %** (enriched — it collects the liberated grains) | **~92 %** |
| FeedLime fines 0/1.5 | 60 000 | 3.9 % | ~96 % |
| FeedLime grits 2/4 | 40 000 | 0.5 % (purified — their liberated grains left through the 1.5 mm cut) | ~99.5 % |
| UltraFin < 65 µm | 284 | **0.5 % (purified — 200 µm grains cannot pass the 65 µm cut)** | ~99.5 % |

Model limits stated: the free-grain allocation is approximate (±3 kt/y of
quartz unallocated to landfill); KFS purification is overstated by the
zone-level liberation assumption — treat KFS at bulk grade.

### ⚠ Product-quality flag — DOWNGRADED to BORDERLINE at the client datum (REV A)

At the earlier 20 % [H] this was an alarm ("normally disqualifying kiln
feed"). At the client's 5 %:

- **KFS lands at ~95–97 % CaCO₃-basis — exactly ON the typical lime-kiln
  spec boundary (> 95–97 %)**. Compliant at 5 %, non-compliant at the top
  of the confirmation band (8 % → ~92 %). The kiln buyer's ACTUAL stone
  spec must be confronted with the XRF result — this stays a decision
  gate, no longer an alarm.
- **AgLime NV ~92 % of pure** — commercially unremarkable.
- **Grits and UltraFin come out quartz-purified (~99.5 %)** — worth a
  premium-purity claim in their market sheets once XRF confirms.

**XRF/mineralogy keeps external-test priority #1** — no longer to save the
project, but to (a) confirm the 5 % figure and its variability across the
deposit, (b) split free rounded grains vs other silica forms (drives wear),
(c) settle the KFS kiln-spec margin.

## 4. Machine wear-duty ranking (engine annual tonnages × quartz exposure × class severity [H])

Relative index (kt-equivalent) — for MAINTENANCE PRIORITIES and RFQ wear
clauses, not absolute life prediction:

| Rank | Machine | Index | Driver |
|---|---|---|---|
| 1 | CR.5009 | 7.5 | 318 kt/y full-stream, embedded grains |
| 2 | CR.5113 | 6.0 | impactor at 107 kt/y on 90 %-liberated feed |
| 3 | RC.2 | 5.5 | smooth rolls, liberated grains in the regrind loop |
| 4 | SC.A | 5.4 | 331 kt/y across wire decks |
| 5 | SC.B | 4.4 | **PU fine mats vs free 200 µm quartz — the RPN-252 screen again** |
| 6–10 | RC.1 4.1 · SR.5111 3.5 · SR.5007 3.4 · CR.5011 3.3 · SR.5115 3.0 | | |

(The RANKING ORDER is quartz-grade-invariant — grade scales every index by
the same factor; REV A indices are the 5 %-datum values, 4× below the
superseded 20 % run.)
| 11–13 | SR.5105 6.6 · SP.36 0.5 · CL.38 0.3 | | classifier circuit sees little mass — but grain-vs-wheel velocity wear needs the vendor's word |

Consequences fed back into the purchase file:

- **CR.5009 RFQ**: tooth-steel loss order **0.3–1.3 t/y (central 0.6)** at
  318 kt/y (REV A at the 5 % client datum) — the wear-guarantee anchor for
  the RFQ.
- **SC.B (Rhewum pick)**: free 200 µm quartz across 1.5/2.0 mm media —
  demand a wear-life guarantee **on quartz-bearing feed** and revisit
  panel material (wire vs PU trade-off changes with quartz).
- **FMECA**: wear-mode occurrence classes for CR.5113, RC.2, SC.A/SC.B were
  scored on limestone-only assumptions — re-score after XRF.
- **Belts/chutes on fines streams** (AgLime loop, 0/1.5 train): liner
  upgrade candidates — the liberated-grain streams are the abrasive ones.

## 5. What does NOT change

Mass balances, capacities, hours, energies: quartz density ≈ calcite
density (2.65 vs 2.71) — the flowsheet arithmetic is composition-blind.
Bond Wi 7.5 [H] may rise somewhat with quartz content (site Bond test
already registered).

## 6. External tests — updated priority order

1. **XRF / mineralogy (quartz %) — NEW #1**: decides KFS and AgLime
   marketability (product chemistry), then re-runs this simulation with the
   real grade.
2. LCPC (ABR + BR) on samples — the governing abrasivity number for every
   wear guarantee (Cerchar secondary, unreliable on this matrix).
3. Drop-weight A·b (was #1 — now #2 ex aequo with LCPC).
4. Bond Ai + site Bond Wi; vendor gradation tests (RC.1/RC.2, sizer curve);
   sieve, absorption, repeat belt-cuts, NACO — unchanged.

---
*Engine-run provenance: plan + photos at commit ffe3247, data
`data/default_parameters.json` defaults; hypothesis set
`eolianite-abrasivity-scenario.json` [H]; evidence
`abrasivity-engine-evidence.json`; replay
`PYTHONPATH=src python scripts/abrasivity_simulation.py`. Produced by
NOEZYS.*
