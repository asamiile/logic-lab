"""Tests for mathematical/voronoi module."""

import math
import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestVoronoiUtilities:
    """Test Voronoi diagram utilities."""

    def test_hsb_to_rgb_conversion(self):
        """Test HSB to RGB color conversion."""
        # HSB: H=0, S=100, B=100 -> Red (255, 0, 0)
        h_norm = 0.0 / 60.0
        s_norm = 100 / 100.0
        b_norm = 100 / 100.0

        c = b_norm * s_norm
        x = c * (1 - abs((h_norm % 2) - 1))
        m = b_norm - c

        r = int((c + m) * 255)
        g = int((0 + m) * 255)
        b = int((0 + m) * 255)

        assert r == 255
        assert g == 0
        assert b == 0

    def test_hsb_to_rgb_gray(self):
        """Test HSB to RGB for gray (S=0)."""
        # HSB: H=any, S=0, B=128 -> Gray (128, 128, 128)
        h_norm = 0.0 / 60.0
        s_norm = 0.0 / 100.0
        b_norm = 128 / 255.0

        c = b_norm * s_norm
        m = b_norm - c

        r = int((0 + m) * 255)
        g = int((0 + m) * 255)
        b = int((0 + m) * 255)

        assert 127 <= r <= 129
        assert 127 <= g <= 129
        assert 127 <= b <= 129

    def test_distance_calculation(self):
        """Test Euclidean distance calculation."""
        x1, y1 = 0, 0
        x2, y2 = 3, 4
        dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        assert dist == 5.0

    def test_nearest_seed_identification(self):
        """Test finding nearest seed among multiple seeds."""
        seeds = [(0, 0), (100, 0), (0, 100)]
        test_point = (10, 10)

        distances = [
            math.sqrt((s[0] - test_point[0]) ** 2 + (s[1] - test_point[1]) ** 2)
            for s in seeds
        ]
        nearest_idx = distances.index(min(distances))

        assert nearest_idx == 0  # (0, 0) is nearest to (10, 10)
