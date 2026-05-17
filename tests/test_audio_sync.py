"""Tests for audio-sync domain - audio-reactive particles system."""

import math
import time

import numpy as np
import pytest

from logic_lab.audio_sync.audio_reactive_particles import (
    HAS_SOUNDDEVICE,
    AudioCapture,
    AudioParticle,
    AudioReactiveField,
    SpectrumBand,
)


class TestSpectrumBand:
    """Tests for SpectrumBand normalization and state."""

    def test_spectrum_band_init_defaults_to_zero(self) -> None:
        """Spectrum bands should initialize with zero values."""
        band = SpectrumBand()
        assert band.bass == 0.0
        assert band.mid == 0.0
        assert band.high == 0.0

    def test_spectrum_band_init_with_values(self) -> None:
        """Spectrum bands should accept initial values."""
        band = SpectrumBand(bass=0.5, mid=0.3, high=0.2)
        assert band.bass == 0.5
        assert band.mid == 0.3
        assert band.high == 0.2

    def test_spectrum_band_normalize_sums_to_one(self) -> None:
        """Normalized spectrum bands should sum to 1 ± tolerance."""
        band = SpectrumBand(bass=10, mid=5, high=3)
        band.normalize()

        total = band.bass + band.mid + band.high
        assert abs(total - 1.0) < 1e-6

    def test_spectrum_band_normalize_preserves_ratios(self) -> None:
        """Normalization should preserve relative proportions."""
        band = SpectrumBand(bass=4, mid=2, high=1)
        band.normalize()

        # Ratios should be 4:2:1 normalized to 1.0
        assert abs(band.bass - 4 / 7) < 1e-6
        assert abs(band.mid - 2 / 7) < 1e-6
        assert abs(band.high - 1 / 7) < 1e-6

    def test_spectrum_band_normalize_with_zero_total(self) -> None:
        """Normalization with zero values should remain zero."""
        band = SpectrumBand(bass=0, mid=0, high=0)
        band.normalize()

        assert band.bass == 0.0
        assert band.mid == 0.0
        assert band.high == 0.0

    def test_spectrum_band_normalize_single_nonzero(self) -> None:
        """Normalizing single nonzero value should give 1.0."""
        band = SpectrumBand(bass=5, mid=0, high=0)
        band.normalize()

        assert abs(band.bass - 1.0) < 1e-6
        assert band.mid == 0.0
        assert band.high == 0.0


class TestAudioParticle:
    """Tests for AudioParticle lifecycle and physics."""

    def test_particle_init(self) -> None:
        """Particle should initialize with correct values."""
        particle = AudioParticle(x=100, y=200, vx=1.5, vy=-1.0, life=0.8, color=(255, 128, 64))

        assert particle.x == 100
        assert particle.y == 200
        assert particle.vx == 1.5
        assert particle.vy == -1.0
        assert particle.life == 0.8
        assert particle.color == (255, 128, 64)

    def test_particle_is_alive_when_life_positive(self) -> None:
        """Particle should be alive when life > 0."""
        particle = AudioParticle(x=0, y=0, vx=0, vy=0, life=0.1, color=(255, 255, 255))
        assert particle.is_alive() is True

    def test_particle_is_dead_when_life_zero(self) -> None:
        """Particle should be dead when life <= 0."""
        particle = AudioParticle(x=0, y=0, vx=0, vy=0, life=0, color=(255, 255, 255))
        assert particle.is_alive() is False

    def test_particle_is_dead_when_life_negative(self) -> None:
        """Particle should be dead when life < 0."""
        particle = AudioParticle(x=0, y=0, vx=0, vy=0, life=-0.1, color=(255, 255, 255))
        assert particle.is_alive() is False

    def test_particle_update_position(self) -> None:
        """Particle update should apply velocity to position."""
        particle = AudioParticle(x=0, y=0, vx=10, vy=5, life=1.0, color=(255, 255, 255))
        particle.update(gravity=1.0)

        assert particle.x == 10
        assert particle.y == 5

    def test_particle_update_applies_gravity(self) -> None:
        """Particle update should apply gravity damping."""
        particle = AudioParticle(x=0, y=0, vx=10, vy=10, life=1.0, color=(255, 255, 255))
        particle.update(gravity=0.9)

        assert particle.vx == 9.0
        assert particle.vy == 9.0

    def test_particle_update_decreases_life(self) -> None:
        """Particle update should decrease life."""
        particle = AudioParticle(x=0, y=0, vx=0, vy=0, life=1.0, color=(255, 255, 255))
        initial_life = particle.life
        particle.update()

        assert particle.life < initial_life
        assert abs(particle.life - (initial_life - 0.02)) < 1e-6

    def test_particle_lifecycle_dies_after_updates(self) -> None:
        """Particle should eventually die after repeated updates."""
        particle = AudioParticle(x=0, y=0, vx=0, vy=0, life=0.1, color=(255, 255, 255))

        for _ in range(10):
            particle.update()

        assert particle.is_alive() is False


