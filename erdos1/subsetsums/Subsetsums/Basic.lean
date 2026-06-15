import Mathlib

set_option linter.style.header false
set_option linter.style.longLine false

/-!
# Erdős #1 — Lemma 0 and the variance floor (Theorem 1's heart), formalised

Distinct-subset-sums (*dissociated*) sets `a : Fin n → ℤ`:
`Dissociated a` ⇔ the subset-sum map `S ↦ ∑_{i∈S} a i` is injective.

Every result compiles with no `sorry`.
-/

open Finset

namespace SubsetSums

variable {n : ℕ}

/-- The subset-sum of `S ⊆ Fin n`. -/
def subsetSum (a : Fin n → ℤ) (S : Finset (Fin n)) : ℤ := ∑ i ∈ S, a i

/-- A set is *dissociated* if all `2ⁿ` subset sums are distinct. -/
def Dissociated (a : Fin n → ℤ) : Prop := Function.Injective (subsetSum a)

/-- **Lemma 0 (combinatorial core).** The number of distinct subset sums is at most `2ⁿ`,
with equality exactly when the set is dissociated. -/
theorem Lemma0 (a : Fin n → ℤ) :
    ((univ : Finset (Finset (Fin n))).image (subsetSum a)).card ≤ 2 ^ n ∧
    (((univ : Finset (Finset (Fin n))).image (subsetSum a)).card = 2 ^ n ↔ Dissociated a) := by
  have hcard : (univ : Finset (Finset (Fin n))).card = 2 ^ n := by
    simp [Finset.card_univ, Fintype.card_finset, Fintype.card_fin]
  refine ⟨?_, ?_⟩
  · calc ((univ : Finset (Finset (Fin n))).image (subsetSum a)).card
        ≤ (univ : Finset (Finset (Fin n))).card := Finset.card_image_le
      _ = 2 ^ n := hcard
  · rw [← hcard, Finset.card_image_iff, Finset.coe_univ, Set.injOn_univ]
    exact Iff.rfl

/-- **Double-sum identity.** `∑_{i,j} (x i − x j)² = 2 (m ∑ xᵢ² − (∑ xᵢ)²)`. -/
theorem sum_sub_sq_double {m : ℕ} (x : Fin m → ℤ) :
    (∑ i, ∑ j, (x i - x j) ^ 2)
      = 2 * ((m : ℤ) * (∑ i, (x i) ^ 2) - (∑ i, x i) ^ 2) := by
  have inner : ∀ i, (∑ j, (x i - x j) ^ 2)
      = (m : ℤ) * (x i) ^ 2 - 2 * (x i) * (∑ j, x j) + (∑ j, (x j) ^ 2) := by
    intro i
    have e : ∀ j, (x i - x j) ^ 2 = (x i) ^ 2 - 2 * (x i) * (x j) + (x j) ^ 2 :=
      fun j => by ring
    simp only [e, Finset.sum_add_distrib, Finset.sum_sub_distrib, Finset.sum_const,
               Finset.card_univ, Fintype.card_fin, nsmul_eq_mul, ← Finset.mul_sum]
  simp only [inner, Finset.sum_add_distrib, Finset.sum_sub_distrib, Finset.sum_const,
             Finset.card_univ, Fintype.card_fin, nsmul_eq_mul, ← Finset.mul_sum,
             ← Finset.sum_mul]
  ring

/-- Strict-monotone **spacing**: for `i ≤ j`, `(j − i) ≤ g j − g i` (integers). -/
theorem fingap {m : ℕ} (g : Fin m → ℤ) (hg : StrictMono g) (i j : Fin m) (hij : i ≤ j) :
    (j : ℤ) - (i : ℤ) ≤ g j - g i := by
  have hijv : i.val ≤ j.val := Fin.le_iff_val_le_val.mp hij
  suffices H : ∀ d : ℕ, ∀ b : ℕ, ∀ hb : b < m, b = i.val + d →
      (b : ℤ) - (i.val : ℤ) ≤ g ⟨b, hb⟩ - g i by
    have key := H (j.val - i.val) j.val j.isLt (by omega)
    have e1 : (⟨j.val, j.isLt⟩ : Fin m) = j := Fin.ext rfl
    rw [e1] at key
    exact key
  intro d
  induction d with
  | zero =>
    intro b hb hbd
    have hb0 : b = i.val := by omega
    subst hb0
    have e0 : (⟨i.val, hb⟩ : Fin m) = i := Fin.ext rfl
    rw [e0]; simp
  | succ p ih =>
    intro b hb hbd
    have hp_lt : i.val + p < m := by omega
    have hih := ih (i.val + p) hp_lt rfl
    have hlt : (⟨i.val + p, hp_lt⟩ : Fin m) < ⟨b, hb⟩ := by rw [Fin.mk_lt_mk]; omega
    have hstep : g ⟨i.val + p, hp_lt⟩ < g ⟨b, hb⟩ := hg hlt
    have hbz : (b : ℤ) = (i.val : ℤ) + (p : ℤ) + 1 := by rw [hbd]; push_cast; ring
    rw [hbz]; push_cast at hih; omega

