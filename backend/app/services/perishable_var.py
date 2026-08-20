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


# ── Spec-compliant class interface ────────────────────────────────────────────

class PerishableTracker:
    """
    Rot-aware routing utilities for perishable cargo.

    Encapsulates Arrhenius kinetic decay and the combined routing-penalty
    objective function used to choose the least-spoilage route.
    """

    # Universal gas constant (J / mol·K)
    _R: float = 8.314

    @staticmethod
    def calculate_kinetic_decay(
        temperature: float,
        activation_energy: float = 80_000,
        a_factor: float = 1e14,
    ) -> float:
        """
        Compute the Arrhenius kinetic decay rate constant k(T).

        Formula::

            k(T) = A * exp(-Ea / (R * T))

        where R = 8.314 J/(mol·K) is the universal gas constant and T is
        the absolute temperature in Kelvin (``temperature`` is expected in
        Kelvin; pass ``celsius + 273.15`` for Celsius inputs).

        Args:
            temperature:       Absolute temperature in Kelvin (K).
            activation_energy: Activation energy Ea in J/mol (default 80 000).
            a_factor:          Pre-exponential frequency factor A (default 1e14).

        Returns:
            Decay rate constant k  (units: 1/s, same as A's units).
        """
        import math
        return a_factor * math.exp(-activation_energy / (PerishableTracker._R * temperature))

    @staticmethod
    def compute_routing_penalty(
        freight_cost: float,
        decay_var: float,
        transit_co2: float,
        spoilage_prob: float,
        replacement_co2: float,
    ) -> float:
        """
        Combined routing-penalty objective for rot-aware path selection.

        Formula::

            penalty = freight_cost + decay_var + transit_co2
                      + spoilage_prob * replacement_co2

        Args:
            freight_cost:     Direct freight cost for the route (USD or index units).
            decay_var:        α-quantile VaR of Arrhenius decay along the route.
            transit_co2:      Expected Scope-3 CO₂e for in-transit emissions.
            spoilage_prob:    Probability of cargo spoilage (0–1).
            replacement_co2:  CO₂e cost of reproducing / replacing spoiled cargo.

        Returns:
            Scalar penalty — minimise across candidate routes to pick the
            least-cost, least-spoilage path.
        """
        return freight_cost + decay_var + transit_co2 + spoilage_prob * replacement_co2


# ── Module-level singleton ─────────────────────────────────────────────────────
perishable_tracker = PerishableTracker()
