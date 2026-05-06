import queue
import threading
from pathlib import Path

import numpy as np
import py5
import sounddevice as sd

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

# Audio parameters
SAMPLE_RATE = 44100
CHUNK_SIZE = 2048
N_FFT = 4096

# Audio buffer
audio_queue = queue.Queue()
audio_thread = None
spectrum = np.zeros(N_FFT // 2, dtype=np.float32)
spectrogram_buffer = None

# Beat detection
beat_threshold = 0.0
beat_detected = False
beat_energy_history = []

# Visualization mode
vis_mode = 0  # 0: bars, 1: circular, 2: spectrogram


def audio_callback(indata, frames, time_info, status):
    """Callback for audio stream."""
    if status:
        print(f"Audio callback status: {status}")
    audio_queue.put(indata[:, 0].copy())


def audio_thread_fn():
    """Thread function for audio processing."""
    global spectrum, beat_detected, beat_energy_history, beat_threshold, spectrogram_buffer

    with sd.InputStream(
        callback=audio_callback,
        channels=1,
        samplerate=SAMPLE_RATE,
        blocksize=CHUNK_SIZE,
        dtype=np.float32,
    ):
        audio_buffer = np.zeros(N_FFT, dtype=np.float32)

        while True:
            try:
                chunk = audio_queue.get(timeout=0.1)
                audio_buffer[:-CHUNK_SIZE] = audio_buffer[CHUNK_SIZE:]
                audio_buffer[-CHUNK_SIZE:] = chunk

                # Compute FFT
                windowed = audio_buffer * np.hanning(N_FFT)
                fft_vals = np.abs(np.fft.rfft(windowed))
                spectrum = fft_vals[: N_FFT // 2]

                # Normalize
                spectrum_max = spectrum.max()
                if spectrum_max > 0:
                    spectrum = spectrum / spectrum_max * 255

                # Beat detection: check low-freq energy
                low_freq_energy = spectrum[: len(spectrum) // 8].mean()
                beat_energy_history.append(low_freq_energy)
                if len(beat_energy_history) > 20:
                    beat_energy_history.pop(0)

                beat_threshold = np.mean(beat_energy_history) * 1.3
                beat_detected = low_freq_energy > beat_threshold

            except queue.Empty:
                pass


def setup() -> None:
    global audio_thread, spectrogram_buffer
    py5.size(640, 480)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    # Initialize spectrogram buffer
    spectrogram_buffer = np.zeros((100, N_FFT // 2), dtype=np.uint8)

    # Start audio thread
    audio_thread = threading.Thread(target=audio_thread_fn, daemon=True)
    audio_thread.start()


def draw() -> None:
    global spectrum, beat_detected, spectrogram_buffer, vis_mode

    if vis_mode == 0:
        # Bar spectrum
        py5.background(0)
        bar_width = py5.width / len(spectrum)
        for i, val in enumerate(spectrum):
            color_val = int(val)
            py5.stroke(color_val, color_val // 2, 255 - color_val)
            py5.line(
                i * bar_width,
                py5.height,
                i * bar_width,
                py5.height - (val / 255) * py5.height,
            )

        # Draw beat indicator
        if beat_detected:
            py5.stroke(255, 0, 0)
            py5.stroke_weight(3)
            py5.rect(5, 5, 30, 30)

    elif vis_mode == 1:
        # Circular spectrum
        py5.background(0)
        cx, cy = py5.width / 2, py5.height / 2
        radius = min(cx, cy) * 0.8

        py5.no_fill()

        # Draw concentric circles
        n_rings = 5
        for ring in range(1, n_rings + 1):
            r = (radius / n_rings) * ring
            py5.stroke(100)
            py5.circle(cx, cy, r * 2)

        # Draw spectrum as rays
        n_samples = min(200, len(spectrum))
        angle_step = (2 * np.pi) / n_samples

        for i in range(n_samples):
            angle = i * angle_step
            mag = spectrum[i] / 255.0
            r = radius * mag

            x1 = cx + np.cos(angle) * (radius * 0.1)
            y1 = cy + np.sin(angle) * (radius * 0.1)
            x2 = cx + np.cos(angle) * r
            y2 = cy + np.sin(angle) * r

            hue = int((i / n_samples) * 255)
            py5.color_mode(py5.HSB)
            py5.stroke(hue, 200, 255)
            py5.stroke_weight(1)
            py5.line(x1, y1, x2, y2)
            py5.color_mode(py5.RGB)

        # Draw beat indicator
        if beat_detected:
            py5.stroke(255, 0, 0)
            py5.stroke_weight(3)
            py5.no_fill()
            py5.circle(cx, cy, radius * 1.2)

    else:
        # Spectrogram (waterfall display)
        py5.background(0)

        # Shift buffer and add new row
        spectrogram_buffer[:-1] = spectrogram_buffer[1:]
        n_freq = min(py5.width, len(spectrum))
        spectrogram_buffer[-1, :n_freq] = spectrum[:n_freq]

        # Draw spectrogram
        for y in range(spectrogram_buffer.shape[0]):
            for x in range(spectrogram_buffer.shape[1]):
                val = spectrogram_buffer[y, x]
                py5.color_mode(py5.HSB)
                py5.stroke(val, 255, 255)
                py5.point(x, py5.height - (y / spectrogram_buffer.shape[0]) * py5.height)
                py5.color_mode(py5.RGB)

    # Draw info
    py5.fill(255)
    py5.text_size(12)
    mode_names = ["Bars", "Circular", "Spectrogram"]
    py5.fill(255)
    py5.text(f"{mode_names[vis_mode]} | v: next view | s: save", 10, 20)


def key_pressed() -> None:
    global vis_mode

    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "audio_fft_####.png"))
    elif py5.key == "v":
        vis_mode = (vis_mode + 1) % 3


py5.run_sketch()
