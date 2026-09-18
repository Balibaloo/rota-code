# The pages rota put to its principal on nights 85 and 86

Rota workflow. Frame 40. The record lists every page the principal was shown on
the two nights, by verb and kind, with its size in tokens, the reply the
scripted principal gave, and a judgement of whether that reply was reasonable.

The run databases are `.rota/clickI_night85.db` and `.rota/clickI_night86.db`.
Night 85 ran from a worktree at 6895000. Night 86 ran from a worktree at
8b15af8.

## Method

1. A page is a row of `messages` with `to_role = 'principal'` and a verb other
   than `converse` (observed: `rota/roles/principal.py`, `pending_asks`).
2. Each page is rendered with `render_page`, the same function the night used.
   The file is unchanged since both night commits (observed: `git log
   6895000..HEAD` and `8b15af8..HEAD` on `rota/roles/principal.py` are empty).
3. Each page is measured on qwen3:8b through the Titan server, as a raw prompt,
   by `prompt_eval_count`. The count is not affected by the prompt cache. A
   repeated prompt returns the same number, and a leading nonce adds exactly
   its own tokens (observed: a probe of 2026-09-18, 201 tokens twice, 210 with
   a 9-token nonce).
4. The replies come from the `messages` rows the principal sent. What the
   Liaison made of the words comes from the `rulings` table.
5. Twelve agents judged whether each reply was reasonable. Twelve more agents
   refuted the judgements against a materiality test.

Two limits of the method:

- A page renders against the database as the night left it. A row that changed
  after the page was shown renders in its later form. The first line of every
  page matches the night log, which is the only per-page record the night kept
  (observed: `.rota/night85.log`, `.rota/night86.log`).
- The token count measures the page alone. It does not measure the seat prompt
  that carried the same rows.

One cross-check: night 85's page m27 measures 3019 tokens here, and the night
85 record gives 3039 from a different probe (observed:
`plans/archive/night85-2026-09-18.md`).

## The principal that answered

The principal was a script, not a person (observed: `probes/walk.py`, class
`Principal` with `WALK_WORDS` set). It gave prepared sentences:

- To every `present` and every `confirm`: "yes that all looks right, go ahead"
  (observed: `probes/gauntlet_click.sh:21`, which exports `WALK_WORDS`).
- To every `clarify` of one sentence: that sentence's single prepared answer.
  Sentence two's answer is "the flag defaults to False so nothing changes for
  existing callers" (observed: `probes/gauntlet_click.sh:78`, the third
  argument of the walk). Both clarifies of night 86 fall in sentence two, so
  both got that answer.

The words land as a principal `converse`. The ask stays open. The Liaison then
reads the words and records a ruling, which sets each row to approved or
contested (observed: `rota/roles/principal.py`, `land`).

## The count

| | night 85 | night 86 |
| --- | ---: | ---: |
| pages | 11 | 21 |
| showings | 13 | 21 |
| verbs | 9 present, 2 confirm | 17 present, 2 confirm, 2 clarify |
| kinds | 9 understand, 2 confirm | 14 understand, 3 touch, 2 confirm, 2 clarify |
| page tokens, total | 5658 | 7165 |
| page tokens, median | 293 | 178 |
| page tokens, largest | 3019 | 2993 |
| page tokens, smallest | 76 | 76 |
| rows approved | 52 | 139 |
| rows contested | 0 | 0 |
| tokens across showings | 11696 | 7165 |
| tokens of assumption and glossary pages | 5302 | 6184 |

Night 85 delivered 11696 tokens of page across its 13 showings, because it
showed the observed entries page three times. The assumption pages and the
glossary page take 94 per cent of night 85's distinct page tokens and 86 per
cent of night 86's. The two features the principal asked for take the rest.

One page carries most of the volume of each night. Night 85's m27 is 3019 of
5658 tokens, which is 53 per cent. Night 86's m30 is 2993 of 7165 tokens, which
is 42 per cent. Every other page of both nights is 76 to 431 tokens.

## Every page

The kind names the branch of `render_page` that built the page. "understand" is
"Here is what I understand you want, on one page." "touch" is "Before I build
this, here is what I expect to touch." "confirm" is "Did I hear you right?"
"clarify" is "I need one thing from you before I can continue."

