"""
WebSocket Simulation Stream
==============================

Streams SupplyChainAI Index frames to the frontend at ~30fps.
Each frame contains both naive and AI panel data.

Protocol:
1. Client connects to /ws/simulation
2. Client sends SimulationConfig JSON
3. Server streams StampedeIndexFrame JSON at 30fps
4. Client can send mid-stream overrides
"""

import asyncio
import json
import time
from fastapi import WebSocket, WebSocketDisconnect


# ── Mock Frame Generator ─────────────────────────────────────────

def generate_mock_frame(tick: int, beta: float = 0.6, adoption: float = 0.0) -> dict:
    """
    Generate a mock SupplyChainAI Index frame for streaming.
    In production, this pulls from the precomputed manifold store.
    """
    import math

    # Simulate naive index climbing to 87 then stabilizing
    naive_base = min(87, 12 + tick * 5)
    naive_noise = math.sin(tick * 0.3) * 2

    # Simulate AI index peaking at 21
    ai_base = min(21, 12 + tick * 0.6)
    ai_noise = math.sin(tick * 0.5) * 1

    # Scale by beta
    naive_index = min(100, naive_base * (0.5 + beta) + naive_noise)
    ai_index = min(100, ai_base * (0.3 + beta * 0.3) + ai_noise)

    # Meta-herd adjustment
    if adoption > 0.6:
        ai_index = min(ai_index + 5, 30)  # Slight increase but still low

    return {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "tick": tick,
        "stampede_index": round(ai_index, 1),
        "components": {
            "spearman_rho": round(0.15 + tick * 0.003, 3),
            "depletion_velocity": round(min(0.12, tick * 0.008), 3),
            "rate_volatility": round(min(0.34, tick * 0.02), 3),
        },
        "naive_index": round(naive_index, 1),
        "naive_components": {
            "spearman_rho": round(min(0.89, 0.1 + tick * 0.05), 3),
            "depletion_velocity": round(min(0.78, tick * 0.05), 3),
            "rate_volatility": round(min(0.91, tick * 0.06), 3),
        },
        "market_impact": {
            "naive_price_delta_pct": round(min(34.2, tick * 2.2), 1),
            "option_price_delta_pct": round(min(4.1, tick * 0.27), 1),
        },
        "kpi": {
            "cost_usd": 3100000,
            "sla_miss_pct": 4.0,
            "carbon_delta_pct": 6.0,
        },
        "naive_kpi": {
            "cost_usd": 12400000,
            "sla_miss_pct": 23.0,
            "carbon_delta_pct": 19.0,
        },
    }


# ── WebSocket Handler ────────────────────────────────────────────

async def websocket_simulation(websocket: WebSocket):
    """
    WebSocket endpoint for streaming simulation state.
    Expects SimulationConfig on connect, streams frames at ~30fps.
    """
    await websocket.accept()

    try:
        # Receive initial config
        config_text = await websocket.receive_text()
        config = json.loads(config_text)
        beta = config.get("beta", 0.6)
        adoption = config.get("market_adoption_pct", 0.0)

        # Stream frames
        tick = 0
        while True:
            frame = generate_mock_frame(tick, beta, adoption)
            await websocket.send_json(frame)
            tick += 1
            await asyncio.sleep(1 / 30)  # ~30fps

            # Check for mid-stream config updates (non-blocking)
            try:
                update_text = await asyncio.wait_for(
                    websocket.receive_text(), timeout=0.001
                )
                update = json.loads(update_text)
                beta = update.get("beta", beta)
                adoption = update.get("market_adoption_pct", adoption)
            except asyncio.TimeoutError:
                pass

    except WebSocketDisconnect:
        print("Client disconnected from simulation stream")
    except Exception as e:
        print(f"WebSocket error: {e}")
