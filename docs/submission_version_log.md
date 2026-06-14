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
