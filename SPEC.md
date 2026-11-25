# P-Arithmetic Formal Specification (`SPEC.md`)

**Version:** 0.1.0  
**Reference Paper:** Ilya Radkevich, *Physically Bounded Non-Associative Arithmetic ($\mathcal{P}$-Arithmetic): Replacing Actual Infinity with Relativistic and Planckian Constraints* (November 2026).

This document is a self-contained formal specification for developers and AI agents implementing, verifying, or porting $\mathcal{P}$-Arithmetic.

---

## 1. Domain and Axioms

Fix a discrete horizon parameter $N_{\max} \in \mathbb{Z}_{\ge 1}$. The carrier set is the finite discrete set:

$$\mathbb{P} = \{0, 1, 2, \dots, N_{\max}\}$$

1. **Discreteness ($\hbar$-Axiom):** Every value is an integer in $\mathbb{P}$ with indivisible minimal unit $1$. No values exist between $n$ and $n+1$; infinitesimals and continua are excluded.
2. **Horizon ($G$-Axiom):** $N_{\max} \in \mathbb{P}$ is a strict upper bound representing maximum distinguishable state or information capacity.
3. **Saturation ($c$-Axiom):** Addition is non-linear and asymptotically bounded by $N_{\max}$, analogous to relativistic velocity addition.

---

## 2. Core Operations

### 2.1 $\mathcal{P}$-Addition (`p_add`)

**Signature:** `p_add(a: int, b: int, n_max: int) -> int`  
**Preconditions:**
- $N_{\max} \in \mathbb{Z},\ N_{\max} \ge 1$
- $a, b \in \mathbb{Z},\ 0 \le a \le N_{\max},\ 0 \le b \le N_{\max}$

**Mathematical Definition (Eq. 1):**

$$a \oplus b = \left\lfloor \frac{a + b}{1 + \frac{a \cdot b}{N_{\max}^2}} \right\rfloor$$

**Exact Integer Implementation Requirement:**  
Implementations **MUST NOT** evaluate Eq. (1) with IEEE-754 floating-point division when $N_{\max}$ is large (e.g. $N_{\max} = 10^{120}$), as float rounding and overflow violate exactness. Use exact rational/integer floor division:

$$a \oplus b = \left\lfloor \frac{(a + b) \cdot N_{\max}^2}{N_{\max}^2 + a \cdot b} \right\rfloor$$

In Python (arbitrary-precision `int`):
```python
n_max_sq = n_max * n_max
result = ((a + b) * n_max_sq) // (n_max_sq + a * b)
```

**Invariants:**
- Closure: $0 \le a \oplus b \le N_{\max}$.
- Low-scale correspondence: For $a, b \ge 1$ with $a, b \ll N_{\max}$, $\frac{a+b}{1 + ab/N_{\max}^2}$ is strictly less than $a + b$ by $< 1$, so the floor yields $a \oplus b = a + b - 1$ (relative error $\to 0$ as $N_{\max} \to \infty$); when $a = 0$ or $b = 0$, $a \oplus b = a + b$ exactly.
- Horizon impenetrability: $N_{\max} \oplus b = N_{\max}$ for all $b \in \mathbb{P}$.

### 2.2 $\mathcal{P}$-Multiplication (`p_mul`)

**Signature:** `p_mul(a: int, b: int, n_max: int) -> int`  
**Preconditions:**
- $N_{\max} \in \mathbb{Z},\ N_{\max} \ge 1$
- $a \in \mathbb{Z},\ 0 \le a \le N_{\max}$
- $b \in \mathbb{Z},\ b \ge 0$ (repetition count)

**Mathematical Definition (Eq. 2):**

$$a \otimes b = \underbrace{a \oplus a \oplus \dots \oplus a}_{b \text{ times}}$$

**Boundary & Early-Termination Rules:**
- $a \otimes 0 = 0$
- $0 \otimes b = 0$
- $a \otimes 1 = a$
- For $b \ge 2$, evaluate left-associatively: $x_1 = a$, $x_{k} = x_{k-1} \oplus a$. If $x_k = x_{k-1}$ for any $k \le b$, the accumulator has reached saturation and $a \otimes b = x_k$ immediately in $O(k)$ steps without iterating to $b$.

### 2.3 Successor Operation (`p_succ`)

**Signature:** `p_succ(n: int, n_max: int) -> int`  
**Definition (Eq. 3):**

$$S(n) = n \oplus 1$$

