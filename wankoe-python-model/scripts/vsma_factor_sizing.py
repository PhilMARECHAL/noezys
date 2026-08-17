"""Fine-screen purchase sizing by the FULL VSMA factor method.

CLIENT DECISION 2026-08-15 (error-hunt M-1, option 1 of 3): the purchase
minima of the three fine screens — SC.B (2 / 1.5 mm), SR.5111 (1.7 mm) and
SR.5115 (1.7 mm) — are re-quoted with the standard VSMA factor-method sizing
(basic capacity x oversize factor x half-size factor x deck-position factor),
because the engine's M4 model carries NO feed-composition factors: its fitted
f0 = 0.347 matches the standard method at SR.5008-like feeds (~46-53 %
half-size, where the half-size factor is ~1) but UNDER-sizes low-half-size
feeds — SC.B carries only 17-20 % half-size and needs ~30 % more area than
the model says. The engine model itself is UNCHANGED (a model-improvement
item stays at the register); this script is the PURCHASE-SIZING authority
for these three screens, replayable from any engine state.

Method data ([H], vendor to verify by its own bed-depth sizing):
- Basic capacity C(a): classic VSMA/metric curve for ~1.6 t/m3 limestone.
- Half-size factor K: 1.0 at 40 % passing a/2 (0.4 + 0.015*pct below 40).
- Oversize factor M: 1.0 at 25 % retained on the aperture (VSMA table).
- Deck-position factor D: 1.0 / 0.9 for a machine's 1st / 2nd deck.
The engine exposes per-deck U (undersize t/h), % half-size and % oversize
on every photo (models.m4_feed_composition — error-hunt M-1 wiring), so
every circumstance the client has ruled is swept below.

FONTAINE %GL CROSS-CHECK (client order 2026-08-17): the identified
source of M4 (Fontaine, "Le criblage" + calculation booklet, Carmeuse
2001, Tableaux 6-7) states Q (m3/h/m2) = 1.4 * a^0.6 / %GL, %GL =
"grains limites" (near-mesh fraction; [H] band convention a/2..1.5a,
exposed by models.m4_feed_composition). This script now evaluates the
Fontaine area beside the VSMA-factor area on every deck and circumstance
(volumetric law converted with the data densities feed_product.properties
dry_density_tm3 / wet_density_tm3 — their first engine-adjacent use).
INFORMATIONAL ONLY: purchase floors are never weakened without a client
arbitration (M-1 rule); a Fontaine area ABOVE a floor is flagged.

Replay:
    PYTHONPATH=src python scripts/vsma_factor_sizing.py
writes docs/design/error-hunt/vsma-fine-screen-sizing.json
"""
from __future__ import annotations

import bisect
import json
import math
import subprocess
from pathlib import Path

from wankoe_model import load_parameters, run_scenario

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "design" / "error-hunt" / "vsma-fine-screen-sizing.json"

AREA_MARGIN = 1.25  # [H] same +25 % purchase allowance as the other sheets

# Basic capacity C(a) [t/h/m2] — classic VSMA metric curve, limestone ~1.6 t/m3
CAP_TABLE = [
    (0.5, 2.2), (1.0, 3.9), (1.5, 5.2), (2.0, 6.3), (3.0, 8.1), (4.0, 9.7),
    (5.0, 11.1), (6.0, 12.3), (8.0, 14.4), (10.0, 16.2), (12.5, 18.2),
    (16.0, 20.7), (20.0, 23.0), (25.0, 25.6), (31.5, 28.4), (35.0, 29.8),
    (40.0, 31.7),
]
OVERSIZE_TABLE = [
    (0, 0.86), (5, 0.90), (10, 0.94), (15, 0.97), (20, 1.00), (25, 1.03),
    (30, 1.06), (35, 1.09), (40, 1.13), (45, 1.17), (50, 1.21), (55, 1.26),
    (60, 1.31), (65, 1.37), (70, 1.44), (75, 1.52), (80, 1.61), (85, 1.71),
    (90, 1.83), (95, 1.96),
]
DECK_FACTOR = {1: 1.0, 2: 0.9}

# Fontaine (Carmeuse 2001, Tableaux 6-7): Q m3/h/m2 = F_COEF * a^F_EXP / GL
# (GL as a fraction). Tabulated range %GL 10-80; outside it the check is
# flagged extrapolated. Densities: material basis per machine [H] — SC.B
# screens DRY zone-1.3 product; SR.5111/5115 screen moist zone-1.2 material.
F_COEF, F_EXP = 1.4, 0.6
F_GL_TABULATED = (10.0, 80.0)
F_DENSITY_KEY = {"SC.B": "dry_density_tm3", "SR.5111": "wet_density_tm3", "SR.5115": "wet_density_tm3"}


