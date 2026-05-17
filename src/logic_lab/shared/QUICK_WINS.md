# Logic Lab Quick Wins - Usage Guide

Three high-value utilities for improving development efficiency: **Profiling**, **Presets**, and **Batch Processing**.

---

## 1. Profiling Tools 📊

Track FPS, frame times, and performance metrics in real-time.

### Basic Usage

```python
from pathlib import Path
import py5
from logic_lab.shared import PerformanceMonitor, overlay_fps, profile_decorator

monitor = PerformanceMonitor(window_size=60)  # 60-frame rolling average

def setup() -> None:
    py5.size(640, 480)

@profile_decorator(monitor)
def draw() -> None:
    py5.background(255)
    # Your algorithm here
    overlay_fps(monitor, x=10, y=20)  # Show FPS on screen
    monitor.print_stats(interval_seconds=5.0)  # Print every 5 seconds

py5.run_sketch()
```

### Monitor Properties

```python
monitor.fps                    # Current FPS
monitor.avg_frame_time_ms      # Average frame time (ms)
monitor.max_frame_time_ms      # Max frame time in window (ms)
monitor.min_frame_time_ms      # Min frame time in window (ms)
monitor.frame_count            # Total frames processed
monitor.elapsed_seconds()      # Total elapsed time
```

### Profiling Code Sections

```python
from logic_lab.shared import profile_section

def expensive_function() -> None:
    with profile_section("Particle Update"):
        # This section will print its execution time
        for particle in particles:
            particle.update()

    with profile_section("Collision Detection"):
        # Track time for another section
        detect_collisions(particles)
```

### Decorator Usage

```python
from logic_lab.shared import profile_decorator

monitor = PerformanceMonitor()

@profile_decorator(monitor)
def compute_frame() -> None:
    # Automatically tracks frame time
    pass

# Access monitor from decorated function
compute_frame()
print(f"FPS: {compute_frame.monitor.fps}")
```

---

## 2. Preset System 💾

Save, load, and manage algorithm parameter configurations.

### Basic Usage

```python
from pathlib import Path
from logic_lab.shared import PresetManager, AlgorithmPreset

# Create preset manager (presets saved to ./presets/)
manager = PresetManager(preset_dir=Path("./presets"))

# Save a preset
manager.save_preset(
    name="sunset_warm",
    algorithm="color_harmony",
    params={
        "hue": 30,
        "saturation": 0.8,
        "brightness": 0.9,
    },
    seed=42,
    description="Warm sunset color palette"
)

# Load a preset
preset = manager.load_preset("sunset_warm")
print(f"Params: {preset.params}")
print(f"Seed: {preset.seed}")
```

### In Sketch

```python
import py5
from logic_lab.shared import PresetManager

manager = PresetManager()
presets = manager.list_presets()

def setup() -> None:
    py5.size(640, 480)

def draw() -> None:
    py5.background(255)
    # Use preset parameters
    if manager.current_preset:
        params = manager.current_preset.params
        # Apply parameters to algorithm

def key_pressed() -> None:
    if py5.key == "s":
        # Save current state as preset
        manager.save_preset(
            name=f"run_{py5.frame_count}",
            algorithm="my_algorithm",
            params={"scale": 1.0, "noise": 0.1},
            seed=py5.random_seed,
        )

    # Load preset with number keys (0-9)
    presets = manager.list_presets()
    if py5.key.isdigit():
        idx = int(py5.key)
        if idx < len(presets):
            manager.load_preset(presets[idx])

py5.run_sketch()
```

### Preset Features

```python
# List all presets
all_presets = manager.list_presets()

# List presets for specific algorithm
algorithm_presets = manager.list_presets(algorithm="color_harmony")

# Get without loading
preset = manager.get_preset("sunset_warm")

# Delete a preset
manager.delete_preset("sunset_warm")

# Export multiple presets to file
manager.export_presets(Path("exported_presets.json"))

# Import from file
manager.import_presets(Path("exported_presets.json"), overwrite=False)
```

---

## 3. Batch Processing 🚀

Run algorithms multiple times without GUI for parameter sweeps and high-throughput rendering.

### Basic Batch Mode

```python
import py5
from logic_lab.shared import BatchRunner, BatchConfig
from pathlib import Path

config = BatchConfig(
    algorithm_name="particle_system",
    output_dir=Path("output/particles"),
    width=1280,
    height=720,
    num_frames=300,
    save_interval=1,  # Save every frame
    seed=12345,
)

runner = BatchRunner(config)

def setup() -> None:
    runner.setup()  # Sets py5.size() and prints config

def draw() -> None:
    py5.background(255)
    # Your algorithm here

    if runner.should_save_frame():
        runner.save_frame()

    runner.advance_frame()

    # Exit when done
    if runner.is_done():
        runner.save_config()  # Save config.json
        py5.exit()

py5.run_sketch()
```

### Run a Batch from Command Line

