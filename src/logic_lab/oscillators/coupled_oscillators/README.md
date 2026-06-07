# Coupled Oscillators (Kuramoto Model)

N phase oscillators with random natural frequencies interact through a mean-field coupling term. Above the critical coupling strength, they spontaneously synchronize — a classic model of emergent collective rhythm in biology, neuroscience, and physics.

```bash
uv run python src/logic_lab/oscillators/coupled_oscillators/coupled_oscillators.py
```

Press `↑/↓` to manually adjust coupling strength K, `Space` to pause, `r` to reset, or `s` to save a screenshot.

Each dot on the circle is an oscillator; its color encodes natural frequency (blue=slow, red=fast). The gold arrow is the order parameter R — its length measures global synchrony (R≈0 chaotic, R≈1 synchronized). The LFO automatically sweeps K across the phase transition so you can watch the flock suddenly lock in.
