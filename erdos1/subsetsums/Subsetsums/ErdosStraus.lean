import Mathlib

set_option linter.style.header false

/-!
# A machine-verified partial result for the Erdős–Straus conjecture

The Erdős–Straus conjecture asserts `4/n = 1/x + 1/y + 1/z` in positive integers for every
`n ≥ 2`.  This file formalises the **K1 / Obláth sufficient criterion** (REPORT §9.2): if the
shifted integer `4p+1` has a divisor `≡ 3 (mod 4)`, then `4/p` is a sum of three unit fractions.
This covers a density-1 family (the failure set has Landau–Ramanujan density → 0).

The heart is a constructive identity: `(4y-1)(4z-1) = 4p+1` forces
`4/p = 1/(yz) + 1/(p·y) + 1/(p·z)`.  No `sorry`.
-/

namespace ErdosStraus

/-- **The m = 1 constructive identity.** If `(4y-1)(4z-1) = 4p+1` with `y, z ≥ 1`, then
`4/p = 1/(y*z) + 1/(p*y) + 1/(p*z)` over `ℚ`. -/
theorem esc_of_factorization (p y z : ℕ) (hp : 0 < p) (hy : 0 < y) (hz : 0 < z)
    (h : (4 * y - 1) * (4 * z - 1) = 4 * p + 1) :
    (4 : ℚ) / p = 1 / (y * z) + 1 / (p * y) + 1 / (p * z) := by
  -- The defining relation `16yz - 4y - 4z + 1 = 4p+1`, i.e. `4yz = p + y + z`.
  have key : 4 * y * z = p + y + z := by
    have h1 : 1 ≤ 4 * y := by omega
    have h2 : 1 ≤ 4 * z := by omega
    zify [h1, h2] at h ⊢
    nlinarith [h]
  have hpQ : (p : ℚ) ≠ 0 := by exact_mod_cast hp.ne'
  have hyQ : (y : ℚ) ≠ 0 := by exact_mod_cast hy.ne'
  have hzQ : (z : ℚ) ≠ 0 := by exact_mod_cast hz.ne'
  have keyQ : (4 : ℚ) * y * z = p + y + z := by exact_mod_cast key
  field_simp
  ring_nf
  nlinarith [keyQ, mul_pos (mul_pos hp hy) hz]

/-- Helper: the complementary divisor of `4p+1` is also `≡ 3 (mod 4)`. -/
theorem comp_mod_four (p D : ℕ) (hD : D ∣ 4 * p + 1) (hD3 : D % 4 = 3) :
    ((4 * p + 1) / D) % 4 = 3 := by
  have hDpos : 0 < D := Nat.pos_of_dvd_of_pos hD (by omega)
  obtain ⟨E, hE⟩ := hD
  have hEval : (4 * p + 1) / D = E := by rw [hE]; exact Nat.mul_div_cancel_left E hDpos
  rw [hEval]
  have hmod : (D * E) % 4 = 1 := by rw [← hE]; omega
  have hDE : (D % 4) * (E % 4) % 4 = 1 := by rwa [Nat.mul_mod] at hmod
  rw [hD3] at hDE
  omega

/-- **K1 / Obláth criterion (machine-verified).** If `4p+1` has a divisor `≡ 3 (mod 4)`, then
`4/p` is a sum of three positive unit fractions — the Erdős–Straus conjecture holds for `p`. -/
theorem esc_of_K1 (p D : ℕ) (hp : 0 < p) (hD : D ∣ 4 * p + 1) (hD3 : D % 4 = 3) :
    ∃ x y z : ℕ, 0 < x ∧ 0 < y ∧ 0 < z ∧
      (4 : ℚ) / p = 1 / x + 1 / y + 1 / z := by
  have hDpos : 0 < D := Nat.pos_of_dvd_of_pos hD (by omega)
  set E := (4 * p + 1) / D with hEdef
  have hDE : D * E = 4 * p + 1 := Nat.mul_div_cancel' hD
  have hE3 : E % 4 = 3 := comp_mod_four p D hD hD3
  have hEpos : 0 < E := by nlinarith [hDE, hp]
  refine ⟨((E + 1) / 4) * ((D + 1) / 4), p * ((E + 1) / 4), p * ((D + 1) / 4), ?_, ?_, ?_, ?_⟩
  · have h1 : 0 < (E + 1) / 4 := by omega
    have h2 : 0 < (D + 1) / 4 := by omega
    positivity
  · exact Nat.mul_pos hp (by omega)
  · exact Nat.mul_pos hp (by omega)
  · have hfac : (4 * ((E + 1) / 4) - 1) * (4 * ((D + 1) / 4) - 1) = 4 * p + 1 := by
      have hy : 4 * ((E + 1) / 4) - 1 = E := by omega
      have hz : 4 * ((D + 1) / 4) - 1 = D := by omega
      rw [hy, hz, mul_comm]; exact hDE
    have H := esc_of_factorization p ((E + 1) / 4) ((D + 1) / 4) hp (by omega) (by omega) hfac
    push_cast at H ⊢
    linarith [H]

