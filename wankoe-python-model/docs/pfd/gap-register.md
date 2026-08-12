# PFD ↔ specification ↔ model gap register

**Authority ruling (the client, 2026-08-12): the NACO/Carmeuse PFDs are
authoritative over the specification v2026-08-08 wherever they diverge —
EXCEPT zone 1.3, where the DV.10 flap and the ML.30 "Unirotor" mill shown
on the DBR PFD have since been DELETED from the design: the current
zone-1.3 topology is the one already implemented in the model
(DY.03 → SN.21 → ML.26 closed loop → SP.36/CL.38 on the 0–1.5 fines).**

Sources archived in this folder:
- `20260806-Wankoe-1.1-PFD-REV15.pdf` (11-01-PFD REV15, NACO/Carmeuse)
- `20260806-Wankoe-1.2-PFD-REV18.pdf` (12-01-PFD REV18)
- `Wankoe-1.3-PFD-DBR.pdf` (design-basis review issue; partly superseded, see ruling)

Status column: OK = model already faithful · RETAG = rename only ·
REBUILD = model topology change required · INFO = design data recorded,
no model change · QUESTION = client/expert arbitration needed.

## Zone 1.1 (PFD REV15) — topology CONFIRMED, tags and design rates differ

| PFD | Model / spec | Item | Status / action |
|---|---|---|---|
| HO.5001 hopper 20 m³, VF.5002 feeder, ROM 0/700 10 000 t | not modeled (upstream of pivot) | primary station internals | INFO — pivot stays the measured belt-cut downstream |
| CR.5003 jaw, product 0/200 on BC.5004 | CR.5003 (blended into measured pivot) | design says top 200 mm; measurement says 19 % > 200 mm | QUESTION (measured curve stays pivot per measurement policy; design/measure tension recorded) |
| **CR.5006** double-roll, 0/200 → 0/40, 250 T/h | **CR.5009** | same machine, new tag | RETAG |
| BC.5007 0/40 350 T/h | — | loop conveyor rating (fresh 250 + recycle) | INFO |
| **SR.5008** double deck #35/#20 | **SR.5007** | same machine, new tag | RETAG |
| **DV.5009** mode flap | **DV-5099** | same flap, new tag | RETAG |
| CR.5011 impactor, BC.5010 20/40 125 T/h | CR.5011 | tag identical; design recycle 125 T/h vs computed 29.5 (mode A) | INFO / QUESTION (see scenario gap below) |
| BC.5012 0/20 170 T/h → **SP.5014 KFS Fines stockpile 0/20 10 000 t** | "0/20 stockpile" | stock now named and sized | INFO (capacity for yard design) |
| BC.5013 20/35 80 T/h → **SP.5015 KFS stockpile 20/35 5 000 t** → kiln | KFS product | stock named and sized | INFO |
| Scenario A: KFS 20-35 **80 tph**, crude 0-20 **170 tph** | model computes 51.35 / 198.6 wet at the measured curve, I = 0.15 | **32 % vs 20.5 % KFS yield — the central design-vs-model gap**; hangs on the design feed curve vs measured curve and on the imperfection arbitration | QUESTION (top of the expert clarification list) |
| Scenario B: crude 0-20 **150 tph** (no KFS) | expert book said "line ≈130 t/h in mode B"; model computes impactor load 86.6 t/h dry at 250 | three values now coexist (PFD 150 / book 130 / model 250-capable) | QUESTION |

## Zone 1.2 (PFD REV18) — topology DIFFERENT from spec/model: REBUILD

