# Agent Instructions for Logic Lab

## Commit Policy

Do not commit changes to git. The user handles all commits manually.

Agents may edit files, create directories, and run checks, but must not run `git add`, `git commit`, or other git write operations.

## Implementation Preferences

- Implement straightforward tasks directly.
- Keep changes scoped to the requested domain or tool.
- Run syntax checks for changed Python files.
- Run focused tests or smoke checks when practical.
- Leave the working tree ready for user review.

## Project Structure

Logic Lab contains Python and py5 translations and experiments for creative coding algorithms.

Use domain-based organization:

- `physics/` for motion, forces, particles, waves, oscillation, and physical systems.
- `steering_behaviors/` for autonomous agents, path following, flow fields, sensors, and swarms.
- `genetic_algorithms/` for DNA, mutation, selection, and evolutionary search.
- `neuro_evolution/` for neural networks evolved by genetic algorithms.
- `fractals/` for recursion, L-systems, trees, Koch curves, and spatial subdivision.
- `cellular_automata/` for CA grids, lattice rules, Pascal patterns, and emergence.
- `mathematical/` for mathematical geometry and numerical generative systems.
- `tiling_patterns/` for symmetry, tiling, textile, and deformation systems.
- `research/` for experimental or hybrid systems that do not fit cleanly elsewhere.
- `shared/` for reusable libraries used by multiple sketches.

Each simulation should usually follow:

```text
domain/simulation_name/
├── simulation_name.py
├── README.md
└── screenshots/
```

## MCP And Manifest

Logic Lab exposes selected algorithm knowledge through a local read-only MCP server in `mcp/logic_lab_server.py`.

The search index lives at `.agents/art_manifest.json`. When adding a new algorithm or simulation, agents should:

1. Add or update the simulation code and `README.md`.
2. Run:

   ```bash
   uv run python .agents/update_art_manifest.py --write
   ```

3. Review the new manifest entry.
4. Refine these fields when the generated draft is too generic:
   - `title`
   - `category`
   - `concepts`
   - `visual_use`
   - `good_for`
   - `complexity`
   - `dependencies`

Manifest entries should help another agent choose algorithms for artwork creation without reading full source files first.

`.agents/art_manifest_baseline.json` records existing files that were intentionally left out of the initial curated manifest. Do not remove paths from the baseline unless you also add a polished entry to `.agents/art_manifest.json`.

Recommended entry content:

- `path`: repo-relative path to the primary `.py` file.
- `title`: short human-readable name.
- `category`: top-level domain folder.
- `concepts`: searchable algorithm ideas such as `flow field`, `boids`, `recursion`, `gravity`.
- `visual_use`: one sentence describing when to use the algorithm visually.
- `good_for`: short tags for artistic intent or composition.
- `complexity`: `low`, `medium`, or `high`.
- `dependencies`: direct runtime libraries such as `py5`, `numpy`, `pymunk`, `networkx`, `matplotlib`, or `neat`.

The MCP server is read-only. Do not add MCP tools that write files, execute shell commands, or run git operations.
