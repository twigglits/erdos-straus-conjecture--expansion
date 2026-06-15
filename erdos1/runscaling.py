#!/usr/bin/env python3
"""How does the longest packed run near the mean scale with sigma?
Critical scale for DFX-tightness is sigma^(2/3).  If maxrun ~ sigma^beta with
beta < 2/3, near-Gaussian dissociated sets provably under-pack the critical
window.

Run: PYTHONNOUSERSITE=1 python3 runscaling.py
"""
import math
import numpy as np
from hunt import conway_guy_set, subset_sum_counts


def longest_central_run(A):
    """Longest run of consecutive integers that are all subset sums, within
    [mu - sigma, mu + sigma]."""
    A = sorted(int(a) for a in A)
    Sigma = sum(A)
    sigma = math.sqrt(sum(a * a for a in A))
    c = subset_sum_counts(A, dtype=np.int8)
    hits = (c > 0).astype(np.int8)
    mu = Sigma // 2
    lo = max(0, int(mu - sigma)); hi = min(Sigma, int(mu + sigma))
    seg = hits[lo:hi + 1]
    idx = np.flatnonzero(np.diff(np.concatenate(([0], seg, [0]))))
    runs = idx[1::2] - idx[0::2]
    return (int(runs.max()) if runs.size else 0), sigma


ns = list(range(12, 27))
logsig, logrun, data = [], [], []
for n in ns:
    R, sigma = longest_central_run(conway_guy_set(n))
    data.append((n, sigma, R))
    logsig.append(math.log(sigma)); logrun.append(math.log(max(R, 1)))

# fit log(maxrun) = beta*log(sigma) + const
b, a = np.polyfit(logsig, logrun, 1)
print(f"{'n':>3} {'sigma':>14} {'maxrun':>8} {'sigma^(2/3)':>12} {'run/crit':>9}")
for n, sigma, R in data:
    crit = sigma ** (2 / 3)
    print(f"{n:>3} {sigma:>14.1f} {R:>8} {crit:>12.1f} {R / crit:>9.4f}")
print(f"\nfit:  maxrun ~ sigma^beta,  beta = {b:.3f}   (critical exponent = 0.667)")
print(f"      => near-Gaussian packing is {'SUB' if b < 2/3 else 'AT/SUPER'}-critical")