| page | verb | kind | lines | tokens | shown | dup lines | rows from a cut seat | rows ruled |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| n85 m2 | present | understand | 4 | 199 | 1 |  |  | 4 |
| n85 m6 | present | understand | 8 | 431 | 1 | 1 | 2 | 7 |
| n85 m9 | present | understand | 7 | 293 | 1 |  | 5 | 7 |
| n85 m12 | present | understand | 7 | 326 | 1 |  | 2 | 7 |
| n85 m15 | present | understand | 7 | 246 | 1 |  | 2 | 7 |
| n85 m18 | present | understand | 7 | 340 | 1 |  |  | 7 |
| n85 m21 | present | understand | 7 | 384 | 1 |  | 3 | 7 |
| n85 m24 | present | understand | 4 | 263 | 1 |  |  | 4 |
| n85 m27 | present | understand | 77 | 3019 | 3 | 9 |  | 0 |
| n85 m30 | confirm | confirm | 1 | 81 | 1 |  |  | 1 |
| n85 m39 | confirm | confirm | 1 | 76 | 1 |  |  | 1 |
| n86 m2 | present | understand | 4 | 199 | 1 |  |  | 4 |
| n86 m6 | present | understand | 7 | 422 | 1 |  | 1 | 7 |
| n86 m9 | present | understand | 9 | 290 | 1 | 2 | 4 | 7 |
| n86 m12 | present | understand | 8 | 381 | 1 | 1 | 1 | 7 |
| n86 m15 | present | understand | 7 | 256 | 1 |  | 2 | 7 |
| n86 m18 | present | understand | 7 | 398 | 1 |  | 2 | 7 |
| n86 m21 | present | understand | 7 | 403 | 1 |  | 1 | 7 |
| n86 m24 | present | understand | 7 | 424 | 1 |  |  | 7 |
| n86 m27 | present | understand | 1 | 78 | 1 |  |  | 1 |
| n86 m30 | present | understand | 75 | 2993 | 1 | 8 |  | 67 |
| n86 m35 | confirm | confirm | 1 | 81 | 1 |  |  | 1 |
| n86 m44 | present | understand | 2 | 140 | 1 |  |  | 2 |
| n86 m49 | clarify | clarify | 0 | 99 | 1 |  |  | 1 |
| n86 m52 | present | touch | 2 | 134 | 1 |  |  | 2 |
| n86 m54 | present | touch | 1 | 107 | 1 |  |  | 1 |
| n86 m72 | clarify | clarify | 0 | 178 | 1 |  |  | 1 |
| n86 m75 | present | understand | 4 | 189 | 1 |  |  | 4 |
| n86 m78 | confirm | confirm | 1 | 76 | 1 |  |  | 1 |
| n86 m87 | present | understand | 2 | 125 | 1 |  |  | 2 |
| n86 m91 | present | understand | 1 | 85 | 1 |  |  | 1 |
| n86 m94 | present | touch | 2 | 107 | 1 |  |  | 2 |

The last three columns are the faults the rows carry. "dup lines" counts
numbered lines that repeat a line already on the same page. "rows from a cut
seat" counts the `ledger` rows on the page that a seat wrote in a session whose
prompt did not fit its window. "rows ruled" counts the refs the landed ruling
names.

## What the page asks for

Seventeen of the 32 pages carry one section and nothing else: "Where you did
not say, I assumed:" (observed: the rendered pages). Those pages show no "You
asked:" section and no "It would:" section. The principal reads a list of
assumptions and approves the list.

The assumption lines are `ledger` rows written by the Vision Keeper on
`tick:reconcile` (observed: `ledger.author` and the `receipts` rows, 43 of 46
shown rows on night 85 and 42 of 57 on night 86). Each line compares the README
with the code. Each line reads as an observation, not as an assumption the
principal must rule on.

The same subject comes back on page after page. The `ledger` holds 48 rows over
34 subjects on night 85, and 57 rows over 42 subjects on night 86 (observed:
the table grouped by `about_ref`). The subject `how_it_works` carries five rows
on both nights, and `defines_commands_and_options` carries four. So the
onboarding pages of a night ask about the same few subjects, in new words each
time. Night 85 shows eight such pages before the observed entries page. Night
86 shows nine.

