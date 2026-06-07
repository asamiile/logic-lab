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
    "polygon": ["angular", "vertices", "edge", "multi-sided", "geometric shape"],
    "line art": ["hatching", "stripes", "linework", "crosshatch", "straight lines"],
    "shape": ["form", "contour", "outline", "silhouette", "morphology"],
    "tiling": ["tessellation", "mosaic", "grid", "periodic", "wallpaper"],
    "symmetry": ["reflection", "rotation", "dihedral", "wallpaper group"],
    "polyhedra": ["platonic solid", "3D shape", "wireframe", "tetrahedron", "cube", "octahedron"],
    "metaball": ["isosurface", "implicit surface", "blob", "potential field", "3D"],
    "gray scott": ["reaction diffusion", "turing pattern", "activator inhibitor", "chemical"],
    "bee foraging": ["swarm intelligence", "colony", "waggle dance", "food site", "optimization"],
    "audio": ["sound", "music", "frequency", "FFT", "reactive", "spectrum"],
    "swarm": ["colony", "ants", "bees", "flock", "swarm intelligence"],
    "volume": ["3D", "volumetric", "voxel", "metaball", "depth"],
    "biological": ["organism", "colony", "growth", "natural", "living"],
    "shader": ["GLSL", "fragment shader", "GPU", "raymarching", "SDF", "noise", "WebGL"],
    "raymarching": ["SDF", "sphere tracing", "ray marching", "3D rendering", "distance field"],
    "domain warp": ["FBM warp", "domain warping", "noise distortion", "space warp"],
    "voronoi": ["cellular", "Worley", "distance field", "cells", "tessellation"],
    "perlin": ["Perlin noise", "gradient noise", "smooth noise", "Ken Perlin"],
    "fbm": ["fractional brownian motion", "octave noise", "multi-octave", "layered noise"],
    "sdf": ["signed distance field", "SDF", "distance function", "implicit surface"],
}

MOOD_PROFILES: dict[str, dict[str, list[str]]] = {
    "ethereal": {
        "concepts": ["noise", "glow", "soft", "light", "FBM", "domain warp", "flow", "atmospheric"],
        "categories": ["shader", "fractals", "mathematical"],
        "good_for": ["atmospheric", "clouds", "abstract", "soft", "fluid"],
    },
    "chaotic": {
        "concepts": ["chaos", "strange attractor", "particle", "swarm", "turbulence", "emergence"],
        "categories": ["physics", "fractals", "steering_behaviors", "swarm_intelligence"],
        "good_for": ["chaos", "dynamic", "complex", "energetic"],
    },
    "geometric": {
        "concepts": ["SDF", "polygon", "tiling", "symmetry", "grid", "polyhedra", "boolean"],
        "categories": ["shader", "tiling_patterns", "mathematical", "three_dimensional"],
        "good_for": ["geometric", "architectural", "precise", "grid", "pattern"],
    },
    "organic": {
        "concepts": [
            "growth",
            "biological",
            "FBM",
            "reaction diffusion",
            "Voronoi",
            "flow",
            "domain warp",
        ],
        "categories": ["biological", "reaction_diffusion", "shader", "cellular_automata"],
        "good_for": ["organic", "nature", "biological", "fluid", "texture"],
    },
    "cosmic": {
        "concepts": [
            "particle",
            "galaxy",
            "attractor",
            "noise",
            "depth",
            "glow",
            "3D",
            "raymarching",
        ],
        "categories": ["physics", "shader", "fractals", "mathematical"],
        "good_for": ["cosmic", "space", "deep", "3D", "atmospheric"],
    },
    "minimal": {
        "concepts": ["line", "circle", "polygon", "SDF", "geometric", "simple"],
        "categories": ["mathematical", "shader", "tiling_patterns"],
        "good_for": ["minimal", "clean", "geometric", "graphic"],
    },
    "generative": {
        "concepts": ["emergent", "growth", "evolution", "self-organization", "pattern"],
        "categories": [
            "cellular_automata",
            "genetic_algorithms",
            "biological",
            "reaction_diffusion",
        ],
        "good_for": ["generative", "emergent", "pattern", "complex"],
    },
    "retro": {
        "concepts": ["pixel", "posterization", "hash", "grid", "cellular"],
        "categories": ["shader", "tiling_patterns", "cellular_automata"],
        "good_for": ["retro", "pixel", "poster", "graphic", "grid"],
    },
}

