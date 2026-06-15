# Final Audit

Paper: 76 constraint_discovery_from_aborted_actions

Version: v4

Terminal decision: STRONG_REVISE

## Evidence Completed

- Local continuous robot-planning benchmark with visible clutter and hidden constraints.
- Abort triggers: collision margin, fixture snag, force limit, human stop, unstable slip, visible collision, timeout.
- Seven seeds: 0 through 6.
- Five evaluation splits.
- 2,205 main rollout rows.
- 2,457 abort-evidence rows.
- 245 seed-level metric rows.
- 294 ablation rollout rows.
- 1,050 stress-sweep raw rows.
- 10 curated negative cases.

## Gate Result

The proposed method clears the local evidence gate, but not the ICLR-main submission gate.

- `abort_constraint_discovery`: 0.841 +/- 0.065 combined-abort-stress success.
- `constraint_classifier`: 0.508 +/- 0.141 combined-abort-stress success.
- `risk_filter_uncertainty`: 0.508 +/- 0.065 combined-abort-stress success.
- Paired success difference versus `constraint_classifier`: 0.333 +/- 0.171.
- Repeated-abort reduction versus `constraint_classifier`: 0.175.
- Boundary-F1 improvement versus `constraint_classifier`: 0.052.
- Oracle upper bound: 0.857 +/- 0.062 success.

## Audit Conclusion

The repo is now a real positive local-simulator artifact. It should not be submitted to ICLR main without external benchmark or hardware validation.

## Continuation Audit 2026-06-15

Rechecked gates:

- `python -m py_compile src/run_experiment.py` passed.
- CSV integrity passed after correcting stale documentation that claimed 12 negative cases; `results/negative_cases.csv` contains 10 data rows.
- Evidence scale matched: 2,205 main rollout rows, 2,457 abort-evidence rows, 245 seed-level metric rows, 35 aggregate metric rows, 30 pairwise rows, 294 ablation rollout rows, 30 stress-sweep aggregate rows, and 1,050 stress-sweep raw rows.
- Required baselines were present: `constraint_classifier`, `risk_filter_uncertainty`, `costmap_from_collisions`, `negative_label_baseline`, `ignore_aborted_actions`, and `oracle_constraints`.
- LaTeX/BibTeX rebuilt a 5-page PDF after repairing missing bibliography authors and fragile float placement warnings.
- `C:/Users/wangz/Downloads/76.pdf` SHA256 is `AC30D3A0C37CD6A23DC3458E61BA3E4E15E501CB0AB45EFC74E44750AC09F7D9`.
- `C:/Users/wangz/Desktop/76.pdf` does not exist.

The local positive result was reproduced. On `combined_abort_stress`, `abort_constraint_discovery` scores 0.841 +/- 0.065 success. The strongest non-oracle baselines, `constraint_classifier` and `risk_filter_uncertainty`, each score 0.508 success. Paired proposed-minus-classifier success difference is 0.333 +/- 0.171 with 6/7 better seeds; paired proposed-minus-risk-filter success difference is 0.333 +/- 0.126 with 7/7 better seeds.

The result is not merely conservatism. Versus `constraint_classifier`, discovered area is lower by 0.025 and path efficiency is only 0.012 lower. Versus `risk_filter_uncertainty`, path efficiency is higher by 0.038 and discovered area is higher by 0.083. Abstention is 0.000 for all central methods.

Ablations support the mechanism locally. The full ablation variant reaches 0.786 +/- 0.170 success; removing abort-reason labels drops to 0.643, removing partial geometry drops to 0.571, and removing safety margin drops to 0.643.

Stress evidence remains favorable but not decisive for ICLR main. At stress level 1.00, `abort_constraint_discovery` reaches 0.657 success, ahead of `constraint_classifier` at 0.629 and `risk_filter_uncertainty` at 0.486, but still below the oracle at 0.886.

Continuation decision: keep `STRONG_REVISE`, not ICLR-main-ready. The missing gates are external benchmark validation, hardware validation, and a deeper manual related-work synthesis.
