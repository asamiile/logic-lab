# Space Colonization Algorithm

Generates realistic tree and vascular network structures via competition between branch tips for scattered auxin attractors. Each tip grows toward nearby attractors; consumed attractors are removed. The result fills the attractor cloud with organic branching.

```bash
uv run python src/logic_lab/biological/space_colonization/space_colonization.py
```

Press `1/2/3` to switch presets (tree/coral/network), `r` to reset, `Space` to pause, or `s` to save a screenshot.

Branch color deepens with depth (dark trunk → bright tips). Small green dots are unconsumed attractors. Adjust `INFLUENCE_RADIUS`, `KILL_RADIUS`, and `SEGMENT_LEN` to control branching density and character — larger influence radius creates sparse elegant trees; smaller produces dense fractals.
