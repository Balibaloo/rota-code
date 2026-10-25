# Night 166, cycle 1: a converse answer that names the asked line as "that line"

Read 2026-10-25 18:40, from `.rota/clickI.db` opened read-only, sessions
s107 to s111, messages m24 to m28, and `.rota/night166.log` line 32. Walk
1, the `get_app_dir` item, cold at 741d2d06.

## The result

**The Liaison could not land his answer m27, the walk resent the page to
him, and his third answer m28 landed.** The cycle line
`liaison|message|converse` at 18:35 is s108 to s110. The door is the
naming door of `rulings.rule`, `_unnamed_contest` at
`rota/roles/api.py:11792`, built by frame 234's pass 2 as 250f3806 on
2026-10-14 (observed: `git show 250f3806`). The door was right on the
three cases night 165's W-E read opened (observed:
`plans/night165-we-read.md`, section 3). Here the door is wrong: the line
his words name is named through the Liaison's own question, and the door
reads his words alone (reasoned: the chain below). Cause 2 of the wall
guide, the door lacks a fact the prompt holds, in `earlier_exchange`.
No open frame holds it. The cost: two Liaison sessions with no ruling,
one resend to him, and one more answer of his, the scarcest budget.

## The chain

1. m24, the page: line 1 the request, line 2 the files, line 3 a ledger
   row, "The behaviour described in s1 is correctly captured by the new
   item and aligns with the ratified statement" (observed: s107's prompt,
   `line_rows`).
2. m25, his first answer: "Line 2 is wrong: get_app_dir is in
   src/click/utils.py ... Line 3 is unclear to me, so please say plainly
   what it assumes." s107 called `rulings.rule` five times: `{2: contest,
   3: ask}` refused, "'ask' is a question back, and a question is its own
   call ... with no rulings"; `{2: contest}` refused, "lines 1, 3 have no
   ruling"; `{1: approve, 2: contest, 3: ask}` refused as the first. s107
   ended with no call. s108 dropped the contest and asked m26 (observed:
   `tool_calls`, s107 and s108). The contest of line 2 then waited.
3. m26, the Liaison's question, repeats the ledger row's own words and
   asks "Is this correct?".
4. m27, his second answer: "I can't tell what 's1' or 'the ratified
   statement' mean, so I can't confirm that line as it's written. If it
   just means the plan matches my first request, then yes, that's
   correct ... Please also fix line 2". s109 and s110 called `{1: approve,
   2: contest, 3: contest}` three times each, refused each time: "The
   words name line 2 and do not name line 3. A contest rests on the
   principal's words." s110 tried `3: ask` once, refused as its own call
   (observed: `turns`, s109 and s110). Neither landed a ruling (observed:
   `receipts`, none for s107 to s110).
5. The walk resent the page: "Your last answer to this page did not reach
   the team" (observed: `night166.log` line 33). m28, his third answer,
   names line 2 and line 3 by number, and s111 landed r_09c72a141b.

## Why the door is wrong here

`_unnamed_contest` takes `read = faulted | matched`, the lines his fault
cues name, and the lines `_LINE_REF` finds in his sentences. `_BACK_REF`
spares a pronoun sentence only after a numbered sentence of his own.
"That line" in m27 answers m26, which asked about line 3 by number, and
m26 is in the prompt as `earlier_exchange` with `asked: true`. The door
never sees it (observed: the caller at `api.py:11462`, its arguments).

## The repair, for the night read's order

In the converse mode, the lines the Liaison's own ask names, found by
`_LINE_REF` on the `earlier_exchange` ask text, enter `read` before
`_unnamed_contest`. One predicate argument and one caller, about 1 cycle
on Opus and a review. The red test: s109 seq 1 of night 166, m27 against
m26, lands `{1: approve, 2: contest, 3: contest}`. The second shape,
a contest and a question in one answer that needs two calls, is the
design of the ask door at `api.py:10715` and is not this wall.
