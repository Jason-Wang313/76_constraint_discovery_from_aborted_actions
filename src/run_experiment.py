from __future__ import annotations

import csv
import heapq
import math
import os
import time
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BASE_SEED = 760_176_031
QUICK_MODE = os.getenv("PAPER76_QUICK", "0") == "1"
SEED_COUNT = int(os.getenv("PAPER76_SEED_COUNT", "1" if QUICK_MODE else "8"))
ONLY_SEEDS = os.getenv("PAPER76_ONLY_SEEDS", "").strip()
SEEDS = [int(item) for item in ONLY_SEEDS.split(",") if item.strip()] if ONLY_SEEDS else list(range(SEED_COUNT))
GRID_N = int(os.getenv("PAPER76_GRID_N", "30" if QUICK_MODE else "40"))
EVAL_SCENARIOS = int(os.getenv("PAPER76_EVAL_SCENARIOS", "3" if QUICK_MODE else "14"))
ABLATION_SCENARIOS = int(os.getenv("PAPER76_ABLATION_SCENARIOS", "3" if QUICK_MODE else "10"))
STRESS_SCENARIOS = int(os.getenv("PAPER76_STRESS_SCENARIOS", "3" if QUICK_MODE else "8"))
FIXED_RISK_SCENARIOS = int(os.getenv("PAPER76_FIXED_RISK_SCENARIOS", "3" if QUICK_MODE else "8"))
MAX_ATTEMPTS = int(os.getenv("PAPER76_MAX_ATTEMPTS", "5" if QUICK_MODE else "6"))
RISK_BUDGETS = [float(item) for item in os.getenv("PAPER76_RISK_BUDGETS", "0.08,0.12,0.18,0.25").split(",") if item.strip()]

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"

METHODS = [
    "ignore_aborted_actions",
    "negative_label_baseline",
    "costmap_from_collisions",
    "risk_filter_uncertainty",
    "constraint_classifier",
    "robust_barrier_mpc",
    "conformal_abort_risk_filter",
    "kernel_trace_constraint_classifier",
    "particle_constraint_belief",
    "abort_constraint_discovery",
    "abort_constraint_discovery_v5",
    "oracle_constraints",
]

ABLATION_METHODS = [
    "abort_discovery_v5_full",
    "abort_discovery_v5_no_partial_geometry",
    "abort_discovery_v5_no_abort_reason_labels",
    "abort_discovery_v5_no_repeated_abort_memory",
    "abort_discovery_v5_no_safety_margin",
    "abort_discovery_v5_no_calibration",
    "abort_discovery_v5_no_dynamic_contact_features",
    "abort_discovery_v5_no_uncertainty_quantile",
    "abort_discovery_v5_no_barrier_inflation",
    "abort_discovery_v5_endpoint_only",
]

STRESS_METHODS = [
    "costmap_from_collisions",
    "risk_filter_uncertainty",
    "constraint_classifier",
    "robust_barrier_mpc",
    "conformal_abort_risk_filter",
    "kernel_trace_constraint_classifier",
    "particle_constraint_belief",
    "abort_constraint_discovery_v5",
    "oracle_constraints",
]

FIXED_RISK_METHODS = [
    "constraint_classifier",
    "risk_filter_uncertainty",
    "robust_barrier_mpc",
    "conformal_abort_risk_filter",
    "kernel_trace_constraint_classifier",
    "particle_constraint_belief",
    "abort_constraint_discovery_v5",
    "oracle_constraints",
]

REFERENCE_METHOD = "abort_constraint_discovery_v5"
PROPOSED_FAMILY = {"abort_constraint_discovery", "abort_constraint_discovery_v5"}
AGGREGATE_SPLITS = {"hidden_wall_abort", "force_limit_abort", "human_stop_constraint", "combined_abort_stress"}

ABORT_REASONS = [
    "collision_margin",
    "fixture_snag",
    "force_limit",
    "joint_limit",
    "unstable_slip",
    "human_stop",
    "visible_collision",
    "timeout",
    "none",
]


@dataclass(frozen=True)
class SplitSpec:
    name: str
    task_id: int
    wall_scale: float
    force_scale: float
    human_scale: float
    slip_scale: float
    observation_noise: float
    abort_noise: float
    evidence_rollouts: int


@dataclass(frozen=True)
class Constraint:
    kind: str
    reason: str
    center: Tuple[float, float] = (0.5, 0.5)
    radius: Tuple[float, float] = (0.08, 0.08)
    angle: float = 0.0
    start: Tuple[float, float] = (0.0, 0.0)
    end: Tuple[float, float] = (1.0, 1.0)
    width: float = 0.025
    severity: float = 1.0
    visible: bool = False


@dataclass(frozen=True)
class Scenario:
    seed: int
    scenario: int
    split: SplitSpec
    start: Tuple[float, float]
    goal: Tuple[float, float]
    visible_constraints: Tuple[Constraint, ...]
    hidden_constraints: Tuple[Constraint, ...]
    force_threshold: float
    noise: float
    abort_noise: float
    stress_level: float
    layout_id: str


@dataclass
class Evidence:
    evidence_id: str
    seed: int
    scenario: int
    split: str
    start: Tuple[float, float]
    goal: Tuple[float, float]
    trace: List[Tuple[float, float]]
    aborted: bool
    success: bool
    reason: str
    abort_point: Tuple[float, float]
    last_safe: Tuple[float, float]
    direction: Tuple[float, float]
    path_length: float
    force_proxy: float
    violation: int


@dataclass
class RolloutResult:
    success: int
    aborted: int
    repeated_abort: int
    violation: int
    attempts: int
    abstained: int
    path_length: float
    straight_line: float
    efficiency: float
    completion_time: float
    safety_margin: float
    final_reason: str
    chosen_path_risk: float
    discovered_area: float
    boundary_f1: float
    boundary_iou: float
    calibration_brier: float
    calibration_ece: float
    evidence_aborts: int
    evidence_successes: int
    trajectory: str


SPLITS = [
    SplitSpec("nominal_known_constraints", 0, 0.05, 0.08, 0.00, 0.00, 0.004, 0.00, 5),
    SplitSpec("hidden_wall_abort", 1, 0.82, 0.05, 0.00, 0.00, 0.006, 0.01, 8),
    SplitSpec("force_limit_abort", 2, 0.12, 0.92, 0.00, 0.10, 0.007, 0.02, 8),
    SplitSpec("human_stop_constraint", 3, 0.08, 0.12, 0.84, 0.04, 0.008, 0.02, 7),
    SplitSpec("combined_abort_stress", 4, 0.86, 0.82, 0.58, 0.58, 0.011, 0.035, 11),
]
SPLIT_BY_NAME = {split.name: split for split in SPLITS}


def ci95(values: Sequence[float]) -> float:
    vals = np.array(values, dtype=float)
    if len(vals) <= 1:
        return 0.0
    return float(1.96 * np.std(vals, ddof=1) / math.sqrt(len(vals)))


def rng_for(seed: int, scenario: int, *parts: object) -> np.random.Generator:
    offset = 0
    for part in parts:
        for idx, char in enumerate(str(part)):
            offset += (idx + 23) * ord(char)
    return np.random.default_rng(BASE_SEED + 65_537 * seed + 4_099 * scenario + offset)


def clamp(x: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, x))


def norm2(v: np.ndarray) -> float:
    return float(np.linalg.norm(v))


def unit_vec(v: Sequence[float]) -> np.ndarray:
    arr = np.array(v, dtype=float)
    n = norm2(arr)
    if n < 1e-9:
        return np.array([1.0, 0.0], dtype=float)
    return arr / n


def point_segment_distance(point: Sequence[float], start: Sequence[float], end: Sequence[float]) -> Tuple[float, np.ndarray, float]:
    p = np.array(point, dtype=float)
    a = np.array(start, dtype=float)
    b = np.array(end, dtype=float)
    ab = b - a
    denom = float(np.dot(ab, ab))
    if denom < 1e-12:
        return norm2(p - a), a, 0.0
    t = clamp(float(np.dot(p - a, ab) / denom))
    closest = a + t * ab
    return norm2(p - closest), closest, t


def rotate_points(dx: np.ndarray, dy: np.ndarray, angle: float) -> Tuple[np.ndarray, np.ndarray]:
    c = math.cos(angle)
    s = math.sin(angle)
    return c * dx + s * dy, -s * dx + c * dy


def constraint_margin(constraint: Constraint, point: Sequence[float]) -> float:
    p = np.array(point, dtype=float)
    if constraint.kind == "segment":
        distance, _, _ = point_segment_distance(p, constraint.start, constraint.end)
        return distance - constraint.width
    if constraint.kind == "circle":
        return norm2(p - np.array(constraint.center, dtype=float)) - constraint.radius[0]
    if constraint.kind == "ellipse":
        dx, dy = p[0] - constraint.center[0], p[1] - constraint.center[1]
        xr = math.cos(constraint.angle) * dx + math.sin(constraint.angle) * dy
        yr = -math.sin(constraint.angle) * dx + math.cos(constraint.angle) * dy
        scaled = math.sqrt((xr / max(1e-6, constraint.radius[0])) ** 2 + (yr / max(1e-6, constraint.radius[1])) ** 2)
        return (scaled - 1.0) * min(constraint.radius)
    if constraint.kind == "rect":
        cx, cy = constraint.center
        rx, ry = constraint.radius
        dx = abs(p[0] - cx) - rx
        dy = abs(p[1] - cy) - ry
        outside = math.sqrt(max(dx, 0.0) ** 2 + max(dy, 0.0) ** 2)
        inside = min(max(dx, dy), 0.0)
        return outside + inside
    raise ValueError(f"unknown constraint kind {constraint.kind}")


def grid_centers(n: int = GRID_N) -> Tuple[np.ndarray, np.ndarray]:
    coords = (np.arange(n, dtype=float) + 0.5) / n
    return np.meshgrid(coords, coords, indexing="ij")


def segment_distance_grid(constraint: Constraint, n: int = GRID_N) -> np.ndarray:
    x, y = grid_centers(n)
    ax, ay = constraint.start
    bx, by = constraint.end
    abx = bx - ax
    aby = by - ay
    denom = abx * abx + aby * aby
    if denom < 1e-12:
        return np.sqrt((x - ax) ** 2 + (y - ay) ** 2)
    t = np.clip(((x - ax) * abx + (y - ay) * aby) / denom, 0.0, 1.0)
    cx = ax + t * abx
    cy = ay + t * aby
    return np.sqrt((x - cx) ** 2 + (y - cy) ** 2)


def constraint_risk_grid(constraint: Constraint, n: int = GRID_N, smooth: float = 0.018) -> np.ndarray:
    x, y = grid_centers(n)
    if constraint.kind == "segment":
        dist = segment_distance_grid(constraint, n) - constraint.width
        risk = 1.0 / (1.0 + np.exp(dist / max(1e-6, smooth)))
    elif constraint.kind == "circle":
        cx, cy = constraint.center
        dist = np.sqrt((x - cx) ** 2 + (y - cy) ** 2) - constraint.radius[0]
        risk = 1.0 / (1.0 + np.exp(dist / max(1e-6, smooth)))
    elif constraint.kind == "ellipse":
        cx, cy = constraint.center
        xr, yr = rotate_points(x - cx, y - cy, constraint.angle)
        scaled = np.sqrt((xr / max(1e-6, constraint.radius[0])) ** 2 + (yr / max(1e-6, constraint.radius[1])) ** 2)
        dist = (scaled - 1.0) * min(constraint.radius)
        risk = 1.0 / (1.0 + np.exp(dist / max(1e-6, smooth)))
    elif constraint.kind == "rect":
        cx, cy = constraint.center
        rx, ry = constraint.radius
        dx = np.abs(x - cx) - rx
        dy = np.abs(y - cy) - ry
        outside = np.sqrt(np.maximum(dx, 0.0) ** 2 + np.maximum(dy, 0.0) ** 2)
        inside = np.minimum(np.maximum(dx, dy), 0.0)
        dist = outside + inside
        risk = 1.0 / (1.0 + np.exp(dist / max(1e-6, smooth)))
    else:
        raise ValueError(f"unknown constraint kind {constraint.kind}")
    return np.clip(risk * constraint.severity, 0.0, 1.0)


def hidden_risk_grid(scenario: Scenario, n: int = GRID_N) -> np.ndarray:
    risk = np.zeros((n, n), dtype=float)
    for constraint in scenario.hidden_constraints:
        risk = np.maximum(risk, constraint_risk_grid(constraint, n))
    return np.clip(risk, 0.0, 1.0)


def visible_block_grid(scenario: Scenario, n: int = GRID_N) -> np.ndarray:
    risk = np.zeros((n, n), dtype=float)
    for constraint in scenario.visible_constraints:
        risk = np.maximum(risk, constraint_risk_grid(constraint, n, smooth=0.012))
    return risk >= 0.50


def point_to_cell(point: Sequence[float], n: int = GRID_N) -> Tuple[int, int]:
    ix = int(clamp(point[0], 0.0, 0.999999) * n)
    iy = int(clamp(point[1], 0.0, 0.999999) * n)
    return ix, iy


def cell_to_point(cell: Tuple[int, int], n: int = GRID_N) -> Tuple[float, float]:
    return ((cell[0] + 0.5) / n, (cell[1] + 0.5) / n)


def path_length(points: Sequence[Tuple[float, float]]) -> float:
    if len(points) <= 1:
        return 0.0
    total = 0.0
    prev = np.array(points[0], dtype=float)
    for point in points[1:]:
        current = np.array(point, dtype=float)
        total += norm2(current - prev)
        prev = current
    return total


def straight_line_path(start: Sequence[float], goal: Sequence[float], steps: int = 80) -> List[Tuple[float, float]]:
    s = np.array(start, dtype=float)
    g = np.array(goal, dtype=float)
    return [tuple(s + (g - s) * t) for t in np.linspace(0.0, 1.0, steps)]


