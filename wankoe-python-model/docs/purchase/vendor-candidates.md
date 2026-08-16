# Vendor Candidate Selection — 13 Purchase Machines

**by NOEZYS** — issued 2026-08-16 (client order: five real catalog candidates per
machine, best-adapted model selected each time)

**Basis and honesty statement.** Candidates were swept from manufacturers'
PUBLIC catalogs on 2026-08-16 (source URL per candidate; real designations
only, none invented). These are catalog-level matches, NOT offers: catalog
capacities carry their own bases (noted where published) and no catalog
guarantees the WANKOE duty points — final selection remains gated by the
acceptance and guarantee tests already written into the 13 datasheets
(vendor gradation test, 1.5 mm gap held under load, certified apertures,
imperfection guarantees, eta_cl trial, capacity tests). Duty specs used are
the committed datasheets, which carry every client decision through the
2026-08-15 error hunt (CR.5011 172.0 quarry bisection, SR.5007 rain minima,
RC.2 2×25, SP.36 fan 420 m³/h, VSMA fine-screen minima).

## Selection summary (best pick per machine)

| Tag | Machine | **Best pick** | Fallback |
|---|---|---|---|
| CR.5009 | Primary crusher 250 t/h, F80 251 quarry | **MMD 500 Series twin-shaft sizer** | thyssenkrupp RollSizer DRS |
| SR.5007 | Double-deck 35/20, rain duty 9.1/9.6 m² | **Haver & Boecker Niagara F-Class 8×20 ft** (14.6 m²/deck) | Metso CVB2060 |
| CR.5011 | Secondary impactor, 90 t/h wet @ CSS 18 | **HAZEMAG APS 1010-class HSI** (the reference machine) | Metso NP1110 |
| SR.5105 | 6 mm wet reclaim screen, ≥ 3.8 m² | **Binder+Co BIVITEC ~1.3×4.0 m flip-flow** | IFE TRISOMAT |
| SR.5111 | 1.7 mm open screen, 100 t/h wet bed | **Binder+Co BIVITEC ~1.5×5.0 m** (bed-load sized) | Hein Lehmann LIWELL LF |
| CR.5113 | AgLime loop fine impactor, 87↔360 kW | **Stedman H-Series multi-row cage mill** | Hazemag HNM hammer mill |
| SR.5115 | 1.7 mm closed loop, ≥ 19.1 m² | **Binder+Co BIVITEC large frame ~22.4 m²** (Banana) | Hein Lehmann LIWELL LF 3.0-8.82 (26.5 m²) |
| RC.1 | Smooth rolls 32 t/h, gap 8 | **Sturtevant 30×16 two-roll** | McLanahan Black Diamond |
| RC.2 | Smooth rolls 2×25 t/h, gap 3.4→1.5 | **2 × Gundlach NANOSIZ-R (TerraSource)** | NANOSIZ-R HC (single frame) |
| SC.A | Double-deck 8/3.75, ≥ 6.0/7.0 m² | **Metso CVB1845** (8.1 m²/deck) | Haver Niagara F-Class 6×16 |
| SC.B | Double-deck 2/1.5, ≥ 7.4/7.5 m², RPN 252 | **Rhewum WA direct-excitation** | Binder+Co BIVITEC e+ |
| SP.36 | Air classifier 65 µm + fan 420 m³/h | **Netzsch CFS size-30 (ConVor)** — see architecture question | Hosokawa Ventoplex C25V (full-stream) |
| CL.38 | Product cyclone d50 4.2 µm | **CECO Fisher-Klosterman XQ miniature** | Vendor-packaged cyclone with SP.36 (single-source) |

## Three findings the catalogs forced into the open

