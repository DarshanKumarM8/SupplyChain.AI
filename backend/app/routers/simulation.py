"""
Simulation Router
==================
POST /api/simulate         — Trigger a simulation run
POST /api/simulate/override — Manual jury override mid-stream
GET  /api/scenarios        — List available scenarios
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


# ── Pydantic Models (matching shared/api_schemas/) ────────────────

class SimulationConfig(BaseModel):
    scenario_id: str = "kaohsiung_typhoon"
    beta: float = 0.6
    market_adoption_pct: float = 0.0
    shock_intensity: float = 0.85
    mode: str = "ai_vs_naive"
    manual_override: Optional[dict] = None


class ManualOverride(BaseModel):
    lane_id: str
    action: str  # grab, release, reroute


# ── Mock Response Data ────────────────────────────────────────────

MOCK_SCENARIOS = [
    {"id": "kaohsiung_typhoon", "name": "Typhoon Hits Port Kaohsiung", "nodes": 120, "severity": "critical"},
    {"id": "suez_blockage", "name": "Suez Canal Blockage", "nodes": 120, "severity": "high"},
    {"id": "semiconductor_shortage", "name": "Global Semiconductor Shortage", "nodes": 120, "severity": "high"},
]

MOCK_REFLEX_DECISION = {
    "event_id": "evt_001",
    "strategy": "temporal_dephasing",
    "stampede_index_before": 87,
    "stampede_index_after": 21,
    "density_field": {
        "lanes": 10,
        "weeks": 6,
        "grid": [[0.12, 0.08, 0.05, 0.04, 0.03, 0.02],
                 [0.15, 0.10, 0.07, 0.05, 0.04, 0.03],
                 [0.08, 0.06, 0.04, 0.03, 0.02, 0.02],
                 [0.10, 0.08, 0.06, 0.04, 0.03, 0.02],
                 [0.05, 0.04, 0.03, 0.02, 0.02, 0.01],
                 [0.07, 0.05, 0.04, 0.03, 0.02, 0.01],
                 [0.04, 0.03, 0.02, 0.02, 0.01, 0.01],
                 [0.06, 0.04, 0.03, 0.02, 0.02, 0.01],
                 [0.03, 0.02, 0.02, 0.01, 0.01, 0.01],
                 [0.05, 0.04, 0.03, 0.02, 0.01, 0.01]],
    },
    "dephasing_schedule": {
        "W1": {"lane_ids": ["lane_3", "lane_7"], "allocation_pct": 0.35},
        "W3": {"lane_ids": ["lane_1", "lane_9"], "allocation_pct": 0.40},
        "W5": {"lane_ids": ["lane_5"], "allocation_pct": 0.25},
    },
    "entropy_budget": {
        "total_budget": 0.023,
        "spent": 0.019,
        "randomized_routes": 4,
    },
    "options_exercised": [
        {"lane_id": "lane_3", "capacity_units": 50, "strike_price": 1200, "spot_price": 1608},
        {"lane_id": "lane_7", "capacity_units": 35, "strike_price": 1100, "spot_price": 1474},
    ],
    "cost_summary": {
        "total_cost_usd": 3100000,
        "sla_miss_pct": 4.0,
        "carbon_delta_pct": 6.0,
    },
}


# ── Endpoints ─────────────────────────────────────────────────────

@router.get("/scenarios")
async def list_scenarios():
    """List all available disruption scenarios."""
    return MOCK_SCENARIOS


@router.post("/simulate")
async def run_simulation(config: SimulationConfig):
    """
    Trigger a simulation run with the given parameters.
    Returns the Reflex agent decision (mock for now).
    """
    # TODO: Wire to actual ai_engine pipeline via Celery
    return {
        **MOCK_REFLEX_DECISION,
        "config": config.model_dump(),
    }


@router.post("/simulate/override")
async def manual_override(override: ManualOverride):
    """
    Jury manual override: grab/release a lane mid-simulation.
    The density solver should react to the localized volume spike.
    """
    # TODO: Wire to live simulation state
    return {
        "status": "override_applied",
        "lane_id": override.lane_id,
        "action": override.action,
        "message": f"Lane {override.lane_id} {override.action}d — density solver re-adjusting",
    }
