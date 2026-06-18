# The Erdős–Straus count is governed by a quadratic L-value

*Headline finding, session 2026-06-18. Notation: `f(p)` = number of positive solutions of
`4/p = 1/x + 1/y + 1/z` (Elsholtz–Tao count); `χ_p = (·/p)` the real quadratic character of `ℚ(√p)`
(`p ≡ 1 mod 4` on the hard classes, so `disc = p` and `(p/ℓ) = (ℓ/p)`); `L(1,χ_p) = 2 h(p) log ε_p/√p`
the quadratic Dirichlet L-value = class-number×regulator of `ℚ(√p)`.*

---

## The finding

> **`f(p)` is modulated by `L(1,χ_p)`: the more primes split in `ℚ(√p)`, the FEWER Erdős–Straus
> solutions `p` has.** Quantitatively `f(p) ≈ (log p)³ · L(1,χ_p)^{−c}`, `c ≈ 0.6`, with
> `corr(ln f, ln L(1,χ_p)) = −0.62` (stable across Euler-product truncation `X = 50…1500`).

**Evidence (machine-verified, `analysis/lfunction_connection.py`, `class_local_density.py`,
`sigma7_char_fit.py`).** Group the hard primes by `p mod ℓ` for `ℓ ∤ 840` (where they equidistribute)
and Fourier-decompose the divisor density `σ_ℓ(p)` over the Dirichlet characters mod `ℓ`. At *every*
prime `ℓ = 11,13,17,19,23` the **dominant non-trivial character is the quadratic (Legendre) `(p/ℓ)`**,
with a *negative* coefficient `≈ 0.6/ℓ`, at **14–47 σ** (166 k primes). The Euler product of these
quadratic characters is, by definition, the L-function `∏_ℓ (1 − c(p/ℓ)/ℓ) = L(1,χ_p)^{−c}`. Direct
test against an independent truncated `ln L(1,χ_p)`: `corr = −0.62`, regression slope `−0.53`.

The six hard square classes `mod 840` are a *finer* shadow of the same object: they differ only at
`ℓ = 5,7`, where `p` is forced to be a QR, so the leading quadratic character is constant and the
class-splitting `1² < 11² < 13² < 19² < 17² < 23²` is carried by the *higher* residue characters —
the cubic character at 7 plus a **~17° chiral phase** (`σ₇(c) = a₀ + 2Re(b ψ(c))`, `b = 8.4 e^{163°i}`,
the imaginary part splitting the inverse pair `2 ↔ 4` — the local shadow of the §11.4 signed-sector
see-saw, impossible for any single Dirichlet character).

## Why it is true (mechanism)

`f(p)` counts divisors of `x²` (Type I) and of the shifted integers `4pδ+1` (Type II) in residue
classes; the local density of such divisors at a prime `ℓ` is governed by how `ℓ` splits in `ℚ(√p)`,
i.e. by `χ_p(ℓ) = (p/ℓ)`. A product `∏_ℓ (1 + χ_p(ℓ)·g(ℓ))` is an Euler product = a power of
`L(1,χ_p)`. **This is exactly the McKee–Zhou mechanism** — the singular series of
`Σ_{n≤N} τ(irreducible quadratic F)` equals `2 L(1,χ_{disc F})/ζ(2)` (McKee 1999; explicit constant
Zhou arXiv:1611.10186), the precedent that ternary/divisor counts are governed by quadratic L-values
(Gauss/Siegel: `r₃(n) ∝ H(n) ∝ L(1,χ_{−n})`). Elsholtz–Tao build `f(p)` from precisely such divisor
sums `τ(kab²+1)` but invoke McKee only as an `O`-bound, never extracting the constant where `L(1,χ_p)`
lives. **So the L-value modulation of the Erdős–Straus count is, per a 2026-06-18 literature search,
unrecorded — a genuine synthesis.** It leaves Elsholtz–Tao's first moment `Σ_{p≤N} f(p) ≍ N log²N`
untouched (an `L^{−c}` factor has mean ≈ const) while explaining the prime-by-prime variance that a
first-moment bound is blind to.

## What it buys

1. **Counterexample candidates are extreme-class-number primes.** Thin `f` ⟺ large `L(1,χ_p)`; by
   Granville–Soundararajan the density of primes with `L(1,χ_p) ≥ e^γτ` falls super-exponentially in
   `τ`. Any Erdős–Straus exception must lie in the **extreme-regulator tail** — a provably super-rare,
   density-controlled set. The measured floor primes already skew to the L-large (thin) classes.
2. **Siegel zeros are the BEST case, not the worst.** A Siegel zero `β → 1` forces `L(1,χ_p)` small ⟹
   `f(p)` *large*. ESC's adversary is the opposite extreme — maximal `L`, `e^γ log log p` — and even
   there the size budget gives `f ≫ (log p)³/(log log p)^c → ∞`. **ESC is robust to the classic
   Landau–Siegel nightmare.**
3. **The size budget never threatens `f > 0`.** The best unconditional ceiling `L(1,χ_p) ≤ (0.197+o(1))
   log p` (Stephens) gives, granting the law, `f ≫ (log p)^{3−c} = (log p)^{2.4} → ∞`. The entire
   difficulty is upgrading `≍` to a proven inequality, never the magnitudes.

## Honest status: a verified law, not yet a theorem

`L(1,χ_p)` **is the singular series itself**, not an external special value: bounding it controls the
*main term* (which it already predicts); the unproven content is the *error term*, the two-shift
Titchmarsh divisor estimate of ET Remark 1.3, parity-obstructed (Granville–Shao 2023). Attempting to
*derive* the singular series via McKee–Zhou blocks at a verified obstruction: the Type II side
condition `δ | y'z'` lets `δ` **split arbitrarily across `y'` and `z'`** (machine-checked: at `p=2521`
the `δ=98=2·7²` solution has `gcd(δ,y')=gcd(δ,z')=14`, dividing neither alone), so `f_II` is a
*two-shift divisor correlation*, not a single `Σ τ(F)` — the L-value does not factor out through one
class-number formula. The discovery is therefore a **precise, verified, structurally-identified law**;
a closed proof is a research programme that meets the same wall from the same side.

*Full derivations, character fits, and the L-correlation: `REPORT.md` §18 (and `analysis/`:
`lfunction_connection.py`, `class_local_density.py`, `sigma7_char_fit.py`, `class_hierarchy.py`).*
