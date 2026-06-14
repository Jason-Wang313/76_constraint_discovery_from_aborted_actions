# Hostile Reviewer Response

## Attack: This is just a costmap from failures.

Response: The v4 evidence includes endpoint-negative and costmap baselines. On `combined_abort_stress`, `costmap_from_collisions` reaches 0.413 +/- 0.062 success, while `abort_constraint_discovery` reaches 0.841 +/- 0.065.

## Attack: A conservative risk filter would solve this.

Response: `risk_filter_uncertainty` reaches 0.508 +/- 0.065 success and repeated abort 0.714. The proposed method reaches 0.841 +/- 0.065 success and repeated abort 0.381.

## Attack: A generic classifier over traces is enough.

Response: `constraint_classifier` ties the strongest baseline mean success at 0.508, but remains below the proposed method by a paired 0.333 +/- 0.171 success difference. The classifier also has lower boundary F1.

## Attack: The method wins by becoming over-conservative.

Response: The discovered-area difference versus `constraint_classifier` is -0.025, and path efficiency is only 0.012 lower. Versus `risk_filter_uncertainty`, the proposed method has higher efficiency by 0.038 and higher discovered area by 0.083. It is not simply refusing to move.

## Attack: The paper is still not ICLR-main-ready.

Response: Correct. The decision is `STRONG_REVISE`, not acceptance-ready. The missing pieces are hardware or external benchmark validation and a deeper manual literature synthesis.
