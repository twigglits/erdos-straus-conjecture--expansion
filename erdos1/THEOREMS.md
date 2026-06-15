# Erdős #1 — rigorous partial results

Complete, self-contained, machine-checkable theorems for the distinct-subset-sums
problem. These are *finite and proven* (not the open conjecture). Companion to the
experimental account in `NOTES.md`; all claims are re-checked by
`verify_theorems.py`.

**Setup.** `A = {a₁ < … < aₙ} ⊂ ℤ₊` is **dissociated**: the `2ⁿ` subset sums
`σ(S) = Σ_{i∈S} aᵢ` are pairwise distinct. Write `N = aₙ = max A`. Let `ε₁,…,εₙ`
be i.i.d. uniform in `{−1,+1}` and `X = Σ εᵢaᵢ` (the signed sum). Put
`σ² = Σ aᵢ²`. The conjecture (Erdős, \$500) is `N ≥ c·2ⁿ` for an absolute `c>0`;
the record is `N ≥ (√(2/π) − o(1))·2ⁿ/√n` (Elkies–Gleason; Dubroff–Fox–Xu 2021).

Two facts used throughout:
- **(D1)** `X` takes `2ⁿ` distinct values, each with probability `2⁻ⁿ`. *Proof.*
  `X = 2σ(S) − σ(A)` where `S = {i : εᵢ = +1}`, an affine image of the subset sum;
  distinct subset sums ⟹ distinct `X`. ∎
- **(D2)** all values of `X` are `≡ σ(A) (mod 2)` (since `εᵢaᵢ ≡ aᵢ`), so they are
  `2ⁿ` distinct integers inside a single coset of `2ℤ`.

---

## Lemma 0 (Fourier characterisation of dissociativity)

> `(1/2π) ∫_{−π}^{π} ∏ᵢ cos²(aᵢt) dt = Σ_k P(X=k)² ≥ 2⁻ⁿ`, with **equality iff `A`
> is dissociated**.

*Proof.* Let `f(k)=P(X=k)`. Its Fourier series is `f̂(t)=E[e^{itX}]=∏ᵢcos(aᵢt)`.
Parseval on `ℤ`: `Σ_k f(k)² = (1/2π)∫_{−π}^{π}|f̂(t)|² dt = (1/2π)∫∏cos²(aᵢt)dt`.
By Cauchy–Schwarz with the `2ⁿ` equally likely sign patterns,
`Σ_k f(k)² ≥ (Σ_k f(k))²/|supp| = 1/|supp| ≥ 2⁻ⁿ`, and `|supp| = 2ⁿ` (equality)
iff the values are distinct, i.e. `A` dissociated. ∎

This is the exact identity used (heuristically) in `NOTES.md`; here it is a clean
two-line lemma and an *iff*.

---

## Theorem 1 (variance floor; tight)

> For every dissociated `A`,  **`Σ aᵢ² ≥ (4ⁿ − 1)/3`**,  with equality iff the
> values of `X` are `2ⁿ` consecutive elements of a coset of `2ℤ` (e.g. `A = {2⁰,…,2ⁿ⁻¹}`).

*Proof.* `Var(X) = Σ Var(εᵢaᵢ) = Σ aᵢ² = σ²` by independence and `E[εᵢ]=0`. By (D1)
`X` is uniform on a set `V` of `2ⁿ` distinct integers (mass `2⁻ⁿ` each); by (D2)
`V` lies in a coset of `2ℤ`, so its sorted elements `v_{(1)}<…<v_{(m)}` (`m=2ⁿ`)
satisfy `v_{(j)} − v_{(i)} ≥ 2(j−i)`. Using the identity
`Σ_i (v_i − v̄)² = (1/m) Σ_{i<j} (v_i − v_j)²`,

  `m·Var(X) = Σ_i (v_{(i)}−v̄)² = (1/m) Σ_{i<j}(v_{(i)}−v_{(j)})²
            ≥ (1/m)·4·Σ_{i<j}(j−i)² = (1/m)·4·m²(m²−1)/12 = m(m²−1)/3.`

