# Harmonic Pantograph

A chain of rotating arms — each an independent oscillator — draws the combined tip path (spirograph / epicycloid). This is equivalent to a Fourier epicycle decomposition: N arms can approximate any closed curve by choosing the right radii and angular frequencies.

```bash
uv run python src/logic_lab/oscillators/harmonic_pantograph/harmonic_pantograph.py
```

Press `1/2/3/4` to switch presets (trident/rose/star/wave), `r` to reset the trail, `Space` to pause, or `s` to save a screenshot.

The LFOBank slowly modulates arm speed and the second arm's frequency, producing curves that continuously drift and morph. Ghost arm lines show the current mechanical linkage while the trail accumulates the swept path.
