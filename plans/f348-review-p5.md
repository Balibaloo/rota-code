# Review of frame 348, commit b126acab on rota/foundation, pass 5

Verdict: not ready to close. Pass 6 fixes the high of p4, and the suite holds. One new high comes from the widened subject rule. A question clause now binds a fault on a line it names in passing, where his words defer the verdict. Counts: 1 high, 2 low.

Worktree: C:/Users/roman/rota_f348e at b126acab. The review removed the worktree after the run.

## (a) Verdicts on the points

1. Fixed. On `_page6`, silent reply, all approve, each of the six texts lands as the brief expects. "Tell me what line 2 means, because it is wrong." refuses line 2. "Tell me what line 2 means, line 4 is wrong." refuses line 4 only. "Please explain why line 2 is wrong." refuses line 2. "Line 3 is unclear to me, so please say what it means." lands all approve. The p3 and p2 texts refuse line 2.
2. No reading changes with the flag off. The one caller that sets `asks` is the loop at `api.py:14284`. The new condition is `A or (asks and ...)`, so `asks=False` gives the old test. No cache keys a reading on the words alone. Over all 29 principal texts of l3_rulings.yaml, `_line_cues` with and without the flag differ in none. The first ten are the same.
3. The three texts bind as the claim says. "Tell me what line 2 means, and line 4 is wrong." binds line 4 as a fault. "Line 4 is wrong, so tell me what line 2 means." binds line 4 as a fault. "Tell me why line 2 and line 4 differ." binds nothing. But a passing mention with a negation in it binds a fault (finding 1).
4. One text differs. Three principal texts match `_is_question`. The L3R-n175-m11-m14 inbound, "I was asking you that, because line 3 only says the team could not check a claim ... so I can tell you if it is right.", binds nothing at 2ebd7f52 and line 3 as a fault at b126acab. In the case, the text is the reply, so the loop does not read it and no case renders the change (finding 1).
5. No hunk falls outside the claim. The api.py diff holds the `asks` flag through `_line_reading`, `LineReading` and `_line_cues`, the removal of `_REQUEST_SPAN`, and the loop re-read. The test file adds three parameters.
6. Confirmed. `test_frame337_earlier_answers.py` and `test_r1_menu_form.py` with `-n0`: 56 passed. The L3R replay with ROTA_DEV_DB on `f348r5rev_cass.db`: 2 failed, 23 passed. The reds are L3R-n171-m27-m28 and L3R-n172-m76-m77.

## (b) Findings

1. `rota/roles/api.py:14284-14286`, the widened rule `set(c["lines"]) & reading.faulted`. Severity high. CONFIRMED.
   The rule binds every faulted line the clause lists, subject or not. The reader faults line 3 on the cue "not" in "could not check", a word that describes the line.
   The words defer the verdict: "so I can tell you if it is right." Law 6 says only his words choose a verdict.
   Probe: the n175 inbound text as the one earlier answer on `_page6`, silent reply, all approve. The door refused approve of line 3. At 2ebd7f52 the loop bound nothing for that text.
   The corpus holds the text as a reply only, so no recorded case renders the path.
   Fix: widen the binding to a non-subject line only on a fault word such as "wrong", and keep the subject rule for a negation cue.
2. `rota/roles/api.py:14284-14286` with `_line_cues`, a reported claim. Severity low. CONFIRMED.
   "Tell me why line 3 says line 2 is wrong." binds line 2 as a fault, with the cue "says". He asks about a claim of line 3 and gives no verdict on line 2.
   Probe: the text as the earlier answer on `_page6`, silent reply, all approve. The door refused approve of line 2. At 2ebd7f52 the loop bound nothing.
   Fix: do not take a head verb of the relating kind as an instruction inside an `asks` sentence.
3. Outside the points. `page_clauses`, the clause line list, review p4 finding 2. Severity low. CONFIRMED, and older than pass 6.
   "Explain why line 2 is fine and line 4 is wrong." gives one clause with lines [2] only. `_line_cues` faults line 4, but the new rule intersects with `c["lines"]`, so line 4 binds nothing and all approve lands.
   The widened rule now depends on `c["lines"]`, so this defect reaches it.
   Fix: let `page_clauses` list every line that a clause names.

## (c) Probes

All probes ran from the worktree root with `ROTA_MODEL=qwen3:8b`. The review deleted the probe test before it removed the worktree.

- `tests/rota/test_probe348p5.py`, 14 earlier answers on the `_page6` fixture, silent reply, all approve. Each printed the lines whose approve the door refused, in turn.
- `scratchpad/p5probe.py`: `_line_cues` with and without `asks` on every principal text of l3_rulings.yaml. It emulated the loop of 2ebd7f52, with `_REQUEST_SPAN` rebuilt from `_ASK_VERB`, beside the new loop on every principal text that `_is_question` matches. It also printed the clauses, the cues and both bindings for the point 3 texts.
- A `python -c` call: `page_clauses`, `_subject_lines` and `_line_cues` on the n175 inbound text.
- `test_frame337_earlier_answers.py` and `test_r1_menu_form.py` as is, with `-n0`.
- `test_l3_rulings.py` with `ROTA_DEV_DB` on `scratchpad/f348r5rev_cass.db`, a fresh copy of `D:/repos/rota/tests/rota/cassettes.db`.

The scratchpad is C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/d5c14419-fc45-4e3f-b734-46fe335c298f/scratchpad.

## (d) Usage

Input tokens: about 19k. Output tokens: about 7k. Total: about 26k. The total is about 1k over the cap of 25k.