1. **SP.36 feed architecture must be ruled before RFQ.** No dynamic
   classifier that runs on the client-ruled 420 m³/h fan can mechanically
   ingest the 23.2 t/h fines stream — the air-coherent frame (Netzsch CFS 30,
   catalog air window 210–455 m³/h) takes ~0.4 t/h and operates as an
   air-swept EXTRACTION stage (consistent with the engine's Φ<65 µm ≈ 0.006
   and the fan spec). Every machine that swallows the full stream
   (Ventoplex C25V: 24 t/h, catalog point at 63 µm) uses an internal fan —
   making the purchased 420 m³/h fan AND the CL.38 cyclone redundant
   (flowsheet change). CLIENT ARBITRATION REQUIRED (question pending).
2. **The RC.2 1.5 mm gate is nobody's catalog guarantee.** No manufacturer
   publishes "smooth rolls hold 1.5 mm within 0.1 mm under load" as
   standard. The catalog evidence narrows to Gundlach NANOSIZ-R (1–2 mm
   limestone product documented), Sturtevant 20×14 (1/16" setting printed
   but drive undersized) and Händle Alpha II (0.5 mm hydraulic gap — on
   clay). The ±0.1 mm-under-load requirement must be the witnessed
   section-7.1 test for EVERY bidder, Gundlach included.
3. **SC.A/SC.B shared-cartridge FMECA requirement cannot survive the SC.B
   technology choice.** The sharpness + certified-aperture gates (RPN 252)
   point to direct-excitation (Rhewum WA — static housing, no exciter
   cartridge); no cartridge interchange with a circle-throw SC.A exists.
   Either the client re-scopes the interchange requirement to the zone-1.2
   BIVITEC family (recommended — 3 screens, one cartridge), or the family
   answer for SC.A+SC.B is IFE (weaker on the SC.B sharpness gate).

---

## CR.5009 — Primary (250 t/h wet, gap 60, F80 181/251 mm, restart under load)

| # | Candidate | Key catalog facts | Fit |
|---|---|---|---|
| 1 | **MMD 500 Series twin-shaft sizer** | ~600 t/h aggregates; reference 350 mm in-feed → 80 mm at 200 t/h on limestone/clay; twin 110 kW | Teeth grab oversize positively — **dissolves the 251 mm nip finding**; soft/wet limestone is sizer home turf |
| 2 | Komatsu MVT-II 600 sizer | ≤ 1 000 t/h; feed ≤ 250 mm; product 25–65 mm | Feed/product window ≈ the duty; 250 mm max feed marginal vs quarry top size |
| 3 | thyssenkrupp RollSizer DRS (CenterSizer) | Series to 1 800+ t/h; soft/sticky/medium-hard incl. limestone | Low-fines primary sizer, European supply |
| 4 | McLanahan DDC-Sizer | Primary/secondary friable low-silica; feed ≤ 1 200 mm; application-sized | Segmented bolt-on teeth (FM1), direct drive |
| 5 | TerraSource Gundlach Multi-Roll S-Series | 10–6 000+ t/h; feed ≤ 1 200 mm; 4:1 single stage | Closest to the toothed double-roll wording; low fines |

**Best pick — MMD 500 Series**: the only shortlisted machine with a
documented like-for-like soft-limestone reference above our top size; the
"F80 > 150 mm nip" standing alert disappears by design instead of being
contracted around; segments bolt-on per FMECA; twin drives give
restart-under-load torque. Vendor to quote the smallest drive package
(installed 220 kW ≫ absorbed 96.6 kW).
**Open**: gradation table 20–60 mm settings on WANKOE stone; guaranteed max
lump vs the real quarry top size; segment life; adjustment concept mapped to
the 5 mm-step gap indication; 7–12 % moisture handling.
Sources: mmdsizers.com; komatsu.com (sizers); thyssenkrupp-polysius.com
(roll sizer); mclanahan.com (sizers); terrasource.com (multi-roll).

## CR.5011 — Secondary impactor (guarantee 90 t/h wet @ CSS 18, 132 kW)

