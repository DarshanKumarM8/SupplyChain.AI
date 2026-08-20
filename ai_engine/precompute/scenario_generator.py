"""
Scenario Generator — 120-Node Synthetic Supply Network
=========================================================

Generates a realistic supply chain graph with:
- 120 nodes (ports, factories, hubs, raw material sources, end markets)
- Regular shipping lane edges
- Contingent substitution edges (activate during disruptions)
- SKU-level buffer vectors per firm for diversity scoring

Output matches: shared/graph_schema/supply_network.json
"""

import json
import os
import numpy as np
from datetime import datetime


def generate_kaohsiung_typhoon_scenario(output_path: str = "data/scenarios/kaohsiung_typhoon.json") -> dict:
    """
    Generate the primary demo scenario: Typhoon hits Port of Kaohsiung.

    Network topology:
    - 15 ports (including Kaohsiung as critical node)
    - 30 factories (semiconductor, electronics, textiles)
    - 25 distribution hubs
    - 20 raw material sources
    - 30 end markets
    - ~200 regular edges + ~40 contingent substitution edges
    """
    # TODO: Implement full scenario generation
    # 1. Create nodes with realistic attributes (capacity, region, buffer vectors)
    # 2. Create regular shipping lane edges with costs and transit times
    # 3. Create contingent edges that activate when Kaohsiung fails
    # 4. Assign buffer vectors for diversity scoring
    raise NotImplementedError("Scenario generation not yet implemented")


if __name__ == "__main__":
    os.makedirs("data/scenarios", exist_ok=True)
    scenario = generate_kaohsiung_typhoon_scenario()
