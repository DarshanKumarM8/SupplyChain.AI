"""
Manifold Store — In-Memory Precomputed Frame Server
=====================================================

Loads precomputed manifold JSON frames into RAM for instant lookup.
Provides O(1) frame retrieval by snapping (β, adoption, shock) to nearest grid point.
"""

import json
import os
import glob
from typing import Optional


class ManifoldStore:
    """In-memory manifold frame lookup indexed by parameter tuples."""

    def __init__(self):
        self._frames: dict[tuple[float, float, float], dict] = {}
        self._grid_points: list[tuple[float, float, float]] = []

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


# Singleton instance
manifold_store = ManifoldStore()