| # | Candidate | Key catalog facts | Fit |
|---|---|---|---|
| 1 | **HAZEMAG APS 1010-class HSI** | ~100–125 stph nominal, real 75–90 t/h limestone, 132 kW; hydraulic aprons | **It IS the reference machine** — the whole capacity arbitration was closed on its documents |
| 2 | Metso Nordberg NP1110 | 1 020×820 inlet, 160 kW | One notch above the duty; hydraulic setting for CSS 30↔18 |
| 3 | Sandvik CI412 Prisec | Two-curtain, primary/secondary configurable | Fine-CSS secondary capability |
| 4 | SBM SMR series reversible | 100–300 t/h medium-hard limestone | Fine tertiary product; reversible rotor doubles bar life |
| 5 | Stedman Grand-Slam GS-4860 | 100–150 stph typical secondary | Mid-range fit; easy bar access |

**Best pick — HAZEMAG APS 1010-class**: least re-qualification risk (the
90 t/h wet /CSS 18 guarantee point and the 172.0 t/h mode-1B bisection were
built against its own figures); routine hydraulic CSS changeover. Fallback
Metso NP1110 if Hazemag declines the CSS-18 guarantee.
**Open**: THE item = written capacity guarantee at CSS 18 / v 30 wet;
gradation value tables CSS 10–30 × v 30–60; blow-bar metallurgy + balancing;
changeover time.
Sources: hazemag.com; metso.com (NP series PDF); rockprocessing.sandvik;
sbm-mp.at; stedman-machine.com.

## CR.5113 — AgLime loop fine impactor (2A 87 kW / 2C 348–360 kW, P80 0.95 mm)

Honesty: 93 t/h closed-loop to 1.7 mm is FINE crushing — cage mills / fine
hammer mills are the catalog home, not classic HSI at CSS 1 mm.

| # | Candidate | Key catalog facts | Fit |
|---|---|---|---|
| 1 | **Stedman H-Series multi-row cage mill** | ≤ 240 stph aglime/fertilizer; state-aglime specs met in OPEN circuit; two counter-rotating cages, EACH on its own drive | **The aglime reference machine type**; native dual-motor answers the 87↔360 kW split (FM1 RPN 224) |
| 2 | Williams Reversible Impactor | AgLime/limestone line; fine-end ~1–5 HP/stph consistent with 348 kW | Proven aglime; grate control |
| 3 | HAZEMAG HNM Novorotor | Fine crushing/mill-drying of limestone | European; mill-drying interesting vs rain |
| 4 | Metso Barmac B7150SE VSI | 110–420 tph; dual drive 260–400 kW | Power story native; PARTIAL on product (no CSS, loop must be re-run) |
| 5 | TerraSource Pennsylvania Reversible Impactor | ≤ 35:1 reduction, limestone listed | High-ratio one-pass fine impact |

**Best pick — Stedman H-Series**: aglime 95 % < 1.7 mm in open circuit means
margin (not risk) in our closed SR.5115 loop; dual-drive splits the 2C
demand; cage speed/row config = the 2A/2C adjustability; wet/sticky capable.
The soft-rock "hold the motor order" ruling is respected — Stedman sizes
drives per gradation test.
**Open**: power/gradation curves at BOTH duty points vs the engine's
348/211 kW (the decisive item before any motor order); guaranteed t/h per
kW step (branch 2); cage wear at 679 h/y campaigns; PT100s/current signals;
wet-feed derate; VFD dual-drive covering both points.
Sources: stedman-machine.com; williamscrusher.com; hazemag.com;
metso.com (Barmac); terrasource.com.

## RC.1 — Smooth rolls stage 1 (32 t/h dry, gap 8, D6 sharpness)

