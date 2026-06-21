# Paper 76 Expanded Submission Plan

Date: 2026-06-21

Paper: `76_constraint_discovery_from_aborted_actions`

Goal: rebuild Paper 76 into a serious 25+ page ICLR-style submission artifact while preserving hostile-review honesty. The paper may remain `STRONG_REVISE` if local evidence survives but external validation is still missing; it must become `KILL_ARCHIVE` if stronger local baselines or frozen stress tests refute the mechanism.

## Non-Negotiable Review Standard

- Do not optimize for pretty results.
- Optimize for a result that survives hostile review.
- Use strong baselines and stress tests to expose weaknesses.
- Improve the method during development.
- Freeze the final protocol before the full run.
- Report all predefined results honestly.

## Frozen Evaluation Targets

- Eight random seeds.
- Larger but CPU-light scenario counts.
- Main evaluation across nominal, hidden-wall, force-limit, human-stop, and combined-abort-stress splits.
- Aggregate hard-regime summary over hidden-wall, force-limit, human-stop, and combined-abort-stress splits.
- Stress sweep over combined hidden-constraint density, abort ambiguity, force/slip severity, and observation noise.
- Fixed-risk safety budget sweep.
- Mechanism ablations for partial geometry, reason labels, repeated abort memory, safe-trace calibration, barrier inflation, and uncertainty quantile terms.
- Negative-case mining from the decisive split.

## Strong Baselines To Add

- Existing visible-only, endpoint-negative, costmap, generic uncertainty filter, trace classifier, and oracle baselines.
- Robust barrier MPC that inflates inferred obstacle and abort-risk barriers.
- Conformal abort-risk filter that calibrates risk thresholding from safe and aborted trace evidence.
- Kernel trace constraint classifier that uses positive abort-tail and safe-trace densities.
- Particle constraint belief planner that samples multiple plausible hidden-constraint maps and plans against their upper confidence envelope.

## Proposed v5 Method

`abort_constraint_discovery_v5` should combine:

- Reason-conditioned partial-geometry updates from aborted traces.
- Repeated-abort surface fitting.
- Safe-trace calibration to avoid pure conservatism.
- Dynamic force/slip feature shaping.
- Quantile/uncertainty inflation for ambiguous abort evidence.
- Explicit safety-aware planning parameters.

The v5 method must not win by refusing to move. It must be checked against discovered-area, path efficiency, abstention, repeated aborts, and violation metrics.

## Submission-Readiness Gates

The final terminal decision is:

- `STRONG_REVISE` if v5 clears local success, repeated-abort, safety, ablation, aggregate, fixed-risk, and max-stress gates but still lacks external or hardware validation.
- `KILL_ARCHIVE` if v5 loses to a strong non-oracle baseline on the decisive local gates, if ablations match or beat the full method, or if fixed-risk/stress evidence shows the method is unsafe.

No local result alone should be marked ICLR-main-ready.

## Manuscript Requirements

- At least 25 pages without filler.
- Theory section with abort trace identifiability, safe-trace calibration, and limitations.
- Main results, aggregate hard-regime results, fixed-risk results, ablations, stress sweep, negative cases, and per-seed appendices.
- Bright boxed citation links that route in-text citations to the reference section.
- Explicit limitations and honest terminal decision.

## Validation Requirements

- Compile Python files.
- Validate expected CSV row counts.
- Generate figures and manuscript from results.
- Build BibTeX/PDF.
- Scan LaTeX log for hard warnings.
- Verify `C:/Users/wangz/Downloads/76.pdf` exists.
- Verify `C:/Users/wangz/Desktop/76.pdf` does not exist.
- Verify public GitHub repo and pushed commit.
