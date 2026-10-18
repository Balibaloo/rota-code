# Frame 298, the count before shape A's pass: the files cue over nights 136 to 156

Read-only agent on Opus, 2026-10-18 11:50. Repository at HEAD 9c4b5368.
Rota workflow, read by the meta workflow. Sources: `.rota/clickI_night136.db`
to `clickI_night156.db` (night 141, 145, 147 and 148 have no request
contest), opened `?mode=ro`; the page texts from `.rota/clickI.principal.jsonl`
and the per-night copies; `.rota/night136.log` to `night156.log`. Scripts:
`extract.py`, `pages.py`, `itemline.py` and `cue.py` in
`scratchpad/f298c` of session 6977407c.

## 0. The result

1. 101 rows: every landed `rulings` row whose `per_item` puts `contest` or
   `revise` on a request item, one row per item. The rows come from 97
   rulings, because 4 rulings ruled two request items (observed:
   `extract.py`).
2. The four counts, by hand: **(a) 27, (b) 43, (c) 18, (d) 13**. The 27
   (a) rows split into 19 faults of the pointer under the request line and
   8 faults of the item's batch line on a touch or stopped page.
3. The cue fires on **19 of 19** pointer faults and on 8 of 8 batch-line
   faults, so 27 of 27. It refuses **43 of 43** right request contests (b),
   and also 18 of 18 (c) and 13 of 13 (d). There is no miss and no false
   fire (observed: `cue.py`, 2026-10-18 11:4x).
4. **The 27 of 27 is in-sample.** The cue was written against these same
   rows, and two misfits were fixed in the cue before the final run (section
   3). The count on a later night is the real count (reasoned: the cue and
   its test set are one set).
5. The split for the door's two texts: of the 19 pointer faults, **5 had a
   live batch and 14 had none**. All 8 batch-line faults had a live batch.
   No (c) reply had a live batch (observed: section 4).
6. Each of the 5 pointer faults with a live batch, and each of the 8
   batch-line faults, killed its batch. The log's `do:cancel` line follows
   the ask that the reply answered, every time (observed: the night logs).

## 1. The method

**The request item.** A row counts when `items.kind` is `in_scope`, the id is
not `how_it_works`, `item_provenance.provenance` is not `observed`, and
`is_description` is not set. This is `_is_request_item`'s rule without the
`delivered:` check, because the database holds the end state and an item
delivered later was open at the reply (reasoned: `principal.py` 533).

**The item's line.** The script finds the numbered page line whose words
best match the item's end text. Three rows matched a later line and were
fixed by hand to line 1: rows 26, 28 and 46 (observed: the page texts).

**The classes**, read by hand per row, about the item's own line:

- (a) the words fault only the files, tests or paths under the item, and
  keep the request's words. The files sit in the pointer ("code that names
  these words") under the request line, or in the item's batch line ("the
  work for:") on a touch or stopped page.
- (b) the words correct the request itself: its content, its scope, a
  missing constraint, "the wrong change", "not a request", "drop this line".
  An approval that adds a constraint, such as "Ok ... Please keep the
  new helper to the standard library json module", is (b).
- (c) both: a files fault and a correction of the request's text in one
  reply. Most (c) replies ask to take his pasted notes out of the request
  text.
- (d) neither: the words do not fault the item's line at all. Examples are
  "ok", "keep going", a request for another page, or words about other lines
  only.

Words about other lines do not change the class. Row 0 faults line 1's
files and corrects line 2's text. The class is (a), because the door rules
line 1 only (reasoned: shape A refuses the line-1 ruling and keeps the
others).

**A live batch.** The `batches` table has no time column. A batch counts as
live at a reply when a message at or before the ask names the batch in
`body_refs` or `body_text`, and the night log has no `do:merge` or
`do:cancel` line for it before the ask's `[mN]` line. "ended ('cancel', N)"
below means that the cancel line follows the `[mN]` line of the ask, so the
cancel came after that reply (reasoned: the log writes the ask line when
the reply lands). The proxy can miss a batch that no message named yet
(reasoned). For the 14 "none" pointer rows, the night's other batches of
the item start later or ended earlier (observed: the first message that
names each batch, and the log).