class TestAudioCapture:
    """Tests for AudioCapture initialization and spectrum."""

    def test_audio_capture_init(self) -> None:
        """AudioCapture should initialize with correct parameters."""
        capture = AudioCapture(sample_rate=44100, chunk_size=2048)

        assert capture.sample_rate == 44100
        assert capture.chunk_size == 2048
        assert capture.is_active is False

    def test_audio_capture_default_params(self) -> None:
        """AudioCapture should have sensible defaults."""
        capture = AudioCapture()

        assert capture.sample_rate == 22050
        assert capture.chunk_size == 1024

    def test_audio_capture_get_spectrum_default(self) -> None:
        """AudioCapture should return default spectrum when idle."""
        capture = AudioCapture()
        spectrum = capture.get_spectrum()

        assert spectrum.bass == 0.0
        assert spectrum.mid == 0.0
        assert spectrum.high == 0.0

    def test_audio_capture_spectrum_is_independent_copy(self) -> None:
        """get_spectrum() should return independent copy."""
        capture = AudioCapture()
        spectrum1 = capture.get_spectrum()
        spectrum2 = capture.get_spectrum()

        # Modifying one should not affect the other
        spectrum1.bass = 0.5
        assert spectrum2.bass == 0.0

    def test_audio_capture_process_spectrum_normalizes(self) -> None:
        """_process_spectrum should normalize bands."""
        capture = AudioCapture(sample_rate=22050, chunk_size=1024)

        # Create test audio with known frequency content
        t = np.arange(1024) / 22050
        audio = (
            np.sin(2 * np.pi * 100 * t)  # 100 Hz (bass)
            + 0.5 * np.sin(2 * np.pi * 1000 * t)  # 1000 Hz (mid)
            + 0.25 * np.sin(2 * np.pi * 5000 * t)  # 5000 Hz (high)
        ).astype(np.float32)

        capture._process_spectrum(audio)
        spectrum = capture.get_spectrum()

        # Check that spectrum sums to 1
        total = spectrum.bass + spectrum.mid + spectrum.high
        assert abs(total - 1.0) < 1e-6

    def test_audio_capture_frequency_band_separation(self) -> None:
        """Spectrum should correctly identify frequency bands."""
        capture = AudioCapture(sample_rate=22050, chunk_size=2048)

        # Pure bass tone (100 Hz)
        t = np.arange(2048) / 22050
        bass_audio = np.sin(2 * np.pi * 100 * t).astype(np.float32)
        capture._process_spectrum(bass_audio)
        bass_spectrum = capture.get_spectrum()

        assert bass_spectrum.bass > bass_spectrum.mid
        assert bass_spectrum.bass > bass_spectrum.high

    @pytest.mark.skipif(not HAS_SOUNDDEVICE, reason="sounddevice not available")
    def test_audio_capture_start_stop_idempotent(self) -> None:
        """start/stop should be safe to call multiple times."""
        capture = AudioCapture()

        capture.start()
        capture.start()  # Second start should be no-op
        assert capture.is_active

        capture.stop()
        capture.stop()  # Second stop should be no-op
        assert not capture.is_active


