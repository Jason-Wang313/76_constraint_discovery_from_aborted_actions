# Final Audit

Paper: 76 constraint_discovery_from_aborted_actions

Version: v4

Terminal decision: STRONG_REVISE

## Evidence Completed

- Local continuous robot-planning benchmark with visible clutter and hidden constraints.
- Abort triggers: collision margin, fixture snag, force limit, human stop, unstable slip, visible collision, timeout.
- Seven seeds: 0 through 6.
- Five evaluation splits.
- 2,205 main rollout rows.
- 2,457 abort-evidence rows.
- 245 seed-level metric rows.
- 294 ablation rollout rows.
- 1,050 stress-sweep raw rows.
- 12 negative cases.

## Gate Result

The proposed method clears the local evidence gate, but not the ICLR-main submission gate.

- `abort_constraint_discovery`: 0.841 +/- 0.065 combined-abort-stress success.
- `constraint_classifier`: 0.508 +/- 0.141 combined-abort-stress success.
- `risk_filter_uncertainty`: 0.508 +/- 0.065 combined-abort-stress success.
- Paired success difference versus `constraint_classifier`: 0.333 +/- 0.171.
- Repeated-abort reduction versus `constraint_classifier`: 0.175.
- Boundary-F1 improvement versus `constraint_classifier`: 0.052.
- Oracle upper bound: 0.857 +/- 0.062 success.

## Audit Conclusion

The repo is now a real positive local-simulator artifact. It should not be submitted to ICLR main without external benchmark or hardware validation.
