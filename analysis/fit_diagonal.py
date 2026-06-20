#!/usr/bin/env python3
"""fit_diagonal.py — fit the log-power exponents of the diagonal vs total Type II
second moment, from engines/fp_delta output (REPORT §19).

Reads data/delta_moment_*.csv (win,n,sum_fI,sum_fII,sum_fII2,diag,sum_f,sum_f2).
Per dyadic window k (p ~ 1.5·2^k) we fit the PER-PRIME means against (log p)^θ:

    E[f_II]          ~ (log p)^θ_1     (first moment per prime; ET ⇒ θ_1 = 2... wait,
                                        ET first moment Σf_II ≍ N log²N over π(N)~N/log
                                        primes ⇒ E[f_II] ~ log³ ⇒ θ_1 = 3)
    E[Σ_δ r_δ²]=diag ~ (log p)^θ_D     (diagonal per prime; claim θ_D = θ_1 = 3
                                        ⇒ D(N)=Σ diag ≍ N log²N, first-moment order)
    E[f_II²]         ~ (log p)^θ_2     (total per prime; claim θ_2 = 6 ⇒ Σf_II² ≍ N log⁵N)

So the headline is θ_2 − θ_D ≈ 3: the diagonal is a factor (log p)³ below the total,
i.e. the diagonal does NOT reach N log⁵N — it stalls at the first-moment order N log²N,
and the entire log³ excess is the off-diagonal two-shift correlation.

A cumulative Σ_{p≤N}(·) ≍ N (log N)^a corresponds to per-prime mean ~ (log N)^{a+1}
(since π(N) ~ N/log N).  We fit θ via least squares of log(mean) on log(log p_k).

Run:  python3 analysis/fit_diagonal.py [data/delta_moment_1e6.csv]
"""
import sys, os, csv, math

HERE = os.path.dirname(os.path.abspath(__file__))
path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, os.pardir, "data", "delta_moment_1e6.csv")

rows = []
with open(path) as fh:
    r = csv.DictReader(fh)
    for d in r:
        k = int(d["win"]); n = float(d["n"])
        if n < 30:                      # skip tiny windows (noisy)
            continue
        p_mid = 1.5 * (2 ** k)          # geometric-ish window centre
        rows.append(dict(
            k=k, n=n, p=p_mid, L=math.log(p_mid),
            E_fII = float(d["sum_fII"]) / n,
            E_diag = float(d["diag"]) / n,
            E_fII2 = float(d["sum_fII2"]) / n,
            E_f2   = float(d["sum_f2"]) / n,
            offdiag_frac = 1 - float(d["diag"]) / float(d["sum_fII2"]),
            off_over_diag = (float(d["sum_fII2"]) - float(d["diag"])) / float(d["diag"]),
        ))

def fit_power(rows, key):
    """least-squares slope θ in log(E) = θ·log(log p) + c, over the upper half of windows
    (asymptotic regime).  Returns (θ, c)."""
    use = rows[len(rows)//3:]           # drop the smallest windows
    xs = [math.log(r["L"]) for r in use]
    ys = [math.log(r[key]) for r in use]
    n = len(xs); sx = sum(xs); sy = sum(ys)
    sxx = sum(x*x for x in xs); sxy = sum(x*y for x, y in zip(xs, ys))
    theta = (n*sxy - sx*sy) / (n*sxx - sx*sx)
    c = (sy - theta*sx) / n
    return theta, c

print(f"# fit_diagonal.py  ({os.path.basename(path)}, {len(rows)} usable windows)")
print(f"# {'win':>4} {'n':>8} {'logp':>6} {'E[fII]':>9} {'E[diag]':>9} {'E[fII²]':>10} "
      f"{'offdiag%':>9} {'off/diag':>8}")
for r in rows:
    print(f"  2^{r['k']:<2d} {r['n']:>8.0f} {r['L']:>6.2f} {r['E_fII']:>9.3f} "
          f"{r['E_diag']:>9.3f} {r['E_fII2']:>10.2f} {r['offdiag_frac']:>9.4f} "
          f"{r['off_over_diag']:>8.2f}")

print("\n# fitted exponents  E[·] ~ (log p)^θ   (upper windows; cumulative Σ_{p≤N} ~ N(log N)^{θ-1})")
for key, label, claim in [("E_fII", "E[f_II]   (first moment/prime)", "θ≈3  ⇒ Σf_II ≍ N log²N"),
                          ("E_diag", "E[Σ_δ r_δ²] (diagonal/prime) ", "θ≈3  ⇒ D    ≍ N log²N"),
                          ("E_fII2", "E[f_II²]  (total/prime)     ", "θ≈6  ⇒ Σf_II²≍ N log⁵N"),
                          ("E_f2",   "E[f²]     (full f, headline)", "θ≈6.5 (pre-asymp)")]:
    th, c = fit_power(rows, key)
    print(f"  {label}:  θ = {th:5.2f}   →  Σ_{{p≤N}} ≍ N (log N)^{th-1:.2f}    [{claim}]")

# the headline gap
thD, _ = fit_power(rows, "E_diag")
th2, _ = fit_power(rows, "E_fII2")
print(f"\n  GAP θ(total) − θ(diagonal) = {th2 - thD:.2f}  "
      f"(≈3 ⇒ diagonal is (log)³ below total; the diagonal stalls at the first-moment")
print(f"  order N log²N and CANNOT reach N log⁵N — the whole excess is off-diagonal).")
