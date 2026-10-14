# Frames 187 and 219, pass 1: the diff review of 92c4f126

Rota workflow: the Vision Keeper's contested wake and the `decisions.author` door.
Worktree `C:/Users/roman/rota_rv187` at 92c4f126, parent 9f7ad611. Read-only review, 2026-10-15.

Verdict: ACCEPT. The four points hold. The review found 0 high and 3 low findings, and none blocks the pass.

## (a) The verdict on each point

1. HOLDS. At the parent, s287 and s288 get "no decisions row with id=...". At HEAD, both get the items refusal, and the re-sent call lands.
2. HOLDS. The clause shows on contested, exhausted and propose, and on an empty tool list. A contested tick wake keys the contested mode, which offers the report. Challenge drops the clause, and its re-sent call is the close.
3. HOLDS, with one low finding. The sentence matches the wake text and the quote result. The sentence comes after the quote, so it keeps the consult-and-quote-first rule.
4. HOLDS. The STE is clean. No pronoun names the principal. Each of the three files has 0 CR bytes.

## Point 1: the night's calls through the door

Night 147 (observed: `clickI_night147.db`, `turns` and `tool_calls` of s287 and s288, read 2026-10-15). Both sessions have wake_kind tick:contested, mode normal, and the item as the only ref. In both sessions, call 4 used the item's own id. The cross-table guard refused call 4 before site A. Call 5 used the id defines_commands_and_options_defense. Calls 6 and 7 used the id d_26efd6365c. All of calls 4 to 7 kept `supersedes` on the item.

- The parent. The night shows the text the seat read after call 5: "no decisions row with id='defines_commands_and_options'; this changes an existing row, so the id has to be one you were given; decisions rows are [... 'd_26efd6365c']". The text lists the principal's ids as ids to use, so the seat went to d_26efd6365c next. At the parent, the `_must_exist` check comes before the author check, so s288's call gets the same text. The pass report's red run shows the same text for both tests.
- HEAD, s287's call. The text is "A decision has no supersedes for an item. `defines_commands_and_options` is an items row, not a decision. Send the same call without supersedes, and close with `msg.report_liaison`." The probe re-sent the call without `supersedes`. The call landed as defines_commands_and_options_defense, author vision_keeper, supersedes None. Then `msg.report_liaison` landed as m1.
- HEAD, s288's call. The text adds "d_26efd6365c is a decision by principal, so send the call again without supersedes, under an id of its own". The offer carries id=INVENT. The probe re-sent the call with a new id, and the call landed. The principal's row stayed unchanged. The report then landed.
- The conftest follow check runs each offer on every test in the file. The four new tests pass, so the follow check admits both offers.

## Point 2: the route clause

The Vision Keeper modes that offer `decisions.author` are challenge, contested, exhausted and propose. Three of them offer `msg.report_liaison`: contested, exhausted and propose. Challenge does not offer the report. `_mode_key` maps the wake tick:contested to the mode contested. `contested.tools` lists `msg.report_liaison`. The probe shows that `_wake_mode_tools` returns the six contested ops on that wake. A sandbox with no wake returns an empty list, and the clause shows. The mode normal has no tools file, so the role's full set applies, and the report is in that set.

In challenge mode, the text ends at "Send the same call without supersedes." The probe set `ctx.trigger` as the runner does. The re-sent call landed. The challenge brief tells the seat to author a decision with refs to the item and no `supersedes`. So the re-sent call is the challenge mode's close. A seat in challenge mode gets a close without the report.

## Point 3: the brief sentence

The seat's wake text starts "You were woken by: tick:contested", so "a tick wake" matches a word the seat reads. On s287, the quote result was "OK transcript.quote -> {}". The phrase "returns nothing" matches that result closely enough. The sentence makes the report depend on the quote result, so the quote comes first. That order keeps the rule at the top of the brief: read `principal_said`, quote, and consult. The prefetch already gives the consult result on the tick wake. One tension stays. The defend branch sends "They said no and not what instead" to `decisions.author` and then the report. The new sentence says to report and stop. The door's text on the same wake offers the author call and then the report. See finding 1.

## Point 4: STE, pronouns, CR bytes

The refusal texts, the brief sentence and the comments use short active sentences. The texts name the principal through the row's author and use no pronoun. The only pronoun in the added lines is "them" at test line 96. That word is in the principal's quoted text, which is an exception. The CR count is 0 in `rota/roles/api.py`, `contested.md` and `tests/rota/test_desk_guards.py`.

## (b) Findings

1. `rota/roles/prompts/vision_keeper/contested.md:55-56` with `rota/roles/api.py:9520-9528`. Severity low. PLAUSIBLE. On a tick wake with no words, the brief says to report and stop. The door's refusal on the same wake offers a decision and then the report. Both routes end at the report, so the wake closes either way. But the seat gets two routes, and night 147's sessions had already chosen the decision route. Each landed decision then carries the Vision Keeper's own reading of the principal's meaning ("the intended meaning was ..."). The brief's "do not minute" paragraph forbids that text. Fix: on a contested wake with no `principal_said`, make the refusal say to leave out the decision and send `msg.report_liaison`.
2. `rota/roles/api.py:9510-9511`. Severity low. PLAUSIBLE. In propose mode, the clause tells the seat to close with `msg.report_liaison`. `propose.md` never names the report. The reason in the comment, Law 11 on the contest of an observed item, applies to the contested wake only. Fix: show the clause only when the mode key is contested or exhausted, or say in the comment why propose keeps it.
3. `tests/rota/test_desk_guards.py:1771-1862`. Severity low. CONFIRMED: the probe shows that the challenge branch drops the clause and that its re-sent call lands, but no test pins the branch. The pass report's open point 1 says the same. Fix: add one test on a message wake with verb challenge and `ctx.trigger` set, and assert that the text ends at "without supersedes.".

Outside the points: no finding. The pass report's open points 3 and 4 still stand: a row with an empty author, and a seat that overwrites its own role's row. This review did not run them.

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/4a757f92-bd97-4750-9830-bd149134e576/scratchpad/rv187/`.

- `probe_door.py` ran the calls of s287 and s288 on a tick:contested wake, and on a sandbox with no wake. The probe printed the tool list and the refusal. Then the probe re-sent each call as the text says and sent `msg.report_liaison`.
- `probe_challenge.py` built a message wake with verb challenge and set `ctx.trigger`. The probe printed the tools and the refusal, and re-sent the call.
- Inline read-only queries on `D:/repos/rota/.rota/clickI_night147.db` read `sessions`, `tool_calls` and `turns` of s287 and s288, and the d_26efd6365c row.
- The pytest run of `tests/rota/test_desk_guards.py` with `-k "night147 or night143 or still_lands"` gave 4 passed.
- A `tr -cd` count of CR bytes on the three files gave 0, 0 and 0.

## (d) Usage

This review's own estimate: about 45k input tokens, about 9k output tokens, about 54k total. The harness line is the record.
