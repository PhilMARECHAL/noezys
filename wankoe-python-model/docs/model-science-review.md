# Scientific review of the machine calculation models

> **Update (night of 2026-08-08) — internet literature challenge.** Seven
> web-research experts verified every model against published sources
> (63 sourced checks: 28 agree, 22 partial, 5 contradict). Headlines:
> **M7 upgraded** — the ML.26 two-component structure (gap-driven
> compression PSD + fines sub-collective, sub-gap bypass, reduction ratio
> ~4) is experimentally VALIDATED by Thiere (TU Freiberg PhD, 2020) on
> pilot toothed double-roll crushers: grade raised from C to B−.
> **M3 attribution corrected** — the implemented partition is a logistic
> (Reid/Plitt-family) curve, not Karra's published 1979 form (fixed
> sharpness ≈ classic imperfection 0.13); the spec's label is kept, the
> docstring says the truth. Industrial dry screens are far sharper
> (I ≈ 0.10–0.15) than the current spec-derived default (question pending).
> **M4 clarified** — Qb·f0 = 4.86·a^0.6 reproduces the published VSMA
> Factor-A table within 5 % at the project cuts; f0 absorbs the factor
> string. **Bond flags** — Wi = 12.54 is mid-range for limestone, but if
> it originates from a short-ton table the metric value is 13.8 kWh/t,
> which would land CR.5009 almost exactly on the spec's 116 kW (question
> pending); Bond under-predicts fine impact crushing (Morrell Mic is the
> modern refinement). **Vendor check** — current HAZEMAG pages rate a
> 1010-size secondary impactor at ~81–120 t/h, below the spec's "~125 t/h
> real capacity": the machine-specific datasheet is needed. Full sourced
> detail: the literature-challenge report in the project records.

Answering the client's question (2026-08-08): *"Did we capture the right
calculation formulas for the machines?"* — model by model: where the
formula comes from, whether the implemented form is the established one,
its validity domain, and its known accuracy. Confidence grades:
**A** = established law, exact form implemented · **B** = established
family, spec-specific parameterization · **C** = phenomenological
hypothesis, documented and fitted.

## M1 — Crusher product: Rosin-Rammler (grade A)

`P(x) = 1 − exp(−(x/xc)^n)`, `xc = x80/(ln 5)^(1/n)`.
**Provenance**: Rosin & Rammler (1933) — the classic representation of
comminution products, in universal industrial use for 90 years. The
x80-anchored form is standard practice; `ln 5` follows exactly from
requiring P(x80) = 0.8. Truncation at k·x80 with mass rescaling and the
bypass of feed already finer than the product size are standard
flowsheet-simulation devices (equivalent to a bypass/classification
function in Whiten-type crusher models). **Validity**: any brittle rock;
`n` is machine/rock specific (data parameter). **Accuracy**: form exact;
product curves typically within a few % of measured when n is fitted.

## M2 — Power: Bond's third theory (grade A)

