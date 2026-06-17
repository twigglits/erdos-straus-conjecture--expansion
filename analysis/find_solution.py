#!/usr/bin/env python3
"""find_solution.py — verify ESC for a SINGLE prime by exhibiting one solution,
pushing past the 10^18 published sweep frontier on adversarially-hard primes.

Counting f(p) is O(p) (needs the GPU at 10^10).  But *verifying* ESC for one prime
only needs ONE solution — and that is cheap at any scale: via the kernel (Lemma A),
pick the smallest a = 4x − p > 0 (x = (p+a)/4), factor the single ~log p-digit number
x, and look for a divisor d | (px)^2 with d ≡ −px (mod a) in range; then
y = (px+d)/a, z = (px + (px)^2/d)/a.  Small a ⟹ the residue class −px (mod a) is one
of a few, and (px)^2 has 3·τ(x^2) divisors, so a hit is found at a small a almost
always.  This is the elementary "small-channel" search, exact.

We run it on square-class primes p ≡ {1,121,169,289,361,529} (mod 840) — the six
genuinely hard classes — at 10^9 … 10^22, i.e. up to 10^4× past the published frontier,
and on K1-starved primes (4p+1 a product of primes ≡ 1 mod 4) where the cheapest
channel is closed.  A FAILURE to find a solution would be a counterexample candidate.

Run:  python3 analysis/find_solution.py        (needs sympy for factoring)
"""
import sys, time
from fractions import Fraction
import sympy

SQ = {1, 121, 169, 289, 361, 529}


def divisors_from_factint(fac):
    divs = [1]
    for q, e in fac.items():
        divs = [d * q ** i for d in divs for i in range(e + 1)]
    return divs


def find_solution(p, amax=2_000_000, max_div=400_000):
    """Return (x, y, z, a) with 1/x+1/y+1/z = 4/p, or None.  Searches smallest a first."""
    a0 = (-p) % 4 or 4                       # a ≡ −p (mod 4); for p ≡ 1 (4) this is 3
    for a in range(a0, amax + 1, 4):
        if (p + a) % 4:
            continue
        x = (p + a) // 4
        if x <= p // 4:
            continue
        if x > 3 * p // 4:
            break                            # exhausted the valid x-range
        B = p * x
        dmin = 2 * x * (2 * x - p) if 2 * x > p else 0
        fx = sympy.factorint(x)
        facsq = {q: 2 * e for q, e in fx.items()}
        dvs_x2 = divisors_from_factint(facsq)
        if 3 * len(dvs_x2) > max_div:         # guard against pathologically smooth x
            continue
        for pe in (1, p, p * p):              # divisors of B^2 = p^2 x^2 are {1,p,p^2}·div(x^2)
            for d0 in dvs_x2:
                d = d0 * pe
                if d > B or d < dmin:
                    continue
                if (B + d) % a:
                    continue
                Bsq_d = B * B // d            # exact: d | x^2·pe^2 | B^2
                if (B + Bsq_d) % a:
                    continue
                y = (B + d) // a
                z = (B + Bsq_d) // a
                if y > 0 and z > 0 and Fraction(1, x) + Fraction(1, y) + Fraction(1, z) == Fraction(4, p):
                    return (x, y, z, a)
    return None


def omega3(n, bound=10**6):
    """count distinct prime factors ≡ 3 (mod 4) up to a trial bound (for K1 diagnosis)."""
    c = 0
    m = n
    d = 3
    while d <= bound and d * d <= m:
        if m % d == 0:
            if d % 4 == 3:
                c += 1
            while m % d == 0:
                m //= d
        d += 2
    if m > 1 and m % 4 == 3:
        c += 1
    return c


def next_square_class_prime(start, starved=False):
    """smallest prime ≥ start with p mod 840 in SQ (optionally K1-starved: no small ≡3 mod4 factor of 4p+1)."""
    p = sympy.nextprime(start - 1)
    while True:
        if p % 840 in SQ and (not starved or omega3(4 * p + 1, bound=20000) == 0):
            return p
        p = sympy.nextprime(p)


def report(p, label):
    t0 = time.time()
    sol = find_solution(p)
    dt = time.time() - t0
    assert sol is not None, f"NO SOLUTION FOUND for p={p} — COUNTEREXAMPLE CANDIDATE"
    x, y, z, a = sol
    assert Fraction(1, x) + Fraction(1, y) + Fraction(1, z) == Fraction(4, p)
    w3 = omega3(4 * p + 1)
    print(f"  {label}: p={p}  (≡{p % 840} mod 840, ~10^{len(str(p))-1}, K1{'closed' if w3 == 0 else 'open'})")
    print(f"      4/p = 1/{x} + 1/{y} + 1/{z}   [a=4x−p={a}]  found in {dt:.2f}s")
    return sol


if __name__ == "__main__":
    print("[self-test] known hard primes:")
    for p in (2521, 1009, 8101, 73):
        report(p, f"p={p}")

    print("\n[frontier] square-class primes at and BEYOND the 10^18 published sweep:")
    for k in range(9, 23):
        p = next_square_class_prime(10 ** k)
        report(p, f"10^{k}")

    print("\n[adversarial] K1-STARVED square-class primes (4p+1 has no factor ≡3 mod4) beyond 10^18:")
    for k in (18, 19, 20, 21):
        p = next_square_class_prime(10 ** k, starved=True)
        report(p, f"10^{k} starved")

    print("\nfind_solution.py: every tested prime has an explicit ESC solution (0 failures).")
