"""
Celery Worker — Async Task Runner
====================================

Handles heavy computation tasks offloaded from the API server:
- Simulation runs
- Manifold precomputation
- VaR calculations
"""

import os
import time
from celery import Celery

# Redis configuration with fallback for Docker Compose network
redis_url = os.getenv("REDIS_URL", os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0"))

celery_app = Celery(
    "supplychainai",
    broker=redis_url,
    backend=redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)


@celery_app.task(name="run_simulation")
def run_simulation(scenario_id: str = "kaohsiung_typhoon") -> dict:
    """
    Run a full simulation for the given scenario ID.
    Simulates a 2-second heavy workload before returning success status.
    """
    time.sleep(2)  # Simulate heavy computation workload
    return {
        "status": "success",
        "scenario_id": scenario_id,
        "message": f"Simulation run for scenario '{scenario_id}' completed successfully."
    }
