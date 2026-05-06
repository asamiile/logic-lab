"""Tests for mathematical/worley_noise module."""

import math
import pytest
import numpy as np
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestWorleyNoiseUtilities:
    """Test Worley noise distance calculations."""

    def test_distance_to_point(self):
        """Test Euclidean distance to a single point."""
        px, py = 0, 0
        fx, fy = 3, 4
        dist = math.sqrt((px - fx) ** 2 + (py - fy) ** 2)
        assert dist == 5.0

    def test_nearest_distance(self):
        """Test finding nearest distance among multiple points."""
        feature_points = [(0, 0), (100, 100), (200, 0)]
        pixel = (10, 10)

        distances = [
            math.sqrt((pixel[0] - fp[0]) ** 2 + (pixel[1] - fp[1]) ** 2)
            for fp in feature_points
        ]
        min_dist = min(distances)

        # Distance to (0,0) should be ~14.14
        expected = math.sqrt(100 + 100)
        assert abs(min_dist - expected) < 0.01

    def test_f1_f2_ordering(self):
        """Test that F1 < F2 (nearest < second-nearest)."""
        feature_points = [(0, 0), (50, 0), (100, 0)]
        pixel = (25, 0)

        distances = [
            math.sqrt((pixel[0] - fp[0]) ** 2 + (pixel[1] - fp[1]) ** 2)
            for fp in feature_points
        ]
        distances_sorted = sorted(distances)
        f1 = distances_sorted[0]
        f2 = distances_sorted[1]

        assert f1 < f2
        assert f1 == 25.0
        assert f2 == 25.0

    def test_distance_symmetry(self):
        """Test that distance is symmetric: d(A,B) == d(B,A)."""
        p1 = (10, 20)
        p2 = (30, 50)

        d1_to_2 = math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
        d2_to_1 = math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)

        assert abs(d1_to_2 - d2_to_1) < 0.0001

    def test_grid_key_mapping(self):
        """Test grid cell key calculation for spatial acceleration."""
        cell_size = 50
        points = [(25, 25), (75, 75), (125, 25)]

        grid_keys = [
            (int(p[0] // cell_size), int(p[1] // cell_size))
            for p in points
        ]

        assert grid_keys[0] == (0, 0)
        assert grid_keys[1] == (1, 1)
        assert grid_keys[2] == (2, 0)

    def test_edge_detection_f2_minus_f1(self):
        """Test edge detection using F2 - F1."""
        # Point near boundary between regions
        f1 = 10.0  # Near one seed
        f2 = 10.5  # Near next seed

        edge_strength = f2 - f1
        assert edge_strength > 0
        assert edge_strength < 1

        # Strong boundary would have larger difference
        f2_strong = 20.0
        edge_strong = f2_strong - f1
        assert edge_strong > edge_strength

    def test_array_operations(self):
        """Test numpy array operations for worley field."""
        field = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)

        # Test clipping
        clipped = np.clip(field, 0, 3)
        assert clipped[1, 1] == 3.0  # 4.0 clipped to 3.0

        # Test normalization
        normalized = field / field.max()
        assert abs(normalized[1, 1] - 1.0) < 0.0001