## 2. The four counts and the lists

| Class | Rows |
|---|---|
| (a) pointer | 19 |
| (a) batch line | 8 |
| (b) | 43 |
| (c) | 18 |
| (d) | 13 |

A ruling with two request items gives two rows, and the two rows can take
different classes: night 136 m74 is (b) twice, night 142 m110 and m129 are
(c) for echo_json and (b) for echo_json_newline, and night 142 m192 is (d)
and (b) (observed: `per_item`).

The (b) rows: 1 n136 m74; 2 n136 m74; 3 n137 m96; 5 n137 m187; 6 n138 m36;
8 n138 m145; 9 n138 m154; 11 n138 m167; 12 n138 m181; 13 n138 m187; 14 n138
m192; 15 n138 m199; 16 n138 m205; 17 n138 m209; 18 n138 m215; 27 n142 m110;
29 n142 m129; 32 n142 m192; 36 n143 m142; 38 n143 m164; 39 n143 m225; 40
n143 m264; 41 n143 m317; 44 n144 m194; 48 n144 m273; 58 n146 m259; 61 n150
m38; 62 n150 m91; 63 n150 m107; 64 n150 m115; 65 n150 m124; 66 n150 m140; 67
n150 m299; 68 n150 m310; 69 n150 m317; 70 n150 m339; 72 n151 m120; 73 n152
m25; 75 n152 m124; 76 n153 m23; 80 n155 m23; 93 n155 m249; 97 n156 m125.

The (d) rows: 4 n137 m175; 7 n138 m110; 10 n138 m161; 19 n139 m81; 23 n140
m136; 31 n142 m192; 33 n142 m356; 50 n146 m46; 59 n146 m272; 60 n149 m58; 71
n151 m46; 74 n152 m60; 77 n153 m49.

**Judgement calls** (reasoned, each a hand reading):

