#!/usr/bin/env python3
"""Type III 43%: where does f1_III / f1 = 0.43 come from?

Signed ESC at a prime p (REPORT §11.3, Lemma H). For positive denominator x:
  a = 4x - p,  B = p*x,  dmin = 2x(2x - p).
Grade-1 solutions <-> divisors d of B^2 = p^2 x^2 with d<0, d == -B (mod |a|),
in the grade-1 window:
  range A:  p/4 < x <= p/2  ->  dmin <= d <= -1     (small |d|)
  range B:  1  <= x <  p/4  ->  d <= dmin (< -B)     (large |d|)
Stratify |d| = p^j e, e | x^2:  j=0 Type I, j=1 II, j=2 III. Each j has exactly
tau(x^2) divisors of B^2 (p does not divide x).

FINDINGS this script establishes:
 1. validates the model: f1(2521) = 377, I/II/III = 115/85/177 exactly.
 2. pure window geometry (drop the residue filter) gives III/f1 -> 1/3, NOT 0.43.
 3. the residue condition d == -B (mod|a|) is what lifts III to 0.43. Per stratum
    it reads  e == 4^(1-j) x^(2-j)  (mod |a|)  [since p == 4x (mod a)], so
    Type I: e==4x^2,  Type II: e==x,  Type III: e==4^{-1}; the divisor involution
    e <-> x^2/e maps the Type I class to the Type III class.

Run:  python3 type3_derivation.py    (stdlib only)
"""


def spf_sieve(N):
    spf = list(range(N + 1))
    i = 2
    while i * i <= N:
        if spf[i] == i:
            for k in range(i * i, N + 1, i):
                if spf[k] == k:
                    spf[k] = i
        i += 1
    return spf


def factor(x, spf):
    f = {}
    while x > 1:
        p = spf[x]
        f[p] = f.get(p, 0) + 1
        x //= p
    return f


def divisors_of_square(x, spf):
    divs = [1]
    for pr, ex in factor(x, spf).items():
        divs = [d * pr**k for d in divs for k in range(2 * ex + 1)]
    return divs


def totient(m, spf):
    if m == 1:
        return 1
    ph = 1
    for pr, ex in factor(m, spf).items():
        ph *= (pr - 1) * pr ** (ex - 1)
    return ph


def f1_strata(p, spf, mode='actual', check_resformula=False):
    """mode = 'actual'  : true residue-conditioned count d == -B (mod|a|)
            = 'geom'    : drop the residue filter (pure window geometry, tau-weight)
            = 'equidist': geometry re-weighted by 1/phi(|a|) (the equidistribution
                          model: each unit residue class holds tau(x^2)/phi(|a|))"""
    cI = cII = cIII = 0.0
    for x in range(1, p // 2 + 1):
        a = 4 * x - p
        if a == 0:
            continue
        B = p * x
        dmin = 2 * x * (2 * x - p)
        absa = abs(a)
        tgt = (-B) % absa
        rangeA = (p < 4 * x <= 2 * p)         # p/4 < x <= p/2
        rangeB = (4 * x < p)                  # x < p/4
        if not (rangeA or rangeB):
            continue
        w = 1.0 / totient(absa, spf) if mode == 'equidist' else 1.0
        for e in divisors_of_square(x, spf):
            for j in (0, 1, 2):
                d = -(p ** j) * e
                if rangeA:
                    if not (dmin <= d <= -1):
                        continue
                else:
                    if d > dmin:
                        continue
                if mode == 'actual' and (d % absa) != tgt:
                    continue
                if check_resformula and (d % absa) == tgt:
                    # claim: e == 4^(1-j) x^(2-j) (mod |a|)
                    inv4 = pow(4, -1, absa) if absa > 1 else 0
                    claim = (pow(4, 1 - j, absa) * pow(x, 2 - j, absa)) % absa \
                        if (1 - j >= 0 and 2 - j >= 0) else \
                        (inv4 * pow(x, 2 - j, absa)) % absa
                    assert e % absa == claim, (p, x, j, e % absa, claim)
                cI, cII, cIII = (cI + (j == 0) * w, cII + (j == 1) * w,
                                 cIII + (j == 2) * w)
    return cI, cII, cIII


def ratio(c):
    t = sum(c)
    return c[2] / t if t else 0.0


if __name__ == "__main__":
    spf = spf_sieve(3000)
    print("validation (f1(2521)=377, I/II/III=115/85/177):")
    c = f1_strata(2521, spf_sieve(2521), mode='actual', check_resformula=True)
    print(f"  {tuple(int(v) for v in c)}  III/f1={ratio(c):.4f}")
    assert tuple(int(v) for v in c) == (115, 85, 177), c
    print("  OK (per-stratum residue formula e==4^(1-j)x^(2-j) mod|a| verified)\n")

    def isprime(n):
        i = 2
        while i * i <= n:
            if n % i == 0:
                return False
            i += 1
        return n >= 2

    spf = spf_sieve(8000)
    for lo, hi in [(73, 1000), (1000, 3000), (3000, 8000)]:
        ps = [p for p in range(lo, hi) if p % 24 == 1 and isprime(p)]
        sums = {m: [0.0, 0.0, 0.0] for m in ('actual', 'geom', 'equidist')}
        for p in ps:
            for m in sums:
                c = f1_strata(p, spf, mode=m)
                sums[m] = [sums[m][i] + c[i] for i in range(3)]
        print(f"\nband [{lo},{hi}): {len(ps)} primes == 1 mod 24")
        for m in ('actual', 'geom', 'equidist'):
            print(f"  {m:9} III/f1 = {ratio(sums[m]):.4f}")
    print("\n  geom ~ 1/3 (window only);  actual ~ 0.43 (residue-lifted);"
          "  equidist = geometry x 1/phi(|a|) captures the lift.")
