# Diffusion-Limited Aggregation (DLA)

Particles perform random walks until they contact a growing aggregate, where they permanently stick. The resulting fractal cluster has a characteristic branching, dendritic form resembling snowflakes, coral, lightning, or mineral deposits.

```bash
uv run python src/logic_lab/biological/dla/dla.py
```

Press `1/2/3` to switch growth modes (radial/linear/circular), `r` to reset, `Space` to pause, or `s` to save a screenshot.

Color encodes the order in which particles joined the aggregate: deep blue = early (old branches), white/cyan = recent growth. Radial mode grows a symmetric crystal from the center; linear grows a terrain-like boundary; circular fills inward from a ring seed.
