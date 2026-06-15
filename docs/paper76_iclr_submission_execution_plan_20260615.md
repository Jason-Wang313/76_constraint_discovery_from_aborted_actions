# Paper 76 ICLR-Main Submission-Readiness Execution Plan

Date: 2026-06-15
Paper: 76 - `constraint_discovery_from_aborted_actions`
Target venue posture: ICLR main only if local positive evidence is paired with enough external validity
Current terminal label entering audit: `STRONG_REVISE`

## Goal

Audit Paper 76 as a real submission candidate rather than a template-positive result. The central question is whether abort-derived constraint discovery is only a strong local-simulator finding, or whether the artifacts support an honest ICLR-main-ready claim.

## Decision Rule

Keep or strengthen `STRONG_REVISE` only if all of the following are true:

1. `abort_constraint_discovery` decisively beats the strongest non-oracle baselines on `combined_abort_stress`.
2. The method improves repeated-abort rate and hidden-boundary quality rather than only increasing conservatism.
3. Ablations show the proposed components are necessary.
4. Stress-sweep evidence remains favorable at high stress.
5. The PDF, raw CSVs, code, and public GitHub repository are reproducible and synchronized.

Upgrade to ICLR-main-ready only if, in addition to the local gates above, the repository contains credible external benchmark or hardware evidence, strong real-robot or high-fidelity validation, and a non-template related-work synthesis.

Downgrade to `KILL_ARCHIVE` if the local positive result does not survive direct verification or if stale documentation misstates the terminal decision.

## Evidence Gates

Run these checks before touching the terminal label:

1. Code integrity: compile `src/run_experiment.py`.
2. Result integrity: verify all CSVs exist, are nonempty, finite, and schema-valid.
3. Scale check: confirm 2,205 main rollout rows, 2,457 abort-evidence rows, 245 seed metric rows, 294 ablation rollout rows, and 1,050 stress-sweep raw rows.
4. Baseline check: confirm `constraint_classifier`, `risk_filter_uncertainty`, `costmap_from_collisions`, `negative_label_baseline`, `ignore_aborted_actions`, and `oracle_constraints` are present.
5. Local positive-evidence check: verify the proposed method beats the strongest non-oracle baselines on `combined_abort_stress`.
6. Non-conservatism check: verify success gains are not caused solely by larger discovered area, lower path efficiency, or abstention.
7. Ablation check: verify component ablations support the proposed mechanism.
8. Stress check: verify high-stress behavior against non-oracle baselines and oracle gap.
9. Documentation consistency check: reconcile stale `KILL_ARCHIVE` wording in old attack logs with the current `STRONG_REVISE` decision if the evidence supports it.
10. Paper build: run LaTeX/BibTeX to produce a clean PDF and copy only `76.pdf` to Downloads.
11. Artifact hygiene: confirm no numbered PDF is copied to the visible Desktop.
12. GitHub hygiene: confirm the matching public GitHub repository exists and the local commit is pushed.
13. Root-report hygiene: update `GLOBAL_POOL_STATUS.md`, `BATCH_STATUS.md`, `SUBMISSION_STATUS.md`, `MASTER_REPORT.md`, and `MASTER_SUBMISSION_REPORT.md`.

## Expected Risk

The existing summary reports a strong local result: 0.841 +/- 0.065 success for `abort_constraint_discovery` versus 0.508 for `constraint_classifier` and `risk_filter_uncertainty`, with paired success gain 0.333 +/- 0.171 versus `constraint_classifier`. However, the repository still appears to lack hardware or external benchmark validation. Unless direct verification finds such external evidence, Paper 76 should remain `STRONG_REVISE`, not ICLR-main-ready.

## Execution Order

1. Re-check repository cleanliness and result inventory.
2. Run code and CSV integrity gates.
3. Extract central, pairwise, ablation, and stress evidence.
4. Rebuild the paper PDF and repair recoverable build warnings.
5. Update stale child docs and write a terminal continuation audit.
6. Update root reports through Paper 76.
7. Commit and push the Paper 76 repository.
8. Verify `Downloads/76.pdf`, no Desktop copy, public GitHub visibility, clean git state, and root report consistency.
