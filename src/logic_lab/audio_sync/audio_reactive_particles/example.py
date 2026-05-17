"""Example visualization of audio-reactive particles.

This example demonstrates interactive audio-reactive visualization that responds
to microphone input (or simulated audio in demo mode).

Controls:
  m - Toggle between microphone and demo mode
  s - Save screenshot
  r - Reset particles
  SPACE - Pause/Resume
  q - Quit
"""

try:
    import py5
except ImportError:
    print("py5 is required for this example. Install with: pip install py5")
    exit(1)

from logic_lab.audio_sync.audio_reactive_particles import AudioReactiveField

field: AudioReactiveField


def setup() -> None:
    """Initialize the sketch."""
    global field
    py5.size(1000, 800)
    py5.smooth()
    py5.background(0)
    field = AudioReactiveField(width=1000, height=800)
    print(f"Demo mode: {field.demo_mode}")
    print("Controls: m=mode, s=screenshot, r=reset, SPACE=pause, q=quit")


def draw() -> None:
    """Main animation loop."""
    # Update field
    field.update()

    # Draw background
    py5.background(field.bg_color)

    # Draw particles
    for particle in field.particles:
        alpha = int(particle.life * 255)
        py5.fill(*particle.color, alpha)
        py5.no_stroke()
        py5.circle(particle.x, particle.y, 4)

    # Draw info text
    spectrum = field.get_spectrum()
    py5.fill(200, 200, 200)
    py5.text_size(12)
    py5.text(f"Particles: {len(field.particles)}", 10, 20)
    py5.text(f"Demo: {field.demo_mode}", 10, 40)
    py5.text(f"Bass: {spectrum.bass:.2f}", 10, 60)
    py5.text(f"Mid: {spectrum.mid:.2f}", 10, 80)
    py5.text(f"High: {spectrum.high:.2f}", 10, 100)
    py5.text(f"FPS: {py5.frame_rate:.0f}", 10, 120)


def key_pressed() -> None:
    """Handle keyboard input."""
    if py5.key == "m":
        field.toggle_demo_mode()
        print(f"Switched to {'demo' if field.demo_mode else 'audio'} mode")
    elif py5.key == "r":
        field.reset()
        print("Particles reset")
    elif py5.key == " ":
        field.toggle_pause()
        print(f"{'Paused' if field.paused else 'Resumed'}")
    elif py5.key == "s":
        import time

        filename = f"audio_particles_{int(time.time())}.png"
        py5.save_frame(filename)
        print(f"Screenshot saved: {filename}")
    elif py5.key == "q":
        field.cleanup()
        py5.exit()


if __name__ == "__main__":
    py5.run_sketch()
