# Belousov-Zhabotinsky Reaction

Chemical oscillator simulation producing self-organizing spiral waves and concentric target patterns. Models the Oregonator approximation of the BZ reaction on a 2D grid.

```bash
uv run python src/logic_lab/reaction_diffusion/belousov_zhabotinsky/belousov_zhabotinsky.py
```

Press `1/2/3` to switch presets (spiral/target/turbulent), `Space` to pause, or `s` to save a screenshot.

The interplay between the activator (u) and inhibitor (v) fields, separated by time scale `eps`, produces rotating spirals, concentric rings, or turbulent wave patterns depending on the stoichiometric parameters.
