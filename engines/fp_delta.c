/* fp_delta.c — the δ-resolved second moment of f_II(p): diagonal vs off-diagonal.
 *
 * REPORT §19 ("how far does the diagonal N log⁵N bound go?").  §14 reduced the Type II
 * second moment to a two-shift sum
 *
 *     Σ_{p≤N} f_II(p)²  =  Σ_{δ₁,δ₂} Σ_{p≤N} r_{δ₁}(p) r_{δ₂}(p),
 *
 * r_δ(p) = #Type II solutions of 4/p with that δ (≈ #divisors u≡3 mod4 of 4pδ+1).  Its
 * DIAGONAL (δ₁=δ₂) is  D(N) = Σ_{p≤N} Σ_δ r_δ(p)², the part a single-shift / Shiu majorant
 * reaches.  §14 measured the off-diagonal *fraction* → 0.988; this engine measures the
 * *exponents* per dyadic window, to settle whether the diagonal reaches N log⁵N (it does not —
 * it tracks the first moment N log²N; the whole log³ excess is off-diagonal).
 *
 * Per prime p (hard class p ≡ 1 mod 24, matching data/hard_1e7_full.csv) it computes, by the
 * Lemma A kernel (mirrors engines/fp_single.c, machine-validated):
 *     f_I(p), f_II(p),  and the δ-multiset {δ} of the Type II solutions,
 * whence  diag_p = Σ_δ r_δ², and accumulates per dyadic window of p:
 *     n, Σf_I, Σf_II, Σf_II², Σdiag, Σf, Σf²   (f = f_I+f_II).
 *
 * Kernel recap: for x in (p/4, 3p/4], a = 4x−p; enumerate d | x²;
 *   Type I  : d ≡ −4x² (mod a), d ≥ dmin              (p ∤ the divisor)
 *   Type II : d ≤ x, d ≡ −x (mod a), p·d ≥ dmin       (then δ = (4y'z'−y'−z')/p,
 *             y' = (x+d)/a, z' = (x²/d+x)/a)
 *
 * Build: gcc -O3 -march=native -fopenmp engines/fp_delta.c -o engines/fp_delta -lm
 * Run:   ./engines/fp_delta <pmin> <pmax> [out.csv]     # table to stdout (+ csv)
 *        ./engines/fp_delta --check                      # self-validate f(p) vs known
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <omp.h>

typedef unsigned long long u64;
typedef unsigned __int128 u128;

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

static int is_prime_u64(u64 n){ if(n<2)return 0; for(u64 i=2;i*i<=n;i++) if(n%i==0) return 0; return 1; }

static int cmp_u64(const void *A, const void *B){ u64 a=*(const u64*)A,b=*(const u64*)B; return (a>b)-(a<b); }

/* full f_I, f_II and the δ-multiset (δ's pushed into dl[], up to dlcap) for ONE prime p.
 * returns f_II; *pfI set; *pndl = #Type II δ's written (== f_II if it fit). */
static u64 fp_one_delta(u64 p, u64 *pfI, u64 *dl, int dlcap, int *pndl) {
    u64 xlo = p/4 + 1, xhi = 3*p/4;
    u64 fI = 0, fII = 0; int ndl = 0;
    for (u64 x = xlo; x <= xhi; x++) {
        u64 a = 4*x - p; if (a == 0) continue;
        u64 xm = x % a;
        u64 r0 = (a - (u64)(((u128)((4*xm)%a) * xm) % a)) % a;   /* −4x² mod a */
        u64 r1 = (a - xm) % a;                                   /* −x   mod a */
        u128 dmin = (2*x > p) ? (u128)(2*x) * (2*x - p) : 0;
        /* factor x */
        u64 q[64]; int e[64], nf = 0; u64 t = x;
        for (int b = 0; b < NBP; b++) { u64 pr = BP[b]; if (pr*pr > t) break;
            if (t % pr == 0) { int ee = 0; while (t % pr == 0) { t /= pr; ee++; } q[nf]=pr; e[nf]=ee; nf++; } }
        if (t > 1) { q[nf] = t; e[nf] = 1; nf++; }
        /* enumerate d | x² by odometer */
        int f[64]; for (int i = 0; i < nf; i++) f[i] = 0;
        u128 d = 1;
        for (;;) {
            u64 m = (u64)(d % a);
            if (m == r0 && d >= dmin) fI++;
            if (d <= (u128)x && m == r1 && (u128)p * d >= dmin) {
                fII++;
                /* δ = (4 y' z' − y' − z')/p ;  y'=(x+d)/a, z'=(x²/d+x)/a  (both integral here) */
                u64 dd = (u64)d;
                u128 yp = ((u128)x + dd) / a;
                u128 zp = ((u128)x * x / dd + x) / a;
                u128 D = 4*yp*zp - yp - zp;            /* divisible by p */
                u64 delta = (u64)(D / p);
                if (ndl < dlcap) dl[ndl++] = delta;
            }
            int i = 0;
            while (i < nf) { if (f[i] < 2*e[i]) { f[i]++; d *= q[i]; break; } f[i]=0; for(int r=0;r<2*e[i];r++) d/=q[i]; i++; }
            if (i == nf) break;
        }
    }
    *pfI = fI; *pndl = ndl;
    return fII;
}

/* diag = Σ_δ r_δ²  from the (possibly unsorted) δ-list of length n */
static u64 diag_from_deltas(u64 *dl, int n) {
    if (n == 0) return 0;
    qsort(dl, n, sizeof(u64), cmp_u64);
    u64 diag = 0; int run = 1;
    for (int i = 1; i <= n; i++) {
        if (i < n && dl[i] == dl[i-1]) run++;
        else { diag += (u64)run*run; run = 1; }
    }
    return diag;
}

