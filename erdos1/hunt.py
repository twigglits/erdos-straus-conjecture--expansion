#!/usr/bin/env python3
"""Erdos #1 (distinct subset sums) — the constant hunt.

Problem: A = {a_1<...<a_n} subset Z+ with all 2^n subset sums distinct
(dissociated). Lower-bound N = max a_i. Record: N >= C(n, n//2) ~ sqrt(2/pi)*2^n/sqrt(n)
(Elkies-Gleason / Dubroff-Fox-Xu 2021). $500 to remove the sqrt(n).

This file is the experimental lab. It computes, for a dissociated set, the two
quantities whose simultaneous extremality makes the DFX bound tight:
  (a) PACKING near the mean  -> pmf locally flat at 2^-n (interval of subset sums)
  (b) local GAUSSIANITY      -> pmf central density ~ sqrt(2/pi)/sigma
The lever: how wide a window can a *small-N* dissociated set keep perfectly
packed?  If forced to o(sigma), DFX is tight; a constant fraction of sigma would
beat sqrt(2/pi).

Conventions: subset sums T = sum_{i in S} a_i, uniform S, 2^n distinct values in
[0, Sigma], Sigma = sum a_i, mean mu = Sigma/2, sd(T) = sigma/2 with
sigma^2 = sum a_i^2.  Record constant sqrt(2/pi) = 0.79788.

Run:  PYTHONNOUSERSITE=1 python3 hunt.py        (self-checks + tables)
"""
import math
import numpy as np

SQRT_2_PI = math.sqrt(2.0 / math.pi)  # 0.7978845608... the record constant


# ---------------------------------------------------------------------------
# core: dissociativity + subset-sum pmf
# ---------------------------------------------------------------------------
def subset_sum_counts(A, dtype=np.int64):
    """Counts c[k] = #{S subset A : sum(S)=k}, k in [0, sum A].
    dtype int64 is overflow-safe for arbitrary A; int8 is safe ONLY for
    dissociated A (then all counts are 0/1) and uses 8x less memory."""
    total = int(sum(A))
    c = np.zeros(total + 1, dtype=dtype)
    c[0] = 1
    hi = 0
    for a in A:
        a = int(a)
        c[a:hi + a + 1] += c[0:hi + 1]
        hi += a
    return c


def is_dissociated(A):
    """All 2^n subset sums distinct <=> every count is 0 or 1."""
    c = subset_sum_counts(A)
    return int(c.max()) == 1


def dissociated_fast(A):
    """Incremental check via the difference set, O(2^|A|). For search loops."""
    SA = {0}
    for a in A:
        a = int(a)
        shifted = {s + a for s in SA}
        if SA & shifted:          # a in SA - SA  => a subset-sum collision
            return False
        SA |= shifted
    return True


