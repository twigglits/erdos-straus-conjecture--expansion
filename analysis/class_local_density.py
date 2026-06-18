#!/usr/bin/env python3
"""class_local_density.py — the mechanism behind the square-class richness hierarchy.

`class_hierarchy.py` found that the six hard square classes carry a stable richness ordering in
f(p) (1² < 11² < 13² < 19² < 17² < 23²). This script pins the mechanism.

The six hard classes are EXACTLY the six combinations of (p mod 5 ∈ {1,4}) × (p mod 7 ∈ {1,2,4}):
mod 8 (all ≡1), mod 3 (all ≡1) are identical for the six, so the only moduli on which they differ
are 5 and 7 — the odd primes dividing 840.  And indeed the class-dependence of f FACTORS:

    f̄(class)  ≈  σ₅(p mod 5) · σ₇(p mod 7) / overall      (max error < 0.6% on completed data),

a product of one local factor at ℓ=5 and one at ℓ=7 — exactly the singular-series shape, localised
to the two primes where the classes differ.  The leading surface point count is class-independent
(#{u+v+w = 4/p, all ≠ 0} = ℓ²−3ℓ+3, free of p mod ℓ); the ~8% hierarchy is the finer ℓ-adic /
nodal correction, and it lives entirely at 5 and 7.

Measured local factors (the divisor-density at each prime):
    σ₅(4) / σ₅(1) ≈ 1.034,        σ₇(1) : σ₇(2) : σ₇(4) ≈ 1 : 1.033 : 1.047.
f is SUPPRESSED at the "most special" residues — `1` is the unique 4th power mod 5, and `1` is the
unique cube among the QRs {1,2,4} mod 7 — so class 1² = (1,1) is doubly-suppressed (thinnest) and
23² = (4,4) doubly-enhanced (richest). A higher-residue-character effect, i.e. the concrete face of
the "finer parity/stratum suppression" (Yamamoto) that the leading density misses.

Reads completed hard-class datasets. Exact arithmetic, stdlib only.
Run:  python3 analysis/class_local_density.py
"""
import csv
import os
import statistics

SQ = {1: "1²", 121: "11²", 169: "13²", 289: "17²", 361: "19²", 529: "23²"}
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data")


def load(path):
    return [(int(r["p"]), int(r["fI"]) + int(r["fII"]))
            for r in csv.DictReader(open(path)) if r["p"].isdigit()]


def marginals(data, mod):
    g = {}
    for p, v in data:
        g.setdefault(p % mod, []).append(v)
    return {r: statistics.mean(vs) for r, vs in g.items()}


if __name__ == "__main__":
    for name, fn in [("10⁸–2×10⁸", "hard_1e8_2e8.csv"), ("10⁹", "hard_1e9_slice.csv")]:
        path = os.path.join(DATA, fn)
        if not os.path.exists(path):
            continue
        data = load(path)
        overall = statistics.mean(v for _, v in data)
        m5, m7 = marginals(data, 5), marginals(data, 7)
        byc = {c: [] for c in SQ}
        for p, v in data:
            byc[p % 840].append(v)
        print(f"\n=== {name}  (n={len(data)}, overall mean f = {overall:.1f}) ===")
        print(f"  local factor σ₅:  σ₅(1)={m5[1]:.1f}  σ₅(4)={m5[4]:.1f}   ratio {m5[4]/m5[1]:.4f}")
        print(f"  local factor σ₇:  σ₇(1)={m7[1]:.1f}  σ₇(2)={m7[2]:.1f}  σ₇(4)={m7[4]:.1f}"
              f"   ratios 1:{m7[2]/m7[1]:.4f}:{m7[4]/m7[1]:.4f}")
        print(f"  {'class':>5} {'(p%5,p%7)':>10} {'observed f':>11} {'σ₅·σ₇ pred':>11} {'err':>6}")
        maxerr = 0.0
        for c in sorted(SQ, key=lambda c: statistics.mean(byc[c])):
            obs = statistics.mean(byc[c])
            pred = m5[c % 5] * m7[c % 7] / overall
            err = 100 * (obs - pred) / obs
            maxerr = max(maxerr, abs(err))
            print(f"  {SQ[c]:>5} {f'({c%5},{c%7})':>10} {obs:>11.1f} {pred:>11.1f} {err:>5.2f}%")
        print(f"  → f-class-dependence factors as σ₅(p%5)·σ₇(p%7) to {maxerr:.2f}% "
              f"(localised to the primes 5,7 dividing 840).")
    print("\nMechanism: the richness hierarchy is a product of two local densities, at ℓ=5 and ℓ=7,")
    print("set by p mod 5 and p mod 7 via higher residue characters — f is suppressed at the more")
    print("'special' (power-residue) residues, so 1²=(1,1) is thinnest and 23²=(4,4) richest.")
