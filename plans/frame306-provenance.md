# Frame 306, the provenance: the principal's words on a page do not reach the criterion, and a change outside the criteria merges with no page that shows it

Provenance read on Opus, 2026-10-23, by the ruling of 2026-10-18 12:02
(every new wall gets a provenance read before its first fix). Repository at
HEAD 4293e3d6. Sources: `rota/roles/api.py` (`rulings_rule` 10189 to 10593,
`_faulted_approve` 9915, `_pass_lines_check` 11782), `rota/core/runner.py`
2239 to 2283 and 286 to 298, `rota/core/sandbox.py` 3900 to 3990,
`rota/core/scheduler.py` 1748 to 1903, `rota/core/lifecycle.py` 704 to 802,
`rota/core/config.py` 70, `rota/LAWS.md` 218 and 233, `rota/DECISIONS.md`
155 and 1485 to 1505, `plans/composition.md` 8 to 26,
`plans/frame213-scope.md`, `plans/night158-read.md` sections 2 and 5,
`git log -S`, `.rota/clickI_night150.db` to `.rota/clickI_night158.db`
opened `?mode=ro`, and the sample tree `D:/repos/_AI/sample_repos/clickI`
(git read-only). Meta workflow. No file but this one is changed.

## The provenance in one paragraph

His m145 words stopped in three doors in series, and each door is a
separate design. The prompt shows the reply's `about` from the asker's
refs, but the ruling door keys on the clarify's own refs, so s286's
revise of cr_2 was refused (observed: `runner.py` 2259, 9c5c71fe of
2026-09-08; `api.py` 10330, a268266b of 2026-09-18). The seat then ruled
the test row approve, and no door reads an approve against the words on a
clarify, because frame 250's door reads numbered lines only (observed:
f0b2924c, 2026-10-16). Even a landed revise of cr_2 on a clarify would
wake the Terminologist in `relay` mode, which cannot respecify (observed:
`park_criterion_relay`, f252df24 of 2026-10-13, maps ruled tests only).
The evidence half has no page at all. The merge gate checks criterion to
line, never line to criterion, and no page shows a diff (observed:
1663c2bb, 2026-10-07; `principal.py`). The composition makes merge
sign-off opt-in, and the opt-in setting `merge_gate = review` blocks with
no page behind it (observed: `config.py` 70, `lifecycle.py` 799).

## 1. The hop from a page reply to the criteria

**The words of m146 reached the `rulings.words` column and stopped there**
(observed: `rulings` r_ac84d845ff, per_item `{tst_version_option_shows_python_02:
approve}`, texts `{}`). The chain on night 158 was this:

1. Critic s288's challenge m144 named cr_2 and tst_02 (observed: `messages`
   m144 body_refs).
2. Liaison s285 woke on `tick:unresolved` for m144 and sent the clarify
   m145 with refs `[tst_02]` only (observed: `tool_calls` s285 seq 8).
3. The principal answered m146: "Do not put parentheses around it"
   (observed: `.rota/night158.log` line 151).
4. Liaison s286 read an `answering.about` of `[cr_2, tst_02]`, built from
   the asker m144 (observed: `turns` s286 t1; `runner.py` 2259 to 2261).
5. s286 ruled `{cr_2: approve, tst_02: approve}`. The door refused cr_2:
   "is not a row of this question ... each key is a row id from `about`:
   tst_version_option_shows_python_02" (observed: `turns` s286 t2). The
   door's `about` is m145's body_refs, not the prompt's (observed:
   `api.py` 10255 to 10334).
6. s286 ruled `{tst_02: approve}` with the words and relayed. The relay
   split sent the test row as its criterion to the Terminologist as m147
   (observed: `sandbox.py` 3953 to 3958; `messages` m147).
7. `park_criterion_relay` counts a criterion only from a verdict or from a
   test row ruled contest or revise. The test was approved, so s287 woke in
   `relay` mode, tried `glossary.adopt` on cr_2, was refused, and ended
   (observed: `turns` s287 t1 to t6; `scheduler.py` 1893 to 1903).
8. cr_2 kept "must contain the word "Python" ... ", written by s274 after
   m136 (observed: `receipts`, no criteria row after s274). The test
   passes on "(Python 3.14.2)", and bg_3 merged (observed: night 158 read,
   W1 b).

**The designs that made each stop.**

- The prompt's `about` is from 9c5c71fe, 2026-09-08, "an answer reaches the
  desk that asked": "The chain holds the context: answer, clarify, the ask
  that caused the clarify" (observed: `runner.py` 2239 to 2247).
- The clarify door is from a268266b, 2026-09-18, "a ruling parks the word":
  "A clarify takes a partial map, and each row the map leaves out is
  parked, not approved" (observed: `api.py` 10256 to 10267). Neither commit
  names the other's set, so the two `about` sets were never compared
  (reasoned).
