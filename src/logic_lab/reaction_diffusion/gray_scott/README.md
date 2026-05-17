# Gray-Scott Reaction-Diffusion System

A beautiful implementation of the Gray-Scott reaction-diffusion equations, which model chemical interactions between two substances creating mesmerizing self-organizing patterns.

## Mathematical Foundation

The Gray-Scott system describes the concentration dynamics of two chemical substances (U and V) under diffusion and reaction:

```
∂U/∂t = Du·∇²U - U·V² + F·(1 - U)
∂V/∂t = Dv·∇²V + U·V² - (F + k)·V
```

Where:
- **U**: Activator (promotes production of both U and V)
- **V**: Inhibitor (suppresses U)
- **Du = 0.16**: Diffusion coefficient for U
- **Dv = 0.08**: Diffusion coefficient for V
- **F**: Feed rate (replenishes U)
- **k**: Kill rate (removes V)
- **∇²**: Laplacian operator (diffusion)

## Pattern Formation

The interplay between feed rate (F) and kill rate (k) produces distinct visual patterns:

### Preset Patterns

1. **Spots** (F=0.035, k=0.065)
   - Creates isolated circular spots
   - High contrast between filled and empty regions
   - Reminiscent of animal coat patterns

2. **Stripes** (F=0.055, k=0.062)
   - Produces elongated stripe patterns
   - Creates rippling, wave-like structures
   - Shows transition between spots and waves

3. **Waves** (F=0.04, k=0.06)
   - Generates traveling wave fronts
   - Creates intricate spiral and labyrinth patterns
   - Most dynamic of the three presets

## Controls

### Keyboard Shortcuts

- **1/2/3**: Select preset pattern (Spots/Stripes/Waves)
- **↑/↓**: Adjust F (feed rate) by ±0.001
- **r**: Reset with current parameters
- **Space**: Pause/Resume simulation
- **s**: Save screenshot

## Visual Output

The system is rendered using a colormap that maps V concentration to colors:
- **Dark blue** (V ≈ 0): Low inhibitor concentration
- **Bright white** (V ≈ 1): High inhibitor concentration

This creates visually striking patterns with clear structure.

## Technical Details

### Numerical Method

- Spatial: Discrete Laplacian via 2D convolution with kernel `[[0,1,0], [1,-4,1], [0,1,0]]`
- Temporal: Forward Euler integration (dt = 1.0)
- Boundary conditions: Toroidal (wrap-around) for smooth, continuous patterns

### Grid Resolution

- Spatial resolution: 256×256 grid
- Display scale: 2×2 pixels per grid cell (512×512 display)
- Efficient pixel-based rendering for smooth visualization

### Initial Conditions

- U initialized to 1.0 with small Gaussian noise (seed pattern)
- V initialized to 0.0 everywhere except a circular region in the center
- Center circle has V = 0.25 to initiate pattern formation

## Performance Characteristics

- Real-time computation (~60 FPS on modern hardware)
- Minimal memory footprint (2×256×256 float32 arrays)
- Efficient convolution-based Laplacian calculation using `scipy.ndimage`

## References

- Gray, P. & Scott, S. K. (1983). "Autocatalytic reactions in the isothermal, continuous stirred tank reactor: Oscillations and instabilities"
- Turing, A. M. (1952). "The chemical basis of morphogenesis" - foundational work on pattern formation
- Karl Sims' website for detailed Gray-Scott parameter maps
