"""
Tests for Stampede Index Computation & Reflex Agent
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import numpy as np
import pytest
from agents.reflex import ReflexAgent


class TestStampedeIndex:

    def setup_method(self):
        self.agent = ReflexAgent(n_lanes=10, n_weeks=6)

    def test_index_in_range(self):
        """Stampede Index must always be in [0, 100]."""
        rng = np.random.default_rng(42)
        for _ in range(20):
            n_firms = rng.integers(3, 20)
            order_vectors = rng.uniform(0, 1, (n_firms, 10))
            capacity_deltas = rng.uniform(-1000, 0, 5)
            capacity_maxes = rng.uniform(1000, 5000, 5)
            rate_vol = rng.uniform(0, 1)

            index = self.agent.compute_stampede_index(
                order_vectors, capacity_deltas, capacity_maxes, rate_vol
            )
            assert 0 <= index <= 100, f"Index {index} out of [0, 100] range"

    def test_high_correlation_high_index(self):
        """Highly correlated orders should produce a high index."""
        # All firms place identical orders (perfect correlation)
        base = np.array([10, 8, 6, 4, 2, 1, 0.5, 0.2, 0.1, 0.05])
        order_vectors = np.tile(base, (10, 1)) + np.random.default_rng(42).normal(0, 0.01, (10, 10))
        capacity_deltas = np.array([-3000, -2500, -2000, -1500, -1000])
        capacity_maxes = np.array([5000, 4000, 3000, 2000, 1500])
        rate_vol = 0.9

        index = self.agent.compute_stampede_index(
            order_vectors, capacity_deltas, capacity_maxes, rate_vol
        )
        assert index > 60, f"High-correlation scenario should produce high index, got {index}"

    def test_low_correlation_low_index(self):
        """Diversified orders should produce a lower index."""
        rng = np.random.default_rng(42)
        order_vectors = rng.dirichlet(np.ones(10), size=10)  # Diverse allocations
        capacity_deltas = np.array([-200, -100, -150, -50, -300])
        capacity_maxes = np.array([5000, 4000, 3000, 2000, 1500])
        rate_vol = 0.1

        index = self.agent.compute_stampede_index(
            order_vectors, capacity_deltas, capacity_maxes, rate_vol
        )
        assert index < 50, f"Low-correlation scenario should produce low index, got {index}"

    def test_naive_higher_than_ai(self):
        """In the Kaohsiung scenario, naive index should be higher than AI index."""
        import json
        scenario_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'scenarios', 'kaohsiung_typhoon.json')
        if not os.path.exists(scenario_path):
            pytest.skip("Scenario file not generated yet")

        with open(scenario_path) as f:
            scenario = json.load(f)

        decision = self.agent.decide(
            event_id="evt_test",
            graph=scenario,
            beta=0.6,
            shock_intensity=0.85,
        )
        assert decision.stampede_index_before > decision.stampede_index_after, \
            f"Naive ({decision.stampede_index_before}) should be > AI ({decision.stampede_index_after})"

    def test_dephasing_allocations_sum_to_one(self):
        """De-phasing allocation percentages should approximately sum to 1.0."""
        rng = np.random.default_rng(42)
        density = rng.dirichlet(np.ones(60)).reshape(10, 6)
        schedule = self.agent.optimize_dephasing(density)

        total_pct = sum(v["allocation_pct"] for v in schedule.allocations.values())
        assert abs(total_pct - 1.0) < 0.05, f"Allocations sum to {total_pct}, expected ~1.0"

    def test_entropy_budget_not_overspent(self):
        """Entropy budget spent must not exceed the total budget."""
        rng = np.random.default_rng(42)
        density = rng.dirichlet(np.ones(60)).reshape(10, 6)
        entropy = self.agent.allocate_entropy(3_100_000, density, rng)

        assert entropy.spent <= entropy.total_budget * 1.01, \
            f"Entropy overspent: {entropy.spent} > {entropy.total_budget}"

    def test_single_firm_index(self):
        """Index should work with a single firm (edge case)."""
        order_vectors = np.array([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]])
        index = self.agent.compute_stampede_index(
            order_vectors,
            np.array([-100]),
            np.array([1000]),
            0.5,
        )
        assert 0 <= index <= 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
