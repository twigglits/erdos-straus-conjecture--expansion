#!/usr/bin/env python3
"""Sweep the lever diagnostics across families and n. Saves sweep.json.

Run: PYTHONNOUSERSITE=1 python3 sweep.py
"""
import json
import math
import time
from hunt import (measure, conway_guy_set, powers_of_two, optimal_set,
                  SQRT_2_PI)

# n ranges chosen by memory budget (int8 pmf ~ n*2^n/8 bytes).
CONWAY_NMAX = 26      # ~26*2^26/8 = 218 MB
POW2_NMAX = 24        # powers of 2 have Sigma=2^n-1, array 2^n bytes; 24 -> 16MB
OPT_NMAX = 7          # brute force ceiling (cross-check; Conway-Guy is optimal here)


def row(fam, n, A):
    m = measure(A)
    m['family'] = fam
    return m


def main():
    rows = []
    t0 = time.time()

    for n in range(2, CONWAY_NMAX + 1):
        rows.append(row('conway_guy', n, conway_guy_set(n)))
    print(f"conway_guy done  {time.time()-t0:.1f}s")

    for n in range(2, POW2_NMAX + 1):
        rows.append(row('powers_of_2', n, powers_of_two(n)))
    print(f"powers_of_2 done {time.time()-t0:.1f}s")

    for n in range(2, OPT_NMAX + 1):
        N, S = optimal_set(n)
        rows.append(row('optimal', n, S))
        print(f"  optimal n={n} N={N}")
    print(f"optimal done     {time.time()-t0:.1f}s")

    with open('sweep.json', 'w') as f:
        json.dump(rows, f, indent=0)
    print(f"wrote sweep.json ({len(rows)} rows)")

    # quick on-screen table for the headline columns
    print(f"\n{'fam':12} {'n':>3} {'N':>12} {'Nsqrt(n)/2^n':>13} "
          f"{'N/2^n':>7} {'V=sig/2^n':>10} {'gaussR':>7} "
          f"{'Wcrit':>8} {'occ_crit':>9} {'run_crit':>9} {'Wpack/sd':>9}")
    for r in rows:
        print(f"{r['family']:12} {r['n']:>3} {r['N']:>12} "
              f"{r['c_lower']:>13.4f} {r['c_upper']:>7.4f} {r['V']:>10.4f} "
              f"{r['gauss_ratio']:>7.4f} {r['Wcrit']:>8} {r['occ_crit']:>9.4f} "
              f"{r['run_crit']:>9.5f} {r['pack_over_sd']:>9.4f}")
    print(f"\nrecord constant sqrt(2/pi) = {SQRT_2_PI:.5f}")


if __name__ == "__main__":
    main()
