"""Tests for mathematical/metaball module."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from logic_lab.mathematical.metaball.metaball import Metaball


class TestMetaball:
    """Test Metaball class and influence calculations."""

    def test_metaball_initialization(self):
        """Test Metaball object creation."""
        ball = Metaball(100, 150, radius=50)
        assert ball.x == 100
        assert ball.y == 150
        assert ball.radius == 50

    def test_metaball_default_radius(self):
        """Test Metaball default radius."""
        ball = Metaball(0, 0)
        assert ball.radius == 50

    def test_influence_at_center(self):
        """Test influence calculation at ball center (should be inf)."""
        ball = Metaball(100, 100, radius=50)
        influence = ball.influence(100, 100)
        assert influence == float("inf")

    def test_influence_at_distance(self):
        """Test influence calculation at known distance."""
        ball = Metaball(0, 0, radius=10)
        # Distance = 5, influence = r² / d² = 100 / 25 = 4
        influence = ball.influence(5, 0)
        assert abs(influence - 4.0) < 0.01

    def test_influence_far_away(self):
        """Test influence drops with distance."""
        ball = Metaball(0, 0, radius=10)
        inf_close = ball.influence(5, 0)
        inf_far = ball.influence(50, 0)
        assert inf_close > inf_far

    def test_contains_near_ball(self):
        """Test contains method for nearby points."""
        ball = Metaball(100, 100, radius=20)
        # Should contain points within radius+10
        assert ball.contains(105, 100)

    def test_contains_outside_ball(self):
        """Test contains method for distant points."""
        ball = Metaball(100, 100, radius=20)
        # Should not contain distant points
        assert not ball.contains(200, 200)

    def test_influence_symmetry(self):
        """Test that influence is symmetric around center."""
        ball = Metaball(100, 100, radius=10)
        inf_right = ball.influence(110, 100)
        inf_left = ball.influence(90, 100)
        assert abs(inf_right - inf_left) < 0.0001

    def test_influence_with_different_radii(self):
        """Test influence scales correctly with radius."""
        ball1 = Metaball(0, 0, radius=10)
        ball2 = Metaball(0, 0, radius=20)
        # Both at distance 5
        inf1 = ball1.influence(5, 0)
        inf2 = ball2.influence(5, 0)
        # ball2 should have 4x influence (radius² scales quadratically)
        assert abs(inf2 - inf1 * 4) < 0.01
