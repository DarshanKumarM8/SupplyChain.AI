"""
Tests for Buffer-Diversity Scorer
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import numpy as np
import pytest
from models.buffer_diversity import compute_buffer_diversity, assign_phased_release


class TestBufferDiversity:

    def test_identical_buffers_have_zero_diversity(self):
        """Firms with identical buffers should have ~0 diversity."""
        buffer = np.array([0.5, 0.3, 0.2])
        firm_buffers = {
            "firm_A": buffer.copy(),
            "firm_B": buffer.copy(),
            "firm_C": buffer.copy(),
        }
        scores = compute_buffer_diversity(firm_buffers)
        for score in scores.values():
            assert score < 0.05, f"Identical buffers should have near-zero diversity, got {score}"

    def test_orthogonal_buffers_have_high_diversity(self):
        """Firms with orthogonal buffers should have high diversity."""
        firm_buffers = {
            "firm_A": np.array([1.0, 0.0, 0.0]),
            "firm_B": np.array([0.0, 1.0, 0.0]),
            "firm_C": np.array([0.0, 0.0, 1.0]),
        }
        scores = compute_buffer_diversity(firm_buffers)
        for score in scores.values():
            assert score > 0.3, f"Orthogonal buffers should have high diversity, got {score}"

    def test_diversity_in_zero_one_range(self):
        """All diversity scores should be in [0, 1]."""
        rng = np.random.default_rng(42)
        firm_buffers = {f"firm_{i}": rng.dirichlet(np.ones(10)) for i in range(10)}
        scores = compute_buffer_diversity(firm_buffers)
        for fid, score in scores.items():
            assert 0.0 <= score <= 1.0, f"{fid} has score {score} outside [0, 1]"

    def test_single_firm_returns_max_diversity(self):
        """Single firm should get max diversity (undefined peer comparison)."""
        scores = compute_buffer_diversity({"firm_A": np.array([0.5, 0.5])})
        assert scores["firm_A"] == 1.0

    def test_phased_release_assigns_all_firms(self):
        """All firms should be assigned to a release week."""
        scores = {"A": 0.1, "B": 0.3, "C": 0.5, "D": 0.7, "E": 0.9, "F": 0.2}
        schedule = assign_phased_release(scores)
        all_assigned = []
        for week, firms in schedule.items():
            all_assigned.extend(firms)
        assert set(all_assigned) == set(scores.keys()), "Not all firms assigned"

    def test_low_diversity_firms_release_first(self):
        """Firms with lowest diversity should be in W1 (earliest release)."""
        scores = {"A": 0.1, "B": 0.8, "C": 0.05, "D": 0.9, "E": 0.15, "F": 0.7}
        schedule = assign_phased_release(scores)
        # W1 should contain the lowest-diversity firms
        w1_firms = set(schedule.get("W1", []))
        assert "C" in w1_firms or "A" in w1_firms, f"Low-diversity firms not in W1: {w1_firms}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
