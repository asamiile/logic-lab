# Predator-Prey Flocking

Reynolds' Boids flocking extended with predator agents that hunt the flock. Prey exhibit emergent escape maneuvers — splitting, scattering, and reforming — driven by fear-weighted steering forces.

```bash
uv run python src/logic_lab/swarm_intelligence/predator_prey_flocking/predator_prey_flocking.py
```

Press `r` to reset, or `s` to save a screenshot.

Prey balance separation, alignment, and cohesion forces until a predator enters fear range, at which point the fear weight overrides flocking to produce evasive bursts. Predators chase the nearest prey using a simple pursuit steering force.
