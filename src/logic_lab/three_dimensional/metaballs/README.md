# Metaballs

Blending implicit surfaces using smooth potential fields. Multiple metaballs create organic, morphing shapes as their influence zones overlap.

## Run

```bash
uv run python src/logic_lab/three_dimensional/metaballs/metaballs.py
```

## Controls

| Key | Effect |
|---|---|
| `s` | Save screenshot |
| `d` | Toggle debug mode (show influence circles) |
| `↑` / `↓` | Increase/decrease threshold (surface visibility) |
| `0-9` | Adjust resolution (1=detailed/slow, 9=fast/blocky) |
| `r` | Reset to initial configuration |
| `click` | Add new metaball at cursor position |

## Algorithm

Each metaball is a point in space with a **potential field** that falls off with distance:

```
influence(x, y) = strength × radius² / (distance² + ε)
```

The **total potential** at any point is the sum of all metaball influences. When this potential exceeds a threshold, the point is rendered as part of the surface.

**Key Properties:**
- **Smooth merging**: Overlapping metaballs blend seamlessly
- **Dynamic**: Metaballs bounce around, creating morphing animations
- **Threshold-based**: Controls how "sticky" the surface appears
- **Resolution parameter**: Trade-off between quality and performance

## Visual Parameters

- **Threshold** (default: 1.0)
  - Higher threshold → thinner, more separated shapes
  - Lower threshold → thicker, more merged shapes

- **Resolution** (default: 2)
  - Lower number = more detail, slower rendering
  - Higher number = faster, blockier appearance

- **Metaball Properties**
  - `radius`: Field extent (controls size and influence area)
  - `strength`: Field intensity (controls how much it affects neighbors)

## Algorithm Details

### Metaball Influence Function

The influence falloff is inverse-square, creating smooth C-infinity continuity at the surface:

```python
influence = strength * (radius²) / (distance² + 1)
```

The small epsilon (1.0) prevents division by zero and creates a smooth peak.

### Rendering Method

1. Sample grid across the screen at `resolution` intervals
2. For each sample point, calculate total potential from all metaballs
3. If potential > threshold, interpolate color between:
   - Inside color: Blue-white (influenced)
   - Outside color: Dark gray (background)
4. Fill pixel blocks for efficiency

### Physics Simulation

Metaballs have simple physics:
- Constant velocity (bouncing off walls)
- Wall collisions with direction reversal
- Optional random initial velocities

## Performance Notes

- **Resolution parameter critical**: Higher resolution value = fewer calculations
- **Pixel-level sampling**: Current implementation is CPU-based
- **GPU alternative**: Could be implemented as fragment shader for real-time performance
- **Typical FPS**: 30-60 at resolution=2-3 on modern hardware

## Mathematical Background

Metaballs are based on **implicit surface equations**. The "blob" appears at the isosurface where:

```
f(x, y) = threshold
```

Where `f` is the sum of potential functions. This creates smooth, organic shapes with:
- C0 continuity (continuous)
- C1 continuity at blend regions (differentiable)
- Smooth normal vectors

## Variations & Extensions

### 3D Metaballs
Current implementation is 2D. 3D extension:
- Calculate `influence(x, y, z)` with 3D distance
- Render as voxel grid or use marching cubes algorithm
- Or: Render 3D rotations as 2D projections

### Metaball Types
- **Blend type**: Normal smooth blend (implemented)
- **Hard blend**: Sharp transitions at threshold
- **Warp fields**: Metaballs repel each other
- **Inverse fields**: "Antiblobs" that carve surfaces

### Interactive Features
- Cursor-following metaballs
- Rhythm-based pulsing (audio sync)
- Multiple threshold layers (cross-fading surfaces)
- Particle generation from surface outline

## Other Environments

**TouchDesigner**:
- GPU-based TOP operators (Composite, Warp)
- GLSL CHOP evaluation for potential calculation
- Multiple feedback loops for organic motion

**UE5**:
- Material functions for metaball blending
- GPU compute shaders for 3D voxel grids
- Volumetric rendering with post-processing

**p5.js**:
- JavaScript translation available
- WebGL version for GPU acceleration
- Real-time interaction in browser

## References

- [Implicit Surface Blending](https://en.wikipedia.org/wiki/Metaball)
- Blinn, J. F. (1982). "A generalization of algebraic surface drawing"
- Wyvill, G., & Wyvill, B. (1986). "Fast evaluation of implicit surfaces"
- Generative Art techniques in creative coding
