"""
Graph Mobility Scorer -- Contingent-Edge Ensemble Analysis
==========================================================

Computes the "Graph Mobility Score" by generating an ensemble of supply network
topologies with different contingent edge activation patterns and measuring the
variance of shortest-path distributions across the ensemble.

High mobility = the network has many viable substitution paths.
Low mobility = the network is rigid and vulnerable to cascading failure.
"""

import numpy as np
import networkx as nx
from typing import Optional
from itertools import combinations


class GraphMobilityScorer:
    """
    Measures how flexible the supply network is under different disruption scenarios
    by evaluating contingent edge activations.
    """

    def __init__(self, graph_data: dict):
        """
        Args:
            graph_data: Supply network dict matching shared/graph_schema/supply_network.json
        """
        self.graph_data = graph_data
        self.base_graph = self._build_networkx_graph(include_contingent=False)
        self._contingent_edges = [
            e for e in graph_data.get("edges", []) if e.get("is_contingent", False)
        ]

    def _build_networkx_graph(
        self,
        include_contingent: bool = False,
        activated_conditions: Optional[set] = None,
        contingent_subset: Optional[list] = None,
    ) -> nx.DiGraph:
        """
        Build a NetworkX graph from the schema data.

        Args:
            include_contingent: If True, include contingent edges
            activated_conditions: Set of node IDs whose failure activates contingent edges
            contingent_subset: Specific list of contingent edges to include (overrides activated_conditions)
        """
        G = nx.DiGraph()
        for node in self.graph_data.get("nodes", []):
            G.add_node(node["id"], **{k: v for k, v in node.items() if k != "buffer_vector"})

        for edge in self.graph_data.get("edges", []):
            if edge.get("is_contingent", False):
                if contingent_subset is not None:
                    if edge in contingent_subset:
                        G.add_edge(edge["source"], edge["target"],
                                   weight=edge.get("cost_per_unit", 1), **edge)
                elif include_contingent and activated_conditions:
                    if edge.get("activation_condition") in activated_conditions:
                        G.add_edge(edge["source"], edge["target"],
                                   weight=edge.get("cost_per_unit", 1), **edge)
            else:
                G.add_edge(edge["source"], edge["target"],
                           weight=edge.get("cost_per_unit", 1), **edge)

        return G

    def generate_topology_ensemble(
        self,
        affected_nodes: list[str],
        n_samples: int = 5,
    ) -> list[nx.DiGraph]:
        """
        Generate an ensemble of graph topologies by sampling different subsets
        of contingent edge activations.

        Strategy: For each sample, randomly activate a subset of contingent edges
        that could plausibly be triggered by the disruption scenario.
        """
        rng = np.random.default_rng(42)
        affected_set = set(affected_nodes)

        # Find all contingent edges that COULD activate (matching activation conditions)
        eligible_contingent = [
            e for e in self._contingent_edges
            if e.get("activation_condition") in affected_set
        ]

        # Also include some random contingent edges to model uncertainty
        other_contingent = [
            e for e in self._contingent_edges
            if e.get("activation_condition") not in affected_set
        ]

        ensemble = []

        for sample_idx in range(n_samples):
            # Always include the eligible contingent edges
            selected = list(eligible_contingent)

            # Randomly add some fraction of other contingent edges
            if other_contingent:
                n_extra = rng.integers(0, max(1, len(other_contingent) // 2) + 1)
                extra_indices = rng.choice(len(other_contingent), size=min(n_extra, len(other_contingent)), replace=False)
                for idx in extra_indices:
                    selected.append(other_contingent[idx])

            G = self._build_networkx_graph(contingent_subset=selected)
            ensemble.append(G)

        return ensemble

    def _compute_mean_reachability(self, G: nx.DiGraph) -> float:
        """
        Compute mean reachability: average number of nodes reachable from any node.
        More informative than shortest path for potentially disconnected graphs.
        """
        total_nodes = G.number_of_nodes()
        if total_nodes == 0:
            return 0.0

        # Sample a subset of nodes for efficiency in large graphs
        sample_size = min(30, total_nodes)
        sample_nodes = list(G.nodes())[:sample_size]

        reachabilities = []
        for node in sample_nodes:
            reachable = nx.descendants(G, node)
            reachabilities.append(len(reachable) / total_nodes)

        return float(np.mean(reachabilities)) if reachabilities else 0.0

    def compute_mobility_score(
        self,
        affected_nodes: list[str],
        n_samples: int = 5,
    ) -> float:
        """
        Graph Mobility Score = normalized measure of path flexibility
        across the topology ensemble.

        High score (near 1.0) = many substitution options (resilient).
        Low score (near 0.0) = rigid network (fragile).

        Returns:
            Score in [0, 1]
        """
        # Generate ensemble of topologies
        ensemble = self.generate_topology_ensemble(affected_nodes, n_samples)

        if not ensemble:
            return 0.0

        # Compute reachability for each topology
        reachabilities = [self._compute_mean_reachability(G) for G in ensemble]

        # Base reachability (without any contingent edges)
        base_reach = self._compute_mean_reachability(self.base_graph)

        # Mobility = how much contingent edges improve reachability
        # Score = mean_ensemble_reachability (higher = more mobile)
        mean_reach = float(np.mean(reachabilities))

        # Normalize: if contingent edges don't help, mobility is low
        # Bonus for low variance (consistent improvement across topologies)
        variance = float(np.var(reachabilities)) if len(reachabilities) > 1 else 0.0
        consistency_bonus = max(0, 0.1 * (1.0 - variance * 10))

        mobility = min(1.0, mean_reach + consistency_bonus)

        return round(mobility, 4)
