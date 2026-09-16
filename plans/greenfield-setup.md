# Greenfield setup — making a new project's floor dynamic (filed 2026-09-03, to be refined)

> Placed 2026-09-16 under `plans/composition.md`, The parties, "The project".
> The page has no line for a project with no code. Piece 1 changed the same
> day: the Principal approves the stack for an empty folder.
Status: a first enumeration, filed at Roman's request after the tips runs;
not yet ruled beyond "add it to the plan". Refine before building.

What exists today is the absolute bare bones, and it is hard-coded to one
stack: `scaffold.py` lays a *test* floor (`.gitignore`, `pyproject.toml` with
`testpaths = ["tests"]`, an empty `tests/`) in each batch worktree and commits
it; `harness.py` runs pytest with rota's own interpreter and venv; the import
allowlist in `api.py` keeps tests to pytest and the standard library. Nothing
scaffolds an entry point, so "no way to run it" is structural (the tips runs,
S0 3.29), and nothing provisions an environment (ENVIRONMENT.md: steps 1-4 of
`environments.py` built, the toolkit deliberately unbuilt, nothing calls the
spawner).

## The components

Each piece has an owner (single writer), an artefact, a door, and a
measurement (a register case and a cold walk). Only 2 and 11 exist.

| # | Component | What it does | Today | Owner |
|---|---|---|---|---|
| 1 | **Stack ruling** | From the account (`how_it_works`): language, runtime, package manager, test runner, program shape (script, library, service, web), run command | None; `frame` does this for an *existing* repo by reading the front | The Principal approves the stack on the intent page. The Architect drafts the guess at intent-time, the twin of what `deliver` got for the account |
| 2 | **Program floor** | The minimum tree for that stack: manifest, entry point with a `__main__`, README run line, `tests/` | Built, Python only, test floor only, no entry point | Machinery: `scaffold.py` as a registry keyed by the ruling |
| 3 | **Floor must run** | Smoke check before any behaviour: the run command executes on the empty floor; the runner finds zero tests cleanly | None | Machinery, in `do:harness` on the floor commit |
| 4 | **Test shape from the account** | Script -> subprocess with stdin/args; service -> start it and call it; library -> import | None; the encode door refuses constant asserts but offers no shape | A push to the Tester plus a door; S0 3.29 generalised |
| 5 | **Provisioner** | Per-batch environment: venv or node_modules, install from the manifest, before the harness runs | None; the harness runs rota's own interpreter | Machinery, `lifecycle.start` hook; `environments.py` steps 1-4 carry it |
| 6 | **Manifest-driven imports** | A dependency the Developer uses must be in the manifest or the door refuses; replaces the fixed stdlib allowlist | Fixed allowlist in `api.py` | Door on `code.write` and `tests.encode` |
| 7 | **Runner adapters** | pytest, npm test, cargo test, each parsed into the same `test_runs` rows | pytest only, hard-coded in `harness.py` | Machinery, keyed by the ruling |
| 8 | **Service environments** | `env.start`, `env.status`, `env.logs`; ports per batch; teardown on terminal states | Designed (ENVIRONMENT.md); spawn and teardown built; toolkit unbuilt by design | Machinery plus a role toolkit; the one piece that leaves something running, awaiting the seat's go |
| 9 | **Greenfield onboarding** | An empty folder skips surveys and goes straight to intent; git init and first commit | Partial: onboard runs, indexes nothing, binds constraint zero to nothing | Machinery plus Liaison intake |
| 10 | **Run contract as a criterion** | "Works as a script" is a criterion the harness can check, and the Critic reviews against it | None | Terminologist brief, Critic brief |
| 11 | **Stack on the page** | The ruling's guesses ride on the signoff page as assumptions with their cost | Built 2026-09-03 for ledger rows (A1) | Ledger, from piece 1 |
| 12 | **README from the account** | The account is the README's first paragraph plus the run line | None | Machinery, from `how_it_works` |

## Judgment versus translation

Pieces 1, the shape choice in 4, and 10 are judgment: briefs, measured on the
register. Everything else is translation from a ruling to files and commands:
machinery. The registry in piece 2 is the hinge -- once the floor is a template
keyed by a ruling instead of a constant, pieces 3, 5, 6, 7 and 12 read the
same key.

## Order

1, then 2 and 3 together (a ruled floor that provably runs), then 4 (the walk
finally delivers a runnable script), then 5 and 6 (real dependencies), then 7
(a second language proves the key is general), then 8 last. Each step is one
register case and one cold walk; the first four are what turns "tip calculator
pls" into a program a person can run.

CI, linting and formatting are the extension ring by ruling R2 and stay out.

## Open questions for the refinement

- Where the stack ruling lives: `frame_rulings` with provenance `decided`
  and the Principal as the author, written after the Principal approves the
  page. The Architect's guess is not a ruling. Check what the frame mode
  writes today before adding anything. Changed 2026-09-16: the composition
  page reserves `decided` for the Principal.
- Whether piece 9 needs an election ("this is a new project" said by the
  principal, or inferred from an empty tree).
- The second language to prove piece 7 with, and whether the Tester's encode
  door can be shaped per stack without a second door.

## Rulings and choices, 2026-09-12

- Dynamic stacks are core (Roman, 2026-09-12), for new projects and for
  existing repositories. Prose repositories get the desks' judgement
  without a mechanical net, and the tool says so on the page; checks on
  documents as a Tester floor were considered and skipped.
- Piece 0, before piece 1: **stack detection on an existing repository**,
  from its manifests. `pyproject.toml` or `setup.py` is Python and
  pytest; `package.json` is Node and `npm test`; `Cargo.toml` is Rust and
  `cargo test`; `go.mod` is Go and `go test`. No judgement: the manifest
  is the fact, and the ruling row it writes is `observed`. Piece 1's
  judged ruling is for the empty folder only.
- The second language is **JavaScript on Node**: installed on this
  machine (Windows and WSL), the most common manifest after Python's, and
  its test runner prints one line per test that piece 7 can parse. The
  sample repository is a small library with `package.json`, a `test`
  script, and one inherited test, built the way tipsI was.
- Build order stays. Piece 0 lands with piece 7's first adapter, since a
  detected stack with no runner adapter changes nothing. Both after click
  merges cold, as the completion doc orders.
