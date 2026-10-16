# ckbase.py <file> [base...]: pointer histogram (64 KB buckets) + for each candidate base, how many
# aligned words point inside the file and how many of those land on an SH-2 prologue (2f e6 / 4f 22 / 2f 86 ...).
import struct, sys
from collections import Counter
f = open(sys.argv[1], 'rb').read()
n = len(f)
vals = [struct.unpack('>I', f[i:i + 4])[0] for i in range(0, n - 3, 4)]
c = Counter(v >> 16 for v in vals if 0x00100000 <= v < 0x06200000)
print(sys.argv[1], 'size', hex(n), 'top buckets', [(hex(k << 16), m) for k, m in c.most_common(10)])
pro = {b'\x2f\xe6', b'\x4f\x22', b'\x2f\x86', b'\x2f\xd6', b'\x2f\xc6', b'\xd3', }
for b in sys.argv[2:]:
    base = int(b, 16)
    inside = [v for v in vals if base <= v < base + n]
    hits = sum(1 for v in inside if f[v - base:v - base + 2] in pro or (v - base) % 2 == 0 and f[v - base:v - base + 1] == b'\xd3')
    print(' base', hex(base), 'inside', len(inside), 'prologue hits', hits, 'max ptr', hex(max(inside)) if inside else '-')
