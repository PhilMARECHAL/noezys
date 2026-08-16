# Eolianite Abrasivity Simulation

**by NOEZYS** — 2026-08-16. Client order (CR.5009 panel Q4 follow-up): no
measured abrasivity figures exist — simulate with aeolian-limestone figures:
a soft porous calcite matrix cementing **well-rounded ~200 µm quartz
grains**, which make an otherwise soft limestone genuinely abrasive.

**Status of every number: [H] simulated**, literature-anchored, pending the
external tests (§6). Product tonnages, PSD band contents and machine annual
throughputs are ENGINE results; the quartz split and severity factors are
the hypothesis model (`eolianite-abrasivity-scenario.json`; replay
`scripts/abrasivity_simulation.py`).

## 1. Rock model

Soft porous calcite matrix (UCS 15–30, porosity ~20 % — consistent with the
2026-08-15 soft-rock and moisture rulings) + **quartz 20 % central
[envelope 5–40 %]**, well-rounded grains d50 ≈ 200 µm (band 100–400 µm).
Quartz (HV ~1100) is the only phase harder than any tool steel
(HV 400–800): **wear is quartz-governed**; the rounded shape shifts
two-body cutting toward three-body rolling — less metal cutting (−20 %
applied), more polishing wear on teeth and severe wear on POLYMER media and
high-velocity surfaces.

## 2. Simulated abrasivity set (the RFQ annex until real tests land)

| Index | Central | Envelope | Class / note |
|---|---|---|---|
| Equivalent quartz content (Rosiwal) | 22.4 % | 6.4–42.4 % | quartz 1.0, calcite 0.03 |
| **LCPC ABR** (the governing test for soft rock + hard grains) | **550 g/t** | 300–900 | **"abrasive" (500–1250)**; roundness allowance −20 % applied |
| LCPC BR | — | — | very breakable (rippable, consistent) |
| Cerchar CAI | 1.1 | 0.8–1.5 | slightly-to-medium; **UNRELIABLE at UCS < 25** (pin ploughs the matrix) — quoted for completeness, LCPC governs |
| Bond abrasion index Ai | 0.10 | 0.03–0.25 | limestone 0.01–0.03, quartz sandstone 0.3–0.6 |

Headline for vendors: *"soft rock" does NOT mean "low wear" here* — the
matrix is soft, the grains are not.

## 3. Where the quartz goes — product purity table (engine streams, quartz 20 % central)

Liberated grains (100–400 µm) travel with each stream's 0.1–0.4 mm band;
embedded grains with the lumps (liberation ladder [H]: 25 % after CR.5009,
40 % in the 0/20 loop, 90 % after the 1.7 mm / fines trains).

| Product | t/y | Quartz % (sim) | CaCO₃-basis value vs pure |
|---|---|---|---|
| KFS 20/35 (kiln feed) | 85 000 | 12 % (model) — **realistically ≈ bulk 15–20 %**, intact lumps keep their embedded grains | **~80–88 %** |
| AgLime 0/1.7 | 135 000 | **32 %** (enriched — it collects the liberated grains) | **~68 %** |
| FeedLime fines 0/1.5 | 60 000 | 15 % | ~85 % |
| FeedLime grits 2/4 | 40 000 | 2 % (purified — their liberated grains left through the 1.5 mm cut) | ~98 % |
| UltraFin < 65 µm | 284 | **2 % (purified — 200 µm grains cannot pass the 65 µm cut)** | ~98 % |

Model limits stated: the free-grain allocation is approximate (±3 kt/y of
quartz unallocated to landfill); KFS purification is overstated by the
zone-level liberation assumption — treat KFS at bulk grade.

### ⚠ PRODUCT-QUALITY ALARM (maximum-honesty flag)

If the rock truly carries ~20 % quartz:

- **KFS at 15–20 % SiO₂ is normally DISQUALIFYING as lime-kiln feed**
  (kiln stone specs typically demand > 95–97 % CaCO₃). The 85 kt/y firm
  KFS commitment — the driver of the whole line — rests on a chemistry that
  this simulation cannot confirm. At the 5 % envelope low end it is
  borderline; at 40 % it is impossible.
- **AgLime neutralizing value ~68 % of pure** — sellable only if the market
  spec is NV-based and the price follows; the silica is agronomically inert.
- Conversely **grits and UltraFin come out quartz-purified** (~98 %) — the
  2/4 grits become the chemically premium product of the line.

**The XRF/mineralogy test therefore becomes the #1 external test of the
project, ahead of the drop-weight test**: it decides product marketability,
not just machine sizing.

## 4. Machine wear-duty ranking (engine annual tonnages × quartz exposure × class severity [H])

Relative index (kt-equivalent) — for MAINTENANCE PRIORITIES and RFQ wear
clauses, not absolute life prediction:

| Rank | Machine | Index | Driver |
|---|---|---|---|
| 1 | CR.5009 | 30.2 | 318 kt/y full-stream, embedded grains |
| 2 | CR.5113 | 24.0 | impactor at 107 kt/y on 90 %-liberated feed |
| 3 | RC.2 | 22.1 | smooth rolls, liberated grains in the regrind loop |
| 4 | SC.A | 21.5 | 331 kt/y across wire decks |
| 5 | SC.B | 17.6 | **PU fine mats vs free 200 µm quartz — the RPN-252 screen again** |
| 6–10 | RC.1 16.4 · SR.5111 14.0 · SR.5007 13.7 · CR.5011 13.2 · SR.5115 12.0 | | |
| 11–13 | SR.5105 6.6 · SP.36 0.5 · CL.38 0.3 | | classifier circuit sees little mass — but grain-vs-wheel velocity wear needs the vendor's word |

Consequences fed back into the purchase file:

- **CR.5009 RFQ**: tooth-steel loss order **0.6–2.5 t/y (central 1.3)** at
  318 kt/y — the wear-guarantee anchor replacing the missing client data.
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
