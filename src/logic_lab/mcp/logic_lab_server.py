from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

SERVER_NAME = "logic-lab"
DEFAULT_MAX_CHARS = 12_000
ABSOLUTE_MAX_CHARS = 20_000

SYNONYMS: dict[str, list[str]] = {
    "chaos": ["butterfly effect", "lorenz", "strange attractor", "chaotic", "sensitivity"],
    "artificial life": ["alife", "amoeba", "creature", "lenia", "organism"],
    "falling sand": ["powder", "granular", "sand game", "gravity", "particle"],
    "flow field": ["vector field", "curl noise", "streamlines", "flow", "motion"],
    "reaction diffusion": ["turing pattern", "gray scott", "activator inhibitor"],
    "cellular automata": ["CA", "rules", "automaton", "grid", "evolution"],
    "fractal": ["self-similar", "recursive", "mandelbrot", "julia", "scaling"],
    "strange attractor": ["chaos", "attractor", "dynamic system", "trajectory"],
    "circle packing": ["apollonius", "tangent", "gasket", "packing"],
    "space filling": ["hilbert", "peano", "curve", "locality"],
    "emergence": ["emergent", "pattern", "self-organization", "complex"],
    "spiral": ["spiral wave", "vortex", "rotation", "cyclic"],
    "game of life": ["conway", "glider", "blinker", "still life"],
    "organic": ["growth", "biological", "natural", "living"],
    "wave": ["oscillation", "propagation", "frequency", "vibration"],
}

REPO_ROOT = Path(__file__).resolve().parents[3]
SOURCE_ROOT = REPO_ROOT / "src" / "logic_lab"
SOURCE_PREFIX = SOURCE_ROOT.relative_to(REPO_ROOT).as_posix()
MANIFEST_PATH = REPO_ROOT / ".agents" / "art_manifest.json"
README_PATH = REPO_ROOT / "README.md"
MCP_README_PATH = Path(__file__).parent / "README.md"

mcp = FastMCP(SERVER_NAME)


class AccessError(ValueError):
    pass


@lru_cache(maxsize=1)
def _load_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _entries() -> list[dict[str, Any]]:
    manifest = _load_manifest()
    entries = manifest.get("entries", [])
    if not isinstance(entries, list):
        raise ValueError("Manifest must contain an entries array")
    return entries


@lru_cache(maxsize=1)
def _manifest_paths() -> set[str]:
    return {entry["path"] for entry in _entries() if isinstance(entry.get("path"), str)}


def _safe_repo_path(path: str) -> tuple[Path, str]:
    if not path or Path(path).is_absolute():
        raise AccessError("Path must be a relative repository path")

    resolved = (REPO_ROOT / path).resolve()
    try:
        rel_path = resolved.relative_to(REPO_ROOT).as_posix()
    except ValueError as exc:
        raise AccessError("Path outside the repository is not allowed") from exc

    return resolved, rel_path


def _manifest_rel_path(repo_rel_path: str) -> str:
    prefix = f"{SOURCE_PREFIX}/"
    if repo_rel_path.startswith(prefix):
        return repo_rel_path.removeprefix(prefix)
    return repo_rel_path


def _resolve_readable_path(repo_rel_path: str) -> Path:
    direct_path = (REPO_ROOT / repo_rel_path).resolve()
    if direct_path.is_file():
        return direct_path

    manifest_rel_path = _manifest_rel_path(repo_rel_path)
    source_path = (SOURCE_ROOT / manifest_rel_path).resolve()
    try:
        source_path.relative_to(SOURCE_ROOT)
    except ValueError:
        return direct_path
    if source_path.is_file():
        return source_path
    return direct_path


