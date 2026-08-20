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
from datetime import datetime, timezone


# ── Node definitions by type ────────────────────────────────────────

PORTS = [
    {"id": "port_kaohsiung",     "label": "Port of Kaohsiung",     "region": "East Asia",    "country": "TW", "lat": 22.62, "lon": 120.27, "capacity_max": 5000, "is_critical": True},
    {"id": "port_shanghai",      "label": "Port of Shanghai",      "region": "East Asia",    "country": "CN", "lat": 31.23, "lon": 121.47, "capacity_max": 8000, "is_critical": True},
    {"id": "port_busan",         "label": "Port of Busan",         "region": "East Asia",    "country": "KR", "lat": 35.10, "lon": 129.04, "capacity_max": 4500, "is_critical": False},
    {"id": "port_singapore",     "label": "Port of Singapore",     "region": "Southeast Asia","country": "SG", "lat":  1.26, "lon": 103.84, "capacity_max": 7000, "is_critical": True},
    {"id": "port_rotterdam",     "label": "Port of Rotterdam",     "region": "Europe",       "country": "NL", "lat": 51.90, "lon":   4.50, "capacity_max": 6000, "is_critical": False},
    {"id": "port_losangeles",    "label": "Port of Los Angeles",   "region": "North America","country": "US", "lat": 33.74, "lon":-118.27, "capacity_max": 5500, "is_critical": False},
    {"id": "port_hamburg",       "label": "Port of Hamburg",       "region": "Europe",       "country": "DE", "lat": 53.55, "lon":   9.99, "capacity_max": 4000, "is_critical": False},
    {"id": "port_dubai",         "label": "Port of Jebel Ali",     "region": "Middle East",  "country": "AE", "lat": 25.01, "lon":  55.06, "capacity_max": 4500, "is_critical": False},
    {"id": "port_mumbai",        "label": "Port of Mumbai JNPT",   "region": "South Asia",   "country": "IN", "lat": 18.95, "lon":  72.95, "capacity_max": 3000, "is_critical": False},
    {"id": "port_tokyo",         "label": "Port of Tokyo",         "region": "East Asia",    "country": "JP", "lat": 35.63, "lon": 139.77, "capacity_max": 3500, "is_critical": False},
    {"id": "port_longbeach",     "label": "Port of Long Beach",    "region": "North America","country": "US", "lat": 33.75, "lon":-118.19, "capacity_max": 5000, "is_critical": False},
    {"id": "port_shenzhen",      "label": "Port of Shenzhen",      "region": "East Asia",    "country": "CN", "lat": 22.54, "lon": 114.06, "capacity_max": 5500, "is_critical": False},
    {"id": "port_hochiminh",     "label": "Port of Ho Chi Minh",   "region": "Southeast Asia","country": "VN","lat": 10.77, "lon": 106.70, "capacity_max": 2500, "is_critical": False},
    {"id": "port_santos",        "label": "Port of Santos",        "region": "South America","country": "BR", "lat":-23.95, "lon": -46.30, "capacity_max": 3000, "is_critical": False},
    {"id": "port_colombo",       "label": "Port of Colombo",       "region": "South Asia",   "country": "LK", "lat":  6.94, "lon":  79.84, "capacity_max": 2000, "is_critical": False},
]

FACTORIES = [
    {"id": f"factory_tw_semi_{i}",  "label": f"Taiwan Semiconductor Fab {i}", "region": "East Asia",     "country": "TW", "sector": "semiconductor"} for i in range(1, 7)
] + [
    {"id": f"factory_cn_elec_{i}",  "label": f"China Electronics Plant {i}",  "region": "East Asia",     "country": "CN", "sector": "electronics"} for i in range(1, 7)
] + [
    {"id": f"factory_kr_chip_{i}",  "label": f"Korea Chip Foundry {i}",       "region": "East Asia",     "country": "KR", "sector": "semiconductor"} for i in range(1, 5)
] + [
    {"id": f"factory_vn_text_{i}",  "label": f"Vietnam Textile Mill {i}",     "region": "Southeast Asia","country": "VN", "sector": "textiles"} for i in range(1, 5)
] + [
    {"id": f"factory_in_pharma_{i}","label": f"India Pharma Plant {i}",       "region": "South Asia",    "country": "IN", "sector": "pharma"} for i in range(1, 5)
] + [
    {"id": f"factory_de_auto_{i}",  "label": f"Germany Auto Assembly {i}",    "region": "Europe",        "country": "DE", "sector": "automotive"} for i in range(1, 5)
]

