# Point Cloud Morphing

Animates smooth transitions between 3D point cloud shapes — sphere, torus, cube, and helix — by linearly interpolating sampled positions with an ease-in-out curve. Points are perspective-projected with depth-based coloring.

```bash
uv run python src/logic_lab/three_dimensional/point_cloud_morph/point_cloud_morph.py
```

Press `s` to save a screenshot.

Shape sequences cycle automatically every `MORPH_DURATION` frames. Depth sorting (painter's algorithm) ensures far points are drawn first so near points appear on top. Modifying `NUM_POINTS`, `MORPH_DURATION`, or `ROTATE_SPEED` changes the density, pace, and spin of the sculpture.