def fontaine_area(u_tph: float, a_mm: float, gl_pct: float, rho_tm3: float) -> dict:
    gl = max(gl_pct, 1e-6) / 100.0
    q_m3 = F_COEF * (a_mm ** F_EXP) / gl
    q_t = q_m3 * rho_tm3
    return {
        "pct_GL_near_mesh": round(gl_pct, 1),
        "Q_m3_h_m2": round(q_m3, 2),
        "rho_tm3": rho_tm3,
        "Q_t_h_m2": round(q_t, 2),
        "area_fontaine_m2": round(u_tph / q_t, 2) if u_tph > 0 else 0.0,
        "within_tabulated_GL_range": F_GL_TABULATED[0] <= gl_pct <= F_GL_TABULATED[1],
    }


def basic_capacity(a_mm: float) -> float:
    xs = [x for x, _ in CAP_TABLE]
    ys = [y for _, y in CAP_TABLE]
    if a_mm <= xs[0]:
        return ys[0]
    if a_mm >= xs[-1]:
        return ys[-1]
    i = bisect.bisect_left(xs, a_mm)
    x0, x1, y0, y1 = xs[i - 1], xs[i], ys[i - 1], ys[i]
    t = (math.log(a_mm) - math.log(x0)) / (math.log(x1) - math.log(x0))
    return y0 + t * (y1 - y0)


def half_size_factor(pct: float) -> float:
    return 0.4 + 0.015 * pct if pct < 40 else 1.0 + 0.02 * (pct - 40)


def oversize_factor(pct: float) -> float:
    for (x0, y0), (x1, y1) in zip(OVERSIZE_TABLE, OVERSIZE_TABLE[1:]):
        if pct <= x1:
            return y0 + (y1 - y0) * (pct - x0) / max(x1 - x0, 1e-9)
    return OVERSIZE_TABLE[-1][1]


# (machine, deck key, aperture mm, machine deck position)
DECKS = {
    "SC.B": [("deck_1", 2.0, 1), ("deck_2", 1.5, 2)],
    "SR.5111": [("deck", 1.7, 1)],
    "SR.5115": [("deck", 1.7, 1)],
}

# circumstance sweep: every client-ruled variation that moves these feeds
def circumstances() -> dict:
    quarry = json.loads(
        (ROOT / "docs/design/zone13-redesign/quarry-target-curve-20pct-margin.json")
        .read_text()
    )["cumulative_passing_curve"]
    cases = {}
    for curve_label, curve_ov in (
        ("measured", {}),
        ("quarry", {"feed_product": {"cumulative_passing_curve": quarry}}),
    ):
        for up_label, up in (("1A", "1A"), ("1B", "1B")):
            for mode_label, mode_ov in (
                ("2A+G", {}),
                ("2A+F", {"zone_1_3_mode": "F"}),
                ("2C", {"zone_1_2_mode": "2C"}),
            ):
                ov = json.loads(json.dumps(curve_ov))  # deep copy
                sc = {"zone_1_1_mode": up, **mode_ov}
                ov.setdefault("default_scenario", {}).update(sc)
                cases[f"{curve_label} / {up_label} / {mode_label}"] = ov
    return cases


