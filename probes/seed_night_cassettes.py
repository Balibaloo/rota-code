"""
Fill the night cassette from a night database's onboarding turns.

    python probes/seed_night_cassettes.py <night.db> <cassettes.db>

Frame 233, step 2. A night's `turns` table holds the system text, the user
text and the completion of every call, and `sessions.pins_json` holds the
rest of the key. So one night seeds the next night with no recording night
(plans/night-reuse-investigation.md, part 2.5). The night database opens
read-only. The cassette file is a required argument. A default under
`paths.RUNS` is the `.rota/` of the checkout that holds this script, and a
night worktree's `.rota/` is not the file the gauntlet reads (frame 233's
review 2, finding 2).

The onboarding sessions are the sessions before the first session that the
first sentence, `m_p1`, woke. Nights 145 and 146 both give 104 sessions
(observed: s105 is the first sentence's Liaison, 2026-10-14). A database
with no sentence is onboarding alone.

The seed takes the text protocol only. A run whose profile sets
`native_tools` is skipped whole. A session with an empty completion is
skipped too. A native reply carries its calls outside the text, and `turns`
keeps the text alone, so the replay would drop the calls.
"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from rota.llm.cassettes import key_for, mark_reason, open_dev_db  # noqa: E402
from rota.llm.llm import Pins  # noqa: E402

PIN_FIELDS = ("model", "temperature", "num_ctx", "prompt_hash", "max_tokens",
              "top_p", "seed", "repeat_penalty", "think")

# Both cut shapes of `run_session` open the turn's results block with this
# prefix, and the block stays in the later prompts. So a turn is cut when the
# next prompt holds one more copy than its own prompt. Night 146 gives five,
# the five sessions night 147 ran live (frame 233, pass 4). The runner writes
# no sign of `invented_result` or `repeating` into the next prompt, so the
# seed infers neither.
CUT_LINE = "ERROR reply cut:"


def _cut(turn, after) -> bool:
    return after is not None and after["user"].count(CUT_LINE) > turn["user"].count(CUT_LINE)


def _native_run(night: sqlite3.Connection) -> bool:
    row = night.execute("SELECT value FROM config WHERE key = 'profile'").fetchone()
    try:
        return bool(row and json.loads(row[0]).get("native_tools"))
    except (ValueError, AttributeError):
        return False


def _walk_start(night: sqlite3.Connection) -> int | None:
    row = night.execute("SELECT MIN(seq) FROM sessions WHERE trigger_msg = 'm_p1'").fetchone()
    return row[0] if row else None


def seed(night_path, cassette_path) -> dict:
    """Write each onboarding turn as a cassette row, and return the counts.
    A key already in the file keeps its row: a live recording is newer."""
    night = sqlite3.connect(f"file:{Path(night_path).as_posix()}?mode=ro", uri=True)
    night.row_factory = sqlite3.Row
    Path(cassette_path).parent.mkdir(parents=True, exist_ok=True)
    out = open_dev_db(cassette_path)
    counts = {"sessions": 0, "turns": 0, "present": 0, "notes": 0,
              "native": 0, "walk": 0, "cut": 0}
    native_run = _native_run(night)
    start = _walk_start(night)
    try:
        sessions = night.execute(
            "SELECT id, seq, pins_json, backend FROM sessions ORDER BY seq").fetchall()
        for s in sessions:
            if start is not None and s["seq"] >= start:
                counts["walk"] += 1
                continue
            turns = night.execute(
                "SELECT system, user, completion FROM turns WHERE session_id = ? "
                "ORDER BY seq", (s["id"],)).fetchall()
            # `db.session_note` writes the runner's account as a turn with an
            # empty system and user text. No model saw it, so it is no wake
            # (frame 233's review 2, finding 1: 61 in night 146's onboarding).
            notes = [t for t in turns if t["system"] == "" and t["user"] == ""]
            counts["notes"] += len(notes)
            turns = [t for t in turns if t not in notes]
            if not turns:
                continue
            if native_run or any(t["completion"] == "" for t in turns):
                counts["native"] += 1
                continue
            stored = json.loads(s["pins_json"] or "{}")
            pins = Pins(**{k: stored[k] for k in PIN_FIELDS if k in stored})
            # A replayed session reads `cassette:ollama`, and its row keeps `ollama`.
            backend = (s["backend"] or "").removeprefix("cassette:")
            added = 0
            for n, t in enumerate(turns):
                key = key_for(t["system"], t["user"], pins, "text")
                cur = out.execute(
                    "INSERT OR IGNORE INTO cassettes (key, model, temperature, num_ctx, "
                    "prompt_hash, system, user, completion, tool_calls, backend, hits) "
                    "VALUES (?,?,?,?,?,?,?,?,'[]',?,0)",
                    (key, pins.model, pins.temperature, pins.num_ctx, pins.prompt_hash,
                     t["system"], t["user"], t["completion"], backend))
                added += cur.rowcount
                counts["present"] += 1 - cur.rowcount
                if not _cut(t, turns[n + 1] if n + 1 < len(turns) else None):
                    continue
                if not cur.rowcount:
                    # Night 147's wrap ran before pass 4, so its live cut rows
                    # hold no reason. A present key gains one only when it
                    # stores this reply and no reason (frame 233, pass 4b).
                    # `mark_reason` leaves a row with a reason as it is.
                    row = out.execute("SELECT completion FROM cassettes WHERE key = ?",
                                      (key,)).fetchone()
                    if row[0] != t["completion"]:
                        continue
                counts["cut"] += mark_reason(out, key, "length")
            counts["turns"] += added
            counts["sessions"] += 1 if added else 0
    finally:
        night.close()
        out.close()
    return counts


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__.strip().splitlines()[2].strip())
        return 2
    src, dst = Path(argv[0]).resolve(), Path(argv[1]).resolve()
    c = seed(src, dst)
    print(f"from {src}")
    print(f"into {dst}")
    print(f"seeded {c['sessions']} sessions, {c['turns']} turns; "
          f"{c['present']} turns already present; skipped {c['native']} native "
          f"and {c['walk']} walk sessions and {c['notes']} note turns; "
          f"marked {c['cut']} turns cut")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