HUBS = [
    {"id": f"hub_sg_{i}",    "label": f"Singapore Dist Hub {i}",     "region": "Southeast Asia","country": "SG"} for i in range(1, 6)
] + [
    {"id": f"hub_nl_{i}",    "label": f"Netherlands Dist Hub {i}",   "region": "Europe",       "country": "NL"} for i in range(1, 6)
] + [
    {"id": f"hub_us_west_{i}","label": f"US West Coast Hub {i}",     "region": "North America","country": "US"} for i in range(1, 6)
] + [
    {"id": f"hub_us_east_{i}","label": f"US East Coast Hub {i}",     "region": "North America","country": "US"} for i in range(1, 4)
] + [
    {"id": f"hub_ae_{i}",    "label": f"Dubai Logistics Hub {i}",    "region": "Middle East",  "country": "AE"} for i in range(1, 4)
] + [
    {"id": f"hub_jp_{i}",    "label": f"Japan Distribution Hub {i}", "region": "East Asia",    "country": "JP"} for i in range(1, 4)
]

RAW_SOURCES = [
    {"id": "raw_au_iron",    "label": "Australia Iron Ore Mine",    "region": "Oceania",       "country": "AU", "commodity": "iron_ore"},
    {"id": "raw_cl_copper",  "label": "Chile Copper Mine",          "region": "South America", "country": "CL", "commodity": "copper"},
    {"id": "raw_au_lithium", "label": "Australia Lithium Mine",     "region": "Oceania",       "country": "AU", "commodity": "lithium"},
    {"id": "raw_cd_cobalt",  "label": "DRC Cobalt Mine",            "region": "Africa",        "country": "CD", "commodity": "cobalt"},
    {"id": "raw_cn_rare",    "label": "China Rare Earth Mine",      "region": "East Asia",     "country": "CN", "commodity": "rare_earth"},
    {"id": "raw_sa_oil",     "label": "Saudi Arabia Oil Field",     "region": "Middle East",   "country": "SA", "commodity": "crude_oil"},
    {"id": "raw_br_soy",     "label": "Brazil Soy Farm",            "region": "South America", "country": "BR", "commodity": "soybeans"},
    {"id": "raw_us_silicon", "label": "US Silicon Quarry",          "region": "North America", "country": "US", "commodity": "silicon"},
    {"id": "raw_in_cotton",  "label": "India Cotton Farm",          "region": "South Asia",    "country": "IN", "commodity": "cotton"},
    {"id": "raw_id_palm",    "label": "Indonesia Palm Oil",         "region": "Southeast Asia","country": "ID", "commodity": "palm_oil"},
    {"id": "raw_za_platinum","label": "South Africa Platinum Mine", "region": "Africa",        "country": "ZA", "commodity": "platinum"},
    {"id": "raw_ar_lithium", "label": "Argentina Lithium Brine",    "region": "South America", "country": "AR", "commodity": "lithium"},
    {"id": "raw_ru_nickel",  "label": "Russia Nickel Mine",         "region": "Europe",        "country": "RU", "commodity": "nickel"},
    {"id": "raw_th_rubber",  "label": "Thailand Rubber Plantation", "region": "Southeast Asia","country": "TH", "commodity": "rubber"},
    {"id": "raw_gh_cocoa",   "label": "Ghana Cocoa Farm",           "region": "Africa",        "country": "GH", "commodity": "cocoa"},
    {"id": "raw_eg_cotton",  "label": "Egypt Cotton Farm",          "region": "Africa",        "country": "EG", "commodity": "cotton"},
    {"id": "raw_my_tin",     "label": "Malaysia Tin Mine",           "region": "Southeast Asia","country": "MY", "commodity": "tin"},
    {"id": "raw_pe_zinc",    "label": "Peru Zinc Mine",             "region": "South America", "country": "PE", "commodity": "zinc"},
    {"id": "raw_ca_potash",  "label": "Canada Potash Mine",         "region": "North America", "country": "CA", "commodity": "potash"},
    {"id": "raw_no_fish",    "label": "Norway Fishery",             "region": "Europe",        "country": "NO", "commodity": "fish"},
]

