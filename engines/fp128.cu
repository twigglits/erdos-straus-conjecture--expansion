// fp128.cu — 128-bit, memory-light f(p) counter; the batch engine past p ≈ 2×10⁹.
//
// fp.cu caps at p ≈ 2×10⁹: u32 primes (wrap 4.29×10⁹), u32 x, u64 x² (overflows ~10¹⁰),
// and a full spf table to (p+1)/2 (20 GB) + a comp sieve to p (10 GB).  fp128 lifts all of
// it: u64 primes/x, unsigned __int128 divisors / dmin / p·d, x factored by trial division
// over base primes ≤ √x (no spf table), and the target primes enumerated by a SEGMENTED
// sieve (no O(p) bitmap) — the rolling-window idea from the sister repo prime-octal.
// Same kernel/algorithm and CSV as fp.cu, so byte-identical in the overlap range.
//
// Build (native Blackwell):  nvcc -O3 -arch=sm_120 fp128.cu -o fp128         (CUDA ≥ 12.8)
//   or portable:             nvcc -O3 -arch=compute_80 fp128.cu -o fp128
// Run: ./fp128 <pmin> <pmax> <mode 0=all|1=p%24==1> <out.csv>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <vector>
#include <algorithm>
#include <chrono>
#include <cuda_runtime.h>

typedef unsigned long long u64;
typedef unsigned int u32;
typedef unsigned __int128 u128;

#define CUDA_CHECK(call) do { cudaError_t e__=(call); if(e__!=cudaSuccess){ \
    fprintf(stderr,"CUDA %s at %s:%d: %s\n",#call,__FILE__,__LINE__,cudaGetErrorString(e__)); \
    exit(1);} } while(0)

#define KMAX 11
#define DX_CAP (1u << 18)
#define SMEM_CAP 6144            // divisors in shared memory (×16 B = 96 KB)
#define TPB 256
#define FATCAP 262144

// Barrett reduction d mod a for d < 2^64 (M = ⌊2^64 / a⌋); fast path of the scan.
__device__ __forceinline__ u64 bar_mod(u64 d, u64 a, u64 M)
{
    u64 r = d - __umul64hi(d, M) * a;
    while (r >= a) r -= a;
    return r;
}

// ---------------- per-(x,p) divisor-class test (u128 divisors) ----------------
__device__ __forceinline__ void scan_divs(const u128* __restrict__ divs, u32 nd,
                                          u64 x, u64 p, u64& c0, u64& c1, u64& n3)
{
    u64 a  = 4 * x - p;
    u64 M  = ~0ULL / a;                           // Barrett constant
    u64 xm = x % a;
    u64 v  = (u64)(((u128)((4 * xm) % a) * xm) % a);
    u64 r0 = (a - v == a) ? 0 : a - v;            // (−4x²) mod a
    u64 r1 = (a - xm == a) ? 0 : a - xm;          // (−x)   mod a
    u128 dmin = (2 * x > p) ? (u128)(2 * x) * (2 * x - p) : 0;
    for (u32 i = 0; i < nd; i++) {
        u128 d = divs[i];
        // most divisors fit u64 (x² < 2^64 for x < 4.2×10⁹); u128 % only for the rest
        u64 m = (d >> 64) ? (u64)(d % a) : bar_mod((u64)d, a, M);
        if (m == r0 && d >= dmin) {
            c0++;
            if (dmin > 0 && d == dmin) n3++;
        }
        if (d <= (u128)x && m == r1 && (u128)p * d >= dmin) {
            c1++;
            if (d == (u128)x) n3++;
            if (dmin > 0 && (u128)p * d == dmin) n3++;
        }
    }
}

