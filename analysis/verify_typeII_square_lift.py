#!/usr/bin/env python3
"""Reproduce the exact checks for REPORT section 22 (standard library only).

The general result has a written proof in the report. These finite checks
compare the new residue criterion with the old divisor kernel, direct
Egyptian-fraction enumeration, and the stored reference counts. They are
regression checks, not a proof of the conjecture or a Lean formalization.

Run from any directory:
  python3 analysis/verify_typeII_square_lift.py
  python3 analysis/verify_typeII_square_lift.py --output data/typeII_square_lift_verification.json
  python3 analysis/verify_typeII_square_lift.py --check-solver  # additionally requires sympy
"""

import argparse
import csv
import json
from collections import Counter
from fractions import Fraction
from math import gcd, isqrt
from pathlib import Path

from second_moment import primes_upto, spf_sieve, type_counts_and_solutions
from typeII_square_lift import (
    complete_shift_bound,
    divisors,
    old_channel_certificates,
    shift_modulus,
    solution_from_shift_factor,
    square_divisibility_root,
)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def brute_typeII(p):
    """Direct enumeration of x <= y <= z; no divisor-class criterion."""
    result = set()
    for x in range(p // 4 + 1, 3 * p // 4 + 1):
        a = 4 * x - p
        B = p * x
        for y in range(max(x, B // a + 1), 2 * B // a + 1):
            numerator = B * y
            denominator = a * y - B
            if numerator % denominator == 0:
                z = numerator // denominator
                if z >= y and y % p == 0 and z % p == 0:
                    result.add((x, y, z))
    return result


def all_shifts(p):
    """Complete shift enumeration, with the proved bound; only for small p."""
    solutions = set()
    counts = Counter()
    inspected = 0
    old_shifts = set()
    for delta in range(1, complete_shift_bound(p) + 1):
        N = 4 * p * delta + 1
        for D in divisors(N):
            if D * D > N:
                break
            if D % 4 != 3:
                continue
            inspected += 1
            E = N // D
            require(E % 4 == 3, (p, delta, D, E))
            Y, Z = (D + 1) // 4, (E + 1) // 4
            side_condition = (Y * Z) % delta == 0
            residue_condition = (D + 1) % shift_modulus(delta) == 0
            require(side_condition == residue_condition, (p, delta, D))
            sol = solution_from_shift_factor(p, delta, D)
            require((sol is not None) == side_condition, (p, delta, D, sol))
            if sol is not None:
                require(sol not in solutions, ("duplicate", p, delta, D))
                solutions.add(sol)
                counts[delta] += 1
            if (D + 1) % (4 * delta) == 0:
                old_shifts.add(delta)
    return solutions, counts, inspected, old_shifts


def no_old_channel_certificate(p):
    """A small replayable certificate ruling out all m, using divisors of p+a."""
    require(not old_channel_certificates(p), ("old channel found", p))
    bound = (1 + isqrt(1 + 4 * p)) // 4
    rows = []
    for a in range(1, bound + 1):
        ds = divisors(p + a)
        eligible = [q for q in ds if (q + 1) % (4 * a) == 0 and (p + a) // q >= a]
        require(not eligible, (p, a, eligible))
        rows.append({"a": a, "p_plus_a": p + a, "divisors": ds})
    return {"p": p, "a_max": bound, "all_eligible_divisors_absent": True, "rows": rows}


def check_weight_identity():
    """Check the exact sum identity using independent squarefree enumeration."""
    bounds = (1, 2, 10, 100, 1000)
    for T in bounds:
        left = sum((Fraction(1, square_divisibility_root(d)) for d in range(1, T + 1)), Fraction())
        right = Fraction()
        for r in range(1, T + 1):
            if all(r % (q * q) for q in range(2, isqrt(r) + 1)):
                right += sum((Fraction(1, r * t) for t in range(1, isqrt(T // r) + 1)), Fraction())
        require(left == right, ("reciprocal-modulus weight identity", T))
    return bounds


def check_large_prime_solver():
    """Exercise the actual prime-factor search and its certificate adapter."""
    from verify_large_primes import _try_factor, check, solve_esc

    targets = (7, 73, 97, 409, 577, 2521, 5569, 9601, 10000001041)
    for p in targets:
        sol = solve_esc(p)
        require(sol is not None and check(p, sol), ("solver miss or invalid solution", p, sol))
    for p, D in ((409, 7), (9601, 23)):
        sol = _try_factor(4, p, D)
        require(sol is not None and check(p, sol), ("square-lift adapter", p, sol))
    return targets


def verify(prime_limit=2000, hard_limit=10000, complete_limit=200):
    require(5 <= complete_limit <= prime_limit <= hard_limit, "require 5 <= complete <= primes <= hard")
    primes = [p for p in primes_upto(hard_limit) if p >= 5 and (p <= prime_limit or p % 24 == 1)]
    spf = spf_sieve(3 * hard_limit // 4 + 2)
    reference = {}
    ref_path = Path(__file__).resolve().parents[1] / "data" / "fp_small.csv"
    with ref_path.open() as stream:
        reader = csv.reader(stream)
        next(reader)
        for row in reader:
            reference[int(row[0])] = int(row[3])

    root_checks = 0
    for delta in range(1, 1001):
        s = square_divisibility_root(delta)
        require(delta % s == 0 and s * s % delta == 0, (delta, s))
        require(all(t * t % delta for t in range(1, s)), ("root not minimal", delta, s))
        root_checks += 1
    for invalid in (0, -1):
        try:
            square_divisibility_root(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError(("accepted invalid shift", invalid))
    require(solution_from_shift_factor(409, 4, 0) is None, "invalid divisor accepted")
    require(solution_from_shift_factor(409, 4, 3) is None, "nondivisor accepted")

    total = ref_checks = full_checks = candidates = old_count = 0
    hard_no_old, hard_no_square = [], []
    for p in primes:
        _, kernel = type_counts_and_solutions(p, spf)
        expected = {(x, p * Y, p * Z) for x, _, Y, Z, _ in kernel}
        require(len(expected) == len(kernel), ("kernel duplicates", p))
        by_delta = Counter(row[4] for row in kernel)
        has_old = False
        for x, d, Y, Z, delta in kernel:
            total += 1
            D = 4 * Y - 1
            sol = solution_from_shift_factor(p, delta, D)
            require(sol == (x, p * Y, p * Z), (p, delta, D, sol))
            require(Fraction(1, sol[0]) + Fraction(1, sol[1]) + Fraction(1, sol[2]) == Fraction(4, p), sol)
            require(delta <= complete_shift_bound(p), ("bound failure", p, delta))
            # The classical gcd normalization isolates precisely the old c=1 sector.
            h = gcd(Y, Z)
            a, b = Y // h, Z // h
            gap = 4 * x - p
            require((a + b) % gap == 0, (p, a, b, gap))
            c = (a + b) // gap
            require(h % c == 0, (p, h, c))
            g = h // c
            require(delta == g * c * c and x == g * a * b, (p, delta, g, c))
            is_old = (D + 1) % (4 * delta) == 0
            require(is_old == (c == 1), (p, delta, c))
            old_count += int(is_old)
            has_old |= is_old
        certificates = old_channel_certificates(p)
        require(bool(certificates) == has_old, ("all-depth old criterion", p))
        for m, a, b in certificates:
            require((m * a * b, p * m * a, p * m * b) in expected, (p, m, a, b))
        if p % 24 == 1 and not has_old:
            hard_no_old.append(p)
        if p % 24 == 1 and not any(isqrt(delta) ** 2 == delta for delta in by_delta):
            hard_no_square.append(p)
        if p in reference:
            require(len(kernel) == reference[p], ("reference mismatch", p))
            ref_checks += 1
        if p <= complete_limit:
            shifted, counted, inspected, old_shifts = all_shifts(p)
            require(shifted == expected == brute_typeII(p), ("independent enumeration mismatch", p))
            require(counted == by_delta, ("fixed-shift counts", p))
            require(old_shifts == {m for m, _, _ in certificates}, ("old-shift mismatch", p))
            full_checks += 1
            candidates += inspected

    regressions = []
    for p, delta, D in ((409, 4, 7), (9601, 4, 23)):
        cert = no_old_channel_certificate(p)
        sol = solution_from_shift_factor(p, delta, D)
        require(sol is not None and (D + 1) % (4 * delta) != 0, (p, delta, D))
        cert.update({"delta": delta, "divisor": D, "new_modulus": shift_modulus(delta), "solution": sol})
        regressions.append(cert)

    return {
        "scope": "Finite exact regression checks; the general proof is in REPORT section 22. ESC remains open.",
        "prime_limit_all_classes": prime_limit,
        "prime_limit_1_mod_24": hard_limit,
        "complete_shift_and_brute_limit": complete_limit,
        "primes_checked": len(primes),
        "typeII_solutions_checked": total,
        "old_channel_solutions": old_count,
        "reference_primes_checked": ref_checks,
        "full_independent_enumeration_primes": full_checks,
        "candidate_factor_pairs_checked": candidates,
        "square_root_minimality_checks": root_checks,
        "exact_weight_identity_bounds": check_weight_identity(),
        "primes_1_mod_24_with_no_old_channel_at_any_shift": hard_no_old,
        "primes_1_mod_24_with_no_square_shift": hard_no_square,
        "all_depth_old_channel_exclusions": regressions,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prime-limit", type=int, default=2000)
    parser.add_argument("--hard-limit", type=int, default=10000)
    parser.add_argument("--complete-limit", type=int, default=200)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check-solver", action="store_true", help="also exercise the SymPy-based large-prime search")
    args = parser.parse_args()
    result = verify(args.prime_limit, args.hard_limit, args.complete_limit)
    if args.check_solver:
        result["large_prime_solver_checks"] = check_large_prime_solver()
    for key, value in result.items():
        if key != "all_depth_old_channel_exclusions":
            print(f"{key}: {value}")
    for cert in result["all_depth_old_channel_exclusions"]:
        print(f"p={cert['p']}: no old K_m at ANY m; new delta={cert['delta']}, D={cert['divisor']}, solution={cert['solution']}")
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print("PASS: all exact checks passed.")


if __name__ == "__main__":
    main()
