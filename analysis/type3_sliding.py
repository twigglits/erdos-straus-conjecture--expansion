#!/usr/bin/env python3
"""The sliding-modulus question (REPORT §13.2 open problem): does averaging over
the moving modulus a=4x-p rescue naive divisor-equidistribution, or reveal a
stable correction?

For each stratum j, define the correction factor
    kappa_j = (true count) / (equidist count),   equidist = sum_x (#in-window divisors)/phi(|a|).
If kappa_j -> stable constants, averaging REVEALS a singular-series correction
(value = explicit but not naive). If they drift, there is no rescue.

Sharp internal test: Type I and Type III share the SAME residue-target structure
(both are squares mod |a|; both reachable iff 4 in H_x = <primes|x>). So any stable
gap kappa_I != kappa_III is PURE window x residue coupling (the council's "false
independence of size and residue" weak link), not an equidistribution effect.

Also measured: reachability rate Pr[4^{-1} in S_x] where S_x = {e mod |a| : e|x^2}
is the achievable residue set (the Erdos-Hall-Tenenbaum subgroup, realised).

Run:  python3 type3_sliding.py     (stdlib only; a few minutes)
"""
from type3_derivation import (spf_sieve, divisors_of_square, totient, f1_strata)


def isprime(n):
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return n >= 2


def reachability(p, spf):
    """Per range, fraction of x for which the Type III target 4^{-1} is an
    achievable divisor-residue (4^{-1} in S_x), and mean |S_x|/phi(|a|)
    (achievable-set density). Range B = x<p/4 (Type III), range A = p/4<x<=p/2."""
    stat = {'B': [0, 0, 0.0], 'A': [0, 0, 0.0]}   # [reachable, total, sum |S|/phi]
    for x in range(1, p // 2 + 1):
        a = 4 * x - p
        if a == 0:
            continue
        m = abs(a)
        rng = 'B' if 4 * x < p else ('A' if p < 4 * x <= 2 * p else None)
        if rng is None:
            continue
        res = {e % m for e in divisors_of_square(x, spf)}
        phi = totient(m, spf)
        inv4 = pow(4, -1, m) if m > 1 else 0
        stat[rng][1] += 1
        stat[rng][0] += (inv4 in res) if m > 1 else 1
        stat[rng][2] += len(res) / phi if phi else 1.0
    return stat


if __name__ == "__main__":
    spf = spf_sieve(8000)
    bands = [(73, 1000), (1000, 2500), (2500, 5000), (5000, 8000)]

    print("kappa_j = actual_j / equidist_j  (does it converge?)\n")
    print(f"{'band':>14} {'n':>4}  {'kI':>6} {'kII':>6} {'kIII':>6}   "
          f"{'III/f1 act':>10} {'III/f1 eq':>9}")
    for lo, hi in bands:
        ps = [p for p in range(lo, hi) if p % 24 == 1 and isprime(p)]
        A = [0.0, 0.0, 0.0]; E = [0.0, 0.0, 0.0]
        for p in ps:
            a = f1_strata(p, spf, mode='actual')
            e = f1_strata(p, spf, mode='equidist')
            A = [A[i] + a[i] for i in range(3)]
            E = [E[i] + e[i] for i in range(3)]
        k = [A[i] / E[i] if E[i] else 0 for i in range(3)]
        ratA = A[2] / sum(A); ratE = E[2] / sum(E)
        print(f"[{lo:>5},{hi:>5}) {len(ps):>4}  {k[0]:>6.3f} {k[1]:>6.3f} "
              f"{k[2]:>6.3f}   {ratA:>10.4f} {ratE:>9.4f}")

    print("\nreachability of the Type III target 4^{-1} in S_x = {e mod|a|: e|x^2}:")
    print(f"{'band':>14}  {'rangeB reach':>12} {'rangeA reach':>12} "
          f"{'B |S|/phi':>10} {'A |S|/phi':>10}")
    for lo, hi in bands:
        ps = [p for p in range(lo, hi) if p % 24 == 1 and isprime(p)]
        agg = {'B': [0, 0, 0.0], 'A': [0, 0, 0.0]}
        for p in ps:
            s = reachability(p, spf)
            for r in 'BA':
                for i in range(3):
                    agg[r][i] += s[r][i]
        rB = agg['B'][0] / agg['B'][1]; rA = agg['A'][0] / agg['A'][1]
        dB = agg['B'][2] / agg['B'][1]; dA = agg['A'][2] / agg['A'][1]
        print(f"[{lo:>5},{hi:>5})  {rB:>12.4f} {rA:>12.4f} {dB:>10.4f} {dA:>10.4f}")
