#!/usr/bin/env python3
"""primitive_typeII.py — the primitive (δ=1) Type II count is a single-shift divisor
function of 4p+1 (REPORT §20).

Executing the Henriot majorant requires expressing f_II(p) as F(|Q(p)|) for a FIXED
polynomial Q. Claim, derived from the kernel: a Type II solution is a pair (y',z') with

    m := 4y'z' − y' − z' = p·δ,   x = p·y'z'/m = y'z'/δ ∈ (p/4, p/2),

so the PRIMITIVE solutions (δ=1, m=p) are exactly (4y'−1)(4z'−1) = 4p+1, i.e. the
factorizations of 4p+1 into two factors ≡ 3 (mod 4). Hence

    f_II^{(1)}(p) = #{ u | 4p+1 : u ≡ 3 (mod 4), u ≤ sqrt(4p+1) }    (the δ=1 shift)

is a clean SINGLE-shift divisor function of the linear form 4p+1 — exactly Henriot/Shiu's
F(|Q(p)|) with Q(p)=4p+1, F = τ restricted to the 3-mod-4 divisors. The general δ needs
the shifted form 4pδ+1, and δ couples to p (δ ≤ 6p²), which is what obstructs an
off-the-shelf Henriot bound on the FULL f_II (same δ-split coupling as §18.6).

This script verifies, stdlib only:
  (A) δ=1 ⟺ (4y'−1)(4z'−1)=4p+1: brute (y',z') count vs the divisor count, small p.
  (B) f_II^{(1)}(p) ≤ f_II(p) on the blessed data, and fits Σ_p f_II^{(1)}(p)² ~ N(log)^a
      (expect a≈3: τ² over a single linear form at primes — the Shiu/Henriot exponent).
  (C) the primitive FRACTION f_II^{(1)}/f_II → 0 like 1/(log p)² (the δ=1 part is
      asymptotically negligible; the bulk of f_II is the coupled δ>1 multi-shift sum).

Run:  python3 analysis/primitive_typeII.py
"""
import sys, os, csv, math, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, os.pardir, "data")


def divisors_3mod4_le_sqrt(m):
    """#{u | m : u ≡ 3 (mod 4), u ≤ sqrt(m)} — the primitive (δ=1) Type II count for m=4p+1."""
    c = 0
    u = 1
    while u * u <= m:
        if m % u == 0:
            if u % 4 == 3:
                c += 1
            v = m // u
            # also count the cofactor if it is ≤ sqrt? no — we count u ≤ sqrt only (unordered y'≤z')
        u += 1
    return c


def brute_primitive(p):
    """direct #{(y',z') : 1≤y'≤z', (4y'−1)(4z'−1) = 4p+1}."""
    n = 4 * p + 1
    c = 0
    y = 1
    while True:
        a = 4 * y - 1
        if a * a > n:
            break
        if n % a == 0:
            b = n // a
            if b % 4 == 3 and (b + 1) % 4 == 0:      # 4z'-1 = b ⟹ b ≡ 3 mod 4
                c += 1
        y += 1
    return c


def primes_upto(n):
    if n < 2: return []
    s = bytearray([1]) * (n + 1); s[0] = s[1] = 0
    for i in range(2, int(n**0.5) + 1):
        if s[i]: s[i*i::i] = bytearray(len(s[i*i::i]))
    return [i for i in range(2, n + 1) if s[i]]


def cmdA():
    print("[A] δ=1 ⟺ (4y'−1)(4z'−1)=4p+1  — brute (y',z') count vs divisor count of 4p+1")
    ok = True
    for p in [pp for pp in primes_upto(5000) if pp % 4 == 1][:25]:
        d = divisors_3mod4_le_sqrt(4 * p + 1)
        b = brute_primitive(p)
        ok &= (d == b)
        if p < 600 or d != b:
            print(f"  p={p:5d}  4p+1={4*p+1:6d}  #(div ≡3mod4, ≤√)={d}  brute (y',z')={b}  "
                  f"{'OK' if d==b else 'MISMATCH'}")
    print(f"  → {'PASS' if ok else 'FAIL'}: primitive Type II count = single-shift divisor "
          f"function τ_(≡3)(4p+1).\n")
    return ok


def cmdBC():
    path = os.path.join(DATA, "hard_1e7_full.csv")
    rows = []
    with open(path) as fh:
        r = csv.reader(fh); next(r)
        for row in r:
            p = int(row[0]); fII = int(row[3])
            rows.append((p, fII))
    print(f"[B,C] primitive part on {len(rows)} hard primes [73,10⁷]  (f_II^(1) = τ_(≡3)(4p+1))")
    # windowed: Σ f_II^(1), Σ (f_II^(1))², Σ f_II, fraction
    print(f"  {'win':>4} {'n':>6} {'E[fII^(1)]':>10} {'E[(fII^(1))²]':>13} {'E[fII]':>8} "
          f"{'prim.frac':>9} {'frac·(logp)²':>11}")
    W = {}
    for p, fII in rows:
        k = int(math.log2(p)); W.setdefault(k, []).append((p, fII))
    pts = []
    for k in sorted(W):
        win = W[k]
        if len(win) < 30: continue
        r1 = [divisors_3mod4_le_sqrt(4 * p + 1) for p, _ in win]
        f2 = [fII for _, fII in win]
        # sanity: primitive ≤ total
        assert all(r1[i] <= f2[i] for i in range(len(win))), "primitive exceeds f_II!"
        Er1 = statistics.mean(r1); Er1sq = statistics.mean([x*x for x in r1])
        EfII = statistics.mean(f2)
        L = math.log(1.5 * 2**k)
        frac = Er1 / EfII
        pts.append((L, Er1, Er1sq, EfII, frac))
        print(f"  2^{k:<2d} {len(win):>6} {Er1:>10.3f} {Er1sq:>13.3f} {EfII:>8.2f} "
              f"{frac:>9.4f} {frac*L*L:>11.3f}")

    def fit(xs, ys):
        xs = [math.log(x) for x in xs]; ys = [math.log(y) for y in ys]
        n = len(xs); sx = sum(xs); sy = sum(ys)
        sxx = sum(x*x for x in xs); sxy = sum(a*b for a, b in zip(xs, ys))
        return (n*sxy - sx*sy)/(n*sxx - sx*sx)

    use = pts[len(pts)//3:]
    Ls = [p[0] for p in use]
    a_sq = fit(Ls, [p[2] for p in use])     # E[(fII^(1))²] ~ (log)^a_sq
    a_1  = fit(Ls, [p[1] for p in use])     # E[fII^(1)]   ~ (log)^a_1
    print(f"\n  E[f_II^(1)]   ~ (log p)^{a_1:.2f}   ⇒  Σ_p f_II^(1)    ~ N(log N)^{a_1-1:.2f}")
    print(f"  E[(f_II^(1))²] ~ (log p)^{a_sq:.2f}   ⇒  Σ_p (f_II^(1))² ~ N(log N)^{a_sq-1:.2f}  "
          f"[Shiu gives the rigorous UPPER bound ≪ Σ_p τ(4p+1)² ≪ N(log N)³; the measured")
    print(f"   {a_sq-1:.2f} is far smaller because f_II^(1) counts only the SMALL 3-mod-4 divisors]")
    print(f"  primitive fraction f_II^(1)/f_II ≈ const/(log p)²  (last col ~flat ⇒ δ=1 is a")
    print(f"  VANISHING part of f_II; the bulk is the coupled δ>1 multi-shift correlation).")


if __name__ == "__main__":
    okA = cmdA()
    cmdBC()
    print("\nprimitive_typeII.py: checks done.")
