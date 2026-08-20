"""
Tests for PricingEngine and compute_stampede_index.

Run with:
    pytest backend/tests/test_pricing.py -v
"""

import math
import pytest

from app.services.pricing_engine import PricingEngine
from app.services.stampede_index import compute_stampede_index


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def engine() -> PricingEngine:
    return PricingEngine()


# ── PricingEngine.calculate_kyle_impact ───────────────────────────────────────

class TestCalculateKyleImpact:

    def test_zero_quantity_returns_base_price(self, engine: PricingEngine):
        """Q=0 means no demand pressure; impacted price must equal p0."""
        result = engine.calculate_kyle_impact(p0=1000.0, q=0.0, d=100.0)
        assert result == pytest.approx(1000.0)

    def test_formula_at_unit_ratio(self, engine: PricingEngine):
        """Q/D = 1 → P = P0 * (1 + λ * 1^γ) = P0 * (1 + λ)."""
        p0, lam, gam = 1000.0, 0.5, 1.5
        result = engine.calculate_kyle_impact(p0=p0, q=100.0, d=100.0,
                                              lambda_val=lam, gamma_val=gam)
        expected = p0 * (1.0 + lam * (1.0 ** gam))
        assert result == pytest.approx(expected)

    def test_impact_scales_with_q_over_d(self, engine: PricingEngine):
        """Higher Q/D ratio must produce a strictly higher impacted price."""
        low  = engine.calculate_kyle_impact(p0=1000.0, q=10.0,  d=100.0)
        mid  = engine.calculate_kyle_impact(p0=1000.0, q=50.0,  d=100.0)
        high = engine.calculate_kyle_impact(p0=1000.0, q=100.0, d=100.0)

        assert low < mid < high, (
            "Price impact must be strictly increasing with Q/D"
        )

    def test_impact_always_at_least_p0(self, engine: PricingEngine):
        """Impacted price can never be less than the base price (λ, γ > 0)."""
        for q in [0, 1, 50, 200]:
            result = engine.calculate_kyle_impact(p0=500.0, q=float(q), d=100.0)
            assert result >= 500.0

    def test_custom_lambda_gamma(self, engine: PricingEngine):
        """Explicit formula check with non-default λ and γ."""
        p0, q, d = 2000.0, 40.0, 80.0
        lam, gam = 0.8, 2.0
        ratio = q / d          # 0.5
        expected = p0 * (1.0 + lam * (ratio ** gam))   # 2000 * (1 + 0.8 * 0.25) = 2400
        result = engine.calculate_kyle_impact(p0=p0, q=q, d=d,
                                              lambda_val=lam, gamma_val=gam)
        assert result == pytest.approx(expected, rel=1e-9)

    def test_zero_depth_does_not_raise(self, engine: PricingEngine):
        """D=0 guard: should return p0 rather than raising ZeroDivisionError."""
        result = engine.calculate_kyle_impact(p0=1000.0, q=50.0, d=0.0)
        assert result == pytest.approx(1000.0)


# ── PricingEngine.simulate_garch_volatility ───────────────────────────────────

