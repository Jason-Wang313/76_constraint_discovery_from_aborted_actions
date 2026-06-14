# Reproducibility Checklist

- Code entry point: `python -m src.run_experiment`.
- Main phase: set `PAPER76_PHASE=main`.
- Ablation phase: set `PAPER76_PHASE=ablation`.
- Stress phase: set `PAPER76_PHASE=stress`.
- Finalization phase: set `PAPER76_PHASE=finalize`.
- Resume support: set `PAPER76_RESUME=1` after an interrupted phase.
- Seed chunking support: set `PAPER76_ONLY_SEEDS=0` or another comma-separated seed list.
- Stress-level chunking support: set `PAPER76_STRESS_LEVELS=0.40` or another comma-separated level list.
- Raw outputs: `results/rollouts.csv`, `results/abort_evidence.csv`, `results/stress_sweep_raw.csv`, `results/ablation_rollouts.csv`.
- Summary outputs: `results/metrics.csv`, `results/pairwise_stats.csv`, `results/ablation_metrics.csv`, `results/stress_sweep.csv`, `results/summary.txt`.
- Figures: `figures/constraint_discovery_final_success.png`, `figures/constraint_discovery_boundary_f1.png`, `figures/constraint_discovery_ablation_success.png`, `figures/constraint_discovery_stress_sweep.png`.

Known environment note: module execution was stable in this rebuild. Prefer `python -m src.run_experiment` over direct `python src/run_experiment.py`.
