# Zone-1.1 internal confidence program — Action 4: Monte Carlo band

**Date:** 2026-08-14 · **Mechanism:** 200 seeded draws (seed 7,
`scripts/monte_carlo_kfs_yield.py`, replayable) over the five uncertain
inputs, each range traceable to a register row: CR.5009 slope n
[1.05;1.65] (RC1), A_j [50;69] and b_j [0.6;1.3] (Q12), SR.5007 I
[0.10;0.20] (Q3), feed size-rescale [0.93;1.07] (RC4). Uniform and
independent — no better information exists before the vendor tests.

## The headline figure, with its honesty attached

| KFS Yield | Value |
|---|---|
| **P50 (median)** | **24.3 %** |
| P10 – P90 | **22.4 % – 26.0 %** |
| Full range (200 draws) | 21.6 % – 27.1 % |
| Naked point figure it replaces | 24.59 % (reference settings, all [H] at their hypothesis values) |

| Derived quantity | P10 | P50 | P90 |
|---|---|---|---|
| Implied 0/20 landfill (t/y, demand 212 079 fixed) | 30 474 | 52 715 | 83 234 |

- **KFS envelope compliant in 200/200 draws** (in-cut 77.9–92.7 %): the
  QUALITY of the KFS product is robust to every hypothesis — only the
  QUANTITY balance moves.
- Labeled pessimistic scenario OUTSIDE the band (full Q12 literature
  tail, b = 3.0 / A = 69): yield 21.8 %, landfill ~92.8 kt/y — the
  drop-weight test decides whether this tail is real.

## The two conclusions that survive EVERY draw

1. **The zero-landfill requirement (28.61 %) lies ABOVE the P90 (26.0 %)
   and even above the best draw (27.1 %)**: no plausible combination of
   model hypotheses makes the current feed close the landfill gap —
   the quarry-curve lever is INDISPENSABLE, not an artifact of one
   parameter choice. The project's central recommendation is
   hypothesis-robust.
2. Landfill stays strictly positive in all 200 draws (min band P10
   30.5 kt): the problem is real under every hypothesis.

**Confidence budget: naked-point-figure component (3 of its 8 pts
closable internally) CLOSED — meta-score 86 % → 89 %. The remaining
5 pts of that component are the [H] values themselves (vendor tests) and
the feed representativeness (repeat belt-cuts) — external by nature.**
