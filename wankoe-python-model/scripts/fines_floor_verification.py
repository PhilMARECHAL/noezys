"""FeedLime fines floor — all-circumstances verification (client 2026-08-15).

Client guarantee request (error-hunt PD-3 arbitration message): "make sure we
produce the fines objective every year IN ALL CASES." This script replays the
annual plan (`run_required_hours`) across every circumstance the client has
ruled — feed curves, rock-hardness envelope, rain-time fraction — and records
whether the 60 000 t/y FeedLime fines objective lands exactly, with feasible
zone hours and no fines alert.

Replay:
    PYTHONPATH=src python scripts/fines_floor_verification.py
writes docs/design/error-hunt/fines-floor-evidence.json
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from wankoe_model import load_parameters, run_required_hours
from wankoe_model.paths import deep_merge

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "design" / "error-hunt" / "fines-floor-evidence.json"


def _quarry_curve() -> list:
    path = ROOT / "docs/design/zone13-redesign/quarry-target-curve-20pct-margin.json"
    return json.loads(path.read_text())["cumulative_passing_curve"]


def _soft_overrides(name: str) -> dict:
    path = ROOT / f"docs/design/soft-rock/soft-rock-scenario{name}.json"
    raw = json.loads(path.read_text())
    return {k: raw[k] for k in ("feed_product", "calibration", "machines") if k in raw}


def circumstances() -> dict:
    quarry = {"feed_product": {"cumulative_passing_curve": _quarry_curve()}}
    rain20 = {
        "default_scenario": {"dry_season_fraction": 0.8, "rain_season_fraction": 0.2}
    }
    cases = {
        "defaults (measured curve, mid-hard, rain 25 %)": {},
        "quarry-target curve (adopted works spec)": quarry,
        "soft rock central (UCS 20, client reference)": _soft_overrides(""),
        "soft rock envelope edge UCS 15": _soft_overrides("-soft15"),
        "soft rock envelope edge UCS 30": _soft_overrides("-soft30"),
        "rain time 20 % (client 2026-08-15 figure)": rain20,
        "quarry curve + soft central": deep_merge(
            dict(quarry), _soft_overrides(""), validate=False
        ),
        "quarry curve + rain 20 %": deep_merge(dict(quarry), rain20, validate=False),
        "soft central + rain 20 %": deep_merge(
            _soft_overrides(""), rain20, validate=False
        ),
    }
    return cases


def main() -> None:
    rows = []
    for label, ov in circumstances().items():
        plan = run_required_hours(load_parameters(overrides=ov))
        fines = plan["production_t"]["FeedLime fines"]
        target = 60000.0
        fines_alerts = [
            a for a in plan["alerts"] if "fines" in a.lower() and "objective" in a.lower()
        ]
        zones_ok = all(z["feasible"] for z in plan["zones"].values())
        rows.append(
            {
                "circumstance": label,
                "fines_t_per_year": fines,
                "objective_t": target,
                "objective_served": bool(abs(fines - target) <= 1.0),
                "zone_1_3_split_h": plan["zone_1_3_split"],
                "zone_1_3_utilization_pct": plan["zones"]["1.3"]["utilization_pct"],
                "all_zones_feasible": zones_ok,
                "fines_alerts": fines_alerts,
            }
        )
        print(
            f"{label:48s} fines {fines:9.0f} t "
            f"{'OK ' if rows[-1]['objective_served'] else 'MISS'} "
            f"z1.3 {plan['zones']['1.3']['utilization_pct']:.1f} % "
            f"feasible={zones_ok}"
        )

    commit = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True
    ).stdout.strip()
    OUT.write_text(
        json.dumps(
            {
                "_provenance": {
                    "engine_commit": commit,
                    "script": "scripts/fines_floor_verification.py",
                    "note": (
                        "Client guarantee check 2026-08-15: FeedLime fines "
                        "objective (60 000 t/y) across all ruled circumstances. "
                        "Runs AFTER the planning error-hunt fixes M-3/M-4/M-5 "
                        "(mass-consistent capped branches, dry-season 2C check, "
                        "scheduled-mode alerts)."
                    ),
                },
                "results": rows,
            },
            indent=1,
        )
    )
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
