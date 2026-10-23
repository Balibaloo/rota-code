# Frame 305, the provenance: the line reader places 'drop' on the line a sentence repeats, and the re-present after a refused ruling names line 1

Provenance read on Opus, 2026-10-23, by the ruling of 2026-10-18 12:02.
HEAD 631dcb25, `rota/foundation`. Sources: `rota/roles/api.py`,
`rota/roles/principal.py` 1417 to 1439, `git log -S`, the commits 39e2fba7,
f0b2924c, 0582873a and c888968b, `plans/frame267-scope.md`,
`plans/frame250-review-1.md`, the stack and its archive, `plans/night158-read.md`,
`.rota/night158.log`, and the databases of nights 140 to 158 opened
`?mode=ro`. The count script is `f305_count.py` in the holding session's
scratchpad. Meta workflow. No file but this one is changed.

## The provenance in one paragraph

Both texts are build-session designs, and no ruling of Roman's chose either
text (observed: sections 1 and 2). The line reader came from frame 234 on
2026-10-14, and the reader binds a fault cue to the nearest line reference
before the cue (observed: 39e2fba7, `_line_cues`). Frame 250 made that
reading a refusal of an approve on 2026-10-16, and its review found this
exact misfire on night 147's "Line 7 just repeats line 2 ... drop it"
(observed: `plans/frame250-review-1.md`, finding 2). The session judged it a
low and parked it on night 150's count, and nobody came back to it
(observed: `plans/stack.md` line 1222). The re-present line came from frame
267 on 2026-10-16, and it takes the first "line N" of the door's refusal
text, which is the seat's line and not the principal's (observed:
`returned_line`, `plans/frame267-scope.md` 5.2). A fix of both texts narrows
two build designs and serves law 6 and the ruling of 2026-10-08 (reasoned:
section 6).

## 1. The line reader of `rulings.rule`