def _allowed_algorithm_path(path: str) -> tuple[Path, str]:
    _, repo_rel_path = _safe_repo_path(path)
    rel_path = _manifest_rel_path(repo_rel_path)
    resolved = _resolve_readable_path(repo_rel_path)
    manifest_paths = _manifest_paths()

    is_manifest_path = rel_path in manifest_paths
    requested_path = Path(repo_rel_path)
    is_python = requested_path.suffix == ".py"
    is_readme = requested_path.name == "README.md"

    if not is_manifest_path and not (is_python or is_readme):
        raise AccessError("Only manifest entries, .py files, and README.md files can be read")
    if not resolved.is_file():
        raise AccessError("Path does not point to a readable file")
    return resolved, rel_path


def _clamp_max_chars(max_chars: int | None) -> int:
    if max_chars is None:
        return DEFAULT_MAX_CHARS
    return max(1, min(int(max_chars), ABSOLUTE_MAX_CHARS))


def _expand_query_with_synonyms(query: str) -> set[str]:
    tokens = set(query.lower().split())
    expanded = tokens.copy()
    for token in tokens:
        if token in SYNONYMS:
            expanded.update(SYNONYMS[token])
    return expanded


def _search_text(entry: dict[str, Any]) -> str:
    values: list[str] = []
    for key in ("title", "category", "visual_use"):
        value = entry.get(key)
        if isinstance(value, str):
            values.append(value)
    for key in ("concepts", "good_for"):
        value = entry.get(key)
        if isinstance(value, list):
            values.extend(str(item) for item in value)
    return " ".join(values).lower()


def _score_entry(entry: dict[str, Any], query: str) -> int:
    query = query.lower().strip()
    if not query:
        return 1

    haystack = _search_text(entry)
    concepts = {str(item).lower() for item in entry.get("concepts", [])}
    expanded_tokens = _expand_query_with_synonyms(query)

    score = 0

    # Exact phrase match (original query)
    if query in haystack:
        score += 8

    # Token-based scoring with synonym expansion
    for token in expanded_tokens:
        if token in haystack:
            score += 2
        if token == str(entry.get("category", "")).lower():
            score += 3
        if token in concepts:
            score += 4

    return score


@lru_cache(maxsize=1)
def _path_to_entry() -> dict[str, dict[str, Any]]:
    return {entry["path"]: entry for entry in _entries() if isinstance(entry.get("path"), str)}


def _entry_for_path(path: str) -> dict[str, Any] | None:
    _, rel_path = _safe_repo_path(path)
    rel_path = _manifest_rel_path(rel_path)
    return _path_to_entry().get(rel_path)


def _manifest_summary() -> dict[str, Any]:
    entries = _entries()
    categories: dict[str, int] = {}
    for entry in entries:
        category = str(entry.get("category", "uncategorized"))
        categories[category] = categories.get(category, 0) + 1

    return {
        "name": SERVER_NAME,
        "description": "Read-only Logic Lab algorithm references for AI agents.",
        "entry_count": len(entries),
        "categories": dict(sorted(categories.items())),
        "recommended_flow": [
            "Use search_algorithms for discovery.",
            "Use get_algorithm_summary for short context.",
            "Use get_algorithm only for selected source paths.",
        ],
        "resources": [
            "resource://logic-lab/manifest",
            "resource://logic-lab/manifest-summary",
            "resource://logic-lab/readme",
            "resource://logic-lab/mcp-readme",
        ],
    }


@mcp.resource(
    "resource://logic-lab/manifest",
    name="logic_lab_manifest",
    title="Logic Lab Art Manifest",
    description="Curated manifest of Logic Lab algorithms for search and artwork planning.",
    mime_type="application/json",
)
def manifest_resource() -> dict[str, Any]:
    """Return the curated Logic Lab algorithm manifest."""
    return _load_manifest()


@mcp.resource(
    "resource://logic-lab/manifest-summary",
    name="logic_lab_manifest_summary",
    title="Logic Lab Manifest Summary",
    description="Small summary of manifest size, categories, and recommended MCP usage.",
    mime_type="application/json",
)
def manifest_summary_resource() -> dict[str, Any]:
    """Return a small summary of the Logic Lab manifest."""
    return _manifest_summary()


