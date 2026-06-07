# Strange Attractors

Chaotic dynamical systems producing fractal trajectories that never repeat yet remain confined to a geometric form. Five classic attractors rendered in 3D with perspective projection and depth-based coloring; an LFO slowly rotates the view.

```bash
uv run python src/logic_lab/mathematical/strange_attractors/strange_attractors.py
```

Press `1/2/3/4/5` to switch attractors (Lorenz/Rössler/Thomas/Aizawa/Dadras), `Space` to pause, or `s` to save a screenshot.

4000 particles integrate simultaneously, each starting at a slightly different initial condition. Tiny differences grow exponentially (sensitive dependence), revealing the attractor's fractal structure. Color encodes position along the chosen axis; depth sorting gives a sense of 3D volume.
