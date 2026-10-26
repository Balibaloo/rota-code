# Frame 337, the agency read: the naming door and its reach

Date: 2026-10-26. Read at 46e5c88b on `rota/foundation`. The code of
`rota/roles/api.py` is the same as at 322da4b9. No pytest, no model call.

## Verdict

**At one door of 14: the fix covers 2 of 14 instances.** Frame 337 fixed
the naming door and the reversal guard. Twelve other places decide or
carry his ruling on `words`, and `words` is his last reply alone
(observed: section 3). The premise holds: the doors read the last reply,
and the seat's prompt holds the exchange (observed:
`plans/wb-naming-provenance.md` section 3, s193's prompt held m76).

## 1. The purpose

`_unnamed_contest` came from 250f3806, 2026-10-14 19:55, frame 234 pass 2
(observed: `git show -s 250f3806`). It closed the wall "the verdict
contests a line he never named": night 147's s281 contested six lines that
m131 did not name, and night 146's over-contests cancelled batches
(observed: the commit body; `api.py` 12775 to 12777). The ground is law 6,
"nothing is ruled on the principal's behalf", and the rule of 2026-09-09
that a door names a state of the text (ruled: `LAWS.md` 188;
`plans/operating-facts.md` 304 to 305). It was measured on single replies
of nights 143 to 147 and closed at 0 of 6 over two nights (observed:
`plans/wall-guide.md` cause 1). `earlier_exchange` came from b57772f5,
2026-09-10, for the ask path, so the seat rules on the whole exchange
after an ask (observed: `landing.md` 21 to 24).

## 2. What exists

| Thing | Where | What it holds or does |
|---|---|---|
| The exchange, the record | `messages`, `cause_id` = ask, `verb` converse | Every answer he gave to the page (observed: `runner.py` 2645 to 2653) |
| The exchange, the reader | `runner.py` 2640 to 2660 | Puts his answers and the asked questions in `landing.earlier_exchange` |
| A second reader | `api.py` 12200 to 12225, `_earlier_reading` | A copy of the runner's query, principal half, from pass 1 and 2 |
| Line readers | `api.py` 11174 `_line_reading`, 11636 `_line_cues` | Faulted, matched and cues of one text |
| Word predicates | `api.py` 11740, 11927, 11984, 12311 | `built_line_faulted`, `pointer_fault`, `code_line_faulted`, `_note_words`, all on one text |
| The ruling's words | `api.py` 12880, `rulings.words` | The seat's `words` argument, stored as given |
| The land re-check | `principal.py` 2261 to 2264, 2311 | Reads `answer.text`, which is `rulings.words` (2663) |
| A check of `words` against a message | none | `rulings_rule` reads no `body_text` of the trigger (observed: provenance section 1) |

No single value "his words on this page" exists. Each door takes the
seat's argument (observed: the files and lines in the table).

## 3. The reach

The cause the frame places: a door reads `words`, and the brief fills
`words` with the last reply, so an earlier answer of the exchange counts
for nothing (observed: stack.md frame 337, Site). The same gap, by
instance (observed: `api.py` and `principal.py` at the lines named):

1. Reversal guard, `api.py` 11797. Covered by pass 2.
2. Naming door, `_unnamed_contest`, `api.py` 12165 to 12173. Covered by pass 1.
3. Agreement door, `_agreed_contest`, `api.py` 12171. A last reply that
   names no line ("Ok, go ahead") after m76 refuses the contest of line 5.
4. Faulted-approve door, `api.py` 11818, cues from `words` at 12725. An
   approve of line 5 after m76 lands. This is r_448c39118c's outcome by
   a first call, with no refusal before it.
5. Batch spare, `_TOUCH_WORDS`, `api.py` 11809.
6. Line-1 request door, `api.py` 11826 to 11858 and `quoted` at 12826.
7. Team-note revise door, `api.py` 12610 to 12626.
8. Files-correction door, `pointer_fault`, `api.py` 12665.
9. Code-line door, `code_line_faulted`, `api.py` 12711 to 12713.
10. Built-batch door, `built_line_faulted`, `api.py` 12753.
11. Land re-check of a built batch, `principal.py` 2261 to 2264.
12. Land re-check of a code line, `principal.py` 2311.
13. The owner's words, `rulings.words`, `api.py` 12880, `principal.py` 2384.
    Line 5's contest reaches its owner with m78, silent on line 5.
14. The brief, `landing.md` 49: "the whole reply as `words`".

Count: 14. Scenes and fixtures in `rota/` with `earlier_exchange`: 0.
Outside `rota/`, two test files and `cassettes.db` hold it (observed: grep).

## 4. The fix against the reach

The built fix covers 2 of 14: instances 1 and 2 (observed: diffs of
7121f613 and 322da4b9). It leaves 3 to 14. The pass report names 3 and 4
as open questions 2 and 3 (observed: `f337_pass1.md`, section (d)).
Instance 4 is the direct path to the frame's own outcome, an approve of a
line he called wrong (reasoned: `_faulted_approve` reads m78's cues only).
The provenance's repair said the owner's words carry the earlier answer,
and no commit does that (observed: `wb-naming-provenance.md`, The repair;
the diffs touch no `words` write). The frame names cause 2, but the fact
was in the prompt, so the guide places it at step 3, cause 1, the hop
where his words change (reasoned: `wall-guide.md` section 4, steps 3 and 6).

## 5. My proposal

Not the same fix. Fix the value `words` once, at its source:

1. `rulings_rule` builds his words from the record, his converse answers
   to the page and the trigger in seq order, with one helper that the
   runner's query also calls (observed: `runner.py` 2645, `api.py` 12200).
2. Every door in instances 3 to 10 reads that exchange in place of the
   seat's argument (observed: `api.py` 11797 to 11858, 12610 to 12753).
3. Pass 2's rule becomes the one line reader: per line, his latest answer
   about the line rules it (observed: `api.py` 12215 to 12222).
4. `rulings.words` stores the exchange, so `land` and the owner read what
   the doors read, instances 11 to 13 (observed: `principal.py` 2663).
5. Count before the pass, every door over nights 160 to 168, gate 0 new
   false refusals (ruled: `wall-guide.md` section 3, "the count").

The brief keeps its text, so no cassette re-records (reasoned: the seat's
argument is no longer read by a door). Price: 1 count, 1 implementer
pass, 1 review, 1 resumed pass and 1 gate, about 5 cycles and 50k of the
holding session (observed: `operating-facts.md` 247, 10k a cycle). Agents
spend about 75k, 70k and 25k (observed: the anchors, frames 24 and 30).
Frame 337 spent 4 cycles on 2 of 14 (observed: stack.md).

## 6. The doubt

- A door that reads joined text can fire on a line he later withdrew.
  The per-line latest rule covers lines, and sentence predicates
  (`_KEEP_CHANGE`, `_names_request`) have no line (reasoned).
- I did not count instances 3 to 13 on night records. Some may have 0
  cases, and then they can wait (reasoned: `wall-guide.md` cause 8).
- I did not read the tests outside `rota/` or the cassettes, so the
  re-record cost of a stored-words change is unproved (reasoned).