Hence `Var(X) ≥ (m²−1)/3 = (4ⁿ−1)/3`. Equality requires `v_{(j)}−v_{(i)}=2(j−i)`
for all `i,j`, i.e. consecutive packing on the coset. ∎

(`Σ_{i<j}(j−i)² = m²(m²−1)/12` is elementary: `Σ_{d=1}^{m−1}(m−d)d²`.)

Powers of two attain equality: `Σ 4^i = (4ⁿ−1)/3`, and their signed sums are exactly
`{−(2ⁿ−1), −(2ⁿ−1)+2, …, 2ⁿ−1}`.

---

## Theorem 2 (the conjecture, for top-heavy sets) — headline

> If `A` is dissociated and **top-heavy**, i.e. `Σ aᵢ² ≤ K·aₙ²` for some `K`, then
>   **`N = aₙ ≥ √((4ⁿ−1)/(3K)) = (1/√(3K))·2ⁿ·(1 − o(1))`.**
> In particular, for any family with `K = O(1)` the **full conjecture holds**:
> `N ≥ c·2ⁿ` with `c = 1/√(3K)`.

*Proof.* Immediate from Theorem 1: `K·aₙ² ≥ Σ aᵢ² ≥ (4ⁿ−1)/3`. ∎

**Scope (honest).** `K = σ²/aₙ² ∈ [1, n]` always (`aₙ² ≤ σ² ≤ n·aₙ²`). The two ends:
- `K = O(1)` ("few large elements carry the ℓ²-mass", e.g. geometric-type sets):
  the conjecture is **proved**, `N ≥ c·2ⁿ`.
- `K ≍ n` (flat / all-comparable, e.g. Conway–Guy, where `K → ~n`): Theorem 2 gives
  only `N ≥ 2ⁿ/√(3n)` — the `√n`-weakened bound. **This is exactly the hard case**
  the record and the open conjecture live in (`NOTES.md` §3–4): near-Gaussian,
  comparable elements. Theorem 2 settles the complementary, easy regime cleanly and
  draws the line precisely at where the difficulty begins.

---

## Theorem 3 (clean self-contained lower bound)

> For every dissociated `A`,  **`N ≥ √((4ⁿ−1)/(3n)) = (1/√3 − o(1))·2ⁿ/√n`.**

*Proof.* `n·aₙ² ≥ Σ aᵢ² ≥ (4ⁿ−1)/3` (Theorem 1), so `aₙ ≥ √((4ⁿ−1)/(3n))`. ∎

Constant `1/√3 = 0.5774`. This is a complete elementary proof of a bound of the
record's *shape* (`2ⁿ/√n`); it is the `K=n` specialisation of Theorem 2 and the
endpoint of the pure second-moment method.

**The record, and what we do/don't claim.** The sharp constant `√(2/π)=0.7979`
(`> 1/√3`) is **Elkies–Gleason / Dubroff–Fox–Xu**, not reproved here — it needs the
near-Gaussian dichotomy + anti-concentration, beyond the elementary variance method.
We cite it. What this study *adds* on top of the cited record is the barrier map of
`NOTES.md` (the `σ^{2/3}` critical window, the Gaussian-vs-packed two-corner
obstruction, the `O(log σ)` shattering) and Lemma 0, which together explain where the
extra `√2` over `1/√3` comes from and why pushing past `√(2/π)` is hard. No proof of
the open conjecture is claimed.

---

## Machine verification

`verify_theorems.py` (run `PYTHONNOUSERSITE=1 python3 verify_theorems.py`) checks, on
powers of two, Conway–Guy sets (to n=20), and brute-force optimal sets (to n=7):
Lemma 0 (numerically, dissociated vs not), Theorem 1 (with equality for powers of
two), Theorem 2 (the top-heavy bound, reporting K per family), and Theorem 3. All
assertions must pass.
