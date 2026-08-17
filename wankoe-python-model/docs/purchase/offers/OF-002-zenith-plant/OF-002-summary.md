# OF-002 — Shanghai Zenith Mineral Co., Ltd — Quotation 2026-06-12 (4 machines + spares)

**by NOEZYS** — summary sheet, 2026-08-17. Original (unmodified,
SHA-256 in the [register](../REGISTER.md)): `original/
ZENITH_quotation_2026-06-12.pdf` (24 p.: quote + technical
specification brochure). Provenance: received from the client
2026-08-17 (his channel — the NOEZYS RFQ package sent nothing).
**Note the date: this quote PREDATES the August design decisions**
(C1 redesign, CR.5107→CR.5113 renaming 2026-08-12, sizer-class ruling
2026-08-16) — it answers an EARLIER machine list carrying the old tags.

## 1. Commercial facts

| Item | Value |
|---|---|
| Vendor | Shanghai Zenith Mineral Co., Ltd, No.1688 East Gaoke Road, Shanghai, China (CE, CQC, ISO9001) |
| Addressee | Carmeuse (South Africa location) |
| Date / validity | 2026-06-12 / 90 days → **expires ~2026-09-10 (still valid at registration)** |
| PART-1 main machines | **USD 323,666 FOB Shanghai** |
| PART-2 spares, 2 years (optional) | **USD 89,146 FOB** |
| Total FOB Shanghai | **USD 412,812** (≈ EUR 357–375k [H FX 1.10–1.156]) |
| Sea freight + insurance to Cape Town | "very unstable, up to ready for delivery" — CIF NOT fixed |
| Payment | 30 % deposit at contract, 60 % after factory inspection, **10 % after installation but ≤ 6 months from B/L** |
| Lead time / warranty | 60 working days; 12 months from trial run, ≤ 15 months ex-factory |
| Components | Siemens/ABB motors, Timken/SKF bearings, Bao Steel structure; third-party inspection (SGS, AI, COTECNA) ACCEPTED |
| Exclusions | Diesel generator set and cables |

## 2. Line items and tag mapping

| # | Zenith model | Their tag label | Price (USD) | Our mapping today | Fit notes |
|---|---|---|---|---|---|
| 1 | C6X100 JAW crusher, 110 kW, feed ≤ 630 mm, CSS 70–175 mm, 130–420 t/h | "CR.5009" | 105,209 | **CR.5009 — WRONG CLASS** | Client ruling Q3 (2026-08-16) = twin-shaft toothed SIZER; a jaw at CSS ≥ 70 mm also cannot make the 0/60 product. Non-conforming as quoted — superseded by the OF-003 toothed roller machine (which IS the right class) |
| 2 | CI5X1315 impact crusher, frame "suitable for 250 kW continuous", 3 apron layers | "CR.5107" | 106,769 | **CR.5113** (renamed 2026-08-12) | 250 kW frame < the 2C branch-1 need (348 kW absorbed, 450 kW rec.) — would force the CAPPED-RATE branch 2 (planning replay needed); motor-branch question of the datasheet applies verbatim |
| 3 | S5X2760-3 screen (2.7×6.0 m, 3 decks), meshes 20/40/80 mm | SR.5007 | 46,323 | **SR.5007 candidate** | Area 16.2 m²/deck ≫ rain minima 9.1/9.6 — PASS; meshes again **40 vs our 35 mm** top cut (same deviation as OF-001; 80 mm = added scalping deck) |
| 4 | S5X3075-2T screen (3.0×7.5 m, 2 decks), meshes 2 mm / 15 mm | "SC.5105" | 65,366 | **Uncertain** — matches no current tag (SR.5105 is a 6 mm single-deck; the 2 mm deck evokes SC.B deck-1) | Mapping to be clarified with the client's original enquiry list |

Spares (PART-2): priced per machine over 2 years — partially aligned
with our mandatory FMECA-spares line (jaw plates 3,000 h / hammers
2,500 h life figures stated).

## 3. Gaps vs the NOEZYS RFQ frame (honesty section)

1. **Machine list is the OLD one**: the quote answers a pre-redesign
   enquiry. Two of four items no longer match the ruled configuration
   (jaw ≠ sizer class; "SC.5105" unmappable). A re-quote against the
   drafted RFQ datasheets is required before evaluation.