## The replies, and whether they were reasonable

The judgement ran in two passes. Twelve agents judged the pages first, one
agent per group. Twelve adversaries then refuted the judgements, one per the
same group. The adversary's default was that the approval was reasonable.

The first pass called 3 of 32 replies reasonable, 15 partly reasonable and 14
not reasonable. That rate is what a judge produces when it is asked to find
faults. The second pass overturned 23 of the 32 judgements. It left 22
reasonable, 5 partly and 5 not.

The second pass is the one to trust (reasoned: it checked each of the first
pass's claims against the page text and found many of them false). One example:
the first pass said page m18 of night 85 repeats line 4 at line 6. The two
lines start with different words and carry different sentences. The first pass
also counted repetition, a heading that misnames its own section, and a missing
citation as reasons to withhold approval. Those are page faults. They do not
make a reply unreasonable.

The adversary held a fault material only if one of these holds:

1. The page states something false about the repository, and the approval puts
   a false fact into the record.
2. The page asks the person to approve a change to their own code that a
   careful person would not want as written.
3. The page hides a decision the person must make, so the approval decides it
   silently.
4. The page is too large or too repetitive to read before answering, so the
   approval is not an informed one.

Ten pages failed that test. The reply was not fully reasonable on these:

| page | verdict | why |
| --- | --- | --- |
| n85 m9 | partly | Line 2 claims the code does not show what the README describes. It names no feature and no file. |
| n85 m15 | no | Line 2 reaches the page as an unrendered template: "the README is stale; the code shows `<Y>`". Line 3 states `windows_expand_args` backwards. |
| n85 m21 | partly | Line 1 says Click leaves Unicode to the standard library. Click does that work in `_winconsole.py`. Line 4 names an `add_ctx_arg` decorator that Click does not have. |
| n85 m24 | partly | Line 4 reads "given up after the attempt bound: -\|tick:constraint_zero\|". The ruling approved it. |
| n85 m27 | no | See the resolution below. |
| n86 m9 | partly | Lines 3 and 6 carry the template with the payload dropped: "the README names a thing the account never mentions". |
| n86 m15 | no | The same `<Y>` template line as night 85's m15. |
| n86 m24 | no | Seven stability constraints on public names are retired at once. Three carry evidence that stops in mid-word. Four carry no evidence at all. |
| n86 m27 | no | The whole page is one line: "The claim about constraints:float is falsified and requires a ruling on its validity and scope." It names no claim, no file and no scope. |
| n86 m75 | no | Line 4 asks the principal to approve a false statement about the tooling. See fact 6. |

**The resolution of one inconsistency** (reasoned: the assistant, because two
adversaries split on the same page). Night 85's m27 and night 86's m30 are the
same page, at 3019 and 2993 tokens. One adversary called the reply to m27
unreasonable under tests 3 and 4. The other called the reply to m30 reasonable
and dismissed the same bulk. A reply to one page cannot be reasonable on one
night and unreasonable on the next. The page is readable at 3000 tokens. It is
not checkable: it asks "Name a line to correct only that line" over 65 lines
that repeat one sentence template, eight of which appear twice under two
numbers, and one of which names the file `src/click.term,py`, which does not
exist. So the verdict for both nights is that the approval is not an informed
one, and the reason is the per-line check the page asks for and defeats.

## Eleven facts the next frames need

1. **A fifth to a third of the rows the principal approved were written by a
   seat that had lost its brief.** Night 85 showed 46 `ledger` rows and 14 of
   them come from a Vision Keeper session whose prompt was cut, which is 30 per
   cent. Night 86 showed 57 rows and 9 come from a cut session, which is 16 per
   cent (observed: `turns.completion` holding "prompt did not fit", joined to
   `receipts` and `ledger`). Five pages of night 85 and six of night 86 carry
   such a row. Page m9 of night 85 carries five of its seven from cut sessions.
   The seat that writes what the principal approves is the seat the overflow
   hits hardest.

2. **Nothing was ever contested.** The rulings of both nights hold 191 approve
   verdicts and no contest and no revise (observed: `rulings.per_item`). No
   page ever reached the contested loop. So the contest path, the amendment
   path and the revocation path are unwalked on both nights, and a night that
   passes proves nothing about them.

3. **One page of each night is the whole context problem.** The observed
   entries page is 3019 tokens on night 85 and 2993 on night 86, against 76 to
   431 for every other page. On night 85 it was shown three times and never
   landed a ruling, because the three Liaison sessions that read the reply had
   prompts of about 17200 tokens against a 12288 window and made zero tool
   calls (observed: s110, s112 and s120, and `turns` measured at 17195 tokens
   for s110). On night 86 the near-identical page landed one ruling of 67
   approvals from one sentence, because its Liaison session prompt was 5248
   tokens and fit (observed: s121). The page size did not change between the
   nights. The prompt around it did.

4. **A page can number the same row twice.** The 32 pages carry 21 duplicate
   numbered lines. The cause is repeated ref ids inside one message's
   `body_refs`, not duplicate rows (observed: night 85's m27 holds 79 refs and
   71 distinct, and night 86's m30 holds 77 and 69). The renderer numbers each
   ref, so the person is asked to rule twice on one row under two numbers. The
   ruling then carries one entry for it. Night 86's m30 numbers 75 lines and
   its ruling names 67 refs.

5. **An answer that does not answer still lands a ruling.** The Developer asked
   where the tests for the new flag belong, because the criteria named tests
   that the loaded file does not hold. The Liaison relayed the question to the
   principal as m72. The scripted principal replied with sentence two's one
   prepared answer, "the flag defaults to False so nothing changes for existing
   callers". That sentence answers a different question. The walk holds one
   answer per sentence, so every clarify of a sentence gets the same words. The Liaison recorded a ruling from it and approved statement s1
   (observed: `rulings` rows `r_m73` and `r_745dfccf5b`). Two seats also
   answered the Developer with refs, so the off-topic reply was one of three
   answers (observed: m67 from the Vision Keeper and m71 from the Architect).

6. **A page reported a wall to the principal in words that hide it.** Line 4 of
   night 86's page m75 reads: "Unable to modify `src/click/termui.py` due to
   partial write restrictions; the existing implementation may already satisfy
   the requirement implicitly or requires a full file rewrite which is outside
   current scope." The Developer wrote that row itself (observed: `ledger` row
   `l_d002235b32`, author developer, session s172). The Developer made 21
   `code.write` calls against that file across seven sessions, and the guard
   refused them in two ways (observed: the `ERROR code.write` lines in `turns`,
   three distinct texts):

   - "this rewrite of `src/click/termui.py` drops clear, echo_via_pager, edit,
     get_pager_file, getchar, hidden_prompt_func, launch, pause, progressbar,
     prompt, secho, style, unstyle, and the batch's tests, its criteria or
     other files use them. Either write the whole file with every existing
     definition kept and your change added, or write only the new definitions
     with start=998, end=998".
   - "src/click/termui.py is not valid Python (expected 'except' or 'finally'
     block, line 301) ... Your text itself does not parse ... Send only the
     lines you add, whole statements".

   So a restriction does exist, and the guard named two ways past it. The
   Developer took neither, and the page then told the principal the file cannot
   be modified and the code may already do the work. A person who reads that
   line learns nothing about the real wall. Frame 38 owns the category ruling,
   and this instance is evidence for it, because the model context named the
   fault and the fix in plain words.

