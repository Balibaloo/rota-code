# Night 165, W-E: his first answer returns because of the Liaison's call

Read on Opus, 2026-10-25, read only, from `.rota/clickI_night16*.db` with
`?mode=ro`, `.rota/clickI_night165.principal.jsonl`, the `### 266.` block of
`plans/stack.md`, `plans/night164-we-read.md`, and a parser probe at HEAD
87b4f57f. No model ran.

## The verdict

W-E is two known parts, and no new mechanism. Part 1 is frame 266's written
hole: `_missing_close` finds the run-on string `"approve}` only when a later
double quote closes it. With single-quoted `words`, no double quote follows,
so the generic text fires, and that text names `text='''...'''`. Part 2 is a
right refusal that the seat repeats: the Liaison contests a line his words do
not name, by its own choice, and the door refuses it correctly. Frame 267's
two-session rule then returns his answer. Night 164's W-E read found the same
two parts (`plans/night164-we-read.md`, section 6). Night 165 is the second
night of the same wall.

## 1. The mechanism today

1. His page reply wakes the Liaison. `rota/core/runner.py:5097` calls
   `toolproto.extract_lenient` with `signatures=_param_sets(sb)`.
2. `extract`, `rota/llm/toolproto.py:1155`, finds no close of the argument
   list at line 1337. `_open_argument` (line 424) returns None, because the
   open string sits after a comma inside the dict. `_missing_close` (line
   467) returns None, because the string that opens at `"approve}` never
   meets a second `"`. The scan reaches the end of the text with the
   string open, and the function returns None at line 556.
3. The `else` branch, lines 1458 to 1464, sends the generic text: "a quote
   inside a quoted argument ended the string early ... put it between
   triple quotes, text='''...''', with the lines as they are, no escaping".
4. The schema is `rulings_rule(ctx, rulings: dict | None = None, words: str
   = "", ask: str = "")`, `rota/roles/api.py:11940`. No `text` argument
   exists. s317 obeyed the text: it put `words` between triple quotes from
   seq 4 and kept `12: "approve}`. The text sent it to the wrong value.
5. Probe: s316 seq 1 with the real signature gets the generic text. With
   `doesn't` and `command's` removed, it still gets the generic text. s226
   of night 151 gets the located text, because its words hold a later `"`.
6. The contest door is `_unnamed_contest`, `rota/roles/api.py:11688`,
   called from `_line_refusal` (line 11317) at line 11358, which
   `rulings_rule` calls at line 12330. The contest of line 7 (m36) and of
   line 9 (m174) is the Liaison's own choice. No default writes a contest.
   On m35, his words name lines 2 to 6, and line 7 restates his own rule.
   His second answer says "line 7 already says that". On m172, his second
   answer says the bare return "still has to give back False", which is
   the content of line 9, with no number. His third answer approves line
   9. The door read both right and named the step. s122 and s318 sent the
   same call three times and ended on "repeated its previous turn verbatim
   twice".
7. The return: `REPLY_SESSIONS = 2`, `rota/core/db.py:877`. The first miss
   keeps the reply open with the refusal in its note. The second miss, or
   any miss on a reply to a returned page, closes the reply (db.py 1335 to
   1349). `returned_line`, `rota/roles/principal.py:1648`, prints "Your
   last answer to this page did not reach the team" on top of the page.

Night 165's three resends: m36 (s121 parse then contest, s122 contest) gave
m37. m173 (s316 and s317, parse alone, generic text) gave m174. m174 (s318,
contest alone) gave m183, which landed as r_df7c82685f.

## 2. The origin

- The generic text naming `text=`: fb1bdbab, 2026-10-04, frame 122. That
  commit made the key branch name the key, and the generic branch kept
  `text='''...'''` (comment at toolproto.py 1435).
- `_missing_close`: 74251f79 and ce658cdb, 2026-10-16, frame 266 passes 1
  and 1b. Review 1, low 2, found the hole, and pass 1b wrote it as "a known
  hole", not built (stack, 266, status 19:17).
- The unnamed-contest door: 250f3806, 2026-10-14, frame 234.
- The return: 0582873a, 2026-10-16, frame 267.

