"""REV B cookie liberation model — engine-instrumented computation.

Physics: quartz grains (d50 0.2 mm, band 0.1-0.4) NEVER break; a grain is
either embedded in a calcite particle or liberated whole. Liberation law:
L(x) = liberated fraction of the quartz inventory associated with fragment
size x:  L=1 for x<=d ; L=ln(k*d/x)/ln(k) for d<x<k*d ; L=0 for x>=k*d.
k central 3 [H], band 2-4. Free grains physically reside in the 0.1-0.4 mm
band of the stream that carries them.

Stream functionals (additive across size-partition classification, i.e.
every screen cut >=1.5 mm; reset upward by comminution):
  freeQ  = g0 * q * Phi(psd),  Phi = integral L(x) dP(x)
  embQ   = g0 * q * (1 - Phi)  (profile e(x)=g0*(1-L(x)), barren below d)
The ONLY cut inside the sub-band region is SP.36 at 65 um: the fine product
takes sub-65um intervals only -> zero grains, zero embedded; the remainder
keeps the whole quartz inventory of the 0/1.5 fines.
"""
from __future__ import annotations
import math, json
from wankoe_model import load_parameters, run_required_hours, run_scenario
from wankoe_model import flowsheet, models
from wankoe_model.grid import PSD

D_GRAIN = 0.2      # mm, d50 of the quartz grains (client datum)
BAND = (0.1, 0.4)  # mm, grain size band

def Lfun(x: float, k: float, d: float = D_GRAIN) -> float:
    if x <= d: return 1.0
    if x >= k * d: return 0.0
    return math.log(k * d / x) / math.log(k)

def phi_lib(psd: PSD, k: float, d: float = D_GRAIN, n: int = 400) -> float:
    """Liberation degree of a stream = integral of L(x) dP(x), fine log grid."""
    kd = k * d
    tot = psd.passing_at(d)          # everything finer than d: L = 1
    xs = [d * (kd / d) ** (i / n) for i in range(n + 1)]
    for a, b in zip(xs, xs[1:]):
        xm = math.sqrt(a * b)
        tot += Lfun(xm, k, d) * (psd.passing_at(b) - psd.passing_at(a))
    return tot

def bandfrac(psd: PSD) -> float:
    return psd.fraction_between(*BAND)

# ------------------------------------------------------------ instrumentation
REC: dict = {"karra": [], "m7": [], "m8": []}
_karra0 = flowsheet._karra_screen
_m7_0 = models.m7_bed_mill_pass
_m8_0 = models.m8_air_classification

def _karra(stream, aperture_mm, imperfection, calib):
    over, under = _karra0(stream, aperture_mm, imperfection, calib)
    REC["karra"].append({"a": aperture_mm, "feed": stream, "over": over, "under": under})
    return over, under

def _m7(feed_psd, gap_mm, calib):
    out = _m7_0(feed_psd, gap_mm, calib)
    REC["m7"].append({"gap": gap_mm, "feed_psd": feed_psd, "out_psd": out})
    return out

def _m8(q, psd, cut_um, phi_meas, calib):
    r = _m8_0(q, psd, cut_um, phi_meas, calib)
    REC["m8"].append({"q": q, "psd": psd, "cut_um": cut_um, "res": r})
    return r

flowsheet._karra_screen = _karra
models.m7_bed_mill_pass = _m7
models.m8_air_classification = _m8

def last(kind, key, val, tol=1e-9):
    hits = [r for r in REC[kind] if abs(r[key] - val) < tol]
    return hits[-1] if hits else None

# ------------------------------------------------------------ engine photos
def photo(overrides):
    for v in REC.values(): v.clear()
    res = run_scenario(load_parameters(overrides=overrides))
    return res, {k: list(v) for k, v in REC.items()}

params = load_parameters()
plan = run_required_hours(params)
H = {"1A": plan["zone_1_1_split"]["mode_1A_hours_effective"],
     "2A": plan["zone_1_2_split"]["dry_season_hours_effective"],
     "2C": plan["zone_1_2_split"]["aglime_2c_campaign_hours_effective"],
     "G": plan["zone_1_3_split"]["mode_G_hours_effective"],
     "F": plan["zone_1_3_split"]["mode_F_hours_effective"]}
