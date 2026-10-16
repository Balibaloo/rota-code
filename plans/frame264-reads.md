# Frame 264, the two reads before a question goes to Roman

Rota workflow throughout, except where a line names the meta workflow.
Read-only. Written 2026-10-16 by an Opus agent from `f264/reads_brief.md`.
Scripts: `roman_words.py`, `count.py` and `count2.py` in `f264/` of session
cc1d654e's scratchpad.

## 0. The answer in brief

1. The records answer half of the question. A request page shows the account.
   DECISIONS.md rules on 2026-09-03 that "a statement gets the account first
   (`how_it_works`...)" (observed: `rota/DECISIONS.md` line 1355).
2. The records do not rule the words of the heading. "What we're building:"
   came from an assistant commit, 81cd0632, 2026-09-04. No Roman ruling names
   it (observed: `git log -S`, the transcripts).
3. The design meant the account of a statement to be the work itself, for a
   new program such as "tip calculator pls". On an onboarded repository such
   as Click, `how_it_works` is the project's observed account. The heading
   then says the wrong thing (reasoned: `plans/a1-seed-interview-at-intent.md`
   line 20 against the night 150 pages).
4. Read 2: 12 replies on 3 of 16 nights read the account rows as the
   description of the work. 6 of the 12 are on pages that show the account
   alone, with no request line. "Leave the rows off a request page" does not
   remove those 6. "A heading that says they are the project as observed"
   holds for all 12 (reasoned: section 2.3).
5. Two other fault kinds ride on the same rows and are not Roman's question:
   the description row cut mid-word (7 replies), and an observed row that
   carries the new work or his feedback (5 verified replies). Each is its own
   frame (reasoned: section 2.4).
6. The open question for Roman, rated medium, is in section 3.

## 1. Read 1, what the records say

### 1.1 LAWS.md and DECISIONS.md

`LAWS.md` and `DECISIONS.md` sit in `rota/`, not at the root.
`rota/LAWS.md` holds no line on the account (observed: grep "account",
2026-10-16).

`rota/DECISIONS.md`, "The seed interview runs at intent-time, and the signoff
page is its first moment", lines 1340 to 1362 (observed):

> Ruled 2026-09-03 ("lets do this now, this is a usability priority").
> ...
> Two things ruled. The interview runs at intent-time too: a statement gets
> the account first (`how_it_works`, the item orient already writes for a
> repository), and what the words left silent is logged where a desk had to
> assume it. And the page the principal signs carries those assumptions

`rota/DECISIONS.md`, "The scope role is Vision Keeper", line 258 (observed):

> identity, purpose, the non-goals, the rejection log, the account
> of what a program is *for*

`plans/a1-seed-interview-at-intent.md` line 20, the design of that ruling
(observed):

> **The account.** `how_it_works` is the first item Vision Keeper writes, for
> a repository (orient) and, since 2026-09-03, for a statement (deliver). It is
> the whole, put to the principal before anything is sliced.

Conclusion: the page shows the account first, by ruling (observed:
DECISIONS.md line 1355). For a statement the design treats the account as
"the whole", the thing to build (reasoned: the a1 design, line 20). No record
says what the page shows when `how_it_works` is the observed account of an
existing repository and the statement is a change to it (observed: no line in
DECISIONS.md, LAWS.md or the a1 design names that case).

### 1.2 plans/composition.md

Section "The parties", lines 40 to 43 (observed):

> **The project** is the codebase the work is about. The structure holds a
> model of its shape, terms, boundaries, and external commitments, as
> records observed from the code. The Principal holds the shape in their
> head. The structure holds it in rows.

Section "Records" (observed): "A record says whether it was observed from the
code or the world, reasoned by a seat, or decided by the Principal (ratified
2026-09-16)." Section "Flows" names no page section.

Conclusion: the composition separates the project, observed, from the
request, which the Principal holds. It does not rule a page heading
(reasoned: no Records or Flows line names the page).

### 1.3 git log -S on the page builder

`rota/roles/principal.py` lines 1486 to 1496 print the three headings today.

| Heading | Commit | Date | Message, verbatim |
|---|---|---|---|
| "What we're building:" | 81cd0632 | 2026-09-04 15:27 | "feat(seat): every ask reads as a message to a person, not a verb and a list of ids". Body: "the account before the behaviours, what it would and would not do, what was assumed where they didn't say, in that order". "The first three of the cheap presentation fixes (2026-09-04)." |
| "What we are building:" | d3d1e4b4 | 2026-09-08 20:09 | "fix(seat): the page and the input are one contract". The STE spelling only. |
| "It does today:" | b16f53a8 | 2026-09-12 16:10 | "fix(seat): observed behaviour under "It does today:"; the touch note carries no ids". Body: "The signoff page listed the account's observed behaviours under "It would:", the heading a plan gets, and the person read "calculate the tip" as new work; the heading follows provenance now." |
| "How it is described:" | 74c43005 | 2026-09-24 | "feat(rota): a description owes no ticket, and the keeper can say so" |

