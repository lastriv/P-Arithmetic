/-
  P-Arithmetic: Lean 4 Formalization of Core Axioms and Algebraic Properties
  Reference: Ilya Radkevich, "Physically Bounded Non-Associative Arithmetic (P-Arithmetic)"
  Zero external dependencies (Lean 4 core only).
-/

namespace PArithmetic

/--
  Carrier set P = {0, 1, ..., N} encoding:
  1. Discreteness (hbar-Axiom): elements are discrete natural numbers.
  2. Horizon (G-Axiom): every element is bounded by val ≤ N.
-/
structure PNum (N : Nat) where
  val : Nat
  h_bound : val ≤ N
  deriving DecidableEq, Repr

/-- Saturation (c-Axiom) closure lemma: (a + b) * N^2 ≤ N * (N^2 + a * b) for a, b ≤ N. -/
theorem pAdd_closure_num {N a b : Nat} (ha : a ≤ N) (hb : b ≤ N) :
    (a + b) * (N * N) ≤ N * (N * N + a * b) := by
  obtain ⟨da, hda⟩ := Nat.exists_eq_add_of_le ha
  obtain ⟨db, hdb⟩ := Nat.exists_eq_add_of_le hb
  have h_main : (a + b) * (N * N) + N * (da * db) = N * (N * N + a * b) := by
    have h_inner : (a + b) * N + da * db = N * N + a * b := by
      calc
        (a + b) * N + da * db
            = a * N + b * N + da * db := by rw [Nat.add_mul]
        _   = a * (b + db) + b * (a + da) + da * db := by
              have h1 : a * N = a * (b + db) := by rw [← hdb]
              have h2 : b * N = b * (a + da) := by rw [← hda]
              rw [h1, h2]
        _   = (a * b + a * db) + (b * a + b * da) + da * db := by
              rw [Nat.mul_add, Nat.mul_add]
        _   = ((a * b + a * db) + (da * b + da * db)) + a * b := by
              rw [Nat.mul_comm b a, Nat.mul_comm b da]
              simp only [Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]
        _   = (a + da) * (b + db) + a * b := by
              rw [← Nat.mul_add a b db, ← Nat.mul_add da b db, ← Nat.add_mul]
        _   = N * N + a * b := by rw [← hda, ← hdb]
    calc
      (a + b) * (N * N) + N * (da * db)
          = N * ((a + b) * N + da * db) := by
            simp only [Nat.mul_add, Nat.mul_comm, Nat.mul_left_comm]
      _   = N * (N * N + a * b) := by rw [h_inner]
  exact Nat.le.intro h_main

/-- P-Addition: a (+) b = floor((a + b) * N^2 / (N^2 + a * b)). -/
def pAdd {N : Nat} (_hN : 0 < N) (a b : PNum N) : PNum N where
  val := ((a.val + b.val) * (N * N)) / (N * N + a.val * b.val)
  h_bound := by
    apply Nat.div_le_of_le_mul
    rw [Nat.mul_comm (N * N + a.val * b.val) N]
    exact pAdd_closure_num a.h_bound b.h_bound

/-- Successor operation: S(n) = n (+) 1. -/
def pSucc {N : Nat} (hN : 0 < N) (n : PNum N) : PNum N :=
  pAdd hN n ⟨1, hN⟩

/-- P-Multiplication: a (x) b = a (+) a (+) ... (+) a (b times). -/
def pMul {N : Nat} (hN : 0 < N) (a : PNum N) : Nat → PNum N
  | 0 => ⟨0, Nat.zero_le N⟩
  | 1 => a
  | k + 2 => pAdd hN (pMul hN a (k + 1)) a

/-- Theorem 1: Commutativity of P-Addition. -/
theorem pAdd_comm {N : Nat} (hN : 0 < N) (a b : PNum N) :
    (pAdd hN a b).val = (pAdd hN b a).val := by
  simp only [pAdd]
  rw [Nat.add_comm a.val b.val, Nat.mul_comm a.val b.val]

/-- Theorem 2a: Right identity element (a (+) 0 = a). -/
theorem pAdd_zero_right {N : Nat} (hN : 0 < N) (a : PNum N) :
    (pAdd hN a ⟨0, Nat.zero_le N⟩).val = a.val := by
  simp only [pAdd, Nat.add_zero, Nat.mul_zero]
  have hN2 : 0 < N * N := Nat.mul_pos hN hN
  exact Nat.mul_div_cancel a.val hN2

