# Logic Lab MCP Server

Local stdio MCP server for read-only access to Logic Lab algorithm references.

Because this is a local stdio MCP server, the `logic-lab` repository must be
cloned on the same machine where the MCP client runs. Register the server with
the local repository path using `uv run --project /path/to/logic-lab logic-lab-mcp`.

## Tools

### `get_manifest()`

Returns the full Logic Lab art algorithm manifest as a JSON object.

The manifest contains an `entries` array. Each entry includes:

| Field | Type | Description |
|---|---|---|
| `path` | `str` | Manifest-relative path (e.g. `physics/wave/wave.py`) |
| `title` | `str` | Human-readable algorithm name |
| `category` | `str` | Domain (see categories below) |
| `concepts` | `list[str]` | Key algorithmic concepts demonstrated |
| `visual_use` | `str` | One-line description of the visual output |
| `good_for` | `list[str]` | Suggested use-cases and aesthetic tags |
| `complexity` | `str` | `low`, `medium`, or `high` |
| `dependencies` | `list[str]` | Required packages beyond py5 |

Use this tool when you need the full entry list or want to enumerate all available
categories. For filtered discovery, prefer `search_algorithms`.

---

### `search_algorithms(query, category=None, limit=5)`

Searches manifest entries by title, category, concepts, `visual_use`, and `good_for`.
Returns manifest metadata only — never reads source files.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `query` | `str` | required | Free-text search terms. Synonym expansion is applied automatically. |
| `category` | `str \| None` | `None` | Exact category filter (case-insensitive). Omit to search all categories. |
| `limit` | `int` | `5` | Max results (range: 1–50). Results are sorted by relevance score. |

**Available categories:** `physics`, `steering_behaviors`, `genetic_algorithms`,
`neuro_evolution`, `fractals`, `cellular_automata`, `mathematical`, `tiling_patterns`,
`research`, `simulation`, `shader`.

Returns an empty list when no entries match — this is not an error. Use this tool
first for discovery, then `get_algorithm_summary`, then `get_algorithm`.

---

### `get_algorithm(path, max_chars=12000)`

Returns source text for a safe repository path. Read-only.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `path` | `str` | required | Manifest-relative path to a `.py` or `README.md` file. |
| `max_chars` | `int` | `12000` | Max characters to return (range: 1–20000). |

Returns a dict with `path`, `content`, `truncated` (bool), and `notice` (truncation
message or `null`). Raises an error if the path escapes the repository root, points to
a non-existent file, or refers to a disallowed file type.

Call `get_algorithm_summary` first to confirm relevance before fetching full source.

---

### `get_algorithm_summary(path)`

Returns a short summary from the manifest entry and nearby `README.md`. Never returns
source code.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `path` | `str` | required | Manifest-relative path to a `.py` or `README.md` file. |

Returns manifest metadata fields (`title`, `category`, `concepts`, `visual_use`,
`good_for`, `complexity`, `dependencies`) plus `readme_excerpt` (first ~6 lines of the
nearest `README.md`, up to 1200 chars). For paths not in the manifest, returns a minimal
summary derived from the path. Use this to assess relevance before calling `get_algorithm`.

---

### `search_by_mood(mood, style=None, limit=8)`

Returns algorithms matching a creative mood or visual atmosphere.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `mood` | `str` | required | One of the 12 available moods (see below). Case-insensitive. |
| `style` | `str \| None` | `None` | Optional free-text style tokens to re-rank results. |
| `limit` | `int` | `8` | Max results (range: 1–50). |

**Available moods:** `ethereal`, `chaotic`, `geometric`, `organic`, `cosmic`, `minimal`,
`generative`, `retro`, `crystalline`, `topological`, `networked`, `geological`.

Returns a dict with `mood`, `style`, `profile_summary`, and `results`. Returns an error
dict with `available_moods` when the mood is unrecognized. Prefer `search_algorithms`
for free-text queries without a clear aesthetic direction.

---

