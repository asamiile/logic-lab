from pathlib import Path
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

# State
time_offset = 0
harmony_mode = 0  # 0: complementary, 1: analogous, 2: triadic


def setup() -> None:
    py5.size(640, 240)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global time_offset
    py5.background(255)

    # Base hue from Perlin noise, animated over time
    base_hue = (py5.noise(time_offset * 0.5) * 360) % 360
    time_offset += 0.01

    # Saturation and brightness
    sat = 80
    bright = 85

    # Generate harmony palette based on mode
    if harmony_mode == 0:  # Complementary
        hues = [base_hue, (base_hue + 180) % 360]
        title = "Complementary"
    elif harmony_mode == 1:  # Analogous
        hues = [
            (base_hue - 30) % 360,
            base_hue,
            (base_hue + 30) % 360,
        ]
        title = "Analogous"
    else:  # Triadic
        hues = [
            base_hue,
            (base_hue + 120) % 360,
            (base_hue + 240) % 360,
        ]
        title = "Triadic"

    # Draw color bands
    band_width = py5.width / len(hues)
    for i, hue in enumerate(hues):
        x = i * band_width
        py5.fill(hue, sat, bright)
        py5.rect(x, 0, band_width, py5.height * 0.8)

        # Draw variations (darker and lighter)
        py5.fill(hue, sat, 60)
        py5.rect(x, py5.height * 0.8, band_width, py5.height * 0.1)

        py5.fill(hue, sat, 95)
        py5.rect(x, py5.height * 0.9, band_width, py5.height * 0.1)

    # Draw info
    py5.fill(0)
    py5.text(f"{title} | Base Hue: {base_hue:.0f}°", 10, py5.height - 10)


def key_pressed() -> None:
    global harmony_mode
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "color_harmony_####.png"))
    elif py5.key == "1":
        harmony_mode = 0
    elif py5.key == "2":
        harmony_mode = 1
    elif py5.key == "3":
        harmony_mode = 2


py5.run_sketch()
