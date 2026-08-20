"""
Market Router
==============
GET /api/market/impact     — Compute Kyle price impact for Q/D ratio
GET /api/market/volatility — Current GARCH lane volatility index
"""

from fastapi import APIRouter, Query

from app.services.pricing_engine import pricing_engine, GARCHVolatility

router = APIRouter()

# Module-level GARCH state for the volatility endpoint
_garch = GARCHVolatility()


@router.get("/market/impact")
async def get_market_impact(
    q: float = Query(..., description="Quantity booked", ge=0),
    d: float = Query(..., description="Available lane depth", gt=0),
    p0: float = Query(1000.0, description="Base price per unit"),
    lambda_val: float = Query(0.5, description="Kyle impact coefficient λ", gt=0),
    gamma_val: float = Query(1.5, description="Kyle curvature exponent γ", gt=0),
    mode: str = Query("spot_booking", description="spot_booking or option_exercise"),
):
    """
    Compute Kyle/Grossman-Stiglitz price impact.

    P_lane(t) = P0 * (1 + λ * (Q/D)^γ)

    For option execution, Q_spot ≈ 0 so impact is minimal.
    """
    # Options are pre-negotiated; only 5% of Q leaks to spot
    effective_q = q * 0.05 if mode == "option_exercise" else q

    price_impacted = pricing_engine.calculate_kyle_impact(
        p0=p0, q=effective_q, d=d,
        lambda_val=lambda_val, gamma_val=gamma_val,
    )
    price_delta_pct = ((price_impacted - p0) / p0) * 100

    return {
        "q_booked": q,
        "d_available": d,
        "price_base": p0,
        "price_impacted": round(price_impacted, 2),
        "price_delta_pct": round(price_delta_pct, 2),
        "lambda": lambda_val,
        "gamma": gamma_val,
        "execution_mode": mode,
    }


@router.get("/market/volatility")
async def get_market_volatility(
    return_shock: float = Query(0.0, description="Latest observed lane-rate return (0 = no new data)"),
):
    """
    Return current GARCH(1,1) conditional lane-rate volatility.

    Optionally accepts a ``return_shock`` query parameter to advance the
    GARCH state with a new observed return before reading the estimate.
    """
    current_sigma = _garch.current_volatility

    if return_shock != 0.0:
        current_sigma = _garch.update(return_shock)

    # Also demonstrate the stateless PricingEngine method (one-shot update)
    updated_sigma = pricing_engine.simulate_garch_volatility(
        current_sigma=current_sigma,
        return_shock=return_shock,
    )

    return {
        "sigma": round(current_sigma, 6),
        "sigma_next": round(updated_sigma, 6),
        "index": round(current_sigma * 100, 2),
        "model": "GARCH(1,1)",
        "window_seconds": 30,
    }
