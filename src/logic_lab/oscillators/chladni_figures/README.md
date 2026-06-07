# Chladni Figures

Visualize standing wave nodal patterns on a 2D plate. Points where the displacement function equals zero (nodal lines) are rendered bright; the rest is dark — replicating the sand patterns Ernst Chladni observed on vibrating metal plates.

```bash
uv run python src/logic_lab/oscillators/chladni_figures/chladni_figures.py
```

Press `←/→` to step through resonant modes, `Space` to pause, or `s` to save a screenshot.

Each mode is defined by an integer pair (m, n). The LFOBank slowly oscillates the nodal threshold and cross-fades between adjacent modes, making the figures breathe and morph over time.
