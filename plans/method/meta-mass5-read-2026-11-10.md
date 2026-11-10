# What the records do for the work: a blind read

Date: 2026-11-10. Read-only, one agent on Opus, about 150k. Meta workflow.
The read did not open `plans/meta-review-2026-11-10.md`, the meta map,
the other mass reads, `plans/f363-*.md`, or lines 17 to 75 of
`plans/stack.md`. Every count is (observed) unless a line carries
another mark. Scripts are in the session's scratchpad.

## Result

1. The records that change the next step are short, have one reader at
   one moment, and carry a verdict first. The review page is the clearest
   case. The holding session reads it within the hour, and its verdict
   decides the next pass (observed: frame 362, 01:55 to 02:08 on
   2026-11-03).
2. The records that do not change the next step are the fields of a
   frame block after the push. Tools and rules read them, but nobody
   rewrites them. They go stale, so the state print states a false world,
   and a taker reads the stack directly.
3. Of 474 read, review and design pages from 2026-10-10 to 2026-11-05,
   388 (82%) are cited by file name 0 times later than the day after they
   were written, 56 once, and 30 twice or more. Nearly all are cited once
   at write time, by the status line that announces them.
4. Of 10 fields that a tool or a rule reads, 5 are stale after 2 weeks,
   1 is true in part, 1 has no live reader, and 3 stay true. Of 11 fields
   that nothing reads, 3 are stale, 2 are written on under half of the
   closes, and 6 are idle. Of 8 facts with copies, 2 agree, 1 agrees but
   is stale, 1 agrees in part, and 4 disagree.
5. The state print did not make the take cheaper. From the `take` command
   to the first agent, the median cost was 59.7k before the print (n=37)
   and 55.7k after it (n=57).
6. What a session needs and no record holds: which frames are live and
   who holds them, the frame's current scope, and the answer to a
   question that a record holds under another key.

## 1. The inventory

The window is 2026-10-10 to 2026-11-09, about 4.3 weeks. Growth comes
from git (`--numstat`, the add dates and blob sizes at five dates).

| Kind | Files now | Bytes now | Added or grown in the window | Writer |
|---|---|---|---|---|
| `plans/stack.md` | 1 | 1,381,486 | 332 KB to 1,346 KB, about 236 KB a week. 2,737 commits touch it | every build session, by `rota.tools.status` (2,562 calls in 99 transcripts) and by hand |
| `plans/archive/` | 110 | 5.1 MB | 23 files. 106 frames closed in the window | the session that pops a frame |
| Review pages | 357 | 3.3 MB | 344 added, about 80 a week | reviewer agents |
| Read pages | 189 | 3.5 MB | 144 added, about 33 a week | Opus agents |
| Design pages | 54 | 1.3 MB | 11 added | Opus agents and Fable |
| Handover notes | 93 (61 new path, 32 old) | 349 KB (new path) | about 22 a week | the leaving session |
| Other `plans/` pages (passes, scopes, briefs) | 259 | 4.9 MB | 178 added | sessions and agents |
| `plans/operating-facts.md` | 1 | 150,608 | 124 KB to 151 KB, 44 commits | sessions |
| `plans/wall-guide.md` | 1 | 59,501 | created 2026-10-15, 5 commits | Fable, then frame 341 |
| `plans/method/reference.md` | 1 | 46,032 | created 2026-10-18, 14 commits | sessions on a ruling |
| `CLAUDE.md` | 1 | 15,991 | 27 KB down to 16 KB at the sweep of 2026-10-18 | sessions on a ruling |
| `plans/composition.md` | 1 | 6,782 | no change | Roman's ratification |
| `rota/COMPLETION.md` | 1 | 33,963 | 1.8 KB more | sessions on a ruling |
| Memory directory | 20 live, 30 archived | 245 KB | 30 moved to `archive/` on 2026-10-18 | sessions |

## 2. Read against written

Citations count the file name. A page cited only on its own day and the
next is "at write time". The base is the 474 pages older than 2026-11-06.

| Kind | Written per week | Evidence of reading |
|---|---|---|
| Stack | about 800 status lines | `state` print run 164 times. `sed -n` on the stack 578 times, `grep` 75 times. Rule C26 and CLAUDE.md: "nobody reads it whole" |
| Review pages | about 80 | 297 of 326 never cited later. Median 2 citations, the launch line and the verdict line. Read by the holder before the pick |
| Read pages | about 33 | 81 of 130 never cited later, 29 once, 20 twice or more. Night reads became 28 Sprint sections and placed 72 frames |
| Design pages | about 2.5 | 10 of 18 never cited later. `frame204-design.md` is cited 10 times later |
| Handover notes | about 22 | `state --from` run 42 times. It prints the Doubts section, which 50 of 92 notes carry. 164 window status lines cite a note |
| operating-facts | about 6 KB | 22 window status lines cite it: 11, 5, 1, 5 and 0 a week. 2 cite a line number |
| wall-guide | 0 after week 2 | 46 status lines cite it: 36, 10, 0, 0, 0 a week. 26 pages after 2026-10-24 cite it |
| reference.md | about 1 KB | 7 status lines. 29 file reads, and moment-sized `sed` reads in each sampled take |
| composition.md | 0 | 0 status lines. Read whole at each sampled take, about 5.5k characters |
| COMPLETION.md | small | 5 status lines, all after 2026-10-31. 5 of 8 frames pushed since then name a capability |
| amendments.md | 0 | 2 open proposals since 2026-10-18. No commit after that day |
| Memory | a few files | The index loads each session. 17 status lines name a memory file |

