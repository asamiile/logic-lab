# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Phase 1: Color harmony (HSV palette generation, HSB color space)
- Phase 1: Worley noise (cellular noise, distance fields, Voronoi distance)
- Phase 1: Poisson disk sampling (blue noise, spatial distribution)
- Phase 2: Voronoi diagram (spatial partition, proximity coloring)
- Phase 2: Diamond-square fractal terrain (heightmap generation)
- Phase 2: Easing functions library (animation curves, tweening)
- Phase 3: Reaction-diffusion (Gray-Scott model, organic patterns)
- Phase 3: Metaball field (implicit surfaces, morphing blobs)
- Phase 4: Interactive spring mesh (fabric simulation, elastic deformation)
- Phase 4: Flowlines streamline visualization (vector field visualization)
- Phase 5: Audio FFT and beat detection (music visualization, real-time analysis)
- Phase 5: Fluid simulation (stable fluids, Navier-Stokes 2D)

### Changed
- Migrated project structure to src/logic_lab/ layout for proper Python packaging
- Updated pyproject.toml with comprehensive metadata and dependency groups
- Restructured MCP server for new src/ layout

### Fixed
- Fixed py5 API compatibility issues (snake_case naming, property vs method access)
- Improved Worley noise performance with grid-based spatial acceleration
- Fixed metaball influence calculations

### Tests
- Added comprehensive pytest suite with 18+ test methods
- Implemented tests for metaball, voronoi, and worley_noise algorithms
- Configured pytest with coverage reporting

## [0.2.0] - 2026-01-15

### Added
- Mathematical algorithms: color_harmony, poisson_disk, worley_noise, voronoi, diamond_square, easing_functions, metaball
- Physics algorithms: particle_flow, spring_mesh
- Steering behaviors: flowlines
- Research: audio_fft
- Comprehensive CONTRIBUTING.md with Conventional Commits specification
- GitHub Actions CI/CD workflows for testing and automated releases
- MCP server entry point (logic-lab-mcp command)

## [0.1.0] - 2025-11-20

### Added
- Initial project structure
- Basic py5 setup and examples
- MCP server implementation for algorithm access
- Initial README and documentation
