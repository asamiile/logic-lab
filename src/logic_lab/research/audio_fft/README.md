# Audio FFT and Beat Detection

Real-time frequency analysis and beat detection from microphone input for music-reactive visuals.

## Run

```bash
uv run python src/logic_lab/research/audio_fft/audio_fft.py
```

**Note**: Requires microphone access. Grant permission when prompted by your system.

## Controls

| Key | Effect |
|---|---|
| `v` | Cycle through visualization modes (bars, circular, spectrogram) |
| `s` | Save screenshot |

## Algorithm

The visualization combines three components:

1. **FFT Spectrum**: `numpy.fft.rfft()` computes the Fast Fourier Transform of incoming audio (44.1 kHz sample rate, 4096-point window with Hanning window function)

2. **Visualization Modes**:
   - **Bars**: Vertical bars per frequency bin colored by magnitude
   - **Circular**: Polar plot where radius = magnitude, angle = frequency, color = hue cycling
   - **Spectrogram**: Waterfall display showing magnitude history over time

3. **Beat Detection**:
   - Extract low-frequency energy (bottom 1/8 of spectrum)
   - Maintain 20-sample history of energy
   - Trigger when current energy exceeds average × 1.3 threshold
   - Visual feedback: red flash on beat onset

Audio input captured in a background thread using `sounddevice`, preventing block. FFT updates every 2048 samples (~46ms at 44.1 kHz).

## Other Environments

**TouchDesigner**: The `Audio Analysis` CHOP provides built-in FFT and beat detection, making it the most efficient choice. Connect microphone input to Audio In TOP, route to Audio Analysis CHOP, and drive visualization parameters via the `chan` outputs.

**UE5**: MetaSounds and Audio Engine provide spectrum analysis via `GetFFTData` or `GetBeatDetection` nodes. Alternatively, route audio to a real-time spectrogram in the Audiolink system for particle/material-driven reactions.
