# 3D L-System (Fractal Tree)

Lindenmayer system that generates 3D branching botanical structures by rewriting a symbol string and interpreting it with a 3D turtle. Rotation commands (`+/-` yaw, `^/&` pitch, `\/` roll) build a perspective-projected tree from recursive rules.

```bash
uv run python src/logic_lab/three_dimensional/lsystem_3d/lsystem_3d.py
```

Press `1/2/3` to switch presets (tree_3d/coral/fern_3d), or `s` to save a screenshot.

Branch depth is tracked in the turtle stack (`[/]`) and controls stroke weight and alpha, giving the appearance of depth without Z-sorting. Adjusting `angle`, `length_scale`, or `iterations` in a preset yields dramatically different botanical forms.