END_MARKETS = [
    {"id": f"market_us_{i}",  "label": f"US Consumer Market {i}",     "region": "North America","country": "US"} for i in range(1, 9)
] + [
    {"id": f"market_eu_{i}",  "label": f"EU Consumer Market {i}",     "region": "Europe",       "country": "EU"} for i in range(1, 7)
] + [
    {"id": f"market_cn_{i}",  "label": f"China Consumer Market {i}",  "region": "East Asia",    "country": "CN"} for i in range(1, 5)
] + [
    {"id": f"market_jp_{i}",  "label": f"Japan Consumer Market {i}",  "region": "East Asia",    "country": "JP"} for i in range(1, 4)
] + [
    {"id": f"market_in_{i}",  "label": f"India Consumer Market {i}",  "region": "South Asia",   "country": "IN"} for i in range(1, 4)
] + [
    {"id": f"market_br_{i}",  "label": f"Brazil Consumer Market {i}", "region": "South America","country": "BR"} for i in range(1, 3)
] + [
    {"id": f"market_kr_{i}",  "label": f"Korea Consumer Market {i}",  "region": "East Asia",    "country": "KR"} for i in range(1, 3)
] + [
    {"id": "market_au_1",     "label": "Australia Consumer Market",   "region": "Oceania",      "country": "AU"},
    {"id": "market_sg_1",     "label": "Singapore Consumer Market",   "region": "Southeast Asia","country": "SG"},
]


# ── Lane type parameters ────────────────────────────────────────────

LANE_PARAMS = {
    "ocean_freight":  {"cost_range": (50, 200),  "transit_range": (14, 45), "capacity_range": (500, 2000)},
    "air_freight":    {"cost_range": (300, 800), "transit_range": (1, 5),   "capacity_range": (50, 200)},
    "rail":           {"cost_range": (80, 250),  "transit_range": (7, 21),  "capacity_range": (200, 800)},
    "truck":          {"cost_range": (100, 400), "transit_range": (1, 7),   "capacity_range": (100, 500)},
    "intermodal":     {"cost_range": (70, 300),  "transit_range": (5, 25),  "capacity_range": (300, 1000)},
}


