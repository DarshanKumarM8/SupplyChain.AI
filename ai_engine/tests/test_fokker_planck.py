"""
Tests for Fokker-Planck 2D PDE Solver
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import numpy as np
import pytest
from models.fokker_planck import FokkerPlanckSolver


class TestFokkerPlanckSolver:

    def setup_method(self):
        self.solver = FokkerPlanckSolver(n_lanes=10, n_weeks=6)

    def test_initial_density_uniform_sums_to_one(self):
        """Uniform initial density must sum to 1.0."""
        rho = self.solver.initialize_density()
        assert abs(rho.sum() - 1.0) < 1e-10

    def test_initial_density_hotspot_sums_to_one(self):
        """Hotspot initial density must sum to 1.0."""
        rho = self.solver.initialize_density(hotspot_indices=[(0, 0), (1, 1)])
        assert abs(rho.sum() - 1.0) < 1e-10

    def test_initial_density_shape(self):
        """Density field must have correct shape."""
        rho = self.solver.initialize_density()
        assert rho.shape == (10, 6)

    def test_solve_preserves_density_normalization(self):
        """After solving, density must still sum to 1.0 (conservation)."""
        rho_0 = self.solver.initialize_density()
        drift = np.zeros((10, 6, 2))
        rho_final = self.solver.solve(rho_0, drift, diffusion=0.1, n_steps=50)
        assert abs(rho_final.sum() - 1.0) < 1e-6, f"Density sum = {rho_final.sum()}"

    def test_solve_non_negative(self):
        """Density must never go negative."""
        rho_0 = self.solver.initialize_density(hotspot_indices=[(0, 0)])
        drift = self.solver.compute_drift_field(
            np.random.default_rng(42).uniform(0, 1, (10, 6)), beta=0.8
        )
        rho_final = self.solver.solve(rho_0, drift, diffusion=0.2, n_steps=100)
        assert np.all(rho_final >= 0), "Negative density detected"

    def test_diffusion_spreads_density(self):
        """Pure diffusion (no drift) should spread a concentrated initial state."""
        rho_0 = self.solver.initialize_density(hotspot_indices=[(5, 3)])
        drift = np.zeros((10, 6, 2))
        rho_final = self.solver.solve(rho_0, drift, diffusion=0.5, n_steps=200)

        # After diffusion, peak should be lower than initial peak
        assert rho_final.max() < rho_0.max(), "Diffusion did not spread density"

    def test_entropy_increases_with_diffusion(self):
        """Shannon entropy should increase with diffusion (more dispersed)."""
        rho_0 = self.solver.initialize_density(hotspot_indices=[(0, 0)])
        drift = np.zeros((10, 6, 2))
        rho_final = self.solver.solve(rho_0, drift, diffusion=0.5, n_steps=200)

        entropy_before = self.solver.compute_entropy(rho_0)
        entropy_after = self.solver.compute_entropy(rho_final)
        assert entropy_after > entropy_before, "Entropy should increase with diffusion"

    def test_find_critical_density(self):
        """Critical density cells should be identified correctly."""
        rho = np.zeros((10, 6))
        rho[3, 2] = 0.5
        rho[7, 4] = 0.3
        critical = self.solver.find_critical_density(rho, threshold=0.15)
        assert (3, 2) in critical
        assert (7, 4) in critical
        assert len(critical) == 2

    def test_trajectory_recording(self):
        """Trajectory recording should return snapshots."""
        rho_0 = self.solver.initialize_density()
        drift = np.zeros((10, 6, 2))
        rho_final, trajectory = self.solver.solve(
            rho_0, drift, diffusion=0.1, n_steps=50, record_trajectory=True
        )
        assert len(trajectory) > 1, "Trajectory should have multiple snapshots"
        assert trajectory[-1].shape == (10, 6)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
