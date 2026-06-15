# Erdős #1 — the second-moment floor, verified (calibrated exposition)

**Status (honest, after council review 2026-06-15).** The results below are *correct
and machine-checked*, but they are **classical** — the second-moment / variance floor of
the Erdős–Moser / Bae–Guy era, **not new mathematics**. Corollary 2 is a one-line
rearrangement of Theorem 1. The genuinely new content of this subproject is the
*obstruction map* in `NOTES.md` (the σ^{2/3} critical window, the Gaussian-vs-packed
two-corner barrier, the `O(log σ)` shattering) — **not** these bounds. This file is a
clean, self-contained, re-checkable account of the floor and of exactly where it stops,
and a Lean-ready target. All claims re-checked by `verify_theorems.py`.

**Setup.** `A = {a₁ < … < aₙ} ⊂ ℤ₊` is **dissociated**: the `2ⁿ` subset sums
`σ(S) = Σ_{i∈S} aᵢ` are pairwise distinct. `N = aₙ`. Let `ε₁,…,εₙ` be i.i.d. uniform in
`{−1,+1}`, `X = Σ εᵢaᵢ`, `σ² = Σ aᵢ²`. The conjecture (Erdős, \$500) is `N ≥ c·2ⁿ`; the
record is `N ≥ (√(2/π) − o(1))·2ⁿ/√n` (Elkies–Gleason; Dubroff–Fox–Xu 2021).

Two facts used throughout:
- **(D1)** `X` takes `2ⁿ` distinct values, each with probability `2⁻ⁿ`. *Proof.*
  `X = 2σ(S) − σ(A)`, `S = {i : εᵢ=+1}`, an affine image of the subset sum. ∎
- **(D2)** every value of `X` is `≡ σ(A) (mod 2)`, so they are `2ⁿ` distinct integers in
  one coset of `2ℤ`.

---

## Lemma 0 (Fourier characterisation of dissociativity)

> `(1/2π) ∫_{−π}^{π} ∏ᵢ cos²(aᵢt) dt = Σ_k P(X=k)² ≥ 2⁻ⁿ`, with **equality iff `A` is
> dissociated**.

*Proof.* `f̂(t)=E[e^{itX}]=∏ᵢcos(aᵢt)`; Parseval on `ℤ` gives `Σ_k f(k)²=(1/2π)∫∏cos²`.
Cauchy–Schwarz: `1=(Σ_{supp}f)² ≤ |supp|·Σf²`, so `Σf² ≥ 1/|supp| ≥ 2⁻ⁿ`, with equality
iff `|supp|=2ⁿ` (distinct). ∎

Standard. Worth recording as a clean *iff*; it is also the object the literature's sharp
constants exploit **quantitatively** (see "the record" below) — here it is used only
qualitatively.

---

## Theorem 1 (variance floor; classical — tight for the variance, not for `N`)

> For every dissociated `A`,  **`Σ aᵢ² ≥ (4ⁿ − 1)/3`**,  with equality **iff
> `A = {2⁰, 2¹, …, 2ⁿ⁻¹}`** (the powers of two) — *uniquely*.

*Proof.* `Var(X) = Σ aᵢ²` (independence, `E εᵢ=0`). By (D1)–(D2), `X` is uniform on a set
`V` of `m=2ⁿ` distinct integers in a coset of `2ℤ`; sorting `v_(1)<…<v_(m)` gives
`v_(j) − v_(i) ≥ 2(j−i)`. With the identity `Σ_i(v_i−v̄)² = (1/m)Σ_{i<j}(v_i−v_j)²`,

  `m·Var(X) = Σ_i(v_(i)−v̄)² ≥ (1/m)·4·Σ_{i<j}(j−i)² = (1/m)·4·m²(m²−1)/12 = m(m²−1)/3,`

so `Var(X) ≥ (m²−1)/3 = (4ⁿ−1)/3`  (using `Σ_{i<j}(j−i)² = m²(m²−1)/12`). ∎

**Equality is unique.** Equality forces `v_(j)−v_(i)=2(j−i)` for all `i,j`, i.e. the
signed sums are an exact step-2 arithmetic progression, equivalently the subset sums are
exactly `{0,1,…,2ⁿ−1}`. The unique set whose subset sums tile `{0,…,2ⁿ−1}` is
`{1,2,4,…,2ⁿ⁻¹}` (binary representation). So "powers of two" is *forced*, not an example.