def _build_nodes(rng: np.random.Generator, n_skus: int = 10) -> list[dict]:
    """Build all 120 nodes with capacity and buffer vectors."""
    all_nodes = []

    for port in PORTS:
        node = {
            "id": port["id"],
            "label": port["label"],
            "type": "port",
            "region": port["region"],
            "country": port["country"],
            "lat": port["lat"],
            "lon": port["lon"],
            "capacity_max": port["capacity_max"],
            "capacity_current": int(port["capacity_max"] * rng.uniform(0.6, 0.95)),
            "is_critical": port.get("is_critical", False),
            "buffer_vector": rng.dirichlet(np.ones(n_skus)).tolist(),
        }
        all_nodes.append(node)

    for factory in FACTORIES:
        cap = rng.integers(500, 3000)
        node = {
            "id": factory["id"],
            "label": factory["label"],
            "type": "factory",
            "region": factory["region"],
            "country": factory["country"],
            "lat": rng.uniform(-40, 60),
            "lon": rng.uniform(-120, 150),
            "capacity_max": int(cap),
            "capacity_current": int(cap * rng.uniform(0.5, 0.9)),
            "is_critical": "semi" in factory["id"],
            "buffer_vector": rng.dirichlet(np.ones(n_skus)).tolist(),
        }
        all_nodes.append(node)

    for hub in HUBS:
        cap = rng.integers(1000, 5000)
        node = {
            "id": hub["id"],
            "label": hub["label"],
            "type": "distribution_hub",
            "region": hub["region"],
            "country": hub["country"],
            "lat": rng.uniform(-40, 60),
            "lon": rng.uniform(-120, 150),
            "capacity_max": int(cap),
            "capacity_current": int(cap * rng.uniform(0.4, 0.85)),
            "is_critical": False,
            "buffer_vector": rng.dirichlet(np.ones(n_skus)).tolist(),
        }
        all_nodes.append(node)

    for raw in RAW_SOURCES:
        cap = rng.integers(2000, 8000)
        node = {
            "id": raw["id"],
            "label": raw["label"],
            "type": "raw_material_source",
            "region": raw["region"],
            "country": raw["country"],
            "lat": rng.uniform(-40, 60),
            "lon": rng.uniform(-120, 150),
            "capacity_max": int(cap),
            "capacity_current": int(cap * rng.uniform(0.7, 1.0)),
            "is_critical": False,
            "buffer_vector": rng.dirichlet(np.ones(n_skus)).tolist(),
        }
        all_nodes.append(node)

    for market in END_MARKETS:
        cap = rng.integers(3000, 10000)
        node = {
            "id": market["id"],
            "label": market["label"],
            "type": "end_market",
            "region": market["region"],
            "country": market["country"],
            "lat": rng.uniform(-40, 60),
            "lon": rng.uniform(-120, 150),
            "capacity_max": int(cap),
            "capacity_current": int(cap * rng.uniform(0.3, 0.7)),
            "is_critical": False,
            "buffer_vector": rng.dirichlet(np.ones(n_skus)).tolist(),
        }
        all_nodes.append(node)

    return all_nodes


def _select_lane_type(source_type: str, target_type: str, rng: np.random.Generator) -> str:
    """Choose a realistic lane type based on source and target node types."""
    if source_type == "raw_material_source":
        return rng.choice(["ocean_freight", "rail", "truck"], p=[0.5, 0.3, 0.2])
    if source_type == "port" and target_type == "port":
        return "ocean_freight"
    if source_type == "port" and target_type in ("factory", "distribution_hub"):
        return rng.choice(["truck", "rail", "intermodal"], p=[0.4, 0.3, 0.3])
    if source_type == "factory" and target_type == "port":
        return rng.choice(["truck", "rail"], p=[0.6, 0.4])
    if source_type == "factory" and target_type == "distribution_hub":
        return rng.choice(["truck", "rail", "intermodal"], p=[0.4, 0.3, 0.3])
    if source_type == "distribution_hub" and target_type == "end_market":
        return rng.choice(["truck", "air_freight", "intermodal"], p=[0.5, 0.2, 0.3])
    return rng.choice(["ocean_freight", "truck", "rail"])


def _make_edge(edge_id: str, source: str, target: str, lane_type: str,
               rng: np.random.Generator, is_contingent: bool = False,
               activation_condition: str = None) -> dict:
    """Create a single edge with realistic attributes."""
    params = LANE_PARAMS[lane_type]
    cost = float(rng.uniform(*params["cost_range"]))
    transit = float(rng.uniform(*params["transit_range"]))
    capacity = int(rng.integers(*params["capacity_range"]))
    base_rate = cost * rng.uniform(0.8, 1.2)
    temp_controlled = lane_type in ("air_freight", "truck") and rng.random() < 0.3

    return {
        "id": edge_id,
        "source": source,
        "target": target,
        "lane_type": lane_type,
        "cost_per_unit": round(cost, 2),
        "transit_days": round(transit, 1),
        "capacity": capacity,
        "is_contingent": is_contingent,
        "activation_condition": activation_condition,
        "base_rate": round(base_rate, 2),
        "temperature_controlled": temp_controlled,
        "avg_temperature_c": round(float(rng.uniform(2, 8)), 1) if temp_controlled else None,
    }


