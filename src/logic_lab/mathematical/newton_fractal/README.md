# Newton Fractal

Visualizes Newton-Raphson convergence basins for complex polynomials.

## Run

```bash
uv run python src/logic_lab/mathematical/newton_fractal/newton_fractal.py
```

## Controls

| Key | Effect |
|---|---|
| `n` | Switch polynomial |
| `+` / `-` | Zoom in or out |
| `<` / `>` | Change maximum iterations |
| `s` | Save screenshot |

## Algorithm

Newton's method iteratively finds roots:

```text
z[n + 1] = z[n] - f(z[n]) / f'(z[n])
```

For each complex starting point, the sketch applies Newton's method and records which root it converges to. The root determines hue, while the iteration count controls brightness. Points near basin boundaries converge slowly and form fractal edges.

Newton fractals are useful for visualizing numerical methods, complex dynamics, convergence basins, and intricate mathematical textures.

## Other Environments

**TouchDesigner**: Implement the Newton iteration in a GLSL TOP, mapping each pixel to a complex starting point and coloring by root basin.

**UE5**: Use a Custom material node or compute shader to iterate the complex polynomial per pixel and map convergence results to color.
