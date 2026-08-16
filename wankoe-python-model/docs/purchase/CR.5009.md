# PURCHASE TECHNICAL DATASHEET — CR.5009

**Toothed double-roll primary crusher — zone 1.1**
Issued 2026-08-15 (client order of the same day: purchase datasheets for the 13 major process machines) — produced by NOEZYS.

## 1. Identification and role

| Item | Value |
|---|---|
| Tag | CR.5009 |
| Type | Toothed double-roll crusher |
| Zone / duty | 1.1 — primary crushing of the pivot feed (KFS + 0/20 chain) |
| Operating modes | 1A (KFS production), 1B (0/20 stock campaigns, auto-rule) |
| Annual running hours (defaults) | 1 366.6 h effective (zone 1.1, Saturday regime, ceiling 2 400 h clock) |
| Criticality | SINGLE POINT for the whole zone-1.1 chain (firm KFS 85 kt/y) |

## 2. Process duty (engine runs, 2026-08-15)

Feed rates follow the total-flow rule (client 2026-08-14): wet basis primary, dry solids in parentheses (wet = dry x 1.07527 at 7 % feed moisture).

| Quantity | Mode 1A | Mode 1B |
|---|---|---|
| Feed rate, wet (primary) | **250.0 t/h** | **172.0 t/h** (re-bisected on the quarry-target curve, client 2026-08-15) |
| Feed rate, dry solids | 232.5 t/h | 160.0 t/h |
| Feed F80 | 180.6 mm (measured belt-cut curve) | 180.6 mm |
| Product P80 | 42.7 mm | 42.7 mm |
| Specific energy W | 0.312 kWh/t | 0.312 kWh/t |
| Net power P_net | 72.5 kW | 54.0 kW |
| Absorbed power (P_net / eta_m 0.75) | **96.6 kW** | 66.5 kW (feed 172.0, client 2026-08-15) |

## 3. Settings and required adjustability (nothing hardcoded — client rule 1)

The purchased machine must offer at least the following adjustment ranges without mechanical rework:

| Parameter | Unit | Range required | Reference setting |
|---|---|---|---|
| Gap g | mm | 20 - 60 | **60** (client 2026-08-13, 0/20-balance optimization) |
| Product shape (RR uniformity n, informative) | - | — | 1.35 (model M1; vendor gradation table to confirm) |

## 4. Capacity and sizing requirements — CLIENT DECISIONS 2026-08-16 (10-expert panel, 10 questions arbitrated)

- **MACHINE CLASS: twin-shaft toothed SIZER (Q3)** — supersedes the as-built toothed-roll designation. Positive tooth engagement of the design lump; low-fines crushing is a SELECTION CRITERION (Q1).
- **CONTRACTUAL PRODUCT CURVE (Q1)**: at the 0/60 setting the vendor GUARANTEES maximum preservation of the 20/35 mm band and a cap on fines < 20 mm, verified by the witnessed gradation test on WANKOE limestone. The offer is evaluated on its curve, not its capacity alone (KFS Yield: each point ≈ 12 kt/y of landfill).
- **Feed top size — STANDING ALERT CLOSED (Q2+Q3)**: the quarry GUARANTEES max lump ≤ 250 mm (ripping + face scalping — to be added to the quarry-works specification), and the sizer class engages that lump positively. `max_feed_size_mm` 150 → 250 in the data; the measured F80 181 mm is now inside the limit and the design check returns **machines_hold: TRUE** for the first time since 2026-08-11. Residual note: the encoded quarry-target curve tail gives F80 251 mm, marginally above the guarantee — the curve top end [H] is to be re-shaped to the 250 mm cap at its next revision (engine alert deliberately kept live on that curve until then).
- **Throughput**: continuous 250 t/h wet (232.5 t/h dry) at the 60 mm setting on WANKOE limestone (UCS 15-30 MPa, reference 20), plus restart under load (by design of the twin-drive package).
- **Drive (Q6)**: vendor standard twin-drive package accepted — 2 × ~110 kW with soft starters (`installed_power_kW` = 220 in the data); worst-mode absorbed stays 96.6 kW. The vendor quotes its standard package; no minimum-drive engineering requested.
- **Installation (Q5, Q9)**: truck → hopper → apron feeder → CR.5009, machine OUTDOOR (weather execution: IP-rated drives, covered lubrication, walkway protection), greenfield civil works (no as-built envelope constraint — the vendor optimizes feed height and discharge).
- **Spares (Q7)**: initial CRITICAL SPARES KIT is a priced, mandatory line of the offer — one full set of tooth segments + one shaft.
- **Tender scope (Q8)**: RFQ to PREMIUM BRANDS, Western AND Chinese (client emphasis on China) — same specification, same witnessed tests for all bidders; see the CR.5009 selection dossier for the candidate list.
- **Wear-guarantee basis (Q4)**: client-held abrasivity data (silica content, Cerchar/LCPC class) to be supplied and attached to the RFQ — vendor wear-life guarantees are priced against it (EXTERNAL INPUT pending).
- **Tramp protection (Q10)**: metal detector + overband magnet on the feed belt, detection threshold agreed with the vendor — in ADDITION to the machine's internal hydraulic overload relief (ripping operations shed digger teeth; the downstream line is protected too).

