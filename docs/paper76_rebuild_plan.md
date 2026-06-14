# Paper 76 Rebuild Plan: Constraint Discovery From Aborted Actions

Date: 2026-06-14

## Goal

Rebuild Paper 76 into a real ICLR-main-target robotics submission candidate, or terminate it honestly as `STRONG_REVISE` / `KILL_ARCHIVE` if the evidence does not justify submission. The central question is whether aborted or interrupted robot actions provide useful evidence for hidden constraints that a planner should infer and respect.

## Core Claim To Test

Robots often abort actions because of force limits, incipient collision, joint-limit approach, fixture snagging, unstable contact, or human interruption. These aborted trajectories are not just failures; they are partial observations of hidden constraints. A constraint-discovery system should infer these constraints and improve future planning more than treating aborted actions as negative labels, deleting them, or using generic uncertainty/risk filters.

## High-Fidelity Benchmark

Build a local robot planning benchmark with physics-based contact and safety aborts. The benchmark should include:

- Planar mobile manipulator or pusher navigating cluttered fixtures.
- Contact-rich pushing or insertion tasks with hidden walls, soft stops, force thresholds, and workspace/joint limits.
- Abort triggers from force spikes, collision margins, torque limits, unstable slip, fixture snagging, and human-style stop zones.
- Partial aborted trajectories that reveal constraint boundaries before task completion.

Each rollout should log:

- State/action traces up to completion or abort.
- True hidden constraints: forbidden regions, force-limit surfaces, contact/no-go boundaries, and dynamic instability zones.
- Abort reason labels: force, collision, torque/joint limit, slip, fixture snag, human stop, timeout.
- Planner belief about constraints before and after aborted evidence.
- Task success, abort rate, violation rate, path efficiency, calibration, and discovered-constraint quality.

Evaluation splits:

- `nominal_known_constraints`: constraints are visible or easy.
- `hidden_wall_abort`: aborts reveal unobserved no-go regions.
- `force_limit_abort`: force/torque stops reveal load and contact constraints.
- `human_stop_constraint`: interruption zones are sparse and ambiguous.
- `combined_abort_stress`: hidden geometry, force limits, sparse aborts, dynamic contact, and noisy observations overlap.

## Methods To Implement

- `ignore_aborted_actions`: trains/plans only on completed trajectories.
- `negative_label_baseline`: treats aborted actions as failed endpoints without geometry inference.
- `costmap_from_collisions`: occupancy/costmap update from abort endpoints.
- `risk_filter_uncertainty`: generic conservative uncertainty/risk filter.
- `constraint_classifier`: learned constraint boundary classifier from all traces.
- `abort_constraint_discovery`: proposed method; infers constraint surfaces from partial aborted trajectories and uses them in planning.
- `oracle_constraints`: upper bound with true hidden constraints.

## Metrics

- Closed-loop task success.
- Constraint violation rate.
- Abort rate and repeated-abort rate.
- Hidden-constraint boundary F1 / IoU.
- Path efficiency and completion time.
- Calibration of predicted violation probability.
- Safety margin under stress.
- Data efficiency: improvement per aborted trajectory observed.

## Experimental Rigor

- Use seven random seeds unless runtime becomes impossible.
- Use multiple constraint families and multiple task layouts.
- Evaluate downstream replanning after abort evidence, not just constraint classification.
- Report mean, 95 percent confidence intervals, and paired comparisons against the strongest non-oracle baseline.
- Include ablations: no partial trajectory geometry, no abort reason labels, no repeated-abort memory, no safety margin, no uncertainty calibration, no dynamic-contact features.
- Include stress sweeps over hidden-constraint density, abort noise, force thresholds, observation noise, human-stop sparsity, and contact instability.
- Save raw rollouts, abort traces, per-seed metrics, summary metrics, pairwise statistics, ablations, stress sweeps, negative cases, figures, and a training/run summary.

## Submission Gate

The paper can only move above archive if `abort_constraint_discovery` beats the strongest non-oracle baseline on `combined_abort_stress` closed-loop success with a meaningful paired effect, reduces constraint violations/repeated aborts, improves hidden-constraint boundary quality, and does not simply become over-conservative. If risk filters, costmaps, or generic classifiers match or beat it, the paper remains `KILL_ARCHIVE` or at best `STRONG_REVISE`.

## Deliverables

- Replace the synthetic scaffold with a reproducible physics-based abort/constraint discovery benchmark runner.
- Generate raw rollout/abort CSVs, metrics, pairwise statistics, ablations, stress sweeps, negative cases, figures, and `training_summary.csv`.
- Rewrite README, claims, novelty boundary, hostile review, reproducibility checklist, final audit, and ICLR gate around actual evidence.
- Rewrite `paper/main.tex` as either a real negative-result paper or a submission-candidate manuscript.
- Compile `paper/main.pdf`, copy exactly to `C:/Users/wangz/Downloads/76.pdf`, and do not copy any PDF to Desktop.
- Commit and push the final Paper 76 repo, then update shared root reports before moving to Paper 77.
