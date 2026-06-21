import Mathlib

set_option linter.style.header false
set_option linter.style.longLine false

/-!
# The generalized Erdős–Straus conjecture `5/a = 1/b + 1/c + 1/d`, machine-verified

A `sorry`-free reproduction of B. Ghermoul, *Almost a Complete Proof of the Generalized
Erdős–Straus Conjecture: 5/a = 1/b + 1/c + 1/d* (arXiv:2508.07367v1, 2025).

The generalized Erdős–Straus conjecture (Sierpiński 1956, attributed to Schinzel) asserts that for
every integer `a ≥ 2`, `5/a = 1/b + 1/c + 1/d` in positive integers.  Ghermoul proves it
**unconditionally for every `a ≢ 1 (mod 5)`**, reduces the remaining class `a = 5q+1` to a single
polynomial-surjectivity statement (Conjecture 2), proves that reduction for every `q ≢ 0 (mod 252)`
by explicit decomposition families, and verifies the residual `q ≡ 0 (mod 252)` computationally to
`≈ 2·10¹⁰`.  Hence the title: *almost* a complete proof — the gap is exactly Conjecture 2.

What is formalised here, with **no `sorry`** (every theorem reduces to `propext, Classical.choice,
Quot.sound`):

* **`esc5_of_cross`** — the workhorse: a subtraction-free natural-number cross-multiplication
  `5·bcd = a·(cd+bd+bc)` upgrades to the rational decomposition `5/a = 1/b+1/c+1/d`.  Every
  decomposition below is one `ring` identity through this lemma.

* **`gesc_master_identity`** — the engine (Ghermoul eq. (14)): the `(r,t)=(5,1)` parametric
  identity behind every family.

* **`gesc_easy`** — *unconditional*: `2 ≤ a → a % 5 ≠ 1 → ESC5 a` (Lemma 2.2 / Theorem 2.1(1), the
  four residue families `a = 5k, 5k+2, 5k+3, 5k+4`).

* **Theorem 2.1(2),(3),(4)** — the `a = 5q+1`, `q ≢ 0 (mod 252)` families: the eleven `q (mod 12)`
  decompositions (18)–(33), the six `u (mod 7)` decompositions (34)–(39), and the two `v (mod 3)`
  decompositions (40)–(41), each as an explicit `ESC5 (5q+1)`.  (Eq. (35) as printed in the paper is
  a copy-paste typo of (34); the corrected form — the general `p₄` decomposition at `y=1` — is used,
  see `gesc_u2mod7`.  Cross-checked symbolically in `analysis/verify_ghermoul.py`.)

* **`Conjecture2`** — the open part, stated exactly (the polynomial `p₁` hits every multiple of
  `252`), together with **`bridge_pos`** (Ghermoul eq. (17): `p₁` always yields a decomposition) and
  **`residual_of_conjecture2`** (Conjecture 2 closes `q ≡ 0 (mod 252)`).

* **`generalized_esc_5`** — the headline, the paper's *almost*-complete proof made a theorem:
  `Conjecture2 → ∀ a ≥ 2, ESC5 a`.

Companion symbolic cross-check: `analysis/verify_ghermoul.py`.
-/

namespace GeneralizedErdosStraus

/-- `ESC5 a` : `5/a` is a sum of three **positive** unit fractions (the generalized Erdős–Straus
property for numerator `5`). -/
def ESC5 (a : ℕ) : Prop :=
  ∃ b c d : ℕ, 0 < b ∧ 0 < c ∧ 0 < d ∧ (5 : ℚ) / a = 1 / b + 1 / c + 1 / d

