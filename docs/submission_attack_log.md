# Submission Attack Log

Paper: 76 constraint_discovery_from_aborted_actions

This log records the v3 ICLR main-conference archive attack. The later v4 real abort-physics rebuild superseded the v3 local-evidence failure and moved the paper to `STRONG_REVISE`, not ICLR-main-ready.

## ICLR Main Gate Round 1
Attack: No real-robot validation.

Verdict: Fatal for ICLR main unless new external evidence is produced.

Action: Not recoverable within the existing local artifacts; archive rather than overclaim.

## ICLR Main Gate Round 2
Attack: No high-fidelity simulator validation.

Verdict: Fatal for ICLR main unless new external evidence is produced.

Action: Not recoverable within the existing local artifacts; archive rather than overclaim.

## ICLR Main Gate Round 3
Attack: Synthetic benchmark is generated from a shared template.

Verdict: Fatal for ICLR main unless new external evidence is produced.

Action: Not recoverable within the existing local artifacts; archive rather than overclaim.

## ICLR Main Gate Round 4
Attack: The mechanism is not empirically learned from real robot data.

Verdict: Fatal for ICLR main unless new external evidence is produced.

Action: Not recoverable within the existing local artifacts; archive rather than overclaim.

## ICLR Main Gate Round 5
Attack: Baselines are synthetic probability models, not implemented competing systems.

Verdict: Fatal for ICLR main unless new external evidence is produced.

Action: Not recoverable within the existing local artifacts; archive rather than overclaim.

## ICLR Main Gate Round 6
Attack: Prior-work threat set is metadata-derived and not a full manual related-work synthesis.

Verdict: Fatal for ICLR main unless new external evidence is produced.

Action: Not recoverable within the existing local artifacts; archive rather than overclaim.

## ICLR Main Gate Round 7
Attack: All papers share nearly identical experiment code, weakening paper-specific novelty.

Verdict: Fatal for ICLR main unless new external evidence is produced.

Action: Not recoverable within the existing local artifacts; archive rather than overclaim.

## ICLR Main Gate Round 8
Attack: No external benchmark comparison such as LIBERO, Meta-World, RLBench, BridgeData, or real manipulation suite.

Verdict: Fatal for ICLR main unless new external evidence is produced.

Action: Not recoverable within the existing local artifacts; archive rather than overclaim.

## ICLR Main Gate Round 9
Attack: No hardware failure modes are measured.

Verdict: Fatal for ICLR main unless new external evidence is produced.

Action: Not recoverable within the existing local artifacts; archive rather than overclaim.

## ICLR Main Gate Round 10
Attack: No learned representation, training curves, or model architecture is implemented.

Verdict: Fatal for ICLR main unless new external evidence is produced.

Action: Not recoverable within the existing local artifacts; archive rather than overclaim.

## ICLR Main Gate Round 11
Attack: No ablation is attached to a real model component; ablations are synthetic knobs.

Verdict: Fatal for ICLR main unless new external evidence is produced.

Action: Not recoverable within the existing local artifacts; archive rather than overclaim.

## ICLR Main Gate Round 12
Attack: No reviewer can reproduce a robotics system, only a diagnostic simulation.

Verdict: Fatal for ICLR main unless new external evidence is produced.

Action: Not recoverable within the existing local artifacts; archive rather than overclaim.

## ICLR Main Gate Round 13
Attack: No statistical test on real deployment outcomes.

Verdict: Fatal for ICLR main unless new external evidence is produced.

Action: Not recoverable within the existing local artifacts; archive rather than overclaim.

## ICLR Main Gate Round 14
Attack: No compute/data/model card for a trained WAM.

Verdict: Fatal for ICLR main unless new external evidence is produced.

Action: Not recoverable within the existing local artifacts; archive rather than overclaim.

## ICLR Main Gate Round 15
Attack: No evidence that the branch atlas can be inferred from observations.

Verdict: Fatal for ICLR main unless new external evidence is produced.

Action: Not recoverable within the existing local artifacts; archive rather than overclaim.

