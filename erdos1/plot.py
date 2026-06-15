#!/usr/bin/env python3
"""Plots for the Erdos #1 hunt, from sweep.json.

Run: PYTHONNOUSERSITE=1 python3 plot.py   (needs apt matplotlib + numpy 1.26)
"""
import json
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SQRT_2_PI = math.sqrt(2 / math.pi)          # 0.79788, the record lower-bd const
BOHMAN = 0.22002                            # best upper-bound const (N <= .22*2^n)
CONWAY_LIMIT = 0.23513                      # lim u_n / 2^n (Conway-Guy)

rows = json.load(open('sweep.json'))
def fam(name):
    rs = sorted([r for r in rows if r['family'] == name], key=lambda r: r['n'])
    return ([r['n'] for r in rs], rs)


# ---- Figure 1: the constant landscape --------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

for name, mk in [('conway_guy', 'o-'), ('optimal', 's')]:
    ns, rs = fam(name)
    ax1.plot(ns, [r['c_upper'] for r in rs], mk, label=name, ms=4)
ax1.axhline(BOHMAN, ls='--', c='r', label=f'Bohman upper {BOHMAN}')
ax1.axhline(CONWAY_LIMIT, ls=':', c='g', label=f'Conway-Guy limit {CONWAY_LIMIT}')
ax1.set_xlabel('n'); ax1.set_ylabel('N / 2^n')
ax1.set_title('Truth side: N/2^n stays ~const (=> N ~ c*2^n, conjecture)')
ax1.legend(fontsize=8); ax1.set_ylim(0, 0.55); ax1.grid(alpha=.3)

for name, mk in [('conway_guy', 'o-'), ('optimal', 's')]:
    ns, rs = fam(name)
    ax2.plot(ns, [r['c_lower'] for r in rs], mk, label=name, ms=4)
ax2.axhline(SQRT_2_PI, ls='--', c='purple', label=f'record sqrt(2/pi)={SQRT_2_PI:.3f}')
ns, rs = fam('conway_guy')
ax2.plot(ns, [CONWAY_LIMIT * math.sqrt(n) for n in ns], 'g:',
         label='0.235*sqrt(n)')
ax2.set_xlabel('n'); ax2.set_ylabel('N*sqrt(n) / 2^n')
ax2.set_title('Proof side: N*sqrt(n)/2^n GROWS ~sqrt(n)\n'
              '(record bound = flat line; truth outruns it by sqrt(n))')
ax2.legend(fontsize=8); ax2.grid(alpha=.3)
fig.tight_layout(); fig.savefig('fig1_landscape.png', dpi=110)
print('wrote fig1_landscape.png')


# ---- Figure 2: the lever obstruction ---------------------------------------
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(16, 5))

# (a) V = sigma/2^n: Conway-Guy blows past 0.798; powers of 2 sit at 1/sqrt3
for name, mk in [('conway_guy', 'o-'), ('powers_of_2', '^-'), ('optimal', 's')]:
    ns, rs = fam(name)
    ax1.plot(ns, [r['V'] for r in rs], mk, label=name, ms=4)
ax1.axhline(SQRT_2_PI, ls='--', c='purple', label='sqrt(2/pi)=0.798 (DFX-tight V)')
ax1.axhline(1 / math.sqrt(3), ls=':', c='gray', label='1/sqrt3=0.577 (uniform)')
ax1.set_xlabel('n'); ax1.set_ylabel('V = sigma / 2^n')
ax1.set_title('Variance ratio: near-Gaussian optimum\novershoots the tight value, never sits on it')
ax1.legend(fontsize=8); ax1.grid(alpha=.3)

# (b) run_crit: packing at the critical scale sigma^(2/3). Conway-Guy shatters.
for name, mk in [('conway_guy', 'o-'), ('powers_of_2', '^-')]:
    ns, rs = fam(name)
    ax2.semilogy(ns, [max(r['run_crit'], 1e-4) for r in rs], mk, label=name, ms=4)
ax2.set_xlabel('n'); ax2.set_ylabel('run_crit  (longest packed run / sigma^(2/3))')
ax2.set_title('Packing at critical scale sigma^(2/3):\nGaussian family SHATTERS (->0), packed family stays O(1)')
ax2.legend(fontsize=8); ax2.grid(alpha=.3, which='both')

# (c) the obstruction plane: gaussR (Gaussianity) vs run_crit (packing).
#     DFX-tight needs the TOP-RIGHT corner (Gaussian AND packed) -- empty.
for name, c in [('conway_guy', 'C0'), ('powers_of_2', 'C1'), ('optimal', 'C2')]:
    ns, rs = fam(name)
    xs = [r['gauss_ratio'] for r in rs]
    ys = [max(r['run_crit'], 1e-4) for r in rs]
    ax3.scatter(xs, ys, c=c, label=name, s=18)
ax3.axvspan(0.95, 1.05, color='purple', alpha=.08)
ax3.text(0.96, 2.5, 'Gaussian\n(gaussR->1)', fontsize=8, color='purple')
ax3.set_yscale('log')
ax3.set_xlabel('gaussR  (central density / Gaussian peak;  1 = Gaussian)')
ax3.set_ylabel('run_crit  (packing at sigma^(2/3))')
ax3.set_title('Obstruction plane: tight bound needs TOP-RIGHT\n(Gaussian AND packed) -- the families avoid it')
ax3.legend(fontsize=8); ax3.grid(alpha=.3, which='both')
fig.tight_layout(); fig.savefig('fig2_obstruction.png', dpi=110)
print('wrote fig2_obstruction.png')
