# Frame 322, review of pass 3: 7e9cbac6

The commit stands after one named fix. The fix is low and is a wording fix in the composed criteria brief.

Commit: 7e9cbac6 on 4bb2656b, "fix(roles): the documentation door's refusal ends on the rewrite". The worktree is `C:/Users/roman/rota_r322b`, a detached head. The review edited no tracked file and ran no model call.

## (a) The verdict on each point

1. Holds. The last sentence is the rewrite, the form is named, and no sentence names a message call.
2. Holds. The predicate of `_docs_ticket_refusal` is unchanged. Only the returned text and one comment changed.
3. Holds. The new test keeps every pin of pass 2 except the Vision Keeper clause, and it adds four pins.
4. Holds with finding 1. The paragraph names the route in the brief's shape. One line of the role base contradicts it.
5. Holds. 7 passed in the touched file. The `test_roles_doc.py` red is the same at 4bb2656b and does not touch this change.

### Point 1: the refusal text

The probe `probe_refusal.py` called `criteria.specify` with s185's c_1 on the docstring ticket. The text in full:

```
tk_1_format_filename_example's headline is 'with shorten set to true, the path a/b/c.txt shows as c.txt in the docstring of format_filename'. The headline names the documentation, and this criterion names no documentation. A documentation criterion says what the docstring, the docs or the help text must say. Write the criterion on the documentation and send it again.
```

- The last sentence is "Write the criterion on the documentation and send it again."
- The third sentence names the form of a documentation criterion.
- The text holds no "msg." and one "Write ".
- `criteria.respecify` in `criterion_repair` mode gives the same text. The probe printed `RESPECIFY same: True`.
- The text names no call at all. "send it again" fits `criteria.specify` and `criteria.respecify` alike.

### Point 2: the predicate

`git diff 4bb2656b 7e9cbac6 -- rota/roles/api.py` shows one hunk, at `rota/roles/api.py:5865-5876`. The hunk changes the comment and the f-string of the return. The guard lines are outside the hunk and unchanged:

- `ticket_id is None or _asks_for(text or "", _NAMES_DOCS)` returns None.
- The headline is read from `tickets.text`.
- `_HEADLINE_NAMES_DOCS` decides the refusal. It matches the whole words "docstring", "docstrings" or "documentation" in the casefolded headline.

`_NAMES_DOCS` and `_HEADLINE_NAMES_DOCS` at lines 5839 and 5846 are unchanged. The two callers, `criteria_specify` at line 6020 and `criteria_respecify` at line 7063, are unchanged.

### Point 3: the rewritten test

The old test, `test_the_refusal_names_the_headline_and_the_two_routes`, pinned four substrings:

1. `_DOC_HEAD`, the headline.
2. "The headline names the documentation".
3. "Write the criterion on the documentation".
4. "msg.challenge_vision_keeper".

The new test, `test_the_refusal_names_the_headline_and_ends_on_the_rewrite`, pins six things:

1. `_DOC_HEAD`. Kept.
2. "The headline names the documentation". Kept.
3. "the docstring, the docs or the help text must say". New. The old test did not pin the form.
4. "challenge_vision_keeper" is absent. This inverts the old pin 4.
5. The text ends with `_REWRITE`. This holds old pin 3, because `_REWRITE` contains "Write the criterion on the documentation". It adds the position.
6. "Write " occurs once. New.

No pin of pass 2 is lost beyond the Vision Keeper clause. `test_respecify_into_behaviour_is_refused_with_the_same_text` still pins the equality of the two texts. The new `test_the_criteria_brief_routes_a_mixed_ticket_once` pins the brief paragraph once, with the challenge and "after its criteria land". No file in the tree outside `plans/` holds the refusal text, apart from `rota/roles/api.py` and the test.

### Point 4: the brief paragraph

`rota/roles/prompts/terminologist/criteria.md:33-36`, quoted from the composed brief:

```
**A ticket whose headline names the docstring takes documentation criteria.**
Each one says what the docstring, the docs or the help text must say. A
behaviour change that the ticket also needs goes to the Vision Keeper:
`msg.challenge_vision_keeper` with the ticket, after its criteria land.
```

