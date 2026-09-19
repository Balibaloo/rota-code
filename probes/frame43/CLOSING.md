# Frame 43: the closing sequence

Session 9a9a20bf (rota-95). Written while the gate ran on pass 6.

## 1. Commit the window rise

The gate must be read whole, never piped. Five lines.

```
PATH="/d/repos/rota/.venv/Scripts:$PATH" VIRTUAL_ENV="D:\repos\rota\.venv" \
  ROTA_MODEL=qwen3:8b python -m rota.tools.gate
```

## 2. The diff review, on a worktree at the closing commit

```
git worktree add C:/Users/roman/rota_review43b <closing-commit> --detach
# ... the review runs read-only there ...
git worktree remove C:/Users/roman/rota_review43b
```

The earlier review's worktree, `C:/Users/roman/rota_review43`, is already
removed. Four worktrees of dead sessions remain under the Temp directories of
sessions 3b4093c6 and 75d12c2b. They are not this frame's.

## 3. The night, from a worktree at the closing commit

Night 87. The baseline is night 86.

```
git worktree add C:/Users/roman/rota_night87 <closing-commit> --detach
ROTA_REPO=C:/Users/roman/rota_night87 \
ROTA_RUNS=D:/repos/rota/.rota \
GAUNTLET_NIGHT=87 \
PATH="/d/repos/rota/.venv/Scripts:$PATH" VIRTUAL_ENV="D:\repos\rota\.venv" \
  bash C:/Users/roman/rota_night87/probes/gauntlet_click.sh
```

Five facts about that command, each checked by this session.

1. `import rota` resolves from the working directory. The venv holds no rota
   and no path file, so the worktree's code runs.
2. `ROTA_RUNS` points at the main checkout on purpose. The night's database is
   the evidence for the frame, and a worktree's `.rota` dies with the worktree.
   Nights 82 to 84 survived only as copies in a killed session's temporary
   directory.
3. Do not set `GAUNTLET_WARM`. The warm snapshot of 2026-09-17 is behind the
   `ledger-kind` schema mark, so a warm night stops at the door. This frame
   needs a full night anyway.
4. The night onboards with `--profile local`, which is the profile this pass
   raises to 16384.
5. A night ends at the `GAUNTLET-DONE` line, never at Stuck. Wait for that
   line or kill the night before the next one starts.

Before the launch: `curl` both `/api/tags`. Both answered at 12:43.
The sample repository is clean at its base commit `2c8cd3a`.

## 4. Check the monitor early, not at the end

`note_spill` sits behind a broad `except Exception` in `loop.step`, so a
failure there is silent by design. Confirm the row exists after the first
sessions instead of trusting it at the end:

```
python -c "import sqlite3,json; c=sqlite3.connect('file:.rota/clickI.db?mode=ro',uri=True); \
print([r[0] for r in c.execute(\"select value from config where key='spill_seen'\")])"
```

`probes/walk.py` also prints `CARD FITS`, `CARD SPILLS` or `CARD UNSEEN` when
the reading changes.

## 5. Copy the night's database at once

```
python -c "import sqlite3; sqlite3.connect('.rota/clickI.db').backup(sqlite3.connect('.rota/clickI_night87.db'))"
```

The script keeps one generation only. The launch after next destroys it.

## 6. Measure the four numbers

```
python probes/frame43/p_night.py .rota/clickI_night87.db
```

Night 86's baseline, and the correction this session made to it:

| number | night 86 as recorded | night 86 corrected |
| --- | ---: | ---: |
| middle evicted | 297 of 825 turns | unchanged |
| wake itself cut | 86 of 825 turns | unchanged |
| sessions cut by the server | 15 of 203 | **14**, s168 fired the 98 per cent clause on a prompt that fit |
| tokens discarded | 179117 | **179267** over the 14 real cuts |

Read both the note count and the reconstruction. At 16384 the false-positive
clause fires at 16056 used tokens.

The prediction to hold the night against: twelve of night 86's fifteen cut
prompts are above 16384 tokens, so the window rise alone clears two of the
fourteen. A night that shows zero cuts shows the four repairs working. If a
cut survives, read s71 at 27155 tokens and s17 at 26007 first.

## 7. One limit to state in the closing status

The spill warning is verified by the TUI driver test, not by a person looking
at the screen. Roman sees it with `rota tui` or `alt+b` on a run whose card
spills.
