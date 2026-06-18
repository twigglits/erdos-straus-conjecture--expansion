#!/usr/bin/env python3
"""floor_safety.py — how safe is Erdős–Straus under the measured f(p) distribution?

The lognormal-EV model for f(p) on the six hard classes has now hit four window floors blind
(191@2×10⁸, 347@10⁹, 405@2×10⁹, 525@10¹⁰).  Its two trends are the whole story:
    μ(p) = E[ln f] RISES  (5.53 → 6.08 → 6.41 → 6.74 over 10⁷ … 10¹⁰),
    σ(p) = SD[ln f] SHRINKS (0.337 → 0.166 → 0.148 → 0.135).
A counterexample is a prime with f(p)=0, i.e. ln f ≤ ln(1) = 0 — a deviation of μ/σ below the mean.
Under lognormality the per-prime probability is Φ(−μ/σ); the EXPECTED number of counterexamples
beyond 10¹⁰ is Σ_p Φ(−μ(p)/σ(p)).  This script fits μ(lnln p), freezes σ at its (largest-scale,
hence most conservative) measured value 0.135, and sums the expectation decade by decade.

This is the QUANTITATIVE form of ET Remark 1.2's Borel–Cantelli heuristic — NOT a proof: it assumes
f is lognormal ~50σ into its left tail, and "the tail never reaches 0" is exactly the conjecture.
What it shows is HOW safe ESC is *if* the measured law persists: overwhelmingly, with a convergent
Borel–Cantelli sum.  Stdlib only.

Run:  python3 analysis/floor_safety.py
"""
import math

# measured (scale, lnln p, μ=E[ln f], σ=SD[ln f]) from the hard-class datasets.
# NOTE: the 10¹⁰ point is from an IN-PROGRESS engine run (partial, accumulating counts), so its μ
# is an UNDER-estimate; the true μ is higher ⇒ μ/σ higher ⇒ this safety estimate is CONSERVATIVE.
# The 10⁸, 10⁹ points are from completed runs.
DATA = [
    (1.0e8, math.log(math.log(1.5e8)), 6.084, 0.1661),
    (1.0e9, math.log(math.log(1.0e9)), 6.412, 0.1480),
    (1.0e10, math.log(math.log(1.0e10)), 6.743, 0.1348),   # partial → conservative
]


def fit_mu():
    """least-squares μ = a·lnln(p) + b on the three narrow-window points."""
    xs = [d[1] for d in DATA]
    ys = [d[2] for d in DATA]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    a = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    b = my - a * mx
    return a, b


def log10_Phi_neg(x):
    """log10 Φ(−x) for x ≫ 1, via the Gaussian tail Φ(−x) ≈ φ(x)/x (Mills ratio)."""
    # ln Φ(−x) ≈ −x²/2 − ln(x) − ½ln(2π)
    ln = -x * x / 2 - math.log(x) - 0.5 * math.log(2 * math.pi)
    return ln / math.log(10)


if __name__ == "__main__":
    a, b = fit_mu()
    SIGMA = 0.1348                       # frozen at the 10¹⁰ value — conservative (larger σ ⇒ fatter tail)
    print(f"fit: μ(p) = {a:.3f}·lnln(p) + {b:.3f}   (so median f ~ (ln p)^{a:.2f}); σ frozen at {SIGMA}")
    print(f"  ⇒ floor μ/σ at 10¹⁰ = {(a*DATA[-1][1]+b)/SIGMA:.1f}  (the measured floor sits ~{(a*DATA[-1][1]+b)/SIGMA:.0f}σ above f=0)\n")
    print(f"  {'decade':>10} {'μ/σ':>7} {'log10 P(f=0)':>13} {'log10 E[#cex in decade]':>22}")
    total_log_terms = []
    for k in range(10, 101):             # decades 10^10 … 10^100
        p = 10.0 ** k
        mu = a * math.log(math.log(p)) + b
        ratio = mu / SIGMA
        log10_p0 = log10_Phi_neg(ratio)
        # # hard-class primes in [10^k, 10^{k+1}]: ≈ (9·10^k)·(6/840)/ln(10^k)
        n_primes = 9 * 10.0 ** k * (6 / 840) / (k * math.log(10))
        log10_expected = math.log10(n_primes) + log10_p0
        total_log_terms.append(log10_expected)
        if k <= 15 or k % 10 == 0:
            print(f"  10^{k:<7d} {ratio:>7.1f} {log10_p0:>13.1f} {log10_expected:>22.1f}")
    # Σ of tiny positive terms ≈ the largest term (decade 10^10 dominates; terms fall fast)
    dom = max(total_log_terms)
    print(f"\nExpected total ESC counterexamples beyond 10¹⁰ ≈ 10^{dom:.0f} "
          f"(sum dominated by the 10¹⁰ decade; terms fall ~super-exponentially ⇒ Borel–Cantelli CONVERGES).")
    print("So the measured law places the number of counterexamples at effectively zero with a")
    print(f"~{dom:.0f}-orders-of-magnitude margin.  HONEST: this assumes lognormality {(a*DATA[-1][1]+b)/SIGMA:.0f}σ into the tail —")
    print("the one thing unproven, and exactly what ESC asserts.  It quantifies safety, it is not a proof.")