Frame 266's ruled repair has landed for one shape alone. The refusal names
the open string when a later matching quote exists. The no-later-quote
shape is not built. Pass 4, s243's shape, sprint 12 row 8, has no built
status in the block. Frame 266 is open, and its last line is 2026-10-24.

## 3. The count, nights 160 to 165 (7 databases, 609 Liaison sessions)

| Night | Parse refusal on `rulings.rule` | Of those, reply got no ruling | Unnamed-contest refusal | Of those, no ruling |
|---|---|---|---|---|
| 160 | 0 | 0 | 2 | 0 |
| 161 | 2 | 1 | 5 | 1 |
| 162 | 1 | 1 | 4 | 2 |
| 163 | 3 | 2 | 1 | 0 |
| 164 | 3 | 3 | 2 | 2 |
| 164a | 0 | 0 | 0 | 0 |
| 165 | 4 | 3 | 3 | 3 |
| All | **13** | **10** | **17** | **8** |

- The 10 parse misses are 7 replies sent back to him. The 8 contest misses
  are 5 replies, and m36 and m192 count in both.
- By text: the generic text fired in 6 sessions, and 6 of 6 got no
  ruling. All 6 have `"approve}, words='` with no later `"`. The located
  text fired in 6 sessions, and 4 of 6 got no ruling. The key text fired
  once, s333, and s333 landed on its next call.
- 11 of the 13 have the same model shape: the last dict value loses its
  closing quote before `}`. s345 has another shape, and s333 has an
  apostrophe in single-quoted `words`.
- Contests on a line his words do not name: 17 sessions refused. In the 3
  cases read here (m36, m174, and night 164's m38), the door was right.

## 4. Frame 266 or a new frame

- The generic text on `"approve}` with single-quoted words: frame 266, its
  written hole. Not a second refusal text.
- The generic text names `text=` on a call with no `text`: the same
  branch, the same site, frame 266's heading "the refusal blames the
  words". Frame 266, in the same pass.
- The contest of an unnamed line and its verbatim repeat: no open frame.
  The door is right, so the door is not the fault. Frame 305 counted a
  repeated right refusal of a line-2 contest and closed on 2026-10-24.
  This is the same seat behaviour on a different door. A new frame,
  heading as in `plans/night164-we-read.md`, section 6, if the offer below
  is taken. Otherwise it is cause 5 residue.

## 5. The repair's shape

Red tests for both: s316 seq 1 on night 165 with the `rulings.rule`
signature, and s122 seq 1 on m36, the contest of line 7.

**Candidate A, the text.** Close frame 266's hole. When the scan ends with a
string still open, look back inside that string for the first `, name=`
whose name the function takes, and give the located text: the string
`"approve}` has no closing quote before `, words=`. Drop `text=` from the
generic branch and name no argument there. s316 then gets the located
text. The m35 contest is not touched, and stays a right refusal. Cost: 1
cycle. The measure argues against it as the whole repair: the located text
already fires, and 4 of 6 such sessions still got no ruling. s316 also has
a second break, `doesn't` inside single quotes, so a fixed quote costs one
more refusal and one more turn.

**Candidate B, the offer.** Each refusal carries the whole call to send. The
parser offers it when the run-on string's head is one closed-vocabulary
word before `}`, such as `"approve}`, and the call parses with the quote
added and `words` between triple quotes. The contest door offers the same
call with the unnamed lines set to approve, which is the step its text
already names. The seat copies one call, and does not compose one. s316
gets one call that lands, both breaks fixed. s122 gets `7: "approve"`.
Cost: 2 cycles, two sites.

**Favoured: B.** Both right texts in the count already fail on the repeat:
the located text misses 4 of 6, and the contest door misses 8 of 17. A
better text does not stop a seat that repeats at temperature zero. A
copyable call does, and it rules nothing new: approve is the step the door
already names, and the added quote changes no value. The offer is a
general form for any refusal with one right correction, not a fit to
`rulings.rule`. Keep A's change to the generic text inside B, because a
call that the offer cannot repair still needs a true text.

Usage: about 45k tokens on Opus, 27 tool calls, no model, no gate, no test.
