"""
Gray-Scott Reaction-Diffusion System Implementation.

The Gray-Scott equations model a chemical reaction between two substances (U and V):
- U is an activator that helps produce more U and V
- V is an inhibitor that suppresses U
- The system exhibits self-organizing pattern formation

Equations:
    U_next = U + dt * (Du * laplacian(U) - U*V*V + F*(1-U))
    V_next = V + dt * (Dv * laplacian(V) + U*V*V - (F+k)*V)

Where:
    - Du, Dv: diffusion coefficients
    - F: feed rate (replenishes U)
    - k: kill rate (removes V)
    - dt: time step
"""

from pathlib import Path

import numpy as np
import py5
import scipy.ndimage

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

# Grid size (256x256)
GRID_SIZE = 256
PIXEL_SCALE = 2  # Scale up for display (256 * 2 = 512)

# Diffusion coefficients
Du = 0.16
Dv = 0.08
dt = 1.0

# Parameter presets: (F, k) pairs for different pattern types
PRESETS = {
    "spots": {"F": 0.035, "k": 0.065},
    "stripes": {"F": 0.055, "k": 0.062},
    "waves": {"F": 0.04, "k": 0.06},
}

# Current state
F = PRESETS["spots"]["F"]
k = PRESETS["spots"]["k"]
preset_name = "spots"

# Grid state (U and V concentrations)
U: np.ndarray
V: np.ndarray

# Laplacian kernel for calculating diffusion
LAPLACIAN_KERNEL = np.array([[0.0, 1.0, 0.0], [1.0, -4.0, 1.0], [0.0, 1.0, 0.0]])

# UI state
paused = False


def initialize_grids() -> tuple[np.ndarray, np.ndarray]:
    """
    Initialize U and V grids with appropriate boundary conditions.

    U starts with mostly 1.0 (uniform)
    V starts with mostly 0.0 (uniform)
    A circular region in the center is perturbed to initiate pattern formation.

    Returns:
        Tuple of (U, V) grids as numpy arrays.
    """
    U_init = np.ones((GRID_SIZE, GRID_SIZE), dtype=np.float32)
    V_init = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float32)

    # Add random noise to U to seed pattern formation
    noise = np.random.RandomState(42).normal(0, 0.05, (GRID_SIZE, GRID_SIZE))
    U_init += noise
    U_init = np.clip(U_init, 0, 1)

    # Create a circular region in the center with high V concentration
    center = GRID_SIZE // 2
    radius = GRID_SIZE // 8
    y, x = np.ogrid[:GRID_SIZE, :GRID_SIZE]
    mask = (x - center) ** 2 + (y - center) ** 2 <= radius**2
    V_init[mask] = 0.25

    return U_init, V_init


def calculate_laplacian(field: np.ndarray) -> np.ndarray:
    """
    Calculate the Laplacian of a field using convolution.

    Uses wrap mode for periodic boundary conditions (toroidal topology).

    Args:
        field: 2D numpy array representing a concentration field.

    Returns:
        2D array with Laplacian values.
    """
    return scipy.ndimage.convolve(field, LAPLACIAN_KERNEL, mode="wrap")


def update_step() -> None:
    """
    Execute one time step of the Gray-Scott reaction-diffusion system.

    Updates both U and V fields based on diffusion and chemical reactions.
    """
    global U, V

    # Calculate Laplacians
    laplacian_U = calculate_laplacian(U)
    laplacian_V = calculate_laplacian(V)

    # Calculate reaction terms
    U_V_squared = U * V * V

    # Update U: diffusion - consumption + feed
    U = U + dt * (Du * laplacian_U - U_V_squared + F * (1.0 - U))

    # Update V: diffusion + production - removal
    V = V + dt * (Dv * laplacian_V + U_V_squared - (F + k) * V)

    # Clamp values to [0, 1] range
    U = np.clip(U, 0, 1)
    V = np.clip(V, 0, 1)


def v_to_color(v_value: float) -> tuple[int, int, int]:
    """
    Convert a V concentration value to RGB color.

    Maps V concentration to a blue-white colormap:
    - 0.0 (low V) -> dark blue
    - 1.0 (high V) -> white

    Args:
        v_value: V concentration (0.0 to 1.0)

    Returns:
        Tuple of (R, G, B) values (0-255).
    """
    # Use a colormap that goes from dark blue to white
    r = int(v_value * 255)
    g = int(v_value * 255)
    b = int(100 + v_value * 155)  # Start from darker blue
    return (r, g, b)


def render_frame() -> None:
    """
    Render the current grid state to the canvas.

    Uses py5's pixel array for efficient rendering.
    Maps V concentration to colors using a colormap.
    """
    py5.load_pixels()
    pixels = py5.pixels

    # Get display dimensions
    display_width = py5.width
    display_height = py5.height

    # Iterate through the grid
    for gy in range(GRID_SIZE):
        for gx in range(GRID_SIZE):
            # Get V value
            v_val = V[gy, gx]

            # Convert to color
            r, g, b = v_to_color(v_val)
            color = py5.color(r, g, b)

            # Draw PIXEL_SCALE x PIXEL_SCALE pixels for each grid cell
            for py_offset in range(PIXEL_SCALE):
                for px_offset in range(PIXEL_SCALE):
                    px = gx * PIXEL_SCALE + px_offset
                    py = gy * PIXEL_SCALE + py_offset

                    if px < display_width and py < display_height:
                        idx = py * display_width + px
                        if idx < len(pixels):
                            pixels[idx] = color

    py5.update_pixels()


def setup() -> None:
    """Initialize the py5 sketch."""
    global U, V
    py5.size(GRID_SIZE * PIXEL_SCALE, GRID_SIZE * PIXEL_SCALE)
    py5.background(0)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    U, V = initialize_grids()


def draw() -> None:
    """Main draw loop."""
    global paused

    # Update simulation state
    if not paused:
        update_step()

    # Render the current frame
    render_frame()

    # Display UI information
    py5.fill(200)
    py5.text_size(12)
    py5.text(f"Preset: {preset_name} | F: {F:.4f} | k: {k:.4f}", 10, 20)
    if paused:
        py5.text("PAUSED", 10, 35)


def key_pressed() -> None:
    """Handle keyboard input."""
    global F, k, U, V, paused, preset_name

    if py5.key == "1":
        # Spots pattern
        F = PRESETS["spots"]["F"]
        k = PRESETS["spots"]["k"]
        preset_name = "spots"
        U, V = initialize_grids()
    elif py5.key == "2":
        # Stripes pattern
        F = PRESETS["stripes"]["F"]
        k = PRESETS["stripes"]["k"]
        preset_name = "stripes"
        U, V = initialize_grids()
    elif py5.key == "3":
        # Waves pattern
        F = PRESETS["waves"]["F"]
        k = PRESETS["waves"]["k"]
        preset_name = "waves"
        U, V = initialize_grids()
    elif py5.key == py5.UP:
        # Increase F (feed rate)
        F = min(F + 0.001, 0.1)
    elif py5.key == py5.DOWN:
        # Decrease F (feed rate)
        F = max(F - 0.001, 0.0)
    elif py5.key == "r":
        # Reset with current parameters
        U, V = initialize_grids()
    elif py5.key == " ":
        # Toggle pause
        paused = not paused
    elif py5.key == "s":
        # Save screenshot
        py5.save_frame(str(SCREENSHOT_DIR / f"gray_scott_{preset_name}_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
