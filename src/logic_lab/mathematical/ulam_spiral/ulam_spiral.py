import math
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

GRID_SIZE = 111
CELL_SIZE = 6
MAX_NUMBER = GRID_SIZE * GRID_SIZE

primes: list[bool] = []
positions: list[tuple[int, int]] = []
mode = 0
modulus = 12
show_lines = True


def setup() -> None:
    global primes, positions

    py5.size(740, 740)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    primes = sieve(MAX_NUMBER)
    positions = ulam_positions(GRID_SIZE)


def draw() -> None:
    py5.background(220, 12, 96)
    py5.translate(py5.width / 2, py5.height / 2)

    if show_lines:
        draw_spiral_path()

    if mode == 0:
        draw_prime_dots()
    elif mode == 1:
        draw_prime_residue_dots()
    else:
        draw_composite_density()

    py5.reset_matrix()
    draw_info()


def sieve(limit: int) -> list[bool]:
    result = [True] * (limit + 1)
    result[0] = False
    result[1] = False

    for number in range(2, int(math.sqrt(limit)) + 1):
        if not result[number]:
            continue
        for multiple in range(number * number, limit + 1, number):
            result[multiple] = False

    return result


def ulam_positions(size: int) -> list[tuple[int, int]]:
    coords = [(0, 0)] * (size * size + 1)
    x = 0
    y = 0
    number = 1
    coords[number] = (x, y)

    step_length = 1
    directions = [(1, 0), (0, -1), (-1, 0), (0, 1)]
    direction_index = 0

    while number < size * size:
        for _ in range(2):
            dx, dy = directions[direction_index % 4]
            for _ in range(step_length):
                if number >= size * size:
                    break
                x += dx
                y += dy
                number += 1
                coords[number] = (x, y)
            direction_index += 1
        step_length += 1

    return coords


def draw_spiral_path() -> None:
    py5.no_fill()
    py5.stroke(220, 12, 72, 22)
    py5.stroke_weight(1)
    py5.begin_shape()
    for number in range(1, MAX_NUMBER + 1):
        x, y = positions[number]
        py5.vertex(x * CELL_SIZE, y * CELL_SIZE)
    py5.end_shape()


def draw_prime_dots() -> None:
    py5.no_stroke()
    for number in range(2, MAX_NUMBER + 1):
        if primes[number]:
            x, y = positions[number]
            radius = 4.4 if number < 1000 else 3.3
            py5.fill(38, 86, 24, 92)
            py5.circle(x * CELL_SIZE, y * CELL_SIZE, radius + 1.3)
            py5.fill(50, 96, 98, 98)
            py5.circle(x * CELL_SIZE, y * CELL_SIZE, radius)


def draw_prime_residue_dots() -> None:
    py5.no_stroke()
    for number in range(2, MAX_NUMBER + 1):
        if not primes[number]:
            continue
        x, y = positions[number]
        hue = (number % modulus) * 360 / modulus
        py5.fill(hue, 76, 96, 94)
        py5.circle(x * CELL_SIZE, y * CELL_SIZE, 4.2)


def draw_composite_density() -> None:
    py5.rect_mode(py5.CENTER)
    py5.no_stroke()
    for number in range(2, MAX_NUMBER + 1):
        x, y = positions[number]
        px = x * CELL_SIZE
        py = y * CELL_SIZE
        if primes[number]:
            py5.fill(45, 94, 100, 95)
            py5.circle(px, py, 4.6)
        else:
            factors = small_factor_count(number)
            hue = 190 + min(factors, 6) * 18
            py5.fill(hue, 54, 42 + min(factors, 6) * 8, 42)
            py5.rect(px, py, 4, 4)
    py5.rect_mode(py5.CORNER)


def small_factor_count(number: int) -> int:
    count = 0
    for divisor in range(2, min(32, int(math.sqrt(number)) + 1)):
        if number % divisor == 0:
            count += 1
    return count


def draw_info() -> None:
    py5.no_stroke()
    py5.fill(220, 20, 12, 90)
    py5.rect(14, 14, 500, 52, 4)
    py5.fill(0, 0, 100, 100)
    mode_name = ["prime dots", "prime residues", "factor density"][mode]
    py5.text(
        f"Ulam spiral | {mode_name} | primes <= {MAX_NUMBER} | m: mode | +/-: modulus {modulus} | l: line | s: save",
        24,
        45,
    )


def key_pressed() -> None:
    global mode, modulus, show_lines

    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "ulam_spiral_####.png"))
    elif py5.key == "m":
        mode = (mode + 1) % 3
    elif py5.key == "l":
        show_lines = not show_lines
    elif py5.key == "+":
        modulus = min(36, modulus + 1)
    elif py5.key == "-":
        modulus = max(2, modulus - 1)


py5.run_sketch()