def a_star(
    scenario: Scenario,
    risk: np.ndarray,
    risk_weight: float,
    block_threshold: float,
    start: Tuple[float, float] | None = None,
    goal: Tuple[float, float] | None = None,
) -> List[Tuple[float, float]]:
    n = risk.shape[0]
    start = scenario.start if start is None else start
    goal = scenario.goal if goal is None else goal
    start_cell = point_to_cell(start, n)
    goal_cell = point_to_cell(goal, n)
    blocked = visible_block_grid(scenario, n) | (risk >= block_threshold)
    blocked[start_cell] = False
    blocked[goal_cell] = False
    neighbors = [
        (-1, -1, math.sqrt(2.0)),
        (-1, 0, 1.0),
        (-1, 1, math.sqrt(2.0)),
        (0, -1, 1.0),
        (0, 1, 1.0),
        (1, -1, math.sqrt(2.0)),
        (1, 0, 1.0),
        (1, 1, math.sqrt(2.0)),
    ]
    frontier: List[Tuple[float, Tuple[int, int]]] = []
    heapq.heappush(frontier, (0.0, start_cell))
    came_from: Dict[Tuple[int, int], Tuple[int, int] | None] = {start_cell: None}
    cost_so_far: Dict[Tuple[int, int], float] = {start_cell: 0.0}

    def heuristic(cell: Tuple[int, int]) -> float:
        return math.hypot(cell[0] - goal_cell[0], cell[1] - goal_cell[1])

    while frontier:
        _, current = heapq.heappop(frontier)
        if current == goal_cell:
            break
        for dx, dy, move_cost in neighbors:
            nxt = (current[0] + dx, current[1] + dy)
            if nxt[0] < 0 or nxt[1] < 0 or nxt[0] >= n or nxt[1] >= n:
                continue
            if blocked[nxt]:
                continue
            local_risk = float(risk[nxt])
            new_cost = cost_so_far[current] + move_cost * (1.0 + risk_weight * local_risk ** 1.35)
            if nxt not in cost_so_far or new_cost < cost_so_far[nxt]:
                cost_so_far[nxt] = new_cost
                priority = new_cost + heuristic(nxt)
                heapq.heappush(frontier, (priority, nxt))
                came_from[nxt] = current

    if goal_cell not in came_from:
        return []
    cells: List[Tuple[int, int]] = []
    cur: Tuple[int, int] | None = goal_cell
    while cur is not None:
        cells.append(cur)
        cur = came_from[cur]
    cells.reverse()
    return [cell_to_point(cell, n) for cell in cells]


def min_hidden_margin(scenario: Scenario, point: Sequence[float]) -> float:
    if not scenario.hidden_constraints:
        return 1.0
    return min(constraint_margin(constraint, point) for constraint in scenario.hidden_constraints)


def check_abort(
    scenario: Scenario,
    point: Sequence[float],
    direction: Sequence[float],
    rng: np.random.Generator,
) -> Tuple[bool, str, float, int]:
    p = np.array(point, dtype=float)
    d = unit_vec(direction)
    for constraint in scenario.visible_constraints:
        if constraint_margin(constraint, p) < -0.002:
            return True, "visible_collision", 1.0, 1
    for constraint in scenario.hidden_constraints:
        margin = constraint_margin(constraint, p)
        if constraint.reason in {"collision_margin", "fixture_snag"}:
            if margin < 0.0:
                force = constraint.severity * (1.0 + max(0.0, -margin / max(1e-6, constraint.width)))
                violation = int(margin < -0.006)
                return True, constraint.reason, force, violation
        elif constraint.reason == "force_limit":
            if margin < 0.0:
                axis = unit_vec([math.cos(constraint.angle), math.sin(constraint.angle)])
                directional_load = 0.75 + 0.45 * abs(float(np.dot(d, axis)))
                force = constraint.severity * directional_load * (1.0 + max(0.0, -margin / max(1e-6, min(constraint.radius))))
                if force > scenario.force_threshold:
                    return True, "force_limit", force, int(force > scenario.force_threshold * 1.18)
        elif constraint.reason == "human_stop":
            if margin < 0.0:
                return True, "human_stop", constraint.severity, 0
        elif constraint.reason == "unstable_slip":
            if margin < 0.0:
                tangent = unit_vec([math.cos(constraint.angle + math.pi / 2.0), math.sin(constraint.angle + math.pi / 2.0)])
                slip_load = constraint.severity * (0.55 + abs(float(np.dot(d, tangent))))
                if slip_load > 0.92:
                    return True, "unstable_slip", slip_load, int(slip_load > 1.15)
        elif constraint.reason == "joint_limit":
            if margin < 0.0:
                return True, "joint_limit", constraint.severity, int(margin < -0.01)
    if scenario.abort_noise > 0.0 and rng.random() < scenario.abort_noise * 0.002:
        return True, "human_stop", 0.25, 0
    return False, "none", 0.0, 0


def execute_path(
    scenario: Scenario,
    path: Sequence[Tuple[float, float]],
    rng: np.random.Generator,
    max_trace_points: int = 120,
) -> Evidence:
    if not path:
        return Evidence(
            evidence_id="no_path",
            seed=scenario.seed,
            scenario=scenario.scenario,
            split=scenario.split.name,
            start=scenario.start,
            goal=scenario.goal,
            trace=[scenario.start],
            aborted=False,
            success=False,
            reason="timeout",
            abort_point=scenario.start,
            last_safe=scenario.start,
            direction=(0.0, 0.0),
            path_length=0.0,
            force_proxy=0.0,
            violation=0,
        )
    trace: List[Tuple[float, float]] = [tuple(path[0])]
    last_safe = np.array(path[0], dtype=float)
    current = np.array(path[0], dtype=float)
    total_length = 0.0
    min_step = 1.0 / GRID_N * 0.55
    violation = 0
    force_proxy = 0.0
    reason = "none"
    direction = np.array([0.0, 0.0], dtype=float)
    for target_tuple in path[1:]:
        target = np.array(target_tuple, dtype=float)
        segment = target - current
        distance = norm2(segment)
        steps = max(1, int(math.ceil(distance / max(1e-6, min_step))))
        for step in range(1, steps + 1):
            alpha = step / steps
            desired = current + alpha * segment
            drift = rng.normal(0.0, scenario.noise, size=2)
            direction = unit_vec(desired - last_safe)
            point = np.clip(desired + drift, 0.01, 0.99)
            total_length += norm2(point - last_safe)
            aborted, reason, force_proxy, step_violation = check_abort(scenario, point, direction, rng)
            violation = max(violation, step_violation)
            trace.append((float(point[0]), float(point[1])))
            if len(trace) > max_trace_points:
                trace = trace[-max_trace_points:]
            if aborted:
                return Evidence(
                    evidence_id="abort",
                    seed=scenario.seed,
                    scenario=scenario.scenario,
                    split=scenario.split.name,
                    start=scenario.start,
                    goal=scenario.goal,
                    trace=trace,
                    aborted=True,
                    success=False,
                    reason=reason,
                    abort_point=tuple(point),
                    last_safe=tuple(last_safe),
                    direction=tuple(direction),
                    path_length=total_length,
                    force_proxy=force_proxy,
                    violation=violation,
                )
            last_safe = point
        current = target
    success = norm2(np.array(trace[-1]) - np.array(scenario.goal)) < 0.055
    return Evidence(
        evidence_id="success" if success else "timeout",
        seed=scenario.seed,
        scenario=scenario.scenario,
        split=scenario.split.name,
        start=scenario.start,
        goal=scenario.goal,
        trace=trace,
        aborted=False,
        success=success,
        reason="none" if success else "timeout",
        abort_point=trace[-1],
        last_safe=trace[-1],
        direction=tuple(direction),
        path_length=total_length,
        force_proxy=force_proxy,
        violation=violation,
    )


def add_gaussian(risk: np.ndarray, point: Sequence[float], radius: float, strength: float) -> None:
    x, y = grid_centers(risk.shape[0])
    px, py = point
    dist2 = (x - px) ** 2 + (y - py) ** 2
    bump = strength * np.exp(-dist2 / max(1e-8, 2.0 * radius * radius))
    np.maximum(risk, bump, out=risk)


def add_ellipse_risk(
    risk: np.ndarray,
    center: Sequence[float],
    normal: Sequence[float],
    radius_normal: float,
    radius_tangent: float,
    strength: float,
) -> None:
    x, y = grid_centers(risk.shape[0])
    c = np.array(center, dtype=float)
    nvec = unit_vec(normal)
    tvec = np.array([-nvec[1], nvec[0]])
    dx = x - c[0]
    dy = y - c[1]
    normal_coord = dx * nvec[0] + dy * nvec[1]
    tangent_coord = dx * tvec[0] + dy * tvec[1]
    scaled = (normal_coord / max(1e-6, radius_normal)) ** 2 + (tangent_coord / max(1e-6, radius_tangent)) ** 2
    bump = strength * np.exp(-0.5 * scaled)
    np.maximum(risk, bump, out=risk)


def add_surface_risk(
    risk: np.ndarray,
    point: Sequence[float],
    normal: Sequence[float],
    half_length: float,
    width: float,
    strength: float,
    beyond: bool = True,
) -> None:
    x, y = grid_centers(risk.shape[0])
    p = np.array(point, dtype=float)
    nvec = unit_vec(normal)
    tvec = np.array([-nvec[1], nvec[0]])
    dx = x - p[0]
    dy = y - p[1]
    signed = dx * nvec[0] + dy * nvec[1]
    tangent = dx * tvec[0] + dy * tvec[1]
    segment_gate = np.exp(-(np.maximum(np.abs(tangent) - half_length, 0.0) ** 2) / max(1e-8, 2.0 * (0.035 + width) ** 2))
    surface = np.exp(-(signed ** 2) / max(1e-8, 2.0 * width * width)) * segment_gate
    bump = strength * surface
    if beyond:
        inside = 1.0 / (1.0 + np.exp(-signed / max(1e-6, width * 1.7)))
        finite_depth = np.exp(-(np.maximum(signed, 0.0) ** 2) / max(1e-8, 2.0 * (5.0 * width) ** 2))
        bump = np.maximum(bump, 0.58 * strength * inside * finite_depth * segment_gate)
    np.maximum(risk, np.clip(bump, 0.0, 1.0), out=risk)


def trace_to_cells(trace: Sequence[Tuple[float, float]], n: int = GRID_N) -> List[Tuple[int, int]]:
    return list({point_to_cell(point, n) for point in trace})


def evidence_feature(point: Tuple[float, float]) -> List[float]:
    x, y = point
    return [
        x,
        y,
        x * x,
        y * y,
        x * y,
        math.sin(math.pi * x),
        math.cos(math.pi * x),
        math.sin(math.pi * y),
        math.cos(math.pi * y),
    ]


