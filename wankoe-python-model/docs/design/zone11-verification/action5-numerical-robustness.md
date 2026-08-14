# Zone-1.1 internal confidence program — Action 5: numerical robustness

**Date:** 2026-08-14 · **Mechanism:** grid refinement (geometric
midpoints, x2 and x4) and loop-tolerance tightening (1e-6 -> 1e-9),
physics untouched (`scripts/numerical_robustness.py`, replayable).

## Verdict: REAL FINDING — the spec grid is not fully converged

| Knob | KFS Yield | KFS in-cut | C1 grits | Balances |
|---|---|---|---|---|
| Base grid (29 meshes) | 24.59 % | 85.39 % | 11.561 t/h | closed |
| Grid x2 (57) | 24.88 % | 82.75 % | 11.253 t/h | closed |
| Grid x4 (113) | **24.91 %** | **82.12 %** | **11.237 t/h** | closed |
| Loop tol 1e-9 | unchanged | unchanged | unchanged | closed |

- The fixed-point loops are numerically clean (1e-9 changes nothing).
- The 29-mesh spec sieve series carries a quantified discretization
  bias: yield UNDERestimated ~0.32 pt (converged ≈ 24.91 %), KFS in-cut
  OVERestimated ~3.3 pts (converged 82.1 %, still envelope-compliant),
  C1 grits overestimated ~0.32 t/h (base capacity ≈ 67.4 kt/y, not 69.3).
- Perspective: smaller than the Monte Carlo parameter band (±1.8 pts) —
  no conclusion flips — but now found, quantified and fixable by US.

**Client arbitration PENDING: adopt the x2 grid as the engine default
(recommended; spec meshes stay the PRESENTATION format), keep the spec
grid with a disclosed bias note, or go x4.**

Numerics component closable on the client's grid decision (89 % → 91 %).
