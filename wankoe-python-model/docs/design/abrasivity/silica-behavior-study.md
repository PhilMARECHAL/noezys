# Silica Behavior Through the Process — Expert-Team Study (REV B)

**by NOEZYS** — 2026-08-16. Client order: *"the silica grains are truly
embedded in the mass like a cookie — mobilize an expert team to evaluate how
the silica behaves through the whole process."* Four experts (liberation
physics, tribology, product quality, industrial hygiene) worked in parallel
on the engine; this study is their joint synthesis. It SUPERSEDES the
product-grade and wear conclusions of REV A
(`eolianite-abrasivity-simulation.md`), whose liberation ladder overstated
liberation 3–35×.

**Basis**: quartz 5 % (client datum, band [3–8]), well-rounded grains
d50 = 0.2 mm embedded in soft porous calcite; grains NEVER break — they are
embedded or free, whole.

## 1. The cookie liberation law (physicist)

**L(x) = 1 for x ≤ d; ln(k·d/x)/ln(k) for d < x < k·d; 0 for x ≥ k·d** —
d = 0.2 mm, k = 3 [2–4] [H] (random breakage of dilute round inclusions
gives k ≈ 1.5–2; interface-preferential detachment in the porous
weakly-cemented eolianite raises it to ~3–4 and raises S_att: grains are
plucked whole at surfaces). Two theorems, verified in the engine
(`scripts/liberation_rev_b.py`): **a closed loop cannot enrich its only
exit**, and **every cut ≥ 1.5 mm leaves both sides at bulk grade**. The
only quartz-discriminating operation of the whole line is the SP.36 65 µm
cut. Real liberation ladder (engine, g0 5 %, k 3): 0/20 loop **1.2 %**,
CR.5113 product **33.5 %**, fines train **12.3 %**, KFS/grits **0 %** —
versus the superseded 25/40/90/90.

## 2. Product silica — the corrected table (flat profile)

| Product | t/y | Quartz % REV B | Free-grain share | CaCO₃-basis |
|---|---|---|---|---|
| KFS 20/35 | 85 000 | **5.00 (= bulk)** | 0 % | 95.0 % (92–97 over [3–8]) |
| AgLime 0/1.7 | 135 000 | **5.00** — REV A's 8.1 % enrichment GONE | 31 % (~2 070 t/y free) | 95.0 % (NV ~95 % of pure — comfortable) |
| FeedLime grits 2/4 | 40 000 | **5.00** — REV A's 0.5 % purification claim WITHDRAWN | 0 % | 95.0 % (check feed buyers' acid-insoluble limits) |
| FeedLime fines 0/1.5 | 60 000 | 5.02 | 12 % (~370 t/y free) | ~95 % |
| **UltraFin < 65 µm** | 284 | **~0 (< 0.2 [H])** — claim STRENGTHENED, doubly locked: a free 200 µm grain cannot pass a 65 µm cut, and a < 65 µm particle cannot CONTAIN a 200 µm grain | — | **~100 % — the line's only premium-purity product** |

Quartz balance closes exactly. **Falsification test (free):** the model
predicts a FLAT acid-insoluble ≈ bulk on KFS/AgLime/grits/fines and ~0 on
UltraFin — add per-product acid-insoluble to the NACO reconciliation; any
measured differentiation between streams refutes the cookie model.

## 3. Kiln chemistry — the verdict HARDENS (product-quality expert)

Per tonne of KFS at 5 % SiO₂: the quicklime concentrates to **~8.6 % SiO₂**
after CO₂ loss; above ~900–1000 °C quartz scavenges free CaO into belite
(1.87 kg CaO per kg SiO₂) — realistic available CaO **~80–88 %** against
merchant specs ≥ 92–94 %; ring/buildup risk from low-melting silicates;
belite dusting on cooling. **The sharper gate is not the CaCO₃ axis: most
kiln stone specs carry an explicit SiO₂ / acid-insoluble limit of
≤ 1–2 %, which the whole [3–8] band fails.** And the silica is embedded —
geological, not washable, not screenable. KFS is sellable only to a kiln
with an unusually permissive spec or into lower-grade lime uses (FGD
sorbent, soil stabilization). **Confronting the kiln buyer's actual spec
sheet with the XRF result is decision gate #1 of the project.**

## 4. Unit-op walkthrough (the client's literal question — one line each)

CR.5009 sizer: inert passenger, breaks matrix at 100–300× grain scale —
wear on tooth tips only. · SR.5007/CR.5011 loop: size-only sorting; grade
of every fraction ≈ bulk. · All screens: inert to composition; silica felt
only as media wear. · DY.03 dryer: quartz thermally inert (α–β at 573 °C,
far above 100–300 °C) — confirmed no issue. · RC.1/RC.2: grains 7× smaller
than gap 1.5 transit untouched; during nip they are incompressible hard
points (indentation-fatigue micro-pitting of the shells). · CR.5113: the
line's closest approach to grain scale (P80 0.95) — partial liberation, but
the closed loop returns everything to AgLime: grade unchanged. · SP.36:
the ONLY discriminating unit — every free grain rejected to the fines
side. · CL.38/dust tail: sub-10 µm dust is matrix-derived, **essentially
pure calcite** if grains don't break — the missing bag filter's health
severity drops, its emission-compliance need stands. · Water circuits:
none after the dryer; quartz inert upstream.

## 5. Wear — modes re-derived (tribologist)

