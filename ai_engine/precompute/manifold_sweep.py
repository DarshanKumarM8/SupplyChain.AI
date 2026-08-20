"""
Manifold Sweep -- Offline Parameter Space Precomputation
=========================================================

Sweeps across the parameter space (beta, adoption_pct, shock_intensity)
and runs the full simulation pipeline for each combination.
Results are saved as JSON files matching the manifold_frame.json schema.

Usage:
    python -m precompute.manifold_sweep --output-dir data/manifold/

Parameter Grid (default):
    beta in [0.1, 0.3, 0.5, 0.7, 0.9]          -> 5 steps
    adoption in [0.0, 0.2, 0.4, 0.6, 0.8]       -> 5 steps
    shock in [0.3, 0.5, 0.7, 1.0]               -> 4 steps
    Total: 100 manifold states
"""

import json
import os
import argparse
import numpy as np
from itertools import product
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from models.fokker_planck import FokkerPlanckSolver
from models.meta_herd_detector import MetaHerdDetector
from shared.constants import (
    INDEX_W1_SPEARMAN,
    INDEX_W2_DEPLETION,
    INDEX_W3_VOLATILITY,
    ENTROPY_BUDGET_PCT,
    META_HERD_COSINE_THRESHOLD,
    DEMO_NAIVE_COST_USD,
    DEMO_AI_COST_USD,
)


# Parameter grid
BETA_GRID = [0.1, 0.3, 0.5, 0.7, 0.9]
ADOPTION_GRID = [0.0, 0.2, 0.4, 0.6, 0.8]
SHOCK_GRID = [0.3, 0.5, 0.7, 1.0]

# Simulation constants
N_LANES = 10
N_WEEKS = 6
N_FIRMS = 20
N_TRAJECTORY_TICKS = 60  # 60 ticks in the simulation timeline


def _compute_naive_index(beta: float, shock: float, tick: int, n_ticks: int) -> float:
    """
    Compute the naive (no-AI) Stampede Index at a given tick.
    Models the herd formation as a sigmoid buildup.
    """
    # Sigmoid ramp-up: herd forms quickly
    progress = tick / max(n_ticks - 1, 1)
    ramp = 1.0 / (1.0 + np.exp(-10 * (progress - 0.3)))

    # Base index driven by shock and beta
    peak = 22.5 + 65 * shock * (0.5 + 0.5 * beta)
    peak = min(100, peak)

    # Resting state before shock
    resting = 12.0

    return resting + (peak - resting) * ramp


def _compute_ai_index(
    beta: float,
    shock: float,
    adoption: float,
    tick: int,
    n_ticks: int,
    meta_herd_detected: bool,
) -> float:
    """
    Compute the AI-optimized Stampede Index at a given tick.
    Models the de-phased, entropy-buffered response.
    """
    progress = tick / max(n_ticks - 1, 1)

    # AI index has a brief spike then quickly resolves
    # The spike is proportional to shock but dampened by AI
    resting = 12.0
    spike_peak = resting + 15 * shock * (0.3 + 0.2 * beta)

    # Quick spike then decay (exponential)
    if progress < 0.2:
        ramp = progress / 0.2
        value = resting + (spike_peak - resting) * ramp
    else:
        decay = np.exp(-3 * (progress - 0.2))
        settled = resting + 5 * shock * (0.2 + 0.1 * beta)
        value = settled + (spike_peak - settled) * decay

    # If meta-herd detected (high adoption), entropy budget adds slight noise
    if meta_herd_detected:
        value += 3 * adoption  # Slight increase due to meta-herd complexity

    return max(0, min(100, value))


