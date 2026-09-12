# A second agent beside the core work

Written 2026-09-12 for a second chat session. The first session works on
core: the briefs, the doors, the register, the gauntlet, the GPUs. This
brief is for a second agent working on the rest at the same time. Read
`CLAUDE.md` first (Simplified Technical English, commit format), then
`rota/COMPLETION.md` ("Core, by capability" and "The plan").

## What the second agent owns

- **A stranger's install.** `pip install` of the wheel on a clean machine,
  `rota --help`, the first run with no profile, the model setup screen
  (alt+m) from nothing to a written profile. Every rough edge is a fix
  in `rota/cli.py`, `rota/cockpit/`, `rota/llm/setup.py`,
  `rota/llm/discover.py`, or the README. Test under WSL as the stranger.
- **Documentation for a person.** `rota/README.md`, the operator loop,
  what a page means, what "stuck" means and what to type. Nothing that
  restates the briefs.
- **The cockpit and the TUI.** Usability of the seat as a screen: the
  page, the reply box, the run state. Not the reply layer's logic.
- **Packaging and the test floor.** The root `conftest.py`, the WSL
  checkout, CI-shaped scripts if any. The `probes/` drivers' portability.
- **The second Ollama and the profiles as files.** `probes/titan_ollama.ps1`,
  the shipped profiles' comments, `rota profile check`.

## What the second agent never touches

- `rota/roles/prompts/**` (the briefs and tools lists).
- `rota/roles/api.py`, `rota/core/sandbox.py`, `rota/core/predicates.py`,
  `rota/core/scheduler.py`, `rota/core/runner.py`, `rota/core/lifecycle.py`,
  `rota/roles/principal.py`, `rota/llm/toolproto.py`, `rota/llm/_lenient.py`.
- `tests/rota/cassettes.db`, `tests/rota/cases/**`, `tests/rota/walks.jsonl`.
- The GPUs: no `ROTA_L1=1`, no walks, no `rota run` on a sample
  repository. Both cards are the first session's.
- `rota/COMPLETION.md` and `rota/DECISIONS.md`: the first session writes
  them. Send findings as a note in `plans/second-seat-log.md`.

## How to work

- Branch `rota/seat2` off `rota/foundation`, in its own git worktree, so
  no half-written file is swept into the other session's commit
  (`git worktree add ../Custom_AI_TUI-seat2 -b rota/seat2`).
- Commit by explicit path. Never push. Never amend the other branch.
- The first session merges `rota/seat2` into `rota/foundation` at quiet
  moments and runs the suite then.
- A test the second agent adds lives beside the code it tests and runs
  without a model (no cassette).
- When a fix seems to need a brief, a door, or a case, stop and write it
  in the log instead: those are the first session's, and they are
  measured before they land.
