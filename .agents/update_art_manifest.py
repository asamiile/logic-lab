#!/usr/bin/env python3
"""Add missing Logic Lab simulations to .agents/art_manifest.json.

The script preserves existing entries and only creates conservative draft entries
for newly discovered simulation files. Agents should refine generated concepts,
visual_use, and good_for fields when they add a new algorithm.
"""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "src" / "logic_lab"
MANIFEST_PATH = ROOT / ".agents" / "art_manifest.json"
BASELINE_PATH = ROOT / ".agents" / "art_manifest_baseline.json"
SCAN_DOMAINS = {
    "physics",
    "steering_behaviors",
    "genetic_algorithms",
    "neuro_evolution",
    "fractals",
    "cellular_automata",
    "mathematical",
    "tiling_patterns",
    "research",
    "three_dimensional",
    "reaction_diffusion",
    "swarm_intelligence",
    "audio_sync",
    "biological",
}

KEYWORD_CONCEPTS = {
    "apollonian": ["apollonius", "circle packing", "tangent", "gasket"],
    "attractor": ["attractor", "chaos", "strange attractor"],
    "attraction": ["attraction", "force field"],
    "bezier": ["bezier", "curve"],
    "boid": ["boids", "swarm"],
    "burning": ["burning ship", "absolute value", "fire"],
    "cellular": ["cellular automata", "rules"],
    "chaos": ["chaos", "strange attractor", "butterfly effect"],
    "cloth": ["cloth", "constraints"],
    "conic": ["conic section", "ellipse", "parabola", "hyperbola"],
    "cyclic": ["cyclic CA", "spiral wave", "rotation"],
    "differential": ["differential growth", "organic growth", "membrane"],
    "dla": ["diffusion limited aggregation", "random walk"],
    "evolution": ["evolution", "fitness"],
    "flow": ["flow field", "vectors", "motion field"],
    "flocking": ["boids", "flocking", "emergence"],
    "force": ["force", "physics"],
    "fractal": ["fractal", "recursion"],
    "ga_": ["genetic algorithm", "selection", "mutation"],
    "game_of_life": ["cellular automata", "emergence", "glider"],
    "gasket": ["apollonius", "circle packing", "fractal"],
    "gravity": ["gravity", "attraction", "physics"],
    "harmony": ["harmonograph", "pendulum", "lissajous"],
    "hilbert": ["hilbert curve", "space filling", "locality"],
    "isometric": ["isometric", "perspective", "3D"],
    "iterated": ["iterated function systems", "IFS", "barnsley"],
    "julia": ["julia set", "complex plane", "iteration"],
    "koch": ["koch curve", "fractal"],
    "l_system": ["l-system", "grammar", "recursion"],
    "langton": ["langton", "ant", "emergence", "highway"],
    "lenia": ["artificial life", "continuous CA", "creature"],
    "lorenz": ["lorenz", "chaos", "butterfly effect", "attractor"],
    "mandelbrot": ["mandelbrot", "complex plane", "escape time"],
    "noise": ["perlin noise", "procedural texture"],
    "particle": ["particle system", "emitter"],
    "pendulum": ["pendulum", "oscillation", "physics"],
    "perlin": ["perlin noise", "organic motion"],
    "physarum": ["physarum", "slime mold", "network"],
    "prime": ["ulam", "prime spiral", "number"],
    "recaman": ["recaman", "integer sequence"],
    "recursive": ["recursion", "subdivision"],
    "rossler": ["rossler", "chaos", "attractor", "spiral"],
    "sand": ["falling sand", "powder", "gravity", "granular"],
    "smooth_life": ["smooth", "continuous", "CA", "glider"],
    "smart_rockets": ["genetic algorithm", "navigation", "fitness"],
    "space_colonization": ["space colonization", "branch", "tree"],
    "spiral": ["spiral", "polar coordinates"],
    "strange": ["strange attractor", "chaos", "dynamic"],
    "substrate": ["substrate", "crack", "fracture"],
    "superellipse": ["superellipse", "lame curve"],
    "thomas": ["thomas", "chaos", "attractor"],
    "tiling": ["tiling", "geometry", "pattern"],
    "tree": ["branching", "recursion", "tree"],
    "truchet": ["truchet", "tile", "pattern"],
    "typography": ["typography", "text", "glyph"],
    "voronoi": ["voronoi", "diagram", "stippling"],
    "wave": ["wave", "oscillation"],
    "wavefront": ["wavefront", "propagation", "pattern"],
    "metaball": ["isosurface", "implicit surface", "blob", "potential field"],
    "gray_scott": ["reaction diffusion", "turing pattern", "activator inhibitor"],
    "bee": ["swarm", "foraging", "colony", "waggle dance"],
    "audio": ["sound", "frequency", "FFT", "reactive"],
}

