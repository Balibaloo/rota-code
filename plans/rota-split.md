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
one, for all 830 commits. Look a SHA up there before deciding a document is
wrong.

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

## What to check after cloning

1. Set `core.autocrlf` to `false`. The old repository set it locally, and a
   clone that does not inherit it will show line-ending churn on every file.
2. Put `tests/rota/cassettes.db` in place, or the L1 and L3 tiers record instead
   of replaying.
3. Run `python -m pytest tests/rota -q`.
