# Paper 76 Protocol Freeze

Date: 2026-06-21

Purpose: freeze the v5 hostile-review protocol before interpreting the final result.

## Frozen Evaluation

- Seeds: 0 through 7.
- Grid: 40 x 40.
- Evaluation scenarios per split: 14.
- Ablation scenarios: 10.
- Stress scenarios: 8.
- Fixed-risk scenarios: 8.
- Maximum replanning attempts: 6.
- Risk budgets: 0.08, 0.12, 0.18, 0.25.
- Decisive split: `combined_abort_stress`.
- Aggregate hard-regime splits: `hidden_wall_abort`, `force_limit_abort`, `human_stop_constraint`, `combined_abort_stress`.

## Frozen Baselines

- `ignore_aborted_actions`
- `negative_label_baseline`
- `costmap_from_collisions`
- `risk_filter_uncertainty`
- `constraint_classifier`
- `robust_barrier_mpc`
- `conformal_abort_risk_filter`
- `kernel_trace_constraint_classifier`
- `particle_constraint_belief`
- `oracle_constraints`

## Frozen Decision Rule

The paper can only remain alive if ACD-v5 clears all local gates:

- main success margin against the strongest non-oracle baseline
- paired lower-bound success test
- violation and repeated-abort reductions without over-conservatism
- aggregate hard-regime success
- ablation necessity
- maximum-stress survival
- fixed-risk survival across all predefined risk budgets

If any required local gate fails, the terminal decision is `KILL_ARCHIVE`. External hardware and benchmark validation would still be required even after a local pass.
