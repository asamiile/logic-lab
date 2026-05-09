from logic_lab.shared.physics2d import (
    CircleBody,
    DistanceConstraint,
    Vec2,
    VerletPoint,
    resolve_circle_collision,
)


def test_vec2_normalized_zero_is_zero() -> None:
    assert Vec2().normalized() == Vec2()


def test_distance_constraint_restores_length() -> None:
    a = VerletPoint.at(0, 0)
    b = VerletPoint.at(20, 0)
    constraint = DistanceConstraint(a, b, length=10, stiffness=1)

    constraint.solve()

    assert round((b.pos - a.pos).mag(), 6) == 10


def test_circle_collision_exchanges_velocity_direction() -> None:
    a = CircleBody(pos=Vec2(0, 0), vel=Vec2(10, 0), radius=10, mass=1)
    b = CircleBody(pos=Vec2(18, 0), vel=Vec2(-10, 0), radius=10, mass=1)

    event = resolve_circle_collision(a, b)

    assert event is not None
    assert a.vel.x < 0
    assert b.vel.x > 0
