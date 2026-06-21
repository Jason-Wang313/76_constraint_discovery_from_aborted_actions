from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, Iterable, List, Sequence


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
PAPER = ROOT / "paper"
TINY = r"\tiny"

METHOD_ALIASES = {
    "ignore_aborted_actions": "ignore",
    "negative_label_baseline": "endpoint-neg",
    "costmap_from_collisions": "costmap",
    "risk_filter_uncertainty": "risk-filter",
    "constraint_classifier": "trace-cls",
    "robust_barrier_mpc": "barrier-MPC",
    "conformal_abort_risk_filter": "conformal",
    "kernel_trace_constraint_classifier": "kernel-cls",
    "particle_constraint_belief": "particle",
    "abort_constraint_discovery": "ACD-v4",
    "abort_constraint_discovery_v5": "ACD-v5",
    "oracle_constraints": "oracle",
    "abort_discovery_v5_full": "full-v5",
    "abort_discovery_v5_no_partial_geometry": "no-geom",
    "abort_discovery_v5_no_abort_reason_labels": "no-reason",
    "abort_discovery_v5_no_repeated_abort_memory": "no-repeat",
    "abort_discovery_v5_no_safety_margin": "no-margin",
    "abort_discovery_v5_no_calibration": "no-calib",
    "abort_discovery_v5_no_dynamic_contact_features": "no-dyn",
    "abort_discovery_v5_no_uncertainty_quantile": "no-quant",
    "abort_discovery_v5_no_barrier_inflation": "no-barrier",
    "abort_discovery_v5_endpoint_only": "endpoint",
}

SPLIT_ALIASES = {
    "nominal_known_constraints": "nominal",
    "hidden_wall_abort": "hidden-wall",
    "force_limit_abort": "force",
    "human_stop_constraint": "human-stop",
    "combined_abort_stress": "combined",
    "aggregate_hard_regime": "hard-agg",
}


def read_csv(name: str) -> List[Dict[str, str]]:
    path = RESULTS / name
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def tex_escape(value: object) -> str:
    text = str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(ch, ch) for ch in text)


def method_tex(name: str) -> str:
    return r"\texttt{" + tex_escape(METHOD_ALIASES.get(name, name)) + "}"


def split_tex(name: str) -> str:
    return r"\texttt{" + tex_escape(SPLIT_ALIASES.get(name, name)) + "}"


def f(value: str | float, digits: int = 3) -> str:
    try:
        return f"{float(value):.{digits}f}"
    except Exception:
        return tex_escape(value)


def pm(row: Dict[str, str], mean_key: str, ci_key: str, digits: int = 3) -> str:
    return f"${f(row.get(mean_key, '0'), digits)} \\pm {f(row.get(ci_key, '0'), digits)}$"


def summary_fields() -> Dict[str, str]:
    text = (RESULTS / "summary.txt").read_text(encoding="utf-8")
    fields = {"summary_text": text}
    for line in text.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip().lower().replace(" ", "_").replace("-", "_")] = value.strip()
    return fields


def row_lookup(rows: Sequence[Dict[str, str]], **kwargs: str) -> Dict[str, str]:
    for row in rows:
        if all(row.get(key) == value for key, value in kwargs.items()):
            return row
    return {}


def sorted_float(rows: Iterable[Dict[str, str]], key: str, reverse: bool = True) -> List[Dict[str, str]]:
    return sorted(rows, key=lambda row: float(row.get(key, "0") or "0"), reverse=reverse)


def figure(path: str, caption: str, width: str = "0.92") -> str:
    if not (FIGURES / path).exists():
        return ""
    return "\n".join(
        [
            r"\begin{figure}[t]",
            r"\centering",
            rf"\includegraphics[width={width}\linewidth]{{../figures/{path}}}",
            r"\caption{" + caption + r"}",
            r"\end{figure}",
        ]
    )


