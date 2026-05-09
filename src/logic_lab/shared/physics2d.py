"""Small reusable 2D physics primitives for creative-coding sketches.

The module keeps simulation logic independent from py5 so sketches can reuse
and test the same dynamics without a drawing context.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from math import cos, hypot, sin
from random import Random

EPSILON = 1.0e-9


@dataclass(slots=True)
class Vec2:
    x: float = 0.0
    y: float = 0.0

    def __add__(self, other: Vec2) -> Vec2:
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vec2) -> Vec2:
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> Vec2:
        return Vec2(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> Vec2:
        return self * scalar

    def __truediv__(self, scalar: float) -> Vec2:
        if abs(scalar) < EPSILON:
            return Vec2()
        return Vec2(self.x / scalar, self.y / scalar)

    def copy(self) -> Vec2:
        return Vec2(self.x, self.y)

    def dot(self, other: Vec2) -> float:
        return self.x * other.x + self.y * other.y

    def mag_sq(self) -> float:
        return self.x * self.x + self.y * self.y

    def mag(self) -> float:
        return hypot(self.x, self.y)

    def normalized(self) -> Vec2:
        length = self.mag()
        if length < EPSILON:
            return Vec2()
        return self / length

    def limit(self, max_length: float) -> Vec2:
        length_sq = self.mag_sq()
        if length_sq <= max_length * max_length:
            return self.copy()
        return self.normalized() * max_length

    def perp(self) -> Vec2:
        return Vec2(-self.y, self.x)

    @classmethod
    def from_angle(cls, angle: float, length: float = 1.0) -> Vec2:
        return cls(cos(angle) * length, sin(angle) * length)


@dataclass(slots=True)
class Particle:
    pos: Vec2
    vel: Vec2 = field(default_factory=Vec2)
    acc: Vec2 = field(default_factory=Vec2)
    mass: float = 1.0
    radius: float = 4.0
    damping: float = 0.99
    fixed: bool = False
    age: float = 0.0
    lifespan: float | None = None

    def apply_force(self, force: Vec2) -> None:
        if not self.fixed:
            self.acc = self.acc + force / max(self.mass, EPSILON)

    def step(self, dt: float) -> None:
        if self.fixed:
            self.acc = Vec2()
            self.vel = Vec2()
            return
        self.vel = (self.vel + self.acc * dt) * self.damping
        self.pos = self.pos + self.vel * dt
        self.acc = Vec2()
        self.age += dt

    def alive(self) -> bool:
        return self.lifespan is None or self.age <= self.lifespan


@dataclass(slots=True)
class VerletPoint:
    pos: Vec2
    prev: Vec2
    acc: Vec2 = field(default_factory=Vec2)
    radius: float = 3.0
    fixed: bool = False

    @classmethod
    def at(cls, x: float, y: float, fixed: bool = False, radius: float = 3.0) -> VerletPoint:
        pos = Vec2(x, y)
        return cls(pos=pos, prev=pos.copy(), fixed=fixed, radius=radius)

    def apply_force(self, force: Vec2) -> None:
        if not self.fixed:
            self.acc = self.acc + force

    def step(self, dt: float, damping: float = 0.995) -> None:
        if self.fixed:
            self.prev = self.pos.copy()
            self.acc = Vec2()
            return
        velocity = (self.pos - self.prev) * damping
        self.prev = self.pos.copy()
        self.pos = self.pos + velocity + self.acc * (dt * dt)
        self.acc = Vec2()


@dataclass(slots=True)
class DistanceConstraint:
    a: VerletPoint
    b: VerletPoint
    length: float
    stiffness: float = 1.0

    def solve(self) -> None:
        delta = self.b.pos - self.a.pos
        distance = delta.mag()
        if distance < EPSILON:
            return
        difference = (distance - self.length) / distance
        correction = delta * (0.5 * self.stiffness * difference)
        if self.a.fixed and self.b.fixed:
            return
        if self.a.fixed:
            self.b.pos = self.b.pos - correction * 2.0
        elif self.b.fixed:
            self.a.pos = self.a.pos + correction * 2.0
        else:
            self.a.pos = self.a.pos + correction
            self.b.pos = self.b.pos - correction


@dataclass(slots=True)
class Spring:
    a: Particle
    b: Particle
    rest_length: float
    stiffness: float = 0.2
    damping: float = 0.02

    def apply(self) -> None:
        delta = self.b.pos - self.a.pos
        distance = delta.mag()
        if distance < EPSILON:
            return
        normal = delta / distance
        stretch = distance - self.rest_length
        relative_velocity = self.b.vel - self.a.vel
        force_mag = self.stiffness * stretch + self.damping * relative_velocity.dot(normal)
        force = normal * force_mag
        self.a.apply_force(force)
        self.b.apply_force(force * -1.0)


@dataclass(slots=True)
class CircleBody:
    pos: Vec2
    vel: Vec2
    radius: float
    mass: float = 1.0
    restitution: float = 0.9
    friction: float = 0.0
    spin: float = 0.0
    angle: float = 0.0

    def step(self, dt: float, gravity: Vec2 = Vec2()) -> None:
        self.vel = self.vel + gravity * dt
        self.vel = self.vel * max(0.0, 1.0 - self.friction * dt)
        self.pos = self.pos + self.vel * dt
        self.angle += self.spin * dt


@dataclass(frozen=True, slots=True)
class CollisionEvent:
    point: Vec2
    normal: Vec2
    impulse: float


def resolve_circle_collision(a: CircleBody, b: CircleBody) -> CollisionEvent | None:
    delta = b.pos - a.pos
    distance = delta.mag()
    min_distance = a.radius + b.radius
    if distance >= min_distance or distance < EPSILON:
        return None

    normal = delta / distance
    penetration = min_distance - distance
    total_mass = a.mass + b.mass
    a.pos = a.pos - normal * (penetration * (b.mass / total_mass))
    b.pos = b.pos + normal * (penetration * (a.mass / total_mass))

    relative_velocity = b.vel - a.vel
    velocity_along_normal = relative_velocity.dot(normal)
    if velocity_along_normal > 0:
        return CollisionEvent(a.pos + normal * a.radius, normal, 0.0)

    restitution = min(a.restitution, b.restitution)
    impulse_mag = -(1.0 + restitution) * velocity_along_normal
    impulse_mag /= (1.0 / a.mass) + (1.0 / b.mass)
    impulse = normal * impulse_mag
    a.vel = a.vel - impulse / a.mass
    b.vel = b.vel + impulse / b.mass
    return CollisionEvent(a.pos + normal * a.radius, normal, impulse_mag)


def resolve_bounds(
    body: CircleBody,
    width: float,
    height: float,
    restitution: float | None = None,
) -> CollisionEvent | None:
    bounce = body.restitution if restitution is None else restitution
    event: CollisionEvent | None = None
    if body.pos.x < body.radius:
        body.pos.x = body.radius
        body.vel.x = abs(body.vel.x) * bounce
        event = CollisionEvent(body.pos.copy(), Vec2(1, 0), abs(body.vel.x) * body.mass)
    elif body.pos.x > width - body.radius:
        body.pos.x = width - body.radius
        body.vel.x = -abs(body.vel.x) * bounce
        event = CollisionEvent(body.pos.copy(), Vec2(-1, 0), abs(body.vel.x) * body.mass)

    if body.pos.y < body.radius:
        body.pos.y = body.radius
        body.vel.y = abs(body.vel.y) * bounce
        event = CollisionEvent(body.pos.copy(), Vec2(0, 1), abs(body.vel.y) * body.mass)
    elif body.pos.y > height - body.radius:
        body.pos.y = height - body.radius
        body.vel.y = -abs(body.vel.y) * bounce
        event = CollisionEvent(body.pos.copy(), Vec2(0, -1), abs(body.vel.y) * body.mass)
    return event


def gravity_force(strength: float) -> Vec2:
    return Vec2(0.0, strength)


def drag_force(particle: Particle, coefficient: float) -> Vec2:
    speed_sq = particle.vel.mag_sq()
    if speed_sq < EPSILON:
        return Vec2()
    return particle.vel.normalized() * (-coefficient * speed_sq)


def radial_force(point: Vec2, center: Vec2, strength: float, min_distance: float = 8.0) -> Vec2:
    delta = center - point
    distance = max(delta.mag(), min_distance)
    return delta.normalized() * (strength / (distance * distance))


def vortex_force(point: Vec2, center: Vec2, strength: float, min_distance: float = 12.0) -> Vec2:
    delta = point - center
    distance = max(delta.mag(), min_distance)
    return delta.perp().normalized() * (strength / distance)


def build_cloth(
    columns: int,
    rows: int,
    spacing: float,
    origin: Vec2,
    fixed_top: bool = True,
) -> tuple[list[VerletPoint], list[DistanceConstraint]]:
    points: list[VerletPoint] = []
    constraints: list[DistanceConstraint] = []
    for y in range(rows):
        for x in range(columns):
            points.append(
                VerletPoint.at(
                    origin.x + x * spacing,
                    origin.y + y * spacing,
                    fixed=fixed_top and y == 0 and x % 3 == 0,
                    radius=2.5,
                )
            )
    for y in range(rows):
        for x in range(columns):
            idx = y * columns + x
            if x < columns - 1:
                constraints.append(DistanceConstraint(points[idx], points[idx + 1], spacing, 0.9))
            if y < rows - 1:
                constraints.append(
                    DistanceConstraint(points[idx], points[idx + columns], spacing, 0.9)
                )
    return points, constraints


def enforce_verlet_bounds(points: Iterable[VerletPoint], width: float, height: float) -> None:
    for point in points:
        if point.fixed:
            continue
        point.pos.x = min(max(point.radius, point.pos.x), width - point.radius)
        point.pos.y = min(max(point.radius, point.pos.y), height - point.radius)


def spawn_particles(
    count: int,
    center: Vec2,
    rng: Random,
    speed_range: tuple[float, float] = (40.0, 160.0),
    radius_range: tuple[float, float] = (2.0, 5.0),
    lifespan: float | None = None,
) -> list[Particle]:
    particles: list[Particle] = []
    for _ in range(count):
        angle = rng.random() * 6.283185307179586
        speed = rng.uniform(*speed_range)
        radius = rng.uniform(*radius_range)
        particles.append(
            Particle(
                pos=center.copy(),
                vel=Vec2.from_angle(angle, speed),
                mass=radius,
                radius=radius,
                damping=0.995,
                lifespan=lifespan,
            )
        )
    return particles


def apply_density_pressure(
    particles: list[Particle],
    interaction_radius: float,
    pressure: float,
    viscosity: float,
) -> None:
    radius_sq = interaction_radius * interaction_radius
    for i, a in enumerate(particles):
        for b in particles[i + 1 :]:
            delta = b.pos - a.pos
            distance_sq = delta.mag_sq()
            if distance_sq <= EPSILON or distance_sq > radius_sq:
                continue
            distance = distance_sq**0.5
            normal = delta / distance
            overlap = 1.0 - distance / interaction_radius
            push = normal * (pressure * overlap)
            a.apply_force(push * -1.0)
            b.apply_force(push)
            relative = b.vel - a.vel
            viscous = relative * (viscosity * overlap)
            a.apply_force(viscous)
            b.apply_force(viscous * -1.0)
