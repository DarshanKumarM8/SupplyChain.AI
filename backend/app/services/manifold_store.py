"""
Manifold Store — In-Memory Precomputed Frame Server
=====================================================

Loads precomputed manifold JSON frames into RAM for instant lookup.
Provides O(1) frame retrieval by snapping (β, adoption, shock) to nearest grid point.

Usage::

    # Load on construction (preferred)
    store = ManifoldStore(data_dir="/app/data/manifold")

    # Or load lazily after construction
    store = ManifoldStore()
    store.load_from_directory("/app/data/manifold")
"""

import json
import os
import glob
from typing import Optional


class ManifoldStore:
    """In-memory manifold frame lookup indexed by parameter tuples."""

    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialise the store.

        Args:
            data_dir: Path to a directory containing ``frame_*.json`` files.
                      When supplied the store is populated immediately at
                      construction time so callers need no extra step.
        """
        self._frames: dict[tuple[float, float, float], dict] = {}
        self._grid_points: list[tuple[float, float, float]] = []

        if data_dir is not None:
            self.load_from_directory(data_dir)

    def load_from_directory(self, directory: str) -> int:
        """
        Load all manifold frame JSON files from a directory.
        Returns number of frames loaded.
        """
        count = 0
        pattern = os.path.join(directory, "frame_*.json")
        for filepath in sorted(glob.glob(pattern)):
            with open(filepath, 'r') as f:
                frame = json.load(f)
            params = frame.get("params", {})
            key = (params.get("beta", 0), params.get("adoption_pct", 0), params.get("shock_intensity", 0))
            self._frames[key] = frame
            self._grid_points.append(key)
            count += 1
        print(f"ManifoldStore: loaded {count} frames from {directory}")
        return count

    def get_frame(self, beta: float, adoption: float, shock: float) -> Optional[dict]:
        """
        Retrieve the nearest precomputed manifold frame.
        Snaps to closest grid point by Euclidean distance.
        """
        if not self._frames:
            return None

        # Find nearest grid point
        target = (beta, adoption, shock)
        nearest = min(self._grid_points, key=lambda p: sum((a - b) ** 2 for a, b in zip(p, target)))
        return self._frames.get(nearest)

    @property
    def frame_count(self) -> int:
        return len(self._frames)


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------
# Constructed without a directory so it starts empty; the FastAPI startup
# event in main.py calls load_from_directory() (or reconstructs with
# data_dir=) once the config path is known at runtime.
manifold_store = ManifoldStore()
