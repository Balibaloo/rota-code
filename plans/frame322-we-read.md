# Frame 322, the W-E read: a docstring item becomes behaviour criteria

Date: 2026-10-26, read at commit 6527dbf6 on `rota/foundation`. Session
ad481e08 (rota-04), sprint 23, row 3. Read-only, no model call, no pytest.

Sources:

- `.rota/clickI_night166.db`, `clickI_night165.db`, `clickI_night164.db`
  and `clickI_night163.db`, opened with `mode=ro`: `sessions`, `turns`,
  `tool_calls`, `receipts`, `tickets`, `criteria`, `statements`, `rulings`
  and `messages`.
- `.rota/clickI_night166.principal.jsonl`, for the page clocks.
- `tests/rota/cassettes.db`, `case_runs`, `mode=ro`, and
  `tests/rota/cases/*.yaml`.
- `rota/roles/api.py` 5087 to 5964: `criteria_specify`, `_twin_refusal`
  and `_surface_names_what_the_item_names`.
- `rota/roles/prompts/terminologist/criteria.md`, as s185's system prompt
  carried it.
- `rota/LAWS.md`, and `rota/DECISIONS.md` 1056 to 1095 and 1513 to 1535.
- `plans/night166-read.md` 161 to 213, `plans/night165-read.md` 70 to 78
  and 156, `plans/night164-read.md` 83 to 85, `plans/night163-read.md` 103
  to 108, `plans/night163-w7w8-read.md` sections 0 and 3, `plans/stack.md`
  frames 322 and 306, and `plans/wall-guide.md` causes 5 and 9.

## The result

**A door, with the predicate: `criteria.specify` and `criteria.respecify`
refuse a text that names no documentation word, "docstring", "document" or
"help text", on a ticket whose headline names one, and the refusal sends a
ticket that also wants a code change to the Vision Keeper for a slice.**
Over nights 163 to 166 the predicate refuses 13 landed writes. All 13 are
on the docstring item, and his page replies or the night reads call each
of them wrong. It refuses 0 writes on the `get_app_dir` and `clear`
tickets, so it has 0 wrong refusals on the four nights (observed: section
3, counted by hand). The wall is not the noise of one night. The docstring
item got behaviour criteria in its first criteria turn on 4 of 4 nights,
all on `qwen3.5:9b` (observed: section 4).

A second strand stays open. His words "only the docstring changes while
the code stays the same" were a landed ruling before s185's criteria
reached a page, and s185's prompt did not carry them (observed: section
1). That strand is the first half of frame 306: his words on a page do not
reach the criterion.

## 1. What s185 saw

The wake and the ticket reached the prompt. The first lines of s185's
turn 1 user prompt read (observed: `turns`, s185 seq 1):

```
You were woken by: tick:criteria
Refs: format_filename_example
No criterion yet: tk_1_format_filename_example (with shorten set to true, the path a/b/c.txt shows as c.txt in the docstring of format_filename).
```

The `[tickets.scan]` block carried the headline "with shorten set to true,
the path a/b/c.txt shows as c.txt in the docstring of format_filename". The
`[the item]` block carried the item text and his ratified s3: "Give
format_filename one example in its docstring: with shorten set to True,
the path a/b/c.txt shows as c.txt." (observed: the same prompt, and
`statements` s3). The prompt also carried the source of `format_filename`,
with `filename = os.path.basename(filename)` (observed: the same prompt).

Turn 1 wrote three criteria, in this order (observed: `turns` s185 seq 1
completion, and `receipts` versions 7 to 9):

1. c_1: "When shorten=True, format_filename strips the directory prefix
   from the path."
2. c_2: "When shorten=True, format_filename returns only the basename of
   the provided path."
3. c_3: "The docstring of format_filename must include an example
   demonstrating that with shorten=True, a/b/c.txt is displayed as c.txt."

Nothing in the prompt told the seat that a docstring item wants a
documentation criterion and no behaviour criterion. The system prompt
holds no word "docstring" and no word "documentation" (observed: a search
of s185's system text). The criteria brief asks for behaviour in its own
words. Every criterion "names its surface", "the callables a test would
exercise". The Tester "is black-box", and "a criterion that never says
what a test would *call* is one it can only restate". "Three is usual and
six is many" (observed: `criteria.md`, as the system prompt carried it).
So the brief gives two pulls toward behaviour and one toward a count of
three, against one headline that names a docstring (reasoned: the brief's
words beside the three writes).

One fact was absent. His reply m69 on the guess page, "only the docstring
changes while the code stays the same", landed as ruling r_1ec1beb146 at
19:32:27. s185's criteria reached page m76 at 19:36:09 (observed:
`rulings`, and the principal log). The string "code stays" is not in
s185's prompt (observed: a search of the prompt). By step 6 of the wall
guide's method, an absent fact is cause 2 (observed: `plans/wall-guide.md`,
about line 776). So the night 166 read's "cause 5, the fact was in the
wake" holds for "in the docstring" and not for his stronger words
(reasoned: the two searches). Night 163 met the same gap: his "the code
does not change" at m24 and m29 did not reach c_1 (observed:
`plans/night163-read.md` 103 to 106).

