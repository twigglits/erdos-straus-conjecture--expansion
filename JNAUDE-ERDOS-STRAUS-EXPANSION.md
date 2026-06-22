
<div align="justify">

# The Erdős–Straus count is governed by a quadratic $L$-value

### An experimental route from solution-counting to $L(1,\chi_p)$, with a machine-verified account of the wall

**J. Naude**, with derivations, engines, and analyses produced in human–AI collaboration (Claude, Anthropic; see the repository commit trailers). Computational artifacts, datasets, and machine proofs accompany this paper in [`REPORT.md`](REPORT.md), [`analysis/`](analysis/), [`engines/`](engines/), and the Lean 4 development [`erdos1/subsetsums/`](erdos1/subsetsums/).

*Working paper, revision of 2026-06-21. The Erdős–Straus conjecture is **open**; nothing here proves or disproves it. The contribution is a measured, reproducible, structurally-identified law for the solution count, a machine-verified delimitation of exactly why the elementary toolbox cannot close the problem, and a complete map of the analytic wall the law runs into.*


---

## Abstract


Let $f(p)$ denote the number of unordered positive solutions of $\tfrac{4}{p}=\tfrac1x+\tfrac1y+\tfrac1z$. Building on the divisor-sum framework of Elsholtz and Tao (2013), we report an empirical law, verified across $278{,}570$ primes of the six hard residue classes $\bmod\,840$ from $73$ to $2.01\times10^{9}$ and reproduced here by direct re-execution:

$$ f(p)\ \approx\ (\log p)^{3}\cdot L(1,\chi_p)^{-c},\qquad \chi_p=\Big(\tfrac{\cdot}{p}\Big),\quad c>0, $$

where $\chi_p$ is the real quadratic character of $\mathbb{Q}(\sqrt p)$ and $L(1,\chi_p)=2h(p)\log\varepsilon_p/\sqrt p$ is its Dirichlet $L$-value — the class number times the regulator. Concretely, $\operatorname{corr}\big(\ln f,\ \ln L(1,\chi_p)\big)=-0.62$ ($n=14{,}955$ primes near $10^9$, re-run for this paper; $95\%$ CI $\approx\pm0.01$, and unchanged under partial correlation controlling for $\log p$), stable across Euler-product truncations $X=50\ldots1500$. The exponent $c$ is **not** a fixed constant: measured in narrow windows it *declines monotonically* with scale — from $\approx0.93$ at $10^{6}$ to $\approx0.46$ at $10^{10}$ (§8.2) — while the correlation itself stays near $-0.62$, so the scale-robust statement is the **sign** of the coupling, not a numerical exponent. The **more** primes split in $\mathbb{Q}(\sqrt p)$, the **fewer** Erdős–Straus solutions $p$ has.

We arrive at the law by a documented chain: (i) a cross-validated solution-count dataset and a lognormal law for $f(p)$ confirmed by blind prediction; (ii) a machine-verified kernel reducing $f(p)$ to divisors of shifted integers in residue classes, together with the square obstruction re-proved in full and formalized in Lean 4 + Mathlib ($20$ theorems, complete with no unproved steps); (iii) a residual spectrum exposing a quadratic-residue ladder $s_q\approx 18\,q^{-1.95}$ — "non-residues richer at every modulus" — which is the first-order shadow of the character $\chi_p$; (iv) a Fourier decomposition of the local divisor density over Dirichlet characters $\bmod\,\ell$ that isolates the quadratic character $(p/\ell)$ as the dominant non-trivial signal at every $\ell\in\{11,13,17,19,23\}$ ($14$–$47\sigma$), whose Euler product is by definition a power of $L(1,\chi_p)$.

The mechanism is the McKee–Zhou identity, by which the singular series of $\sum_{n\le N}\tau(F(n))$ for an irreducible quadratic $F$ equals $2L(1,\chi_{\mathrm{disc}\,F})/\zeta(2)$ — the precedent that divisor/representation counts are governed by quadratic $L$-values (Gauss–Siegel). The law is **not** a theorem: deriving the singular series via McKee–Zhou blocks at a verified obstruction (the Type II side-condition $\delta\mid y'z'$ makes $f_{\mathrm{II}}$ a *two-shift* divisor correlation, not a single $\sum\tau(F)$), which is the two-shift Titchmarsh estimate flagged out of reach by Elsholtz–Tao and blocked by the classical (Selberg) $\sqrt x$ parity barrier. What the $L$-lens does buy is sharp and unconditional in spirit: any Erdős–Straus exception must lie in the **extreme class-number tail** (a Granville–Soundararajan super-rare set), Siegel zeros are the **best** case rather than the worst, and the size budget — even at the maximal order $L(1,\chi_p)\asymp e^{\gamma}\log\log p$ — never threatens $f>0$.


---

## 1. Introduction

### 1.1 The conjecture


The Erdős–Straus conjecture (Erdős and Straus, 1948) asserts that for every integer $n\ge2$ there exist positive integers $x,y,z$ with

$$ \frac{4}{n}=\frac1x+\frac1y+\frac1z. $$

It suffices to prove it for primes $p$, and solutions are known to exist for every $p$ except possibly those in the six "square classes"

$$ p\equiv 1^2,\,11^2,\,13^2,\,17^2,\,19^2,\,23^2 \pmod{840}, $$

where every covering-congruence identity provably dies (Mordell; Schinzel; Yamamoto). The statement has been verified computationally to $10^{17}$ (Salez, 2014) and to $10^{18}$ (Mihnea–Bogdan, 2025); it remains open. Throughout, $p\ge5$ is prime, and on the hard classes $p\equiv1\pmod4$, so $\mathbb{Q}(\sqrt p)$ is real with discriminant $p$ and $\chi_p=(\tfrac{\cdot}{p})$ satisfies $(p/\ell)=(\ell/p)$ by reciprocity.


### 1.2 What was known


The deepest count-theoretic results are due to **Elsholtz and Tao** (*J. Aust. Math. Soc.* **94** (2013), 50–105; arXiv:1107.1010). Writing $f(p)$ for the number of solutions with $x\le y\le z$, they prove, among much else:

- a first-moment bound $\displaystyle N\log^2 N \ll \sum_{p\le N} f(p)\ll N\log^2 N\log\log N$ (so the *average* order of $f(p)$ is $\log^3 p$, up to a $\log\log$ factor that they note but cannot remove);
- pointwise bounds $f(p)\ll p^{3/5+o(1)}$ and a lower bound $f(p)\ge(\log p)^{0.549}$ valid on a **density-1** set of primes (their Thm 1.8);
- a Type I / Type II decomposition realizing $f(p)$ as a sum of divisor counts of shifted integers;
- the remark (their Remark 1.3) that even the **second moment** $\sum_p f(p)^2$ "seems to … lie out of reach of our methods, as the level of the relevant divisor sums becomes too great to handle," and a Poisson/Borel–Cantelli heuristic for solubility (Remark 1.2).

The strongest "almost all" statement is **Vaughan (1970)**: the number of $n\le N$ for which $4/n$ is *not* so expressible is $\ll N\exp\!\big(-c(\log N)^{2/3}\big)$. The square classes are immune to covering systems by **Schinzel** and **Yamamoto** ($f_I(c^2)=f_{II}(c^2)=0$ for odd squares, by quadratic reciprocity), so that the conjecture's content is precisely the gap "density $1\to$ all primes." The absence of a Brauer–Manin obstruction *to the existence of solutions* (Bright–Loughran, 2020 — their Brauer group is a nontrivial $\mathbb{Z}/2\mathbb{Z}$, but it obstructs only strong approximation, not existence) confirms that the difficulty is **analytic, not cohomological**.


### 1.3 Contribution


This paper's central result is the **$L$-function law** of the abstract: $f(p)$ is modulated by $L(1,\chi_p)$, equivalently by the class number/regulator of $\mathbb{Q}(\sqrt p)$. To our knowledge this connection is unrecorded — Elsholtz–Tao build $f(p)$ out of exactly the divisor sums whose averages McKee's theorem evaluates, but the count-theoretic literature uses only their order of magnitude, never extracting the constant where (as §8 shows) $L(1,\chi_p)$ lives. (We attribute the singular-series constant to McKee, not to Elsholtz–Tao, who do not invoke it.) The paper's secondary contributions, each a rung on the ladder to the law and each separately machine-checked, are:

1. the largest per-prime solution-count dataset we are aware of, four-engine cross-validated and validated against the published external dataset with zero discrepancies (§3);
2. a lognormal law for $f(p)$, confirmed by four blind predictions of window minima before the computations were run (§3.3);
3. the kernel bijection and the square obstruction, re-proved in full and **formalized in Lean 4 + Mathlib, complete with no unproved steps** ($20$ theorems; §4, Appendix A), together with a no-finite-channel-system theorem (Theorem F) and an $\varepsilon$-covering cost law;
4. the explicit reduction of the second moment of $f_{\mathrm{II}}$ to a two-shift Titchmarsh divisor sum, measured $98.5\%$ off-diagonal, and the one rigorous distributional law in the circle, an Erdős–Kac theorem for the channel count $\omega_3(4p+1)$ (§6);
5. a heuristic but data-matched derivation of the growth exponent $f(p)\sim(\log p)^3$ from the arithmetic geometry of the Cayley cubic (§7).

We are scrupulous about epistemic status. The $L$-function law is a **verified, structurally-identified empirical law**, not a theorem; §9 maps in full why a proof meets the same two-shift parity wall as every other route, and which single inequality would change that.


### 1.4 Method and standards of evidence


The project's working rule is: **no claim without a machine check, no engine without independent validation, no model without a blind test.** Four solution-counting engines were written independently in C, Rust, CUDA, and C/OpenMP; their outputs are byte-identical at five scales and reproduce the external dataset of the 2025 verification preprint on thousands of overlapping primes. Every numbered lemma in the structural sections is checked in exact arithmetic (`analysis/verify_lemmas.py`, $8{,}719$ assertions; `analysis/verify_signed.py`, $536{,}988$ assertions), and the elementary theory is additionally formalized in Lean. Statistical models were frozen on small scales and tested on uncomputed ranges. The single empirical claim on which the headline rests — the correlation $\operatorname{corr}(\ln f,\ln L(1,\chi_p))=-0.62$ — was re-executed for this paper and is reported with its raw output in §8.2 and §10.


### 1.5 Plan of the paper


The argument is a single descent from the data to the law, and the reader may follow it as one thread. §3 establishes the empirical ground — the cross-validated solution counts and the lognormal law, confirmed by blind prediction. §4 supplies the structural reduction, the divisor-class kernel and the square obstruction (both formalized in Lean), and with it the exact reason the elementary toolbox stops. §5 is the pivot: stripped of its obvious trends, the residual count still carries a consistent quadratic-residue signal at every modulus. §6 and §7 then gather the law's two remaining ingredients and fix its limits — the **second moment**, which exposes the count as a two-shift divisor correlation and so locates the analytic wall (with one rigorous Erdős–Kac anchor), and the **growth exponent** $3$, derived independently from the arithmetic geometry of the Cayley cubic. §8 assembles these into the $L$-function law, through a Fourier decomposition over Dirichlet characters and the McKee–Zhou singular series. §9 maps in full why the law stops short of a theorem; §10 records the three-layer source verification; §11 concludes. The main thread is $\S3\to\S4\to\S5\to\S8$; §6 and §7 run parallel to it and may be read after §8 without loss of continuity.


---

## 2. Notation and preliminaries


For a prime $p\ge5$:

- $f(p)$ — number of solutions of $4/p=1/x+1/y+1/z$ with $x\le y\le z$, $x,y,z\in\mathbb{Z}_{>0}$ (OEIS A192787).
- **Type I / Type II.** Every solution has least denominator $x\in(p/4,3p/4]$. With $a=4x-p$ and $B=px$, solutions are in bijection with divisors $d\mid B^2$, $d\equiv -B\pmod a$ (Lemma A, §4.1). Exactly two strata occur at primes: **Type I** ($p\nmid d$: $d\mid x^2$, $d\equiv -4x^2\pmod a$) and **Type II** ($d=pd'$: $d'\mid x^2$, $d'\equiv -x\pmod a$). We write $f=3f_I+3f_{II}$ for the essentially-distinct counts of each stratum (the factor $3$ is the placement symmetry of the $p$-divisible denominators).
- $\chi_p=(\tfrac{\cdot}{p})$ — the Legendre/Jacobi quadratic character; for $p\equiv1\pmod4$ it is the real character of conductor $p$ attached to $\mathbb{Q}(\sqrt p)$.
- $L(1,\chi_p)=\displaystyle\sum_{n\ge1}\frac{\chi_p(n)}{n}=\prod_{\ell}\Big(1-\frac{\chi_p(\ell)}{\ell}\Big)^{-1}=\frac{2\,h(p)\,\log\varepsilon_p}{\sqrt p}$ — the Dirichlet $L$-value, with $h(p)$ the class number and $\varepsilon_p$ the fundamental unit of $\mathbb{Q}(\sqrt p)$ (Dirichlet class-number formula).
- $\omega_3(n)=\#\{\ell\equiv3\ (4)\ \text{prime}:\ell\mid n\}$ — the **channel count**.


---

## 3. The empirical landscape

### 3.1 Data and validation


We computed $f(p)$, with its Type I/II split, for all $278{,}570$ primes of the six hard classes $\bmod\,840$ from $73$ to $2.01\times10^{9}$ — beyond the largest previously published per-prime dataset ($3.5\times10^{7}$). Validation was exhaustive and is summarized below; no mismatch was found anywhere.

| Check | Result |
|---|---|
| Rust vs C vs CUDA vs OpenMP engines, $5$ scales | byte-identical |
| $1$-thread vs $16$-thread; segmented vs single | byte-identical |
| Our engine vs the external published dataset (independent code/authors) | $4{,}519$ primes, $0$ mismatches (incl. Type I/II) |
| Independent Python solution-enumerator vs both | exact on all targets |


### 3.2 Zero-free, with a rising floor


Across all $278{,}570$ primes, $f,f_I,f_{II}>0$: the conjecture holds throughout, and **both mechanisms are always available.** The per-window minimum (the "floor") grows as

$$ \min f \sim (\ln p)^{3.27\pm0.2},\qquad \mathrm{median}\,f\sim(\ln p)^{3.30}, $$

i.e. the floor and the median grow at the **same** exponent, itself consistent with the Elsholtz–Tao average order $\log^3 p$. The all-time record low is $f(2521)=9$ ($2521\equiv1\bmod840$); no prime in the four following orders of magnitude approaches it. Meanwhile the relative dispersion $\sigma(\ln f)$ shrinks monotonically, $0.30\to0.144$ over five decades — the landscape *tightens* as it rises.


### 3.3 The lognormal law and four blind confirmations


Per dyadic window, $\ln f$ is normal to high precision, so window minima are pure order statistics of a lognormal with a rising mean and a shrinking variance. Fitting $\mu(\ln f)$ and $\sigma$ on small scales, freezing them, and predicting the minima of then-uncomputed ranges gives a clean falsification protocol. Four predictions, each stated before its computation:

| Range | Predicted | Observed |
|---|---|---|
| $[10^{8},2\times10^{8}]$ | $\min f\in[175,225]$ | $191$ |
| $[10^{9},1.01\times10^{9}]$ | $\approx 345$ | $347$ |
| $[2\times10^{9},2.01\times10^{9}]$ | median $681$; $\min\in[351,404]$ | median $681$ exact; $\min 405$ |
| $[10^{10},10^{10}+10^{7}]$ | $\min\in[439,499]$; median $\approx852$ | targeted $\min=534$ (safe side); $f(10000001041)=980$, $f(10000003129)=945$ |

The $10^{10}$ row required two new $128$-bit engines to break the $2\times10^9$ counting wall; the measured floor $534$ sits $\approx7\%$ **above** the predicted band — the model under-predicts, i.e. the conjecture is even safer than the law says — and is consistent with the $\sim\!10\%$ accuracy of the lognormal extreme-value model on held-out minima. The lognormal is the central empirical fact; everything that follows explains its mechanism.


---

## 4. The kernel and the square obstruction (machine-verified)


The mechanism the lognormal demands begins not with analysis but with structure. Before any analytic input, $f(p)$ is an *exact* divisor count in prescribed residue classes — this is what makes it computable, and what will, in §§5–8, make it an $L$-value — while at the six square classes that count provably collapses in its coprime strata. Both facts are theorems, re-proved here in full and formalized in Lean 4 + Mathlib; they fix the floor of the landscape and the reason the elementary toolbox cannot raise it.


### 4.1 The divisor-class kernel (Lemma A)


> **Lemma A (kernel bijection).** For prime $p\ge5$ and $x\in(p/4,3p/4]$, put $a=4x-p$, $B=px$ (so $\gcd(a,B)=1$). Solutions of $4/p=1/x+1/y+1/z$ with least denominator $x$ are in bijection with divisors $d\mid B^2$, $d\le B$, $d\equiv-B\pmod a$, via $y=(B+d)/a$, $z=(B+B^2/d)/a$.

The bijection is now machine-verified in Lean 4 + Mathlib **in both directions**, with no unproved steps. Forward (`esc_kernel`): from $a+p=4x$, $B=px$, $de=B^2$ and $ay=B+d$, $az=B+e$, the identity $4/p=1/x+1/y+1/z$ follows from the two clean steps $1/y+1/z=a/B$ and $1/x+a/B=4/p$. Converse (`esc_kernel_converse`): every solution yields $d=ay-B$, $e=az-B$ with $de=B^2$, because the equation *is* $a\cdot yz=B(y+z)$, whence $(ay-B)(az-B)=a^2yz-aB(y+z)+B^2=B^2$. Forward and converse live in the **same** $(x,d,a,B)$ coordinates as the obstruction below, so kernel and obstruction reason about one object.


### 4.2 Channels, identities, and their death at squares


A **channel** is a congruence rule producing a Type I or Type II solution for a whole residue class. Mordell's identities are precisely the class-wide channels; the Type II channel of "index $m$" exists for $p$ iff the shifted integer $4pm+1$ has a divisor $\equiv3\pmod4$ with the side-condition $m\mid y_1z_1$. The square classes are special because a prime $p\equiv\square\pmod{840}$ is a quadratic residue mod $3,5,7$, so **every channel whose congruence conditions live on the primes of $840$ is dead**; channels on new primes fire for only $\sim1/q$ of the class. This is Schinzel's theorem read channel-by-channel, and it is visible in data: floor primes' Type I spectra begin at $e=116$ (for $2521$) versus $e=5$ for every covered-class prime.


### 4.3 The square obstruction (Lemma D), proved in full and in Lean


> **Lemma D.** Let $n=c^2$ ($c$ odd), $x\in(n/4,3n/4]$ with $\gcd(4x-n,nx)=1$, $a=4x-n\equiv3\pmod4$. Then no divisor of $x^2$ lies in the Type I class $d\equiv-4x^2\pmod a$, and no divisor $d'\le x$ of $x^2$ lies in the Type II class $d'\equiv-x\pmod a$: **the coprime strata are empty at odd squares.**

The proof rests on two Jacobi-symbol facts that pull in opposite directions:

1. **Required sign $-1$.** For each $\ell\mid a$, $\ell\nmid2x$, so $\big(\tfrac{d}{\ell}\big)=\big(\tfrac{-4x^2}{\ell}\big)=\big(\tfrac{-1}{\ell}\big)$; multiplying over $\ell\mid a$ and using $a\equiv3\pmod4$ gives $\big(\tfrac{d}{a}\big)=\big(\tfrac{-1}{a}\big)=-1$. (Type II: $c^2\equiv4x\ (\ell)$ makes $x$ a residue, so $\big(\tfrac{-x}{a}\big)=-1$ likewise.)
2. **Actual sign $+1$.** Any $d\mid x^2$ is $d=\delta^2 d_0$ with $d_0\mid x$ squarefree, so $\big(\tfrac{d}{a}\big)=\big(\tfrac{d_0}{a}\big)$; reciprocity with $a\equiv3\pmod4$ and $a\equiv-c^2\pmod{d_0}$ gives $\big(\tfrac{d_0}{a}\big)=+1$.

The contradiction empties the coprime strata. This is the coprime case of Yamamoto's theorem — the case in which the engine and all covering arguments live.

**Lean formalization.** The file `erdos1/subsetsums/Subsetsums/ErdosStraus.lean` machine-verifies, with no unproved steps (every theorem depending only on Lean's standard axioms `propext, Classical.choice, Quot.sound`), $20$ theorems spanning all three movements:

- *Sufficient conditions:* `esc_of_factorization`, `esc_of_K1` (Obláth's criterion: $4p+1$ has a divisor $\equiv3\bmod4$), and the master `esc_of_typeII` ($\,(4y-1)(4z-1)=4p\delta+1$, $\delta\mid yz$).
- *The obstruction, all divisors and both strata:* `typeI_target_jacobi` and `typeII_target_jacobi` (the target classes force Jacobi symbol $-1$); `div_jacobi_one` (every $d\mid x^2$ coprime to $a$, **odd or even**, has Jacobi symbol $+1$); hence `typeI_obstruction` and `typeII_obstruction` derive `False`. The prime cores `four_sq_add_one_div_one_mod_four` and `eight_sq_add_one_div_one_or_three_mod_eight` discharge the K1/K2 channels by strong induction.
- *Chirality and positivity:* `typeI_neg_div_jacobi` (the obstruction is one-sided — a *negative* divisor is sign-compatible, so only the positive windows are emptied) and Theorem G (`esc_two_term_pos`, `esc_two_term_signed`): two unit fractions already give $4/p$, positive for $p\equiv3\ (4)$ and signed for $p\equiv1\ (4)$.

The development also records that the obstruction is **not** a disproof: $4/9=1/3+1/12+1/36$ holds at the square $n=9$ even though its pure coprime strata are empty — solutions persist in mixed strata, exactly as Erdős–Straus requires.


### 4.4 No finite channel system (Theorem F) and the $\varepsilon$-covering cost


> **Theorem F.** If a channel valid on $n\equiv r\pmod m$ (with finitely many coprimality conditions, $n>n_0$) produces a coprime-stratum solution, then $r$ is **not** a unit square $\bmod\,m$. Consequently any finite channel system with $M=\operatorname{lcm}$ of its moduli leaves every prime $p\equiv1\pmod M$ uncovered — a set of relative density $1/\varphi(M)>0$.

*Proof.* If $r\equiv u^2\pmod m$, CRT produces odd $c\equiv u$ with $n=c^2$ in the channel's class, where Lemma D forbids a coprime-stratum solution. The six square classes $\bmod\,840$ are the $M=840$ cross-section. $\quad\blacksquare$

A complementary $\varepsilon$-covering theorem (Theorem E) shows that explicit channel families can cover all but a density-$\varepsilon$ set of primes, but at cost $T\approx\exp(\varepsilon^{-2})$ identities (the uncovered density falls only as $(\log T)^{-1/2}$, by Mertens). **The square classes can never be closed by identities, covering congruences, or the circle method** — a structural reason, not a failure of ingenuity, for eighty years of plateau. What a proof needs instead is a *pointwise lower bound for divisors of shifted integers in prescribed residue classes, uniform in $p$* — available today only on average and on density-1 sets.


---

## 5. The residual spectrum: a quadratic-character fingerprint


This is the pivot from "the elementary toolbox fails" to "an $L$-function governs the count." After removing the window trend and the $\bmod\,840$ class means from $z=\ln f$, the residual is not noise: the residue $p\bmod q$ still predicts $z$ at **every** prime modulus $q\le199$ coprime to $840$, and always with the same sign. Define the quadratic-residue contrast

$$ s_q=\operatorname{mean}\,z(p\ \text{non-residue}\ \bmod q)-\operatorname{mean}\,z(p\ \text{residue}\ \bmod q). $$

Then $s_q>0$ at $19$ of $21$ moduli $q\le97$ (the two flat ones have the smallest predicted effects), with a measured decay law

$$ s_q\ \approx\ 18.2\,q^{-1.95}. $$

"Non-residues richer at every modulus" is exactly the statement that $f(p)$ carries the multiplicative signal of the Legendre symbol $\big(\tfrac{p}{q}\big)$ at every prime $q$, with a *consistent sign* — being a residue $\bmod\,q$ prunes channels (Theorem F seen from below). An additive model over these contrasts saturates out-of-sample at $\approx58\%$ of the residual variance, the remaining $\approx42\%$ being carried by the prime factorizations of the shifted integers $4pm+1$ themselves. The $q^{-2}$-summable ladder over a consistent quadratic signal is the empirical silhouette of an Euler product $\prod_q\big(1-c\left(\tfrac{p}{q}\right)/q\big)$ with a scalar $c>0$; §8 confirms it *is* one.


---

## 6. The second moment and the analytic core


§5 located the signal; turning it into an $L$-value (§8) needs two further inputs, supplied by this section and the next. Here we take the analytic route, through the **second moment** of $f$. It pays twice. It exposes the precise arithmetic object the count is built from — a correlation of two shifted divisor sums — and, in the same breath, locates the wall that stops a proof. The section then closes on firmer ground, with the one fully rigorous distributional law within reach: an Erdős–Kac theorem that anchors the §3 lognormal in the second moment and identifies the floor primes exactly.


### 6.1 The two-shift Titchmarsh reduction (exact)


A Type II solution corresponds bijectively to $(y',z',\delta)$ with

$$ (4y'-1)(4z'-1)=4p\delta+1,\qquad \delta\mid y'z',\qquad p=\frac{(4y'-1)(4z'-1)-1}{4\delta}, $$

so $f_{II}(p)$ counts divisors $\equiv3\pmod4$ of the shifted integers $\{4p\delta+1\}_\delta$ with the divisibility side-condition (machine-verified on every Type II solution of $499$ primes). Writing $r_\delta(p)$ for the count at fixed $\delta$, unfolding the square gives the exact identity

$$ \sum_{p\le N} f_{II}(p)^2 = \sum_{\delta_1,\delta_2}\ \sum_{\substack{p\le N\\ p\ \mathrm{prime}}} r_{\delta_1}(p)\,r_{\delta_2}(p), $$

a correlation of two divisor-type functions of the linear forms $4\delta_1 p+1$, $4\delta_2 p+1$ over primes — a **two-shift Titchmarsh divisor problem**. This is the explicit form of Elsholtz–Tao's Remark 1.3, apparently written down here for the first time.


### 6.2 The wall hardens with scale


Measured on exact $\delta$-decompositions, the sum is **$98.5\%$ off-diagonal** ($\delta_1\ne\delta_2$), and the off-diagonal share *rises* with $p$: $0.9554\,(10^4)\to0.9754\,(10^5)\to0.9836\,(10^6)$, because distinct Type II solutions occupy near-unique shifts ($\delta$-multiplicity $\approx1.08$, constant). With $f_{II}\asymp(\log p)^3$ the diagonal fraction falls like $C/(\log p)^3\to0$: the second moment is *asymptotically pure two-shift Titchmarsh*. The required level of distribution — conductor $\sim p^2$, two simultaneous shifts, over primes — sits past Bombieri–Vinogradov ($p^{1/2}$), past the ternary-divisor records (Sharma $p^{1/2+1/30}$ for a single modulus; Aydemir–Boran $p^{8/11}$ averaged), and past the GRH-conditional Titchmarsh power-savings (Drappeau; Assing–Blomer–Li). A pointwise version is additionally **parity-blocked** — the classical Selberg/$\sqrt x$ parity barrier, which any unconditional handling of the divisor function over primes must break via a Type-II/bilinear input (the line of Granville–Shao, *beyond the $x^{1/2}$-barrier for multiplicative functions in APs*, arXiv:1703.06865). This is the analytic mirror of Theorem F.


### 6.3 The rigorous anchor: an Erdős–Kac channel law


The one rigorous distributional statement available is a theorem, not a heuristic. Since $\sum_{\ell\equiv3(4)}1/\ell\sim\tfrac12\ln\ln x$ and the prime factors of $4p+1$ equidistribute $\bmod\,4$ (Bombieri–Vinogradov), the Kubilius–Shapiro / Halberstam (1956) central limit theorem for additive functions of shifted primes gives:

$$ \omega_3(4p+1)\ \text{is asymptotically Normal with mean}\ \sim\ \mathrm{Var}\ \sim\ \tfrac12\ln\ln p. $$

Measured: mean $1.056$, $\mathrm{Var}\,1.072$ (the Erdős–Kac signature), skew $\to0$. The K1 channel fires iff $\omega_3(4p+1)\ge1$, so **K1-starvation $\iff\omega_3(4p+1)=0$** — a Landau–Ramanujan event of density $\sim C/\sqrt{\ln p}$ (measured $0.473$), and all four documented floor primes ($2521,4201,9601,20521$) have $\omega_3(4p+1)=0$. The floor is the **left-tail large deviation of an Erdős–Kac variable**. Crucially this also settles the distributional shape: $\mathrm{Var}/\mathrm{mean}$ grows $3.5\to13.8$ (so $f$ is over-dispersed, *not* Poisson), while $\mathrm{Var}/\mathrm{mean}^2\approx e^{\sigma^2}-1$ holds to $\approx5\%$ in the largest windows — $f$ is **lognormal**, confirming §3.3 in the second moment. Why it does not prove ESC: an Erdős–Kac law gives a left tail that is *thin* (density $\to0$) but provably *non-empty*, and "thin but non-empty" is exactly the density-1$\to$all-primes gap.


---

## 7. The growth exponent from the Cayley cubic (heuristic)


We return to the wall in §9; the law's one remaining ingredient is its exponent. The $3$ in $f(p)\sim(\log p)^3$ — so far an empirical fact (§3) matching the Elsholtz–Tao average order — has an independent arithmetic-geometry derivation. The Erdős–Straus surface $4xyz=n(xy+yz+zx)$ has open part $V_n\cong\mathbb{G}_m^2$ (Bright–Loughran, 2020: geometric unit group of rank $2$), with a boundary triangle of lines at infinity. Applying the Browning–Wilsch (2025) Batyrev–Manin–Peyre heuristic for integral points on log-K3 cubic surfaces,

$$ N^{\circ}_U(B)\ \sim\ c\,(\log B)^{\varrho_U+b}, $$

with $\varrho_U=\operatorname{rank}\operatorname{Pic}(U)$ and $b$ the maximal number of boundary components meeting at a real point, and calibrating against the authors' own Markoff computation (triangle boundary, exponent $2$ = Zagier's law), the Cayley cubic's rank-$2$ unit group gives $\varrho_U+b=3$. (Browning–Wilsch treat the Markoff and sum-of-three-cubes surfaces; the calibration to the Cayley/Erdős–Straus cubic is ours, not a result of theirs.) With height $B\asymp p$,

$$ f(p)=N^{\circ}_{U_p}(B)\ \sim\ c\,(\log p)^3, $$

matching the Elsholtz–Tao average and, on the repo's own data, $k=3.03$ for $\ln(\mathrm{median}\,f)=k\ln\ln p+b$ over six decades. Two honest hedges: $b$ is model-dependent (pinning it rigorously means a Tamagawa/Clemens computation on the weak-dP3 model neither paper has done), and the framework is provably **blind to the square classes** — a direct count gives the cubic exactly $\ell^2+1$ points $\bmod\,\ell$ independent of $n$'s quadratic-residue status. The geometry fixes the exponent and the typical size; it sees nothing of existence. The square-class suppression is the finer character/parity effect that §8 identifies.


---

## 8. The $L$-function law


Every piece is now in hand: the quadratic-residue ladder of §5, the second moment built from divisor sums of quadratics (§6), and the exponent $3$ (§7). This section assembles them into the law of the abstract. The ladder sharpens into a single Fourier coefficient (§8.1); that coefficient's Euler product is, by definition, $L(1,\chi_p)$ (§8.2); and McKee–Zhou supplies the rigorous precedent that divisor sums of quadratics are governed by exactly this $L$-value (§8.3). The destination promised at the end of §5 is reached here.


### 8.1 The character decomposition


The local divisor density of $f(p)$ at a prime $\ell\nmid840$ — measurable because the hard primes equidistribute $\bmod\,\ell$ — was Fourier-decomposed over the Dirichlet characters $\bmod\,\ell$. At **every** $\ell\in\{11,13,17,19,23\}$ the dominant non-trivial character is the **quadratic (Legendre) character $(p/\ell)$**, with a *negative* coefficient of order $1/\ell$ (its size is the scale-dependent exponent $c$ of §8.2), at $14$–$47\sigma$ ($166{,}000$ primes; `analysis/lfunction_connection.py`, `class_local_density.py`, `sigma7_char_fit.py`). The mechanism (made precise in §8.4): $f(p)$ counts divisors of the shifted integers $4p\delta+1$ in residue classes, and these counts track how $\ell$ splits in $\mathbb{Q}(\sqrt p)$, i.e. $\chi_p(\ell)=(p/\ell)$ — though §8.4 shows the signal is **not** a single-$\ell$ local density (those are character-free) but a shadow of the cross-prime correlation. The §5 ladder $s_q\approx18\,q^{-1.95}$ is exactly the first-order ($O(1/\ell)$) shadow of this signal.


### 8.2 The law


The product of these quadratic characters is, by definition, the Euler product of the quadratic $L$-function:

$$ f(p)\ \approx\ (\log p)^3\cdot\prod_{\ell}\Big(1-\frac{c\,\chi_p(\ell)}{\ell}\Big)\ \approx\ (\log p)^3\cdot L(1,\chi_p)^{-c},\qquad c>0. $$

Here $\chi_p(\ell)=(\tfrac{p}{\ell})$ is the Legendre symbol of §2 and $c>0$ is a single scalar exponent — **not** a function of $\ell$ (its *fitted value* drifts with scale; Table 1). The two displayed forms agree to first order in $1/\ell$: the Euler product gives $\prod_\ell\big(1-\chi_p(\ell)/\ell\big)=L(1,\chi_p)^{-1}$ exactly, and $(1-x)^c=1-cx+O(x^2)$, whence $\prod_\ell\big(1-c\,\chi_p(\ell)/\ell\big)=L(1,\chi_p)^{-c}\,(1+O(1))$ — the convergent $O(1/\ell^2)$ remainder is absorbed into the amplitude. This is an **empirical law** ($f(p)$ carrying the character signal with mean order $(\log p)^3$), not a claimed identity; the $(\log p)^3$ is the Elsholtz–Tao average order (and §7's Cayley-cubic count), independent of the $L$-modulation it multiplies. By Dirichlet's class-number formula $L(1,\chi_p)=2h(p)\log\varepsilon_p/\sqrt p$, this says **$f(p)$ is modulated by the class number / regulator of $\mathbb{Q}(\sqrt p)$: larger $L(1,\chi_p)\Rightarrow$ fewer Erdős–Straus solutions.** A direct test against an independent truncated $\ln L(1,\chi_p)=-\sum_{\ell\le X}\log\big(1-(p/\ell)/\ell\big)$ — built with no reference to the $f$-data — gives, on $14{,}955$ hard primes near $10^9$ (re-executed for this paper; output of `analysis/lfunction_connection.py`, where `#Euler factors` is the number of primes $\ell\le X$ in the truncated product, **not** the sample size):

```
  n = 14,955 hard primes near 1e9   (p in [1.000, 1.010]e9, ln p ~ 20.73,
       so the (log p)^3 trend is ~constant across the slice)

  truncation X   #Euler factors (l<=X)   corr(ln f, ln L)   95% CI (Fisher z)
         50              11             -0.5977          [-0.6079, -0.5873]
        200              42             -0.6173          [-0.6271, -0.6073]
        500              91             -0.6200          [-0.6298, -0.6100]
       1500             235             -0.6199          [-0.6296, -0.6099]

  partial corr(ln f, ln L | ln p) = -0.6199   ((log p)^3 trend removed)
  regression slope d(ln f)/d(ln L) = -0.527   (an estimate of -c)
```

The correlation is $-0.62$ ($95\%$ CI $\approx\pm0.01$ at $n=14{,}955$), stable across truncation and — because the slice spans only $\ln p\in[20.723,20.733]$ — **unchanged when the $(\log p)^3$ trend is partialled out** (partial $r=-0.62$): it is the $L$-value, not the size of $p$, that $f$ tracks. But this $-0.62$ is the value **at $10^9$**, and the exponent it implies is not universal. Measured in narrow windows from $10^6$ to $10^{10}$ (Table 1 below; the $10^{11}$ row awaits a multi-day GPU run still in progress), the correlation itself is nearly scale-stable — it stays within a $\pm0.03$ band of $-0.62$, with a shallow (but statistically resolved) maximum near $p\sim10^7$–$10^8$ and only a gentle weakening beyond it ($-0.620$ at $10^9$, $-0.596$ at $10^{10}$). What moves with scale is the *dynamic range* of $f$: $\sigma(\ln f)$ shrinks monotonically (from $0.21$ down to $0.14$) as the count distribution tightens, while $\sigma(\ln L)$ climbs from $\approx0.13$ and saturates near $0.175$ by $10^8$. The implied $c=|\mathrm{corr}|\cdot\sigma(\ln f)/\sigma(\ln L)$ therefore **declines monotonically** across the whole range — from $0.93$ at $10^6$ to $0.46$ at $10^{10}$ — driven by the narrowing spread of $f$, not by any collapse of the $L$-coupling (whose correlation barely moves). Only the **sign** is scale-robust — negative at every scale tested; the magnitude is a finite-size quantity, and whether $c$ tends to a positive limit or to $0$ as $p\to\infty$ we cannot yet decide, though the monotone descent over four decades is, if anything, weak evidence for the latter. The six hard square classes $\bmod\,840$ are a *finer* shadow of the same object: at $\ell=5,7$ the prime $p$ is forced to be a residue, so the leading quadratic character is constant and the class-splitting is carried by the higher residue characters — a cubic character at $7$ plus a $\sim17^\circ$ **chiral phase** ($\sigma_7(c)=a_0+2\operatorname{Re}(b\,\psi(c))$, $b=8.4\,e^{163^\circ i}$), the local shadow of the signed-sector see-saw and impossible for any single Dirichlet character.

**Table 1. The $L$-correlation and the implied exponent across scale.** Narrow windows (so $\log p$ is held fixed within each), computed cleanly from scratch with a single validated engine (`fp128` mode 2; driver `analysis/run_scale_study.sh`, table by `analysis/scale_table.py`). Here $f=f_{\mathrm I}+f_{\mathrm{II}}$ and $\ln L$ is the truncated quadratic $L$-value at $X=1500$ ($235$ Euler factors); the $10^9$ row reproduces the headline $-0.620$. The correlation is nearly scale-stable (shallow maximum near $10^7$–$10^8$), $\sigma(\ln f)$ shrinks monotonically and $\sigma(\ln L)$ saturates near $0.175$ by $10^8$, so the implied $c=|\mathrm{corr}|\,\sigma(\ln f)/\sigma(\ln L)$ **declines monotonically** with scale. The sign is negative at every scale; the $95\%$ CI on each correlation is $\approx\pm0.01$ at $n\approx14{,}000$ and $\approx\pm0.03$ at $n\approx2{,}000$.

| scale $p$ | $n$ | $\sigma(\ln f)$ | $\sigma(\ln L)$ | $\mathrm{corr}(\ln f,\ln L)$ | implied $c$ |
|---|---|---|---|---|---|
| $10^{6}$  | $1{,}927$  | $0.208$ | $0.132$ | $-0.588$ | $0.925$ |
| $10^{7}$  | $2{,}161$  | $0.185$ | $0.161$ | $-0.646$ | $0.741$ |
| $10^{8}$  | $2{,}001$  | $0.166$ | $0.170$ | $-0.640$ | $0.625$ |
| $10^{9}$  | $14{,}955$ | $0.148$ | $0.174$ | $-0.620$ | $0.527$ |
| $10^{10}$ | $13{,}564$ | $0.135$ | $0.175$ | $-0.596$ | $0.458$ |
| $10^{11}$ | — | — | — | — | — |

*(Rows $10^6$–$10^{10}$ are the completed fresh recomputation; the $10^{11}$ row awaits a multi-day GPU run still in progress and is filled on completion.)*


### 8.3 The mechanism: McKee–Zhou and the Gauss–Siegel precedent


The rigorous engine behind the law is classical. For an irreducible quadratic $F$, the divisor sum $\sum_{n\le N}\tau(F(n))$ has singular series

$$ \mathfrak{S}(F)=\frac{2\,L(1,\chi_{\mathrm{disc}\,F})}{\zeta(2)} $$

(McKee, *Math. Proc. Camb. Phil. Soc.* **126** (1999); explicit constant in Zhou, arXiv:1611.10186; cf. Lapkova). This is the divisor-count analogue of the Gauss–Siegel fact that ternary representation counts are governed by quadratic $L$-values ($r_3(n)\propto H(n)\propto L(1,\chi_{-n})$). Elsholtz–Tao construct $f(p)$ from precisely such divisor sums $\tau(kab^2+1)$ but use McKee only as an $O$-bound, never extracting the constant — which is exactly where $L(1,\chi_p)$ lives. Because an $L(1,\chi_p)^{-c}$ factor has mean $\approx$ const, the law leaves the Elsholtz–Tao first moment (of order $N\log^2N$) untouched while explaining the **prime-by-prime variance** a first-moment bound is blind to.


### 8.4 Why the signal is not local


A natural attempt at a proof would extract the $-c$ exponent one prime at a time, as the quadratic-character content of an $\ell$-local solution density. This cannot work: **the signal is invisible to every single-prime local density.** Two exact facts, each a finite check (verified at $\ell=11,13$, $k\le2$; `analysis/local_sign.py`, `local_signal_origin.py`), where $a:=p\bmod\ell^k$.

**Proposition (local triviality).** Over $\mathbb{Z}/\ell^k$, for every $\ell\nmid p$:
*(i)* the bare surface $4xyz=p\,(xy+yz+zx)$ has solution count $|V_a|$ **independent of** $a$ among units, so its Legendre projection $\sum_a|V_a|\,(a/\ell)$ vanishes identically; and
*(ii)* the Type II count $N_\ell(a)=\#\{(y',z'):v_\ell(4y'z'-y'-z')\le v_\ell(y')+v_\ell(z')\}$ is likewise independent of $a$.

*Proof.* (i) The dilation $(x,y,z)\mapsto(\lambda x,\lambda y,\lambda z)$, $\lambda\in(\mathbb{Z}/\ell^k)^\times$, multiplies the cubic term by $\lambda^3$ and the quadratic by $\lambda^2$, so it carries $V_a$ bijectively onto $V_{\lambda a}$; the units act transitively, hence $|V_a|$ is constant. (ii) The §6.1 relation $p\delta=4y'z'-y'-z'$ fixes $\delta\equiv(4y'z'-y'-z')\,a^{-1}$, so $v_\ell(\delta)=v_\ell(4y'z'-y'-z')$ is $a$-free and the side-condition $\delta\mid y'z'$ reads $v_\ell(\delta)\le v_\ell(y'z')$, also $a$-free. $\square$

The mod-$4$ divisorship $d=4y'-1\equiv3$ is built into the integrality of $y'$, not an odd-$\ell$ degree of freedom, so it does not break the dilation. This matches §8.3 exactly: McKee's $L(1,\chi_p)$ surfaces only *after* the sum over $n$ (here over $\delta$), never as a product of single Euler factors.

So where does the measured signal sit? In the conditional mean $\mathbb{E}[\ln f\mid p\equiv a]$ — present in **both** $f_I$ and $f_{II}$ — and the lognormal identity ties it to the second moment:
$$ \mathbb{E}[\ln f\mid a]=\ln\mathbb{E}[f\mid a]-\tfrac12\operatorname{Var}(\ln f\mid a), $$
verified to four decimals on the $10^9$ slice (Legendre projections at $\ell=11$: $-0.05421$ on the left vs.\ $-0.05423$ on the right). Its dominant part is the projection of $\ln\mathbb{E}[f\mid a]$ itself ($-0.0532$) — and since every local density is flat, that can only be generated by the side-condition $\delta\mid y'z'$ acting on **all primes at once** (the factorization of $\delta$ must divide $y'z'$ at each $\ell$ simultaneously). That global coupling is precisely the two-shift correlation of §6.1. The negativity of $c$ is therefore not a missing local computation but a property of the correlation, hence parity-bound (§9.2): **the wall is structural, not a gap in effort.**


### 8.5 What the $L$-lens buys


Three consequences are immediate and structurally important, granting the law:

1. **The exceptional set is theorem-controlled.** Thin $f\iff$ large $L(1,\chi_p)$. By Granville–Soundararajan, $\#\{p\le N:L(1,\chi_p)\ge e^{\gamma}\tau\}$ falls **super-exponentially** in $\tau$. Any Erdős–Straus exception must lie in the **extreme class-number tail** — a provably super-rare, density-controlled set. (Compare the unconditional "almost all" of Vaughan, 1970.)
2. **Siegel zeros are the best case, not the worst.** A Siegel zero $\beta\to1$ forces $L(1,\chi_p)$ *small*, hence $f(p)$ *large*. The conjecture's adversary is the opposite extreme — maximal $L$, of order $e^{\gamma}\log\log p$ — and even there the budget gives $f\gg(\log p)^3/(\log\log p)^c\to\infty$. **ESC is robust to the classic Landau–Siegel nightmare.**
3. **The size budget never threatens $f>0$.** The best unconditional ceiling $L(1,\chi_p)\le(0.197+o(1))\log p$ (Stephens) gives, granting the law, $f\gg(\log p)^{3-c}\to\infty$ (the measured $c<1$ makes the exponent exceed $2$; and were $c\to0$ with scale, the bound would only strengthen toward $(\log p)^3$). The entire difficulty is upgrading $\asymp$ to a proven inequality — never the magnitudes.


---

## 9. Honest status: a verified law, short of a theorem


The payoffs of §8.5 are real but conditional on the law. This section discharges that condition as far as it will go, and marks precisely where it will not: a derivation of the singular series blocks at the $\delta$-split (§9.1), the asymptotic and the matching lower bound are parity-obstructed (§9.2), and only a low-payoff upper bound survives parity-safe (§9.3). The wall met here is the same one §6.2 measured, now read from the side of a proof.


### 9.1 Where a derivation blocks (McKee–Zhou and the $\delta$-split)


$L(1,\chi_p)$ here is the **singular series itself**, not an external special value: bounding it controls the *main term*, which it already predicts. The unproven content is the *error term* — that the two-shift divisor sum is asymptotic to its singular series with a power saving, at conductor $\sim p^2$, over primes. Attempting to *derive* the singular series via McKee–Zhou meets a verified obstruction. McKee–Zhou needs the count to be $\sum\tau(F(n))$ for a **single** irreducible quadratic $F$; but the Type II count carries the side-condition $\delta\mid y'z'$, and $\delta$ splits *arbitrarily* across $y'$ and $z'$ in real solutions — at $p=2521$ the solution with $\delta=98=2\cdot7^2$ has $\gcd(\delta,y')=\gcd(\delta,z')=14$, dividing neither factor alone. A direct reduction to one quadratic divisor sum therefore **undercounts** (the clean conic form returns $f_{II}(2521)=1$ versus the true $3$). The split is exactly what makes $f_{II}$ a **two-shift divisor correlation**, not a single $\sum\tau(F)$: the $L$-value does not factor out through one class-number formula. The effective exponent $c$ (scale-dependent — §8.2 — and negative-signed, i.e. Yamamoto suppression) is the *aggregate* character content of that correlation.


### 9.2 The parity wall, and why upper bounds are the only safe target


By Cauchy–Schwarz, $\#\{p\le N:f(p)>0\}\ge(\sum_p f)^2/\sum_p f^2$. The numerator is the Elsholtz–Tao first moment (order $N\log^2 N$); the denominator is the §6 second moment, of expected order $N\log^5 N$. A one-sided **upper** bound $\sum_p f^2\ll N(\log N)^5$ is the rare parity-*safe* target — Selberg's barrier blocks asymptotics and lower bounds, not majorants — and is winnable in principle by divisor-correlation technology (Nair–Tenenbaum; Henriot) applied to $d(4\delta p+1)$, with a Brun–Titchmarsh majorant on the single prime constraint. We verified (§18.7 of the report) that the resulting $\delta$-split correlation upper bound is genuinely parity-safe and structurally winnable. But its only payoff is Cauchy–Schwarz — a **positive proportion** $1/C$ with $C=\mathbb{E}[f^2]/\mathbb{E}[f]^2$ — which is *weaker* than the **density 1** already given unconditionally by Vaughan (1970). And it delivers only the *order* of the second moment, not the leading constant, so it does not even establish the $L(1,\chi_p)$ law rigorously.


### 9.3 The complete map


The valuable statements — the asymptotic second moment, the exact $L(1,\chi_p)^{-c}$ singular series, the $L$-controlled exceptional set — all require the matching **lower** bound $f\gg(\log p)^3 L^{-C}$, which is the two-shift Titchmarsh asymptotic, which is parity-blocked. So the honest map is:

| Target | Parity | Winnable? | Payoff |
|---|---|---|---|
| Upper bound $\sum_p f^2\ll N\log^5N$ | safe | yes (research-level) | positive proportion ($\le$ Vaughan), order only |
| Asymptotic second moment | blocked | no | density 1, the $L$-constant |
| Lower bound $f\gg(\log p)^3L^{-C}$ | blocked | no | the $L$-law as a theorem; with $L\le\tfrac12\log p$, ESC for the class |
| Pointwise / nonempty-left-tail | blocked | no | the conjecture |

One parity-safe but low-payoff target, and a fence of parity-blocked high-value ones beyond it. **The session's genuine advance is the $L(1,\chi_p)$ lens itself** — it proves the magnitudes are never the obstacle, confines any counterexample to a super-rare $L$-extreme set, and isolates the single needed inequality cleanly — *not* a new bound.


---

## 10. Provenance and source verification


Because the paper's value depends on building correctly on prior work, every cited source was verified at **three layers**: (i) first-party confirmation that each arXiv identifier resolves to a real paper with the stated authors, title, and date (we fetched the abstract pages directly — every identifier below was confirmed); (ii) first-party theorem-level confirmation that the specific result we lean on is genuinely the paper's (we checked the load-bearing claims against primary sources and explicit statements); (iii) an independent four-agent web audit (arXiv API, ar5iv full text, journal DOIs) run in parallel. That audit has **completed and agrees**: **every cited source resolves to a real, on-topic paper, correctly attributed — no fabricated or hallucinated citation exists** (including all five post-2025 identifiers). The central empirical claim was additionally **re-executed** (the raw table in §8.2). The corrections below — all already folded into the text above — are matters of exact title, volume, dating, and author-name order, plus two claim-precision fixes (the Elsholtz–Tao first moment, and crediting the McKee constant to McKee rather than to Elsholtz–Tao). **None touches the substance of the $L$-function law or the wall.**

**Corrections folded in (from the verification pass):**

- **arXiv:2509.00128** is *Further verification and empirical evidence for the Erdős–Straus conjecture* by **Spiridon Mihnea and Dumitru C. Bogdan** (29 Aug 2025), verifying to $\mathbf{10^{18}}$ and tabulating $f(p)$ — resolving a three-way author/ceiling confusion ($10^{17}$ was Salez's separate result).
- **Granville–Shao** (arXiv:1703.06865) is **2017** (rev. 2019), *not* 2023; its explicit content is multiplicative functions in APs *beyond the $x^{1/2}$-barrier* (level $x^{20/39}$). The "parity" point we attach to it is the **classical $\sqrt x$/Selberg parity barrier** that this line of work engages, stated as such, not a verbatim "every-modulus equidistribution is false" theorem.
- Exact titles (the report sometimes paraphrased): Zhou 1611.10186 = *The explicit asymptotic formula of divisor function on average over values of quadratic polynomial*; Sharma 2303.06087 = *Bilinear sums with $GL(2)$ coefficients and the exponent of distribution of $d_3$* ($1/2+1/30$ confirmed); Drappeau 1504.05549 = *Sums of Kloosterman sums in arithmetic progressions, and the error term in the dispersion method*; Aydemir–Boran 2601.12601 = *Improved Averaged Distribution of $d_3(n)$ in Prime Arithmetic Progressions* ($8/11$ confirmed); Topacoğullari 1512.05770 = *On a certain additive divisor problem* (Acta Arith. 181, 2017).
- **McKee** (1999, MPCPS **126**, 17–22): his $\lambda=12H^*(\Delta)\log\varepsilon_\Delta/(\pi^2\sqrt\Delta)$ for $\Delta>0$ equals $2L(1,\chi_\Delta)/\zeta(2)$ by the class-number formula — the mechanism of §8.3 is exact. Explicit version: **Lapkova**, arXiv:1704.02498.
- **Granville–Soundararajan**, *The distribution of values of $L(1,\chi_d)$*, GAFA **13** (2003) 992–1028: the large-value proportion decays **double-exponentially** in $\tau$ — stronger than the "super-exponential" we claim.
- **Stephens** (*Optimizing the size of $L(1,\chi)$*, Proc. LMS (3) **24** (1972) 1–14): $|L(1,\chi)|\le\tfrac12(1-e^{-1/2}+o(1))\log q$, and $\tfrac12(1-e^{-1/2})=0.1967\ldots$ — the constant $0.197$ is exact, prime conductor (extended to all moduli by Pintz; recent explicit $\tfrac12\log q$).
- **Elsholtz–Tao first moment** is the two-sided bound $N\log^2N\ll\sum_{p\le N}f(p)\ll N\log^2N\log\log N$ — **not** a clean $\asymp N\log^2N$; the average order is $\log^3p$ only up to the $\log\log$ factor they note but cannot remove. Corrected wherever stated.
- **The McKee singular-series constant is credited to McKee, not to Elsholtz–Tao.** ET's contribution is the divisor-sum realization of $f(p)$; the constant $2L(1,\chi_{\mathrm{disc}})/\zeta(2)$ is McKee's (via the class-number formula). We no longer phrase ET as "invoking McKee."
- **Halberstam** — the Erdős–Kac CLT for additive functions of *shifted primes* is Part **III**, *J. London Math. Soc.* **31** (1956) 14–27 (Part I is **30** (1955) 43–53). Corrected from "30 (1955)."
- **Bright–Loughran** — "no Brauer–Manin obstruction" holds *for the existence of solutions* (Thm 1.1); their Brauer group is the nontrivial $\mathbb{Z}/2\mathbb{Z}$ (Thm 1.6) and does obstruct *strong approximation* (Thm 1.8). Stated with that qualifier; the existence claim is what makes the difficulty analytic.
- **Browning–Wilsch** treat the Markoff and sum-of-three-cubes surfaces; the calibration to the Cayley/Erdős–Straus cubic giving exponent $3$ is **our** application of their heuristic, presented as such, never as their stated result.

| Source | We use it for | Verification |
|---|---|---|
| Elsholtz–Tao, *J. Aust. Math. Soc.* 94 (2013), arXiv:1107.1010 | $f(p)$; first moment $N\log^2N\ll\Sigma\ll N\log^2N\log\log N$; Type I/II split; Remarks 1.2–1.3; density-1 lower bound (Thm 1.8) | ✔ ID + claim (was $\asymp$ → two-sided) |
| Vaughan, *Mathematika* 17 (1970) | almost-all exceptional set $\ll N\exp(-c(\log N)^{2/3})$ | ✔ standard |
| Mordell, *Diophantine Equations* (1969) | the six square classes $\bmod\,840$; covering identities | ✔ standard |
| Schinzel (2000); Yamamoto | no identity family covers a class with squares; $f_I=f_{II}=0$ on odd squares | ✔ standard (+ Lean re-proof) |
| Salez (2014), arXiv:1406.6307 | seven modular equations; verification to $10^{17}$ | ✔ ID + claim |
| McKee (1999, MPCPS 126); Zhou 1611.10186; Lapkova 1704.02498 | singular series $\sum\tau(\text{quad.})=2L(1,\chi_{\mathrm{disc}})/\zeta(2)$ | ✔ ID + theorem |
| Gauss; Siegel | $r_3(n)\propto H(n)\propto L(1,\chi_{-n})$ (the $L$-value precedent) | ✔ classical |
| Granville–Soundararajan, GAFA 13 (2003) | double-exponential tail of $L(1,\chi)$ values | ✔ ID + theorem |
| Stephens (+ Pintz) | $L(1,\chi_p)\le(0.197+o(1))\log p=\tfrac12(1-e^{-1/2})\log p$ | ✔ constant exact |
| Granville–Shao, arXiv:1703.06865 (2017/19) | level beyond $x^{1/2}$ for multiplicative functions; the $\sqrt x$ parity barrier | ✔ ID; parity = classical barrier |
| Halberstam, *JLMS* **31** (1956) 14–27 (Part III) | Erdős–Kac CLT for additive functions of shifted primes | ✔ (vol/yr corrected) |
| Ford, *Annals* 168 (2008), arXiv:math/0401223 | lognormal divisor-in-interval law | ✔ ID + claim |
| Browning–Wilsch, *Selecta Math.* 31 (2025), arXiv:2407.16315 | $(\log B)^{\varrho_U+b}$ integral-point heuristic; Markoff calibration | ✔ ID; Cayley/exponent-3 is **our** application |
| Bright–Loughran, *Bull. LMS* 52 (2020), arXiv:1908.02526 | $V_n\cong\mathbb{G}_m^2$; no BM obstruction *to existence* (Br $=\mathbb{Z}/2\mathbb{Z}$ obstructs strong approx.) | ✔ ID + claim + qualifier |
| Sharma 2303.06087; Aydemir–Boran 2601.12601; Drappeau 1504.05549; Assing–Blomer–Li 2005.13915; Topacoğullari 1512.05770 | divisor-in-AP / Titchmarsh records that fall short of the two-shift need | ✔ all IDs + levels |
| Mihnea–Bogdan (2025), arXiv:2509.00128 | external $f(p)$ dataset (cross-validated); $10^{18}$ frontier | ✔ ID + authors fixed |
| Ventas 2605.04551; Bello-Hernández–Benito–Fernández 2606.10922; Mballa 2602.20036 | CF reformulation; divisor parametrization; density-one parametrization (all heuristic, hit parity) | ✔ all IDs + content |
| Pomerance–Weingartner (2025), arXiv:2511.16817 | exceptions to the Erdős–Straus–Schinzel conjecture | ✔ ID + claim |

The faithful-use principle applied throughout: where a cited result is used **rigorously** (McKee–Zhou's singular series, Halberstam's CLT, Bright–Loughran's geometry, Vaughan's exceptional set, Granville–Soundararajan's and Stephens' $L$-value bounds, the Lean-internal lemmas), it is invoked as a theorem; where it is used **heuristically or by extrapolation** (Browning–Wilsch's exponent, the lognormal extreme-value model, the $L^{-c}$ correlation as a law), it is labeled as such and never upgraded. No source is cited for a stronger statement than it proves.


---

## 11. Conclusion


The Erdős–Straus solution count $f(p)$ is governed, to the accuracy we can measure and reproduce, by the quadratic $L$-value $L(1,\chi_p)$ — the class number and regulator of $\mathbb{Q}(\sqrt p)$. We reached this not by guessing but by a documented descent: the lognormal law and its blind confirmations established that $f$ has a clean distribution; the machine-verified kernel and square obstruction established that $f$ is a divisor count in residue classes and pinned why elementary methods stop; the residual spectrum exposed a consistent quadratic-residue ladder at every modulus; and the character decomposition turned that ladder into an Euler product, hence into $L(1,\chi_p)^{-c}$, with the McKee–Zhou singular series as the rigorous precedent.

The law is verified and structurally identified, but it is not a theorem, and we have mapped exactly why: the underlying object is a two-shift Titchmarsh divisor correlation whose asymptotic and lower-bound content is parity-obstructed, leaving only a low-payoff upper bound as parity-safe. What the law nonetheless settles, conditionally on itself and consistent with everything unconditional, is the *shape* of the problem: the magnitudes never threaten $f>0$, Siegel zeros help rather than hurt, and any counterexample is confined to the extreme class-number tail — a super-rare, density-controlled set. That is a sharper picture of where an Erdős–Straus exception could possibly hide than the conjecture has had, and it points the next rigorous effort at a single, cleanly isolated inequality.


---

## Appendix A. The Lean 4 + Mathlib development


`erdos1/subsetsums/Subsetsums/ErdosStraus.lean` formalizes the elementary theory completely, with no unproved steps; `#print axioms` reports only Lean's standard `propext, Classical.choice, Quot.sound` for every theorem. The $20$ theorems, by role:

- **Kernel:** `esc_kernel`, `esc_kernel_converse` (Lemma A, both directions).
- **Sufficient conditions:** `esc_of_factorization`, `esc_of_K1` (Obláth), `esc_of_typeII` (master Type II), `comp_mod_four` (helper).
- **Obstruction (prime cores):** `prime_factor_four_sq_add_one`, `four_sq_add_one_div_one_mod_four`; `prime_factor_eight_sq_add_one`, `eight_sq_add_one_div_one_or_three_mod_eight`.
- **Obstruction (general Lemma D):** `typeI_target_jacobi`, `typeII_target_jacobi` (target classes force $-1$); `typeI_div_jacobi_one`, `div_jacobi_one` (every divisor of $x^2$ gives $+1$, no parity restriction); `typeI_obstruction`, `typeII_obstruction` (the contradictions).
- **Chirality and positivity:** `typeI_neg_div_jacobi` (one-sidedness); `esc_two_term_pos`, `esc_two_term_signed` (Theorem G).

Non-vacuity is witnessed by worked examples ($4/2$ via K1; the obstruction biting at $n=9$; $4/9=1/3+1/12+1/36$ persisting in mixed strata). Build/verify: `cd erdos1/subsetsums && lake exe cache get && lake build`. Numeric cross-checks: `analysis/verify_lemmas.py` ($8{,}719$ assertions).


## Appendix B. Reproducing the headline

```bash
# the L(1,χ_p) correlation of §8.2 (needs sympy; reads data/hard_1e9_slice.csv)
python3 analysis/lfunction_connection.py
#   → corr(ln f, ln L) = -0.60 … -0.62 across X = 50 … 1500; slope -0.527 (at p~1e9;
#     the implied exponent c is scale-dependent — see the §8.2 scale table)

# the character decomposition (dominant quadratic (p/ℓ) at ℓ = 11..23, 14–47 σ)
python3 analysis/class_local_density.py
python3 analysis/sigma7_char_fit.py

# the second-moment reduction and Erdős–Kac channel law (§6)
python3 analysis/second_moment.py
python3 analysis/offdiag_scaling.py
```


## References

1. P. Erdős, E. G. Straus (1948). The original problem; see T. Bloom, *Erdős Problems* #242, <https://www.erdosproblems.com/242>.
2. C. Elsholtz, T. Tao. *Counting the number of solutions to the Erdős–Straus equation on unit fractions.* J. Aust. Math. Soc. **94** (2013) 50–105. arXiv:1107.1010.
3. R. C. Vaughan (1970). On a problem of Erdős, Straus and Schinzel. *Mathematika* 17.
4. L. J. Mordell. *Diophantine Equations.* Academic Press (1969), 287–290.
5. A. Schinzel. *On sums of three unit fractions with polynomial denominators.* Funct. Approx. Comment. Math. **28** (2000) 187–194.
6. S. E. Salez. *The Erdős–Straus conjecture: new modular equations and checking up to $N=10^{17}$* (2014). arXiv:1406.6307.
7. J. McKee. *The average number of divisors of an irreducible quadratic polynomial.* Math. Proc. Camb. Phil. Soc. **126** (1999) 17–22. Explicit constant: N. Zhou, *The explicit asymptotic formula of divisor function on average over values of quadratic polynomial*, arXiv:1611.10186; K. Lapkova, *Explicit upper bound for the average number of divisors of irreducible quadratic polynomials*, arXiv:1704.02498.
8. A. Granville, K. Soundararajan. *The distribution of values of $L(1,\chi_d)$.* Geom. Funct. Anal. **13** (2003) 992–1028 (the large-value proportion decays double-exponentially in $\tau$).
9. P. J. Stephens. *Optimizing the size of $L(1,\chi)$.* Proc. London Math. Soc. (1972): $|L(1,\chi)|\le\tfrac12(1-e^{-1/2}+o(1))\log q$, constant $0.1967\ldots$ (extended to all moduli by J. Pintz).
10. A. Granville, X. Shao. *Bombieri–Vinogradov for multiplicative functions, and beyond the $x^{1/2}$-barrier.* arXiv:1703.06865 (2017, rev. 2019). The relevant parity limitation is the classical Selberg/$\sqrt x$ barrier.
11. H. Halberstam. *On the distribution of additive number-theoretic functions III.* J. London Math. Soc. **31** (1956) 14–27. (The Erdős–Kac CLT for additive functions of shifted primes; Part I is **30** (1955) 43–53.)
12. K. Ford. *The distribution of integers with a divisor in a given interval.* Ann. of Math. **168** (2008) 367–433. arXiv:math/0401223.
13. T. Browning, F. Wilsch. *Integral points on cubic surfaces: heuristics and numerics.* Selecta Math. **31** (2025); arXiv:2407.16315 (2024).
14. M. Bright, D. Loughran. *Brauer–Manin obstruction for Erdős–Straus surfaces* (2019/2020). arXiv:1908.02526.
15. P. Sharma, *Bilinear sums with $GL(2)$ coefficients and the exponent of distribution of $d_3$* (2023/24), arXiv:2303.06087 (level $\tfrac12+\tfrac1{30}$); M. C. Aydemir, M. Boran, *Improved Averaged Distribution of $d_3(n)$ in Prime Arithmetic Progressions* (2026), arXiv:2601.12601 (level $8/11$); S. Drappeau, *Sums of Kloosterman sums in arithmetic progressions, and the error term in the dispersion method* (2015/16), arXiv:1504.05549; E. Assing, V. Blomer, J. Li, *Uniform Titchmarsh divisor problems* (2020), arXiv:2005.13915; B. Topacoğullari, *On a certain additive divisor problem*, Acta Arith. **181** (2017), arXiv:1512.05770.
16. S. Mihnea, D. C. Bogdan. *Further verification and empirical evidence for the Erdős–Straus conjecture* (2025) — external $f(p)$ dataset cross-validated here; verification to $10^{18}$. arXiv:2509.00128.
17. A. Ventas, *A Ceiling Continued Fraction Approach to the Erdős–Straus Conjecture* (2026), arXiv:2605.04551; M. Bello-Hernández, M. Benito, E. Fernández, *A Divisor Parametrization for the Erdős–Straus Conjecture* (2026), arXiv:2606.10922; P. U. Mballa, *A unified parametric approach … natural density one* (2026), arXiv:2602.20036; C. Pomerance, A. Weingartner, *Exceptions to the Erdős–Straus–Schinzel conjecture* (2025), arXiv:2511.16817.

*Full derivations, tables, and machine checks: [`REPORT.md`](REPORT.md) §§2–18; figures in [`plots/`](plots/).*

</div>