PROD_T = plan["production_t"]

resG, recG = photo({})
resF, recF = photo({"default_scenario": {"zone_1_3_mode": "F"}})
res2C, rec2C = photo({"default_scenario": {"zone_1_2_mode": "2C"}})

def sget(rec, kind, key, val):
    hits = [r for r in rec[kind] if abs(r[key] - val) < 1e-9]
    return hits[-1] if hits else None

# ------------------------------------------------------------ per-photo model
def stream_state(q, psd, g0, k):
    """(free t/h, embedded t/h, total t/h) quartz for a stream carrying its
    natural fines complement (valid for every stream here except UltraFin
    and the post-SP.36 remainder, handled explicitly)."""
    ph = phi_lib(psd, k)
    return g0 * q * ph, g0 * q * (1 - ph), g0 * q

def analyse(g0=0.05, k=3.0, verbose=True):
    out = {"products": {}, "fluxes": {}, "phi": {}, "band": {}}

    # ---- zone 1.1 (photo G = mode 1A reference)
    ap20 = sget(recG, "karra", "a", 20.0)
    kfs = resG["products"]["KFS"]; q_kfs = kfs["tph"]  # dry state product
    s020 = ap20["under"]; q020, psd020 = s020["q"], s020["psd"]
    kfs_psd_pts = kfs["passing_curve_pct"]
    # KFS psd from ap20 oversize (same stream object as product)
    psd_kfs = ap20["over"]["psd"]
    f_kfs, e_kfs, t_kfs = stream_state(q_kfs, psd_kfs, g0, k)
    f020, e020, t020 = stream_state(q020, psd020, g0, k)
    out["phi"]["0/20 (post CR.5006/5011 loop)"] = phi_lib(psd020, k)
    out["phi"]["KFS 20/35"] = phi_lib(psd_kfs, k)

    # ---- zone 1.2 mode 2A (photo G): SR.5105 6mm, SR.5111/5115 1.7mm
    ap6 = sget(recG, "karra", "a", 6.0)
    fl = ap6["over"]; u06 = ap6["under"]
    k17 = [r for r in recG["karra"] if abs(r["a"] - 1.7) < 1e-9]
    sr5111 = k17[0]; sr5115 = k17[-1]
    ag1 = sr5111["under"]; over1 = sr5111["over"]
    cr13_out = sr5115["feed"]; ag2 = sr5115["under"]
    f_fl, e_fl, t_fl = stream_state(fl["q"], fl["psd"], g0, k)
    f_u06, _, _ = stream_state(u06["q"], u06["psd"], g0, k)
    f_ag1, e_ag1, t_ag1 = stream_state(ag1["q"], ag1["psd"], g0, k)
    f_cr, e_cr, t_cr = stream_state(cr13_out["q"], cr13_out["psd"], g0, k)
    f_ag2, e_ag2, t_ag2 = stream_state(ag2["q"], ag2["psd"], g0, k)
    ag = resG["products"]["AgLime"]
    q_ag_dry = ag1["q"] + ag2["q"]
    ag_quartz = t_ag1 + t_ag2   # per-stream identity: free+emb = g0*q
    out["phi"]["AgLime 0/1.7 (2A)"] = (f_ag1 + f_ag2) / max(ag_quartz, 1e-12)
    out["phi"]["loop feed 0/6 (2A)"] = phi_lib(u06["psd"], k)
    out["phi"]["CR.5113 product (2A)"] = phi_lib(cr13_out["psd"], k)

    # ---- zone 1.2 mode 2C (photo 2C)
    k17c = [r for r in rec2C["karra"] if abs(r["a"] - 1.7) < 1e-9]
    sr5111c = k17c[0]; sr5115c = k17c[-1]
    ag1c, ag2c = sr5111c["under"], sr5115c["under"]
    f_ag1c, _, t_ag1c = stream_state(ag1c["q"], ag1c["psd"], g0, k)
    f_ag2c, _, t_ag2c = stream_state(ag2c["q"], ag2c["psd"], g0, k)
    cr13c = sr5115c["feed"]

    # ---- zone 1.3 C1 (photos G and F)
    def z13(rec, res, mode):
        ap8 = sget(rec, "karra", "a", 8.0); ap375 = sget(rec, "karra", "a", 3.75)
        ap2 = sget(rec, "karra", "a", 2.0); ap15 = sget(rec, "karra", "a", 1.5)
        m8 = rec["m8"][-1]
        rc = {}
        for r in rec["m7"]:
            rc.setdefault(round(r["gap"], 3), r)  # first-seen per gap
        for r in rec["m7"]:
            rc[round(r["gap"], 3)] = r            # keep last per gap
        gaps = sorted(rc)  # RC.2 gap < RC.1 gap
        g_rc2, g_rc1 = gaps[0], gaps[-1]
        rc1_q = res["machines"]["RC.1"]["throughput_tph"]
        rc2_q = res["machines"]["RC.2"]["throughput_tph"]
        d = {"sca_feed": ap8["feed"], "scb_feed": ap375["under"],
             "scb_d2_feed": ap2["under"], "grits": ap2["over"],
             "sliver": ap15["over"], "fines": ap15["under"],
             "rc1": (rc1_q, rc[g_rc1], g_rc1), "rc2": (rc2_q, rc[g_rc2], g_rc2),
             "m8": m8}
        return d
    zG = z13(recG, resG, "G"); zF = z13(recF, resF, "F")

    # products: grits (G), fines (F+G), UltraFin
    grits = zG["grits"]
    f_gr, e_gr, t_gr = stream_state(grits["q"], grits["psd"], g0, k)
    finesG, finesF = zG["fines"], zF["fines"]
    m8G, m8F = zG["m8"], zF["m8"]
    fines_states = {}
    for tag, fs, m8 in (("G", finesG, m8G), ("F", finesF, m8F)):
        f_f, e_f, t_f = stream_state(fs["q"], fs["psd"], g0, k)
        q_uf = m8["res"]["fine_product_tph"]; q_rem = m8["res"]["remainder_tph"]
        # SP.36: UltraFin = sub-65um intervals only -> 0 quartz;
        # remainder keeps the WHOLE fines quartz inventory
        fines_states[tag] = {"q_fines": fs["q"], "quartz": t_f, "free": f_f,
                             "q_uf": q_uf, "q_rem": q_rem,
                             "grade_rem": t_f / q_rem, "psd": fs["psd"]}
        out["phi"][f"fines 0/1.5 (mode {tag})"] = phi_lib(fs["psd"], k)
    out["phi"]["grits 2/4 (G)"] = phi_lib(grits["psd"], k)

    # ---- product grade table (annual, plan tonnages)
    def prow(name, grade, free_share, note=""):
        t = PROD_T[name]
        out["products"][name] = {
            "annual_t": t, "quartz_pct": 100 * grade,
            "quartz_t_y": grade * t, "free_share_of_quartz": free_share,
            "caco3_basis_pct": 100 * (1 - grade), "note": note}

    prow("KFS", t_kfs / q_kfs, f_kfs / max(t_kfs, 1e-12),
         "embedded in 20-35 mm lumps")
    # AgLime annual = 2A hours + 2C hours blend
    agA_q = q_ag_dry * H["2A"]; agC_q = (ag1c["q"] + ag2c["q"]) * H["2C"]
    agA_qz = ag_quartz * H["2A"]; agC_qz = (t_ag1c + t_ag2c) * H["2C"]
    agA_fr = (f_ag1 + f_ag2) * H["2A"]; agC_fr = (f_ag1c + f_ag2c) * H["2C"]
    prow("AgLime", (agA_qz + agC_qz) / (agA_q + agC_q),
         (agA_fr + agC_fr) / (agA_qz + agC_qz), "2A+2C annual blend")
    prow("FeedLime grits", t_gr / grits["q"], f_gr / max(t_gr, 1e-12),
         "embedded in 2-4 mm particles")
    # FeedLime fines annual = G + F campaign remainders
    fq = fines_states
    rem_q = fq["G"]["q_rem"] * H["G"] + fq["F"]["q_rem"] * H["F"]
    rem_qz = fq["G"]["quartz"] * H["G"] + fq["F"]["quartz"] * H["F"]
    rem_fr = fq["G"]["free"] * H["G"] + fq["F"]["free"] * H["F"]
    prow("FeedLime fines", rem_qz / rem_q, rem_fr / rem_qz,
         "keeps ALL fines-train quartz after UltraFin extraction")
    prow("UltraFin", 0.0, 0.0, "no grain route past the 65 um cut (grain >=100 um)")

    # ---- band (0.1-0.4 mm) sub-band grades: where the free grains sit
    for tag, fs in (("AgLime 2A", ag1), ("fines G", finesG), ("fines F", finesF),
                    ("0/20", s020)):
        q, psd = fs["q"], fs["psd"]
        fr = stream_state(q, psd, g0, k)[0]
        bm = q * bandfrac(psd)
        out["band"][tag] = {"band_tph": bm, "free_quartz_tph": fr,
                            "band_quartz_pct": 100 * fr / max(bm, 1e-12),
                            "band_frac_pct": 100 * bandfrac(psd)}

    # ---- free-grain flux map (t/h free grains at machine interfaces)
    FX = out["fluxes"]
    def flux(name, tph_free, hours, note):
        FX[name] = {"free_tph": tph_free, "hours_y": hours,
                    "free_t_y": tph_free * hours, "note": note}

    flux("0/20 stream (SR.5008 -> stockpile, 1A)", f020, H["1A"],
         "free grains in the 0.1-0.4 band of the 0/20; embedded rest at bulk")
    flux("SR.5111 feed (2A loop feed 0/6)", f_u06, H["2A"],
         "free grains crossing the 1.7 mm mat -> AgLime with the undersize")
    f_reclaim_2c = stream_state(sr5111c["feed"]["q"], sr5111c["feed"]["psd"], g0, k)[0]
    flux("SR.5111 feed (2C whole reclaim)", f_reclaim_2c, H["2C"], "2C campaign")
    flux("SR.5115 feed (CR.5113 product, 2A)", f_cr, H["2A"],
         "liberation raised by the impactor pass")
    f_crc = stream_state(cr13c["q"], cr13c["psd"], g0, k)[0]
    flux("SR.5115 feed (CR.5113 product, 2C)", f_crc, H["2C"], "")
    for tag, z in (("G", zG), ("F", zF)):
        scb1, scb2 = z["scb_feed"], z["scb_d2_feed"]
        flux(f"SC.B deck-1 2.0 mm feed (mode {tag})",
             stream_state(scb1["q"], scb1["psd"], g0, k)[0], H[tag],
             "free grains vs the PU mat (RPN-252 screen)")
        flux(f"SC.B deck-2 1.5 mm feed (mode {tag})",
             stream_state(scb2["q"], scb2["psd"], g0, k)[0], H[tag], "")
        sca = z["sca_feed"]
        flux(f"SC.A feed (mode {tag})",
             stream_state(sca["q"], sca["psd"], g0, k)[0], H[tag], "wire decks")
        for unit in ("rc1", "rc2"):
            qrc, r, gap = z[unit]
            fin = g0 * qrc * phi_lib(r["feed_psd"], k)
            fout = g0 * qrc * phi_lib(r["out_psd"], k)
            flux(f"{unit.upper()} gap {gap} mm feed-side (mode {tag})", fin,
                 H[tag], "grains already free entering the gap - transit untouched")
            flux(f"{unit.upper()} gap {gap} mm product-side (mode {tag})", fout,
                 H[tag], f"generation in-pass: +{fout-fin:.4f} t/h")
        m8 = z["m8"]
        f_fines = stream_state(m8["q"], m8["psd"], g0, k)[0]
        flux(f"SP.36 circuit feed 0/1.5 (mode {tag})", f_fines, H[tag],
             "grains reaching the classifier circuit; ALL rejected by the "
             "65 um cut -> wheel/housing wear, zero into UltraFin")
    return out

