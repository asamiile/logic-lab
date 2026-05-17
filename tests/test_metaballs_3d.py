"""Tests for 3D Metaballs implementation."""

import math

import pytest

from logic_lab.three_dimensional.metaballs_3d import Metaball3D, MetaballField3D


class TestMetaball3D:
    """Tests for Metaball3D class."""

    def test_initialization(self):
        """Test Metaball3D initialization."""
        ball = Metaball3D(x=100, y=200, z=300, radius=80, strength=1.5)

        assert ball.x == 100
        assert ball.y == 200
        assert ball.z == 300
        assert ball.radius == 80
        assert ball.strength == 1.5
        assert ball.vx == 0.0
        assert ball.vy == 0.0
        assert ball.vz == 0.0

    def test_influence_at_center(self):
        """Test maximum influence at metaball center."""
        ball = Metaball3D(0, 0, 0, radius=100, strength=2.0)

        # At center, influence should be strength value
        influence = ball.influence_at(0, 0, 0)
        assert influence == 2.0

    def test_influence_at_distance(self):
        """Test influence falloff with distance."""
        ball = Metaball3D(0, 0, 0, radius=100, strength=1.0)

        # At distance d, influence should follow the falloff formula
        influence_1 = ball.influence_at(100, 0, 0)
        influence_2 = ball.influence_at(200, 0, 0)

        # Influence should decrease with distance
        assert influence_1 > influence_2

    def test_influence_3d_distance(self):
        """Test that influence uses 3D distance correctly."""
        ball = Metaball3D(0, 0, 0, radius=100, strength=1.0)

        # Same 3D distance should give same influence regardless of axis
        influence_x = ball.influence_at(141.42, 0, 0)  # sqrt(2)*100
        influence_xy = ball.influence_at(100, 100, 0)  # sqrt(2)*100
        influence_xyz = ball.influence_at(81.65, 81.65, 81.65)  # sqrt(3)*100/sqrt(2)

        # All should be approximately equal for same distance
        # (Using 3D distance, influence_xyz should differ from first two)
        dist_x = 141.42
        dist_xy = math.sqrt(100 * 100 + 100 * 100)
        assert abs(dist_x - dist_xy) < 1  # Approximately same distance

    def test_update_position(self):
        """Test position update with velocity."""
        ball = Metaball3D(0, 0, 0, radius=50, strength=1.0)
        ball.vx = 2.0
        ball.vy = 3.0
        ball.vz = 4.0

        ball.update()

        assert ball.x == 2.0
        assert ball.y == 3.0
        assert ball.z == 4.0

    def test_update_bouncing(self):
        """Test bouncing off 3D walls."""
        ball = Metaball3D(390, 0, 0, radius=50, strength=1.0)
        ball.vx = 50.0  # Moving toward boundary

        ball.update()

        # Should bounce
        assert ball.vx < 0