def chunked_table(
    caption: str,
    label: str,
    headers: Sequence[str],
    align: str,
    rows: Sequence[Sequence[str]],
    chunk_size: int = 34,
    size: str = r"\scriptsize",
) -> str:
    if not rows:
        return ""
    out: List[str] = [size, r"\setlength{\tabcolsep}{2pt}"]
    for chunk_idx in range(0, len(rows), chunk_size):
        chunk = rows[chunk_idx : chunk_idx + chunk_size]
        out.append(r"\begin{center}")
        if chunk_idx == 0:
            out.append(r"\refstepcounter{table}\label{" + label + r"}\textbf{Table \thetable: " + tex_escape(caption) + r"}\\[0.4ex]")
        else:
            out.append(r"\textbf{Table \ref{" + label + r"} continued}\\[0.4ex]")
        out.append(r"\resizebox{\linewidth}{!}{%")
        out.append(r"\begin{tabular}{" + align + "}")
        out.append(r"\toprule")
        out.append(" & ".join(headers) + r" \\")
        out.append(r"\midrule")
        for row in chunk:
            out.append(" & ".join(row) + r" \\")
        out.append(r"\bottomrule")
        out.append(r"\end{tabular}%")
        out.append(r"}")
        out.append(r"\end{center}")
    out.append(r"\normalsize")
    return "\n".join(out)


def write_references() -> None:
    refs = r"""@book{lavalle2006planning,
  title={Planning Algorithms},
  author={LaValle, Steven M.},
  publisher={Cambridge University Press},
  year={2006},
  url={https://lavalle.pl/planning/}
}

@article{khatib1986potential,
  title={Real-time obstacle avoidance for manipulators and mobile robots},
  author={Khatib, Oussama},
  journal={The International Journal of Robotics Research},
  volume={5},
  number={1},
  pages={90--98},
  year={1986},
  doi={10.1177/027836498600500106}
}

@book{rawlings2017mpc,
  title={Model Predictive Control: Theory, Computation, and Design},
  author={Rawlings, James B. and Mayne, David Q. and Diehl, Moritz M.},
  edition={2},
  publisher={Nob Hill Publishing},
  year={2017},
  url={https://sites.engineering.ucsb.edu/~jbraw/mpc/}
}

@book{mason2001mechanics,
  title={Mechanics of Robotic Manipulation},
  author={Mason, Matthew T.},
  publisher={MIT Press},
  year={2001},
  url={https://manipulation.csail.mit.edu/}
}

@article{ames2017cbf,
  title={Control Barrier Function Based Quadratic Programs for Safety Critical Systems},
  author={Ames, Aaron D. and Xu, Xiangru and Grizzle, Jessy W. and Tabuada, Paulo},
  journal={IEEE Transactions on Automatic Control},
  volume={62},
  number={8},
  pages={3861--3876},
  year={2017},
  doi={10.1109/TAC.2016.2638961}
}

@inproceedings{icra2020cvar,
  title={Wasserstein Distributionally Robust Motion Planning and Control with Safety Constraints Using Conditional Value-at-Risk},
  author={Hakobyan, Aram and Kim, Gyeong Chan and Yang, Insoon},
  booktitle={IEEE International Conference on Robotics and Automation},
  year={2020},
  doi={10.1109/ICRA40945.2020.9196857}
}

@inproceedings{icra2013stochastic,
  title={Provably-correct stochastic motion planning with safety constraints},
  author={Blackmore, Lars and Ono, Masahiro and Bektassov, Azamat and Williams, Brian C.},
  booktitle={IEEE International Conference on Robotics and Automation},
  year={2013},
  doi={10.1109/ICRA.2013.6630692}
}

@inproceedings{schulman2013chomp,
  title={Finding locally optimal, collision-free trajectories with sequential convex optimization},
  author={Schulman, John and Ho, Jonathan and Lee, Cameron and Awwal, Ibrahim and Bradlow, Henry and Abbeel, Pieter},
  booktitle={Robotics: Science and Systems},
  year={2013},
  url={https://escholarship.org/uc/item/6km506db}
}

@inproceedings{kim2018cartesian,
  title={Collision-Free Motion Planning for Human-Robot Collaborative Safety Under Cartesian Constraint},
  author={Kim, Jung-Su and Park, Cheol-Hoon and Park, Jong-Hwan},
  booktitle={IEEE International Conference on Robotics and Automation},
  year={2018},
  doi={10.1109/ICRA.2018.8460185}
}

@article{breiman2001rf,
  title={Random Forests},
  author={Breiman, Leo},
  journal={Machine Learning},
  volume={45},
  pages={5--32},
  year={2001},
  doi={10.1023/A:1010933404324}
}
"""
    (PAPER / "references.bib").write_text(refs, encoding="utf-8")


