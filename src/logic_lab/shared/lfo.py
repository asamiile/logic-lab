"""LFO (Low Frequency Oscillator) utility for parameter modulation.

Provides an LFOBank that manages multiple named oscillators. Each LFO
outputs a time-varying value that can drive any numeric parameter of
another algorithm — gravity, feed rate, hue, particle speed, etc.

Waveform shapes:
    sine      — smooth sinusoidal oscillation
    triangle  — linear ramp up and down
    sawtooth  — linear ramp up, instant reset
    rsaw      — reverse sawtooth (ramp down, instant reset)
    square    — bang between low and high values
    pulse     — square with configurable duty cycle
    noise     — smoothed random walk

Example usage in a py5 sketch::

    from logic_lab.shared.lfo import LFOBank

    lfo = LFOBank(sample_rate=60)
    lfo.add("gravity",  shape="sine",     freq=0.1,  low=200, high=600)
    lfo.add("hue",      shape="sawtooth", freq=0.02, low=0,   high=360)
    lfo.add("feed",     shape="triangle", freq=0.005,low=0.03, high=0.06)

    def draw():
        gravity = lfo.tick("gravity")
        hue     = lfo.tick("hue")
        feed    = lfo.tick("feed")
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Literal

Shape = Literal["sine", "triangle", "sawtooth", "rsaw", "square", "pulse", "noise"]

_SHAPES: frozenset[str] = frozenset(
    ["sine", "triangle", "sawtooth", "rsaw", "square", "pulse", "noise"]
)


@dataclass
class LFO:
    """A single low-frequency oscillator."""

    name: str
    shape: Shape
    freq: float  # Cycles per second (Hz)
    low: float = 0.0  # Output minimum
    high: float = 1.0  # Output maximum
    phase: float = 0.0  # Initial phase offset [0, 1)
    duty: float = 0.5  # Duty cycle for 'pulse' shape [0, 1]

    # Internal state
    _t: float = field(default=0.0, init=False, repr=False)
    _noise_prev: float = field(default=0.0, init=False, repr=False)
    _noise_next: float = field(default=0.0, init=False, repr=False)
    _noise_phase: float = field(default=0.0, init=False, repr=False)

    def __post_init__(self) -> None:
        rng = random.Random(hash(self.name))
        self._noise_prev = rng.uniform(0.0, 1.0)
        self._noise_next = rng.uniform(0.0, 1.0)
        self._t = self.phase

    def _raw(self) -> float:
        """Return raw [0, 1] oscillator value at current internal phase."""
        p = (self._t % 1.0 + 1.0) % 1.0  # normalise to [0, 1)
        if self.shape == "sine":
            return 0.5 + 0.5 * math.sin(p * math.tau)
        if self.shape == "triangle":
            return 1.0 - abs(2.0 * p - 1.0)
        if self.shape == "sawtooth":
            return p
        if self.shape == "rsaw":
            return 1.0 - p
        if self.shape == "square":
            return 1.0 if p < 0.5 else 0.0
        if self.shape == "pulse":
            return 1.0 if p < self.duty else 0.0
        if self.shape == "noise":
            # Smooth interpolation between random targets, one target per cycle
            if p < self._noise_phase:
                # Phase wrapped — advance to next target
                self._noise_prev = self._noise_next
                rng = random.Random(hash((self.name, self._t)))
                self._noise_next = rng.uniform(0.0, 1.0)
            self._noise_phase = p
            t_smooth = p * p * (3.0 - 2.0 * p)  # smoothstep
            return self._noise_prev + t_smooth * (self._noise_next - self._noise_prev)
        return 0.0

    def advance(self, dt: float) -> float:
        """Advance by dt seconds and return the mapped output value."""
        self._t += self.freq * dt
        raw = self._raw()
        return self.low + raw * (self.high - self.low)

    @property
    def value(self) -> float:
        """Current output value without advancing time."""
        raw = self._raw()
        return self.low + raw * (self.high - self.low)

    def reset(self) -> None:
        self._t = self.phase


class LFOBank:
    """Manage a collection of named LFOs.

    Args:
        sample_rate: Frames (or ticks) per second used when calling
            ``tick()`` without an explicit ``dt``. Defaults to 60.
    """

    def __init__(self, sample_rate: float = 60.0) -> None:
        self._sample_rate = sample_rate
        self._lfos: dict[str, LFO] = {}

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def add(
        self,
        name: str,
        shape: Shape = "sine",
        freq: float = 1.0,
        low: float = 0.0,
        high: float = 1.0,
        phase: float = 0.0,
        duty: float = 0.5,
    ) -> LFOBank:
        """Add or replace a named LFO. Returns self for chaining."""
        if shape not in _SHAPES:
            raise ValueError(f"Unknown shape '{shape}'. Choose from: {sorted(_SHAPES)}")
        self._lfos[name] = LFO(
            name=name,
            shape=shape,
            freq=freq,
            low=low,
            high=high,
            phase=phase,
            duty=duty,
        )
        return self

    def remove(self, name: str) -> None:
        self._lfos.pop(name, None)

    def reset(self, name: str | None = None) -> None:
        """Reset one or all LFOs to their initial phase."""
        targets = [self._lfos[name]] if name else list(self._lfos.values())
        for lfo in targets:
            lfo.reset()

    # ------------------------------------------------------------------
    # Playback
    # ------------------------------------------------------------------

    def tick(self, name: str, dt: float | None = None) -> float:
        """Advance the named LFO by one sample and return its value.

        Args:
            name: LFO identifier as given to ``add()``.
            dt:   Time delta in seconds. Defaults to ``1 / sample_rate``.

        Returns:
            Mapped float value in ``[low, high]``.
        """
        if name not in self._lfos:
            raise KeyError(f"No LFO named '{name}'. Call add() first.")
        step = dt if dt is not None else 1.0 / self._sample_rate
        return self._lfos[name].advance(step)

    def tick_all(self, dt: float | None = None) -> dict[str, float]:
        """Advance all LFOs and return a dict of current values."""
        step = dt if dt is not None else 1.0 / self._sample_rate
        return {name: lfo.advance(step) for name, lfo in self._lfos.items()}

    def peek(self, name: str) -> float:
        """Return the current value of a named LFO without advancing time."""
        if name not in self._lfos:
            raise KeyError(f"No LFO named '{name}'.")
        return self._lfos[name].value

    # ------------------------------------------------------------------
    # Inspection
    # ------------------------------------------------------------------

    def names(self) -> list[str]:
        return list(self._lfos.keys())

    def __repr__(self) -> str:
        entries = ", ".join(f"{n}({l.shape} {l.freq}Hz)" for n, l in self._lfos.items())
        return f"LFOBank(rate={self._sample_rate}, [{entries}])"