# ------------------------------------------------------------ run + report
R = analyse(0.05, 3.0)
print("=== Phi (liberation degree of the stream quartz inventory), k=3, d=0.2")
for kk, v in R["phi"].items(): print(f"  {kk:38s} {100*v:6.2f} %")
print("\n=== REV B product table (g0=5 %, k=3)")
for name, p in R["products"].items():
    print(f"  {name:16s} {p['annual_t']:9.0f} t/y  quartz {p['quartz_pct']:5.2f} % "
          f"({p['quartz_t_y']:7.0f} t/y, free share {100*p['free_share_of_quartz']:5.1f} %)  "
          f"CaCO3-basis {p['caco3_basis_pct']:5.2f} %  | {p['note']}")
print("\n=== 0.1-0.4 mm sub-band (where the free grains live)")
for kk, v in R["band"].items():
    print(f"  {kk:12s} band {v['band_frac_pct']:5.1f} % of stream, "
          f"{v['band_tph']:7.3f} t/h; free quartz {v['free_quartz_tph']:6.3f} t/h "
          f"-> band grade {v['band_quartz_pct']:5.2f} % quartz")
print("\n=== Free-grain flux map (t/h and t/y of FREE quartz grains)")
for kk, v in R["fluxes"].items():
    print(f"  {kk:46s} {v['free_tph']:8.4f} t/h x {v['hours_y']:6.0f} h "
          f"= {v['free_t_y']:8.1f} t/y  {v['note']}")

