from logic_lab.shared.physics2d import (
    CircleBody,
    DistanceConstraint,
    SpatialHash,
    Vec2,
    VerletPoint,
    ray_segment_intersection,
    rectangle_vertices,
    resolve_circle_collision,
    sat_collision,
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


def test_sat_collision_detects_overlapping_rectangles() -> None:
    a = rectangle_vertices(10, 10)
    b = [vertex + Vec2(5, 0) for vertex in rectangle_vertices(10, 10)]

    result = sat_collision(a, b)

    assert result.overlaps
    assert result.depth > 0


def test_spatial_hash_reports_potential_pair() -> None:
    grid = SpatialHash(cell_size=20)
    grid.insert_circle(0, Vec2(10, 10), 5)
    grid.insert_circle(1, Vec2(14, 14), 5)

    assert (0, 1) in grid.potential_pairs()


def test_ray_segment_intersection_returns_nearest_hit_data() -> None:
    hit = ray_segment_intersection(Vec2(0, 0), Vec2(1, 0), Vec2(5, -2), Vec2(5, 2))

    assert hit is not None
    assert hit.point == Vec2(5, 0)
    assert hit.distance == 5