/-- The squared spacing bound, both directions: `(i − j)² ≤ (g i − g j)²`. -/
theorem orderEmb_sq_le {m : ℕ} (g : Fin m → ℤ) (hg : StrictMono g) (i j : Fin m) :
    ((i : ℤ) - (j : ℤ)) ^ 2 ≤ (g i - g j) ^ 2 := by
  rcases le_total i j with h | h
  · have hgap := fingap g hg i j h
    have hmono : g i ≤ g j := hg.monotone h
    have hcast : (i : ℤ) ≤ (j : ℤ) := by exact_mod_cast Fin.le_iff_val_le_val.mp h
    nlinarith [hgap, hmono, hcast]
  · have hgap := fingap g hg j i h
    have hmono : g j ≤ g i := hg.monotone h
    have hcast : (j : ℤ) ≤ (i : ℤ) := by exact_mod_cast Fin.le_iff_val_le_val.mp h
    nlinarith [hgap, hmono, hcast]

/-- `2·∑_{k<m} k = m(m−1)`. -/
theorem sum_range_id2 (m : ℕ) :
    2 * (∑ i ∈ Finset.range m, (i : ℤ)) = (m : ℤ) * ((m : ℤ) - 1) := by
  induction m with
  | zero => simp
  | succ k ih => rw [Finset.sum_range_succ, mul_add, ih]; push_cast; ring

/-- `6·∑_{k<m} k² = m(m−1)(2m−1)`. -/
theorem sum_range_sq6 (m : ℕ) :
    6 * (∑ i ∈ Finset.range m, (i : ℤ) ^ 2) = (m : ℤ) * ((m : ℤ) - 1) * (2 * (m : ℤ) - 1) := by
  induction m with
  | zero => simp
  | succ k ih => rw [Finset.sum_range_succ, mul_add, ih]; push_cast; ring

/-- Closed form for the *consecutive* case: `12 (m ∑ i² − (∑ i)²) = m⁴ − m²`. -/
theorem closed_form (m : ℕ) :
    12 * ((m : ℤ) * (∑ i : Fin m, (i : ℤ) ^ 2) - (∑ i : Fin m, (i : ℤ)) ^ 2)
      = (m : ℤ) ^ 4 - (m : ℤ) ^ 2 := by
  rw [Fin.sum_univ_eq_sum_range (fun k => (k : ℤ) ^ 2),
      Fin.sum_univ_eq_sum_range (fun k => (k : ℤ))]
  linear_combination (2 * (m : ℤ)) * sum_range_sq6 m
    + (-6 * (∑ i ∈ Finset.range m, (i : ℤ)) - 3 * (m : ℤ) * ((m : ℤ) - 1)) * sum_range_id2 m

