# Bee Foraging Algorithm

Swarm intelligence simulation where bees discover and exploit food sources through local search and information sharing via waggle dance.

```bash
uv run python src/logic_lab/swarm_intelligence/bee_foraging/bee_foraging.py
```

Press `r` to reset, `s` to save screenshot, `d` for debug mode, or `SPACE` to pause.

Bees transition through scout (random exploration), employed (local search), and onlooker (following waggle dance) phases to efficiently optimize over a multi-peak fitness landscape.
