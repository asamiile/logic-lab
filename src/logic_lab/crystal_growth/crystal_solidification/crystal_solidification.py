"""
Crystal Solidification — Phase-Field Model of Dendritic Growth
The phase-field method tracks a continuous order parameter φ ∈ [0,1]:
  φ = 0  →  liquid
  φ = 1  →  solid

Evolution equations (simplified Karma-Rappel model):
  τ · ∂φ/∂t = W²·∇·[a(θ)²·∇φ] + φ(1−φ)(φ−0.5+λu)

  ∂u/∂t = D·∇²u + 0.5·∂φ/∂t

where u = (T−Tm)/ΔT is the dimensionless temperature field.
The anisotropy function  a(θ) = 1 + ε·cos(m·(θ−θ₀))  generates:
  m=4 → cubic (4-fold) symmetry  — metallic crystals
  m=6 → hexagonal (6-fold)        — ice / snowflakes
  m=3 → trigonal (3-fold)         — some mineral crystals

The latent heat released at the solid–liquid interface heats the
surrounding liquid, slowing further growth (diffusion-limited morphology).
At low undercooling or high anisotropy, classic dendritic arms appear
with secondary and tertiary side branches.

Controls:
  1       — 4-fold anisotropy (metallic / cubic)
  2       — 6-fold anisotropy (hexagonal / ice)
  3       — 3-fold anisotropy (trigonal)
  e/E     — decrease / increase anisotropy strength ε
  u/U     — decrease / increase undercooling
  r       — reset (new seed)
  Space   — pause / resume
  s       — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 900, 900
GRID = 300  # grid cells (square)
DX = 1.0
DT = 0.02

TAU = 1.0  # phase-field relaxation time
W0 = 1.0  # interface thickness
LAMBDA = 3.0  # coupling strength
D = 2.0  # thermal diffusivity

ANISO_M = 4  # symmetry order
ANISO_EPS = 0.04  # anisotropy strength (0=isotropic)
UNDERCOOL = -0.55  # initial temperature field (u₀ < 0 = undercooled)

STEPS_PER_FRAME = 5

paused = False
color_mode = 1  # 1=solid fraction, 2=temperature, 3=gradient mag

_phi: np.ndarray  # (GRID, GRID) order parameter
_u: np.ndarray  # (GRID, GRID) temperature field


def _laplacian(f: np.ndarray) -> np.ndarray:
    return (np.roll(f, 1, 0) + np.roll(f, -1, 0) + np.roll(f, 1, 1) + np.roll(f, -1, 1) - 4 * f) / (
        DX * DX
    )


def _grad(f: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    fx = (np.roll(f, -1, 1) - np.roll(f, 1, 1)) / (2 * DX)
    fy = (np.roll(f, -1, 0) - np.roll(f, 1, 0)) / (2 * DX)
    return fx, fy


def _anisotropic_laplacian(phi: np.ndarray) -> np.ndarray:
    """∇·[a(θ)²·∇φ] with a(θ) = 1 + ε·cos(m·θ)."""
    phix, phiy = _grad(phi)
    theta = np.arctan2(phiy, phix)
    a = 1.0 + ANISO_EPS * np.cos(ANISO_M * theta)
    a2 = a * a

    # ∇·(a²·∇φ)  via finite differences on the flux a²·∇φ
    fx = a2 * phix
    fy = a2 * phiy
    div = (np.roll(fx, -1, 1) - np.roll(fx, 1, 1)) / (2 * DX) + (
        np.roll(fy, -1, 0) - np.roll(fy, 1, 0)
    ) / (2 * DX)
    return div


def _step() -> None:
    global _phi, _u

    dphi_dt = (W0 * W0 / TAU) * _anisotropic_laplacian(_phi) + _phi * (1 - _phi) * (
        _phi - 0.5 + LAMBDA * _u
    ) / TAU

    phi_new = np.clip(_phi + DT * dphi_dt, 0.0, 1.0)
    dphi = phi_new - _phi

    u_new = _u + DT * (D * _laplacian(_u) + 0.5 * dphi / DT * DT)
    _phi = phi_new
    _u = u_new


def _reset() -> None:
    global _phi, _u
    _phi = np.zeros((GRID, GRID), dtype=np.float64)
    _u = np.full((GRID, GRID), UNDERCOOL, dtype=np.float64)
    # Seed: small solid nucleus at center
    cx, cy = GRID // 2, GRID // 2
    r_seed = 5
    yy, xx = np.ogrid[:GRID, :GRID]
    mask = (xx - cx) ** 2 + (yy - cy) ** 2 <= r_seed**2
    _phi[mask] = 1.0
    _u[mask] = 0.0


def _render() -> np.ndarray:
    ph, pw = py5.pixel_height, py5.pixel_width
    gy = (np.arange(ph) * GRID / ph).astype(int).clip(0, GRID - 1)
    gx = (np.arange(pw) * GRID / pw).astype(int).clip(0, GRID - 1)

    if color_mode == 1:
        # φ: black (liquid) → bright teal/white (solid)
        t = _phi[np.ix_(gy, gx)].astype(np.float32)
        r8 = np.clip(t * 100 + t * t * 155, 0, 255).astype(np.uint8)
        g8 = np.clip(t * 210, 0, 255).astype(np.uint8)
        b8 = np.clip(t * 180 + (1 - t) * 30, 0, 255).astype(np.uint8)
    elif color_mode == 2:
        # temperature u: cold=blue, hot=red (latent heat at interface)
        u_d = _u[np.ix_(gy, gx)].astype(np.float32)
        u_n = np.clip((u_d - UNDERCOOL) / (0.5 - UNDERCOOL), 0, 1)
        r8 = np.clip(u_n * 220, 0, 255).astype(np.uint8)
        g8 = np.clip((1 - abs(u_n - 0.5) * 2) * 120, 0, 255).astype(np.uint8)
        b8 = np.clip((1 - u_n) * 220, 0, 255).astype(np.uint8)
    else:
        # gradient magnitude of φ (highlights the interface)
        phix, phiy = _grad(_phi)
        mag = np.sqrt(phix * phix + phiy * phiy)
        mag_d = mag[np.ix_(gy, gx)].astype(np.float32)
        m_max = float(np.percentile(mag, 99.5)) + 1e-6
        t = np.clip(mag_d / m_max, 0, 1)
        phi_d = _phi[np.ix_(gy, gx)].astype(np.float32)
        r8 = np.clip(t * 255 + phi_d * 40, 0, 255).astype(np.uint8)
        g8 = np.clip(t * 180 + phi_d * 80, 0, 255).astype(np.uint8)
        b8 = np.clip(t * 60 + phi_d * 160, 0, 255).astype(np.uint8)

    argb = (
        np.int32(-16777216)
        | (r8.astype(np.int32) << 16)
        | (g8.astype(np.int32) << 8)
        | b8.astype(np.int32)
    )
    return argb


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    py5.frame_rate(30)
    _reset()


def draw() -> None:
    if not paused:
        for _ in range(STEPS_PER_FRAME):
            _step()

    argb = _render()
    py5.load_pixels()
    py5.pixels[:] = argb.flatten()
    py5.update_pixels()

    solid_frac = float(_phi.mean())
    sym_names = {3: "3-fold", 4: "4-fold", 6: "6-fold"}
    cmode_names = ["", "phase", "temp", "gradient"]
    py5.fill(210, 235, 255)
    py5.no_stroke()
    py5.text_size(12)
    py5.text(
        f"Crystal solidification  sym:{sym_names.get(ANISO_M,'?')}  "
        f"ε={ANISO_EPS:.3f}  u₀={UNDERCOOL:.2f}  "
        f"solid:{solid_frac:.3f}  cmap:{cmode_names[color_mode]}  "
        f"{'PAUSED' if paused else ''}",
        8,
        18,
    )


def key_pressed() -> None:
    global paused, color_mode, ANISO_M, ANISO_EPS, UNDERCOOL
    k = py5.key
    if k == " ":
        paused = not paused
    elif k == "r":
        _reset()
    elif k == "1":
        color_mode = 1
    elif k == "2":
        color_mode = 2
    elif k == "3":
        color_mode = 3
    elif k == "e":
        ANISO_EPS = max(0.0, round(ANISO_EPS - 0.01, 3))
        _reset()
    elif k == "E":
        ANISO_EPS = min(0.15, round(ANISO_EPS + 0.01, 3))
        _reset()
    elif k == "u":
        UNDERCOOL = max(-0.9, round(UNDERCOOL - 0.05, 2))
        _reset()
    elif k == "U":
        UNDERCOOL = min(-0.1, round(UNDERCOOL + 0.05, 2))
        _reset()
    elif k == "4":
        ANISO_M = 4
        _reset()
    elif k == "6":
        ANISO_M = 6
        _reset()
    elif k == "9":
        ANISO_M = 3
        _reset()
    elif k == "s":
        py5.save_frame(str(SCREENSHOT_DIR / f"solidify_{ANISO_M}fold_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
