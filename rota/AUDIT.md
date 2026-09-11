# What rota executes, and what it trusts

Written 2026-09-10, goal 7 of the plan. One list. Each item says where
the execution or the trust happens, what could go wrong, what stands
today, and the door owed. Not a sandbox and not a claim of one. The
harness runs the target project's own code by design, the same as pytest
or pip on a cloned repository. The list is what a careful person needs to
know before they point rota at a repository they did not write.

| # | What runs or is trusted | Where | Today | Door owed |
|---|---|---|---|---|
| 1 | pip installs the project's declared dependencies into the batch venv, then the project itself, editable, when it is a package. Every package's setup and the project's build backend run. | `core/provision.py` `ensure_env` | The manifest is the repository's. A model-written manifest is refused unless a criterion names a dependency (`core/fence.py` `check_manifest`). | None. |
| 2 | pytest imports and runs the repository's tests, the model-written tests and the model-written code, with the user's rights. | `core/harness.py` `_run_one` | 120 s timeout per file. The fence refuses model-written reaches: network, process, removal, outside path, dynamic code. The repository's own tests are not fenced: they are the repository. The seam is in: `core/execute.py` `run(worktree, argv)`, `local` by default, chosen by the `runner` setting. | A container or WSL runner registered under its own name. |
| 3 | git runs on the checkout: index, worktree, add, commit, merge. A checkout's hooks run on commit and merge. | `core/worktrees.py`, `onboarding/boot.py`, `onboarding/indexer.py`, `roles/api.py` | Every git command rota runs carries `core.hooksPath` set to a directory that does not exist, so no hook runs (`worktrees.GIT`). | None. |
| 4 | Model-written files land in the batch's worktree. | `roles/api.py` `code.write` | Inside the worktree only (`_within`, `_batch_worktree`). The fence. The entry point keeps its guard. No test files from the Developer. | None. |
| 5 | Model-written tests land in the batch and the harness runs them. | `roles/api.py` `tests.encode` | The fence. Python only. | None. |
| 6 | The repository's own text reaches the model: README, source, manifests. A repository can carry words meant for a model. | `roles/api.py`: `code.prose`, `code.source`, `code.survey` | Nothing filters it. The backstop is the fence: whatever the words persuade the model to write, the write still reaches only what the criteria name. | None that is a fact. Read the repository before you onboard it. |
| 7 | The cockpit serves the run's database over HTTP. | `cockpit/server.py` | Binds `127.0.0.1` only. Reads only, plus layout saves. | None. |
| 8 | A run profile names the model and the endpoint the prompts go to. A project can ship one under `.rota/profiles/`. | `llm/profile.py` `places` | The project's profile is read first. `rota profile show` prints its endpoint. | `rota onboard` says which profile it froze and the endpoint it points at, in words, before the first session. Owed. |
| 9 | Prompts carry the repository's code and the principal's words to the model endpoint. | `llm/llm.py` | Local Ollama by default. A hosted endpoint sends the code out. | The same line at onboard as item 8. |

What is not on the list, and why: the scheduler, the predicates and the
doors run rota's own code on rota's own database. The transcript holds the
principal's words verbatim and nothing executes them.