CATEGORY_DEFAULTS = {
    "physics": ["motion", "force"],
    "steering_behaviors": ["steering", "agents"],
    "genetic_algorithms": ["genetic algorithm", "evolution"],
    "neuro_evolution": ["neural network", "evolution"],
    "fractals": ["fractal", "recursion"],
    "cellular_automata": ["cellular automata", "rules"],
    "mathematical": ["geometry", "mathematics"],
    "tiling_patterns": ["tiling", "pattern"],
    "research": ["simulation", "system"],
    "three_dimensional": ["3D", "volumetric", "spatial"],
    "reaction_diffusion": ["reaction diffusion", "pattern formation", "turing"],
    "swarm_intelligence": ["swarm", "agents", "emergence"],
    "audio_sync": ["audio", "sound", "frequency"],
    "biological": ["biological", "organism", "colony"],
}

VISUAL_DEFAULTS = {
    "physics": "Use for motion studies, forces, particles, fields, or physical animation.",
    "steering_behaviors": "Use for autonomous agents, swarms, navigation, or lifelike movement.",
    "genetic_algorithms": "Use for evolved forms, optimization, generations, or selection-driven variation.",
    "neuro_evolution": "Use for agents that learn behavior through evolved neural networks.",
    "fractals": "Use for recursive geometry, branching structures, or self-similar patterns.",
    "cellular_automata": "Use for rule-based grids, emergent textures, or evolving binary patterns.",
    "mathematical": "Use for geometric systems, numerical patterns, or structured generative art.",
    "tiling_patterns": "Use for textile patterns, symmetry studies, ornaments, or tiled surfaces.",
    "research": "Use for experimental systems, hybrid simulations, or advanced visual behaviors.",
    "three_dimensional": "Use for 3D geometry, volumetric effects, spatial structures, or depth rendering.",
    "reaction_diffusion": "Use for organic textures, spot/stripe patterns, chemical wave simulation, or Turing patterns.",
    "swarm_intelligence": "Use for colony behavior, decentralized navigation, emergent foraging, or agent optimization.",
    "audio_sync": "Use for audio-reactive visuals, frequency-driven animation, sound visualization, or music-synchronized art.",
    "biological": "Use for biological organisms, colony growth, organic networks, or symbiotic systems.",
}

GOOD_FOR_DEFAULTS = {
    "physics": ["motion", "fields", "animation"],
    "steering_behaviors": ["agents", "swarms", "navigation"],
    "genetic_algorithms": ["evolution", "variation", "optimization"],
    "neuro_evolution": ["learning agents", "games", "training"],
    "fractals": ["recursion", "growth", "geometry"],
    "cellular_automata": ["emergence", "grids", "patterns"],
    "mathematical": ["geometry", "patterns", "composition"],
    "tiling_patterns": ["tiling", "symmetry", "textiles"],
    "research": ["experiments", "systems", "hybrids"],
    "three_dimensional": ["3D", "spatial", "volumetric"],
    "reaction_diffusion": ["patterns", "textures", "chemistry"],
    "swarm_intelligence": ["swarms", "colonies", "optimization"],
    "audio_sync": ["music", "sound", "reactive"],
    "biological": ["organisms", "colonies", "networks"],
}


