"""Audio-reactive particles system with frequency-driven visualization.

This module provides real-time audio visualization through particle systems
that react to different frequency bands (bass, mid, high) from audio input.
When sounddevice is not available, it gracefully falls back to demo mode
with simulated audio signals.
"""

import math
import threading
import time
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import py5

try:
    import sounddevice as sd

    HAS_SOUNDDEVICE = True
except ImportError:
    HAS_SOUNDDEVICE = False


@dataclass
class AudioParticle:
    """A single particle in the audio-reactive system.

    Attributes:
        x: Horizontal position (0-width)
        y: Vertical position (0-height)
        vx: Horizontal velocity
        vy: Vertical velocity
        life: Lifetime from 0 (dead) to 1 (newborn)
        color: RGB color tuple (0-255)
    """

    x: float
    y: float
    vx: float
    vy: float
    life: float
    color: tuple[int, int, int]

    def update(self, gravity: float = 0.98) -> None:
        """Update particle position and apply physics.

        Args:
            gravity: Velocity damping factor per frame
        """
        self.x += self.vx
        self.y += self.vy
        self.vx *= gravity
        self.vy *= gravity
        self.life -= 0.02

    def is_alive(self) -> bool:
        """Check if particle is still active."""
        return self.life > 0


@dataclass
class SpectrumBand:
    """Normalized frequency spectrum bands.

    Attributes:
        bass: Energy in 0-300Hz range (0-1)
        mid: Energy in 300-3000Hz range (0-1)
        high: Energy in 3000Hz+ range (0-1)
    """

    bass: float = 0.0
    mid: float = 0.0
    high: float = 0.0

    def normalize(self) -> None:
        """Normalize bands to sum to 1 (within tolerance)."""
        total = self.bass + self.mid + self.high
        if total > 1e-9:
            self.bass /= total
            self.mid /= total
            self.high /= total


class AudioCapture:
    """Captures audio from microphone and computes FFT spectrum.

    This class manages audio input and frequency analysis. It runs
    audio capture in a background thread and provides thread-safe
    access to the current spectrum.

    Attributes:
        sample_rate: Sample rate in Hz (default 22050)
        chunk_size: Audio chunk size (default 1024)
    """

    def __init__(self, sample_rate: int = 22050, chunk_size: int = 1024):
        """Initialize audio capture.

        Args:
            sample_rate: Audio sample rate in Hz
            chunk_size: Number of samples per chunk
        """
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.is_active = False
        self.stream: sd.InputStream | None = None

        self._spectrum_lock = threading.Lock()
        self._current_spectrum = SpectrumBand()
        self._audio_buffer: list[np.ndarray] = []

    def start(self) -> None:
        """Start capturing audio from microphone."""
        if not HAS_SOUNDDEVICE:
            return

        if self.is_active:
            return

        self.is_active = True
        self.stream = sd.InputStream(
            channels=1,
            samplerate=self.sample_rate,
            blocksize=self.chunk_size,
            callback=self._audio_callback,
            dtype=np.float32,
        )
        self.stream.start()

    def stop(self) -> None:
        """Stop capturing audio."""
        self.is_active = False
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None

    def _audio_callback(self, indata: np.ndarray, frames: int, time_info, status) -> None:
        """Callback for audio stream processing."""
        if status:
            return

        audio_data = indata[:, 0].copy().astype(np.float32)
        self._process_spectrum(audio_data)

    def _process_spectrum(self, audio_data: np.ndarray) -> None:
        """Compute FFT and extract frequency bands."""
        # Compute FFT
        spectrum = np.abs(np.fft.rfft(audio_data))
        freqs = np.fft.rfftfreq(len(audio_data), 1 / self.sample_rate)

        # Extract frequency bands
        bass_mask = freqs < 300
        mid_mask = (freqs >= 300) & (freqs < 3000)
        high_mask = freqs >= 3000

        bass_energy = spectrum[bass_mask].sum()
        mid_energy = spectrum[mid_mask].sum()
        high_energy = spectrum[high_mask].sum()

        # Normalize
        total = bass_energy + mid_energy + high_energy
        if total > 1e-9:
            bass = bass_energy / total
            mid = mid_energy / total
            high = high_energy / total
        else:
            bass = mid = high = 0.0

        with self._spectrum_lock:
            self._current_spectrum.bass = bass
            self._current_spectrum.mid = mid
            self._current_spectrum.high = high

    def get_spectrum(self) -> SpectrumBand:
        """Get current spectrum bands (thread-safe).

        Returns:
            SpectrumBand with normalized frequency data
        """
        with self._spectrum_lock:
            return SpectrumBand(
                bass=self._current_spectrum.bass,
                mid=self._current_spectrum.mid,
                high=self._current_spectrum.high,
            )


