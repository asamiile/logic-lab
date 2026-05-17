"""3D Metaballs with Perspective Projection - Blending implicit surfaces in 3D space.

Creates organic, morphing 3D shapes by blending multiple spherical potential fields.
Uses perspective projection with Y-axis rotation to display 3D scene on 2D screen.
Each point in 3D space contributes to the field based on distance from metaballs.
When the combined field exceeds a threshold, it's rendered as part of the surface.
"""

import math
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


class Metaball3D:
    """A single 3D metaball - a center point with radius and potential strength."""

    def __init__(
        self,
        x: float,
        y: float,
        z: float,
        radius: float = 80,
        strength: float = 1.0,
    ):
        """Initialize a 3D metaball.

        Args:
            x, y, z: 3D coordinates
            radius: Influence radius
            strength: Potential strength multiplier
        """
        self.x = x
        self.y = y
        self.z = z
        self.radius = radius
        self.strength = strength
        self.vx = 0.0
        self.vy = 0.0
        self.vz = 0.0

    def influence_at(self, x: float, y: float, z: float) -> float:
        """Calculate the potential influence at position (x, y, z).

        Uses 3D distance for smooth falloff.
        """
        dx = x - self.x
        dy = y - self.y
        dz = z - self.z
        distance_sq = dx * dx + dy * dy + dz * dz

        # Smooth falloff: influence = strength * radius² / (distance² + epsilon)
        if distance_sq < 1:
            return self.strength
        return self.strength * (self.radius * self.radius) / (distance_sq + 1)

    def update(self) -> None:
        """Update position based on velocity."""
        self.x += self.vx
        self.y += self.vy
        self.z += self.vz

        # Bounce off walls (3D bounds)
        bounds = 400
        if self.x - self.radius < -bounds or self.x + self.radius > bounds:
            self.vx *= -1
            self.x = max(-bounds + self.radius, min(bounds - self.radius, self.x))
        if self.y - self.radius < -bounds or self.y + self.radius > bounds:
            self.vy *= -1
            self.y = max(-bounds + self.radius, min(bounds - self.radius, self.y))
        if self.z - self.radius < -bounds or self.z + self.radius > bounds:
            self.vz *= -1
            self.z = max(-bounds + self.radius, min(bounds - self.radius, self.z))

    def display(self, projection_func) -> None:
        """Draw the metaball center with projection."""
        screen_x, screen_y, depth = projection_func(self.x, self.y, self.z)

        # Only display if on screen
        if 0 <= screen_x < py5.width and 0 <= screen_y < py5.height:
            py5.stroke(255, 100)
            py5.fill(255, 50)
            radius_2d = self.radius * 0.3  # Scale for visibility
            py5.circle(screen_x, screen_y, radius_2d * 2)
            py5.fill(255)
            py5.circle(screen_x, screen_y, 5)