Conclusion: the account heading's words came from an assistant feat commit,
not from a ruling (observed: 81cd0632 cites "cheap presentation fixes" and no
ruling). b16f53a8 is a precedent of the same shape: a person read observed
rows as new work, and the fix moved the heading to follow provenance without
a ruling (observed: its message, 2026-09-12).

### 1.4 plans/archive and plans/operating-facts.md

`plans/operating-facts.md` line 355 (observed):

> The owner's page heads a seat-written description with "How it is
> described:", after "What we are building:" and before "It would:" (ruled:
> Roman, 2026-09-24 20:20, asked with two other wordings; frame 80's heading
> check).

`plans/frame190-design.md` line 70 maps `account`, "the item `how_it_works`",
to "What we are building:" (observed). The archive holds no ruling on the
account on a request page (observed: grep "What we are building", "account
row", "request page" over `plans/archive/`, 2026-10-16).

Conclusion: the ruling of 2026-09-24 20:20 rules the description heading and
the order. It names "What we are building:" as a fixed point. The question
then was the description heading, not the account heading (reasoned: the
line says "asked with two other wordings" of the description heading).

### 1.5 Roman's words in the build transcripts

The transcripts start 2026-09-16, so the rulings of 2026-09-03 and
2026-09-04 are not in them (observed: the oldest file's first timestamp,
2026-09-16T01:45). 626 typed user messages stream from 111 files. None of
Roman's typed messages names the account, "What we are building", "describes
Click" or a request page's account rows (observed: `roman_words.py`,
2026-10-16). The answer of 2026-09-24 20:20 is not in a typed message, and a
grep of `AskUserQuestion` results for "describ" found no hit (observed:
2026-10-16).

## 2. Read 2, whether the recommended answer holds

### 2.1 The six replies of night 150

All six are in phase `sentence 3`, the show_python request (observed:
`.rota/clickI_night150.principal.jsonl`, `"night": "150"`).

| Ask | Page holds | Account line faulted | Other lines faulted | Cost, dollars |
|---|---|---|---|---|
| m354 | the request, account, description, 2 observed rows, 4 assumed | line 3, "describes Click in general and should instead say what we build" | lines 4 and 8 cut mid-word; 7 to 10 repeat 3 to 6 | 0.158 |
| m376 | the account and 1 observed row, no request line | line 1, "should describe what we are building" | none | 0.154 |
| m393 | the account alone | line 1, "still describes Click in general" | none | 0.148 |
| m398 | the request, account, 1 observed row | line 4, "still describes Click in general" | line 5, an observed row that carries the new flag: "Click doesn't have this flag today" | 0.152 |
| m408 | the account and 1 observed row, no request line | line 1, "still describes Click in general" | line 2, the observed row with the flag | 0.149 |
| m416 | the request, account, description, 2 observed rows, 3 assumed | line 6, "still describes Click in general" | line 8, the observed row with the flag; line 7 cut mid-word | 0.154 |

The six cost 0.915 dollars of principal calls, two `CYCLE` lines, and two keys
quarantined at 3 attempts (observed: the log; the quarantine from
`plans/night150-read.md` section 10).