/-- **The workhorse.** A positive-denominator cross-multiplication identity `5·(bcd) = a·(cd+bd+bc)`
yields the rational decomposition `5/a = 1/b + 1/c + 1/d`.  Every explicit family below is this lemma
applied to a `ring` identity in the residue parameter. -/
theorem esc5_of_cross (a b c d : ℕ) (ha : 0 < a) (hb : 0 < b) (hc : 0 < c) (hd : 0 < d)
    (h : 5 * (b * c * d) = a * (c * d + b * d + b * c)) :
    (5 : ℚ) / a = 1 / b + 1 / c + 1 / d := by
  have haq : (a : ℚ) ≠ 0 := Nat.cast_ne_zero.mpr ha.ne'
  have hbq : (b : ℚ) ≠ 0 := Nat.cast_ne_zero.mpr hb.ne'
  have hcq : (c : ℚ) ≠ 0 := Nat.cast_ne_zero.mpr hc.ne'
  have hdq : (d : ℚ) ≠ 0 := Nat.cast_ne_zero.mpr hd.ne'
  have hkey : (5 : ℚ) * (b * c * d) = a * (c * d + b * d + b * c) := by exact_mod_cast h
  field_simp
  ring_nf
  ring_nf at hkey
  linarith [hkey]

/-! ## The engine — Ghermoul's master parametric identity (eq. (14)) -/

/-- **The master identity (Ghermoul eq. (14)), machine-verified.** The fully substituted
`(r,t) = (5,1)` decomposition: writing `q = κz − s` and `c = κ(5z+1)/(5s−1)`, one has, as a rational
identity, `5/(5(κz−s)+1) = 1/(κz(c−1)) + 1/(z(c−1)(5(κz−s)+1)) + 1/(κz)`.  This is the algebraic
engine specialised by every `a = 5q+1` family; its integrality side-conditions (`c ∈ ℕ`, etc.) are
what each `Cᵢ`/`p_i` choice arranges. -/
theorem gesc_master_identity (κ z s c : ℚ) (hz : z ≠ 0) (hκ : κ ≠ 0) (hc1 : c - 1 ≠ 0)
    (hA : 5 * (κ * z - s) + 1 ≠ 0) (hcdef : c * (5 * s - 1) = κ * (5 * z + 1)) :
    5 / (5 * (κ * z - s) + 1)
      = 1 / (κ * z * (c - 1)) + 1 / (z * (c - 1) * (5 * (κ * z - s) + 1)) + 1 / (κ * z) := by
  field_simp
  linear_combination hcdef

/-! ## Theorem 2.1(1) / Lemma 2.2 — unconditional for `a ≢ 1 (mod 5)`

The four residue families.  Each is `esc5_of_cross` applied to a `ring` identity; positivity is
free because every denominator is a subtraction-free polynomial with positive constant term. -/

/-- `a = 5k` (Lemma 2.2 (2.1)). -/
theorem esc5_5k (k : ℕ) (hk : 0 < k) : ESC5 (5 * k) :=
  ⟨(k + 1) ^ 2, k * (k + 1) ^ 2, k + 1,
   by positivity, Nat.mul_pos hk (by positivity), by positivity,
   esc5_of_cross _ _ _ _ (by omega) (by positivity) (Nat.mul_pos hk (by positivity))
     (by positivity) (by ring)⟩

/-- `a = 5(2q)+2` (Lemma 2.2 (2.2), even case). -/
theorem esc5_5k2_even (q : ℕ) : ESC5 (5 * (2 * q) + 2) :=
  ⟨10 * q ^ 2 + 7 * q + 1, 20 * q ^ 2 + 14 * q + 2, 2 * q + 1,
   by positivity, by positivity, by positivity,
   esc5_of_cross _ _ _ _ (by positivity) (by positivity) (by positivity) (by positivity) (by ring)⟩

/-- `a = 5(2q+1)+2` (Lemma 2.2 (2.2), odd case). -/
theorem esc5_5k2_odd (q : ℕ) : ESC5 (5 * (2 * q + 1) + 2) :=
  ⟨10 * q ^ 2 + 17 * q + 7, 20 * q ^ 2 + 34 * q + 14, 2 * q + 2,
   by positivity, by positivity, by positivity,
   esc5_of_cross _ _ _ _ (by positivity) (by positivity) (by positivity) (by positivity) (by ring)⟩

/-- `a = 5k+3` (Lemma 2.2 (2.3)). -/
theorem esc5_5k3 (k : ℕ) : ESC5 (5 * k + 3) :=
  ⟨5 * k ^ 2 + 8 * k + 3, 5 * k ^ 2 + 8 * k + 3, k + 1,
   by positivity, by positivity, by positivity,
   esc5_of_cross _ _ _ _ (by positivity) (by positivity) (by positivity) (by positivity) (by ring)⟩

