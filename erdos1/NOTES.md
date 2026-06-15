# Erdős #1 — the distinct-subset-sums constant hunt

**Problem (Erdős #1, "perhaps my first serious problem", 1931; $500).**
Let `A = {a₁ < … < aₙ} ⊂ ℤ₊` have all `2ⁿ` subset sums distinct (`A` is
*dissociated*). Lower-bound `N = max aᵢ`. Conjecture: `N ≥ c·2ⁿ` (remove the
`√n` from the record). Powers of 2 give `N = 2ⁿ⁻¹`; best construction
`N ≤ 0.22002·2ⁿ` (Bohman). erdosproblems.com/1, OEIS A276661.

**Record lower bound (the constant we are hunting):**
`N ≥ C(n, ⌊n/2⌋) = (√(2/π) − o(1))·2ⁿ/√n`, `√(2/π) = 0.79788`.
Elkies–Gleason (unpublished) = Dubroff–Fox–Xu 2021 (arXiv:2006.12988).
Ladder of constants: ¼ (Erdős–Moser) → 1/√π (Elkies) → √(3/2π) (Aliev) →
√(2/π) (DFX). See `../README`-style note and the parent ESC repo for context;
full recon in the project memory `erdos1-subset-sums-hunt`.

This subproject is the experimental lab + a sharpening of where the difficulty
of beating `√(2/π)` actually lives. **It does not beat the constant** — that is
a hard 95-year-old problem and `√(2/π)` is the natural Gaussian endpoint. What
it does: make the lever precise and measurable, and map the obstruction.

**Rigorous, proven, machine-checked results** — the variance floor
`Σaᵢ² ≥ (4ⁿ−1)/3` (tight), the **full conjecture for top-heavy sets**
(`Σaᵢ² ≤ K·aₙ² ⟹ N ≥ 2ⁿ/√(3K)`), and the clean `N ≥ (1/√3−o(1))·2ⁿ/√n` bound —
are in **`THEOREMS.md`** (proofs) and `verify_theorems.py` (checks). They settle
the easy/top-heavy regime exactly and draw the line at the hard near-Gaussian case
this analysis maps below.

---

## 1. The exact reduction

Work with the signed sum `X = Σ εᵢaᵢ`, `εᵢ = ±1` iid, equivalently the subset
sum `T = Σ_{i∈S} aᵢ` (`X = 2T − Σaᵢ`). Dissociated ⟺ the `2ⁿ` values of `T`
are distinct ⟺ pmf `f(k) = 2⁻ⁿ·1[k is a subset sum]`. Put `σ² = Σaᵢ²`, so
`sd(T) = σ/2`, mean `μ = Σaᵢ/2`.

**Fourier characterisation of dissociativity (verified numerically, hunt.py):**

>  `(1/2π) ∫₋π^π ∏ᵢ cos²(aᵢ t) dt = 2⁻ⁿ`   ⟺  `A` dissociated.

(The integral equals `2⁻ⁿ·#{ε ∈ {−1,0,1}ⁿ weighted : Σεᵢaᵢ = 0}`; dissociated
⟺ only the trivial solution. For `[1,2,3]` it is `1.25·2⁻³`, the excess counting
the collision `1+2=3`.) The integrand `∏cos²(aᵢt)` is two Gaussian-ish revival
bumps of width `~1/σ` at `t = 0` and `t = π` (parity), plus minor resonances;
≈76–80 % of the mass sits in the two bumps for near-Gaussian sets, 97 % for
powers of 2. Extra resonances *raise* `σ` — extremal sets are resonance-minimal.

**The DFX dichotomy.** Far-from-Gaussian dissociated sets already have
`N = Ω(2ⁿ)` (powers of 2: `N = 2ⁿ⁻¹`). The bound `σ ≥ √(2/π)·2ⁿ` is **only** a
*near-Gaussian* statement — so powers of 2 having `σ = 2ⁿ/√3 = 0.577·2ⁿ <
0.798·2ⁿ` is **not** a contradiction; they live in the other branch. The whole
game is the near-Gaussian regime, where the bound combines

- **(1) distinctness:** `P(T ∈ window of length L) ≤ (L+1)·2⁻ⁿ` — tight ⟺
  *consecutive packing* (every integer site in the window is a subset sum);
- **(2) local Gaussian:** `P(|T−μ| ≤ L/2) ≈ √(2/π)·L/σ` — tight ⟺ *locally
  Gaussian*.

Combining and sending `L → ∞` (with `L ≪ σ`) gives `σ ≥ √(2/π)·2ⁿ`, hence
`N ≥ σ/√n ≥ √(2/π)·2ⁿ/√n`.

**The critical scale.** Optimising the combination over `L`, the curvature loss
is `~c(L/σ)²` and the window-edge loss `~1/L`, so the optimal window is

>  `L* ~ σ^(2/3) = (2ⁿ)^(2/3)`,    which is `o(σ)` but `→ ∞`.

At `L*` the relative Gaussian curvature is `~σ^(−2/3) → 0`: **flat (perfect
packing) and Gaussian are compatible to leading order over a window of width
`σ^(2/3)`.** That is exactly why DFX is tight at `√(2/π)` and why beating it is
hard. To improve the constant one must show a dissociated set cannot keep
*perfect packing* over a `σ^(2/3)` window — a packing defect bounded below at
that scale. No such arithmetic obstruction is known.

---

## 2. The lab

| file | what |
|------|------|
| `hunt.py` | core: `is_dissociated`, exact subset-sum pmf (int8 — dissociated ⟹ 0/1 counts, 8× memory cut, feasible to n≈28), `conway_guy_set` (A005318, every set re-verified dissociated), brute-force `optimal_set`, and `measure()` returning the diagnostics below. `python3 hunt.py` runs self-checks. |
| `sweep.py` | sweeps families × n → `sweep.json` + table. |
| `plot.py`  | `fig1_landscape.png`, `fig2_obstruction.png`. |

Run everything with `PYTHONNOUSERSITE=1` (apt matplotlib 3.6.3 + numpy 1.26;
`~/.local` numpy 2.2 crashes it).

Diagnostics per set: `N`, `N√n/2ⁿ` (vs record 0.798), `N/2ⁿ` (vs Bohman 0.22),
`V = σ/2ⁿ` (DFX-tight value 0.798), `gauss_ratio` (smoothed central density /
Gaussian peak; 1 = locally Gaussian), and at the critical scale `Wc = σ^(2/3)`:
`occ_crit` (occupancy) and `run_crit` (longest gap-free run / Wc).

Validation: reproduces A276661 = 1,2,4,7,13,24,44 (brute force = Conway–Guy);
the Fourier `L²` identity `Σf² = 2⁻ⁿ` holds to machine precision; every
Conway–Guy set to n=27 independently verified dissociated.

---

## 3. Findings

**(a) The conjecture looks true; the √n gap is entirely in the proof.**
For the true optimum (Conway–Guy, proven optimal to n≈22) `N/2ⁿ` decreases
toward its limit `0.235`, staying ~constant — so `N ~ c·2ⁿ`, not `2ⁿ/√n`.
Correspondingly `N√n/2ⁿ` *grows* like `0.235√n`, outrunning the flat record line
`√(2/π)` (fig1). The record lower bound is never approached by the actual
optimum.

**(b) The near-Gaussian optimum overshoots the tight variance and never sits on
it.** `V = σ/2ⁿ` for Conway–Guy crosses `0.798` near n=8 and climbs to `1.22`
at n=26 (`V ~ √n`). The DFX-tight regime `V ≡ 0.798` (which would force *all* n
elements into a dyadic band around `2ⁿ/√n`) is not approached by any known
family (fig2a).

**(c) The two tightness conditions are realised by structurally OPPOSITE
families, and nothing bridges them — the visible obstruction.**
The DFX-extremal set must be near-Gaussian (`gauss_ratio → 1`) AND consecutively
packed at scale `σ^(2/3)` (`run_crit = O(1)`). Instead:

- **Conway–Guy** (near-Gaussian, *comparable*: max/min → 2.008 at n=26,
  dissociated, optimal): `run_crit` collapses `2.0 → 3·10⁻⁴` — **shattered**;
  its subset sums near the mean are full of gaps, not an interval (fig2b).
- **Powers of 2** (perfectly packed, `run_crit ≈ 2`): `gauss_ratio` stuck at
  `0.724` — **uniform, never Gaussian** (uniform central density is exactly
  `1/√(6/π) = 0.724` of the same-variance Gaussian peak).

The "Gaussian AND packed" corner is empty for both natural families (fig2c).
Comparability fights dissociativity (an arithmetic progression — maximally
comparable — fails dissociativity at n=4: `{1,4}` and `{2,3}`), which is the
crux of why a near-Gaussian set cannot also pack like an interval.

**(d) The shattering is logarithmic, exponentially below the critical scale**
(`runscaling.py`). The longest run of *consecutive* subset sums near the mean of
Conway–Guy is essentially constant — 51 → 62 as σ grows from `3.7·10³` to
`8.2·10⁷` (n=12→26). Fit `maxrun ~ σ^β` gives `β ≈ 0.02 ≪ 2/3`; the true law is
`maxrun ~ O(log σ) = O(n)` (the max-run-of-successes of a positively-correlated
Bernoulli field at occupancy ≈ 0.66). So near-Gaussian dissociated sets pack
runs only of *logarithmic* length, vs the `σ^(2/3)` the tight bound would need —
short by an exponential factor.

*Caveat (the honest limit of (c)/(d)):* occupancy at the critical window is
≈ 0.50 = `gauss_ratio · √(2/π)/V` exactly — fully explained by Gaussianity and
V, with **no independent arithmetic deficiency**. Because distinctness forces
`#(sites hit) = mass·2ⁿ`, occupancy carries no signal beyond `(Gaussianity, V)`.
The shattering (d) is therefore an **arrangement**-level fact (gap structure),
strictly stronger than the *count* the DFX inequality (1) uses. The unsolved
step is to find a count-level (or new) functional that converts "runs are only
log-length" into a constant improvement.

---

## 4. Honest assessment & open sub-question

`√(2/π)` is very likely the truth of the anti-concentration method; the data is
consistent with the bound being tight *as a method bound* even though no single
set achieves it (the two tightness conditions are split across families). The
genuine open lever, now sharp:

>  **Does there exist a dissociated set whose subset sums perfectly pack (cover
>  every integer) over a window of width `~σ^(2/3)` around the mean, while being
>  locally Gaussian?** Equivalently: is the packing defect at scale `σ^(2/3)`
>  bounded below for near-Gaussian dissociated sets?

A lower bound on that defect of relative size `ε` would improve the constant to
`√(2/π)/(1−ε)`. The structural fact (c) — near-Gaussian ⟹ shattered at the
critical scale — is the encouraging direction, but it is *arrangement*-level
(gap structure) and the current DFX argument only uses the *count* in a window;
turning shattering into a count-level (or new-functional) improvement is the
unsolved step. Honest odds of beating `√(2/π)`: low.

**Next candidates.** (i) Quantify `run_crit` decay rate vs `σ^(2/3)` precisely
(is it `exp(−c·n)`? a power of σ?) and compare to the `σ^(−2/3)` curvature
allowance. (ii) Find/relax a *count-level* functional that sees the shattering
(e.g. weighted window counts, or second-moment of occupancy across shifted
windows). (iii) Search small-n for the dissociated set maximising `run_crit` at
fixed near-Gaussianity — is there a ceiling? (iv) The autocorrelation/positive-
definite variational relaxation gives a clean ≤0.577 σ-bound (powers-of-2 cap),
confirming the σ-route alone cannot reach 0.798 — documents why the dichotomy is
essential.