| # | Candidate | Key catalog facts | Fit |
|---|---|---|---|
| 1 | **Sturtevant 30×16 two-roll** | 17–76 stph (friable, max-range basis); product 6.4–38 mm; 2×11 kW; spring-cushioned rolls | Only PUBLIC table bracketing the exact duty; smooth pure compression = D6 bet; overload release built in |
| 2 | TerraSource Gundlach 2000 Series 2030S/2040S | Lime/limestone ≤ 55 MPa; Nitroil tramp protection; exchange rolls | FM1/EM.09 served; smooth shells = vendor variant (standard toothed) |
| 3 | McLanahan Black Diamond | Products to −6 mm documented; smooth shells offered for fine low-fines product | Custom-engineered; −6 mm guarantee culture |
| 4 | J.C. Steele Smooth Roll | ≤ 70 t/h @ 3.2 mm gap; soft limestone listed | Speed differential adds shear — S_att/D6 risk (demoted) |
| 5 | CPM Roskamp 1600 Series | Limestone/salt; automated gap | Corrugated standard — smooth = variant |

**Best pick — Sturtevant 30×16**: table covers gap 6–10 mm and 32 t/h;
zero-differential smooth compression is the right sharpness bet at 0.8 pt D6
margin; installed 22.4 kW at the 22 kW datasheet minimum. Capacity figure is
max-range on generic friable stone — the 32 t/h × 2 h witnessed test stays
contractual.
**Open**: n_comp/S_att via the gradation test (gaps 6–10); shell life;
drive confirmation.
Sources: sturtevantinc.com (Size Reduction PDF); terrasource.com/Astec
Gundlach 2026 brochure; mclanahan.com; jcsteele.com; onecpm.com.

## RC.2 — Smooth rolls stage 2 (2 × 25 t/h, gap 3.4 → 1.5 mm HELD ±0.1 mm)

| # | Candidate | Key catalog facts | Fit |
|---|---|---|---|
| 1 | **TerraSource Gundlach NANOSIZ-R standard** | ≤ 36 t/h fine-grinding limestone at 1–2 mm product; close-clearance bearings "for tight product size control"; chilled-iron rolls | **Only machine documenting BOTH gates**: 1–2 mm on limestone AND ≥ 25 t/h per frame with comp_lam margin |
| 2 | Gundlach NANOSIZ-R HC | ≤ 120 t/h same basis | Single-frame fallback (client twin-unit decision says no, unless twins fail the test) |
| 3 | Sturtevant 20×14 | Product to 1.6 mm printed; 2×7.5 kW | Only US table with a 1.6 mm setting; drive undersized vs 30 kW/unit — engineered variant |
| 4 | Händle ALPHA II hydraulic fine roller mill | **Min gap 0.5 mm**, closed-loop hydraulic gap hold | The gap-hold TECHNOLOGY proof — but catalog basis is clay; abrasion-duty variant required |
| 5 | CPM Roskamp 1200/1600 | Limestone documented; gap automation | Smooth-shell + P80 2.6 confirmation needed |

Near-miss: J.C. Steele — 1.6 mm PRODUCT but practical min gap 3.2 mm: fails
the 1.5 mm gate as cataloged.

**Best pick — 2 × Gundlach NANOSIZ-R standard (18"×40" class)**: documents
the 1–2 mm limestone product and 36 t/h per frame (margin over 25 t/h vs the
comp_lam ±7.5 % band); close-clearance bearing design is the catalog feature
mapping to the ±0.1 mm hold; chilled-iron rolls + exchange practice = FM1
staggered campaigns; two identical frames = the client's interchangeability
decision, HC as the documented uprate path.
**HONESTY (client must know)**: nobody's catalog guarantees "1.5 mm held
±0.1 mm under load". The witnessed section-7.1 test is mandatory for every
bidder, Gundlach included.
**Open**: n_comp/S_att and comp_lam via the gradation test (gaps 1.5–4.5) —
carries the D6 margin and the mode-F loop stability; roll wear at 44 t/h
regrind; installed kW (catalog silent); tramp thresholds for EM.09.
Sources: terrasource.com (Nanosiz-R); sturtevantinc.com; haendle.com;
onecpm.com; jcsteele.com.

## SR.5007 — Double-deck 35/20 (RAIN duty ≥ 9.1/9.6 m², 324.5 t/h wet)

