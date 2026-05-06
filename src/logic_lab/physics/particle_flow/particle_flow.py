import math
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

# Particle system
particles = []
particle_count = 5000
time_offset = 0

# Mouse tracking
mouse_x = 0
mouse_y = 0
mouse_is_pressed = False

# Visualization mode
vis_mode = 0  # 0: trails, 1: velocity colors, 2: lifetime colors


class Particle:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.lifetime = 0.0
        self.max_lifetime = 255

    def update(self, time_offset: float):
        """Update particle based on velocity field."""
        # Perlin noise-based velocity field
        angle = py5.noise(self.x * 0.01, self.y * 0.01, time_offset * 0.1) * 2 * math.pi
        mag = py5.noise(self.x * 0.005, self.y * 0.005 + 100, time_offset * 0.1) * 2
        self.vx = math.cos(angle) * mag
        self.vy = math.sin(angle) * mag

        # Mouse repulsion/attraction (access globals directly)
        global mouse_x, mouse_y, mouse_is_pressed
        if mouse_is_pressed:
            dx = self.x - mouse_x
            dy = self.y - mouse_y
            dist = math.sqrt(dx * dx + dy * dy) + 1
            if dist < 150:
                force = (1 - dist / 150) * 0.5
                self.vx += (dx / dist) * force
                self.vy += (dy / dist) * force

        # Update position
        self.x += self.vx
        self.y += self.vy
        self.lifetime += 2

        # Wrap around boundaries
        w, h = py5.width, py5.height
        if self.x < 0:
            self.x += w
        elif self.x >= w:
            self.x -= w
        if self.y < 0:
            self.y += h
        elif self.y >= h:
            self.y -= h

    def reset(self):
        """Reset particle to random position."""
        self.x = py5.random(py5.width)
        self.y = py5.random(py5.height)
        self.lifetime = 0


def setup() -> None:
    global particles
    py5.size(640, 480)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    # Create particles
    particles = [
        Particle(py5.random(py5.width), py5.random(py5.height)) for _ in range(particle_count)
    ]


def draw() -> None:
    global particles, time_offset, vis_mode, mouse_x, mouse_y, mouse_is_pressed

    # Background with slight fade
    py5.background(10, 10, 20)

    # Update all particles
    for particle in particles:
        particle.update(time_offset)

        # Reset if too old
        if particle.lifetime > particle.max_lifetime:
            particle.reset()

    # Draw particles
    py5.no_stroke()
    for particle in particles:
        # Color based on mode
        if vis_mode == 0:  # Trails (lifetime-based)
            alpha = int(255 * (1 - particle.lifetime / particle.max_lifetime))
            py5.fill(100, 150, 255, alpha)
        elif vis_mode == 1:  # Velocity colors
            vel_mag = math.sqrt(particle.vx**2 + particle.vy**2)
            hue = int((math.atan2(particle.vy, particle.vx) / (2 * math.pi) + 1) * 0.5 * 255) % 256
            sat = int(min(255, vel_mag * 50))
            py5.color_mode(py5.HSB)
            py5.fill(hue, sat, 255)
            py5.color_mode(py5.RGB)
        else:  # Lifetime colors
            alpha = int(255 * (1 - particle.lifetime / particle.max_lifetime))
            py5.fill(particle.lifetime % 256, 100, 255 - (particle.lifetime % 256), alpha)

        py5.circle(particle.x, particle.y, 2)

    # Draw info
    py5.fill(255)
    modes = ["Trails", "Velocity", "Lifetime"]
    py5.text(f"{modes[vis_mode]} | Mouse: attract/repel | 1/2/3: mode | s: save", 10, 20)

    # Time animation
    time_offset += 0.016


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
    global vis_mode
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "particle_flow_####.png"))
    elif py5.key == "1":
        vis_mode = 0
    elif py5.key == "2":
        vis_mode = 1
    elif py5.key == "3":
        vis_mode = 2


py5.run_sketch()
