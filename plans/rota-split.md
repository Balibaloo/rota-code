# The split: rota out of Custom_AI_TUI

rota grew inside `Custom_AI_TUI`, a Textual chat application. On 2026-09-14 the
rota work moved to its own repository at `Balibaloo/rota-code`. This document
records what moved, what did not, and what a reader must know to follow a SHA
quoted in an older document.

## Where the history starts

The root commit is `docs(design): amend HANDOFF and TESTS after implementation
challenges`, which was `e1281f5` in the old repository. That commit added
`rota_tui/HANDOFF.md`, `rota_tui/TESTS.md` and `rota_tui/team-graph.html`. Those
three files are rota's design documents, and the graph extractor still reads the
third one. Nothing before that commit is rota.

The directory name `rota_tui` stopped meaning anything once there was no TUI
beside it, so the three files were filed with the other documents: `HANDOFF.md`
and `TESTS.md` at the top of the package, and `team-graph.html` in
`rota/design/`, next to the JSON that is extracted from it.

`git replace --graft` made the commit parentless, and `git filter-repo` made the
graft permanent. 828 commits followed it. 802 survived the path filter. The 26
that went were commits whose whole content was a file this repository does not
keep.

Two branches came across: `rota/foundation` and `rota/seat2`. Every other branch
in the old repository was the chat application, or a backup of a history rewrite.

## Every SHA changed

A path filter rewrites every commit, so no SHA quoted in `COMPLETION.md`,
`DECISIONS.md`, the wake audit or any older plan resolves here.

`plans/archive/commit-map-rota-split-20260914.tsv` maps the old SHA to the new
one, for every commit, including the ones carried across after the split. Look
a SHA up there before deciding a document is wrong.

## What did not come across

**The chat application.** `src/`, `main.py`, `main_reverse_engineered.py`,
`.architect/`, `active_sessions/`, and the 30 test files under `tests/` that
drove the old TUI.

rota had reached into it three times, always for a widget, always through a
`sys.path` insert to the repository root:

  * `ChatMessage`, from `src/ui/widgets.py`, is now `rota/cockpit/widgets.py`.
  * `ConfirmationModal` and `InputModal`, from `src/ui/modals.py`, are now
    `rota/cockpit/modals.py`.

The two helpers `ChatMessage` needs, `_PreRenderedMarkdown` and
`_preprocess_thought_blocks`, came with it. The cockpit already carried the CSS
for both modal containers, so nothing about the appearance changed.

**The old TUI's plans.** Eight documents under `plans/archive/` described the
chat application and were filtered out of the history. One stayed:
`plans/archive/system-prompt-fixer.md`, because `rota/tools/vocabulary.py` names
it as the source of its method.

**The cassette database.** See below.

## The cassettes are no longer tracked

`tests/rota/cassettes.db` is about 590 MB, and a recording session writes a new
version most days. The old repository held 153 versions of it in Git LFS, which
came to 57 GB. GitHub gives 1 GB of LFS storage on the free tier.

The file is now gitignored. This repository has no LFS objects at all and packs
to about 3 MB. `rota/README.md` says where to put the file.

**The old repository is the only place the recording history exists.** Keep
`D:\repos\_AI\Custom_AI_TUI` and its `.git/lfs` until you are sure no earlier
recording is ever needed again.

## What stayed behind, and must not be lost

Several sessions shared the old checkout. At the time of the split it held three
things this repository does not:

  * `stash@{0}`, "Stop gate" of 2026-08-30, over `rota/core/runner.py`,
    `rota/roles/api.py`, `tests/rota/test_runner.py` and
    `tests/rota/test_t0_sandbox.py`. Later commits supersede it. It was not
    carried.
  * The `rota/seat2` worktree. It was empty and clean. The branch came across.
    Recreate the worktree here.
  * A re-record of 28 stale register cases, and the Titan walk `tipsBH`. Both
    were running when the split was taken. Each writes a database that Git does
    not track, so each had to be copied across by hand when it finished.

## What to check after cloning

1. Do nothing about line endings. `.gitattributes` enforces LF whatever
   `core.autocrlf` says. `CONTRIBUTING.md` has the measurement.
2. Put `tests/rota/cassettes.db` in place, or the L1 and L3 tiers record instead
   of replaying. `rota cassettes pull` fetches the published one.
3. Run `python -m pytest tests/rota -q`.

## Moving the working checkout

Do these steps in order. `<new>` is the path Roman chooses.

**Warning: a model run must not have its checkout moved while it is running.**
Wait for every walk and every re-record to finish first.

1. Confirm no walk and no re-record is running. Ask each session that shares
   `D:\repos\_AI\Custom_AI_TUI`, and check `.rota/` for a database written in
   the last few minutes.
2. Rename `D:\repos\rota-split` to `<new>`.
3. Copy the untracked local state from the old checkout: `.env`, `.rota\`,
   `.rota-coverage.json`, `.rota-timings.json`, `.vscode\` and
   `.claude\settings.local.json`.
4. Copy `.venv`, or build a new one with `pip install -r requirements.txt`.
   A copied virtual environment keeps absolute paths in `Scripts\`, so rebuild
   it if anything in it misbehaves.
5. Copy `tests/rota/cassettes.db` again if a re-record has finished since the
   last copy, with SQLite's backup API and not `cp` (`CONTRIBUTING.md` says
   why). The file is the only copy of that work.
6. Run `python -m pytest tests/rota -q` in `<new>` before trusting it.
7. Recreate the second seat: `git worktree add <new>-seat2 rota/seat2`.
8. Leave `D:\repos\_AI\Custom_AI_TUI` where it is. It holds the only copy of
   the 57 GB recording history, and about a hundred worktrees still point into
   it.
