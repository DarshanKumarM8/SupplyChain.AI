"""
Manifold Sweep — Offline Parameter Space Precomputation
=========================================================

Sweeps across the parameter space (β, adoption_pct, shock_intensity)
and runs the full simulation pipeline for each combination.
Results are saved as JSON files matching the manifold_frame.json schema.

Usage:
    python -m precompute.manifold_sweep --output-dir data/manifold/

Parameter Grid (default):
    β ∈ [0.1, 0.3, 0.5, 0.7, 0.9]          → 5 steps
    adoption ∈ [0.0, 0.2, 0.4, 0.6, 0.8]    → 5 steps
    shock ∈ [0.3, 0.5, 0.7, 1.0]            → 4 steps
    Total: 100 manifold states
"""

import json
import os
import argparse
import numpy as np
from itertools import product


# Parameter grid
BETA_GRID = [0.1, 0.3, 0.5, 0.7, 0.9]
ADOPTION_GRID = [0.0, 0.2, 0.4, 0.6, 0.8]
SHOCK_GRID = [0.3, 0.5, 0.7, 1.0]


def run_single_simulation(beta: float, adoption: float, shock: float, scenario: dict) -> dict:
    """
    Run a single simulation for given parameters and return a manifold frame.

    Args:
        beta: Competitor panic parameter
        adoption: Market adoption fraction of SupplyChainAI
        shock: Disruption intensity

    Returns:
        Manifold frame dict matching shared/api_schemas/manifold_frame.json
    """
    # TODO: Implement simulation pipeline
    # 1. Load scenario graph
    # 2. Initialize agents with beta/adoption/shock
    # 3. Run Sentinel → Triage → Reflex pipeline
    # 4. Record SupplyChainAI Index trajectory (naive + AI)
    # 5. Record node states, density field, meta-herd status
    raise NotImplementedError("Single simulation not yet implemented")


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

    for beta, adoption, shock in product(beta_grid, adoption_grid, shock_grid):
        print(f"  Sweeping: β={beta}, adoption={adoption}, shock={shock} (frame {frame_id})")

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
            json.dump(frame, f, indent=2)

        output_files.append(filepath)
        frame_id += 1

    print(f"Generated {frame_id} manifold frames in {output_dir}")
    return output_files


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SupplyChainAI Manifold Sweep")
    parser.add_argument("--scenario", default="data/scenarios/kaohsiung_typhoon.json")
    parser.add_argument("--output-dir", default="data/manifold/")
    args = parser.parse_args()

    sweep_manifold(args.scenario, args.output_dir)