/-- `a = 5k+4` (Lemma 2.2 (2.4)). -/
theorem esc5_5k4 (k : ℕ) : ESC5 (5 * k + 4) :=
  ⟨5 * (k + 1) ^ 2 * (5 * k + 4), 5 * (k + 1) ^ 2, k + 1,
   by positivity, by positivity, by positivity,
   esc5_of_cross _ _ _ _ (by positivity) (by positivity) (by positivity) (by positivity) (by ring)⟩

/-- **Theorem 2.1(1), assembled (machine-verified, unconditional).** The generalized Erdős–Straus
conjecture for numerator `5` holds for *every* `a ≥ 2` with `a ≢ 1 (mod 5)`. -/
theorem gesc_easy (a : ℕ) (ha : 2 ≤ a) (h : a % 5 ≠ 1) : ESC5 a := by
  rcases (by omega : a % 5 = 0 ∨ a % 5 = 2 ∨ a % 5 = 3 ∨ a % 5 = 4) with h0 | h2 | h3 | h4
  · obtain ⟨k, rfl⟩ : ∃ k, a = 5 * k := ⟨a / 5, by omega⟩
    exact esc5_5k k (by omega)
  · obtain ⟨k, rfl⟩ : ∃ k, a = 5 * k + 2 := ⟨a / 5, by omega⟩
    rcases (by omega : k % 2 = 0 ∨ k % 2 = 1) with he | ho
    · obtain ⟨q, rfl⟩ : ∃ q, k = 2 * q := ⟨k / 2, by omega⟩; exact esc5_5k2_even q
    · obtain ⟨q, rfl⟩ : ∃ q, k = 2 * q + 1 := ⟨k / 2, by omega⟩; exact esc5_5k2_odd q
  · obtain ⟨k, rfl⟩ : ∃ k, a = 5 * k + 3 := ⟨a / 5, by omega⟩; exact esc5_5k3 k
  · obtain ⟨k, rfl⟩ : ∃ k, a = 5 * k + 4 := ⟨a / 5, by omega⟩; exact esc5_5k4 k

/-! ## Theorem 2.1(2) — `a = 5q+1`, `q ≢ 0 (mod 12)` : the eleven `q (mod 12)` families (18)–(33) -/

/-- `q ≡ 1 (mod 12)` — eq. (28). -/
theorem gesc_q1mod12 (q : ℕ) (h : q % 12 = 1) : ESC5 (5 * q + 1) := by
  obtain ⟨x, rfl⟩ : ∃ x, q = 1 + 12 * x := ⟨q / 12, by omega⟩
  exact ⟨6 + 60 * x, 3 + 30 * x, 3 + 30 * x, by positivity, by positivity, by positivity,
    esc5_of_cross _ _ _ _ (by positivity) (by positivity) (by positivity) (by positivity) (by ring)⟩

/-- `q ≡ 2 (mod 12)` — eq. (18). -/
theorem gesc_q2mod12 (q : ℕ) (h : q % 12 = 2) : ESC5 (5 * q + 1) := by
  obtain ⟨x, rfl⟩ : ∃ x, q = 2 + 12 * x := ⟨q / 12, by omega⟩
  exact ⟨3 * (1 + 4 * x) * (3 + 16 * x), 3 * (3 + 16 * x) * (11 + 60 * x), 3 * (1 + 4 * x),
    by positivity, by positivity, by positivity,
    esc5_of_cross _ _ _ _ (by positivity) (by positivity) (by positivity) (by positivity) (by ring)⟩

/-- `q ≡ 3 (mod 12)` — eq. (30). -/
theorem gesc_q3mod12 (q : ℕ) (h : q % 12 = 3) : ESC5 (5 * q + 1) := by
  obtain ⟨x, rfl⟩ : ∃ x, q = 3 + 12 * x := ⟨q / 12, by omega⟩
  exact ⟨16 + 60 * x, 8 + 30 * x, 8 + 30 * x, by positivity, by positivity, by positivity,
    esc5_of_cross _ _ _ _ (by positivity) (by positivity) (by positivity) (by positivity) (by ring)⟩

