from pathlib import Path

import numpy as np
import py5
from scipy.ndimage import gaussian_filter, zoom

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
    "watercolor_bleed": {"F": 0.014, "k": 0.054, "name": "Watercolor Bleed"},
    "watercolor_tendrils": {"F": 0.037, "k": 0.060, "name": "Watercolor Tendrils"},
}

# Diffusion rates
Da = 1.0
Db = 0.5
dt = 1.0

# Watercolor extensions
PAPER_TEXTURE = None
PAPER_FIBER_SCALE = 0.008
PAPER_FIBER_OCTAVES = 6
PAPER_FIBER_FALLOFF = 0.6
PAPER_WETNESS = 0.6
render_mode = "classic"  # "classic" | "watercolor"

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


def build_paper_texture(width: int, height: int) -> np.ndarray:
    """Precompute Perlin-based paper grain field."""
    py5.noise_detail(PAPER_FIBER_OCTAVES, PAPER_FIBER_FALLOFF)
    xx, yy = np.meshgrid(
        np.linspace(0, width * PAPER_FIBER_SCALE, width, endpoint=False),
        np.linspace(0, height * PAPER_FIBER_SCALE, height, endpoint=False),
    )
    texture = py5.noise(xx, yy).astype(np.float32)
    py5.noise_detail(4, 0.5)  # Reset to defaults
    return texture


def step(
    U: np.ndarray,
    V: np.ndarray,
    F: float,
    k: float,
    paper: np.ndarray | None = None,
    wetness: float = 0.6,
) -> tuple:
    """Single time step of Gray-Scott model."""
    # Compute Laplacians
    lap_U = laplacian(U)
    lap_V = laplacian(V)

    # Gray-Scott equations
    U_new = U + (Da * lap_U - U * V * V + F * (1 - U)) * dt

    # Apply paper texture to V diffusion for capillary effect
    if paper is not None:
        porosity = 0.3 + 1.4 * (1.0 - paper)
        effective_Db = Db * (1.0 - wetness * 0.5 + wetness * porosity)
        V_new = V + (effective_Db * lap_V + U * V * V - (F + k) * V) * dt
    else:
        V_new = V + (Db * lap_V + U * V * V - (F + k) * V) * dt

    # Clamp to [0, 1]
    U_new = np.clip(U_new, 0, 1)
    V_new = np.clip(V_new, 0, 1)

    return U_new, V_new


def setup() -> None:
    global U, V, PAPER_TEXTURE
    py5.size(640, 480)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    U, V = initialize_grid(py5.width, py5.height)
    PAPER_TEXTURE = build_paper_texture(py5.width, py5.height)


def draw() -> None:
    global U, V, current_preset, PAPER_TEXTURE, render_mode

    # Get current parameters
    params = PRESETS[current_preset]
    F = params["F"]
    k = params["k"]

    # Update multiple steps per frame for speed
    for _ in range(5):
        U, V = step(U, V, F, k, paper=PAPER_TEXTURE, wetness=PAPER_WETNESS)

    # Handle potential Retina display size mismatch
    scale_y = py5.pixel_height / V.shape[0]
    scale_x = py5.pixel_width / V.shape[1]

    if scale_y != 1.0 or scale_x != 1.0:
        V_display = zoom(V, (scale_y, scale_x), order=1)
        PAPER_TEXTURE_display = zoom(PAPER_TEXTURE, (scale_y, scale_x), order=1)
    else:
        V_display = V
        PAPER_TEXTURE_display = PAPER_TEXTURE

    # Render based on mode
    if render_mode == "watercolor":
        # Watercolor rendering with paper texture and soft edges
        paper_bg_r = (240 + PAPER_TEXTURE_display * 10).astype(np.float32)
        paper_bg_g = (228 + PAPER_TEXTURE_display * 10).astype(np.float32)
        paper_bg_b = (215 + PAPER_TEXTURE_display * 8).astype(np.float32)

        V_soft = gaussian_filter(V_display, sigma=1.2)

        # Wet-edge brightening: peak at V ~ 0.4
        edge_factor = np.exp(-((V_soft - 0.4) ** 2) / (2 * 0.12**2))

        # Indigo ink color
        ink_r, ink_g, ink_b = 40.0, 30.0, 110.0

        alpha = np.clip(V_soft * 1.5, 0, 1)
        bright_boost = edge_factor * 0.3

        r_out = (
            (paper_bg_r * (1 - alpha) + (ink_r + bright_boost * 180) * alpha)
            .clip(0, 255)
            .astype(np.uint8)
        )
        g_out = (
            (paper_bg_g * (1 - alpha) + (ink_g + bright_boost * 200) * alpha)
            .clip(0, 255)
            .astype(np.uint8)
        )
        b_out = (
            (paper_bg_b * (1 - alpha) + (ink_b + bright_boost * 220) * alpha)
            .clip(0, 255)
            .astype(np.uint8)
        )

        pixels = np.stack([r_out, g_out, b_out], axis=-1)
    else:
        # Classic rendering with vectorized color mapping
        r = (V_display * 255).astype(np.uint8)
        g = ((1 - V_display) * 127).astype(np.uint8)
        b = ((1 - V_display) * 255).astype(np.uint8)
        pixels = np.stack([r, g, b], axis=-1)

    py5.set_np_pixels(pixels, bands="RGB")

    # Draw info
    py5.fill(255)
    mode_text = " | w: watercolor" if render_mode == "watercolor" else " | w: classic"
    py5.text(f"{params['name']} | F={F:.4f} k={k:.4f} | 1-7: preset{mode_text} | s: save", 10, 20)


def key_pressed() -> None:
    global U, V, current_preset, render_mode

    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "reaction_diffusion_####.png"))
    elif py5.key in "1234567":
        # Switch preset
        presets_list = list(PRESETS.keys())
        idx = int(py5.key) - 1
        if idx < len(presets_list):
            current_preset = presets_list[idx]
            U, V = initialize_grid(py5.width, py5.height)
    elif py5.key == "r":
        U, V = initialize_grid(py5.width, py5.height)
    elif py5.key == "w":
        # Toggle watercolor mode
        render_mode = "watercolor" if render_mode == "classic" else "classic"


py5.run_sketch()