7. **The page said "falsified" where the Critic gave up.** Night 86's pages m24
   and m27 carry five lines of the form "The claim about `constraints:X` is
   falsified and requires a ruling on its validity and scope", for
   format_filename, paramtype, intrange, floatrange and float. The Critic
   falsified none of them. The `challenges` table holds seven rows, three
   falsified and four standing, and no row for any of the five (observed: the
   table). `tick_attempts` holds exactly those five Critic challenge ticks,
   each quarantined at three attempts (observed: the table). One Liaison
   session, s103, woken on `tick:blindspot`, wrote all five ledger rows
   (observed: the `receipts` rows). The scripted principal approved all five.
   So the record now says the principal retired five stability constraints on
   public names of click, on the strength of a verdict that does not exist. An
   abandoned tick reached the page as a finding. This is the worst fault of
   either night, and it is a defect of the write path, not of the model.

8. **No page ever reports an outcome.** The four page kinds are understand,
   touch, confirm and clarify. Every one asks for a ruling before work. None
   reports what the work did (observed: the verbs and kinds of all 32 pages).
   Night 86 cut a batch, committed at `da5e7e8`, ran 37 test runs and left
   three failing at attempt 10. The principal was shown none of it.

9. **The two nights are one run repeated, at the page level.** Both ran at
   project commit `2c8cd3ac` with the same profile, models and pins (observed:
   the `config` rows). Three page texts are byte-identical across the nights:
   m2, and both confirms. 114 of night 86's 134 distinct numbered lines, which
   is 85 per cent, were already shown on night 85. By characters the share is
   84 per cent. A reader must not count the two nights as two samples of the
   page set.

