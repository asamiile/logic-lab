from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from logic_lab.mcp._data import COMBINATION_RECIPES, MOOD_PROFILES, SYNONYMS

SERVER_NAME = "logic-lab"
DEFAULT_MAX_CHARS = 12_000
ABSOLUTE_MAX_CHARS = 20_000

# Paths that work for both repo checkout and pip/uvx installation.
# logic_lab_server.py lives at <root>/logic_lab/mcp/logic_lab_server.py
# regardless of whether <root> is src/logic_lab (checkout) or site-packages/logic_lab (installed).
_SERVER_DIR = Path(__file__).resolve().parent  # …/logic_lab/mcp/
SOURCE_ROOT = _SERVER_DIR.parent  # …/logic_lab/
MANIFEST_PATH = _SERVER_DIR / "data" / "art_manifest.json"
MCP_README_PATH = _SERVER_DIR / "README.md"

# Top-level project README: available only in a repo checkout.
_candidate_readme = SOURCE_ROOT.parent.parent / "README.md"
README_PATH = _candidate_readme if _candidate_readme.exists() else MCP_README_PATH

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


@lru_cache(maxsize=1)
def _path_to_entry() -> dict[str, dict[str, Any]]:
    return {entry["path"]: entry for entry in _entries() if isinstance(entry.get("path"), str)}


def _strip_legacy_prefix(path: str) -> str:
    """Remove src/logic_lab/ or logic_lab/ prefix kept for backward compatibility."""
    for prefix in ("src/logic_lab/", "logic_lab/"):
        if path.startswith(prefix):
            return path.removeprefix(prefix)
    return path


def _validate_source_path(path: str) -> tuple[Path, str]:
    """Resolve *path* against SOURCE_ROOT and reject anything that escapes it.

    Accepts manifest-relative paths (e.g. ``physics/wave/wave.py``) and the
    legacy ``src/logic_lab/…`` prefix used by older clients.
    Returns (absolute_path, normalized_relative_path).
    """
    if not path or Path(path).is_absolute():
        raise AccessError("Path must be a relative path")

    normalized = _strip_legacy_prefix(path)
    resolved = (SOURCE_ROOT / normalized).resolve()
    try:
        rel_path = resolved.relative_to(SOURCE_ROOT).as_posix()
    except ValueError as exc:
        raise AccessError("Path outside the source root is not allowed") from exc

    return resolved, rel_path


def _allowed_algorithm_path(path: str) -> tuple[Path, str]:
    """Return (resolved_path, rel_path) only for permitted file types."""
    resolved, rel_path = _validate_source_path(path)
    manifest_paths = _manifest_paths()

    is_manifest_path = rel_path in manifest_paths
    is_python = Path(rel_path).suffix == ".py"
    is_readme = Path(rel_path).name == "README.md"

    if not is_manifest_path and not (is_python or is_readme):
        raise AccessError("Only manifest entries, .py files, and README.md files can be read")
    if not resolved.is_file():
        raise AccessError("Path does not point to a readable file")
    return resolved, rel_path


def _clamp_max_chars(max_chars: int | None) -> int:
    if max_chars is None:
        return DEFAULT_MAX_CHARS
    return max(1, min(int(max_chars), ABSOLUTE_MAX_CHARS))


# ---------------------------------------------------------------------------
# Search helpers
# ---------------------------------------------------------------------------


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
    if query in haystack:
        score += 8
    for token in expanded_tokens:
        if token in haystack:
            score += 2
        if token == str(entry.get("category", "")).lower():
            score += 3
        if token in concepts:
            score += 4
    return score


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


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------


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
    description="Top-level README for Logic Lab (falls back to MCP README when installed standalone).",
    mime_type="text/markdown",
)
def readme_resource() -> str:
    """Return the project README."""
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


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


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
            f"Content truncated to {limit} characters. "
            f"Increase max_chars up to {ABSOLUTE_MAX_CHARS}."
            if truncated
            else None
        ),
    }


