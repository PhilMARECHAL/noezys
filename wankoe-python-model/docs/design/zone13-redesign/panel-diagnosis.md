# Panel round 1 — DIAGNOSIS (2026-08-14, engine-backed, commit d82a679)

Baseline: dried 29.85 t/h -> grits 7.79 t/h (26.1 %), fines 22.07, ratio 2.83.
Attribution: ML.26 compression spread (n_comp 0.86) 67 % · bed attrition
(S_att 0.171) 28 % · sliver-band leak 5 % · feed fines 0 % (feed blameless).
Counter-intuitive, engine-proven: closed loop & screen imperfection are NOT
ratio destroyers (perfect screens WORSEN ratio 2.83 -> 3.65; the loop
recovers 1.19 t/h of 1.5-2 into grits — at the cost of grits <2 mm = 15.4 %,
marginally over D6). Settings-only floor at current machine: 2.90 (810-run
sweep). SAME topology reaches <= 1.25 if the mill places >= 40 % of each
crushed tonne in 2-4 with <= 29 % < 1.5 (RR n >= 1.6 at x80 = 4); <= 1.0
needs n >= 1.8 or n 1.6 + attrition halved. IT IS A MACHINE PROBLEM.
Caveat: current n_comp 0.86 is itself hypothesis H-M7-1; the real ML.26
vendor curve could move the baseline either way.
(Full report in session log 2026-08-14; scripts in session scratchpad.)
