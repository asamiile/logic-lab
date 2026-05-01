# Smart Rockets Basic

```bash
uv run python simulation/smart_rockets_basic/smart_rockets_basic.py
```

- Genetic algorithm that evolves rockets to reach a target using steering forces.
- Each rocket's DNA contains 250 force vectors (one per frame).
- Population of 50 rockets evolves through fitness-based selection and reproduction.
- Rockets improve over generations to reach the target more efficiently.
- Click the mouse to move the target; rockets will adapt to the new goal.
- Press `s` to save a screenshot to `simulation/smart_rockets_basic/screenshots/`.
