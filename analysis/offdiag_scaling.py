#!/usr/bin/env python3
"""offdiag_scaling.py — does the second moment's OFF-DIAGONAL (two-shift Titchmarsh) part
grow with p?  REPORT §14 reduced Σ_p f_II(p)² to Σ_p Σ_{δ1,δ2} r_{δ1}(p) r_{δ2}(p), with the
diagonal δ1=δ2 piece = Σ_p Σ_δ r_δ(p)² (a tractable single-shift divisor sum) and the off-diagonal
piece the genuine two-shift sum that is "out of reach" (ET Remark 1.3).  `second_moment.py` measured
the split once, at p ≤ 8000 (≈ 98.5% off-diagonal).  Here we track it ACROSS SCALES: if the
off-diagonal fraction → 1, the tractable diagonal vanishes and the analytic wall hardens with p.

For a sample of hard primes (p ≡ 1 mod 4) near 10⁴, 10⁵, 10⁶ we compute the full δ-decomposition
r_δ(p) (exact, via the kernel in `second_moment.py`) and report
    off_frac(scale) = 1 − Σ_p Σ_δ r_δ(p)²  /  Σ_p f_II(p)².
Exact integer arithmetic; stdlib only.

Run:  python3 analysis/offdiag_scaling.py
"""
import os
import sys
import time
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import second_moment as sm        # reuse the validated kernel + bridge asserts


def offdiag_in_range(spf, plo, phi, max_primes):
    """Sample up to max_primes hard primes p ≡ 1 (mod 4) in [plo, phi]; return a summary dict."""
    tot_f2 = diag = sum_f = nfp = 0
    deepest_delta = 0
    for p in range(plo, phi):
        if nfp >= max_primes:
            break
        if p % 4 != 1 or spf[p] != p:
            continue
        _, t2 = sm.type_counts_and_solutions(p, spf)
        fII = len(t2)
        if fII == 0:
            continue
        rc = Counter(s[4] for s in t2)            # r_δ(p): solutions per shift δ
        diag += sum(v * v for v in rc.values())   # diagonal Σ_δ r_δ²
        tot_f2 += fII * fII                        # full second moment f_II²
        sum_f += fII
        deepest_delta = max(deepest_delta, max(rc))
        nfp += 1
    off = 1.0 - diag / tot_f2 if tot_f2 else float("nan")
    return dict(n=nfp, off=off, mean_fII=sum_f / nfp if nfp else 0,
                tot_f2=tot_f2, diag=diag, maxdelta=deepest_delta)


if __name__ == "__main__":
    # one sieve covering the largest scale; samples shrink as per-prime cost grows ~p
    PMAX = 1_050_000
    print(f"sieving smallest-prime-factor to {PMAX} ...")
    t0 = time.time()
    spf = sm.spf_sieve(PMAX)
    print(f"  done ({time.time()-t0:.1f}s)\n")

    print("off-diagonal (two-shift Titchmarsh) fraction of the f_II second moment, by scale:")
    print(f"  {'scale':>8} {'#primes':>8} {'mean f_II':>10} {'off-diag frac':>14} {'max δ':>7}")
    scales = [(10**4, 40_000, 400), (10**5, 140_000, 200), (10**6, 1_050_000, 50)]
    rows = []
    for plo, phi, cap in scales:
        ts = time.time()
        r = offdiag_in_range(spf, plo, phi, cap)
        rows.append((plo, r))
        print(f"  {plo:>8.0e} {r['n']:>8d} {r['mean_fII']:>10.2f} "
              f"{r['off']:>13.4f} {r['maxdelta']:>7d}   [{time.time()-ts:.1f}s]")

    print()
    if len(rows) >= 2 and all(rows[i][1]['off'] == rows[i][1]['off'] for i in range(len(rows))):
        d = rows[-1][1]['off'] - rows[0][1]['off']
        trend = "RISING → diagonal vanishing, wall hardens" if d > 0.002 else \
                ("falling" if d < -0.002 else "flat → scale-invariant structure")
        print(f"off-diagonal fraction {rows[0][1]['off']:.4f} (10^4) → {rows[-1][1]['off']:.4f} "
              f"(10^6):  {trend}.")
    print("Both pieces are positive and O(1)-bounded per prime; the off-diagonal bulk is the\n"
          "two-shift sum no 2026 method evaluates to the precision a pointwise f_II>0 needs.")
