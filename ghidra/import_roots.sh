#!/bin/bash
# root programs of the US disc (JAPUS -> CK1_A, GAPUS -> CK2US_A) at 0x06003000; run after import_us.sh (one headless job at a time)
export SP="${SP:?scripts dir}"
cd "${CK_GHIDRA:-.}"
G="${CK_GHIDRA_WIN:?windows path of this dir}"
L=logs
for p in ${ROOTS:-CK1_A CK2US_A}; do
  b="$G"'\bin\'"$p.BIN"
  bash ckrun.sh $L/import_$p.log -import "$b" -processor SuperH:BE:32:SH-2 -loader BinaryLoader -loader-baseAddr 0x06003000 -postScript FindSh2FunctionsMem.java -postScript CreateAt.java 0x06003000 >/dev/null 2>&1
  bash ckrun.sh $L/export_$p.log -process $p.BIN -noanalysis -readOnly -postScript ExportFuncInfo.java "$G\funcinfo_$p.tsv" >/dev/null 2>&1
  bash ckrun.sh $L/dump_$p.log -process $p.BIN -noanalysis -readOnly -postScript CsDumpAll.java "$G\decomp_$p.c" >/dev/null 2>&1
  echo "$p F=$(awk '$1=="F"' funcinfo_$p.tsv | wc -l) dump=$(grep -c '^// ====' decomp_$p.c)"
done
echo ROOTSDONE