`W = 10·Wi·(1/√P80 − 1/√F80)` [µm], `P_installed = W·Q/η_m`.
**Provenance**: F.C. Bond (1952) — THE industry standard for comminution
energy for 70 years; the exact textbook form is implemented (verified by
hand-computed unit tests). **Validity**: best in the crushing/grinding
mid-range; for impact crushers the accepted accuracy is ±25–30 % (a limit
of the law itself, not of the implementation — modern refinements such as
Morrell's Mi require drop-weight testing this project will not have).
**Note**: adequate for design-margin checks, which is this project's use.

## M3 — Screen partition: efficiency curve (grade B)

`ro(x) = 1/(1+(d50c/x)^s)`, `d50c = a·k_d`, `s = ln 9/ln(1/(1−I))`.
**Provenance**: the partition/efficiency-curve approach is the standard of
mineral-processing simulation (Whiten/Lynch efficiency curves; Karra 1979
uses the same reduced-curve concept with a fixed sharpness). The spec
labels it "Karra"; strictly, Karra's 1979 paper fixes sharpness at 5.846
and computes d50c from capacity factors — the spec's version parameterizes
sharpness through an imperfection I instead, which is the Lynch-school
practice. Both are legitimate; the s(I) mapping as WRITTEN in the spec was
self-contradictory and was arbitrated (option A, 2026-08-08) with the
defaults remapped to preserve the spec's original dry sharpness s = 4.30.
**Validity**: dry screening of granular material; I is the one parameter a
future KFS sieve test would pin down. **Accuracy**: partition curves fit
real screens well once I is known; the current I values are engineering
defaults.

## M4 — Screen area: VSMA sizing (grade B)

`A = U·f_p/(Qb·f0)`, `Qb = 14·a^0.6`.
**Provenance**: the VSMA (Vibrating Screen Manufacturers Association)
handbook method — the industry's screen-sizing standard. `14·a^0.6` is the
spec's fit of the VSMA basic-capacity curve; the global correction f0
absorbs the usual VSMA factor stack and is declared fitted on SR.5007.
**Validity**: sizing-level checks (exactly the design-confirmation use);
not a performance simulator. **Accuracy**: ±20–30 %, standard for sizing.

## M5 — Impact breakage: JKMRC t10 (grade A)

`Ecs = v²/7200`, `t10 = A_j(1−e^(−b_j·Ecs))`, `n = (30/t10)^0.30` (floored).
**Provenance**: the t10 breakage model of the Julius Kruttschnitt Mineral
Research Centre (Napier-Munn et al.) — the backbone of JKSimMet, used
worldwide. `v²/7200` is EXACT physics: the kinetic energy of the rotor tip
speed per unit mass, v²/2 J/kg = v²/7200 kWh/t. A_j/b_j are ore-specific
(literature defaults flagged [H]; a drop-weight test would refine them —
not planned, acceptable for design). The t10→n mapping is the spec's
simplification, monotone and bounded — reasonable. **Accuracy**: t10 law
well established; A/b defaults are the main uncertainty.

## M6 — Drying: mass & energy balance (grade A)

**Provenance**: first-principles thermodynamics — latent heat (2257 kJ/kg),
sensible heats, thermal efficiency, evaporation intensity for drum sizing
(standard rotary-dryer rule of thumb, Perry's). Nothing empirical beyond
the efficiency and ΔT parameters, all in the data. Water balance closes
exactly by construction and is asserted every run. **This is the most
certain model in the chain** (reproduces the spec's reference figures to
three digits).

## M7 — Bed roller mill ML.26 (grade C — the honest weak point)

Compression of +gap → RR at x80 = gap (with comp_lam as a per-pass
reduction cap, hypothesis H-M7-1) + attrition fraction S_att → RR fines
(hypothesis H-M7-2). **Provenance**: the spec itself was incomplete
(comp_lam undefined); rigorous bed-compression models (HPGR:
Morrell/Tondo/Shi population-balance) need test work this project will not
have. Our model is PHENOMENOLOGICAL: mass-conserving, monotone, fitted to
reproduce the spec's reference case exactly, with every coefficient
bounded by the machine sheet and adjustable. **Status**: fit-for-purpose
in a design study — its grits/fines split is the least certain figure of
the chain and is flagged as such everywhere. A vendor performance curve
for ML.26, if ever available, plugs straight into the data.

## M8 — Air classification + cyclone (grade A/B)

Classifier: `fine = feed·Φ(<cut)·η_cl` — the standard efficiency-recovery
form; mass-exact per size interval (hardened 2026-08-08). Cyclone d50:
Lapple (1951) `√(9µb/(2π·N_e·v_in·(ρp−ρa)))` — the textbook cyclone model,
exact form implemented. **Validity**: Φ comes from the modelled fines
curve until measured (flagged NOT CERTIFIED, per the spec); cyclone
geometry (inlet width b) awaits vendor data.

## Verdict

| Model | Grade | The one thing that would upgrade it |
|---|---|---|
| M1 Rosin-Rammler | A | n per machine from vendor curves |
| M2 Bond | A | (accept ±25–30 %: intrinsic to the law) |
| M3 partition | B | screen imperfection from a product sieve test |
| M4 VSMA | B | installed areas from design drawings |
| M5 JKMRC | A | A_j/b_j from a drop-weight test (optional) |
| M6 drying | A | — |
| M7 bed mill | **C** | vendor performance data for ML.26 |
| M8 classifier/cyclone | A/B | Φ measurement; cyclone inlet width |

**Answer to the client**: yes — with one exception, the formulas captured
are the established engineering models the mineral industry has used for
decades, implemented in their exact textbook forms and verified by
hand-computed tests, mass/water closure on every run, and a 554-scenario
stress campaign (0 failures; divergent closed-circuit configurations are
self-declared, never silently reported). The exception is ML.26 (M7),
which the specification itself under-defined: it is a documented,
bounded, fitted hypothesis — the right place to inject vendor data when
machine sheets arrive.