// ---------------- factor x by trial division over base primes (no spf table) -----------
__global__ void factor_chunk(const u32* __restrict__ bp, u32 nbp, u64 X0, u32 len,
                             u32* __restrict__ kfac, u32* __restrict__ ndfac,
                             u64* __restrict__ qfac, u128* __restrict__ qpfac)
{
    u32 j = blockIdx.x * blockDim.x + threadIdx.x;
    if (j >= len) return;
    u64 tt = X0 + j;
    u32 k = 0, nd = 1;
    for (u32 b = 0; b < nbp; b++) {
        u64 q = bp[b];
        if (q * q > tt) break;
        if (tt % q == 0) {
            u32 e = 0;
            while (tt % q == 0) { tt /= q; e++; }
            u128 pw = 1;
            for (u32 i = 0; i < 2 * e; i++) pw *= q;
            qfac[j * KMAX + k] = q; qpfac[j * KMAX + k] = pw;
            nd *= (2 * e + 1); k++;
        }
    }
    if (tt > 1) {                                  // remaining prime factor (≤ x, may be > u32)
        qfac[j * KMAX + k] = tt; qpfac[j * KMAX + k] = (u128)tt * tt;
        nd *= 3; k++;
    }
    kfac[j] = k; ndfac[j] = nd;
}

// window helper: prime indices with p ∈ [2x−1, 4x) (same range as fp.cu)
__device__ __forceinline__ void prime_window(const u64* primes, int np, u64 x,
                                             int& lo_out, int& hi_out)
{
    u64 plo = 2 * x - 1, phi = 4 * x;
    int lo = 0, hi = np;
    while (lo < hi) { int m=(lo+hi)>>1; if (primes[m] < plo) lo=m+1; else hi=m; }
    lo_out = lo;
    int lo2 = lo; hi = np;
    while (lo2 < hi) { int m=(lo2+hi)>>1; if (primes[m] < phi) lo2=m+1; else hi=m; }
    hi_out = lo2;
}

// build the divisor list (odometer) from the factorisation of x
__device__ __forceinline__ void build_divs(u128* divs, u32 k, const u64* q, const u128* qp)
{
    u32 f[KMAX];
    for (u32 i = 0; i < k; i++) f[i] = 0;
    // recover exponents from qp = q^{2e}: 2e = log_q(qp)
    u32 twoE[KMAX];
    for (u32 i = 0; i < k; i++) { u128 t = qp[i]; u32 c = 0; while (t > 1) { t /= q[i]; c++; } twoE[i] = c; }
    u128 d = 1;
    for (u32 c = 0;; c++) {
        divs[c] = d;
        u32 i = 0;
        while (i < k) {
            if (f[i] < twoE[i]) { f[i]++; d *= q[i]; break; }
            f[i] = 0; d /= qp[i]; i++;
        }
        if (i == k) break;
    }
}

__global__ void fp_kernel(const u64* __restrict__ primes, int np, u64 X0,
                          const u32* __restrict__ kfac, const u32* __restrict__ ndfac,
                          const u64* __restrict__ qfac, const u128* __restrict__ qpfac,
                          u64* __restrict__ c0a, u64* __restrict__ c1a, u64* __restrict__ n3a)
{
    extern __shared__ u128 s_divs[];
    __shared__ int s_lo, s_hi;
    u32 j = blockIdx.x;
    u64 x = X0 + j;
    u32 nd = ndfac[j];
    if (nd > SMEM_CAP) return;
    if (threadIdx.x == 0) {
        prime_window(primes, np, x, s_lo, s_hi);
        if (s_lo < s_hi) {
            u32 k = kfac[j]; u64 q[KMAX]; u128 qp[KMAX];
            for (u32 i=0;i<k;i++){ q[i]=qfac[j*KMAX+i]; qp[i]=qpfac[j*KMAX+i]; }
            build_divs(s_divs, k, q, qp);
        }
    }
    __syncthreads();
    int lo = s_lo, hi = s_hi;
    if (lo >= hi) return;
    for (int ip = lo + threadIdx.x; ip < hi; ip += TPB) {
        u64 p = primes[ip];
        u64 c0=0,c1=0,n3=0;
        scan_divs(s_divs, nd, x, p, c0, c1, n3);
        if (c0|c1) {
            atomicAdd((unsigned long long*)&c0a[ip],(unsigned long long)c0);
            if (c1) atomicAdd((unsigned long long*)&c1a[ip],(unsigned long long)c1);
            if (n3) atomicAdd((unsigned long long*)&n3a[ip],(unsigned long long)n3);
        }
    }
}

