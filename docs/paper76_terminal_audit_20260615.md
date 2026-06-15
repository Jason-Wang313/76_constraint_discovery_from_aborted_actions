# Paper 76 Terminal Audit

Date: 2026-06-15 07:21:11 +0100
Paper: 76 - `constraint_discovery_from_aborted_actions`
Decision: `STRONG_REVISE`

## Verification Performed

- Compiled `src/run_experiment.py`.
- Verified required CSV artifacts and schemas.
- Confirmed evidence scale: 2,205 main rollout rows, 2,457 abort-evidence rows, 245 seed metric rows, 35 aggregate metric rows, 30 pairwise rows, 294 ablation rollout rows, 30 stress-sweep aggregate rows, 1,050 stress-sweep raw rows, and 10 curated negative cases.
- Confirmed seven seeds: 0 through 6.
- Confirmed required baselines: `constraint_classifier`, `risk_filter_uncertainty`, `costmap_from_collisions`, `negative_label_baseline`, `ignore_aborted_actions`, and `oracle_constraints`.
- Rebuilt the LaTeX/BibTeX PDF after fixing bibliography author warnings and fragile float placement warnings.
- Copied only `76.pdf` to Downloads.
- Confirmed no `C:/Users/wangz/Desktop/76.pdf` exists.

## Decisive Local Evidence

On `combined_abort_stress`:

- `abort_constraint_discovery`: 0.841 +/- 0.065 success, 0.381 repeated abort, 0.556 violation, 0.440 boundary F1, 0.251 path efficiency, 0.235 discovered area.
- `constraint_classifier`: 0.508 +/- 0.141 success, 0.556 repeated abort, 0.556 violation, 0.388 boundary F1, 0.263 path efficiency, 0.259 discovered area.
- `risk_filter_uncertainty`: 0.508 +/- 0.065 success, 0.714 repeated abort, 0.746 violation, 0.406 boundary F1, 0.213 path efficiency, 0.151 discovered area.
- `costmap_from_collisions`: 0.413 +/- 0.062 success, 0.746 repeated abort, 0.762 violation, 0.415 boundary F1.
- `oracle_constraints`: 0.857 +/- 0.062 success.

Paired comparisons:

- Versus `constraint_classifier`: +0.333 +/- 0.171 success, +0.175 repeated-abort reduction, +0.052 boundary-F1 difference, 6/7 better seeds.
- Versus `risk_filter_uncertainty`: +0.333 +/- 0.126 success, +0.190 violation reduction, +0.333 repeated-abort reduction, +0.034 boundary-F1 difference, 7/7 better seeds.
- Versus `costmap_from_collisions`: +0.429 +/- 0.088 success, +0.206 violation reduction, +0.365 repeated-abort reduction, 7/7 better seeds.

The local mechanism is supported: aborted partial trajectories provide useful hidden-constraint evidence beyond endpoint labels, costmaps, generic classifiers, and uncertainty filters.

## Non-Conservatism Gate

The win is not explained by refusing to move.

- Abstention is 0.000 for central methods.
- Versus `constraint_classifier`, discovered area is lower by 0.025 and path efficiency is only 0.012 lower.
- Versus `risk_filter_uncertainty`, path efficiency is higher by 0.038 and discovered area is higher by 0.083.

## Ablation Gate

The ablation evidence supports the mechanism locally.

- `abort_discovery_full`: 0.786 +/- 0.170 success.
- `abort_discovery_no_abort_reason_labels`: 0.643 +/- 0.111 success.
- `abort_discovery_no_partial_geometry`: 0.571 +/- 0.140 success.
- `abort_discovery_no_safety_margin`: 0.643 +/- 0.181 success.
- `abort_discovery_no_dynamic_contact_features`: 0.738 +/- 0.066 success.
- `abort_discovery_no_repeated_abort_memory`: 0.738 +/- 0.120 success.

## Stress Gate

The proposed method is the best non-oracle method at every stress level. At maximum stress level 1.00:

- `abort_constraint_discovery`: 0.657 success, 0.457 repeated abort, 0.486 violation, 0.461 boundary F1.
- `constraint_classifier`: 0.629 success, 0.429 repeated abort, 0.457 violation, 0.396 boundary F1.
- `risk_filter_uncertainty`: 0.486 success, 0.714 repeated abort, 0.771 violation, 0.387 boundary F1.
- `oracle_constraints`: 0.886 success.

The local stress result is positive but not enough for ICLR-main readiness because the validation remains local.

## Artifact Result

- PDF: `C:/Users/wangz/Downloads/76.pdf`
- SHA256: `AC30D3A0C37CD6A23DC3458E61BA3E4E15E501CB0AB45EFC74E44750AC09F7D9`
- Public GitHub: `https://github.com/Jason-Wang313/76_constraint_discovery_from_aborted_actions`

## Final Recommendation

Keep `STRONG_REVISE`. Do not submit as-is. A submission-ready revival requires hardware or accepted external benchmark validation, stronger learned-planner baselines, and a deeper manual related-work synthesis.