The paragraph has the brief's shape: a bold rule, then the route. It orders the criteria before the message. That order fits the case read, because a message ends the session. The paragraph does not contradict lines 28-31 of `criteria.md`. Those lines govern an item that cannot mean anything consistent. Finding 1 is a contradiction with the role base. `prompts.compose("terminologist", "criteria")` puts the role base in front of the mode text.

### Point 5: the test runs

At 7e9cbac6, in `C:/Users/roman/rota_r322b`:

- `tests/rota/test_frame322_docs_ticket.py`: 7 passed.
- `tests/rota/test_roles_doc.py`: 1 failed, 8 passed.
- The two files together: 1 failed, 15 passed.

At 4bb2656b, from a `git archive` copy, the two files together gave 1 failed, 14 passed. The probe printed that `rota` imported from the copy. The failure is the same test with the same assertion: `{'answer': 'some channels carry words and some do not'}` at `tests/rota/test_roles_doc.py:221`.

The failure does not touch this change. The test reads `rota.design.graph.load()`, the message graph. The commit changes only `rota/roles/api.py`, `criteria.md` and the test file. It changes no file under `rota/design`.

## (b) Findings

1. `rota/roles/prompts/terminologist/criteria.md:33-36`. Severity low. CONFIRMED. The composed criteria brief holds the role-base line "**`msg.challenge_vision_keeper`** when an approved item cannot mean anything consistent. Refs the item". The new paragraph sends the same call for a behaviour change, with the ticket. The two lines disagree on when the call applies and on what it refs. Probe 2 printed the composed text around the role-base line. A small model can read the role-base line as a bar on the new route. The old refusal had the same route with the ticket, so the conflict is not new. Pass 3 moves the route into the brief, where the two lines now meet. Fix: widen the role-base line to name the slice of a ticket that holds more than one piece of work.

Outside the points:

2. `rota/roles/prompts/terminologist/criteria.md:33`. Severity low. CONFIRMED by a text comparison. The paragraph says "names the docstring". The door at `rota/roles/api.py:5846` also fires on "documentation" and "docstrings". A headline that names only "documentation" gets the refusal, and the brief paragraph does not name that headline. The refusal still names the form, so the retry is not blocked. Fix: write "names the docstring or the documentation" in the bold rule.

