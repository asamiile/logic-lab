"""Audio-Reactive Particles - Frequency-driven particle visualization system."""

from .audio_reactive_particles import (
    HAS_SOUNDDEVICE,
    AudioCapture,
    AudioParticle,
    AudioReactiveField,
    SpectrumBand,
)

__all__ = [
    "HAS_SOUNDDEVICE",
    "AudioParticle",
    "SpectrumBand",
    "AudioCapture",
    "AudioReactiveField",
]