def _build_edges(nodes: list[dict], rng: np.random.Generator) -> list[dict]:
    """Build ~200 regular edges + ~40 contingent substitution edges."""
    node_by_id = {n["id"]: n for n in nodes}
    node_ids_by_type = {}
    for n in nodes:
        node_ids_by_type.setdefault(n["type"], []).append(n["id"])

    edges = []
    edge_id_counter = 0

    def _add(src, tgt, contingent=False, activation=None):
        nonlocal edge_id_counter
        lt = _select_lane_type(node_by_id[src]["type"], node_by_id[tgt]["type"], rng)
        eid = f"lane_{edge_id_counter:04d}"
        edges.append(_make_edge(eid, src, tgt, lt, rng, contingent, activation))
        edge_id_counter += 1

    # ── Raw materials → Ports / Factories ──────────────────────────
    for raw_id in node_ids_by_type["raw_material_source"]:
        n_targets = rng.integers(2, 5)
        targets = rng.choice(
            node_ids_by_type["port"] + node_ids_by_type["factory"],
            size=min(n_targets, len(node_ids_by_type["port"]) + len(node_ids_by_type["factory"])),
            replace=False,
        )
        for tgt in targets:
            _add(raw_id, tgt)

    # ── Ports → Ports (inter-port ocean routes) ────────────────────
    port_ids = node_ids_by_type["port"]
    for i, src in enumerate(port_ids):
        n_routes = rng.integers(1, 4)
        candidates = [p for p in port_ids if p != src]
        targets = rng.choice(candidates, size=min(n_routes, len(candidates)), replace=False)
        for tgt in targets:
            _add(src, tgt)

    # ── Ports → Factories (inbound supply) ─────────────────────────
    for factory_id in node_ids_by_type["factory"]:
        region = node_by_id[factory_id]["region"]
        regional_ports = [p for p in port_ids if node_by_id[p]["region"] == region]
        if not regional_ports:
            regional_ports = rng.choice(port_ids, size=2, replace=False).tolist()
        for port_id in regional_ports[:2]:
            _add(port_id, factory_id)

    # ── Factories → Ports (outbound to shipping) ──────────────────
    for factory_id in node_ids_by_type["factory"]:
        region = node_by_id[factory_id]["region"]
        regional_ports = [p for p in port_ids if node_by_id[p]["region"] == region]
        if not regional_ports:
            regional_ports = rng.choice(port_ids, size=1, replace=False).tolist()
        _add(factory_id, regional_ports[0])

    # ── Factories → Distribution Hubs ──────────────────────────────
    for factory_id in node_ids_by_type["factory"]:
        n_hubs = rng.integers(1, 4)
        hub_targets = rng.choice(node_ids_by_type["distribution_hub"],
                                  size=min(n_hubs, len(node_ids_by_type["distribution_hub"])),
                                  replace=False)
        for hub_id in hub_targets:
            _add(factory_id, hub_id)

    # ── Ports → Distribution Hubs ─────────────────────────────────
    for port_id in port_ids:
        region = node_by_id[port_id]["region"]
        regional_hubs = [h for h in node_ids_by_type["distribution_hub"]
                         if node_by_id[h]["region"] == region]
        if regional_hubs:
            for hub_id in regional_hubs[:2]:
                _add(port_id, hub_id)

    # ── Distribution Hubs → End Markets ───────────────────────────
    for hub_id in node_ids_by_type["distribution_hub"]:
        region = node_by_id[hub_id]["region"]
        regional_markets = [m for m in node_ids_by_type["end_market"]
                            if node_by_id[m]["region"] == region]
        if not regional_markets:
            regional_markets = rng.choice(node_ids_by_type["end_market"],
                                           size=2, replace=False).tolist()
        n_markets = min(rng.integers(2, 5), len(regional_markets))
        for market_id in regional_markets[:n_markets]:
            _add(hub_id, market_id)

    # ── Contingent substitution edges (activate when Kaohsiung fails) ──
    kaohsiung_dependent_factories = [f for f in node_ids_by_type["factory"]
                                      if node_by_id[f]["country"] == "TW"]
    alt_ports = ["port_busan", "port_shanghai", "port_shenzhen", "port_hochiminh", "port_singapore"]

    for factory_id in kaohsiung_dependent_factories:
        for alt_port in rng.choice(alt_ports, size=min(3, len(alt_ports)), replace=False):
            _add(alt_port, factory_id, contingent=True, activation="port_kaohsiung")

    # Additional contingent edges: factories to alternative hubs
    for factory_id in kaohsiung_dependent_factories:
        alt_hubs = rng.choice(node_ids_by_type["distribution_hub"],
                               size=min(2, len(node_ids_by_type["distribution_hub"])),
                               replace=False)
        for hub_id in alt_hubs:
            _add(factory_id, hub_id, contingent=True, activation="port_kaohsiung")

    # More contingent edges for non-TW critical paths (Shanghai, Singapore disruptions)
    for critical_port in ["port_shanghai", "port_singapore"]:
        dependent = [f for f in node_ids_by_type["factory"]
                     if node_by_id[f]["country"] == node_by_id[critical_port]["country"]]
        for factory_id in dependent[:3]:
            backup_port = rng.choice([p for p in alt_ports if p != critical_port])
            _add(backup_port, factory_id, contingent=True, activation=critical_port)

    return edges


