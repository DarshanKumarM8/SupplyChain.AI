"""
WebSocket Simulation Stream
==============================

Streams SupplyChainAI Index frames to the frontend at ~30 fps.

Protocol
--------
1. Client connects to ``/ws/simulation``
2. Client sends a JSON payload::

       {"beta": 0.6, "market_adoption_pct": 0.0, "shock_intensity": 0.85}

3. Server fetches the matching manifold trajectory via ManifoldStore
4. Server streams each trajectory tick back as JSON at ~30 fps
5. On disconnect the connection is torn down cleanly
"""

import asyncio
import json
import math
import time
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect

from app.services.manifold_store import manifold_store


# ── Target frame interval ────────────────────────────────────────────────────
_FPS = 30
_FRAME_INTERVAL = 1.0 / _FPS


# ── Mock fallback frame generator ────────────────────────────────────────────
# Used when ManifoldStore has no precomputed data loaded (dev / CI).

def _generate_mock_frame(
    tick: int,
    beta: float = 0.6,
    adoption: float = 0.0,
    shock: float = 0.85,
) -> dict[str, Any]:
    """Synthesise a single mock frame for a given simulation tick."""

    # Naive index climbs toward ~87 then plateaus
    naive_base = min(87, 12 + tick * 5)
    naive_noise = math.sin(tick * 0.3) * 2

    # AI index stays low, peaking around 21
    ai_base = min(21, 12 + tick * 0.6)
    ai_noise = math.sin(tick * 0.5) * 1

    # Scale by β
    naive_index = min(100, naive_base * (0.5 + beta) + naive_noise)
    ai_index = min(100, ai_base * (0.3 + beta * 0.3) + ai_noise)

    # Meta-herd bump at high adoption
    if adoption > 0.6:
        ai_index = min(ai_index + 5, 30)

    return {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "tick": tick,
        "stampede_index": round(ai_index, 1),
        "naive_index": round(naive_index, 1),
        "components": {
            "spearman_rho": round(0.15 + tick * 0.003, 3),
            "depletion_velocity": round(min(0.12, tick * 0.008), 3),
            "rate_volatility": round(min(0.34, tick * 0.02), 3),
        },
        "naive_components": {
            "spearman_rho": round(min(0.89, 0.1 + tick * 0.05), 3),
            "depletion_velocity": round(min(0.78, tick * 0.05), 3),
            "rate_volatility": round(min(0.91, tick * 0.06), 3),
        },
        "market_impact": {
            "naive_price_delta_pct": round(min(34.2, tick * 2.2), 1),
            "option_price_delta_pct": round(min(4.1, tick * 0.27), 1),
        },
        "kpi": {"cost_usd": 3_100_000, "sla_miss_pct": 4.0, "carbon_delta_pct": 6.0},
        "naive_kpi": {"cost_usd": 12_400_000, "sla_miss_pct": 23.0, "carbon_delta_pct": 19.0},
        "_source": "mock",
    }


# ── Precomputed-frame streamer ───────────────────────────────────────────────

