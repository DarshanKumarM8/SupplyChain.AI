"""
Tests for the GET /api/manifold/frame endpoint.

Uses FastAPI's synchronous TestClient (no async test runner needed) and
unittest.mock to patch ManifoldStore so tests run without real frame data on disk.

Run with:
    pytest backend/tests/test_manifold.py -v
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app


# ── TestClient fixture ────────────────────────────────────────────────────────

@pytest.fixture
def client() -> TestClient:
    """Synchronous ASGI test client wrapping the FastAPI app."""
    return TestClient(app)


# ── Shared mock frame ─────────────────────────────────────────────────────────
# Matches the shape returned by ManifoldStore.get_frame() (and the mock router
# fallback) — mirrors the structure in routers/manifold.py::_MOCK_FRAME.

MOCK_FRAME = {
    "params": {"beta": 0.6, "adoption_pct": 0.4, "shock_intensity": 0.85},
    "frame_id": 1,
    "stampede_index_trajectory": [12, 21, 35, 52, 74, 87],
    "ai_index_trajectory":       [12, 13, 14, 16, 18, 21],
    "node_states": [
        {"id": "node_kaohsiung_port", "capacity_pct": 0.0, "is_bottleneck": True,
         "lane_price_delta": 0.0},
    ],
    "density_field_snapshot": [[0.12, 0.08], [0.15, 0.10]],
    "meta_herd_detected": False,
    "entropy_budget_active": False,
}


# ── /api/manifold/frame — status and structure ────────────────────────────────

class TestGetManifoldFrame:

    def test_returns_200_with_valid_params(self, client: TestClient):
        """Valid query parameters must yield a 200 OK."""
        response = client.get("/api/manifold/frame",
                              params={"beta": 0.6, "adoption": 0.4, "shock": 0.85})
        assert response.status_code == 200

    def test_response_is_json(self, client: TestClient):
        """Response content-type must be application/json."""
        response = client.get("/api/manifold/frame",
                              params={"beta": 0.6, "adoption": 0.0, "shock": 0.85})
        assert response.headers["content-type"].startswith("application/json")

    def test_response_contains_params_key(self, client: TestClient):
        """Top-level response must include a 'params' object."""
        response = client.get("/api/manifold/frame",
                              params={"beta": 0.6, "adoption": 0.0, "shock": 0.85})
        data = response.json()
        assert "params" in data

    def test_params_echo_query_inputs(self, client: TestClient):
        """The 'params' object must echo back the supplied beta/adoption/shock."""
        response = client.get("/api/manifold/frame",
                              params={"beta": 0.7, "adoption": 0.3, "shock": 0.9})
        params = response.json()["params"]
        assert params["beta"]           == pytest.approx(0.7)
        assert params["adoption_pct"]   == pytest.approx(0.3)
        assert params["shock_intensity"] == pytest.approx(0.9)

    # ── Schema field presence ─────────────────────────────────────────────────

    def test_mock_path_has_required_schema_fields(self, client: TestClient):
        """
        When the store is empty the mock fallback runs.
        Verify all required stampede_index.json fields are present.
        """
        with patch(
            "app.routers.manifold.manifold_store.get_frame",
            return_value=None,          # force mock path
        ):
            response = client.get("/api/manifold/frame",
                                  params={"beta": 0.6, "adoption": 0.0, "shock": 0.85})

        assert response.status_code == 200
        data = response.json()

        required_top_keys = [
            "params",
            "frame_id",
            "stampede_index_trajectory",
            "ai_index_trajectory",
            "node_states",
            "density_field_snapshot",
            "meta_herd_detected",
            "entropy_budget_active",
        ]
        for key in required_top_keys:
            assert key in data, f"Missing key '{key}' in response"

    # ── Precomputed store path ────────────────────────────────────────────────

    def test_precomputed_path_returns_frame_from_store(self, client: TestClient):
        """When get_frame() returns data the router must pass it through."""
        with patch(
            "app.routers.manifold.manifold_store.get_frame",
            return_value=MOCK_FRAME,
        ):
            response = client.get("/api/manifold/frame",
                                  params={"beta": 0.6, "adoption": 0.4, "shock": 0.85})

        assert response.status_code == 200
        data = response.json()
        assert data.get("_source") == "precomputed"
        assert data["frame_id"] == 1
        assert len(data["stampede_index_trajectory"]) == 6

    def test_precomputed_path_contains_node_states(self, client: TestClient):
        """Node states from the store must be forwarded to the client."""
        with patch(
            "app.routers.manifold.manifold_store.get_frame",
            return_value=MOCK_FRAME,
        ):
            response = client.get("/api/manifold/frame",
                                  params={"beta": 0.6, "adoption": 0.4, "shock": 0.85})

        node_states = response.json().get("node_states", [])
        assert isinstance(node_states, list)
        assert len(node_states) >= 1
        assert node_states[0]["id"] == "node_kaohsiung_port"

    # ── Query parameter validation ────────────────────────────────────────────

    def test_beta_below_minimum_returns_422(self, client: TestClient):
        """beta < 0.1 violates the ge=0.1 constraint → 422 Unprocessable Entity."""
        response = client.get("/api/manifold/frame",
                              params={"beta": 0.0, "adoption": 0.0, "shock": 0.85})
        assert response.status_code == 422

    def test_beta_above_maximum_returns_422(self, client: TestClient):
        """beta > 0.9 violates the le=0.9 constraint → 422."""
        response = client.get("/api/manifold/frame",
                              params={"beta": 1.0, "adoption": 0.0, "shock": 0.85})
        assert response.status_code == 422

    def test_adoption_above_maximum_returns_422(self, client: TestClient):
        """adoption > 0.8 violates the le=0.8 constraint → 422."""
        response = client.get("/api/manifold/frame",
                              params={"beta": 0.6, "adoption": 0.9, "shock": 0.85})
        assert response.status_code == 422

    def test_shock_below_minimum_returns_422(self, client: TestClient):
        """shock < 0.1 violates the ge=0.1 constraint → 422."""
        response = client.get("/api/manifold/frame",
                              params={"beta": 0.6, "adoption": 0.0, "shock": 0.0})
        assert response.status_code == 422

    # ── Default parameters ────────────────────────────────────────────────────

    def test_default_parameters_return_200(self, client: TestClient):
        """Calling the endpoint with no query params uses the declared defaults."""
        response = client.get("/api/manifold/frame")
        assert response.status_code == 200

    # ── Meta-herd flag ────────────────────────────────────────────────────────

    def test_meta_herd_detected_at_high_adoption(self, client: TestClient):
        """adoption > 0.6 must flip meta_herd_detected to True (mock path)."""
        with patch(
            "app.routers.manifold.manifold_store.get_frame",
            return_value=None,
        ):
            response = client.get("/api/manifold/frame",
                                  params={"beta": 0.6, "adoption": 0.7, "shock": 0.85})

        assert response.status_code == 200
        assert response.json()["meta_herd_detected"] is True

    def test_meta_herd_not_detected_at_low_adoption(self, client: TestClient):
        """adoption ≤ 0.6 must keep meta_herd_detected False (mock path)."""
        with patch(
            "app.routers.manifold.manifold_store.get_frame",
            return_value=None,
        ):
            response = client.get("/api/manifold/frame",
                                  params={"beta": 0.6, "adoption": 0.3, "shock": 0.85})

        assert response.status_code == 200
        assert response.json()["meta_herd_detected"] is False
