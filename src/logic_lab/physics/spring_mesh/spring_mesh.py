import math
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

# Physics parameters
gravity = py5.Py5Vector(0, 0.2)
damping = 0.99
spring_constant = 0.15
spring_rest_length = 20
mouse_radius = 30

# Mesh grid
grid_cols = 20
grid_rows = 15
particles = []
springs = []

# State
selected_particle = None
wireframe_mode = True

# Mouse tracking
mouse_x = 0
mouse_y = 0
mouse_is_pressed = False


class Particle:
    def __init__(self, x: float, y: float, pinned: bool = False):
        self.pos = py5.Py5Vector(x, y)
        self.old_pos = py5.Py5Vector(x, y)
        self.vel = py5.Py5Vector(0, 0)
        self.acc = py5.Py5Vector(0, 0)
        self.pinned = pinned
        self.radius = 4

    def apply_force(self, force: py5.Py5Vector) -> None:
        self.acc += force

    def update(self) -> None:
        if self.pinned:
            return

        # Verlet integration
        self.vel = (self.pos - self.old_pos) * damping
        self.old_pos = py5.Py5Vector(self.pos.x, self.pos.y)
        self.pos += self.vel
        self.pos += self.acc

        # Apply gravity
        self.apply_force(gravity)

        # Reset acceleration
        self.acc = py5.Py5Vector(0, 0)

        # Boundary constraints
        if self.pos.x < 0:
            self.pos.x = 0
        if self.pos.x > py5.width:
            self.pos.x = py5.width
        if self.pos.y < 0:
            self.pos.y = 0
        if self.pos.y > py5.height:
            self.pos.y = py5.height

    def constrain_to(self, x: float, y: float) -> None:
        self.pos = py5.Py5Vector(x, y)
        self.old_pos = py5.Py5Vector(self.pos.x, self.pos.y)


class Spring:
    def __init__(self, p1: Particle, p2: Particle):
        self.p1 = p1
        self.p2 = p2
        self.rest_length = p1.pos.dist(p2.pos)

    def apply_constraint(self) -> None:
        # Spring constraint
        delta = self.p2.pos - self.p1.pos
        dist = delta.mag

        if dist == 0:
            return

        # Hooke's law
        correction = (dist - self.rest_length) / dist
        offset = delta * (correction * spring_constant * 0.5)

        if not self.p1.pinned:
            self.p1.pos += offset
        if not self.p2.pinned:
            self.p2.pos -= offset


def setup() -> None:
    global particles, springs
    py5.size(800, 600)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    # Create particle grid
    spacing_x = py5.width / (grid_cols - 1)
    spacing_y = py5.height / (grid_rows - 1)

    for y in range(grid_rows):
        for x in range(grid_cols):
            px = x * spacing_x
            py_val = y * spacing_y
            pinned = y == 0  # Top row is pinned
            particles.append(Particle(px, py_val, pinned))

    # Create springs
    for y in range(grid_rows):
        for x in range(grid_cols):
            idx = y * grid_cols + x

            # Horizontal springs
            if x < grid_cols - 1:
                springs.append(Spring(particles[idx], particles[idx + 1]))

            # Vertical springs
            if y < grid_rows - 1:
                springs.append(Spring(particles[idx], particles[idx + grid_cols]))


def draw() -> None:
    global selected_particle, particles, springs, mouse_x, mouse_y, mouse_is_pressed
    py5.background(250)

    # Update physics
    for particle in particles:
        particle.update()

    # Apply spring constraints multiple times for stability
    for _ in range(3):
        for spring in springs:
            spring.apply_constraint()

    # Handle mouse interaction
    if mouse_is_pressed:
        closest = None
        closest_dist = mouse_radius

        for particle in particles:
            d = math.sqrt((particle.pos.x - mouse_x) ** 2 + (particle.pos.y - mouse_y) ** 2)
            if d < closest_dist:
                closest = particle
                closest_dist = d

        selected_particle = closest
        if selected_particle:
            selected_particle.constrain_to(mouse_x, mouse_y)
    else:
        selected_particle = None

    # Draw springs (wireframe)
    py5.stroke(150)
    py5.stroke_weight(1)
    py5.no_fill()

    if wireframe_mode:
        for y in range(grid_rows - 1):
            py5.begin_shape(py5.QUAD_STRIP)
            for x in range(grid_cols):
                idx = y * grid_cols + x
                p1 = particles[idx]
                p2 = particles[idx + grid_cols]
                py5.vertex(p1.pos.x, p1.pos.y)
                py5.vertex(p2.pos.x, p2.pos.y)
            py5.end_shape()
    else:
        # Filled mesh
        py5.stroke(100)
        py5.fill(200, 220, 255, 100)
        for y in range(grid_rows - 1):
            py5.begin_shape(py5.QUAD_STRIP)
            for x in range(grid_cols):
                idx = y * grid_cols + x
                p1 = particles[idx]
                p2 = particles[idx + grid_cols]
                py5.vertex(p1.pos.x, p1.pos.y)
                py5.vertex(p2.pos.x, p2.pos.y)
            py5.end_shape()

    # Draw particles
    py5.fill(50)
    py5.no_stroke()
    for particle in particles:
        if particle == selected_particle:
            py5.fill(255, 0, 0)
        else:
            py5.fill(50)
        py5.ellipse(particle.pos.x, particle.pos.y, particle.radius * 2, particle.radius * 2)

    # Draw info
    py5.fill(0)
    py5.text(
        f"w: wireframe {'ON' if wireframe_mode else 'OFF'} | Click: drag mesh | s: save", 10, 20
    )


def mouse_pressed() -> None:
    global mouse_x, mouse_y, mouse_is_pressed
    mouse_x = py5.mouse_x
    mouse_y = py5.mouse_y
    mouse_is_pressed = True


def mouse_dragged() -> None:
    global mouse_x, mouse_y
    mouse_x = py5.mouse_x
    mouse_y = py5.mouse_y


def mouse_released() -> None:
    global mouse_is_pressed
    mouse_is_pressed = False


def key_pressed() -> None:
    global wireframe_mode
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "spring_mesh_####.png"))
    elif py5.key == "w":
        wireframe_mode = not wireframe_mode


py5.run_sketch()
