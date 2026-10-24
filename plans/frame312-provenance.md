# Frame 312, the provenance: the page after a review with no verdict, and the shift page's row for a parked batch

Written 2026-10-24 01:20 by a reader on Opus, read-only, at the branch head
`c42ece2e`, over `.rota/clickI_night1NN.db` with `?mode=ro`.

## 1. The verdict

The two pages are built from rows that do not separate a review that landed
no verdict from work that failed. The stopped page uses one text for every
quarantined key. The shift page does not read `tick_attempts` at all. So on
night 160 he read "stopped work" on a green change, and later read "nothing
from you" on the same stuck change, and parked it (observed: sections 2 to 4).
No reply of his has a lever that revives a review quarantine, so m46 could
not restart the review even if a seat had understood it (observed: section 3).

## 2. The text and its commit

- The text "The team stopped work on this change." is in
  `rota/roles/principal.py`, `render_page`, line 1616, in the branch
  `verb == "present" and keys and touches` (observed: the file).
- `git log -S` names one commit: `358fed11`, 2026-10-09, "every page to the
  principal numbers the request's own lines first", frame 190, pass 1
  (observed: git). The code comment names the case: "Night 136's m96 opened
  'Before I build this' on a batch the Tester had given up on (frame 190's
  design, 2.F, amendment 6)". That case is a Tester's `tests_missing`
  quarantine, which is not a review.
- The state the text reads: `door_rows(conn, ask_id, "stalled")`, which is
  the `config` row `stalled:<message id>`, the quarantined keys of the wake
  that sent the page. A batch ref with no resolved row makes `touches`
  non-empty (observed: `render_page`, `door_rows` at line 1819).