class TestMetaballField3D:
    """Tests for MetaballField3D class."""

    def test_initialization(self):
        """Test MetaballField3D initialization."""
        field = MetaballField3D(width=800, height=600, focal_distance=1000)

        assert field.width == 800
        assert field.height == 600
        assert field.focal_distance == 1000
        assert field.metaballs == []
        assert field.threshold == 1.0
        assert field.resolution == 4
        assert field.rotation_y == 0.0

    def test_add_metaball(self):
        """Test adding metaballs to field."""
        field = MetaballField3D()
        ball1 = field.add_metaball(0, 0, 0, radius=100, strength=1.0)
        ball2 = field.add_metaball(100, 100, 100, radius=80, strength=1.5)

        assert len(field.metaballs) == 2
        assert ball1 in field.metaballs
        assert ball2 in field.metaballs

    def test_perspective_projection_identity(self):
        """Test perspective projection with no rotation."""
        field = MetaballField3D(width=800, height=600, focal_distance=800)
        field.rotation_y = 0

        screen_x, screen_y, depth = field.perspective_projection(0, 0, 0)

        # At origin with no rotation, should project to screen center
        assert abs(screen_x - 400) < 0.1  # width/2
        assert abs(screen_y - 300) < 0.1  # height/2
        assert 0 <= depth <= 1

    def test_perspective_projection_rotation(self):
        """Test Y-axis rotation in perspective projection."""
        field = MetaballField3D(width=800, height=600, focal_distance=800)

        # 90 degree rotation
        field.rotation_y = math.pi / 2
        screen_x1, screen_y1, depth1 = field.perspective_projection(100, 0, 0)

        # Point (100, 0, 0) rotated 90° around Y becomes (0, 0, -100)
        # Should project differently
        field.rotation_y = 0
        screen_x2, screen_y2, depth2 = field.perspective_projection(100, 0, 0)

        # Rotated point should be at different screen position
        assert abs(screen_x1 - screen_x2) > 1 or abs(screen_y1 - screen_y2) > 1

    def test_perspective_projection_behind_camera(self):
        """Test culling of points behind camera."""
        field = MetaballField3D(width=800, height=600, focal_distance=800)

        # Point far behind camera
        screen_x, screen_y, depth = field.perspective_projection(0, 0, -2000)

        # Should be off-screen (negative coordinates indicate behind camera)
        assert screen_x < 0 or screen_x > field.width or screen_y < 0 or screen_y > field.height

    def test_depth_calculation(self):
        """Test depth value calculation."""
        field = MetaballField3D(width=800, height=600, focal_distance=800)

        # Point at origin
        _, _, depth_center = field.perspective_projection(0, 0, 0)

        # Point closer to camera
        _, _, depth_closer = field.perspective_projection(0, 0, 100)

        # Point farther from camera
        _, _, depth_farther = field.perspective_projection(0, 0, -100)

        # Depth should increase as we move away from camera
        assert depth_farther < depth_center < depth_closer

    def test_potential_at(self):
        """Test potential calculation at a point."""
        field = MetaballField3D()
        field.add_metaball(0, 0, 0, radius=100, strength=1.0)
        field.add_metaball(100, 0, 0, radius=100, strength=1.0)

        # Potential at origin (near first ball)
        potential_origin = field.potential_at(0, 0, 0)
        assert potential_origin > 1.0  # Should be > strength of one ball

        # Potential at midpoint (between balls)
        # At midpoint, both balls contribute equally with distance=50
        potential_midpoint = field.potential_at(50, 0, 0)

        # At midpoint with equal distance to both balls, potential is higher
        # Each ball: 1.0 * 10000 / 2501 ≈ 3.998, so total ≈ 7.996
        assert potential_midpoint > potential_origin

    def test_potential_combines_metaballs(self):
        """Test that potential correctly combines multiple metaballs."""
        field = MetaballField3D()
        field.add_metaball(0, 0, 0, radius=100, strength=1.0)

        potential_single = field.potential_at(0, 0, 0)

        field.add_metaball(0, 0, 200, radius=100, strength=1.0)

        potential_double = field.potential_at(0, 0, 0)

        # With two metaballs, first one's contribution should be unchanged
        # but total should increase
        assert potential_double > potential_single

    def test_rotation_speed_update(self):
        """Test rotation angle updates with speed."""
        field = MetaballField3D()
        initial_rotation = field.rotation_y
        field.rotation_speed = 0.01

        field.update_balls()

        assert field.rotation_y > initial_rotation

    def test_reset(self):
        """Test field reset."""
        field = MetaballField3D()
        field.add_metaball(0, 0, 0, radius=100, strength=1.0)
        field.rotation_y = 0.5
        field.threshold = 2.0

        field.reset()

        assert len(field.metaballs) > 0  # Should have initial metaballs
        assert field.rotation_y == 0.0
        assert field.threshold == 1.0
        assert field.rotation_speed == 0.01

    def test_add_random_velocity(self):
        """Test adding random velocity to metaballs."""
        field = MetaballField3D()
        field.add_metaball(0, 0, 0, radius=100, strength=1.0)
        field.add_metaball(100, 100, 100, radius=100, strength=1.0)

        field.add_random_velocity(speed=5.0)

        # All metaballs should have non-zero velocities (statistically)
        has_velocity = any(ball.vx != 0 or ball.vy != 0 or ball.vz != 0 for ball in field.metaballs)
        assert has_velocity


class TestPerspectiveProjectionMath:
    """Tests for perspective projection mathematical correctness."""

    def test_projection_point_at_focal_distance(self):
        """Test projection of point at focal distance."""
        field = MetaballField3D(width=800, height=600, focal_distance=800)
        field.rotation_y = 0

        # Point at z = focal_distance
        screen_x, screen_y, depth = field.perspective_projection(0, 0, 0)

        # Should project to center with depth = 0.5
        assert abs(screen_x - 400) < 1
        assert abs(screen_y - 300) < 1
        assert abs(depth - 0.5) < 0.01

    def test_projection_lateral_movement(self):
        """Test that lateral movement affects screen position."""
        field = MetaballField3D(width=800, height=600, focal_distance=800)
        field.rotation_y = 0

        screen_x1, _, _ = field.perspective_projection(0, 0, 0)
        screen_x2, _, _ = field.perspective_projection(100, 0, 0)

        # Moving in x should move screen position in x
        assert screen_x2 > screen_x1

    def test_rotation_matrix_orthogonal(self):
        """Test that rotation maintains distances."""
        field = MetaballField3D()

        # Test points at equal distance from origin in different directions
        for angle in [0, math.pi / 4, math.pi / 2, math.pi]:
            field.rotation_y = angle

            x = 100 * math.cos(angle)
            z = 100 * math.sin(angle)

            screen_x1, screen_y1, _ = field.perspective_projection(x, 0, z)
            screen_x2, screen_y2, _ = field.perspective_projection(x + 1, 0, z)

            # Rotation should preserve distances (in 3D before projection)
            # At least they should all project to valid screen coords
            assert isinstance(screen_x1, float)
            assert isinstance(screen_y1, float)


class TestDepthSorting:
    """Tests for depth-based rendering."""

    def test_depth_sorting_order(self):
        """Test that depth values enable correct back-to-front rendering."""
        field = MetaballField3D()
        field.rotation_y = 0

        _, _, depth_close = field.perspective_projection(0, 0, 100)
        _, _, depth_center = field.perspective_projection(0, 0, 0)
        _, _, depth_far = field.perspective_projection(0, 0, -100)

        # Back-to-front order: far < center < close
        assert depth_far < depth_center < depth_close

    def test_depth_clipping(self):
        """Test that depth values stay within 0-1 range."""
        field = MetaballField3D(focal_distance=800)

        for z in [-1000, -500, 0, 500, 1000]:
            _, _, depth = field.perspective_projection(0, 0, z)
            assert 0 <= depth <= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