### `recommend_combinations(intent, count=3)`

Suggests multi-layer algorithm combinations for a given artistic intent.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `intent` | `str` | required | Free-text description of the artistic goal. |
| `count` | `int` | `3` | Number of recipes to return (range: 1–total recipes). |

Returns a dict with `intent`, `combinations` (layered recipes with live algorithm
suggestions per role), and a `tip`. Layer roles include background, agents, texture,
overlay, etc. Follow up with `get_algorithm_summary` or `get_algorithm` on chosen paths.

## Resources

`list_mcp_resources` exposes these read-only resources:

- `resource://logic-lab/manifest` — full curated manifest JSON
- `resource://logic-lab/manifest-summary` — small category and usage summary
- `resource://logic-lab/readme` — top-level project README
- `resource://logic-lab/mcp-readme` — this MCP server README

Algorithm source files are intentionally not exposed as static resources. Use
`search_algorithms`, `get_algorithm_summary`, and `get_algorithm` so path checks
and `max_chars` limits are applied.

## Security

- **Read-only:** no file creation, editing, deletion, shell, or git tools are available.
- **Repository boundary:** paths are resolved against the Logic Lab repo root and rejected
  if they escape it.
- **File allowlist:** `get_algorithm` reads only manifest paths, repo-local `.py` files,
  or repo-local `README.md` files.
- **Size limit:** `get_algorithm` defaults to 12,000 characters and clamps requests to
  at most 20,000 characters.
- **Search safety:** `search_algorithms` returns manifest metadata only, never source code.

## Recommended Workflow

1. `search_algorithms` (or `search_by_mood` / `recommend_combinations`) for discovery
2. `get_algorithm_summary` for short context on candidates
3. `get_algorithm` only for paths you intend to use

This keeps the agent from pulling unrelated code into the working context.

## Manual Install

Requires [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/asamiile/logic-lab.git
cd logic-lab
uv sync
```

## Run

You usually do not run the server manually. MCP clients start this command for
you after registration. Manual execution is mainly for smoke testing:

```bash
uv run --project /path/to/logic-lab logic-lab-mcp
```

## Register

Use the registration examples in the root [README.md](../README.md). It includes
Codex, Claude Code, GitHub Copilot in VS Code, Cursor, and Antigravity examples.

The server command is always the same:

```bash
uv run --project /path/to/logic-lab logic-lab-mcp
```

## GitHub Copilot Cloud Agent

GitHub Copilot cloud agent uses repository settings on GitHub.com and a
different JSON shape with `mcpServers` plus an explicit `tools` allowlist. This
local stdio server only works there if the cloud agent environment can access a
checkout of `logic-lab` at the configured path. For most cloud-agent use, expose
Logic Lab through a future HTTP MCP server instead.

Example shape:

```json
{
  "mcpServers": {
    "logic-lab": {
      "type": "local",
      "command": "uv",
      "args": [
        "run",
        "--project",
        "/path/to/logic-lab",
        "logic-lab-mcp"
      ],
      "tools": [
        "get_manifest",
        "search_algorithms",
        "get_algorithm",
        "get_algorithm_summary",
        "search_by_mood",
        "recommend_combinations"
      ]
    }
  }
}
```

## Manifest Updates

When adding a new simulation, update the manifest:

```bash
uv run python .agents/update_art_manifest.py --write
```

The updater preserves existing entries and appends draft entries for missing simulation
files. Agents should refine generated `concepts`, `visual_use`, `good_for`, `complexity`,
and `dependencies` before finishing work.

## Use From Other Repositories

Register this MCP server once, then use it from any workspace where an AI coding agent
is working on creative coding, simulation, or artwork generation. The other repository
does not need to copy Logic Lab files or depend on Logic Lab directly.

Example prompt for an agent:

```text
Use the logic-lab MCP as a read-only algorithm reference.
Search for algorithms good for "flowing smoke with invisible force fields".
Fetch summaries first, then retrieve only the source for the best one or two candidates.
```
