import sys
sys.path.insert(0, "C:/Users/roman/rota_review43")
from rota.core import runner as R

def room(budget, wake, completion):
    return min(R.TURN_RESULT_CHARS,
               max(budget - wake - completion - 6 - R._CUT_NOTE_CHARS, R._MIN_EXCHANGE))

def cap(result_room, is_source):
    return min(R.SOURCE_CHARS if is_source else R.RESULT_CHARS,
               max(result_room - R._CUT_NOTE_CHARS, 0))

print("TURN_RESULT_CHARS", R.TURN_RESULT_CHARS, "MIN_RESULT_CHARS", R.MIN_RESULT_CHARS)
for num_ctx, system in ((12288, 4000), (12288, 6000), (16384, 4000), (16384, 6000)):
    b = R._fit_budget(num_ctx, system)
    # the largest wake+completion that still lets a whole 14000 source read through
    thresh = b - 14000 - R._CUT_NOTE_CHARS - 6 - R._CUT_NOTE_CHARS
    print("num_ctx=%d system=%d budget=%d  whole SOURCE_CHARS needs wake+reply <= %d"
          % (num_ctx, system, b, thresh))

print()
b = R._fit_budget(12288, 4000)
for wake, comp in ((3000, 500), (6000, 500), (6000, 2000), (10000, 1500), (13594, 1000)):
    r = room(b, wake, comp)
    print("budget=%d wake=%5d reply=%5d -> result_room=%6d  source cap=%6d (whole? %s)"
          % (b, wake, comp, r, cap(r, True), cap(r, True) >= R.SOURCE_CHARS))

print()
print("-- claim: probe(2200) then source, at a generous budget --")
r = room(100000, 3000, 500)
print("room", r)
r2 = max(0, r - 2200 - len("code.probe") - 7)
print("after probe, room", r2, "source cap", cap(r2, True))
print()
print("-- claim: two source reads --")
r = room(100000, 3000, 500)
c1 = cap(r, True); r2 = max(0, r - c1 - len("code.source") - 7)
c2 = cap(r2, True); r3 = max(0, r2 - c2 - len("code.source") - 7)
print("first cap", c1, "-> room", r2, "second cap", c2, "-> room", r3)
c3 = cap(r3, False)
print("third call cap", c3, "withheld?" , c3 < R.MIN_RESULT_CHARS)
print()
print("-- four results: when does the stub appear, and can it repeat? --")
r = room(100000, 3000, 500)
shown = []
for i, (name, is_src, size) in enumerate(
        [("code.source", True, 40000), ("code.source", True, 40000),
         ("code.probe", False, 9000), ("code.area", False, 9000)]):
    c = cap(r, is_src)
    if c >= R.MIN_RESULT_CHARS:
        s = "X" * min(size, c)
    else:
        s = ("ran, and this turn has no room left for its result (%s characters "
             "of results already). Ask for it again in your next turn, on its own"
             % format(min(R.TURN_RESULT_CHARS, 100000), ","))
        print("  call %d %s -> STUB" % (i + 1, name))
    shown.append(s)
    r = max(0, r - len(s) - len(name) - 7)
    print("  call %d %-12s cap=%6d shown=%6d room left=%6d" % (i + 1, name, c, len(s), r))
print("  call 3 stub == call 4 stub:", shown[2] == shown[3])
