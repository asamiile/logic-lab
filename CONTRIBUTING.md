# Contributing to Logic Lab

Thank you for contributing to Logic Lab! Please follow this guide when adding new algorithms and features.

## Setup

```bash
# Install dependencies
uv sync

# Install development dependencies
uv sync --group dev
```

## Development Workflow

1. **Create a branch**: Create a new branch from `feature/your-feature-name`
2. **Implement**: Add your algorithm or feature
3. **Test**: Add and run tests
4. **Commit**: Follow [Conventional Commits](#conventional-commits)
5. **Create PR**: Open a pull request to `main`
6. **Merge**: Merging to `main` automatically triggers the release process

## Adding Algorithms

### File Structure

New algorithms follow this structure:

```
src/logic_lab/{domain}/{algorithm_name}/
├── {algorithm_name}.py    # Main implementation
├── README.md              # Algorithm description and usage
└── screenshots/           # Screenshot directory
```

### Choosing a Domain

- **mathematical/**: Math algorithms (color, noise, geometry, etc.)
- **physics/**: Physics simulations (particles, springs, fluids, etc.)
- **steering_behaviors/**: Agent control (flow fields, flocking, etc.)
- **genetic_algorithms/**: Evolutionary algorithms
- **neuro_evolution/**: Neural network evolution
- **fractals/**: Fractal generation
- **cellular_automata/**: Cellular automata
- **tiling_patterns/**: Tiling and pattern generation
- **research/**: Experimental and hybrid systems

### py5 Skeleton

```python
from pathlib import Path
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

def setup() -> None:
    py5.size(640, 480)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

def draw() -> None:
    py5.background(255)
    # Implementation goes here

def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "screenshot_####.png"))

py5.run_sketch()
```

### README Template

```markdown
# Algorithm Title

One-sentence description.

## Run

```bash
uv run python src/logic_lab/{domain}/{name}/{name}.py
```

## Controls

| Key | Effect |
|---|---|
| `s` | Save screenshot |

## Algorithm

Brief mathematical explanation.

## Other Environments

**TouchDesigner**: ...

**UE5**: ...
```

### Updating the Manifest

After implementing an algorithm, update the manifest:

```bash
uv run python .agents/update_art_manifest.py --write
```

## Testing

```bash
# Run all tests
uv run pytest tests/

# Run specific test file
uv run pytest tests/test_metaball.py -v

# Run with coverage report
uv run pytest tests/ --cov=src/logic_lab
```

### Adding Tests

Create a test file `tests/test_{algorithm_name}.py`:

```python
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from logic_lab.mathematical.metaball.metaball import Metaball

class TestMetaball:
    def test_initialization(self):
        ball = Metaball(100, 150, radius=50)
        assert ball.x == 100
        assert ball.radius == 50
```

## Conventional Commits

Logic Lab follows [Conventional Commits](https://www.conventionalcommits.org/) for semantic versioning.

### Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Commit Types

- **feat**: New feature (triggers minor version bump)
  ```bash
  git commit -m "feat: add worley noise cellular texture generation"
  ```

- **fix**: Bug fix (triggers patch version bump)
  ```bash
  git commit -m "fix: correct metaball influence calculation at boundaries"
  ```

- **test**: Test additions or fixes (no version bump)
  ```bash
  git commit -m "test: add voronoi distance calculation tests"
  ```

- **docs**: Documentation updates (no version bump)
  ```bash
  git commit -m "docs: update README with installation instructions"
  ```

- **refactor**: Code refactoring (no version bump)
  ```bash
  git commit -m "refactor: simplify particle flow advection"
  ```

- **perf**: Performance improvements
  ```bash
  git commit -m "perf: optimize voronoi grid acceleration structure"
  ```

- **chore**: Build, dependencies, or config changes (no version bump)
  ```bash
  git commit -m "chore: update dependencies in pyproject.toml"
  ```

### Breaking Changes (Major Version Bump)

Add `!` after the type:

```bash
git commit -m "feat!: redesign particle API for better composability"
```

Also add a `BREAKING CHANGE:` section in the commit body:

```
feat!: redesign particle API

BREAKING CHANGE: Particle.update() now requires time_offset parameter
```

### Scope (Optional)

Specify the affected domain:

```bash
git commit -m "feat(metaball): add threshold control parameter"
git commit -m "fix(voronoi): correct HSB to RGB conversion"
```

### Examples

```bash
# New algorithm
git commit -m "feat(mathematical): add diamond-square fractal terrain generation"

# Bug fix
git commit -m "fix(physics): correct spring mesh boundary condition handling"

# Test addition
git commit -m "test(metaball): add influence field distance tests"

# Documentation
git commit -m "docs: add Conventional Commits guide to CONTRIBUTING.md"

# Breaking change
git commit -m "feat(api)!: refactor particle system for GPU compatibility"
```

## Code Quality

```bash
# Lint check with ruff
uv run ruff check src/

# Format with black
uv run black src/ tests/

# Run both lint and fix
uv run ruff check --fix src/
uv run black src/
```

## Release Process

Releases are fully automated. When merging to `main`, the following happens automatically:

- `CHANGELOG.md` is updated with new entries
- Version is automatically determined based on Conventional Commits
- Git tag is created
- GitHub Release is generated

**Developers only need to follow Conventional Commits.** No manual version management required.

## License

All contributions are published under the MIT License.

## Questions & Feedback

Please create an [Issue](https://github.com/asamiii/logic-lab/issues) if you have questions or feedback.
