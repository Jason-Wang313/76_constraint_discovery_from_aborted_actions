# ICLR Main Gate

Gate status: STRONG_REVISE.

The v4 rebuild clears the local empirical gate: the proposed method beats all non-oracle baselines on the decisive `combined_abort_stress` split with seven seeds, paired statistics, ablations, and stress sweeps.

It does not clear the ICLR-main submission gate because:

- The benchmark is local and diagnostic, not an accepted external robotics benchmark.
- No real robot experiments are present.
- The baselines are implemented planning systems, but not large learned robotic policy stacks.
- The related-work synthesis is still based primarily on the local hostile pool rather than a full manual literature audit.

Required action before submission: external validation plus a stronger manual related-work pass.
