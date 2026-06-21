# Final Audit

Paper: 76 constraint_discovery_from_aborted_actions

Version: v5 expanded evidence audit

Terminal decision: KILL_ARCHIVE

## Evidence Completed

- Local continuous robot-planning benchmark with visible clutter and hidden constraints.
- Abort triggers: collision margin, fixture snag, force limit, human stop, unstable slip, visible collision, timeout.
- Eight seeds: 0 through 7.
- Five evaluation splits with 14 scenarios per split.
- 40 x 40 grid and six closed-loop replanning attempts.
- 6,720 main rollout rows.
- 4,368 abort-evidence rows.
- 480 seed-level metric rows.
- 96 aggregate hard-regime seed rows.
- 800 ablation rollout rows.
- 80 ablation seed rows.
- 4,032 stress-sweep raw rows.
- 2,048 fixed-risk raw rows.
- 256 fixed-risk seed rows.
- 12 curated negative cases.
- 39-page compiled PDF with bright boxed citations and reference links.

## Gate Result

The proposed v5 method fails the frozen local evidence gate.

- `abort_constraint_discovery_v5`: 0.545 +/- 0.059 combined-abort-stress success.
- `robust_barrier_mpc`: 0.884 +/- 0.052 combined-abort-stress success.
- `particle_constraint_belief`: 0.866 +/- 0.072 combined-abort-stress success.
- `kernel_trace_constraint_classifier`: 0.857 +/- 0.059 combined-abort-stress success.
- Paired success difference versus `robust_barrier_mpc`: -0.339 +/- 0.074.
- Violation reduction versus the strongest baseline: 0.107.
- Repeated-abort reduction versus the strongest baseline: 0.080.
- Boundary-F1 difference versus the strongest baseline: 0.036.
- Efficiency difference versus the strongest baseline: -0.135.
- Oracle upper bound: 0.911 +/- 0.044 success.

Failed predefined gates:

- `main_success_margin`
- `main_paired_lower_bound`
- `over_conservatism`
- `aggregate_hard_regime`
- `ablation_necessity`
- `maximum_stress`
- `fixed_risk`

## Fixed-Risk Result

At every predefined risk budget, ACD-v5 loses to a hostile non-oracle method.

- Budget 0.08: ACD-v5 0.469 success; best non-oracle `robust_barrier_mpc` 0.922.
- Budget 0.12: ACD-v5 0.547 success; best non-oracle `robust_barrier_mpc` 0.938.
- Budget 0.18: ACD-v5 0.500 success; best non-oracle `particle_constraint_belief` 0.938.
- Budget 0.25: ACD-v5 0.469 success; best non-oracle `robust_barrier_mpc` 0.859.

## Audit Conclusion

The artifact is a serious negative result, not a submission-ready paper. It demonstrates that aborted-action traces can reduce repeated aborts and violations, but under stronger baselines that advantage does not translate into enough closed-loop success, efficiency, or component necessity. The honest terminal action is `KILL_ARCHIVE`.

## Artifact Audit 2026-06-21

Rechecked gates:

- `python scripts/validate_submission_artifacts.py` passed.
- Full CSV row counts matched the frozen v5 protocol.
- `C:/Users/wangz/Downloads/76.pdf` has 39 pages.
- `C:/Users/wangz/Downloads/76.pdf` SHA256 is `6FC325FF84FB16ACC5F86CB5FA908F1A68FAD5FAAC327C96D1907A2FA101A43E`.
- `C:/Users/wangz/Desktop/76.pdf` does not exist.
- Visual PDF samples checked: title/decision page, boxed citations, result plots, appendix tables, and bibliography pages.

Continuation decision: keep `KILL_ARCHIVE`. Do not submit as-is. A revival requires a redesigned method that survives robust-barrier, kernel-trace, and particle-belief baselines, plus accepted external benchmark or hardware validation.
