# The paths of nights 170 to 173: exercised and never reached

Read-only report for Roman's ask of 2026-10-28: "Can you get a report of
non-exercised paths in the walks and see what it shows us?" Brief:
`plans/method/paths-read-brief.md`. No code changed. Nothing committed.

## The result first

- The four nights ran 980 seat sessions and wrote 3,639 refusal lines
  (observed: the runner's account at the end of each session, `turns`).
- api.py and sandbox.py hold 374 `raise ValueError` sites. 119 fired and
  255 never fired (observed: Appendix B).
- The rulings door refused 198 calls. 124 were fact doors and 74 were
  reading doors (observed: Appendix D).
- About 24 of the 74 reading refusals fell on calls that held his words
  right (reasoned: my reading of his reply against the call, section 5.2).
- At those points `liaison/landing.md` told the seat to do what the seat
  did (observed: landing.md lines 50 to 77). No Liaison prompt says what to
  do after a refusal (observed: grep of `rota/roles/prompts/liaison/`).
- Of 49 tick and do kinds, 38 were raised and 11 never. Of 48 predicates,
  40 fired and 8 never (observed: Appendices E and F).
- Of 111 prompt files, 82 were read and 29 never (observed: Appendix G).
- All four page kinds went out. 24 of 62 page sentences never went out
  (observed: Appendix I).

The three largest never-reached groups:

1. 149 door sites that check the shape of a call, in ops the seats called.
   The small model never made that mistake (reasoned: keyword rule, 5.1).
2. 60 door sites that wait on a state no night produced: a retired
   criterion, a finding, a park, a closed change (reasoned: same rule).
3. 46 door sites behind no reachable op, plus 29 prompt files and 16 ops no
   seat used. Part of this group is dead since a design change (5.1).

## How the records were read

1. The four registers and principal logs were copied to the scratchpad
   before any read. The WAL files were empty (observed: `ls -la .rota`).
2. A session that met a refusal ends with "SESSION ENDED. The runner's
   account:". The account lists every refusal of the session, one line each
   (observed: night 170, s1 and s2). This report counts those lines.
3. Each line was matched to the source statement whose string literals it
   holds, with a preference for code that the called op reaches (method:
   `scratchpad/scripts/match2.py`). 122 of 3,639 lines matched no statement
   (observed: Appendix C, "(none)").
4. The `tool_calls` table records only the calls that passed the dispatcher.
   It is not a count of refusals (observed: night 170, s1 has 3 rows and 7
   refusals).
5. A prompt counts as read when half its long lines are in a session's
   system prompt. A wake counts as raised when a session carries that
   `wake_kind`, or the launch log names it.

Limits of the method:

- The call graph follows names only. A `msg.*` send goes through
  `sandbox._bind_send`, so a helper reached only from a send shows as "no
  op". 39 sites have that mark, and some of them are live (reasoned: the
  graph does not model the send path).
- A helper's text that two raise sites share is counted on both.
- The page check matches literals. Some never-sent rows in Appendix I are
  SQL or one-word constants, not sentences.
- `landing.md` last changed at 3214898d, 2026-10-27 10:31, before night 170
  started (observed: `git log`, `launch_night170.sh`). The other prompts
  were matched as they are today.

## 1. The doors

Appendix B lists all 374 sites by file, function and line, with the count,
the nights and the seats. Appendix C lists the refusal texts from other
code. The largest of those come from `runner.py` (980 lines): the repeat
refusal ("repeat refused: code.source asked three times", 283), "wrote its
own tool results" (194), "repeated its previous turn verbatim twice" (70)
(observed: Appendix C).

### 1.1 The rulings door split

All 198 refusals of `rulings.rule` came to the Liaison (observed: the seat
of each account line). The door is `api.rulings_rule`, lines 13784 to
14536, and its helpers.

Fact doors check a thing in the records: the page is open, the key is a
line, the words are a copy of his reply, the act span is in his reply, the
call has `words`, each line has a ruling. Reading doors check a meaning in
his words through `_line_reading` and its cues (reasoned: the split follows
the code each check calls).

| Kind | Refusals | In a session that later landed a ruling | In a session that landed none |
|---|---|---|---|
| Fact | 124 | 53 | 71 |
| Reading | 74 | 43 | 31 |

"Later landed" means the session wrote a `rulings` receipt (observed:
`receipts`). One reply takes one ruling, so the landed call came after the
refusal (reasoned: `rulings_rule` line 13824).

The reading doors that fired:

| Function | Line | Check | Refusals |
|---|---|---|---|
| rulings_rule | 14086 | his words confirm the read-back line | 35 |
| _unnamed_contest via _line_refusal | 13430 | a contest rests on a line his words name | 19 |
| _faulted_approve via _line_refusal | 13316 | an approve of a line his words fault | 12 |
| rulings_rule | 14339 | his words fault a built change's files (`built_line_faulted`) | 4 |
| rulings_rule | 14289 | his words fault the code (`code_line_faulted`) | 3 |
| _line_refusal | 13040 | his words say a line matches, and the call contests it | 1 |

The fact doors that fired most: the act span is not in his reply (14146,
36), a contest with empty `words` (14489, 20), lines with no ruling (14357,
21), a verdict word the door does not know (`_ruling_word`, 15), a key that
is no line of the page (14059, 7), act fields given as keys
(`_stray_act_fields`, 7) (observed: Appendix D).

Never fired in the rulings door: 24 sites. Examples are the pointer-fault
doors (14248, 14254, 14261), the team-note doors (14209, 14224), the closed
change doors (14282, 14327), the account-page door (14399,
`_account_page_refusal`), and `_unbacked_approve` (14477) (observed:
Appendix B).

## 2. The wakes and the predicates

Raised on the four nights: `message` and 37 tick kinds, and `do:harness`,
`do:merge` and `do:preempt` in the launch logs (observed: Appendix E).

Never raised: `tick:contradiction`, `tick:park_ask`, `tick:reopen`,
`tick:finding_review`, `tick:finding_violated`, `tick:checkpoint_invalid`,
`tick:constraint_zero`, `tick:findings_exhausted`, `do:cancel`, `do:park`,
`do:defer_baseline` and `cascade` (observed: Appendix E). Night 171 wrote two
`item_parks` rows of kind `park`, and no `do:park` is in its log (observed:
`item_parks`, `night171_launch.log`).

Never fired, of the 48 predicates: `contradiction`, `reopen`,
`finding_review`, `finding_violated`, `cancel`, `checkpoint_invalid`,
`park_ask`, `constraint_zero` (observed: Appendix F). `findings_exhausted`
shows as fired because it shares `tick:exhausted`. Its own kind never rose.

Every finding on the four nights is `satisfied` (10 in all), so no
`violated` finding existed for `finding_violated` or `finding_review` to
wake on. One Critic verdict failed, on night 172. Checkpoints: 0 on all four
nights. No Researcher session ran (observed: `findings`, `verdicts`,
`checkpoints`, `sessions`).

## 3. The prompts

82 of 111 prompt files were read (observed: Appendix G). The 29 never read:

- Six `.deprecation_candidate` files.
- The terminologist lens surveys: `account/survey.md`, `grain/survey.md`,
  `source/survey.md`, `vocab/survey.md`. `terminologist/survey.md` was
  read.
- `vision_keeper/survey.md`, `elect.md`, `answer.md`, `ask.md`.
- `liaison/answer.md`, `contradiction.md`, `park_ask.md`, `unresolved.md`.
- `critic/answer.md`, `finding_review.md`.
- `developer/challenge.md`, `finding_violated.md`, `findings_exhausted.md`,
  `reopen.md`.
- `architect/ask.md`, `terminologist/answer.md`, `terminologist/ask.md`.
- `researcher/base.md`, `researcher/question.md`.

16 ops of the working sets were never called, among them `rulings.line`,
`verdicts.rule`, `references.record`, `web.fetch`, `web.search`, and every
`msg.answer_*` and `msg.ask_*` to the terminologist and the Vision Keeper
(observed: Appendix H).

### 3.1 The Liaison's prompts after a refusal

No Liaison prompt has a section on what to do after a refusal (observed:
grep for "refus", "error", "again" in `rota/roles/prompts/liaison/`). The
lines that name a refusal only warn before the call:

- `landing.md` line 17 and `answering.md` line 24: "Copy into `words` the
  exact words of the reply that ask for the change, because other words
  are refused."
- `quarantined.md` line 15: "`tick: quarantined` is refused at the door."
- `blindspot.md` line 23 and `verdict_signoff.md` line 19 name one refused
  form each.

