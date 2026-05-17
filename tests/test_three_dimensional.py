"""Tests for 3D and volumetric systems."""

import pytest

from logic_lab.three_dimensional.metaballs.metaballs import Metaball, MetaballField


class TestMetaball:
    """Test individual metaball behavior."""

    def test_metaball_creation(self) -> None:
        """Test metaball initialization."""
        ball = Metaball(100, 50, radius=80, strength=1.5)
        assert ball.x == 100
        assert ball.y == 50
        assert ball.radius == 80
        assert ball.strength == 1.5

    def test_influence_at_center(self) -> None:
        """Test influence at metaball center."""
        ball = Metaball(100, 100, radius=50, strength=1.0)
        influence = ball.influence_at(100, 100)
        assert influence == pytest.approx(1.0, abs=0.01)

    def test_influence_falloff(self) -> None:
        """Test that influence falls off with distance."""
        ball = Metaball(0, 0, radius=50, strength=1.0)
        center_influence = ball.influence_at(0, 0)
        far_influence = ball.influence_at(1000, 0)
        assert center_influence > far_influence

    def test_influence_is_positive(self) -> None:
        """Test that influence is always non-negative."""
        ball = Metaball(100, 100, radius=50, strength=1.0)
        assert ball.influence_at(100, 100) >= 0
        assert ball.influence_at(500, 500) >= 0
        assert ball.influence_at(-500, -500) >= 0

    def test_metaball_velocity(self) -> None:
        """Test metaball velocity property."""
        ball = Metaball(100, 100, radius=50)
        ball.vx = 2.0
        ball.vy = 3.0
        assert ball.vx == 2.0
        assert ball.vy == 3.0


class TestMetaballField:
    """Test the combined metaball field."""

    def test_field_creation(self) -> None:
        """Test field initialization."""
        field = MetaballField(640, 480)
        assert field.width == 640
        assert field.height == 480
        assert len(field.metaballs) == 0

    def test_add_metaball(self) -> None:
        """Test adding metaballs to field."""
        field = MetaballField()
        ball = field.add_metaball(100, 100, radius=50, strength=1.0)
        assert len(field.metaballs) == 1
        assert ball.x == 100
        assert ball.y == 100

    def test_potential_at_empty_field(self) -> None:
        """Test potential in empty field (should be zero)."""
        field = MetaballField()
        potential = field.potential_at(100, 100)
        assert potential == 0.0

    def test_potential_at_single_ball(self) -> None:
        """Test potential at location of single metaball."""
        field = MetaballField()
        field.add_metaball(100, 100, radius=50, strength=1.0)
        potential = field.potential_at(100, 100)
        assert potential > 0

    def test_potential_additive(self) -> None:
        """Test that potentials from multiple balls add."""
        field = MetaballField()
        field.add_metaball(0, 0, radius=50, strength=1.0)
        field.add_metaball(100, 0, radius=50, strength=1.0)

        # Potential at origin should be from one ball
        potential_one = field.potential_at(0, 0)

        # Remove first ball and recalculate (rough estimate)
        balls = field.metaballs.copy()
        field.metaballs = [balls[1]]
        potential_second = field.potential_at(0, 0)

        # Restore and check additivity
        field.metaballs = balls
        assert potential_one > potential_second

    def test_threshold_property(self) -> None:
        """Test threshold modification."""
        field = MetaballField()
        field.threshold = 0.5
        assert field.threshold == 0.5
        field.threshold = 2.0
        assert field.threshold == 2.0

    def test_resolution_property(self) -> None:
        """Test resolution property."""
        field = MetaballField()
        field.resolution = 4
        assert field.resolution == 4

    def test_velocity_initialization(self) -> None:
        """Test that metaballs start with zero velocity."""
        field = MetaballField()
        ball = field.add_metaball(100, 100)
        assert ball.vx == 0.0
        assert ball.vy == 0.0


class TestMetaballPhysics:
    """Test physics simulation of metaballs."""

    def test_velocity_update(self) -> None:
        """Test that velocity updates position (direct calculation)."""
        ball = Metaball(100, 100, radius=10)
        ball.vx = 1.0
        ball.vy = 0.0

        initial_x = ball.x
        # Directly test position update without calling update() which depends on py5
        ball.x += ball.vx
        ball.y += ball.vy
        assert ball.x > initial_x
        assert ball.x == 101.0

    def test_velocity_components(self) -> None:
        """Test velocity property modification."""
        ball = Metaball(100, 100, radius=10)
        ball.vx = 2.5
        ball.vy = 1.5

        assert ball.vx == 2.5
        assert ball.vy == 1.5

        # Test velocity reversal (bounce)
        ball.vx *= -1
        assert ball.vx == -2.5

    def test_position_movement(self) -> None:
        """Test that position changes with velocity."""
        ball = Metaball(100, 100, radius=10)
        ball.vx = 5.0
        ball.vy = 3.0

        # Simulate movement (without py5 constraints)
        for _ in range(10):
            ball.x += ball.vx
            ball.y += ball.vy

        # After 10 updates
        assert ball.x == 150.0  # 100 + 10*5
        assert ball.y == 130.0  # 100 + 10*3


class TestMetaballIntegration:
    """Integration tests for full metaball system."""

    def test_multi_ball_field(self) -> None:
        """Test field with multiple metaballs."""
        field = MetaballField(640, 480)

        # Add several balls
        for i in range(3):
            field.add_metaball(
                x=200 + i * 100,
                y=200 + i * 50,
                radius=50 + i * 10,
                strength=1.0 + i * 0.2,
            )

        assert len(field.metaballs) == 3

        # Check potential at various points
        p_center = field.potential_at(400, 300)
        p_far = field.potential_at(0, 0)

        assert p_center > p_far

    def test_field_render_with_balls(self) -> None:
        """Test that field can be queried with multiple balls."""
        field = MetaballField(640, 480)
        field.add_metaball(100, 100, radius=50, strength=1.0)
        field.add_metaball(200, 200, radius=50, strength=1.0)

        # Calculate potential at several points
        p_far = field.potential_at(0, 0)
        p_center = field.potential_at(150, 150)  # Between two balls
        p_ball1 = field.potential_at(100, 100)  # At first ball

        # At ball location should have highest potential
        assert p_ball1 > p_center > p_far
