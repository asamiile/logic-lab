# Flappy Bird

```bash
uv run python neuro_evolution/flappy_bird/flappy_bird.py
```

- Classic Flappy Bird game mechanics implemented in py5
- A bird maintains constant horizontal position (x = 50) and falls due to gravity
- Click the mouse to make the bird flap (jump)
- Pipes scroll from right to left at constant velocity
- New pipes are generated every 100 frames
- Collision detection when the bird hits a pipe or the floor
- Press `s` to save a screenshot to `neuro_evolution/flappy_bird/screenshots/`

## How it works

1. **Bird physics**:
   - Gravity constantly pulls the bird downward (+0.5 pixels per frame²)
   - Flapping applies an upward force (-10 pixels per frame)
   - Velocity is damped by 0.95 each frame (friction)
   - Bird stops at the floor (bottom of screen)

2. **Pipes**:
   - Each pipe has a gap of 100 pixels (spacing)
   - Top of gap is randomized between 0 and (height - spacing)
   - Pipes move left at 2 pixels per frame
   - Removed when they scroll off-screen

3. **Collision detection**:
   - Checks if bird is vertically outside the gap (above top or below bottom)
   - AND if bird is within the horizontal range of the pipe
   - Shows "OOPS!" when collision occurs

## Controls

- **Click mouse**: Make the bird flap/jump
- **S key**: Save a screenshot

This example demonstrates:
- Physics simulation (gravity, velocity, damping)
- Collision detection
- Game loop mechanics
- Object management (creating and removing pipes)

This is the foundation for adding neural networks and genetic algorithms in future examples to create an AI that learns to play the game.
