"""
Pricing Engine — Kyle Market Impact & GARCH Volatility
========================================================

Implements:
- Kyle/Grossman-Stiglitz price impact: P_lane(t) = P0 * (1 + λ * (Q/D)^γ)
- GARCH(1,1) realized lane-rate volatility index
"""

import numpy as np
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from shared.constants import KYLE_LAMBDA, KYLE_GAMMA, GARCH_OMEGA, GARCH_ALPHA, GARCH_BETA


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