The other two criteria wakes of the night show a right first turn. s116
on `get_app_dir` wrote three behaviour criteria on a behaviour ticket.
s156 on `clear()` wrote one criterion and then a second, and his m62 said
"ok" (observed: `turns` s116 and s156 seq 1, and `messages` m62). Neither
ticket names documentation (observed: `tickets`).

## 2. Whether the design decides it

The design says what a criterion is, and it admits a documentation
criterion. It says nothing on whether one item may hold criteria of one
kind only.

- What a criterion is: "Criteria describe what must be *true when it is
  done*, not how to build it" (observed: `criteria.md`). The criterion is
  the Tester's "*only material*", and it must carry a callable surface
  (observed: `rota/DECISIONS.md` 1056 to 1075, built 2026-08-26). That
  entry is a design record, not a ruling of Roman's (observed: it holds no
  ruled line). `rota/LAWS.md` names who writes criteria and defines none
  (observed: LAWS lines 56 and 101).
- A documentation criterion: "a line of a kind that does no behaviour, a
  docstring or a comment, is evidence for a criterion only when that
  criterion's own words ask for the code's documentation, with the words
  "docstring", "document" or "help text"" (ruled: Roman, 2026-10-24 01:05,
  "Yes", recorded in `rota/DECISIONS.md` 1513 to 1535). So a criterion
  that asks only for the docstring is legitimate. c_3 names
  `src/click/utils.py::format_filename` as its surface, so it also
  satisfies the surface record (observed: `criteria.surface_refs`).
- One kind only: no record in LAWS, DECISIONS or the brief says that an
  item may have criteria of one kind only (observed: searches for
  "docstring", "documentation", "one kind" and "only the docstring").

The brief and the ruling do not contradict each other. The brief is
silent on documentation. Its pulls toward behaviour date from 2026-08-26
to 2026-09-12 (observed: `git log -S` gives d579f6cf, 2026-09-12, for
"Three is usual"). The ruling is newer, 2026-10-24. The door of section 3
reads the ruling's own three words, so it carries a ruled rule from the
Critic to the Terminologist and needs no new ruling (reasoned: the
predicate uses the ruling's words, and his page replies on nights 163 and
166 say that the code stays the same). No question for Roman stands.

## 3. Whether a door can read it

No present refusal reads the ticket's headline against the kind of the
criterion. `criteria_specify` refuses an item id, a retired ticket, a
ticket of another item, an id that another ticket owns, an id reused with
new words, a text about the tests, an exact twin, a seventh criterion, a
surface that the item does not name, and an exception from no source
(observed: `rota/roles/api.py` 5736 to 5897). `_twin_refusal` reads only
the sibling tickets with no criterion (observed: `api.py` 5695 to 5718).

The rows: on each of the four nights the docstring item had one ticket.
The other tickets were `get_app_dir` and `clear()`, and their headlines
name no documentation word (observed: `tickets`). Each write below is a
landed `criteria.specify` or `criteria.respecify` text (observed:
`receipts`, with the turn that sent the call).

| Night | Writes on the docstring ticket | Called wrong by |
|---|---|---|
| 163 | s114 c_1 "returns the basename"; s114 c_2, docstring; s123 c_1 again, "returns os.path.basename(path)" | m24 and m29, "the code does not change" (`night163-read.md` 104) |
| 164 | s171 cr_1 to cr_6, all behaviour; s181 and s208 respecify all six to docstring texts | m95 and m101 contest cr_2 to cr_6, and cr_1 is respecified (`night164-read.md` 83 and 85) |
| 165 | s338 crit_1 "returns only the basename", crit_2 and crit_3, all behaviour; s412 respecifies crit_1 to "The docstring for format_filename is updated..." | m200, m244 and m249 (`night165-read.md` 156) |
| 166 | s185 c_1 and c_2, behaviour, and c_3, docstring; s194 respecifies c_1 and c_2 to docstring texts | m77 |

Predicate A: a criterion that names behaviour on a ticket whose headline
names only documentation. The door reads the ticket's headline and the
criterion's text for "docstring", "document" or "help text". It refuses 13
writes: 2 on night 163, 6 on night 164, 3 on night 165 and 2 on night 166.
The table shows each of the 13 called wrong. It refuses 0 of the writes
that name the docstring, and 0 on the `get_app_dir` and `clear` tickets.
Right criteria refused: 0 (observed: the table, counted by hand). A door
cannot read the word "only" in a headline. So the door reads "names a
documentation word", and its refusal text sends a ticket that wants code
too to `msg.challenge_vision_keeper` for a slice (reasoned: a mixed
headline such as "fix X and update its docstring" has no sample on these
nights, and the slice is the present route for a ticket with two pieces of
work, `api.py` 5889 to 5894).

