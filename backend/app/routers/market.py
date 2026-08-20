"""
Market Router
==============
GET /api/market/impact     — Compute Kyle price impact for Q/D ratio
GET /api/market/volatility — Current GARCH lane volatility index
"""

from fastapi import APIRouter, Query
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from shared.constants import KYLE_LAMBDA, KYLE_GAMMA

router = APIRouter()


@router.get("/market/impact")
async def get_market_impact(
    q: float = Query(..., description="Quantity booked", ge=0),
    d: float = Query(..., description="Available lane depth", gt=0),
    p0: float = Query(1000.0, description="Base price per unit"),
    mode: str = Query("spot_booking", description="spot_booking or option_exercise"),
):
    """
    Compute Kyle/Grossman-Stiglitz price impact.
    P_lane(t) = P0 * (1 + λ * (Q/D)^γ)

    For option execution, Q_spot ≈ 0 so impact is minimal.
    """
    if mode == "option_exercise":
        # Options are pre-negotiated; no spot market impact
        effective_q = q * 0.05  # Only 5% leaks to spot
    else:
        effective_q = q

    ratio = effective_q / d if d > 0 else 0
    price_impacted = p0 * (1 + KYLE_LAMBDA * (ratio ** KYLE_GAMMA))
    price_delta_pct = ((price_impacted - p0) / p0) * 100

    return {
        "q_booked": q,
        "d_available": d,
        "price_base": p0,
        "price_impacted": round(price_impacted, 2),
        "price_delta_pct": round(price_delta_pct, 2),
        "lambda": KYLE_LAMBDA,
        "gamma": KYLE_GAMMA,
        "execution_mode": mode,
    }


@router.get("/market/volatility")
async def get_market_volatility():
    """
    Returns current GARCH(1,1) realized lane-rate volatility index.
    Mock data for initial scaffold.
    """
    # TODO: Implement GARCH volatility engine
    return {
        "sigma": 0.12,
        "index": 45.2,
        "model": "GARCH(1,1)",
        "window_seconds": 30,
    }
