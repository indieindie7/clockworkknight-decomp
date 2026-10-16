# ovlprep.py: prepare Sonnet naming slices for one overlay program.
# usage: py -3.13 -I ovlprep.py <ghidra> <prog> <desc> <N>
# Reads decomp_<prog>.c, replaces func_0x060xxxxx / FUN_060xxxxx with hand_GEKAN.txt names and FUN_002xxxxx with
# hand_<prog>.txt names, writes naming/<prog>_sub.c, slices it (slice2.py rules: FUN_ only, not in hand) into
# naming/<prog>_<k>.c, and writes naming/<prog>_prompt.txt from scripts/n1_prompt_ck_area_t.txt.
import sys, os, re
g, prog, desc, n = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
def hand(fn):
    d = {}
    if not os.path.exists(fn): return d
    for l in open(fn, encoding='utf-8', errors='replace'):
        f = l.split(None, 4)
        if len(f) >= 4: d[f[0][2:].lower().zfill(8)] = f[2]
    return d
boot = {} if prog.endswith('_A') else hand(os.path.join(g, 'hand_%s.txt' % prog.split('_AREA')[0]))  # overlays: their game's boot names (hand_GEKAN / hand_CK1 / hand_CK2US)
own = hand(os.path.join(g, 'hand_%s.txt' % prog))
nm = {**boot, **own}
src = open(os.path.join(g, 'decomp_%s.c' % prog), encoding='utf-8', errors='replace').read()
src = re.sub(r'(?:func_0x|FUN_|PTR_FUN_)([0-9a-fA-F]{8})', lambda m: nm.get(m.group(1).lower(), m.group(0)), src)
nd = os.path.join(g, 'naming'); os.makedirs(nd, exist_ok=True)
open(os.path.join(nd, prog + '_sub.c'), 'w', encoding='utf-8', newline='\n').write(src)
# slice: whole functions, FUN_ only
funcs, cur = [], None
for l in src.splitlines(True):
    m = re.match(r'// ==== (\S+) @ ([0-9a-fA-F]+)', l)
    if m:
        cur = [m.group(1), m.group(2).lower().zfill(8), []]; funcs.append(cur)
    if cur: cur[2].append(l)
todo = [f for f in funcs if f[0].startswith('FUN_') and f[1] not in own]
tot = sum(len(f[2]) for f in todo); per = tot / max(n, 1)
k, acc, out = 1, 0, []
files = []
def flush():
    global k, acc, out
    if out:
        fn = os.path.join(nd, '%s_%d.c' % (prog, k))
        open(fn, 'w', encoding='utf-8', newline='\n').write(''.join(''.join(f[2]) for f in out))
        files.append((fn, len(out), sum(len(f[2]) for f in out)))
        k += 1; acc = 0; out = []
for f in todo:
    out.append(f); acc += len(f[2])
    if acc >= per and k < n: flush()
flush()
t = open(os.path.join(g, 'scripts', 'n1_prompt_ck_area_t.txt'), encoding='utf-8').read()
GAMES = {'GEKAN': ('Sega Saturn game Clockwork Knight 2 (Sega CS2, Japan GS-9029 "Pepperouchau no Daibouken Gekan" 1995-07; SH-2 code, likely Hitachi SHC or GNU).', 'A.BIN'),
         'CK1': ('Sega Saturn game Clockwork Knight 1 (Sega CS2, 1994; the build bundled on the US Clockwork Knight 2 disc as JAPUS.BIN; SH-2 code, likely Hitachi SHC or GNU).', 'JAPUS.BIN'),
         'CK2US': ('Sega Saturn game Clockwork Knight 2 (Sega CS2, US MK-81036 1995; boot program GAPUS.BIN; SH-2 code, likely Hitachi SHC or GNU).', 'GAPUS.BIN')}
game, bootbin = GAMES[re.sub(r'_A$', '', prog.split('_AREA')[0])]
t = t.replace('{OVL}', prog + '.BIN').replace('{DESC}', desc).replace('{GAME}', game).replace('{BOOT}', bootbin)
open(os.path.join(nd, prog + '_prompt.txt'), 'w', encoding='utf-8', newline='\n').write(t)
print(prog, 'todo', len(todo), ' '.join('%s:%d/%d' % (os.path.basename(a), b, c) for a, b, c in files))
