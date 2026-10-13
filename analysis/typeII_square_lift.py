"""Exact fixed-shift Type II certificates (REPORT section 22).

For delta > 0, let s(delta) = product_q q**ceil(v_q(delta)/2). Given
    D*E = 4*n*delta + 1,  D == E == -1 (mod 4),
the side condition delta | ((D+1)/4)*((E+1)/4) is equivalent to
    D == -1 (mod 4*s(delta)).
Thus one residue class includes every solution at this shift. The older
K_delta class modulo 4*delta is sufficient but can miss solutions when delta
has a square factor. These are exact identities, not an existence theorem.

No factoring of n or the complementary divisor E is needed to check a
certificate. See verify_typeII_square_lift.py for independent finite checks.
"""

from math import isqrt


def square_divisibility_root(delta: int) -> int:
    """The least positive s such that delta divides s*s; delta must be positive."""
    if delta < 1:
        raise ValueError("delta must be positive")
    remaining = delta
    root = 1
    prime = 2
    while prime * prime <= remaining:
        exponent = 0
        while remaining % prime == 0:
            remaining //= prime
            exponent += 1
        root *= prime ** ((exponent + 1) // 2)
        prime = 3 if prime == 2 else prime + 2
    if remaining > 1:
        root *= remaining
    return root


def shift_modulus(delta: int) -> int:
    """The complete divisor-class modulus at the specified shift."""
    return 4 * square_divisibility_root(delta)


def solution_from_shift_factor(n: int, delta: int, divisor: int):
    """Return (x, y, z), x <= y <= z, or None for an invalid divisor.

    The returned positive denominators satisfy 4/n = 1/x + 1/y + 1/z.
    Primality is unnecessary for the identity. For prime n >= 5 this is
    Type II. Invalid n/delta raise ValueError; a failed certificate returns
    None and makes no claim about other divisors, shifts, or solution types.
    """
    if n < 1:
        raise ValueError("n must be positive")
    modulus = shift_modulus(delta)
    if divisor < 1 or (divisor + 1) % modulus:
        return None
    shifted = 4 * n * delta + 1
    if shifted % divisor:
        return None
    cofactor = shifted // divisor
    if (cofactor + 1) % modulus:
        return None
    Y, Z = sorted(((divisor + 1) // 4, (cofactor + 1) // 4))
    if (Y * Z) % delta:
        return None
    x, y, z = Y * Z // delta, n * Y, n * Z
    if not (0 < x <= y <= z):
        return None
    if 4 * x * y * z != n * (x * y + x * z + y * z):
        return None
    return x, y, z


def complete_shift_bound(p: int) -> int:
    """An upper bound on delta for every Type II solution, for odd prime p >= 5.

    The caller must establish primality. Put a0 = (-p) mod 4. The divisor
    kernel gives delta <= ((p+a0+4)/(4*a0))**2; division is exact floor here.
    This is a completeness bound, not a practical recommendation to scan
    every shift for large p.
    """
    if p < 5 or p % 2 == 0:
        raise ValueError("p must be an odd prime at least 5")
    a0 = (-p) % 4
    return (p + a0 + 4) ** 2 // (16 * a0 * a0)


def divisors(n: int):
    """All positive divisors in increasing order; trial division for small checks."""
    if n < 1:
        raise ValueError("n must be positive")
    lower, upper = [], []
    for d in range(1, isqrt(n) + 1):
        if n % d == 0:
            lower.append(d)
            if d * d != n:
                upper.append(n // d)
    return lower + upper[::-1]


def old_channel_certificates(p: int):
    """Enumerate ALL old K_m certificates at any m, in finite exact bounds.

    An old certificate is equivalent to p = 4*m*a*b-a-b with 1 <= a <= b.
    Then 4*a*a-2*a <= p, and q = 4*m*a-1 divides p+a with b=(p+a)/q.
    Returns (m, a, b) triples. An empty list rules out this restricted
    family at every shift; it does not rule out Erdős--Straus solutions.
    """
    if p < 1:
        raise ValueError("p must be positive")
    bound = (1 + isqrt(1 + 4 * p)) // 4
    result = []
    for a in range(1, bound + 1):
        for q in divisors(p + a):
            if (q + 1) % (4 * a) == 0 and (p + a) // q >= a:
                m = (q + 1) // (4 * a)
                b = (p + a) // q
                assert 4 * m * a * b - a - b == p
                result.append((m, a, b))
    return result
