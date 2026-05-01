# Smart Rockets

```bash
uv run python simulation/smart_rockets/smart_rockets.py
```

- Genetic algorithm that evolves rockets to navigate around an obstacle to reach a target.
- Population of 150 rockets with 400-frame DNA sequences.
- Evolution occurs when any rocket reaches the target.
- Rockets are penalized for hitting obstacles and rewarded for reaching the target.
- Click the mouse to move the target; rockets adapt to the new goal.
- Press `s` to save a screenshot to `simulation/smart_rockets/screenshots/`.