Predicate B: a criterion count above the ticket's statement count. Each
item has one ratified statement (observed: `statements` s1 to s3). So the
door keeps the first write on a ticket and refuses the rest. On night 166
it keeps c_1, a wrong one, and refuses c_3, the one his m77 ruling
approved (observed: `rulings` r_a5e4b30470). It also refuses the second
`get_app_dir` criterion, which m42 asks for, "the Local folder under the
home folder when it is not", and the second `clear()` criterion, which m62
approved (observed: `criteria`, `messages`). On night 163 it keeps c_1
"returns the basename" and refuses the docstring c_2. Right criteria
refused: at least 4 over the four nights, and the door misses each wrong
first write (reasoned: the order of the writes). Predicate B is not a door.

Predicate C: a criterion whose words are not in the item, the ticket or
the project. The words "strips", "directory", "prefix", "returns" and
"basename" are in the project, because the source of `format_filename`
calls `os.path.basename` (observed: s185's prompt). So it refuses 0 of the
two wrong writes of W-E. For right criteria, the choice of which words
count, such as "invoked", "unset" and "terminal", is a judgement. The wall
guide lists a judgement-shaped guard as an overfit for cause 5 (observed:
`plans/wall-guide.md`, cause 5, "Overfits"). Predicate C is not a door.

Only predicate A has 0 wrong refusals on the four nights.

## 4. Whether it is the model's limit

The recorded cases cannot answer the question, because no criteria case
carries a documentation ticket. The three criteria cases are
`L1-TE-specify-criteria`, "add a delete button to the account page",
`L1-TE-a-new-behaviour-is-a-new-callable`, a split of a bill, and
`L3-scope-becomes-a-ticket-with-criteria` (observed:
`tests/rota/cases/l1_terminologist.yaml` 25 to 47, `l1_surface.yaml`, and
`l3_handoffs.yaml` 73). Their pass counts (observed: `case_runs`):

| Case | qwen3:8b | qwen3.5:9b |
|---|---|---|
| L1-TE-specify-criteria | 3054 of 3054 | 40 of 45 |
| L1-TE-a-new-behaviour-is-a-new-callable | 3040 of 3084 | 30 of 40 |
| L3-scope-becomes-a-ticket-with-criteria | 2435 of 2435 | no runs |

The nights are the only measure. The first criteria turn on the docstring
item wrote behaviour criteria on 4 of 4 nights, all on `qwen3.5:9b`: 1 of
2 writes on night 163, 6 of 6 on night 164, 3 of 3 on night 165 and 2 of
3 on night 166 (observed: `sessions.model` for s114, s171, s338 and s185,
and the writes of section 3). Nights 163 to 165 had no wake detail. Night
166 had the ticket's headline in the wake, and the rate was still 2 of 3
(observed: `sessions.wake_detail`). No `qwen3:8b` sample exists.

By the cause 5 ruling, the model is the last suspect, and the interview
and a stronger model on the same turn come first (ruled: Roman,
2026-10-15, `plans/wall-guide.md` cause 5). The brief's own words pull
toward behaviour (section 1), so the structure is not cleared (reasoned).
The verdict is therefore not the model's limit.

A case would carry: an item "Give format_filename one example in its
docstring", one ticket with that headline, the source of `format_filename`
in the index, and `tick: criteria`. It would expect each landed criterion
to name a documentation word, and it would forbid a criterion that names
none.

## 5. What his own words say

m42 is his reply to page m41, at 2026-10-25 18:46:21 (observed:
`messages` m42, and the principal log):

> Line 3 is wrong: it falls back to the bare home folder, which is the old
> behaviour I want to replace. When the variable is missing, the fallback
> should be the AppData Roaming or AppData Local folder under the home
> folder. Line 2 is too loose and should say the path is the Roaming folder
> under the home folder when the roaming flag is True, and the Local folder
> under the home folder when it is not.

Page m41 has no body text of its own in `messages` (observed). The night
166 read files this reply under m41. It calls two behaviour criteria wrong
on a behaviour ticket. Line 3 restates "the old behaviour I want to
replace", and line 2 is "too loose". Neither complaint is about the kind
of criterion (reasoned: his words). So m42 is not a W-E case.

m77 is his reply to page m76, at 2026-10-25 19:36:10 (observed:
`messages` m77, and the principal log):

> Lines 2 and 3 are not what I asked for. They make rules for how the
> function behaves, but only the docstring changes and the code stays the
> same.

Lines 2 and 3 of m76 are s185's c_1 and c_2. He calls them wrong because
they "make rules for how the function behaves". He gives the reason:
"only the docstring changes and the code stays the same". His m69, four
minutes earlier, said the same words about the guess page (observed:
`messages` m69). So the rule of predicate A is his rule in his words
(reasoned: m24 and m29 on night 163, m69 and m77 on night 166).

## The recommendation

Build predicate A at `criteria.specify` and `criteria.respecify`, with the
three words of the ruling, a refusal text that names the headline and
offers a docstring criterion or a slice, and a new register case for a
docstring ticket. Leave the cause 2 strand, m69 absent from the criteria
wake, as a residue for frame 306. Price: 2 cycles, about 60k on Opus and a
review, plus one case recording after a night (reasoned: a door predicate,
by the rule of 2026-10-11 05:51).
