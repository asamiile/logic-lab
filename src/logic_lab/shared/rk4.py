"""4th-order Runge-Kutta integrator.

More accurate than forward-Euler for ODE systems — per-step truncation
error drops from O(dt²) to O(dt⁵), keeping chaotic trajectories on
their true attractor for longer and reducing numerical drift.

Example::

    from logic_lab.shared.rk4 import rk4_step

    def lorenz(t, state):
        x, y, z = state
        return [10*(y - x), x*(28 - z) - y, x*y - (8/3)*z]

    state = [1.0, 0.0, 0.0]
    for _ in range(1000):
        state = rk4_step(lorenz, 0.0, state, dt=0.005)
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

Vec = list[float]
DerivFn = Callable[[float, Sequence[float]], Sequence[float]]


def rk4_step(f: DerivFn, t: float, y: Sequence[float], dt: float) -> Vec:
    """Advance state vector *y* by one RK4 step of size *dt*.

    Args:
        f:  Derivative function ``f(t, y) -> dy/dt``.
            Autonomous systems may ignore *t*.
        t:  Current time (passed through to *f*).
        y:  Current state as any sequence of floats.
        dt: Time step.

    Returns:
        New state as ``list[float]``.
    """
    k1 = list(f(t, y))
    k2 = list(f(t + dt * 0.5, [yi + ki * dt * 0.5 for yi, ki in zip(y, k1)]))
    k3 = list(f(t + dt * 0.5, [yi + ki * dt * 0.5 for yi, ki in zip(y, k2)]))
    k4 = list(f(t + dt, [yi + ki * dt for yi, ki in zip(y, k3)]))
    return [
        yi + dt * (k1i + 2.0 * k2i + 2.0 * k3i + k4i) / 6.0
        for yi, k1i, k2i, k3i, k4i in zip(y, k1, k2, k3, k4)
    ]
