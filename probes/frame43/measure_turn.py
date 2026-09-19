"""What the two-source-read turn actually renders, so the test asserts facts."""
import pathlib
import sys
import tempfile

from rota.core.db import init_db
from rota.core.runner import TURN_RESULT_CHARS, run_session
from rota.core.scheduler import Wake
from rota.llm.llm import Pins, ScriptedBackend

tmp = pathlib.Path(tempfile.mkdtemp())
db = init_db(tmp / "rota.db")
db.execute("INSERT INTO entries (id, author, text, ts_order) "
           "VALUES ('u1','principal','x',1)")
db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
           "VALUES ('i1','delete an account','in_scope','approved',1,1)")
root = tmp / "wt"
(root / "src").mkdir(parents=True)
db.execute("INSERT INTO batches (id, item_id, status, worktree) "
           "VALUES ('b1','i1','running',?)", (str(root),))
db.commit()
(root / "src" / "big.py").write_text(
    "".join(f"VALUE_{i:04d} = {'x' * 48!r}\n" for i in range(900)))

reply = ("TOOL: code.source(path='src/big.py', start=0, end=400)\n"
         "TOOL: code.source(path='src/big.py', start=400, end=800)")
backend = ScriptedBackend([reply, "Done."])
out = run_session(db, Wake(role="developer", kind="tick:batch_start", refs=("b1",)),
                  backend=backend, pins=Pins(model="scripted"), batch_id="b1")
from rota.core.runner import _fit_budget
sys0, user0 = backend.calls[0]
print("budget", _fit_budget(12288, len(sys0)), "system", len(sys0),
      "wake", len(user0), "reply", len(reply))
prompt = backend.calls[1][1]
block = prompt.split(reply)[-1]
print("committed", out.committed, out.errors[:2])
print("TURN_RESULT_CHARS", TURN_RESULT_CHARS)
print("feedback block", len(block))
print("TRUNCATED count", block.count("TRUNCATED"))
print("VALUE_ count", block.count("VALUE_"))
print("has VALUE_0400", "VALUE_0400" in block, "has VALUE_0000", "VALUE_0000" in block)
for line in block.splitlines():
    if "TRUNCATED" in line:
        print("  note:", line[:200])
for i, part in enumerate(block.split("OK code.source -> ")):
    print("part", i, "len", len(part), "VALUE lines", part.count("VALUE_"),
          "tail:", repr(part[-120:]))
