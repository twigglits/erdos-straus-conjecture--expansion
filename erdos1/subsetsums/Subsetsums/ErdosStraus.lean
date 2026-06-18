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

/-- **K2 square obstruction, prime core (machine-verified).** Every prime factor of `8c²+1` is
`≡ 1 or 3 (mod 8)`: in `ZMod ℓ`, `(4c)² = −2`, so `−2` is a square, hence `ℓ % 8 ∈ {1,3}`
(Mathlib `ZMod.exists_sq_eq_neg_two_iff`). In particular none is `≡ 7 (mod 8)`. -/
theorem prime_factor_eight_sq_add_one (ℓ c : ℕ) (hℓ : ℓ.Prime) (hdvd : ℓ ∣ 8 * c ^ 2 + 1) :
    ℓ % 8 = 1 ∨ ℓ % 8 = 3 := by
  haveI : Fact ℓ.Prime := ⟨hℓ⟩
  have hne2 : ℓ ≠ 2 := by rintro rfl; omega
  have hodd : ℓ % 2 = 1 := Nat.odd_iff.mp (hℓ.odd_of_ne_two hne2)
  have h0 : ((8 * c ^ 2 + 1 : ℕ) : ZMod ℓ) = 0 := (CharP.cast_eq_zero_iff (ZMod ℓ) ℓ _).mpr hdvd
  have hsq : IsSquare (-2 : ZMod ℓ) := ⟨4 * c, by push_cast at h0; linear_combination -2 * h0⟩
  exact (ZMod.exists_sq_eq_neg_two_iff hne2).mp hsq

/-- **K2 square obstruction, full (machine-verified).** Every divisor of `8c²+1` is `≡ 1 or 3
(mod 8)`; in particular `8c²+1` has no divisor `≡ 7 (mod 8)`, so the K2 criterion never fires at
`n = c²`. -/
theorem eight_sq_add_one_div_one_or_three_mod_eight (c : ℕ) :
    ∀ D, D ∣ 8 * c ^ 2 + 1 → D % 8 = 1 ∨ D % 8 = 3 := by
  intro D
  induction D using Nat.strong_induction_on with
  | _ D ih =>
    intro hD
    rcases Nat.lt_or_ge D 2 with hlt | hge
    · have hpos : 0 < D := Nat.pos_of_dvd_of_pos hD (by positivity)
      interval_cases D
      left; rfl
    · obtain ⟨ℓ, hℓ, hℓD⟩ := Nat.exists_prime_and_dvd (by omega : D ≠ 1)
      have hℓ8 := prime_factor_eight_sq_add_one ℓ c hℓ (hℓD.trans hD)
      obtain ⟨E, hE⟩ := hℓD
      have hEpos : 0 < E := by
        rcases Nat.eq_zero_or_pos E with rfl | h
        · rw [Nat.mul_zero] at hE; omega
        · exact h
      have hElt : E < D := by have := hℓ.two_le; nlinarith [hE, hEpos]
      have hE8 := ih E hElt ((Dvd.intro_left ℓ hE.symm).trans hD)
      rw [hE, Nat.mul_mod]
      rcases hℓ8 with h1 | h1 <;> rcases hE8 with h2 | h2 <;> rw [h1, h2] <;> decide

/-- **General Lemma D — the "required sign" half (machine-verified).** For `a ≡ 3 (mod 4)` odd
with `gcd(2x, a) = 1`, the Jacobi symbol of the Type I target `−4x²` is `−1`. So *any* divisor of
`x²` lying in the Type I class `≡ −4x² (mod a)` would have Jacobi symbol `−1` — whereas a divisor
of `x²` has symbol `+1` (the squarefree/reciprocity "actual sign" half, discharged in full for the
K1/K2 channels above). This is the clean half of REPORT §9.4's general obstruction. -/
theorem typeI_target_jacobi (x a : ℕ) (ha3 : a % 4 = 3) (hcop : Int.gcd (2 * x) a = 1) :
    jacobiSym (-(4 * (x : ℤ) ^ 2)) a = -1 := by
  have hodd : Odd a := Nat.odd_iff.mpr (by omega)
  have e : -(4 * (x : ℤ) ^ 2) = (-1) * (2 * (x : ℤ)) ^ 2 := by ring
  rw [e, jacobiSym.mul_left, jacobiSym.sq_one' hcop, mul_one, jacobiSym.at_neg_one hodd,
    ZMod.χ₄_nat_three_mod_four ha3]

/-- **General Lemma D — the "actual sign" half (machine-verified).** For `a = 4x − c²` with
`a ≡ 3 (mod 4)`, *every* divisor `d ∣ x²` coprime to `a` has `jacobiSym d a = +1`. Combined with
`typeI_target_jacobi` (the Type I target class `≡ −4x²` forces `−1`), **no divisor of `x²` lies in
the Type I residue class** — the general square obstruction of REPORT §9.4, Type I, in full (the
K1/K2 theorems above are this argument specialised to the `4c²+1` and `8c²+1` channels).

