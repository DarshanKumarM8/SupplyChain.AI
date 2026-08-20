"""
Fokker-Planck 2D Density Field Solver
======================================

Solves the Fokker-Planck PDE on a discrete (lanes × weeks) grid
to model the evolution of rerouting agent density under herd drift and entropy diffusion.

PDE: ∂ρ/∂t = -∇·(μρ) + D·∇²ρ

Method: Explicit finite-difference (Euler forward) with reflective boundary conditions.
Stability: dt < dx² / (4D)
"""

import numpy as np
from typing import Optional


class FokkerPlanckSolver:
    """
    2D Fokker-Planck density field solver for supply chain agent rerouting.
    """

    def __init__(self, n_lanes: int, n_weeks: int, dx: float = 1.0):
        """
        Args:
            n_lanes: Number of discrete shipping lanes
            n_weeks: Number of discrete time windows (weeks)
            dx: Spatial grid spacing (normalized)
        """
        self.n_lanes = n_lanes
        self.n_weeks = n_weeks
        self.dx = dx

    def initialize_density(self, hotspot_indices: Optional[list[tuple[int, int]]] = None) -> np.ndarray:
        """
        Create initial density field. Default: uniform.
        If hotspot_indices provided, concentrate density at those (lane, week) cells.
        """
        # TODO: Implement initial density configuration
        rho = np.ones((self.n_lanes, self.n_weeks)) / (self.n_lanes * self.n_weeks)
        if hotspot_indices:
            rho *= 0.1
            for i, j in hotspot_indices:
                rho[i, j] = 0.5 / len(hotspot_indices)
        # Normalize
        rho /= rho.sum()
        return rho

    def compute_drift_field(self, herd_signal: np.ndarray) -> np.ndarray:
        """
        Compute drift vector field from herd behavior signals.
        Drift points toward the most popular (lane, week) choices.

        Args:
            herd_signal: (n_lanes, n_weeks) — intensity of herd behavior per cell

        Returns:
            (n_lanes, n_weeks, 2) drift vector field
        """
        # TODO: Implement drift computation from order flow data
        raise NotImplementedError("Drift field computation not yet implemented")

    def solve(
        self,
        rho_0: np.ndarray,
        drift: np.ndarray,
        diffusion: float,
        n_steps: int = 200,
        dt: Optional[float] = None,
    ) -> np.ndarray:
        """
        Solve the FP equation using explicit Euler finite differences.

        Args:
            rho_0: (n_lanes, n_weeks) initial density
            drift: (n_lanes, n_weeks, 2) drift vector field [d_lane, d_week]
            diffusion: scalar diffusion coefficient D
            n_steps: number of time integration steps
            dt: time step (auto-computed for stability if None)

        Returns:
            rho_final: (n_lanes, n_weeks) density at final time
        """
        # TODO: Implement the finite-difference PDE solver
        # 1. Compute stable dt if not provided: dt < dx² / (4 * diffusion)
        # 2. For each time step:
        #    a. Compute advection term: -∇·(μρ) using central differences
        #    b. Compute diffusion term: D·∇²ρ using 5-point Laplacian stencil
        #    c. Update: ρ_new = ρ + dt * (diffusion_term + advection_term)
        #    d. Apply reflective (Neumann) boundary conditions
        #    e. Renormalize to ensure ∫ρ = 1
        # 3. Return final density field
        raise NotImplementedError("FP PDE solver not yet implemented")

    def find_critical_density(self, rho: np.ndarray, threshold: float = 0.15) -> list[tuple[int, int]]:
        """
        Identify cells where density exceeds the critical tipping threshold.
        These are the "shock line" positions rendered in the UI.
        """
        critical = []
        for i in range(self.n_lanes):
            for j in range(self.n_weeks):
                if rho[i, j] > threshold:
                    critical.append((i, j))
        return critical
