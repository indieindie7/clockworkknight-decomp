# fpgroups.py: count functions shared between overlays by masked fingerprint (same key as ovltransfer.py MASK=1).
# usage: py -3.13 -I fpgroups.py <ghidra> <prog>...   prints per program: functions, shared with another listed program
import sys, os
from collections import defaultdict
g, progs = sys.argv[1], sys.argv[2:]
def img(p):
    for c in (os.path.join(g, 'bin', 'areas', p + '.BIN'), os.path.join(g, 'bin', p + '.BIN')):
        if os.path.exists(c): return open(c, 'rb').read()
def key(b, o, s):
    n = max(16, min(s, 96)); w = bytearray(b[o:o + n])
    for i in range(0, n - 3, 4):
        v = int.from_bytes(w[i:i + 4], 'big')
        if 0x00200000 <= v < 0x00300000 or 0x06000000 <= v < 0x06100000: w[i:i + 4] = bytes(4)
    for i in range(0, n - 1, 2):
        if w[i] & 0xf0 in (0xa0, 0xb0): w[i] &= 0xf0; w[i + 1] = 0
        if w[i] & 0xf0 == 0xd0: w[i + 1] = 0
    return (s, bytes(w))
owners, per = defaultdict(set), {}
for p in progs:
    base = 0x06003000 if p.endswith('_A') else 0x200000
    b = img(p); ks = []
    for l in open(os.path.join(g, 'funcinfo_%s.tsv' % p), encoding='utf-8', errors='replace'):
        f = l.split()
        if f and f[0] == 'F' and len(f) > 4 and int(f[4]) > 0:
            k = key(b, int(f[1], 16) - base, int(f[4])); ks.append(k); owners[k].add(p)
    per[p] = ks
uniq = set()
for p in progs:
    sh = sum(1 for k in per[p] if len(owners[k]) > 1)
    print(p, 'functions', len(per[p]), 'shared', sh)
    uniq |= set(per[p])
print('distinct bodies over all', len(uniq), 'total functions', sum(len(v) for v in per.values()))
