# VENDOR OFFERS REGISTER — WANKOE project

**⚠ Zone-1.1 tag equivalence (2026-08-17):** CR.5009 = **CR.5006** and SR.5007 = **SR.5008** (PFD REV15 retag). Offer mappings below predate the retag and use the spec-era tags — same machines; the dispatched RFQ 01 likewise.

**by NOEZYS.** Full-traceability register of every vendor offer received.
Rules: (1) every offer gets a sequential ID OF-nnn and its own folder
with the ORIGINAL files archived UNMODIFIED under `original/` (SHA-256
checksums recorded here — the archive is verifiable without the
assistant); (2) a summary sheet per offer extracts the commercial facts
and maps the items to the machine tags, with every gap vs our RFQ
gates flagged honestly; (3) provenance is recorded — offers received
through the CLIENT's own channel are marked as such (RFQ package
status: PARTIAL RELEASE 2026-08-17 — RFQ 01 only, to Guildco + Zenith
only, dispatched by the client; everything else stays SUSPENDED);
(4) originals are never edited; corrections live in the summary sheets;
(5) individuals are not named in NOEZYS-produced summaries (brand
rule) — the archived originals speak for themselves.

## Register

| ID | Received | Vendor | Quote ref / rev | Items → tags | Amount (ex-VAT) | Validity | Incoterm | Provenance | Status |
|----|----------|--------|-----------------|--------------|------------------|----------|----------|------------|--------|
| [OF-001](OF-001-guildco/OF-001-summary.md) | 2026-08-17 (client upload) | **Guildco Pty Ltd**, Johannesburg, South Africa (reg. 2012/029229/07, VAT 4960314369) | QU-Wankoe 01_v1, dated 2026-08-15 | Inclined screen SI8202 → **SR.5007 candidate** · Toothed roller crusher LPS625-3 → **CR.5009 candidate** | **ZAR 4,312,165.53** (≈ USD 266,183 at the quote's R16.20/USD; ≈ EUR 230–242k [H FX]) | 30 days (expiry 2026-09-13) | **FOB Shanghai** (shipping to South Africa excluded, quoted at order) | Received by the client directly; NOT a response to the suspended NOEZYS RFQ package | RECEIVED — re-quotation of the primary requested via RFQ 01 (partial release 2026-08-17); screen line held |
| [OF-002](OF-002-zenith-plant/OF-002-summary.md) | 2026-08-17 (client upload) | **Shanghai Zenith Mineral Co., Ltd**, Shanghai, China (CE/CQC/ISO9001) | Quotation dated 2026-06-12 ("Jaw Crusher & Impact crusher", old tag list) | C6X100 jaw → "CR.5009" (**wrong class vs Q3 sizer ruling**) · CI5X1315 → **CR.5113** (ex-CR.5107; 250 kW frame vs 348 kW 2C) · S5X2760-3 → **SR.5007 candidate** (meshes 20/40/80) · S5X3075-2T → "SC.5105" (**unmapped**, meshes 2/15) · + 2-y spares USD 89,146 | **USD 412,812 FOB Shanghai** (machines 323,666 + spares; ≈ EUR 357–375k [H FX]) | 90 days (expires ~2026-09-10 — still valid) | CIF Cape Town stated but freight "very unstable" — **CIF not fixed** | Client channel; answers a PRE-REDESIGN enquiry (old tags) | RECEIVED + TECHNICAL ANNEXES 2026-08-17 (GA/foundation/civil drawings, see summary §4bis) — NOT conforming as quoted (old machine list); primary superseded by the RFQ 01 re-quotation request (2026-08-17); other lines held |
| [OF-003](OF-003-zenith-roller/OF-003-summary.md) | 2026-08-17 (client upload) | **Shanghai Zenith Mineral Co., Ltd** (same entity) | CIF quote dated 2025-12-31, 45-day validity | Teeth-roller crusher 2PG-1216CT + control cabinet → **CR.5009 candidate (right class family)** | **USD 163,922 CIF Cape Town** (FOB 153,522 + freight 10,400; ≈ EUR 142–149k [H FX]) | 45 days → **EXPIRED ~2026-02-14** | **CIF Cape Town** (freight fixed USD 10,400) | Client channel; predates the whole model/redesign era | RECEIVED — EXPIRED; re-issue against RFQ 01 REQUESTED (partial release 2026-08-17) |

## Comparison

[comparison-guildco-zenith.md](comparison-guildco-zenith.md) (2026-08-17):
the two head-to-head duels (primary crusher, zone-1.1 screen) on the
common gate frame, normalized prices [H], commercial terms side by side,
Zenith-only items. Pre-re-quote market intelligence, not an award basis.

## File integrity (SHA-256)

| Offer | File | SHA-256 |
|---|---|---|
| OF-001 | original/Quote_QU_Wankoe_01_Rev1.pdf | 1535d8139abbf9c09858a5130aadf40b2ed704765b57a6e6e743e8187643645d |
| OF-001 | original/Roller_Crusher_GA.pdf | 3d0f3bb2fe4eecdb08ae14516a6ead75f26fb9da894931edabb470dbdc82eae9 |
| OF-002 | original/ZENITH_quotation_2026-06-12.pdf | dcd0630da73f45f0bd5625287f524bed025cfaac3b2515d3772605b5a46593ea |
| OF-003 | original/ZENITH_CIF_Cape_Town_roller_crusher_2025-12-31.pdf | 0e9d3cdb51dd6f0fda258ca27807eb09b3292fd0277a8e87bb6fd8de52aa7471 |
| OF-002 suppl. | original/technical-annexes/S5X2760-3_GA_load_civil.pdf | 993a3e5730642242c60c1a684ccc01e0bb10e1d57f85726c92707acf0e472a3f |
| OF-002 suppl. | original/technical-annexes/S5X3075-2T_GA_load_civil.pdf | a33c500302163d198e018abd24ba67088783d317ed5da38d35c06092ba9f3a1d |
| OF-002 suppl. | original/technical-annexes/CI5X1315-III_anchor_loads.pdf | 2714095ca60a4afab0c3b9e2994189ef2339139bdc882898a28108bce6338061 |
| OF-002 suppl. | original/technical-annexes/CI5X1315_cross_section.pdf | c7701417bbe428f5ad8b9c9e283257d8b4d79a3526c3d37d91e99a96265352a5 |

## Evaluation rule

Offers are evaluated against the drafted RFQ frame
([../rfq/00-common-conditions.md](../rfq/00-common-conditions.md)):
pass/fail gates first, then the 30/30/20/10/10 grid — the SAME grid
for every vendor, West and China. An offer received outside the RFQ
process is welcome commercial intelligence but is NOT yet a conforming
bid: its gaps vs the guarantee points and the contractual frame are
listed in its summary sheet and must be closed before any award.

---
*Register opened 2026-08-17 on the client's order (dedicated folder,
total traceability). Produced by NOEZYS.*
