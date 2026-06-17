#!/usr/bin/env python3
"""target_1e10.py — locate the predicted-thinnest hard primes in [10^10, 10^10+1e7].

The full square-class sweep at 10^10 (~13,500 primes) is a ~2-day GPU job; but the §12
adversarial score (fitted on p ≤ 2×10^8, residual_effects.json) ranks where f is thinnest,
and at 10^9/2×10^9 its predicted bottom-1% CONTAINED the true window floor. So to test the
§13.5 blind prediction (min f ∈ [439, 499]) we score all square-class primes in the window
and emit the bottom-K — then `engines/fp_single` counts exact f(p) for just those K.

Writes the bottom-K primes (one per line) to data/target_1e10_bottomK.txt.
Run from analysis/:  PYTHONNOUSERSITE=1 python3 target_1e10.py [K]
"""
import json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SQ = {1, 121, 169, 289, 361, 529}
LO, HI = 10**10, 10**10 + 10**7
K = int(sys.argv[1]) if len(sys.argv) > 1 else 150

eff = json.load(open(os.path.join(HERE, "residual_effects.json")))
QS = eff["qs"]
EQ = {int(q): v for q, v in eff["effects"].items()}
CM = {int(c): m for c, m in eff["class_means_sq"].items()}

def score(p):
    s = CM[p % 840]
    for q in QS:
        s += EQ[q][p % q]
    return s

def seg_primes_sqclass(lo, hi):
    """segmented sieve → primes in [lo,hi] with p%840 in SQ (the rolling window)."""
    import math as m
    limit = m.isqrt(hi) + 1
    base = []
    c = bytearray([1]) * (limit + 1)
    for i in range(2, limit + 1):
        if c[i]:
            base.append(i)
            c[i*i::i] = bytearray(len(c[i*i::i]))
    out = []
    CH = 1 << 22
    s = lo
    while s <= hi:
        e = min(s + CH - 1, hi)
        sz = e - s + 1
        sv = bytearray([1]) * sz
        for q in base:
            first = max(q*q, ((s + q - 1)//q)*q)
            sv[first - s::q] = bytearray(len(sv[first - s::q]))
        for i in range(sz):
            if sv[i]:
                p = s + i
                if p % 840 in SQ:
                    out.append(p)
        s = e + 1
    return out

if __name__ == "__main__":
    print(f"sieving square-class primes in [{LO:.3g}, {HI:.3g}] ...", flush=True)
    ps = seg_primes_sqclass(LO, HI)
    print(f"  {len(ps)} square-class primes (≈ PNT×6/192 expected ~{int((HI-LO)/math.log(LO)*6/192)})")
    ps.sort(key=score)
    bottom = ps[:K]
    outp = os.path.join(HERE, os.pardir, "data", "target_1e10_bottomK.txt")
    with open(outp, "w") as f:
        f.write("\n".join(map(str, bottom)) + "\n")
    print(f"  wrote bottom-{K} by score (predicted thinnest) → {outp}")
    print(f"  score range of bottom-{K}: [{score(bottom[0]):.3f}, {score(bottom[-1]):.3f}]; "
          f"full range [{score(ps[0]):.3f}, {score(ps[-1]):.3f}]")
    print(f"  next: ./engines/fp_single $(cat {outp}) | sort -t= -k4 -n | head")
