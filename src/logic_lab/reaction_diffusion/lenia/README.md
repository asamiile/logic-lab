# Lenia Continuous Cellular Automaton

Continuous generalization of Conway's Game of Life that produces gliding life-like creatures and complex emergent patterns. Introduced by Bert Wang-Chak Chan (2019).

```bash
uv run python src/logic_lab/reaction_diffusion/lenia/lenia.py
```

Press `1/2/3` to switch creature presets (orbium/geminium/scutium), `Space` to pause, or `s` to save a screenshot.

An annular bell-shaped kernel convolves with the activity field, and a bell-curve growth function drives evolution. The kernel radius `R`, growth center `mu`, and width `sigma` together determine whether the system produces stable gliders, oscillators, or chaos.
