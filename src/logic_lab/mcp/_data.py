"""Static lookup tables for search, mood matching, and combination recipes."""

from __future__ import annotations

from typing import Any

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
    "crystal": ["snowflake", "dendrite", "crystallization", "ice", "mineral", "solidification"],
    "snowflake": ["crystal growth", "dendritic", "6-fold symmetry", "Reiter model", "ice crystal"],
    "dendrite": [
        "branching crystal",
        "dendritic solidification",
        "crystal arm",
        "diffusion limited",
    ],
    "topology": ["manifold", "Mobius", "Klein bottle", "torus knot", "genus", "non-orientable"],
    "knot": ["torus knot", "trefoil", "knot theory", "link", "braid"],
    "network": ["graph", "node", "edge", "scale-free", "small world", "Watts-Strogatz"],
    "scale-free": ["power law", "hub", "Barabasi-Albert", "preferential attachment"],
    "wavelet": ["wavelet transform", "frequency", "time-frequency", "multiresolution"],
    "signal": ["signal processing", "filter", "frequency", "spectral", "convolution"],
    "som": ["self-organizing map", "Kohonen", "competitive learning", "neural map"],
    "erosion": ["hydraulic erosion", "terrain sculpting", "water flow", "geological"],
    "terrain": ["heightmap", "elevation map", "landscape", "procedural terrain", "geology"],
    "diffraction": ["wave diffraction", "interference fringe", "single slit", "double slit"],
    "caustic": ["light caustic", "refraction", "lens effect", "underwater light"],
    "illusion": ["optical illusion", "perceptual geometry", "impossible object", "gestalt"],
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
    "crystalline": {
        "concepts": ["crystal", "snowflake", "dendrite", "lattice", "6-fold", "mineral"],
        "categories": ["crystal_growth", "mathematical", "tiling_patterns"],
        "good_for": ["crystalline", "snowflake", "mineral", "symmetric", "nature"],
    },
    "topological": {
        "concepts": ["topology", "manifold", "knot", "surface", "continuous", "deformation"],
        "categories": ["topology", "mathematical", "three_dimensional"],
        "good_for": ["topological", "abstract", "mathematical", "3D", "surface"],
    },
    "networked": {
        "concepts": ["network", "graph", "node", "edge", "spreading", "connectivity"],
        "categories": ["network_dynamics", "steering_behaviors", "swarm_intelligence"],
        "good_for": ["networks", "graphs", "spreading", "connected", "emergent"],
    },
    "geological": {
        "concepts": ["terrain", "erosion", "heightmap", "landscape", "geological", "noise"],
        "categories": ["procedural_terrain", "physics", "mathematical"],
        "good_for": ["terrain", "landscape", "erosion", "geological", "natural"],
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
    {
        "name": "Crystal Universe",
        "description": "Dendritic snowflake growth rendered against a deep-space particle field",
        "moods": ["crystalline", "cosmic"],
        "layers": [
            {"role": "background", "query": "perlin noise", "category": "shader"},
            {
                "role": "crystal",
                "query": "snowflake crystal dendrite",
                "category": "crystal_growth",
            },
            {"role": "glow", "query": "raymarching sphere glow", "category": "shader"},
        ],
    },
    {
        "name": "Network Bloom",
        "description": "Scale-free network topology emerging from biological growth rules",
        "moods": ["networked", "generative"],
        "layers": [
            {
                "role": "structure",
                "query": "scale-free network graph",
                "category": "network_dynamics",
            },
            {"role": "growth", "query": "space colonization branch", "category": "biological"},
            {"role": "texture", "query": "Voronoi stippling", "category": "mathematical"},
        ],
    },
    {
        "name": "Geological Strata",
        "description": "Procedural terrain with hydraulic erosion and noise-driven layering",
        "moods": ["geological", "ethereal"],
        "layers": [
            {
                "role": "terrain",
                "query": "hydraulic erosion heightmap",
                "category": "procedural_terrain",
            },
            {"role": "detail", "query": "domain warp FBM", "category": "shader"},
            {"role": "color", "query": "worley noise", "category": "mathematical"},
        ],
    },
]
