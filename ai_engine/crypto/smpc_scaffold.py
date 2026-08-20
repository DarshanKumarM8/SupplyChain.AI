"""
SMPC Scaffold -- Private Set Intersection for Quiet Coalitions
===============================================================

Mock implementation of PSI (Private Set Intersection) and SMPC
(Secure Multi-Party Computation) for the "Quiet Coalitions" demo.

In production: uses proper cryptographic protocols.
For hackathon MVP: simulates the intersection logic with epsilon-differential privacy noise.
"""

import hashlib
import numpy as np
from typing import Optional
from datetime import datetime, timezone


class SMPCScaffold:
    """Mock PSI/SMPC for cross-firm capacity attestation."""

    def __init__(self, epsilon: float = 1.0):
        """
        Args:
            epsilon: Differential privacy parameter (lower = more private)
        """
        self.epsilon = epsilon

    def hash_bottleneck_set(self, node_ids: list[str], salt: str = "") -> set[str]:
        """
        Hash a firm's set of bottleneck node IDs for PSI.
        In production, this would use oblivious transfer or Diffie-Hellman PSI.
        """
        hashed = set()
        for nid in node_ids:
            h = hashlib.sha256(f"{salt}:{nid}".encode()).hexdigest()[:16]
            hashed.add(h)
        return hashed

    def compute_intersection(
        self,
        firm_sets: dict[str, list[str]],
        salt: str = "supplychainai_psi",
    ) -> dict:
        """
        Compute the intersection cardinality of bottleneck node sets
        across multiple firms, with epsilon-DP noise.

        Args:
            firm_sets: {firm_id: [bottleneck_node_ids]}

        Returns:
            {
                "intersection_cardinality": int (noised),
                "participating_firms": int,
                "dp_noise_added": float,
                "raw_intersection": list[str]  # only in mock mode
            }
        """
        if not firm_sets:
            return {
                "intersection_cardinality": 0,
                "participating_firms": 0,
                "dp_noise_added": 0.0,
                "raw_intersection": [],
            }

        # 1. Hash each firm's node set
        hashed_sets = {}
        for firm_id, node_ids in firm_sets.items():
            hashed_sets[firm_id] = self.hash_bottleneck_set(node_ids, salt)

        # 2. Compute set intersection across all firms
        all_sets = list(hashed_sets.values())
        intersection = all_sets[0]
        for s in all_sets[1:]:
            intersection = intersection & s

        raw_cardinality = len(intersection)

        # 3. Add Laplace noise calibrated to epsilon: noise ~ Laplace(1/epsilon)
        rng = np.random.default_rng()
        noise = rng.laplace(loc=0, scale=1.0 / self.epsilon)
        noised_cardinality = max(0, int(round(raw_cardinality + noise)))

        # 4. Reverse-hash to get original node IDs (mock mode only)
        # In production, we would NEVER reveal this
        raw_node_sets = list(firm_sets.values())
        raw_intersection_nodes = set(raw_node_sets[0])
        for ns in raw_node_sets[1:]:
            raw_intersection_nodes = raw_intersection_nodes & set(ns)

        return {
            "intersection_cardinality": noised_cardinality,
            "participating_firms": len(firm_sets),
            "dp_noise_added": round(float(noise), 4),
            "raw_intersection": sorted(list(raw_intersection_nodes)),
        }

    def attest_capacity(self, firm_id: str, lane_id: str, has_capacity: bool) -> dict:
        """
        Binary capacity attestation: a firm attests whether it has available
        capacity on a given lane, without revealing exact volumes.

        Returns commitment hash that can be verified later.
        """
        nonce = np.random.default_rng().integers(1_000_000_000)
        commitment = hashlib.sha256(
            f"{firm_id}:{lane_id}:{has_capacity}:{nonce}".encode()
        ).hexdigest()
        return {
            "firm_id": firm_id,
            "lane_id": lane_id,
            "commitment": commitment,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "verified": False,
        }

    def verify_attestation(
        self,
        firm_id: str,
        lane_id: str,
        has_capacity: bool,
        nonce: int,
        commitment: str,
    ) -> bool:
        """Verify a capacity attestation against its commitment hash."""
        expected = hashlib.sha256(
            f"{firm_id}:{lane_id}:{has_capacity}:{nonce}".encode()
        ).hexdigest()
        return expected == commitment

    def aggregate_capacity_attestations(
        self,
        attestations: list[dict],
    ) -> dict:
        """
        Aggregate binary attestations to compute total available capacity
        on a lane across firms, with DP noise for privacy.
        """
        total_yes = sum(1 for a in attestations if "has_capacity" in a and a["has_capacity"])
        total_no = len(attestations) - total_yes

        # Add Laplace noise to the count
        rng = np.random.default_rng()
        noise = rng.laplace(loc=0, scale=1.0 / self.epsilon)
        noised_yes = max(0, int(round(total_yes + noise)))

        return {
            "lane_id": attestations[0]["lane_id"] if attestations else "unknown",
            "firms_with_capacity": noised_yes,
            "total_firms": len(attestations),
            "dp_epsilon": self.epsilon,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