async def _stream_precomputed(
    websocket: WebSocket,
    frame_data: dict[str, Any],
) -> None:
    """
    Stream the trajectories inside *frame_data* one tick at a time.

    Every tick emits a JSON message conforming exactly to the
    ``stampede_index.json`` schema (required fields: timestamp, tick,
    stampede_index, components, naive_index, naive_components,
    market_impact, kpi, naive_kpi) plus enrichment fields (node_states,
    density_field_snapshot, params, meta_herd_detected, entropy_budget_active).
    """
    naive_traj = frame_data.get("stampede_index_trajectory", [])
    ai_traj = frame_data.get("ai_index_trajectory", [])
    node_states = frame_data.get("node_states", [])
    density = frame_data.get("density_field_snapshot", [])
    params = frame_data.get("params", {})
    total_ticks = max(len(naive_traj), len(ai_traj), 1)

    for tick in range(total_ticks):
        naive_val = naive_traj[tick] if tick < len(naive_traj) else 0
        ai_val = ai_traj[tick] if tick < len(ai_traj) else 0

        # Derive per-tick component estimates from the trajectory curves
        progress = tick / max(total_ticks - 1, 1)

        msg: dict[str, Any] = {
            # ── Schema-required fields (stampede_index.json) ──────────
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "tick": tick,
            "stampede_index": round(ai_val, 1),
            "components": {
                "spearman_rho": round(min(0.25, 0.05 + progress * 0.20), 3),
                "depletion_velocity": round(min(0.15, progress * 0.15), 3),
                "rate_volatility": round(min(0.35, progress * 0.35), 3),
            },
            "naive_index": round(naive_val, 1),
            "naive_components": {
                "spearman_rho": round(min(0.89, 0.10 + progress * 0.79), 3),
                "depletion_velocity": round(min(0.78, progress * 0.78), 3),
                "rate_volatility": round(min(0.91, progress * 0.91), 3),
            },
            "market_impact": {
                "naive_price_delta_pct": round(min(34.2, progress * 34.2), 1),
                "option_price_delta_pct": round(min(4.1, progress * 4.1), 1),
            },
            "kpi": {
                "cost_usd": 3_100_000,
                "sla_miss_pct": 4.0,
                "carbon_delta_pct": 6.0,
            },
            "naive_kpi": {
                "cost_usd": 12_400_000,
                "sla_miss_pct": 23.0,
                "carbon_delta_pct": 19.0,
            },
            # ── Enrichment fields ─────────────────────────────────────
            "total_ticks": total_ticks,
            "node_states": node_states,
            "density_field_snapshot": density,
            "params": params,
            "meta_herd_detected": frame_data.get("meta_herd_detected", False),
            "entropy_budget_active": frame_data.get("entropy_budget_active", False),
            "_source": "precomputed",
        }
        await websocket.send_json(msg)
        await asyncio.sleep(_FRAME_INTERVAL)


# ── Mock-frame streamer (infinite loop) ──────────────────────────────────────

async def _stream_mock(
    websocket: WebSocket,
    beta: float,
    adoption: float,
    shock: float,
) -> None:
    """Infinite mock stream at ~30 fps — runs until the client disconnects."""
    tick = 0
    while True:
        frame = _generate_mock_frame(tick, beta, adoption, shock)
        await websocket.send_json(frame)
        tick += 1
        await asyncio.sleep(_FRAME_INTERVAL)


# ── WebSocket Handler ────────────────────────────────────────────────────────

async def websocket_simulation(websocket: WebSocket) -> None:
    """
    ``/ws/simulation`` endpoint.

    1. Accept connection
    2. Receive a JSON config with ``beta``, ``market_adoption_pct``,
       ``shock_intensity``
    3. Look up the nearest manifold trajectory via :pydata:`manifold_store`
    4. Stream frames at ~30 fps; gracefully handle disconnect
    """
    await websocket.accept()

    try:
        # ── 1. Receive initial simulation config ─────────────────────────
        config_text = await websocket.receive_text()
        config = json.loads(config_text)

        beta: float = config.get("beta", 0.6)
        adoption: float = config.get("market_adoption_pct", 0.0)
        shock: float = config.get("shock_intensity", 0.85)

        # ── 2. Look up the precomputed frame ─────────────────────────────
        frame_data = manifold_store.get_frame(beta, adoption, shock)

        # ── 3. Stream ────────────────────────────────────────────────────
        if frame_data is not None:
            await _stream_precomputed(websocket, frame_data)
            # Finite trajectory exhausted — send an end-of-stream marker
            await websocket.send_json({"event": "stream_complete"})
        else:
            # No precomputed data: fall back to continuous mock stream
            await _stream_mock(websocket, beta, adoption, shock)

    except WebSocketDisconnect:
        print("Client disconnected from /ws/simulation")
    except Exception as exc:
        # Catch-all so a bad payload or serialisation error never crashes the
        # server; log it and let the connection close naturally.
        print(f"WebSocket error on /ws/simulation: {exc}")
