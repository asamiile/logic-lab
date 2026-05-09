from __future__ import annotations

import math
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

waveforms = ["square", "sawtooth", "triangle"]
waveform_index = 0
harmonics = 9
phase = 0.0


def setup() -> None:
    py5.size(760, 440)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def component(n: int, t: float, waveform: str) -> float:
    if waveform == "square":
        k = n * 2 + 1
        return math.sin(k * t) / k
    if waveform == "triangle":
        k = n * 2 + 1
        sign = -1 if n % 2 else 1
        return sign * math.sin(k * t) / (k * k)
    k = n + 1
    return ((-1) ** (k + 1)) * math.sin(k * t) / k


def synth(t: float, waveform: str) -> float:
    total = sum(component(n, t, waveform) for n in range(harmonics))
    if waveform == "triangle":
        return total * 0.82
    return total


def draw() -> None:
    global phase
    phase += 0.035
    waveform = waveforms[waveform_index]
    py5.background(48, 16, 9)

    py5.stroke(48, 10, 70, 35)
    for i in range(1, harmonics + 1):
        x = 42 + i * 24
        h = abs(component(i - 1, phase, waveform)) * 230
        py5.line(x, 376, x, 376 - h)

    py5.no_fill()
    py5.stroke(190, 72, 96)
    py5.stroke_weight(3)
    py5.begin_shape()
    for x in range(44, py5.width - 43):
        t = (x - 44) / (py5.width - 88) * py5.TWO_PI * 2 + phase
        y = py5.height * 0.45 - synth(t, waveform) * 96
        py5.vertex(x, y)
    py5.end_shape()

    py5.stroke(34, 72, 96, 70)
    py5.stroke_weight(1.2)
    for n in range(harmonics):
        py5.begin_shape()
        for x in range(44, py5.width - 43, 4):
            t = (x - 44) / (py5.width - 88) * py5.TWO_PI * 2 + phase
            y = py5.height * 0.45 - component(n, t, waveform) * 96
            py5.vertex(x, y)
        py5.end_shape()

    py5.fill(44, 80, 96)
    py5.no_stroke()
    py5.text_size(16)
    py5.text(f"{waveform} wave  harmonics {harmonics}", 26, 30)


def key_pressed() -> None:
    global waveform_index, harmonics
    if py5.key == " ":
        waveform_index = (waveform_index + 1) % len(waveforms)
    elif py5.key in ("+", "="):
        harmonics = min(32, harmonics + 2)
    elif py5.key == "-":
        harmonics = max(1, harmonics - 2)
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "fourier_wave_synthesis_####.png"))


py5.run_sketch()
