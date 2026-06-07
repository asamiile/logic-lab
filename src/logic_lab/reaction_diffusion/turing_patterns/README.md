# Turing Patterns (Gierer-Meinhardt)

Activator-inhibitor reaction-diffusion system implementing Alan Turing's morphogenesis model. A short-range autocatalytic activator and a long-range inhibitor spontaneously generate animal coat-like patterns.

```bash
uv run python src/logic_lab/reaction_diffusion/turing_patterns/turing_patterns.py
```

Press `1/2/3` to switch presets (spots/stripes/labyrinth), `Space` to pause, or `s` to save a screenshot.

Pattern type is determined by the ratio of diffusion coefficients `Da`/`Dh` and the decay rates `mu_a`/`mu_h`. Slow activator diffusion relative to the inhibitor is the necessary condition for spatial pattern formation (Turing instability).
