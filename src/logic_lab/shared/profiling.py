"""Performance profiling utilities for Logic Lab sketches.

Provides decorators and context managers for tracking FPS, frame time, and memory usage.
"""

import functools
import time
from collections.abc import Callable
from contextlib import contextmanager
from typing import Any, Optional

import py5


class PerformanceMonitor:
    """Track FPS, frame time, and memory usage statistics."""

    def __init__(self, window_size: int = 60):
        self.window_size = window_size
        self.frame_times: list[float] = []
        self.start_time = time.perf_counter()
        self.frame_count = 0
        self._last_print_time = time.perf_counter()

    def record_frame(self, frame_time: float) -> None:
        """Record a frame time sample."""
        self.frame_times.append(frame_time)
        if len(self.frame_times) > self.window_size:
            self.frame_times.pop(0)
        self.frame_count += 1

    @property
    def fps(self) -> float:
        """Calculate current FPS from recent frames."""
        if not self.frame_times or len(self.frame_times) < 2:
            return 0.0
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        return 1.0 / avg_frame_time if avg_frame_time > 0 else 0.0

    @property
    def avg_frame_time_ms(self) -> float:
        """Average frame time in milliseconds."""
        if not self.frame_times:
            return 0.0
        return (sum(self.frame_times) / len(self.frame_times)) * 1000

    @property
    def max_frame_time_ms(self) -> float:
        """Maximum frame time in recent window (ms)."""
        return max(self.frame_times) * 1000 if self.frame_times else 0.0

    @property
    def min_frame_time_ms(self) -> float:
        """Minimum frame time in recent window (ms)."""
        return min(self.frame_times) * 1000 if self.frame_times else 0.0

    def elapsed_seconds(self) -> float:
        """Total elapsed time since creation."""
        return time.perf_counter() - self.start_time

    def print_stats(self, interval_seconds: float = 5.0) -> None:
        """Print stats periodically (not every frame)."""
        now = time.perf_counter()
        if now - self._last_print_time >= interval_seconds:
            print(
                f"FPS: {self.fps:.1f} | "
                f"Avg: {self.avg_frame_time_ms:.1f}ms | "
                f"Min/Max: {self.min_frame_time_ms:.1f}/{self.max_frame_time_ms:.1f}ms | "
                f"Frames: {self.frame_count}"
            )
            self._last_print_time = now


def profile_decorator(monitor: PerformanceMonitor | None = None) -> Callable:
    """Decorator to automatically track frame time in a function.

    Args:
        monitor: PerformanceMonitor instance to use. Creates new one if None.
    """

    def decorator(func: Callable) -> Callable:
        nonlocal monitor
        if monitor is None:
            monitor = PerformanceMonitor()

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            monitor.record_frame(elapsed)
            return result

        wrapper.monitor = monitor  # type: ignore
        return wrapper

    return decorator


@contextmanager
def profile_section(label: str = "Section"):
    """Context manager to profile a code section."""
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = (time.perf_counter() - start) * 1000
        print(f"[{label}] {elapsed:.2f}ms")


def overlay_fps(
    monitor: PerformanceMonitor,
    x: int = 10,
    y: int = 20,
    text_size: int = 12,
    color: tuple[int, int, int] = (255, 255, 255),
) -> None:
    """Draw FPS overlay on canvas.

    Call this in your draw() function to show real-time stats.
    """
    py5.fill(*color)
    py5.text_size(text_size)
    py5.text(f"FPS: {monitor.fps:.1f}", x, y)
    py5.text(f"Frame: {monitor.avg_frame_time_ms:.1f}ms", x, y + 20)