| PFD | Model / spec | Item | Status / action |
|---|---|---|---|
| Source: KFS Fines stockpile 0/20 (10 000 t) → **BF.5101 + BF.5102** (2 feeders, 100 T/h) → BC.5103 | single BF.5101 | two extraction feeders | REBUILD (data) |
| **DV.5104** mode flap after BC.5103 | absent | routes to screen (A) or bypass (B) | REBUILD |
| **SR.5105 single deck #6 (6 mm)**: 6/20 = **FEED LIME** (42 tph, scen. A) → BC.5107/5108 → **SP.5109 Feed stockpile 6 000 t** → Feed Plant | SR.5105 double deck 15/5; FeedLime = 5–15 mid cut | **FeedLime is 6/20, cut at 6 mm, single deck** | REBUILD (major) |
| **DV.5106** flap: routes 0/6 (A) or 0/20 (B: to Feed stock / C: to loop) | absent | mode routing | REBUILD |
| BC.5110 0/20-0/6 **60 T/h** → **SR.5111 first 1.7 mm screen (open circuit)** | absent | first closing screen — undersize AgLime, oversize to crusher | REBUILD (major) |
| BC.5112 1.7/20 100 T/h → **CR.5113** crusher → BC.5114 → **SR.5115 second 1.7 mm screen**; SR.5115 oversize recycles to BC.5112 (closed loop on second screen only) | single SR.5115 + CR.5107 loop | two-stage closing, crusher retagged CR.5113 | REBUILD (major) + RETAG |
| AgLime 0/1.7 → BC.5116/5117 60 T/h → **SP.5118 AG stockpile 28 000 t** | AgLime product | loop and conveyors rated 60 t/h; stock sized | INFO |
| Scenario table: A = FeedLime 6-20 42 tph + AgLime 0-1.7 58 tph · B = 0-20 100 tph to Feed · C = AgLime 60 tph | modes 2A/2B/2C | design rates for the three modes | INFO (verification targets for the rebuilt model) |
| Feed stockpile capacity **6 000 t** | — | model's seasonal FeedLime swing finding (~16 400 t) does NOT fit | QUESTION (yard design / operating strategy) |

Documents impacted: the zone-1.2 calculation-sheet document (2026-08-12)
is topologically wrong — WITHDRAWN, to be re-issued after the rebuild.
DT-001 sheets 4.4–4.6 likewise outdated. The zone-1.2 question round of
2026-08-12 (8 client decisions) largely survives: reclaim rate, weather,
moisture, planning rule c2, weekly ceiling, AgLime criterion carry over;
the PSD/cut-dependent parts must be recomputed on the 6 mm topology.

## Zone 1.3 (DBR PFD) — model topology CONFIRMED by the client ruling

| PFD | Model | Item | Status / action |
|---|---|---|---|
| DV.10 flap + **ML.30 "Unirotor" mill** circuit feeding SP.36 | absent | **DELETED from the design (client, 2026-08-12)** — model topology stands; UltraFin remains natural-fines extraction | OK (no change) |
| HO.01, BC.02 30 t/h with weighing, DY.03 + BU.04, FI.05/FN.06 dust filter, EM.09 metal detector | DY.03 modeled; auxiliaries not | dryer chain | OK / INFO |
| SN.21 #4/#2/#1.5 → grits 2–4 → BC.22 **15 t/h** → silo BI.80 (250 t); >4 & 1.5–2 → ML.26 loop; 0–1.5 → BE.40 **20 t/h** → silos BI.60/BI.70 (0.1–1.5, 250 t each) | matches model | conveyor/silo ratings | INFO |
| SP.36 + CL.38 → UltraFin → silo BI.50 (**250 t, 100 µm**) → tanker, "market to develop" | matches model | silo label supports the ~100 µm product envelope (note vs Q6's 65 µm cut) | INFO / note |
| Packing plant: MX.90 mixer 30 t/h, packers PK.64/74/87/92/100, pallets, loadouts; products FLF/FLG/FBL/FLUF/"Legend 10" with annual packaging tonnages | out of model scope | commercial packaging data | INFO (valuable for market/offtake checks) |

## Immediate model work plan (pending explicit client go)

1. Zone 1.2 flowsheet rebuild to PFD REV18 (6 mm split; open SR.5111 +
   CR.5113/SR.5115 closed loop; DV.5104/DV.5106 mode routing; loop rating
   60 t/h), verification against the PFD scenario table (42/58, 100, 60 tph).
2. Zone 1.1 retags (CR.5006, SR.5008, DV.5009) + scenario-B line feed
   150 t/h + design-rate confrontation (KFS 80 vs 51.35).
3. Zone 1.3: no topology change; absorb tags/ratings as data.
4. Re-issue: zone-1.2 calc document, DT-001 revision.
