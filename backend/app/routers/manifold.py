"""
Manifold Router
================
GET /api/manifold/frame — Fetch precomputed manifold frame by parameters
"""

from fastapi import APIRouter, Query

router = APIRouter()

# ── Mock Manifold Frame ───────────────────────────────────────────

MOCK_MANIFOLD_FRAME = {
    "params": {"beta": 0.6, "adoption_pct": 0.40, "shock_intensity": 0.85},
    "frame_id": 142,
    "stampede_index_trajectory": [12, 14, 28, 52, 74, 87, 92, 88, 85, 82, 80, 78],
    "ai_index_trajectory":      [12, 14, 16, 18, 19, 21, 22, 21, 20, 19, 18, 18],
    "node_states": [
        {"id": "node_kaohsiung_port", "capacity_pct": 0.0,  "is_bottleneck": True,  "lane_price_delta": 0.0},
        {"id": "node_supplier_b",     "capacity_pct": 0.05, "is_bottleneck": True,  "lane_price_delta": 0.34},
        {"id": "node_supplier_c",     "capacity_pct": 0.72, "is_bottleneck": False, "lane_price_delta": 0.08},
        {"id": "node_hub_shanghai",   "capacity_pct": 0.45, "is_bottleneck": True,  "lane_price_delta": 0.22},
        {"id": "node_hub_singapore",  "capacity_pct": 0.88, "is_bottleneck": False, "lane_price_delta": 0.03},
    ],
    "density_field_snapshot": [
        [0.12, 0.08, 0.05, 0.04, 0.03, 0.02],
        [0.15, 0.10, 0.07, 0.05, 0.04, 0.03],
        [0.08, 0.06, 0.04, 0.03, 0.02, 0.02],
    ],
    "meta_herd_detected": False,
    "entropy_budget_active": False,
}


@router.get("/manifold/frame")
async def get_manifold_frame(
    beta: float = Query(0.6, ge=0.1, le=0.9),
    adoption: float = Query(0.0, ge=0.0, le=0.8),
    shock: float = Query(0.85, ge=0.1, le=1.0),
):
    """
    Fetch a precomputed manifold frame for the given parameter combination.
    Snaps to nearest precomputed grid point.
    """
    # TODO: Look up from in-memory manifold store
    frame = {**MOCK_MANIFOLD_FRAME}
    frame["params"] = {
        "beta": beta,
        "adoption_pct": adoption,
        "shock_intensity": shock,
    }

    # Meta-herd fires above 60% adoption
    frame["meta_herd_detected"] = adoption > 0.6
    frame["entropy_budget_active"] = adoption > 0.6

    return frame
