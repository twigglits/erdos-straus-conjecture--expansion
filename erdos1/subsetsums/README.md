# Erdős #1 in Lean 4 — Lemma 0 and Theorem 1 (the variance floor)

A machine-checked formalisation (Lean 4 + Mathlib, `v4.31.0`) of the elementary results
in `../THEOREMS.md`. Everything is in `Subsetsums/Basic.lean`; **no `sorry`** — the file
ends with `#print axioms` for the three headline results, each depending only on
`[propext, Classical.choice, Quot.sound]` (Mathlib's standard axioms, i.e. no `sorryAx`).

## What is proved

For `a : Fin n → ℤ`, `Dissociated a` means the subset-sum map `S ↦ ∑_{i∈S} a i` is injective.

- **`Lemma0`** — the number of distinct subset sums is `≤ 2ⁿ`, with equality iff dissociated
  (the combinatorial core of `THEOREMS.md`'s Lemma 0).
- **`varLB`** *(the mathematical heart)* — for any `V : Finset ℤ` of `m` distinct integers,
  `12 (m ∑_{v∈V} v² − (∑_{v∈V} v)²) ≥ m⁴ − m²`. This is the variance floor for distinct
  integers, proved from the strict-monotone spacing of the sorted elements
  (`fingap`, `orderEmb_sq_le`) + the double-sum identity (`sum_sub_sq_double`) + the
  consecutive closed form (`closed_form`, via `sum_range_id2`, `sum_range_sq6`).
- **`Theorem1_of_moments`** — a dissociated set satisfies `4ⁿ − 1 ≤ 3 ∑ aᵢ²`
  (i.e. `∑ aᵢ² ≥ (4ⁿ−1)/3`). Proved from `varLB` applied to the subset-sum image
  (card `2ⁿ`), **modulo** the two *standard* second-moment identities supplied as
  hypotheses `hI1`, `hI2`:
  `2 ∑_S T(S) = 2ⁿ ∑ aᵢ` and `4 ∑_S T(S)² = 2ⁿ ((∑ aᵢ)² + ∑ aᵢ²)`
  (each element lies in half the subsets; each pair `i≠j` in a quarter). These are
  elementary subset-counting facts; isolating them keeps the *reduction* fully verified.
  The parity factor of the `2ℤ`-coset argument in `THEOREMS.md` is absorbed into `hI2`,
  which is why the generic (spacing-1) `varLB` yields the sharp `(4ⁿ−1)/3`.

## Honest scope

These are **classical** bounds (Erdős–Moser / Bae–Guy second-moment floor), re-proved for
verification — not new mathematics; the sharp record `√(2/π)` is **not** formalised (see
`../THEOREMS.md`). What is new here is the machine-checked proof object. Remaining elementary
step to a fully standalone Theorem 1: discharge `hI1`, `hI2` (subset-counting in Mathlib).

## Build / verify

```
elan toolchain install $(cat lean-toolchain)   # once
lake exe cache get                              # download Mathlib oleans
lake build                                      # checks the proofs; prints the axiom audit
```
