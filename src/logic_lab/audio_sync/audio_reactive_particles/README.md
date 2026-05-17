# Audio-Reactive Particles

Real-time visualization of audio frequencies through particles that spawn and animate in response to bass, mid, and high-frequency content from microphone input or simulated audio.

```bash
uv run python src/logic_lab/audio_sync/audio_reactive_particles/audio_reactive_particles.py
```

Press `m` to toggle between microphone input and demo mode, `s` to save a screenshot, `r` to reset, or `SPACE` to pause.

The system analyzes audio frequencies using FFT, mapping bass to explosion radius, mid-frequencies to spawn rate, and high frequencies to color shifts (blue → purple → pink).