The cap refusal at `rota/roles/api.py:6080` and the id-reuse route at line 6006 still name `msg.challenge_vision_keeper`. They fire on other conditions, a seventh criterion and a landed id with new words. They are not the documentation door, and no case of this frame reaches them.

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/4cdad7e1-c78d-472d-86ab-f4c72d52763e/scratchpad/r322p3/`.

1. `probe_refusal.py`, run from the worktree root. It built the test's database by hand. It called `criteria.specify` and `criteria.respecify` with s185's c_1. It printed the refusal, its last sentence, the "msg." check and the "Write " count. It composed the `criteria` and `criterion_repair` briefs, counted the challenge mentions, and printed the new paragraph.
2. A `python -c` call that printed 500 characters before the first challenge mention in the composed `criteria` brief. It showed the role-base line of finding 1.
3. `base_4bb2656b/`, a `git archive 4bb2656b` copy. The two test files ran there with `ROTA_MODEL=qwen3:8b`.
4. `git diff 4bb2656b 7e9cbac6 -- rota/roles/api.py` and `git diff --name-only`, in the worktree, for points 2 and 5.
5. A grep of the tree outside `plans/` for the refusal's sentences.

## (d) Usage

The harness counter fell from 15,000,000 to about 14,946,000. The harness does not report input and output tokens apart. The total is about 54k, over the brief's cap of 30k because of two failed writes of this record.

Verdict: stands after the named fixes. Finding 1 is the fix. Finding 2 is an optional wording fix.

## Pass 3b: e03b1098

Pass 3b stands. The review found no finding on the three points and one low finding outside them.

Commit: e03b1098, "fix(core): the glossary answer door offers only a call the mode holds". `git log --oneline -1` in `C:/Users/roman/rota_r322b` printed e03b1098. Its parent is 269bd943, a docs commit on 864ea719. Against 864ea719 the commit changes `rota/core/sandbox.py`, the test file and `plans/stack.md`.

### (a) The verdict on each point

1. Holds. The criteria mode gets the refusal with no offer. The question mode gets the report offer, and it holds that call.
2. Holds. In the question mode the text and the recorded offer are the same at 864ea719 and at e03b1098.
3. Holds. The two new tests pin the two cases. The diff removes no line of the test file.
4. Counts: `tests/rota/test_frame322_docs_ticket.py` gave 9 passed, and pytest exited 0.

### Point 1: the two refusal texts

Probe `probe_3b.py` sent `msg.answer_tester(refs=[<ticket>], round_no=0)` from a Terminologist seat in each mode.

The criteria mode holds no `msg.report_liaison` and no `glossary.amend`. Its refusal:

```
an answer from the glossary carries a term, and refs=['tk_1_format_filename_example'] names none. The glossary does not carry this.
```

The question mode holds `msg.report_liaison`. Its refusal:

```
an answer from the glossary carries a term, and refs=['tk_1_format_filename_example'] names none. The glossary does not carry this: send msg.report_liaison(refs=['tk_1_format_filename_example']) with the same refs.
```

Probe `probe_3b_offer.py` set `api.RECORD` and read `ctx.offers`. The criteria mode recorded no offer. The question mode recorded `msg.report_liaison` with the refs. A scan of every `.tools` file found four Terminologist modes that send an answer. `criteria` and `criterion_repair` hold neither call and take the route with no offer. `question` and `unresolved` hold the report and take the report route. The door applies to the Terminologist only, at `rota/core/sandbox.py:4254`. No mode offers a call it does not hold.

### Point 2: the question mode against 864ea719

`git diff 864ea719 e03b1098 -- rota/core/sandbox.py` holds one hunk, at lines 4271-4295. The report branch keeps the old f-string, the op and the args. The same two probes ran in a `git archive 864ea719` copy. The question-mode text was the same to the byte, and the recorded offer was the same. At 864ea719 the criteria mode offered `msg.report_liaison`, which was the defect.

### Point 3: the tests

- `test_the_criteria_mode_is_offered_no_call_it_does_not_hold` pins the full text that ends at "carry this." It also pins that the mode does not hold `msg.report_liaison`.
- `test_a_mode_that_holds_the_report_is_offered_it_unchanged` pins the full text with the report offer in the question mode.

The e03b1098 test file ran in the 864ea719 copy. The criteria test failed there, and the follow check printed "second refusal: NotInWorkingSet: msg.report_liaison is not in this role's working set". The question test passed there. So the first test pins the fix, and the second test pins the unchanged text. `git diff 864ea719 e03b1098` removes 0 lines from the test file.

### Findings, pass 3b

3. `rota/core/sandbox.py:4289-4294`. Severity low. PLAUSIBLE, outside the points. The `glossary.amend` route records its offer with empty args, `{}`. The follow check runs each offer, and `glossary.amend` with no args can fail as a second refusal. No mode reaches this route today. The `.tools` scan found no Terminologist mode that sends an answer and holds `glossary.amend`. Fix: remove the route, or record the offer with the args that `glossary.amend` needs.

### Probes, pass 3b

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/4cdad7e1-c78d-472d-86ab-f4c72d52763e/scratchpad/r322p3/`.

1. `probe_3b.py`, with `probe_refusal_db.py` for the database. It printed the working set and the refusal text in the criteria mode and the question mode.
2. `probe_3b_offer.py`. It printed the recorded offers in the two modes.
3. `base_864ea719/`, a `git archive 864ea719` copy. Probes 1 and 2 ran there, and the e03b1098 test file ran there as `t3b_new.py`, with 1 failed and 8 passed.
4. A `python -c` scan of `rota/roles/prompts/*/*.tools` through `prompts.mode_tools`.
5. `pytest tests/rota/test_frame322_docs_ticket.py` at e03b1098: 9 passed, exit 0.

### Usage, pass 3b

The harness counter fell from about 14,944,000 to about 14,929,000 for pass 3b. The total is about 15k.

Verdict on pass 3b: stands.