- The kind of key does not change the heading. `_stalled_words` (line 1277)
  adds one line, "The team gave up on: review for bg_1, 3 attempts.", from
  the key and `tick_attempts.attempts` (observed: the file and m45's page).
- So one text serves a code fault and a green review. Night 160 shows both
  on bg_1: m34 had the key `developer|tick:tests_failing|bg_1`, and m45 had
  `critic|tick:review|bg_1`. Both open with "The team stopped work on this
  change." (observed: `config` rows `stalled:m34` and `stalled:m45`). Over
  nights 140 to 160 the 49 stopped pages carry these keys:
  `tests_failing`, `tests_missing`, `review`, `verdict_failed`,
  `batch_start` and `touch_strayed` (observed: section 5's script output).
- The tick names and attempts already show. What the page does not say is
  that the code is built and its tests pass, that the review landed no
  verdict, and how to restart the review.

## 3. m45 and m46

- The page m45, as the Liaison s152 received it in `landing.page`
  (observed: `turns`, s152 turn 1):

  ```
  The team stopped work on this change.
  You asked:
    1. Add an echo_json(obj) helper next to echo that prints an object as compact JSON on one line, followed by a newline.
  It must:
    2. The function `echo_json` must not print any additional text (such as labels or prompts) before or after the JSON output.
       check: echo json output, calls output = f.getvalue(), expects output == "{\"y\":2}\n". Passes.
  The team gave up on: review for bg_1, 3 attempts.
  The team expects to touch:
    3. the work for: Add an echo_json(obj) helper ...; expected to touch src/click/utils.py, tests/test_utils/test_echo.py, tests/test_utils/test_echo_json.py (a new file)
  Reply 'ok' if every line says what you want. Name a line to correct only that line. Ask, if something here is unclear. To change what you asked for, name line 1.
  ```

- The sender: s151, a Liaison woken by `tick:quarantined` with the detail
  "1 abandoned: review for bg_1 (critic), 3 attempts", called
  `msg.present_principal(refs=['bg_1'])` (observed: `sessions`, `turns`).
  The quarantine came from five Critics, s145, s146, s148, s149 and s150,
  on `tick:review` of bg_1 (observed: `sessions`). The key
  `critic|tick:review|bg_1` has `attempts` 3, `quarantined` 1, `reported` 1
  at the night's end (observed: `tick_attempts`).
- The code was right. All 35 runs of bg_1 pass at `8877b1b8`, the only head
  commit (observed: `test_runs`). The review tick fires only on a green
  harness at the head with a test for every criterion
  (`rota/core/predicates.py`, `review`, line 1336).
- His reply m46: "Line 2 and its check now say what I want, and the test
  passes. What did the review object to, since the page does not say? I want
  the team to fix that problem and finish this change, not drop it."
  (observed: `messages`).
- The seat that read m46: s152, a Liaison. Its first call was
  `rulings.rule({"1": "approve", "2": "approve", "3": "contest"})`. The door
  refused: "line 3: the words do not fault bg_1's files. Approve line 3."
  The seat then approved all three lines, and the ruling `r_bd1555ee6f`
  landed with every line approve (observed: `turns`, `rulings`). The refusal
  is in `rota/roles/api.py` at line 11312, frame 255's predicate
  `built_line_faulted`: a contest on a built batch line lands only if the
  words fault its files.
- Why no seat answered or restarted the review:
  1. The Liaison's path for a reply to a page is the ruling. The ruling has
     no answer to a question and no "review again" outcome. His question was
     stored only as the ruling's `words` (observed: `rulings.words`).
  2. The approves moved no row. `echo_json` was already approved, and an
     approve of the batch line writes nothing to `batches`. A quarantined
     key revives only when a commit moves a row its refs name, or moves a
     criterion or test of the batch (`rota/core/db.py`, lines 585 to 650,
     "Law 6: ... only a move revives"). So `critic|tick:review|bg_1` stayed
     quarantined.
  3. No message after m46 names bg_1 for the rest of the night (observed:
     `messages`, seq 47 to the end).

## 4. The shift page

- The builder: `_shift_page` in `rota/roles/principal.py`, line 1388, with
  the rows from `_shift_where` (line 1332) and `_shift_waits` (line 1359).
  All three came in `61a0f41d`, 2026-10-10, "the shift question of frame
  193, pass 2" (observed: `git log -S "Where it stands"`).
- `_shift_where` reads `items.approval`, the live batch in `batches`, and
  the newest run of each test in `test_runs`. `_shift_waits` reads open
  pages to the principal and open `ledger` notes. Neither reads
  `tick_attempts` (observed: the file).
- The quarantine is readable from the tables. The row
  `critic|tick:review|bg_1`, `quarantined` 1, is in `tick_attempts` before
  the shift page and to the night's end. The key ends in the batch id, the
  same LIKE form that `db.py` uses (observed: `tick_attempts`).
- The page that m53 answered, ask `m_shift_echo_json_m_p2`, refs
  `["echo_json", "s2"]` (observed: `turns`, the session woken by m53,
  `landing.page`):

  ```
  You asked for something new: Let confirm() take a default_on_eof flag: when stdin is closed it returns the default instead of aborting.
  Before that you asked for this, and it is not finished:
    1. Add an echo_json(obj) helper next to echo that prints an object as compact JSON on one line, followed by a newline.
       Where it stands: approved. The change bg_1 is built, and all 35 of its tests pass.
       What it waits on: nothing from you.
  Choose one for line 1:
    - later: put it aside until the new request is merged. Nothing more about it reaches you until then.
    - now: answer its open page first, then the new request.
    - drop: stop it. Its change is abandoned.
  ```

- "What it waits on: nothing from you." is false. bg_1 waited on a review
  that was quarantined, and only a move could revive it. m45 was answered,
  so `_shift_waits` found no open page.
- His reply m53: "Later. Line 1 is approved and built, and it needs nothing
  from me, so leave it until the confirm change is merged." The ruling
  `r_dc97bf8e7c` landed `{"echo_json": "park"}` with verdict m54, and
  `item_parks` row `ip_b7fdebfb5d` parked the item by `shift`. bg_1 ends the
  night `deferred` (observed: `rulings`, `item_parks`, `batches`). His words
  repeat the page's two rows.

## 5. The count with its query

Over `.rota/clickI_night140.db` to `clickI_night160.db`, all 21 exist:

| Measure | Count |
|---|---|
| Pages that say "The team stopped work" (a `stalled:` key and a batch ref) | 49 |
| Of those, the stalled key is a review tick, so the last runs passed | 11 |
| Of the 11, a later ruling of his parked the batch's item | 6 pages, by 4 replies |
| Of the 11, a later ruling dropped it | 0 |

The 11 pages: night 144 m218; night 153 m132; night 155 m48; night 157
m183; night 158 m34, m135, m148; night 160 m45, m84, m89, m94. The 4 park
replies: night 144 m255, night 155 m203, night 160 m53 (for m45), night 160
m135 (for m84, m89, m94). Every park came from a shift page, and none came
from a reply to the stopped page itself (observed: the script output).

Limit: "the last test run passed" is read from the key, not from a dated
run. `predicates.review` fires only on a green harness at the head, and a
new head commit revives the key, so a quarantined review key means green at
its last wake. `test_run_journal` cannot date runs against a page: it exists
on night 160 only, and its `seq` is its own counter, not the message `seq`
(observed: the tables). On night 160 the end state confirms 35 of 35 pass
for bg_1.

The script is
`C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/0cdcac52-3588-4266-b1fb-fc5d7d31b805/scratchpad/f312_count.py`.
Its queries:

```sql
-- the stopped pages
SELECT m.id, m.seq, m.body_refs, cf.value AS keys FROM messages m
JOIN config cf ON cf.key = 'stalled:' || m.id
WHERE m.to_role = 'principal' AND m.verb = 'present'
  AND cf.value NOT IN ('[]', '') ORDER BY m.seq;
-- keep a page when one body ref is in batches, and green when a key holds '|tick:review|'
-- his later park or drop of that batch or its item
SELECT r.ask_id, r.reply_id, r.per_item FROM rulings r
JOIN messages m ON m.id = r.reply_id WHERE m.seq > :page_seq
  AND (r.per_item LIKE '%"park"%' OR r.per_item LIKE '%"drop"%')
  AND (r.per_item LIKE '%"' || :item || '"%' OR r.per_item LIKE '%"' || :batch || '"%');
-- then keep a row when per_item[item] or per_item[batch] is park or drop
```

## 6. The repair

Each option names the file and the function.

- A. The stopped page: in `rota/roles/principal.py`, `render_page`, the
  stalled branch, a key of kind `tick:review` opens with "The review of this
  change landed no verdict after 3 attempts. The code is built and its tests
  pass." in place of "The team stopped work", and it offers one reply that
  restarts the review.
- B. The shift page: in `rota/roles/principal.py`, `_shift_where` and
  `_shift_waits`, read the quarantined `tick_attempts` keys that end in the
  live batch id. Name the stuck tick and its attempts, and say that the
  change waits on a restart of its review, not "nothing from you".
- C. The restart lever: in `rota/roles/principal.py`, `land`, an approve of
  the batch line on a page whose `stalled:` keys hold a review tick deletes
  that one quarantined key, as a recorded move under `db.py`'s revive rule.
  Without C, the restart that A offers moves nothing, the same way m46 moved
  nothing.

Recommendation: one helper, for example `_stuck_words(conn, batch)` beside
`_stalled_words`, that reads the batch's quarantined keys from
`tick_attempts` and says per key kind whether the code failed or the review
landed no verdict. `render_page`'s stalled branch (A) and `_shift_where` and
`_shift_waits` (B) both call it, so the two pages cannot disagree again.
C is the lever. C needs a ruling before a build, because it lets a reply
lift a quarantine that law 6 and `db.py` lift only on a move. One revive per
key per ruling keeps the bound. This keeps frame 190's stalled page and
`_stalled_words` (2.F, amendment 6), frame 193's shift page with its three
answers (2.F.2), and frame 255's refusal of a contest that does not fault
the files.

The red tests:

1. m45: a fixture with the batch row `bg_1`, `item_id` `echo_json`,
   `head_commit` `8877b1b8...`, status `running`; 35 `test_runs` of bg_1 at
   that commit, all `pass`; `tick_attempts` row `critic|tick:review|bg_1`,
   attempts 3, quarantined 1; `config` `stalled:m45` =
   `["critic|tick:review|bg_1"]`; message m45 with refs
   `["bg_1", "echo_json", "echo_json_helper"]`. Today `render_page` returns
   "The team stopped work on this change." first. The test asks for the
   no-verdict text, the tick, 3 attempts and a restart reply. With C, the
   landed approve of line 3 deletes the key and `predicates.review` wakes
   the Critic again.
2. m53: the same batch and tick rows, item `echo_json` approved, statement
   `s2`, ask `m_shift_echo_json_m_p2` with refs `["echo_json", "s2"]`, and
   m45 answered. Today `_shift_page` shows "What it waits on: nothing from
   you." The test asks for the stuck review and its 3 attempts on line 1.

## 7. Usage

About 47k tokens in this reader's context, over the 40k cap. One script was
run against read-only connections. Nothing in the repository was edited
except this report.
