# Mandelbrot / Julia

Visualizes escape-time fractals for the quadratic complex map.

## Run

```bash
uv run python mathematical/mandelbrot_julia/mandelbrot_julia.py
```

## Controls

| Key | Effect |
|---|---|
| `m` | Toggle Mandelbrot or Julia mode |
| `n` | Switch Julia constant preset |
| `+` / `-` | Zoom in or out |
| `<` / `>` | Change maximum iterations |
| `c` | Switch color mode |
| `s` | Save screenshot |

## Algorithm

Both images come from iterating the quadratic map:

```text
z[n + 1] = z[n]^2 + c
```

For the Mandelbrot set, each pixel is a different `c` and starts at `z = 0`. For a Julia set, `c` is fixed and each pixel is the starting value of `z`. The sketch colors points by how quickly they escape beyond radius `2`; points that do not escape within the iteration limit are drawn dark.

The same recurrence reveals connectedness, fractal boundaries, spirals, islands, and dust-like structures depending on the constant and view.

## Other Environments

**TouchDesigner**: Implement the escape loop in a GLSL TOP and expose `c`, zoom, and iteration count as uniforms.

**UE5**: Use a Custom material node or compute shader to iterate the complex recurrence per pixel and color by escape time.