| # | Candidate | Key catalog facts | Fit |
|---|---|---|---|
| 1 | **Haver & Boecker Niagara F-Class 8×20 ft** | 14.6 m²/deck; double-eccentric four-bearing shaft = **constant stroke under load** | The rain gate: stroke does not collapse as bed mass rises; Haver is the wire-cloth maker (certified apertures, imperfection guarantee culture) |
| 2 | Metso CVB2060 | 12.0 m²/deck; wet processing named | Family pooling fallback |
| 3 | Sandvik SC/SA 2160 class | 12.6 m²/deck; wash option | Large installed base |
| 4 | Terex Cedarapids TSV6202/03 | 11.2 m²/deck; triple-shaft oval stroke | Anti-pegging in wet 20 mm |
| 5 | Schenck/Sandvik LinaClass SLK | to 14.4+ m²; DF twin exciter | Exciter-cartridge architecture per FMECA |

**Best pick — Niagara F-Class 8×20 ft** (rationale above; 14.6 ≫ 9.6 m²
leaves room for the vendor's own wet factor).
**Open**: vendor V-factor/bed-depth at BOTH duty points (dry + rain 0.75
[H]); binding imperfection guarantee (replaces I = 0.15); panel ranges;
condition-monitoring pads.
Sources: haverniagara.com (+F-Class PDF); metso.com; rockprocessing.sandvik;
terex.com; Schenck LinaClass PDF.

## SR.5105 — 6 mm wet reclaim (≥ 3.8 m², moisture spikes ~13.7 %)

Candidates: **Binder+Co BIVITEC ~1.3×4.0 m (pick)**; IFE TRISOMAT;
Hein Lehmann LIWELL LF; Spaleck flip-flow; Metso Compact CVB1540 with
self-cleaning media (conventional fallback).
**Best pick — BIVITEC**: blinding resistance at a wet 6 mm cut is the
flip-flow design case (50 g mat acceleration, no spray water available);
4–8 mm adjustability = mat exchange; **family argument**: one BIVITEC family
across SR.5105/5111/5115 closes the FMECA shared-exciter-cartridge
requirement structurally.
**Open**: efficiency guarantee at 100 t/h wet; blinding endurance run on
client material at 13.7 %; common drive cartridge confirmed.
Sources: binder-co.com; ife-bulk.com; heinlehmann.com; spaleck-us.com;
metso.com.

## SR.5111 — 1.7 mm open (≥ 2.1 m² cut duty; bed 100 t/h wet governs)

Candidates: **Binder+Co BIVITEC ~1.5×5.0 m ≈ 7.5 m² (pick — sized on the bed
load, not the cut floor)**; Hein Lehmann LIWELL LF 1.5-5.67 (8.5 m²);
IFE TRISOMAT; JOEST OSCILLA; Spaleck. Flip-flow is the only credible
technology class at a moist 1.7 mm cut (the project's own rain physics).
**Best pick — BIVITEC**: low dynamic loads of the dual-mass frame serve the
FM4 structural-fatigue finding (the 167 % loop resize); fine PU mats
quick-change with 2 spare sets; family cartridge with 5105/5115.
**Open**: **bed-depth sizing at 100 t/h wet = the real area** (catalog floor
is not the answer); imperfection guarantee at both duties; fatigue calc for
the 2C bed; mats 1.5–2.0 mm in 0.1 steps.
Sources: as above + joest.com.

## SR.5115 — 1.7 mm closed loop (≥ 19.1 m², 92.5 t/h wet)

Candidates: **Binder+Co BIVITEC large frame ~2.8×8.0 m = 22.4 m², Banana
execution (pick)**; Hein Lehmann LIWELL LF 3.0-8.82/28 ED (26.5 m² — the
largest documented single flip-flow deck, strong alternate); JOEST OSCILLA
large; Rhewum WA (only if feed proven dry); Derrick FTB banks (modular
high-frequency, 650 t/h limestone dry reference).
**Best pick — BIVITEC large frame**: one of only two catalog lines
documenting a SINGLE deck above the 19.1 m² client floor (to 42 m²) — the
closed-loop mass balance stays a one-machine affair; flip-flow physics at
~7 % moisture; Banana variant for the ~78 % oversize recycle; family
cartridge argument completes.
**Open**: vendor bed-depth at the 2C loop equilibrium (may exceed 19.1 —
the floor is a floor); imperfection at 2C duty; loop stability 4 h; mat life
at heavy near-mesh.
Sources: binder-co.com; heinlehmann.com (+ LIWELL brochure); joest.com;
rhewum.com; derrick.com (FTB brochure).

## SC.A — Double-deck 8/3.75 dry (≥ 6.0/7.0 m²)

Candidates: **Metso CVB1845 = 8.1 m²/deck (pick)**; Haver Niagara F-Class
6×16 (8.9 m²); IFE circular-motion 1.8×4.5 (80 000 h bearing culture);
McLanahan MAX 5×16 (bolted A572 frames); Terex Cedarapids TSV6162.
**Best pick — CVB1845**: both minima cleared on one compact standard frame
with 15–35 % headroom; modular media covers 6–10 / 3.5–4.5 mm adjustability
with anti-pegging options on the 3.75 mm deck (FM2).
**Caveat (stated honestly)**: the FMECA SC.A/SC.B shared-cartridge ask
cannot be met if SC.B goes Rhewum (no cartridge on a static direct-excitation
machine) — see finding 3 above.
**Open**: bed-depth at 92 t/h mode F; efficiency guarantees on both decks
(the loop has no slack); cartridge-interchange re-scope; anti-pegging media
life.
Sources: metso.com/pilotcrushtec; haverniagara.com; ife-bulk.com;
mclanahan.com (+ MAX brochure); terex.com.

## SC.B — Double-deck 2/1.5 dry (≥ 7.4/7.5 m², TOP RPN 252, certified apertures)

Technology statement: at 2/1.5 mm dry with heavy near-mesh, circle-throw is
the wrong class — high-frequency direct excitation (sharpest cut, certified
woven wire) vs flip-flow (best anti-pegging, PU mats certify less tightly).

Candidates: **Rhewum WA (pick)** — static housing, high-speed rocker shafts
excite the cloth directly, certified woven wire (ISO 9044-class per-batch
aperture certificates), clamped quick-change cloths; Binder+Co BIVITEC e+
double-deck 2.0×4.0 (8 m²/deck) — the anti-pegging alternate;
Derrick FTB double-deck banks (Polyweb urethane, 38 µm–3 mm dry);
Spaleck 2-deck flip-flow; JOEST OSCILLA double-deck. (Regional alternate:
General Kinematics bivi-TEC, licensed BIVITEC.)
**Best pick — Rhewum WA (two-cut execution ≥ 7.4/7.5 m² per cut)**: the
RPN-252 requirement (per-batch measured-aperture delivery certificates) is
industry-standard ONLY on woven wire; direct cloth excitation gives the
sharpest d50 at 2.0 mm — the only credible basis for a sharpness guarantee
that preserves the 0.8 pt D6 margin; static body decouples the top-RPN
machine from structural fatigue. If vendor trials show pegging (FM3,
RPN 105) dominates certification, fallback BIVITEC e+ — but 252 > 105, so
Rhewum stands.
**Open**: sharpness/imperfection guarantee at mode-G duty with real d50 vs
nominal aperture (coupled to the RC gradation test); near-mesh bed sizing at
50 t/h mode F; certificate format per panel; ball-deck anti-pegging demo;
formal re-scope of the SC.A/SC.B cartridge requirement.
Sources: rhewum.com; binder-co.com (BIVITEC e+); derrick.com;
spaleck-us.com; joest.com; generalkinematics.com.

## SP.36 — Air classifier 65 µm (fan ≥ 420 m³/h VFD) — ARCHITECTURE PENDING

Candidates: **Netzsch CFS size-30 ConVor (pick, conditional)** — d97 window
10–250 µm referenced on limestone (covers the whole 45–150 µm band), catalog
air window **210–455 m³/h brackets the ruled 420 fan**, VFD wheel = in-run
cut lever, ceramic wear options, witnessed Hanau lab trials (the eta_cl
guarantee path); Hosokawa Ventoplex C25V — 24 t/h full-stream, catalog point
5.6 t/h fines at df97 63 µm on limestone, internal fan (**makes the 420 m³/h
fan and CL.38 redundant**); Hosokawa Stratoplex ASP 315 — complete with fan/
cyclone/filter but 2 500 m³/h (6× the ruled fan); Sturtevant Whirlwind —
38–150 µm band, internal fan, vane adjustment (not an in-run VFD lever);
Comex ACX small frames — 3–150 µm, European. (Set aside: Alpine ATP —
caps ~100–120 µm; Netzsch CFS/HD-S — too fine; Metso GI/gyrotor — misses
45 µm / air far above spec; RSG — quote-only.)
**Best pick — Netzsch CFS size-30**, conditional on the air-swept-extraction
reading (finding 1): its inlet takes ~0.4 t/h, coherent with the engine's
UltraFin duty (0.067–0.104 t/h) and the ruled fan — NOT with a mechanical
23.2 t/h passage. If the client rules full-stream passage, the honest pick
flips to Ventoplex C25V and the fan + CL.38 leave the flowsheet.
**Open**: the architecture ruling (client); eta_cl trial on WANKOE fines
(if 50–65 %, engine re-runs the balance before contract); fan-curve
stability at 130–210 m³/h turndown; acceptance sieve/laser on both products.
Sources: grinding.netzsch.com (+CFS/HD-S PDF); easyfairsassets (Alpine
brochure); hosokawa-alpine.com; hmicronpowder.com; sturtevantinc.com
(Whirlwind bulletin); comex-group.com; metso.com; airclassify.com.

## CL.38 — Product cyclone d50 4.2 µm (~480 g/m³ product loading)

Candidates: **CECO Fisher-Klosterman XQ miniature frame (pick)** —
high-efficiency series in miniature sizes, engineered grade-efficiency
curves (= the value table golden rule 3), refractory/ceramic lining options;
Van Tongeren custom high-efficiency (recovery to 5 µm, custom liners/ports —
the FMECA wish-list is their core offer); Nederman MikroPul small-diameter
(catalog pairs cyclone + fabric filter = exactly the missing tail
architecture, one vendor for both); vendor-packaged cyclone with the SP.36
award (single guarantee across cut + grade efficiency + tail loading —
equal-merit if Netzsch/Hosokawa wins SP.36); Aerodyne SplitStream
(7–10 µm class — below spec, listed for the re-entrainment-resistant
geometry only). (Set aside: Kice CK — 4× oversize; Donaldson/Camfil — not
product cyclones, but the natural vendors for the missing polishing bag
filter.)
**Best pick — FKI XQ miniature, ceramic-lined** — with the single-source
package as equal-merit alternative if SP.36 goes to Netzsch.
**Open**: measured grade-efficiency at 133/207 m³/h (confirms Lapple
4.23 µm); **tail dust loading g/m³ at duty** = the sizing input of the
missing sub-4 µm bag filter (candidates Donaldson Torit / Camfil); ceramic
liner life at ~480 g/m³, 3 610 h/y; dP baselines.
Sources: cecoenviro.com (FKI brochure); van-tongeren.com;
nedermanmikropul.com; dustcollectorhq.com (SplitStream).

---
*Provenance: candidates compiled from manufacturer public catalogs
2026-08-16 by four parallel NOEZYS sourcing reviews (crushers / roll
crushers / screens / air classification), duty specs = the committed
datasheets at engine commit dbc96d7 (all five error-hunt arbitrations
included). Catalog figures are assistant-compiled from vendor documents,
NOT engine output; capacity bases quoted where published; three makers
publish application-sized (non-tabulated) capacities and are flagged as
such in the sections above. Produced by NOEZYS.*