This is the classical second-moment floor (Erdős–Moser era). **"Tight" here means tight
for the variance `Σaᵢ²`** — it does *not* make the `N`-bound below tight; the `√n` gap to
the conjecture survives intact. Note the extremiser is the *maximum-`N`* family
(`aₙ=2ⁿ⁻¹`), irrelevant to the conjecture's hard, minimum-`N` instances.

---

## Corollary 2 (the conjecture in the easy / lacunary regime)

> If `A` is dissociated and `Σ aᵢ² ≤ K·aₙ²`, then  **`N = aₙ ≥ √((4ⁿ−1)/(3K))`**  (an
> *exact* inequality). For any family with `K = O(1)`, `N ≥ c·2ⁿ` with `c = 1/√(3K)`.

*Proof.* `K·aₙ² ≥ Σ aᵢ² ≥ (4ⁿ−1)/3` (Theorem 1). ∎

This is Theorem 1 rearranged (`K = σ²/aₙ² ∈ [1,n]`). **Honest caveat:** `K=O(1)` means
`σ ≍ aₙ` — the lacunary/geometric regime where the top element already carries the
ℓ²-mass, so *the hypothesis morally assumes the conclusion*. The hard
near-Gaussian/comparable case is exactly `K ≍ n` (e.g. Conway–Guy), where this yields only
`2ⁿ/√(3n)`. So Corollary 2 settles the easy regime and *locates the boundary* of the
difficulty; it is **not progress on the open problem**. (It is *tight* in its own regime:
powers of two have `K → 4/3` and give `N ≥ 2ⁿ⁻¹`, exactly `N`.)

---

## Theorem 3 (the `1/√3` second-moment bound — Bae / Guy)

> For every dissociated `A`,  **`N ≥ √((4ⁿ−1)/(3n)) = (1/√3)·2ⁿ/√n·√(1−4⁻ⁿ)`**  (*exact*).

*Proof.* `n·aₙ² ≥ Σ aᵢ² ≥ (4ⁿ−1)/3` (Theorem 1). ∎

Constant `1/√3 = 0.5774`. This is the **classical** second-moment lower bound (attributed
to Bae and to Guy), the `K=n` case of Corollary 2, and the **ceiling of the pure
second-moment method**: powers of two saturate the floor, so no second-moment refinement
can beat `1/√3`. The inequality is *exact per `n`* — no `o(1)` is needed (it was previously
written with a cosmetic `−o(1)` to mimic the record's shape; dropped).

---

## The record, and what is / isn't claimed

The sharp record `N ≥ (√(2/π) − o(1))·2ⁿ/√n`, `√(2/π) = 0.7979 (> 1/√3)`, is
**Elkies–Gleason / Dubroff–Fox–Xu — cited, not reproved**. It comes from using Lemma 0
*quantitatively* (bounding the `cos²` integral by its Gaussian peaks at `t=0,π` — the
anti-concentration / local-CLT refinement of the *same* `σ`-floor), beyond the elementary
method here. The constant ladder `¼ → … → 1/√3 → √(3/2π) → √(2/π)` is monotone and `1/√3`
is a known lower rung. **We claim no improvement and no progress on the open conjecture.**
The value-add of this subproject over the cited literature is the `NOTES.md` barrier map
and Lemma 0's clean iff-form — *not* the bounds in this file.

---

## Where the elementary method could honestly go (not done here)

- **Lemma 0 quantitatively** (the Elkies/Lindsey integral): isolate the `t=0,π` Gaussian
  bumps of `∫∏cos²` — the elementary route `1/√3 → 1/√π → √(3/2π)`.
- **A multi-moment argument** (combine `Σaᵢ²` with `Σaᵢ⁴`) to enlarge Corollary 2's class
  from `K=O(1)` toward `K=o(n)` — the only direction here that would touch new sets.
- **Lean-formalise Lemma 0 + Theorem 1** (crisp extremal; `formal-conjectures`'
  `ErdosProblems/1.lean` carries this bound as `sorry`). The genuine, finite value-add.

---

## Machine verification

`verify_theorems.py` (`PYTHONNOUSERSITE=1 python3 verify_theorems.py`) checks, on powers
of two, Conway–Guy sets (n≤20), and brute-force optimal sets (n≤7): Lemma 0 (numerically,
dissociated vs not), Theorem 1 (with equality, ratio 1.000000, only for powers of two),
Corollary 2 (the bound, reporting `K` per family — `pow2` `K→4/3`, Conway–Guy `K↑`), and
Theorem 3. All assertions pass.