- Rows 64 to 66 (night 150, "Ok, I approve ... Please read line 1 as the
  details of line 2") are (b), because they ask to merge two request lines.
  They carry no files words, so (b) or (d) gives the same cue count.
- Row 42 (night 143, m359) is (a) on the batch line. Its last sentence, "add
  the Python version to the end of the message only when the flag is on",
  restates the request and does not correct it.
- Row 21 is (a). "is exported from the package top level" is the reason for
  the module, not a new demand.
- Row 84 is (c). "It also drops what I added last time" asks for words back
  in the request.

The (a) and (c) rows, with every reply verbatim:

### (a), the pointer under the request line

| Row | Night | Ask, reply | Item, ruling | Item line | Live batch at the reply (status, version, head, ended) |
|---|---|---|---|---|---|
| 0 | 136 | m48, m49 | echo_json: contest | 1 | none |
| 21 | 140 | m97, m98 | echo_json: contest | 1 | none |
| 24 | 142 | m97, m98 | echo_json_newline: contest | 1 | none |
| 25 | 142 | m101, m102 | echo_json: contest | 1 | echo_json_batch(abandoned,v1,head=y,end=('cancel', 101)) |
| 30 | 142 | m159, m160 | echo_json: contest | 1 | none |
| 35 | 143 | m119, m120 | echo_json: revise | 2 | none |
| 46 | 144 | m230, m231 | echo_json: contest | 1 | none |
| 47 | 144 | m236, m237 | echo_json: contest | 1 | none |
| 54 | 146 | m169, m170 | echo_json_support: contest | 1 | bg_4(abandoned,v1,head=y,end=('cancel', 169)) |
| 78 | 154 | m22, m24 | echo_json: contest | 1 | none |
| 79 | 154 | m119, m120 | confirm_default_on_eof: contest | 1 | b2(abandoned,v1,head=y,end=('cancel', 119)) |
| 81 | 155 | m52, m53 | echo_json: contest | 1 | bg_1(abandoned,v1,head=y,end=('cancel', 52)) |
| 83 | 155 | m69, m70 | echo_json: contest | 1 | none |
| 86 | 155 | m108, m109 | echo_json: contest | 1 | none |
| 87 | 155 | m134, m135 | echo_json: contest | 2 | none |
| 88 | 155 | m149, m150 | echo_json_tests: contest | 2 | none |
| 92 | 155 | m186, m187 | echo_json_tests: contest | 2 | none |
| 94 | 156 | m22, m24 | echo_json: revise | 1 | none |
| 98 | 156 | m191, m192 | version_option_show_python: contest | 1 | bg_3(abandoned,v1,head=y,end=('cancel', 191)) |

- Row 0, night 136, m49: "The wording of line 1 is right, but it points only at test files and not at the place where echo lives in the source, and I don't see why the context tests are on the list. Line 2 should also say that the helper uses only the standard library json module and adds no new dependency."
- Row 21, night 140, m98: "Line 1's code pointer still names only test files. It should also name the utilities module where echo lives, because the new helper goes there right after echo and is exported from the package top level. Everything else on the page looks right."
- Row 24, night 142, m98: "Line 1 has the behaviour right, but the code it points to is wrong. The options, termui and basic test files have nothing to do with echo, so the new tests belong with the echo tests in the utils tests, next to echo itself."
- Row 25, night 142, m102: "Line 7 is wrong: its check strips the newline from the output and then compares it to text that still has the newline, so the test is broken, not the helper, and it never checks that only the standard json module is used. Line 2 should also say that we drop the spaces the json module adds by default, because its default output is not compact. Lines 8 to 14 repeat what I asked for, so they are not assumptions, and line 1 should point only at the echo tests, not the termui or context tests."
- Row 30, night 142, m160: "Line 1 should point only at the echo tests in the utils tests, so drop the termui and context tests. Line 7's check is about the stdlib import, but it strips the newline and compares output, so make it check that the helper's source imports only the json module. Line 9 should keep only its first sentence, because the rest is my feedback pasted in."
- Row 35, night 143, m120: "Line 1 isn't a request, it's my answer to your earlier question, so please drop it from the page. Line 2 still only names test files, so it should also name Click's utils module, where the helper goes right below echo."
- Row 46, night 144, m231: "Line 1 is wrong because it points the work at the options, termui and basic test files, but the new helper's tests belong in the echo tests. The rest of the page looks right to me."
- Row 47, night 144, m237: "Line 12 is wrong: I never overruled the helper. I still want it added next to echo, and my note about line 1 was only about which test files it points at. On line 1, the echo tests are right, but the termui and context test files don't belong there."
- Row 54, night 146, m170: "Line 1 names the context, formatting and termui test files, but only the utils module and the existing echo tests file should change. Line 9 is wrong because the helper prints the compact JSON with one newline and does not return a string. Line 10 is also wrong because the helper should let the usual json error through, not return an error string."
- Row 78, night 154, m24: "On line 1, please take the context tests file off the list of related code and keep the two echo test files, because my change only touches echo. On line 3, please add that the helper uses only the standard library json module and adds no new dependency. Lines 2 and 3 are otherwise fine as written."
- Row 79, night 154, m120: "Line 2's first check expects the letter y, which is wrong because confirm only returns True or False; please drop it, and have the passing check set a default of True, and also note that the flag is off by default. Line 4's check fails on a broken test setup rather than on confirm itself, so please fix the test so it really closes stdin, passes a default of True, and checks that stdout and stderr stay empty. Line 1 should point only to the terminal UI test file, not the options or defaults tests, and lines 8, 9 and 11 just repeat lines 5 and 6, so please remove them."
- Row 81, night 155, m53: "Line 1 is wrong because it adds the pager and context tests, and only the echo test file should get new tests for this. Line 4 is fine. Lines 3 and 5 are garbled, so I can't tell what the tests assume there; can you rewrite them in plain words?"
- Row 83, night 155, m70: "Line 1 reads right now, but the code it names still points at the options, terminal and basic tests, and the only test file for this is the echo test file. Line 2 is fine. Line 3 is wrong, because I did answer that question: build the helper now, and fix the page so I can approve it."
- Row 86, night 155, m109: "Line 1 should list only the echo test file and the place next to echo in utils.py. The termui and context test files have nothing to do with this change. Lines 2, 3 and 4 are fine."
- Row 87, night 155, m135: "Please take line 1 off. It was only my answer to your question, not a request. Line 2 should list only the new function next to echo in utils.py and new tests in the echo test file, not the options, termui or basic test files. Lines 3 to 6 are fine."
- Row 88, night 155, m150: "Please take line 1 off. It was only my answer to your earlier question, not something I asked for. On line 2, the file list should name only the utils test file, not the options, termui or basic test files."
- Row 92, night 155, m187: "Please take line 1 off, because it was only my answer to an earlier question and not something I asked for. On line 2, the files to touch should be only tests/test_utils.py and src/click/utils.py, not the options, termui or basic test files. The other lines are fine."
- Row 94, night 156, m24: "On line 1, keep my request as written but change the code it points at: drop the terminal UI tests and the context tests, and point at the echo function in click's utils module and the echo tests. On line 3, add that the helper uses only the standard library json module and adds no new dependency. Line 2 is fine as it is."
- Row 98, night 156, m192: "Lines 2 to 4 are still wrong: each check runs with the flag off and looks for a hard-coded 3.10.0, but each one should turn the flag on and check that the message ends with "Python" and major.minor.micro taken from the running interpreter's version info. Lines 9 and 11 are wrong too, because version option already builds its own callback, so show_python only needs to be a normal keyword argument with no callback from the caller. Line 1 also names the options and defaults test files, which have nothing to do with this change, so keep the work to version option and its tests in the basic tests file."

### (a), the batch line of the item on a touch or stopped page

| Row | Night | Ask, reply | Item, ruling | Item line | Live batch at the reply (status, version, head, ended) |
|---|---|---|---|---|---|
| 42 | 143 | m358, m359 | version_option_show_python: contest | 1 | bg_6(abandoned,v1,head=y,end=('cancel', 358)) |
| 43 | 144 | m166, m167 | echo_json: contest | 1 | bg_2(abandoned,v1,head=y,end=('cancel', 166)) |
| 45 | 144 | m218, m219 | echo_json: contest | 2 | bg_3(abandoned,v1,head=y,end=('cancel', 218)) |
| 49 | 146 | m35, m36 | echo_json: contest | 1 | bg_1(abandoned,v1,head=n,end=('cancel', 35)) |
| 53 | 146 | m119, m120 | echo_json_support: contest | 1 | bg_2(abandoned,v1,head=n,end=('cancel', 119)) |
| 82 | 155 | m61, m62 | echo_json: contest | 1 | bg_2(abandoned,v1,head=n,end=('cancel', 61)) |
| 85 | 155 | m92, m93 | echo_json: contest | 1 | bg_3(abandoned,v1,head=n,end=('cancel', 92)) |
| 91 | 155 | m178, m179 | echo_json_tests: contest | 1 | bg_4(abandoned,v1,head=n,end=('cancel', 178)) |

- Row 42, night 143, m359: "Please keep going with a fix and don't drop this change. Line 5 is wrong because it still touches the Command class in core.py, and the flag belongs only to the version option in decorators.py. Keep the change there and add the Python version to the end of the message only when the flag is on."
- Row 43, night 144, m167: "Please don't give up on this change. Have the team fix the failing tests and keep going. Line 5 still lists the pager test file, and I asked to leave that file alone, so the work should touch only utils and the echo tests."
- Row 45, night 144, m219: "I'd like the team to fix this rather than drop it, so please keep going with the review. Line 5 is wrong because it plans to touch the pager test file when nothing shows the new helper broke those tests, and it leaves out the echo tests where the new helper's tests belong."
- Row 49, night 146, m36: "Line 3 isn't right: I don't want any special conversion, so objects should go straight to the standard library json module and fail with its usual error when they can't be serialized. Line 5 also goes too far, because I didn't ask for anything about the pager, so please drop the pager test and keep the new test in the existing echo tests file."
- Row 53, night 146, m120: "Line 2 is wrong because the helper should write the compact JSON and one newline to the stream the way echo does, and return nothing. Line 4 is wrong because the helper should not catch errors and should let the usual json error through when an object can't be serialized. Line 5 names the wrong files, since shell completion has nothing to do with this, and the helper belongs in the utils module next to echo, with its test in the existing utils tests rather than in new files."
- Row 82, night 155, m62: "Line 3 is still wrong. echo_json is a new function next to echo, so the work should only add it to utils.py and add new tests in the echo test file. It shouldn't change echo itself, the pager, the testing pause code or the pager tests. Line 2 is fine."
- Row 85, night 155, m93: "Line 5 is still wrong. It should only add echo_json next to echo in utils.py and add new tests in the echo test file, and it should not touch echo itself, the pager, the testing pause code or the pager tests. Lines 2, 3 and 4 are fine."
- Row 91, night 155, m179: "On line 5, tests/test_utils.py is not a new file, because it already exists and already holds the echo tests. The new tests go into that existing file. The list should also name src/click/utils.py, because the new function goes there next to echo."

### (c), the files and the request's text

| Row | Night | Ask, reply | Item, ruling | Item line | Live batch at the reply (status, version, head, ended) |
|---|---|---|---|---|---|
| 20 | 140 | m86, m87 | echo_json: contest | 1 | none |
| 22 | 140 | m119, m120 | echo_json: contest | 1 | none |
| 26 | 142 | m109, m110 | echo_json: contest | 1 | none |
| 28 | 142 | m128, m129 | echo_json: contest | 1 | none |
| 34 | 143 | m104, m105 | echo_json: revise | 1 | none |
| 37 | 143 | m152, m153 | echo_json: contest | 1 | none |
| 51 | 146 | m101, m102 | echo_json_support: contest | 1 | none |
| 52 | 146 | m112, m113 | echo_json_support: contest | 1 | none |
| 55 | 146 | m218, m219 | confirm_default_on_eof: contest | 1 | none |
| 56 | 146 | m226, m227 | confirm_default_on_eof: contest | 1 | none |
| 57 | 146 | m233, m234 | confirm_default_on_eof: contest | 1 | none |
| 84 | 155 | m77, m78 | echo_json: contest | 1 | none |
| 89 | 155 | m158, m159 | echo_json: contest | 2 | none |
| 90 | 155 | m170, m171 | echo_json: contest | 1 | none |
| 95 | 156 | m32, m33 | echo_json: contest | 1 | none |
| 96 | 156 | m40, m41 | echo_json: contest | 1 | none |
| 99 | 156 | m200, m201 | version_option_show_python: contest | 1 | none |
| 100 | 156 | m215, m216 | version_option_show_python: contest | 1 | none |

- Row 20, night 140, m87: "Line 3 stops in the middle of a word, so please finish that sentence. In line 1, the code pointer names only test files and misses the module where echo itself lives, and that module is where the new helper goes. Also, use only the standard library json module and add no new dependency."
- Row 22, night 140, m120: "Line 1 is still wrong. Please take the part about the code pointer out of my request, so it ends at "followed by a newline". Then add the utilities module where echo lives to the list of code next to the three test files."
- Row 26, night 142, m110: "Line 1 is wrong: it should keep only my first two sentences, because the rest is my earlier feedback pasted in, and it should point at the echo tests in the utils tests instead of the options, termui and basic tests. Line 7 still has the broken check, which strips the newline and then expects one, and line 2 still says the compact format is the json module's default when we actually drop the spaces it adds. Line 8 repeats line 1 and should go, and lines 13 to 19 are README text that has nothing to do with this change."
- Row 28, night 142, m129: "Line 1 is still wrong: keep only my first two sentences, and point it at the echo tests in the utils tests, not the options, termui and basic tests. Line 7's check still strips the newline before it compares, so it should compare the whole output, newline included, and line 8 should go because it repeats line 1. Lines 10 and 11 should keep only their first sentence, because the rest is my feedback pasted in, and line 13 is already answered: the work goes in the echo tests."
- Row 34, night 143, m105: "Line 3 stops in the middle of a word, so please finish that sentence. For line 1, the files you list are all tests, but the helper should sit next to echo in Click's own utils code. Please also use only the standard library json module and add no new dependency."
- Row 37, night 143, m153: "Line 4 still leaves out that the output must be compact JSON on one line, followed by a newline, so please add that. Line 1 still ends with the sentence about naming Click's utils module, so please delete only that sentence. The code it names is still only test files, so please add Click's utils module there too."
- Row 51, night 146, m102: "Line 1 names the wrong files. The context and formatting tests have nothing to do with this, and the new test belongs in the existing echo tests file, next to the helper in utils. Line 1 also no longer says to use only the standard library json module, or that the helper fails with the usual json error when it can't serialize an object, so please put both back."
- Row 52, night 146, m113: "Line 1 still names the wrong files. The context and formatting tests have nothing to do with this change, so the new test belongs in the existing echo tests file and the helper goes in utils next to echo. Please also add back that the helper uses only the standard json module and lets the usual json error through when an object can't be serialized."
- Row 55, night 146, m219: "Line 1 is not in my words any more. It should say what I asked: let confirm take a default on EOF flag that returns the default when stdin is closed instead of aborting, with the flag off by default. Its file list names the option, defaults and arguments tests, but this change belongs with the confirm tests in the terminal UI tests file. Lines 2 to 4 are fine."
- Row 56, night 146, m227: "Line 1 still doesn't use my words, and its file list still names the option, defaults and arguments tests. It should say that confirm takes a default on EOF flag that returns the default when stdin is closed instead of aborting, and that the flag is off by default. The new tests go next to the existing confirm tests in the terminal UI tests file."
- Row 57, night 146, m234: "Line 1 still isn't in my words, and its file list still names the options, defaults and arguments tests when the new tests belong next to the confirm tests in the terminal UI tests file. Line 5 is wrong because the flag is missing from confirm only because adding it is the change I asked for, so it's not a reason to block anything. Line 6 is fine."
- Row 84, night 155, m78: "Line 1 is wrong again. It names the terminal and context test files, but the only test file for this change is the echo test file. It also drops what I added last time: add the function to utils.py only, and leave echo, the pager and the testing pause code alone. Line 2 is fine."
- Row 89, night 155, m159: "Please take line 1 off, because it was only my answer to your earlier question and not a request. On line 2, the file list should name only src/click/utils.py and tests/test_utils.py, not the options, termui or basic test files, and the extra sentence about debugging and logging is not something I said. Lines 3 to 5 are fine."
- Row 90, night 155, m171: "On line 1, the files to touch should be only src/click/utils.py and tests/test_utils.py, not the options, termui or basic test files. Please also drop the sentence about debugging and logging, because I did not say it. Lines 2 to 4 are fine."
- Row 95, night 156, m33: "Line 1 still points at the wrong code. Drop the options, terminal UI and basic tests, and point it at the echo function in click's utils module and the echo tests instead. Also take my correction notes out of the request text, and keep only my original sentence plus the note that the helper uses only the standard library json module."
- Row 96, night 156, m41: "Line 1 still points at the wrong code. Drop the options, terminal UI and basic tests, and point it only at the echo function in click's utils module and the echo tests in the utils test folder. The request text should be only my original sentence plus the note that the helper uses only the standard library json module, with my correction notes taken out."
- Row 99, night 156, m201: "Line 1 still names the options and shell completion test files, which have nothing to do with this change, and it mixes in my notes about the tests. Line 1 should only say to add the show_python flag. Lines 5 and 8 are wrong because they remove existing code, which would break the normal version message when the flag is off, so keep all current behaviour and only add the Python version when the flag is on."
- Row 100, night 156, m216: "Line 1 is still wrong. It should only say to add a show_python flag to version_option that appends the running Python version, and the work should touch only version_option and the basic tests file, not the options or shell completion test files. Lines 2 to 4 are fine."

## 3. The cue as code

**The predicate reads the words clause by clause, and keeps only the
clauses about the item's line or its batch line** (reasoned: the replies
correct several lines at once, and a fault of line 7 says nothing of line
1). A clause with no line number is about the line of the clause before it.
The first clause with no line number is about the page as a whole, and the
predicate reads it.

