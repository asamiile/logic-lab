# Logic Lab

Python translations of creative coding examples using py5. Each simulation is organized by domain, demonstrating core computational creativity concepts: physics, steering behaviors, genetic algorithms, neural networks, fractals, cellular automata, tiling patterns, and mathematical systems.

## MCP Server

Logic Lab is available as an MCP server for AI agents. Agents can search the Logic Lab manifest, find algorithms by visual intent or category, read short summaries, and fetch bounded source snippets for selected examples.

[![Glama MCP Server](https://glama.ai/mcp/servers/asamiile/logic-lab/badge)](https://glama.ai/mcp/servers/asamiile/logic-lab)

### Option 1: Quick Start

If you just want to use the MCP server directly via [Glama](https://glama.ai/mcp/servers/asamiile/logic-lab) or your AI agent without cloning the repository, you can run it remotely using `uvx`.

Add the following to your AI tool's MCP

configuration:

```json
{
  "mcpServers": {
    "logic-lab": {
      "command": "uvx",
      "args": [
        "--from",
        "logic-lab",
        "logic-lab-mcp"
      ]
    }
  }
}
```

### Option 2: Manual Installation (For local development)

Requires uv. Clone this repository locally if you want to modify the algorithms or run the server from your local source.

```bash
git clone https://github.com/asamiile/logic-lab.git
cd logic-lab
uv sync
```

### Registration (Local)

After manual installation, register the local server with your AI tool using the logic-lab-mcp command:

Claude Code:

```bash
claude mcp add logic-lab -- logic-lab-mcp
```

Codex:

```bash
codex mcp add logic-lab -- logic-lab-mcp
```

GitHub Copilot in VS Code (.vscode/mcp.json or user MCP settings):

```json
{
  "servers": {
    "logic-lab": {
      "type": "stdio",
      "command": "logic-lab-mcp"
    }
  }
}
```

Cursor (.cursor/mcp.json or ~/.cursor/mcp.json):

```json
{
  "mcpServers": {
    "logic-lab": {
      "type": "stdio",
      "command": "logic-lab-mcp"
    }
  }
}
```

### Available Tools

303 algorithms across 11 domains are accessible via 6 MCP tools:

| Tool | Description |
|---|---|
| `search_algorithms(query, category, limit)` | Free-text search across titles, concepts, and visual descriptions. Start here. |
| `search_by_mood(mood, style, limit)` | Find algorithms by aesthetic mood: `ethereal`, `chaotic`, `geometric`, `organic`, `cosmic`, `minimal`, and 6 more. |
| `recommend_combinations(intent, count)` | Returns layered multi-algorithm recipes for a given artistic intent. |
| `get_algorithm_summary(path)` | Returns manifest metadata and README excerpt for a path. Check relevance before fetching source. |
| `get_algorithm(path, max_chars)` | Returns source code for a specific algorithm file. Read-only, size-limited. |
| `get_manifest()` | Returns the full manifest JSON. Use when you need to enumerate all entries or categories. |

**Recommended workflow:** `search_algorithms` → `get_algorithm_summary` → `get_algorithm`

See [src/logic_lab/mcp/README.md](src/logic_lab/mcp/README.md) for full parameter reference, security notes, and resource endpoints.

### Agent Conversation Example

> **User:** I want to create flowing smoke with invisible force fields.
>
> **Agent:** Running `search_algorithms("flowing smoke invisible force fields")`...
> - `steering_behaviors/flow_field.py` — particles following a fluid vector field
> - `physics/fluid_simulation.py` — grid-based fluid dynamics
>
> Checking details with `get_algorithm_summary("steering_behaviors/flow_field.py")`...
> complexity: medium, concepts: [flow field, Perlin noise, autonomous agents]
>
> Fetching source with `get_algorithm("steering_behaviors/flow_field.py")` to use as reference for implementation.

### Algorithm Domains

- **mathematical/** - Generative geometry, color harmony, noise functions, fractals
- **physics/** - Particle systems, forces, spring physics, fluid dynamics, collision
- **steering_behaviors/** - Autonomous agents, flocking, pathfinding, flow fields
- **genetic_algorithms/** - Evolution, selection, crossover, mutation
- **neuro_evolution/** - Neural networks evolved via genetic algorithms
- **fractals/** - Recursive structures, space-filling curves, Mandelbrot sets
- **cellular_automata/** - Rule-based systems, Game of Life, emergence
- **tiling_patterns/** - Symmetry, tessellations, ornamental patterns
- **research/** - Experimental systems combining multiple domains
- **simulation/** - Prototype implementations and archived experiments
- **shader/** - GLSL fragment shaders for TouchDesigner and UE5


### Example: Autonomous Artwork Generation

[py5-media-art](https://github.com/asamiile/py5-media-art) — a project that uses the Logic Lab MCP server with Claude Code to autonomously generate py5 sketches. Claude searches Logic Lab for relevant algorithms, adapts them into new compositions, and optionally writes accompanying articles.


## Gallery

Examples of generative art created with Logic Lab algorithms:

[![Watch on YouTube](https://img.shields.io/badge/YouTube-Watch%20Demos-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/playlist?list=PL5Uiqt5oXo0HR6D_6HbPiDWkYEQUHo1UD)

<div align="center">
  <a href="https://stock.adobe.com/jp/stock-photo/id/2062431194" target_blank=""><img src="https://as2.ftcdn.net/v2/jpg/20/62/43/11/1000_F_2062431194_dvPNXz37lpu9s7KMLecEiW2kjC13bwSu.jpg" width="49%" /></a>
  <a href="https://stock.adobe.com/jp/stock-photo/id/2062143692" target_blank=""><img src="https://as1.ftcdn.net/v2/jpg/20/62/14/36/1000_F_2062143692_yKRP6MaFdPe97hSihM7RQwUMDy4Vz6sX.jpg" width="49%" /></a>
</div>
<div align="center">
  <a href="https://stock.adobe.com/jp/stock-photo/id/2047805683" target_blank=""><img src="https://as1.ftcdn.net/v2/jpg/20/47/80/56/1000_F_2047805683_wyMES8dS3vOQhGcwyrDoy4XGrASya9QW.jpg" width="49%" /></a>
  <a href="https://stock.adobe.com/jp/stock-photo/id/2032573507" target_blank=""><img src="https://as2.ftcdn.net/v2/jpg/20/32/57/35/1000_F_2032573507_st1OGDqWZe7S3creI7NUfFtKtWyri5HM.jpg" width="49%" /></a>
</div>
<div align="center">
  <a href="https://stock.adobe.com/jp/stock-photo/id/2032571820" target_blank=""><img src="https://as1.ftcdn.net/v2/jpg/20/32/57/18/1000_F_2032571820_4BuIFIcInA01dV1omOtcLtKieWRxcbdR.jpg" width="49%" /></a>
  <a href="https://stock.adobe.com/jp/stock-photo/id/2007580121" target_blank=""><img src="https://as2.ftcdn.net/v2/jpg/20/07/58/01/1000_F_2007580121_ccthPfcDLpYcgFqNCjHZdXt73XkAM4Q1.jpg" width="49%" /></a>
</div>
<div align="center">
  <a href="https://stock.adobe.com/jp/stock-photo/id/2062125691" target_blank=""><img src="https://as1.ftcdn.net/v2/jpg/20/62/12/56/1000_F_2062125691_lR5yaxaW0n3z8qT5W5yJwCYhRQlNk3cG.jpg" width="49%" /></a>
  <a href="https://stock.adobe.com/jp/stock-photo/id/2019999379" target_blank=""><img src="https://as2.ftcdn.net/v2/jpg/20/19/99/93/1000_F_2019999379_gv2YF2KTn0PnPsrDe1Pr9QNrbL5BynBJ.jpg" width="49%" /></a>
</div>
<div align="center">
  <a href="https://stock.adobe.com/jp/stock-photo/id/2032572727" target_blank=""><img src="https://as2.ftcdn.net/v2/jpg/20/32/57/27/1000_F_2032572727_D1KiwH9sq3Y7SN4w75WKbCQ9t5X371az.jpg" width="49%" /></a>
  <a href="https://stock.adobe.com/jp/stock-photo/id/2062106598" target_blank=""><img src="https://as2.ftcdn.net/v2/jpg/20/62/10/65/1000_F_2062106598_OsonjoxQg5h04RIVjNj8h53nM87GpXYk.jpg" width="49%" /></a>
</div>


## Development

To contribute new algorithms or fixes, see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on:
- Development setup with `uv`
- Algorithm addition workflow
- py5 code patterns and templates
- Testing requirements
- Conventional Commits specification
- Automated release process

### Setup

Install dependencies:

```bash
uv sync
```

### Running Tests

```bash
# Install dev dependencies
uv sync --group dev

# Run all tests
uv run pytest tests/

# Run with coverage
uv run pytest tests/ --cov=src/logic_lab
```

### Code Quality

```bash
# Lint with ruff
uv run ruff check src/ tests/

# Format with black
uv run black src/ tests/

# Lint and fix
uv run ruff check --fix src/ tests/
```

### Repository Structure

```
logic-lab/
├── src/logic_lab/                 # Package root
│   ├── __init__.py
│   ├── mcp/                       # MCP server for AI agent access
│   ├── physics/                   # Motion, forces, particles, simulations
│   ├── steering_behaviors/        # Autonomous agents, flow fields, flocking
│   ├── genetic_algorithms/        # Selection, mutation, evolutionary search
│   ├── neuro_evolution/           # Neural networks evolved via genetics
│   ├── fractals/                  # Recursion, trees, Koch curves, L-systems
│   ├── cellular_automata/         # Rule-based grids, lattice systems
│   ├── mathematical/              # Noise, curves, geometry, harmony
│   ├── tiling_patterns/           # Symmetry, tessellation, ornaments
│   ├── research/                  # Experimental and hybrid systems
│   ├── simulation/                # Prototypes and reference implementations
│   ├── shared/                    # Reusable utilities and helpers
│   └── shader/                    # GLSL shader experiments
├── tests/                         # Pytest test suite
├── CONTRIBUTING.md                # Contributor guidelines and conventions
├── CHANGELOG.md                   # Version history and release notes
├── pyproject.toml                 # Package configuration and dependencies
└── .github/workflows/
    ├── test.yml                   # CI: lint and test automation
    └── release.yml                # CD: automated releases with release-please
```


## Reference

- [The Nature of Code](https://natureofcode.com/)
- [Pythonではじめるオープンエンドな進化的アルゴリズム](https://www.oreilly.co.jp/books/9784814400003/)
- [数学から創るジェネラティブアート](https://gihyo.jp/book/2019/978-4-297-10463-4/support)
- [リアルタイムグラフィックスの数学](https://gihyo.jp/book/2022/978-4-297-13034-3)

## License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Author

[Asami.K](https://asami.tokyo/)

If you find this helpful, consider supporting the work:

[![BuyMeACoffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/asamiile)