**The sandpaper-particle question, settled quantitatively**: cookie
particles present ~quartz-only contacts (grains are the hardest AND tallest
asperities, fracture routes around them), BUT at low-stress sliding the
per-grain contact pressure is ~0.3–0.4 GPa — **5× below the plasticity
onset of HV 500 steel and ~15× below cutting**. Cookie particles POLISH,
they do not cut; PU/rubber spread the contact and are barely attacked.
The regime flips to cutting only under **confinement** (crusher nip:
~4–5 GPa at the grain seat) or **inertia** (impact at 25–40 m/s: dynamic
pressure above any metal's flow).

| Machine | Dominant regime | vs REV A | RFQ clause edit |
|---|---|---|---|
| CR.5009 | embedded, confined compression | ≈ #1 by absolute loss | tooth overlay ≥ HV 650; LCPC annex as UPPER bound; keep 0.3–1.3 t/y anchor |
| CR.5113 | embedded+free IMPACT, partial in-machine liberation | ↑ co-#1, highest g/t | renewable high-Cr pins; wear cost per 1 000 h contractual |
| **CR.5011** | embedded-grain IMPACT at 30 m/s | **↑↑ rank 9 → ~3** (inertia defeats the soft-matrix excuse) | blow bars high-Cr HV 700–850 min; **ceramic-insert option priced** |
| RC.2 | confined grain-on-shell point loads | ≈ rank, mode re-classified: indentation micro-pitting | shell ≥ 60 HRC; **gap-hold ±0.1 mm guaranteed over shell wear life**; unbroken-grain product check |
| SC.B | free grains + polishing | metal loss ↓, **cut-integrity risk ↑** | **keep Rhewum wire** (certification governs; wear no longer argues for PU); add **in-service aperture-drift guarantee** |
| **SP.36 wheel** | grain-ENRICHED reject recirculation at wheel speed | ↑↑ highest SPECIFIC severity in plant (tiny tonnage) | **ceramic wheel MANDATORY** (was option) |
| **Fan** | behind the 4 µm cut — grains physically cannot reach it | **↓↓ erosion clause WITHDRAWN** | standard construction + inspection port |
| SC.A / SR.5007 / SR.5105 / SR.5111/5115 / belts / DY.03 | polishing / mild | ↓ to ↓↓ | AR/PU chute liners only at AgLime-loop + fines-train impact points |

LCPC caveat: the test liberates the grains it crushes — it OVER-represents
our mostly-embedded compression/sliding duties (use 310 g/t as upper bound
there), is about right for the impactors, and locally UNDER-represents the
SP.36 wheel. The regime map goes into every RFQ so vendors price the right
number for the right machine.

**Hottest free-grain interface of the plant: SR.5115** (~1 800 t/y of free
grains through the CR.5113 product), not SC.B (~370 t/y per deck) — a
REV B re-ranking the FMECA wear occurrences inherit.

## 6. Respirable crystalline silica (industrial hygiene)

**Verdict: monitoring item, NOT a plant-wide design driver — with one
design-driver exception: the missing CL.38 polishing bag filter.** The
cookie physics (200 µm unbroken grains vs the 4–10 µm health conventions,
plus the 65 µm and 4.2 µm cuts that geometrically strip grains) predicts
quartz-in-respirable-dust ≪ the break-even fractions (RCS OEL 0.1 mg/m³ —
binding at ~1.25–2.5 % quartz in respirable dust; bulk 5 % sits ABOVE
every break-even, so the physics is the only shield and it must be
MEASURED, never assumed). Residual mechanisms ranked: (1) a natural
sub-10 µm quartz second population in the matrix — the one that could flip
everything, now an explicit XRF/XRD requirement; (2) grain-surface
micro-chipping in the impactors (~0.1–1 t/y seeded fine quartz — trivial
mass, non-trivial vs a 0.1 mg/m³ OEL); (3) RC.2 attrition polishing.
Dust-point map and controls: dryer filter FI.05/FN.06 exists (add
broken-bag detector + emission guarantee); **CL.38 polishing filter
specified NOW with "dust may contain RCS pending XRD", ePTFE membrane
bags, ≤ 5 mg/Nm³**; zone-1.3 LEV dedusting package = new RFQ line item;
loadout telescopic chutes + bagging LEV; water/fog suppression in zones
1.1/1.2. Products: quartz ≥ 1 % must appear in AgLime and fines SDS
(Section 3), but CLP hazard classification follows the RESPIRABLE silica
content (SWeRF < 1 % → not classified) — the cookie physics is also the
product-safety defense, substantiated by the SWeRF measurement.
Carcinogens-Directive obligations (minimization, exposure records, health
surveillance) apply wherever any RCS exposure exists.

## 7. The XRF/XRD campaign — one test closes every question

1. Bulk SiO₂ % + deposit variability (benches/belt-cuts) → the [3–8] band.
2. Mineralogical split (XRD/SEM): rounded quartz grains vs clay/chert/opal.
3. Grain-size distribution of the acid-insoluble residue → confirm
   100–400 µm and the ABSENCE of a sub-65 µm quartz tail (locks UltraFin
   purity AND the RCS verdict — the same measurement).
4. Acid-insoluble by size fraction on a lab-crushed sample: flat profile =
   cookie model confirmed (falsification test).
5. SWeRF on AgLime/fines (product SDS defense); XRD of dryer-filter and
   CL.38 tail catches at commissioning.
6. KFS full oxide suite + calcination/slaking reactivity, confronted
   line-by-line with the kiln buyer's spec — **decision gate #1**.

---
*Provenance: 4 expert reviews 2026-08-16 on engine state 71db567+;
liberation evidence `liberation-rev-b-evidence.json`
(`scripts/liberation_rev_b.py`, ratified from the physicist's replay);
grades/fluxes engine-computed at g0 5 %, k 3; contact mechanics, kiln
chemistry and regulatory arithmetic assistant-computed [H]. REV A tables
in `eolianite-abrasivity-simulation.md` remain as the historical record —
this study supersedes their product grades and wear ranking. Produced by
NOEZYS.*