/-- `q ≡ 4 (mod 12)` — eq. (32). -/
theorem gesc_q4mod12 (q : ℕ) (h : q % 12 = 4) : ESC5 (5 * q + 1) := by
  obtain ⟨x, rfl⟩ : ∃ x, q = 4 + 12 * x := ⟨q / 12, by omega⟩
  exact ⟨6 * (7 + 20 * x), 14 + 40 * x, 7 + 20 * x, by positivity, by positivity, by positivity,
    esc5_of_cross _ _ _ _ (by positivity) (by positivity) (by positivity) (by positivity) (by ring)⟩

/-- `q ≡ 5 (mod 12)` — eq. (19). -/
theorem gesc_q5mod12 (q : ℕ) (h : q % 12 = 5) : ESC5 (5 * q + 1) := by
  obtain ⟨x, rfl⟩ : ∃ x, q = 5 + 12 * x := ⟨q / 12, by omega⟩
  exact ⟨6 * (1 + 2 * x) * (7 + 16 * x), 6 * (7 + 16 * x) * (13 + 30 * x), 3 * (2 + 4 * x),
    by positivity, by positivity, by positivity,
    esc5_of_cross _ _ _ _ (by positivity) (by positivity) (by positivity) (by positivity) (by ring)⟩

/-- `q ≡ 6 (mod 12)` — eq. (21). -/
theorem gesc_q6mod12 (q : ℕ) (h : q % 12 = 6) : ESC5 (5 * q + 1) := by
  obtain ⟨x, rfl⟩ : ∃ x, q = 6 + 12 * x := ⟨q / 12, by omega⟩
  exact ⟨(7 + 12 * x) * (8 + 15 * x), (7 + 12 * x) * (8 + 15 * x) * (31 + 60 * x), 7 + 12 * x,
    by positivity, by positivity, by positivity,
    esc5_of_cross _ _ _ _ (by positivity) (by positivity) (by positivity) (by positivity) (by ring)⟩

/-- `q ≡ 7 (mod 12)` — eq. (33). -/
theorem gesc_q7mod12 (q : ℕ) (h : q % 12 = 7) : ESC5 (5 * q + 1) := by
  obtain ⟨x, rfl⟩ : ∃ x, q = 7 + 12 * x := ⟨q / 12, by omega⟩
  exact ⟨8 * (3 + 5 * x), 24 * (3 + 5 * x), 4 * (3 + 5 * x), by positivity, by positivity, by positivity,
    esc5_of_cross _ _ _ _ (by positivity) (by positivity) (by positivity) (by positivity) (by ring)⟩

/-- `q ≡ 8 (mod 12)` — eq. (20). -/
theorem gesc_q8mod12 (q : ℕ) (h : q % 12 = 8) : ESC5 (5 * q + 1) := by
  obtain ⟨x, rfl⟩ : ∃ x, q = 8 + 12 * x := ⟨q / 12, by omega⟩
  exact ⟨3 * (3 + 4 * x) * (11 + 16 * x), 3 * (11 + 16 * x) * (41 + 60 * x), 3 * (3 + 4 * x),
    by positivity, by positivity, by positivity,
    esc5_of_cross _ _ _ _ (by positivity) (by positivity) (by positivity) (by positivity) (by ring)⟩

/-- `q ≡ 9 (mod 12)` — eq. (29). -/
theorem gesc_q9mod12 (q : ℕ) (h : q % 12 = 9) : ESC5 (5 * q + 1) := by
  obtain ⟨x, rfl⟩ : ∃ x, q = 9 + 12 * x := ⟨q / 12, by omega⟩
  exact ⟨46 + 60 * x, 23 + 30 * x, 23 + 30 * x, by positivity, by positivity, by positivity,
    esc5_of_cross _ _ _ _ (by positivity) (by positivity) (by positivity) (by positivity) (by ring)⟩

/-- `q ≡ 10 (mod 12)` — eq. (22). -/
theorem gesc_q10mod12 (q : ℕ) (h : q % 12 = 10) : ESC5 (5 * q + 1) := by
  obtain ⟨x, rfl⟩ : ∃ x, q = 10 + 12 * x := ⟨q / 12, by omega⟩
  exact ⟨(11 + 12 * x) * (13 + 15 * x), 3 * (11 + 12 * x) * (13 + 15 * x) * (17 + 20 * x), 11 + 12 * x,
    by positivity, by positivity, by positivity,
    esc5_of_cross _ _ _ _ (by positivity) (by positivity) (by positivity) (by positivity) (by ring)⟩

