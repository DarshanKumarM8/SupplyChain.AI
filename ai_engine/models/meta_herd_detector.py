"""
Meta-Herd Cohort Detector
===========================

Detects when multiple firms adopt identical anti-herding (de-phasing) strategies,
creating a second-order stampede. Triggers entropy budget reallocation.

Detection: if >=3 firms have de-phasing pattern cosine similarity > 0.85,
a meta-herd is forming and the entropy budget must fire.
"""

import numpy as np
from itertools import combinations
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.constants import META_HERD_COSINE_THRESHOLD


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two vectors."""
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


class MetaHerdDetector:
    """Detects second-order herding among anti-herding strategies."""

    def __init__(
        self,
        similarity_threshold: float = META_HERD_COSINE_THRESHOLD,
        min_cohort_size: int = 3,
    ):
        self.similarity_threshold = similarity_threshold
        self.min_cohort_size = min_cohort_size

    def detect(self, dephasing_vectors: dict[str, np.ndarray]) -> dict:
        """
        Detect meta-herd formation among firms' de-phasing strategies.

        Args:
            dephasing_vectors: {firm_id: de-phasing allocation vector}

        Returns:
            {
                "meta_herd_detected": bool,
                "cohort_size": int,
                "cohort_firms": list[str],
                "max_similarity": float
            }
        """
        firm_ids = list(dephasing_vectors.keys())
        n_firms = len(firm_ids)

        if n_firms < self.min_cohort_size:
            return {
                "meta_herd_detected": False,
                "cohort_size": 0,
                "cohort_firms": [],
                "max_similarity": 0.0,
            }

        # Compute pairwise cosine similarities
        sim_matrix = np.zeros((n_firms, n_firms))
        for i in range(n_firms):
            for j in range(i + 1, n_firms):
                sim = _cosine_similarity(
                    dephasing_vectors[firm_ids[i]],
                    dephasing_vectors[firm_ids[j]],
                )
                sim_matrix[i, j] = sim
                sim_matrix[j, i] = sim

        # Find the largest clique where all pairwise similarities > threshold
        # Use greedy approach: start from highest-similarity pair, grow the cohort
        best_cohort = []
        best_max_sim = 0.0

        # Build adjacency list of "similar" firms
        similar_pairs = {}
        for i in range(n_firms):
            similar_pairs[i] = set()
            for j in range(n_firms):
                if i != j and sim_matrix[i, j] > self.similarity_threshold:
                    similar_pairs[i].add(j)

        # Greedy clique finding: for each node, try to build a maximal clique
        for start in range(n_firms):
            if len(similar_pairs[start]) < self.min_cohort_size - 1:
                continue

            cohort = {start}
            candidates = set(similar_pairs[start])

            for candidate in sorted(candidates, key=lambda c: -sim_matrix[start, c]):
                # Check if candidate is similar to ALL current cohort members
                is_similar_to_all = all(
                    sim_matrix[candidate, member] > self.similarity_threshold
                    for member in cohort
                )
                if is_similar_to_all:
                    cohort.add(candidate)

            if len(cohort) > len(best_cohort):
                best_cohort = list(cohort)
                # Compute max similarity within the cohort
                cohort_sims = [
                    sim_matrix[i, j]
                    for i, j in combinations(cohort, 2)
                ]
                best_max_sim = max(cohort_sims) if cohort_sims else 0.0

        detected = len(best_cohort) >= self.min_cohort_size
        cohort_firm_ids = [firm_ids[i] for i in best_cohort]

        return {
            "meta_herd_detected": detected,
            "cohort_size": len(best_cohort),
            "cohort_firms": sorted(cohort_firm_ids),
            "max_similarity": round(best_max_sim, 4),
        }
