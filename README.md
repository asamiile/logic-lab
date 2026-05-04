# Logic Lab

Python translations of creative coding examples using py5. Each simulation is organized by domain, demonstrating core computational creativity concepts: physics, steering behaviors, genetic algorithms, neural networks, fractals, cellular automata, tiling patterns, and mathematical systems.

## Setup

Install dependencies:

```bash
uv sync
```

## MCP Server

Logic Lab includes a local read-only MCP server for AI agents. Clone this
repository locally, run `uv sync`, register the server with the local path, then
use it from any other workspace as an algorithm reference.

With the MCP server, agents can search the Logic Lab manifest, find algorithms
by visual intent or category, read short summaries, and fetch bounded source
snippets for selected examples.

Register with Codex:

```bash
codex mcp add logic-lab -- uv run --project /path/to/logic-lab python mcp/logic_lab_server.py
```

Register with Claude Code:

```bash
claude mcp add logic-lab -- uv run --project /path/to/logic-lab python mcp/logic_lab_server.py
```

Register with GitHub Copilot in VS Code (`.vscode/mcp.json` or user MCP settings):

```json
{
  "servers": {
    "logic-lab": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "run",
        "--project",
        "/path/to/logic-lab",
        "python",
        "mcp/logic_lab_server.py"
      ]
    }
  }
}
```

Register with Cursor (`.cursor/mcp.json` or `~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "logic-lab": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "run",
        "--project",
        "/path/to/logic-lab",
        "python",
        "mcp/logic_lab_server.py"
      ]
    }
  }
}
```

Register with Antigravity:

Add this server entry to your Antigravity MCP settings file:

```json
{
  "servers": {
    "logic-lab": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "run",
        "--project",
        "/path/to/logic-lab",
        "python",
        "mcp/logic_lab_server.py"
      ]
    }
  }
}
```

See [mcp/README.md](mcp/README.md) for tools, security notes, and usage details.

## Repository Map

- **physics/** - motion, forces, waves, oscillation, particles, and physical systems
- **steering_behaviors/** - autonomous agents, seek/arrive, path following, flow fields, and flocking
- **genetic_algorithms/** - selection, mutation, fitness, DNA, and evolutionary search
- **neuro_evolution/** - neural networks evolved by genetic algorithms
- **fractals/** - recursion, trees, Koch curves, L-systems, and spatial subdivision
- **cellular_automata/** - rule-based grids, lattice systems, and emergent patterns
- **mathematical/** - spirals, Bezier curves, modular arithmetic, Fibonacci systems, and generative geometry
- **tiling_patterns/** - symmetry, tiling, textile patterns, deformations, and ornaments
- **research/** - experimental or hybrid systems that do not fit a single domain
- **simulation/** - older experiments and custom prototypes kept for reference
- **shared/** - reusable support libraries
- **shader/** - GLSL shader experiments
- **mcp/** - read-only MCP server for AI agent access to algorithm references

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
