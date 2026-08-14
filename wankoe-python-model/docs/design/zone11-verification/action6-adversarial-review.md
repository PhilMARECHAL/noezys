# Zone-1.1 internal confidence program — Action 6: adversarial formula review

**Date:** 2026-08-14 · **Mechanism:** two independent adversarial
reviewers (units/conventions lens; formula-fidelity lens), each
instructed to hunt for errors and forbidden to invent findings, each
claim backed by a numeric probe. Every finding adjudicated and closed.

## Verdict: high fidelity — 0 sign/inversion/exponent errors in M1-M8;
## 15 findings adjudicated: 3 code fixes, 6 doc/data fixes, 6 disclosed

### Fixed in code (engine behavior corrected)
| # | Finding | Fix |
|---|---|---|
| 1 | **M7 capped-regime bypass**: when the per-pass reduction cap raised the effective x80 above the gap, material in ]gap; effective_x80] bypassed UNBROKEN — particles wider than the roll gap surviving the pass, contradicting the documented mechanism | M1 gains an explicit `bypass_below` threshold; M7 pins it at the GAP. Converged defaults unchanged (cap only bound in transient loop iterations); capped regimes (e.g. comp_lam at its 1.8 min) now physical |
| 2 | **Capacity checks mixed dry loads with wet ratings**: CR.5011's 90 t/h vendor rating (wet) was compared against the dry loop stream — a ~7.5 % blind spot at 7 % moisture | `capacity_basis` declared per machine in data (CR.5011 wet — vendor; RC.1/RC.2 dry — engine-derived purchase specs at 0.5 % moisture); the check converts accordingly |
| 3 | **M6 phantom duty**: a no-drying pass still reported ~1.2 MW of solids-sensible burner duty | duty and burner now zero when no drying is needed |

### Fixed in docs/data (numbers were right, words were wrong)
M3 docstring no longer calls I "classic" — the d10/d90-vs-classic
convention gap is stated with the conversion formulas (Q3 family);
M1 anchor note added (P(x80)=0.8 BEFORE truncation, delivered ~0.83);
Phi_100 description now says "measure at THE CUT (65 µm), not 100 µm"
(latent data-entry trap defused); A_j unit label %, densities label
kg/m³; RC.2 "splits the feed" note corrected (no split needed — PSD is
flow-independent, mathematically equivalent); RC.1 alert message shows
its n_units; zone_1_1 now takes weather as an argument like zone_1_2.

### Disclosed, no change (intentional or negligible, now on record)
VSMA area on dry tonnage (~7.5 %, absorbed by the f0 fit, method ±20 %);
loop PSD criterion absolute-on-fractions under a "relative" name
(behaviorally sound at 1e-6); M1 truncation exact only on grid meshes
(<0.5 % between meshes, refined grid shrinks it); attrition-fines RR
truncated like every M1 product (cache key correct); dryer outlet
sensible heat neglected (~0.7 % of duty); dual sub-mesh convention
(<1 %, documented in M8).

### Categories verified CLEAN by probe
mm/µm, wet/dry at every model boundary, %/fraction, kWh/t→kW (η once,
never twice), M6 thermal chain, M8 air/Lapple (reproduces 4.2 µm),
per-hour/per-year, RR conventions, blending water bookkeeping, C1
composition (regrind blend, per-machine overrides reach m7).

**Confidence budget: formula-transcription residual CLOSED —
meta-score 91 % → 94 %, the internal ceiling. The remaining 6 pts are
external by nature: vendor gradation curves ([H] n, S_att), drop-weight
A·b (Q12), screen sieve test (Q3), repeat belt-cuts (RC4), NACO
design-curve reconciliation (RC7).**
