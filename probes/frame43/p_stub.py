import sys
WT = "C:/Users/roman/rota_review43"
sys.path.insert(0, WT)
from rota.core import runner as R

budget = R._fit_budget(12288, 4000)
SIZE = {"A": 40000, "B": 40000, "C": 9000, "D": 9000}
SRC = {"A": True, "B": True, "C": False, "D": False}
NAME = {"A": "code.source", "B": "code.source", "C": "code.probe", "D": "code.area"}

already, answered, repeated = set(), {}, {}

def turn(n, wake, reply, batch):
    global already, answered, repeated
    room = min(R.TURN_RESULT_CHARS,
               max(budget - wake - reply - 6 - R._CUT_NOTE_CHARS, R._MIN_EXCHANGE))
    print("turn %d  result_room=%d" % (n, room))
    for k in batch:
        repeat = k in already
        cap = min(R.SOURCE_CHARS if SRC[k] else R.RESULT_CHARS,
                  max(room - R._CUT_NOTE_CHARS, 0))
        if cap >= R.MIN_RESULT_CHARS:
            shown = "X" * min(SIZE[k], cap)
            kind = "served %d" % len(shown)
        else:
            shown = ("ran, and this turn has no room left for its result "
                     "(%s characters of results already). Ask for it again in "
                     "your next turn, on its own" % format(min(R.TURN_RESULT_CHARS, budget), ","))
            kind = "WITHHELD (stub)"
        unchanged = repeat and answered.get(k) == shown
        already.add(k)
        answered[k] = shown
        if unchanged and repeated.get(k, 0) >= 1:
            print("   %s %-14s -> REFUSED as a repeat" % (k, NAME[k]))
            repeated[k] = repeated.get(k, 0) + 1
        elif unchanged:
            repeated[k] = repeated.get(k, 0) + 1
            print("   %s %-14s -> 'unchanged since you asked earlier this "
                  "session; the answer is above'   [%s]" % (k, NAME[k], kind))
        else:
            room = max(0, room - len(shown) - len(NAME[k]) - 7)
            print("   %s %-14s -> %-16s room left %d" % (k, NAME[k], kind, room))

for n in (1, 2, 3, 4):
    turn(n, 3000, 500, ["A", "B", "C", "D"])
