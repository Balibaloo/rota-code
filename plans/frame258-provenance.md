# Frame 258, the provenance read: how a contest on the request line is admitted today

Read at c87a313b. Read-only, except this file. The night database was opened with `mode=ro`.

## Result

The door admits a line-1 contest when other lines are named and any unnumbered sentence shares one content word with the request text. Criteria restate the request's words, so a correction of the criteria spares line 1 by default. s181's sentences 3 and 4 share `closed`, `stdin`, `default`, `true` and `false` with `confirm_default_on_eof`, and every one of those words is also in cr_1 to cr_3. The keep rule `_KEEP_CHANGE` did not fire, because "I don't want to drop" puts "want to" between "don't" and "drop". The repair: an unnumbered sentence spares line 1 only when it opens with a build verb, or when it shares with the request a content word that no faulted line's text holds. No recorded YAML case goes stale or red.

## 1. The door

`rulings_rule` runs three doors in order, in `rota/roles/api.py`:

1. The batch door, lines 11387 to 11423. A contest of a built batch line lands only when `built_line_faulted(words, order, ref, read_faulted)` is true (line 11414). Otherwise it raises "the words do not fault {ref}'s files" (line 11422). This door is a positive test: a contest needs a fault.
2. The completeness door, lines 11424 to 11430. Every line of the page needs a ruling.
3. The line reader, `_line_refusal`, called at about line 11478. It returns a refusal or None, and None admits.

`_unnamed_contest` (line 10941) leaves line 1 out on purpose: `unnamed = sorted(n for n in contested - named if n != 1)` (line 10964). Its docstring says "Line 1 stays with the line-1 refusal and its guards". The line-1 refusal is in `_line_refusal`, lines 10638 to 10676. It is a negative test: it admits unless one refusal condition holds. The predicate that admitted s181 is at lines 10668 to 10673:

```python
batch_faulted = bool(batch_lines & faulted)
if not _KEEP_CHANGE.search(words or "") and any(
        s.strip() and not _LINE_REF.search(s)
        and not _BARE_AGREEMENT.fullmatch(s)
        and not (batch_faulted and _FILES_TALK.search(s))
        and _names_request(s, request_texts) for s in sentences):
    return approve
```

`approve` was None, so the contest landed. Probe on s181's words:

| Sentence | line ref | `_names_request` | shared words | `_FILES_TALK` |
|---|---|---|---|---|
| "I don't want to drop this change, so please fix it and try again." | no | False | none | no |
| "The checks on lines 2, 3 and 4 look wrong: ..." | yes | (skipped) | | |
| "The error also suggests the test's fake closed stdin is broken, ..." | no | True | closed, stdin | yes |
| "Please give the tests a proper closed stdin and have them expect a true or false default." | no | True | closed, default, false, stdin, true | yes |

`batch_faulted` is False, because the words fault lines 2 to 4 and not line 5. So the files-talk guard was off, and the tests sentences counted as request corrections. `_KEEP_CHANGE` is `\b(?:don['’]?t|do not) (?:drop|give up)\b|\bkeep going\b` (line 10689). It needs "don't drop" with nothing between.

The comment at line 11194 is about a clarify page, not this case. A clarify numbers no line, and the comment explains why a clarify takes a partial map.

The line-5 refusal has no sibling for line 1 because the two doors test opposite directions. The batch door asks "do the words fault this line?" and refuses when they do not. The line-1 door asks "does some refusal condition hold?" and admits when none holds. Frame 234 built the line-1 door as a refusal of a known bad shape, and frame 258 then added spares for right corrections. No commit wrote a positive test for line 1.

## 2. The history

