# Executing the Henriot majorant: it closes the primitive shadow, not the bulk

*Session 2026-06-20 (cont.). REPORT §20. Follows §19 (the second moment is irreducibly off-diagonal).*

---

## The attempt

§18.7 called `Σ_{p≤N} f(p)² ≪ N(log N)⁵` "winnable in principle via Nair–Tenenbaum / Henriot." This note
*executes* it against Henriot's actual theorem (arXiv:1102.1643, Thm 1 & 3). Henriot bounds
`Σ_n F(|Q₁(n)|,…,|Q_k(n)|)` for **fixed** polynomials `Q_i` and `F` in Shiu's class — so it needs `f_II(p)`
to be `F(`fixed poly`(p))`.

## A clean new identity (machine-verified, `analysis/primitive_typeII.py [A]`, 0 mismatches)

A Type II solution is a pair `(y',z')` with `m := 4y'z'−y'−z' = p·δ`. The **primitive** (`δ=1`) ones are
exactly
> `(4y'−1)(4z'−1) = 4p+1`  ⟺  the divisors `u ≡ 3 (mod 4)` of `4p+1`.

So `f_II^{(1)}(p) = #{u | 4p+1 : u≡3 (4), u≤√(4p+1)}` is a **single-shift** divisor function of the fixed
linear form `4p+1`; the full count `f_II(p) = Σ_δ r_δ(p)` runs over the shifts `4pδ+1`.

## What Henriot closes — rigorously

`Q(p)=4p+1` linear, `F=τ²∈M` ⇒ Shiu/Henriot gives, parity-free and unconditional,
> `Σ_{p≤N} f_II^{(1)}(p)²  ≤  Σ_{p≤N} τ(4p+1)²  ≪  N(log N)³.`
(Machine-checked true exponent `~ N(log N)^{1.1}`, well inside.) A genuine rigorous bound on the primitive
Type II second moment.

## What it does NOT close — and why (the wall)

The primitive part is a **vanishing** slice: `f_II^{(1)}/f_II ≈ C/(log p)² → 0` (machine-verified, the
`frac·(log p)²` column flat at `≈3.6` over 12 octaves), since `f_II^{(1)}~log p` but `f_II~(log p)³`. The
bulk needs the shifts `4pδ+1` with `δ ≤ 6p²` **coupled to `p`** (only `~(log p)³` realised, and which ones
depends on `p`). Per fixed `(δ₁,δ₂)` Henriot applies (`Σ_p τ(4δ₁p+1)τ(4δ₂p+1) ≪ N(log N)·G`), but summing
over all `δ ≲ N²` overcounts by powers of `N`; keeping only realised shifts is bounding `f_II` itself —
circular.

> **Off-the-shelf Henriot bounds only the `δ=1` primitive shadow. The bulk `Σf² ≍ N(log N)⁵` is the coupled
> multi-shift δ-correlation — the same δ-split that blocks McKee–Zhou (§18.6), now obstructing the majorant.**

## Honest verdict (corrects §18.7)

The upper bound is **true** (numerics `N(log N)^{5.3}`) and parity-safe in principle, but **not** an
off-the-shelf Henriot application. The bulk needs genuine multi-shift / 2D additive-divisor technology
(de la Bretèche–Browning binary-form divisor machinery, summing over the conic `4y'z'≡y'+z' (mod p)` with
realised-shift control) — research-level, and the asymptotic/lower-bound is parity-blocked as everywhere.
Even completed, the payoff is Cauchy–Schwarz positive proportion `≤ Vaughan`. Deliverables: the primitive↔
divisors-of-`4p+1` identity, and the rigorous `Σ f_II^{(1)2} ≪ N(log N)³`. Reproduce: `analysis/primitive_typeII.py`.