def classifier_risk(evidence: Sequence[Evidence], scenario: Scenario, n: int = GRID_N) -> np.ndarray:
    positive_points: List[Tuple[float, float]] = []
    negative_points: List[Tuple[float, float]] = []
    for ev in evidence:
        if len(ev.trace) < 3:
            continue
        if ev.aborted:
            tail = ev.trace[max(0, len(ev.trace) - 14) :]
            for point in tail:
                positive_points.append(point)
            for point in ev.trace[: max(2, len(ev.trace) // 2) : 2]:
                negative_points.append(point)
            direction = unit_vec(ev.direction)
            tangent = np.array([-direction[1], direction[0]])
            abort = np.array(ev.abort_point)
            for scale in [-0.05, 0.05, -0.10, 0.10]:
                sample = np.clip(abort + scale * tangent, 0.01, 0.99)
                positive_points.append((float(sample[0]), float(sample[1])))
        else:
            stride = max(1, len(ev.trace) // 18)
            for point in ev.trace[::stride]:
                negative_points.append(point)
    gx, gy = grid_centers(n)
    pos_density = np.zeros((n, n), dtype=float)
    neg_density = np.zeros((n, n), dtype=float)
    for px, py in positive_points:
        dist2 = (gx - px) ** 2 + (gy - py) ** 2
        pos_density = np.maximum(pos_density, np.exp(-dist2 / (2.0 * 0.070**2)))
    for nx, ny in negative_points:
        dist2 = (gx - nx) ** 2 + (gy - ny) ** 2
        neg_density = np.maximum(neg_density, np.exp(-dist2 / (2.0 * 0.045**2)))
    proba = np.clip(0.10 + 0.92 * pos_density - 0.46 * neg_density, 0.0, 1.0)
    endpoint = np.zeros((n, n), dtype=float)
    for ev in evidence:
        if ev.aborted:
            add_gaussian(endpoint, ev.abort_point, 0.050, 0.45)
    return np.clip(0.74 * proba + 0.26 * endpoint, 0.0, 1.0)


def safe_trace_mask(evidence: Sequence[Evidence], n: int = GRID_N) -> np.ndarray:
    safe = np.zeros((n, n), dtype=float)
    for ev in evidence:
        stride = max(1, len(ev.trace) // 32)
        points = ev.trace[::stride]
        if ev.aborted:
            points = ev.trace[: max(1, int(0.62 * len(ev.trace))) : stride]
        for point in points:
            add_gaussian(safe, point, 0.020, 0.55)
    return safe


def dilate_risk(risk: np.ndarray, decay: float = 0.78) -> np.ndarray:
    out = risk.copy()
    shifts = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    for dx, dy in shifts:
        shifted = np.zeros_like(risk)
        src_x0 = max(0, -dx)
        src_x1 = risk.shape[0] - max(0, dx)
        dst_x0 = max(0, dx)
        dst_x1 = risk.shape[0] - max(0, -dx)
        src_y0 = max(0, -dy)
        src_y1 = risk.shape[1] - max(0, dy)
        dst_y0 = max(0, dy)
        dst_y1 = risk.shape[1] - max(0, -dy)
        shifted[dst_x0:dst_x1, dst_y0:dst_y1] = risk[src_x0:src_x1, src_y0:src_y1]
        out = np.maximum(out, decay * shifted)
    return np.clip(out, 0.0, 1.0)


def method_parameters(method: str, risk_budget: Optional[float] = None) -> Tuple[float, float]:
    if method == "ignore_aborted_actions":
        params = (0.0, 1.10)
    elif method == "negative_label_baseline":
        params = (2.0, 1.05)
    elif method == "costmap_from_collisions":
        params = (3.2, 0.98)
    elif method == "risk_filter_uncertainty":
        params = (4.6, 0.92)
    elif method == "constraint_classifier":
        params = (3.7, 0.96)
    elif method == "kernel_trace_constraint_classifier":
        params = (4.9, 0.93)
    elif method == "robust_barrier_mpc":
        params = (7.4, 0.88)
    elif method == "conformal_abort_risk_filter":
        params = (7.0, 0.84)
    elif method == "particle_constraint_belief":
        params = (7.9, 0.86)
    elif method in {"abort_constraint_discovery", "abort_discovery_full"}:
        params = (8.6, 0.91)
    elif method in {"abort_constraint_discovery_v5", "abort_discovery_v5_full"}:
        params = (9.2, 0.84)
    elif method == "abort_discovery_v5_no_safety_margin":
        params = (4.6, 0.96)
    elif method == "abort_discovery_v5_no_calibration":
        params = (7.0, 0.86)
    elif method == "abort_discovery_v5_endpoint_only":
        params = (3.6, 1.00)
    elif method.startswith("abort_discovery_v5_"):
        params = (6.3, 0.88)
    elif method == "oracle_constraints":
        params = (8.0, 0.50)
    else:
        raise ValueError(method)

    if risk_budget is None or method == "oracle_constraints":
        return params
    risk_weight, block_threshold = params
    strictness = max(0.0, 0.25 - risk_budget)
    budget_threshold = 0.72 + 0.84 * risk_budget
    return risk_weight * (1.0 + 3.0 * strictness), min(block_threshold, budget_threshold)


def legacy_abort_discovery_method(method: str) -> bool:
    return method == "abort_constraint_discovery" or method.startswith("abort_discovery_") and not method.startswith("abort_discovery_v5_")


def v5_abort_discovery_method(method: str) -> bool:
    return method == "abort_constraint_discovery_v5" or method.startswith("abort_discovery_v5_")


def build_belief(method: str, scenario: Scenario, evidence: Sequence[Evidence], n: int = GRID_N) -> np.ndarray:
    if method == "oracle_constraints":
        return hidden_risk_grid(scenario, n)

    risk = np.zeros((n, n), dtype=float)
    aborted = [ev for ev in evidence if ev.aborted]

    if method == "ignore_aborted_actions":
        return risk

    if method == "negative_label_baseline":
        for ev in aborted:
            add_gaussian(risk, ev.abort_point, 0.040, 0.65)
        return np.clip(risk, 0.0, 1.0)

    if method == "costmap_from_collisions":
        for ev in aborted:
            radius = 0.070 if ev.reason in {"collision_margin", "fixture_snag", "visible_collision"} else 0.085
            add_gaussian(risk, ev.abort_point, radius, 0.82)
        return np.clip(risk, 0.0, 1.0)

    if method == "risk_filter_uncertainty":
        for ev in aborted:
            add_gaussian(risk, ev.abort_point, 0.085, 0.78)
        gx, gy = grid_centers(n)
        coverage = safe_trace_mask(evidence, n)
        central_uncertainty = 0.15 * np.exp(-((gx - 0.52) ** 2) / 0.16) * (1.0 - 0.45 * coverage)
        obstacle_halo = np.zeros((n, n), dtype=float)
        for visible in scenario.visible_constraints:
            obstacle_halo = np.maximum(obstacle_halo, constraint_risk_grid(visible, n, smooth=0.060) * 0.18)
        return np.clip(np.maximum(risk, central_uncertainty + obstacle_halo), 0.0, 1.0)

    if method == "constraint_classifier":
        return classifier_risk(evidence, scenario, n)

    if method == "kernel_trace_constraint_classifier":
        base = classifier_risk(evidence, scenario, n)
        safe = safe_trace_mask(evidence, n)
        tail_density = np.zeros((n, n), dtype=float)
        gx, gy = grid_centers(n)
        for ev in aborted:
            tail = ev.trace[max(0, len(ev.trace) - 18) :]
            for point in tail[:: max(1, len(tail) // 8)]:
                px, py = point
                dist2 = (gx - px) ** 2 + (gy - py) ** 2
                tail_density = np.maximum(tail_density, np.exp(-dist2 / (2.0 * 0.052**2)))
            direction = unit_vec(ev.direction)
            ahead = np.clip(np.array(ev.abort_point) + 0.035 * direction, 0.01, 0.99)
            add_gaussian(tail_density, (float(ahead[0]), float(ahead[1])), 0.060, 0.82)
        return np.clip(0.62 * base + 0.56 * tail_density - 0.35 * safe, 0.0, 1.0)

    if method == "robust_barrier_mpc":
        for ev in aborted:
            radius = 0.080 if ev.reason in {"collision_margin", "fixture_snag", "joint_limit"} else 0.100
            add_gaussian(risk, ev.abort_point, radius, 0.84)
            direction = unit_vec(ev.direction)
            boundary = 0.52 * np.array(ev.abort_point) + 0.48 * np.array(ev.last_safe)
            add_surface_risk(risk, boundary, direction, 0.145, 0.034, 0.72, beyond=False)
        for visible in scenario.visible_constraints:
            risk = np.maximum(risk, 0.22 * constraint_risk_grid(visible, n, smooth=0.075))
        risk = dilate_risk(risk, decay=0.72)
        safe = safe_trace_mask(evidence, n)
        return np.clip(risk * (1.0 - 0.22 * safe), 0.0, 1.0)

    if method == "conformal_abort_risk_filter":
        base = np.maximum(classifier_risk(evidence, scenario, n), build_belief("costmap_from_collisions", scenario, evidence, n))
        safe = safe_trace_mask(evidence, n)
        if aborted:
            abort_scores = [float(base[point_to_cell(ev.abort_point, n)]) for ev in aborted]
            quantile = float(np.quantile(abort_scores, 0.35))
        else:
            quantile = 0.35
        conformal = np.where(base >= max(0.12, quantile), np.minimum(1.0, base * 1.18 + 0.10), base * 0.72)
        gx, gy = grid_centers(n)
        ambiguity = 0.08 * np.exp(-((gx - 0.5) ** 2 + (gy - 0.5) ** 2) / 0.24)
        return np.clip(np.maximum(conformal, ambiguity) * (1.0 - 0.30 * safe), 0.0, 1.0)

    if method == "particle_constraint_belief":
        maps = [
            build_belief("costmap_from_collisions", scenario, evidence, n),
            classifier_risk(evidence, scenario, n),
            build_belief("kernel_trace_constraint_classifier", scenario, evidence, n),
        ]
        for scale, width in [(0.75, 0.050), (0.95, 0.070), (1.10, 0.095)]:
            particle = np.zeros((n, n), dtype=float)
            for ev in aborted:
                direction = unit_vec(ev.direction)
                center = np.clip(np.array(ev.abort_point) + (scale - 0.90) * 0.050 * direction, 0.01, 0.99)
                add_gaussian(particle, (float(center[0]), float(center[1])), width, 0.70)
                add_surface_risk(particle, 0.55 * center + 0.45 * np.array(ev.last_safe), direction, 0.12 * scale, 0.026 * scale, 0.66)
            maps.append(np.clip(particle, 0.0, 1.0))
        stacked = np.stack(maps, axis=0)
        upper = np.quantile(stacked, 0.72, axis=0)
        safe = safe_trace_mask(evidence, n)
        return np.clip(dilate_risk(upper, decay=0.70) * (1.0 - 0.24 * safe), 0.0, 1.0)

    if legacy_abort_discovery_method(method) or v5_abort_discovery_method(method):
        v5 = method in {"abort_constraint_discovery_v5", "abort_discovery_v5_full"} or method.startswith("abort_discovery_v5_")
        full = method in {"abort_constraint_discovery", "abort_discovery_full", "abort_constraint_discovery_v5", "abort_discovery_v5_full"}
        partial_geometry = full or method not in {"abort_discovery_no_partial_geometry", "abort_discovery_v5_no_partial_geometry", "abort_discovery_v5_endpoint_only"}
        reason_labels = full or method not in {"abort_discovery_no_abort_reason_labels", "abort_discovery_v5_no_abort_reason_labels", "abort_discovery_v5_endpoint_only"}
        repeated_memory = full or method not in {"abort_discovery_no_repeated_abort_memory", "abort_discovery_v5_no_repeated_abort_memory", "abort_discovery_v5_endpoint_only"}
        safety_margin = full or method not in {"abort_discovery_no_safety_margin", "abort_discovery_v5_no_safety_margin"}
        calibration = full or method not in {"abort_discovery_no_calibration", "abort_discovery_v5_no_calibration", "abort_discovery_v5_endpoint_only"}
        dynamic_features = full or method not in {"abort_discovery_no_dynamic_contact_features", "abort_discovery_v5_no_dynamic_contact_features", "abort_discovery_v5_endpoint_only"}
        uncertainty_quantile = (not v5) or full or method not in {"abort_discovery_v5_no_uncertainty_quantile", "abort_discovery_v5_endpoint_only"}
        barrier_inflation = (not v5) or full or method not in {"abort_discovery_v5_no_barrier_inflation", "abort_discovery_v5_endpoint_only"}

        endpoint_radius = 0.052 if v5 and safety_margin else 0.045 if safety_margin else 0.032
        for ev in aborted:
            direction = unit_vec(ev.direction)
            boundary = 0.58 * np.array(ev.abort_point) + 0.42 * np.array(ev.last_safe)
            reason = ev.reason if reason_labels else "generic_abort"
            if reason == "visible_collision":
                continue
            add_gaussian(risk, ev.abort_point, endpoint_radius * (1.30 if v5 else 1.18), 0.56 if v5 else 0.52)
            if not partial_geometry:
                add_gaussian(risk, ev.abort_point, endpoint_radius, 0.72)
                continue
            if reason in {"collision_margin", "fixture_snag", "visible_collision", "joint_limit", "generic_abort"}:
                half_length = (0.20 if v5 else 0.17) if safety_margin else 0.10
                width = (0.034 if v5 else 0.030) if safety_margin else 0.018
                add_surface_risk(risk, boundary, direction, half_length, width, 0.99, beyond=False)
                add_gaussian(risk, ev.abort_point, endpoint_radius, 0.55)
            elif reason == "force_limit":
                if dynamic_features:
                    add_ellipse_risk(risk, np.array(ev.abort_point) + 0.045 * direction, direction, 0.135 if v5 else 0.120, 0.255 if v5 else 0.230, 0.96)
                    add_surface_risk(risk, boundary, direction, 0.16 if v5 else 0.14, 0.026 if v5 else 0.024, 0.58, beyond=False)
                else:
                    add_surface_risk(risk, boundary, direction, 0.13, 0.026, 0.72, beyond=False)
            elif reason == "human_stop":
                add_gaussian(risk, ev.abort_point, (0.135 if v5 else 0.120) if safety_margin else 0.078, 0.92)
            elif reason == "unstable_slip":
                if dynamic_features:
                    add_ellipse_risk(risk, ev.abort_point, direction, 0.118 if v5 else 0.100, 0.245 if v5 else 0.220, 0.94)
                else:
                    add_gaussian(risk, ev.abort_point, 0.065, 0.70)
            else:
                add_gaussian(risk, ev.abort_point, endpoint_radius, 0.65)

        if repeated_memory and len(aborted) >= 2:
            by_reason: Dict[str, List[Evidence]] = {}
            for ev in aborted:
                if ev.reason in {"collision_margin", "fixture_snag", "joint_limit", "force_limit"}:
                    by_reason.setdefault(ev.reason if reason_labels else "generic_abort", []).append(ev)
            for _, group in by_reason.items():
                if len(group) < 2:
                    continue
                points = np.array([ev.abort_point for ev in group], dtype=float)
                directions = np.array([unit_vec(ev.direction) for ev in group], dtype=float)
                center = np.mean(points, axis=0)
                cov = np.cov((points - center).T) if len(group) > 2 else np.eye(2) * 1e-4
                eigvals, eigvecs = np.linalg.eigh(cov)
                tangent = eigvecs[:, int(np.argmax(eigvals))]
                normal = unit_vec(np.mean(directions, axis=0))
                if abs(float(np.dot(normal, tangent))) > 0.65:
                    normal = np.array([-tangent[1], tangent[0]])
                projections = (points - center) @ tangent
                half_length = float(max(0.14 if v5 else 0.12, 0.5 * (np.max(projections) - np.min(projections)) + (0.11 if v5 else 0.09)))
                add_surface_risk(risk, center, normal, half_length, (0.028 if v5 else 0.024) if safety_margin else 0.016, 0.90 if v5 else 0.88, beyond=False)

        if calibration:
            safe = safe_trace_mask(evidence, n)
            risk = np.clip(risk * (1.0 - (0.56 if v5 else 0.48) * safe), 0.0, 1.0)
            for ev in aborted:
                add_gaussian(risk, ev.abort_point, 0.026 if v5 else 0.024, 0.70 if v5 else 0.68)
        if v5 and uncertainty_quantile and aborted:
            kernel = build_belief("kernel_trace_constraint_classifier", scenario, evidence, n)
            abort_scores = [float(kernel[point_to_cell(ev.abort_point, n)]) for ev in aborted]
            q = float(np.quantile(abort_scores, 0.40))
            ambiguous = np.where(kernel >= max(0.16, q), kernel * 0.34, kernel * 0.12)
            risk = np.maximum(risk, ambiguous)
        if v5 and barrier_inflation:
            risk = np.maximum(risk, 0.84 * dilate_risk(risk, decay=0.62))
        return np.clip(risk, 0.0, 1.0)

    raise ValueError(f"unknown method {method}")


def scenario_constraints(split: SplitSpec, rng: np.random.Generator, stress_level: float) -> Tuple[Tuple[Constraint, ...], Tuple[Constraint, ...], float]:
    visible: List[Constraint] = [
        Constraint("circle", "visible_collision", center=(0.28, 0.25 + 0.06 * rng.normal()), radius=(0.055, 0.055), severity=1.0, visible=True),
        Constraint("circle", "visible_collision", center=(0.71, 0.75 + 0.05 * rng.normal()), radius=(0.060, 0.060), severity=1.0, visible=True),
    ]
    if split.name in {"combined_abort_stress", "hidden_wall_abort"}:
        visible.append(
            Constraint("rect", "visible_collision", center=(0.50, 0.08), radius=(0.10, 0.035), severity=1.0, visible=True)
        )
    hidden: List[Constraint] = []
    wall_scale = clamp(split.wall_scale + 0.30 * stress_level, 0.0, 1.0)
    force_scale = clamp(split.force_scale + 0.24 * stress_level, 0.0, 1.0)
    human_scale = clamp(split.human_scale + 0.18 * stress_level, 0.0, 1.0)
    slip_scale = clamp(split.slip_scale + 0.22 * stress_level, 0.0, 1.0)
    force_threshold = 0.88 - 0.16 * force_scale

    if wall_scale > 0.20:
        x = 0.48 + 0.04 * rng.normal()
        gap_center = clamp(0.50 + 0.23 * rng.normal(), 0.33, 0.72)
        gap_width = 0.17 - 0.045 * stress_level + 0.015 * rng.normal()
        gap_width = clamp(gap_width, 0.105, 0.22)
        low = clamp(gap_center - 0.5 * gap_width, 0.16, 0.74)
        high = clamp(gap_center + 0.5 * gap_width, 0.24, 0.86)
        width = 0.017 + 0.014 * wall_scale
        hidden.append(Constraint("segment", "collision_margin", start=(x, 0.09), end=(x + 0.025 * rng.normal(), low), width=width, severity=0.95))
        hidden.append(Constraint("segment", "fixture_snag", start=(x + 0.020 * rng.normal(), high), end=(x, 0.93), width=width, severity=0.96))

    if force_scale > 0.18:
        center = (clamp(0.58 + 0.10 * rng.normal(), 0.42, 0.75), clamp(0.48 + 0.18 * rng.normal(), 0.24, 0.78))
        hidden.append(
            Constraint(
                "ellipse",
                "force_limit",
                center=center,
                radius=(0.105 + 0.045 * force_scale, 0.055 + 0.025 * force_scale),
                angle=float(rng.uniform(-0.8, 0.8)),
                severity=0.92 + 0.52 * force_scale,
            )
        )

    if human_scale > 0.18:
        count = 1 + int(human_scale > 0.72)
        for idx in range(count):
            hidden.append(
                Constraint(
                    "circle",
                    "human_stop",
                    center=(clamp(0.40 + 0.22 * rng.random() + 0.06 * idx, 0.22, 0.82), clamp(0.28 + 0.50 * rng.random(), 0.16, 0.88)),
                    radius=(0.062 + 0.045 * human_scale, 0.062 + 0.045 * human_scale),
                    severity=0.80 + 0.25 * human_scale,
                )
            )

    if slip_scale > 0.20:
        hidden.append(
            Constraint(
                "ellipse",
                "unstable_slip",
                center=(clamp(0.66 + 0.13 * rng.normal(), 0.42, 0.86), clamp(0.45 + 0.19 * rng.normal(), 0.19, 0.82)),
                radius=(0.115 + 0.040 * slip_scale, 0.048 + 0.025 * slip_scale),
                angle=float(rng.uniform(-1.2, 1.2)),
                severity=0.86 + 0.38 * slip_scale,
            )
        )

    if split.name == "nominal_known_constraints":
        hidden = hidden[:1]
        force_threshold = 1.15

    return tuple(visible), tuple(hidden), force_threshold


def build_scenario(split: SplitSpec, seed: int, scenario_idx: int, purpose: str, stress_level: float = 0.0) -> Scenario:
    for attempt in range(40):
        rng = rng_for(seed, scenario_idx, purpose, split.name, f"{stress_level:.2f}", attempt)
        start_y = clamp(0.50 + 0.24 * rng.normal(), 0.18, 0.82)
        goal_y = clamp(start_y + 0.11 * rng.normal(), 0.16, 0.84)
        start = (0.065 + 0.018 * rng.random(), start_y)
        goal = (0.925 - 0.018 * rng.random(), goal_y)
        visible, hidden, force_threshold = scenario_constraints(split, rng, stress_level)
        scenario = Scenario(
            seed=seed,
            scenario=scenario_idx,
            split=split,
            start=start,
            goal=goal,
            visible_constraints=visible,
            hidden_constraints=hidden,
            force_threshold=force_threshold,
            noise=split.observation_noise + 0.004 * stress_level,
            abort_noise=split.abort_noise + 0.012 * stress_level,
            stress_level=stress_level,
            layout_id=f"{split.name}_{seed}_{scenario_idx}_{attempt}",
        )
        oracle_path = a_star(scenario, hidden_risk_grid(scenario), 8.0, 0.50)
        if oracle_path:
            return scenario
    return scenario


def probe_pairs(scenario: Scenario, count: int, rng: np.random.Generator) -> List[Tuple[Tuple[float, float], Tuple[float, float]]]:
    pairs: List[Tuple[Tuple[float, float], Tuple[float, float]]] = [(scenario.start, scenario.goal)]
    ys = np.linspace(0.16, 0.84, max(2, count))
    rng.shuffle(ys)
    for idx, y in enumerate(ys[: count - 1]):
        jitter = 0.035 * rng.normal()
        if idx % 4 == 0:
            pairs.append(((0.07, clamp(float(y + jitter), 0.10, 0.90)), (0.93, clamp(float(y - 0.5 * jitter), 0.10, 0.90))))
        elif idx % 4 == 1:
            pairs.append(((0.12, 0.14), (0.88, clamp(float(y), 0.12, 0.88))))
        elif idx % 4 == 2:
            pairs.append(((0.10, 0.86), (0.91, clamp(float(y), 0.12, 0.88))))
        else:
            pairs.append(((0.16, clamp(float(y), 0.12, 0.88)), (0.86, clamp(float(1.0 - y + jitter), 0.12, 0.88))))
    return pairs[:count]


def generate_evidence(scenario: Scenario) -> List[Evidence]:
    rng = rng_for(scenario.seed, scenario.scenario, scenario.split.name, "evidence", scenario.layout_id)
    evidence: List[Evidence] = []
    for idx, (start, goal) in enumerate(probe_pairs(scenario, scenario.split.evidence_rollouts, rng)):
        probe_scenario = replace(scenario, start=start, goal=goal)
        path = a_star(probe_scenario, np.zeros((GRID_N, GRID_N), dtype=float), 0.0, 1.10)
        if not path:
            path = straight_line_path(start, goal)
        ev = execute_path(probe_scenario, path, rng_for(scenario.seed, scenario.scenario, "probe", idx, scenario.layout_id))
        ev.evidence_id = f"probe_{idx:02d}"
        evidence.append(ev)
    return evidence


def calibration_metrics(risk: np.ndarray, truth: np.ndarray) -> Tuple[float, float]:
    labels = (truth >= 0.50).astype(float).ravel()
    preds = np.clip(risk.ravel(), 0.0, 1.0)
    brier = float(np.mean((preds - labels) ** 2))
    ece = 0.0
    for lo in np.linspace(0.0, 0.9, 10):
        hi = lo + 0.1
        mask = (preds >= lo) & (preds < hi if hi < 1.0 else preds <= hi)
        if np.any(mask):
            ece += float(np.mean(mask)) * abs(float(np.mean(preds[mask])) - float(np.mean(labels[mask])))
    return brier, ece


def boundary_metrics(risk: np.ndarray, truth: np.ndarray) -> Tuple[float, float]:
    pred = risk >= 0.50
    true = truth >= 0.50
    tp = float(np.sum(pred & true))
    fp = float(np.sum(pred & ~true))
    fn = float(np.sum(~pred & true))
    if tp == 0.0 and fp == 0.0 and fn == 0.0:
        return 1.0, 1.0
    if tp == 0.0:
        return 0.0, 0.0
    precision = tp / max(1e-9, tp + fp)
    recall = tp / max(1e-9, tp + fn)
    f1 = 2.0 * precision * recall / max(1e-9, precision + recall)
    iou = tp / max(1e-9, tp + fp + fn)
    return float(f1), float(iou)


def risk_along_path(risk: np.ndarray, path: Sequence[Tuple[float, float]]) -> float:
    if not path:
        return 1.0
    vals = [float(risk[point_to_cell(point, risk.shape[0])]) for point in path]
    return float(np.mean(vals))


def run_closed_loop(method: str, scenario: Scenario, base_evidence: Sequence[Evidence], risk_budget: Optional[float] = None) -> RolloutResult:
    evidence = list(base_evidence)
    evidence_aborts = sum(1 for ev in evidence if ev.aborted)
    evidence_successes = sum(1 for ev in evidence if ev.success)
    total_path = 0.0
    aborts = 0
    violation = 0
    final_reason = "none"
    trajectory_parts: List[str] = []
    final_risk = build_belief(method, scenario, evidence)
    final_path_risk = 0.0
    min_margin = 1.0
    abstained = 0
    straight = norm2(np.array(scenario.goal) - np.array(scenario.start))

    for attempt in range(MAX_ATTEMPTS):
        final_risk = build_belief(method, scenario, evidence)
        risk_weight, block_threshold = method_parameters(method, risk_budget)
        path = a_star(scenario, final_risk, risk_weight, block_threshold)
        final_path_risk = risk_along_path(final_risk, path)
        if not path:
            abstained = 1
            final_reason = "no_path"
            trajectory_parts.append(f"a{attempt}:no_path")
            break
        rng = rng_for(scenario.seed, scenario.scenario, method, attempt, scenario.layout_id)
        ev = execute_path(scenario, path, rng)
        total_path += ev.path_length
        violation = max(violation, ev.violation)
        for point in ev.trace:
            min_margin = min(min_margin, min_hidden_margin(scenario, point))
        trajectory_parts.append(f"a{attempt}:{ev.reason}:{len(ev.trace)}")
        if ev.success:
            truth = hidden_risk_grid(scenario)
            f1, iou = boundary_metrics(final_risk, truth)
            brier, ece = calibration_metrics(final_risk, truth)
            efficiency = straight / max(1e-6, total_path)
            return RolloutResult(
                success=1,
                aborted=int(aborts > 0),
                repeated_abort=int(aborts >= 2),
                violation=violation,
                attempts=attempt + 1,
                abstained=abstained,
                path_length=total_path,
                straight_line=straight,
                efficiency=efficiency,
                completion_time=total_path + 0.22 * aborts + 0.06 * attempt,
                safety_margin=min_margin,
                final_reason="none",
                chosen_path_risk=final_path_risk,
                discovered_area=float(np.mean(final_risk >= 0.50)),
                boundary_f1=f1,
                boundary_iou=iou,
                calibration_brier=brier,
                calibration_ece=ece,
                evidence_aborts=evidence_aborts,
                evidence_successes=evidence_successes,
                trajectory=";".join(trajectory_parts),
            )
        final_reason = ev.reason
        if ev.aborted:
            aborts += 1
            if method != "ignore_aborted_actions":
                ev.evidence_id = f"closed_loop_abort_{attempt}"
                evidence.append(ev)
        else:
            break

    truth = hidden_risk_grid(scenario)
    f1, iou = boundary_metrics(final_risk, truth)
    brier, ece = calibration_metrics(final_risk, truth)
    return RolloutResult(
        success=0,
        aborted=int(aborts > 0),
        repeated_abort=int(aborts >= 2),
        violation=violation,
        attempts=min(MAX_ATTEMPTS, max(1, len(trajectory_parts))),
        abstained=abstained,
        path_length=total_path,
        straight_line=straight,
        efficiency=0.0 if total_path <= 1e-9 else straight / max(1e-6, total_path) * 0.35,
        completion_time=total_path + 0.22 * aborts + 0.12 * abstained,
        safety_margin=min_margin,
        final_reason=final_reason,
        chosen_path_risk=final_path_risk,
        discovered_area=float(np.mean(final_risk >= 0.50)),
        boundary_f1=f1,
        boundary_iou=iou,
        calibration_brier=brier,
        calibration_ece=ece,
        evidence_aborts=evidence_aborts,
        evidence_successes=evidence_successes,
        trajectory=";".join(trajectory_parts),
    )


def evidence_rows(scenario: Scenario, evidence: Sequence[Evidence]) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for ev in evidence:
        rows.append(
            {
                "seed": str(ev.seed),
                "scenario": str(ev.scenario),
                "layout_id": scenario.layout_id,
                "split": ev.split,
                "evidence_id": ev.evidence_id,
                "aborted": str(int(ev.aborted)),
                "success": str(int(ev.success)),
                "reason": ev.reason,
                "trace_points": str(len(ev.trace)),
                "path_length": f"{ev.path_length:.5f}",
                "force_proxy": f"{ev.force_proxy:.5f}",
                "violation": str(ev.violation),
                "start_x": f"{ev.start[0]:.5f}",
                "start_y": f"{ev.start[1]:.5f}",
                "goal_x": f"{ev.goal[0]:.5f}",
                "goal_y": f"{ev.goal[1]:.5f}",
                "abort_x": f"{ev.abort_point[0]:.5f}",
                "abort_y": f"{ev.abort_point[1]:.5f}",
                "direction_x": f"{ev.direction[0]:.5f}",
                "direction_y": f"{ev.direction[1]:.5f}",
            }
        )
    return rows


def evaluate_scenario(method: str, scenario: Scenario, evidence: Sequence[Evidence], risk_budget: Optional[float] = None) -> Dict[str, str]:
    result = run_closed_loop(method, scenario, evidence, risk_budget=risk_budget)
    return {
        "seed": str(scenario.seed),
        "scenario": str(scenario.scenario),
        "layout_id": scenario.layout_id,
        "split": scenario.split.name,
        "method": method,
        "stress_level": f"{scenario.stress_level:.2f}",
        "risk_budget": "" if risk_budget is None else f"{risk_budget:.2f}",
        "success": str(result.success),
        "aborted": str(result.aborted),
        "repeated_abort": str(result.repeated_abort),
        "violation": str(result.violation),
        "attempts": str(result.attempts),
        "abstained": str(result.abstained),
        "path_length": f"{result.path_length:.5f}",
        "straight_line": f"{result.straight_line:.5f}",
        "path_efficiency": f"{result.efficiency:.5f}",
        "completion_time": f"{result.completion_time:.5f}",
        "safety_margin": f"{result.safety_margin:.5f}",
        "boundary_f1": f"{result.boundary_f1:.5f}",
        "boundary_iou": f"{result.boundary_iou:.5f}",
        "calibration_brier": f"{result.calibration_brier:.5f}",
        "calibration_ece": f"{result.calibration_ece:.5f}",
        "chosen_path_risk": f"{result.chosen_path_risk:.5f}",
        "discovered_area": f"{result.discovered_area:.5f}",
        "evidence_aborts": str(result.evidence_aborts),
        "evidence_successes": str(result.evidence_successes),
        "final_abort_reason": result.final_reason,
        "trajectory": result.trajectory,
    }


def group_rows(rows: Sequence[Dict[str, str]], keys: Sequence[str]) -> Dict[Tuple[str, ...], List[Dict[str, str]]]:
    grouped: Dict[Tuple[str, ...], List[Dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(tuple(row[key] for key in keys), []).append(row)
    return grouped


def build_seed_metrics(rows: Sequence[Dict[str, str]]) -> List[Dict[str, str]]:
    grouped = group_rows(rows, ["method", "split", "seed"])
    metrics: List[Dict[str, str]] = []
    metric_names = [
        "success",
        "aborted",
        "repeated_abort",
        "violation",
        "abstained",
        "path_efficiency",
        "completion_time",
        "safety_margin",
        "boundary_f1",
        "boundary_iou",
        "calibration_brier",
        "calibration_ece",
        "chosen_path_risk",
        "discovered_area",
    ]
    for (method, split, seed), group in sorted(grouped.items()):
        item = {"method": method, "split": split, "seed": seed, "episodes": str(len(group))}
        for metric in metric_names:
            vals = [float(row[metric]) for row in group]
            item[metric] = f"{float(np.mean(vals)):.5f}"
        item["tail_risk"] = f"{1.0 - float(item['success']):.5f}"
        metrics.append(item)
    return metrics


def build_summary(seed_rows: Sequence[Dict[str, str]]) -> List[Dict[str, str]]:
    grouped = group_rows(seed_rows, ["method", "split"])
    summary: List[Dict[str, str]] = []
    metric_names = [
        "success",
        "tail_risk",
        "aborted",
        "repeated_abort",
        "violation",
        "abstained",
        "path_efficiency",
        "completion_time",
        "safety_margin",
        "boundary_f1",
        "boundary_iou",
        "calibration_brier",
        "calibration_ece",
        "chosen_path_risk",
        "discovered_area",
    ]
    for (method, split), group in sorted(grouped.items()):
        item = {"method": method, "split": split, "seeds": str(len(group))}
        for metric in metric_names:
            vals = [float(row[metric]) for row in group]
            item[f"mean_{metric}"] = f"{float(np.mean(vals)):.5f}"
            item[f"ci95_{metric}"] = f"{ci95(vals):.5f}"
        summary.append(item)
    return summary


def build_pairwise(seed_rows: Sequence[Dict[str, str]], reference: str = REFERENCE_METHOD) -> List[Dict[str, str]]:
    by_key = {(row["method"], row["split"], row["seed"]): row for row in seed_rows}
    methods = sorted({row["method"] for row in seed_rows})
    splits = sorted({row["split"] for row in seed_rows})
    seeds = sorted({row["seed"] for row in seed_rows})
    out: List[Dict[str, str]] = []
    for split in splits:
        for method in methods:
            if method == reference:
                continue
            success_diffs: List[float] = []
            violation_reductions: List[float] = []
            repeat_reductions: List[float] = []
            f1_diffs: List[float] = []
            efficiency_diffs: List[float] = []
            area_diffs: List[float] = []
            for seed in seeds:
                ref = by_key.get((reference, split, seed))
                other = by_key.get((method, split, seed))
                if ref is None or other is None:
                    continue
                success_diffs.append(float(ref["success"]) - float(other["success"]))
                violation_reductions.append(float(other["violation"]) - float(ref["violation"]))
                repeat_reductions.append(float(other["repeated_abort"]) - float(ref["repeated_abort"]))
                f1_diffs.append(float(ref["boundary_f1"]) - float(other["boundary_f1"]))
                efficiency_diffs.append(float(ref["path_efficiency"]) - float(other["path_efficiency"]))
                area_diffs.append(float(ref["discovered_area"]) - float(other["discovered_area"]))
            if success_diffs:
                out.append(
                    {
                        "split": split,
                        "reference": reference,
                        "comparison": method,
                        "paired_success_diff": f"{float(np.mean(success_diffs)):.5f}",
                        "ci95_success_diff": f"{ci95(success_diffs):.5f}",
                        "paired_violation_reduction": f"{float(np.mean(violation_reductions)):.5f}",
                        "paired_repeated_abort_reduction": f"{float(np.mean(repeat_reductions)):.5f}",
                        "paired_boundary_f1_diff": f"{float(np.mean(f1_diffs)):.5f}",
                        "paired_efficiency_diff": f"{float(np.mean(efficiency_diffs)):.5f}",
                        "paired_discovered_area_diff": f"{float(np.mean(area_diffs)):.5f}",
                        "reference_better_seeds": str(sum(1 for diff in success_diffs if diff > 0.0)),
                        "seeds": str(len(success_diffs)),
                    }
                )
    return out


def build_aggregate_seed_metrics(seed_rows: Sequence[Dict[str, str]]) -> List[Dict[str, str]]:
    metric_names = [
        "success",
        "tail_risk",
        "aborted",
        "repeated_abort",
        "violation",
        "abstained",
        "path_efficiency",
        "completion_time",
        "safety_margin",
        "boundary_f1",
        "boundary_iou",
        "calibration_brier",
        "calibration_ece",
        "chosen_path_risk",
        "discovered_area",
    ]
    eligible = [row for row in seed_rows if row["split"] in AGGREGATE_SPLITS]
    grouped = group_rows(eligible, ["method", "seed"])
    out: List[Dict[str, str]] = []
    for (method, seed), group in sorted(grouped.items()):
        item = {
            "method": method,
            "split": "aggregate_hard_regime",
            "seed": seed,
            "episodes": str(sum(int(row.get("episodes", "0") or "0") for row in group)),
        }
        for metric in metric_names:
            vals = [float(row[metric]) for row in group]
            item[metric] = f"{float(np.mean(vals)):.5f}"
        out.append(item)
    return out


def build_fixed_risk_seed_metrics(rows: Sequence[Dict[str, str]]) -> List[Dict[str, str]]:
    grouped = group_rows(rows, ["risk_budget", "method", "split", "seed"])
    metrics: List[Dict[str, str]] = []
    metric_names = [
        "success",
        "aborted",
        "repeated_abort",
        "violation",
        "abstained",
        "path_efficiency",
        "completion_time",
        "safety_margin",
        "boundary_f1",
        "boundary_iou",
        "calibration_brier",
        "calibration_ece",
        "chosen_path_risk",
        "discovered_area",
    ]
    for (risk_budget, method, split, seed), group in sorted(grouped.items()):
        item = {"risk_budget": risk_budget, "method": method, "split": split, "seed": seed, "episodes": str(len(group))}
        for metric in metric_names:
            vals = [float(row[metric]) for row in group]
            item[metric] = f"{float(np.mean(vals)):.5f}"
        item["tail_risk"] = f"{1.0 - float(item['success']):.5f}"
        metrics.append(item)
    return metrics


def build_fixed_risk_summary(seed_rows: Sequence[Dict[str, str]]) -> List[Dict[str, str]]:
    grouped = group_rows(seed_rows, ["risk_budget", "method", "split"])
    summary: List[Dict[str, str]] = []
    metric_names = [
        "success",
        "tail_risk",
        "aborted",
        "repeated_abort",
        "violation",
        "abstained",
        "path_efficiency",
        "completion_time",
        "safety_margin",
        "boundary_f1",
        "boundary_iou",
        "calibration_brier",
        "calibration_ece",
        "chosen_path_risk",
        "discovered_area",
    ]
    for (risk_budget, method, split), group in sorted(grouped.items()):
        item = {"risk_budget": risk_budget, "method": method, "split": split, "seeds": str(len(group))}
        for metric in metric_names:
            vals = [float(row[metric]) for row in group]
            item[f"mean_{metric}"] = f"{float(np.mean(vals)):.5f}"
            item[f"ci95_{metric}"] = f"{ci95(vals):.5f}"
        summary.append(item)
    return summary


def build_fixed_risk_pairwise(seed_rows: Sequence[Dict[str, str]], reference: str = REFERENCE_METHOD) -> List[Dict[str, str]]:
    by_key = {(row["risk_budget"], row["method"], row["split"], row["seed"]): row for row in seed_rows}
    budgets = sorted({row["risk_budget"] for row in seed_rows}, key=float)
    methods = sorted({row["method"] for row in seed_rows})
    splits = sorted({row["split"] for row in seed_rows})
    seeds = sorted({row["seed"] for row in seed_rows})
    out: List[Dict[str, str]] = []
    for budget in budgets:
        for split in splits:
            for method in methods:
                if method == reference:
                    continue
                success_diffs: List[float] = []
                violation_reductions: List[float] = []
                repeat_reductions: List[float] = []
                f1_diffs: List[float] = []
                efficiency_diffs: List[float] = []
                area_diffs: List[float] = []
                for seed in seeds:
                    ref = by_key.get((budget, reference, split, seed))
                    other = by_key.get((budget, method, split, seed))
                    if ref is None or other is None:
                        continue
                    success_diffs.append(float(ref["success"]) - float(other["success"]))
                    violation_reductions.append(float(other["violation"]) - float(ref["violation"]))
                    repeat_reductions.append(float(other["repeated_abort"]) - float(ref["repeated_abort"]))
                    f1_diffs.append(float(ref["boundary_f1"]) - float(other["boundary_f1"]))
                    efficiency_diffs.append(float(ref["path_efficiency"]) - float(other["path_efficiency"]))
                    area_diffs.append(float(ref["discovered_area"]) - float(other["discovered_area"]))
                if success_diffs:
                    out.append(
                        {
                            "risk_budget": budget,
                            "split": split,
                            "reference": reference,
                            "comparison": method,
                            "paired_success_diff": f"{float(np.mean(success_diffs)):.5f}",
                            "ci95_success_diff": f"{ci95(success_diffs):.5f}",
                            "paired_violation_reduction": f"{float(np.mean(violation_reductions)):.5f}",
                            "paired_repeated_abort_reduction": f"{float(np.mean(repeat_reductions)):.5f}",
                            "paired_boundary_f1_diff": f"{float(np.mean(f1_diffs)):.5f}",
                            "paired_efficiency_diff": f"{float(np.mean(efficiency_diffs)):.5f}",
                            "paired_discovered_area_diff": f"{float(np.mean(area_diffs)):.5f}",
                            "reference_better_seeds": str(sum(1 for diff in success_diffs if diff > 0.0)),
                            "seeds": str(len(success_diffs)),
                        }
                    )
    return out


def build_stress_summary(rows: Sequence[Dict[str, str]]) -> List[Dict[str, str]]:
    grouped = group_rows(rows, ["method", "stress_level"])
    summary: List[Dict[str, str]] = []
    for (method, stress_level), group in sorted(grouped.items()):
        seed_rows = build_seed_metrics(group)
        item = {"method": method, "stress_level": stress_level, "seeds": str(len(seed_rows))}
        for metric in ["success", "aborted", "repeated_abort", "violation", "boundary_f1", "path_efficiency"]:
            vals = [float(row[metric]) for row in seed_rows]
            item[f"mean_{metric}"] = f"{float(np.mean(vals)):.5f}"
            item[f"ci95_{metric}"] = f"{ci95(vals):.5f}"
        summary.append(item)
    return summary


def write_csv(path: Path, rows: Sequence[Dict[str, str]]) -> None:
    path.parent.mkdir(exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields: List[str] = []
    for row in rows:
        for key in row.keys():
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def negative_cases(rows: Sequence[Dict[str, str]]) -> List[Dict[str, str]]:
    selected = [
        row
        for row in rows
        if row["split"] == "combined_abort_stress" and row["method"] == "abort_constraint_discovery" and row["success"] == "0"
    ]
    out: List[Dict[str, str]] = []
    for row in selected[:12]:
        out.append(
            {
                "seed": row["seed"],
                "scenario": row["scenario"],
                "layout_id": row["layout_id"],
                "final_abort_reason": row["final_abort_reason"],
                "evidence_aborts": row["evidence_aborts"],
                "attempts": row["attempts"],
                "boundary_f1": row["boundary_f1"],
                "path_efficiency": row["path_efficiency"],
                "lesson": "v5 abort-surface inference reduced repeated failures but did not find a safe route for this layout",
            }
        )
    return out or [
        {
            "seed": "",
            "scenario": "",
            "layout_id": "",
            "final_abort_reason": "",
            "evidence_aborts": "",
            "attempts": "",
            "boundary_f1": "",
            "path_efficiency": "",
            "lesson": "no combined-stress failures for abort_constraint_discovery_v5 in this run",
        }
    ]


def decide(
    summary: Sequence[Dict[str, str]],
    pairwise: Sequence[Dict[str, str]],
    aggregate_summary: Sequence[Dict[str, str]],
    aggregate_pairwise: Sequence[Dict[str, str]],
    fixed_summary: Sequence[Dict[str, str]],
    fixed_pairwise: Sequence[Dict[str, str]],
    ablation_summary: Sequence[Dict[str, str]],
    stress_summary: Sequence[Dict[str, str]],
) -> Tuple[str, str]:
    combined = [row for row in summary if row["split"] == "combined_abort_stress"]
    proposed = [row for row in combined if row["method"] == REFERENCE_METHOD][0]
    non_oracle = [row for row in combined if row["method"] not in PROPOSED_FAMILY | {"oracle_constraints"}]
    best = max(non_oracle, key=lambda row: float(row["mean_success"]))
    pair = [row for row in pairwise if row["split"] == "combined_abort_stress" and row["comparison"] == best["method"]][0]
    prop_success = float(proposed["mean_success"])
    best_success = float(best["mean_success"])
    paired = float(pair["paired_success_diff"])
    paired_ci = float(pair["ci95_success_diff"])
    violation_reduction = float(pair["paired_violation_reduction"])
    repeat_reduction = float(pair["paired_repeated_abort_reduction"])
    f1_diff = float(pair["paired_boundary_f1_diff"])
    efficiency_diff = float(pair["paired_efficiency_diff"])
    area_diff = float(pair["paired_discovered_area_diff"])
    not_over_conservative = area_diff <= 0.085 and efficiency_diff >= -0.070

    agg_rows = [row for row in aggregate_summary if row["split"] == "aggregate_hard_regime"]
    agg_prop = [row for row in agg_rows if row["method"] == REFERENCE_METHOD][0]
    agg_non_oracle = [row for row in agg_rows if row["method"] not in PROPOSED_FAMILY | {"oracle_constraints"}]
    agg_best = max(agg_non_oracle, key=lambda row: float(row["mean_success"]))
    agg_pair = [row for row in aggregate_pairwise if row["split"] == "aggregate_hard_regime" and row["comparison"] == agg_best["method"]][0]
    agg_diff = float(agg_pair["paired_success_diff"])
    agg_ci = float(agg_pair["ci95_success_diff"])

    ablation_rows = [row for row in ablation_summary if row["split"] == "combined_abort_stress"]
    full_ablation = [row for row in ablation_rows if row["method"] == "abort_discovery_v5_full"][0]
    full_ablation_success = float(full_ablation["mean_success"])
    matching_ablations = [
        row["method"]
        for row in ablation_rows
        if row["method"] != "abort_discovery_v5_full" and float(row["mean_success"]) >= full_ablation_success - 0.005
    ]

    max_level = max(float(row["stress_level"]) for row in stress_summary)
    max_rows = [row for row in stress_summary if abs(float(row["stress_level"]) - max_level) < 1e-9]
    max_prop = [row for row in max_rows if row["method"] == REFERENCE_METHOD][0]
    max_non_oracle = [row for row in max_rows if row["method"] not in {REFERENCE_METHOD, "oracle_constraints"}]
    max_best = max(max_non_oracle, key=lambda row: float(row["mean_success"]))

    fixed_lines: List[str] = []
    fixed_failures: List[str] = []
    fixed_budgets = sorted({row["risk_budget"] for row in fixed_summary}, key=float)
    strict_budgets = set(f"{budget:.2f}" for budget in sorted(RISK_BUDGETS)[:2])
    for budget in fixed_budgets:
        rows = [row for row in fixed_summary if row["risk_budget"] == budget and row["split"] == "combined_abort_stress"]
        prop_budget = [row for row in rows if row["method"] == REFERENCE_METHOD][0]
        non_oracle_budget = [row for row in rows if row["method"] not in {REFERENCE_METHOD, "oracle_constraints"}]
        best_budget = max(non_oracle_budget, key=lambda row: float(row["mean_success"]))
        fixed_lines.append(f"budget {budget}: v5={float(prop_budget['mean_success']):.3f}, best={best_budget['method']}:{float(best_budget['mean_success']):.3f}")
        if budget in strict_budgets and float(prop_budget["mean_success"]) + 0.005 < float(best_budget["mean_success"]):
            fixed_failures.append(f"budget {budget} trails {best_budget['method']}")

    failures: List[str] = []
    if prop_success - best_success < 0.025:
        failures.append("main_success_margin")
    if paired - paired_ci <= -0.005:
        failures.append("main_paired_lower_bound")
    if violation_reduction < -0.030:
        failures.append("violation_reduction")
    if repeat_reduction < -0.010:
        failures.append("repeated_abort_reduction")
    if f1_diff < 0.015:
        failures.append("boundary_f1_mechanism")
    if not not_over_conservative:
        failures.append("over_conservatism")
    if agg_diff - agg_ci <= -0.005 or float(agg_prop["mean_success"]) + 0.010 < float(agg_best["mean_success"]):
        failures.append("aggregate_hard_regime")
    if matching_ablations:
        failures.append("ablation_necessity")
    if float(max_prop["mean_success"]) + 0.020 < float(max_best["mean_success"]):
        failures.append("maximum_stress")
    if fixed_failures:
        failures.append("fixed_risk")

    if not failures:
        return (
            "STRONG_REVISE",
            f"{REFERENCE_METHOD} clears the frozen local gates against strongest non-oracle baseline {best['method']} on combined_abort_stress "
            f"({prop_success:.3f} vs {best_success:.3f} success; paired diff {paired:.3f}+/-{paired_ci:.3f}), "
            f"aggregate hard-regime paired diff {agg_diff:.3f}+/-{agg_ci:.3f} against {agg_best['method']}, "
            f"fixed-risk checks ({'; '.join(fixed_lines)}), max-stress v5={float(max_prop['mean_success']):.3f} vs best_non_oracle={max_best['method']}:{float(max_best['mean_success']):.3f}, "
            f"repeated-abort reduction {repeat_reduction:.3f}, boundary-F1 gain {f1_diff:.3f}, and no matching ablation. "
            "It still lacks hardware and external benchmark validation, so it is not ICLR-main-ready.",
        )
    return (
        "KILL_ARCHIVE",
        f"{REFERENCE_METHOD} does not honestly clear the frozen local gate against strongest non-oracle baseline {best['method']} "
        f"(proposed={prop_success:.3f}, best={best_success:.3f}, paired diff={paired:.3f}+/-{paired_ci:.3f}, "
        f"violation_reduction={violation_reduction:.3f}, repeated_abort_reduction={repeat_reduction:.3f}, "
        f"boundary_f1_diff={f1_diff:.3f}, efficiency_diff={efficiency_diff:.3f}, discovered_area_diff={area_diff:.3f}). "
        f"Aggregate hard-regime diff against {agg_best['method']} is {agg_diff:.3f}+/-{agg_ci:.3f}; "
        f"fixed-risk checks: {'; '.join(fixed_lines)}; "
        f"matching ablations: {', '.join(matching_ablations) if matching_ablations else 'none'}; "
        f"max-stress v5={float(max_prop['mean_success']):.3f}, best_non_oracle={max_best['method']}:{float(max_best['mean_success']):.3f}. "
        f"Failed gates: {', '.join(failures)}.",
    )


def plot_bar(summary: Sequence[Dict[str, str]], split: str, metric: str, path: Path, title: str) -> None:
    rows = [row for row in summary if row["split"] == split]
    reverse = metric in {"success", "boundary_f1", "path_efficiency", "safety_margin"}
    rows = sorted(rows, key=lambda row: float(row[f"mean_{metric}"]), reverse=reverse)
    labels = [row["method"].replace("_", "\n") for row in rows]
    means = [float(row[f"mean_{metric}"]) for row in rows]
    cis = [float(row[f"ci95_{metric}"]) for row in rows]
    plt.figure(figsize=(10.8, 4.8))
    plt.bar(range(len(rows)), means, yerr=cis, color="#4f6f5f", edgecolor="#1f3028", capsize=3)
    plt.xticks(range(len(rows)), labels, fontsize=7)
    plt.ylabel(metric.replace("_", " "))
    plt.title(title)
    if metric in {"success", "boundary_f1", "path_efficiency"}:
        plt.ylim(-0.02, 1.05)
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def plot_stress(stress_summary: Sequence[Dict[str, str]], path: Path) -> None:
    plt.figure(figsize=(8.0, 4.8))
    for method in sorted({row["method"] for row in stress_summary}):
        rows = sorted([row for row in stress_summary if row["method"] == method], key=lambda row: float(row["stress_level"]))
        xs = [float(row["stress_level"]) for row in rows]
        ys = [float(row["mean_success"]) for row in rows]
        es = [float(row["ci95_success"]) for row in rows]
        plt.errorbar(xs, ys, yerr=es, marker="o", linewidth=2, capsize=3, label=method)
    plt.xlabel("combined abort stress level")
    plt.ylabel("closed-loop success")
    plt.title("Paper 76 aborted-action constraint stress sweep")
    plt.ylim(-0.02, 1.02)
    plt.legend(fontsize=7)
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def plot_fixed_risk(fixed_summary: Sequence[Dict[str, str]], path: Path) -> None:
    rows = [row for row in fixed_summary if row["split"] == "combined_abort_stress"]
    plt.figure(figsize=(8.4, 4.8))
    for method in sorted({row["method"] for row in rows}):
        method_rows = sorted([row for row in rows if row["method"] == method], key=lambda row: float(row["risk_budget"]))
        xs = [float(row["risk_budget"]) for row in method_rows]
        ys = [float(row["mean_success"]) for row in method_rows]
        es = [float(row["ci95_success"]) for row in method_rows]
        plt.errorbar(xs, ys, yerr=es, marker="o", linewidth=2, capsize=3, label=method)
    plt.xlabel("risk budget")
    plt.ylabel("closed-loop success")
    plt.title("Paper 76 fixed-risk success")
    plt.ylim(-0.02, 1.02)
    plt.legend(fontsize=7)
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def main() -> None:
    start_time = time.time()
    RESULTS.mkdir(exist_ok=True)
    FIGURES.mkdir(exist_ok=True)
    progress_path = RESULTS / "progress.txt"

    def progress(message: str) -> None:
        elapsed = time.time() - start_time
        line = f"[{elapsed:.1f}s] {message}"
        print(line, flush=True)
        with progress_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    progress_path.write_text("", encoding="utf-8")
    progress(
        f"start Paper76 full runner quick={QUICK_MODE} seeds={SEEDS} grid={GRID_N} "
        f"eval={EVAL_SCENARIOS} ablation={ABLATION_SCENARIOS} stress={STRESS_SCENARIOS} "
        f"fixed_risk={FIXED_RISK_SCENARIOS} attempts={MAX_ATTEMPTS} reference={REFERENCE_METHOD}"
    )
    phase = os.getenv("PAPER76_PHASE", "all").strip().lower()
    progress(f"phase={phase}")

    if phase == "main":
        resume = os.getenv("PAPER76_RESUME", "0") == "1"
        rollout_rows: List[Dict[str, str]] = read_csv(RESULTS / "rollouts.csv") if resume and (RESULTS / "rollouts.csv").exists() else []
        evidence_log: List[Dict[str, str]] = read_csv(RESULTS / "abort_evidence.csv") if resume and (RESULTS / "abort_evidence.csv").exists() else []
        training_rows: List[Dict[str, str]] = []
        completed_seed_counts: Dict[str, int] = {}
        for row in rollout_rows:
            completed_seed_counts[row["seed"]] = completed_seed_counts.get(row["seed"], 0) + 1
        expected_per_seed = len(SPLITS) * EVAL_SCENARIOS * len(METHODS)
        for seed in SEEDS:
            if completed_seed_counts.get(str(seed), 0) >= expected_per_seed:
                progress(f"main seed {seed} already complete rows={completed_seed_counts[str(seed)]}")
                continue
            progress(f"main seed {seed} begin")
            seed_evidence_count = 0
            seed_abort_count = 0
            for split in SPLITS:
                progress(f"main seed {seed} split {split.name} begin")
                for local_idx in range(EVAL_SCENARIOS):
                    scenario = build_scenario(split, seed, 1000 * split.task_id + local_idx, "eval")
                    evidence = generate_evidence(scenario)
                    seed_evidence_count += len(evidence)
                    seed_abort_count += sum(1 for ev in evidence if ev.aborted)
                    evidence_log.extend(evidence_rows(scenario, evidence))
                    for method in METHODS:
                        rollout_rows.append(evaluate_scenario(method, scenario, evidence))
                progress(f"main seed {seed} split {split.name} complete rollouts={len(rollout_rows)}")
            training_rows.append(
                {
                    "seed": str(seed),
                    "quick_mode": str(QUICK_MODE),
                    "eval_scenarios_per_split": str(EVAL_SCENARIOS),
                    "evidence_rollouts": str(seed_evidence_count),
                    "evidence_abort_count": str(seed_abort_count),
                    "grid_n": str(GRID_N),
                    "max_attempts": str(MAX_ATTEMPTS),
                }
            )
            progress(f"main seed {seed} complete evidence={seed_evidence_count} aborts={seed_abort_count}")
            progress("main phase checkpoint writing artifacts")
            seed_rows = build_seed_metrics(rollout_rows)
            summary = build_summary(seed_rows)
            pairwise = build_pairwise(seed_rows)
            aggregate_seed = build_aggregate_seed_metrics(seed_rows)
            aggregate_summary = build_summary(aggregate_seed)
            aggregate_pairwise = build_pairwise(aggregate_seed)
            write_csv(RESULTS / "abort_evidence.csv", evidence_log)
            write_csv(RESULTS / "rollouts.csv", rollout_rows)
            write_csv(RESULTS / "raw_seed_metrics.csv", seed_rows)
            write_csv(RESULTS / "metrics.csv", summary)
            write_csv(RESULTS / "pairwise_stats.csv", pairwise)
            write_csv(RESULTS / "aggregate_seed_metrics.csv", aggregate_seed)
            write_csv(RESULTS / "aggregate_metrics.csv", aggregate_summary)
            write_csv(RESULTS / "aggregate_pairwise_stats.csv", aggregate_pairwise)
            write_csv(
                RESULTS / "training_summary.csv",
                [
                    {
                        "quick_mode": str(QUICK_MODE),
                        "seeds": ";".join(str(seed) for seed in SEEDS),
                        "seed_count": str(len(SEEDS)),
                        "grid_n": str(GRID_N),
                        "eval_scenarios_per_split": str(EVAL_SCENARIOS),
                        "ablation_scenarios": str(ABLATION_SCENARIOS),
                        "stress_scenarios": str(STRESS_SCENARIOS),
                        "fixed_risk_scenarios": str(FIXED_RISK_SCENARIOS),
                        "max_attempts": str(MAX_ATTEMPTS),
                        "reference_method": REFERENCE_METHOD,
                        "splits": str(len(SPLITS)),
                        "methods": str(len(METHODS)),
                        "ablation_methods": str(len(ABLATION_METHODS)),
                        "fixed_risk_methods": str(len(FIXED_RISK_METHODS)),
                        "main_rollout_rows": str(len(rollout_rows)),
                        "abort_evidence_rows": str(len(evidence_log)),
                        "ablation_rows": "pending",
                        "stress_rows": "pending",
                        "fixed_risk_rows": "pending",
                    }
                ]
                + training_rows,
            )
        if rollout_rows:
            progress("main phase final writing artifacts")
            seed_rows = build_seed_metrics(rollout_rows)
            summary = build_summary(seed_rows)
            pairwise = build_pairwise(seed_rows)
            aggregate_seed = build_aggregate_seed_metrics(seed_rows)
            aggregate_summary = build_summary(aggregate_seed)
            aggregate_pairwise = build_pairwise(aggregate_seed)
            write_csv(RESULTS / "abort_evidence.csv", evidence_log)
            write_csv(RESULTS / "rollouts.csv", rollout_rows)
            write_csv(RESULTS / "raw_seed_metrics.csv", seed_rows)
            write_csv(RESULTS / "metrics.csv", summary)
            write_csv(RESULTS / "pairwise_stats.csv", pairwise)
            write_csv(RESULTS / "aggregate_seed_metrics.csv", aggregate_seed)
            write_csv(RESULTS / "aggregate_metrics.csv", aggregate_summary)
            write_csv(RESULTS / "aggregate_pairwise_stats.csv", aggregate_pairwise)
        progress("main phase complete")
        return

    if phase == "ablation":
        resume = os.getenv("PAPER76_RESUME", "0") == "1"
        ablation_rows: List[Dict[str, str]] = read_csv(RESULTS / "ablation_rollouts.csv") if resume and (RESULTS / "ablation_rollouts.csv").exists() else []
        completed_seed_counts: Dict[str, int] = {}
        for row in ablation_rows:
            completed_seed_counts[row["seed"]] = completed_seed_counts.get(row["seed"], 0) + 1
        expected_per_seed = ABLATION_SCENARIOS * len(ABLATION_METHODS)
        combined = SPLIT_BY_NAME["combined_abort_stress"]
        for seed in SEEDS:
            if completed_seed_counts.get(str(seed), 0) >= expected_per_seed:
                progress(f"ablation seed {seed} already complete rows={completed_seed_counts[str(seed)]}")
                continue
            progress(f"ablation seed {seed} begin")
            for local_idx in range(ABLATION_SCENARIOS):
                scenario = build_scenario(combined, seed, 7000 + local_idx, "ablation")
                evidence = generate_evidence(scenario)
                for method in ABLATION_METHODS:
                    ablation_rows.append(evaluate_scenario(method, scenario, evidence))
            progress(f"ablation seed {seed} complete rows={len(ablation_rows)}")
            ablation_seed = build_seed_metrics(ablation_rows)
            ablation_summary = build_summary(ablation_seed)
            write_csv(RESULTS / "ablation_rollouts.csv", ablation_rows)
            write_csv(RESULTS / "ablation_seed_metrics.csv", ablation_seed)
            write_csv(RESULTS / "ablation_metrics.csv", ablation_summary)
        if ablation_rows:
            ablation_seed = build_seed_metrics(ablation_rows)
            ablation_summary = build_summary(ablation_seed)
            write_csv(RESULTS / "ablation_rollouts.csv", ablation_rows)
            write_csv(RESULTS / "ablation_seed_metrics.csv", ablation_seed)
            write_csv(RESULTS / "ablation_metrics.csv", ablation_summary)
        progress("ablation phase complete")
        return

    if phase == "stress":
        resume = os.getenv("PAPER76_RESUME", "0") == "1"
        stress_raw: List[Dict[str, str]] = read_csv(RESULTS / "stress_sweep_raw.csv") if resume and (RESULTS / "stress_sweep_raw.csv").exists() else []
        combined = SPLIT_BY_NAME["combined_abort_stress"]
        levels_env = os.getenv("PAPER76_STRESS_LEVELS", "").strip()
        if levels_env:
            stress_levels: Iterable[float] = [float(item) for item in levels_env.split(",") if item.strip()]
        else:
            stress_levels = [0.0, 1.0] if QUICK_MODE else np.linspace(0.0, 1.2, 7)
        completed_levels = {row["stress_level"] for row in stress_raw}
        for stress_level in stress_levels:
            level_key = f"{float(stress_level):.2f}"
            if level_key in completed_levels:
                progress(f"stress level {level_key} already complete")
                continue
            progress(f"stress level {float(stress_level):.2f} begin")
            for seed in SEEDS:
                for local_idx in range(STRESS_SCENARIOS):
                    scenario = build_scenario(
                        combined,
                        seed,
                        9000 + int(100 * float(stress_level)) + local_idx,
                        "stress",
                        stress_level=float(stress_level),
                    )
                    evidence = generate_evidence(scenario)
                    for method in STRESS_METHODS:
                        row = evaluate_scenario(method, scenario, evidence)
                        row["stress_level"] = f"{float(stress_level):.2f}"
                        stress_raw.append(row)
            progress(f"stress level {float(stress_level):.2f} complete rows={len(stress_raw)}")
            stress_summary = build_stress_summary(stress_raw)
            write_csv(RESULTS / "stress_sweep_raw.csv", stress_raw)
            write_csv(RESULTS / "stress_sweep.csv", stress_summary)
            write_csv(FIGURES / "stress_curve_data.csv", stress_summary)
        if stress_raw:
            stress_summary = build_stress_summary(stress_raw)
            write_csv(RESULTS / "stress_sweep_raw.csv", stress_raw)
            write_csv(RESULTS / "stress_sweep.csv", stress_summary)
            write_csv(FIGURES / "stress_curve_data.csv", stress_summary)
        progress("stress phase complete")
        return

    if phase == "fixed_risk":
        resume = os.getenv("PAPER76_RESUME", "0") == "1"
        fixed_raw: List[Dict[str, str]] = read_csv(RESULTS / "fixed_risk_raw.csv") if resume and (RESULTS / "fixed_risk_raw.csv").exists() else []
        combined = SPLIT_BY_NAME["combined_abort_stress"]
        completed = {(row["risk_budget"], row["seed"]) for row in fixed_raw}
        for budget in RISK_BUDGETS:
            budget_key = f"{budget:.2f}"
            for seed in SEEDS:
                if (budget_key, str(seed)) in completed:
                    progress(f"fixed-risk budget {budget_key} seed {seed} already complete")
                    continue
                progress(f"fixed-risk budget {budget_key} seed {seed} begin")
                for local_idx in range(FIXED_RISK_SCENARIOS):
                    scenario = build_scenario(
                        combined,
                        seed,
                        11000 + int(1000 * budget) + local_idx,
                        "fixed_risk",
                        stress_level=0.55,
                    )
                    evidence = generate_evidence(scenario)
                    for method in FIXED_RISK_METHODS:
                        fixed_raw.append(evaluate_scenario(method, scenario, evidence, risk_budget=budget))
                progress(f"fixed-risk budget {budget_key} seed {seed} complete rows={len(fixed_raw)}")
                fixed_seed = build_fixed_risk_seed_metrics(fixed_raw)
                fixed_summary = build_fixed_risk_summary(fixed_seed)
                fixed_pairwise = build_fixed_risk_pairwise(fixed_seed)
                write_csv(RESULTS / "fixed_risk_raw.csv", fixed_raw)
                write_csv(RESULTS / "fixed_risk_seed_metrics.csv", fixed_seed)
                write_csv(RESULTS / "fixed_risk_metrics.csv", fixed_summary)
                write_csv(RESULTS / "fixed_risk_pairwise.csv", fixed_pairwise)
                write_csv(FIGURES / "fixed_risk_curve_data.csv", fixed_summary)
        if fixed_raw:
            fixed_seed = build_fixed_risk_seed_metrics(fixed_raw)
            fixed_summary = build_fixed_risk_summary(fixed_seed)
            fixed_pairwise = build_fixed_risk_pairwise(fixed_seed)
            write_csv(RESULTS / "fixed_risk_raw.csv", fixed_raw)
            write_csv(RESULTS / "fixed_risk_seed_metrics.csv", fixed_seed)
            write_csv(RESULTS / "fixed_risk_metrics.csv", fixed_summary)
            write_csv(RESULTS / "fixed_risk_pairwise.csv", fixed_pairwise)
            write_csv(FIGURES / "fixed_risk_curve_data.csv", fixed_summary)
        progress("fixed-risk phase complete")
        return

    if phase == "finalize":
        progress("finalize phase reading artifacts")
        rollout_rows = read_csv(RESULTS / "rollouts.csv")
        seed_rows = read_csv(RESULTS / "raw_seed_metrics.csv")
        summary = read_csv(RESULTS / "metrics.csv")
        pairwise = read_csv(RESULTS / "pairwise_stats.csv")
        aggregate_seed = read_csv(RESULTS / "aggregate_seed_metrics.csv")
        aggregate_summary = read_csv(RESULTS / "aggregate_metrics.csv")
        aggregate_pairwise = read_csv(RESULTS / "aggregate_pairwise_stats.csv")
        ablation_rows = read_csv(RESULTS / "ablation_rollouts.csv")
        ablation_seed = read_csv(RESULTS / "ablation_seed_metrics.csv")
        ablation_summary = read_csv(RESULTS / "ablation_metrics.csv")
        stress_raw = read_csv(RESULTS / "stress_sweep_raw.csv")
        stress_summary = read_csv(RESULTS / "stress_sweep.csv")
        fixed_raw = read_csv(RESULTS / "fixed_risk_raw.csv")
        fixed_seed = read_csv(RESULTS / "fixed_risk_seed_metrics.csv")
        fixed_summary = read_csv(RESULTS / "fixed_risk_metrics.csv")
        fixed_pairwise = read_csv(RESULTS / "fixed_risk_pairwise.csv")
        evidence_log = read_csv(RESULTS / "abort_evidence.csv")
        write_csv(RESULTS / "negative_cases.csv", negative_cases(rollout_rows))
        write_csv(
            RESULTS / "training_summary.csv",
            [
                {
                    "quick_mode": str(QUICK_MODE),
                    "seeds": ";".join(str(seed) for seed in SEEDS),
                    "seed_count": str(len(SEEDS)),
                    "grid_n": str(GRID_N),
                    "eval_scenarios_per_split": str(EVAL_SCENARIOS),
                    "ablation_scenarios": str(ABLATION_SCENARIOS),
                    "stress_scenarios": str(STRESS_SCENARIOS),
                    "fixed_risk_scenarios": str(FIXED_RISK_SCENARIOS),
                    "max_attempts": str(MAX_ATTEMPTS),
                    "reference_method": REFERENCE_METHOD,
                    "splits": str(len(SPLITS)),
                    "methods": str(len(METHODS)),
                    "ablation_methods": str(len(ABLATION_METHODS)),
                    "fixed_risk_methods": str(len(FIXED_RISK_METHODS)),
                    "main_rollout_rows": str(len(rollout_rows)),
                    "abort_evidence_rows": str(len(evidence_log)),
                    "seed_metric_rows": str(len(seed_rows)),
                    "aggregate_seed_rows": str(len(aggregate_seed)),
                    "aggregate_metric_rows": str(len(aggregate_summary)),
                    "ablation_rows": str(len(ablation_rows)),
                    "ablation_seed_rows": str(len(ablation_seed)),
                    "stress_rows": str(len(stress_raw)),
                    "fixed_risk_rows": str(len(fixed_raw)),
                    "fixed_risk_seed_rows": str(len(fixed_seed)),
                }
            ],
        )
        plot_bar(summary, "combined_abort_stress", "success", FIGURES / "constraint_discovery_final_success.png", "Paper 76 combined-abort closed-loop success")
        plot_bar(summary, "combined_abort_stress", "boundary_f1", FIGURES / "constraint_discovery_boundary_f1.png", "Paper 76 hidden-constraint boundary F1")
        plot_bar(ablation_summary, "combined_abort_stress", "success", FIGURES / "constraint_discovery_ablation_success.png", "Paper 76 abort-discovery ablations")
        plot_stress(stress_summary, FIGURES / "constraint_discovery_stress_sweep.png")
        plot_fixed_risk(fixed_summary, FIGURES / "constraint_discovery_fixed_risk.png")
        decision, reason = decide(summary, pairwise, aggregate_summary, aggregate_pairwise, fixed_summary, fixed_pairwise, ablation_summary, stress_summary)
        elapsed = time.time() - start_time
        combined_rows = [row for row in summary if row["split"] == "combined_abort_stress"]
        aggregate_rows = [row for row in aggregate_summary if row["split"] == "aggregate_hard_regime"]
        with (RESULTS / "summary.txt").open("w", encoding="utf-8") as f:
            f.write("Paper 76 constraint_discovery_from_aborted_actions expanded v5 abort-physics rebuild\n")
            f.write(f"Terminal recommendation: {decision}\n")
            f.write(f"Reason: {reason}\n")
            f.write(f"Main rollout rows: {len(rollout_rows)}\n")
            f.write(f"Abort evidence rows: {len(evidence_log)}\n")
            f.write(f"Seed metric rows: {len(seed_rows)}\n")
            f.write(f"Aggregate seed rows: {len(aggregate_seed)}\n")
            f.write(f"Ablation rows: {len(ablation_rows)}\n")
            f.write(f"Ablation seed rows: {len(ablation_seed)}\n")
            f.write(f"Stress rows: {len(stress_raw)}\n")
            f.write(f"Fixed-risk rows: {len(fixed_raw)}\n")
            f.write(f"Fixed-risk seed rows: {len(fixed_seed)}\n")
            f.write(f"Seeds: {SEEDS}\n")
            f.write(f"Grid size: {GRID_N}x{GRID_N}\n")
            f.write(f"Evaluation scenarios per split: {EVAL_SCENARIOS}\n")
            f.write(f"Risk budgets: {RISK_BUDGETS}\n")
            f.write(f"Finalize runtime seconds: {elapsed:.2f}\n\n")
            f.write("Combined-abort-stress summary:\n")
            for row in sorted(combined_rows, key=lambda item: -float(item["mean_success"])):
                f.write(
                    f"{row['method']} success={row['mean_success']} ci95={row['ci95_success']} "
                    f"abort={row['mean_aborted']} repeated={row['mean_repeated_abort']} violation={row['mean_violation']} "
                    f"boundary_f1={row['mean_boundary_f1']} iou={row['mean_boundary_iou']} "
                    f"efficiency={row['mean_path_efficiency']} area={row['mean_discovered_area']}\n"
                )
            f.write("\nAggregate hard-regime summary:\n")
            for row in sorted(aggregate_rows, key=lambda item: -float(item["mean_success"])):
                f.write(
                    f"{row['method']} success={row['mean_success']} ci95={row['ci95_success']} "
                    f"repeated={row['mean_repeated_abort']} violation={row['mean_violation']} "
                    f"boundary_f1={row['mean_boundary_f1']} efficiency={row['mean_path_efficiency']} area={row['mean_discovered_area']}\n"
                )
            f.write("\nFixed-risk combined-abort-stress summary:\n")
            for row in sorted([r for r in fixed_summary if r["split"] == "combined_abort_stress"], key=lambda item: (float(item["risk_budget"]), -float(item["mean_success"]))):
                f.write(
                    f"budget={row['risk_budget']} {row['method']} success={row['mean_success']} ci95={row['ci95_success']} "
                    f"repeated={row['mean_repeated_abort']} violation={row['mean_violation']} efficiency={row['mean_path_efficiency']}\n"
                )
        print(f"wrote Paper 76 abort-constraint evidence to {RESULTS}")
        print(f"terminal recommendation: {decision}")
        print(reason)
        progress(f"finalize phase complete decision={decision}")
        return

    rollout_rows: List[Dict[str, str]] = []
    evidence_log: List[Dict[str, str]] = []
    training_rows: List[Dict[str, str]] = []

    for seed in SEEDS:
        progress(f"main seed {seed} begin")
        seed_evidence_count = 0
        seed_abort_count = 0
        for split in SPLITS:
            progress(f"main seed {seed} split {split.name} begin")
            for local_idx in range(EVAL_SCENARIOS):
                scenario = build_scenario(split, seed, 1000 * split.task_id + local_idx, "eval")
                evidence = generate_evidence(scenario)
                seed_evidence_count += len(evidence)
                seed_abort_count += sum(1 for ev in evidence if ev.aborted)
                evidence_log.extend(evidence_rows(scenario, evidence))
                for method in METHODS:
                    rollout_rows.append(evaluate_scenario(method, scenario, evidence))
            progress(f"main seed {seed} split {split.name} complete rollouts={len(rollout_rows)}")
        training_rows.append(
            {
                "seed": str(seed),
                "quick_mode": str(QUICK_MODE),
                "eval_scenarios_per_split": str(EVAL_SCENARIOS),
                "evidence_rollouts": str(seed_evidence_count),
                "evidence_abort_count": str(seed_abort_count),
                "grid_n": str(GRID_N),
                "max_attempts": str(MAX_ATTEMPTS),
            }
        )
        progress(f"main seed {seed} complete evidence={seed_evidence_count} aborts={seed_abort_count}")

    progress("building main summaries")
    seed_rows = build_seed_metrics(rollout_rows)
    summary = build_summary(seed_rows)
    pairwise = build_pairwise(seed_rows)
    aggregate_seed = build_aggregate_seed_metrics(seed_rows)
    aggregate_summary = build_summary(aggregate_seed)
    aggregate_pairwise = build_pairwise(aggregate_seed)

    ablation_rows: List[Dict[str, str]] = []
    combined = SPLIT_BY_NAME["combined_abort_stress"]
    for seed in SEEDS:
        progress(f"ablation seed {seed} begin")
        for local_idx in range(ABLATION_SCENARIOS):
            scenario = build_scenario(combined, seed, 7000 + local_idx, "ablation")
            evidence = generate_evidence(scenario)
            for method in ABLATION_METHODS:
                ablation_rows.append(evaluate_scenario(method, scenario, evidence))
        progress(f"ablation seed {seed} complete rows={len(ablation_rows)}")
    progress("building ablation summaries")
    ablation_seed = build_seed_metrics(ablation_rows)
    ablation_summary = build_summary(ablation_seed)

    stress_raw: List[Dict[str, str]] = []
    stress_levels: Iterable[float] = [0.0, 1.0] if QUICK_MODE else np.linspace(0.0, 1.2, 7)
    for stress_level in stress_levels:
        progress(f"stress level {float(stress_level):.2f} begin")
        for seed in SEEDS:
            for local_idx in range(STRESS_SCENARIOS):
                scenario = build_scenario(combined, seed, 9000 + int(100 * float(stress_level)) + local_idx, "stress", stress_level=float(stress_level))
                evidence = generate_evidence(scenario)
                for method in STRESS_METHODS:
                    row = evaluate_scenario(method, scenario, evidence)
                    row["stress_level"] = f"{float(stress_level):.2f}"
                    stress_raw.append(row)
        progress(f"stress level {float(stress_level):.2f} complete rows={len(stress_raw)}")
    progress("building stress summaries and writing artifacts")
    stress_summary = build_stress_summary(stress_raw)

    fixed_raw: List[Dict[str, str]] = []
    for budget in RISK_BUDGETS:
        progress(f"fixed-risk budget {budget:.2f} begin")
        for seed in SEEDS:
            for local_idx in range(FIXED_RISK_SCENARIOS):
                scenario = build_scenario(combined, seed, 11000 + int(1000 * budget) + local_idx, "fixed_risk", stress_level=0.55)
                evidence = generate_evidence(scenario)
                for method in FIXED_RISK_METHODS:
                    fixed_raw.append(evaluate_scenario(method, scenario, evidence, risk_budget=budget))
        progress(f"fixed-risk budget {budget:.2f} complete rows={len(fixed_raw)}")
    fixed_seed = build_fixed_risk_seed_metrics(fixed_raw)
    fixed_summary = build_fixed_risk_summary(fixed_seed)
    fixed_pairwise = build_fixed_risk_pairwise(fixed_seed)

    write_csv(RESULTS / "abort_evidence.csv", evidence_log)
    write_csv(RESULTS / "rollouts.csv", rollout_rows)
    write_csv(RESULTS / "raw_seed_metrics.csv", seed_rows)
    write_csv(RESULTS / "metrics.csv", summary)
    write_csv(RESULTS / "pairwise_stats.csv", pairwise)
    write_csv(RESULTS / "aggregate_seed_metrics.csv", aggregate_seed)
    write_csv(RESULTS / "aggregate_metrics.csv", aggregate_summary)
    write_csv(RESULTS / "aggregate_pairwise_stats.csv", aggregate_pairwise)
    write_csv(RESULTS / "ablation_rollouts.csv", ablation_rows)
    write_csv(RESULTS / "ablation_seed_metrics.csv", ablation_seed)
    write_csv(RESULTS / "ablation_metrics.csv", ablation_summary)
    write_csv(RESULTS / "stress_sweep_raw.csv", stress_raw)
    write_csv(RESULTS / "stress_sweep.csv", stress_summary)
    write_csv(FIGURES / "stress_curve_data.csv", stress_summary)
    write_csv(RESULTS / "fixed_risk_raw.csv", fixed_raw)
    write_csv(RESULTS / "fixed_risk_seed_metrics.csv", fixed_seed)
    write_csv(RESULTS / "fixed_risk_metrics.csv", fixed_summary)
    write_csv(RESULTS / "fixed_risk_pairwise.csv", fixed_pairwise)
    write_csv(FIGURES / "fixed_risk_curve_data.csv", fixed_summary)
    write_csv(RESULTS / "negative_cases.csv", negative_cases(rollout_rows))
    write_csv(
        RESULTS / "training_summary.csv",
        [
            {
                "quick_mode": str(QUICK_MODE),
                "seeds": ";".join(str(seed) for seed in SEEDS),
                "seed_count": str(len(SEEDS)),
                "grid_n": str(GRID_N),
                "eval_scenarios_per_split": str(EVAL_SCENARIOS),
                "ablation_scenarios": str(ABLATION_SCENARIOS),
                "stress_scenarios": str(STRESS_SCENARIOS),
                "fixed_risk_scenarios": str(FIXED_RISK_SCENARIOS),
                "max_attempts": str(MAX_ATTEMPTS),
                "reference_method": REFERENCE_METHOD,
                "splits": str(len(SPLITS)),
                "methods": str(len(METHODS)),
                "ablation_methods": str(len(ABLATION_METHODS)),
                "fixed_risk_methods": str(len(FIXED_RISK_METHODS)),
                "main_rollout_rows": str(len(rollout_rows)),
                "abort_evidence_rows": str(len(evidence_log)),
                "seed_metric_rows": str(len(seed_rows)),
                "aggregate_seed_rows": str(len(aggregate_seed)),
                "ablation_rows": str(len(ablation_rows)),
                "ablation_seed_rows": str(len(ablation_seed)),
                "stress_rows": str(len(stress_raw)),
                "fixed_risk_rows": str(len(fixed_raw)),
                "fixed_risk_seed_rows": str(len(fixed_seed)),
            }
        ]
        + training_rows,
    )

    plot_bar(summary, "combined_abort_stress", "success", FIGURES / "constraint_discovery_final_success.png", "Paper 76 combined-abort closed-loop success")
    plot_bar(summary, "combined_abort_stress", "boundary_f1", FIGURES / "constraint_discovery_boundary_f1.png", "Paper 76 hidden-constraint boundary F1")
    plot_bar(ablation_summary, "combined_abort_stress", "success", FIGURES / "constraint_discovery_ablation_success.png", "Paper 76 abort-discovery ablations")
    plot_stress(stress_summary, FIGURES / "constraint_discovery_stress_sweep.png")
    plot_fixed_risk(fixed_summary, FIGURES / "constraint_discovery_fixed_risk.png")

    decision, reason = decide(summary, pairwise, aggregate_summary, aggregate_pairwise, fixed_summary, fixed_pairwise, ablation_summary, stress_summary)
    elapsed = time.time() - start_time
    combined_rows = [row for row in summary if row["split"] == "combined_abort_stress"]
    aggregate_rows = [row for row in aggregate_summary if row["split"] == "aggregate_hard_regime"]
    with (RESULTS / "summary.txt").open("w", encoding="utf-8") as f:
        f.write("Paper 76 constraint_discovery_from_aborted_actions expanded v5 abort-physics rebuild\n")
        f.write(f"Terminal recommendation: {decision}\n")
        f.write(f"Reason: {reason}\n")
        f.write(f"Main rollout rows: {len(rollout_rows)}\n")
        f.write(f"Abort evidence rows: {len(evidence_log)}\n")
        f.write(f"Seed metric rows: {len(seed_rows)}\n")
        f.write(f"Aggregate seed rows: {len(aggregate_seed)}\n")
        f.write(f"Ablation rows: {len(ablation_rows)}\n")
        f.write(f"Ablation seed rows: {len(ablation_seed)}\n")
        f.write(f"Stress rows: {len(stress_raw)}\n")
        f.write(f"Fixed-risk rows: {len(fixed_raw)}\n")
        f.write(f"Fixed-risk seed rows: {len(fixed_seed)}\n")
        f.write(f"Seeds: {SEEDS}\n")
        f.write(f"Grid size: {GRID_N}x{GRID_N}\n")
        f.write(f"Evaluation scenarios per split: {EVAL_SCENARIOS}\n")
        f.write(f"Risk budgets: {RISK_BUDGETS}\n")
        f.write(f"Runtime seconds: {elapsed:.2f}\n\n")
        f.write("Combined-abort-stress summary:\n")
        for row in sorted(combined_rows, key=lambda item: -float(item["mean_success"])):
            f.write(
                f"{row['method']} success={row['mean_success']} ci95={row['ci95_success']} "
                f"abort={row['mean_aborted']} repeated={row['mean_repeated_abort']} violation={row['mean_violation']} "
                f"boundary_f1={row['mean_boundary_f1']} iou={row['mean_boundary_iou']} "
                f"efficiency={row['mean_path_efficiency']} area={row['mean_discovered_area']}\n"
            )
        f.write("\nAggregate hard-regime summary:\n")
        for row in sorted(aggregate_rows, key=lambda item: -float(item["mean_success"])):
            f.write(
                f"{row['method']} success={row['mean_success']} ci95={row['ci95_success']} "
                f"repeated={row['mean_repeated_abort']} violation={row['mean_violation']} "
                f"boundary_f1={row['mean_boundary_f1']} efficiency={row['mean_path_efficiency']} area={row['mean_discovered_area']}\n"
            )
        f.write("\nFixed-risk combined-abort-stress summary:\n")
        for row in sorted([r for r in fixed_summary if r["split"] == "combined_abort_stress"], key=lambda item: (float(item["risk_budget"]), -float(item["mean_success"]))):
            f.write(
                f"budget={row['risk_budget']} {row['method']} success={row['mean_success']} ci95={row['ci95_success']} "
                f"repeated={row['mean_repeated_abort']} violation={row['mean_violation']} efficiency={row['mean_path_efficiency']}\n"
            )
    print(f"wrote Paper 76 abort-constraint evidence to {RESULTS}")
    print(f"terminal recommendation: {decision}")
    print(reason)
    progress(f"complete decision={decision}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback

        traceback.print_exc()
        raise
