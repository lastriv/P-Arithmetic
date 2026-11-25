"""Physically Bounded Non-Associative Arithmetic (P-Arithmetic).

Zero-dependency reference implementation of P-Arithmetic operations
(p_add, p_mul, p_succ) and cosmological toy models (bounded Hubble's Law,
bounded mass-energy equivalence, discrete cosmic time).
"""

from __future__ import annotations

import math

__all__ = [
    "p_add",
    "p_mul",
    "p_succ",
    "associativity_defect",
    "saturation_threshold",
    "bounded_hubble",
    "bounded_hubble_tanh",
    "bounded_mass_energy",
    "bounded_mass_energy_tanh",
    "cosmic_time_step",
]

__version__ = "0.1.0"


def _validate_horizon(n_max: int) -> None:
    """Validate that n_max is a positive integer >= 1."""
    if isinstance(n_max, bool) or not isinstance(n_max, int) or n_max < 1:
        raise ValueError(f"n_max must be a positive integer >= 1, got {n_max!r}")


def _validate_operand(x: int, n_max: int, name: str = "operand") -> None:
    """Validate that an operand belongs to P = {0, 1, ..., n_max}."""
    if isinstance(x, bool) or not isinstance(x, int):
        raise TypeError(f"{name} must be an int, got {type(x).__name__}")
    if x < 0 or x > n_max:
        raise ValueError(f"{name} must satisfy 0 <= {name} <= {n_max}, got {x}")


def p_add(a: int, b: int, n_max: int) -> int:
    """Compute P-addition: a (+) b = floor((a + b) / (1 + (a * b) / n_max^2)).

    Uses exact arbitrary-precision integer arithmetic so there is no
    floating-point rounding error even at cosmological scales (e.g. n_max = 10^120).
    """
    _validate_horizon(n_max)
    _validate_operand(a, n_max, "a")
    _validate_operand(b, n_max, "b")

    n_max_sq = n_max * n_max
    return ((a + b) * n_max_sq) // (n_max_sq + a * b)


def p_mul(a: int, b: int, n_max: int) -> int:
    """Compute P-multiplication: a (x) b = a (+) a (+) ... (+) a (b times).

    By convention, a (x) 0 = 0 and a (x) 1 = a.
    Stops early if the accumulator saturates (acc (+) a == acc).
    """
    _validate_horizon(n_max)
    _validate_operand(a, n_max, "a")
    if isinstance(b, bool) or not isinstance(b, int) or b < 0:
        raise ValueError(f"b (repetition count) must be a non-negative integer, got {b!r}")

    if b == 0 or a == 0:
        return 0
    if b == 1:
        return a

    acc = a
    for _ in range(b - 1):
        nxt = p_add(acc, a, n_max)
        if nxt == acc:
            break
        acc = nxt
    return acc


def p_succ(n: int, n_max: int) -> int:
    """Compute the P-Arithmetic successor S(n) = n (+) 1."""
    return p_add(n, 1, n_max)


def associativity_defect(a: int, b: int, c: int, n_max: int) -> int:
    """Return |(a (+) b) (+) c - a (+) (b (+) c)|."""
    left = p_add(p_add(a, b, n_max), c, n_max)
    right = p_add(a, p_add(b, c, n_max), n_max)
    return abs(left - right)


def saturation_threshold(n_max: int) -> int:
    """Return the smallest n in P where S(n) = n (+) 1 = n (quantum saturation).

    Under floor quantization, for all 1 <= n <= n_max:
        n <= (n + 1) * n_max^2 / (n_max^2 + n) < n + 1,
    so S(0) = 1 and S(n) = n for every n >= 1.
    """
    _validate_horizon(n_max)
    return 1


def _validate_nonneg_finite(x: float, name: str) -> None:
    """Validate that a continuous parameter is finite and non-negative."""
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        raise TypeError(f"{name} must be a real number, got {type(x).__name__}")
    if not math.isfinite(x) or x < 0:
        raise ValueError(f"{name} must be finite and >= 0, got {x!r}")


def bounded_hubble(hubble_param: int, distance: int, c_horizon: int) -> int:
    """Exact discrete bounded Hubble's Law: v(d) = H (x) d with N_max = c_horizon."""
    return p_mul(hubble_param, distance, c_horizon)


def bounded_hubble_tanh(hubble_param: float, distance: float, c_horizon: float) -> int:
    """Continuous tanh approximation from Eq. (4): floor(c * tanh(H * d / c))."""
    _validate_nonneg_finite(hubble_param, "hubble_param")
    _validate_nonneg_finite(distance, "distance")
    _validate_nonneg_finite(c_horizon, "c_horizon")
    if c_horizon <= 0:
        raise ValueError("c_horizon must be positive")
    return math.floor(c_horizon * math.tanh((hubble_param * distance) / c_horizon))


def bounded_mass_energy(k: int, rest_energy: int, e_max: int) -> int:
    """Exact discrete bounded mass-energy: E_total = k (x) (m*c^2) with horizon E_max."""
    return p_mul(rest_energy, k, e_max)


def bounded_mass_energy_tanh(k: int, rest_energy: float, e_max: float) -> int:
    """Continuous tanh approximation from Eq. (5): floor(E_max * tanh(k * m*c^2 / E_max))."""
    _validate_nonneg_finite(k, "k")
    _validate_nonneg_finite(rest_energy, "rest_energy")
    _validate_nonneg_finite(e_max, "e_max")
    if e_max <= 0:
        raise ValueError("e_max must be positive")
    return math.floor(e_max * math.tanh((k * rest_energy) / e_max))


def cosmic_time_step(t: int, t_max: int) -> int:
    """Discrete cosmic time evolution: t_next = t (+) 1 (Section 5.3)."""
    return p_add(t, 1, t_max)
