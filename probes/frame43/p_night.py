"""
The four context numbers of a night, rebuilt from the night's database.

Frame 43 is measured against night 86. This probe is the query that produces
the baseline, so a later night can be compared on the same definitions.

Read-only. It opens the database with `mode=ro` and imports nothing from
`rota`.

Usage:
    python probes/frame43/p_night.py [path/to/night.db]

The default path is `.rota/clickI.db`.

The denominator: what 825 counts
--------------------------------
`turns` holds two kinds of row. A model turn carries the prompt that was sent
(`system` and `user` both set, `ms` above zero). A session note carries the
runner's account of the session and has `system = ''`, `user = ''` and
`ms = 0`, written by `session_note` at `rota/core/runner.py:2675`. Night 86
holds 937 rows: 825 model turns and 112 session notes. Night 85 holds 430
rows: 366 model turns and 64 session notes. Both denominators in the record
(825 and 366) are the model turns, so the filter is `user <> ''`.

Number 1: the middle eviction
-----------------------------
Site: `_dropped_note(dropped)` at `rota/core/runner.py:486`, called by `_fit`
at `rota/core/runner.py:627`. It replaces the evicted blocks with the line
"[N earlier exchange(s) dropped to fit the window. ...]".

Filter: a model turn whose `user` holds "earlier exchange(s) dropped to fit
the window.". The notice is one per prompt on night 86 (the maximum count in
any single prompt is 1), so a turn count and an occurrence count agree.

Denominator: the model turns.

Number 2: the wake-alone cut
----------------------------
Site: `_render_cut(transcript[0], wake_room)` at
`rota/core/runner.py:598`. `_render_cut` at `rota/core/runner.py:478` appends
"... the rest of your wake (N characters) did not fit the window. Ask for what
you need.".

Filter: a model turn whose `user` holds "did not fit the window. Ask for what
you need.".

One caution. `_render_cut` has a second caller at
`rota/core/runner.py:2029`, which cuts the seat's own over-long reply and
leaves the same words. The text filter cannot tell the two apart, so the probe
cross-checks by position: the wake cut leaves its notice at exactly
`wake_room`, which is two thirds of `_fit_budget(num_ctx, len(system))`, and
both values are on the row. Night 86: all 86 turns carry a notice at exactly
`wake_room`, plus one extra notice elsewhere. Night 85: 2 turns carry a
notice and neither is at `wake_room`, because night 85 ran on an earlier
budget. The cross-check line says how many of the counted turns are confirmed.

Denominator: the model turns.

Number 3: the sessions the server cut
-------------------------------------
Site: the `truncated` flag at `rota/llm/llm.py:416`, which is
`used >= num_ctx * 0.98 or estimate > num_ctx`, where `estimate` is
`int((len(system) + len(user)) / 3.97)` at `rota/llm/llm.py:415`. The runner
turns the flag into the line "prompt did not fit: ..." at
`rota/core/runner.py:1999`, appends it to `outcome.errors`, and
`session_note` writes it to a session-note row.

Filter: a session with at least one session-note row holding "prompt did not
fit:". Counted per session, not per line, which is what the record states.

Denominator: the rows of `sessions`.

The note is the only record of the cut, and it is lost when a session later
fails (`rota/core/runner.py:2826`). The count is therefore a floor. The
cross-check below rebuilds the `estimate > num_ctx` half of the flag from the
prompt rows, which no failure can erase.

Number 4: the tokens discarded
------------------------------
Definition: the prompt tokens the server never evaluated. Ollama collapses a
prompt over `num_ctx` to `num_ctx / 2 + 2` and keeps the tail (finding 79 in
`plans/operating-facts.md`), so the discarded part is the front, where the
brief is.

Filter: for every "prompt did not fit: A of about B tokens evaluated against a
C window" line, add B - A. A is `prompt_eval_count` as the server reported it.
B is `prompt_estimate`, the runner's own count of the prompt it sent.

Night 85 carries an older note, "prompt did not fit: A tokens evaluated
against a C window", with no B. The probe says so and falls back to the
reconstruction: for every model turn whose estimate exceeds `num_ctx`, add
estimate - (num_ctx // 2 + 2).
"""

from __future__ import annotations

import re
import sqlite3
import sys
from pathlib import Path

# `rota/llm/llm.py:415`: the measured ratio for these models.
CHARS_PER_TOKEN = 3.97
# `rota/llm/llm.py:416`: the near-window half of the `truncated` flag.
NEAR_WINDOW = 0.98

DROPPED = "earlier exchange(s) dropped to fit the window."
WAKE_CUT = "did not fit the window. Ask for what you need."
# `_render_cut` appends this after exactly `limit` characters of the block.
NOTICE_OPEN = "\n... the rest of your wake ("

NOTE_WITH_ESTIMATE = re.compile(
    r"prompt did not fit: (\d+) of about (\d+) tokens "
    r"evaluated against a (\d+) window")
NOTE_WITHOUT_ESTIMATE = re.compile(
    r"prompt did not fit: (\d+) tokens evaluated against a (\d+) window")


