# Wankoe Python Model

**Static deterministic** calculation model of the WANKOE limestone processing
line (zones 1.1 / 1.2 / 1.3). For one parameter set (a "scenario") it
computes the synchronized "photo" of the whole line: flows, size
distributions, mass and water balances, powers, gaps to production targets.

Specification: `docs/WANKOE-cahier-des-charges-modele-v2026-08-08.docx`
(9 chapters, models M1-M8, machine sheets, flowsheet, reference case —
in French, the project's working language for specifications).

## Principles (the specification's golden rules)

1. **Data is separated from code**: every parameter lives in `data/*.json`
   and can be changed without reprogramming (enforced by
   `tests/test_parameters.py`, hardened after a dedicated parameterization
   audit on 2026-08-08).
2. Every formula symbol is defined (name, unit) — see the docstrings in
   `src/wankoe_model/models.py` and the `calibration` section of the data.
3. **Automatic mass + water closure** on every scenario (adjustable
   tolerance), reproduction of the chapter 9 reference case, tests shipped
   with the code.

## Layout

```
wankoe-python-model/
├── data/
│   ├── default_parameters.json      # ALL parameters (machines, calibration, products...)
│   └── reference_feed_curve.json    # CALIBRATED feed curve (hypothesis -> replace by measurement)
├── docs/                            # specification + input-data workbook (originals)
├── scripts/
│   ├── calibrate_reference_feed_curve.py  # pivot-curve fit on the chapter 9 case
│   └── run_sweep.py                 # automatic scenario sweep / optimum search (CLI)
├── src/wankoe_model/
│   ├── grid.py                      # mesh grid, PSD curves (cumulative % passing)
│   ├── models.py                    # common models M1-M8 (pure functions)
│   ├── flowsheet.py                 # zones 1.1/1.2/1.3, closed circuits, machine codes
│   ├── scenario.py                  # parameter loading + run_scenario (pure function)
│   └── optimize.py                  # parameter sweeps, scoring, ranking (spec §7.3/§8)
└── tests/                           # 48 tests: M1-M8 units, reference case, parameterization, sweeps
```

## Usage

```python
from wankoe_model import load_parameters, run_scenario, run_seasonal_balance

# default scenario (chapter 9 reference case)
results = run_scenario(load_parameters())
print(results["products"]["KFS"]["tph"])   # 59.1 t/h wet
print(results["balances"])                  # mass + water closure
print(results["alerts"])                    # bottlenecks, non-compliances, hypotheses

# modified scenario — NO code change
params = load_parameters(overrides={
    "machines": {"SR.5007": {"parameters": {"a1": {"default": 30}}}},
    "default_scenario": {"weather": "rain", "flow_rates_tph": {"zone_1_1_feed": 200}},
})
results = run_scenario(params)

# season-weighted yearly balance (dry/rain mix, spec §7.2)
seasonal = run_seasonal_balance(load_parameters(overrides={
    "default_scenario": {"zones": {
        "1.1": {"available_hours": 5000, "availability_pct": 80},
        "1.2": {"available_hours": 5000, "availability_pct": 80},
        "1.3": {"available_hours": 5000, "availability_pct": 80},
    }},
}))
```

`run_scenario` is a **pure function** (parameters -> results, no state).

## Automatic sweeps / optimum search

The engine never imposes an operating choice; `wankoe_model.optimize`
automates what a user does by hand — define many scenarios, run the photos,
score and rank them against the specification's arbitration rule (meet FIRM
targets, minimize unsellable surplus):

```bash
python scripts/run_sweep.py data/sweep_example.json -o data/sweep_results.json
```

The sweep config (JSON, no code) declares the variables (any parameter
path), the method (`grid` or seeded `random`), and the objective weights.
Results are ranked best-first with per-product tonnages, firm shortfall,
surplus and total installed power.

## Tests

```bash
pip install -e ".[dev]"
pytest
```

