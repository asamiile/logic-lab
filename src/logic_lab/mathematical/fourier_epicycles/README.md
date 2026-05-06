# Fourier Epicycles

Reconstructs closed curves from rotating circles using the discrete Fourier transform.

## Run

```bash
uv run python mathematical/fourier_epicycles/fourier_epicycles.py
```

## Controls

| Key | Effect |
|---|---|
| `p` | Switch source curve |
| `+` / `-` | Change number of epicycles |
| `<` / `>` | Change drawing speed |
| `c` | Toggle circle outlines |
| Space | Pause or resume animation |
| `s` | Save screenshot |

## Algorithm

Fourier epicycles decompose a sampled path into circular motions:

1. **Sample a curve**: Convert a closed 2D path into complex numbers.
2. **DFT**: Measure how strongly each frequency contributes to the path.
3. **Sort by amplitude**: Draw the largest rotating vectors first.
4. **Accumulate circles**: Each vector rotates at its frequency and starts at the previous vector endpoint.
5. **Trace the endpoint**: The final endpoint reconstructs the original path over time.

Using more epicycles captures more detail. Using fewer epicycles creates a simplified harmonic version of the same curve.

## Other Environments

**TouchDesigner**: Store sampled curve points in a DAT, compute DFT coefficients in Python, and instance circles or line segments from the coefficient list. Feed the final endpoint into a Trail SOP or CHOP for the drawing path.

**UE5**: Precompute coefficients in C++ or Blueprint, then animate spline or debug line components from the rotating vector chain. The endpoint trail can drive Niagara ribbons or spline mesh strokes.