def estimate_tokens(system: str, user: str) -> int:
    """`prompt_estimate`, as `rota/llm/llm.py:415` computes it."""
    return int((len(system) + len(user)) / CHARS_PER_TOKEN)


def wake_room(num_ctx: int, system_chars: int) -> int:
    """
    The characters `_fit` leaves the wake, and so the offset of the wake cut's
    notice. `_fit_budget` is at `rota/core/runner.py:566` and the two thirds
    are at `rota/core/runner.py:596`.
    """
    budget = max(2000, int(num_ctx / 2 * CHARS_PER_TOKEN) - system_chars)
    return (budget * 2) // 3


def measure(path: Path) -> dict:
    conn = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT t.session_id, t.seq, t.system, t.user, t.completion, t.ms,"
            "       s.num_ctx "
            "FROM turns t JOIN sessions s ON s.id = t.session_id "
            "ORDER BY t.session_id, t.seq").fetchall()
        sessions = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
    finally:
        conn.close()

    model_turns = [r for r in rows if r["user"] != ""]
    notes = [r for r in rows if r["user"] == ""]

    evicted = sum(1 for r in model_turns if DROPPED in r["user"])
    wake_cut = sum(1 for r in model_turns if WAKE_CUT in r["user"])

    # Confirm each counted turn by position. The wake cut leaves its notice at
    # exactly `wake_room`; any other offset is `_render_cut` on a reply.
    confirmed = 0
    unplaced = 0
    for r in model_turns:
        if WAKE_CUT not in r["user"]:
            continue
        room = wake_room(r["num_ctx"] or 0, len(r["system"]))
        offsets = [m.start() for m in re.finditer(re.escape(NOTICE_OPEN),
                                                  r["user"])]
        if room in offsets:
            confirmed += 1
        unplaced += sum(1 for o in offsets if o != room)

    cut_sessions: set[str] = set()
    cut_lines = 0
    discarded = 0
    old_format_lines = 0
    for r in notes:
        text = r["completion"] or ""
        if "prompt did not fit:" not in text:
            continue
        cut_sessions.add(r["session_id"])
        with_estimate = NOTE_WITH_ESTIMATE.findall(text)
        for used, whole, _window in with_estimate:
            discarded += int(whole) - int(used)
            cut_lines += 1
        if not with_estimate:
            old_format_lines += len(NOTE_WITHOUT_ESTIMATE.findall(text))

    # The cross-check. `estimate > num_ctx` is the half of the `truncated`
    # flag that the prompt rows still hold, whatever happened to the note.
    over_turns = []
    for r in model_turns:
        window = r["num_ctx"] or 0
        est = estimate_tokens(r["system"], r["user"])
        if window and est > window:
            over_turns.append((r["session_id"], r["seq"], est, window))
    rebuilt_discarded = sum(est - (window // 2 + 2)
                            for _, _, est, window in over_turns)

    return {
        "rows": len(rows),
        "model_turns": len(model_turns),
        "notes": len(notes),
        "sessions": sessions,
        "evicted": evicted,
        "wake_cut": wake_cut,
        "wake_cut_confirmed": confirmed,
        "notices_elsewhere": unplaced,
        "cut_sessions": len(cut_sessions),
        "cut_lines": cut_lines,
        "old_format_lines": old_format_lines,
        "discarded": discarded,
        "over_turns": len(over_turns),
        "over_sessions": len({s for s, _, _, _ in over_turns}),
        "rebuilt_discarded": rebuilt_discarded,
    }


def report(path: Path, m: dict) -> None:
    print(f"night database: {path}")
    print(f"  {m['rows']} turns rows = {m['model_turns']} model turns "
          f"+ {m['notes']} session notes")
    print(f"  {m['sessions']} sessions")
    print()
    print(f"1. middle evicted      {m['evicted']:>7} of {m['model_turns']} turns")
    print(f"2. wake itself cut     {m['wake_cut']:>7} of {m['model_turns']} turns")
    print(f"3. cut by the server   {m['cut_sessions']:>7} of {m['sessions']} sessions")
    if m["old_format_lines"]:
        print(f"4. tokens discarded    {'unrecorded':>7} "
              f"({m['old_format_lines']} notes carry the old format, "
              f"which omits the prompt estimate)")
    else:
        print(f"4. tokens discarded    {m['discarded']:>7} over "
              f"{m['cut_lines']} cut turns")
    print()
    print("cross-check, rebuilt from the prompt rows:")
    print(f"  turns whose prompt estimate exceeds num_ctx: {m['over_turns']}, "
          f"in {m['over_sessions']} sessions")
    print(f"  tokens discarded on those turns: {m['rebuilt_discarded']}")
    print(f"  wake cuts confirmed at wake_room: "
          f"{m['wake_cut_confirmed']} of {m['wake_cut']}")
    if m["notices_elsewhere"]:
        print(f"  cut notices at another offset, so from a reply and not the "
              f"wake: {m['notices_elsewhere']}")


def main(argv: list[str]) -> int:
    path = Path(argv[1] if len(argv) > 1 else ".rota/clickI.db")
    if not path.exists():
        print(f"no such database: {path}", file=sys.stderr)
        return 1
    report(path, measure(path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