__global__ void collect_fat(const u32* __restrict__ ndfac, u32 len,
                            u32* __restrict__ fat_idx, u32* __restrict__ fat_cnt)
{
    u32 j = blockIdx.x*blockDim.x+threadIdx.x;
    if (j>=len) return;
    if (ndfac[j] > SMEM_CAP) { u32 s=atomicAdd(fat_cnt,1u); fat_idx[s]=j; }
}

__global__ void fat_fill(u64 x, u32 k, const u64* __restrict__ qfac,
                         const u128* __restrict__ qpfac, u32 j, u128* __restrict__ g)
{
    if (blockIdx.x||threadIdx.x) return;
    u64 q[KMAX]; u128 qp[KMAX];
    for (u32 i=0;i<k;i++){ q[i]=qfac[j*KMAX+i]; qp[i]=qpfac[j*KMAX+i]; }
    build_divs(g, k, q, qp);
}

__global__ void fat_scan(const u64* __restrict__ primes, int np, u64 x, u32 nd,
                         const u128* __restrict__ g, u64* __restrict__ c0a,
                         u64* __restrict__ c1a, u64* __restrict__ n3a)
{
    int lo,hi; prime_window(primes,np,x,lo,hi);
    int ip = lo + blockIdx.x*blockDim.x+threadIdx.x;
    if (ip>=hi) return;
    u64 p=primes[ip], c0=0,c1=0,n3=0;
    scan_divs(g, nd, x, p, c0, c1, n3);
    if (c0|c1){ atomicAdd((unsigned long long*)&c0a[ip],(unsigned long long)c0);
        if(c1) atomicAdd((unsigned long long*)&c1a[ip],(unsigned long long)c1);
        if(n3) atomicAdd((unsigned long long*)&n3a[ip],(unsigned long long)n3); }
}

// ---------------- host ----------------
static void write_csv(const char* path, const std::vector<u64>& primes,
                      const std::vector<u64>& c0, const std::vector<u64>& c1,
                      const std::vector<u64>& n3)
{
    FILE* f = fopen(path,"w"); if(!f){perror("fopen");exit(1);}
    fprintf(f,"p,ford,fI,fII\n");
    for (size_t i=0;i<primes.size();i++){
        long long ford = 6LL*(long long)(c0[i]+c1[i]) - 3LL*(long long)n3[i];
        fprintf(f,"%llu,%lld,%llu,%llu\n", primes[i], ford, c0[i], c1[i]);
    }
    fclose(f);
}

