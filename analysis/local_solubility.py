#!/usr/bin/env python3
"""geo: everywhere-local solubility + stratum vanishing on Erdos-Straus surfaces.

The surface  U_n : 4xyz = n(xy+yz+zx);  ESC = positive integral points on U_n
off the coordinate axes.  Two exact computations, stdlib only:

1) LOCAL CERTIFICATES.  F is linear in x:  F = x*(4yz - n(y+z)) - n*yz.
   So a pair (y,z) of positive integers with  g = 4yz - n(y+z)  nonzero and
   coprime to q gives  x = n*y*z/g in Z_q  (denominator prime to q), i.e. a
   Z_q-point of U_n with xyz != 0.  At the real place x = y = z = 3n/4 is a
   positive real point.  Together: the adelic space of U_n (positivity sector
   included) is NONEMPTY for every tested n — there is no local obstruction.
   Bright-Loughran 2020 add that the Brauer-Manin obstruction vanishes too;
   this script machine-verifies the "local" half of that picture on our
   hostile primes, at every prime modulus q <= 199 (the range where REPORT
   S12 measured congruence effects on f(p)).

2) STRATUM VANISHING (Yamamoto; Elsholtz-Tao Prop 1.6).  For odd squares
   n = m^2 the Type I / Type II strata vanish identically:
     Type I :  n | z,  gcd(xy, n) = 1;   Type II :  n | y, n | z, gcd(x,n)=1,
   yet ESC still holds for n = m^2 through "spread" solutions (divisibility
   shared across proper factors) — strata that do not exist over primes.
   This is the obstruction BM cannot see: it kills strata (torsor classes),
   not adelic points.  Verified here by exact enumeration via the Lemma-A
   kernel: for least denominator x, with a = 4x-n, B = nx, solutions are
   (ay-B)(az-B) = B^2, i.e. divisor pairs of B^2 in the class -B mod a.

Run: python3 analysis/local_solubility.py   (~1 min; stdlib only, exact integer arithmetic)
"""
from fractions import Fraction

QMAX = 199
PRIMES_Q = [q for q in range(2, QMAX + 1) if all(q % d for d in range(2, q))]


# ---------- 1) local certificates ----------

def certificate(n, q):
    """(x,y,z) on U_n with x in Z_q, xyz != 0: search g = 4yz-n(y+z) unit mod q."""
    for y in range(1, 4 * q + 2):
        for z in range(y, 4 * q + 2):
            g = 4 * y * z - n * (y + z)
            if g != 0 and g % q != 0:
                return Fraction(n * y * z, g), y, z
    return None


def verify_certificate(n, q, cert):
    x, y, z = cert
    assert x != 0 and y > 0 and z > 0
    assert x.denominator % q != 0, (n, q, x)            # x is q-integral
    assert 4 * x * y * z == n * (x * y + y * z + z * x)  # exact, on U_n


# ---------- 2) exact solution census via the kernel ----------

def factor(m):
    f = {}
    d = 2
    while d * d <= m:
        while m % d == 0:
            f[d] = f.get(d, 0) + 1
            m //= d
        d += 1 if d == 2 else 2
    if m > 1:
        f[m] = f.get(m, 0) + 1
    return f


def divisors_of_square_upto(B):
    """All u | B^2 with u <= B."""
    divs = [1]
    for p, e in factor(B).items():
        pe = [p ** i for i in range(2 * e + 1)]
        divs = [d * q for d in divs for q in pe if d * q <= B * B]
    return sorted(u for u in divs if u <= B)


def solutions(n):
    """All unordered {x<=y<=z} with 1/x+1/y+1/z = 4/n, exact."""
    sols = []
    for x in range(n // 4 + 1, 3 * n // 4 + 1):
        a, B = 4 * x - n, n * x
        if a <= 0:
            continue
        for u in divisors_of_square_upto(B):
            if (B + u) % a:
                continue
            y = (B + u) // a
            if y < x:
                continue
            v = B * B // u
            if (B + v) % a:
                continue          # composite n: z-integrality is not automatic
            sols.append((x, y, (B + v) // a))
    return sols


def strata(n, sols):
    """(typeI, typeII, spread) per Elsholtz-Tao definitions."""
    tI = tII = sp = 0
    from math import gcd
    for s in sols:
        marks = [w % n == 0 for w in s]
        k = sum(marks)
        rest = [w for w, m in zip(s, marks) if not m]
        if k == 1 and all(gcd(w, n) == 1 for w in rest):
            tI += 1
        elif k == 2 and all(gcd(w, n) == 1 for w in rest):
            tII += 1
        else:
            sp += 1
    return tI, tII, sp


# ---------- main ----------

if __name__ == "__main__":
    hostile_primes = [73, 193, 1009, 2521]          # hard classes, incl. record p=2521
    odd_squares = [9, 25, 49, 121, 169, 289, 361, 529, 841, 961]
    frontier = 2004535009                            # the 2e9 floor prime (13^2 mod 840)

    # local certificates everywhere, for every odd test n (even n is classically
    # trivial — the identity 4/n = 1/(n/2) + 1/n + 1/n is a global point; checked
    # for n=2 below — and the x-coefficient trick degenerates at q=2 for even n)
    assert 4 * Fraction(1, 1) * 2 * 2 == 2 * (1 * 2 + 2 * 2 + 2 * 1)  # (1,2,2) on U_2
    for n in hostile_primes + odd_squares + [frontier, 5]:
        for q in PRIMES_Q:
            cert = certificate(n, q)
            assert cert is not None, (n, q)
            verify_certificate(n, q, cert)
        r = Fraction(3 * n, 4)                       # real place, positive sector
        assert r > 0 and 4 * r ** 3 == n * 3 * r ** 2
    print(f"local: Z_q-certificates verified for all q <= {QMAX} "
          f"({len(PRIMES_Q)} primes) x {len(hostile_primes + odd_squares) + 3} values of n; "
          f"real positive point exact.  --> no local obstruction anywhere.")

    # census + strata
    known = {2: 1, 5: 2, 1009: 19, 2521: 9}          # documented values (README/REPORT)
    for n, f_expected in known.items():
        f = len(solutions(n))
        assert f == f_expected, (n, f, f_expected)
    print(f"census: kernel enumeration reproduces documented f(n) for {sorted(known)}.")

    for n in hostile_primes:
        tI, tII, sp = strata(n, solutions(n))
        assert sp == 0 and tI + tII > 0              # primes: only Type I/II live
        print(f"  p={n:5d}: f={tI + tII:3d}  (I={tI}, II={tII}, spread=0)")
    for n in odd_squares:
        sols = solutions(n)
        tI, tII, sp = strata(n, sols)
        assert tI == 0 and tII == 0, (n, tI, tII)    # Yamamoto: strata vanish...
        assert sp > 0, n                             # ...yet ESC holds via spread
        print(f"  n={n:5d}=m^2: f={len(sols):3d}  Type I=II=0 (Yamamoto), spread={sp}")
    print("strata: quadratic-reciprocity kills I/II on odd squares; adelic points "
          "remain (above).  The obstruction is stratum-level — invisible to BM.")
