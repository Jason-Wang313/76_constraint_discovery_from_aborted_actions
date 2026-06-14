# Experiment Rigor Checklist

## v4 Evidence

- [x] High-fidelity local simulator benchmark.
- [x] Continuous execution with physics-style abort checks.
- [x] Seven random seeds.
- [x] Strong non-oracle baselines.
- [x] Oracle upper bound.
- [x] Paired seed-level comparisons.
- [x] Ablations for partial geometry, reason labels, repeated memory, safety margin, calibration, and dynamic-contact features.
- [x] Stress sweeps.
- [x] Negative cases.
- [x] Raw rollout and abort-evidence CSVs.
- [x] Reproducibility instructions.

## Still Missing For ICLR Main

- [ ] Real robot validation.
- [ ] External robotics benchmark validation.
- [ ] Larger learned-policy or neural planner baselines.
- [ ] Full manual related-work synthesis.
- [ ] Qualitative videos or external rollout artifacts.

Decision: pass local evidence gate, fail ICLR-main readiness gate.
