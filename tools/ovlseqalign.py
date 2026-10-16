# ovlseqalign.py: transfer hand names between two builds of the same overlay by sequence alignment.
# The US-disc overlays are a recompile of the Gekan ones (same function order, sizes differ by a few bytes), so the
# byte fingerprint of ovltransfer.py fails. This aligns the two function lists (sorted by address) with a DP that
# scores a pair by size similarity and callee count, and writes hand_<tgt>.txt lines "=seq:<src>" for the aligned
# pairs. usage: py -3.13 -I ovlseqalign.py <ghidra> <tgt> <src> [--show]
import sys, os
g, tgt, src = sys.argv[1], sys.argv[2], sys.argv[3]
show = '--show' in sys.argv
def funcs(p):
    out, cur = [], None
    for l in open(os.path.join(g, 'funcinfo_%s.tsv' % p), encoding='utf-8', errors='replace'):
        f = l.split()
        if not f: continue
        if f[0] == 'F':
            cur = [int(f[1], 16), f[2], int(f[4]) if len(f) > 4 else 0, 0]; out.append(cur)
        elif f[0] == 'C' and cur: cur[3] += 1
    return out
def hand(p):
    d = {}
    fn = os.path.join(g, 'hand_%s.txt' % p)
    if not os.path.exists(fn): fn = os.path.join(g, 'hand_%s.txt' % p.rsplit('_', 1)[0])
    for l in open(fn, encoding='utf-8', errors='replace'):
        f = l.split(None, 4)
        if len(f) >= 4: d[int(f[0], 16)] = (f[2], f[4].strip() if len(f) > 4 else '')
    return d
T, S, H = funcs(tgt), funcs(src), hand(src)
def score(a, b):
    sa, sb = a[2], b[2]
    if sa == 0 or sb == 0: return -9
    r = abs(sa - sb) / max(sa, sb)
    if r > 0.15: return -9
    s = 3 - 20 * r
    if a[3] == b[3]: s += 1
    elif abs(a[3] - b[3]) > 2: s -= 1
    return s
n, m = len(T), len(S)
D = [[0.0] * (m + 1) for _ in range(n + 1)]
P = [[0] * (m + 1) for _ in range(n + 1)]
GAP = -0.5
for i in range(1, n + 1):
    for j in range(1, m + 1):
        best, p = D[i - 1][j] + GAP, 1
        if D[i][j - 1] + GAP > best: best, p = D[i][j - 1] + GAP, 2
        sc = score(T[i - 1], S[j - 1])
        if sc > -9 and D[i - 1][j - 1] + sc > best: best, p = D[i - 1][j - 1] + sc, 3
        D[i][j], P[i][j] = best, p
i, j, pairs = n, m, []
while i > 0 and j > 0:
    if P[i][j] == 3: pairs.append((T[i - 1], S[j - 1])); i -= 1; j -= 1
    elif P[i][j] == 1: i -= 1
    else: j -= 1
pairs.reverse()
out, used, named = [], {}, 0
for a, b in pairs:
    if b[0] not in H: continue
    nm, cm = H[b[0]]
    if nm in used: nm = '%s_%06x' % (nm, a[0])
    used[nm] = 1
    r = abs(a[2] - b[2]) / max(a[2], b[2])
    weak = 'provisional ' if (r > 0.10 or abs(a[3] - b[3]) > 1) and 'provisional' not in cm else ''
    out.append('0x%08x func %s hand %s=seq:%s r=%.2f %s' % (a[0], nm, weak, src, r, cm)); named += 1
    if show: print('%08x %5d %2d <- %08x %5d %2d %s' % (a[0], a[2], a[3], b[0], b[2], b[3], nm))
fn = os.environ.get('OUT') or os.path.join(g, 'hand_%s.txt' % tgt)
open(fn, 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + ('\n' if out else ''))
print(tgt, 'functions', n, 'src', m, 'aligned', len(pairs), 'named', named, 'unmatched', n - named)
