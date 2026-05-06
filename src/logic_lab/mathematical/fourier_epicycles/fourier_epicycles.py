from __future__ import annotations

from pathlib import Path
import cmath
import math

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

Sample = complex
Coefficient = dict[str, float | int | complex]

PRESETS = ["star", "heart", "rose", "square"]

samples: list[Sample] = []
coefficients: list[Coefficient] = []
trace: list[tuple[float, float]] = []
preset_index = 0
circle_count = 32
speed = 1.0
show_circles = True
paused = False
time_value = 0.0


def setup() -> None:
    py5.size(800, 620)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    load_preset()


def draw() -> None:
    global time_value

    py5.background(220, 14, 96)
    py5.translate(py5.width * 0.5, py5.height * 0.53)

    endpoint = draw_epicycles(time_value)
    trace.insert(0, endpoint)
    trace[:] = trace[: len(samples)]

    draw_trace()

    if not paused:
        time_value += py5.TWO_PI / len(samples) * speed
        if time_value >= py5.TWO_PI:
            time_value %= py5.TWO_PI
            trace.clear()

    py5.reset_matrix()
    draw_info()


def load_preset() -> None:
    global samples, coefficients, trace, time_value

    samples = preset_samples(PRESETS[preset_index], 220)
    coefficients = sorted(dft(samples), key=lambda item: float(item["amplitude"]), reverse=True)
    trace = []
    time_value = 0.0


def preset_samples(name: str, count: int) -> list[Sample]:
    if name == "heart":
        return heart_samples(count)
    if name == "rose":
        return rose_samples(count)
    if name == "square":
        return square_samples(count)
    return star_samples(count)


def star_samples(count: int) -> list[Sample]:
    points = []
    for i in range(count):
        theta = py5.TWO_PI * i / count
        radius = 170 + 58 * math.cos(5 * theta)
        points.append(complex(math.cos(theta) * radius, math.sin(theta) * radius))
    return points


def heart_samples(count: int) -> list[Sample]:
    points = []
    for i in range(count):
        theta = py5.TWO_PI * i / count
        x = 16 * math.sin(theta) ** 3
        y = -(
            13 * math.cos(theta)
            - 5 * math.cos(2 * theta)
            - 2 * math.cos(3 * theta)
            - math.cos(4 * theta)
        )
        points.append(complex(x * 12, y * 12))
    return points


def rose_samples(count: int) -> list[Sample]:
    points = []
    for i in range(count):
        theta = py5.TWO_PI * i / count
        radius = 188 * math.sin(4 * theta)
        points.append(complex(math.cos(theta) * radius, math.sin(theta) * radius))
    return points


def square_samples(count: int) -> list[Sample]:
    corners = [
        complex(-170, -170),
        complex(170, -170),
        complex(170, 170),
        complex(-170, 170),
    ]
    points = []
    per_edge = count // 4
    for i in range(4):
        start = corners[i]
        end = corners[(i + 1) % 4]
        for step in range(per_edge):
            amount = step / per_edge
            points.append(start + (end - start) * amount)
    while len(points) < count:
        points.append(corners[0])
    return points[:count]


def dft(input_samples: list[Sample]) -> list[Coefficient]:
    result = []
    sample_count = len(input_samples)
    for frequency in range(sample_count):
        total = 0j
        for index, value in enumerate(input_samples):
            angle = -py5.TWO_PI * frequency * index / sample_count
            total += value * cmath.exp(1j * angle)
        total /= sample_count
        shifted_frequency = frequency
        if frequency > sample_count // 2:
            shifted_frequency = frequency - sample_count
        result.append(
            {
                "frequency": shifted_frequency,
                "amplitude": abs(total),
                "phase": cmath.phase(total),
                "value": total,
            }
        )
    return result


def draw_epicycles(t: float) -> tuple[float, float]:
    x = 0.0
    y = 0.0
    active = coefficients[:circle_count]

    for i, coefficient in enumerate(active):
        previous_x = x
        previous_y = y
        frequency = int(coefficient["frequency"])
        amplitude = float(coefficient["amplitude"])
        phase = float(coefficient["phase"])
        angle = frequency * t + phase
        x += math.cos(angle) * amplitude
        y += math.sin(angle) * amplitude

        hue = (198 + i * 8) % 360
        if show_circles:
            py5.no_fill()
            py5.stroke(hue, 34, 52, 30)
            py5.stroke_weight(1)
            py5.circle(previous_x, previous_y, amplitude * 2)

        py5.stroke(hue, 70, 30, 76)
        py5.stroke_weight(1.4)
        py5.line(previous_x, previous_y, x, y)
        py5.no_stroke()
        py5.fill(42, 94, 98, 88)
        py5.circle(x, y, 4)

    return x, y


def draw_trace() -> None:
    if len(trace) < 2:
        return

    py5.no_fill()
    py5.stroke(26, 86, 94, 98)
    py5.stroke_weight(2.6)
    py5.begin_shape()
    for x, y in trace:
        py5.vertex(x, y)
    py5.end_shape()

    py5.stroke(210, 42, 20, 28)
    py5.stroke_weight(1)
    py5.begin_shape()
    for point in samples:
        py5.vertex(point.real, point.imag)
    py5.end_shape(py5.CLOSE)


def draw_info() -> None:
    py5.no_stroke()
    py5.fill(220, 24, 12, 90)
    py5.rect(14, 14, 610, 54, 4)
    py5.fill(0, 0, 100, 100)
    py5.text(
        f"Fourier epicycles | {PRESETS[preset_index]} | circles {circle_count} | p: preset | +/-: circles | </>: speed {speed:.1f} | c: circles | space: pause | s: save",
        24,
        46,
    )


def key_pressed() -> None:
    global preset_index, circle_count, speed, show_circles, paused

    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "fourier_epicycles_####.png"))
    elif py5.key == "p":
        preset_index = (preset_index + 1) % len(PRESETS)
        load_preset()
    elif py5.key == "+":
        circle_count = min(len(coefficients), circle_count + 4)
        trace.clear()
    elif py5.key == "-":
        circle_count = max(1, circle_count - 4)
        trace.clear()
    elif py5.key == "." or py5.key == ">":
        speed = min(4.0, speed + 0.2)
    elif py5.key == "," or py5.key == "<":
        speed = max(0.2, speed - 0.2)
    elif py5.key == "c":
        show_circles = not show_circles
    elif py5.key == " ":
        paused = not paused


py5.run_sketch()
