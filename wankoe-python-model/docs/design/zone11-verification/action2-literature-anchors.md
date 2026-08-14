# Zone-1.1 internal confidence program — Action 2: literature anchors

**Date:** 2026-08-14 · **Mechanism:** each model function is confronted
with its source-literature formula evaluated INDEPENDENTLY — every
expected value is hand arithmetic written into the permanent test module
`tests/test_literature_anchors.py` (sources cited), never read back from
the engine.

## Verdict: PASS — 7/7 anchors

| Model | Anchor (source) | Result |
|---|---|---|
| M2 Bond | Worked case Wi 12.74, 25→3 mm → W = 1.520246 kWh/t (Bond third law; Wills) | ✅ exact to 1e-5 |
| M5 | Ecs = v²/7200 is EXACT physics (kinetic energy unit conversion), v=30 → 0.125 | ✅ exact to 1e-12 |
| M5 | JKMRC t10 = A(1−e^(−b·Ecs)) → 5.709755 % (Napier-Munn 1996) | ✅ exact to 1e-5 |
| M3 | Logistic partition quartiles x25/x75 analytic (Reid/Plitt; King Table 7.1) | ✅ engine reproduces both |
| M3 | Sharpness s = ln9/ln(1/(1−I)) = 13.5198 at I=0.15 | ✅ |
| M4 | VSMA effective capacity vs published Factor-A: 29.3 vs 30.8 (20 mm), 41.0 vs 39.5 (35 mm) | ✅ within 5 % |
| M1 | Truncated Rosin-Rammler P_t(x80) = 0.830814 (hand exponentials) + hard truncation at 1.7·x80 | ✅ exact to 1e-5 |

## Two findings, disclosed

1. **Test-side arithmetic error caught by the engine** (M1): a first
   4-digit hand evaluation gave 0.830783; the engine said 0.8308142; the
   high-precision recomputation confirmed THE ENGINE (0.830814). The
   independent check corrected the checker — recorded verbatim in the
   test docstring.
2. **M3 attribution nuance quantified** (pre-existing, now numeric): with
   the spec's prescribed sharpness formula, the partition curve's CLASSIC
   imperfection (d75−d25)/(2·d50) is sinh(ln(1/(1−I))/2) ≈ **0.081 when
   I = 0.15 is input** — the implemented screens are ~2x sharper than a
   classic I = 0.15 screen (close to Karra 1979's fixed-sharpness family).
   Spec convention, client-arbitrated 2026-08-08; a reviewer sees it
   stated, not hidden. Belongs to the Q3 sieve-test closure.

**Confidence budget: transcription component (4 pts) CLOSED —
meta-score 79 % → 83 %.**
