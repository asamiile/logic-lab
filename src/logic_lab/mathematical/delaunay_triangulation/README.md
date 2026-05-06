# Delaunay Triangulation

Builds a triangle mesh from scattered points using the Bowyer-Watson algorithm.

## Run

```bash
uv run python mathematical/delaunay_triangulation/delaunay_triangulation.py
```

## Controls

| Key / Action | Effect |
|---|---|
| Click | Add a point |
| `r` | Regenerate random points |
| `+` / `-` | Change random point count |
| `f` | Toggle triangle fill |
| `c` | Toggle circumcircles |
| `s` | Save screenshot |

## Algorithm

Delaunay triangulation connects points so that no point lies inside the circumcircle of any triangle:

1. **Super triangle**: Start with one large triangle containing all points.
2. **Insert points**: Add each point one at a time.
3. **Remove invalid triangles**: Find triangles whose circumcircles contain the new point.
4. **Rebuild the cavity**: Connect the new point to the boundary edges of the removed region.
5. **Trim scaffolding**: Remove triangles that touch the original super triangle.

The result tends to avoid skinny triangles, making it useful for mesh generation, terrain networks, low-poly rendering, and proximity structures. Delaunay triangulation is also the geometric dual of the Voronoi diagram.

## Other Environments

**TouchDesigner**: Use Script SOP or Python DAT to compute triangle indices, then feed points and primitives into a Geometry COMP. Circumcircle overlays can be drawn as debug curves.

**UE5**: Generate triangle indices in C++ or Blueprint and submit them to a Procedural Mesh Component. Use the mesh as a basis for low-poly terrain, point-cloud surfaces, or proximity-driven effects.