class MetaballField3D:
    """The combined potential field of multiple 3D metaballs."""

    def __init__(self, width: int = 1024, height: int = 768, focal_distance: float = 800):
        """Initialize the 3D metaball field.

        Args:
            width, height: Screen dimensions for projection
            focal_distance: Distance for perspective projection
        """
        self.width = width
        self.height = height
        self.focal_distance = focal_distance
        self.metaballs: list[Metaball3D] = []
        self.threshold = 1.0
        self.resolution = 4  # Pixel skip for speed
        self.rotation_y = 0.0  # Y-axis rotation in radians
        self.rotation_speed = 0.01  # Default rotation increment per frame
        self.show_influence = False
        self.debug_mode = False

    def add_metaball(
        self,
        x: float,
        y: float,
        z: float,
        radius: float = 80,
        strength: float = 1.0,
    ) -> Metaball3D:
        """Add a 3D metaball to the field."""
        ball = Metaball3D(x, y, z, radius, strength)
        self.metaballs.append(ball)
        return ball

    def perspective_projection(self, x: float, y: float, z: float) -> tuple[float, float, float]:
        """Project 3D point to 2D screen with perspective.

        Applies Y-axis rotation, then perspective projection.
        Returns: (screen_x, screen_y, depth)
        """
        # Y-axis rotation
        cos_ry = math.cos(self.rotation_y)
        sin_ry = math.sin(self.rotation_y)
        rotated_x = x * cos_ry - z * sin_ry
        rotated_z = x * sin_ry + z * cos_ry

        # Perspective projection
        focal = self.focal_distance
        z_offset = rotated_z + focal
        if z_offset <= 0:
            # Behind camera, return off-screen
            return (-1000, -1000, 0.0)

        screen_x = self.width / 2 + rotated_x * focal / z_offset
        screen_y = self.height / 2 + y * focal / z_offset
        depth = (rotated_z + self.focal_distance) / (2 * self.focal_distance)
        depth = max(0.0, min(1.0, depth))  # Clamp to 0-1

        return (screen_x, screen_y, depth)

    def potential_at(self, x: float, y: float, z: float) -> float:
        """Calculate total potential at position (x, y, z)."""
        total = 0.0
        for ball in self.metaballs:
            total += ball.influence_at(x, y, z)
        return total

    def render(self) -> None:
        """Render the 3D metaball field with depth-based coloring."""
        py5.load_pixels()
        pixels = py5.pixels

        # Create list of (x, y, potential, depth) for sorting
        surface_points = []

        # Sample 3D space
        sample_range = 300
        sample_step = self.resolution * 3
        z_step = self.resolution * 4

        for z in range(-sample_range, sample_range, z_step):
            for y in range(-sample_range, sample_range, sample_step):
                for x in range(-sample_range, sample_range, sample_step):
                    potential = self.potential_at(x, y, z)

                    if potential > self.threshold:
                        screen_x, screen_y, depth = self.perspective_projection(x, y, z)

                        # Check if point is on screen
                        if 0 <= screen_x < self.width and 0 <= screen_y < self.height:
                            surface_points.append((screen_x, screen_y, potential, depth))

        # Sort by depth (back to front)
        surface_points.sort(key=lambda p: p[3])

        # Clear background
        for i in range(len(pixels)):
            pixels[i] = py5.color(10, 10, 10)

        # Draw surface points with depth-based coloring
        for screen_x, screen_y, potential, depth in surface_points:
            intensity = int(py5.constrain(potential * 50, 0, 255))
            # Darker for distant, brighter for near
            brightness_factor = 0.5 + depth * 0.5
            r = int(intensity * brightness_factor)
            g = int((150 + intensity // 2) * brightness_factor)
            b = int(255 * brightness_factor)

            color = py5.color(r, g, b)

            # Fill rectangular region
            idx_base = int(screen_y) * self.width + int(screen_x)
            for dy in range(self.resolution):
                for dx in range(self.resolution):
                    sx = int(screen_x) + dx
                    sy = int(screen_y) + dy
                    if sy < self.height and sx < self.width:
                        idx = sy * self.width + sx
                        if idx < len(pixels):
                            pixels[idx] = color

        py5.update_pixels()

        # Draw metaball centers if debug mode
        if self.show_influence:
            py5.hint(py5.DISABLE_DEPTH_TEST)
            for ball in self.metaballs:
                ball.display(self.perspective_projection)

    def update_balls(self) -> None:
        """Update all metaballs and rotation."""
        for ball in self.metaballs:
            ball.update()

        # Auto-rotate around Y axis
        self.rotation_y += self.rotation_speed

    def add_random_velocity(self, speed: float = 1.0) -> None:
        """Give metaballs random initial velocities."""
        for ball in self.metaballs:
            ball.vx = py5.random(-speed, speed)
            ball.vy = py5.random(-speed, speed)
            ball.vz = py5.random(-speed, speed)

    def reset(self) -> None:
        """Reset field to default state."""
        self.metaballs.clear()
        self.rotation_y = 0.0
        self.rotation_speed = 0.01
        self.threshold = 1.0

        # Create initial 3D grid of metaballs
        spacing = 200
        for x in [-spacing, 0, spacing]:
            for y in [-spacing, 0, spacing]:
                for z in [-spacing, 0, spacing]:
                    strength = 1.0 + py5.random(-0.3, 0.3)
                    self.add_metaball(x, y, z, radius=100, strength=strength)

        self.add_random_velocity(speed=1.0)


# Global field
field: MetaballField3D | None = None


def setup() -> None:
    """Setup py5 sketch."""
    py5.size(1024, 768)
    global field
    field = MetaballField3D(py5.width, py5.height)

    # Initialize with 3D grid of metaballs
    field.reset()
    field.resolution = 3

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    """Main draw loop."""
    if field is None:
        return

    py5.background(10)

    # Update physics and rotation
    field.update_balls()

    # Control rotation speed with mouse Y position
    mouse_y_norm = py5.mouse_y / py5.height
    field.rotation_speed = 0.005 + mouse_y_norm * 0.03

    # Render the 3D metaball field
    field.render()

    # Draw info
    py5.fill(200)
    py5.text_size(12)
    py5.text(f"Threshold: {field.threshold:.2f} (arrow up/down)", 10, 20)
    py5.text(f"Rotation speed: {field.rotation_speed:.4f} (mouse Y)", 10, 35)
    py5.text(f"Resolution: {field.resolution} (0-9 keys)", 10, 50)
    py5.text(f"FPS: {py5.frame_rate:.1f}", 10, 65)
    py5.text("Press 'd' for debug | 's' for screenshot | 'r' to reset", 10, py5.height - 10)


def key_pressed() -> None:
    """Handle keyboard input."""
    if field is None:
        return

    key = py5.key

    if key == "s":
        path = SCREENSHOT_DIR / f"metaballs_3d_{py5.frame_count:05d}.png"
        py5.save_frame(str(path))
        print(f"Screenshot saved: {path}")

    elif key == "d":
        field.show_influence = not field.show_influence
        print(f"Debug mode: {field.show_influence}")

    elif key == py5.UP:
        field.rotation_speed = min(field.rotation_speed + 0.005, 0.1)
    elif key == py5.DOWN:
        field.rotation_speed = max(field.rotation_speed - 0.005, 0.0)

    elif key.isdigit():
        # Resolution control with number keys
        res = int(key) if key != "0" else 10
        field.resolution = max(1, res)

    elif key == "r":
        field.reset()
        print("Field reset")


def mouse_pressed() -> None:
    """Handle mouse click."""
    if field is None:
        return

    # Add metaball at mouse position (use z=0 for mouse plane)
    field.add_metaball(
        py5.mouse_x - field.width / 2,
        py5.mouse_y - field.height / 2,
        0,
        radius=80,
        strength=1.0,
    )
    if len(field.metaballs) > 30:
        # Remove oldest
        field.metaballs.pop(0)


py5.run_sketch()
