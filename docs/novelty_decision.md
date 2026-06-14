# Novelty Decision

Decision: conditionally novel, not yet submission-ready.

The local evidence supports a specific mechanism: aborted actions are partial observations of hidden constraints, and using abort geometry plus reason labels improves downstream replanning more than endpoint labels, costmaps, generic risk filters, or a trace classifier.

The novelty boundary is not "another safe planner" or "another uncertainty filter." The contribution is the representation and use of aborted partial trajectories as constraint-surface evidence.

The boundary remains vulnerable because related work in safety-constrained motion planning, control barrier functions, risk-aware planning, failure-aware robot learning, and human-robot safety is broad. A main-conference version needs a deeper manual synthesis and external validation.
