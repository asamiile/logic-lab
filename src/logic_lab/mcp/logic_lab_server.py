from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field

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
    """Return the full Logic Lab art algorithm manifest as a JSON object.

    The manifest contains an 'entries' array. Each entry includes:
    - path (str): manifest-relative path to the source file (e.g. 'physics/wave/wave.py')
    - title (str): human-readable algorithm name
    - category (str): domain (physics, steering_behaviors, genetic_algorithms,
      neuro_evolution, fractals, cellular_automata, mathematical, tiling_patterns,
      research, simulation, shader)
    - concepts (list[str]): key algorithmic concepts demonstrated
    - visual_use (str): one-line description of the visual output
    - good_for (list[str]): suggested use-cases and aesthetic tags
    - complexity (str): 'low', 'medium', or 'high'
    - dependencies (list[str]): required Python packages beyond py5

    This tool is read-only and returns cached data for the current session.
    Prefer search_algorithms for filtered discovery. Use get_manifest when you
    need the full entry list or want to enumerate all available categories.
    """
    return _load_manifest()


@mcp.tool()
def search_algorithms(
    query: Annotated[
        str,
        Field(
            description=(
                "Free-text search terms matched against title, category, concepts, "
                "visual_use, and good_for fields. Use short descriptive phrases such as "
                "'flow field particles', 'recursive tree', or 'emergent flocking'. "
                "Synonym expansion is applied automatically (e.g. 'flow' also matches 'fluid')."
            )
        ),
    ],
    category: Annotated[
        str | None,
        Field(
            description=(
                "Exact category filter (case-insensitive). Limits results to a single domain. "
                "Available values: physics, steering_behaviors, genetic_algorithms, "
                "neuro_evolution, fractals, cellular_automata, mathematical, tiling_patterns, "
                "research, simulation, shader. Omit to search across all categories."
            )
        ),
    ] = None,
    limit: Annotated[
        int,
        Field(
            description=(
                "Maximum number of results to return. Accepts integers in the range 1–50. "
                "Default: 5. Results are sorted by relevance score descending."
            )
        ),
    ] = 5,
) -> list[dict[str, Any]]:
    """Search the Logic Lab manifest for algorithms by keyword, category, or visual intent.

    Returns a list of manifest entries sorted by relevance score. Each entry includes
    path, title, category, concepts, visual_use, good_for, complexity, and dependencies.
    Returns an empty list when no entries match — this is not an error.

    This tool returns manifest metadata only; it never reads source files.
    Synonym expansion is applied automatically so queries like 'flow' also match
    'fluid' and 'stream'. Combining query with category narrows results to a
    specific domain.

    Recommended workflow: call this tool for discovery, then get_algorithm_summary
    for short context on candidates, then get_algorithm only for paths you intend
    to use.
    """
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
def get_algorithm(
    path: Annotated[
        str,
        Field(
            description=(
                "Manifest-relative path to a .py or README.md file within the Logic Lab "
                "repository (e.g. 'physics/wave/wave.py' or 'fractals/mandelbrot/README.md'). "
                "Must be a relative path — absolute paths are rejected. Paths that escape "
                "the repository root are rejected. Use search_algorithms or get_manifest "
                "to discover valid paths."
            )
        ),
    ],
    max_chars: Annotated[
        int,
        Field(
            description=(
                f"Maximum characters of source text to return. Accepts integers in the "
                f"range 1–{ABSOLUTE_MAX_CHARS}. Default: {DEFAULT_MAX_CHARS}. "
                f"When the file exceeds this limit the response sets truncated=true and "
                f"includes a notice. Increase this value for large source files, up to "
                f"the hard limit of {ABSOLUTE_MAX_CHARS}."
            )
        ),
    ] = DEFAULT_MAX_CHARS,
) -> dict[str, Any]:
    """Return the source text of a Logic Lab .py file or README.md.

    This tool is read-only: it reads only .py files and README.md files within
    the repository boundary. File creation, editing, deletion, and shell execution
    are not available through this server.

    Returns a dict with:
    - path (str): normalized manifest-relative path
    - content (str): file text, possibly truncated
    - truncated (bool): true when the file exceeded max_chars
    - notice (str | null): truncation message with the current limit and maximum,
      or null when content was not truncated

    Raises AccessError when the path escapes the repository root, points to a
    non-existent file, or refers to a disallowed file type (not .py or README.md).

    Call get_algorithm_summary first to confirm relevance before fetching full
    source. Call search_algorithms or get_manifest to discover valid paths.
    """
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
def get_algorithm_summary(
    path: Annotated[
        str,
        Field(
            description=(
                "Manifest-relative path to a .py or README.md file "
                "(e.g. 'physics/wave/wave.py'). Must be a relative path within the "
                "Logic Lab repository. Use search_algorithms to discover valid paths."
            )
        ),
    ],
) -> dict[str, Any]:
    """Return a short summary of a Logic Lab algorithm without fetching full source.

    For paths in the manifest, returns all metadata fields:
    - path, title, category, concepts, visual_use, good_for, complexity, dependencies
    - readme_excerpt: first ~6 non-empty lines of the nearest README.md (up to 1200
      chars) when a README.md exists in the same directory

    For paths not in the manifest, returns a minimal summary derived from the file
    path (title inferred from directory name, category from the first path segment)
    plus readme_excerpt when available.

    This tool never returns source code — call get_algorithm for that. Use this
    tool to assess relevance before committing to a full source fetch. It is
    cheaper in context than get_algorithm for files you may not end up using.
    """
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
def search_by_mood(
    mood: Annotated[
        str,
        Field(
            description=(
                "Creative mood or visual atmosphere. Must be one of: ethereal, chaotic, "
                "geometric, organic, cosmic, minimal, generative, retro, crystalline, "
                "topological, networked, geological. Case-insensitive. Returns an error "
                "dict with available_moods when the value is not recognized."
            )
        ),
    ],
    style: Annotated[
        str | None,
        Field(
            description=(
                "Optional style refinement as free-text tokens (e.g. 'fluid', 'dark', "
                "'crystalline', 'monochrome'). Tokens are matched against algorithm "
                "metadata to boost ranking within the mood results. Omit to use the "
                "mood profile alone."
            )
        ),
    ] = None,
    limit: Annotated[
        int,
        Field(
            description=(
                "Maximum number of results to return. Accepts integers in the range 1–50. "
                "Default: 8. Results are sorted by combined mood-profile and style score."
            )
        ),
    ] = 8,
) -> dict[str, Any]:
    """Search algorithms by creative mood or visual atmosphere.

    Returns a dict with:
    - mood (str): the normalized mood used for the query
    - style (str | null): the style refinement if provided
    - profile_summary (dict): the mood's associated categories and key concepts
    - results (list): ranked manifest entries matching the mood

    Each mood maps to a curated set of algorithm categories, concepts, and good_for
    tags. The style parameter re-ranks results by matching its tokens against all
    metadata fields. When the mood is unrecognized, returns an error dict containing
    'error', 'available_moods', and a 'tip'.

    Prefer search_algorithms for free-text queries without a clear aesthetic direction.
    Use this tool when you have a specific visual mood in mind (e.g. 'cosmic',
    'minimal', 'chaotic').

    Available moods: ethereal, chaotic, geometric, organic, cosmic, minimal,
    generative, retro, crystalline, topological, networked, geological.
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
def recommend_combinations(
    intent: Annotated[
        str,
        Field(
            description=(
                "Free-text description of the artistic intent or visual goal "
                "(e.g. 'cosmic void with particle trails', 'organic growth with "
                "geometric structure', 'flowing smoke with invisible force fields'). "
                "Used to rank curated multi-layer recipes by keyword relevance."
            )
        ),
    ],
    count: Annotated[
        int,
        Field(
            description=(
                "Number of combination recipes to return. Accepts integers in the range "
                "1 to the total number of available recipes. Default: 3. Recipes are "
                "ranked by how closely their name, description, moods, and layer queries "
                "match the intent."
            )
        ),
    ] = 3,
) -> dict[str, Any]:
    """Suggest multi-layer algorithm combinations for a given artistic intent.

    Returns a dict with:
    - intent (str): the original intent string
    - combinations (list): ranked list of layered recipes
    - tip (str): guidance for following up on returned paths

    Each combination includes:
    - name (str): recipe name
    - description (str): recipe description
    - moods (list[str]): associated creative moods
    - layers (list): each layer has role (str), query (str), and suggestions
      (list of manifest entries resolved by search_algorithms)

    Layer roles describe compositional function (e.g. background, agents, texture,
    overlay). Suggestions are live manifest entries — use get_algorithm_summary or
    get_algorithm on any suggested path for full details.

    Use this tool to plan layered generative artworks from a text description.
    It combines curated recipes with dynamic algorithm lookup per layer.
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
