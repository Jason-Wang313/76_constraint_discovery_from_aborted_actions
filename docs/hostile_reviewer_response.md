# Hostile Reviewer Response

## Attack: This is just a costmap from failures.

Response: The older ACD-v4 method beats the costmap baseline, but the expanded ACD-v5 method does not survive stronger hostile baselines. This attack alone is not fatal; the stronger barrier, kernel-trace, and particle-belief baselines are fatal.

## Attack: A conservative risk filter or barrier planner would solve this.

Response: Accepted. Under the frozen v5 protocol, `robust_barrier_mpc` reaches 0.884 +/- 0.052 success on `combined_abort_stress`, while ACD-v5 reaches 0.545 +/- 0.059. ACD-v5 reduces violations and repeated aborts, but it sacrifices too much closed-loop success and efficiency.

## Attack: A generic trace model is enough.

Response: Mostly accepted. `kernel_trace_constraint_classifier` reaches 0.857 +/- 0.059 success on the decisive split and 0.962 aggregate hard-regime success. ACD-v5 reaches 0.545 and 0.817, respectively.

## Attack: The method wins by becoming over-conservative.

Response: The v5 method does not win. It has lower violation and repeated-abort rates than several baselines, but the lower success and efficiency indicate excessive caution or miscalibrated constraint expansion rather than a submission-quality planner.

## Attack: The ablations do not prove component necessity.

Response: Accepted. Matching ablations include `abort_discovery_v5_no_partial_geometry`, `abort_discovery_v5_no_repeated_abort_memory`, `abort_discovery_v5_no_safety_margin`, and `abort_discovery_v5_no_uncertainty_quantile`.

## Attack: The paper is still not ICLR-main-ready.

Response: Correct. The terminal decision is `KILL_ARCHIVE`, not `STRONG_REVISE`. The paper fails local hostile-review gates before even reaching the independent hardware and external-benchmark blockers.