Each page shows the heading "What we are building:" and closes "'ok' approves
all of this and starts building". On m376, m393 and m408 the account is the
only row he can approve. He reads the heading and the closing line together
as a plan (reasoned: his words repeat the heading, "should describe what we
are building").

### 2.2 The nights before, 133 to 149

Scope: every principal call in a `sentence` phase whose page holds an
account, description or observed row, nights 133 to 150, one record per
night and ask. 101 such pages, 44 of them on night 150 (observed:
`count2.py`, 2026-10-16). The script classes each reply by the line numbers
it names and by its words. A hand read then checked every hit.

| Fault kind | Replies | Asks | Cost, dollars |
|---|---|---|---|
| A. The account row read as the work: "describes Click in general", "only describes what Click is" | 9 | 133 m185, m212, m225; the six of night 150 | 1.29 |
| B. The description row read as the work: "should describe how confirm acts", "should describe the new show_python flag" | 3 | 142 m220, m234, m315 | 0.42 |
| C. The description row cut mid-word | 7 | 133 m59, 135 m148, 139 m49, 140 m86, 143 m104, 150 m354, m416 | 0.95 |
| D. An observed row carries the new work or his pasted feedback | 5 verified | 142 m128, m211; 150 m398, m408, m416 | 0.76 |

A and B together: 12 replies on 3 of 16 nights with such pages, 1.71 dollars
of principal calls. 133 m185, m212 and m225 show the account alone in
sentence 2 (observed: the pages). Replies overlap between kinds, so the
costs do not add.

Hits removed by the hand read: 136 m73, 141 m32 and 150 m294 fault a request
line, "the wrong change", not the account. 142 m31 and 147 m86 name the
account line as "right". 142 m211 faults the account row as "the wrong
change" because the row held the other request's words, so it counts under
D, not A. 142 m159 and m191 name a line the regex placed under "It does
today:", and the hand read did not confirm it, so D leaves them out
(observed: the pages, 2026-10-16).

### 2.3 Whether the recommended answer holds

The recommended answer has two forms.

1. **Off the request page, and the state page carries them.** This form does
   not hold alone. 6 of the 9 A replies are on pages with no request line:
   133 m185, m212, m225 and 150 m376, m393, m408. Those pages put the account
   to him during a request, from a contested or signoff wake. Moving the rows
   off the request page does not change those pages (reasoned: the six pages
   hold only account and observed rows). This form also reverses the ruling
   of 2026-09-03 that a statement gets the account first (observed:
   DECISIONS.md line 1355).
2. **A heading that says the rows are the project as observed, not the
   request.** This form holds for all 12 A and B replies. Each reply echoes
   the heading's word, "building" or "described", as what the line should
   say (observed: the words in 2.1 and 2.2). It keeps the 2026-09-03 ruling.
   It follows the b16f53a8 precedent: the heading follows provenance.

The narrower answer that holds: keep the account on the page, and change the
account heading and the description heading on an onboarded project. The new
words say that the rows are the project today and not the request. Also, a
page that holds only the account and observed rows does not close with "'ok'
... starts building" (reasoned: m376, m393, m408 and 133 m185 to m225 read
the closing line as a plan).

The heading change does not fix C or D. A reply that also faults a cut or
polluted row still contests the page (reasoned: m354, m398, m408 and m416
each name C or D beside A). The ends-when "from 6 toward 0 of the next 3"
needs C and D fixed too, or a ratio that counts A and B only.

### 2.4 The two kinds that are not the question

- **C, the description row cut mid-word.** The row ends at "comma", at about
  120 characters, on nights 133 to 150 (observed: m354 line 4, m416 line 7,
  133 m59). The cut is in the row or the render, not in a ruling. A cheap
  fix, its own frame (reasoned: the wall guide, cheap).
- **D, an observed row carries the new work.** On night 150 the observed row
  `parses_and_executes_inputs` reads "..., including the new version flag
  which is off by default ..." on m398, m408 and m416. The Vision Keeper's
  rewrite of that row was refused (observed: the pages;
  `plans/night150-read.md` section 10). On night 142, m128 and m211 show his
  feedback pasted into observed rows. Some write path changes the text of an
  observed row. This read did not find that write. It is its own frame, a
  read of the write first (reasoned: an observed row holds the code's words).

## 3. The question for Roman

**[med]** The rating is medium. An edit depends on which way it goes, and
the answer sets what the principal sees, which is a composition line. No GPU
hour depends on it.

The story. You onboard Click. Then you ask for one change: a show_python flag
on the version option. The page you get lists your request. Under it, a
heading says "What we are building:", and the line under the heading is the
team's summary of Click as a whole. You reply: "Line 3 describes Click in
general and should instead say what we build." The team cannot change that
line, because it is the summary of the code as it is today. The page comes
back five more times with the same line. Three times the page holds that
summary and nothing of your request, and it ends "'ok' approves all of this
and starts building".

Today, the summary of an existing project sits under "What we are building".
Those words were written for a brand-new program, where the summary is the
plan.

The options:

1. **Change the heading on an existing project (recommended).** The summary
   stays on the page. The heading says "The project today, not your
   request:" or similar words. A page that holds only that summary asks "Is
   this still how the project works?" and does not say "starts building".
   Next: you read the line as background and leave it alone. One edit in the
   page builder. The same as the label "Current address" above a form where
   you write your new address.
2. **Write a new summary for each request.** The team writes a second summary
   that describes the change, and that line sits under "What we are
   building". Next: the line says what you expect. This needs a new record, a
   new write for the Vision Keeper, and a design frame.
3. **Take the summary off a request page.** The summary shows only on the
   page about the project as a whole. This leaves 6 of the 12 contested
   replies in place, because those pages hold the summary alone. It also
   reverses the ruling of 2026-09-03 that a request gets the summary first.

Recommended: option 1, with the words of the heading his choice. The
evidence: 12 replies on 3 nights, each against the heading's word, and the
2026-09-12 precedent that moved observed rows under "It does today:" for the
same reading.
