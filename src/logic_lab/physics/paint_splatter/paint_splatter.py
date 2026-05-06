from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

# Default values (matching original slider defaults)
SPREAD = 0.25
BASE_SIZE = 20 / 240  # sizeSlider / height
SIZE_SPREAD = 0.01
BASE_HUE = 250.0
HUE_SPREAD = 15.0
ALPHA = 0.75

# Watercolor bleed extensions
BLEED_RINGS = True
BLEED_MAX_DROPS = 200
BLEED_RING_LIFETIME = 90
BLEED_SPREAD_RATE = 0.18
BLEED_INITIAL_RADIUS = 0.005

active_drops: list = []


def spawn_bleed_drop(x: float, y: float, hue: float, sat: float, bright: float) -> None:
    """Register a new drop for bleed simulation."""
    global active_drops
    if len(active_drops) >= BLEED_MAX_DROPS:
        active_drops.pop(0)
    active_drops.append({
        "x": x, "y": y,
        "hue": hue, "sat": sat, "bright": bright,
        "age": 0,
        "radius": BLEED_INITIAL_RADIUS,
        "noise_seed": py5.random(10000),
    })


def draw_bleed_rings() -> None:
    """Draw all active bleed rings, aging them each frame."""
    global active_drops

    py5.push_matrix()
    py5.translate(py5.width / 2, py5.height / 2)
    py5.scale(py5.height / 2)

    for drop in active_drops:
        t = drop["age"] / BLEED_RING_LIFETIME
        alpha = (1.0 - t) ** 2 * 0.35
        if alpha < 0.005:
            continue

        dry_sat = drop["sat"] * (1.0 - t * 0.7)
        dry_bright = min(100, drop["bright"] + t * 25)

        py5.stroke(drop["hue"], dry_sat, dry_bright, alpha)
        py5.no_fill()

        r = drop["radius"]
        SEGMENTS = 24
        py5.begin_shape()
        for seg in range(SEGMENTS + 1):
            angle = (seg / SEGMENTS) * py5.TWO_PI
            noise_r = py5.noise(
                py5.cos(angle) * 0.5 + drop["noise_seed"],
                py5.sin(angle) * 0.5 + drop["noise_seed"] + 100,
                drop["age"] * 0.02,
            )
            perturb = 0.75 + 0.5 * noise_r
            perturb_r = r * perturb
            py5.vertex(
                drop["x"] + py5.cos(angle) * perturb_r,
                drop["y"] + py5.sin(angle) * perturb_r,
            )
        py5.end_shape(py5.CLOSE)

        drop["age"] += 1
        drop["radius"] += BLEED_SPREAD_RATE * (1.0 - t)

    py5.pop_matrix()

    active_drops = [d for d in active_drops if d["age"] < BLEED_RING_LIFETIME]


def setup() -> None:
    py5.size(640, 240)
    py5.color_mode(py5.HSB, 360, 100, 100, 1)
    py5.background(97, 0, 97)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.translate(py5.width / 2, py5.height / 2)
    py5.scale(py5.height / 2)

    x = py5.random_gaussian(0, SPREAD)
    y = py5.random_gaussian(0, SPREAD)
    size = py5.random_gaussian(BASE_SIZE, SIZE_SPREAD)
    if size <= 0:
        size = 0.001

    paint_hue = py5.random_gaussian(BASE_HUE, HUE_SPREAD) % 360
    paint_sat = min(py5.random_gaussian(80, 20), 100)
    paint_bright = min(py5.random_gaussian(80, 20), 100)

    py5.no_stroke()
    py5.fill(paint_hue, paint_sat, paint_bright, ALPHA)
    py5.ellipse(x, y, size, size)

    # Spawn bleed drop every 3 frames for performance
    if BLEED_RINGS and py5.frame_count % 3 == 0:
        spawn_bleed_drop(x, y, paint_hue, paint_sat, paint_bright)

    if BLEED_RINGS:
        draw_bleed_rings()


def key_pressed() -> None:
    global BLEED_RINGS, active_drops
    if py5.key == " ":
        py5.background(97, 0, 97)
        active_drops.clear()
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "paint_splatter_####.png"))
    elif py5.key == "b":
        BLEED_RINGS = not BLEED_RINGS


py5.run_sketch()