@mcp.tool()
def get_algorithm_summary(path: str) -> dict[str, Any]:
    """Return a short summary from the manifest entry and nearby README when available."""
    resolved, rel_path = _allowed_algorithm_path(path)
    entry = _path_to_entry().get(rel_path)

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
        return {
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
    return {
        "path": rel_path,
        "title": resolved.parent.name.replace("_", " ").title(),
        "category": rel_path.split("/", 1)[0],
        "readme_excerpt": readme_excerpt,
    }


@mcp.tool()
def search_by_mood(mood: str, style: str | None = None, limit: int = 8) -> dict[str, Any]:
    """Return algorithms matching a creative mood or visual atmosphere.

    Available moods: ethereal, chaotic, geometric, organic, cosmic, minimal,
    generative, retro, crystalline, topological, networked, geological.
    Optional style narrows results further (e.g. "fluid", "crystalline", "dark").
    """
    normalized_mood = mood.lower().strip()
    profile = MOOD_PROFILES.get(normalized_mood)

    if profile is None:
        return {
            "error": f"Unknown mood '{mood}'.",
            "available_moods": sorted(MOOD_PROFILES.keys()),
            "tip": "Try one of the available moods, or use search_algorithms for free-text search.",
        }

    max_results = max(1, min(int(limit), 50))
    style_tokens = set(style.lower().split()) if style else set()

    scores: list[tuple[int, dict[str, Any]]] = []
    for entry in _entries():
        entry_category = str(entry.get("category", "")).lower()
        entry_concepts = {str(c).lower() for c in entry.get("concepts", [])}
        entry_good_for = {str(g).lower() for g in entry.get("good_for", [])}
        haystack = _search_text(entry)

        score = 0
        if entry_category in profile["categories"]:
            score += 4
        for concept in profile["concepts"]:
            if concept in haystack or concept in entry_concepts:
                score += 2
        for tag in profile["good_for"]:
            if tag in entry_good_for:
                score += 3
        for token in style_tokens:
            if token in haystack:
                score += 5

        if score > 0:
            scores.append((score, entry))

    scores.sort(key=lambda item: (-item[0], item[1].get("path", "")))
    results = [entry for _, entry in scores[:max_results]]

    return {
        "mood": normalized_mood,
        "style": style,
        "profile_summary": {
            "categories": profile["categories"],
            "key_concepts": profile["concepts"][:6],
        },
        "results": results,
    }


@mcp.tool()
def recommend_combinations(intent: str, count: int = 3) -> dict[str, Any]:
    """Suggest multi-layer algorithm combinations for a given artistic intent.

    Returns curated recipes and dynamically ranked algorithm suggestions per layer role.
    Use this to plan layered generative artworks from a text description.
    """
    max_count = max(1, min(int(count), len(COMBINATION_RECIPES)))
    intent_lower = intent.lower()

    recipe_scores: list[tuple[int, dict[str, Any]]] = []
    for recipe in COMBINATION_RECIPES:
        score = 0
        if any(m in intent_lower for m in recipe["moods"]):
            score += 6
        for word in intent_lower.split():
            if word in recipe["name"].lower() or word in recipe["description"].lower():
                score += 2
            for layer in recipe["layers"]:
                if word in layer["query"]:
                    score += 1
        recipe_scores.append((score, recipe))

    recipe_scores.sort(key=lambda x: -x[0])
    top_recipes = [r for _, r in recipe_scores[:max_count]]

    resolved_recipes = []
    for recipe in top_recipes:
        resolved_layers = []
        for layer in recipe["layers"]:
            candidates = search_algorithms(
                query=layer["query"],
                category=layer.get("category"),
                limit=2,
            )
            resolved_layers.append(
                {
                    "role": layer["role"],
                    "query": layer["query"],
                    "suggestions": candidates,
                }
            )
        resolved_recipes.append(
            {
                "name": recipe["name"],
                "description": recipe["description"],
                "moods": recipe["moods"],
                "layers": resolved_layers,
            }
        )

    return {
        "intent": intent,
        "combinations": resolved_recipes,
        "tip": (
            "Each combination has layered roles (background, agents, texture, etc.). "
            "Use get_algorithm or get_algorithm_summary on any suggested path for details."
        ),
    }


def main() -> None:
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
