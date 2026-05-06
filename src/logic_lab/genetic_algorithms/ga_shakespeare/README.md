# GA Shakespeare

```bash
uv run python src/logic_lab/genetic_algorithms/ga_shakespeare/ga_shakespeare.py
```

- Genetic algorithm that evolves random text toward the target phrase "to be or not to be".
- Population of 150 individuals evolves through selection, crossover, and mutation.
- Fitness is calculated by matching characters to the target phrase.
- Higher fitness individuals reproduce more frequently, driving evolution toward the target.
- Press `s` to save a screenshot to `genetic_algorithms/ga_shakespeare/screenshots/`.
