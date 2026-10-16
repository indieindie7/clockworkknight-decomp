# Clockwork Knight (Sega Saturn, 1994-95) reverse-engineering notes and symbols

Hand-named function map, review records, notes and tools for the Sega Saturn **Clockwork Knight** games
(Sega CS2): *Pepperouchau no Daibouken Gekan* (JP, GS-9029, 1995), *Clockwork Knight 2 - Pepperouchau's
Adventure* (US, MK-81036, 1995) and the *Pepperouchau no Fukubukuro* compilation (JP, GS-9074, 1995).
SH-2 code, Sega SBL library. Seventeen programs are covered, every function hand-named (a provisional
mark means the first review round could not settle the name):

- `GEKAN_A` (the Gekan boot program `A.BIN` at 0x06003000): 565 functions, 34 provisional;
- `CK2USA_A` (the US boot program, built from the Fukubukuro code): 405 functions, 18 provisional;
- `FUKU_A` (the Fukubukuro boot program): 443 functions, 5 provisional;
- the 14 Gekan level overlays `AREA<n><x>.BIN`, which run in low work RAM at 0x00200000
  (`<n>B` are the boss overlays): 0B 96, 51 147, 52 83, 5B 73, 61 167, 62 234, 6B 116, 71 214,
  72 111, 7B 136, 81 218, 82 184, 8B 136, 9B 78 functions; 58 provisional in all.

3451 names, 115 still provisional.

**CK1 and CK2 from the US disc** (*Clockwork Knight 2* US disc, which also carries the first game): 29 more
programs, every function named.

- `CK1_A` (Clockwork Knight 1 program from `JAPUS.BIN`, 0x06003000): 782 functions, 16 provisional after review;
- `CK2US_A` (Clockwork Knight 2 program from `GAPUS.BIN`, 0x06003000): 669 functions, 6 provisional after review;
- `CK1_AREA<x>`, 13 overlays at 0x00200000 (11 13 1B 2B 31 32 3B 41 43 4B 71 73 7B): 1737 functions;
- `CK2US_AREA<x>`, 14 overlays at 0x00200000 (same set as Gekan): 2003 functions.

5191 names in these 29 programs. Only the two boot programs went through a review round. **Most overlay
names (1460 of 1737 in CK1, 668 of 2003 in CK2 US) are still marked `provisional`**: they come from one
naming pass and are a good first guess, not a checked name. The US CK2 overlays are a recompile of the
Gekan ones, so their names came over by sequence alignment (`tools/ovlseqalign.py`); CK1 was named from
scratch and spread between its overlays by masked fingerprint (`ovltransfer.py MASK=1`).

Same method as [pandemonium-decomp](https://github.com/indieindie7/pandemonium-decomp)
and [sonicr-decomp](https://github.com/indieindie7/sonicr-decomp): function discovery by SH-2 prologue scan,
a first naming pass in slices, name transfer between overlays by body fingerprint (size + first 96 bytes),
then a review round in which every provisional name was re-read together with its callers. The overlay
base was proved from the pointer histogram (A.BIN's BSS fills high work RAM; 0x0603b400 is only the CD
staging buffer). Non-commercial, done for study and preservation.

**No game data is included**: no disc image, no program files, no unpacked data, no decompiled C,
no game text, no Ghidra database. You need your own copies of the games to use any of this.

## What is here

| Path | Content |
|---|---|
| `NOTES.md` | the working log: disc layout, Ghidra setup, the overlay base search, naming rounds, review counts |
| `ghidra/hand_GEKAN.txt`, `hand_CK2USA.txt`, `hand_FUKU.txt` | hand-named boot-program functions (`0x<addr> func <name> hand <comment>`) |
| `ghidra/hand_GEKAN_AREA<x>.txt` | hand-named overlay functions, one file per overlay |
| `ghidra/funcinfo_*.tsv` | per-function export: `F` address name source size, `C` callees (string rows removed) |
| `ghidra/review/rv_*.txt` | review verdicts (`<prog> 0x<addr> <old> CONFIRM/RENAME/UNSURE <new> <reason>`) |
| `ghidra/scripts/` | the naming and review prompts |
| `ghidra/ckrun.sh`, `ckrun_areas.sh`, `apply_root.sh`, `apply3.sh` | headless Ghidra wrappers and the apply + export loops (set `GHIDRA_HEADLESS`, `PROJ_DIR`, `SP`, `CK_GHIDRA`, `CK_GHIDRA_WIN`) |
| `ghidra/hand_CK1.txt`, `hand_CK2US.txt`, `hand_CK1_AREA<x>.txt`, `hand_CK2US_AREA<x>.txt` | the US-disc programs, same format |
| `ghidra/import_us.sh`, `import_roots.sh` | import the US-disc programs (bases above) |
| `tools/` | `ovltransfer.py` (fingerprint name transfer, `MASK=1` masks pointers), `ovlseqalign.py` (transfer between recompiled builds), `xfermerge.py`, `fpgroups.py` (shared-body counts), `ovlprep.py` / `ovlmerge.py` (naming slices), `ckprovctx.py` (review contexts), `ckbase.py` (load-base pointer histogram) |

`ApplyNames.java`, `ExportFuncInfo.java` and `FindSh2FunctionsMem.java` come from the Scorcher / AMOK /
Pandemonium repos.

## Licence

Notes, names and tools: MIT (see `LICENSE`). Clockwork Knight belongs to its rights holders; nothing from
the games is distributed here. Takedown requests will be honoured.
