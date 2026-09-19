import random, sys
sys.path.insert(0, "C:/Users/roman/rota_review43")
from rota.core import runner as R
tot = lambda ts: sum(len(t) + 2 for t in ts)
random.seed(3)
worst = -10**9; case = None
for trial in range(60000):
    n = random.choice([1, 3, 5, 7, 9, 11])
    budget = random.choice([16000, 20391, 24391, 27000])
    ts = [chr(97 + i % 26) * random.choice([1, 50, 800, 2100, 6000, 14000, 20000, 30000, 120000])
          for i in range(n)]
    out = R._fit(list(ts), budget)
    o = tot(out) - budget
    if o > worst:
        worst, case = o, (n, budget, [len(t) for t in ts])
print("worst overrun at realistic budgets:", worst, case)

# the smallest budget at which the floor can bind
for b in range(5900, 6600, 20):
    ts = ["a" * 120000, "b" * 6000, "c" * 2100]
    out = R._fit(list(ts), b)
    if tot(out) > b:
        print("floor binds up to budget", b, "overrun", tot(out) - b)