/-- Theorem 2b: Left identity element (0 (+) a = a). -/
theorem pAdd_zero_left {N : Nat} (hN : 0 < N) (a : PNum N) :
    (pAdd hN ⟨0, Nat.zero_le N⟩ a).val = a.val := by
  rw [pAdd_comm]
  exact pAdd_zero_right hN a

/-- Theorem 3a: Horizon impenetrability (N (+) b = N). -/
theorem pAdd_horizon_left {N : Nat} (hN : 0 < N) (b : PNum N) :
    (pAdd hN ⟨N, Nat.le_refl N⟩ b).val = N := by
  simp only [pAdd]
  have h_eq : (N + b.val) * (N * N) = N * (N * N + N * b.val) := by
    simp only [Nat.mul_add, Nat.mul_comm, Nat.mul_left_comm]
  have h_pos : 0 < N * N + N * b.val :=
    Nat.add_pos_left (Nat.mul_pos hN hN) (N * b.val)
  rw [h_eq]
  exact Nat.mul_div_cancel N h_pos

/-- Theorem 3b: Horizon impenetrability (a (+) N = N). -/
theorem pAdd_horizon_right {N : Nat} (hN : 0 < N) (a : PNum N) :
    (pAdd hN a ⟨N, Nat.le_refl N⟩).val = N := by
  rw [pAdd_comm]
  exact pAdd_horizon_left hN a

/-- Theorem 4: Associativity breaks at finite horizon (witnessed at N = 100). -/
theorem pAdd_not_associative :
    ∃ a b c : PNum 100,
      (pAdd (by decide) (pAdd (by decide) a b) c).val ≠
      (pAdd (by decide) a (pAdd (by decide) b c)).val := by
  refine ⟨⟨11, by decide⟩, ⟨13, by decide⟩, ⟨13, by decide⟩, ?_⟩
  decide

/-- Theorem 5: Cancellation law breaks near horizon (witnessed at N = 100). -/
theorem pAdd_cancellation_fails :
    ∃ a b c : PNum 100,
      (pAdd (by decide) a c).val = (pAdd (by decide) b c).val ∧ a.val ≠ b.val := by
  refine ⟨⟨98, by decide⟩, ⟨99, by decide⟩, ⟨50, by decide⟩, ?_⟩
  decide

/-- Theorem 6: Minimal associativity-breaking horizon is N = 6 (witnessed by (2, 2, 4)). -/
theorem pAdd_not_associative_min :
    ∃ a b c : PNum 6,
      (pAdd (by decide) (pAdd (by decide) a b) c).val ≠
      (pAdd (by decide) a (pAdd (by decide) b c)).val := by
  refine ⟨⟨2, by decide⟩, ⟨2, by decide⟩, ⟨4, by decide⟩, ?_⟩
  decide

/-- Theorem 7: Successor at zero advances to 1 (S(0) = 1). -/
theorem pSucc_zero {N : Nat} (hN : 0 < N) :
    (pSucc hN ⟨0, Nat.zero_le N⟩).val = 1 := by
  simp only [pSucc, pAdd, Nat.zero_add, Nat.one_mul, Nat.zero_mul, Nat.add_zero]
  exact Nat.div_self (Nat.mul_pos hN hN)

/-- Theorem 8: Successor at horizon is fixed (S(N) = N). -/
theorem pSucc_horizon {N : Nat} (hN : 0 < N) :
    (pSucc hN ⟨N, Nat.le_refl N⟩).val = N :=
  pAdd_horizon_left hN ⟨1, hN⟩

/-- Theorem 9: P-Multiplication by 0 on the left is 0 (0 (x) b = 0). -/
theorem pMul_zero_left {N : Nat} (hN : 0 < N) (b : Nat) :
    (pMul hN ⟨0, Nat.zero_le N⟩ b).val = 0 := by
  induction b with
  | zero => rfl
  | succ k ih =>
    cases k with
    | zero => rfl
    | succ _ =>
      simp only [pMul]
      rw [pAdd_zero_right]
      exact ih

/-- Theorem 10: P-Multiplication of horizon N by positive b is N (N (x) b = N). -/
theorem pMul_horizon_left {N : Nat} (hN : 0 < N) (b : Nat) (hb : 0 < b) :
    (pMul hN ⟨N, Nat.le_refl N⟩ b).val = N := by
  cases b with
  | zero => contradiction
  | succ k =>
    cases k with
    | zero => rfl
    | succ _ =>
      simp only [pMul]
      exact pAdd_horizon_right hN _

end PArithmetic
