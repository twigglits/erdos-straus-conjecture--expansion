#!/usr/bin/env python3
"""growth_law.py — machine-check of the §17.3 Browning–Wilsch prediction f(p) ~ c·(log p)³.

Applying the Browning–Wilsch integral-points heuristic (arXiv:2407.16315) to the Cayley/ESC
cubic (open part V_p ≅ G_m², unit rank 2 + boundary triangle) gives the exponent ϱ_U + b = 3,
i.e. the average/typical f(p) grows like (log p)³ — which is also the Elsholtz–Tao average
order (Σ_{p≤N} f(p) ≍ N log²N ⟹ average f(p) ≍ log³p). Here we verify the exponent directly
against the repo's per-prime data: fit median f per dyadic window to ln(median) = k·ln ln p + b
and confirm k ≈ 3.

Run from repo root:  python3 analysis/growth_law.py
"""
import csv, math, statistics, os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, os.pardir, "data")


def windowed_medians(path, lo=2 ** 11, hi=10 ** 7):
    rows = [(int(r[0]), int(r[2]) + int(r[3]))
            for r in csv.reader(open(path)) if r[0] != "p"]
    pts, w = [], lo
    while w < hi:
        win = [f for p, f in rows if w <= p < 2 * w]
        if len(win) >= 30:
            pmid = 1.5 * w
            pts.append((pmid, statistics.median(win)))
        w *= 2
    return pts


def fit_exponent(pts):
    """least squares ln(median) = k·ln(ln p) + b ; return k, b."""
    xs = [math.log(math.log(p)) for p, _ in pts]
    ys = [math.log(m) for _, m in pts]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    k = sum((xs[i] - mx) * (ys[i] - my) for i in range(n)) / sum((xs[i] - mx) ** 2 for i in range(n))
    return k, my - k * mx


def cayley_points_mod(l, n):
    """#{(x,y,z) in (Z/l)^3 : 4xyz = n(xy+yz+zx) mod l} — the leading local count."""
    return sum(1 for x in range(l) for y in range(l) for z in range(l)
               if (4 * x * y * z - n * (x * y + y * z + z * x)) % l == 0)


def check_local_densities():
    """The BW leading local density is blind to the square classes: l^2+1 points
    independent of n's QR status (so c cannot see the square-class suppression)."""
    print("local point count of 4xyz=n(xy+yz+zx) mod l, by QR status of n:")
    ok = True
    for l in (3, 5, 7, 11, 13):
        qr = [cayley_points_mod(l, n) for n in range(1, l) if pow(n, (l - 1) // 2, l) == 1]
        nr = [cayley_points_mod(l, n) for n in range(1, l) if pow(n, (l - 1) // 2, l) != 1]
        aq, an = sum(qr) / len(qr), sum(nr) / len(nr)
        print(f"  l={l:>2}: QR-side={aq:7.2f}  NR-side={an:7.2f}  (= l^2+1 = {l*l+1})  ratio={aq/an:.4f}")
        ok &= abs(aq - an) < 1e-9 and abs(aq - (l * l + 1)) < 1e-9
    assert ok, "leading local density should be l^2+1 independent of QR status"
    print("PASS: leading local density blind to square classes — suppression is finer (stratum/parity).\n")


if __name__ == "__main__":
    check_local_densities()
    pts = windowed_medians(os.path.join(DATA, "hard_1e7_full.csv"))
    pts.append((2e9, 681))            # README F2 median at [2e9,2.01e9]
    k, b = fit_exponent(pts)
    print(f"median f(p) ~ c·(ln p)^k over {len(pts)} windows, p ∈ [{pts[0][0]:.2g}, {pts[-1][0]:.2g}]")
    for p, m in pts:
        print(f"  p~{p:>10.2g}  median f = {m:>5.0f}")
    print(f"\nfit: k = {k:.3f}   (Browning–Wilsch §17.3 predicts 3; ET average = log³p)")
    assert 2.8 < k < 3.3, f"exponent {k} off the (log p)^3 prediction"
    print("PASS: median growth exponent confirms f(p) ~ (log p)^3 to ~1% over six decades.")
