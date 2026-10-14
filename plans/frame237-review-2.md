# Frame 237, pass 1b: the last diff review of the list-under-a-name account

Review of a1ffe54d over 478163c0 on the worktree `C:/Users/roman/rota_rv237b`.
Rota workflow: the runner's account and nudges. Reviewer: Opus, read-only.
Date: 2026-10-14.

## Verdict

Accept. Pass 1b closes review 1's high 1, and the nudge routes carry the note on the night's shape.
One low finding stays open. It can go to a later frame and does not block the walk.

## (a) The points

1. Review 1's high 1: closed. The bullet call names nothing, `1. glossary.amend(...)` names `glossary.amend`, and s187's turn 1 names `glossary.amend` and `code.source`.
2. The three routes: the night's shape reaches the seat. One shape reaches no route: a list with no call after a landed write and with no intent words (finding 1).
3. The name filter: `allowed` holds the seven survey calls on a `tick:survey` wake. A `surveys.attest` heading over files names `surveys.attest`.
4. STE: the note text and the comments pass. Both files hold 0 `\r` bytes.

## Point 1

The probe ran `extract_lenient` with the test's survey calls, then `listed_not_called` with the parsed names.
"- `glossary.amend(term="a", sense_body="b", sense_short="c")`" under the heading parses to `{glossary.amend}`. The function names nothing.
"1. glossary.amend(...)" parses to no call. The function names `glossary.amend`.
s187's turn 1, read from `clickI_night147.db`, is byte-equal to the fixture `S187_TURN1`. The function names `glossary.amend` and `code.source`.
Inside a real `run_session`, the spy saw the same empty `called` set for s187, with `_param_sets` signatures. (observed: probe P1 and P2, 2026-10-14)

## Point 2

The note reaches the seat by three routes. The intent route fires on a reply with no call and an INTENT phrase. The no-op route fires on a `tick:` wake with no call, no writes and no outbound. The feedback route fires on a reply with at least one call.
The probe drove `run_session` with `ScriptedBackend` on a survey wake:

- s187's turn 1: the no-op route. Turn 2 holds the note for both names and the old no-op text.
- "I will record these words." over a list: the intent route. Turn 2 holds the note and the old intent text.
- The list twice: turn 2 holds the note. The second list ends the session, because `noop_warned` is set. That is the told-once design.
- `code.source`, a landed `glossary.amend`, then the list: no route fires. The session ends after the list turn, and the seat never reads the note (finding 1).

With no note, the texts are byte-equal. `"\n".join([] + [s])` returns `s`, and `list([])` is `[]`. The probe checked the turn-2 user text on a plain intent reply and a plain no-op reply. Each ends with the old literal after `"\n\n"`, as at the parent. (observed: probe P2, 2026-10-14)
The cut route (`cut_note and not calls`) also carries no note. A cut reply is rare on a list, so the report does not count it as a finding.

## Point 3

The spy recorded `allowed` at the hook on a `tick:survey` wake: `code.area`, `code.source`, `glossary.amend`, `glossary.consult`, `problem.baseline`, `surveys.attest`, `surveys.consult`. This is the mode's set, and it equals the test's `SURVEY_CALLS`.
"`surveys.attest`:" over two file paths parses to no call, and the function names `surveys.attest`. The note then says "Write each call on its own line: `TOOL: surveys.attest(...)`". The sentence is correct for one attest call.
A heading for `foo.bar` names nothing, as the commit's test shows.

## Point 4

The note text uses short sentences in the active voice. The new comments and the docstring pass the STE rules. The docstring line "`called` is the names" is a small grammar slip and is not a finding.
`rota/core/runner.py` and `tests/rota/test_onboarding_phases.py` each hold 0 bytes of value 13.

## (b) Findings

1. `rota/core/runner.py:3739` and `3761`. Low. CONFIRMED: probe `test_p2_after_landed_write` lands `glossary.amend` on turn 2, then sends the list with no call and no intent words. The session ends after 3 backend calls, and no turn shows the note. The intent route needs an INTENT phrase, and the no-op route needs a session with no writes. The line reaches only `outcome.errors`. Night 147's measured shape is turn 1 with no writes, so the frame's case is covered. Fix: before `if not calls:`, add a once-only branch that appends the reply and `listed_note` when the note is not empty, then `continue`.

High: 0. Low: 1.

## (c) Probes

All in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/4a757f92-bd97-4750-9830-bd149134e576/scratchpad/rv237/test_probe237.py`, run from the worktree with `ROTA_MODEL=qwen3:8b`, `pytest -q -s -p no:cacheprovider`. 8 passed.

- `test_p1_units`: `extract_lenient` then `listed_not_called` on the bullet call, the numbered ellipsis, the attest heading over files, and s187's turn 1 from `D:/repos/rota/.rota/clickI_night147.db` (read-only URI).
- `test_p2_routes[s187|intent|after_write|twice|plain_intent|plain_noop]`: `run_session` with `ScriptedBackend` on `tick_survey`, a spy on `runner.listed_not_called` that records `called`, `allowed` and the result, and a search of each next-turn user text for the note and the old nudge texts. The `after_write` case lands no write, because the amend gate refuses an unread word.
- `test_p2_after_landed_write`: `code.source`, a landed `glossary.amend` for "transaction", then the list, then "Nothing more.".
- A byte count of value 13 in the two files.

## (d) Usage

Estimate from this context, not the harness line: about 60k input tokens, 9k output tokens, 69k total. The brief's cap was 30k. The harness line is the authority.
