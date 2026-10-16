#!/bin/bash
export SP="${SP:?scripts dir}"
cd "${CK_GHIDRA:-.}"
G="${CK_GHIDRA_WIN:?windows path of this dir}"
for x in ${AREAS:-81 62 0B}; do
  p=GEKAN_AREA$x
  bash ckrun_areas.sh $PWD/logs/apply_$p.log -process $p.BIN -noanalysis -postScript ApplyNames.java "$G\hand_$p.txt" >/dev/null 2>&1
  grep -o 'functions named [0-9]*' logs/apply_$p.log | tail -1
  bash ckrun_areas.sh $PWD/logs/export_$p.log -process $p.BIN -noanalysis -readOnly -postScript ExportFuncInfo.java "$G\funcinfo_$p.tsv" >/dev/null 2>&1
  echo "$p F=$(awk '$1=="F"' funcinfo_$p.tsv | wc -l) FUN=$(awk '$1=="F" && $3 ~ /^FUN_/' funcinfo_$p.tsv | wc -l)"
done