```bash
# Headless mode - no window display
uv run python src/logic_lab/physics/particle_system/batch_run.py
```

### Parameter Sweeps

```python
from logic_lab.shared import ParameterSweep, BatchSequence
from pathlib import Path

# Create a sweep over multiple parameters
sweep = ParameterSweep(base_params={"color": (255, 0, 0)})
sweep.add_range("scale", start=0.5, end=2.0, num_steps=5)
sweep.add_range("noise", start=0.0, end=1.0, num_steps=3)

# Generate all combinations
combinations = sweep.generate()
print(f"Generated {len(combinations)} combinations")

# Example: 5 × 3 = 15 combinations with different scale and noise values
```

### Batch Sequence

```python
from logic_lab.shared import BatchSequence
from pathlib import Path

# Run multiple algorithms in sequence
sequence = BatchSequence(output_base_dir=Path("output"))

sequence.add_job(
    algorithm_name="algorithm_1",
    num_frames=100,
    seed=42,
    params={"scale": 1.0}
)

sequence.add_job(
    algorithm_name="algorithm_2",
    num_frames=100,
    seed=43,
    params={"scale": 1.5}
)

# Save manifest describing all jobs
sequence.save_manifest()
```

### Advanced Example: Sweep with Batch

```python
from logic_lab.shared import BatchRunner, BatchConfig, ParameterSweep, ParameterSweep
from pathlib import Path
import py5

# Create parameter sweep
sweep = ParameterSweep(base_params={"seed": 0})
sweep.add_range("scale", 0.5, 2.0, num_steps=3)
sweep.add_range("noise", 0.0, 1.0, num_steps=2)

# Generate all combinations: 3 × 2 = 6 variations
combinations = sweep.generate()

# Run each combination
for i, params in enumerate(combinations):
    config = BatchConfig(
        algorithm_name="test_algorithm",
        output_dir=Path(f"output/sweep_{i:03d}"),
        num_frames=60,
        params=params,
    )

    runner = BatchRunner(config)

    def setup() -> None:
        runner.setup()

    def draw() -> None:
        py5.background(255)
        scale = runner.config.params["scale"]
        noise = runner.config.params["noise"]
        # Use parameters...

        if runner.should_save_frame():
            runner.save_frame()

        runner.advance_frame()

        if runner.is_done():
            runner.save_config()
            py5.exit()

    py5.run_sketch()
```

---

## 4. Combining All Three

Complete example using profiling, presets, and batch mode together:

```python
import py5
from pathlib import Path
from logic_lab.shared import (
    PerformanceMonitor,
    overlay_fps,
    PresetManager,
    BatchRunner,
    BatchConfig,
    profile_decorator,
)

# Setup managers
monitor = PerformanceMonitor()
preset_manager = PresetManager()
batch_config = BatchConfig(
    algorithm_name="combined_example",
    output_dir=Path("output"),
    num_frames=300,
)
batch_runner = BatchRunner(batch_config)

# Load preset if available
preset = preset_manager.load_preset("default") if "default" in preset_manager.list_presets() else None

@profile_decorator(monitor)
def setup() -> None:
    batch_runner.setup()

@profile_decorator(monitor)
def draw() -> None:
    py5.background(255)

    # Use preset parameters if loaded
    if preset:
        params = preset.params
    else:
        params = {}

    # Your algorithm here

    # Show performance overlay
    overlay_fps(monitor, x=10, y=20)

    # Save frames in batch mode
    if batch_runner.should_save_frame():
        batch_runner.save_frame()

    batch_runner.advance_frame()

    # Periodically print stats
    monitor.print_stats(interval_seconds=10.0)

    if batch_runner.is_done():
        batch_runner.save_config()
        preset_manager.current_preset = preset
        py5.exit()

def key_pressed() -> None:
    if py5.key == "p":
        # Print current stats
        print(f"\nFPS: {monitor.fps:.1f}")
        print(f"Avg Frame: {monitor.avg_frame_time_ms:.2f}ms")

    elif py5.key == "s":
        # Save current state
        preset_manager.save_preset(
            name=f"snapshot_{py5.frame_count}",
            algorithm="combined_example",
            params={},
            seed=batch_config.seed,
        )

py5.run_sketch()
```

---

## Tips & Best Practices

### Profiling
- Use `profile_section()` to identify bottlenecks
- Call `print_stats()` with appropriate interval to avoid console spam
- Check `monitor.fps` to ensure consistent performance

### Presets
- Save presets frequently during creative exploration
- Use descriptive preset names ("warm_palette", "fast_particles")
- Export presets for sharing configurations

### Batch Processing
- Use batch mode for generating large image series
- Parameter sweeps help explore design space systematically
- Save config.json to document batch parameters
- Redirect stdout to file: `python script.py > output.log`

### Performance
- Profile before optimizing - identify real bottlenecks
- Batch processing runs headless (no GUI overhead)
- Monitor frame times to detect performance regressions
