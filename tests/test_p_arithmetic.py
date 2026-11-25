"""Unit tests for P-Arithmetic."""

import json
from pathlib import Path
import unittest

from p_arithmetic import (
    associativity_defect,
    bounded_hubble,
    bounded_hubble_tanh,
    bounded_mass_energy,
    bounded_mass_energy_tanh,
    cosmic_time_step,
    p_add,
    p_mul,
    p_succ,
    saturation_threshold,
)


class TestPArithmeticCore(unittest.TestCase):
    def test_low_scale_floor_addition(self) -> None:
        n_max = 10_000
        # For a, b >= 1 with a, b << n_max, floor((a+b)/(1 + ab/N^2)) == a + b - 1.
        for a in range(1, 50, 7):
            for b in range(1, 50, 11):
                self.assertEqual(p_add(a, b, n_max), a + b - 1)

    def test_commutativity_and_identity(self) -> None:
        n_max = 100
        for a in range(0, n_max + 1, 5):
            self.assertEqual(p_add(a, 0, n_max), a)
            self.assertEqual(p_add(0, a, n_max), a)
            for b in range(0, n_max + 1, 7):
                self.assertEqual(p_add(a, b, n_max), p_add(b, a, n_max))

    def test_horizon_impenetrability(self) -> None:
        n_max = 100
        for b in range(0, n_max + 1):
            self.assertEqual(p_add(n_max, b, n_max), n_max)
            self.assertEqual(p_add(b, n_max, n_max), n_max)

    def test_quantum_saturation_threshold(self) -> None:
        for n_max in (1, 2, 10, 50, 100, 1000, 10**120):
            thresh = saturation_threshold(n_max)
            self.assertEqual(thresh, 1)
            self.assertEqual(p_succ(0, n_max), 1)
            self.assertEqual(p_succ(thresh, n_max), thresh)

    def test_non_associativity(self) -> None:
        n_max = 100
        a, b, c = 10, 50, 90
        left = p_add(p_add(a, b, n_max), c, n_max)
        right = p_add(a, p_add(b, c, n_max), n_max)
        self.assertNotEqual(left, right)
        self.assertEqual(associativity_defect(a, b, c, n_max), 1)

    def test_cancellation_breakdown(self) -> None:
        n_max = 100
        # Universal cancellation failure: 0 (+) c == 1 (+) c == c for all c >= 1.
        self.assertEqual(p_add(0, 50, n_max), p_add(1, 50, n_max))
        # Near-horizon cancellation failure: 98 (+) 50 == 99 (+) 50.
        self.assertEqual(p_add(98, 50, n_max), p_add(99, 50, n_max))

    def test_exact_integer_precision_at_cosmological_scale(self) -> None:
        n_max = 10**120
        a = 10**60
        b = 10**60
        self.assertEqual(p_add(a, b, n_max), 2 * 10**60 - 1)
        self.assertEqual(p_add(n_max, n_max, n_max), n_max)

    def test_p_mul(self) -> None:
        n_max = 100
        self.assertEqual(p_mul(7, 0, n_max), 0)
        self.assertEqual(p_mul(0, 50, n_max), 0)
        self.assertEqual(p_mul(1, 50, n_max), 1)
        self.assertEqual(p_mul(7, 1, n_max), 7)
        self.assertEqual(p_mul(n_max, 50, n_max), n_max)
        self.assertEqual(p_mul(3, 4, 1000), 9)
        self.assertLessEqual(p_mul(20, 1000, n_max), n_max)
        self.assertEqual(p_mul(20, 1000, n_max), 97)
        self.assertEqual(p_mul(20, 1000, n_max), p_mul(20, 10_000_000, n_max))
        with self.assertRaises(RuntimeError):
            p_mul(2, 10**9, 10**120, max_steps=100)

    def test_validation_errors(self) -> None:
        with self.assertRaises(ValueError):
            p_add(1, 1, 0)
        with self.assertRaises(ValueError):
            p_add(1, 1, -5)
        with self.assertRaises(TypeError):
            p_add(1, 1, True)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            p_add(1, 1, 10.0)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            p_add(-1, 1, 10)
        with self.assertRaises(ValueError):
            p_add(11, 1, 10)
        with self.assertRaises(TypeError):
            p_add(1.5, 1, 10)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            p_add(True, 1, 10)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            p_mul(2, -1, 10)
        with self.assertRaises(TypeError):
            p_mul(2, True, 10)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            saturation_threshold(0)
        with self.assertRaises(ValueError):
            bounded_hubble_tanh(-1, 5, 100)
        with self.assertRaises(ValueError):
            bounded_hubble_tanh(1, 5, 0)
        with self.assertRaises(ValueError):
            bounded_hubble_tanh(1, float("inf"), 100)
        with self.assertRaises(ValueError):
            bounded_mass_energy_tanh(1, float("nan"), 100)
        with self.assertRaises(TypeError):
            bounded_mass_energy_tanh(1.5, 5.0, 100)  # type: ignore[arg-type]

    def test_conformance_vectors_json(self) -> None:
        vectors_path = Path(__file__).resolve().parent / "test_vectors.json"
        data = json.loads(vectors_path.read_text(encoding="utf-8"))
        for row in data["p_add"]:
            self.assertEqual(p_add(row["a"], row["b"], row["n_max"]), row["expected"])
        for row in data["p_mul"]:
            self.assertEqual(p_mul(row["a"], row["b"], row["n_max"]), row["expected"])

    def test_minimal_associativity_threshold_n6(self) -> None:
        # Associative for all N_max <= 5; first break occurs at N_max = 6 on (2, 2, 4).
        for n_max in range(1, 6):
            for a in range(0, n_max + 1):
                for b in range(0, n_max + 1):
                    for c in range(0, n_max + 1):
                        self.assertEqual(associativity_defect(a, b, c, n_max), 0)
        self.assertGreater(associativity_defect(2, 2, 4, 6), 0)


class TestCosmologyModels(unittest.TestCase):
    def test_bounded_hubble(self) -> None:
        c = 1000
        self.assertEqual(bounded_hubble(2, 5, c), 6)
        v_far = bounded_hubble(10, 500, c)
        self.assertLessEqual(v_far, c)
        self.assertGreater(v_far, 900)
        # Strictly below c even for large finite arguments where float64 tanh rounds to 1.0
        self.assertEqual(bounded_hubble_tanh(10, 5000, c), c - 1)

    def test_bounded_hubble_tanh_huge_ints(self) -> None:
        # Ensure huge ints (>= 10^309) do not raise OverflowError in validation or ratio.
        val = bounded_hubble_tanh(10**400, 100, 10**400)
        self.assertEqual(val, 10**400 - 1)

    def test_bounded_mass_energy(self) -> None:
        e_max = 1000
        self.assertEqual(bounded_mass_energy(3, 5, e_max), 13)
        e_dense = bounded_mass_energy(500, 10, e_max)
        self.assertLessEqual(e_dense, e_max)
        self.assertEqual(bounded_mass_energy_tanh(5000, 10, e_max), e_max - 1)

    def test_cosmic_time_freeze(self) -> None:
        t_max = 100
        # Under strict floor quantization: 0 (+) 1 == 1, and t (+) 1 == t for all t >= 1.
        self.assertEqual(cosmic_time_step(0, t_max), 1)
        self.assertEqual(cosmic_time_step(1, t_max), 1)
        self.assertEqual(cosmic_time_step(t_max, t_max), t_max)


if __name__ == "__main__":
    unittest.main()
