import random, sys
sys.path.insert(0, "C:/Users/roman/rota_review43")
from rota.core import runner as R

def total(ts):
    return sum(len(t) + 2 for t in ts)

random.seed(7)
bad_over, bad_dup, bad_neg, bad_lost = [], [], [], []
for trial in range(20000):
    n = random.choice([1, 2, 3, 4, 5, 6, 7, 8])
    budget = random.choice([2000, 3000, 6000, 12000, 20391, 24391])
    ts = []
    for i in range(n):
        size = random.choice([10, 500, 2000, 6000, 15000, 40000, 120000])
        ts.append(chr(97 + i % 26) * size)
    out = R._fit(list(ts), budget)
    wake_head = ts[0][:50]
    # the wake must appear once, at the front
    heads = [b for b in out if b.startswith(wake_head)]
    if out[0][:50] != wake_head:
        bad_lost.append((n, budget))
    if len(heads) > 1:
        bad_dup.append((n, budget, len(heads)))
    if "dropped to fit" in " ".join(out):
        import re
        m = re.search(r"\[(-?\d+) earlier", " ".join(out))
        if m and int(m.group(1)) <= 0:
            bad_neg.append((n, budget, m.group(1)))
    if n >= 3 and total(out) > budget:
        bad_over.append((n, budget, total(out), total(out) - budget))

print("wake lost/moved:", len(bad_lost), bad_lost[:3])
print("wake twice:", len(bad_dup), bad_dup[:3])
print("dropped <= 0:", len(bad_neg), bad_neg[:3])
print("over budget at n>=3:", len(bad_over))
if bad_over:
    worst = max(bad_over, key=lambda x: x[3])
    print("  worst overrun:", worst)
    from collections import Counter
    print("  by (n,budget):", Counter((a, b) for a, b, c, d in bad_over).most_common(8))

# one and two blocks, explicitly
for n in (1, 2):
    over = 0
    for budget in (2000, 6000, 20391, 24391):
        for size in (10, 2000, 6000, 40000, 120000):
            ts = [chr(97) * size] + [chr(98) * size for _ in range(n - 1)]
            out = R._fit(list(ts), budget)
            if total(out) > budget:
                over += 1
    print("n=%d over-budget combinations: %d of 20" % (n, over))
