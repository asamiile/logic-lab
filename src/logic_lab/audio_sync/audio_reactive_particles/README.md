# Audio-Reactive Particles

Real-time visualization of audio frequencies through an interactive particle system. Particles spawn and animate in response to bass, mid, and high-frequency content from microphone input or simulated audio.

## Features

- **Real-time Audio Analysis**: FFT-based frequency analysis with three bands (bass, mid, high)
- **Frequency-Driven Animation**: Particle spawning and color shifts controlled by audio spectrum
- **Fallback Demo Mode**: Graceful degradation with simulated audio when sounddevice is unavailable
- **Thread-Safe Audio Processing**: Background audio capture with safe spectrum access
- **Interactive Controls**:
  - `m`: Toggle between mic input and demo mode
  - `s`: Screenshot
  - `r`: Reset (clear all particles)
  - `SPACE`: Pause/Resume

## Architecture

### AudioParticle
Individual particle with position, velocity, lifetime, and color.
- Life cycles from 1.0 (newborn) to 0 (dead)
- Applies gravity/damping during physics updates
- Tracks RGB color that shifts based on frequency content

### SpectrumBand
Normalized frequency spectrum data.
- `bass` (0-300 Hz): Low frequencies control explosion radius and background intensity
- `mid` (300-3000 Hz): Mid frequencies control particle spawn rate
- `high` (3000+ Hz): High frequencies control color shifts and sparkle effects

### AudioCapture
Manages microphone input in a background thread.
- Captures 1-channel float32 audio at configurable sample rate (default 22.05 kHz)
- Computes FFT and extracts energy from three frequency bands
- Thread-safe spectrum access via `get_spectrum()`

### AudioReactiveField
Main visualization system.
- Manages particle list and lifecycle
- Integrates audio input (real or simulated)
- Implements audio-driven effects:
  - Bass drives explosion radius and background color
  - Mid frequencies control spawn rate
  - High frequencies shift particle colors (blue → purple → pink)

## Audio Processing Pipeline

```
Microphone Input
       ↓
AudioCapture (background thread)
       ↓
FFT + Windowing
       ↓
Frequency Band Analysis
       ↓
Normalization (sum = 1.0)
       ↓
SpectrumBand (thread-safe)
       ↓
AudioReactiveField.update()
       ↓
Particle Spawning & Animation
```

## Frequency Mapping

### Bass (0-300 Hz)
Controls low-end visual impact:
- Explosion radius: `100 + bass * 200` pixels
- Background intensity: `10 + bass * 40`

### Mid (300-3000 Hz)
Controls particle generation:
- Spawn rate: `2 + int(mid * 8)` particles per frame

### High (3000+ Hz)
Controls color and sparkle:
- Hue shift: `0-120°` based on high energy
- Color: Blue (low) → Purple (mid) → Pink (high)

## Demo Mode

When `sounddevice` is not available, the system generates simulated audio:

```python
bass = sin(time * 2) * 0.5 + 0.5    # ~1 Hz oscillation
mid = sin(time * 4) * 0.3 + 0.3     # ~2 Hz oscillation
high = sin(time * 8) * 0.3 + 0.3    # ~4 Hz oscillation
```

This provides a smooth, predictable visualization for testing and demonstration.

## Running the Simulation

Interactive simulation with real-time controls:

```bash
python -m logic_lab.audio_sync.audio_reactive_particles.audio_reactive_particles
```

## Usage Example

```python
from logic_lab.audio_sync.audio_reactive_particles import AudioReactiveField
import py5

field = AudioReactiveField(width=800, height=600)

def setup():
    py5.size(800, 600)
    py5.background(0)

def draw():
    py5.background(field.bg_color)

    field.update()

    for particle in field.particles:
        py5.fill(*particle.color, int(particle.life * 255))
        py5.circle(particle.x, particle.y, 4)

def key_pressed():
    if py5.key == 'm':
        field.toggle_demo_mode()
    elif py5.key == 'r':
        field.reset()
    elif py5.key == ' ':
        field.toggle_pause()

py5.run_sketch()
```

## Dependencies

- `numpy`: FFT computation and array operations
- `sounddevice` (optional): Real microphone input
- `py5`: Visualization (example only)

## Thread Safety

- Audio capture runs in a background thread
- Spectrum access is protected by a threading lock
- Main update loop can safely call `get_spectrum()` without blocking

## Performance

- FFT computation: ~1-2ms per 1024 samples at 22050 Hz
- Particle physics: O(n) where n is particle count
- Typically runs 60+ FPS with 1000+ particles