10. **The record says the principal made 102 decisions.** Night 85 holds 45
    `decisions` rows with author `principal`, and night 86 holds 57. Every one
    reads "default taken at signoff: ..." (observed: the table). The person
    said one sentence per page. Nothing in the record separates a default the
    person read from one they did not.

11. **The mechanism for "the answer did not land" was never used.** No message
    of either night carries the status `unresolved`. Night 86 sets
    `unresolved_note` twice and leaves the status alone (observed: the
    `messages` table). The column exists for the case of fact 5, where an
    answer lands and does not help.

## What a person should never have been shown

Four items on these pages are not fit for a person, and every one was approved
(observed: the rendered pages):

- `the README is stale; the code shows <Y>`. An unrendered template reached the
  page on both nights, as line 2 of m15.
- `given up after the attempt bound: -|tick:constraint_zero|`. A machine string
  reached night 85's page m24 as line 4.
- Evidence that stops in mid-word. Night 85's m24 line 1 ends "Even if the
  source in `.utils` were renamed (e.g., to." Night 86's m24 carries three such
  lines.
- The write claim of fact 6.
- The five "is falsified and requires a ruling" lines of fact 7, which name a
  verdict that no seat reached.

## What this record does not answer

- Whether the Developer's ten failed attempts on night 86 trace to anything on
  these pages. That is frame 38.
- What the seat prompts cost around each page. Four sessions were measured, not
  all of them.
- How a person reads a 3000-token page. No person read these pages. The
  judgement is an agent's reading of what a careful person would do.
- Whether a principal that contests would get better pages. Nothing was ever
  contested on either night, so the contested loop is unmeasured. That is
  frames 41 and 42.

## What the next frames take from this

- **Frame 41**, the agent principal: the paths never walked are contest,
  revise, and any ruling on night 85's m27. An agent principal proves something
  new only if it contests at least once. The ten pages above are the material to
  contest, and five of them carry a fault a careful person would catch in
  seconds.
- **Frame 42**, the designed principal: four page kinds cover both nights, and
  the understand kind is 23 of the 32 pages. A designed principal needs an
  answer for each kind, plus a rule for the assumption list, which is 17 of the
  32 pages.
- **Frame 43**, the context caps: the observed entries page is the one page
  that grows with the repository, and it is 42 to 53 per cent of a night's page
  volume. The page alone is not the cap's customer. The seat prompt that
  carries the same rows is: 17195 tokens on night 85 against a 12288 window,
  and 5248 tokens on night 86 for the same page. So the cap belongs on the
  session's working set, not on the page.
- **A new frame, above all three**: fact 7. An abandoned tick reached the page
  as a finding, and the principal retired five constraints on the strength of
  it. One Liaison session wrote all five rows. A gate that refuses a page line
  naming a verdict the `challenges` table does not hold would have stopped
  every one. The fix is cheap and the fault is on the delivery path.

## What the sweep added

A thirteenth agent read the whole set and named what the record missed. Facts
7 to 11 come from that pass. Each was checked against the databases before it
was written here (observed: the queries of 2026-09-18).

The same pass corrected this record. An earlier draft of fact 6 said no write
restriction exists. The guard's own refusal text shows one does, and it names
two ways past it. The correction stands in fact 6.

One claim of the pass did not survive its check. It said neither night uses
`unresolved_note`. Night 86 sets the column twice. The status `unresolved` is
the part that was never used.
