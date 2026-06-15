# Plan

Rebuild paper 76 `constraint_discovery_from_aborted_actions` into a real abort-physics evidence artifact, compile PDF to Downloads only, publish the exact-name public repo, and mark the ICLR-main gate honestly.

## 2026-06-15 Continuation Plan

- Re-run code integrity and result-schema gates without rerunning expensive experiments.
- Verify the full evidence scale: 2,205 main rollout rows, 2,457 abort-evidence rows, 245 seed metric rows, 294 ablation rollout rows, 1,050 stress-sweep raw rows, and 10 curated negative cases.
- Re-evaluate the decisive `combined_abort_stress` comparison against `constraint_classifier`, `risk_filter_uncertainty`, and `costmap_from_collisions`.
- Check whether gains are not merely conservative abstention or enlarged discovered area.
- Re-check ablations and stress sweeps.
- Rebuild the LaTeX/BibTeX PDF, copy only `76.pdf` to Downloads, and confirm no Desktop PDF exists.
- Update stale child docs and root reports, then commit and push the public GitHub repository.

## 2026-06-15 Continuation Result

The local positive evidence holds, so the decision remains `STRONG_REVISE`. `abort_constraint_discovery` reaches 0.841 +/- 0.065 success on `combined_abort_stress`, while `constraint_classifier` and `risk_filter_uncertainty` each reach 0.508. Paired success gains are 0.333 +/- 0.171 versus the classifier and 0.333 +/- 0.126 versus the risk filter. The method reduces repeated aborts versus those baselines and is the best non-oracle method at every stress level, including stress 1.00. It still lacks hardware and accepted external benchmark validation, so it is not ICLR-main-ready.