/-- `q ≡ 11 (mod 12)` — eq. (31). -/
theorem gesc_q11mod12 (q : ℕ) (h : q % 12 = 11) : ESC5 (5 * q + 1) := by
  obtain ⟨x, rfl⟩ : ∃ x, q = 11 + 12 * x := ⟨q / 12, by omega⟩
  exact ⟨56 + 60 * x, 28 + 30 * x, 28 + 30 * x, by positivity, by positivity, by positivity,
    esc5_of_cross _ _ _ _ (by positivity) (by positivity) (by positivity) (by positivity) (by ring)⟩

/-! ## Theorem 2.1(3) — `q = 12u`, `u ≢ 0 (mod 7)` : the six `u (mod 7)` families (34)–(39) -/

/-- `u ≡ 1 (mod 7)` — eq. (34). -/
theorem gesc_u1mod7 (u : ℕ) (h : u % 7 = 1) : ESC5 (5 * (12 * u) + 1) := by
  obtain ⟨x, rfl⟩ : ∃ x, u = 7 * x + 1 := ⟨u / 7, by omega⟩
  exact ⟨84 * x + 14, 7 * (48 * x + 7) * (420 * x + 61), 14 * (6 * x + 1) * (48 * x + 7),
    by positivity, by positivity, by positivity,
    esc5_of_cross _ _ _ _ (by positivity) (by positivity) (by positivity) (by positivity) (by ring)⟩

/-- `u ≡ 2 (mod 7)` — corrected eq. (35) (the printed (35) duplicates (34); this is the general `p₄`
decomposition at `y = 1`, verified in `analysis/verify_ghermoul.py`). -/
theorem gesc_u2mod7 (u : ℕ) (h : u % 7 = 2) : ESC5 (5 * (12 * u) + 1) := by
  obtain ⟨x, rfl⟩ : ∃ x, u = 7 * x + 2 := ⟨u / 7, by omega⟩
  exact ⟨2 * (3 * x + 1) * (420 * x + 121), 6 * (3 * x + 1) * (28 * x + 9) * (420 * x + 121), 3 * (28 * x + 9),
    by positivity, by positivity, by positivity,
    esc5_of_cross _ _ _ _ (by positivity) (by positivity) (by positivity) (by positivity) (by ring)⟩

/-- `u ≡ 3 (mod 7)` — eq. (36). -/
theorem gesc_u3mod7 (u : ℕ) (h : u % 7 = 3) : ESC5 (5 * (12 * u) + 1) := by
  obtain ⟨x, rfl⟩ : ∃ x, u = 7 * x + 3 := ⟨u / 7, by omega⟩
  exact ⟨84 * x + 39, 3 * (28 * x + 13) * (30 * x + 13) * (420 * x + 181), 3 * (28 * x + 13) * (30 * x + 13),
    by positivity, by positivity, by positivity,
    esc5_of_cross _ _ _ _ (by positivity) (by positivity) (by positivity) (by positivity) (by ring)⟩

/-- `u ≡ 4 (mod 7)` — eq. (37). -/
theorem gesc_u4mod7 (u : ℕ) (h : u % 7 = 4) : ESC5 (5 * (12 * u) + 1) := by
  obtain ⟨x, rfl⟩ : ∃ x, u = 7 * x + 4 := ⟨u / 7, by omega⟩
  exact ⟨8820 * x ^ 2 + 10353 * x + 3038, (12 * x + 7) * (105 * x + 62) * (420 * x + 241), 84 * x + 49,
    by positivity, by positivity, by positivity,
    esc5_of_cross _ _ _ _ (by positivity) (by positivity) (by positivity) (by positivity) (by ring)⟩

/-- `u ≡ 5 (mod 7)` — eq. (38). -/
theorem gesc_u5mod7 (u : ℕ) (h : u % 7 = 5) : ESC5 (5 * (12 * u) + 1) := by
  obtain ⟨x, rfl⟩ : ∃ x, u = 7 * x + 5 := ⟨u / 7, by omega⟩
  exact ⟨2520 * x ^ 2 + 3714 * x + 1368, 14 * (4 * x + 3) * (60 * x + 43) * (105 * x + 76), 84 * x + 63,
    by positivity, by positivity, by positivity,
    esc5_of_cross _ _ _ _ (by positivity) (by positivity) (by positivity) (by positivity) (by ring)⟩

