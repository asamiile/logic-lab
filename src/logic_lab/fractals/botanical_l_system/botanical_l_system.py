from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from random import Random

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


@dataclass(frozen=True)
class PlantPreset:
    name: str
    axiom: str
    rules: dict[str, str]
    generations: int
    step: float
    angle: float
    seed: int
    stem_hue: float
    leaf_hue: float
    flower_hue: float


PRESETS = [
    PlantPreset(
        name="fern canopy",
        axiom="X",
        rules={"X": "F-[[X]+X]+F[+FX]-X", "F": "FF"},
        generations=5,
        step=4.2,
        angle=24,
        seed=14,
        stem_hue=95,
        leaf_hue=135,
        flower_hue=320,
    ),
    PlantPreset(
        name="flowering herb",
        axiom="A",
        rules={"A": "F[+L][-L]F[+A]F[-A]+B", "B": "F[+L]F[-L]O", "F": "FF"},
        generations=4,
        step=5.4,
        angle=19,
        seed=31,
        stem_hue=86,
        leaf_hue=128,
        flower_hue=338,
    ),
    PlantPreset(
        name="vine tendrils",
        axiom="F",
        rules={"F": "F[+F]F[-F][L]F"},
        generations=4,
        step=6.0,
        angle=28,
        seed=72,
        stem_hue=108,
        leaf_hue=148,
        flower_hue=42,
    ),
]

preset_index = 0
sentence = ""
rng = Random(0)


def expand(axiom: str, rules: dict[str, str], generations: int) -> str:
    current = axiom
    for _ in range(generations):
        current = "".join(rules.get(symbol, symbol) for symbol in current)
    return current


def configure_preset(index: int) -> None:
    global preset_index, sentence, rng
    preset_index = index % len(PRESETS)
    preset = PRESETS[preset_index]
    sentence = expand(preset.axiom, preset.rules, preset.generations)
    rng = Random(preset.seed)


def max_branch_depth(source: str) -> int:
    depth = 0
    result = 0
    for symbol in source:
        if symbol == "[":
            depth += 1
            result = max(result, depth)
        elif symbol == "]":
            depth = max(0, depth - 1)
    return max(result, 1)


def draw_leaf(size: float, hue: float) -> None:
    py5.push_matrix()
    py5.rotate(py5.radians(rng.uniform(-18, 18)))
    py5.no_stroke()
    py5.fill(hue + rng.uniform(-8, 8), 58, 72, 78)
    py5.begin_shape()
    py5.vertex(0, 0)
    py5.bezier_vertex(size * 0.42, -size * 0.36, size * 0.62, -size * 1.0, 0, -size * 1.35)
    py5.bezier_vertex(-size * 0.62, -size * 1.0, -size * 0.42, -size * 0.36, 0, 0)
    py5.end_shape(py5.CLOSE)
    py5.pop_matrix()


def draw_flower(size: float, hue: float) -> None:
    py5.push_matrix()
    py5.no_stroke()
    for i in range(7):
        py5.push_matrix()
        py5.rotate(py5.TWO_PI * i / 7)
        py5.fill(hue + rng.uniform(-12, 12), 52, 88, 82)
        py5.ellipse(0, -size * 0.46, size * 0.42, size)
        py5.pop_matrix()
    py5.fill(47, 75, 96, 95)
    py5.circle(0, 0, size * 0.45)
    py5.pop_matrix()


def render_plant() -> None:
    preset = PRESETS[preset_index]
    branch_depth = 0
    max_depth = max_branch_depth(sentence)

    for symbol in sentence:
        depth_ratio = min(branch_depth / max_depth, 1.0)
        step = preset.step * (1.0 - depth_ratio * 0.34) * rng.uniform(0.86, 1.12)

        if symbol in {"F", "A", "B", "X"}:
            weight = max(0.55, 3.7 * (1.0 - depth_ratio) + 0.35)
            py5.stroke(preset.stem_hue + rng.uniform(-8, 8), 50, 42 + depth_ratio * 28, 76)
            py5.stroke_weight(weight)
            py5.line(0, 0, 0, -step)
            py5.translate(0, -step)
        elif symbol == "+":
            py5.rotate(py5.radians(preset.angle + rng.uniform(-6, 6)))
        elif symbol == "-":
            py5.rotate(py5.radians(-preset.angle + rng.uniform(-6, 6)))
        elif symbol == "[":
            branch_depth += 1
            py5.push_matrix()
        elif symbol == "]":
            py5.pop_matrix()
            branch_depth = max(0, branch_depth - 1)
        elif symbol == "L":
            draw_leaf(preset.step * rng.uniform(1.8, 2.9), preset.leaf_hue)
        elif symbol == "O":
            draw_flower(preset.step * rng.uniform(1.4, 2.1), preset.flower_hue)


def setup() -> None:
    py5.size(900, 900)
    py5.smooth()
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    configure_preset(0)


def draw() -> None:
    py5.background(48, 13, 96)
    rng.seed(PRESETS[preset_index].seed)
    py5.translate(py5.width / 2, py5.height - 55)
    py5.rotate(py5.radians(rng.uniform(-2.5, 2.5)))
    render_plant()
    py5.no_loop()


def key_pressed() -> None:
    if py5.key in {"1", "2", "3"}:
        configure_preset(int(py5.key) - 1)
        py5.redraw()
    elif py5.key == "r":
        preset = PRESETS[preset_index]
        PRESETS[preset_index] = replace(preset, seed=preset.seed + 1)
        configure_preset(preset_index)
        py5.redraw()
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "botanical_l_system_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
