#!/usr/bin/env python3
"""Symbolic verification of every decomposition identity in Ghermoul's paper
"Almost a Complete Proof of the Generalized Erdős–Straus Conjecture: 5/a = 1/b+1/c+1/d"
(arXiv:2508.07367v1).

Companion numeric/symbolic cross-check for the Lean reproduction
(Subsetsums/GeneralizedErdosStraus.lean), same spirit as analysis/verify_lemmas.py.

Each check confirms  LHS - RHS == 0  identically as a rational function.
"""
import sympy as sp

x, y, z, k, q = sp.symbols('x y z k q', integer=True)
ok = True

def chk(tag, lhs, rhs):
    global ok
    d = sp.simplify(lhs - rhs)
    good = (d == 0)
    ok &= good
    print(f"  [{'OK ' if good else 'FAIL'}] {tag}")
    if not good:
        print(f"        residual = {d}")

inv = lambda e: sp.Integer(1)/e

print("== Lemma 2.2 / Theorem 2.1(1): a not = 1 (mod 5), unconditional ==")
chk("(2.1) a=5k",      inv(k),            inv((k+1)**2) + inv(k*(k+1)**2) + inv(k+1))
chk("(2.2a) k=2q",     5*inv(10*q+2),     inv(10*q**2+7*q+1)  + inv(20*q**2+14*q+2)  + inv(2*q+1))
chk("(2.2b) k=2q+1",   5*inv(10*q+7),     inv(10*q**2+17*q+7) + inv(20*q**2+34*q+14) + inv(2*q+2))
chk("(2.3) a=5k+3",    5*inv(5*k+3),      inv(5*k**2+8*k+3)   + inv(5*k**2+8*k+3)    + inv(k+1))
chk("(2.4) a=5k+4",    5*inv(5*k+4),      inv(5*(k+1)**2*(5*k+4)) + inv(5*(k+1)**2)  + inv(k+1))

print("== Bridge identities for a = 5q+1 (the p1/p2/p3 engine) ==")
p1 = z*(x*(5*y-1)-y) - x
chk("(17) p1 full",
    5*inv(5*p1+1),
    inv((x*(5*y-1)-y)*((5*y-1)*z-1)*(5*x*((5*y-1)*z-1)-5*y*z+1))
    + inv(z*(x*(5*y-1)-y)*((5*y-1)*z-1))
    + inv(z*(x*(5*y-1)-y)))
p2 = x*(5*y-3) - 2*y + 1
chk("(25) p2 full",
    5*inv(5*p2+1),
    inv((5*x-2)*(10*y**2-11*y+3)) + inv(10*x*y-5*x-4*y+2) + inv(10*x*y-5*x-4*y+2))
p3 = x*(10*y-7) - 6*y + 4
chk("(27) p3 full",
    5*inv(5*p3+1),
    inv(2*(5*x-3)*(30*y**2-41*y+14)) + inv(30*x*y-20*x-18*y+12) + inv(15*x*y-10*x-9*y+6))

print("== Theorem 2.1(2): a=5q+1, q !=0 (mod 12) -- 11 residues C.1.x / C.2.x ==")
A = lambda i: 1 + 5*(i + 12*x)
chk("(18) q=2  (mod12)", 5*inv(A(2)),  inv(3*(1+4*x)*(3+16*x))   + inv(3*(3+16*x)*(11+60*x))  + inv(3*(1+4*x)))
chk("(19) q=5  (mod12)", 5*inv(A(5)),  inv(6*(1+2*x)*(7+16*x))   + inv(6*(7+16*x)*(13+30*x))  + inv(3*(2+4*x)))
chk("(20) q=8  (mod12)", 5*inv(A(8)),  inv(3*(3+4*x)*(11+16*x))  + inv(3*(11+16*x)*(41+60*x)) + inv(3*(3+4*x)))
chk("(21) q=6  (mod12)", 5*inv(A(6)),  inv((7+12*x)*(8+15*x))    + inv((7+12*x)*(8+15*x)*(31+60*x)) + inv(7+12*x))
chk("(22) q=10 (mod12)", 5*inv(A(10)), inv((11+12*x)*(13+15*x))  + inv(3*(11+12*x)*(13+15*x)*(17+20*x)) + inv(11+12*x))
chk("(28) q=1  (mod12)", 5*inv(A(1)),  inv(6+60*x)   + inv(3+30*x)  + inv(3+30*x))
chk("(29) q=9  (mod12)", 5*inv(A(9)),  inv(46+60*x)  + inv(23+30*x) + inv(23+30*x))
chk("(30) q=3  (mod12)", 5*inv(A(3)),  inv(16+60*x)  + inv(8+30*x)  + inv(8+30*x))
chk("(31) q=11 (mod12)", 5*inv(A(11)), inv(56+60*x)  + inv(28+30*x) + inv(28+30*x))
chk("(32) q=4  (mod12)", 5*inv(A(4)),  inv(6*(7+20*x)) + inv(14+40*x) + inv(7+20*x))
chk("(33) q=7  (mod12)", 5*inv(A(7)),  inv(8*(3+5*x)) + inv(24*(3+5*x)) + inv(4*(3+5*x)))

