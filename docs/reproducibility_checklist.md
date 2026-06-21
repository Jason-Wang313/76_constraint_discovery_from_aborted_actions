# Reproducibility Checklist

- Code entry point: `python -m src.run_experiment`.
- Main phase: set `PAPER76_PHASE=main`.
- Ablation phase: set `PAPER76_PHASE=ablation`.
- Stress phase: set `PAPER76_PHASE=stress`.
- Fixed-risk phase: set `PAPER76_PHASE=fixed_risk`.
- Finalization phase: set `PAPER76_PHASE=finalize`.
- Resume support: set `PAPER76_RESUME=1` after an interrupted phase.
- Seed chunking support: set `PAPER76_ONLY_SEEDS=0` or another comma-separated seed list.
- Stress-level chunking support: set `PAPER76_STRESS_LEVELS=0.40` or another comma-separated level list.
- Risk-budget chunking support: set `PAPER76_RISK_BUDGETS=0.08` or another comma-separated budget list.
- Raw outputs: `results/rollouts.csv`, `results/abort_evidence.csv`, `results/stress_sweep_raw.csv`, `results/ablation_rollouts.csv`, `results/fixed_risk_raw.csv`.
- Summary outputs: `results/metrics.csv`, `results/pairwise_stats.csv`, `results/aggregate_metrics.csv`, `results/aggregate_pairwise_stats.csv`, `results/ablation_metrics.csv`, `results/stress_sweep.csv`, `results/fixed_risk_metrics.csv`, `results/fixed_risk_pairwise.csv`, `results/summary.txt`.
- Figures: `figures/constraint_discovery_final_success.png`, `figures/constraint_discovery_boundary_f1.png`, `figures/constraint_discovery_ablation_success.png`, `figures/constraint_discovery_stress_sweep.png`, `figures/constraint_discovery_fixed_risk.png`.
- Manuscript generator: `python scripts/generate_manuscript.py`.
- Artifact validator: `python scripts/validate_submission_artifacts.py`.
- Canonical PDF: `C:/Users/wangz/Downloads/76.pdf`.
- Validated SHA256: `6FC325FF84FB16ACC5F86CB5FA908F1A68FAD5FAAC327C96D1907A2FA101A43E`.

Known environment note: module execution was stable in this rebuild. Prefer `python -m src.run_experiment` over direct `python src/run_experiment.py`.
