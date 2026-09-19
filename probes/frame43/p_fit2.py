import random, sys
sys.path.insert(0, "C:/Users/roman/rota_review43")
from rota.core import runner as R
tot = lambda ts: sum(len(t) + 2 for t in ts)
random.seed(11)
worst = {}
for trial in range(40000):
    n = random.randint(1, 9)
    budget = random.choice([6000, 9000, 12000, 20391, 24391, 32000])
    ts = [chr(97 + i % 26) * random.choice([1, 50, 800, 2100, 6000, 14000, 30000, 120000])
          for i in range(n)]
    out = R._fit(list(ts), budget)
    over = tot(out) - budget
    if over > worst.get(n, (-10**9,))[0]:
        worst[n] = (over, budget, [len(t) for t in ts])
for n in sorted(worst):
    print("n=%d worst overrun %+d  budget=%d sizes=%s" % (n, worst[n][0], worst[n][1], worst[n][2]))
# the smallest budget _fit_budget can hand out in practice
print("fit_budget(12288, 4000) =", R._fit_budget(12288, 4000))
print("fit_budget(12288, 22400) =", R._fit_budget(12288, 22400))
print("MIN_EXCHANGE", R._MIN_EXCHANGE)
