"""
Talk to it.

    python -m rota.tools.talk --db run.db

Everything this needs already existed and nothing connected it. `ConsolePrincipal`
has been in `roles/principal.py` since the seam was written -- "the human, same
protocol, stdin instead of a script" -- wired to nothing, called by nothing, and
covered by no test. `loop.run` takes a `principal=` backend. The gap between a
system that can be talked to and one that cannot was this file.

What it does:

  * opens or creates a project database
  * takes your first sentence and puts it where the principal's words go: an
    entry in the transcript, and a `converse` to Liaison
  * turns the crank, printing each session as it lands
  * stops when the system is quiescent or when it has something to ask you

The asymmetry is the point and is worth seeing directly. You speak in sentences;
the roles answer each other in ids. Liaison is the only thing standing between
those two, which is why its briefs are the longest in the system.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

from .. import paths
from ..core import loop as loop_mod
from ..core.db import init_db
from ..core.runner import new_id
from ..llm import llm
from ..roles.principal import ConsolePrincipal


def open_with(conn: sqlite3.Connection, text: str) -> str:
    """
    The principal's first words, put where the system looks for them.

    Intake is a `converse` to Liaison whose transcript entry is the thing it
    refers to. Both, because the entry is the record -- Liaison segments
    statements out of it and every statement keeps a span back into it -- and
    the message is what wakes anybody.
    """
    # The entry's id is derived from the message's, and must be: `dispatch`
    # finds the entry to segment by looking up `f"e_{wake.message_id}"`. That
    # coupling is a naming convention rather than a foreign key, and nothing
    # declares it -- intake built with independent ids produced a Liaison that
    # read the sentence, called `brief.segment` four times, was refused "no
    # entry to segment against" every time, and committed a session that
    # reported ok while writing nothing.
    msg_id = new_id("m", conn)
    entry_id = f"e_{msg_id}"
    order = conn.execute(
        "SELECT COALESCE(MAX(ts_order), 0) + 1 n FROM entries").fetchone()["n"]
    conn.execute(
        "INSERT INTO entries (id, author, text, ts_order) VALUES (?,?,?,?)",
        (entry_id, "principal", text, order))

    seq = conn.execute(
        "SELECT COALESCE(MAX(seq), 0) + 1 n FROM messages").fetchone()["n"]
    conn.execute(
        "INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
        "body_refs, body_text, seq, status) "
        "VALUES (?,?,?,?,?,?,?,?,'open')",
        (msg_id, msg_id, "principal", "liaison", "converse",
         json.dumps([entry_id]), text, seq))
    conn.commit()
    return msg_id


def _announce(step) -> None:
    """
    One line per session, and the errors when there are any.

    `Step.__str__` already says who woke and whether it committed. The first
    version of this reached for `step.role` and `step.mode`, which do not
    exist, and printed a column of question marks over a session that was
    quietly refusing every write it made -- so the run looked like it worked.
    """
    print(f"  · {step}"[:150], flush=True)
    errors = getattr(step.outcome, "errors", None) if step.outcome else None
    for e in (errors or [])[:4]:
        print(f"      ! {str(e)[:120]}", flush=True)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Talk to rota.")
    ap.add_argument("--db", default="talk.db", help="project database")
    ap.add_argument("--model", default=llm.DEFAULT_MODEL)
    ap.add_argument("--max-steps", type=int, default=40,
                    help="a tripwire, not a quota")
    args = ap.parse_args(argv)

    path = Path(args.db)
    fresh = not path.exists()
    conn = init_db(path)

    print(f"rota — {args.model} — {path}{' (new)' if fresh else ''}")
    print("Say what you want built. Ctrl-C to stop.\n")

    try:
        opening = input("> ").strip()
    except (EOFError, KeyboardInterrupt):
        return 0
    if not opening:
        return 0

    open_with(conn, opening)

    pins = llm.Pins(model=args.model, temperature=0.0)
    try:
        trace = loop_mod.run(
            conn,
            backend=llm.OllamaBackend(),
            pins=pins,
            principal=ConsolePrincipal(),
            max_steps=args.max_steps,
            on_step=_announce,
        )
    except KeyboardInterrupt:
        print("\nstopped.")
        return 130

    print(f"\n{trace.render()}")
    return 0


if __name__ == "__main__":                                 # pragma: no cover
    sys.exit(main())