- The faulted-approve door is f0b2924c, 2026-10-16, frame 250: "An approve
  keeps the line as it is, and his words reach nobody" (observed:
  `api.py` 9960). It reads page line numbers, and "A clarify numbers no
  line" (observed: `api.py` 10256). So the door's own sentence describes
  m146, and the door cannot fire on it (reasoned).
- The repair-mode key is f252df24, 2026-10-13, frame 213 pass 1b: "a ruled
  test row wakes the Terminologist in the repair mode" (observed: the
  commit body). A criterion ruled directly on a clarify is not in that
  set, so frame 213 closed route B for a test row and left it open for a
  criterion row (reasoned: `scheduler.py` 1764 to 1769 needs a verdict).
- The ruling that every one of these serves is Roman's of 2026-10-08,
  point 4: "Every word of the principal is a ruling on a row, or it earns
  one Liaison question that names a row" (ruled: Roman, 2026-10-08, quoted
  in `plans/frame213-scope.md` 220). Point 2 adds "The principal never
  rules on a test" (ruled: the same).

**The same shape before night 158.** Frame 213's scope counted night 144's
m312 as route B, yet its ruling was "all approve" (observed:
`plans/frame213-scope.md` line 60). Route B moves only a contest or a
revise, so m312 was the m146 shape and did not move (reasoned: `scheduler.py`
1900). The scope's count of 4 of 4 route B cases is 3 of 4.

## 2. The evidence page before a merge

**No page shows the principal a diff, before or after a merge** (observed:
`rota/roles/principal.py`, the page renderers `render_page`,
`request_block`, `_park_page` and `code_line`). The pages show:

- the request lines and each criterion with its check line;
- a code line: "The team's guess at the code this touches", or "The team's
  plan of the code this touches: expected to touch ..." (observed:
  `principal.py` 1108 to 1142);
- a park page, "The team stopped work on this change", with the criteria
  and the tests' state.

**The merge needs no page.** `mergeable` holds a batch on a missing test,
no verdict, a failed verdict, an unjudged file stray, a failing test, a
missing structural review, a violated constraint and an owing seat
(observed: `lifecycle.py` 704 to 797). Then `merge_gate = review` returns
"waiting on the principal's review", and nothing else reads that state
(observed: `lifecycle.py` 799; `git grep merge_gate`). The setting has
been `auto` on nights 150 to 158 (observed: `config`, no `merge_gate` row).

**The rulings and designs.**

- "Sign-offs after that, including on merges, are opt-in" (ruled: Roman,
  2026-09-16, `plans/composition.md` 22 to 23, commit 9f8cbdf5).
- "PR versus auto-merge is a config switch ... a diff-level gate is
  redundant when supervised and essential when unattended" (ruled:
  DECISIONS, 035ad351, 2026-08-11, `rota/DECISIONS.md` 153 to 155).
- `merge_gate` with "auto" and "review", "trust should not increase on a
  schedule" (observed: 7e3be756, 2026-08-09; `rota/LAWS.md` 218). The
  `review` value was built as a block with no page (reasoned).
- "the Critic names, for each criterion, the line of the change that meets
  it ... The door cannot see whether the line meets the criterion"
  (ruled: Roman, 2026-10-07 08:57, `api.py` 11785, commit 1663c2bb). The
  map runs criterion to line. No door maps a line to a criterion
  (observed: `_pass_lines_check`).