class AudioReactiveField:
    """Main audio-reactive particle system.

    This class manages particles and responds to audio input. It can run
    in real-time mode (with microphone) or demo mode (with simulated audio).

    Attributes:
        particles: List of active particles
        capture: AudioCapture instance (None if running in demo mode)
        demo_mode: True if running without audio input
    """

    def __init__(self, width: int = 800, height: int = 600):
        """Initialize the audio-reactive field.

        Args:
            width: Canvas width
            height: Canvas height
        """
        self.width = width
        self.height = height
        self.particles: list[AudioParticle] = []

        # Initialize audio capture
        self.capture: AudioCapture | None = None
        self.demo_mode = not HAS_SOUNDDEVICE

        if HAS_SOUNDDEVICE:
            self.capture = AudioCapture()
            self.capture.start()
        else:
            print("sounddeviceなし。デモモードで実行します")

        # Demo mode simulation
        self.demo_time = 0.0
        self.paused = False
        self.bg_color = 10

    def get_spectrum(self) -> SpectrumBand:
        """Get current audio spectrum.

        Returns:
            SpectrumBand with frequency data (real or simulated)
        """
        if not self.demo_mode and self.capture is not None:
            return self.capture.get_spectrum()

        # Demo mode: simulate periodic audio
        self.demo_time += 0.016  # ~60fps
        bass = (math.sin(self.demo_time * 2) * 0.5 + 0.5) * 0.8
        mid = (math.sin(self.demo_time * 4) * 0.3 + 0.3) * 0.6
        high = (math.sin(self.demo_time * 8) * 0.3 + 0.3) * 0.6

        spectrum = SpectrumBand(bass=bass, mid=mid, high=high)
        spectrum.normalize()
        return spectrum

    def update(self) -> None:
        """Update all particles and spawn new ones based on audio."""
        if self.paused:
            return

        spectrum = self.get_spectrum()

        # Update background based on bass
        self.bg_color = int(10 + spectrum.bass * 40)

        # Spawn new particles based on mid frequencies
        spawn_count = 2 + int(spectrum.mid * 8)
        self._spawn_particles(spawn_count, spectrum)

        # Update existing particles
        alive_particles = []
        for particle in self.particles:
            particle.update()
            if particle.is_alive():
                alive_particles.append(particle)

        self.particles = alive_particles

    def _spawn_particles(self, count: int, spectrum: SpectrumBand) -> None:
        """Spawn new particles at center.

        Args:
            count: Number of particles to spawn
            spectrum: Current spectrum for color control
        """
        center_x = self.width / 2
        center_y = self.height / 2

        # Explosion radius based on bass
        radius = 100 + spectrum.bass * 200

        for _ in range(count):
            angle = np.random.uniform(0, 2 * math.pi)
            speed = np.random.uniform(1, 4)

            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed

            # Color shift based on high frequencies
            # Blue -> Purple -> Pink
            hue_shift = spectrum.high * 120
            if hue_shift < 60:
                # Blue to Purple
                r = int(100 + hue_shift)
                g = int(100 - hue_shift * 0.5)
                b = 200
            else:
                # Purple to Pink
                r = 200
                g = int(100 - (hue_shift - 60) * 0.5)
                b = int(200 - (hue_shift - 60))

            particle = AudioParticle(
                x=center_x,
                y=center_y,
                vx=vx,
                vy=vy,
                life=1.0,
                color=(max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))),
            )
            self.particles.append(particle)

    def reset(self) -> None:
        """Clear all particles."""
        self.particles.clear()
        self.demo_time = 0.0

    def toggle_demo_mode(self) -> None:
        """Toggle between demo and real audio mode."""
        if not HAS_SOUNDDEVICE:
            return

        self.demo_mode = not self.demo_mode
        if self.demo_mode:
            if self.capture is not None:
                self.capture.stop()
        else:
            if self.capture is not None:
                self.capture.start()

    def toggle_pause(self) -> None:
        """Toggle pause/resume."""
        self.paused = not self.paused

    def cleanup(self) -> None:
        """Clean up audio resources."""
        if self.capture is not None:
            self.capture.stop()


# Global field instance for py5 sketch
audio_field: AudioReactiveField | None = None


def setup() -> None:
    """Initialize the sketch."""
    global audio_field
    py5.size(1000, 800)
    py5.smooth()
    py5.background(0)
    audio_field = AudioReactiveField(width=1000, height=800)
    print(f"Demo mode: {audio_field.demo_mode}")
    print("Controls: m=mode, s=screenshot, r=reset, SPACE=pause, q=quit")


def draw() -> None:
    """Main animation loop."""
    if audio_field is None:
        return

    audio_field.update()
    py5.background(audio_field.bg_color)

    for particle in audio_field.particles:
        alpha = int(particle.life * 255)
        py5.fill(*particle.color, alpha)
        py5.no_stroke()
        py5.circle(particle.x, particle.y, 4)

    py5.fill(200)
    py5.text_size(11)
    py5.text(f"FPS: {py5.get_frame_rate():.1f}", 10, 20)
    py5.text(f"Particles: {len(audio_field.particles)}", 10, 35)
    mode = "Demo" if audio_field.demo_mode else "Mic"
    py5.text(f"Mode: {mode} (m to toggle)", 10, 50)
    py5.text("s=screenshot, r=reset, SPACE=pause", 10, py5.height - 10)


def key_pressed() -> None:
    """Handle key presses."""
    if audio_field is None:
        return

    key = py5.key

    if key == "s":
        filename = f"audio_reactive_{py5.frame_count:05d}.png"
        py5.save_frame(filename)
        print(f"Screenshot saved: {filename}")

    elif key == "m":
        audio_field.toggle_mode()

    elif key == "r":
        audio_field.particles.clear()

    elif key == " ":
        audio_field.toggle_pause()

    elif key == "q":
        py5.exit_sketch()


if __name__ == "__main__":
    py5.run_sketch()
