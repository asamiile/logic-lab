# Logic Lab

Python translations of creative coding examples using py5. Each simulation is organized by domain, demonstrating core computational creativity concepts: physics, steering behaviors, genetic algorithms, neural networks, fractals, cellular automata, tiling patterns, and mathematical systems.

## Setup

Install dependencies:

```bash
uv sync
```

## MCP Server

Logic Lab includes a local read-only MCP server for AI agents. Clone this
repository locally, install dependencies with `uv sync`, then register the server
for use across your workspace.

With the MCP server, agents can search the Logic Lab manifest, find algorithms
by visual intent or category, read short summaries, and fetch bounded source
snippets for selected examples.

### Installation

```bash
git clone https://github.com/asamiii/logic-lab.git
cd logic-lab
uv sync
```

### Registration

After installation, register the server with your AI tool using the `logic-lab-mcp` command:

**Claude Code:**
```bash
claude mcp add logic-lab -- logic-lab-mcp
```

**Codex:**
```bash
codex mcp add logic-lab -- logic-lab-mcp
```

**GitHub Copilot in VS Code** (`.vscode/mcp.json` or user MCP settings):
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

**Cursor** (`.cursor/mcp.json` or `~/.cursor/mcp.json`):
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

See [src/logic_lab/mcp/README.md](src/logic_lab/mcp/README.md) for tools, security notes, and usage details.

## Repository Structure

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

## Development

To contribute new algorithms or fixes, see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on:
- Development setup with `uv`
- Algorithm addition workflow
- py5 code patterns and templates
- Testing requirements
- Conventional Commits specification
- Automated release process

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
