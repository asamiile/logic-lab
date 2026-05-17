# 3D Metaballs with Perspective Projection

Creates organic, morphing 3D shapes by blending multiple spherical potential fields in 3D space. Uses perspective projection with Y-axis rotation to display the 3D scene on a 2D screen.

## Overview

Metaballs are implicit surfaces where each point in space contributes a potential value based on its distance from the metaball center. When the combined potential exceeds a threshold, the point is rendered as part of the surface.

### Key Features

- **3D Metaballs**: Full 3D coordinate system with implicit potential fields
- **Perspective Projection**: Converts 3D coordinates to 2D screen space with proper depth handling
- **Y-axis Rotation**: Auto-rotating 3D view with mouse-controlled rotation speed
- **Depth-based Coloring**: Distant surfaces appear darker, near surfaces brighter
- **Physics Simulation**: Metaballs move and bounce within 3D bounds
- **Interactive Controls**: Mouse and keyboard control over rendering and physics

## Class Design

### Metaball3D

Represents a single 3D metaball with potential influence.

```python
class Metaball3D:
    x, y, z: float              # 3D coordinates
    radius, strength: float     # Influence parameters
    vx, vy, vz: float          # 3D velocity

    def influence_at(x, y, z) -> float  # Potential at position
    def update() -> None                 # Physics update
    def display(projection_func) -> None # Render with projection
```

### MetaballField3D

Manages the combined 3D potential field and rendering.

```python
class MetaballField3D:
    width, height: int              # Screen dimensions
    focal_distance: float           # Perspective projection parameter
    metaballs: list[Metaball3D]    # All metaballs in field
    threshold, resolution: float    # Rendering parameters
    rotation_y: float              # Y-axis rotation angle
    rotation_speed: float          # Rotation speed control

    def perspective_projection(x, y, z) -> (x, y, depth)  # 3D->2D projection
    def render() -> None                                   # Render field
    def update_balls() -> None                            # Physics update
```

## Mathematical Details

### Potential Calculation

For each point P and metaball with center C and radius R, strength S:

```
distance² = (P.x - C.x)² + (P.y - C.y)² + (P.z - C.z)²
influence = S * R² / (distance² + 1)
```

### Perspective Projection

The 3D scene is rotated around the Y-axis, then projected to 2D screen coordinates using perspective projection:

**Y-axis Rotation** (angle θ = rotation_y):
```
rotated_x = x * cos(θ) - z * sin(θ)
rotated_z = x * sin(θ) + z * cos(θ)
```

**Perspective Projection** (focal distance f):
```
screen_x = width/2 + rotated_x * f / (rotated_z + f)
screen_y = height/2 + y * f / (rotated_z + f)
depth = (rotated_z + focal_distance) / (2 * focal_distance)  // 0-1 range
```

Points with `rotated_z + f <= 0` are behind the camera and are culled.

## Running the Simulation

Interactive 3D visualization with real-time perspective control:

```bash
python -m logic_lab.three_dimensional.metaballs_3d.metaballs_3d
```

## Controls

| Key | Action |
|-----|--------|
| ↑ | Increase rotation speed |
| ↓ | Decrease rotation speed |
| 0-9 | Set resolution (higher = faster/less detail) |
| d | Toggle debug mode (show metaball centers) |
| s | Save screenshot |
| r | Reset field |
| Mouse Y | Control rotation speed |
| Click | Add metaball at click position |

## Usage

```python
from logic_lab.three_dimensional.metaballs_3d import MetaballField3D, Metaball3D

# Create field
field = MetaballField3D(width=1024, height=768)

# Add metaballs
field.add_metaball(x=-200, y=0, z=0, radius=100, strength=1.0)
field.add_metaball(x=200, y=0, z=0, radius=100, strength=1.0)

# Update and render
field.update_balls()
field.render()
```

## Performance Considerations

- **Resolution**: Higher values skip more pixels, faster but less detailed
- **Sample Range**: The 3D sampling volume affects render quality
- **Focal Distance**: Affects projection distortion and clipping
- **Threshold**: Higher thresholds show only the densest regions

## Implementation Notes

- The field uses depth sorting to ensure correct rendering order (back to front)
- Metaballs bounce off 3D boundaries (±400 units)
- Rotation speed can be controlled via mouse Y position or keyboard
- Points behind the camera (negative projected distance) are culled
