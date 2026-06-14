# 76 Constraint Discovery From Aborted Actions

Submission-hardening version: v4

Terminal decision: STRONG_REVISE for ICLR main conference, not submission-ready.

This repository now contains a real Paper 76 rebuild: a local continuous 2D robot-planning benchmark with hidden walls, fixture snags, force-limit regions, human-stop zones, unstable-slip regions, visible clutter, aborted action traces, closed-loop replanning, seven-seed evaluation, strong non-oracle baselines, ablations, stress sweeps, negative cases, figures, and a rewritten manuscript.

The evidence supports the mechanism locally, but the paper still lacks hardware and external benchmark validation. On the decisive `combined_abort_stress` split, `abort_constraint_discovery` reaches 0.841 +/- 0.065 closed-loop success. The strongest non-oracle baselines, `constraint_classifier` and `risk_filter_uncertainty`, reach 0.508 success. The paired success difference versus `constraint_classifier` is 0.333 +/- 0.171. The method also reduces repeated aborts and improves hidden-boundary F1, but it remains below an oracle and is not ICLR-main-ready.

## Main Result

Full run:

- Main rollout rows: 2,205.
- Abort evidence rows: 2,457.
- Seed-level metric rows: 245.
- Ablation rollout rows: 294.
- Stress-sweep raw rows: 1,050.
- Seeds: 0 through 6.
- Evaluation scenarios per split: 9.
- Grid: 38 x 38 with continuous execution and hidden physics abort checks.
- Closed-loop replanning budget: 5 attempts.

Combined-abort-stress summary:

- `oracle_constraints`: 0.857 +/- 0.062 success, repeated abort 0.222, boundary F1 1.000.
- `abort_constraint_discovery`: 0.841 +/- 0.065 success, repeated abort 0.381, boundary F1 0.440.
- `constraint_classifier`: 0.508 +/- 0.141 success, repeated abort 0.556, boundary F1 0.388.
- `risk_filter_uncertainty`: 0.508 +/- 0.065 success, repeated abort 0.714, boundary F1 0.406.
- `costmap_from_collisions`: 0.413 +/- 0.062 success, repeated abort 0.746, boundary F1 0.415.
- `negative_label_baseline`: 0.127 +/- 0.111 success.
- `ignore_aborted_actions`: 0.016 +/- 0.031 success.

## Reproduce

Use module execution rather than direct file execution:

```powershell
$env:PAPER76_PHASE = "main"; python -m src.run_experiment
$env:PAPER76_PHASE = "ablation"; python -m src.run_experiment
$env:PAPER76_PHASE = "stress"; python -m src.run_experiment
$env:PAPER76_PHASE = "finalize"; python -m src.run_experiment
```

If a long phase is interrupted, rerun it with:

```powershell
$env:PAPER76_RESUME = "1"
```

Outputs are written under `results/` and `figures/`.

## Rebuild PDF

```powershell
cd paper
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Canonical local PDF: `C:/Users/wangz/Downloads/76.pdf`

No PDF is copied to the visible Desktop.