| Text | Commit | Date | Frame | What the body says it was for |
|---|---|---|---|---|
| "have no ruling. Every line of the page takes one ... A line the reply does not contest is approve" | b57772f5 | 2026-09-10 | none, the Liaison landing feature | The words land through the Liaison and `rulings.rule`, a map from each line to approve, contest or revise. The refusal makes the map complete. Moved unchanged inside the file by 30c4a121 (frame 298, pass 3). |
| "the words do not fault {ref}'s files" | 4fe07692 | 2026-10-15 | 255, pass 1 | `built_line_faulted` admits a files correction after the head commit and refuses 9 of 9 contests the words do not support. |
| "Line 1 is the request, and they do not fault it" | 39e2fba7 | 2026-10-14 | 234 | Night 146 lost 4 of 8 batches. Refuse a line-1 contest when the words fault other lines and do not quote line 1. |
| `_unnamed_contest` | 250f3806 | 2026-10-14 | 234, pass 2 | Refuse a contest on a line the words do not name. |
| `_names_request` | 59030519 | 2026-10-16 | 258, pass 2 | m46 "Please don't drop this change" contested line 1 through the m263 guard. The guard now spares line 1 only for a build verb or a content word shared with the request. |
| `_KEEP_CHANGE` | 2284cfab, 06b3988d, c641d108 | 2026-10-18 | 258, passes 3 to 3c | A sentence about the batch's files spares nothing when a batch line is faulted. The keep rule reads the whole reply. |
| "The words do not fault line 1, and they ask to keep the change" | 405fc29b | 2026-10-23 | 305, review 2 | Refuse a line-1 contest when no line is faulted and the reply asks to keep the change (m46, m64). |

The stack block of frame 258 (`plans/stack.md`, line 1021) records the known gaps. Review 2 of 59030519 found that the spare "spares line 1 wrongly ... under a sentence that names the request's subject". The review of c641d108 found that "keep the change" does not match the keep rule. s181 is both gaps on one reply.

## 3. The seat's path

The seat ruled in the landing mode, `rota/roles/prompts/liaison/landing.md`. The sentences about lines:

- "The reply names the line, or corrects the thing the line says: `contest`. A reply that says line 3 is wrong contests line 3 and approves the others."
- "The reply strikes or drops a line from the change: `contest`. The door reads `drop`, `remove` and `strike` as `contest`."
- "A correction counts against the line it is about, and only that line. A correction of a criterion, a check or the files contests that line, not line 1."
- "The line under a request is the code it touches. Words about files, tests or paths go on that line, never on the request."
- "Every line gets a ruling."

The brief and the refusal agree: an uncontested line is approve, and a criteria correction does not contest line 1. The seat's first call followed the brief. It left line 1 out and put the tests words on line 5, the batch line, as "Words about files, tests or paths go on that line" says. The batch door refused line 5. The tests words then had no line, and the reply opens with "drop this change ... please fix it". The completeness refusal named line 1 without a ruling and did not say which ruling. The seat had just been told to take its contest off the change's line, and it put the contest on the other line of the change, the item. The refusal text says "A line the reply does not contest is approve", but the seat read "fix it" as a contest of "it", the change. Reasoned, not measured: the "drop" bullet and "fix it" made contest the reading the seat chose.

## 4. The repair

Add one positive test in the shape of the line-5 refusal. In the final branch of `_line_refusal`, an unnumbered sentence spares line 1 only when it faults the request. "Faults the request" comes from what the reader computes already:

1. A sentence names line 1: `1 in faulted`, or a `_LINE_REF` that covers line 1. The door has this test now.
2. The words quote line 1: `quoted`. The door has this test now.
3. A sentence with no line number, after `_unnumbered` drops the back references, that corrects the request. It opens with `_BUILD_VERB` (m263, "Also, take the version ..."), or it shares with the request text a content word that no faulted line's text holds.

Point 3's second half is the change. The caller passes the texts of the faulted lines beside `request_texts`, and `_names_request` subtracts their words. On s181 the shared words are `closed` and `stdin`, and `closed`, `default`, `false`, `stdin` and `true`. Every one is in cr_1 to cr_3, so nothing remains and the spare does not fire. The request words that no criterion holds are `let` and `take`. Also widen `_KEEP_CHANGE` to "don't want to drop" and "keep the change". The pass 3c review already named the second shape.