**The reader is frame 234's pass 1, commit 39e2fba7, 2026-10-14 11:29, rota
workflow, built by an implementer on Opus for session 58da19ca** (observed:
`git log -S "def _line_reading"`, `plans/archive/stack-2026-10-15.md` lines
5 to 17). The frame's "Ends when" says: "a verdict's contest lands on a
line only when the principal's words name that line or quote it" (observed:
the same file, line 7). The commit says: "The door reads the words for line
references with a direction, faulted or matched" (observed: `git show
39e2fba7`). No ruling of Roman's names the reader. The rulings above it are
law 6, "nothing is ruled on the principal's behalf", and DECISIONS of
2026-10-08, "the principal's words always land on a row" (observed: the
docstrings, `rota/DECISIONS.md` line 1446).

**The reader binds a verb to the reference before it.** `_line_cues` splits
the words into sentences, then gives each reference the clause up to the
next reference (observed: `api.py` 9379 to 9420):

```
end = refs[i + 1].start() if i + 1 < len(refs) else len(sentence)
window = sentence[ref.end():end]
fault, match = _LINE_FAULT.search(window), _LINE_MATCH.search(window)
```

On m105, "Line 7 just repeats line 3 and isn't really an assumption, so
drop it", the window of line 7 is " just repeats ". The window holds no cue
of `_LINE_FAULT`. The window of line 3 is the rest of the sentence, and
"drop" is in `_LINE_FAULT` (observed: `api.py` 9318 to 9320). So the reader
gives `{2: 'wrong', 3: 'drop'}` and faults no line 7 (observed: a probe of
`_line_cues` at HEAD). The design has no notion of a subject and an object
of a verb. A sentence that names two lines gives every later cue to the
second line (reasoned: the code above).

**The refusal is frame 250's door, commit f0b2924c, 2026-10-16 00:49**
(observed: `git log -S "def _faulted_approve"`). `_faulted_approve` refuses
an approve of any line in `cues` (observed: `api.py` 9697 to 9745). The
docstring records the misfire as known: "One was right: night 147's m86,
where 'Line 7 just repeats line 2' reads as a fault of line 2" (observed:
`api.py`, the docstring of `_faulted_approve`). Review 1 named it finding 2,
low, CONFIRMED: "the right map cannot land with the reply whole", with a fix
(observed: `plans/frame250-review-1.md` line 20). The judge wrote "the other
lows wait on night 150's count of each refused seat's next call" (observed:
`plans/stack.md` line 1222). No later status line takes the finding up
(observed: `grep m86` over `plans/stack.md` and the archive).

## 2. The re-present text after a refused ruling

**The text is frame 267's, commit 0582873a, 2026-10-16 19:48, rota
workflow, designed by the scope read of 17:47 and judged by session rota-e7**
(observed: `git log -S "def returned_line"`,
`plans/archive/stack-2026-10-17.md` lines 110 to 127). The scope proposed
the words "with the line number taken from the refusal's `line N` when it
has one" (observed: `plans/frame267-scope.md` lines 218 to 224). The
judge accepted "one plain line, 'the team' and not 'the lead'" (observed:
the stack, frame 267, status of 17:49). No ruling of Roman's names the
text. The scope's one constraint was "No identifier, no tool name, no
refusal text", because the principal has no name for the mechanism
(observed: the scope, line 222).

**The number comes from the first `line N` of the door's refusal, read by a
regular expression** (observed: `principal.py` 1417 to 1439):

```
line = re.search(r"\bline (\d+)\b", row["unresolved_note"])
about = f" about line {line.group(1)}" if line else ""
```

The note is the first barren session's last refusal, prefixed with the
reply id (observed: `db.py` near 1000, m122's note). The refusal speaks to
the seat. Its first `line N` is often the line the seat ruled wrong, or the
line the door assigns. On m122 the note reads "m123: rulings.rule: The
words name no line and agree with the page, so their instruction is about
the request, line 1" (observed: `messages`). The words named no line, and
the door's own inference became "your words about line 1" (reasoned: the
two quotes). The pattern also skips the plural "lines 2", so on "The words
name lines 2 to 4 and do not name line 5" it takes line 5, the line his
words did not name (observed: night 156's m104 note, section 5).

## 3. What `_offer` does with an offered call

**`_offer` records the call and returns the sentence unchanged. It checks
nothing, and it records only under pytest** (observed: `api.py` 278 to 295,
"if not RECORD: return said"). The build decision is c888968b, 2026-10-05,
frame 144, after frame 135's law that "a refusal names only a call the
doors admit" (observed: `git show c888968b`). The commit says
"`sandbox.dry_run` sends an offered call through the real doors", and "No
door calls the dry run" (observed: the same). So in a night the offer is
text only. In the suite, the conftest hook dry-runs the offered call, and a
refusal of it fails the test (observed: `tests/rota/conftest.py` lines 215
to 238).

**Neither night-158 refusal calls `_offer` today.** "the words do not fault
the code of {item}. Approve {key}." is a bare `ValueError` (observed:
`api.py` 10218). `_agreed_contest` returns a bare string (observed: `api.py`
9881 to 9884). A call with line 2 approved and another line carrying the
words would pass the doors in a dry run only if the rest of the call passes
the same words check. The read found that true for cycle 3 and false for
cycle 2, where the seat's contest of line 4 goes against m91's "Keep lines
4 and 5 as the rules" (observed: `plans/night158-read.md` section 2).

## 4. The record of night 158

**m104 to m106.** The page m104 numbered eight lines: 1 the request, 2 the
guess, 3 `how_it_works`, 4 to 6 the account rows, 7 `l_e7c6ed5501` and 8
`l_b093572e02` (observed: s225 turn 1, `landing.lines`). Line 7's text is
line 3's text word for word (observed: the page in s225 turn 1). The reply
m105 says: "Line 7 just repeats line 3 and isn't really an assumption, so
drop it" (observed: `messages`).

**s225's turns** (observed: `turns` and `tool_calls` of s225):

1. Turns 1 to 4 met the team-note door on line 8 and the every-line door.
   Turn 4 sent 1, 3 to 6 approve and 2, 7, 8 contest, the right map.
2. Turn 5 met: 'The words fault line 3, "drop". An approve keeps the line
   as it is, and his words reach nobody. Rule line 3 contest or revise, as
   the words say, and pass the words. It takes no approve.'
3. Turn 5 then contested line 3. The ruling r_026d75b56b landed with
   `how_it_works: contest` (observed: `rulings`).

A probe at HEAD gives the same result. The right map, contest 2 and 7 and
approve the rest, is refused with that text, and s225's map passes
(observed: `_line_refusal` on m105's words, 2026-10-23).

**s240 and m122.** The contest of `how_it_works` quarantined after 3
attempts, and s240 woke on `tick:quarantined` and presented `how_it_works`
as m122 (observed: `sessions` s240, `tool_calls` s240).

**m122's page and cycle 3.** The seats s241 and s243 saw three lines: 1 the
request, 2 the guess, 3 `how_it_works`. The guess row is absent from
`line_rows` (observed: s241 and s243 turn 1). s241 sent `{1: approve, 2:
contest, 3: contest}` against m123, "Ok, I approve this page. Please
remember that the flag is off by default ...", and met the `_agreed_contest`
text. s243 sent `{1: approve, 2: contest, 3: approve}` against m124, and met
"The words name line 1 and do not name line 2" (observed: `turns`).

**The three re-presents** (observed: `.rota/night158.log` lines 87, 94,
117, 125 and 160):

1. m89, walk 2, after m90. The note is "the words do not fault the code of
   confirm_default_on_eof. Approve 2." It holds no "line N", so the line
   reads "could not turn your words into a ruling". He answered m91.
2. m89, walk 3, the same note and text. He answered m98, which landed as
   r_ce163d8060.
3. m122, after m123. The line reads "could not turn your words about line 1
   into a ruling". He answered m124: "every line on it stays as written,
   including line 1". The walk ended on m122 with the same line on top.

The end page in the log numbers the description as line 1 and the request
as line 2, with no guess line (observed: log lines 161 to 165). So at the
end, "line 1" names the description row on the page he reads (reasoned:
the log against m122's note).

## 5. The counts over nights 140 to 158

All 19 databases exist and were read (observed: the script's first line).

**Sentences that name two line numbers with one verb: 12. Of these, 4 relate
the two lines and put the verb after both, and the reader took the second
line each time** (observed: `f305_count.py`):

- night 140 m56, "Line 4 repeats line 2, so please remove it": took 2.
- night 142 m7, "Line 41 repeats line 37 word for word, so please drop
  it": took 37.
- night 147 m87, the review's m86: took 2.
- night 158 m105: took 3.

How I judged: a sentence of a principal message with exactly two single-line
references, every `_LINE_FAULT` cue after the second reference, and a
relating verb between them (repeats, duplicates, same as, overlaps,
contradicts, covers). In all 4, the drop falls on the repeating line, the
subject, by plain English (reasoned: "it" follows "repeats"). The other 8
sentences have no relating verb, and I did not judge them.

**Re-presents that name a line his words did not: 5 of 14** (observed: the
same script):

- night 154 m130: line 4, his words named 1, 2 and 5.
- night 155 the shift page: line 2, his words named line 1.
- night 156 m104: line 5, his words named 2 to 4.
- night 157 m22: line 1, his words named no line.
- night 158 m122: line 1, his words named no line.

How I judged: an ask to the principal whose note starts with a reply id is
a re-present. I took the first `\bline (\d+)\b` as `returned_line` does, and
read the reply's own references with `_LINE_REF`. Of the other 9, 4 name a
line he did name, and 5 name no line. In 2 of the 5 wrong ones the pattern
skipped the plural "lines" and took the door's "do not name line N"
(reasoned: the note texts).

## 6. The design's own condition, and the repair

**The build did not meet its own condition on this shape.** Frame 234's
condition is that a contest lands only on a line his words name and fault.
Frame 250's door forces a contest of the repeated line, which his words do
not fault, and refuses the right map (observed: section 4's probe). That
is a ruling on his behalf, against law 6 (reasoned). The build knew the case
on 2026-10-16 and parked it (observed: section 1). Frame 267's scope said
the line names "the line number that the refusal named". The code meets
that, but the refusal names the seat's line, so the condition was the wrong
proxy for "the line his words were about" (reasoned: section 2).

**A fix narrows both designs and reverses no ruling.** It narrows frame
250's door on a two-reference sentence, and it narrows frame 267's source of
the number. It extends law 6 and the ruling of 2026-10-08 to the two cases
(reasoned: no ruling of Roman's names either text, sections 1 and 2).

**The repair I would brief, in two sentences.** In `_line_cues`, a fault
cue that follows two references joined by a relating verb binds to the
first reference, the subject, and never to the object. `returned_line`
takes the number from the reply's own `_LINE_REF` references when they name
exactly one line, and names no line otherwise.

**What I doubt.**

- The sample is 4 sentences of one shape. "Drop line 3, because it
  repeats line 7" inverts under a subject rule, so a test holds both orders.
- Review 1's fix, skip a line that is not the first reference of its
  sentence, is simpler but drops real faults such as "Line 2 is fine but
  line 3 is wrong" (reasoned: that sentence's window).
- The re-present may matter less than the end page's own numbering. The
  end page puts the description on line 1, so any line number there can
  mislead (observed: section 4).

**What the interview of s209 turn 1 must settle.** s209 woke with the head
"Its last refusal or error: ... the words do not fault the code of
confirm_default_on_eof. Approve 2.", and sent the same call as s208,
contest 2, 4 and 5 (observed: s209 turn 1). The interview must settle
whether the seat reads "Approve 2" as line 2 or as a key, and which words of
m90 it took as a fault of line 2. It must also settle whether the missing
guess row in `line_rows` made line 2 look like a test line. The answers
place the line-2 contests as cause 4 or 5 (reasoned: W4).
