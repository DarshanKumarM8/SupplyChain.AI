"""
Fokker-Planck 2D Density Field Solver
======================================

Solves the Fokker-Planck PDE on a discrete (lanes x weeks) grid
to model the evolution of rerouting agent density under herd drift and entropy diffusion.

PDE: dρ/dt = -div(μρ) + D * laplacian(ρ)

Method: Explicit finite-difference (Euler forward) with reflective boundary conditions.
Stability: dt < dx^2 / (4D)
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
        rho = np.ones((self.n_lanes, self.n_weeks)) / (self.n_lanes * self.n_weeks)
        if hotspot_indices:
            rho *= 0.1
            for i, j in hotspot_indices:
                rho[i, j] = 0.5 / len(hotspot_indices)
            # Normalize
            rho /= rho.sum()
        return rho

    def compute_drift_field(self, herd_signal: np.ndarray, beta: float = 0.6) -> np.ndarray:
        """
        Compute drift vector field from herd behavior signals.
        Drift points toward the most popular (lane, week) choices,
        scaled by competitor panic parameter beta.

        The drift is computed as the gradient of the herd signal,
        pointing from low-demand to high-demand cells (the direction
        the "herd" is moving).

        Args:
            herd_signal: (n_lanes, n_weeks) -- intensity of herd behavior per cell
            beta: Competitor panic parameter [0, 1]. Higher = stronger herd following.

        Returns:
            (n_lanes, n_weeks, 2) drift vector field [d_lane, d_week]
        """
        drift = np.zeros((self.n_lanes, self.n_weeks, 2))

        # Compute gradients using central differences with zero-padding at boundaries
        # Gradient along lane axis (axis 0)
        for i in range(self.n_lanes):
            for j in range(self.n_weeks):
                # Lane gradient (axis 0)
                if i == 0:
                    drift[i, j, 0] = herd_signal[i + 1, j] - herd_signal[i, j]
                elif i == self.n_lanes - 1:
                    drift[i, j, 0] = herd_signal[i, j] - herd_signal[i - 1, j]
                else:
                    drift[i, j, 0] = (herd_signal[i + 1, j] - herd_signal[i - 1, j]) / 2.0

                # Week gradient (axis 1)
                if j == 0:
                    drift[i, j, 1] = herd_signal[i, j + 1] - herd_signal[i, j]
                elif j == self.n_weeks - 1:
                    drift[i, j, 1] = herd_signal[i, j] - herd_signal[i, j - 1]
                else:
                    drift[i, j, 1] = (herd_signal[i, j + 1] - herd_signal[i, j - 1]) / 2.0

        # Scale drift by beta (higher panic = stronger herding)
        drift *= beta

        return drift

    def solve(
        self,
        rho_0: np.ndarray,
        drift: np.ndarray,
        diffusion: float,
        n_steps: int = 200,
        dt: Optional[float] = None,
        record_trajectory: bool = False,
    ) -> np.ndarray | tuple[np.ndarray, list[np.ndarray]]:
        """
        Solve the FP equation using explicit Euler finite differences.

        PDE: dρ/dt = -div(μρ) + D * laplacian(ρ)

        Args:
            rho_0: (n_lanes, n_weeks) initial density
            drift: (n_lanes, n_weeks, 2) drift vector field [d_lane, d_week]
            diffusion: scalar diffusion coefficient D (entropy budget drives this)
            n_steps: number of time integration steps
            dt: time step (auto-computed for stability if None)
            record_trajectory: if True, also return list of density snapshots

        Returns:
            rho_final: (n_lanes, n_weeks) density at final time
            If record_trajectory, returns (rho_final, trajectory_list)
        """
        dx = self.dx
        NL = self.n_lanes
        NW = self.n_weeks

        # 1. Compute stable dt if not provided: dt < dx^2 / (4 * D)
        if dt is None:
            max_drift = np.max(np.abs(drift)) + 1e-12
            dt_diffusion = (dx ** 2) / (4.0 * diffusion + 1e-12)
            dt_advection = dx / (2.0 * max_drift)
            dt = 0.4 * min(dt_diffusion, dt_advection)  # Safety factor 0.4

        rho = rho_0.copy()
        trajectory = []

        for step in range(n_steps):
            if record_trajectory and step % max(1, n_steps // 20) == 0:
                trajectory.append(rho.copy())

            rho_new = rho.copy()

            # --- Interior points (1..NL-2, 1..NW-2) ---
            for i in range(NL):
                for j in range(NW):
                    # ── Diffusion term: D * laplacian(ρ) using 5-point stencil ──
                    # laplacian = (ρ_{i+1,j} + ρ_{i-1,j} + ρ_{i,j+1} + ρ_{i,j-1} - 4ρ_{i,j}) / dx^2
                    # Use reflective (Neumann) BC: at boundary, neighbor = self
                    rho_ip = rho[min(i + 1, NL - 1), j]  # i+1
                    rho_im = rho[max(i - 1, 0), j]        # i-1
                    rho_jp = rho[i, min(j + 1, NW - 1)]  # j+1
                    rho_jm = rho[i, max(j - 1, 0)]        # j-1

                    laplacian = (rho_ip + rho_im + rho_jp + rho_jm - 4.0 * rho[i, j]) / (dx ** 2)
                    diffusion_term = diffusion * laplacian

                    # ── Advection term: -div(μρ) using upwind scheme ──
                    # div(μρ) = d(μ_x * ρ)/dx + d(μ_y * ρ)/dy
                    mu_x = drift[i, j, 0]
                    mu_y = drift[i, j, 1]

                    # Upwind differencing for stability
                    if mu_x >= 0:
                        d_murho_x = (mu_x * rho[i, j] - drift[max(i - 1, 0), j, 0] * rho[max(i - 1, 0), j]) / dx
                    else:
                        d_murho_x = (drift[min(i + 1, NL - 1), j, 0] * rho[min(i + 1, NL - 1), j] - mu_x * rho[i, j]) / dx

                    if mu_y >= 0:
                        d_murho_y = (mu_y * rho[i, j] - drift[i, max(j - 1, 0), 1] * rho[i, max(j - 1, 0)]) / dx
                    else:
                        d_murho_y = (drift[i, min(j + 1, NW - 1), 1] * rho[i, min(j + 1, NW - 1)] - mu_y * rho[i, j]) / dx

                    advection_term = -(d_murho_x + d_murho_y)

                    # ── Euler update ──
                    rho_new[i, j] = rho[i, j] + dt * (diffusion_term + advection_term)

            # ── Enforce non-negativity and renormalize ──
            rho_new = np.maximum(rho_new, 0.0)
            total = rho_new.sum()
            if total > 0:
                rho_new /= total

            rho = rho_new

        if record_trajectory:
            trajectory.append(rho.copy())
            return rho, trajectory
        return rho

    def find_critical_density(self, rho: np.ndarray, threshold: float = 0.15) -> list[tuple[int, int]]:
        """
        Identify cells where density exceeds the critical tipping threshold.
        These are the "shock line" positions rendered in the UI.
        """
        indices = np.argwhere(rho > threshold)
        return [(int(i), int(j)) for i, j in indices]

    def compute_peak_density(self, rho: np.ndarray) -> float:
        """Return the maximum density value in the field."""
        return float(np.max(rho))

    def compute_entropy(self, rho: np.ndarray) -> float:
        """
        Compute the Shannon entropy of the density field.
        Higher entropy = more dispersed (good, less herding).
        """
        rho_flat = rho.flatten()
        rho_flat = rho_flat[rho_flat > 0]
        return float(-np.sum(rho_flat * np.log(rho_flat)))