def main() -> None:
    props = load_parameters()["feed_product"]["properties"]
    densities = {
        code: props[key]["default"] for code, key in F_DENSITY_KEY.items()
    }
    rows = []
    worst: dict = {}
    worst_fontaine: dict = {}
    for label, ov in circumstances().items():
        r = run_scenario(load_parameters(overrides=ov))
        for code, decks in DECKS.items():
            sheet = r["machines"].get(code, {})
            areas = sheet.get("areas_m2") or {}
            for deck_key, aperture, position in decks:
                entry = areas.get(deck_key)
                if not entry or "feed_pct_half_size" not in entry:
                    continue  # machine inactive in this photo
                u = entry["undersize_tph"]
                c = basic_capacity(aperture)
                m = oversize_factor(entry["feed_pct_oversize"])
                k = half_size_factor(entry["feed_pct_half_size"])
                d = DECK_FACTOR[position]
                a_vsma = u / (c * m * k * d) if u > 0 else 0.0
                row = {
                    "circumstance": label,
                    "machine": code,
                    "deck": deck_key,
                    "aperture_mm": aperture,
                    "undersize_tph": round(u, 2),
                    "pct_half_size": round(entry["feed_pct_half_size"], 1),
                    "pct_oversize": round(entry["feed_pct_oversize"], 1),
                    "factors": {
                        "C_basic": round(c, 2),
                        "M_oversize": round(m, 2),
                        "K_half_size": round(k, 2),
                        "D_deck": d,
                    },
                    "area_vsma_m2": round(a_vsma, 2),
                    "area_model_m2": round(entry["required_area_m2"], 2),
                }
                if "feed_pct_near_mesh" in entry:
                    row["fontaine"] = fontaine_area(
                        u, aperture, entry["feed_pct_near_mesh"], densities[code]
                    )
                rows.append(row)
                key = (code, deck_key)
                if key not in worst or a_vsma > worst[key]["area_vsma_m2"]:
                    worst[key] = {**row}
                fa = row.get("fontaine", {}).get("area_fontaine_m2", 0.0)
                if key not in worst_fontaine or fa > worst_fontaine[key]["fontaine"]["area_fontaine_m2"]:
                    worst_fontaine[key] = {**row}

    minima = {}
    for (code, deck_key), w in sorted(worst.items()):
        floor = math.ceil(w["area_vsma_m2"] * AREA_MARGIN * 10) / 10  # round UP
        wf = worst_fontaine[(code, deck_key)]
        fon = wf.get("fontaine", {})
        f_area = fon.get("area_fontaine_m2", 0.0)
        f_margined = round(f_area * AREA_MARGIN, 2)
        minima.setdefault(code, {})[deck_key] = {
            "worst_circumstance": w["circumstance"],
            "worst_vsma_area_m2": w["area_vsma_m2"],
            "model_area_at_worst_m2": w["area_model_m2"],
            "purchase_min_m2": floor,
            "fontaine_cross_check": {
                "worst_circumstance": wf["circumstance"],
                "worst_area_m2": f_area,
                "worst_area_x_margin_m2": f_margined,
                "pct_GL_at_worst": fon.get("pct_GL_near_mesh"),
                "within_tabulated_GL_range": fon.get("within_tabulated_GL_range"),
                "verdict": (
                    "EXCEEDS the published purchase floor — client arbitration "
                    "candidate (floors are never weakened, but a HIGHER "
                    "independent requirement must be surfaced)"
                    if f_margined > floor
                    else "inside the published purchase floor — floor stands"
                ),
            },
        }
        print(
            f"{code} {deck_key}: worst VSMA {w['area_vsma_m2']:.2f} m2 "
            f"({w['circumstance']}; model said {w['area_model_m2']:.2f}) "
            f"-> purchase >= {floor} m2 | Fontaine %GL check: "
            f"{f_area:.2f} m2 (x{AREA_MARGIN} = {f_margined:.2f}) at "
            f"%GL {fon.get('pct_GL_near_mesh')} ({wf['circumstance']}) -> "
            f"{minima[code][deck_key]['fontaine_cross_check']['verdict'].split(' — ')[0]}"
        )

    commit = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True
    ).stdout.strip()
    OUT.write_text(
        json.dumps(
            {
                "_provenance": {
                    "engine_commit": commit,
                    "script": "scripts/vsma_factor_sizing.py",
                    "margin": f"x{AREA_MARGIN} [H] on the factor-method worst case",
                    "note": (
                        "Client decision 2026-08-15 (error-hunt M-1, option 1): "
                        "fine-screen purchase minima by the FULL VSMA factor "
                        "method (the engine M4 model has no composition factors "
                        "and under-sizes low-half-size feeds by ~25-30 %). "
                        "Factor data [H]; vendor bed-depth sizing verifies. "
                        "FONTAINE %GL CROSS-CHECK added 2026-08-17 (client "
                        "order; source: Le criblage + calculation booklet, "
                        "Carmeuse 2001, Tableaux 6-7 — the identified source "
                        "of M4): Q = 1.4 a^0.6 / %GL m3/h/m2, near-mesh band "
                        "a/2..1.5a [H], densities from feed_product.properties "
                        "(dry 1.5 / wet 1.62 t/m3, first use). INFORMATIONAL: "
                        "purchase floors never weakened; exceedances surfaced "
                        "for client arbitration."
                    ),
                },
                "purchase_minima": minima,
                "sweep": rows,
            },
            indent=1,
        )
    )
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
