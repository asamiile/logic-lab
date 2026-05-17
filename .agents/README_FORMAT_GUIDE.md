# Logic Lab Algorithm README Format Guide

Standard format for all algorithm documentation in the Logic Lab project.

## Structure

```markdown
# Algorithm Name

One-line description of what the algorithm does.

\`\`\`bash
uv run python src/logic_lab/category/algorithm_name/algorithm_name.py
\`\`\`

List of key keyboard controls (1-2 lines max).

Brief explanation of core behavior or mechanism (1-2 sentences).
```

## Example

```markdown
# Ant Colony Optimization

Stigmergic ant navigation using pheromone deposition and evaporation.

\`\`\`bash
uv run python src/logic_lab/biological/ant_colony/ant_colony.py
\`\`\`

Press `s` to save a screenshot.

Ants autonomously explore leaving pheromone trails.
```

## Guidelines

### Do's
✅ Keep it **concise** - max 5-6 lines of actual content
✅ Start with **action-oriented title** (algorithm name)
✅ Include **one-line description** immediately after title
✅ Provide **execution command** in the standard format
✅ List **key controls** in 1-2 lines
✅ Add **brief explanation** (1-2 sentences) of core behavior

### Don'ts
❌ Don't add extensive mathematical details
❌ Don't create complex subsection hierarchies
❌ Don't duplicate content from manifest entries
❌ Don't use module invocation style (`python -m`)

## Manifest Integration

Each algorithm README must have a corresponding entry in `.agents/art_manifest.json`:

- **path**: Relative path to the `.py` file (e.g., `audio_sync/audio_reactive_particles/audio_reactive_particles.py`)
- **title**: Algorithm name
- **category**: Domain folder name
- **concepts**: Key technical terms (max 6)
- **visual_use**: One sentence about recommended use
- **good_for**: List of applications (max 3)
- **complexity**: low/medium/high based on line count
- **dependencies**: Python packages required

## Manifest Regeneration

When adding new algorithms, update the manifest automatically:

```bash
uv run python .agents/update_art_manifest.py --write
```

This script scans all algorithm files and generates manifest entries with conservative defaults. Review and refine the generated entries, especially `concepts`, `visual_use`, and `good_for` fields.

## MCP Server Discovery

The MCP server uses both README and manifest for AI agent discovery:
- README: Quick reference for users and agents
- Manifest: Searchable metadata for discovery (concepts, categories)
- Source code: Available via `get_algorithm()` for detailed exploration

Keep both in sync for optimal agent experience.
