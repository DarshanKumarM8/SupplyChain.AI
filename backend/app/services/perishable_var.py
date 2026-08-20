"""
Perishable VaR — Rot-Aware Routing with Arrhenius Decay
=========================================================

Implements the perishable cargo optimization objective:
min_route [Cost_freight(r) + VaR_α(Decay_r) + E[CO2e_transit + I(Spoil) * CO2e_reproduce]]
"""

import numpy as np
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from shared.constants import (
    ARRHENIUS_A, ARRHENIUS_EA, GAS_CONSTANT_R, DECAY_VAR_ALPHA,
    CO2E_REPRODUCE_MULTIPLIER,
)


def arrhenius_decay_rate(temperature_c: float) -> float:
    """
    Compute kinetic decay rate constant using Arrhenius equation.
    k(T) = A * exp(-Ea / (R * T_kelvin))
    """
    t_kelvin = temperature_c + 273.15
    return ARRHENIUS_A * np.exp(-ARRHENIUS_EA / (GAS_CONSTANT_R * t_kelvin))


def compute_decay_var(temperature_profile: list[float], transit_hours: float, alpha: float = DECAY_VAR_ALPHA) -> float:
    """
    Compute the α-quantile Value-at-Risk of kinetic decay
    integrated along the temperature profile of a route.

    Args:
        temperature_profile: list of temperatures (°C) along the route
        transit_hours: total transit time in hours
        alpha: VaR quantile (e.g., 0.05 for 5th percentile)

    Returns:
        Estimated decay VaR (higher = more spoilage risk)
    """
    # TODO: Implement proper VaR calculation
    # 1. Integrate Arrhenius decay rate along temperature profile
    # 2. Add stochastic temperature variance
    # 3. Compute alpha-quantile of decay distribution
    raise NotImplementedError("Decay VaR not yet implemented")


def compute_routing_objective(
    freight_cost: float,
    decay_var: float,
    co2e_transit: float,
    spoilage_prob: float,
    co2e_reproduce: float,
) -> float:
    """
    Combined objective function for rot-aware routing.
    Objective = freight_cost + decay_var + E[co2e_transit + I(spoil) * co2e_reproduce]
    """
    expected_carbon = co2e_transit + spoilage_prob * co2e_reproduce * CO2E_REPRODUCE_MULTIPLIER
    return freight_cost + decay_var + expected_carbon
