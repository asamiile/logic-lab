# Logic Lab MCP Server

Local stdio MCP server for read-only access to Logic Lab algorithm references.

Because this is a local stdio MCP server, the `logic-lab` repository must be
cloned on the same machine where the MCP client runs. Register the server with
the local repository path using `uv run --project /path/to/logic-lab ...`.

## Tools

- `get_manifest()` returns `.agents/art_manifest.json`.
- `search_algorithms(query, category=None, limit=5)` searches manifest `title`, `category`, `concepts`, `visual_use`, and `good_for`. It returns manifest entries only, not source code.
- `get_algorithm(path, max_chars=12000)` returns source text for a safe repository path.
- `get_algorithm_summary(path)` returns a short summary from the manifest entry and nearby `README.md`.

## Run

You usually do not run the server manually. MCP clients start this command for
you after registration. Manual execution is mainly for smoke testing:

```bash
uv run python mcp/logic_lab_server.py
```

## Register

Use the registration examples in the root [README.md](../README.md). It includes
Codex, Claude Code, GitHub Copilot in VS Code, Cursor, and Antigravity examples.

The server command is always the same:

```bash
uv run --project /path/to/logic-lab python mcp/logic_lab_server.py
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
        "python",
        "mcp/logic_lab_server.py"
      ],
      "tools": [
        "get_manifest",
        "search_algorithms",
        "get_algorithm",
        "get_algorithm_summary"
      ]
    }
  }
}
```

## Security

- Read-only: the server implements no file creation, editing, deletion, shell, or git tools.
- Repository boundary: paths are resolved against the Logic Lab repo root and rejected if they escape it.
- File allowlist: `get_algorithm` reads only manifest paths, repo-local `.py` files, or repo-local `README.md` files.
- Size limit: `get_algorithm` defaults to `12000` characters and clamps requests to at most `20000` characters.
- Search safety: `search_algorithms` returns manifest metadata only.

## Manifest Updates

When adding a new simulation, update the manifest:

```bash
uv run python .agents/update_art_manifest.py --write
```

The updater preserves existing entries and appends draft entries for missing simulation files. Agents should refine generated `concepts`, `visual_use`, `good_for`, `complexity`, and `dependencies` before finishing work.

`.agents/art_manifest_baseline.json` records existing files that were intentionally omitted from the initial curated manifest. This lets the updater detect future additions without bulk-adding every historical sketch.

## Use From Other Repositories

This MCP server is meant to be registered once, then used from any workspace
where an AI coding agent is working on creative coding, simulation, or artwork
generation. The other repository does not need to copy Logic Lab files or depend
on Logic Lab directly; the agent queries this MCP server for references and only
fetches the small amount of source it needs.

Typical operation:

1. Register this MCP server with Codex, Claude Code, Antigravity, or another MCP client.
2. Open a different project workspace where you are building an artwork or simulation.
3. Ask the agent to use the `logic-lab` MCP as an algorithm reference.
4. The agent calls `search_algorithms` with the desired visual or behavioral intent, for example `flow field particles`, `recursive textile`, `evolving creatures`, or `orbital motion`.
5. The agent inspects returned manifest entries and chooses only relevant candidates.
6. The agent calls `get_algorithm_summary` for short context.
7. The agent calls `get_algorithm` only for selected source paths that are useful for the current implementation.

The expected pattern is search first, summary second, source last. This keeps the
agent from pulling unrelated code into the working context.

Example prompt for an agent:

```text
Use the logic-lab MCP as a read-only algorithm reference.
Search for algorithms good for "flowing smoke with invisible force fields".
Fetch summaries first, then retrieve only the source for the best one or two candidates.
```