print("\n=== sensitivity: product quartz % and key fluxes")
for g0 in (0.03, 0.05, 0.08):
    for kf in (2.0, 3.0, 4.0):
        r = analyse(g0, kf, verbose=False)
        scb = r["fluxes"]["SC.B deck-2 1.5 mm feed (mode F)"]["free_t_y"]
        s11 = (r["fluxes"]["SR.5111 feed (2A loop feed 0/6)"]["free_t_y"]
               + r["fluxes"]["SR.5111 feed (2C whole reclaim)"]["free_t_y"])
        loop = r["fluxes"]["0/20 stream (SR.5008 -> stockpile, 1A)"]["free_t_y"]
        ag = r["products"]["AgLime"]["quartz_pct"]
        fi = r["products"]["FeedLime fines"]["quartz_pct"]
        print(f"  g0={100*g0:3.0f}% k={kf:.0f}: AgLime {ag:5.2f}% fines {fi:5.2f}% | "
          f"free t/y: 0/20 {loop:7.1f}  SR.5111 {s11:6.1f}  SC.B-d2(F) {scb:6.1f}")

# mass-balance closure check (zone 1.1, g0=5% k=3)
g0 = 0.05
print("\n=== closure checks (g0=5%, k=3)")
ap20 = sget(recG, "karra", "a", 20.0)
qk, q0 = ap20["over"]["q"], ap20["under"]["q"]
print(f"  zone 1.1: quartz KFS+0/20 = {g0*(qk+q0):.3f} t/h vs g0*(sum q) identity")
m8G = recG["m8"][-1]
print(f"  SP.36 G: fines {m8G['q']:.3f} t/h -> UF {m8G['res']['fine_product_tph']:.3f} "
      f"+ rem {m8G['res']['remainder_tph']:.3f}")
print(f"  UltraFin annual check: {PROD_T['UltraFin']} t/y")


# ---- evidence dump (script ratified into the repo 2026-08-16, REV B) ----
import subprocess
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_OUT = _ROOT / "docs/design/abrasivity/liberation-rev-b-evidence.json"
_central = analyse(0.05, 3.0, verbose=False)
_commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=_ROOT,
                         capture_output=True, text=True).stdout.strip()
_OUT.write_text(json.dumps({
    "_provenance": {
        "engine_commit": _commit,
        "script": "scripts/liberation_rev_b.py",
        "note": ("REV B cookie liberation model (expert team 2026-08-16): "
                 "L(x)=ln(k*d/x)/ln(k) on d<x<k*d, d=0.2 mm client grains, "
                 "k=3 [2-4] [H]. Central run g0=5 % (client datum, band 3-8). "
                 "Supersedes the REV A liberation ladder 25/40/90/90."),
    },
    "central_g0_5pct_k3": _central,
}, indent=1, default=float))
print(f"wrote {_OUT.relative_to(_ROOT)}")
