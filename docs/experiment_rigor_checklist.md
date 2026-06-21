# Experiment Rigor Checklist

## v5 Evidence

- [x] High-fidelity local simulator benchmark.
- [x] Continuous execution with physics-style abort checks.
- [x] Eight random seeds.
- [x] Strong non-oracle baselines.
- [x] Oracle upper bound.
- [x] Paired seed-level comparisons.
- [x] Aggregate hard-regime evaluation.
- [x] Fixed-risk evaluation across four predefined budgets.
- [x] Ablations for partial geometry, reason labels, repeated memory, safety margin, calibration, dynamic-contact features, uncertainty quantiles, barrier inflation, and endpoint-only evidence.
- [x] Stress sweeps through maximum combined abort stress.
- [x] Negative cases.
- [x] Raw rollout and abort-evidence CSVs.
- [x] 39-page PDF built from frozen CSV artifacts.
- [x] Bright boxed in-text citations and reference links.
- [x] Reproducibility and validator scripts.

## Still Missing For ICLR Main

- [ ] Real robot validation.
- [ ] External robotics benchmark validation.
- [ ] Larger learned-policy or neural planner baselines.
- [ ] Full manual related-work synthesis.
- [ ] Qualitative videos or external rollout artifacts.

## Failed Local Gates

- [ ] Main success margin.
- [ ] Main paired lower-bound test.
- [ ] Over-conservatism check.
- [ ] Aggregate hard-regime check.
- [ ] Ablation-necessity check.
- [ ] Maximum-stress check.
- [ ] Fixed-risk check.

Decision: pass artifact-rigor gate, fail local evidence gate, fail ICLR-main readiness gate.
