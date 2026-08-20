"""
Buffer-Diversity Scorer
========================

Computes per-firm buffer diversity to detect synchronized inventory positions.
D_buffer(i) = 1 - cos_sim(b_i, mean(b_{-i}))

Low diversity → the firm holds the same buffers as everyone else → high stampede risk.
"""

import numpy as np


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
    # TODO: Implement the exact formula
    # For each firm i:
    #   1. Compute b_bar_{-i} = mean of all other firms' buffer vectors
    #   2. D_buffer(i) = 1 - cosine_similarity(b_i, b_bar_{-i})
    raise NotImplementedError("Buffer diversity computation not yet implemented")


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
        release_weeks = ["W1", "W3", "W5"]

    # TODO: Implement phased release assignment
    # Sort firms by d_buffer ascending (lowest diversity first)
    # Split into len(release_weeks) equal groups
    # Assign each group to a release week
    raise NotImplementedError("Phased release assignment not yet implemented")
