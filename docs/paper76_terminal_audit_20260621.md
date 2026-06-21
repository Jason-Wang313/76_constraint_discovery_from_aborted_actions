# Paper 76 Terminal Audit

Date: 2026-06-21 16:48:27 +08:00

Decision: `KILL_ARCHIVE`

## Final Evidence Scale

- Main rollout rows: 6,720.
- Abort evidence rows: 4,368.
- Seed metric rows: 480.
- Aggregate seed rows: 96.
- Ablation rows: 800.
- Ablation seed rows: 80.
- Stress rows: 4,032.
- Fixed-risk rows: 2,048.
- Fixed-risk seed rows: 256.
- Seeds: 0 through 7.
- Grid: 40 x 40.
- Evaluation scenarios per split: 14.
- Risk budgets: 0.08, 0.12, 0.18, 0.25.

## Decisive Result

On `combined_abort_stress`:

- `abort_constraint_discovery_v5`: 0.545 +/- 0.059 success.
- `robust_barrier_mpc`: 0.884 +/- 0.052 success.
- `particle_constraint_belief`: 0.866 +/- 0.072 success.
- `kernel_trace_constraint_classifier`: 0.857 +/- 0.059 success.
- Paired ACD-v5 minus strongest non-oracle success difference: -0.339 +/- 0.074.

## Failed Gates

- `main_success_margin`
- `main_paired_lower_bound`
- `over_conservatism`
- `aggregate_hard_regime`
- `ablation_necessity`
- `maximum_stress`
- `fixed_risk`

## PDF Audit

- Canonical PDF: `C:/Users/wangz/Downloads/76.pdf`
- Page count: 39
- SHA256: `6FC325FF84FB16ACC5F86CB5FA908F1A68FAD5FAAC327C96D1907A2FA101A43E`
- Desktop copy: absent
- Visual samples checked: title/decision page, citation boxes, main figures, stress/fixed-risk tables, appendix tables, and references.

## Terminal Action

Archive this version. The rigorous rebuild is valuable because it prevents an overclaimed submission, but the paper should not be submitted to ICLR main unless the method is redesigned and rerun under the same hostile protocol with hardware or accepted external benchmark validation.
