# 76 Constraint Discovery From Aborted Actions

Submission-hardening version: v5 expanded evidence audit

Terminal decision: KILL_ARCHIVE for ICLR main conference.

This repository contains a real local continuous 2D robot-planning benchmark for studying whether aborted actions can reveal hidden constraints for replanning. The v5 rebuild expanded the paper to a 39-page ICLR-style artifact, added stronger hostile baselines, aggregate hard-regime tests, fixed-risk budgets, stress sweeps, additional ablations, public reproducibility scripts, and bright boxed PDF citations.

The evidence is useful but not submission-ready. Under the frozen v5 gate, `abort_constraint_discovery_v5` reaches 0.545 +/- 0.059 closed-loop success on the decisive `combined_abort_stress` split, while the strongest non-oracle baseline, `robust_barrier_mpc`, reaches 0.884 +/- 0.052. The paired success difference is -0.339 +/- 0.074. Aggregate hard-regime, fixed-risk, maximum-stress, over-conservatism, and ablation-necessity gates also fail. The honest result is therefore `KILL_ARCHIVE`, not `STRONG_REVISE`.

## Main Result

Full v5 run:

- Main rollout rows: 6,720.
- Abort evidence rows: 4,368.
- Seed-level metric rows: 480.
- Aggregate hard-regime seed rows: 96.
- Ablation rollout rows: 800.
- Ablation seed rows: 80.
- Stress-sweep raw rows: 4,032.
- Fixed-risk raw rows: 2,048.
- Fixed-risk seed rows: 256.
- Seeds: 0 through 7.
- Evaluation scenarios per split: 14.
- Grid: 40 x 40 with continuous execution and hidden physics abort checks.
- Closed-loop replanning budget: 6 attempts.
- Risk budgets: 0.08, 0.12, 0.18, 0.25.

Combined-abort-stress summary:

- `oracle_constraints`: 0.911 +/- 0.044 success, repeated abort 0.205, boundary F1 1.000.
- `robust_barrier_mpc`: 0.884 +/- 0.052 success, repeated abort 0.250, boundary F1 0.396.
- `particle_constraint_belief`: 0.866 +/- 0.072 success, repeated abort 0.259, boundary F1 0.396.
- `kernel_trace_constraint_classifier`: 0.857 +/- 0.059 success, repeated abort 0.357, boundary F1 0.322.
- `abort_constraint_discovery`: 0.732 +/- 0.044 success, repeated abort 0.366, boundary F1 0.446.
- `abort_constraint_discovery_v5`: 0.545 +/- 0.059 success, repeated abort 0.170, boundary F1 0.432.
- `costmap_from_collisions`: 0.536 +/- 0.070 success.
- `risk_filter_uncertainty`: 0.500 +/- 0.075 success.
- `negative_label_baseline`: 0.188 +/- 0.064 success.
- `ignore_aborted_actions`: 0.027 +/- 0.026 success.

Failure summary:

- Main success margin fails against `robust_barrier_mpc`.
- Aggregate hard-regime success is 0.817 for ACD-v5 versus 0.962 for the strongest non-oracle methods.
- Fixed-risk success fails at all four predefined budgets.
- Maximum-stress success is 0.406 for ACD-v5 versus 0.734 for the best non-oracle method.
- Several ablations match the full v5 method, so component necessity is not established.
- Local-only evidence still lacks hardware and accepted external benchmark validation.

## Reproduce

Use module execution rather than direct file execution:

```powershell
$env:PAPER76_PHASE = "main"; python -m src.run_experiment
$env:PAPER76_PHASE = "ablation"; python -m src.run_experiment
$env:PAPER76_PHASE = "stress"; python -m src.run_experiment
$env:PAPER76_PHASE = "fixed_risk"; python -m src.run_experiment
$env:PAPER76_PHASE = "finalize"; python -m src.run_experiment
```

If a long phase is interrupted, rerun it with:

```powershell
$env:PAPER76_RESUME = "1"
```

Generate and validate the paper:

```powershell
python scripts/generate_manuscript.py
cd paper
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
cd ..
python scripts/validate_submission_artifacts.py
```

Canonical local PDF: `C:/Users/wangz/Downloads/76.pdf`

Validated PDF SHA256: `6FC325FF84FB16ACC5F86CB5FA908F1A68FAD5FAAC327C96D1907A2FA101A43E`

No PDF is copied to the visible Desktop.
