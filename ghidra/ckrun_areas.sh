#!/bin/bash
# headless Ghidra wrapper (set GHIDRA_HEADLESS = analyzeHeadless.bat, PROJ_DIR = Ghidra project dir, SP = scripts dir, CK_GHIDRA = this dir). usage: ckrun.sh <abs log> <args...> (e.g. -process X -noanalysis -postScript Y)
log="$1"; shift
cd "${CK_GHIDRA:-.}" || exit 1
cmd //c "${GHIDRA_HEADLESS} ${PROJ_DIR} ClockworkKnight/areas $* -scriptPath ${SP}" < /dev/null > "$log" 2>&1
tail -2 "$log"
