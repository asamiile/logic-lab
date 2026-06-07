"""2D smooth noise field for organic parameter variation.

Implements value noise with quintic-smoothstep interpolation and fractal
Brownian motion (fBm) octave stacking. Output is in [0, 1].

No external dependencies beyond numpy.

Example::

    from logic_lab.shared.noise_field import NoiseField

    field = NoiseField(seed=42, octaves=4)
    v = field.sample(1.3, 0.7)            # single scalar in [0, 1]
    arr = field.grid(400, 400, t=0.05)    # (400, 400) float32 numpy array
"""

from __future__ import annotations

import math

import numpy as np

_PERM_SIZE = 256


class NoiseField:
    """Tileable 2D value noise with fBm octave stacking.

    Args:
        seed:        Integer seed for the value table.
        octaves:     Number of fBm octaves (1 = raw noise).
        persistence: Amplitude multiplier per octave (0 < p < 1).
        lacunarity:  Frequency multiplier per octave (> 1).
        scale:       Base spatial frequency applied to input coordinates.
    """

    def __init__(
        self,
        seed: int = 0,
        octaves: int = 4,
        persistence: float = 0.5,
        lacunarity: float = 2.0,
        scale: float = 1.0,
    ) -> None:
        self.octaves = max(1, octaves)
        self.persistence = float(persistence)
        self.lacunarity = float(lacunarity)
        self.scale = float(scale)

        rng = np.random.default_rng(seed)
        perm = rng.permutation(_PERM_SIZE).astype(np.int32)
        self._perm: np.ndarray = np.concatenate([perm, perm])  # doubled for wrap-free ix+1
        self._vals: np.ndarray = rng.uniform(0.0, 1.0, _PERM_SIZE).astype(np.float32)

    # ------------------------------------------------------------------
    # Single-point API
    # ------------------------------------------------------------------

    def sample(self, x: float, y: float) -> float:
        """Return fBm noise in [0, 1] at coordinates (x, y)."""
        total = 0.0
        amplitude = 1.0
        frequency = self.scale
        max_val = 0.0
        for _ in range(self.octaves):
            total += self._raw_scalar(x * frequency, y * frequency) * amplitude
            max_val += amplitude
            amplitude *= self.persistence
            frequency *= self.lacunarity
        return total / max_val

    def _raw_scalar(self, x: float, y: float) -> float:
        ix = int(math.floor(x)) & 0xFF
        iy = int(math.floor(y)) & 0xFF
        fx = x - math.floor(x)
        fy = y - math.floor(y)
        u = fx * fx * fx * (fx * (fx * 6.0 - 15.0) + 10.0)
        v = fy * fy * fy * (fy * (fy * 6.0 - 15.0) + 10.0)
        p, vals = self._perm, self._vals
        v00 = float(vals[p[(p[ix] + iy) & 0xFF]])
        v10 = float(vals[p[(p[ix + 1] + iy) & 0xFF]])
        v01 = float(vals[p[(p[ix] + iy + 1) & 0xFF]])
        v11 = float(vals[p[(p[ix + 1] + iy + 1) & 0xFF]])
        return v00 * (1 - u) * (1 - v) + v10 * u * (1 - v) + v01 * (1 - u) * v + v11 * u * v

    # ------------------------------------------------------------------
    # Grid API (vectorized via numpy)
    # ------------------------------------------------------------------

    def grid(self, width: int, height: int, t: float = 0.0) -> np.ndarray:
        """Return a (height, width) float32 array of fBm noise values.

        *t* shifts the x-axis — increment each frame to animate.
        """
        xs = np.linspace(t * self.scale, t * self.scale + 4.0, width, dtype=np.float64)
        ys = np.linspace(0.0, 4.0, height, dtype=np.float64)
        gx, gy = np.meshgrid(xs, ys)
        return self._fbm_grid(gx, gy)

    def _fbm_grid(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        total = np.zeros_like(x, dtype=np.float32)
        amplitude = 1.0
        frequency = self.scale
        max_val = 0.0
        for _ in range(self.octaves):
            total += self._raw_grid(x * frequency, y * frequency) * np.float32(amplitude)
            max_val += amplitude
            amplitude *= self.persistence
            frequency *= self.lacunarity
        return (total / np.float32(max_val)).astype(np.float32)

    def _raw_grid(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        ix = np.floor(x).astype(np.int32) & 0xFF
        iy = np.floor(y).astype(np.int32) & 0xFF
        fx = (x - np.floor(x)).astype(np.float32)
        fy = (y - np.floor(y)).astype(np.float32)
        u = fx * fx * fx * (fx * (fx * 6.0 - 15.0) + 10.0)
        v = fy * fy * fy * (fy * (fy * 6.0 - 15.0) + 10.0)
        ix1 = (ix + 1) & 0xFF
        iy1 = (iy + 1) & 0xFF
        p, vals = self._perm, self._vals
        v00 = vals[p[(p[ix] + iy) & 0xFF]]
        v10 = vals[p[(p[ix1] + iy) & 0xFF]]
        v01 = vals[p[(p[ix] + iy1) & 0xFF]]
        v11 = vals[p[(p[ix1] + iy1) & 0xFF]]
        return (
            v00 * (1 - u) * (1 - v) + v10 * u * (1 - v) + v01 * (1 - u) * v + v11 * u * v
        ).astype(np.float32)