COMBINATION_RECIPES: list[dict[str, Any]] = [
    {
        "name": "Organic Flow Field",
        "description": "Fluid, living motion through FBM-warped space with biological agents",
        "moods": ["organic", "ethereal"],
        "layers": [
            {"role": "background", "query": "domain warp", "category": "shader"},
            {"role": "agents", "query": "steering flow", "category": "steering_behaviors"},
            {"role": "texture", "query": "FBM noise", "category": "shader"},
        ],
    },
    {
        "name": "Cosmic Particle Storm",
        "description": "Deep-space particle systems driven by gravity and noise attractors",
        "moods": ["cosmic", "chaotic"],
        "layers": [
            {"role": "background", "query": "perlin noise", "category": "shader"},
            {"role": "dynamics", "query": "gravity particle", "category": "physics"},
            {"role": "glow", "query": "raymarching sphere", "category": "shader"},
        ],
    },
    {
        "name": "Living Crystal",
        "description": "Geometric 3D forms that grow and evolve like living organisms",
        "moods": ["geometric", "generative"],
        "layers": [
            {"role": "form", "query": "SDF morphing", "category": "shader"},
            {"role": "growth", "query": "reaction diffusion", "category": "reaction_diffusion"},
            {"role": "structure", "query": "Voronoi", "category": "shader"},
        ],
    },
    {
        "name": "Swarm Texture",
        "description": "Emergent patterns painted by swarm agents on a noise canvas",
        "moods": ["organic", "generative"],
        "layers": [
            {"role": "canvas", "query": "value noise", "category": "shader"},
            {"role": "agents", "query": "swarm intelligence", "category": "swarm_intelligence"},
            {"role": "trails", "query": "steering behaviors", "category": "steering_behaviors"},
        ],
    },
    {
        "name": "Fractal Cosmos",
        "description": "Infinite self-similar structures rendered with recursive depth",
        "moods": ["cosmic", "ethereal"],
        "layers": [
            {"role": "base", "query": "FBM", "category": "shader"},
            {"role": "structure", "query": "fractal", "category": "fractals"},
            {"role": "detail", "query": "worley layers", "category": "shader"},
        ],
    },
    {
        "name": "Bio-Mechanical Growth",
        "description": "Cellular automata patterns shaped by mycelium-like biological networks",
        "moods": ["organic", "generative"],
        "layers": [
            {"role": "growth", "query": "cellular automata", "category": "cellular_automata"},
            {"role": "network", "query": "mycelium biological", "category": "biological"},
            {"role": "texture", "query": "Voronoi noise", "category": "shader"},
        ],
    },
    {
        "name": "Geometric Minimal",
        "description": "Clean, precise shapes with SDF-based composition and subtle gradients",
        "moods": ["minimal", "geometric"],
        "layers": [
            {"role": "shapes", "query": "SDF boolean 2D", "category": "shader"},
            {"role": "pattern", "query": "tiling symmetry", "category": "tiling_patterns"},
            {"role": "color", "query": "polar coordinates", "category": "shader"},
        ],
    },
    {
        "name": "Reaction Diffusion Landscape",
        "description": "Chemical pattern formation evolving over animated terrain",
        "moods": ["organic", "generative"],
        "layers": [
            {
                "role": "chemistry",
                "query": "gray scott reaction diffusion",
                "category": "reaction_diffusion",
            },
            {"role": "terrain", "query": "domain warp FBM", "category": "shader"},
            {"role": "detail", "query": "displacement surface", "category": "shader"},
        ],
    },
]

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


@mcp.tool()
def search_by_mood(mood: str, style: str | None = None, limit: int = 8) -> dict[str, Any]:
    """Return algorithms matching a creative mood or visual atmosphere.

    Available moods: ethereal, chaotic, geometric, organic, cosmic, minimal, generative, retro.
    Optional style narrows results further (e.g. "fluid", "crystalline", "dark").
    """
    normalized_mood = mood.lower().strip()
    profile = MOOD_PROFILES.get(normalized_mood)

    if profile is None:
        available = sorted(MOOD_PROFILES.keys())
        return {
            "error": f"Unknown mood '{mood}'.",
            "available_moods": available,
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
        # Category match
        if entry_category in profile["categories"]:
            score += 4
        # Concept overlap
        for concept in profile["concepts"]:
            if concept in haystack or concept in entry_concepts:
                score += 2
        # good_for overlap
        for tag in profile["good_for"]:
            if tag in entry_good_for:
                score += 3
        # Optional style refinement
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

    # Score recipes by how well they match the intent
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

    # Resolve each recipe's layers to actual manifest entries
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
