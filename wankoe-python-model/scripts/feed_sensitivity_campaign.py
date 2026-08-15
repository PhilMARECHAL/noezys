"""Feed-sensitivity campaign (client, 2026-08-14): five zone-1 inlet
curves through the full two-mode annual plan at FIXED reference settings.
Cases: measured | smoothed fit (best of Rosin-Rammler / Swebrec, LSQ) |
D50 -30 % (k=0.70) | D50 +30 % (k=1.30) | D50 +60 % (k=1.60), all
shape-preserving homothetic rescales of the MEASURED curve (client Q1)."""
import json, math, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from wankoe_model import load_parameters, run_required_hours

base = load_parameters()
meas = {float(k): v for k, v in base["feed_product"]["cumulative_passing_curve"].items()}
pts = sorted(meas.items())
xs = [p[0] for p in pts]; ys = [p[1] for p in pts]

def interp(x):
    if x <= pts[0][0]: return pts[0][1]*x/pts[0][0]
    if x >= pts[-1][0]: return 100.0
    for (x0,p0),(x1,p1) in zip(pts, pts[1:]):
        if x <= x1:
            t=(math.log(x)-math.log(x0))/(math.log(x1)-math.log(x0)); return p0+t*(p1-p0)

def scaled(k):
    c = {str(x): round(interp(x/k),4) for x in meas}; c[str(pts[-1][0])]=100.0; return c

# smoothed: LSQ grid search — RR (x50,n) vs Swebrec (x50,b; xmax=320)
def rr(x, x50, n): return 100*(1-math.exp(-math.log(2)*(x/x50)**n))
def swe(x, x50, b):
    if x >= 320: return 100.0
    return 100/(1+(math.log(320/x)/math.log(320/x50))**b)
best = None
for name, f, prange in (("Rosin-Rammler", rr, [n/100 for n in range(30,121,2)]),
                        ("Swebrec", swe, [b/100 for b in range(80,301,5)])):
    for x50 in [20+i for i in range(0,31)]:
        for p in prange:
            sse = sum((f(x,x50,p)-y)**2 for x,y in pts if x < 320)
            if best is None or sse < best[0]: best = (sse, name, x50, p, f)
sse, fname, fx50, fp, ffun = best
smoothed = {str(x): round(min(100.0, ffun(x, fx50, fp)),4) for x in meas}
smoothed[str(pts[-1][0])] = 100.0
print(f"smoothed fit: {fname} (x50={fx50}, p={fp}, SSE={sse:.0f})")

CASES = [("measured", None), (f"smoothed ({fname})", smoothed),
         ("D50 -30% (k=0.70)", scaled(0.70)), ("D50 +30% (k=1.30)", scaled(1.30)),
         ("D50 +60% (k=1.60)", scaled(1.60))]
rows = []
for label, curve in CASES:
    ov = {} if curve is None else {"feed_product": {"cumulative_passing_curve": curve}}
    plan = run_required_hours(load_parameters(overrides=ov))
    ky, st, pr = plan["kfs_yield"], plan["stockpiles_t"], plan["production_t"]
    machine_alerts = [a for a in plan["alerts"] if any(a.startswith(c) for c in
        ("CR.", "SR.", "RC.", "SC.", "DY.", "ML.", "Zone")) ]
    rows.append({"case": label,
        "p20": round(interp(20.0) if curve is None else float(curve["20.0"]),1),
        "kfs": pr["KFS"], "grits": pr["FeedLime grits"], "fines": pr["FeedLime fines"],
        "aglime": pr["AgLime"], "landfill": st["0/20 to LANDFILL (net loss)"],
        "y": ky["realized_pct"], "yreq": ky["required_for_zero_landfill_pct"],
        "u": [d["utilization_pct"] for d in plan["zones"].values()],
        "alerts": machine_alerts})
    r = rows[-1]
    print(f"{label:22s} <20mm {r['p20']:5.1f}% | KFS {r['kfs']:.0f} grits {r['grits']:.0f} fines {r['fines']:.0f} AgLime {r['aglime']:.0f} | landfill {r['landfill']:7.0f} | Y {r['y']:.2f}/{r['yreq']:.2f} | util {r['u']}")
    for a in machine_alerts: print("     !", a[:120])
json.dump({"cases": rows, "smoothed_curve": smoothed}, open(ROOT/"docs/design/zone13-redesign/feed-sensitivity-campaign.json","w"), indent=1)
