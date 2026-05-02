# Interactive Selection - Evolving Flowers

```bash
uv run python genetic_algorithms/interactive_selection/interactive_selection.py
```

- Interactive genetic algorithm where you control evolution by selecting flowers
- 8 flowers are displayed with genetically determined traits (petal color, size, count; center color/size; stem color/length)
- Each flower has 14 genes (floats 0-1) controlling different visual properties
- Hover the mouse over flowers to increase their fitness (each flower displays its fitness value below)
- Click the "evolve new generation" button to create the next generation based on fitness selection
- Higher-fitness parents are more likely to produce offspring
- Press `s` to save a screenshot to `genetic_algorithms/interactive_selection/screenshots/`

## How to use

1. Hover over flowers you like to increase their fitness score (fitness increases each frame)
2. Click "evolve new generation" when ready to breed the next generation
3. Repeat to evolve flowers toward your aesthetic preferences

## Gene structure

- genes[0-3]: Petal color (RGB + alpha)
- genes[4]: Petal size (mapped 0-1 to 4-24 pixels)
- genes[5]: Petal count (mapped 0-1 to 2-16 petals)
- genes[6-8]: Center color (RGB)
- genes[9]: Center size (mapped 0-1 to 24-48 pixels)
- genes[10-12]: Stem color (RGB)
- genes[13]: Stem length (mapped 0-1 to 50-100 pixels)
