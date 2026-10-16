#!/bin/bash
# import the US-disc programs: CK1_A / CK2US_A (root, base 0x06003000) and CK1_AREA* / CK2US_AREA* (/areas, base 0x00200000)
export SP="${SP:?scripts dir}"
cd "${CK_GHIDRA:-.}"
G="${CK_GHIDRA_WIN:?windows path of this dir}"
L=logs
imp() { # runner prog binpath base
  r=$1; p=$2; b=$3; base=$4
  bash $r $L/import_$p.log -import "$b" -processor SuperH:BE:32:SH-2 -loader BinaryLoader -loader-baseAddr $base -postScript FindSh2FunctionsMem.java -postScript CreateAt.java $base >/dev/null 2>&1
  bash $r $L/export_$p.log -process $p.BIN -noanalysis -readOnly -postScript ExportFuncInfo.java "$G\funcinfo_$p.tsv" >/dev/null 2>&1
  bash $r $L/dump_$p.log -process $p.BIN -noanalysis -readOnly -postScript CsDumpAll.java "$G\decomp_$p.c" >/dev/null 2>&1
  echo "$p F=$(awk '$1=="F"' funcinfo_$p.tsv | wc -l) dump=$(grep -c '^// ====' decomp_$p.c)"
}
for p in ${ROOTS:-CK1_A CK2US_A}; do imp ckrun.sh $p "$G\bin\$p.BIN" 0x06003000; done
for x in ${CK1AREAS:-11 13 1B 2B 31 32 3B 41 43 4B 71 73 7B}; do imp ckrun_areas.sh CK1_AREA$x "$G\bin\areas\CK1_AREA$x.BIN" 0x00200000; done
for x in ${CK2AREAS:-0B 51 52 5B 61 62 6B 71 72 7B 81 82 8B 9B}; do imp ckrun_areas.sh CK2US_AREA$x "$G\bin\areas\CK2US_AREA$x.BIN" 0x00200000; done
echo ALLDONE
