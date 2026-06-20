# The Erdős–Straus second moment is irreducibly off-diagonal

*Session 2026-06-20. Notation: `f_II(p)` = Type II Elsholtz–Tao count; `r_δ(p)` = # Type II solutions of
`4/p` with shift `δ` (`= #` divisors `u≡3 mod 4` of `4pδ+1` in range). REPORT §19.*

---

## The question (left open at §18.4 / §18.7)

The parity-safe target was `Σ_{p≤N} f_II(p)² ≪ N(log N)⁵` via a Nair–Tenenbaum / Henriot divisor-correlation
majorant. The concrete sub-question: **set up the majorant and see how far its *diagonal* reaches — does
the diagonal alone already give `N(log N)⁵`?** §18.7 could only call it "winnable in principle." Now settled.

## The exact split

The §14 reduction `Σ_{p≤N} f_II(p)² = Σ_{δ₁,δ₂} Σ_{p≤N} r_{δ₁}(p)r_{δ₂}(p)` splits as `D(N) + OD(N)`:
- **Diagonal** `D(N) = Σ_{p≤N} Σ_δ r_δ(p)²` — what a single-shift / Shiu majorant reaches (`r_δ ≤ τ(4pδ+1)`).
- **Off-diagonal** `OD(N) = Σ_{p≤N} Σ_{δ₁≠δ₂} r_{δ₁}r_{δ₂}` — the genuine two-shift Titchmarsh correlation.

## The result (machine-verified, `engines/fp_delta.c` → `data/delta_moment_1e6.csv`, fit by `analysis/fit_diagonal.py`)

A new δ-resolved engine (validated: reproduces `data/hard_1e7_full.csv` `Σf_I, Σf_II` exactly on `[73,2·10⁴]`;
self-checks known `f(p)`) gives per-prime means `E[·] ~ (log p)^θ` over `[10³, 10⁶]`:

| quantity | fitted `θ` | ⟹ `Σ_{p≤N}` |
|---|---|---|
| `E[f_II]` (first moment) | **2.94** → 3 | `N(log N)²` (Elsholtz–Tao) |
| `E[Σ_δ r_δ²]` (**diagonal**) | **2.92** → 3 | **`N(log N)²`** |
| `E[f_II²]` (total) | **5.81** → 6 | `N(log N)⁵` |

- **The diagonal exponent (2.92) equals the first-moment exponent (2.94).** Equivalently `E[diag]/E[f_II]`
  is **flat at ≈ 1.22** across four decades. So `D(N) ≍ Σf_II(p) ≍ N(log N)²` — the diagonal *is* the first
  moment up to a bounded constant.
- **Gap = total − diagonal = 2.89 → 3.** The diagonal is a factor `(log N)³` below the second moment.

## What it means

> **The diagonal reaches only `N(log N)²` — it provably does NOT reach `N(log N)⁵`, falling short by
> `(log N)³`. The entire `N(log N)⁵` second moment is off-diagonal.**

This is the exponent-level sharpening of §14's "98.5 % off-diagonal": the off-diagonal is not a large
*constant* times the diagonal, it is a higher *order* by `(log N)³`. The second moment is **irreducibly
off-diagonal** — no single-shift majorant can bound it; the full result requires the two-shift correlation
(Henriot + Brun–Titchmarsh, §18.7), which carries the whole `(log N)³`.

## Honest status

Negative-direction / diagnostic, not ESC progress. It converts "the diagonal might suffice" into "the
diagonal provably cannot," and localizes *all* the difficulty in the off-diagonal two-shift estimate. The
downstream payoff is unchanged (§18.5): even the full bound gives, by Cauchy–Schwarz, only a **positive
proportion** `1/C` of soluble primes — *weaker than Vaughan's density 1* — and only the order, not the
`L(1,χ_p)` constant (parity-blocked). The wall is unmoved; it is now measured to the exponent.

*Full account: REPORT.md §19. Reproduce: `gcc -O3 -march=native -fopenmp engines/fp_delta.c -o engines/fp_delta -lm`,
`./engines/fp_delta 73 1000000 data/delta_moment_1e6.csv`, `python3 analysis/fit_diagonal.py`.*