## ICLR Main Gate Round 16
Attack: No proof that the proposed mechanism beats strong real baselines.

Verdict: Fatal for ICLR main unless new external evidence is produced.

Action: Not recoverable within the existing local artifacts; archive rather than overclaim.

## ICLR Main Gate Round 17
Attack: Potential novelty collision with world models, uncertainty planning, conformal filters, and model-based RL remains unresolved.

Verdict: Fatal for ICLR main unless new external evidence is produced.

Action: Not recoverable within the existing local artifacts; archive rather than overclaim.

## ICLR Main Gate Round 18
Attack: The paper text is template-like across the batch.

Verdict: Fatal for ICLR main unless new external evidence is produced.

Action: Not recoverable within the existing local artifacts; archive rather than overclaim.

## ICLR Main Gate Round 19
Attack: The PDF is better framed as an archive memo than an ICLR submission.

Verdict: Recoverable by rewriting honesty, not by claiming readiness.

Action: Rewrite as ICLR main gate archive.

## ICLR Main Gate Round 20
Attack: Main-conference claim validity fails.

Verdict: Fatal for ICLR main unless new external evidence is produced.

Action: Not recoverable within the existing local artifacts; archive rather than overclaim.

## ICLR Main Gate Round 21
Attack: Advisor-name policy is respected but does not rescue technical evidence.

Verdict: Coverage probe only.

Action: Keep names weak and do not rank by them.

## ICLR Main Gate Round 22
Attack: Reproducibility is adequate for synthetic code but inadequate for robotics claims.

Verdict: Fatal for ICLR main unless new external evidence is produced.

Action: Not recoverable within the existing local artifacts; archive rather than overclaim.

## ICLR Main Gate Round 23
Attack: No figures from real rollouts or model predictions.

Verdict: Fatal for ICLR main unless new external evidence is produced.

Action: Not recoverable within the existing local artifacts; archive rather than overclaim.

## ICLR Main Gate Round 24
Attack: No dataset release beyond generated CSVs.

Verdict: Fatal for ICLR main unless new external evidence is produced.

Action: Not recoverable within the existing local artifacts; archive rather than overclaim.

## ICLR Main Gate Round 25
Attack: No causal identification of the mechanism.

Verdict: Fatal for ICLR main unless new external evidence is produced.

Action: Not recoverable within the existing local artifacts; archive rather than overclaim.

## ICLR Main Gate Round 26
Attack: No theoretical guarantee strong enough to replace empirical validation.

Verdict: Fatal for ICLR main unless new external evidence is produced.

Action: Not recoverable within the existing local artifacts; archive rather than overclaim.

## ICLR Main Gate Round 27
Attack: No meaningful recoverable ICLR-main issue remains after archiving.

Verdict: Terminal condition reached.

Action: v3 marked `KILL_ARCHIVE`; v4 reopened the idea with real local evidence and moved the current terminal decision to `STRONG_REVISE`.

## Continuation Attack 2026-06-15

The current v4 artifacts were attacked again.

- Code, CSV, BibTeX/PDF, public GitHub, and Downloads-only artifact gates passed.
- The local positive claim survives: `abort_constraint_discovery` reaches 0.841 +/- 0.065 success on `combined_abort_stress`, while `constraint_classifier` and `risk_filter_uncertainty` each reach 0.508.
- Paired proposed-minus-classifier success difference is 0.333 +/- 0.171 with 6/7 better seeds.
- Paired proposed-minus-risk-filter success difference is 0.333 +/- 0.126 with 7/7 better seeds.
- The result is not pure conservatism: central abstention is 0.000, discovered area is lower than the classifier by 0.025, and path efficiency is higher than the risk filter by 0.038.
- Stress gate is locally favorable: the proposed method is best non-oracle at every stress level and reaches 0.657 success at stress 1.00.
- ICLR-main gate still fails because no hardware or external benchmark validation is present.

Updated terminal action: keep `STRONG_REVISE`; do not submit as-is.
