from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

# Gray-Scott parameters
# F: feed rate, k: kill rate
PRESETS = {
    "coral": {"F": 0.0095, "k": 0.057, "name": "Coral"},
    "mitosis": {"F": 0.046, "k": 0.063, "name": "Mitosis"},
    "fingerprint": {"F": 0.039, "k": 0.058, "name": "Fingerprint"},
    "worms": {"F": 0.078, "k": 0.061, "name": "Worms"},
    "spirals": {"F": 0.0545, "k": 0.062, "name": "Spirals"},
    "pulsing": {"F": 0.025, "k": 0.06, "name": "Pulsing"},
}

# Diffusion rates
Da = 1.0
Db = 0.5
dt = 1.0

# State
U = None
V = None
current_preset = "coral"


def initialize_grid(width: int, height: int) -> tuple:
    """Initialize U and V grids."""
    U = np.ones((height, width), dtype=np.float32)
    V = np.zeros((height, width), dtype=np.float32)

    # Add seed in center
    center_x = width // 2
    center_y = height // 2
    radius = 20

    for y in range(height):
        for x in range(width):
            dx = x - center_x
            dy = y - center_y
            if dx * dx + dy * dy < radius * radius:
                U[y, x] = 0.5
                V[y, x] = 0.25

    return U, V


def laplacian(field: np.ndarray) -> np.ndarray:
    """Compute Laplacian with wrap-around boundary."""
    # Using np.roll for wrap-around (toroidal boundary)
    lap = -4 * field
    lap += np.roll(field, 1, axis=0)  # Up
    lap += np.roll(field, -1, axis=0)  # Down
    lap += np.roll(field, 1, axis=1)  # Left
    lap += np.roll(field, -1, axis=1)  # Right
    return lap


def step(U: np.ndarray, V: np.ndarray, F: float, k: float) -> tuple:
    """Single time step of Gray-Scott model."""
    # Compute Laplacians
    lap_U = laplacian(U)
    lap_V = laplacian(V)

    # Gray-Scott equations
    U_new = U + (Da * lap_U - U * V * V + F * (1 - U)) * dt
    V_new = V + (Db * lap_V + U * V * V - (F + k) * V) * dt

    # Clamp to [0, 1]
    U_new = np.clip(U_new, 0, 1)
    V_new = np.clip(V_new, 0, 1)

    return U_new, V_new


def setup() -> None:
    global U, V
    py5.size(640, 480)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    U, V = initialize_grid(py5.width, py5.height)


def draw() -> None:
    global U, V, current_preset

    # Get current parameters
    params = PRESETS[current_preset]
    F = params["F"]
    k = params["k"]

    # Update multiple steps per frame for speed
    for _ in range(5):
        U, V = step(U, V, F, k)

    # Visualize V concentration
    # V high = color, V low = white
    pixels = np.zeros((py5.pixel_height, py5.pixel_width, 3), dtype=np.uint8)

    # Resize V to screen
    for y in range(py5.pixel_height):
        src_y = int((y / py5.pixel_height) * V.shape[0])
        for x in range(py5.pixel_width):
            src_x = int((x / py5.pixel_width) * V.shape[1])
            val = V[src_y, src_x]

            # Color mapping: low V = purple, high V = yellow/red
            r = int(val * 255)
            g = int((1 - val) * 255 * 0.5)
            b = int((1 - val) * 255)

            pixels[y, x] = [r, g, b]

    py5.set_np_pixels(pixels, bands="RGB")

    # Draw info
    py5.fill(255)
    py5.text(f"{params['name']} | F={F:.4f} k={k:.4f} | 1-5: preset | s: save", 10, 20)


def key_pressed() -> None:
    global U, V, current_preset

    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "reaction_diffusion_####.png"))
    elif py5.key in "12345":
        # Switch preset
        presets_list = list(PRESETS.keys())
        idx = int(py5.key) - 1
        if idx < len(presets_list):
            current_preset = presets_list[idx]
            U, V = initialize_grid(py5.width, py5.height)
    elif py5.key == "r":
        U, V = initialize_grid(py5.width, py5.height)


py5.run_sketch()