def run_single_simulation(
    beta: float,
    adoption: float,
    shock: float,
    scenario: dict,
) -> dict:
    """
    Run a single simulation for given parameters and return a manifold frame.

    Args:
        beta: Competitor panic parameter
        adoption: Market adoption fraction of SupplyChainAI
        shock: Disruption intensity

    Returns:
        Manifold frame dict matching shared/api_schemas/manifold_frame.json
    """
    rng = np.random.default_rng(int(beta * 1000 + adoption * 100 + shock * 10))

    # ── Fokker-Planck density field ──
    solver = FokkerPlanckSolver(N_LANES, N_WEEKS)

    # Build herd signal from shock
    herd_signal = np.zeros((N_LANES, N_WEEKS))
    n_hot = max(1, int(2 + shock * 3))
    for i in range(min(n_hot, N_LANES)):
        for j in range(min(2, N_WEEKS)):
            herd_signal[i, j] = shock * (1.0 - 0.15 * i)
    herd_signal += rng.uniform(0, 0.05, (N_LANES, N_WEEKS))

    # Solve density field with AI diffusion
    rho_0 = solver.initialize_density()
    drift = solver.compute_drift_field(herd_signal, beta=beta)
    diffusion = 0.05 + 0.2 * ENTROPY_BUDGET_PCT * 100
    rho_final = solver.solve(rho_0, drift, diffusion=diffusion, n_steps=100)

    # ── Meta-herd detection ──
    meta_herd_detected = False
    entropy_budget_active = False
    if adoption > 0.5:
        # Simulate firms adopting similar de-phasing -> meta-herd risk
        detector = MetaHerdDetector()
        dephasing_vecs = {}
        for i in range(N_FIRMS):
            if rng.random() < adoption:
                # Firms using AI have similar strategies
                base = rng.dirichlet(np.ones(N_LANES) * 2.0)
                dephasing_vecs[f"firm_{i}"] = base + rng.normal(0, 0.02 * (1 - adoption), N_LANES)
            else:
                dephasing_vecs[f"firm_{i}"] = rng.dirichlet(np.ones(N_LANES))

        result = detector.detect(dephasing_vecs)
        meta_herd_detected = result["meta_herd_detected"]
        entropy_budget_active = meta_herd_detected

    # ── Compute index trajectories ──
    naive_trajectory = []
    ai_trajectory = []
    for tick in range(N_TRAJECTORY_TICKS):
        naive_idx = _compute_naive_index(beta, shock, tick, N_TRAJECTORY_TICKS)
        ai_idx = _compute_ai_index(beta, shock, adoption, tick, N_TRAJECTORY_TICKS, meta_herd_detected)
        naive_trajectory.append(round(naive_idx, 1))
        ai_trajectory.append(round(ai_idx, 1))

    # ── Build node states ──
    nodes = scenario.get("nodes", [])
    node_states = []
    for node in nodes[:30]:  # Limit for JSON size
        is_bottleneck = rng.random() < 0.15 * shock
        capacity_pct = float(rng.uniform(0.2, 0.95))
        if is_bottleneck:
            capacity_pct = float(rng.uniform(0.05, 0.4))
        lane_price_delta = float(rng.uniform(0, 0.1))
        if is_bottleneck:
            lane_price_delta = float(rng.uniform(0.15, max(0.16, 0.45 * shock)))

        node_states.append({
            "id": node["id"],
            "capacity_pct": round(capacity_pct, 2),
            "is_bottleneck": bool(is_bottleneck),
            "lane_price_delta": round(lane_price_delta, 2),
        })

    # ── Build manifold frame ──
    frame = {
        "stampede_index_trajectory": naive_trajectory,
        "ai_index_trajectory": ai_trajectory,
        "node_states": node_states,
        "density_field_snapshot": rho_final.tolist(),
        "meta_herd_detected": meta_herd_detected,
        "entropy_budget_active": entropy_budget_active,
    }

    return frame


def sweep_manifold(
    scenario_path: str,
    output_dir: str,
    beta_grid: list[float] = None,
    adoption_grid: list[float] = None,
    shock_grid: list[float] = None,
) -> list[str]:
    """
    Run the full parameter sweep and save manifold frames.

    Returns:
        List of output file paths
    """
    if beta_grid is None:
        beta_grid = BETA_GRID
    if adoption_grid is None:
        adoption_grid = ADOPTION_GRID
    if shock_grid is None:
        shock_grid = SHOCK_GRID

    os.makedirs(output_dir, exist_ok=True)

    with open(scenario_path, 'r') as f:
        scenario = json.load(f)

    output_files = []
    frame_id = 0
    total = len(beta_grid) * len(adoption_grid) * len(shock_grid)

    print(f"Starting manifold sweep: {total} parameter combinations")
    print(f"  Beta: {beta_grid}")
    print(f"  Adoption: {adoption_grid}")
    print(f"  Shock: {shock_grid}")
    print()

    for beta, adoption, shock in product(beta_grid, adoption_grid, shock_grid):
        print(f"  [{frame_id + 1}/{total}] beta={beta}, adoption={adoption}, shock={shock}", end="")

        frame = run_single_simulation(beta, adoption, shock, scenario)
        frame["frame_id"] = frame_id
        frame["params"] = {
            "beta": beta,
            "adoption_pct": adoption,
            "shock_intensity": shock,
        }

        filename = f"frame_{frame_id:04d}.json"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(frame, f, separators=(',', ':'))  # Compact JSON

        output_files.append(filepath)
        frame_id += 1
        print(f" -> OK")

    # Also save an index file for quick lookup
    index = {
        "total_frames": frame_id,
        "parameter_grid": {
            "beta": beta_grid,
            "adoption_pct": adoption_grid,
            "shock_intensity": shock_grid,
        },
        "frames": [
            {
                "frame_id": i,
                "params": {
                    "beta": b,
                    "adoption_pct": a,
                    "shock_intensity": s,
                },
                "filename": f"frame_{i:04d}.json",
            }
            for i, (b, a, s) in enumerate(product(beta_grid, adoption_grid, shock_grid))
        ],
    }
    index_path = os.path.join(output_dir, "manifold_index.json")
    with open(index_path, 'w') as f:
        json.dump(index, f, indent=2)

    print(f"\n[DONE] Generated {frame_id} manifold frames in {output_dir}")
    print(f"  Index file: {index_path}")
    return output_files


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SupplyChainAI Manifold Sweep")
    parser.add_argument("--scenario", default="data/scenarios/kaohsiung_typhoon.json")
    parser.add_argument("--output-dir", default="data/manifold/")
    args = parser.parse_args()

    # Resolve paths relative to ai_engine directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    scenario_path = os.path.join(base_dir, args.scenario)
    output_dir = os.path.join(base_dir, args.output_dir)

    sweep_manifold(scenario_path, output_dir)