The proof needs no per-prime factorisation: writing `d = b²·d₀` with `d₀` squarefree
(`sq_mul_squarefree`), `d₀ ∣ x²` gives `d₀ ∣ x` (`Squarefree.dvd_pow_iff_dvd`), so `d₀ ∣ 4x = a+c²`
and `a ≡ −c² (mod d₀)` for the *whole* `d₀`. Then `J(a|d₀) = χ₄ d₀`, and quadratic reciprocity with
`a ≡ 3 (mod 4)` makes the sign `(−1)^{(d₀/2)(a/2)}` equal `χ₄ d₀` as well, so `J(d₀|a) = (χ₄ d₀)² = 1`. -/
theorem typeI_div_jacobi_one (x c a d : ℕ) (hdodd : Odd d) (ha3 : a % 4 = 3)
    (hsum : a + c ^ 2 = 4 * x) (hda : Nat.Coprime d a) (hdx : d ∣ x ^ 2) :
    jacobiSym (d : ℤ) a = 1 := by
  have ha_odd : Odd a := Nat.odd_iff.mpr (by omega)
  -- squarefree decomposition d = b² · d₀
  obtain ⟨d0, b, hbd, hsf⟩ := Nat.sq_mul_squarefree d
  have hd0d : d0 ∣ d := ⟨b ^ 2, by rw [← hbd]; ring⟩
  have hbdvd : b ∣ d := (dvd_pow_self b (two_ne_zero)).trans ⟨d0, hbd.symm⟩
  -- d₀ is odd and divides x
  have hd0odd : Odd d0 := by
    rcases Nat.even_or_odd d0 with he | ho
    · exfalso; have : 2 ∣ d := (even_iff_two_dvd.mp he).trans hd0d
      rw [Nat.odd_iff] at hdodd; omega
    · exact ho
  have hd0x : d0 ∣ x := (hsf.dvd_pow_iff_dvd (two_ne_zero)).mp (hd0d.trans hdx)
  -- coprimalities, lifted to ℤ for the Jacobi API
  have hcop_ba : Nat.Coprime b a := Nat.Coprime.coprime_dvd_left hbdvd hda
  have hcop_cd0 : Nat.Coprime c d0 := by
    have h2 : Nat.gcd c d0 ∣ c := Nat.gcd_dvd_left c d0
    have h1 : Nat.gcd c d0 ∣ x := (Nat.gcd_dvd_right c d0).trans hd0x
    have hc2 : Nat.gcd c d0 ∣ c ^ 2 := h2.trans (dvd_pow_self c (two_ne_zero))
    have hsum' : Nat.gcd c d0 ∣ a + c ^ 2 := by rw [hsum]; exact h1.mul_left 4
    have hga : Nat.gcd c d0 ∣ a := by
      have h : Nat.gcd c d0 ∣ c ^ 2 + a := by rw [Nat.add_comm]; exact hsum'
      exact (Nat.dvd_add_right hc2).mp h
    have hgd : Nat.gcd c d0 ∣ d := (Nat.gcd_dvd_right c d0).trans hd0d
    have hdvd1 : Nat.gcd c d0 ∣ Nat.gcd d a := Nat.dvd_gcd hgd hga
    rw [hda] at hdvd1; exact Nat.dvd_one.mp hdvd1
  have hgcd_ba : Int.gcd (b : ℤ) (a : ℤ) = 1 := by rw [Int.gcd_natCast_natCast]; exact hcop_ba
  have hgcd_cd0 : Int.gcd (c : ℤ) (d0 : ℤ) = 1 := by rw [Int.gcd_natCast_natCast]; exact hcop_cd0
  -- a ≡ −c² (mod d₀), as integers
  have hsumdvd : d0 ∣ a + c ^ 2 := by rw [hsum]; exact hd0x.mul_left 4
  have hZ : (d0 : ℤ) ∣ (a : ℤ) + (c : ℤ) ^ 2 := by
    have := Int.natCast_dvd_natCast.mpr hsumdvd; push_cast at this; exact this
  have hmod : (a : ℤ) ≡ -(c : ℤ) ^ 2 [ZMOD (d0 : ℤ)] := by
    rw [Int.modEq_iff_dvd]
    have he : -(c : ℤ) ^ 2 - a = -((a : ℤ) + c ^ 2) := by ring
    rw [he]; exact (dvd_neg).mpr hZ
  -- J(a | d₀) = J(−1 | d₀)
  have hJa : jacobiSym (a : ℤ) d0 = jacobiSym (-1 : ℤ) d0 := by
    rw [jacobiSym.mod_left' hmod, show -(c : ℤ) ^ 2 = (-1) * (c : ℤ) ^ 2 by ring,
      jacobiSym.mul_left, jacobiSym.sq_one' hgcd_cd0, mul_one]
  -- reduce d to its squarefree part, then apply reciprocity
  have hbcast : (d : ℤ) = (b : ℤ) ^ 2 * (d0 : ℤ) := by rw [← hbd]; push_cast; ring
  rw [hbcast, jacobiSym.mul_left, jacobiSym.sq_one' hgcd_ba, one_mul,
    jacobiSym.quadratic_reciprocity hd0odd ha_odd, hJa, jacobiSym.at_neg_one hd0odd]
  -- the sign (−1)^{(d₀/2)(a/2)} equals χ₄ d₀, so the product is (χ₄ d₀)² = 1
  have hd0m2 : d0 % 2 = 1 := Nat.odd_iff.mp hd0odd
  rcases (show d0 % 4 = 1 ∨ d0 % 4 = 3 by omega) with h41 | h43
  · rw [ZMod.χ₄_nat_one_mod_four h41,
      Even.neg_one_pow ((Nat.even_iff.mpr (by omega : d0 / 2 % 2 = 0)).mul_right _)]; ring
  · rw [ZMod.χ₄_nat_three_mod_four h43,
      Odd.neg_one_pow ((Nat.odd_iff.mpr (by omega : d0 / 2 % 2 = 1)).mul
        (Nat.odd_iff.mpr (by omega : a / 2 % 2 = 1)))]; ring

/-- **General Lemma D, Type I — the obstruction (machine-verified).** When `a = 4x − c² ≡ 3 (mod 4)`
with `gcd(2x, a) = 1`, *no* divisor `d ∣ x²` coprime to `a` can lie in the Type I residue class
`d ≡ −4x² (mod a)`: such a `d` would have Jacobi symbol both `+1` (as a divisor of `x²`,
`typeI_div_jacobi_one`) and `−1` (as a class member, `typeI_target_jacobi`). This is REPORT §9.4's
general Type I square obstruction, in full and with no `sorry` — the unification the K1/K2 channel
theorems above specialise. -/
theorem typeI_obstruction (x c a d : ℕ) (hdodd : Odd d) (ha3 : a % 4 = 3)
    (hsum : a + c ^ 2 = 4 * x) (h2x : Int.gcd (2 * x) a = 1) (hda : Nat.Coprime d a)
    (hdx : d ∣ x ^ 2) (hcl : (d : ℤ) ≡ -(4 * (x : ℤ) ^ 2) [ZMOD a]) : False := by
  have h1 : jacobiSym (d : ℤ) a = 1 := typeI_div_jacobi_one x c a d hdodd ha3 hsum hda hdx
  have h2 : jacobiSym (d : ℤ) a = -1 := by
    rw [jacobiSym.mod_left' hcl]; exact typeI_target_jacobi x a ha3 h2x
  rw [h1] at h2; norm_num at h2

/-! ## Sanity checks (the theorems are non-vacuous). -/

-- ESC holds for p = 2 via K1: `4·2+1 = 9 = 3²` has the divisor `3 ≡ 3 (mod 4)`.
example : ∃ x y z : ℕ, 0 < x ∧ 0 < y ∧ 0 < z ∧ (4 : ℚ) / 2 = 1 / x + 1 / y + 1 / z :=
  esc_of_K1 2 3 (by norm_num) (by norm_num) (by norm_num)

-- The obstruction bites at `n = 9 = 3²`: every divisor of `4·9+1 = 37` is `≡ 1 (mod 4)`.
example (D : ℕ) (hD : D ∣ 4 * 3 ^ 2 + 1) : D % 4 = 1 :=
  four_sq_add_one_div_one_mod_four 3 D hD

-- K2 obstruction at `n = 9`: every divisor of `8·9+1 = 73` is `≡ 1 or 3 (mod 8)`, never 7.
example (D : ℕ) (hD : D ∣ 8 * 3 ^ 2 + 1) : D % 8 = 1 ∨ D % 8 = 3 :=
  eight_sq_add_one_div_one_or_three_mod_eight 3 D hD

-- The general Type I "actual sign" half is non-trivial: `x=3, c=1, a=4·3−1=11≡3 mod 4`,
-- and the divisor `d=3 ∣ 9=x²` (coprime to 11) indeed has `jacobiSym 3 11 = +1`.
example : jacobiSym (3 : ℤ) 11 = 1 := by
  have h := typeI_div_jacobi_one 3 1 11 3 (by decide) (by norm_num) (by norm_num)
    (by decide) (by norm_num)
  simpa using h

end ErdosStraus
