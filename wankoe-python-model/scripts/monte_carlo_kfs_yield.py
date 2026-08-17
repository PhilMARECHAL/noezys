"""Monte Carlo uncertainty band on KFS Yield (confidence program action 4).

Draws the five uncertain inputs over their DOCUMENTED plausible ranges
(uniform, independent — no better information exists before the vendor
tests) and publishes the KFS Yield distribution that replaces the naked
point figure.

Ranges (each traceable to a register row / open question):
- CR.5006 product slope n     : [1.05 ; 1.65]  (RC1 — no vendor curve)
- A_j                          : [50 ; 69]      (Q12 — calcite literature)
- b_j                          : [0.6 ; 1.3]    (Q12 — hypothesis 0.8;
  the full literature tail b -> 3.0 is reported as a separate labeled
  scenario, NOT mixed into the band: the t10->n mapping is calibrated
  around the hypothesis family and extreme extrapolation is exactly what
  the drop-weight test must settle)
- SR.5008 imperfection I       : [0.10 ; 0.20]  (Q3 — unratified 0.15)
- Feed curve size-rescale k    : [0.93 ; 1.07]  (single belt-cut, RC4 —
  repeatability envelope pending the repeat campaign)

Implied landfill per draw: 0/20 produced = KFS_target*(1-y)/y (wet), vs
the fixed downstream demand 212 079 t/y (2A + 2C at the current plan).

Usage: python scripts/monte_carlo_kfs_yield.py [N]   (default 200, seed 7)
"""
import json
import math
import random
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from wankoe_model import load_parameters, run_scenario  # noqa: E402

N = int(sys.argv[1]) if len(sys.argv) > 1 else 200
rng = random.Random(7)

base = load_parameters()
meas = {float(m): v for m, v in base["feed_product"]["cumulative_passing_curve"].items()}
pts = sorted(meas.items())

def passing_at(x):
    if x <= pts[0][0]:
        return pts[0][1] * x / pts[0][0]
    if x >= pts[-1][0]:
        return 100.0
    for (x0, p0), (x1, p1) in zip(pts, pts[1:]):
        if x <= x1:
            t = (math.log(x) - math.log(x0)) / (math.log(x1) - math.log(x0))
            return p0 + t * (p1 - p0)

def curve(k):
    c = {str(x): round(passing_at(x / k), 4) for x in meas}
    c[str(pts[-1][0])] = 100.0
    return c

KFS_TARGET = 85000.0
DEMAND_020 = 212079.0  # 2A FeedLime-demand reclaim + 2C campaigns (register 2026-08-14)

def one(nv, aj, bj, iv, k):
    ov = {
        "machines": {
            "CR.5006": {"parameters": {"n": {"default": nv}}},
            "SR.5008": {"parameters": {"I": {"default": iv}}},
        },
        "calibration": {"A_j": {"default": aj}, "b_j": {"default": bj}},
        "feed_product": {"cumulative_passing_curve": curve(k)},
    }
    r = run_scenario(load_parameters(overrides=ov))
    y = r["indicators"]["kfs_yield_pct"]
    comp = r["products"]["KFS"]["compliance"]
    landfill = max(0.0, KFS_TARGET * (100.0 - y) / y - DEMAND_020)
    return y, comp["compliant"], comp["in_cut_pct"], landfill

draws = []
for _ in range(N):
    draws.append(one(rng.uniform(1.05, 1.65), rng.uniform(50, 69),
                     rng.uniform(0.6, 1.3), rng.uniform(0.10, 0.20),
                     rng.uniform(0.93, 1.07)))

ys = sorted(d[0] for d in draws)
lf = sorted(d[3] for d in draws)
q = lambda v, p: v[min(len(v) - 1, int(p * len(v)))]
result = {
    "n_draws": N, "seed": 7,
    "kfs_yield_pct": {"P10": q(ys, 0.10), "P50": statistics.median(ys), "P90": q(ys, 0.90),
                      "min": ys[0], "max": ys[-1], "mean": statistics.fmean(ys)},
    "implied_landfill_t_y": {"P10": q(lf, 0.10), "P50": statistics.median(lf), "P90": q(lf, 0.90)},
    "kfs_envelope_pass_rate_pct": 100.0 * sum(1 for d in draws if d[1]) / N,
    "in_cut_pct": {"min": min(d[2] for d in draws), "max": max(d[2] for d in draws)},
}
# separate labeled pessimistic scenario: full literature tail (Q12)
y, c, ic, l = one(1.35, 69, 3.0, 0.15, 1.0)
result["literature_tail_scenario_b3.0_A69"] = {
    "kfs_yield_pct": y, "envelope_compliant": c, "in_cut_pct": ic, "implied_landfill_t_y": l}

print(json.dumps(result, indent=1))
