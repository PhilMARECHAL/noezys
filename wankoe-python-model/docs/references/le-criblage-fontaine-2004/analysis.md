# Reference analysis — "Le criblage" + "Cribles : approche de la détermination par le calcul", J.-M. Fontaine, Carmeuse S.A. 2001

**by NOEZYS** — REV B, 2026-08-17 (supersedes the text-only REV A of the
same day after the client supplied the PDF export). Archived unmodified:
`Le_criblage.doc` (SHA-256 9f5f1a82…, Word 9.0 binary, 2004 save of the
2001 course) and `Le_criblage.pdf` (SHA-256 a83f7e6a…, 60 p., the
client's export — the visual reference). Collection: Carmeuse Service
Formation, "Équipements Fours & Carrières", 2001. Author: the project's
own [ref.] lineage (the model's Wi 12.54 and M4 cite Fontaine).

**The PDF revealed what the text harvest could not: the file contains
TWO booklets.** Part 1 (p. 1–14): "Le criblage" — screens technology
notice. Part 2 (p. 15–49): **"Cribles — approche de la détermination
par le calcul" — THE "note de calcul" that Part 1 references.** It was
believed missing; it is here. Part 3 (p. 50–60): maintenance,
troubleshooting, vendor checklist, practical data tables.

## 1. THE HEADLINE FINDING — the source of M4 is identified

Tableau 6/7 (p. 40–41) states the screen capacity law:

> **Q (m³/h/m²) = 1,4 · a^0,6 / %GL** — a = mesh (mm), %GL = the
> percentage of "grains limites" (near-mesh limit grains) in the feed.

At %GL = 10 % this is **Q = 14 · a^0,6** — EXACTLY the engine's
`qb_coef = 14`, `qb_exp = 0.6` (spec model M4). The full lineage of our
area model is now documented:

- The spec's Qb = 14·a^0.6 is Fontaine's law evaluated at 10 % limit
  grains, in **volumetric** units (m³/h/m², not t/h/m²).
- The engine's fitted f0 = 0.347 therefore absorbs (a) the m³→t
  conversion at the working bulk density and (b) the REAL %GL of the
  duty vs the 10 % reference — which is exactly the composition
  dependence whose absence the error-hunt M-1 flagged and the client
  fixed by the VSMA factor method. Fontaine's own law gives the project
  a NATIVE near-mesh-aware sizing check: Q = 1.4·a^0.6/%GL.
- Follow-up (proposed): add the Fontaine %GL cross-check to
  `scripts/vsma_factor_sizing.py` and cite the true source in DT-002
  §4.4 at its next revision.

Also on p. 30: the worked efficiency model — screening efficiency
(90/95 %) is held from the mesh DOWN TO HALF-MESH, then tends to 100 %
below a/2. That is Fontaine's partition-curve shape statement, to put
beside our logistic M3 in the same expert clarification note as the
k_d and I-convention questions.

## 2. Other content findings (Part 2 — the calculation booklet, p. 15–49)

| Item | Value | Bearing |
|---|---|---|
| Machine power | P(kW) = rpm × couple(kgm) / 973.4 | Screen drive sanity checks |
| Amplitude | a = excitation couple (kgm) / vibrating weight (kg); stroke = 2a | Commissioning baselines (DT-002 tie-in) |
| Vertical acceleration | OPTIMUM 3.3 g (efficiency/wear); < 1.5 g product does not lift; 1.6–2.3 g fragile/friable products; 2.3–4 g coarse non-friable; > 4.2 g premature machine wear | Acceptance criterion vocabulary for screen commissioning; note BIVITEC-class flip-flow mats work at much higher mat accelerations — distinct concept |
| Frequency by cut | < 15 mm → 1500 rpm; 15–40 mm → 1000; > 40 mm → 750 | Vendor-offer sanity check (SR.5008 at 20/35 → ~1000 rpm class) |
| Amplitude by mesh | 100→6.5, 75→5.5, 50→4.5, 25→3.5, 12→3, 6→2, 2→1.5 mm | Same |
| Böttcher transport speed | Vh = (g/2)(η²/f)·60·cotg α, η from abaque 1; abaques 2–4 give Vm/min at 720/940/1410 rpm | Bed transport/depth checks |
| Extraction under hopper | PEX ≈ 1.5 kW per tonne of influenced material, hm = a·b/0.32(a+b) | If any screen is hopper-fed |
| Suspensions | Spring working rate ~2 500 daN/cm²; rubber buffers ≈ 2× spring stiffness; countermass ≥ 50 % machine weight divides vertical dynamic reactions by 10 (and "costs very dear") | Installation/structure file |
| Unidirectional (exciter) vs circular screens | Exciters: sharper cut, horizontal mesh, better for big flows and dewatering; circular: cheaper, need larger areas, work only at 2.8–5.5 g; AVOID oil-lubricated circular mechanisms — greased bearings last 3–4× | Machine-class arguments: supports the F-Class/exciter choice for SR.5008 and documents the maintenance preference |
| Machine-type matrix (p. 59–60) | 16 separation machine types × ~19 criteria with remarks: sonic-wave screens "très intéressant en criblage ultra fin < 250 µ"; Mogensen for 0.5–3 mm dry multi-cuts | Independent support for the SC.B direct-excitation class and the fine-screening technology map |

## 3. Content findings (Parts 1 and 3) — carried over from REV A, now page-referenced

1. **Mesh 10–20 % larger than the required cut** (p. 9) — calibration
   confrontation with our k_d = 1.0 (joins Q3, expert note).
2. Stratification completes in the first metre; < a/2 passes at once;
   lengthening a screen is marginal (p. 9) — VSMA half-size logic.
3. Open areas at 8 mm: wire 64 % > perforated 44 % > PU 41 % > rubber
   31 % (p. 10); PU/rubber wear 3–4× plate but need LARGER areas (p. 9)
   — SC.B wire choice + BIVITEC open-area check.
4. Ball-deck / cloth heating anti-blinding (p. 9, fig 12); wash water
   1–1.5 m³/m³ (p. 10).
5. **Vendor enquiry checklist** (p. 58) — add to our screen RFQs: bulk
   density, peak vs average rate, cloth-tensioning preference;
   countermass cost warning in red.
6. Practical tables (p. 59): round mesh d = 1.25·a equivalence;
   **approximate capacities, crushed stone**: 2 mm 5 · 4 mm 7 · 7 mm 10
   · 10 mm 14 · 14 mm 16.5 · 20 mm 20 · 32 mm 26 · 40 mm 30 · 60 mm 35
   · 90 mm 40 t/m² — the table follows ≈ 3.3·a^0.6 over 2–40 mm (same
   0.6 exponent as M4!), i.e. ≈ 68 % of our effective 4.86·a^0.6.
   Reading with §1: Fontaine's practical column corresponds to a
   HIGHER %GL / all-in operating conditions than the engine's fitted
   reference — a coherent lineage, not a contradiction; the honest
   conclusion stands that our dry-photo areas are optimistic whenever
   the near-mesh fraction is heavy, which is exactly why the purchase
   minima use the VSMA factor method and the rain duty.
7. Operations rules (p. 50–57): no flame/welding on screen bodies ever
   (crack initiation), stop-drill cracks, 8.8 bolt torque table,
   CD/CN ≥ 2.5 starting torque, no VFD without start bypass, clearances
   50/80/50/20 mm, feed full-width and "à rebrousse-poils", reception
   plate on the top deck, winter icing changes apertures — FMECA and
   commissioning enrichment.

## 4. Presentation review (now VISUAL — the client's stated reason)

The document's visual language, page-verified:

1. **Cover**: brand logo + collection ("Service Formation"), massive
   navy title, author + function, constant footer "CARMEUSE S.A. 2001 ·
   ÉQUIPEMENTS FOURS & CARRIÈRES · page".
2. **Chapter cover pages**: pale-yellow banner box, oversized red drop
   cap, photo grid of the real machines, then the SOMMAIRE.
3. **Section heads**: white-on-navy filled banners (I. LE CRIBLAGE);
   sub-sections in teal filled banners (2.1 PARTIE MÉCANIQUE);
   sub-sub-heads in red underlined italics.
4. **Red circled figure badges** (1, 2a, 2b…) placed ON the photos and
   referenced inline as (fig 2b) — text and image lock together.
5. **Formula boxes**: pale-yellow panels with teal titles and real
   fraction layout; every formula numbered (I)…(X).
6. **Red STOP octagon callouts** for load-bearing cautions; red (!)
   inline warnings; a green box for cross-machine remarks.
7. **Data tables with colored header bands** (yellow for practical
   tables, navy for dimensional tables, orange for worked analyses);
   the closing machine-type matrix uses a green remarks column.
8. Worked numeric examples embedded after each formula (the balourd
   example computed to the kgm), then abaques as full-page annexes.

**ADOPTION — the NOEZYS documentary standard (proposed, pending client
confirmation):** keep our provenance/traceability layer and adopt:
(a) filled banner section heads, (b) definition-first statements set
apart (capitals or box), (c) numbered formula boxes with worked
examples, (d) figure badges locked to inline references, (e) STOP-style
callouts for load-bearing cautions, (f) colored table header bands,
(g) closing practical-checklist annexes. The noezys-report generator
can carry (a)(b)(f) directly; (c)(d)(e) enter the DT templates at
their next issues.

---
*REV B analysis from the full PDF (visual) + extracted text; archived
originals prevail. Produced by NOEZYS.*