It fires when at least one kept clause faults files and no kept clause
corrects the request's text. It reuses `_LINE_REF`, `_ref_lines`,
`_BARE_AGREEMENT` and `_KEEP_CHANGE` from `rota/roles/api.py`. It does not
use `_quotes_line`. The clause rule separated the classes without it (observed: the counts below).

```python
# --- the cue ---------------------------------------------------------------
# Files talk: tests, a path, a file, a non-json module, where the line points.
FILES = re.compile(r"\btests?\b|\w\.py\b|\bfiles?\b|(?<!json )\bmodule\b|"
                   r"\bpoints?\b|\bpointer\b|\bfile list\b|\btouch(?:es)?\b", re.I)
# Words that correct the request's own text, even beside files talk.
REQUEST_TEXT = re.compile(
    r"\bsays\b|\bshould (?:only |also )?say\b|\bmy words\b|"
    r"\bmy (?:own )?(?:first|original|earlier)\b|\bsentences?\b|\bpasted\b|"
    r"\brequest text\b|\bout of my request\b|\bcorrection notes?\b|"
    r"\bmix(?:es)? in\b|\bnot a request\b|\bisn't a request\b|\bwrong change\b|"
    r"\bdrops what\b|\bput (?:both|them|it) back\b|\badd(?:ed)? back\b", re.I)
AGREE = re.compile(r"\b(?:right|fine|reasonable|good|correct|match(?:es)?|"
                   r"as written)\b", re.I)
FAULT = re.compile(r"\b(?:wrong|not|never|only|drop|instead|should|remove|"
                   r"take|but)\b|n't\b", re.I)
BARE_FAULT = re.compile(r"^\W*(?:on\s+)?(?:lines?|notes?)\s+[\d ,toand-]+\W*"
                        r"(?:is|are)\s+(?:still\s+|also\s+)?wrong(?:\s+again)?\W*$",
                        re.I)
KEEP = re.compile(_KEEP_CHANGE.pattern + r"|\btry again\b|\bfix (?:the )?failing\b"
                  r"|\brather than drop\b", re.I)
CLAUSE = re.compile(r",\s+(?:and|but)\s+|\s+but\s+|:\s+|;\s+|,\s+so\s+")


def clauses(words):
    """Each clause with the lines it is about. A clause with no line
    reference is about the lines of the clause before it."""
    out, last = [], None
    for sent in re.split(r"(?<=[.!?])\s+", (words or "").strip()):
        for cl in CLAUSE.split(sent):
            refs = set()
            for r in _LINE_REF.finditer(cl):
                refs |= _ref_lines(r, 60)
            if refs:
                last = refs
            out.append((cl, set(last) if last else None, sent.rstrip().endswith("?")))
    return out


def pointer_fault(words, line, batch_lines=frozenset()):
    """The words fault only the files under request line `line` (its pointer)
    or under the item's batch line, and correct none of the request's text."""
    files = content = False
    for cl, refs, question in clauses(words):
        if refs is not None and not (refs & ({line} | set(batch_lines))):
            continue            # about another line
        if question or KEEP.search(cl) or _BARE_AGREEMENT.fullmatch(cl):
            continue
        if BARE_FAULT.match(cl):
            continue
        has_files = bool(FILES.search(cl))
        if AGREE.search(cl) and not FAULT.search(cl):
            continue            # "the echo tests are right", "line 2 is fine"
        if REQUEST_TEXT.search(cl):
            content = True
        elif has_files:
            files = True
        elif refs and refs <= set(batch_lines):
            continue            # a batch line holds only files
        else:
            content = True
    return files and not content
```

