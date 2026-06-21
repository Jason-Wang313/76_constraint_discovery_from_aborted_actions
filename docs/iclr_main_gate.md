# ICLR Main Gate

Gate status: KILL_ARCHIVE.

The v5 expanded audit does not clear the local empirical gate. The proposed ACD-v5 method improves some safety-side metrics, but the strongest hostile non-oracle baselines achieve much higher closed-loop success under the frozen protocol.

Fatal local failures:

- `robust_barrier_mpc` beats ACD-v5 on the decisive `combined_abort_stress` split: 0.884 versus 0.545 success.
- Aggregate hard-regime success is 0.962 for the strongest baselines versus 0.817 for ACD-v5.
- Fixed-risk checks fail at all four predefined budgets.
- Maximum-stress success is 0.406 for ACD-v5 versus 0.734 for the best non-oracle method.
- Several ablations match the full v5 method, so component necessity is not established.

Independent ICLR-readiness blockers also remain: no hardware validation, no accepted external robotics benchmark validation, no learned-policy stack comparison, and no full manual related-work synthesis.

Required action before any revival: redesign the method and rerun the frozen hostile protocol. Do not submit this paper to ICLR main in its current form.