/-- `u ≡ 6 (mod 7)` — eq. (39). -/
theorem gesc_u6mod7 (u : ℕ) (h : u % 7 = 6) : ESC5 (5 * (12 * u) + 1) := by
  obtain ⟨x, rfl⟩ : ∃ x, u = 7 * x + 6 := ⟨u / 7, by omega⟩
  exact ⟨2520 * x ^ 2 + 4434 * x + 1950, 2 * (15 * x + 13) * (28 * x + 25) * (420 * x + 361), 84 * x + 75,
    by positivity, by positivity, by positivity,
    esc5_of_cross _ _ _ _ (by positivity) (by positivity) (by positivity) (by positivity) (by ring)⟩

/-! ## Theorem 2.1(4) — `u = 7v`, `v ≢ 0 (mod 3)` : the two `v (mod 3)` families (40)–(41) -/

/-- `v ≡ 1 (mod 3)` — eq. (40). -/
theorem gesc_v1mod3 (v : ℕ) (h : v % 3 = 1) : ESC5 (5 * (12 * (7 * v)) + 1) := by
  obtain ⟨x, rfl⟩ : ∃ x, v = 3 * x + 1 := ⟨v / 3, by omega⟩
  exact ⟨(126 * x + 43) * (140 * x + 47) * (1260 * x + 421), 35280 * x ^ 2 + 23884 * x + 4042, 252 * x + 86,
    by positivity, by positivity, by positivity,
    esc5_of_cross _ _ _ _ (by positivity) (by positivity) (by positivity) (by positivity) (by ring)⟩

/-- `v ≡ 2 (mod 3)` — eq. (41). -/
theorem gesc_v2mod3 (v : ℕ) (h : v % 3 = 2) : ESC5 (5 * (12 * (7 * v)) + 1) := by
  obtain ⟨x, rfl⟩ : ∃ x, v = 3 * x + 2 := ⟨v / 3, by omega⟩
  exact ⟨(28 * x + 19) * (1260 * x + 841), 2 * (28 * x + 19) * (126 * x + 85) * (1260 * x + 841), 252 * x + 170,
    by positivity, by positivity, by positivity,
    esc5_of_cross _ _ _ _ (by positivity) (by positivity) (by positivity) (by positivity) (by ring)⟩

/-- **Theorem 2.1(2)+(3)+(4), assembled (machine-verified, unconditional).** Every `a = 5q+1` with
`q ≢ 0 (mod 252)` admits a positive three-term decomposition.  The nested residue cover is exactly
Ghermoul's: `q (mod 12)`, then (when `12 ∣ q`) `u (mod 7)`, then (when `7 ∣ u`) `v (mod 3)`; the only
escape is `v ≡ 0`, i.e. `q ≡ 0 (mod 252)`, which contradicts the hypothesis. -/
theorem gesc_5q1_proven (q : ℕ) (h252 : q % 252 ≠ 0) : ESC5 (5 * q + 1) := by
  rcases (by omega : q % 12 = 1 ∨ q % 12 = 2 ∨ q % 12 = 3 ∨ q % 12 = 4 ∨ q % 12 = 5 ∨ q % 12 = 6 ∨
      q % 12 = 7 ∨ q % 12 = 8 ∨ q % 12 = 9 ∨ q % 12 = 10 ∨ q % 12 = 11 ∨ q % 12 = 0) with
    h | h | h | h | h | h | h | h | h | h | h | h12
  · exact gesc_q1mod12 q h
  · exact gesc_q2mod12 q h
  · exact gesc_q3mod12 q h
  · exact gesc_q4mod12 q h
  · exact gesc_q5mod12 q h
  · exact gesc_q6mod12 q h
  · exact gesc_q7mod12 q h
  · exact gesc_q8mod12 q h
  · exact gesc_q9mod12 q h
  · exact gesc_q10mod12 q h
  · exact gesc_q11mod12 q h
  · -- 12 ∣ q
    obtain ⟨u, rfl⟩ : ∃ u, q = 12 * u := ⟨q / 12, by omega⟩
    rcases (by omega : u % 7 = 1 ∨ u % 7 = 2 ∨ u % 7 = 3 ∨ u % 7 = 4 ∨ u % 7 = 5 ∨ u % 7 = 6 ∨
        u % 7 = 0) with h | h | h | h | h | h | h7
    · exact gesc_u1mod7 u h
    · exact gesc_u2mod7 u h
    · exact gesc_u3mod7 u h
    · exact gesc_u4mod7 u h
    · exact gesc_u5mod7 u h
    · exact gesc_u6mod7 u h
    · -- 7 ∣ u
      obtain ⟨v, rfl⟩ : ∃ v, u = 7 * v := ⟨u / 7, by omega⟩
      rcases (by omega : v % 3 = 1 ∨ v % 3 = 2 ∨ v % 3 = 0) with h | h | h3
      · exact gesc_v1mod3 v h
      · exact gesc_v2mod3 v h
      · exact absurd (by omega : 12 * (7 * v) % 252 = 0) h252

