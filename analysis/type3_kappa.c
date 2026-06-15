/* type3_kappa.c — fast (C/OpenMP) computation of the correction constants
 * kappa_j = (sum_x actual_j)/(sum_x equidist_j) for the signed-ESC Type I/II/III
 * grade-1 strata (REPORT §13.2). Pushes the Python type3_kappa.py to large p to
 * test whether kappa_I, kappa_II converge or keep drifting.
 *
 * Per prime p (== 1 mod 24), per positive denominator x in (0, p/2]:
 *   a=4x-p, m=|a|, B=px, dmin=2x(2x-p).  Divisors e | x^2, |d|=p^j e.
 *   range A (p/4<x<=p/2): j=0 window 1<=e<=|dmin|; j=1 window 1<=pe<=|dmin|.
 *   range B (x<p/4):      j=1 window pe>=|dmin|;   j=2 window automatic.
 *   actual_j += [p^j e == B (mod m)] (modular, no overflow); equidist_j += 1/phi(m).
 * All magnitudes fit int64 for p up to ~1e6 (we never form p^2 e).
 *
 * Build: gcc -O2 -fopenmp -o type3_kappa_c type3_kappa.c
 * Run:   ./type3_kappa_c 100000
 * Validates against Python: [73,2000) -> kappa ~ 1.646 / 0.709 / 0.972.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef long long ll;
#define MAXDIV 16384

static int *spf;  /* smallest prime factor, 0..PMAX */

static void sieve(int N) {
    spf = malloc((size_t)(N + 1) * sizeof(int));
    for (int i = 0; i <= N; i++) spf[i] = i;
    for (int i = 2; (ll)i * i <= N; i++)
        if (spf[i] == i)
            for (int k = i * i; k <= N; k += i)
                if (spf[k] == k) spf[k] = i;
}

static ll totient(ll m) {
    if (m == 1) return 1;
    ll ph = 1, mm = m;
    while (mm > 1) {
        int pr = spf[mm];
        ll pk = 1;
        while (mm % pr == 0) { mm /= pr; pk *= pr; }
        ph *= (pk / pr) * (pr - 1);
    }
    return ph;
}

/* divisors of x^2 into divs[], return count */
static int divs_sq(ll x, ll *divs) {
    int nd = 1; divs[0] = 1;
    ll xx = x;
    while (xx > 1) {
        int pr = spf[xx], cnt = 0;
        while (xx % pr == 0) { xx /= pr; cnt++; }
        int e2 = 2 * cnt, cur = nd;
        ll pk = 1;
        for (int k = 1; k <= e2; k++) {
            pk *= pr;
            for (int t = 0; t < cur; t++) {
                if (nd >= MAXDIV) { fprintf(stderr, "MAXDIV overflow x=%lld\n", x); exit(1); }
                divs[nd++] = divs[t] * pk;
            }
        }
    }
    return nd;
}

static void work(ll p, unsigned long long act[3], double eqd[3]) {
    act[0] = act[1] = act[2] = 0; eqd[0] = eqd[1] = eqd[2] = 0;
    ll divs[MAXDIV];
    for (ll x = 1; x <= p / 2; x++) {
        ll a = 4 * x - p, m = a < 0 ? -a : a;
        if (m == 0) continue;
        int rangeA = (4 * x > p) && (4 * x <= 2 * p);
        int rangeB = (4 * x < p);
        if (!rangeA && !rangeB) continue;
        ll B = p * x, dmin = 2 * x * (2 * x - p);
        ll absd = dmin < 0 ? -dmin : dmin;
        ll Bmod = B % m, pmod = p % m, p2 = (pmod * pmod) % m;
        double invphi = 1.0 / (double) totient(m);
        int nd = divs_sq(x, divs);
        for (int i = 0; i < nd; i++) {
            ll e = divs[i], em = e % m;
            if (rangeA) {
                if (e <= absd) { eqd[0] += invphi; if (em == Bmod) act[0]++; }
                if (p * e <= absd) { eqd[1] += invphi; if ((pmod * em) % m == Bmod) act[1]++; }
            } else { /* rangeB */
                if (p * e >= absd) { eqd[1] += invphi; if ((pmod * em) % m == Bmod) act[1]++; }
                eqd[2] += invphi; if ((p2 * em) % m == Bmod) act[2]++;
            }
        }
    }
}

int main(int argc, char **argv) {
    int PMAX = argc > 1 ? atoi(argv[1]) : 100000;
    sieve(PMAX);

    int cap = 0;
    for (int p = 73; p < PMAX; p++) if (p % 24 == 1 && spf[p] == p) cap++;
    ll *primes = malloc(cap * sizeof(ll));
    int np = 0;
    for (int p = 73; p < PMAX; p++) if (p % 24 == 1 && spf[p] == p) primes[np++] = p;

    unsigned long long (*A)[3] = malloc(np * sizeof(*A));
    double (*E)[3] = malloc(np * sizeof(*E));

    #pragma omp parallel for schedule(dynamic, 4)
    for (int i = 0; i < np; i++) work(primes[i], A[i], E[i]);

    int ckpts[] = {3000, 10000, 25000, 50000, 100000, 200000, 400000, 1000000};
    int nck = sizeof(ckpts) / sizeof(ckpts[0]);
    printf("%9s %8s  %8s %8s %8s  %8s   %s\n",
           "P", "nprimes", "kI", "kII", "kIII", "III/f1", "actual I/II/III");
    for (int c = 0; c < nck; c++) {
        if (ckpts[c] > PMAX) break;
        unsigned long long cA[3] = {0, 0, 0};
        double cE[3] = {0, 0, 0};
        int cnt = 0;
        for (int i = 0; i < np; i++) {
            if (primes[i] >= ckpts[c]) break;      /* primes in [73, ckpt) */
            for (int j = 0; j < 3; j++) { cA[j] += A[i][j]; cE[j] += E[i][j]; }
            cnt++;
        }
        double kI = cA[0] / cE[0], kII = cA[1] / cE[1], kIII = cA[2] / cE[2];
        double rat = (double) cA[2] / (cA[0] + cA[1] + cA[2]);
        printf("%9d %8d  %8.4f %8.4f %8.4f  %8.4f   %llu/%llu/%llu\n",
               ckpts[c], cnt, kI, kII, kIII, rat, cA[0], cA[1], cA[2]);
    }
    return 0;
}