**Quantum Saturation under Floor Quantization:**  
For all $N_{\max} \ge 1$ and every $n \in \{1, \dots, N_{\max}\}$:

$$n \le \frac{(n + 1) N_{\max}^2}{N_{\max}^2 + n} < n + 1$$

because $(n + 1) N_{\max}^2 - n(N_{\max}^2 + n) = N_{\max}^2 - n^2 \ge 0$ and $(n + 1)(N_{\max}^2 + n) - (n + 1) N_{\max}^2 = n(n + 1) > 0$.  
Consequently, under strict floor quantization $\lfloor \cdot \rfloor$, $S(0) = 1$ and $S(n) = n$ for **every** $n \ge 1$ (so $n_{\text{sat}} = 1$). *(Note: in a nearest-integer rounding variant, $S(n)$ continues advancing until $n^2 + n \ge \frac{1}{2}(N_{\max}^2 + n)$.)*

---

## 3. Algebraic Laws

| Property | Classical ($\mathbb{N}$) | $\mathcal{P}$-Arithmetic ($\mathbb{P}$) |
| :--- | :--- | :--- |
| **Commutativity** ($a \oplus b = b \oplus a$) | Preserved | **Preserved** (symmetric numerator & denominator) |
| **Identity** ($a \oplus 0 = a$) | Preserved | **Preserved** |
| **Associativity** ($(a \oplus b) \oplus c = a \oplus (b \oplus c)$) | Preserved | **Broken** at large scales due to floor quantization |
| **Cancellation** ($a \oplus c = b \oplus c \Rightarrow a = b$) | Preserved | **Broken** near $N_{\max}$ (horizon information loss) |
| **Induction** | Unbounded | **Local** (holds only while $S(n) \neq n$) |

---

## 4. Cosmological & Physical Toy Models (Section 5)

Without the floor function, repeated $\oplus$ converges to $\tanh$:

1. **Bounded Hubble's Law (Eq. 4):** Setting $N_{\max} = c$:
   $$v(d) = H \otimes d \approx \left\lfloor c \cdot \tanh\left(\frac{H \cdot d}{c}\right) \right\rfloor$$
   - Local regime ($H \cdot d \ll c$): $v(d) \approx H \cdot d$.
   - Horizon regime: $v(d) \to c$ asymptotically.

2. **Bounded Mass-Energy Equivalence (Eq. 5):** Setting $N_{\max} = E_{\max}$:
   $$E_{\text{total}} = k \otimes (mc^2) \approx \left\lfloor E_{\max} \cdot \tanh\left(\frac{k \cdot mc^2}{E_{\max}}\right) \right\rfloor$$
   - Everyday scale: $E = mc^2$.
   - Extreme density: sub-linear growth, forbidding infinite energy/density singularities.

3. **Discrete Cosmic Time (Section 5.3):**
   $$t_{\text{next}} = t \oplus 1$$
   Asymptotically approaches a finite computational freeze at $N_{\max} \oplus 1 = N_{\max}$.

---

## 5. Conformance Test Vectors

Any conforming implementation must satisfy all of the following exact outputs:

| Operation | Inputs $(a, b, N_{\max})$ | Expected Output | Notes |
| :--- | :--- | :--- | :--- |
| `p_add` | `(3, 4, 1000)` | `6` | Low-scale floor quantization ($\lfloor 6.9999\dots \rfloor = 6$) |
| `p_add` | `(100, 42, 100)` | `100` | Horizon impenetrability ($N_{\max} \oplus b = N_{\max}$) |
| `p_add` | `(99, 1, 100)` | `99` | Quantum saturation ($S(99) = 99$) |
| `p_add` | `(31, 47, 100)` | `68` | $\lfloor 78 \cdot 10000 / 11457 \rfloor = 68$ |
| `p_add` | `(68, 83, 100)` | `96` | $(31 \oplus 47) \oplus 83 = 96$ |
| `p_add` | `(47, 83, 100)` | `93` | $\lfloor 130 \cdot 10000 / 13901 \rfloor = 93$ |
| `p_add` | `(10**60, 10**60, 10**120)` | `1999999999999999999999999999999999999999999999999999999999999` | Exact integer precision ($2 \cdot 10^{60} - 1$) |
| `p_mul` | `(7, 0, 100)` | `0` | Zero repetition |
| `p_mul` | `(3, 4, 1000)` | `9` | Low-scale repeated $\mathcal{P}$-addition |
| `p_mul` | `(20, 1000, 100)` | `97` | Early saturation below $N_{\max} = 100$ |