def _build_firms(nodes: list[dict], rng: np.random.Generator, n_firms: int = 20, n_skus: int = 10) -> list[dict]:
    """Generate synthetic firms with SKU-level buffer vectors."""
    firms = []
    for i in range(n_firms):
        firm_id = f"firm_{chr(65 + i)}" if i < 26 else f"firm_{i}"
        # Some firms have similar buffers (low diversity → stampede risk)
        if i < 5:
            # Cluster: these 5 firms have very similar buffers
            base = rng.dirichlet(np.ones(n_skus) * 0.5)
            buffer = base + rng.normal(0, 0.02, n_skus)
            buffer = np.clip(buffer, 0, None)
            buffer /= buffer.sum()
        else:
            buffer = rng.dirichlet(np.ones(n_skus) * rng.uniform(0.3, 2.0))

        firms.append({
            "firm_id": firm_id,
            "buffer_vector": buffer.tolist(),
            "home_region": rng.choice(["East Asia", "Europe", "North America", "South Asia"]),
        })

    return firms


def generate_kaohsiung_typhoon_scenario(
    output_path: str = "data/scenarios/kaohsiung_typhoon.json",
    seed: int = 42,
) -> dict:
    """
    Generate the primary demo scenario: Typhoon hits Port of Kaohsiung.

    Network topology:
    - 15 ports (including Kaohsiung as critical node)
    - 30 factories (semiconductor, electronics, textiles, pharma, automotive)
    - 25 distribution hubs
    - 20 raw material sources
    - 30 end markets
    - ~200 regular edges + ~40 contingent substitution edges
    """
    rng = np.random.default_rng(seed)

    nodes = _build_nodes(rng)
    edges = _build_edges(nodes, rng)
    firms = _build_firms(nodes, rng)

    regular_edges = [e for e in edges if not e["is_contingent"]]
    contingent_edges = [e for e in edges if e["is_contingent"]]

    scenario = {
        "network_id": "kaohsiung_typhoon_v1",
        "metadata": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "regular_edge_count": len(regular_edges),
            "contingent_edge_count": len(contingent_edges),
            "scenario": "Typhoon hits Port of Kaohsiung — critical semiconductor supply corridor disrupted",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "seed": seed,
        },
        "nodes": nodes,
        "edges": edges,
        "firms": firms,
        "disruption": {
            "event_type": "port_closure",
            "affected_nodes": ["port_kaohsiung"],
            "description": "Category 4 typhoon forces Port of Kaohsiung to close for 3+ weeks",
            "severity": 0.85,
            "estimated_duration_weeks": 3,
        },
    }

    # Write to file
    abs_output = os.path.join(os.path.dirname(__file__), "..", output_path)
    os.makedirs(os.path.dirname(abs_output), exist_ok=True)
    with open(abs_output, "w") as f:
        json.dump(scenario, f, indent=2)

    print(f"[OK] Generated scenario: {len(nodes)} nodes, {len(regular_edges)} regular edges, "
          f"{len(contingent_edges)} contingent edges, {len(firms)} firms")
    print(f"  Saved to: {abs_output}")

    return scenario


if __name__ == "__main__":
    generate_kaohsiung_typhoon_scenario()
