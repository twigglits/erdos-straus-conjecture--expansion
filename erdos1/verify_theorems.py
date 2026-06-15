#!/usr/bin/env python3
"""Machine verification of the rigorous results in THEOREMS.md.

Checks, on powers of two / Conway-Guy / brute-optimal dissociated sets:
  Lemma 0  : (1/2pi) int prod cos^2(a_i t) dt = 2^-n   (=, dissociated;  >, not)
  Theorem 1: sum a_i^2 >= (4^n-1)/3,  equality for powers of two
  Corollary 2: top-heavy bound a_n >= sqrt((4^n-1)/(3K)), K = sum a_i^2 / a_n^2
  Theorem 3: a_n >= sqrt((4^n-1)/(3n))   (the 1/sqrt3 * 2^n/sqrt n bound)
All asserts must pass.

Run:  PYTHONNOUSERSITE=1 python3 verify_theorems.py
"""
import math
import numpy as np
from hunt import conway_guy_set, powers_of_two, optimal_set, is_dissociated


def fourier_integral(A, M=4_000_001):
    """(1/2pi) int_{-pi}^{pi} prod cos^2(a_i t) dt, by fine trapezoid."""
    t = np.linspace(-math.pi, math.pi, M)
    integrand = np.prod(np.cos(np.outer(t, np.array(A, float))), axis=1) ** 2
    return np.trapz(integrand, t) / (2 * math.pi)


def check_lemma0():
    print("Lemma 0 — Fourier characterisation of dissociativity:")
    for A in ([3, 5, 6, 7], [6, 9, 11, 12, 13], [1, 2, 4, 8]):
        n = len(A); val = fourier_integral(A); tgt = 2.0 ** -n
        ok = abs(val - tgt) < 1e-6
        print(f"  dissoc {A}: integral={val:.8f}  2^-n={tgt:.8f}  ==? {ok}")
        assert ok and is_dissociated(A)
    A = [1, 2, 3]; val = fourier_integral(A)   # NOT dissociated (1+2=3)
    ok = val > 2.0 ** -3 + 1e-4
    print(f"  NOT-dissoc {A}: integral={val:.8f} > 2^-n=0.125 ? {ok}  (excess counts 1+2=3)")
    assert ok and not is_dissociated(A)
    print("  PASS\n")


def families(nmax_cg=20):
    fams = []
    for n in range(2, nmax_cg + 1):
        fams.append(("pow2", powers_of_two(n)))
        fams.append(("CG", conway_guy_set(n)))
    for n in range(2, 8):                       # brute optimal (slow past 7)
        fams.append(("opt", optimal_set(n)[1]))
    return fams


def check_theorems():
    print("Theorems 1–3 on pow2 / Conway-Guy (n<=20) / optimal (n<=7):")
    print(f"  {'fam':5} {'n':>3} {'sum a^2':>14} {'(4^n-1)/3':>14} "
          f"{'T1':>4} {'K':>7} {'T2 c=1/sqrt(3K)':>16} {'T3':>4}")
    worst_t1_gap = math.inf
    for name, A in families():
        n = len(A); s2 = sum(a * a for a in A); an = max(A)
        floor = (4 ** n - 1) // 3
        t1 = s2 >= floor                                   # Theorem 1
        if name == "pow2":
            assert s2 == floor, ("pow2 not tight", n, s2, floor)   # equality
        K = s2 / an ** 2
        t2 = an ** 2 >= (4 ** n - 1) / (3 * K) - 1e-6      # Corollary 2 (== T1)
        t3 = an >= math.sqrt((4 ** n - 1) / (3 * n)) - 1e-9  # Theorem 3
        assert t1 and t2 and t3, (name, n, t1, t2, t3)
        worst_t1_gap = min(worst_t1_gap, s2 / floor)
        if name == "pow2" or n <= 7:
            print(f"  {name:5} {n:>3} {s2:>14} {floor:>14} "
                  f"{str(t1):>4} {K:>7.3f} {1/math.sqrt(3*K):>16.4f} {str(t3):>4}")
    print(f"\n  Theorem 1 tight ratio (min sum a^2 / floor over all sets) = "
          f"{worst_t1_gap:.6f}  (==1 means some family is exactly tight)")
    print("  PASS — Theorem 1, Corollary 2, Theorem 3 hold on every set tested.\n")


if __name__ == "__main__":
    check_lemma0()
    check_theorems()
    print("ALL CHECKS PASS — THEOREMS.md is machine-verified on the test families.")