int main(int argc, char** argv)
{
    if (argc < 5) { fprintf(stderr,"usage: %s pmin pmax mode(0|1) out.csv\n",argv[0]); return 1; }
    u64 pmin = strtoull(argv[1],0,10), pmax = strtoull(argv[2],0,10);
    int mode = atoi(argv[3]); const char* out_path = argv[4];
    auto in_mode = [&](u64 p){ return mode==0 || p%24==1; };
    auto t_start = std::chrono::steady_clock::now();

    // base primes to √pmax (covers both factoring x ≤ (pmax+1)/2 and the segmented sieve)
    u64 lim = (u64)sqrtl((long double)pmax) + 2;
    std::vector<u32> base; {
        std::vector<char> c(lim+1,0);
        for (u64 i=2;i<=lim;i++) if(!c[i]){ base.push_back((u32)i); for(u64 j=i*i;j<=lim;j+=i) c[j]=1; }
    }
    // segmented sieve → target primes (u64), no O(p) bitmap
    std::vector<u64> primes;
    { const u64 SEG = 1u<<22; std::vector<char> seg(SEG);
      u64 start = pmin<5?5:pmin;
      for (u64 lo=start; lo<=pmax; lo+=SEG) {
        u64 hi=std::min(lo+SEG-1,pmax), sz=hi-lo+1;
        std::fill(seg.begin(), seg.begin()+sz, 1);
        for (u32 q: base){ u64 q2=(u64)q*q; u64 first=q2>lo?q2:((lo+q-1)/q)*q;
            for(u64 m=first;m<=hi;m+=q) seg[m-lo]=0; }
        for (u64 i=0;i<sz;i++) if(seg[i]){ u64 p=lo+i; if(in_mode(p)) primes.push_back(p); }
      } }
    int np=(int)primes.size();
    fprintf(stderr,"primes in range/mode: %d   base primes: %zu (√pmax=%llu)\n",np,base.size(),lim);
    if(!np){ write_csv(out_path,primes,{},{},{}); return 0; }

    u32 nbp=(u32)base.size();
    u32 *d_base,*d_kfac,*d_ndfac; u64 *d_qfac,*d_primes,*d_c0,*d_c1,*d_n3; u128 *d_qpfac;
    CUDA_CHECK(cudaMalloc(&d_base,nbp*sizeof(u32)));
    CUDA_CHECK(cudaMemcpy(d_base,base.data(),nbp*sizeof(u32),cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMalloc(&d_primes,(size_t)np*sizeof(u64)));
    CUDA_CHECK(cudaMemcpy(d_primes,primes.data(),(size_t)np*sizeof(u64),cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMalloc(&d_c0,(size_t)np*sizeof(u64))); CUDA_CHECK(cudaMemset(d_c0,0,(size_t)np*sizeof(u64)));
    CUDA_CHECK(cudaMalloc(&d_c1,(size_t)np*sizeof(u64))); CUDA_CHECK(cudaMemset(d_c1,0,(size_t)np*sizeof(u64)));
    CUDA_CHECK(cudaMalloc(&d_n3,(size_t)np*sizeof(u64))); CUDA_CHECK(cudaMemset(d_n3,0,(size_t)np*sizeof(u64)));
    CUDA_CHECK(cudaMalloc(&d_kfac,DX_CAP*sizeof(u32)));
    CUDA_CHECK(cudaMalloc(&d_ndfac,DX_CAP*sizeof(u32)));
    CUDA_CHECK(cudaMalloc(&d_qfac,(size_t)DX_CAP*KMAX*sizeof(u64)));
    CUDA_CHECK(cudaMalloc(&d_qpfac,(size_t)DX_CAP*KMAX*sizeof(u128)));
    u32 *d_fat_idx,*d_fat_cnt; u128 *d_fat_divs;
    CUDA_CHECK(cudaMalloc(&d_fat_idx,DX_CAP*sizeof(u32)));
    CUDA_CHECK(cudaMalloc(&d_fat_cnt,sizeof(u32)));
    CUDA_CHECK(cudaMalloc(&d_fat_divs,(size_t)FATCAP*sizeof(u128)));
    size_t smem=(size_t)SMEM_CAP*sizeof(u128);
    CUDA_CHECK(cudaFuncSetAttribute(fp_kernel,cudaFuncAttributeMaxDynamicSharedMemorySize,(int)smem));

    u64 Xcur=pmin/4+1; if(Xcur<2)Xcur=2;
    u64 Xend=(pmax+1)/2; u64 dX=1<<13, launches=0;
    std::vector<u64> h_c0(np),h_c1(np),h_n3(np);
    while (Xcur<=Xend) {
        u64 X1=Xcur+dX; if(X1>Xend+1)X1=Xend+1; u32 len=(u32)(X1-Xcur);
        auto t0=std::chrono::steady_clock::now();
        factor_chunk<<<(len+255)/256,256>>>(d_base,nbp,Xcur,len,d_kfac,d_ndfac,d_qfac,d_qpfac);
        CUDA_CHECK(cudaGetLastError());
        CUDA_CHECK(cudaMemset(d_fat_cnt,0,sizeof(u32)));
        collect_fat<<<(len+255)/256,256>>>(d_ndfac,len,d_fat_idx,d_fat_cnt);
        fp_kernel<<<len,TPB,smem>>>(d_primes,np,Xcur,d_kfac,d_ndfac,d_qfac,d_qpfac,d_c0,d_c1,d_n3);
        CUDA_CHECK(cudaGetLastError());
        u32 fat_cnt=0; CUDA_CHECK(cudaMemcpy(&fat_cnt,d_fat_cnt,sizeof(u32),cudaMemcpyDeviceToHost));
        if (fat_cnt) {
            std::vector<u32> fi(fat_cnt);
            CUDA_CHECK(cudaMemcpy(fi.data(),d_fat_idx,fat_cnt*sizeof(u32),cudaMemcpyDeviceToHost));
            for (u32 f=0; f<fat_cnt; f++) {
                u32 j=fi[f],kx=0,nd=0;
                CUDA_CHECK(cudaMemcpy(&kx,d_kfac+j,sizeof(u32),cudaMemcpyDeviceToHost));
                CUDA_CHECK(cudaMemcpy(&nd,d_ndfac+j,sizeof(u32),cudaMemcpyDeviceToHost));
                if (nd>FATCAP){ fprintf(stderr,"FATAL d(x²)=%u>FATCAP at x=%llu\n",nd,Xcur+j); exit(1); }
                u64 x=Xcur+j, plo=2*x-1, phi=4*x;
                int lo=(int)(std::lower_bound(primes.begin(),primes.end(),plo)-primes.begin());
                int hi=(int)(std::lower_bound(primes.begin(),primes.end(),phi)-primes.begin());
                if (lo>=hi) continue;
                fat_fill<<<1,1>>>(x,kx,d_qfac,d_qpfac,j,d_fat_divs);
                fat_scan<<<(hi-lo+TPB-1)/TPB,TPB>>>(d_primes,np,x,nd,d_fat_divs,d_c0,d_c1,d_n3);
                CUDA_CHECK(cudaGetLastError());
            }
        }
        CUDA_CHECK(cudaDeviceSynchronize());
        double dt=std::chrono::duration<double>(std::chrono::steady_clock::now()-t0).count();
        Xcur=X1; launches++;
        if (dt<0.12 && dX<DX_CAP) dX*=2; else if (dt>0.5 && dX>1024) dX/=2;
        if (launches%200==0 || Xcur>Xend) {
            double frac=(double)(Xcur-(pmin/4+1))/(double)(Xend-(pmin/4+1)+1);
            double el=std::chrono::duration<double>(std::chrono::steady_clock::now()-t_start).count();
            fprintf(stderr,"x=%llu/%llu (%.1f%%) dX=%llu elapsed=%.0fs eta=%.0fs\n",
                    Xcur,Xend,100*frac,dX,el,frac>0?el/frac-el:0);
        }
        if (launches%1000==0){
            CUDA_CHECK(cudaMemcpy(h_c0.data(),d_c0,(size_t)np*sizeof(u64),cudaMemcpyDeviceToHost));
            CUDA_CHECK(cudaMemcpy(h_c1.data(),d_c1,(size_t)np*sizeof(u64),cudaMemcpyDeviceToHost));
            CUDA_CHECK(cudaMemcpy(h_n3.data(),d_n3,(size_t)np*sizeof(u64),cudaMemcpyDeviceToHost));
            char tmp[4096]; snprintf(tmp,sizeof tmp,"%s.partial",out_path);
            write_csv(tmp,primes,h_c0,h_c1,h_n3);
        }
    }
    CUDA_CHECK(cudaMemcpy(h_c0.data(),d_c0,(size_t)np*sizeof(u64),cudaMemcpyDeviceToHost));
    CUDA_CHECK(cudaMemcpy(h_c1.data(),d_c1,(size_t)np*sizeof(u64),cudaMemcpyDeviceToHost));
    CUDA_CHECK(cudaMemcpy(h_n3.data(),d_n3,(size_t)np*sizeof(u64),cudaMemcpyDeviceToHost));
    write_csv(out_path,primes,h_c0,h_c1,h_n3);
    double total=std::chrono::duration<double>(std::chrono::steady_clock::now()-t_start).count();
    fprintf(stderr,"primes=%d launches=%llu time=%.1fs\n",np,launches,total);
    return 0;
}
