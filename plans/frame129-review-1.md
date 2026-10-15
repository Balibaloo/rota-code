# Frame 129, review 1: the item-rewrite door at 0bf6a5ea

Reviewer: read-only diff review on the worktree `C:/Users/roman/rota_r129` at 0bf6a5ea, 2026-10-15. Workflow: the meta workflow reviews a change to the rota workflow's Vision Keeper door.

## Verdict

Accept with one second pass. The door refuses night 149's s232 rewrite, and the `unchanged` path still passes (observed: replay, 2026-10-15). The refusal text is wrong on two of the three wakes that newly meet it. The answer mode offers neither named call. The deliver mode does not offer `decisions.author`. The deliver wake also re-asserts decided items often on real nights, so night 150 can meet the refusal on a path no case records.

## (a) The six points

1. CONFIRMED. At HEAD the s232 call is refused. At the parent the call lands. Refusal text at HEAD: "confirm_default_on_eof is the principal's own words. A propose wake does not rewrite them. Send msg.report_liaison with what the item should say, so the principal rules. Or answer with decisions.author". The parent returns `{'id': 'confirm_default_on_eof'}`, the landed shape.
2. Non-onboarding wakes that offer `problem.assert` and now meet the refusal: propose, deliver and answer. Challenge, exhausted and contested keep their own branches. Orient, reorient and survey wake on onboarding ticks, so the door returns None at its first line. See answer 2 below for what a rewrite means in each mode.
3. Finding 1 and finding 2. The propose mode offers both named calls. The deliver mode lacks `decisions.author`. The answer mode lacks both calls.
4. CONFIRMED. The item's own words on a propose wake return `unchanged: True` at HEAD. The same-kind same-words check runs before the new refusal (api.py, before the challenge branch).
5. Test 1 is red at the parent with `Failed: DID NOT RAISE <class 'ValueError'>`, the right reason. Test 2 is green at the parent and at HEAD. Test 2 is a guard of the contested branch and cannot be red before the change. The file reads `17 passed` at HEAD. Neither touched file holds a CR byte.
6. Night 150's read: count Vision Keeper refusals that start "is the principal's own words. A" per wake verb, and read each deliver and answer refusal for the next call.

## Answer 2 in detail: what a rewrite of a decided item means per mode

A `decided` item is any item whose refs reach a ratified statement or a landed ruling (schema.sql, the `provenance` view). The class does not need the principal's approval. A draft that the Vision Keeper wrote from a statement is `decided` too.

- propose (message, verb `propose`, from the Architect): the brief says "assert it as an item", a new item for a refactor. A rewrite of a decided item has no brief basis. The refusal is right. Night 149 s232 is the case.
- deliver (message, verb `deliver`, from the Liaison): a new ratified statement arrives. The brief says an item already on file for the same behaviour "is not asserted again under a new id". So the seat amends the existing id with the new statement. That amend carries the principal's newly ratified words. The door now refuses it. Real nights do this often: 219 deliver-wake asserts re-assert an id that an earlier session wrote, and 111 of those ids are `decided` now, over 46 nights (observed: `r129_count.py`, all `clickI_night1*.db`, 2026-10-15). In night 142, `echo_json` reached version 7 across deliver sessions s98, s322, s325 and s438. The provenance at the call is not stored, so the count is an upper bound. The brief's "If `how_it_works` is already on file, leave it" agrees with a refusal for that one item.
- answer (message, verb `answer`, from the Researcher or another role): the brief says to cite the reference on the item with `problem.assert`. A cite with new words on a decided item is now refused. A cite with the same words returns `unchanged`.
- challenge, exhausted, contested: no change. Their branches run before the new line.
- orient, reorient, survey: `ctx.onboarding` is true on these ticks (`ONBOARDING_TICKS`, scheduler.py line 558). The door returns None.

## (b) Findings

1. rota/roles/api.py lines 1330 to 1333 (the new refusal). Severity high. CONFIRMED: on an answer wake the refusal names `msg.report_liaison` and `decisions.author`, and `answer.tools` offers neither (probe `r129_modes.py`). The seat then calls a tool it lacks, or ends its session. The mode offers `msg.submit_liaison` and `schedule.reask`. Fix: build the route from `ctx.allow`, and name only calls the mode offers, for example "Send msg.submit_liaison with what the item should say" in the answer mode.
2. rota/roles/api.py lines 1330 to 1333. Severity high. CONFIRMED: on a deliver wake the refusal names `decisions.author`, and `deliver.tools` does not offer it (probe `r129_modes.py`). Fix: in the deliver mode, end the text at "so the principal rules", or use the same `ctx.allow` filter as finding 1.
3. rota/roles/api.py lines 1328 to 1333. Severity high. PLAUSIBLE: a later deliver wake amends a decided item with a newly ratified statement, and the door now refuses that amend. Why: the deliver brief tells the seat to keep the existing id, and 111 deliver re-asserts on decided-now ids landed on past nights. No recorded case replays a second deliver on a decided item, so the suite stays green. Fix: admit a deliver wake when the trigger's statement refs reach the item, or rule that a deliver amend goes through the Liaison, and record the case.
4. rota/roles/api.py line 1330. Severity low. CONFIRMED: the answer wake reads "A answer wake does not rewrite them" (probe `r129_modes.py`). Fix: choose "An" when `named` starts with a vowel.

Outside the points: none beyond finding 3, which reaches past the brief's s232 case.

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/cd6300cd-93cb-43d0-81c1-5833e2698637/scratchpad/`.

- `r129_look.py`, `r129_look2.py`: read s232's calls, the trigger m118, the item row and its provenance from `clickI_night149.db` opened `?mode=ro`.
- `r129_replay.py`: copies the night 149 database into memory, sets `confirm_default_on_eof` back to approved version 2 with the words "The flag defaults to False", builds the Vision Keeper in propose mode on m118, and sends s232's `problem.assert`. Then it sends the item's own words. Ran at HEAD with the worktree on `PYTHONPATH`, and at the parent from `r129_parent/` (a `git archive` of 0bf6a5ea^). The night database holds no item history, so the version 2 text is a reconstruction from `plans/night149-read.md` section 1.4.
- `r129_modes.py`: a fresh database with one decided item, a deliver message from the Liaison and an answer message from the Researcher. Sends a changed-words assert on each wake and prints the offered calls.
- `r129_count.py`, `r129_ver.py`: count deliver-wake and answer-wake re-asserts of an existing id over every `clickI_night1*.db`, opened `?mode=ro`, and read the versions in nights 142, 143 and 149. The count found no answer-wake re-asserts.
- The test file at HEAD: 17 passed. The HEAD test file on the parent tree in `r129_parent/`, `-k s232`: 1 failed (DID NOT RAISE), 1 passed.
- CR count by bytes on both touched files: 0 and 0.

## (d) Usage

Input tokens about 45k, output tokens about 8k, total about 53k (estimate, the harness line is the record). No sub-agents.
