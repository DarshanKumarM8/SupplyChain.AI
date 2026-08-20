"""
SupplyChainAI Index — Server-Side Computation
================================================

Computes the SupplyChainAI Index identically for both naive and AI panels.
S_t = 100 × [w1·(1+ρ_Spearman)/2 + w2·v_deplete + w3·σ_rate]
"""

import numpy as np
try:
    from scipy.stats import spearmanr
except ImportError:
    spearmanr = None

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from shared.constants import INDEX_W1_SPEARMAN, INDEX_W2_DEPLETION, INDEX_W3_VOLATILITY


def compute_spearman_correlation(order_vectors: np.ndarray) -> float:
    """
    Compute mean pairwise Spearman rank correlation of order vectors across firms.

    Args:
        order_vectors: (N_firms, N_lanes) matrix of order placements

    Returns:
        Mean Spearman ρ ∈ [-1, 1]
    """
    n_firms = order_vectors.shape[0]
    if n_firms < 2:
        return 0.0

    correlations = []
    for i in range(n_firms):
        for j in range(i + 1, n_firms):
            rho, _ = spearmanr(order_vectors[i], order_vectors[j])
            if not np.isnan(rho):
                correlations.append(rho)

    return float(np.mean(correlations)) if correlations else 0.0


def compute_depletion_velocity(capacity_deltas: np.ndarray, capacity_maxes: np.ndarray) -> float:
    """
    Normalized capacity depletion velocity of shared bottleneck nodes.
    v_deplete = min(1, mean(-ΔC_k/Δt / C_k_max))
    """
    if len(capacity_deltas) == 0 or len(capacity_maxes) == 0:
        return 0.0

    velocities = -capacity_deltas / np.maximum(capacity_maxes, 1e-8)
    return float(min(1.0, np.mean(np.clip(velocities, 0, None))))


def compute_stampede_index(
    spearman_rho: float,
    v_deplete: float,
    sigma_rate: float,
) -> float:
    """
    Compute the SupplyChainAI Stampede Index.

    Formula:
        S_t = 100 * [w1 * ((1 + spearman_rho) / 2) + w2 * v_deplete + w3 * sigma_rate]

    Static weights:
        w1 = 0.45  (Spearman rank-correlation herd component)
        w2 = 0.35  (bottleneck depletion-velocity component)
        w3 = 0.20  (lane-rate volatility component)

    Args:
        spearman_rho: Mean pairwise Spearman ρ of firm order vectors, in [-1, 1].
        v_deplete:    Normalized capacity depletion velocity of bottleneck nodes, in [0, 1].
        sigma_rate:   Normalized lane-rate volatility, in [0, 1].

    Returns:
        S_t clamped to [0.0, 100.0].
    """
    raw = 100.0 * (
        0.45 * ((1 + spearman_rho) / 2)
        + 0.35 * v_deplete
        + 0.20 * sigma_rate
    )
    return min(100.0, max(0.0, raw))