print("== Theorem 2.1(3): q=12u, u !=0 (mod 7) -- 6 residues (34)-(39) ==")
B = lambda i: 420*x + 60*i + 1     # 5*12*(7x+i)+1
chk("(34) u=1 (mod7)", 5*inv(B(1)), inv(84*x+14) + inv(7*(48*x+7)*(420*x+61)) + inv(14*(6*x+1)*(48*x+7)))
# (35) as PRINTED is a copy-paste of (34); confirm it is genuinely WRONG (a paper typo):
_printed35 = sp.simplify(5*inv(B(2)) - (inv(84*x+14) + inv(7*(48*x+7)*(420*x+61)) + inv(14*(6*x+1)*(48*x+7))))
print(f"  [{'OK ' if _printed35 != 0 else 'FAIL'}] (35) PRINTED confirmed a typo (residual != 0)")
ok &= (_printed35 != 0)
# (35) CORRECT, from the general p4 form at y=1  (5/((420x+121)(5y-4)) at y=1):
chk("(35) CORRECT (p4,y=1)", 5*inv(B(2)),
    inv(2*(3*x+1)*(420*x+121)) + inv(6*(3*x+1)*(28*x+9)*(420*x+121)) + inv(3*(28*x+9)))
chk("(36) u=3 (mod7)", 5*inv(B(3)), inv(84*x+39) + inv(3*(28*x+13)*(30*x+13)*(420*x+181)) + inv(3*(28*x+13)*(30*x+13)))
chk("(37) u=4 (mod7)", 5*inv(B(4)), inv(8820*x**2+10353*x+3038) + inv((12*x+7)*(105*x+62)*(420*x+241)) + inv(84*x+49))
chk("(38) u=5 (mod7)", 5*inv(B(5)), inv(2520*x**2+3714*x+1368) + inv(14*(4*x+3)*(60*x+43)*(105*x+76)) + inv(84*x+63))
chk("(39) u=6 (mod7)", 5*inv(B(6)), inv(2520*x**2+4434*x+1950) + inv(2*(15*x+13)*(28*x+25)*(420*x+361)) + inv(84*x+75))

print("== Theorem 2.1(4): q=84v, v !=0 (mod 3) -- 2 residues (40)-(41) ==")
C = lambda i: 1260*x + 420*i + 1   # 5*84*(3x+i)+1
chk("(40) v=1 (mod3)", 5*inv(C(1)),
    inv((126*x+43)*(140*x+47)*(1260*x+421)) + inv(35280*x**2+23884*x+4042) + inv(252*x+86))
chk("(41) v=2 (mod3)", 5*inv(C(2)),
    inv((28*x+19)*(1260*x+841)) + inv(2*(28*x+19)*(126*x+85)*(1260*x+841)) + inv(252*x+170))

print("== Remark 2 representative reduced forms ==")
chk("R2 C.1 p1(1,1,z)", 5*inv(5*(3*z-1)+1), inv(3*z*(4*z-1)) + inv(3*(4*z-1)*(15*z-4)) + inv(3*z))
chk("R2 C.1 p1(1,y,1)", 5*inv(5*(4*y-2)+1), inv((4*y-1)*(5*y-2)) + inv((4*y-1)*(5*y-2)*(20*y-9)) + inv(4*y-1))
chk("R2 C.2 c=2",       5*inv(5*(2*x+1)+1), inv(10*x+6) + inv(5*x+3) + inv(5*x+3))
chk("R2 C.2 c=3",       5*inv(5*(3*x+1)+1), inv(6*(5*x+2)) + inv(10*x+4) + inv(5*x+2))

print("== Covering: every q>=1 hits a proven residue OR q=0 (mod 252) ==")
# proven 5q+1 residues: q%12 in 1..11 ; or q%12=0 & u=q/12, u%7 in 1..6 ; or u%7=0 & v=u/7, v%3 in 1..2
def covered(qq):
    if qq % 12 != 0: return True
    u = qq // 12
    if u % 7 != 0: return True
    v = u // 7
    if v % 3 != 0: return True
    return False  # q % 252 == 0
miss = [qq for qq in range(1, 5000) if not covered(qq) and qq % 252 != 0]
extra = [qq for qq in range(1, 5000) if covered(qq) and qq % 252 == 0]
chk("covering == (q % 252 != 0)", len(miss) + len(extra), 0)

print()
print("ALL IDENTITIES VERIFIED" if ok else "SOME CHECKS FAILED (see above)")
import sys; sys.exit(0 if ok else 1)