`batch_lines` are the page's lines that start with "the work for:", for the
item. On a present page the set is empty.

**The counts** (observed: `cue.py`, 2026-10-18 11:4x):

| Class | Fires | Of |
|---|---|---|
| (a) pointer | 19 | 19 |
| (a) batch line | 8 | 8 |
| (b) | 0 | 43 |
| (c) | 0 | 18 |
| (d) | 0 | 13 |

So the cue fires on 27 of 27 files faults (19 of 19 pointer faults), and
refuses 43 of 43 right request contests, with 31 of 31 (c) and (d) rows
refused too. There is no miss and no false fire in this set.

**The two fixes made while the cue was written** (observed: `cue.py`
before the final run):

1. Rows 46, 26 and 28 read the wrong item line. The page match picked a
   later line. The fix is to the test data, not to the cue.
2. Rows 42, 49 and 82 missed. Their batch-line clauses say "goes too far,
   because I didn't ask for anything about the pager", "echo_json is a new
   function next to echo" and "add the Python version ... only when the flag
   is on". These name no file, so the first cue read them as request text.
   The fix: a clause about the batch line alone is neutral unless it has a
   request-text word, because a batch line holds only files (reasoned: the
   touch line of `batch_touch`).

**`_FILES_TALK` alone is too narrow for the pointer.** With
`_FILES_TALK` in place of `FILES`, the cue fires on 15 of 19 pointer faults
and on 8 of 8 batch-line faults. It misses rows 21, 24, 35 and 94: "code
pointer ... utilities module", "the code it points to is wrong", "names test
files ... utils module", and night 156's m24, "change the code it points at"
(observed: `cue.py` with the swap). The wider `FILES` adds "file", "module"
other than the json module, "points", "pointer", "file list" and "touch".
"file" stays out of `_FILES_TALK` for a reason: "write to a file" corrects
the request (copied: the `_FILES_TALK` comment, frame 258). Here `FILES`
fires only together with no request-text clause on the same line, so that
risk is smaller, but it is not measured (reasoned).

