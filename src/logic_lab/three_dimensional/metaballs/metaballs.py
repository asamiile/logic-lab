"""Metaballs - Blending implicit surfaces using smooth threshold functions.

Creates organic, morphing shapes by blending multiple spherical potential fields.
Each point in space has a field value determined by nearby metaballs.
When the combined field exceeds a threshold, it's rendered as part of the surface.
"""

from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


class Metaball:
    """A single metaball - a center point with a radius and potential strength."""

    def __init__(self, x: float, y: float, radius: float = 80, strength: float = 1.0):
        self.x = x
        self.y = y
        self.radius = radius
        self.strength = strength
        self.vx = 0.0
        self.vy = 0.0

    def influence_at(self, x: float, y: float) -> float:
        """Calculate the potential influence at position (x, y)."""
        dx = x - self.x
        dy = y - self.y
        distance_sq = dx * dx + dy * dy
        # Smooth falloff: influence = strength * radius² / (distance² + epsilon)
        if distance_sq < 1:
            return self.strength  # Maximum influence at center
        return self.strength * (self.radius * self.radius) / (distance_sq + 1)

    def update(self) -> None:
        """Update position based on velocity."""
        self.x += self.vx
        self.y += self.vy

        # Bounce off walls
        width = py5.width
        height = py5.height
        if self.x - self.radius < 0 or self.x + self.radius > width:
            self.vx *= -1
            self.x = py5.constrain(self.x, self.radius, width - self.radius)
        if self.y - self.radius < 0 or self.y + self.radius > height:
            self.vy *= -1
            self.y = py5.constrain(self.y, self.radius, height - self.radius)

    def display(self) -> None:
        """Draw the metaball center and influence circle."""
        py5.stroke(255, 100)
        py5.fill(255, 50)
        py5.circle(self.x, self.y, self.radius * 2)
        py5.fill(255)
        py5.circle(self.x, self.y, 5)


class MetaballField:
    """The combined potential field of multiple metaballs."""

    def __init__(self, width: int = 640, height: int = 480):
        self.width = width
        self.height = height
        self.metaballs: list[Metaball] = []
        self.threshold = 1.0
        self.resolution = 4  # Pixel skip for speed (higher = faster, less detail)
        self.show_influence = False

    def add_metaball(
        self, x: float, y: float, radius: float = 80, strength: float = 1.0
    ) -> Metaball:
        """Add a metaball to the field."""
        ball = Metaball(x, y, radius, strength)
        self.metaballs.append(ball)
        return ball

    def potential_at(self, x: float, y: float) -> float:
        """Calculate total potential at position (x, y)."""
        total = 0.0
        for ball in self.metaballs:
            total += ball.influence_at(x, y)
        return total

    def render(self) -> None:
        """Render the metaball field."""
        py5.load_pixels()
        pixels = py5.pixels

        for y in range(0, self.height, self.resolution):
            for x in range(0, self.width, self.resolution):
                potential = self.potential_at(x, y)

                if potential > self.threshold:
                    # Inside metaball surface - color based on potential
                    intensity = int(py5.constrain(potential * 50, 0, 255))
                    color = py5.color(intensity, 150 + intensity // 2, 255)
                else:
                    # Outside - gradient background
                    bg_value = int(20 + (potential / self.threshold) * 30)
                    color = py5.color(bg_value, bg_value, bg_value)

                # Fill rectangular region
                idx_base = y * self.width + x
                for dy in range(self.resolution):
                    for dx in range(self.resolution):
                        if y + dy < self.height and x + dx < self.width:
                            idx = (y + dy) * self.width + (x + dx)
                            if idx < len(pixels):
                                pixels[idx] = color

        py5.update_pixels()

        # Draw metaball centers if debug mode
        if self.show_influence:
            py5.hint(py5.DISABLE_DEPTH_TEST)
            for ball in self.metaballs:
                ball.display()

    def update_balls(self) -> None:
        """Update all metaballs."""
        for ball in self.metaballs:
            ball.update()

    def add_random_velocity(self, speed: float = 2.0) -> None:
        """Give metaballs random initial velocities."""
        for ball in self.metaballs:
            ball.vx = py5.random(-speed, speed)
            ball.vy = py5.random(-speed, speed)


# Global field
field: MetaballField | None = None


def setup() -> None:
    py5.size(1024, 768)
    global field
    field = MetaballField(py5.width, py5.height)

    # Create initial metaballs
    field.add_metaball(py5.width * 0.25, py5.height * 0.3, radius=100, strength=1.2)
    field.add_metaball(py5.width * 0.75, py5.height * 0.3, radius=100, strength=1.2)
    field.add_metaball(py5.width * 0.5, py5.height * 0.65, radius=120, strength=1.0)
    field.add_metaball(py5.width * 0.5, py5.height * 0.5, radius=60, strength=0.8)

    # Give them initial movement
    field.add_random_velocity(speed=1.5)
    field.resolution = 2  # Adjust for performance/quality tradeoff

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    if field is None:
        return

    py5.background(10)

    # Update physics
    field.update_balls()

    # Render the metaball field
    field.render()

    # Draw info
    py5.fill(200)
    py5.text_size(12)
    py5.text(f"Threshold: {field.threshold:.2f} (arrow up/down)", 10, 20)
    py5.text(f"Resolution: {field.resolution} (0-9 keys)", 10, 35)
    py5.text(f"FPS: {py5.frame_rate():.1f}", 10, 50)
    py5.text("Press 'd' for debug mode | 's' for screenshot", 10, py5.height - 10)


def key_pressed() -> None:
    if field is None:
        return

    key = py5.key

    if key == "s":
        path = SCREENSHOT_DIR / f"metaballs_{py5.frame_count:05d}.png"
        py5.save_frame(str(path))
        print(f"Screenshot saved: {path}")

    elif key == "d":
        field.show_influence = not field.show_influence

    elif key == py5.UP:
        field.threshold = min(field.threshold + 0.1, 3.0)
    elif key == py5.DOWN:
        field.threshold = max(field.threshold - 0.1, 0.1)

    elif key.isdigit():
        # Resolution control with number keys
        res = int(key) if key != "0" else 10
        field.resolution = max(1, res)

    elif key == "r":
        # Reset
        field.metaballs.clear()
        field.add_metaball(py5.width * 0.25, py5.height * 0.3, radius=100, strength=1.2)
        field.add_metaball(py5.width * 0.75, py5.height * 0.3, radius=100, strength=1.2)
        field.add_metaball(py5.width * 0.5, py5.height * 0.65, radius=120, strength=1.0)
        field.add_metaball(py5.width * 0.5, py5.height * 0.5, radius=60, strength=0.8)
        field.add_random_velocity(speed=1.5)


def mouse_pressed() -> None:
    if field is None:
        return
    # Add metaball at mouse position
    field.add_metaball(py5.mouse_x, py5.mouse_y, radius=80, strength=1.0)
    if len(field.metaballs) > 10:
        # Remove oldest
        field.metaballs.pop(0)


py5.run_sketch()
