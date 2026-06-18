# The Erdős–Straus solution count f(p): three results

*A focused distillation (2026-06-18) of the genuinely-new, citable content from this
repository's `REPORT.md`, separated cleanly into what is **proved**, what is **heuristic**,
and what is **measured**. Notation as in Elsholtz–Tao (ET), J. Aust. Math. Soc. 94 (2013):
f(p) = #{(x,y,z) : 4/p = 1/x+1/y+1/z, x≤y≤z}, with the Type I/II split f = 3f_I + 3f_II.*

---

## Result 1 (reduction, exact). The second moment of f_II is a two-shift Titchmarsh sum.

**Setup.** A Type II solution of 4/p corresponds bijectively to a triple (y′,z′,δ) ∈ ℕ³ with
> (4y′−1)(4z′−1) = 4pδ + 1,  δ | y′z′,  p = [(4y′−1)(4z′−1) − 1]/(4δ),

i.e. f_II(p) counts divisors u ≡ 3 (mod 4) of the shifted integers {4pδ+1}_δ with a divisibility
side-condition. (Machine-verified bijection, `analysis/second_moment.py`.)

**Statement.** Writing r_δ(p) = #{Type II solutions of 4/p with that δ}, so f_II(p) = Σ_δ r_δ(p),
> **Σ_{p≤N} f_II(p)² = Σ_{δ₁,δ₂} Σ_{p≤N, prime} r_{δ₁}(p) · r_{δ₂}(p)**,

a correlation of two divisor-type functions of the linear forms 4δ₁p+1, 4δ₂p+1 over primes — a
**two-shift Titchmarsh divisor problem**. Measured structure (small p): the sum is **98.5%
off-diagonal** (δ₁ ≠ δ₂), so it is not reducible to the tractable single-shift diagonal.

**Status.** The reduction is *exact and elementary* but, to our knowledge, unrecorded. It makes
ET's Remark 1.3 ("the second moment lies out of reach… the level of the divisor sums is too
great") **explicit**: the required level of distribution is conductor ~p² with two simultaneous
shifts over primes — past Bombieri–Vinogradov (p^{1/2}), past the ternary-divisor records
(Sharma p^{1/2+1/30}; Aydemir–Boran p^{8/11} averaged), and not delivered even by the
GRH-conditional Titchmarsh power-savings (Drappeau; Assing–Blomer–Li). A pointwise version is
*additionally* parity-blocked (Granville–Shao). **This is the precise analytic wall.**

## Result 2 (heuristic + measured). f(p) ~ c·(log p)³ from the geometry of the Cayley cubic.

Applying the Browning–Wilsch integral-points heuristic (Selecta Math. 31 (2025); for a log-K3
cubic surface, N°_U(B) ~ c·(log B)^{ϱ_U + b}) to the Erdős–Straus surface 4xyz = n(xy+yz+zx),
whose open part is V_p ≅ 𝔾_m² (Bright–Loughran, unit rank 2) with a boundary triangle of lines:
calibrated against the authors' own Markoff computation, the invariants give **ϱ_U + b = 3**, so
with height B ≍ p (denominators are polynomial in p),
> **f(p) ~ c·(log p)³.**

This equals the Elsholtz–Tao *average* order (Σ_{p≤N} f(p) ≍ N log²N ⟹ average f(p) ≍ log³p).
**Machine-check** (`analysis/growth_law.py`): the median of f(p) per dyadic window over
3×10³ ≤ p ≤ 2×10⁹ fits ln(median) = k·ln ln p + b with **k = 3.03** — the exponent 3 to ~1% over
six decades.

**Status.** Heuristic (a growth-law prediction), apparently the first application of this machine
to the Cayley cubic. It recovers a *known average*; it does **not** reach existence: a direct
count shows the Cayley cubic has exactly ℓ²+1 points mod ℓ (and (ℓ−1)(ℓ−2)+1 off-axis)
**independent of n's quadratic-residue status** (ℓ ≤ 23), so neither the exponent nor the
constant distinguishes the hard square classes. The square-class suppression is a finer global
stratum/parity effect (Yamamoto), invisible to the geometry's leading order.

## Result 3 (measured). Channel independence ⟹ the Borel–Cantelli safety heuristic is empirically clean.

Over 4000 hard primes ~10⁶, the distinct "channels" that produce solutions fire near-independently:
corr(K1,K2) = −0.04, corr(K1,A3) = +0.09, corr(K2,A3) = +0.01 (K1: 4p+1 has a prime factor
≡ 3 mod 4; K2: 8p+1 has one ≡ 7 mod 8; A3: (p+3)/4 has one ≢ 1 mod 3). Each fires for ~half of
hard primes and positively predicts f (corr(K_i, ln f) = +0.14…+0.32). Consequently f is
lognormal/over-dispersed from *within*-channel spread, and **f = 0 requires every near-independent
channel to fail simultaneously**, of probability ≈ the product of the per-channel failure rates,
each → 0 (Landau–Ramanujan). This is the measured form of the independence assumption underlying
ET Remark 1.2's Poisson/Borel–Cantelli argument. Empirically the solubility "channel depth" (the
smallest a = 4x−p giving a solution) stays ≤ 55 over 10⁶–10¹⁰ with no upward trend, and explicit
solutions exist for adversarial square-class primes verified to **10⁵⁰** (`analysis/find_solution.py`).

---

## What this does and does not do

It does not prove or disprove Erdős–Straus, and no fabrication is offered. It (i) writes down the
explicit second-moment reduction and pins the exact analytic input the problem needs; (ii) gives a
new heuristic derivation of f(p)'s growth law from arithmetic geometry, machine-checked; (iii)
measures the channel independence that makes the conjecture "safe." The single live seam remains a
**parity-breaking two-shift Titchmarsh estimate** — beyond current technology, and the place every
independent angle (sieve, geometry, dynamics, conditionals, continued fractions) terminates.

*Engines (this session): `engines/fp128.cu` (GPU, 128-bit, native sm_120) and
`engines/fp_single.c` (CPU) lift the per-prime counting frontier past 2×10⁹; exact f(p) at 10¹⁰ is
cross-validated between them. Full derivations, machine checks, and references: `REPORT.md`
§§14, 16, 17.*