#define WMAX 48
int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr,"usage: %s <pmin> <pmax> [out.csv] | --check\n", argv[0]); return 1; }

    if (!strcmp(argv[1], "--check")) {
        struct { u64 p; u64 f; } K[] = {{5,2},{7,7},{73,7},{1009,19},{2521,9}};
        int ok = 1;
        for (int i = 0; i < 5; i++) {
            free(BP); build_base((u64)sqrt((double)(3*K[i].p/4))+2);
            u64 dl[4096]; int ndl; u64 fI;
            u64 fII = fp_one_delta(K[i].p, &fI, dl, 4096, &ndl);
            u64 diag = diag_from_deltas(dl, ndl);
            int pass = (fI+fII == K[i].f) && ((int)fII == ndl);
            printf("  p=%llu f=%llu+%llu=%llu (exp %llu)  fII=%llu ndl=%d diag=%llu  %s\n",
                   K[i].p, fI, fII, fI+fII, K[i].f, fII, ndl, diag, pass?"OK":"FAIL");
            ok &= pass;
        }
        printf("%s\n", ok?"self-check PASSED":"self-check FAILED");
        return ok?0:2;
    }

    u64 pmin = strtoull(argv[1],NULL,10), pmax = strtoull(argv[2],NULL,10);
    const char *outpath = (argc>3)? argv[3] : NULL;
    build_base((u64)sqrt((double)(3.0*pmax/4.0))+2);

    /* gather hard primes p ≡ 1 mod 24 in [pmin,pmax] (matches hard_1e7_full.csv) */
    u64 plo = pmin<5?5:pmin;
    long cap = (long)(pmax/ (log((double)pmax)) ) + 1024;  /* generous */
    u64 *primes = malloc(sizeof(u64)*cap); long np = 0;
    for (u64 n = plo + ((25 - plo%24)%24); n <= pmax; n += 24)   /* n ≡ 1 mod 24 */
        if (is_prime_u64(n)) { if (np>=cap){cap*=2; primes=realloc(primes,sizeof(u64)*cap);} primes[np++]=n; }

    /* per-window accumulators (k = floor(log2 p)) */
    double Wn[WMAX]={0}, WsfI[WMAX]={0}, WsfII[WMAX]={0}, WsfII2[WMAX]={0},
           Wdiag[WMAX]={0}, Wsf[WMAX]={0}, Wsf2[WMAX]={0};

    #pragma omp parallel
    {
        double Ln[WMAX]={0}, LsfI[WMAX]={0}, LsfII[WMAX]={0}, LsfII2[WMAX]={0},
               Ldiag[WMAX]={0}, Lsf[WMAX]={0}, Lsf2[WMAX]={0};
        u64 *dl = malloc(sizeof(u64)*(1<<16));
        #pragma omp for schedule(dynamic, 64)
        for (long idx = 0; idx < np; idx++) {
            u64 p = primes[idx];
            u64 fI; int ndl;
            u64 fII = fp_one_delta(p, &fI, dl, 1<<16, &ndl);
            u64 diag = diag_from_deltas(dl, ndl);
            u64 f = fI + fII;
            int k = (int)floor(log2((double)p));
            if (k>=WMAX) k=WMAX-1;
            Ln[k]+=1; LsfI[k]+=fI; LsfII[k]+=fII; LsfII2[k]+=(double)fII*fII;
            Ldiag[k]+=diag; Lsf[k]+=f; Lsf2[k]+=(double)f*f;
        }
        free(dl);
        #pragma omp critical
        for (int k=0;k<WMAX;k++){ Wn[k]+=Ln[k]; WsfI[k]+=LsfI[k]; WsfII[k]+=LsfII[k];
            WsfII2[k]+=LsfII2[k]; Wdiag[k]+=Ldiag[k]; Wsf[k]+=Lsf[k]; Wsf2[k]+=Lsf2[k]; }
    }

    printf("# fp_delta: hard primes p≡1 mod24 in [%llu,%llu], n=%ld\n", pmin, pmax, np);
    printf("# %-5s %8s %12s %14s %14s %10s %8s %8s\n",
           "win","n","sum_fII","sum_fII2","diag(Σrδ²)","offdiag%","SfII2/Sf","off/diag");
    FILE *out = outpath? fopen(outpath,"w"):NULL;
    if (out) fprintf(out,"win,n,sum_fI,sum_fII,sum_fII2,diag,sum_f,sum_f2\n");
    for (int k=0;k<WMAX;k++) {
        if (Wn[k] < 1) continue;
        double off = WsfII2[k]-Wdiag[k];
        double offfrac = WsfII2[k]>0? off/WsfII2[k] : 0;
        double offdiagratio = Wdiag[k]>0? off/Wdiag[k] : 0;
        printf("  2^%-3d %8.0f %12.0f %14.0f %14.0f %9.4f %8.3f %8.2f\n",
               k, Wn[k], WsfII[k], WsfII2[k], Wdiag[k], offfrac,
               WsfII[k]>0? WsfII2[k]/WsfII[k]:0, offdiagratio);
        if (out) fprintf(out,"%d,%.0f,%.0f,%.0f,%.0f,%.0f,%.0f,%.0f\n",
               k, Wn[k], WsfI[k], WsfII[k], WsfII2[k], Wdiag[k], Wsf[k], Wsf2[k]);
    }
    if (out) { fclose(out); fprintf(stderr,"wrote %s\n", outpath); }
    free(primes); free(BP);
    return 0;
}