`landing.md` ends the ruling with "Call `rulings.rule` once, with `rulings`
for every line and the whole reply as `words`. Then stop." (observed:
landing.md line 79). The refusal text itself is the only guidance a seat
gets after a refusal (reasoned: the runner sends the text back as "ERROR
<op>: <text>", `runner.py` line 5393).

## 4. The page shapes

86 page calls went to the principal: 58 `present`, 13 `clarify`, 13
`confirm`, 2 `converse` (observed: the principal logs, rows of the night).
All four page kinds went out. No seat called `msg.converse_principal`. The
two converse pages came from `db.py` line 1388 (observed: Appendix H, and
grep).

Never sent (observed: Appendix I):

- The park page: `_park_page` lines 2192, 2202, 2214 ("This change
  stopped. The team tried", "Nothing waits on you").
- The account sentence `ACCOUNT_UNNAMED` (line 2387) and
  `account_unnamed_line`.
- The unread-code sentences of `_page_body` (lines 2793, 2800, 2803, 2840)
  and the heading "How it is described:" (line 2817).
- The closed plan line of `code_line` (1806), the shift wait lines of
  `_built_words` and `_shift_waits`, and the request hints of
  `_name_request` (1960) and `_name_guess` (1971).

## 5. What it shows

### 5.1 The never-reached paths in groups

The 255 never-fired door sites, split by a keyword rule on each site's text
(reasoned: the rule is in `scratchpad/scripts`, and a reader can move a
site between groups B and C):

| Group | Door sites | Other paths |
|---|---|---|
| A. Dead since a design change, or behind no reachable op | 46 | 6 deprecation prompts, 4 lens surveys, 16 ops never called |
| B. Waiting on a shape no night produced | 60 | 8 predicates, 11 tick and do kinds, the park, account and unread-code pages |
| C. Guarding a case the small model never makes | 149 | none |

Group A, what the records show:

- `criteria_retire` (6681, 6688, 6704) is in no working set (observed:
  Appendix H source, no `.tools` file lists `criteria.retire`).
- `rulings_line` (14557, 14572) and `verdicts_rule` (16584 to 16600) sit
  behind ops no seat called. `references_record` (24701) waits on the
  Researcher, and no Researcher session ran (observed: `sessions.role`).
- The six `.deprecation_candidate` files and the four lens surveys are not
  in any system prompt (observed: Appendix G). Whether a design change
  retired the lens surveys is not in the records this report read.
- The other 39 "no op" sites include send-path helpers such as
  `refuse_signoff_without_draft` (786) and `sandbox._stage_reason` (2763).
  The method cannot see that path, so they may be live (reasoned: 2).

Group B is state the walks never built: a retired criterion (6040, 9674), a
filed finding (4264 to 4376, `verdicts_rule`), a judged stray
(`batches_judge_touch`, 24364 to 24453), a closed change in a ruling
(14282, 14327), a park and a cancel, a checkpoint (observed: Appendix B and
E). The walks merged 8 changes and parked 2 items in four nights, and no
change was cancelled (observed: `batches`, `item_parks`).

Group C is the larger half of every op the seats did call. Examples in the
rulings door: `rulings` not a map (13958), `acts` not a map (14096),
`acts[k]` not an object (14112), a ruling with no open page (13819). In
`_code_write`, 22 of its sites never fired (observed: Appendix B).

### 5.2 Reading doors that fired on calls that held his words right

I read his reply and the refused call for each reading refusal (reasoned:
my reading, not a door's). About 24 of 74 fell on a right call:

| Night, session | His words | The call | The door | What landing.md says |
|---|---|---|---|---|
| 170 and 171, s92 and s93 | "line 1 and the rest of the word notes are fine" | approve line 1 | `_faulted_approve` 13316: "The words fault line 1, \"are fine\"" (8) | "fine, go ahead" approves |
| 170, s156 | "line 4 reads my last answer right" | approve line 4 | 14086, read-back not confirmed (1) | approve the read-back line "when the words name it" |
| 170, s164 | "lines 5 and 6 read my earlier answers right" | approve 5 and 6 | 14086 (2) | same |
| 170, s192 | "line 4 reads my last answer correctly" | approve line 4 | 14086 (1) | same |
| 171, s113 | "Line 4 rea..." (the first turn cuts the reply) | approve line 4 | 14086 (1) | same |
| 172, s187 and s188 | "line 6 reads my last answer correctly" | approve line 6 | 14086 (2) | same |
| 172, s215 | "Line 2 is wrong ... The other lines are fine." | approve read-back line 4 | 14086 (1) | "approves the others, except the read-back line", which then needs "the words name it or approve the whole page" |
| 172, s224 | "The other lines are fine, and the team read my earlier answer ..." | approve read-back lines 6 and 7 | 14086 (2) | approve the read-back line when the words name it |
| 172, s196 | "The first request is right. The second line is wrong ... please drop it" | approve 1, contest 2 | `_faulted_approve` 13316: "The words fault line 1, \"drop\"" (2) | "The door reads `drop` ... as `contest`" |
| 172, s199 and s200 | "drop the second line" | contest line 2 | `_unnamed_contest` 13430: "do not name line 2" (4) | "The reply strikes or drops a line from the change: `contest`" |

In each row the seat did what `landing.md` says, and the door read his
words in a different way (reasoned: the table). Three causes show in the
texts: a fault cue taken from an approving clause ("are fine", "drop"
about another line), a read-back line named in words the door does not
match ("reads my last answer right"), and an ordinal the door does not read
as a number ("the second line") (reasoned: from the refusal texts).

The other reading refusals caught a real misreading by the seat. Examples:
170 s103 approved read-back line 5 that his words never named, 170 s215
contested line 4 that his words never named, 173 s173 contested line 2 of
"Lines 1 to 13 are fine" (observed: the calls in the turns).

25 of the 37 sessions with a reading refusal later landed a ruling, and 12
landed none (observed: `receipts`). Whether the landed ruling matched his
words is not in the records this report read.

## Appendix A. The counts per night

| Night | Sessions | Refusal lines in the runner's accounts | From api.py | From sandbox.py | From runner.py | No source found |
|---|---|---|---|---|---|---|
| 170 | 230 | 773 | 477 | 58 | 219 | 19 |
| 171 | 231 | 817 | 459 | 109 | 216 | 33 |
| 172 | 275 | 1152 | 730 | 89 | 292 | 41 |
| 173 | 244 | 897 | 542 | 73 | 253 | 29 |

## Appendix B. Every `raise ValueError` site in api.py and sandbox.py

Fired is the count of refusal lines whose text matches the site, or a helper the site raises. Seats are the roles that met it. Reached by is the ops of a working set whose call graph reaches the function.

| File | Function | Line | Fired | Nights | Seats | Reached by an op that was called | First words |
|---|---|---|---|---|---|---|---|
| sandbox.py | _answer_evidence | 1160 | 0 |  |  | no op | an answer to a challenge names the criterion the test stands on in ref |
| sandbox.py | _answer_evidence | 1174 | 0 |  |  | no op | an answer that keeps the test carries the criterion's words: quotes= c |
| sandbox.py | _challenge_evidence | 1750 | 0 |  |  | yes | a challenge to the tester names both sides of the conflict in refs -- |
| sandbox.py | _challenge_evidence | 1762 | 0 |  |  | yes | is not a criterion of this batch. The conflict you may challenge is b |
| sandbox.py | _challenge_evidence | 1778 | 8 | 170:1,171:7 | developer:8 | yes | has no criterion: it is the project's own test and  it passed before |
| sandbox.py | _challenge_evidence | 1822 | 3 | 171:2,172:1 | developer:3 | yes |  |
| sandbox.py | _challenge_evidence | 1833 | 3 | 171:2,172:1 | developer:3 | yes |  |
| sandbox.py | _challenge_evidence | 1836 | 3 | 171:2,172:1 | developer:3 | yes | and of |
| sandbox.py | _challenge_evidence | 1840 | 3 | 171:2,172:1 | developer:3 | yes | or of |
| sandbox.py | _challenge_evidence | 1858 | 15 | 170:4,171:6,172:5 | architect:5,terminologist:10 | yes |  |
| sandbox.py | _escalation_over_removed_grain | 1877 | 0 |  |  | no op | . Then code.commit the finding stands on a fact about your tree, and t |
| sandbox.py | _escalation_over_removed_grain | 1892 | 0 |  |  | no op | the finding   is about  , which constraint   binds, and no file in the |
| sandbox.py | door | 2180 | 7 | 170:3,171:4 | terminologist:7 | no op |  |
| sandbox.py | _stage_reason | 2763 | 0 |  |  | no op | msg.challenge_tester  Send msg.challenge_tester(refs= ) with the same |
| sandbox.py | _stage_reason | 2790 | 0 |  |  | no op | the reason's id   Write the reason in your own words. |
| sandbox.py | _refuse_confirm_off_entry | 3456 | 0 |  |  | no op | The words that woke you, ` `, have no statement. Segment them with `br |
| sandbox.py | stage | 3513 | 0 |  |  | no op | the principal already has this question. Send nothing more, and stop |
| sandbox.py | stage | 3561 | 0 |  |  | no op | refs is a list, not a string that holds a list. You sent  . Send the l |
| sandbox.py | stage | 3565 | 12 | 170:3,171:3,172:4,173:2 | liaison:7,architect:2,terminologist:2,developer:1 | no op | refs is a list of ids and you sent a bare string,  . A string is a seq |
| sandbox.py | stage | 3586 | 0 |  |  | no op | refs are ids and nothing else; you sent  . Send the id on its own -- w |
| sandbox.py | stage | 3600 | 24 | 170:4,171:4,172:6,173:10 | liaison:24 | no op | refs are ids, and   is not one. An id looks like `s_1b9009` and comes |
| sandbox.py | stage | 3616 | 2 | 170:1,172:1 | terminologist:1,liaison:1 | no op | names no row -- not in any table, not written this session. Refs are |
| sandbox.py | stage | 3664 | 1 | 172:1 | vision_keeper:1 | no op | is not an item. A reopen names the item that changed under the batch; |
| sandbox.py | stage | 3672 | 0 |  |  | no op | is approved at its current version; nothing changed under the batch, |
| sandbox.py | stage | 3689 | 0 |  |  | no op | a page carries at most   open assumptions and this one carries  . Send |
| sandbox.py | stage | 3715 | 0 |  |  | no op | you have already put these words to the principal, in  . Asking twice |
| sandbox.py | stage | 3755 | 11 | 171:11 | liaison:11 | no op | ...' is the principal's own sentence, pasted back to them. They know |
| sandbox.py | stage | 3791 | 0 |  |  | no op | names no row, so this question is about your own bookkeeping, not abo |
| sandbox.py | stage | 3802 | 0 |  |  | no op | is a message, and the principal has never seen one. Refs on this chan |
| sandbox.py | stage | 3825 | 0 |  |  | no op | an ask carries the question in its refs and you sent none. This channe |
| sandbox.py | stage | 3846 | 0 |  |  | no op | 's last run reached input() through the code it calls -- pytest captur |
| sandbox.py | stage | 3880 | 0 |  |  | no op | already has your open question,  , and the answer will wake you. Aski |
| sandbox.py | stage | 3895 | 0 |  |  | no op | you were woken for batch   and a report from here is about it: add ' ' |
| sandbox.py | stage | 3943 | 0 |  |  | no op |  |
| sandbox.py | stage | 3948 | 6 | 172:6 | developer:6 | no op |  |
| sandbox.py | stage | 3982 | 0 |  |  | no op | has answered   questions of yours on these rows and they did not sett |
| sandbox.py | stage | 4013 | 0 |  |  | no op | claim the branch first: brief.intake(verdict='work') if they asked for |
| sandbox.py | stage | 4020 | 0 |  |  | no op | you claimed work, so the reply carries refs -- the statements you segm |
| sandbox.py | stage | 4036 | 0 |  |  | no op | you claimed work and segmented nothing. The refs name the entry, and a |
| sandbox.py | stage | 4074 | 0 |  |  | no op | you looked up   and the glossary had nothing, and you have defined not |
| sandbox.py | stage | 4121 | 0 |  |  | no op | already asked --   carries   to the Terminologist. Encode the others o |
| sandbox.py | stage | 4373 | 0 |  |  | no op | read the reply before you relay it. This message answers a question yo |
| sandbox.py | stage | 4411 | 0 |  |  | no op | the answer you are relaying cites nothing it came from -- only the que |
| sandbox.py | stage | 4452 | 0 |  |  | no op | an answer names the rows it came from, and these name none -- only the |
| sandbox.py | stage | 4492 | 11 | 171:10,172:1 | developer:7,architect:4 | no op | msg.report_liaison : send msg.report_liaison(refs= ) with the same ref |
| sandbox.py | stage | 4499 | 11 | 171:10,172:1 | developer:7,architect:4 | no op | glossary.amend : write the term down with glossary.amend, then cite it |
| sandbox.py | stage | 4504 | 11 | 171:10,172:1 | developer:7,architect:4 | no op |  |
| sandbox.py | stage | 4513 | 11 | 171:10,172:1 | developer:7,architect:4 | no op |  |
| sandbox.py | stage | 4537 | 2 | 170:1,173:1 | liaison:2 | no op | is not a statement, and a confirmation asks the principal to ratify o |
| sandbox.py | stage | 4558 | 0 |  |  | no op |  |
| sandbox.py | stage | 4573 | 128 | 170:26,171:36,172:38,173:28 | liaison:48,developer:23,tester:8,architect:5,terminologist:40,vision_keeper:4 | no op | you have already sent   to  ; saying it again with different refs is a |
| sandbox.py | stage | 4625 | 0 |  |  | no op | is the test of  , and its batch   is  . The Tester rewrites a test wh |
| sandbox.py | stage | 4631 | 13 | 171:3,172:6,173:4 | terminologist:13 | no op | no change built from this criterion has a commit yet, so the Tester ha |
| sandbox.py | stage | 4689 | 0 |  |  | no op | the principal approved these criteria as they stand, so no owner has a |
| sandbox.py | stage | 4752 | 21 | 170:4,171:3,172:8,173:6 | liaison:21 | no op | every owner these rows belong to has its relay already; saying it agai |
| sandbox.py | wrapper | 5021 | 2 | 170:1,171:1 | vision_keeper:2 | no op | is the   row you wrote this session, and a   row is a different thing |
| sandbox.py | wrapper | 5035 | 20 | 170:2,171:7,173:11 | terminologist:2,vision_keeper:18 | no op | is already a row of  ; an artefact id is unique across every artefact |
| api.py | _must_exist | 550 | 6 | 170:1,171:1,172:2,173:2 | tester:2,vision_keeper:4 | yes | row with id= ; this changes an existing row, so the id has to be one |
| api.py | refuse_second_answer | 639 | 0 |  |  | yes | you have already  , which is one answer to what the principal said. Th |
| api.py | refuse_repeated_sentence | 745 | 0 |  |  | yes | you answered these words in  , and the principal said them again. That |
| api.py | refuse_signoff_without_draft | 786 | 0 |  |  | no op | msg.submit_liaison  Send msg.submit_liaison(refs= refs |
| api.py | refuse_answered_question | 854 | 2 | 172:1,173:1 | liaison:2 | yes | you asked this in  , and the principal answered it in  . Read that rep |
| api.py | brief_segment | 959 | 0 |  |  | yes | no entry to segment against |
| api.py | brief_segment | 971 | 0 |  |  | yes | is a statement, and a statement is not an entry. |
| api.py | brief_segment | 974 | 0 |  |  | yes | names no entry. The entry this session can segment is |
| api.py | brief_segment | 976 | 0 |  |  | yes | names no entry, and there is no entry to segment against |
| api.py | brief_segment | 992 | 0 |  |  | yes | There is no earlier request on the page, so leave supersedes out. |
| api.py | brief_segment | 995 | 0 |  |  | yes | supersedes names  , and the current request's earlier statement is  . |
| api.py | brief_segment | 1007 | 2 | 170:1,173:1 | liaison:2 | yes | `supersedes` names ` `, and the new words share no word with it. A fol |
| api.py | brief_segment | 1020 | 0 |  |  | yes | `supersedes` names ` `, which is about  . These words name  , so they |
| api.py | brief_segment | 1045 | 0 |  |  | yes | that span is a question, and a question is never a statement to ratify |
| api.py | brief_segment | 1094 | 0 |  |  | yes | does not appear in the entry you are segmenting. A statement is a spa |
| api.py | brief_segment | 1113 | 0 |  |  | yes | these words are  , from another entry. Leave span_entry out. Segment t |
| api.py | brief_segment | 1118 | 0 |  |  | yes | these words are  , which the principal ratified. Cite  . There is noth |
| api.py | brief_segment | 1122 | 0 |  |  | yes | these words are  , which waits for the principal. Send msg.confirm_pri |
| api.py | brief_segment | 1125 | 0 |  |  | yes | these words are  , on file as  . Cite  . There is nothing to segment s |
| api.py | brief_segment | 1140 | 0 |  |  | yes | is on file; a statement keeps its id. Segment these words as |
| api.py | brief_ratify | 1197 | 2 | 172:2 | liaison:2 | yes |  |
| api.py | stage_ref | 1244 | 0 |  |  | yes | kind is one of  , not |
| api.py | stage_ref | 1246 | 0 |  |  | yes | is not a table that carries refs |
| api.py | cite | 1351 | 0 |  |  | no op | is a key, not a row of |
| api.py | cite | 1358 | 0 |  |  | no op | is not a row of |
| api.py | cite | 1364 | 0 |  |  | no op | names no  : a   ref targets |
| api.py | problem_assert | 2052 | 0 |  |  | yes | you have already put   in this session and this says  . Those are the |
| api.py | problem_assert | 2063 | 1 | 172:1 | vision_keeper:1 | yes |  |
| api.py | problem_assert | 2102 | 0 |  |  | yes |  |
| api.py | problem_assert | 2107 | 6 | 171:6 | vision_keeper:6 | yes | is the account's observed row and these are its words. Asserting it a |
| api.py | problem_assert | 2126 | 0 |  |  | yes | is observed, and these are not the principal's words: the statement y |
| api.py | problem_assert | 2168 | 0 |  |  | yes | those are  's words, a criterion of an item that exists. An item is wh |
| api.py | problem_assert | 2180 | 0 |  |  | yes | how_it_works is the account of the whole program, and this text keeps |
| api.py | problem_assert | 2189 | 0 |  |  | yes | is a grain in the index, so this is a sentence about a file or a func |
| api.py | problem_set_approval | 2306 | 0 |  |  | yes | the principal ruled  . land wrote ` . Leave it |
| api.py | problem_set_approval | 2323 | 1 | 171:1 | vision_keeper:1 | yes | the principal approved   on  , ruling  , and this relay  . Leave it. |
| api.py | problem_set_approval | 2345 | 0 |  |  | yes | is   at version  , and no verdict of the principal approved it. Only |
| api.py | problem_describe | 2391 | 1 | 172:1 | vision_keeper:1 | yes | is the principal's own words, so it asks for something. If its ticket |
| api.py | problem_describe | 2401 | 0 |  |  | yes | has work in batch  , so it asks for something. Answer the challenge w |
| api.py | _adopt_rows | 2636 | 0 |  |  | yes | adopt names the rows the principal approved, and you named none |
| api.py | _adopt_rows | 2643 | 0 |  |  | yes | adopt needs a landed ruling on the chain of the message that woke you: |
| api.py | _adopt_rows | 2655 | 8 | 170:3,172:5 | architect:8 | yes | is not a row of  ; adopt what the ruling names, from the refs you wer |
| api.py | glossary_amend | 2786 | 0 |  |  | yes | a term needs a word in it |
| api.py | glossary_amend | 2797 | 1 | 172:1 | terminologist:1 | yes | has no sense under it. A glossary of words is the index with the colu |
| api.py | glossary_amend | 2805 | 6 | 170:1,172:4,173:1 | terminologist:6 | yes | has a body and no `sense_short`. That is the one line every reader of |
| api.py | glossary_amend | 2864 | 0 |  |  | yes | surveys.attest this session is about   and nothing else;   is not that |
| api.py | glossary_amend | 2903 | 0 |  |  | yes | is defined without saying where it is written down. Name the key a us |
| api.py | glossary_amend | 2947 | 4 | 170:1,171:1,172:1,173:1 | terminologist:4 | yes | is a kind here, and the sense does not say so. The concordance shows |
| api.py | glossary_amend | 2958 | 0 |  |  | yes | surveys.attest  is the frame you were woken in, not something this pro |
| api.py | glossary_amend | 2985 | 10 | 170:4,171:1,172:3,173:2 | terminologist:10 | yes | nothing you read this session says  . A word means what the code using |
| api.py | glossary_amend | 3120 | 0 |  |  | yes | already means that. `sense= ` asks for a second sense of the word, an |
| api.py | glossary_amend | 3181 | 0 |  |  | yes | already means that: the glossary's entry says everything this one doe |
| api.py | glossary_synthesise | 3264 | 4 | 172:4 | terminologist:4 | yes | synthesis composes more than one reading. One row is an amendment -- ` |
| api.py | glossary_synthesise | 3276 | 0 |  |  | yes | is not among the rows you were woken about. Those are  , and they are |
| api.py | glossary_synthesise | 3287 | 0 |  |  | yes | is not a glossary id. The ids are the ones the wake named, spelled as |
| api.py | glossary_synthesise | 3293 | 0 |  |  | yes | are different words. Synthesis writes one sense of one word from the |
| api.py | glossary_synthesise | 3298 | 0 |  |  | yes | a synthesised sense needs both: `sense_body` is what the readings add |
| api.py | glossary_synthesise | 3306 | 2 | 170:1,173:1 | terminologist:2 | yes | that is   again, word for word. Synthesis is for the sense the reading |
| api.py | glossary_synthesise | 3359 | 1 | 173:1 | terminologist:1 | yes | that says nothing the readings did not already say -- it is a summary |
| api.py | glossary_same | 3457 | 0 |  |  | yes | is not a glossary id. The words with more than one live sense are — |
| api.py | glossary_same | 3462 | 0 |  |  | yes | keep and drop are the same row; nothing to merge. |
| api.py | glossary_same | 3466 | 0 |  |  | yes | and   are different words. This says two rows are one word said twice |
| api.py | glossary_same | 3484 | 0 |  |  | yes | say why they are the same before merging them. Reporting two senses co |
| api.py | glossary_same | 3501 | 0 |  |  | yes | is a reason they are *not* the same -- it says  . Two senses that dif |
| api.py | glossary_same | 3509 | 0 |  |  | yes | does not mention anything either sense says. Name what the two have i |
| api.py | model_amend | 3690 | 0 |  |  | yes | a constraint needs a headline with a word in it |
| api.py | model_amend | 3698 | 28 | 170:4,171:4,172:10,173:10 | architect:28 | yes | is a label, not a headline. Say what is promised, in the words the so |
| api.py | model_amend | 3722 | 0 |  |  | yes | names a  , and a constraint is what a caller outside relies on.  head |
| api.py | model_amend | 3728 | 0 |  |  | yes | names a  , and a constraint is what a caller outside relies on. Write |
| api.py | model_amend | 3733 | 0 |  |  | yes | names a  , and a constraint is what a caller outside relies on. First |
| api.py | model_amend | 3773 | 14 | 170:3,171:3,172:4,173:4 | architect:14 | yes | names nobody outside this area -- a maintainer, the codebase, the bui |
| api.py | model_amend | 3785 | 27 | 170:6,171:5,172:9,173:7 | architect:27 | yes | that is what the product does, and an item already says it. A constrai |
| api.py | model_amend | 3791 | 0 |  |  | yes | is derived: its bindings are the areas nobody has surveyed, and a sur |
| api.py | model_amend | 3817 | 79 | 170:72,172:2,173:5 | architect:79 | yes | already governs this subject:  . If both commitments hold together, s |
| api.py | model_amend | 3841 | 0 |  |  | yes | is a reference, not a grain -- bindings are the code a constraint gov |
| api.py | model_amend | 3871 | 16 | 170:6,171:6,172:3,173:1 | architect:16 | yes | is not a grain in the index. A binding is the path of a file that kee |
| api.py | model_amend | 3886 | 0 |  |  | yes | is not the path of a file this session read, and there is no code ind |
| api.py | model_amend | 3905 | 430 | 170:60,171:60,172:149,173:161 | architect:430 | yes | you have not read   this session. A constraint binds the grains it gov |
| api.py | model_amend | 3917 | 12 | 170:6,171:6 | architect:12 | yes | a constraint from the survey of   binds the grain that keeps it: bindi |
| api.py | model_amend | 3962 | 0 |  |  | yes | is a title with nothing under it. A title cannot be checked, argued w |
| api.py | findings_find | 4264 | 0 |  |  | yes | you have already filed   on   in this session; decide, and send the on |
| api.py | findings_find | 4278 | 3 | 170:1,172:1,173:1 | architect:3 | yes | finding id   is held by batch  , and this call would replace that batc |
| api.py | findings_find | 4297 | 0 |  |  | yes | . A finding names a constraint from model.consult. |
| api.py | findings_find | 4299 | 2 | 172:2 | architect:2 | yes | . A finding names a constraint from model.consult. |
| api.py | findings_find | 4311 | 0 |  |  | yes | the batch's diff does not touch  ; it changed  . A finding names what |
| api.py | findings_find | 4324 | 2 | 172:2 | architect:2 | yes | does not bind  , so this diff cannot violate it. |
| api.py | findings_find | 4328 | 0 |  |  | yes | is constraint zero, the area no survey has read. It is a fact about t |
| api.py | findings_find | 4344 | 3 | 170:1,172:1,173:1 | architect:3 | yes | the batch's diff does not touch  ; it changed  . A finding names a fil |
| api.py | findings_find | 4361 | 0 |  |  | yes | is for a file that no constraint reaches, and   constraints reach  . |
| api.py | findings_find | 4376 | 0 |  |  | yes | finding id   is already filed in this session, as   on  , and this cal |
| api.py | model_describe | 4401 | 0 |  |  | yes | is not an area: the account of the whole program is the orientation's |
| api.py | model_describe | 4406 | 0 |  |  | yes | an account says what the area is for and how it works -- a sentence or |
| api.py | model_describe | 4412 | 0 |  |  | yes | that is a list of files, and the index already holds it. Say what the |
| api.py | surveys_attest | 4522 | 0 |  |  | yes | no area: attesting closes the area you were woken for, and this sessio |
| api.py | surveys_attest | 4631 | 64 | 170:16,171:16,172:16,173:16 | vision_keeper:58,architect:6 | yes | your   was refused this session:   -- and nothing of that kind has lan |
| api.py | surveys_attest | 4651 | 0 |  |  | yes | you have attested `found` and written no items. The account is not the |
| api.py | surveys_attest | 4656 | 82 | 170:20,171:20,172:21,173:21 | vision_keeper:70,architect:10,liaison:2 | yes | you have attested `found` and written no  . What you found is not the |
| api.py | surveys_attest | 4681 | 0 |  |  | yes | everything you wrote this session is a title with nothing under it ( ) |
| api.py | surveys_attest | 4811 | 5 | 172:3,173:2 | terminologist:5 | yes | you cited   and opened none of them. `code.survey` lists an area; it d |
| api.py | surveys_attest | 4865 | 2 | 170:1,173:1 | architect:2 | yes | Reading nothing and reporting nothing are not the same answer. You hav |
| api.py | tickets_slice | 4966 | 0 |  |  | yes | how_it_works is the account of the whole program, not a behaviour to b |
| api.py | tickets_slice | 4971 | 0 |  |  | yes | is observed: it is what the repository already does, and a ticket for |
| api.py | tickets_slice | 5015 | 0 |  |  | yes | went out in batch  , which is  . New work is a new ticket: give it a |
| api.py | tickets_slice | 5024 | 0 |  |  | yes | a ticket is its text, and this one says nothing. Slice the item into a |
| api.py | _exception_from_a_source | 5388 | 0 |  |  | yes | is in none of his words, the item, or the source of the surface. A cr |
| api.py | _vet_surface | 5443 | 5 | 170:5 | terminologist:5 | yes | this rewrite names no surface, and the repair exists because the words |
| api.py | _vet_surface | 5469 | 0 |  |  | yes |  |
| api.py | _vet_surface | 5489 | 8 | 172:8 | terminologist:8 | yes | is a test ( ), and a test is not a surface. The surface is the progra |
| api.py | _vet_surface | 5505 | 0 |  |  | yes | is in  , and the frame marks that file  , not program code. The progr |
| api.py | _vet_surface | 5522 | 5 | 171:2,172:3 | terminologist:5 | yes | is not a symbol the index knows. A surface is a callable a test would |
| api.py | _vet_surface | 5541 | 9 | 170:4,172:5 | terminologist:9 | yes | is not a symbol the index knows, not a name the item or the ticket gi |
| api.py | _surface_names_what_the_item_names | 5831 | 0 |  |  | yes | the item names  , a callable the index holds, and this surface names |
| api.py | _surface_names_what_the_item_names | 5855 | 0 |  |  | yes | the item names  , a new callable, and this surface also names  , which |
| api.py | _surface_names_what_the_item_names | 5870 | 0 |  |  | yes | is a name the index does not hold and no item or ticket gives. A surf |
| api.py | _surface_names_what_the_item_names | 5878 | 0 |  |  | yes | the item names  , and the index has no such callable: a new behaviour |
| api.py | criteria_specify | 6018 | 0 |  |  | yes | criteria.specify  is an item, not a ticket. Its tickets are  . A crite |
| api.py | criteria_specify | 6040 | 0 |  |  | yes | is retired: its item was amended and sliced again. Write the criteria |
| api.py | criteria_specify | 6055 | 0 |  |  | yes | belongs to  , and you were woken for  , whose tickets are  . Write th |
| api.py | criteria_specify | 6081 | 0 |  |  | yes | criteria.specify  is already  's criterion. An id you invent is yours |
| api.py | criteria_specify | 6106 | 2 | 172:2 | terminologist:2 | yes | criteria.specify  already holds a criterion on  . An id you invent is |
| api.py | criteria_specify | 6115 | 0 |  |  | yes | Say what the script does for a valid name and for an empty or wrong on |
| api.py | criteria_specify | 6121 | 0 |  |  | yes |  |
| api.py | criteria_specify | 6142 | 22 | 170:12,171:8,172:1,173:1 | terminologist:22 | yes |  |
| api.py | criteria_specify | 6175 | 3 | 172:3 | terminologist:3 | yes | has   criteria already, and six is many. A seventh decides scope the |
| api.py | criteria_retire | 6681 | 0 |  |  | no op | is not a criterion. Retire a criterion by its id |
| api.py | criteria_retire | 6688 | 0 |  |  | no op | no ruling of the principal drops the line of  . Only his ruling retire |
| api.py | criteria_retire | 6704 | 0 |  |  | no op | this wake is not the relay of his ruling on  . Only the relay of the r |
| api.py | tests_retire | 6731 | 17 | 170:3,172:10,173:4 | tester:17 | yes | is not a test. Retire a test by its id |
| api.py | tests_retire | 6734 | 0 |  |  | yes | only the Tester retires a test. Answer the Tester with the test id in |
| api.py | tests_retire | 6745 | 139 | 170:1,171:2,172:136 | tester:139 | yes | . Only his ruling that drops the check line retires a test. Encode the |
| api.py | tests_retire | 6754 | 0 |  |  | yes | this wake does not carry his ruling   on  . Only the Tester's answer w |
| api.py | _near_twin | 6844 | 0 |  |  | yes |  |
| api.py | criteria_respecify | 6910 | 0 |  |  | yes | Rewrite it as what the script does for a valid name and for an empty o |
| api.py | criteria_respecify | 6984 | 2 | 170:1,172:1 | terminologist:2 | yes |  |
| api.py | criteria_respecify | 7009 | 0 |  |  | yes | the principal contested   in this criterion. His words:  . No row of r |
| api.py | criteria_respecify | 7054 | 0 |  |  | yes | the principal contested these words:  . Write what he asked for.  word |
| api.py | criteria_respecify | 7057 | 14 | 171:3,172:6,173:5 | terminologist:14 | yes | the principal contested these words:  . Write what he asked for words |
| api.py | criteria_respecify | 7075 | 0 |  |  | yes |  |
| api.py | batches_group | 7264 | 0 |  |  | yes | item_id is required: the named tickets trace to   and a batch delivers |
| api.py | batches_group | 7283 | 0 |  |  | yes | is not the item any of these tickets trace to. A batch delivers exact |
| api.py | batches_group | 7310 | 0 |  |  | yes | Group the other tickets of your wake,  , and leave |
| api.py | batches_group | 7313 | 0 |  |  | yes | Group nothing, and stop. |
| api.py | batches_group | 7327 | 0 |  |  | yes | not among the tickets you were woken to group. Those are  : the ticke |
| api.py | batches_group | 7335 | 6 | 170:2,171:1,172:1,173:2 | architect:6 | yes | is already a batch ( ), and a batch is never re-formed under its old |
| api.py | batches_group | 7370 | 5 | 170:2,171:3 | architect:5 | yes | 's work is already batched as  . A batch delivers exactly one approved |
| api.py | _refuse_stray_dirs | 7409 | 0 |  |  | yes | is under a directory the tree does not have. The directories here are |
| api.py | _refuse_program_path | 7514 | 0 |  |  | yes | path   is a program file of the project. The harness writes the test a |
| api.py | _refuse_unindexed_files | 7608 | 0 |  |  | yes | is not a file the index holds. The index holds these files in  . Writ |
| api.py | batches_guess | 7640 | 0 |  |  | yes | . The request is `item` in your working set, |
| api.py | batches_guess | 7645 | 0 |  |  | yes | a guess names at least one path. A new file goes beside the files that |
| api.py | batches_guess | 7675 | 0 |  |  | yes | . Or leave symbols out |
| api.py | batches_guess | 7683 | 8 | 170:1,171:1,172:4,173:2 | architect:8 | yes | names no path. A symbol is written path::name.  Write the symbol that |
| api.py | batches_guess | 7694 | 2 | 173:2 | architect:2 | yes | is already guessed in this session. One call per item |
| api.py | tests_triage | 8021 | 0 |  |  | yes | contradicts_request needs two spans. Copy request_span= from the reque |
| api.py | tests_triage | 8041 | 0 |  |  | yes | request_span is not in the statements, the item or the ticket. Copy th |
| api.py | tests_triage | 8046 | 0 |  |  | yes | criterion_span is not in the words of  . Copy the span from the criter |
| api.py | tests_triage | 8052 | 0 |  |  | yes |  |
| api.py | _refuse_retired | 9674 | 0 |  |  | yes | is retired: the principal's ruling   dropped its line. Encode only th |
| api.py | tests_encode | 9836 | 0 |  |  | yes | path   is outside the project. The harness writes the test at its path |
| api.py | tests_encode | 9844 | 0 |  |  | yes | is a placeholder, not an id. Give this test an id of its own, a short |
| api.py | tests_encode | 9854 | 0 |  |  | yes | was triaged   in this session. A routed criterion gets no test. Encod |
| api.py | tests_encode | 9876 | 0 |  |  | yes |  |
| api.py | tests_encode | 9881 | 12 | 171:2,172:5,173:5 | tester:12 | yes | tests.triage  has no triage verdict from you yet. Call tests.triage(cr |
| api.py | tests_encode | 9898 | 1 | 170:1 | tester:1 | yes | path   is not a Python file. The harness runs pytest; name the file te |
| api.py | tests_encode | 10341 | 7 | 170:1,172:6 | tester:7 | yes | this test imports  , and the batch's other tests import   -- one progr |
| api.py | tests_encode | 10766 | 0 |  |  | yes | the test   passes ` ` to `.invoke`, and ` ` is a plain function in ` ` |
| api.py | tests_encode | 10778 | 0 |  |  | yes | the test   passes   to `.invoke`, and `CliRunner.invoke` takes a click |
| api.py | tests_encode | 10904 | 0 |  |  | yes | ` is a decorator factory in ` `: it returns a decorator and prints not |
| api.py | tests_encode | 10928 | 0 |  |  | yes | , and   never runs the option that ` ` adds |
| api.py | tests_encode | 11005 | 0 |  |  | yes | the test uses what   returns, and the criterion   says it prints |
| api.py | tests_encode | 11009 | 4 | 172:4 | tester:4 | yes | ledger.log the test uses what   returns, and the criterion, its ticket |
| api.py | tests_encode | 11052 | 13 | 170:1,173:12 | tester:13 | yes | exists and belongs to no batch, and this session was not woken for on |
| api.py | tests_encode | 11127 | 0 |  |  | yes |  |
| api.py | tests_encode | 11152 | 0 |  |  | yes | tests.encode  is stored at  . To replace it, send this encode again wi |
| api.py | tests_encode | 11191 | 1 | 170:1 | tester:1 | yes | tests.encode criterion_id path body batch_id  is a test of batch  , an |
| api.py | tests_encode | 11222 | 0 |  |  | yes | tests.encode  is  's file, and this wake challenges  . To fix that tes |
| api.py | tests_encode | 11243 | 8 | 171:1,172:4,173:3 | tester:8 | yes | tests.encode  is already  's file, and that file holds the project's o |
| api.py | tests_encode | 11256 | 1 | 171:1 | tester:1 | yes | tests.encode  is  's file, and   is the test of this same criterion. T |
| api.py | tests_encode | 11269 | 38 | 170:20,171:4,172:5,173:9 | tester:38 | yes | is already  's file; two tests in one file overwrite each other on di |
| api.py | _ruling_word | 11541 | 0 |  |  | yes | line   is a question back, and a question is its own call: rulings.rul |
| api.py | _ruling_word | 11546 | 6 | 171:6 | liaison:6 | yes | line   takes later, now or drop: the question is which request goes fi |
| api.py | _ruling_word | 11550 | 0 |  |  | yes | line   is not an answer here. Line   takes later, now or drop. later, |
| api.py | _ruling_word | 11556 | 9 | 172:6,173:3 | liaison:9 | yes | line   is not a ruling. Each line takes approve, contest or revise. dr |
| api.py | _ruling_shape | 11830 | 0 |  |  | yes | line  : the object has no verdict. Write it as {"verdict": "contest", |
| api.py | _ruling_shape | 11839 | 6 | 171:6 | liaison:6 | yes | line   is not an act. An act is  . Leave act out when the words grant |
| api.py | _ruling_shape | 11847 | 0 |  |  | yes | line   is not a target kind. A target kind is |
| api.py | rulings_rule | 13819 | 0 |  |  | yes | no open page: this session was not woken by a reply to a confirm, a pr |
| api.py | rulings_rule | 13824 | 0 |  |  | yes | this reply is already read: one ruling per reply. Stop |
| api.py | rulings_rule | 13833 | 0 |  |  | yes | the principal has your sentence. Stop |
| api.py | rulings_rule | 13904 | 0 |  |  | yes |  |
| api.py | rulings_rule | 13937 | 0 |  |  | yes |  |
| api.py | rulings_rule | 13958 | 0 |  |  | yes | rulings is a map of page line number (or row id) to approve, contest o |
| api.py | rulings_rule | 13997 | 7 | 170:2,171:1,172:4 | liaison:7 | yes |  |
| api.py | rulings_rule | 14001 | 4 | 172:3,173:1 | liaison:4 | yes |  |
| api.py | rulings_rule | 14027 | 0 |  |  | yes | line   is not waiting. resume takes up a request you put aside. |
| api.py | rulings_rule | 14041 | 0 |  |  | yes | is your earlier request,  , and this page is about another request. W |
| api.py | rulings_rule | 14045 | 0 |  |  | yes | is no line of this page. Words on this page do not change it. Leave t |
| api.py | rulings_rule | 14054 | 0 |  |  | yes | is not a row of this question. A clarify numbers no line, so each key |
| api.py | rulings_rule | 14059 | 7 | 171:6,172:1 | liaison:7 | yes | is not a line of the page. The page numbers its rows 1 to  ; use thos |
| api.py | rulings_rule | 14067 | 0 |  |  | yes | is a row of his earlier answer, and this page does not number it. Rul |
| api.py | rulings_rule | 14086 | 35 | 170:8,171:7,172:13,173:7 | liaison:35 | yes | line   is his read-back line, and only his words confirm it. His reply |
| api.py | rulings_rule | 14096 | 0 |  |  | yes | acts is a map of the keys of rulings to an act, for example {"2": {"ac |
| api.py | rulings_rule | 14103 | 0 |  |  | yes |  |
| api.py | rulings_rule | 14108 | 3 | 170:2,171:1 | liaison:3 | yes | acts has the key  , and rulings has no such key. Each key of acts is a |
| api.py | rulings_rule | 14112 | 0 |  |  | yes | acts[ ] is an object with act, target and words |
| api.py | rulings_rule | 14119 | 0 |  |  | yes | acts[ ] gives the verdict. |
| api.py | rulings_rule | 14121 | 1 | 170:1 | liaison:1 | yes | line  : acts and rulings give two verdicts. Give the verdict in ruling |
| api.py | rulings_rule | 14125 | 2 | 171:2 | liaison:2 | yes | line   has its act in rulings and in acts. Give it once |
| api.py | rulings_rule | 14146 | 42 | 170:1,171:24,172:10,173:7 | liaison:42 | yes | : the act   rests on  , and his words do not hold it. Copy the words o |
| api.py | rulings_rule | 14209 | 0 |  |  | yes | is the team's note, not your request. The words use a word the note i |
| api.py | rulings_rule | 14224 | 0 |  |  | yes | is the team's note, not your request. To drop the note, contest it. |
| api.py | rulings_rule | 14248 | 0 |  |  | yes | That code is line  , and the team rewrites it from the principal's wo |
| api.py | rulings_rule | 14254 | 0 |  |  | yes | That code is line  , the change's plan. Rule line   contest with the |
| api.py | rulings_rule | 14261 | 0 |  |  | yes | The team has not guessed that code yet. Rule the key   contest with t |
| api.py | rulings_rule | 14282 | 0 |  |  | yes | is the change's plan, and the change is  . A ruling on it moves nothi |
| api.py | rulings_rule | 14289 | 3 | 171:3 | liaison:3 | yes | the words do not fault the code of  . Approve |
| api.py | rulings_rule | 14327 | 0 |  |  | yes | is the change's line, and the change is  . A ruling on it moves nothi |
| api.py | rulings_rule | 14339 | 4 | 171:4 | liaison:4 | yes | the words do not fault  's files. |
| api.py | rulings_rule | 14357 | 21 | 170:3,171:8,172:3,173:7 | liaison:21 | yes | lines   have no ruling. Every line of the page takes one: the ask clos |
| api.py | rulings_rule | 14399 | 32 | 170:9,171:6,172:11,173:6 | liaison:32 | yes |  |
| api.py | rulings_rule | 14473 | 32 | 170:9,171:6,172:11,173:6 | liaison:32 | yes |  |
| api.py | rulings_rule | 14477 | 0 |  |  | yes |  |
| api.py | rulings_rule | 14482 | 0 |  |  | yes | a reading carries the principal's words, and words is empty. Pass the |
| api.py | rulings_rule | 14489 | 20 | 170:3,171:7,172:10 | liaison:20 | yes | a contest carries the principal's words to the row's owner, and words |
| api.py | rulings_line | 14557 | 0 |  |  | op not called | no open page: this session was not woken by a reply to a confirm, a pr |
| api.py | rulings_line | 14572 | 0 |  |  | op not called | is not a line of the page. The page numbers its rows 1 to  ; `line` t |
| api.py | ledger_log | 14838 | 1 | 172:1 | developer:1 | yes |  |
| api.py | ledger_log | 14844 | 108 | 170:25,171:31,172:25,173:27 | vision_keeper:100,terminologist:4,developer:4 | yes |  |
| api.py | ledger_log | 14872 | 0 |  |  | yes | is a message. An assumption is about a row of the project, never abou |
| api.py | ledger_log | 14882 | 0 |  |  | yes | an assumption is a sentence a reader learns from. Name what went unrea |
| api.py | ledger_log | 14915 | 53 | 170:16,171:8,172:18,173:11 | vision_keeper:20,liaison:2,terminologist:29,developer:2 | yes | names no row. about_ref is the id of the row the assumption is about |
| api.py | ledger_log | 14924 | 0 |  |  | yes | is a ledger row. An assumption is about an artefact, never about anot |
| api.py | ledger_log | 14936 | 6 | 170:2,171:2,172:1,173:1 | terminologist:3,developer:3 | yes | ledger.log  is a row of  , not of  . about_ref and about_table name on |
| api.py | ledger_log | 14950 | 0 |  |  | yes | an assumption is a sentence a reader learns from. Name what went unrea |
| api.py | ledger_log | 14970 | 88 | 170:22,171:22,172:22,173:22 | vision_keeper:88 | yes | the two halves of this assumption say the same words: what the README |
| api.py | ledger_log | 14986 | 160 | 170:40,171:40,172:40,173:40 | vision_keeper:160 | yes |  |
| api.py | ledger_log | 14990 | 6 | 172:6 | developer:6 | yes | a conflict with   is a question for the row's owner, and the owner ans |
| api.py | ledger_log | 15004 | 4 | 172:4 | developer:1,tester:3 | yes | a change of scope on   is a question for the Vision Keeper, which owns |
| api.py | _refuse_an_echo | 15120 | 12 | 170:3,171:2,172:6,173:1 | terminologist:12 | yes | the principal ruled on   in the relay that woke you, and their words a |
| api.py | ledger_unaddressed | 15195 | 4 | 171:4 | liaison:4 | yes | names no row. about_ref is the id of a row the question was about, fr |
| api.py | ledger_unaddressed | 15200 | 0 |  |  | yes | question is the question you put to the principal, in one sentence. Th |
| api.py | decisions_author | 15277 | 0 |  |  | yes | you amended   this session, so a decision about it would be minuting y |
| api.py | decisions_author | 15300 | 0 |  |  | yes | decisions.author  is a criterion, and resolves_ledger takes the id of |
| api.py | decisions_author | 15306 | 0 |  |  | yes | resolves_ledger is the id of the ledger entry this decision closes, no |
| api.py | decisions_author | 15335 | 0 |  |  | yes | decisions.author A decision has no supersedes for an item. ` ` is an i |
| api.py | decisions_author | 15351 | 1 | 172:1 | vision_keeper:1 | yes | decisions.author ` is the principal's decision. A seat's decision does |
| api.py | decisions_author | 15365 | 1 | 172:1 | vision_keeper:1 | yes | Write yours under a new id. |
| api.py | verdicts_claim_encodes | 15420 | 0 |  |  | yes | you already claimed  's test   it this session; that is the session's |
| api.py | verdicts_emit | 15480 | 0 |  |  | yes | you have already challenged the tester this session, and that is your |
| api.py | verdicts_emit | 15495 | 19 | 170:3,171:2,172:6,173:8 | critic:19 | yes | your verdict on batch   at this commit already landed, and one commit |
| api.py | verdicts_emit | 15509 | 0 |  |  | yes | A fail names a live criterion of batch |
| api.py | verdicts_emit | 15529 | 0 |  |  | yes | . `verdicts.claim_encodes( , encodes=...)` first: True and the fail ca |
| api.py | verdicts_rule | 16584 | 0 |  |  | op not called | is not the finding you were woken about. That is  , and it is the fin |
| api.py | verdicts_rule | 16589 | 0 |  |  | op not called | is not a ruling. A ruling is 'upheld', and the Developer answers the |
| api.py | verdicts_rule | 16594 | 0 |  |  | op not called | a ruling carries its reason: the line or the verdict that decided it |
| api.py | verdicts_rule | 16600 | 0 |  |  | op not called | is not a finding on file |
| api.py | schedule_reask | 16654 | 0 |  |  | yes | what_is_missing is what you cannot proceed without, in words. The role |
| api.py | schedule_reask | 16661 | 0 |  |  | yes | this says the answer that woke you did not resolve your question, and |
| api.py | schedule_reask | 16682 | 4 | 170:4 | tester:4 | yes | the message that woke you is not a reply to a question you asked |
| api.py | schedule_reask | 16689 | 0 |  |  | yes | Only the role that asked can say that the answer did not land. |
| api.py | _claim_of | 18029 | 0 |  |  | yes | names no claim: a claim ref is <table>:<row id> over |
| api.py | challenge_uphold | 18184 | 0 |  |  | yes | an uphold carries the line that supports the claim: quote= the source' |
| api.py | challenge_uphold | 18188 | 0 |  |  | yes | uphold |
| api.py | challenge_break | 18221 | 0 |  |  | yes | a break carries at least its reason: why= what defeats the claim |
| api.py | challenge_break | 18227 | 2 | 170:1,171:1 | critic:2 | yes | a break carries the line and the reason: quote= the source's words, ci |
| api.py | challenge_break | 18237 | 0 |  |  | yes | a break, even flagged, is a reading's act: open the claim's cited file |
| api.py | challenge_vacuous | 18289 | 0 |  |  | yes | say what makes it empty: why= the reason no line could support or defe |
| api.py | challenge_vacuous | 18292 | 0 |  |  | yes | vacuity is still a reading's verdict: call challenge.load first. It sh |
| api.py | frame_assign | 18429 | 0 |  |  | yes | kind must be one of program/attached/ignore/boundary, not |
| api.py | frame_assign | 18440 | 4 | 170:2,171:2 | architect:4 | yes | covers nothing in the index; assign a path the tree above actually sh |
| api.py | frame_assign | 18443 | 4 | 170:1,171:1,172:1,173:1 | architect:4 | yes | is a manifest: claimed mechanically as a boundary already, not the ju |
| api.py | frame_assign | 18448 | 0 |  |  | yes | carries a principal's ruling, which outranks the judge; it stands |
| api.py | _batch_worktree | 18997 | 0 |  |  | yes | batch   has no worktree . Code is written and committed in a batch's w |
| api.py | walk | 19866 | 0 |  |  | yes |  |
| api.py | _within | 20535 | 0 |  |  | yes | escapes the worktree |
| api.py | _code_write | 20683 | 0 |  |  | yes | no batch: code is written in a batch's worktree, and this session was |
| api.py | _code_write | 20723 | 0 |  |  | yes | is the name of the argument, not a file. Send the file's path, the on |
| api.py | _code_write | 20734 | 0 |  |  | yes | start=  came with no end. Send end=-1 for the whole file, or the end o |
| api.py | _empty_write | 20755 | 1 | 170:1 | developer:1 | yes | an empty write to   changes nothing the tree can use. To take out a fi |
| api.py | _code_write | 20776 | 0 |  |  | yes | does not exist, so start= , end=  names no lines to replace. Write a |
| api.py | _code_write | 20783 | 0 |  |  | yes | start= , end=  is not a span of  , which has   lines lines |
| api.py | _code_write | 21251 | 0 |  |  | yes |  |
| api.py | _future_door | 21279 | 0 |  |  | yes | code.write start= , end= : Python refuses any statement above the `fro |
| api.py | _code_write | 21320 | 0 |  |  | yes | start= , end= : line   is the docstring of  . Your text goes before it |
| api.py | _code_write | 21376 | 0 |  |  | yes |  |
| api.py | _code_write | 21432 | 0 |  |  | yes | is a new module at the project root, and the project's package lives |
| api.py | _code_write | 21439 | 0 |  |  | yes | at the project root has the name of the standard-library module  , an |
| api.py | _code_write | 21523 | 0 |  |  | yes |  |
| api.py | _code_write | 21528 | 0 |  |  | yes | is not valid Python ( , line   in code.source numbering); the harness |
| api.py | _code_write | 21576 | 7 | 171:7 | developer:7 | yes | is not valid Python ( , line   in code.source numbering); the harness |
| api.py | _code_write | 21613 | 0 |  |  | yes | defines   twice (lines   and  ). Python keeps the last one and the fi |
| api.py | _code_write | 21683 | 0 |  |  | yes | defines  , and the tree already defines   in  . A second definition o |
| api.py | _code_write | 21715 | 2 | 170:1,171:1 | developer:2 | yes | is a test file, and the tests are the Tester's. The harness runs the |
| api.py | _code_write | 21740 | 0 |  |  | yes | is the program's entry point: it has an `if __name__ == "__main__":` |
| api.py | _code_write | 21765 | 0 |  |  | yes | the `__main__` block of   calls  , which the file defines today and th |
| api.py | _code_write | 21788 | 0 |  |  | yes | reads input() at module level (line  ), so importing it under pytest |
| api.py | _code_write | 21837 | 0 |  |  | yes | reads input() internally, and a test in this batch calls  () directly |
| api.py | _code_write | 21897 | 0 |  |  | yes | is the surface for a criterion that gets its value from the user (  t |
| api.py | _code_write | 22051 | 2 | 172:2 | developer:2 | yes | this rewrite of   drops  , and  . To change   alone, write only   span |
| api.py | _code_write | 22066 | 26 | 171:22,172:4 | developer:26 | yes | this rewrite of   drops  , and  . Either write the whole file with eve |
| api.py | _code_write | 22158 | 0 |  |  | yes | imports   from   at module level, and   imports  : a cycle, and every |
| api.py | _code_write | 22171 | 127 | 170:20,171:56,172:31,173:20 | vision_keeper:30,architect:20,liaison:3,critic:9,terminologist:9,developer:56 | yes |  |
| api.py | _code_write | 22174 | 0 |  |  | yes | the batch's tests import   and no such module exists yet;   is a name |
| api.py | _code_write | 22184 | 0 |  |  | yes | is not where `import  ` looks: the import path is the worktree root, |
| api.py | code_commit | 22554 | 0 |  |  | yes | no batch: a commit belongs to one |
| api.py | code_commit | 22561 | 1 | 172:1 | developer:1 | yes |  |
| api.py | code_commit | 22620 | 0 |  |  | yes | the tree does not define  , the surface the criteria name and the test |
| api.py | code_commit | 22646 | 0 |  |  | yes |  |
| api.py | code_commit | 22658 | 0 |  |  | yes | . Change the file, then commit nothing changed, and the finding stands |
| api.py | batches_judge_touch | 24364 | 0 |  |  | yes | has no unjudged stray on its head commit; nothing to judge |
| api.py | batches_judge_touch | 24399 | 0 |  |  | yes | cannot be both foreseen and a mistake |
| api.py | batches_judge_touch | 24413 | 0 |  |  | yes | still unjudged, because a file path does not judge a removal. Name |
| api.py | batches_judge_touch | 24427 | 0 |  |  | yes | still unjudged. Every open stray is foreseen or a mistake; say which |
| api.py | batches_judge_touch | 24453 | 0 |  |  | yes | no code, and the plan did not name the file before the write. A fores |
| api.py | batches_strays | 24488 | 0 |  |  | yes | is not a batch |
| api.py | references_record | 24701 | 0 |  |  | op not called | your fetch of   was refused this session, so there is no passage behin |
| api.py | batches_expect | 24762 | 0 |  |  | yes | is not a batch |

## Appendix C. Refusal texts that come from other code

These lines match no `raise ValueError` site of the two files. The source is the statement whose literals match best.

| Source | Function | Line | Count | Seats | First words |
|---|---|---|---|---|---|
| runner.py | run_session | 5828 | 453 | vision_keeper:308,critic:56,developer:10,tester:59,architect:10,terminologist:10 | repeat refused: code.probe asked three times this session and the answer has not |
| runner.py | run_session | 5497 | 194 | vision_keeper:56,critic:49,terminologist:13,architect:40,developer:24,tester:10,liaison:2 | wrote its own tool results |
| runner.py | run_session | 5504 | 166 | vision_keeper:28,critic:49,terminologist:13,architect:40,developer:24,tester:10,liaison:2 | the stream stopped at the invented result "OK code.probe ->" on line 3 of the re |
| api.py | _misplaced_conflict | 15092 | 160 | vision_keeper:160 | defines_commands_and_options is the row this note is about, and one side of the |
| (none) |  | 0 | 122 | vision_keeper:30,liaison:25,critic:17,architect:19,tester:19,developer:7,terminologist:5 | repeated its previous turn verbatim twice; ended |
| api.py | kind_questions | 14654 | 108 | vision_keeper:100,terminologist:4,developer:4 | kind='none' is no word this mode offers. Answer three questions, and the word fo |
| api.py | code_callables | 18610 | 64 | architect:41,terminologist:23 | cut the candidate symbols: 865 of 885 rows not shown |
| api.py | code_callables | 18625 | 45 | terminologist:16,architect:29 | cut the symbols matching the hint: 36 of 76 rows not shown |
| api.py | _code_write | 22307 | 38 | vision_keeper:20,critic:9,terminologist:9 | a quote inside assumption ended it early, and the text after that quote is not a |
| runner.py | run_session | 5979 | 36 | vision_keeper:2,terminologist:12,developer:5,tester:6,critic:10,architect:1 | code.probe was refused the same way in four turns; the session ended on it |
| runner.py | run_session | 5781 | 34 | vision_keeper:24,architect:10 | repeat refused: code.source served three times this session, and the window took |
| api.py | _code_write | 22303 | 33 | vision_keeper:10,architect:20,liaison:3 | unterminated argument list: a quote inside a quoted argument ended the string ea |
| runner.py | run_session | 5231 | 31 | vision_keeper:14,architect:11,terminologist:3,tester:2,critic:1 | your reply was cut at the output budget before it ended, so the last call did no |
| sandbox.py | __getattr__ | 451 | 29 | liaison:15,architect:7,terminologist:5,vision_keeper:2 | 'transcript.quote' is not in this role's working set; available: msg.present_pri |
| runner.py | run_session | 5336 | 29 | liaison:10,vision_keeper:6,critic:2,tester:5,terminologist:3,architect:1,developer:2 | named an act and did not perform it |
| api.py | challenge_vacuous | 18311 | 28 | critic:28 | cut the challenge row's why: 44 of 344 characters not stored |
| api.py | tests_encode | 9932 | 21 | tester:21 | pytest will collect nothing from this body: it needs a def test_...() containing |
| api.py | _twin_refusal | 5976 | 20 | terminologist:20 | those are c_4's words already, on the same ticket. The same words are the same c |
| api.py | _unnamed_contest | 13430 | 19 | liaison:19 | The words name lines 1 and 18 to 29 and do not name lines 2 to 17. A contest res |
| runner.py | run_session | 5359 | 15 | liaison:7,developer:6,terminologist:2 | ended a tick with nothing done |
| sandbox.py | _rows_quote_refusal | 1124 | 15 | architect:5,terminologist:10 | quotes= holds no span of the live text of inh_fe7f4bfc, and refs names inh_fe7f4 |
| api.py | _faulted_approve | 13316 | 12 | liaison:12 | The words fault line 1, "are fine". An approve keeps the line as it is, and his |
| api.py | tests_encode | 9922 | 12 | tester:12 | the body is not Python (unterminated string literal (detected at line 11), line |
| runner.py | _native_calls | 6448 | 11 | vision_keeper:2,developer:3,liaison:4,tester:2 | could not parse arguments: malformed node or string on line 1: BinOp(left=Name(i |
| api.py | _near_twin | 6839 | 11 | terminologist:11 | this says what c_4 says, in nearly the same words ('When get_app_dir is called o |
| api.py | _first_pass_hold | 16528 | 11 | critic:11 | before the pass lands, answer for c_1, c_2, c_3, c_4 and c_5. Criterion c_1 says |
| api.py | challenge_uphold | 18194 | 8 | critic:8 | cut the challenge row's quote: 107 of 407 characters not stored |
| api.py | _refuse_after_challenge | 20634 | 8 | developer:8 | you sent challenge to tester in this session (m55): you challenged the test, and |
| sandbox.py | _ruling_answer_refusal | 2090 | 7 | terminologist:7 | No respecify of c_1_format_filename_example has landed in this session. The prin |
| api.py | _pass_lines_check | 16200 | 7 | critic:7 | the value for c_1 holds 8 lines, and a pass names one added line per criterion. |
| api.py | _code_write | 21118 | 7 | developer:7 | start=506, end=527: start=506 falls inside docstring (lines 484 to 514 in code.s |
| api.py | challenge_break | 18268 | 7 | critic:7 | cut the principal's ledger row, from this verdict's quote: 35 of 195 characters |
| api.py | _arrange_run_refusal | 20055 | 6 | tester:6 | The run of this body on the batch's head raises at line 18, `result = get_app_di |
| api.py | _stray_act_fields | 11682 | 6 | liaison:6 | rulings.rule: `act`, `target_kind`, `words` are fields of line 2's object, not l |
| sandbox.py | _bind_positional | 209 | 6 | liaison:6 | msg.relay_vision_keeper: ['round_no'] given both by position and by name |
| api.py | _code_write | 21544 | 6 | developer:6 | src/click/utils.py is not valid Python (expected ':', line 484 in code.source nu |
| api.py | tests_encode | 10736 | 6 | tester:6 | the surface 'src/click/utils.py::get_app_dir' lives in utils.py and this test im |
| sandbox.py | _green_at_head_refusal | 1638 | 6 | developer:6 | tst_c3_format_filename_example passes on the batch's head 128bec7e: its last run |
| sandbox.py | validate_args | 357 | 5 | architect:5 | batches.consult: unexpected argument(s) ['id']; accepts () |
| runner.py | run_session | 5311 | 5 | tester:5 | wrote a test into its reply |
| sandbox.py | _challenge_repeat_refusal | 3229 | 5 | developer:5 | you sent challenge to tester on exactly these refs already (m56) and they answer |
| api.py | _pass_lines_check | 16206 | 4 | critic:4 | a pass names, for each criterion, the added line of the diff that meets it, and |
| api.py | tests_triage | 8086 | 4 | tester:4 | tests.triage: verdict='attested' is not one of ['encodable', 'cannot', 'ambiguou |
| api.py | _surface_outside_batch | 5609 | 4 | terminologist:4 | 'src/click/exceptions.py::MissingParameter' lives in src/click/exceptions.py, an |
| sandbox.py | _scalar_refusal | 263 | 3 | liaison:3 | msg.relay_vision_keeper: round_no='The principal has already answered that with |
| sandbox.py | _bind_send | 4483 | 3 | terminologist:3 | an answer from the glossary carries a term, and refs=['tk_1'] names none. The gl |
| sandbox.py | validate_args | 399 | 3 | liaison:1,terminologist:2 | ledger.unaddressed: about_ref was given a list; it takes a single value (about_r |
| api.py | _escape_refusal | 19875 | 3 | tester:3 | line 15 of the body, `assert "AppData\Local" in result`, holds `\L`, and `\L` th |
| sandbox.py | _quote_refusal | 1598 | 3 | developer:3 | quotes= holds `runner.invoke(cmd, ['--version'])`, and it is not in the live tex |
| runner.py | run_session | 5293 | 3 | developer:3 | wrote code into its reply |
| sandbox.py | _rowless_answer_refusal | 1343 | 3 | architect:3 | refs=['c_3', 'tst_get_app_dir_no_exception', 'd_65b74b7809'] add no row to the r |
| api.py | _surface_move_fault | 6470 | 2 | terminologist:2 | The item asks for `format_filename`, and this move drops `format_filename` from |
| api.py | _code_write | 21145 | 2 | developer:2 | start=506, end=507: start=506 falls inside docstring (lines 484 to 514 in code.s |
| sandbox.py | _same_refs_refusal | 3367 | 2 | developer:2 | you sent escalate to architect on exactly these refs already (m58) and they answ |
| api.py | _code_write | 21341 | 2 | developer:2 | start=530, end=538 crosses from one block to another. start=530 is in the body o |
| api.py | _argument_key | 13747 | 2 | liaison:2 | rulings has a key ask, and ask is its own argument, not a line of the page. A qu |
| api.py | _twin_refusal | 5990 | 2 | terminologist:2 | those are c_10's words already, on the same ticket. c_10 is your criterion from |
| api.py | _argument_key | 13771 | 2 | liaison:2 | rulings has a key acts, and acts is its own argument, not a line of the page: ru |
| api.py | contested_refusal | 1180 | 2 | liaison:2 | the principal contested s3 in r_m81, so s3 is not ratified and not delivered. Ra |
| api.py | _bound_exit | 4110 | 2 | architect:2 | 'c_1_format_filename_example' is a row of criteria, not a constraint. A finding |

73 sources in all. The table shows the 60 largest.

## Appendix D. The rulings door, fact doors and reading doors

| Kind | Function | Line | Refusals | In a session that later landed a ruling | In a session that landed none |
|---|---|---|---|---|---|
| fact | rulings_rule | 14146 | 36 | 10 | 26 |
| fact | rulings_rule | 14357 | 21 | 15 | 6 |
| fact | rulings_rule | 14489 | 20 | 2 | 18 |
| fact | _ruling_word | 11556 | 9 | 3 | 6 |
| fact | rulings_rule | 14059 | 7 | 4 | 3 |
| fact | _stray_act_fields | 11682 | 6 | 6 | 0 |
| fact | _ruling_shape | 11839 | 6 | 2 | 4 |
| fact | _ruling_word | 11546 | 6 | 1 | 5 |
| fact | rulings_rule | 14108 | 3 | 2 | 1 |
| fact | rulings_rule | 14125 | 2 | 2 | 0 |
| fact | _argument_key | 13747 | 2 | 0 | 2 |
| fact | refuse_answered_question | 854 | 2 | 2 | 0 |
| fact | _argument_key | 13771 | 2 | 2 | 0 |
| fact | rulings_rule | 14121 | 1 | 1 | 0 |
| fact | _stray_act_fields | 11641 | 1 | 1 | 0 |
| reading | rulings_rule | 14086 | 35 | 25 | 10 |
| reading | _unnamed_contest | 13430 | 19 | 8 | 11 |
| reading | _faulted_approve | 13316 | 12 | 8 | 4 |
| reading | rulings_rule | 14339 | 4 | 1 | 3 |
| reading | rulings_rule | 14289 | 3 | 0 | 3 |
| reading | _line_refusal | 13040 | 1 | 1 | 0 |

## Appendix E. The wake kinds

| Wake kind | Raised as a session | Named in the launch log | Never |
|---|---|---|---|
| cascade |  |  | never |
| do:cancel |  |  | never |
| do:defer_baseline |  |  | never |
| do:harness |  | 170:7,171:7,172:11,173:10 |  |
| do:merge |  | 170:2,171:1,172:2,173:3 |  |
| do:park |  |  | never |
| do:preempt |  | 171:1 |  |
| message | 170:86,171:94,172:111,173:77 |  |  |
| tick:agenda | 170:2,171:2,172:2,173:1 |  |  |
| tick:annotate | 170:3,171:2,172:3,173:3 |  |  |
| tick:awaiting_confirm | 172:1 |  |  |
| tick:batch_start | 170:3,171:2,172:3,173:4 |  |  |
| tick:blindspot | 170:1,171:1,172:1,173:1 |  |  |
| tick:boundary | 170:3,171:3,172:3,173:3 |  |  |
| tick:challenge | 170:15,171:14,172:27,173:37 | 172:1,173:1 |  |
| tick:checkpoint_invalid |  |  | never |
| tick:constraint_zero |  |  | never |
| tick:contested | 170:1,171:4 |  |  |
| tick:contradiction |  |  | never |
| tick:criteria | 170:3,171:2,172:3,173:3 |  |  |
| tick:criterion_repair | 172:1 |  |  |
| tick:define | 170:20,171:20,172:20,173:20 |  |  |
| tick:exhausted | 170:3,171:3,172:3 |  |  |
| tick:finding_review |  |  | never |
| tick:finding_violated |  |  | never |
| tick:findings_exhausted |  |  | never |
| tick:frame | 170:1,171:1,172:1,173:1 |  |  |
| tick:grouping | 170:3,171:2,172:3,173:3 |  |  |
| tick:guess | 170:3,171:3,172:3,173:3 |  |  |
| tick:observed_entries | 170:2,171:1,172:2,173:3 |  |  |
| tick:orient | 170:1,171:1,172:1,173:1 |  |  |
| tick:park_ask |  |  | never |
| tick:quarantined | 170:2,171:4,172:4,173:3 |  |  |
| tick:reconcile | 170:40,171:40,172:39,173:39 |  |  |
| tick:reopen |  |  | never |
| tick:reorient | 170:1,171:1,172:1,173:1 |  |  |
| tick:request_shift | 171:2 |  |  |
| tick:review | 170:2,171:4,172:3,173:3 | 171:1 |  |
| tick:round_close | 173:3 | 173:1 |  |
| tick:signoff | 170:4,171:4,172:4,173:4 |  |  |
| tick:slicing | 170:3,171:2,172:3,173:3 |  |  |
| tick:structural_review | 170:2,171:1,172:2,173:3 |  |  |
| tick:survey | 170:12,171:4,172:12,173:12 |  |  |
| tick:term_collision | 170:3,171:1,172:2,173:3 |  |  |
| tick:tests_failing | 170:2,171:6,172:4,173:3 | 172:1 |  |
| tick:tests_missing | 170:5,171:2,172:5,173:4 | 170:1 |  |
| tick:touch_mistaken | 172:3 |  |  |
| tick:touch_note | 170:3,171:2,172:3,173:3 |  |  |
| tick:touch_strayed | 171:1,172:1 |  |  |
| tick:unresolved | 170:1,171:2 |  |  |
| tick:verdict_failed | 172:1 |  |  |

## Appendix F. The predicates of predicates.py

| Predicate | Wake kinds | Fired |
|---|---|---|
| message_tips | message | fired |
| request_shift | tick:request_shift | fired |
| awaiting_confirm | tick:awaiting_confirm | fired |
| contradiction | tick:contradiction | never |
| contested | tick:contested | fired |
| guess | tick:guess | fired |
| signoff | tick:signoff | fired |
| term_collision | tick:term_collision | fired |
| round_close | tick:round_close | fired |
| slicing | tick:slicing | fired |
| criteria | tick:criteria | fired |
| grouping | tick:grouping | fired |
| observed_entries | do:defer_baseline, tick:observed_entries | fired |
| tests_missing | tick:tests_missing | fired |
| harness | do:harness | fired |
| annotate | tick:annotate | fired |
| touch_note | tick:touch_note | fired |
| batch_start | tick:batch_start | fired |
| tests_failing | tick:tests_failing | fired |
| reopen | tick:reopen | never |
| exhausted | tick:exhausted | fired |
| findings_exhausted | tick:exhausted, tick:findings_exhausted | fired |
| unresolved | tick:unresolved | fired |
| criterion_repair | tick:criterion_repair | fired |
| review | tick:review | fired |
| finding_review | tick:finding_review | never |
| structural_review | tick:structural_review | fired |
| verdict_failed | tick:verdict_failed | fired |
| finding_violated | tick:finding_violated | never |
| cancel | do:cancel | never |
| preempt | do:park, do:preempt | fired |
| merge | do:merge | fired |
| checkpoint_invalid | tick:checkpoint_invalid | never |
| quarantined | tick:quarantined | fired |
| park_ask | tick:park_ask | never |
| agenda | tick:agenda | fired |
| constraint_zero | tick:constraint_zero | never |
| frame | tick:frame | fired |
| orient | tick:orient | fired |
| reconcile | tick:reconcile | fired |
| define | tick:define | fired |
| survey | tick:survey | fired |
| reorient | tick:reorient | fired |
| boundary | tick:boundary | fired |
| challenge | tick:challenge | fired |
| blindspot | tick:blindspot | fired |
| touch_strayed | tick:touch_strayed | fired |
| touch_mistaken | tick:touch_mistaken | fired |

48 predicates, 40 fired, 8 never.

## Appendix G. The prompt files

Read means half or more of the file's lines over 40 characters are in the system prompt of a session. A file of three lines or fewer is weak evidence. `.tools` files are not matched by text.

| File | Lines matched | Read | Nights | Wakes |
|---|---|---|---|---|
| architect/annotate.md | 18/18 | read | 170,171,172,173 | message,tick:annotate |
| architect/answer.md | 18/18 | read | 170,171 | message |
| architect/ask.md | 0/11 | never |  |  |
| architect/base.md | 32/33 | read | 170,171,172,173 | message,tick:annotate,tick:boundary,tick:exhausted,tick:fram |
| architect/boundary.md | 28/28 | read | 170,171,172,173 | tick:boundary |
| architect/deliver.md | 25/25 | read | 170,171,172,173 | message |
| architect/escalate.md | 32/32 | read | 170,171,172 | message |
| architect/exhausted.md | 17/17 | read | 170,171,172 | tick:exhausted |
| architect/frame.md | 27/27 | read | 170,171,172,173 | tick:frame |
| architect/grouping.md | 14/14 | read | 170,171,172,173 | tick:grouping |
| architect/guess.md | 16/16 | read | 170,171,172,173 | message,tick:guess |
| architect/relay.md | 13/13 | read | 170,171,172,173 | message |
| architect/structural_review.md | 18/18 | read | 170,171,172,173 | tick:structural_review |
| architect/survey.base.md | 3/3 | read | 170,171,172,173 | tick:survey |
| architect/survey.md | 33/33 | read | 170,171,172,173 | tick:survey |
| architect/touch_strayed.md | 28/28 | read | 171,172 | tick:touch_strayed |
| architect/unresolved.md | 21/21 | read | 171 | tick:unresolved |
| critic/answer.md | 0/18 | never |  |  |
| critic/base.md | 26/26 | read | 170,171,172,173 | tick:review |
| critic/challenge.base.md | 4/4 | read | 170,171,172,173 | tick:challenge |
| critic/challenge.md | 34/34 | read | 170,171,172,173 | tick:challenge |
| critic/finding_review.md | 0/18 | never |  |  |
| critic/review.md | 44/44 | read | 170,171,172,173 | tick:review |
| developer/answer.md | 45/46 | read | 170,171,172,173 | message |
| developer/base.md | 15/15 | read | 170,171,172,173 | message,tick:batch_start,tick:exhausted,tick:tests_failing,t |
| developer/batch_start.md | 46/46 | read | 170,171,172,173 | tick:batch_start |
| developer/challenge.md | 0/18 | never |  |  |
| developer/exhausted.md | 20/21 | read | 170,171,172 | tick:exhausted |
| developer/finding_violated.md | 0/20 | never |  |  |
| developer/findings_exhausted.md | 6/16 | never |  |  |
| developer/reopen.md | 0/11 | never |  |  |
| developer/tests_failing.md | 43/43 | read | 170,171,172,173 | tick:tests_failing |
| developer/touch_mistaken.md | 11/13 | read | 172 | tick:touch_mistaken |
| developer/verdict_failed.md | 13/13 | read | 172 | tick:verdict_failed |
| liaison/agenda.md | 15/15 | read | 170,171,172,173 | tick:agenda |
| liaison/answer.md | 0/31 | never |  |  |
| liaison/answering.md | 62/62 | read | 170,171,172,173 | message |
| liaison/awaiting_confirm.md | 4/4 | read | 172 | tick:awaiting_confirm |
| liaison/base.md | 37/37 | read | 170,171,172,173 | message,tick:agenda,tick:awaiting_confirm,tick:blindspot,tic |
| liaison/blindspot.md | 21/22 | read | 170,171,172,173 | tick:blindspot |
| liaison/contradiction.md | 0/6 | never |  |  |
| liaison/converse.md | 79/79 | read | 170,171,172,173 | message |
| liaison/landing.base.md | 13/13 | read | 170,171,172,173 | message |
| liaison/landing.md | 62/62 | read | 170,171,172,173 | message |
| liaison/observed_entries.md | 11/11 | read | 170,171,172,173 | tick:observed_entries |
| liaison/park_ask.md | 0/9 | never |  |  |
| liaison/quarantined.md | 14/14 | read | 170,171,172,173 | tick:quarantined |
| liaison/report.md | 33/33 | read | 170,171,172,173 | message |
| liaison/request_shift.md | 3/3 | read | 171 | tick:request_shift |
| liaison/round_close.md | 34/34 | read | 173 | tick:round_close |
| liaison/submit.md | 24/24 | read | 170,171,172,173 | message |
| liaison/touch_note.md | 13/13 | read | 170,171,172,173 | tick:touch_note |
| liaison/unresolved.md | 0/19 | never |  |  |
| liaison/verdict.md | 24/24 | read | 170,171,172,173 | message |
| liaison/verdict_signoff.md | 18/18 | read | 170,171,172,173 | message |
| researcher/base.md | 1/30 | never |  |  |
| researcher/question.md | 0/28 | never |  |  |
| terminologist/answer.md | 0/21 | never |  |  |
| terminologist/ask.md | 0/13 | never |  |  |
| terminologist/base.md | 29/30 | read | 170,171,172,173 | message,tick:criteria,tick:criterion_repair |
| terminologist/criteria.md | 36/36 | read | 170,171,172,173 | tick:criteria |
| terminologist/criterion_repair.md | 41/41 | read | 170,171,172,173 | message,tick:criterion_repair |
| terminologist/define.base.md | 2/2 | read | 170,171,172,173 | message,tick:agenda,tick:awaiting_confirm,tick:blindspot,tic |
| terminologist/define.md | 38/38 | read | 170,171,172,173 | tick:define |
| terminologist/deliver.md | 32/32 | read | 170,171,172,173 | message |
| terminologist/question.md | 15/15 | read | 170,171,172 | message |
| terminologist/relay.md | 9/9 | read | 170,171,172,173 | message |
| terminologist/survey.base.md | 2/2 | read | 170,171,172,173 | message,tick:agenda,tick:awaiting_confirm,tick:blindspot,tic |
| terminologist/survey.deprecation_candidate | 0/6 | never |  |  |
| terminologist/survey.md | 19/19 | read | 170,171,172,173 | tick:survey |
| terminologist/term_collision.base.md | 2/2 | read | 170,171,172,173 | message,tick:agenda,tick:awaiting_confirm,tick:blindspot,tic |
| terminologist/term_collision.md | 21/21 | read | 170,171,172,173 | tick:term_collision |
| terminologist/unresolved.md | 9/17 | read | 171 | tick:unresolved |
| terminologist/account/base.md | 2/2 | read | 170,171,172,173 | message,tick:agenda,tick:awaiting_confirm,tick:blindspot,tic |
| terminologist/account/survey.md | 1/13 | never |  |  |
| terminologist/account/term_collision.deprecation_candidate | 0/9 | never |  |  |
| terminologist/account/term_collision.md | 16/16 | read | 170,171,172,173 | tick:term_collision |
| terminologist/grain/base.md | 2/2 | read | 170,171,172,173 | message,tick:agenda,tick:awaiting_confirm,tick:blindspot,tic |
| terminologist/grain/survey.deprecation_candidate | 0/4 | never |  |  |
| terminologist/grain/survey.md | 1/19 | never |  |  |
| terminologist/source/base.md | 2/2 | read | 170,171,172,173 | message,tick:agenda,tick:awaiting_confirm,tick:blindspot,tic |
| terminologist/source/survey.deprecation_candidate | 0/3 | never |  |  |
| terminologist/source/survey.md | 1/19 | never |  |  |
| terminologist/vocab/base.md | 2/2 | read | 170,171,172,173 | message,tick:agenda,tick:awaiting_confirm,tick:blindspot,tic |
| terminologist/vocab/survey.deprecation_candidate | 0/4 | never |  |  |
| terminologist/vocab/survey.md | 0/19 | never |  |  |
| tester/answer.md | 15/15 | read | 170,171,172,173 | message |
| tester/base.md | 22/22 | read | 170,171,172,173 | message,tick:tests_missing |
| tester/challenge.md | 19/19 | read | 170,171,172,173 | message |
| tester/tests_missing.md | 51/51 | read | 170,171,172,173 | tick:tests_missing |
| vision_keeper/answer.md | 0/15 | never |  |  |
| vision_keeper/ask.md | 0/10 | never |  |  |
| vision_keeper/base.md | 25/26 | read | 170,171,172,173 | message,tick:contested,tick:exhausted,tick:reorient,tick:sig |
| vision_keeper/challenge.md | 14/14 | read | 170,171,172 | message |
| vision_keeper/contested.md | 40/40 | read | 170,171 | tick:contested |
| vision_keeper/deliver.md | 43/43 | read | 170,171,172,173 | message |
| vision_keeper/elect.md | 0/6 | never |  |  |
| vision_keeper/exhausted.md | 19/19 | read | 170,171,172 | tick:exhausted |
| vision_keeper/orient.base.md | 3/3 | read | 170,171,172,173 | tick:orient,tick:reconcile |
| vision_keeper/orient.md | 26/26 | read | 170,171,172,173 | tick:orient |
| vision_keeper/propose.md | 6/6 | read | 170 | message |
| vision_keeper/question.md | 9/9 | read | 170,171,172 | message |
| vision_keeper/reconcile.base.md | 3/3 | read | 170,171,172,173 | tick:orient,tick:reconcile |
| vision_keeper/reconcile.md | 28/28 | read | 170,171,172,173 | tick:reconcile |
| vision_keeper/relay.md | 17/17 | read | 170,171,172,173 | message |
| vision_keeper/reorient.md | 21/21 | read | 170,171,172,173 | tick:reorient |
| vision_keeper/signoff.md | 7/7 | read | 170,171,172,173 | tick:signoff |
| vision_keeper/slicing.md | 23/23 | read | 170,171,172,173 | tick:slicing |
| vision_keeper/survey.deprecation_candidate | 0/10 | never |  |  |
| vision_keeper/survey.md | 3/38 | never |  |  |
| vision_keeper/unresolved.md | 23/23 | read | 170,171 | tick:unresolved |

## Appendix H. The ops of the working sets never called

| Op | Working sets |
|---|---|
| code.survey | terminologist/grain/survey.tools, vision_keeper/survey.tools |
| code.vocabulary | terminologist/source/survey.tools, terminologist/vocab/survey.tools |
| msg.answer_critic | terminologist/question.tools, terminologist/unresolved.tools, tester/challenge.tools |
| msg.answer_liaison | architect/ask.tools, architect/unresolved.tools, terminologist/ask.tools, terminologist/unresolved.tools, vision_keeper/ask.tools, vision_keeper/unresolved.tools |
| msg.answer_terminologist | researcher/question.tools |
| msg.answer_vision_keeper | researcher/question.tools |
| msg.ask_terminologist | liaison/converse.tools |
| msg.ask_vision_keeper | liaison/converse.tools |
| msg.challenge_developer | critic/review.tools |
| msg.converse_principal | liaison/answer.tools |
| msg.elect_vision_keeper | developer/reopen.tools |
| references.record | researcher/question.tools |
| rulings.line | liaison/landing.tools |
| verdicts.rule | critic/finding_review.tools |
| web.fetch | researcher/question.tools |
| web.search | researcher/question.tools |

## Appendix I. The page sentences of principal.py

86 page calls on the four nights. A sentence is sent when its literals are in a page text.

| Function | Line | Sent | First words |
|---|---|---|---|
| ruled | 943 | never | ruling_status = 'landed' |
| const _READ_BACK_VERDICT | 1155 | never | is approved |
| const READ_BACK_ASK | 1163 | sent | Say ok, or say what we misread. |
| reading_line | 1261 | sent | Your answer " |
| code_line | 1806 | never | The team's plan for this change is closed. |
| code_line | 1810 | sent | expected to touch |
| code_line | 1814 | sent | The team's plan of the code this touches: |
| code_line | 1827 | sent | The team's guess at the code this touches: |
| request_block | 1913 | sent | The team has not guessed the code this touches yet. |
| request_block | 1923 | never | AND t.batch_id = ? |
| request_block | 1948 | sent | check: none. The team gave up writing it after |
| _name_request | 1959 | sent | To change what you asked for, name line |
| _name_request | 1960 | never | To change what you asked for, name its line, |
| _name_guess | 1970 | sent | To correct the code it touches, name line |
| _name_guess | 1971 | never | To correct the code they touch, name line |
| const TICK_WORDS | 2123 | never | tests_failing |
| _tick_words | 2152 | sent | the team could not finish a step |
| const TEAM_NOTES | 2176 | sent | The team's notes. A seat wrote each of these where your words were silent. They |
| const ACCOUNT_TODAY | 2180 | sent | What the project does today. This is not your request: |
| _park_page | 2192 | never | Nothing waits on you. A new commit on the change starts it again. |
| _park_page | 2202 | never | This change stopped. The team tried |
| _park_page | 2214 | never | Reply 'ok' if every line says what you want. The team then stops here and tells |
| _park_page | 2216 | sent | Name a line to correct only that line. Ask, if something here is unclear. |
| _shift_where | 2228 | sent | No change is built for it yet. |
| _shift_where | 2229 | sent | Its review stopped after |
| _built_words | 2246 | never | The change |
| _built_words | 2251 | never | The change |
| _built_words | 2254 | never | The change |
| _built_words | 2256 | sent | The change |
| _shift_waits | 2279 | sent | one page to you with |
| _shift_waits | 2291 | never | a new start of its review |
| _shift_page | 2309 | sent | You asked for something new: |
| _shift_page | 2311 | sent | Before that you asked for this, and it is not finished: |
| returned_line | 2356 | sent | Your last answer to this page did not reach the team. The team could not turn yo |
| const ACCOUNT_UNNAMED | 2387 | never | Your last answer named no line of the page about the project today, and answers |
| const _PIECE | 2437 | never | (`+) ?(.+?) ?\1(?: at line (\d+))? |
| _behaviour_words | 2472 | never | the branch |
| removal_line | 2499 | sent | The change removes code that no answer of yours allowed: |
| _quiet_line | 2574 | never | Not shown: |
| _page_body | 2746 | sent | Did I hear you right? I have taken this as |
| _page_body | 2750 | sent | Reply 'ok' if that is what you meant. Reply with words if it is wrong. After 'ok |
| _page_body | 2766 | sent | The review of this change stopped after |
| _page_body | 2770 | sent | The team stopped work on this change. |
| _page_body | 2779 | sent | The team expects to touch: |
| _page_body | 2781 | sent | Reply 'ok' if every line says what you want. Name a line to correct only that li |
| _page_body | 2785 | sent | Before I build this, here is what I expect to touch. |
| _page_body | 2790 | sent | The team expects to touch: |
| _page_body | 2793 | never | Some of that code has not been read yet. I cannot say what a change there might |
| _page_body | 2795 | sent | This is a prediction, not a promise. Reply 'ok' to go ahead. Reply with words if |
| _page_body | 2800 | never | Nothing here has been read yet, so I cannot say what a change might break. That |
| _page_body | 2803 | never | Reply 'ok' to go ahead. I will flag anything I touch that I have not read. |
| _page_body | 2806 | sent | Here is what I understand you want, on one page. |
| _page_body | 2815 | sent | What we are building: |
| _page_body | 2817 | never | How it is described: |
| _page_body | 2831 | sent | Where you did not say, I assumed: |
| _page_body | 2834 | sent | A word that means more than one thing here: |
| _page_body | 2840 | never | Some of this code has not been read yet. I will flag anything I touch there. |
| _page_body | 2842 | sent | Reply in your own words. 'ok' approves all of this and starts building. Name a l |
| _page_body | 2847 | sent | I need one thing from you before I can continue. |
| _page_body | 2856 | sent | Reply in a sentence. I take it from there. |
| touch_words | 2951 | never | the work for: |
| touch_words | 2952 | sent | expected to touch |