# ---------------------------------------------------------------------------
# the measurement: realized constant + the two DFX defects
# ---------------------------------------------------------------------------
def measure(A):
    A = sorted(int(a) for a in A)
    n = len(A)
    N = A[-1]
    sig2 = sum(a * a for a in A)         # = sum a_i^2
    sigma = math.sqrt(sig2)
    Sigma = sum(A)
    c = subset_sum_counts(A, dtype=np.int8)   # 0/1 for dissociated A
    # robust dissociativity certificate (immune to int8 wrap): exactly 2^n
    # distinct subset sums must be hit, and no count exceeds 1.
    nhit = int(np.count_nonzero(c))
    assert nhit == 2**n and int(c.max()) == 1, ("not dissociated", nhit, 2**n)

    # realized constants
    c_lower = N * math.sqrt(n) / 2**n    # compare to record sqrt(2/pi)=0.798
    c_upper = N / 2**n                    # compare to Bohman 0.22002
    V = sigma / 2**n                      # variance ratio; powers of 2 -> 1/sqrt3

    # PACKING: largest symmetric window around mu where EVERY integer is a subset
    # sum (pmf flat at 2^-n). hits[k]=1 iff k is a subset sum.
    hits = (c > 0).astype(np.int8)
    mu = Sigma / 2.0
    # half-integer mean if Sigma odd; center the window on the nearest sites.
    lo_c = int(math.floor(mu))
    hi_c = int(math.ceil(mu))
    # grow W until a gap appears on either side
    Wpack = 0
    while True:
        lo = lo_c - Wpack
        hi = hi_c + Wpack
        if lo < 0 or hi > Sigma:
            break
        if hits[lo] and hits[hi]:
            Wpack += 1
        else:
            break
    packed_halfwidth = Wpack             # # of consecutive filled sites each side
    # express as a fraction of the standard deviation sigma/2
    pack_over_sd = packed_halfwidth / (sigma / 2.0)

    # OCCUPANCY profile: fraction of integer sites that are subset sums, in
    # symmetric windows of half-width W = frac * sd, sd = sigma/2.  Perfect
    # packing -> 1.0.  Gaussian bulk stays ~1 only while flat (W << sd).
    sd = sigma / 2.0
    occ = {}
    for frac in (0.25, 0.5, 1.0, 2.0):
        W = int(round(frac * sd))
        lo = max(0, int(round(mu)) - W)
        hi = min(Sigma, int(round(mu)) + W)
        occ[frac] = float(np.count_nonzero(hits[lo:hi + 1])) / (hi - lo + 1)

    # local GAUSSIANITY: SMOOTHED central pmf density vs Gaussian peak.
    # smoothing half-width h ~ sqrt(sd) << sd kills the single-point parity noise
    # while staying in the flat-Gaussian core.  Gaussian peak density =
    # 1/(sd*sqrt(2pi)); central density = (mass in [mu-h,mu+h]) / (2h+1).
    cmid = int(round(mu))
    h = max(1, int(round(math.sqrt(sd))))
    lo = max(0, cmid - h); hi = min(Sigma, cmid + h)
    central_density = (np.count_nonzero(hits[lo:hi + 1]) * 2.0**-n) / (hi - lo + 1)
    gauss_peak = 1.0 / (sd * math.sqrt(2 * math.pi))
    gauss_ratio = central_density / gauss_peak     # ->1 at DFX equality

    # DFX-CRITICAL scale: window half-width W ~ sigma^(2/3) (the L* that
    # optimises the curvature/edge trade-off).  occ_crit = occupancy there;
    # run_crit = longest gap-free run there / W (arrangement, not just count).
    Wc = max(1, int(round(sigma ** (2.0 / 3.0))))
    lo = max(0, cmid - Wc); hi = min(Sigma, cmid + Wc)
    seg = hits[lo:hi + 1]
    occ_crit = float(np.count_nonzero(seg)) / seg.size
    # longest run of consecutive 1s in seg
    if seg.any():
        idx = np.flatnonzero(np.diff(np.concatenate(([0], seg, [0]))))
        runs = idx[1::2] - idx[0::2]
        run_crit = int(runs.max()) / Wc
    else:
        run_crit = 0.0

    # Fourier identity: dissociated  <=>  (1/2pi) int cos^2 product = 2^-n
    #   == sum_k f(k)^2 (L2 mass).  here f(k)=c[k]/2^n.
    l2 = float(np.sum((c.astype(np.float64) / 2**n) ** 2))   # should equal 2^-n

    return dict(n=n, N=N, c_lower=c_lower, c_upper=c_upper, V=V,
                sigma=sigma, Sigma=Sigma, packed_halfwidth=packed_halfwidth,
                pack_over_sd=pack_over_sd, gauss_ratio=gauss_ratio,
                Wcrit=Wc, occ_crit=occ_crit, run_crit=run_crit,
                occ=occ, l2=l2, l2_target=2.0**-n)


# ---------------------------------------------------------------------------
# families
# ---------------------------------------------------------------------------
def powers_of_two(n):
    return [2**i for i in range(n)]


