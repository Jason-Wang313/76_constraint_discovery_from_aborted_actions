# Child Status 76

Current stage: 2026-06-21 expanded v5 terminal audit
Last update: 2026-06-21 16:48:27 +08:00
PDF: C:/Users/wangz/Downloads/76.pdf
GitHub: https://github.com/Jason-Wang313/76_constraint_discovery_from_aborted_actions
Submission-hardening version: v5 expanded evidence audit
Terminal decision: KILL_ARCHIVE
ICLR main ready: no

Evidence: 6,720 main rollouts, 4,368 abort-evidence rows, 800 ablation rollouts, 4,032 stress-sweep rows, 2,048 fixed-risk rows, eight seeds, 40 x 40 grid, 14 scenarios per split, and four fixed-risk budgets.

Expanded audit 2026-06-21: code compile, full CSV integrity, manuscript generation, BibTeX/PDF rebuild, visual PDF sampling, Desktop exclusion, and validator gates passed. The current PDF is 39 pages at `C:/Users/wangz/Downloads/76.pdf` with SHA256 `6FC325FF84FB16ACC5F86CB5FA908F1A68FAD5FAAC327C96D1907A2FA101A43E`.

The v5 method does not survive the stronger frozen local gate. On `combined_abort_stress`, `abort_constraint_discovery_v5` reaches 0.545 +/- 0.059 success, while `robust_barrier_mpc` reaches 0.884 +/- 0.052. Aggregate hard-regime, fixed-risk, maximum-stress, over-conservatism, and ablation-necessity gates fail. The terminal decision is `KILL_ARCHIVE`.