/-- **Variance floor for distinct integers** (the heart of Theorem 1).
For any finite `V ⊆ ℤ` of `m` distinct integers,
`12 (m ∑_{v∈V} v² − (∑_{v∈V} v)²) ≥ m⁴ − m²`. -/
theorem varLB (V : Finset ℤ) :
    (V.card : ℤ) ^ 4 - (V.card : ℤ) ^ 2
      ≤ 12 * ((V.card : ℤ) * (∑ v ∈ V, v ^ 2) - (∑ v ∈ V, v) ^ 2) := by
  set m := V.card with hm
  let g : Fin m → ℤ := V.orderEmbOfFin hm.symm
  have hg_inj : Function.Injective g := (V.orderEmbOfFin hm.symm).injective
  have hstrict : StrictMono g := (V.orderEmbOfFin hm.symm).strictMono
  have himg : Finset.image g Finset.univ = V := Finset.image_orderEmbOfFin_univ V hm.symm
  have hsum1 : (∑ v ∈ V, v) = ∑ i : Fin m, g i := by
    rw [← himg, Finset.sum_image (fun x _ y _ h => hg_inj h)]
  have hsum2 : (∑ v ∈ V, v ^ 2) = ∑ i : Fin m, (g i) ^ 2 := by
    rw [← himg, Finset.sum_image (fun x _ y _ h => hg_inj h)]
  have hD := sum_sub_sq_double g
  have hDc := sum_sub_sq_double (fun i : Fin m => (i : ℤ))
  have hle : (∑ i : Fin m, ∑ j : Fin m, ((i : ℤ) - (j : ℤ)) ^ 2)
      ≤ ∑ i : Fin m, ∑ j : Fin m, (g i - g j) ^ 2 :=
    Finset.sum_le_sum fun i _ => Finset.sum_le_sum fun j _ => orderEmb_sq_le g hstrict i j
  rw [hD, hDc] at hle
  have hcf := closed_form m
  rw [hsum1, hsum2]
  nlinarith [hle, hcf]

/-- **Theorem 1 (the variance floor).** A dissociated set satisfies `∑ aᵢ² ≥ (4ⁿ−1)/3`,
stated as `4ⁿ − 1 ≤ 3 ∑ aᵢ²`.  Proved from `varLB` together with the two *standard*
second-moment identities for subset sums (each i lies in half the subsets; each pair
i≠j in a quarter), supplied here as hypotheses `hI1`, `hI2`. -/
theorem Theorem1_of_moments (a : Fin n → ℤ) (h : Dissociated a)
    (hI1 : 2 * (∑ S : Finset (Fin n), subsetSum a S) = (2 : ℤ) ^ n * (∑ i, a i))
    (hI2 : 4 * (∑ S : Finset (Fin n), (subsetSum a S) ^ 2)
            = (2 : ℤ) ^ n * ((∑ i, a i) ^ 2 + ∑ i, (a i) ^ 2)) :
    (4 : ℤ) ^ n - 1 ≤ 3 * ∑ i, (a i) ^ 2 := by
  set V := (univ : Finset (Finset (Fin n))).image (subsetSum a) with hVdef
  have hVcard : V.card = 2 ^ n := by
    rw [hVdef, Finset.card_image_of_injective _ h]
    simp [Finset.card_univ, Fintype.card_finset, Fintype.card_fin]
  have hPV : (∑ v ∈ V, v) = ∑ S : Finset (Fin n), subsetSum a S := by
    rw [hVdef, Finset.sum_image (fun x _ y _ hxy => h hxy)]
  have hQV : (∑ v ∈ V, v ^ 2) = ∑ S : Finset (Fin n), (subsetSum a S) ^ 2 := by
    rw [hVdef, Finset.sum_image (fun x _ y _ hxy => h hxy)]
  have hv := varLB V
  rw [hVcard, hPV, hQV] at hv
  simp only [Nat.cast_pow, Nat.cast_ofNat] at hv
  have hkey : 12 * ((2 : ℤ) ^ n * (∑ S : Finset (Fin n), (subsetSum a S) ^ 2)
              - (∑ S : Finset (Fin n), subsetSum a S) ^ 2)
            = 3 * ((2 : ℤ) ^ n) ^ 2 * (∑ i, (a i) ^ 2) := by
    linear_combination 3 * (2 : ℤ) ^ n * hI2
      - 3 * (2 * (∑ S : Finset (Fin n), subsetSum a S) + (2 : ℤ) ^ n * (∑ i, a i)) * hI1
  have h4 : (4 : ℤ) ^ n = ((2 : ℤ) ^ n) ^ 2 := by
    rw [show (4 : ℤ) = 2 ^ 2 from by norm_num, ← pow_mul, ← pow_mul, Nat.mul_comm]
  have ht2 : (0 : ℤ) < ((2 : ℤ) ^ n) ^ 2 := by positivity
  rw [h4]
  nlinarith [hv, hkey, ht2]

end SubsetSums

-- axiom audit (no `sorryAx` may appear)
#print axioms SubsetSums.Lemma0
#print axioms SubsetSums.varLB
#print axioms SubsetSums.Theorem1_of_moments
