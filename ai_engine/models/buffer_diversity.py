"""
Buffer-Diversity Scorer
========================

Computes per-firm buffer diversity to detect synchronized inventory positions.
D_buffer(i) = 1 - cos_sim(b_i, mean(b_{-i}))

Low diversity -> the firm holds the same buffers as everyone else -> high stampede risk.
"""

import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.constants import BUFFER_DIVERSITY_THRESHOLD, PHASED_RELEASE_WEEKS


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def compute_buffer_diversity(firm_buffers: dict[str, np.ndarray]) -> dict[str, float]:
    """
    Compute buffer-diversity score for each firm.

    D_buffer(i) = 1 - cos_sim(b_i, mean(b_{-i}))

    Args:
        firm_buffers: {firm_id: SKU-level buffer vector as np.ndarray}

    Returns:
        {firm_id: d_buffer score}
    """
    firm_ids = list(firm_buffers.keys())
    n_firms = len(firm_ids)

    if n_firms < 2:
        # With fewer than 2 firms, diversity is undefined; return max diversity
        return {fid: 1.0 for fid in firm_ids}

    # Stack all buffer vectors into a matrix for efficient computation
    buffer_matrix = np.array([firm_buffers[fid] for fid in firm_ids])  # (n_firms, n_skus)
    total_sum = buffer_matrix.sum(axis=0)  # Sum of all buffer vectors

    diversity_scores = {}
    for idx, firm_id in enumerate(firm_ids):
        b_i = buffer_matrix[idx]

        # Mean of all *other* firms' buffer vectors: (total_sum - b_i) / (n_firms - 1)
        b_bar_neg_i = (total_sum - b_i) / (n_firms - 1)

        cos_sim = cosine_similarity(b_i, b_bar_neg_i)
        d_buffer = 1.0 - cos_sim

        diversity_scores[firm_id] = round(d_buffer, 4)

    return diversity_scores


def assign_phased_release(
    diversity_scores: dict[str, float],
    release_weeks: list[str] = None,
) -> dict[str, list[str]]:
    """
    Assign firms to phased release tranches based on buffer diversity.
    Low-diversity firms (most synchronized) release first to desynchronize.

    Args:
        diversity_scores: {firm_id: d_buffer}
        release_weeks: e.g., ["W1", "W3", "W5"]

    Returns:
        {week: [firm_ids]}
    """
    if release_weeks is None:
        release_weeks = list(PHASED_RELEASE_WEEKS)

    # Sort firms by d_buffer ascending (lowest diversity = most synchronized, release first)
    sorted_firms = sorted(diversity_scores.items(), key=lambda x: x[1])
    firm_ids_sorted = [fid for fid, _ in sorted_firms]

    n_firms = len(firm_ids_sorted)
    n_weeks = len(release_weeks)

    # Split into roughly equal groups
    schedule = {}
    chunk_size = max(1, n_firms // n_weeks)
    for week_idx, week in enumerate(release_weeks):
        start = week_idx * chunk_size
        if week_idx == n_weeks - 1:
            # Last week gets all remaining firms
            schedule[week] = firm_ids_sorted[start:]
        else:
            schedule[week] = firm_ids_sorted[start:start + chunk_size]

    return schedule


def classify_risk(diversity_scores: dict[str, float], threshold: float = BUFFER_DIVERSITY_THRESHOLD) -> dict[str, str]:
    """
    Classify firms into risk categories based on buffer diversity.

    Returns:
        {firm_id: "high_risk" | "medium_risk" | "low_risk"}
    """
    classifications = {}
    for firm_id, score in diversity_scores.items():
        if score < threshold:
            classifications[firm_id] = "high_risk"
        elif score < threshold * 2:
            classifications[firm_id] = "medium_risk"
        else:
            classifications[firm_id] = "low_risk"
    return classifications