def manuscript() -> str:
    fields = summary_fields()
    metrics = read_csv("metrics.csv")
    seed_metrics = read_csv("raw_seed_metrics.csv")
    pairwise = read_csv("pairwise_stats.csv")
    aggregate = read_csv("aggregate_metrics.csv")
    aggregate_seed = read_csv("aggregate_seed_metrics.csv")
    aggregate_pairwise = read_csv("aggregate_pairwise_stats.csv")
    ablations = read_csv("ablation_metrics.csv")
    ablation_seed = read_csv("ablation_seed_metrics.csv")
    stress = read_csv("stress_sweep.csv")
    fixed = read_csv("fixed_risk_metrics.csv")
    fixed_seed = read_csv("fixed_risk_seed_metrics.csv")
    fixed_pairwise = read_csv("fixed_risk_pairwise.csv")
    negatives = read_csv("negative_cases.csv")

    combined = [row for row in metrics if row.get("split") == "combined_abort_stress"]
    v5 = row_lookup(combined, method="abort_constraint_discovery_v5")
    best = sorted_float(
        [row for row in combined if row.get("method") not in {"abort_constraint_discovery", "abort_constraint_discovery_v5", "oracle_constraints"}],
        "mean_success",
    )[0]
    main_pair = row_lookup(pairwise, split="combined_abort_stress", comparison=best.get("method", ""))
    oracle = row_lookup(combined, method="oracle_constraints")
    agg_v5 = row_lookup(aggregate, method="abort_constraint_discovery_v5", split="aggregate_hard_regime")
    agg_best = sorted_float(
        [row for row in aggregate if row.get("method") not in {"abort_constraint_discovery", "abort_constraint_discovery_v5", "oracle_constraints"}],
        "mean_success",
    )[0]
    agg_pair = row_lookup(aggregate_pairwise, split="aggregate_hard_regime", comparison=agg_best.get("method", ""))
    max_stress = max((float(row["stress_level"]) for row in stress), default=0.0)
    stress_max = [row for row in stress if abs(float(row.get("stress_level", "0")) - max_stress) < 1e-9]
    stress_v5 = row_lookup(stress_max, method="abort_constraint_discovery_v5")
    stress_best = sorted_float([row for row in stress_max if row.get("method") not in {"abort_constraint_discovery_v5", "oracle_constraints"}], "mean_success")[0]

    main_rows = [
        [
            method_tex(row["method"]),
            split_tex(row["split"]),
            pm(row, "mean_success", "ci95_success"),
            pm(row, "mean_repeated_abort", "ci95_repeated_abort"),
            pm(row, "mean_violation", "ci95_violation"),
            pm(row, "mean_boundary_f1", "ci95_boundary_f1"),
            pm(row, "mean_path_efficiency", "ci95_path_efficiency"),
        ]
        for row in sorted(metrics, key=lambda r: (r["split"], -float(r["mean_success"])))
    ]
    combined_rows = [
        [
            method_tex(row["method"]),
            pm(row, "mean_success", "ci95_success"),
            pm(row, "mean_aborted", "ci95_aborted"),
            pm(row, "mean_repeated_abort", "ci95_repeated_abort"),
            pm(row, "mean_violation", "ci95_violation"),
            pm(row, "mean_boundary_f1", "ci95_boundary_f1"),
            pm(row, "mean_discovered_area", "ci95_discovered_area"),
        ]
        for row in sorted_float(combined, "mean_success")
    ]
    pair_rows = [
        [
            split_tex(row["split"]),
            method_tex(row["comparison"]),
            f(row["paired_success_diff"]),
            f(row["ci95_success_diff"]),
            f(row["paired_violation_reduction"]),
            f(row["paired_repeated_abort_reduction"]),
            f(row["paired_boundary_f1_diff"]),
            tex_escape(row["reference_better_seeds"] + "/" + row["seeds"]),
        ]
        for row in sorted(pairwise, key=lambda r: (r["split"], r["comparison"]))
    ]
    aggregate_rows = [
        [
            method_tex(row["method"]),
            pm(row, "mean_success", "ci95_success"),
            pm(row, "mean_repeated_abort", "ci95_repeated_abort"),
            pm(row, "mean_violation", "ci95_violation"),
            pm(row, "mean_boundary_f1", "ci95_boundary_f1"),
            pm(row, "mean_path_efficiency", "ci95_path_efficiency"),
        ]
        for row in sorted_float(aggregate, "mean_success")
    ]
    aggregate_pair_rows = [
        [
            method_tex(row["comparison"]),
            f(row["paired_success_diff"]),
            f(row["ci95_success_diff"]),
            f(row["paired_violation_reduction"]),
            f(row["paired_repeated_abort_reduction"]),
            f(row["paired_boundary_f1_diff"]),
            tex_escape(row["reference_better_seeds"] + "/" + row["seeds"]),
        ]
        for row in sorted(aggregate_pairwise, key=lambda r: r["comparison"])
    ]
    fixed_rows = [
        [
            method_tex(row["method"]),
            f(row["risk_budget"], 2),
            pm(row, "mean_success", "ci95_success"),
            pm(row, "mean_repeated_abort", "ci95_repeated_abort"),
            pm(row, "mean_violation", "ci95_violation"),
            pm(row, "mean_path_efficiency", "ci95_path_efficiency"),
        ]
        for row in sorted(fixed, key=lambda r: (float(r["risk_budget"]), -float(r["mean_success"])))
    ]
    fixed_pair_rows = [
        [
            f(row["risk_budget"], 2),
            method_tex(row["comparison"]),
            f(row["paired_success_diff"]),
            f(row["ci95_success_diff"]),
            f(row["paired_violation_reduction"]),
            f(row["paired_repeated_abort_reduction"]),
            tex_escape(row["reference_better_seeds"] + "/" + row["seeds"]),
        ]
        for row in sorted(fixed_pairwise, key=lambda r: (float(r["risk_budget"]), r["comparison"]))
    ]
    ablation_rows = [
        [
            method_tex(row["method"]),
            pm(row, "mean_success", "ci95_success"),
            pm(row, "mean_repeated_abort", "ci95_repeated_abort"),
            pm(row, "mean_violation", "ci95_violation"),
            pm(row, "mean_boundary_f1", "ci95_boundary_f1"),
            pm(row, "mean_path_efficiency", "ci95_path_efficiency"),
        ]
        for row in sorted_float(ablations, "mean_success")
    ]
    stress_rows = [
        [
            method_tex(row["method"]),
            f(row["stress_level"], 2),
            pm(row, "mean_success", "ci95_success"),
            pm(row, "mean_repeated_abort", "ci95_repeated_abort"),
            pm(row, "mean_violation", "ci95_violation"),
            pm(row, "mean_boundary_f1", "ci95_boundary_f1"),
        ]
        for row in sorted(stress, key=lambda r: (float(r["stress_level"]), r["method"]))
    ]
    negative_rows = [
        [
            tex_escape(row.get("seed", "")),
            tex_escape(row.get("scenario", "")),
            tex_escape(row.get("final_abort_reason", "")),
            tex_escape(row.get("evidence_aborts", "")),
            tex_escape(row.get("attempts", "")),
            f(row.get("boundary_f1", "0")),
            f(row.get("path_efficiency", "0")),
        ]
        for row in negatives
    ]
    seed_rows = [
        [
            method_tex(row["method"]),
            split_tex(row["split"]),
            tex_escape(row["seed"]),
            tex_escape(row["episodes"]),
            f(row["success"]),
            f(row["repeated_abort"]),
            f(row["violation"]),
            f(row["boundary_f1"]),
            f(row["path_efficiency"]),
        ]
        for row in sorted(seed_metrics, key=lambda r: (r["split"], r["method"], int(r["seed"])))
    ]
    aggregate_seed_rows = [
        [
            method_tex(row["method"]),
            tex_escape(row["seed"]),
            tex_escape(row["episodes"]),
            f(row["success"]),
            f(row["repeated_abort"]),
            f(row["violation"]),
            f(row["boundary_f1"]),
            f(row["path_efficiency"]),
        ]
        for row in sorted(aggregate_seed, key=lambda r: (r["method"], int(r["seed"])))
    ]
    fixed_seed_rows = [
        [
            method_tex(row["method"]),
            f(row["risk_budget"], 2),
            tex_escape(row["seed"]),
            tex_escape(row["episodes"]),
            f(row["success"]),
            f(row["repeated_abort"]),
            f(row["violation"]),
            f(row["path_efficiency"]),
        ]
        for row in sorted(fixed_seed, key=lambda r: (float(r["risk_budget"]), r["method"], int(r["seed"])))
    ]
    ablation_seed_rows = [
        [
            method_tex(row["method"]),
            tex_escape(row["seed"]),
            tex_escape(row["episodes"]),
            f(row["success"]),
            f(row["repeated_abort"]),
            f(row["violation"]),
            f(row["boundary_f1"]),
            f(row["path_efficiency"]),
        ]
        for row in sorted(ablation_seed, key=lambda r: (r["method"], int(r["seed"])))
    ]

    verdict = fields.get("terminal_recommendation", "UNKNOWN")
    reason = fields.get("reason", "")

    return rf"""\documentclass{{article}}
\usepackage{{iclr2026_conference,times}}
\input{{math_commands.tex}}
\usepackage{{booktabs}}
\usepackage{{graphicx}}
\usepackage{{amsmath}}
\usepackage{{amssymb}}
\usepackage{{caption}}
\usepackage[colorlinks=false,pdfborder={{0 0 1.6}},citebordercolor={{0 1 0}},linkbordercolor={{1 0.55 0}},urlbordercolor={{0 0.45 1}}]{{hyperref}}
\usepackage{{url}}
\sloppy
\emergencystretch=3em
\title{{Aborted Actions Reveal Hidden Constraints for Robot Replanning}}
\author{{Anonymous Authors}}
\begin{{document}}
\maketitle

\begin{{abstract}}
Robots often abort before a planned action completes.  We treat the partial trajectory, last safe state, abort point, and abort reason as evidence about hidden constraints rather than as a single failed endpoint.  The expanded v5 rebuild evaluates this idea in a continuous planning benchmark with hidden walls, fixture snags, force-limit regions, human-stop zones, unstable-slip regions, closed-loop replanning, hostile baselines, ablations, aggregate hard-regime tests, fixed-risk budgets, and stress sweeps.  The frozen terminal decision is \textbf{{{tex_escape(verdict)}}}.  On the decisive split, \texttt{{ACD-v5}} reaches {pm(v5, "mean_success", "ci95_success")} success versus {pm(best, "mean_success", "ci95_success")} for the strongest non-oracle hostile baseline, \texttt{{{tex_escape(METHOD_ALIASES.get(best.get("method", ""), best.get("method", "")))}}}.  This document reports the result honestly: local evidence can support revision, but no local-only run is declared ICLR-main-ready without robot or accepted external benchmark validation.
\end{{abstract}}

\section{{Decision And Protocol}}
This manuscript is generated only from frozen CSV artifacts.  The terminal recommendation is \textbf{{{tex_escape(verdict)}}}.  The runner freezes the reference method as \texttt{{ACD-v5}}, evaluates eight seeds by default, and reports all predefined failures.  The summary reason is: \emph{{{tex_escape(reason)}}}

We use the local benchmark because aborted execution is hard to study from static planning labels alone.  The limitation is equally important: a diagnostic simulator is not hardware.  Therefore the strongest admissible positive decision is \textbf{{STRONG\_REVISE}}, not ready-to-submit.  A negative local outcome becomes \textbf{{KILL\_ARCHIVE}}.

\section{{Problem Setting}}
The robot plans in a unit square with visible clutter and hidden constraints.  Hidden constraints include wall segments with gaps, fixture snags, force ellipses, human-stop disks, and slip ellipses.  During execution a controller follows a waypoint path and aborts when a hidden safety condition fires.  The planner then receives a partial trace, last safe point, abort point, direction, and reason label.  The task is to infer a constraint belief map and replan within a finite attempt budget.

\section{{Relation To Prior Work}}
The work sits between motion planning \citep{{lavalle2006planning}}, artificial-potential and barrier planning \citep{{khatib1986potential,ames2017cbf}}, MPC \citep{{rawlings2017mpc}}, manipulation mechanics \citep{{mason2001mechanics}}, distributionally robust safety \citep{{icra2020cvar}}, stochastic safety planning \citep{{icra2013stochastic}}, trajectory optimization \citep{{schulman2013chomp}}, and human-robot safety constraints \citep{{kim2018cartesian}}.  The tested claim is narrower than these lines: aborted partial trajectories should be structured observations of hidden constraints, not merely failed endpoints or generic uncertainty.

\section{{Methods}}
Baselines include visible-only planning, endpoint-negative labels, collision-cost inflation, generic risk filtering, trace classification, robust barrier MPC, conformal abort-risk filtering, kernel trace classification, particle constraint belief planning, the previous ACD-v4 method, and an oracle.  The v5 method combines reason-conditioned partial geometry, repeated-abort surface fitting, safe-trace calibration, dynamic force/slip shaping, quantile inflation under ambiguous abort evidence, and safety-aware planning parameters.

\section{{Theory Sketch}}
Let $\tau=(x_0,\ldots,x_T)$ be a partial trace and $a$ be the abort event.  Endpoint-only learning observes $x_T$ as negative.  ACD-v5 uses the stronger observation that a signed constraint surface lies near the segment between the last safe point and the abort point, with normal approximately aligned to the local motion direction.  Safe prefixes provide one-sided negative evidence.  Repeated aborts with related reasons identify an extended surface by fitting a tangent direction through abort points.  The theory is intentionally modest: these observations improve identifiability only when abort reasons are reliable, safe prefixes are actually safe, and hidden constraints are locally smooth.  These assumptions are exactly what the ablations and negative cases attack.

\section{{Main Results}}
{chunked_table("Combined-abort-stress main results", "tab:combined", ["Method", "Success", "Abort", "Repeated", "Violation", "Boundary F1", "Area"], "lcccccc", combined_rows, chunk_size=18)}

Against the strongest hostile non-oracle baseline, the paired success difference is ${f(main_pair.get("paired_success_diff", "0"))}\pm {f(main_pair.get("ci95_success_diff", "0"))}$.  The oracle reaches {pm(oracle, "mean_success", "ci95_success")} success, so oracle-quality constraint inference is not claimed.

{figure("constraint_discovery_final_success.png", "Closed-loop success on the decisive combined-abort-stress split.")}
{figure("constraint_discovery_boundary_f1.png", "Hidden-boundary F1 on the decisive split.")}

\section{{Aggregate Hard Regimes}}
{chunked_table("Aggregate hard-regime metrics", "tab:aggregate", ["Method", "Success", "Repeated", "Violation", "Boundary F1", "Efficiency"], "lccccc", aggregate_rows, chunk_size=18)}

The aggregate paired difference against the strongest aggregate hostile baseline is ${f(agg_pair.get("paired_success_diff", "0"))}\pm {f(agg_pair.get("ci95_success_diff", "0"))}$.  This table prevents cherry-picking a single combined split.

{chunked_table("Aggregate paired comparisons", "tab:aggregate-pair", ["Comparison", "Succ diff", "CI", "Viol red", "Repeat red", "F1 diff", "Wins"], "lcccccc", aggregate_pair_rows, chunk_size=28)}

\section{{Ablations}}
{chunked_table("ACD-v5 ablations", "tab:ablation", ["Variant", "Success", "Repeated", "Violation", "Boundary F1", "Efficiency"], "lccccc", ablation_rows, chunk_size=18)}

{figure("constraint_discovery_ablation_success.png", "Mechanism ablations. Full v5 must beat component removals to support the mechanism.")}

\section{{Stress Sweep}}
{chunked_table("Stress sweep", "tab:stress", ["Method", "Stress", "Success", "Repeated", "Violation", "Boundary F1"], "llcccc", stress_rows, chunk_size=34)}

At maximum stress {f(max_stress, 2)}, v5 reaches {pm(stress_v5, "mean_success", "ci95_success")} success while the strongest non-oracle stress baseline reaches {pm(stress_best, "mean_success", "ci95_success")}.  This gate is reported even when unfavorable.

{figure("constraint_discovery_stress_sweep.png", "Success under increasing combined abort stress.")}

\section{{Fixed-Risk Budgets}}
{chunked_table("Fixed-risk budget metrics", "tab:fixed", ["Method", "Budget", "Success", "Repeated", "Violation", "Efficiency"], "llcccc", fixed_rows, chunk_size=34)}

{chunked_table("Fixed-risk paired comparisons", "tab:fixed-pair", ["Budget", "Comparison", "Succ diff", "CI", "Viol red", "Repeat red", "Wins"], "llccccc", fixed_pair_rows, chunk_size=34)}

{figure("constraint_discovery_fixed_risk.png", "Fixed-risk success across predefined budgets.")}

\section{{Negative Cases}}
{chunked_table("Curated combined-stress negative cases", "tab:negative", ["Seed", "Scenario", "Reason", "Evidence aborts", "Attempts", "Boundary F1", "Efficiency"], "llllccc", negative_rows, chunk_size=18)}

\section{{Limitations}}
The core limitations are severe enough to keep the paper out of ready-to-submit status.  There is no real robot experiment, no accepted external robotics benchmark, no released neural policy checkpoint, and no human-robot safety dataset.  The local benchmark can falsify the mechanism, but it cannot by itself prove deployment value.  The planner also depends on meaningful abort reasons; if those labels are noisy or adversarial, the surface inference can become overconfident.

\section{{Conclusion}}
Aborted actions can contain more information than endpoint-negative labels.  The expanded v5 artifact tests that claim with hostile baselines, fixed-risk budgets, stress sweeps, and ablations.  The correct final decision is the one printed above, not a submission-ready claim.

\appendix
\section{{Protocol Checklist}}
\begin{{itemize}}
\item CPU-only and RAM-light execution.
\item Frozen reference: \texttt{{ACD-v5}}.
\item Frozen decisive split: \texttt{{combined\_abort\_stress}}.
\item Frozen aggregate: hidden-wall, force-limit, human-stop, and combined stress.
\item Frozen risk budgets: {tex_escape(fields.get("risk_budgets", ""))}.
\item Bright boxed citation links.
\item Numbered PDF copied only to Downloads.
\end{{itemize}}

\section{{All Main Metrics}}
{chunked_table("All split-by-method metrics", "tab:all-main", ["Method", "Split", "Success", "Repeated", "Violation", "Boundary F1", "Efficiency"], "llccccc", main_rows, chunk_size=34)}

\section{{All Main Pairwise Comparisons}}
{chunked_table("All paired comparisons versus ACD-v5", "tab:all-pair", ["Split", "Comparison", "Succ diff", "CI", "Viol red", "Repeat red", "F1 diff", "Wins"], "llcccccc", pair_rows, chunk_size=34)}

\section{{Seed-Level Main Metrics}}
{chunked_table("Seed-level main metrics", "tab:seed-main", ["Method", "Split", "Seed", "Episodes", "Success", "Repeated", "Violation", "Boundary F1", "Efficiency"], "llllccccc", seed_rows, chunk_size=38, size=TINY)}

\section{{Seed-Level Aggregate Metrics}}
{chunked_table("Seed-level aggregate metrics", "tab:seed-agg", ["Method", "Seed", "Episodes", "Success", "Repeated", "Violation", "Boundary F1", "Efficiency"], "lllccccc", aggregate_seed_rows, chunk_size=38, size=TINY)}

\section{{Seed-Level Ablation Metrics}}
{chunked_table("Seed-level ablation metrics", "tab:seed-ablation", ["Variant", "Seed", "Episodes", "Success", "Repeated", "Violation", "Boundary F1", "Efficiency"], "lllccccc", ablation_seed_rows, chunk_size=38, size=TINY)}

\section{{Seed-Level Fixed-Risk Metrics}}
{chunked_table("Seed-level fixed-risk metrics", "tab:seed-fixed", ["Method", "Budget", "Seed", "Episodes", "Success", "Repeated", "Violation", "Efficiency"], "llllcccc", fixed_seed_rows, chunk_size=38, size=TINY)}

\bibliographystyle{{iclr2026_conference}}
\bibliography{{references}}

\end{{document}}
"""


def main() -> None:
    PAPER.mkdir(exist_ok=True)
    write_references()
    (PAPER / "main.tex").write_text(manuscript(), encoding="utf-8")
    print(f"wrote {PAPER / 'main.tex'}")


if __name__ == "__main__":
    main()
