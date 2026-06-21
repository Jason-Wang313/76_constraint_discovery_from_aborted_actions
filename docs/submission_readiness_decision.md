# Submission Readiness Decision

Decision: KILL_ARCHIVE

ICLR main-conference readiness: NO.

Reason: The v5 expanded rebuild created a serious local artifact, but the proposed method fails the frozen hostile local gate. ACD-v5 reaches 0.545 +/- 0.059 success on the decisive split, while `robust_barrier_mpc` reaches 0.884 +/- 0.052. Aggregate hard-regime, fixed-risk, maximum-stress, over-conservatism, and ablation-necessity checks also fail.

Honest terminal action: archive this version. Do not submit it to ICLR main.

Revival condition: redesign the method so it beats robust-barrier, kernel-trace, and particle-belief baselines under the same frozen protocol, then validate on hardware or an accepted external robotics benchmark.
