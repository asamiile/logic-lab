# Stable Fluids

Real-time incompressible fluid simulation using Jos Stam's unconditionally stable semi-Lagrangian scheme (1999). Drag the mouse to inject velocity and colored dye; random impulses keep the fluid in motion autonomously.

```bash
uv run python src/logic_lab/physics/stable_fluids/stable_fluids.py
```

Drag the mouse to paint fluid. Press `r` to clear, `Space` to pause, or `s` to save a screenshot.

The simulation runs on a 128×128 grid (upscaled 5×). Each frame: forces are added, velocity is diffused, projected to be divergence-free (ensuring incompressibility), then advected. Dye color cycles through the hue spectrum as you paint.
