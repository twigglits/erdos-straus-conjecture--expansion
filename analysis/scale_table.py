#!/usr/bin/env python3
"""scale_table.py — populate §8.2 Table 1 (the L-correlation across scale).

For each decade window produced by run_scale_study.sh (data/fresh/fresh_<tag>.csv,
columns p,ford,fI,fII), compute the same quantities as lfunction_connection.py:

    f      = fI + fII                         (hard-prime ESC count)
    ln f   = log f
    ln L   = -Σ_{ℓ≤X, 840∤ℓ} log(1 - (p/ℓ)/ℓ)  (truncated quadratic L-value, X=1500)
    corr   = Pearson(ln f, ln L)
    c      = |corr| · σ(ln f) / σ(ln L)        (implied exponent)

X=1500 is the truncation used for the headline -0.62 and the slope in
lfunction_connection.py. Run: python3 analysis/scale_table.py
"""
import csv
import math
import os
import statistics

from sympy import primerange

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "fresh")
X = 1500
SMALL = [l for l in primerange(2, X + 1) if 840 % l != 0]


def legendre(p, l):
    r = pow(p % l, (l - 1) // 2, l)
    return 1 if r == 1 else (-1 if r == l - 1 else 0)


def pearson(xs, ys):
    mx, my = statistics.mean(xs), statistics.mean(ys)
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)


def row(tag):
    path = os.path.join(DATA, f"fresh_{tag}.csv")
    if not os.path.exists(path):
        return None
    rows = [(int(r["p"]), int(r["fI"]) + int(r["fII"]))
            for r in csv.DictReader(open(path)) if r["p"].isdigit()]
    lnf = [math.log(v) for _, v in rows]
    logL = [-sum(math.log(1 - legendre(p, l) / l) for l in SMALL) for p, _ in rows]
    n = len(rows)
    sf, sL = statistics.pstdev(lnf), statistics.pstdev(logL)
    r = pearson(lnf, logL)
    c = abs(r) * sf / sL
    return n, sf, sL, r, c


if __name__ == "__main__":
    print(f"truncation X = {X}  ({len(SMALL)} Euler factors, 840∤ℓ)\n")
    print(f"{'scale':>6} | {'n':>6} | {'σ(lnf)':>7} | {'σ(lnL)':>7} | {'corr':>7} | {'c':>6}")
    print("-" * 52)
    for tag in ("1e6", "1e7", "1e8", "1e9", "1e10", "1e11"):
        res = row(tag)
        if res is None:
            print(f"{tag:>6} | {'(no data — run pending)':>40}")
            continue
        n, sf, sL, r, c = res
        print(f"{tag:>6} | {n:>6} | {sf:>7.3f} | {sL:>7.3f} | {r:>+7.3f} | {c:>6.3f}")
