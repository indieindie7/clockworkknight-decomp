#!/bin/bash
# apply + export for root programs: PROGS="GEKAN_A CK2USA_A GEKAN_AREA61_LO" bash apply_root.sh
export SP="${SP:?scripts dir}"
cd "${CK_GHIDRA:-.}"
G="${CK_GHIDRA_WIN:?windows path of this dir}"
for p in ${PROGS:-GEKAN_A CK2USA_A}; do
  h=$(echo $p | sed 's/_A$//; s/_LO$//')
  bash ckrun.sh logs/apply_$p.log -process $p.BIN -noanalysis -postScript ApplyNames.java "$G\hand_$h.txt" >/dev/null 2>&1
  grep -o 'functions named [0-9]*' logs/apply_$p.log | tail -1
  bash ckrun.sh logs/export_$p.log -process $p.BIN -noanalysis -readOnly -postScript ExportFuncInfo.java "$G\funcinfo_$p.tsv" >/dev/null 2>&1
  echo "$p F=$(awk '$1=="F"' funcinfo_$p.tsv | wc -l) FUN=$(awk '$1=="F" && $3 ~ /^FUN_/' funcinfo_$p.tsv | wc -l)"
done
