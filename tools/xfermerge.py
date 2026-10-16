# xfermerge.py: merge transfer files into hand_<prog>.txt; earlier files win per address (fingerprint first, then
# alignment). Names made unique with a _<addr> suffix. usage: py -3.13 -I xfermerge.py <ghidra> <prog> <file>...
import sys, os, re
g, prog, files = sys.argv[1], sys.argv[2], sys.argv[3:]
d = {}
for fn in files:
    if not os.path.exists(fn): continue
    for l in open(fn, encoding='utf-8', errors='replace'):
        m = re.match(r'(0x[0-9a-fA-F]{8}) func (\S+) hand ?(.*)$', l.rstrip('\r\n'))
        if m and int(m.group(1), 16) not in d: d[int(m.group(1), 16)] = [m.group(2), m.group(3)]
seen = set()
for a in sorted(d):
    if d[a][0] in seen: d[a][0] = '%s_%06x' % (d[a][0], a)
    seen.add(d[a][0])
open(os.path.join(g, 'hand_%s.txt' % prog), 'w', encoding='utf-8', newline='\n').write(''.join('0x%08x func %s hand %s\n' % (a, v[0], v[1]) for a, v in sorted(d.items())))
print(prog, 'names', len(d), 'provisional', sum('provisional' in v[1] for v in d.values()))
