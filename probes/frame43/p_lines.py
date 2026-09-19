import sys, types
WT = "C:/Users/roman/rota_review43"
sys.path.insert(0, WT)
from rota.core import runner as R

class C:
    def __init__(s, name, pos=(), args=None, raw=""):
        s.name, s.pos, s.args, s.raw = name, pos, args or {}, raw
why = ("asked three times this session and the answer "
       "has not changed; not answered again")
for call in (C("surveys.consult", (), {"area": "src/click"}),
             C("code.source", (), {"path": "src/click/termui.py", "start": 0, "end": 400}),
             C("glossary.lookup", (), {"term": "template"})):
    tag = R._call_tag(call, 331)
    new = f"ERROR {tag}: {why}. Use the answer above, or finish without it."
    old = f"OK {call.name} -> unchanged since you asked earlier this session; the answer is above."
    print("%-16s new=%3d old=%3d  x327 -> new %6d old %6d"
          % (call.name, len(new), len(old), len(new) * 327, len(old) * 327))
print()
print("fixtures parse of the error string:")
for err in ("repeat refused: code.source " + why, "code.source: boom"):
    fn = err.split(":", 1)[0].strip()
    print("   %-40s -> fn=%-18r counted=%s" % (err[:40], fn, "." in fn))
