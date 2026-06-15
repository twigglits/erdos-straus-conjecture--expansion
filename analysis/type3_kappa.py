#!/usr/bin/env python3
"""Test whether the correction factors kappa_I, kappa_II (REPORT §13.2) are constants.

kappa_j = (sum_x actual_j) / (sum_x equidist_j), equidist = #in-window divisors / phi(|a|).
Single-pass engine (actual and equidist together). Prints CUMULATIVE kappa_j over [73, P).

RESULT (this script to ~1.6e4; type3_kappa.c to 4e5): they are NOT constants. All three
kappa_j DRIFT monotonically (kappa_I 1.64->1.54, kappa_II 0.708->0.678, kappa_III 0.98->1.02)
because the 1/phi(|a|) normalisation is itself a drifting approximation to the true
divisor-in-AP density. zeta(2)=1.6449 for kappa_I is excluded. The only stable object is
the ratio III/f1 ~ 0.436. No clean closed form.

Run:  python3 type3_kappa.py     (stdlib only)
"""
import math
from type3_derivation import spf_sieve, factor, divisors_of_square


def isprime(n):
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return n >= 2


def totient_from(m, spf):
    if m == 1:
        return 1
    ph = 1
    for pr, ex in factor(m, spf).items():
        ph *= (pr - 1) * pr ** (ex - 1)
    return ph


def strata_both(p, spf):
    """One pass: actual[j] and equidist[j] (=sum 1/phi over in-window divisors)."""
    A = [0, 0, 0]
    E = [0.0, 0.0, 0.0]
    for x in range(1, p // 2 + 1):
        a = 4 * x - p
        if a == 0:
            continue
        m = abs(a)
        B = p * x
        dmin = 2 * x * (2 * x - p)
        rangeA = (p < 4 * x <= 2 * p)
        rangeB = (4 * x < p)
        if not (rangeA or rangeB):
            continue
        tgt = (-B) % m
        invphi = 1.0 / totient_from(m, spf)
        pj = (1, p, p * p)
        for e in divisors_of_square(x, spf):
            for j in (0, 1, 2):
                d = -pj[j] * e
                if rangeA:
                    if not (dmin <= d <= -1):
                        continue
                else:
                    if d > dmin:
                        continue
                E[j] += invphi
                if (-pj[j] * e) % m == tgt:
                    A[j] += 1
    return A, E


if __name__ == "__main__":
    PMAX = 16000
    spf = spf_sieve(PMAX)
    checkpoints = [2000, 4000, 8000, 12000, 16000]
    cumA = [0, 0, 0]
    cumE = [0.0, 0.0, 0.0]
    ci = 0
    print(f"{'P':>7} {'nprimes':>7}  {'kI':>8} {'kII':>8} {'kIII':>8}  "
          f"{'III/f1':>8}")
    nprimes = 0
    for p in range(73, PMAX):
        if p % 24 != 1 or not isprime(p):
            continue
        a, e = strata_both(p, spf)
        cumA = [cumA[i] + a[i] for i in range(3)]
        cumE = [cumE[i] + e[i] for i in range(3)]
        nprimes += 1
        if ci < len(checkpoints) and p >= checkpoints[ci]:
            k = [cumA[i] / cumE[i] for i in range(3)]
            rat = cumA[2] / sum(cumA)
            print(f"{checkpoints[ci]:>7} {nprimes:>7}  {k[0]:>8.4f} {k[1]:>8.4f} "
                  f"{k[2]:>8.4f}  {rat:>8.4f}")
            ci += 1

    k = [cumA[i] / cumE[i] for i in range(3)]
    z2 = math.pi**2 / 6
    print(f"\nfinal kappa_I  = {k[0]:.4f}   zeta(2)=pi^2/6 = {z2:.4f}   "
          f"ratio kI/zeta2 = {k[0]/z2:.4f}")
    print(f"final kappa_II = {k[1]:.4f}   1/sqrt2 = {1/math.sqrt(2):.4f}   "
          f"6/pi^2 = {6/math.pi**2:.4f}   2-zeta2 = {2-z2:.4f}")
    print(f"final kappa_III= {k[2]:.4f}   (expected ->1)")
    print(f"kappa_I * kappa_II = {k[0]*k[1]:.4f} ;  kappa_I/kappa_II = {k[0]/k[1]:.4f}")