- Law 12: the touch set "is a prediction, never a permission. Nothing
  rejects a diff for straying outside it", and the Architect judges each
  stray path (ruled: Roman, 2026-10-17, `rota/DECISIONS.md` 1489 to 1499).
  The route works per file, so a change inside a predicted file is never a
  stray (observed: frame 114's history read, `plans/stack.md` 2215).

**bg_1 and `separators`.** s120 committed `json.dumps(obj,
separators=(',', ':'))` at 42415b9. s133, on `tick:tests_failing`,
committed 3f89c75 and 055b2dc, "Remove separators argument from json.dumps
to use default formatting with spaces", because the test expected spaces
(observed: clickI `git log -S separators`; `tool_calls` s133). Critic s135
passed with the line `file.write(json.dumps(obj))` for `echo_json_helper`,
whose text says "compact" (observed: `verdicts`). The principal's last
pages on bg_1 were m29, the touch note before the build, and m34, the park
page before s133 (observed: the log, lines 32 and 38). **No page showed
the `separators` change**, and the merge ran at 75cf8ed (observed: the log
line 45).

## 3. The composition's line against the records

**The records do not meet "no work happens that the Principal did not ask
for, and no work stays invisible"** (reasoned: sections 1, 2 and 4). Six of
twelve merged batches hold a hunk no criterion names, and no page showed
any of them (observed: section 4).

The build tested the condition from four sides and left one open:

- Did the work touch an unpredicted file? Tested, the stray route
  (cf067ce4, 2026-09-13).
- Did the work add an unpredicted definition? Tested, frame 286's
  definition-level stray (64fa6b6a, 2026-10-18).
- Does each criterion have a test and an added line? Tested, `mergeable`
  and the 2026-10-07 door.
- Did the principal's words reach a row? Tested on numbered pages only,
  frame 250's door.
- **Does every hunk of the merged diff answer a criterion, and did he see
  the hunks that do not?** Untested. No door, no page and no instrument
  reads it (observed: section 2). The night report counts "1 change built,
  tested and merged" as the good line (observed: the log, line 49).

Night 158's read found W1 by a manual run of clickI `main`, not by any
count of the build (observed: `plans/night158-read.md` section 2). The
instrument that would see it does not exist (reasoned).

## 4. The counts over nights 150 to 158

**Merged batches: 12 in 9 nights. 6 hold a source hunk no criterion
names, and 2 more hold code against the request with every hunk named**
(observed: `batches`, `criteria`, and `git diff -U0` of each head against
the night's base in clickI, `src/` only).

| Night | Batch | Unnamed hunk | Judged |
|---|---|---|---|
| 151 | bg_2 echo_json | no | compact, all named |
| 151 | bg_3 confirm | yes, cosmetic | two blank lines removed, typo "a" to "an" in the base |
| 152 | bg_1 echo_json | yes | an `nl` parameter and `obj=None` that prints nothing |
| 152 | bg_2 confirm | yes, dead | `import sys` in `confirm` with no use |
| 152 | bg_3 version_option | yes | `param_decls` default added, and no code appends the version |
| 153 | bg_1 echo_json | no, against the ticket | `print(json.dumps(obj))`, spaces; the criterion did not say compact |
| 153 | bg_2 confirm | no | all named |
| 154 | b1 echo_json | yes | `file` and `nl` parameters |
| 154 | b3 confirm | no | a `False` for a `None` default, inside the criterion |
| 156 | bg_1 confirm | no | all named |
| 158 | bg_1 echo_json | no, against the criterion | `separators` removed, spaces against "compact" |
| 158 | bg_3 version_option | yes | `ctx.exit()` removed, a duplicate block, three `versionchanged` entries deleted |

How I judged: a hunk counts when it changes behaviour, the public surface
or base text that no criterion of the batch names. A docstring or a
`versionadded` note for the asked parameter counts as named (reasoned).
Four of the six change behaviour or the surface (reasoned).

**His page replies, sampled on nights 156, 157 and 158: 24 replies fault
a criterion or a test row, and 11 of them left the faulted criterion with
no later write** (observed: `rulings` with words and a contest, a revise,
or an approve whose words fault the row; `receipts` of `criteria` in later
sessions; script in the scratchpad, `f306_q4.py`). Night 156: 4 of 7
(m165, m179, m186, m191). Night 157: 5 of 12 (m110, m139, m183, m205,
m210). Night 158: 2 of 5 (m89, m145).

How I judged: a reply faults a row when its words say a line is wrong or
must change. The count is an upper bound. Some words fault the check and
not the criterion text, and route B then rewrites the test, not the
criterion (reasoned: frame 213, fix 2). m145 is not of that kind: cr_2's
"contain" admits the parentheses he refused (reasoned).

## 5. The repairs, their prices, and the doubt

**Half 1, the hop.** One `about` set for the prompt and the clarify door,
the asker's refs with the clarify's, so a criterion the asker named is a
key. A criterion ruled contest or revise on a clarify reply wakes
`criterion_repair`, as a ruled test row does, and an approve on a clarify
whose words fault the row is refused as frame 250 refuses it on a page.
Price: 2 cycles, red test s286 turns 1 and 2 of night 158, and night
144's m312 as the second case (reasoned). It crosses no ruling. It carries
out point 4 of the 2026-10-08 ruling (reasoned: section 1).

**Half 2, the evidence.** The Critic's pass maps each added hunk to a
criterion, and a hunk no criterion names becomes a hunk-level stray that
the Architect judges, as law 12 routes a file. The end page and the night
report list every merged hunk that no criterion named, as a notice with no
question. Price: 3 cycles, red tests night 158's bg_3 diff and night 152's
bg_1 diff (reasoned). This crosses no ruling. It holds the merge as a
file stray holds it and refuses no write (ruled: Roman, 2026-10-17).

**A question to Roman, only if he wants more.** A page that shows the diff
and waits for him before every merge crosses the composition: "Sign-offs
after that, including on merges, are opt-in" (ruled: 2026-09-16). So
`merge_gate = review` gets a page only as his opt-in, and a default of
`review` is his ruling to make (reasoned).

**The doubt.**

- A hunk-to-criterion map is the same judgement the Critic failed on
  night 158. It passed `separators` and a duplicate it named itself
  (observed: `verdicts`). The map would not have caught bg_1, because the
  `separators` hunk is named and wrong. That is frame 201's half, not this
  one (reasoned).
- Version notes sit in 8 of 12 merged diffs, and docstrings in all 12. A strict map
  floods the Architect, and a loose one admits 151's cosmetic edits
  (reasoned: section 4 table).
- The reply count rests on a lexical reading of "faults" and on any later
  criteria write. Both are coarse (reasoned).

## Usage

The harness count is not visible to this agent. The meta workflow takes
the harness line as the measure.
