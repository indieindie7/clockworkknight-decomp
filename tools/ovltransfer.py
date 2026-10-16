# ovltransfer.py: copy hand names between AREA overlays by function-body fingerprint.
# usage: py -3.13 -I ovltransfer.py <ghidra dir> <target prog e.g. GEKAN_AREA62> <source prog>...
# Reads <ghidra>/funcinfo_<prog>.tsv (F addr name src size), <ghidra>/bin/areas/<prog>.BIN or bin/<prog>_LO.BIN,
# and hand_<src>.txt. Key = (size, first min(size,96) bytes). Writes hand_<target>.txt lines for matches
# (comment prefixed with =<src>) and prints matched/unmatched counts; unmatched FUN_ listed in naming/<target>_left.txt.
import sys, os
g, tgt, srcs = sys.argv[1], sys.argv[2], sys.argv[3:]
BASE = 0x06003000 if tgt.endswith('_A') else 0x200000  # root programs (*_A) at 0x06003000, overlays at 0x00200000
def img(p):
    for c in (os.path.join(g, 'bin', 'areas', p + '.BIN'), os.path.join(g, 'bin', p + '_LO.BIN'), os.path.join(g, 'bin', p + '.BIN')):
        if os.path.exists(c): return open(c, 'rb').read()
    raise SystemExit('no image for ' + p)
def funcs(p):
    out = []
    for l in open(os.path.join(g, 'funcinfo_%s.tsv' % p), encoding='utf-8', errors='replace'):
        f = l.split()
        if f and f[0] == 'F': out.append((int(f[1], 16), f[2], int(f[4]) if len(f) > 4 else 0))
    return out
def hand(p):
    d = {}
    fn = os.path.join(g, 'hand_%s.txt' % p)
    if not os.path.exists(fn) and (p.endswith('_LO') or p.endswith('_A')): fn = os.path.join(g, 'hand_%s.txt' % p.rsplit('_',1)[0])
    if not os.path.exists(fn): return d
    for l in open(fn, encoding='utf-8', errors='replace'):
        f = l.split(None, 4)
        if len(f) >= 4: d[int(f[0], 16)] = (f[2], f[4].strip() if len(f) > 4 else '')
    return d
MASK = os.environ.get('MASK') == '1'  # MASK=1: zero pointer words and bsr/bra/jsr-pool displacements (cross-build transfer)
def key(b, a, s):
    o = a - BASE; n = max(16, min(s, 96))
    w = bytearray(b[o:o + n])
    if MASK:
        for i in range(0, n - 3, 4):
            v = int.from_bytes(w[i:i + 4], 'big')
            if 0x00200000 <= v < 0x00300000 or 0x06000000 <= v < 0x06100000: w[i:i + 4] = bytes(4)
        for i in range(0, n - 1, 2):
            if w[i] & 0xf0 in (0xa0, 0xb0): w[i] &= 0xf0; w[i + 1] = 0   # bra / bsr
            if w[i] & 0xf0 == 0xd0: w[i + 1] = 0                           # mov.l @(disp,pc),Rn
    return (s, bytes(w))
table = {}
for s in srcs:
    b = img(s); h = hand(s)
    for a, n, sz in funcs(s):
        if a in h and sz > 0: table.setdefault(key(b, a, sz), (s, h[a][0], h[a][1]))
b = img(tgt); out = []; left = []; used = {}
for a, n, sz in funcs(tgt):
    k = key(b, a, sz) if sz > 0 else None
    if k in table:
        s, nm, cm = table[k]
        if nm in used: nm = '%s_%06x' % (nm, a)
        used[nm] = 1
        out.append('0x%08x func %s hand =%s %s' % (a, nm, s, cm))
    else: left.append('%08x' % a)
open(os.path.join(g, 'hand_%s.txt' % tgt), 'w', encoding='utf-8').write('\n'.join(out) + ('\n' if out else ''))
os.makedirs(os.path.join(g, 'naming'), exist_ok=True)
open(os.path.join(g, 'naming', '%s_left.txt' % tgt), 'w').write('\n'.join(left) + '\n')
print(tgt, 'functions', len(out) + len(left), 'matched', len(out), 'unmatched', len(left))
