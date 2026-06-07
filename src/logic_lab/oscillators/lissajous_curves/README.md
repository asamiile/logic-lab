# Lissajous Curves

Two sinusoidal oscillators drive the X and Y axes, tracing curves whose shape is determined by the frequency ratio a:b and phase offset delta. The LFOBank slowly drifts delta and zoom over time for a continuously evolving figure.

```bash
uv run python src/logic_lab/oscillators/lissajous_curves/lissajous_curves.py
```

Press `1/2/3/4` to switch presets (classic/knot/figure8/drift), `Space` to pause, `r` to reset the trail, or `s` to save a screenshot.

Integer frequency ratios produce closed curves; irrational ratios produce open, space-filling traces. The "drift" preset uses a slow LFO on the phase offset to smoothly morph between all possible shapes in the a:b family.