Night 149's m25 needs no change. It names no line, so it takes the `_agreed_contest` path. That path already refuses `how_it_works: contest` and admits a contest of line 1.

The refusal text, 30 words: "line 1: the words do not fault the request. They fault lines 2, 3 and 4. Rule lines 2, 3 and 4 as the words say, and approve line 1." Next, the seat sends 1 approve, 2 to 4 contest and 5 approve. The door admits that map. The criteria contests go to their writer, the item stays approved, and b_2 stays on the schedule.

Stale or red cases: none. No case in `tests/rota/cases/*.yaml` runs the landing prompt and expects a contest on line 1. The nine landing cases in `l1_landing.yaml` expect line 1 approve, park or a question. Three cases carry a contest of a page's first ref as a stored verdict: `L1-AR-a-ruled-constraint-gets-no-new-row` (`<k1>`), `L1-AR-re-annotate-from-the-principals-correction` (`<b1>`), and `L1-LI-a-contested-statement-is-not-delivered` (`<s1>`). The door does not read a stored verdict. In those cases line 1 is not a request item, so `request_first` is False. The Python tests that touch the spare are in `tests/rota/test_frame234_verdict_lines.py`, `test_request_page.py` and `test_frame250_verdict_faults.py`. This read did not run them.

## 5. The red tests

**s181, night 161, walk 2, page m66.**

- Lines: 1 the item `confirm_default_on_eof`, "Let confirm() take a default_on_eof flag: when stdin is closed it returns the default (True or False) instead of aborting." 2 to 4 the criteria cr_1 to cr_3 of that item, from the database. 5 the batch b_2 with a head commit, open.
- Words: "I don't want to drop this change, so please fix it and try again. The checks on lines 2, 3 and 4 look wrong: the default for confirm is yes or no as true or false, not the word \"yes\". The error also suggests the test's fake closed stdin is broken, so it doesn't test real end-of-input. Please give the tests a proper closed stdin and have them expect a true or false default."
- Call: `rulings={"1": "contest", "2": "contest", "3": "contest", "4": "contest", "5": "approve"}`.
- Expected: refused, with the text in section 4. The text names line 1 and lines 2, 3 and 4. A second test: the map with line 1 approve lands, and the item stays approved.

**m25, night 149.**

- Lines: 1 a request item. A later line holds `how_it_works`, the description row. The other lines are criteria or notes as on the night's page (`.rota/clickI_night149.db`).
- Words: "ok, this matches what I asked for. Please keep it to the standard library json module"
- Call: `rulings` with `how_it_works: contest` and every other line approve.
- Expected: refused at HEAD by `_agreed_contest`: "The words name no line and agree with the page, so their instruction is about the request, line 1. Approve line N, and rule line 1 as the words say." A second test: the map with line 1 contest lands. The repair must keep both results.

## 6. What this read does not settle

- The count over every night's records. Of the 58 line-1 contests that reached the line-1 refusal to night 155, this read does not say how many the new subtraction refuses, or whether it refuses a right one.
- Whether a criterion that repeats the whole request leaves a right request correction with no word of its own. Review 2 of 59030519 named "Sort the keys." as a right correction that shares no word, a shape no night shows, and the build-verb test does not catch it.
- Whether the completeness refusal should say "approve line 1" when the words do not fault line 1. Frame 305 owns that text.
- Whether the landing brief's "drop" bullet pulls a seat to contest the change when the reply says "don't drop". No count was made.
- Whether the seat sends the right map on the first call after the new refusal, on qwen3:8b and qwen3.5:9b. No L1 case was run.
- Night 160's s290 `revise` on line 1. The repair reads `contested` only, and `revise` goes through no line-1 test. That is frame 296's site.

Token usage: about 55k.
