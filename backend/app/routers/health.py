"""
Health Check Endpoint
======================
Simple uptime probe for compliance verification and cloud health checks.
"""

import time
from fastapi import APIRouter

router = APIRouter()

_start_time = time.time()


@router.get("/health")
async def health_check():
    """Returns server status and uptime in seconds."""
    return {
        "status": "ok",
        "service": "SupplyChainAI Backend",
        "uptime_s": round(time.time() - _start_time, 1),
    }
