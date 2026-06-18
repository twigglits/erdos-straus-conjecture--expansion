#!/usr/bin/env python3
"""sigma7_char_fit.py — the exact multi-character expansion of σ₇(c).

The square-class richness factors as f̄ ∝ σ₅(p%5)·σ₇(p%7) (class_local_density.py). The hard classes
only realize the quadratic residues mod 7, {1,2,4}, which form the cyclic order-3 subgroup generated
by 2 (1=2⁰, 2=2¹, 4=2²). A function on a cyclic group of order 3 has an EXACT 3-term discrete Fourier
expansion over the cubic character ψ (ψ(2)=ω=e^{2πi/3}):

    σ₇(c) = a₀ + b·ψ(c) + b̄·ψ̄(c) = a₀ + 2·Re( b·ψ(c) ),     a₀ = mean, b = (1/3)Σ_m σ₇(2^m) ω^{-m}.

The content is entirely in the complex coefficient b:
  • Re b  — the SYMMETRIC cubic part: it suppresses c=1 (the unique cube), the dominant term and the
            reason 1² is thinnest;
  • Im b  — the CHIRAL / odd part: it is antisymmetric under c → c⁻¹ (here 2 ↔ 4, since 2·4≡1),
            so it splits σ₇(2) ≠ σ₇(4). A density is symmetric; an odd part is the local shadow of
            the signed-sector chirality (REPORT §11.4). No single Dirichlet character has it.

Equivalently σ₇(c) = a₀ + 2|b|·cos(arg b + 2π·ind₂(c)/3); a PURE density would have arg b ∈ {0,π}
(real), and the measured offset of arg b from π is exactly the chiral angle.

Reads completed hard-class datasets. Stdlib only.
Run:  python3 analysis/sigma7_char_fit.py
"""
import cmath
import csv
import math
import os
import statistics

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data")
W = cmath.exp(2j * math.pi / 3)            # ω


def sigma7(path):
    g = {1: [], 2: [], 4: []}
    for r in csv.DictReader(open(path)):
        if not r["p"].isdigit():
            continue
        c = int(r["p"]) % 7
        if c in g:
            g[c].append(int(r["fI"]) + int(r["fII"]))
    return {c: statistics.mean(v) for c, v in g.items()}


if __name__ == "__main__":
    for name, fn in [("10⁸–2×10⁸", "hard_1e8_2e8.csv"), ("10⁹", "hard_1e9_slice.csv")]:
        path = os.path.join(DATA, fn)
        if not os.path.exists(path):
            continue
        s = sigma7(path)
        s0, s1, s2 = s[1], s[2], s[4]               # by power of 2: m = 0,1,2
        a0 = (s0 + s1 + s2) / 3
        b = (s0 + s1 * W.conjugate() + s2 * W) / 3  # cubic coefficient (b̄ is the conjugate term)
        ang = math.degrees(cmath.phase(b))
        print(f"\n=== {name} ===  σ₇(1)={s0:.1f}  σ₇(2)={s1:.1f}  σ₇(4)={s2:.1f}")
        print(f"  a₀ (trivial)            = {a0:.2f}")
        print(f"  Re b (symmetric cubic)  = {b.real:+.3f}   rel {2*b.real/a0:+.4f}")
        print(f"  Im b (chiral / odd)     = {b.imag:+.3f}   rel {2*b.imag/a0:+.4f}")
        print(f"  |b| = {abs(b):.3f},  arg b = {ang:.1f}°  (pure density ⇒ 180°; "
              f"chiral angle = {abs(180-ang):.1f}°)")
        print(f"  chiral/symmetric        = {abs(b.imag/b.real):.3f}")
        rec = {1: a0 + 2 * b.real, 2: (a0 + 2 * (b * W).real), 4: (a0 + 2 * (b * W * W).real)}
        assert all(abs(rec[c] - s[c]) < 1e-6 for c in (1, 2, 4)), "DFT not exact?!"
        print(f"  exact reconstruction ✓  ({rec[1]:.1f}, {rec[2]:.1f}, {rec[4]:.1f})")
    print("\nThe expansion is one cubic character with a phase: the magnitude makes 1² thinnest,")
    print("the ~17° phase-offset-from-real is the chiral term splitting the inverse pair 2↔4.")