**Risks to check before the pass** (reasoned):

- The words "says", "sentence", "pasted", "my words" and "my original" carry
  the (c) refusals. A files fault phrased as "line 1 says test_options.py"
  would not fire. No reply in the set says that.
- Neutral clauses are the bare fault ("Line 1 is still wrong"), agreement
  with no fault word, a question, and a keep-change sentence. A request
  correction phrased as a bare question would pass as neutral.
- Night 156's three deaths: the cue fires on m24 (row 94) and m192 (row 98).
  It refuses m33 and m41 (rows 95, 96, "take my correction notes out of the
  request text"), m201 and m216 (rows 99, 100), and m125 (row 97, frame
  296's case). So shape A alone stops bg_3's death and the first echo_json
  amendment, and it leaves the later (c) loop to his words (observed: the
  rows; reasoned: the door).

## 4. The split for the door's two texts

| Class | Live batch | No batch |
|---|---|---|
| (a) pointer | 5 | 14 |
| (a) batch line | 8 | 0 |
| (c) | 0 | 18 |

(observed: section 2's tables.)

**All 5 live batches under a pointer fault had a head commit**: night 142
echo_json_batch, night 146 bg_4, night 154 b2, night 155 bg_1 and night 156
bg_3. Each was at version 1 and ended `abandoned` by the `do:cancel` that
followed the reply (observed: `batches`, the night logs).

**This matters for shape A's first text** (reasoned: `rulings_rule` and
`built_line_faulted` in `rota/roles/api.py`). After the head commit, the
batch door admits a contest or revise of the batch only when
`built_line_faulted` finds the batch's line in `order` and in the faulted
lines. On a present page the batch is not in `order`, so an off-page
`bg_3: contest` that the refusal invites would meet the batch door's own
refusal, "the words do not fault bg_x's files". The pass must admit the
off-page batch key on the files cue itself, or the first text sends the
seat into a second refusal. All 5 live cases are after the head commit.

**The 14 no-batch cases take the second text**, "approve line 1. No change
exists yet to correct". The files words then reach no owner, as in section
4 of `plans/frame298-investigation.md` (reasoned).

## 5. Register lines

None written. This frame writes only this report.