## Validation status (reference case, chapter 9)

| Quantity | Expected | Achieved | Deviation |
|---|---|---|---|
| 9.1 KFS | 59.3 t/h (23.7 %) | 59.1 t/h (23.6 %) | OK |
| 9.1 0/20 undersize | 190.7 t/h | 190.9 t/h | OK |
| 9.1 CR.5009 power | ~116 kW | 106 kW | -9 % (documented) |
| 9.1 CR.5011 power | ~37 kW | 18 kW at loop equilibrium; 45 kW net at the 125 t/h nameplate | see note below |
| 9.2 AgLime | 55.0 t/h | 55.0 t/h | OK |
| 9.3 Vapor | ~2.3 t/h | 2.26 t/h | OK |
| 9.3 Grits | 10.1 t/h | 10.1 t/h | OK (H-M7 fitted) |
| 9.3 UltraFin | ~1.3 t/h | 1.23 t/h | OK |
| 9.3 ML.26 power | ~45 kW | 51 kW | +13 % |
| 9.3 DY.03 burner | ~3.8 MW | 3.83 MW | OK |

## Measured feed curve (2026-08-08)

The default feed is now the REAL belt-cut measurement at the primary
crusher outlet (raw data: `data/feed_measurement_2026-08-08.json`; d50
32 mm, d80 180 mm, moisture 7 %). The model reproduces d50 = 32.3 mm and
d80 = 180.6 mm. Two completion hypotheses, both replaceable by data:
H-FEED-1 (fine tail < 19 mm: reference-curve shape renormalized to the
measured 45 % at 19 mm) and H-FEED-2 (top size: log-linear to 100 % at
320 mm). Rebuild with `scripts/build_feed_curve_from_measurement.py`.

Key impacts vs the hypothetical curve (250 t/h, mode 1A): KFS drops to
53.8 t/h (21.5 %), CR.5009 power rises to 141 kW, and the feed F80
(181 mm) exceeds the roll crusher's 150 mm nip limit — saturation alert.
The chapter 9 test suite keeps validating the model against the PINNED
calibrated curve, since chapter 9 was authored with it.

## Open hypotheses (flagged [H] in the data)

- **Feed fine tail** (< 19 mm) and **top size** (> 200 mm): hypotheses
  H-FEED-1 / H-FEED-2 above — a sieve analysis of the fine fraction would
  remove the main one.
- **M7 / ML.26**: the exact role of `comp_lam` is not specified ->
  hypothesis H-M7-1 (maximum reduction ratio per pass); attrition fines
  distribution -> hypothesis H-M7-2. Fitted on case 9.3, to be confirmed
  by plant trials.
- **Phi(<100 um)**: not measured -> UltraFin flagged "NOT CERTIFIED".
- **CR.5011**: the spec's ~37 kW matches the impactor evaluated AT its
  125 t/h nameplate capacity (Bond W x 125 = 37 kW with the spec's assumed
  F80 = 45 mm), not at the loop equilibrium the model computes (~38 t/h ->
  18 kW installed). A parameter study (screen imperfection, CR.5009
  uniformity) confirmed no plausible setting raises the equilibrium load to
  ~125 t/h. The model now reports BOTH figures (`P_installed_kW` at
  equilibrium and `P_net_at_capacity_kW`/`P_installed_at_capacity_kW` at
  nameplate); the residual gap (45 vs 37 kW net) comes from the loop's
  coarser F80 (~56 mm vs the spec's assumed 45 mm).
- **KFS "30/55/15" envelope** (spec §6): interpreted (validated 2026-08-08)
  as three %-passing control thresholds — max 30 % below 20 mm, min 55 %
  within 20-35, max 15 % above 35 mm. Wired as `output_products.KFS.envelope`
  (adjustable). The default scenario yields 27.6 / 56.9 / 15.5 %: the first
  two thresholds pass, the above-cut limit is marginally exceeded.

© Noezys — All rights reserved.