class TestSimulateGarchVolatility:

    def test_returns_float(self, engine: PricingEngine):
        """Return value must be a plain float."""
        result = engine.simulate_garch_volatility(
            current_sigma=0.1, return_shock=0.02
        )
        assert isinstance(result, float)

    def test_non_negative(self, engine: PricingEngine):
        """Volatility is a standard deviation — always non-negative."""
        for shock in [-0.5, 0.0, 0.5, 2.0]:
            result = engine.simulate_garch_volatility(
                current_sigma=0.1, return_shock=shock
            )
            assert result >= 0.0, f"Negative sigma for shock={shock}"

    def test_matches_garch_formula(self, engine: PricingEngine):
        """σ_{t+1} = sqrt(ω + α·r²_t + β·σ²_t)."""
        sigma, shock, omega, alpha, beta = 0.12, 0.03, 0.01, 0.10, 0.85
        expected = math.sqrt(omega + alpha * shock**2 + beta * sigma**2)
        result = engine.simulate_garch_volatility(
            current_sigma=sigma, return_shock=shock,
            omega=omega, alpha=alpha, beta=beta,
        )
        assert result == pytest.approx(expected, rel=1e-9)

    def test_larger_shock_increases_volatility(self, engine: PricingEngine):
        """A bigger return shock should produce a higher next-period σ."""
        small = engine.simulate_garch_volatility(current_sigma=0.1, return_shock=0.01)
        large = engine.simulate_garch_volatility(current_sigma=0.1, return_shock=0.50)
        assert large > small

    def test_zero_shock_converges_toward_long_run_vol(self, engine: PricingEngine):
        """With zero shocks GARCH decays toward long-run vol, not to zero."""
        sigma = 0.3
        for _ in range(50):
            sigma = engine.simulate_garch_volatility(
                current_sigma=sigma, return_shock=0.0,
                omega=0.01, alpha=0.1, beta=0.85,
            )
        long_run = math.sqrt(0.01 / (1 - 0.85))   # sqrt(ω/(1-β)) when shock=0
        assert sigma == pytest.approx(long_run, rel=0.01)


# ── compute_stampede_index ────────────────────────────────────────────────────

class TestComputeStampedeIndex:

    def test_returns_float(self):
        result = compute_stampede_index(0.5, 0.5, 0.5)
        assert isinstance(result, float)

    def test_exact_formula_mid_values(self):
        """Manually verify the formula at known inputs."""
        rho, v, s = 0.5, 0.4, 0.3
        expected = 100.0 * (0.45 * ((1 + rho) / 2) + 0.35 * v + 0.20 * s)
        result = compute_stampede_index(rho, v, s)
        assert result == pytest.approx(expected, rel=1e-9)

    def test_minimum_inputs_clamp_to_zero(self):
        """All-minimum inputs (rho=-1, v=0, s=0) → raw = 0 → clamped = 0."""
        result = compute_stampede_index(spearman_rho=-1.0, v_deplete=0.0, sigma_rate=0.0)
        assert result == pytest.approx(0.0)

    def test_maximum_inputs_clamp_to_100(self):
        """All-maximum inputs (rho=1, v=1, s=1) → raw = 100 → clamped = 100."""
        result = compute_stampede_index(spearman_rho=1.0, v_deplete=1.0, sigma_rate=1.0)
        assert result == pytest.approx(100.0)

    def test_extreme_positive_inputs_clamped(self):
        """Inputs far beyond [0,1] must still be clamped to ≤ 100.0."""
        result = compute_stampede_index(spearman_rho=1.0, v_deplete=1e6, sigma_rate=1e6)
        assert result <= 100.0

    def test_extreme_negative_inputs_clamped(self):
        """Extreme negative inputs must still be clamped to ≥ 0.0."""
        result = compute_stampede_index(spearman_rho=-1e6, v_deplete=-1e6, sigma_rate=-1e6)
        assert result >= 0.0

    def test_output_always_in_range(self):
        """Fuzz over a grid of valid inputs — all outputs must be in [0, 100]."""
        import itertools
        rhos  = [-1.0, -0.5, 0.0, 0.5, 1.0]
        vdeps = [0.0, 0.25, 0.5, 0.75, 1.0]
        sigs  = [0.0, 0.25, 0.5, 0.75, 1.0]

        for rho, v, s in itertools.product(rhos, vdeps, sigs):
            result = compute_stampede_index(rho, v, s)
            assert 0.0 <= result <= 100.0, (
                f"Out-of-range result {result} for inputs rho={rho}, v={v}, s={s}"
            )

    def test_monotone_in_spearman_rho(self):
        """Higher ρ (more herd behaviour) should produce a higher index."""
        low  = compute_stampede_index(spearman_rho=-0.5, v_deplete=0.5, sigma_rate=0.5)
        high = compute_stampede_index(spearman_rho=0.5,  v_deplete=0.5, sigma_rate=0.5)
        assert high > low
