#!/usr/bin/env bash
# Fresh f(p) at six decade scales via fp128 mode 2 (sq-classes) — for the §8.2 scale table
# (how the L-correlation / exponent c moves with p).  Single validated engine, clean from scratch.
#
# Resumable at SCALE granularity: re-running skips any scale whose output CSV already exists,
# so a crash/reboot only costs the in-flight scale.  (fp128 writes the CSV only on completion;
# its <out>.partial is a progress snapshot, not a resume point.)
#
# Launch:  nohup bash analysis/run_scale_study.sh &   (or via the agent's background runner)
set -u
cd "$(dirname "$0")/.."
ENG=./engines/fp128
OUT=data/fresh; mkdir -p "$OUT"

# tag   pmin            pmax            (1e9/1e10 = the full existing windows ~14955/13564 hard;
#                                        others sized for ~2000 hard primes)
RUNS="
1e6   1000000         1900000
1e7   10000000        11100000
1e8   100000000       101200000
1e9   1000000000      1010000000
1e10  10000000000     10010000000
1e11  100000000000    100001700000
"

echo "[$(date '+%F %T')] scale study start (engine: $ENG, mode 2 = sq-classes)"
echo "$RUNS" | while read -r tag lo hi; do
  [ -z "$tag" ] && continue
  csv="$OUT/fresh_${tag}.csv"
  if [ -s "$csv" ]; then
    echo "[$(date '+%F %T')] SKIP  $tag  (already have $(($(wc -l <"$csv")-1)) rows)"
    continue
  fi
  echo "[$(date '+%F %T')] START $tag  $ENG $lo $hi 2 -> $csv"
  "$ENG" "$lo" "$hi" 2 "$csv" 2> "$OUT/fresh_${tag}.log"
  rc=$?
  n=$(( $(wc -l < "$csv" 2>/dev/null || echo 1) - 1 ))
  echo "[$(date '+%F %T')] DONE  $tag  rc=$rc  n=$n"
  if [ $rc -ne 0 ]; then
    echo "[$(date '+%F %T')] ABORT at $tag (rc=$rc) — fix and re-run this script to resume."
    exit $rc
  fi
done
echo "[$(date '+%F %T')] ALL SCALES COMPLETE"
