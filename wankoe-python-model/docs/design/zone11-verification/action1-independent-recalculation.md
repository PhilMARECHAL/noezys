# Zone-1.1 internal confidence program — Action 1: independent recalculation

**Date:** 2026-08-14 · **Protocol:** blind — the verification agent was
forbidden to read `src/`, `tests/` and the engine reference extract; it
worked only from the documented model definitions
(`docs/model-science-review.md`, the issued zone-1 calculation document,
the expert book) and `data/default_parameters.json`, in pure standard
library Python (`scripts/verify_zone11_independent.py`, replayable).

## Verdict: PASS — full concordance

| Quantity | Engine | Independent | Deviation |
|---|---|---|---|
| KFS Yield (wet/wet, pivot) | 24.59 % | 24.59 % | 0 |
| KFS product | 61.478 t/h wet | 61.478 t/h wet | 0 |
| KFS PSD in-cut / below / above | 85.39 / 6.62 / 7.99 % | 85.39 / 6.62 / 7.99 % | 0 |
| 0/20 stream | 175.325 t/h dry | 175.325 t/h dry | 0 |
| Recirculation (CR.5011 load) | 69.261 t/h | 69.261 t/h | 0 |
| KFS cumulative curve, 29 mesh points | — | — | **0.00 at every point** |
| CR.5009 W / P_net / P_inst / F80 / P80 | 0.312 / 72.468 / 96.624 / 180.575 / 42.709 | idem (2-dec rounding) | < 5·10⁻³ (rounding only) |
| CR.5011 Ecs / t10 / n / P_net / F80 / P80 | 0.125 / 5.71 / 1.645 / 16.163 / 63.022 / 29.277 | idem | < 3·10⁻³ (rounding only) |
| SR.5007 VSMA areas | 6.80 / 7.18 m² | 6.80 / 7.18 m² | 0 |

25 scalar values + the full 29-point product curve: no real deviation.

## Bonus validation

Before computing at the current settings, the agent re-ran the OLD
published settings (g=40 / CSS=20 / v=45) and reproduced every figure of
the issued zone-1 calculation document exactly (recycle 29.47, KFS 47.76
dry / 51.35 wet, 0/20 184.74, areas 6.80/7.56, envelope 7.48/85.73/6.78)
— the implemented conventions are provably the documented ones, at two
different operating points.

## Honest limits

- The headline yield (24.59) is quoted in project docs the agent could
  read; the probative evidence is the exact match of the 25 unpublished
  scalars and the full mesh-by-mesh curve, plus the old-settings replay.
- 16 formula-detail assumptions the agent decided alone are recorded in
  `zone11_independent_result.json` — every one landed on the engine's
  convention, i.e. the documentation is sufficient to rebuild the model.
- This action proves the IMPLEMENTATION, not the formula choices
  (action 2) nor the [H] parameter values (action 4).

**Confidence budget: implementation-error component (5 pts) CLOSED —
meta-score 74 % → 79 %.**