def title_from_path(path: Path) -> str:
    readme = path.parent / "README.md"
    if readme.exists():
        for line in readme.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line.startswith("# "):
                return line.removeprefix("# ").strip()
    return path.stem.replace("_", " ").title()


def imports_for(path: Path) -> list[str]:
    dependencies: set[str] = set()
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return []

    allowed = {"py5", "numpy", "pymunk", "networkx", "matplotlib", "neat"}
    for node in ast.walk(tree):
        name = None
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name.split(".")[0]
                if name in allowed:
                    dependencies.add(name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            name = node.module.split(".")[0]
            if name in allowed:
                dependencies.add(name)
    return sorted(dependencies)


def infer_concepts(rel_path: str, category: str) -> list[str]:
    haystack = rel_path.lower()
    concepts: list[str] = []
    for keyword, values in KEYWORD_CONCEPTS.items():
        if keyword in haystack:
            for value in values:
                if value not in concepts:
                    concepts.append(value)
    for value in CATEGORY_DEFAULTS.get(category, []):
        if value not in concepts:
            concepts.append(value)
    return concepts[:6]


def complexity_for(path: Path) -> str:
    lines = path.read_text(encoding="utf-8", errors="replace").count("\n") + 1
    if lines > 260:
        return "high"
    if lines > 120:
        return "medium"
    return "low"


def discover_algorithm_files() -> list[Path]:
    files: list[Path] = []
    for domain in sorted(SCAN_DOMAINS):
        root = SOURCE_ROOT / domain
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            if path.name == "__init__.py" or path.name.endswith("_helpers.py"):
                continue
            files.append(path)
    return sorted(files, key=lambda p: p.relative_to(SOURCE_ROOT).as_posix())


def load_manifest() -> dict[str, Any]:
    if not MANIFEST_PATH.exists():
        return {
            "schema_version": 1,
            "description": "Read-only manifest of selected Logic Lab algorithms for AI agents and MCP search.",
            "entries": [],
        }
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def load_baseline_paths() -> set[str]:
    if not BASELINE_PATH.exists():
        return set()
    data = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    return {path for path in data.get("paths", []) if isinstance(path, str)}


def build_entry(path: Path) -> dict[str, Any]:
    rel_path = path.relative_to(SOURCE_ROOT).as_posix()
    category = rel_path.split("/", 1)[0]
    return {
        "path": rel_path,
        "title": title_from_path(path),
        "category": category,
        "concepts": infer_concepts(rel_path, category),
        "visual_use": VISUAL_DEFAULTS.get(category, "Use as a Logic Lab algorithm reference."),
        "good_for": GOOD_FOR_DEFAULTS.get(category, ["reference"]),
        "complexity": complexity_for(path),
        "dependencies": imports_for(path) or ["py5"],
    }


def update_manifest(write: bool) -> int:
    manifest = load_manifest()
    entries = manifest.setdefault("entries", [])
    existing_paths = {entry["path"] for entry in entries}
    baseline_paths = load_baseline_paths()

    additions = [
        build_entry(path)
        for path in discover_algorithm_files()
        if path.relative_to(SOURCE_ROOT).as_posix() not in existing_paths
        and path.relative_to(SOURCE_ROOT).as_posix() not in baseline_paths
    ]

    if not additions:
        print("art_manifest.json is up to date")
        return 0

    print(f"Found {len(additions)} missing manifest entr{'y' if len(additions) == 1 else 'ies'}:")
    for entry in additions:
        print(f"- {entry['path']}")

    if not write:
        print("Run with --write to append draft entries.")
        return 1

    entries.extend(additions)
    entries.sort(key=lambda entry: (entry.get("category", ""), entry.get("path", "")))
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Updated {MANIFEST_PATH.relative_to(ROOT)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write", action="store_true", help="append missing draft entries to the manifest"
    )
    args = parser.parse_args()
    return update_manifest(write=args.write)


if __name__ == "__main__":
    raise SystemExit(main())