## 5. FMECA-derived purchase requirements (docs/design/maintenance/fmeca-register.json, 2026-08-15)

| FM (RPN) | Failure mode | Purchase requirement |
|---|---|---|
| CR.5009-FM4 (175) | Tramp / uncrushable jamming | **Tramp-metal protection on the zone-1.1 pivot feed** (belt magnet + metal detector, EM.09-adjacent — FMECA design recommendation: no detection exists upstream of this machine); crusher supplied with an overload/relief system and a safe jam-clearing procedure and access |
| CR.5009-FM1 (168) | Tooth / segment wear (saturated duty) | Bolt-on replaceable tooth SEGMENTS (not welded rolls), wear-resistant metallurgy stated for limestone duty, tooth-profile gauging templates supplied; guaranteed segment life at the 250 t/h wet saturated duty |
| CR.5009-FM2 (140) | Main roll bearing failure | **Bearing temperature probes with trend alarm wired at purchase** (design provision) + vibration measurement access; labyrinth/purged seals against limestone fines ingress |
| CR.5009-FM5 (100) | Gap / setting drift | Gap position indication (readable setting, repeatable to the 5 mm step) for the weekly check against the reference g = 60 |
| CR.5009-FM3 (84) | Drive train failure | Gearbox with oil-analysis sampling point; spare coupling element in the initial spares list |

## 6. Open [H] items the vendor must close

- **[H] Vendor gradation curve**: product PSD at gaps 20-60 mm on WANKOE limestone, delivered **as a value table with the interpolation mode declared** (spec golden rule 3). Confirms the M1 model (x80 = g, n = 1.35).
- **[H] Installed power**: vendor motor rating (data slot `installed_power_kW` = null).
- **[H] Wi 12.54 kWh/t [ref.]** pending the site Bond test — vendor to state the power guarantee basis.
- Max feed size / nip capability vs the measured F80 181 mm (section 4 — vendor must state which branch its offer satisfies).

## 7. Acceptance tests and QC criteria

1. **Gradation acceptance test** on WANKOE feed (or witnessed equivalent): product curve at g = 60 within the vendor table tolerance; P80 consistent with 42.7 mm (engine reference).
2. **Capacity test**: 250 t/h wet sustained 2 h at g = 60 without relief-system actuation on in-spec feed.
3. **Power verification**: absorbed power at duty ≤ vendor guarantee; reference engine value 96.6 kW.
4. **Downstream QC tie-in**: the belt-cut PSD at the CR.5009 outlet is the plant's ONLY measurement point — the vendor must accept it as the wear-trend/acceptance measurement basis. KFS envelope (30 % max below / 55 % min in-cut / 15 % max above 20-35 mm) on SR.5007 product is the end criterion the primary's product curve must keep reachable.
5. Bearing temperature and vibration baselines recorded at commissioning.

---
*Engine provenance: commit 5dc5b53, run 2026-08-15, `wankoe_model.scenario.run_scenario` (per-mode photos 1A / forced 1B, weather dry), data `data/default_parameters.json`. Replay: `PYTHONPATH=src python scripts/purchase_datasheet_evidence.py` -> `docs/purchase/purchase-engine-evidence.json`. Motor x1.15 and screen-area margins are assistant-stated sizing hypotheses [H], flagged as such. Produced by NOEZYS.*
