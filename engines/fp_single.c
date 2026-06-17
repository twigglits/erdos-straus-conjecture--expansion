/* fp_single.c — exact f(p) for INDIVIDUAL primes, 128-bit, past the sweep frontier.
 *
 * The batch engines (fp.c/fp.cu) top out at p ≈ 2×10⁹ (u32 primes/x, u64 x², 20 GB spf
 * table).  Counting the *whole* hard class at 10¹⁰ is a ~2-day GPU job; but counting f(p)
 * for a HANDFUL of chosen primes is cheap per prime and needs no big table.  This does that
 * in __int128 with trial-division factoring (memory-free), so it runs at 10¹⁰, 10¹¹, … —
 * extending §15's "exhibit one solution" to "count ALL solutions" beyond the frontier.
 *
 * Kernel (Lemma A): for x in (p/4, 3p/4], a = 4x−p, B = px, solutions with least
 * denominator x ↔ divisors d | x² (Type I, d ≡ −4x² mod a, d ≥ dmin) and d | x², d ≤ x
 * (Type II, d ≡ −x mod a).  f(p) = Σ_x (Type I + Type II).  Unordered count = fI + fII.
 *
 * Build: gcc -O3 -march=native -fopenmp engines/fp_single.c -o engines/fp_single -lm
 * Run:   ./engines/fp_single <p1> [p2 ...]        # one or more primes
 *        ./engines/fp_single --check              # self-validate vs known f(p)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <omp.h>

typedef unsigned long long u64;
typedef unsigned __int128 u128;

/* base primes up to `limit` (for trial-dividing x ≤ 3p/4, limit = isqrt(3p/4)+1) */
static u64 *BP; static int NBP;
static void build_base(u64 limit) {
    char *c = calloc(limit + 1, 1);
    NBP = 0;
    for (u64 i = 2; i <= limit; i++) if (!c[i]) { NBP++; for (u64 j = i*i; j <= limit; j += i) c[j] = 1; }
    BP = malloc(sizeof(u64) * NBP);
    int k = 0;
    for (u64 i = 2; i <= limit; i++) if (!c[i]) BP[k++] = i;
    free(c);
}

/* count Type I + Type II solutions contributed by a single x (factor x, enumerate d|x²) */
static void count_x(u64 x, u64 p, u64 *fI, u64 *fII, u64 *n3) {
    u64 a = 4*x - p;                       /* a ≤ 2p, fits u64 */
    u64 xm = x % a;
    u64 r0 = (a - (u64)(((u128)((4*xm)%a) * xm) % a)) % a;   /* −4x² mod a */
    u64 r1 = (a - xm) % a;                                   /* −x   mod a */
    u128 dmin = (2*x > p) ? (u128)(2*x) * (2*x - p) : 0;

    /* factor x */
    u64 q[64]; int e[64], nf = 0; u64 t = x;
    for (int b = 0; b < NBP; b++) { u64 pr = BP[b]; if (pr*pr > t) break;
        if (t % pr == 0) { int ee = 0; while (t % pr == 0) { t /= pr; ee++; } q[nf] = pr; e[nf] = ee; nf++; } }
    if (t > 1) { q[nf] = t; e[nf] = 1; nf++; }

    /* enumerate divisors d of x² = Π q^(2e) by odometer; check both strata */
    int f[64]; for (int i = 0; i < nf; i++) f[i] = 0;
    u128 d = 1;
    u64 cI = 0, cII = 0, c3 = 0;
    for (;;) {
        u64 m = (u64)(d % a);
        if (m == r0 && d >= dmin) { cI++; if (dmin > 0 && d == dmin) c3++; }
        if (d <= (u128)x && m == r1 && (u128)p * d >= dmin) {
            cII++;
            if (d == (u128)x) c3++;
            if (dmin > 0 && (u128)p * d == dmin) c3++;
        }
        int i = 0;
        while (i < nf) { if (f[i] < 2*e[i]) { f[i]++; d *= q[i]; break; } f[i] = 0; for (int r=0;r<2*e[i];r++) d /= q[i]; i++; }
        if (i == nf) break;
    }
    *fI = cI; *fII = cII; *n3 = c3;
}

/* exact f(p) for one prime: parallel over x in (p/4, 3p/4] */
static void fp_one(u64 p, u64 *FI, u64 *FII, long long *FORD) {
    u64 xlo = p/4 + 1, xhi = 3*p/4;
    u64 tI = 0, tII = 0, t3 = 0;
    #pragma omp parallel for schedule(dynamic, 1<<16) reduction(+:tI,tII,t3)
    for (u64 x = xlo; x <= xhi; x++) {
        u64 a = 4*x - p; if (a == 0) continue;
        u64 i, ii, n3; count_x(x, p, &i, &ii, &n3);
        tI += i; tII += ii; t3 += n3;
    }
    *FI = tI; *FII = tII; *FORD = 6LL*(long long)(tI+tII) - 3LL*(long long)t3;
}

static int is_prime(u64 n){ if(n<2)return 0; for(u64 i=2;i*i<=n;i++) if(n%i==0) return 0; return 1; }

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: %s <p1> [p2 ...]  |  --check\n", argv[0]); return 1; }

    if (!strcmp(argv[1], "--check")) {
        /* known unordered f(p) = fI+fII (REPORT/local_solubility): f(5)=2,f(7)=7,f(1009)=19,f(2521)=9 */
        struct { u64 p; u64 f; } K[] = {{5,2},{7,7},{1009,19},{2521,9},{73,7}};
        build_base((u64)(sqrt((double)(3*2521/4)))+2);
        int ok = 1;
        for (int i = 0; i < 5; i++) {
            free(BP); build_base((u64)sqrt((double)(3*K[i].p/4))+2);
            u64 fI, fII; long long ford; fp_one(K[i].p, &fI, &fII, &ford);
            int pass = (fI+fII == K[i].f);
            printf("  p=%llu  f=fI+fII=%llu+%llu=%llu  expected %llu  %s\n",
                   K[i].p, fI, fII, fI+fII, K[i].f, pass?"OK":"FAIL");
            ok &= pass;
        }
        printf("%s\n", ok ? "self-check PASSED" : "self-check FAILED");
        return ok ? 0 : 2;
    }

    for (int i = 1; i < argc; i++) {
        u64 p = strtoull(argv[i], NULL, 10);
        if (!is_prime(p)) { printf("p=%llu  NOT PRIME — skipped\n", p); continue; }
        free(BP); build_base((u64)sqrt((double)(3.0*p/4.0))+2);
        double t0 = omp_get_wtime();
        u64 fI, fII; long long ford; fp_one(p, &fI, &fII, &ford);
        printf("p=%llu  (mod840=%llu)  f=%llu  fI=%llu  fII=%llu  ford=%lld  [%.1fs]\n",
               p, p%840, fI+fII, fI, fII, ford, omp_get_wtime()-t0);
        fflush(stdout);
    }
    return 0;
}