/-- **General Type II criterion (machine-verified).** If `(4y-1)(4z-1) = 4pδ+1` with `δ ∣ y*z`,
then with `x = y*z/δ` one has `4/p = 1/x + 1/(p*y) + 1/(p*z)` — a positive Erdős–Straus solution.
This is the master sufficient condition behind every K-criterion (K1 is `δ=1`); see REPORT §14. -/
theorem esc_of_typeII (p y z δ : ℕ) (hp : 0 < p) (hy : 0 < y) (hz : 0 < z)
    (hdvd : δ ∣ y * z) (h : (4 * y - 1) * (4 * z - 1) = 4 * p * δ + 1) :
    ∃ x : ℕ, 0 < x ∧ (4 : ℚ) / p = 1 / x + 1 / (p * y) + 1 / (p * z) := by
  obtain ⟨x, hx⟩ := hdvd
  have hxpos : 0 < x := by
    rcases Nat.eq_zero_or_pos x with rfl | h0
    · simp only [Nat.mul_zero] at hx
      have := Nat.mul_pos hy hz; omega
    · exact h0
  refine ⟨x, hxpos, ?_⟩
  have key : 4 * y * z = p * δ + y + z := by
    have h1 : 1 ≤ 4 * y := by omega
    have h2 : 1 ≤ 4 * z := by omega
    zify [h1, h2] at h ⊢
    nlinarith [h]
  have hpQ : (p : ℚ) ≠ 0 := by exact_mod_cast hp.ne'
  have hyQ : (y : ℚ) ≠ 0 := by exact_mod_cast hy.ne'
  have hzQ : (z : ℚ) ≠ 0 := by exact_mod_cast hz.ne'
  have hxQ : (x : ℚ) ≠ 0 := by exact_mod_cast hxpos.ne'
  have hxrel : (y : ℚ) * z = δ * x := by exact_mod_cast hx
  have keyQ : (4 : ℚ) * y * z = p * δ + y + z := by exact_mod_cast key
  have hxinv : (1 : ℚ) / (x : ℚ) = (δ : ℚ) / ((y : ℚ) * z) := by
    rw [div_eq_div_iff hxQ (by positivity)]; linarith [hxrel]
  rw [hxinv]
  field_simp
  nlinarith [keyQ, mul_pos (mul_pos hp hy) hz]

/-- **The square obstruction, prime core (machine-verified).** Every prime factor of `4c²+1` is
`≡ 1 (mod 4)`. Hence `4c²+1` has no prime factor `≡ 3 (mod 4)`, so the K1 criterion can never
fire at `n = c²` — the quadratic-reciprocity reason elementary methods fail at squares (REPORT
§9.4, the coprime case of Yamamoto's theorem). -/
theorem prime_factor_four_sq_add_one (ℓ c : ℕ) (hℓ : ℓ.Prime) (hdvd : ℓ ∣ 4 * c ^ 2 + 1) :
    ℓ % 4 = 1 := by
  haveI : Fact ℓ.Prime := ⟨hℓ⟩
  have hne2 : ℓ ≠ 2 := by rintro rfl; omega
  have h0 : ((4 * c ^ 2 + 1 : ℕ) : ZMod ℓ) = 0 :=
    (CharP.cast_eq_zero_iff (ZMod ℓ) ℓ _).mpr hdvd
  have h4c2 : (4 : ZMod ℓ) * (c : ZMod ℓ) ^ 2 = -1 := by push_cast at h0; linear_combination h0
  have hsq : IsSquare (-1 : ZMod ℓ) := ⟨2 * c, by linear_combination -h4c2⟩
  have hne3 : ℓ % 4 ≠ 3 := ZMod.exists_sq_eq_neg_one_iff.mp hsq
  have hodd : ℓ % 2 = 1 := Nat.odd_iff.mp (hℓ.odd_of_ne_two hne2)
  omega

/-- **Square obstruction, full statement (machine-verified).** Every divisor of `4c²+1` is
`≡ 1 (mod 4)`. In particular `4c²+1` has no divisor `≡ 3 (mod 4)`, so the K1 criterion
(`esc_of_K1`) can never fire at `n = c²` — `4n+1 = 4c²+1`. This is REPORT §9.4 (coprime Yamamoto)
for the K1 channel: the elementary method that proves ESC for a density-1 family provably fails
at the squares. -/
theorem four_sq_add_one_div_one_mod_four (c : ℕ) :
    ∀ D, D ∣ 4 * c ^ 2 + 1 → D % 4 = 1 := by
  intro D
  induction D using Nat.strong_induction_on with
  | _ D ih =>
    intro hD
    rcases Nat.lt_or_ge D 2 with hlt | hge
    · -- D = 0 impossible (D ∣ positive); D = 1 gives 1 % 4 = 1
      have hpos : 0 < D := Nat.pos_of_dvd_of_pos hD (by positivity)
      interval_cases D
      simp
    · obtain ⟨ℓ, hℓ, hℓD⟩ := Nat.exists_prime_and_dvd (by omega : D ≠ 1)
      have hℓ4 : ℓ % 4 = 1 := prime_factor_four_sq_add_one ℓ c hℓ (hℓD.trans hD)
      obtain ⟨E, hE⟩ := hℓD
      have hEpos : 0 < E := by
        rcases Nat.eq_zero_or_pos E with rfl | h
        · rw [Nat.mul_zero] at hE; omega
        · exact h
      have hElt : E < D := by have := hℓ.two_le; nlinarith [hE, hEpos]
      have hEdvd : E ∣ 4 * c ^ 2 + 1 := (Dvd.intro_left ℓ hE.symm).trans hD
      have hE4 : E % 4 = 1 := ih E hElt hEdvd
      rw [hE, Nat.mul_mod, hℓ4, hE4]

end ErdosStraus