def conway_guy_seq(K):
    """A005318 u_0..u_K.  u_k = 2 u_{k-1} - u_{k-1-r(k)},  r(k)=m on the
    triangular block k in [2 + m(m-1)/2, 2 + m(m+1)/2).  Validated below by
    checking every constructed Conway-Guy set is dissociated."""
    u = [0, 1]
    while len(u) <= K:
        k = len(u)
        m = 1
        while 2 + m * (m + 1) // 2 <= k:
            m += 1
        r = m
        u.append(2 * u[k - 1] - u[k - 1 - r])
    return u[:K + 1]


def conway_guy_set(n):
    """Conway-Guy dissociated n-set: {u_n - u_{n-i} : i=1..n}, N = u_n.
    Conjecturally minimal-N for small n (proven optimal to n~22)."""
    u = conway_guy_seq(n)
    return sorted(u[n] - u[n - i] for i in range(1, n + 1))


def optimal_set(n, Mmax=None):
    """Brute-force minimal-N dissociated n-set (ground-truth extremal object).
    Returns (N, set) for the lexicographically-first minimal-max witness.
    Feasible to ~n=13."""
    if n == 0:
        return (0, [])
    if Mmax is None:
        Mmax = 2**n  # generous ceiling

    best = [None]  # (N, set)

    def dfs(cur, SA, start):
        k = len(cur)
        if k == n:
            if best[0] is None or cur[-1] < best[0][0]:
                best[0] = (cur[-1], list(cur))
            return
        cap = best[0][0] - 1 if best[0] is not None else Mmax
        # need n-k more strictly-increasing elements <= cap
        a = start
        while a <= cap - (n - k - 1):
            shifted = {s + a for s in SA}
            if not (SA & shifted):           # stays dissociated
                cur.append(a)
                dfs(cur, SA | shifted, a + 1)
                cur.pop()
            a += 1

    dfs([], {0}, 1)
    return best[0]


# ---------------------------------------------------------------------------
# self-check
# ---------------------------------------------------------------------------
def demo():
    # dissociativity
    assert is_dissociated([1, 2, 4, 8])
    assert is_dissociated([3, 5, 6, 7])
    assert not is_dissociated([1, 2, 3])         # 1+2=3
    assert dissociated_fast([3, 5, 6, 7])
    assert not dissociated_fast([1, 2, 3])

    # powers of 2: subset sums fill [0,2^n-1] exactly once; V = 1/sqrt3
    m = measure(powers_of_two(10))
    assert m['N'] == 512
    assert abs(m['V'] - 1 / math.sqrt(3)) < 1e-5, m['V']   # ~2^-n correction
    assert abs(m['l2'] - m['l2_target']) < 1e-18  # dissociativity identity
    # powers of 2 pack PERFECTLY everywhere: window runs to the edge
    assert m['packed_halfwidth'] == 512, m['packed_halfwidth']

    # Conway-Guy sequence reproduces A005318, and EVERY constructed set is
    # dissociated (validates the recurrence).
    u = conway_guy_seq(12)
    assert u[:12] == [0, 1, 2, 4, 7, 13, 24, 44, 84, 161, 309, 594], u
    for n in range(1, 21):   # validates the recurrence; heavier n trusted in runs
        S = conway_guy_set(n)
        assert is_dissociated(S), (n, S)
        assert S[-1] == conway_guy_seq(n)[n]

    # optimal small-n sets must reproduce A276661 = A005318: 1,2,4,7,13,24,44
    a276661 = {1: 1, 2: 2, 3: 4, 4: 7, 5: 13, 6: 24, 7: 44}
    for n, Nexp in a276661.items():
        Nopt, S = optimal_set(n)
        assert Nopt == Nexp, (n, Nopt, Nexp, S)
        assert is_dissociated(S)
        # Conway-Guy IS optimal here
        assert conway_guy_set(n)[-1] == Nexp, n
    print("demo: all checks pass")


if __name__ == "__main__":
    demo()
