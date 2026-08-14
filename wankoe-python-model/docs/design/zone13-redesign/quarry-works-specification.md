# QUARRY WORKS SPECIFICATION — Zone-1 inlet PSD target

**Status: ADOPTED by the client 2026-08-14** (margin definition: 20 % of
the AgLime market held free as operational flex; engine bisection on the
full two-mode annual plan, commit of record in the decision register).

## The objective in one line

Deliver a coarser blast/scalping product so that the zone-1 inlet
(measured at the PIVOT, downstream of the primary crusher CR.5003)
carries **40.1 % passing 20 mm** instead of today's 45.5 %.

## Target curve (cumulative passing, log-interpolated between points)

| Mesh (mm) | Target (%) | Mesh (mm) | Target (%) |
|---|---|---|---|
| 0.5 | 0.7 | 31.5 | 46.4 |
| 2.0 | 4.2 | 40 | 48.7 |
| 6.3 | 16.6 | 63 | 53.9 |
| 10 | 25.8 | 100 | 62.5 |
| **20 — control point** | **40.1** | 200 | 77.5 |
| 25 | 42.5 | 320 (top size, unchanged) | 100 |

Shape: size-rescale k = 1.426 of the measured 2026-08-08 belt-cut
(D50 moves 32 -> ~46 mm). Full curve: `quarry-target-curve-20pct-margin.json`.
Semi-log comparison chart: `quarry-target-curve-semilog.png`.

## Why this exact number

- Firm sales stay exactly served: KFS 85 000 + grits 40 000 + fines
  60 000 t/y (two-mode zone 1.3).
- AgLime baseline lands at 108 000 t (80 % of its 135 kt market): the
  remaining **27 000 t of market is the shock absorber** — if the quarry
  drifts FINER than target, the extra 0/20 is absorbed by pushing the
  AgLime 2C campaigns, never landfilled.
- 0/20 to landfill = 0 by construction, with that 20 % buffer.
- KFS Yield (live indicator, wet KFS stream / wet pivot feed) becomes
  self-consistent at **28.3 %** — the plant-side control number.

## Control protocol

1. **Measure at the pivot** — belt-cut PSD downstream of CR.5003, the
   project's standard measurement point (same protocol as 2026-08-08).
2. **Control point: % passing 20 mm.** Acceptance logic:
   - <= 40.1 %: on target or coarser — full flexibility available.
   - 40.1-45.5 %: workable — the AgLime campaigns absorb the excess;
     flexibility shrinks accordingly (KFS Yield alert quantifies it).
   - > 45.5 %: worse than today — landfill risk returns; escalate.
3. **Live monitor**: the engine's KFS Yield indicator (realized vs
   required) on every run — the gap in points x ~12 kt/y/pt is the
   landfill exposure.
4. Coarser than target is SAFE for the balance but watch CR.5009: feed
   F80 is already above the 150 mm max nip (standing alert) — top-size
   control at the primary matters as much as the fines fraction.