Tools that parse records, and the fields they read:

- `state.py`: the frame heading and its session ids, the `Site:` field
  and its workflow word, `Waits on:`, `Sprint:`, a rating, the last status
  line, `(assumed:` and `taken by timeout` for `--since`, the archive
  headings, the note's section "What I believe, and what to doubt".
  `reach_line` reads `Reach:`, but only tests call it.
- `status.py`: the frame number, the `Pointer:` line as the place to
  insert, the Site's workflow word.
- `handover.py`: the mailbox, the peers table and its `handed` column,
  the note path.
- `rulings.py`: the stack, the archive, the composition and the plans
  pages by headings and `Keys:`. 12 runs in 99 transcripts.

## 3. A field with a reader against one without

Three frames each, pushed at least 2 weeks ago where possible: 243
(2026-10-15), 306 (2026-10-21), 322 (2026-10-25), and 362 (2026-11-03)
for scope.

Fields with a reader:

| Field | Reader | Kept true? |
|---|---|---|
| Heading session ids | `state` "Held by" | No. 9 of 17 printed frames name a holder that is spent or silent for 2 weeks: 306, 315, 316, 322, 326, 327 by 66edc387 and 4cdad7e1 (both "spent"), 266 by 1cf2843b, 140 and 203 by eefbf293 |
| `Waits on:` | `state`, open decisions | No. 243 says "the scope read" and is parked. 306 says "the provenance read", which landed. 322 says "nothing" and was moved to the front on 2026-11-08. 29 of 32 frames parked by a status line do not say so here |
| `Sprint:` | `state`, rule C46 | No. On 58 of 136 frames. 31 name a numbered sprint below the current 35: 243 "sprint 6", 306 "sprint 15", 322 "sprint 21" |
| `Site:` | `state`, `status`, rule C41 | In part. On 70 of 136 frames, against "every frame". True for 243, 306 and 322. 362's Site names the survey, and its last 100 lines are dry runs 5 to 8 |
| `Pointer:` | `state` "Read the frame's Pointer", `status` | No. 362 says "the demand read ... when it lands", which landed 2026-11-03. 306 names only night 158's read, not its provenance or close read |
| `Reach:` | rule C76, `reach_line` | Idle. On 7 open frames and 17 archived. No production caller |
| `handed` and "holding" | `peers`, CLAUDE.md `holding` | No. 17 of 20 "holding" rows name an archived frame, for example 63, 37 and 81 |
| `(assumed:` | `state --since` | Yes as a mark. 45 window lines. `--since` ran 2 times |
| Note Doubts section | `state --from` | Yes. 50 of 92 notes. Read 42 times |
| Last status line | `state` | Yes, by construction |

Fields with no reader:

| Field | Kept true? |
|---|---|
| `Ends when:` (133 frames). Not in the state print | No for 362: the ends-when is the onboarding demand read, a design and a slice. The lines are dry runs 3 to 8 |
| Price in `Waits on:` (65 frames) | No. 362 "about 4 cycles before any build", then 241 status lines and no re-price |
| `Cycles: n of about m` (484 lines) | Not used. 5 of 24 parsable lines run over. The anchors in operating-facts date from frames 24 to 30. 3 cycle lines were added in the window |
| Closing actual beside the estimate (C42) | 42 of 106 closing lines |
| Register lines in the close (C69) | 1 of 106 closing lines |
| `Doubt:` in a status line | 7 lines. No reader |
| Agent cap "about Xk against Yk" | 245 of 305 run over. The fact "a cap written in a brief does not bind" is in operating-facts since 2026-09-23 |
| "Rota workflow." at a status line's end | 672 lines. `state` reads the word only from the Site |
| Sprint sections at the head | Stale. 84 KB. Step 1 names frame 353, archived 2026-10-31 |
| "## Stack" and "The batches" | Their own text says "superseded". 13 KB kept as history |
| `Reasoning:` field (73 frames) | Not checked over time |

## 4. Duplication and drift