2. **Payment**: 90 % paid before/at factory gate, final 10 % capped at
   6 months from B/L, tied to installation not to a PERFORMANCE TEST —
   closer to our frame than OF-001 (a real post-installation holdback
   exists) but still short of the Ndola clauses (≥ 20 % retained to
   the passed site performance test on WANKOE material).
3. **No product-curve guarantees, no value tables, no witnessed duty
   tests** (golden rules 2/3 unmet); capacity figures are catalog
   ranges.
4. **CIF not fixed** ("freight very unstable") — landed cost open.
5. **No abrasivity basis** (5 % embedded quartz context absent);
   blow-bar/hammer life given generically (2,500 h).
6. Warranty 12/15 months standard — obligations do not survive to
   full performance.

## 4. Budget cross-check

Four-machine bundle ≈ EUR 280–294k FOB [H FX] against the CENTRAL sum
of the four nearest tags (CR.5009 380 + CR.5113 400 + SR.5007 195 +
[unmapped] ≈ 95–180) — the bundle sits far below CENTRAL and inside
the premium-Chinese LOW anchors of the budget file, consistent with
OF-001. Positive evaluation signals to keep: third-party inspection
accepted, Siemens/Timken components, priced 2-year spares.

## 4bis. TECHNICAL ANNEXES received 2026-08-17 (supplement — original/technical-annexes/, SHA-256 in the register)

Zenith supplied engineering-grade documentation (all drawings dated
2025-12-01, construction stage, edition A) — general arrangements,
FOUNDATION LOAD DIAGRAMS and CIVIL-WORKS guidance drawings. Extracted
facts:

| Machine | Key data from the drawings | NOEZYS reading |
|---|---|---|
| **S5X2760-3** (→ SR.5008 candidate) | 3 decks, 16.2 m²/deck (2.7×6.0), graded 2–70 mm, 120–900 t/h, media woven wire/rubber/PU (tension), 850 rpm (800/900), double amplitude 7–11 mm, tilt 18°, max feed 200 mm, motor 37 kW YE3-225S-4, 13 020 kg; support loads: static 31.9 kN, working ±5.0 kN, max ±24.8 kN per point; C30 foundation drawing, feed drop ≤ 400 mm | Area amply clears the 9.1/9.8 m² rain minima. CROSS-CHECK vs the Fontaine reference (circular screens work 2.8–5.5 g): amplitude 3.5–5.5 mm at 850 rpm gives 2.8–4.4 g — inside the band, coherent engineering. Circular 18° machine: the vendor must still state stroke behavior under the RAIN bed (RFQ 02 gate G5) — a circular free-oscillation machine is debit-sensitive per the same reference |
| **S5X3075-2T** (the "SC.5105" mystery line) | 2 decks, 21.6 m², graded 2–150 mm, 180–1 800 t/h, 2×22 kW dual motors, 850 rpm, amplitude 8–12 mm, tilt 20°, max feed 300 mm, 17 538 kg; loads ±5.6/±28.1 kN; C30 civil drawing | With quote meshes 2/15 and 21.6 m² ≥ the 19.1 m² SR.5115 floor, this frame COULD be aimed at the AgLime-loop closed screen — but it is a CONVENTIONAL circular screen: the project's own rain physics (1.7 mm moist cut = flip-flow territory) makes the technology class the question, not the size. Mapping still to be clarified with the client's original enquiry |
| **CI5X1315-III** (→ CR.5113 candidate) | Cross-section confirms a THREE-curtain HSI (4-bar rotor, three adjustable aprons — the quote's "three layers impact plates"); anchor plan: M36×800 ×6 host bolts, static 30 kN / dynamic 103 kN per hole; single motor 1 670 kg, transmission package 2 075 kg | The 3rd curtain is the fine-product argument for the AgLime duty; the motor-branch question (250 kW frame vs 355.5 kW 2C absorbed post-Q12) remains THE open item — drawings add no power data |

Reading overall: Zenith substantiates its offer at a level (foundation
loads, civils, embedded plates, bolt schedules) that de-risks the
SCHEDULE and INSTALLATION axes of the evaluation grid — none of which
replaces the missing gates (efficiency guarantees, witnessed tests,
setting evidence).

## 5. Status

RECEIVED — under technical evaluation; NOT conforming as quoted (old
machine list). Candidate next step (client's call): send Zenith the
drafted RFQ datasheets for a re-quote on the CURRENT configuration.

---
*Extraction: NOEZYS reading of the archived PDF (assistant-read, no
engine run); the original prevails in any discrepancy. Produced by
NOEZYS.*