@mcp.resource(
    "resource://logic-lab/readme",
    name="logic_lab_readme",
    title="Logic Lab README",
    description="Top-level README for Logic Lab.",
    mime_type="text/markdown",
)
def readme_resource() -> str:
    """Return the top-level Logic Lab README."""
    return README_PATH.read_text(encoding="utf-8", errors="replace")


@mcp.resource(
    "resource://logic-lab/mcp-readme",
    name="logic_lab_mcp_readme",
    title="Logic Lab MCP README",
    description="MCP server usage, tools, security notes, and manifest update workflow.",
    mime_type="text/markdown",
)
def mcp_readme_resource() -> str:
    """Return the Logic Lab MCP README."""
    return MCP_README_PATH.read_text(encoding="utf-8", errors="replace")


@mcp.tool()
def get_manifest() -> dict[str, Any]:
    """Return the Logic Lab art algorithm manifest."""
    return _load_manifest()


@mcp.tool()
def search_algorithms(
    query: str, category: str | None = None, limit: int = 5
) -> list[dict[str, Any]]:
    """Search manifest entries by title, category, concepts, visual_use, and good_for."""
    normalized_category = category.lower().strip() if category else None
    max_results = max(1, min(int(limit), 50))

    results: list[tuple[int, dict[str, Any]]] = []
    for entry in _entries():
        entry_category = str(entry.get("category", "")).lower()
        if normalized_category and entry_category != normalized_category:
            continue
        score = _score_entry(entry, query)
        if score > 0:
            results.append((score, entry))

    results.sort(key=lambda item: (-item[0], item[1].get("path", "")))
    return [entry for _, entry in results[:max_results]]


@mcp.tool()
def get_algorithm(path: str, max_chars: int = DEFAULT_MAX_CHARS) -> dict[str, Any]:
    """Return read-only source text for a safe repository .py or README.md path."""
    resolved, rel_path = _allowed_algorithm_path(path)
    limit = _clamp_max_chars(max_chars)
    text = resolved.read_text(encoding="utf-8", errors="replace")

    truncated = len(text) > limit
    if truncated:
        text = text[:limit]

    return {
        "path": rel_path,
        "content": text,
        "truncated": truncated,
        "notice": (
            f"Content truncated to {limit} characters. Increase max_chars up to {ABSOLUTE_MAX_CHARS}."
            if truncated
            else None
        ),
    }


@mcp.tool()
def get_algorithm_summary(path: str) -> dict[str, Any]:
    """Return a short summary from the manifest entry and nearby README when available."""
    resolved, rel_path = _allowed_algorithm_path(path)
    entry = _entry_for_path(rel_path)

    readme_path = resolved if resolved.name == "README.md" else resolved.parent / "README.md"
    readme_excerpt = None
    if readme_path.exists() and readme_path.is_file():
        lines = [
            line.strip()
            for line in readme_path.read_text(encoding="utf-8", errors="replace").splitlines()
            if line.strip() and not line.strip().startswith("```")
        ]
        readme_excerpt = "\n".join(lines[:6])[:1200] if lines else None

    if entry:
        summary = {
            "path": rel_path,
            "title": entry.get("title"),
            "category": entry.get("category"),
            "concepts": entry.get("concepts", []),
            "visual_use": entry.get("visual_use"),
            "good_for": entry.get("good_for", []),
            "complexity": entry.get("complexity"),
            "dependencies": entry.get("dependencies", []),
            "readme_excerpt": readme_excerpt,
        }
    else:
        summary = {
            "path": rel_path,
            "title": resolved.parent.name.replace("_", " ").title(),
            "category": rel_path.split("/", 1)[0],
            "readme_excerpt": readme_excerpt,
        }
    return summary


def main() -> None:
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
