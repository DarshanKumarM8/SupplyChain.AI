"""
Celery Worker — Async Task Runner
====================================

Handles heavy computation tasks offloaded from the API server:
- Simulation runs
- Manifold precomputation
- VaR calculations
"""

from celery import Celery
import os

redis_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")

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


@celery_app.task(bind=True, name="run_simulation")
def run_simulation(self, config: dict) -> dict:
    """
    Run a full simulation for the given configuration.
    This is offloaded to Celery to avoid blocking the API server.
    """
    # TODO: Wire to ai_engine pipeline
    # 1. Load scenario graph
    # 2. Run Sentinel → Triage → Reflex
    # 3. Return reflex decision
    return {"status": "completed", "config": config}


@celery_app.task(bind=True, name="precompute_manifold")
def precompute_manifold(self, scenario_path: str, output_dir: str) -> dict:
    """
    Run the offline manifold sweep precomputation.
    """
    # TODO: Wire to ai_engine/precompute/manifold_sweep.py
    return {"status": "completed", "scenario": scenario_path}