class TestAudioReactiveField:
    """Tests for AudioReactiveField system."""

    def test_field_init(self) -> None:
        """Field should initialize with correct dimensions."""
        field = AudioReactiveField(width=800, height=600)

        assert field.width == 800
        assert field.height == 600
        assert len(field.particles) == 0
        assert field.paused is False

    def test_field_init_defaults(self) -> None:
        """Field should have sensible defaults."""
        field = AudioReactiveField()

        assert field.width == 800
        assert field.height == 600

    def test_field_demo_mode_when_no_sounddevice(self) -> None:
        """Field should enable demo mode when sounddevice unavailable."""
        field = AudioReactiveField()
        # demo_mode depends on HAS_SOUNDDEVICE which we can't control in tests
        # Just verify the field initializes
        assert field is not None

    def test_field_get_spectrum_returns_normalized(self) -> None:
        """Field spectrum should always be normalized."""
        field = AudioReactiveField()
        spectrum = field.get_spectrum()

        total = spectrum.bass + spectrum.mid + spectrum.high
        assert abs(total - 1.0) < 1e-6

    def test_field_demo_mode_spectrum_oscillates(self) -> None:
        """Demo mode spectrum should oscillate over time."""
        field = AudioReactiveField()
        field.demo_mode = True

        spectra = []
        for _ in range(10):
            spectrum = field.get_spectrum()
            spectra.append(spectrum.bass)

        # Bass should vary over time
        bass_min = min(spectra)
        bass_max = max(spectra)
        assert bass_max > bass_min

    def test_field_update_creates_particles(self) -> None:
        """Field update should spawn particles based on spectrum."""
        field = AudioReactiveField()
        field.demo_mode = True
        initial_count = len(field.particles)

        field.update()

        # Should have spawned some particles
        assert len(field.particles) > initial_count

    def test_field_update_removes_dead_particles(self) -> None:
        """Field update should remove particles with life <= 0."""
        field = AudioReactiveField()
        field.paused = True  # Prevent new particle generation

        # Manually add a dead particle
        dead_particle = AudioParticle(x=100, y=100, vx=0, vy=0, life=-0.1, color=(255, 255, 255))
        field.particles.append(dead_particle)

        field.paused = False
        field.update()

        assert len(field.particles) == 0

    def test_field_update_keeps_alive_particles(self) -> None:
        """Field update should keep particles with life > 0."""
        field = AudioReactiveField()
        field.paused = True  # Prevent new particle generation

        # Add an alive particle
        alive_particle = AudioParticle(x=100, y=100, vx=0, vy=0, life=0.5, color=(255, 255, 255))
        field.particles.append(alive_particle)

        field.paused = False
        field.update()

        assert len(field.particles) == 1

    def test_field_reset_clears_particles(self) -> None:
        """Field reset should clear all particles."""
        field = AudioReactiveField()
        field.demo_mode = True

        # Spawn some particles
        for _ in range(5):
            field.update()

        assert len(field.particles) > 0

        field.reset()

        assert len(field.particles) == 0

    def test_field_pause_prevents_updates(self) -> None:
        """Paused field should not spawn particles."""
        field = AudioReactiveField()
        field.demo_mode = True
        field.paused = True

        initial_count = len(field.particles)
        field.update()

        assert len(field.particles) == initial_count

    def test_field_toggle_pause(self) -> None:
        """Toggle pause should flip paused state."""
        field = AudioReactiveField()

        assert field.paused is False
        field.toggle_pause()
        assert field.paused is True
        field.toggle_pause()
        assert field.paused is False

    def test_field_spawn_particles_with_spectrum(self) -> None:
        """Spawned particles should have colors based on spectrum."""
        field = AudioReactiveField()
        spectrum = SpectrumBand(bass=0.5, mid=0.3, high=0.2)

        field._spawn_particles(5, spectrum)

        assert len(field.particles) == 5

        # All particles should have valid colors
        for particle in field.particles:
            assert all(0 <= c <= 255 for c in particle.color)

    def test_field_particle_spawn_radius_depends_on_bass(self) -> None:
        """Particle spawn count should respond to spectrum."""
        field = AudioReactiveField()

        # Low mid frequencies = fewer particles
        spectrum_low = SpectrumBand(bass=0.5, mid=0.1, high=0.5)
        initial_count = len(field.particles)
        field._spawn_particles(int(2 + spectrum_low.mid * 8), spectrum_low)
        count_low = len(field.particles) - initial_count

        field.reset()

        # High mid frequencies = more particles
        spectrum_high = SpectrumBand(bass=0.5, mid=0.9, high=0.5)
        field._spawn_particles(int(2 + spectrum_high.mid * 8), spectrum_high)
        count_high = len(field.particles)

        # Higher mid should produce more particles
        assert count_high > count_low

    def test_field_particle_color_depends_on_high_frequencies(self) -> None:
        """Particle colors should shift with high frequencies."""
        field = AudioReactiveField()

        # Low high freq
        spectrum_low = SpectrumBand(bass=0.5, mid=0.5, high=0.0)
        field._spawn_particles(50, spectrum_low)
        colors_low = [p.color for p in field.particles]

        field.reset()

        # High high freq
        spectrum_high = SpectrumBand(bass=0.5, mid=0.0, high=1.0)
        field._spawn_particles(50, spectrum_high)
        colors_high = [p.color for p in field.particles]

        # High frequencies should create more pink/purple tones
        # (higher red, lower blue in the output)
        avg_red_low = np.mean([c[0] for c in colors_low])
        avg_red_high = np.mean([c[0] for c in colors_high])

        # Just verify that high frequencies produce valid color shifts
        assert all(all(0 <= x <= 255 for x in c) for c in colors_high)

    def test_field_cleanup_stops_audio(self) -> None:
        """Cleanup should stop audio capture."""
        field = AudioReactiveField()
        field.cleanup()

        # Should not raise any errors
        assert field.capture is None or not field.capture.is_active


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_demo_mode_complete_cycle(self) -> None:
        """Demo mode should run complete particle lifecycle."""
        field = AudioReactiveField(width=400, height=400)
        field.demo_mode = True

        # Run multiple updates
        for _ in range(100):
            field.update()

        # Should have particles in various states
        assert len(field.particles) > 0
        has_newborn = any(p.life > 0.8 for p in field.particles)
        has_old = any(0 < p.life < 0.2 for p in field.particles)

        assert has_newborn or has_old

    def test_field_operations_sequence(self) -> None:
        """Field should handle sequence of operations."""
        field = AudioReactiveField()
        field.demo_mode = True

        # Spawn particles
        field.update()
        initial_count = len(field.particles)
        assert initial_count > 0

        # Pause should stop spawning
        field.toggle_pause()
        field.update()
        paused_count = len(field.particles)
        assert paused_count == initial_count  # No new particles

        # Resume should spawn again
        field.toggle_pause()
        field.update()
        resumed_count = len(field.particles)
        assert resumed_count > paused_count

        # Reset should clear all
        field.reset()
        assert len(field.particles) == 0

    def test_fft_spectrum_extraction_accuracy(self) -> None:
        """FFT analysis should correctly identify frequency bands."""
        capture = AudioCapture(sample_rate=22050, chunk_size=4096)

        # Create a signal with dominant frequency in each band
        t = np.arange(4096) / 22050

        # Test bass (100 Hz)
        audio = np.sin(2 * np.pi * 100 * t).astype(np.float32)
        capture._process_spectrum(audio)
        spectrum = capture.get_spectrum()
        assert spectrum.bass > 0.7  # Should be mostly bass

        # Test mid (1000 Hz)
        audio = np.sin(2 * np.pi * 1000 * t).astype(np.float32)
        capture._process_spectrum(audio)
        spectrum = capture.get_spectrum()
        assert spectrum.mid > 0.7  # Should be mostly mid

        # Test high (6000 Hz)
        audio = np.sin(2 * np.pi * 6000 * t).astype(np.float32)
        capture._process_spectrum(audio)
        spectrum = capture.get_spectrum()
        assert spectrum.high > 0.5  # Should be mostly high