/-! ## The open part — Ghermoul's Conjecture 2, the bridge identity (17), and the reduction -/

/-- `P1 X Y Z = p₁(X+1, Y+1, Z+1)` where `p₁(x,y,z) = z(x(5y−1)−y) − x` is Ghermoul's polynomial
(16).  Written in shifted variables `X,Y,Z ≥ 0` (the paper's `x,y,z ∈ ℕ*`) it is subtraction-free,
so it is honestly a natural number and every denominator of (17) is manifestly positive. -/
def P1 (X Y Z : ℕ) : ℕ :=
  5 * X * Y * Z + 4 * X * Z + 4 * Y * Z + 3 * Z + 5 * X * Y + 3 * X + 4 * Y + 2

/-- `P1` is exactly the paper's `p₁` on `x,y,z ≥ 1` (checked over `ℤ`, where subtraction is honest). -/
theorem P1_eq_paper (X Y Z : ℕ) :
    (P1 X Y Z : ℤ) = (Z + 1) * ((X + 1) * (5 * (Y + 1) - 1) - (Y + 1)) - (X + 1) := by
  simp only [P1]; push_cast; ring

/-- **The bridge (Ghermoul eq. (17)), machine-verified.** For all `X,Y,Z ≥ 0` (i.e. the paper's
`x,y,z ≥ 1`), `5/(5·p₁+1)` is an explicit sum of three positive unit fractions.  This is what makes
Conjecture 2 *imply* the conjecture on `a = 5q+1`: a value `q = p₁(x,y,z)` is automatically
decomposable. -/
theorem bridge_pos (X Y Z : ℕ) : ESC5 (5 * P1 X Y Z + 1) := by
  refine ⟨(5 * X * Y + 4 * X + 4 * Y + 3) * (5 * Y * Z + 5 * Y + 4 * Z + 3) *
        (25 * X * Y * Z + 25 * X * Y + 20 * X * Z + 15 * X + 20 * Y * Z + 20 * Y + 15 * Z + 11),
      (Z + 1) * (5 * X * Y + 4 * X + 4 * Y + 3) * (5 * Y * Z + 5 * Y + 4 * Z + 3),
      (Z + 1) * (5 * X * Y + 4 * X + 4 * Y + 3),
      by positivity, by positivity, by positivity, ?_⟩
  refine esc5_of_cross _ _ _ _ (by positivity) (by positivity) (by positivity) (by positivity) ?_
  simp only [P1]; ring

/-- **Ghermoul's Conjecture 2** (the *only* unproven ingredient): the polynomial `p₁` is surjective
onto the positive multiples of `252`.  Equivalently `252·ℕ* ⊆ p₁(ℕ*³)`.  Verified computationally to
`5q+1 ≈ 2·10¹⁰` in the paper; left open in general. -/
def Conjecture2 : Prop := ∀ ℓ : ℕ, 0 < ℓ → ∃ X Y Z : ℕ, P1 X Y Z = 252 * ℓ

/-- **The reduction (machine-verified).** Conjecture 2 closes the residual class: assuming it, every
`a = 5q+1` with `q ≡ 0 (mod 252)` (and `q > 0`) is decomposable, via `bridge_pos`. -/
theorem residual_of_conjecture2 (hC : Conjecture2) (q : ℕ) (hq : 0 < q) (h : q % 252 = 0) :
    ESC5 (5 * q + 1) := by
  obtain ⟨ℓ, rfl⟩ : ∃ ℓ, q = 252 * ℓ := ⟨q / 252, by omega⟩
  obtain ⟨X, Y, Z, hP⟩ := hC ℓ (by omega)
  rw [← hP]
  exact bridge_pos X Y Z

/-! ## The headline — Ghermoul's *almost*-complete proof, as a theorem -/

/-- **Generalized Erdős–Straus for numerator 5 (machine-verified, conditional on Conjecture 2).**
This is Ghermoul's main result: *assuming the single open Conjecture 2*, `5/a = 1/b + 1/c + 1/d` in
positive integers for **every** integer `a ≥ 2`.

The proof is the paper's complete case tree: `a ≢ 1 (mod 5)` is unconditional (`gesc_easy`);
`a = 5q+1` splits into the proven cover `q ≢ 0 (mod 252)` (`gesc_5q1_proven`) and the residual
`q ≡ 0 (mod 252)` (`residual_of_conjecture2`, the only place Conjecture 2 is used). Everything
except Conjecture 2 is fully proven, with no `sorry`. -/
theorem generalized_esc_5 (hC : Conjecture2) (a : ℕ) (ha : 2 ≤ a) : ESC5 a := by
  rcases eq_or_ne (a % 5) 1 with h1 | h1
  · obtain ⟨q, rfl⟩ : ∃ q, a = 5 * q + 1 := ⟨a / 5, by omega⟩
    rcases eq_or_ne (q % 252) 0 with h0 | h0
    · exact residual_of_conjecture2 hC q (by omega) h0
    · exact gesc_5q1_proven q h0
  · exact gesc_easy a ha h1

/-! ## Sanity checks (the theorems are non-vacuous) -/

-- Unconditional: `5/7 = 1/7 + 1/14 + 1/2` (a = 7 = 5·1 + 2, odd sub-case q = 0).
example : ESC5 7 := gesc_easy 7 (by norm_num) (by norm_num)
example : (5 : ℚ) / 7 = 1 / 7 + 1 / 14 + 1 / 2 := by norm_num

-- Unconditional small cases reached only through the `k = 0` boundary of the families:
example : ESC5 2 := gesc_easy 2 (by norm_num) (by norm_num)   -- 5/2 = 1/1 + 1/2 + 1/1
example : ESC5 3 := gesc_easy 3 (by norm_num) (by norm_num)   -- 5/3 = 1/3 + 1/3 + 1/1
example : ESC5 4 := gesc_easy 4 (by norm_num) (by norm_num)   -- 5/4 = 1/20 + 1/5 + 1/1

-- The proven `a = 5q+1` cover, with `q ≢ 0 (mod 252)`: e.g. a = 11 (q = 2), a = 61 (q = 12, u = 1).
example : ESC5 11 := gesc_5q1_proven 2 (by norm_num)
example : ESC5 61 := gesc_5q1_proven 12 (by norm_num)

-- The bridge in action: `p₁(1,3,23) = 252`, so 5/(5·252+1) = 5/1261 is decomposable (eq. 17).
example : P1 0 2 22 = 252 := by norm_num [P1]
example : ESC5 1261 := by
  have h : (5 * P1 0 2 22 + 1) = 1261 := by norm_num [P1]
  rw [← h]; exact bridge_pos 0 2 22

-- The headline is genuinely conditional: given Conjecture 2 it decides any `a ≥ 2`, e.g. the
-- otherwise-open residual a = 5·252 + 1 = 1261 (q = 252 ≡ 0 mod 252).
example (hC : Conjecture2) : ESC5 1261 := generalized_esc_5 hC 1261 (by norm_num)

-- Conjecture 2 is consistent at ℓ = 1 (the start of the verified range): 252 is hit by p₁.
example : ∃ X Y Z : ℕ, P1 X Y Z = 252 * 1 := ⟨0, 2, 22, by norm_num [P1]⟩

end GeneralizedErdosStraus
