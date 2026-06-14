# Claims

## Supported Claims

- The repository implements a real local continuous robot-planning benchmark for constraint discovery from aborted actions.
- Aborted trajectories carry useful geometric and semantic information about hidden constraints.
- `abort_constraint_discovery` improves closed-loop success on the decisive `combined_abort_stress` split relative to all non-oracle baselines.
- The proposed method reduces repeated aborts relative to endpoint-only, costmap, classifier, and generic uncertainty baselines.
- Partial abort geometry, abort reason labels, repeated-abort memory, and safety margins are useful components in the ablation suite.

## Unsupported Claims

- Do not claim ICLR-main readiness.
- Do not claim real-robot validation.
- Do not claim state-of-the-art safety-constrained motion planning.
- Do not claim external benchmark validation.
- Do not claim the discovered boundaries are oracle-quality.

## Terminal Claim

Paper 76 is a strong local simulator result: aborted actions are useful observations for hidden-constraint discovery, but the project remains `STRONG_REVISE` until validated on hardware or external robotics benchmarks.
