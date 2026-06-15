# Submission Version Log

## v1 - Generated Draft

- Original continuation-batch generated paper and toy single-seed experiment.

## v2 - Submission Hardening

- Added hostile reviewer attack log and response docs.
- Replaced the toy experiment with seven-seed synthetic metrics, stronger baselines, ablations, stress tests, and negative cases.
- Narrowed claims to synthetic diagnostic evidence.
- Terminal decision: WORKSHOP_ONLY.

## v3 - ICLR Main Gate Archive

- Applied the stricter ICLR-main-conference standard.
- Determined that missing real/high-fidelity evidence and template-generated experiments were fatal.
- Terminal decision: KILL_ARCHIVE.

## v4 - Real Abort-Physics Rebuild

- Replaced the synthetic scaffold with a continuous hidden-constraint discovery benchmark.
- Added abort-evidence rollouts, implemented baselines, oracle, paired stats, ablations, stress sweeps, figures, and a rewritten manuscript.
- `abort_constraint_discovery` beats all non-oracle baselines on `combined_abort_stress`.
- Terminal decision: STRONG_REVISE because hardware and external benchmark validation are still missing.

## 2026-06-15 Continuation Audit

- Rechecked code, CSV, ablation, stress, BibTeX/PDF, artifact-location, public-GitHub, and stale-documentation gates.
- Corrected stale negative-case documentation from 12 to the actual 10 data rows in `results/negative_cases.csv`.
- Rebuilt the PDF after adding bibliography authors and replacing fragile `[h]` float specifiers.
- Terminal decision remains: STRONG_REVISE because the local result is positive but not externally validated.
