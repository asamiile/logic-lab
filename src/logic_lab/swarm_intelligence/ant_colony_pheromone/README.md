# Ant Colony Pheromone Trails

Stigmergy-based foraging simulation where ants deposit two pheromone types — home-trail and food-trail — that evaporate over time and reinforce shortest paths between hive and food sources.

```bash
uv run python src/logic_lab/swarm_intelligence/ant_colony_pheromone/ant_colony_pheromone.py
```

Press `r` to reset, or `s` to save a screenshot.

Each ant senses pheromone at three forward positions (left, center, right) and steers toward the strongest gradient. Carrying ants deposit a stronger food-trail on return, creating emergent network art whose topology reflects the optimal foraging paths.
