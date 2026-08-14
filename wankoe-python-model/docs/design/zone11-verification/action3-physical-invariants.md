# Zone-1.1 internal confidence program — Action 3: physical invariants

**Date:** 2026-08-14 · **Mechanism:** two layers. (1) The full stress
campaign (scripts/stress_test.py: 500 seeded random draws over every
machine-setting range + every setting at min/max + degenerate feeds +
brutal rates) re-run at today's HEAD — it now exercises the ADOPTED C1
zone-1.3 circuit, which the original 2026-08-08 campaign predated.
(2) A NEW permanent module tests/test_physical_invariants.py proving the
engine moves in the right DIRECTION, not just that it conserves mass.

## Verdict: PASS — 580/580 stress runs clean, 9/9 direction laws hold

| Physical law (engine-checked) | Result |
|---|---|
| Coarser feed -> higher KFS Yield (the quarry lever's sign) | ✅ strict |
| Wider CR.5009 gap -> higher yield (why g sits at max) | ✅ |
| Wider CR.5011 CSS -> higher yield (why CSS sits at max) | ✅ |
| Slower impactor -> higher yield (why v = 30 was adopted) | ✅ |
| Screen imperfection degrades in-cut monotonically; near-perfect screen -> in-cut > 96 % | ✅ strict chain |
| M3 limit: near-perfect screen splits a mono-class > 99.9 % correctly both ways | ✅ |
| M1 limit: all-fine feed bypasses the crusher unchanged | ✅ exact |
| M6 limit: feed at target moisture -> zero evaporation | ✅ exact |
| M2 floor: product coarser than feed -> zero energy, never negative | ✅ |
| Stress: 500 random + extremes + degenerate + brutal (580 runs): balances closed, curves monotone 0-100 %, all values finite, no negative tonnage/power | ✅ 0 failures |

Every optimization decision of the project (g max, CSS max, v min,
quarry-coarsening) now rests on an ENGINE-PROVEN monotonicity, not on a
plausible narrative.

**Confidence budget: physical-behavior component (3 pts) CLOSED —
meta-score 83 % → 86 %.**