| Fact | Copies | Today |
|---|---|---|
| The intent | `CLAUDE.md` section 1, `plans/method/intent.md` | Agree. One paragraph sits in another place |
| Heredoc strikes | MEMORY.md index, the memory file | Agree: 30, 2026-11-08 |
| The take cost "35k from a 3,700-line stack" | `design.md`, reference C26, `state.py` | Agree, and stale. The stack has 5,643 lines. A take costs about 56k |
| The status-time rule | reference C68 (15 strikes, archived memory), the live memory (6 strikes to 2026-10-28), `status.py` | In part. Two memory files hold one rule. The reference cites the archived one |
| "Waits on: Roman's order" | stack head "41" (2026-10-31), the frames | Disagree, and the debt is unpaid: 39 to 47 lines now |
| The order | stack head steps 1 and 2 (frame 353), frames 362 and 363 | Disagree. 353 is archived. 362 and 363 both say "this sprint, first" |
| The assumed mark | reference section 8 as a rule, `amendments.md` as an open proposal | Disagree on whether it is ruled |
| Who holds a frame | stack headings, the peers table | Disagree on 17 of 20 rows |

Rule C67 says "A frame is five lines". 35 open frames have more than 20
lines, and 16 have more than 50.

## 5. The stack itself

- 1,420 status lines, 69% of the bytes. Mean 671 characters, median 596,
  maximum 2,188. 27% of the October and November lines exceed 1,000.
- Frame 362: 241 status lines, 232 KB, 16.8% of the file, 14 peer names
  in 7 days. Its heading is onboarding. Its lines carry dry runs 3 to 8.
- 136 open frames. 105 have no status line after 2026-10-26. They hold
  45% of the bytes, 27% as status lines.
- Closed in fact: 7 frames whose last line says built at HEAD with only a
  residue, or the premise overruled (264, 280, 315, 316, 326, 327, 130).
  They hold 4.7% of the bytes. This is a lower bound by keyword.
- The Sprint sections hold 6.1%. The head and the superseded sections
  hold 1.5% more.
- By the rules a taker reads the state print and the Pointer. The print
  shows four lines for each held frame. It shows 17 of 136 frames. 110
  frames above "## Parked" have no holder and never print.
- In practice, five sampled takes after 2026-11-02 read about 75k
  characters of the stack by `sed` and `grep`, against 21k of the print,
  45k of reference.md and 65k of other pages.

## 6. What a session looked for and did not find

1. What each seat needs from onboarding (frame 362's heading, 2026-11-03).
2. Roman's words for the criteria clause of e8e1a207
   (`frame114-history-read.md`).
3. Whether a change outside the criteria goes to the Architect (the same).
4. Whether a Developer must ask the Vision Keeper first
   (`frame204-history-read.md`).
5. Whether a test may rely on a value it finds on the machine (frame 281).
6. A key score for the click dry runs (`dry3-key-score-2026-11-03.md`).
7. The text of seven edges of his earlier answers (frame 352).
8. The provenance of frame 193's rule "a page is about one request"
   (`f1-f15-f21-night172-read.md`).
9. A frame for the 15 unit reds, "which no frame holds" (Sprint 35).
10. A seat that holds the whole between runs (frame 363's heading). The
    dry run 8 read found 7 walls that match 8 frames pushed and never
    built.

The wider count: of 103 questions to Roman from 2026-10-01 to 2026-10-17,
the records held the answer for 19, and a read dissolved 6
(`frame287-questions.md`). No later count exists.

## 7. The composition's rules against the build's records

- One writer. Each frame has one holder at a time. The file has 3.5
  writers a day on average, and 9 at most. The peers table has one
  writer, the tool, and still drifts, because nothing writes it on a
  close.
- Conclusions cross, reasoning stays. 54% of open status lines name a
  page. But status lines carry findings lists, and the frame blocks grew
  past the five-line rule. The review page keeps the rule best.
- Nothing stops quietly. Not kept. 105 frames are silent for 2 weeks, 110
  never print, the two amendments wait unseen, and the 41 debt lines stay.
  The print says "Live things: 17 of 10", and nothing acts on it.
- The mark. 2,452 of 3,452 window status lines (71%) carry a mark. 2,208
  carry `(observed`, 172 `(reasoned`, 141 `(ruled`, 45 `(assumed`.

## 8. The opposite: a record that made later work better

The review page. 349 in the window. Each has one writer, one reader and
one moment, the pick. Its first line is the verdict, and each finding is
CONFIRMED or PLAUSIBLE with a fix line. Example: `f362-review-p1.md`
found that `grain_area` returns None for a new file. Pass 1c fixed it in
10 minutes, and the second look found one more high, fixed by pass 1d.
The night reads are the second case: 28 Sprint sections and 72 placed
frames come from them, 40 of them now closed. Both are records with a
fixed consumer and a key, and neither must stay true after its moment.
The frame block must stay true for weeks, and no step rewrites it.

## 9. What this read could not see

- Reads that leave no citation: a page read by `sed` in a transcript and
  never named. Only five takes were opened for this.
- Citations by phrase, such as "night 168's read", are not counted.
- Subagent transcripts. The take cost includes the standby's wake turn.
- Whether Roman reads any page. Untracked pages are dated 2026-11-09.
- "Closed in fact" needs judgement per frame. The count is a lower bound.
