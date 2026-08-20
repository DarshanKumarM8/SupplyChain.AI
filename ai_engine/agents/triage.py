"""
Triage Agent -- Buffer-Diversity Scoring & Blast Radius Analysis
================================================================

Responsibilities:
- Compute blast radius (BFS over supply graph with contingent edges)
- Calculate buffer-diversity scores per firm: D_buffer(i) = 1 - cos_sim(b_i, mean(b_{-i}))
- Generate phased release schedule (W1, W3, W5) based on diversity scores
- Report graph mobility score across dynamic topology ensemble

Key Formula:
  D_buffer(i) = 1 - (b_i . mean(b_{-i})) / (||b_i||_2 . ||mean(b_{-i})||_2)

Output: TriageReport schema (see shared/api_schemas/triage_report.json)
"""

import numpy as np
from collections import deque
from dataclasses import dataclass, field
from typing import Optional
import sys
import os

# Add parent to path for shared imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.constants import (
    BUFFER_DIVERSITY_THRESHOLD,
    PHASED_RELEASE_WEEKS,
)
from ai_engine.models.buffer_diversity import compute_buffer_diversity, assign_phased_release
from ai_engine.models.graph_mobility import GraphMobilityScorer


@dataclass
class BlastRadius:
    direct_affected: int
    tier2_cascade: int
    total_exposed: int


@dataclass
class BufferDiversityScore:
    firm_id: str
    d_buffer: float


@dataclass
class TriageReport:
    event_id: str
    blast_radius: BlastRadius
    graph_mobility_score: float
    buffer_diversity_scores: list[BufferDiversityScore]
    phased_release_schedule: dict[str, list[str]]
    contingent_edges_activated: int
    topology_ensemble_count: int

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "blast_radius": {
                "direct_affected": self.blast_radius.direct_affected,
                "tier2_cascade": self.blast_radius.tier2_cascade,
                "total_exposed": self.blast_radius.total_exposed,
            },
            "graph_mobility_score": round(self.graph_mobility_score, 2),
            "buffer_diversity_scores": [
                {"firm_id": s.firm_id, "d_buffer": round(s.d_buffer, 2)}
                for s in self.buffer_diversity_scores
            ],
            "phased_release_schedule": self.phased_release_schedule,
            "contingent_edges_activated": self.contingent_edges_activated,
            "topology_ensemble_count": self.topology_ensemble_count,
        }


class TriageAgent:
    """
    Triage Agent: assesses disruption impact, scores buffer diversity,
    and generates phased release schedules to prevent synchronized depletion.
    """

    def __init__(self, graph: dict):
        """
        Args:
            graph: Supply network graph dict matching shared/graph_schema/supply_network.json
        """
        self.graph = graph
        self.nodes = {n["id"]: n for n in graph.get("nodes", [])}
        self.edges = graph.get("edges", [])

        # Build adjacency lists for BFS
        self._adjacency = {}  # node_id -> [(neighbor_id, edge)]
        self._contingent_edges = []
        for edge in self.edges:
            src = edge["source"]
            tgt = edge["target"]
            if edge.get("is_contingent", False):
                self._contingent_edges.append(edge)
            else:
                self._adjacency.setdefault(src, []).append((tgt, edge))
                # Also add reverse for undirected BFS
                self._adjacency.setdefault(tgt, []).append((src, edge))

    def compute_blast_radius(self, affected_node_ids: list[str]) -> BlastRadius:
        """
        BFS from affected nodes across the supply graph.
        Contingent edges activate when their trigger node is in the affected set.
        """
        affected_set = set(affected_node_ids)

        # Activate contingent edges whose activation_condition matches affected nodes
        activated_contingent = []
        contingent_adjacency = {}
        for edge in self._contingent_edges:
            condition = edge.get("activation_condition")
            if condition and condition in affected_set:
                activated_contingent.append(edge)
                src = edge["source"]
                tgt = edge["target"]
                contingent_adjacency.setdefault(src, []).append((tgt, edge))
                contingent_adjacency.setdefault(tgt, []).append((src, edge))

        # BFS with depth tracking
        visited = set()
        tier1 = set()  # Direct neighbors of affected nodes
        tier2_plus = set()  # Nodes reached via 2+ hops

        queue = deque()
        for node_id in affected_node_ids:
            if node_id in self.nodes:
                visited.add(node_id)
                queue.append((node_id, 0))

        while queue:
            current, depth = queue.popleft()

            # Get neighbors from regular + activated contingent edges
            neighbors = self._adjacency.get(current, [])
            neighbors += contingent_adjacency.get(current, [])

            for neighbor_id, edge in neighbors:
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    if depth == 0:
                        tier1.add(neighbor_id)
                    else:
                        tier2_plus.add(neighbor_id)
                    # Limit BFS depth to prevent runaway cascades in dense graphs
                    if depth < 4:
                        queue.append((neighbor_id, depth + 1))

        return BlastRadius(
            direct_affected=len(tier1),
            tier2_cascade=len(tier2_plus),
            total_exposed=len(tier1) + len(tier2_plus),
        )

    def compute_buffer_diversity(self, firm_buffers: dict[str, np.ndarray]) -> list[BufferDiversityScore]:
        """
        Compute buffer-diversity score for each firm.
        D_buffer(i) = 1 - cosine_similarity(b_i, mean(b_{-i}))

        Args:
            firm_buffers: {firm_id: SKU-level buffer vector}
        """
        scores = compute_buffer_diversity(firm_buffers)
        return [
            BufferDiversityScore(firm_id=fid, d_buffer=score)
            for fid, score in sorted(scores.items(), key=lambda x: x[1])
        ]

    def generate_phased_release(
        self, diversity_scores: list[BufferDiversityScore]
    ) -> dict[str, list[str]]:
        """
        Assign firms to staggered release tranches (W1, W3, W5)
        based on their buffer-diversity scores.
        Low-diversity firms release first to desynchronize depletion.
        """
        scores_dict = {s.firm_id: s.d_buffer for s in diversity_scores}
        return assign_phased_release(scores_dict)

    def assess(
        self,
        event_id: str,
        affected_nodes: list[str],
        firm_buffers: dict[str, np.ndarray],
    ) -> TriageReport:
        """
        Main entry point: run full triage assessment pipeline.
        """
        # 1. Compute blast radius
        blast = self.compute_blast_radius(affected_nodes)

        # 2. Compute buffer diversity scores
        diversity_scores = self.compute_buffer_diversity(firm_buffers)

        # 3. Generate phased release schedule
        phased_schedule = self.generate_phased_release(diversity_scores)

        # 4. Compute graph mobility score
        mobility_scorer = GraphMobilityScorer(self.graph)
        mobility_score = mobility_scorer.compute_mobility_score(affected_nodes)

        # 5. Count activated contingent edges
        affected_set = set(affected_nodes)
        activated_count = sum(
            1 for e in self._contingent_edges
            if e.get("activation_condition") in affected_set
        )

        return TriageReport(
            event_id=event_id,
            blast_radius=blast,
            graph_mobility_score=mobility_score,
            buffer_diversity_scores=diversity_scores,
            phased_release_schedule=phased_schedule,
            contingent_edges_activated=activated_count,
            topology_ensemble_count=5,  # Default ensemble size
        )
