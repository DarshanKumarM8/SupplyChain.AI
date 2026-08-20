"""
Manifold Router
================
GET /api/manifold/frame — Fetch precomputed manifold frame by parameters.

Delegates to ManifoldStore for O(1) snapped-grid lookup.  Falls back to an
embedded mock when no precomputed data has been loaded yet (dev/CI mode).
"""

from fastapi import APIRouter, HTTPException, Query

from app.services.manifold_store import manifold_store

router = APIRouter()


# ── Dev-mode fallback ─────────────────────────────────────────────────────────
# Used only when the store is empty (no frame_*.json files loaded).

_MOCK_FRAME = {
    "params": {"beta": 0.6, "adoption_pct": 0.40, "shock_intensity": 0.85},
    "frame_id": 142,
    "stampede_index_trajectory": [12, 14, 28, 52, 74, 87, 92, 88, 85, 82, 80, 78],
    "ai_index_trajectory":       [12, 14, 16, 18, 19, 21, 22, 21, 20, 19, 18, 18],
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
    "_source": "mock",
}


# ── Endpoint ──────────────────────────────────────────────────────────────────

@router.get("/manifold/frame")
async def get_manifold_frame(
    beta: float = Query(0.6, ge=0.1, le=0.9,  description="Herd-behaviour coupling constant β"),
    adoption: float = Query(0.0, ge=0.0, le=0.8, description="AI market adoption fraction (0–0.8)"),
    shock: float = Query(0.85, ge=0.1, le=1.0, description="Disruption shock intensity (0.1–1.0)"),
):
    """
    Return the precomputed manifold frame nearest to the supplied parameters.

    The store snaps *(beta, adoption, shock)* to the closest pre-computed grid
    point using Euclidean distance.  When no frames have been loaded yet the
    endpoint returns a built-in mock so the frontend can develop against it
    immediately.
    """
    frame = manifold_store.get_frame(beta, adoption, shock)

    if frame is None:
        # Store is empty — return mock with live params patched in
        frame = {
            **_MOCK_FRAME,
            "params": {
                "beta": beta,
                "adoption_pct": adoption,
                "shock_intensity": shock,
            },
            "meta_herd_detected": adoption > 0.6,
            "entropy_budget_active": adoption > 0.6,
        }
    else:
        # Real frame: tag it so the client can distinguish sources
        frame = {**frame, "_source": "precomputed"}

    return frame
