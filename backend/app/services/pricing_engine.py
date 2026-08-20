"""
Pricing Engine — Kyle Market Impact & GARCH Volatility
========================================================

Implements:
- Kyle/Grossman-Stiglitz price impact: P_lane(t) = P0 * (1 + λ * (Q/D)^γ)
- GARCH(1,1) realized lane-rate volatility index
"""

import math
import sys
import os

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from shared.constants import KYLE_LAMBDA, KYLE_GAMMA, GARCH_OMEGA, GARCH_ALPHA, GARCH_BETA


# ── High-level service class (primary interface) ─────────────────────────────

class PricingEngine:
    """
    Stateless pricing utilities for lane-rate impact and volatility modelling.

    Methods accept all parameters explicitly so callers can override the
    shared default constants at call time without patching global state.
    """

    @staticmethod
    def calculate_kyle_impact(
        p0: float,
        q: float,
        d: float,
        lambda_val: float = 0.5,
        gamma_val: float = 1.5,
    ) -> float:
        """
        Kyle/Grossman-Stiglitz price impact formula.

        P_lane = P0 * (1 + lambda_val * (Q / D) ** gamma_val)

        Args:
            p0:         Base (pre-impact) lane price.
            q:          Quantity being booked (demand).
            d:          Available lane depth (supply).
            lambda_val: Market-impact coefficient λ (default 0.5).
            gamma_val:  Curvature exponent γ (default 1.5).

        Returns:
            Impacted lane price as a float.
        """
        ratio = q / d if d > 0 else 0.0
        return p0 * (1.0 + lambda_val * (ratio ** gamma_val))

    @staticmethod
    def simulate_garch_volatility(
        current_sigma: float,
        return_shock: float,
        omega: float = 0.01,
        alpha: float = 0.1,
        beta: float = 0.85,
    ) -> float:
        """
        Single GARCH(1,1) variance update step.

        σ²_{t+1} = ω + α * r²_t + β * σ²_t

        Args:
            current_sigma: Conditional volatility at time *t* (σ_t, not σ²_t).
            return_shock:  Observed return r_t.
            omega:         Long-run variance weight ω (default 0.01).
            alpha:         ARCH coefficient α (default 0.1).
            beta:          GARCH coefficient β (default 0.85).

        Returns:
            Updated conditional volatility σ_{t+1}.
        """
        sigma_sq_t = current_sigma ** 2
        sigma_sq_next = omega + alpha * (return_shock ** 2) + beta * sigma_sq_t
        return math.sqrt(sigma_sq_next)


# ── Module-level singleton ────────────────────────────────────────────────────
pricing_engine = PricingEngine()


# ── Legacy helpers (kept for backwards compatibility) ─────────────────────────

def kyle_price_impact(q_booked: float, d_available: float, p0: float = 1000.0) -> dict:
    """
    Compute Kyle price impact.
    P_lane(t) = P0 * (1 + λ * (Q/D)^γ)
    """
    ratio = q_booked / d_available if d_available > 0 else 0
    p_impacted = p0 * (1 + KYLE_LAMBDA * (ratio ** KYLE_GAMMA))
    return {
        "price_base": p0,
        "price_impacted": p_impacted,
        "price_delta_pct": ((p_impacted - p0) / p0) * 100,
        "q_d_ratio": ratio,
    }


class GARCHVolatility:
    """GARCH(1,1) model for lane-rate volatility estimation."""

    def __init__(self):
        self.sigma_sq = GARCH_OMEGA / (1 - GARCH_ALPHA - GARCH_BETA)  # Unconditional variance
        self.returns: list[float] = []

    def update(self, return_t: float) -> float:
        """
        Update GARCH(1,1) with a new return observation.
        σ²_{t+1} = ω + α·r²_t + β·σ²_t

        Returns current conditional volatility σ_t.
        """
        self.returns.append(return_t)
        self.sigma_sq = GARCH_OMEGA + GARCH_ALPHA * (return_t ** 2) + GARCH_BETA * self.sigma_sq
        return np.sqrt(self.sigma_sq)

    @property
    def current_volatility(self) -> float:
        return np.sqrt(self.sigma_sq)
