# Reference analysis — "Le criblage", J.-M. Fontaine, 2004

**by NOEZYS** — received from the client 2026-08-17; archived unmodified
(`Le_criblage.doc`, SHA-256 9f5f1a829f2858e8c27ab003efa79311269d5de528f9c8caad2d5ad02eb25446;
Word 9.0 binary, created 2004-10-26, 7 672 words, 3 embedded OLE objects).
Author: the project's own [ref.] source (the model's Wi 12.54 "Fontaine,
Belgian limestone" and the M4 "VSMA / Fontaine" area form) — this notice is
upstream literature of our calibration lineage, not an outside opinion.

**Extraction honesty**: the 2004 binary refuses to load in this
environment's LibreOffice (all filters tried); analysis is built on the
FULL text harvested from the WordDocument stream
(`extracted-text-raw.txt`). Layout, figures (e.g. "fig 12" ball-deck) and
the 3 embedded equation/drawing objects were NOT visually inspected — the
presentation review below is structural, not visual. A PDF export from the
client's Word would complete it.

## 1. Content: what it is

A two-part practitioner's notice on vibrating screens: PART A theory and
selection (I screening principle, II screen conceptions by use and by
design, III components, IV screening media, V mesh section/selection);
PART B operations (startup checks, troubleshooting symptom→remedy,
general remarks, vendor enquiry checklist, practical data tables:
round/square mesh equivalence, approximate capacities t/m²).

## 2. Content: does it help us? YES — six concrete cross-links

| # | Fontaine 2004 says | Bearing on the project |
|---|---|---|
| 1 | "The screening mesh is generally 10 to 20 % LARGER than the required cut" | **Calibration confrontation for M3**: our k_d = 1.0 puts d50c AT the aperture; Fontaine's practice implies d50c below the aperture (a ≈ 1.1–1.2 × cut). Same open family as the I-convention question (Q3). To weigh in the expert clarification note — a k_d of ~0.83–0.91 would shift every cut curve |
| 2 | Stratification completes in the first metre; everything < a/2 passes immediately; lengthening a screen gives marginal returns | Independent support for the HALF-SIZE logic of the VSMA factor method (client M-1 decision) and for sizing by AREA not length |
| 3 | Open-area % at 8 mm: steel wire 64 % > perforated plate 44 % > PU 41 % > rubber 31 %; "replacing a deck with PU/rubber reduces the possible throughput — check the screen was sized for it" | Quantifies the SC.B woven-wire choice (Rhewum) and flags a REAL check for the BIVITEC PU family (SR.5105/5111/5115): vendor sizing must state the open-area assumption of its mats |
| 4 | Ball-deck under the cloth or electric cloth heating against blinding fines; wash water 1–1.5 m³/m³ | Our SC.B anti-pegging provision (FMECA FM3) is standard Fontaine practice; the wash-water figure prices any future wet-assist option (currently excluded by the client's no-moisture-works ruling) |
| 5 | "Enseignements à donner aux fournisseurs" — vendor enquiry checklist: rates avg/peak, material nature, bulk density, exact feed curve, moisture, cuts and decks, required efficiencies, washing/dewatering, enclosure, layout, screen type and slope, media, countermass, cloth tensioning, product envelopes | Near-superposable with our screen RFQ content lists — three items WE should add at next RFQ revision: **bulk density**, **peak rate vs average**, **cloth tensioning preference (side/end)**; countermass cost warning is new input for the installation file |
| 6 | Operations part: resonance crossing rules (fast start, no VFD without start bypass, brake at stop), clearances 50/80/50/20 mm, feed across full width, winter icing changes apertures and curves, re-purposing a screen requires full recalculation | Direct enrichment for the FMECA preventive plan and commissioning checklists; the winter/icing note is a new photo idea for cold-period quality watch |

Also archived for cross-check: the approximate-capacity table (t/m² per
square mesh, gravel vs crushed) — a potential independent anchor for the
M4 effective capacity (4.86·a^0.6), NOT yet exploited because the text
extraction lost the aperture column alignment; to be read off the
original layout when a PDF export is available.

## 3. What it does NOT change

No partition-curve mathematics, no capacity formula derivation, no
imperfection values in the extracted text (the calculation note it cites
— "voir note de calcul" — is a SEPARATE document we do not have; if the
client can retrieve it, it is likely the direct source of the spec's M4
constants). Nothing here contradicts the engine; item 1 is a calibration
question, not an error.

## 4. Presentation: why the client likes it, and what NOEZYS adopts

Structural qualities visible in the text (visual layout not inspected —
see honesty note):

1. **Cover states title, author, function** — the document carries its
   authority visibly.
2. **SOMMAIRE with page numbers** up front.
3. **Roman-numbered progression from definition to practice**: what it
   is → machine classes by USE then by DESIGN → components → media →
   selection → operations → troubleshooting → what to tell vendors →
   practical data tables. The reader always knows where he is.
4. **Key statements set apart in capitals** ("UN CRIBLE EST UN APPAREIL
   VIBRANT CONSTITUÉ DE: …") — one-glance definitions.
5. **Symptom → remedy lists** in the troubleshooting part (a pegging
   screen: five ordered causes, each with its fix).
6. **Practical value tables** (mesh equivalences, capacities) instead of
   prose.
7. **A vendor checklist as a closing annex** — the document ends on
   something the reader can USE tomorrow.

ADOPTION (proposed as the NOEZYS documentary reference, pending client
confirmation): future NOEZYS technical notes (DT-nnn and datasheets)
keep our provenance/traceability layer AND take over: the
definition-first capitals convention for load-bearing statements, the
symptom→remedy table form for operational sections, closing
practical-checklist annexes, and the use-then-design classification
order for didactic sections. DT-002 already follows several of these
(progression, tables, replay annex); the capitals convention and
symptom→remedy form are the two genuinely new imports.

---
*Analysis from the full extracted text; the archived original prevails.
Produced by NOEZYS.*
