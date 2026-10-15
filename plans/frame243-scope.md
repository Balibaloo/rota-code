# Frame 243 scope read: the declined format enters the build at the Terminologist's respecify after a contest

Read-only, 2026-10-15 01:29. Rota workflow for every seat named below. Meta
workflow for the method, the price and the doubts.

Sources, each opened read-only (`file:...?mode=ro` on every database):

- `.rota/clickI_night148.db`: `sessions`, `turns`, `tool_calls`, `messages`,
  `rulings`, `decisions`, `criteria`, `ledger`, `verdicts`.
- `.rota/clickI_night147.db`: the same tables.
- `.rota/clickI_night145.db` and `.rota/clickI_night146.db`: `rulings.texts`
  and the respecify turns, for the door's count.
- `.rota/clickI_night148.principal.jsonl` and
  `.rota/clickI_night147.principal.jsonl`, by `night`.
- The tree `C:/Users/roman/rota_night148` at 92c4f126: `rota/roles/api.py`
  (`criteria_respecify` 5307-5481, `_named_tokens` 5068, `_QUOTED_SPAN` 5052,
  `rulings_rule` 8510-8795, `decisions_author` 9417-9546),
  `rota/roles/principal.py` (`last_ruling_on` 726),
  `tests/rota/test_criterion_contest.py`.
- `git show` and `git diff` in `D:/repos/_AI/sample_repos/clickI`. The bg_3
  worktree is gone, so the read used `batch/bg_3` and the main objects.
- `rota/LAWS.md`, `rota/DECISIONS.md`, `plans/composition.md`,
  `plans/archive/stack-2026-10-14.md` (frame 221),
  `plans/archive/stack-2026-10-15.md` (frame 219).
- Scripts in this session's scratchpad `f243/`: `dump.py` (every turn of a
  session to a file), `scan.py` (the door's count over nights 145 to 148).

## 0. The answer in brief

**The seam is the Terminologist's `criteria.respecify` on a relay that carries
the principal's contest** (seam 1). s188 respecified `ver_opt_show_py` after
m71 and kept `"{command} {python_version}"` from the text he contested. s190
built `0252730` from that text alone (observed: s190's prompt holds the
criterion, the ticket and the request, and no decision row). So the format
entered the build at 00:43:15, before the m81 page existed at 00:51:11
(observed: the commit date, the jsonl clock).

The other two seams did not put the format into the build:

- Seam 2, s189's `supersedes` on the principal's `d_565d2845d4`: no reader
  in `rota/core` or `rota/roles` reads `decisions.supersedes`. s190 never
  loaded a decision. The decision's text reached the m81 page and s203's
  answer, after the commit (observed: grep at 92c4f126, s190's turns).
- Seam 3, the m81 clarify verdict `approve`: it ran after the commit. It
  locked the format in, because no rule other than `approve` reached the
  Terminologist or the Tester. It is the second cause, and frame 234's
  residue (reasoned: the order of events).

Night 147 holds seam 1 twice and seam 3 three times (section 2). The door
below covers night 148's case. Night 147's seam 1 cases have other shapes
and need the brief line after an interview (section 4.3).

**The door**: on a contest relay, `criteria.respecify` refuses a rewrite that
keeps a double-quoted literal of the contested text when one sentence of the
principal's words carries a removal word and every placeholder word of that
literal. On nights 145 to 148 it fires 1 time in 60 contested respecifies:
s188, the true case (observed: `scan.py`, 2026-10-15).

**Price**: about 4 cycles and about 280k in agents before the night, then the
count on night 149 at 0 cycles (section 4.5).

**Prior ruling**: none in the records names `supersedes` on a principal's
decision. The composition answers it by effect: "The tool never rules for the
Principal." Law 1 makes the decision record a journal with one author per
entry. `challenge.md` says "no `supersedes`" since 81f27127, frame 221, 2026-10-14
(section 5).

## 1. The chain of night 148, turn by turn

Times from the principal's record and the commit (observed).

| When | Seat | What it did |
|---|---|---|
| s182 | Terminologist, `tick:criteria` | specified `ver_opt_show_py`: "If the show_python flag is enabled, the output format must be "{command} {python_version}" where python_version is obtained from sys.version." |
| m70, 00:41:37 | principal | "Line 2 is wrong because the Python version should come from sys.version_info as major.minor.micro, not from sys.version. It should also be added to the end of the normal version message, not replace that message with just the command name and the Python version." |
| s187 | Liaison, verdict | `r_4c8fd5d3ad`: `ver_opt_show_py: contest`, `texts` holds s182's text. Correct |
| s188 | Terminologist, relay m73 | respecify, version 4, kept the format, added his words. Then `msg.challenge_vision_keeper` |
| s189 | Vision Keeper, challenge m74 | `d_74_challenge_ver_opt_show_py` with `supersedes='d_565d2845d4'` |
| s190, 00:43:15 | Developer, `tick:batch_start` | committed `0252730`, `echo(f"{prog_name} {python_version}")` in place of the message |
| s191, s192 | Tester | `tst_ver_opt_show_py`: `assert expected_version in result.output` |
| s193 to s201 | Developer, Tester, Vision Keeper | the `package_name` red, three challenges, two `tick:unresolved` wakes |
| m81, 00:51:11 | Liaison s202's page, principal | "It should not expect only the command name and the Python version." |
| s204 | Liaison, answering | `r_3340e1e9d9`: all four rows `approve` |
| s203 | Developer, answer m80 | `code.commit` with nothing changed |
| s207 | Vision Keeper, relay m85 | `problem.set_approval` approved `d_f422882cbd` and `d_74_challenge_ver_opt_show_py` |

### 1.1 s188, the Terminologist's relay (the seam)

What it saw (observed: turn 1 `user`): `principal_verdict`
`{"ver_opt_show_py": "contest"}`, `principal_said` with m71's words whole, and
`resolved_refs` with s182's text. The brief, the relay mode (verbatim):

> For each criterion with contest or revise, rewrite it with
> `criteria.respecify` to say what the words say. Write the criterion in the
> principal's words. Do not send the sentence he contested. Keep the other
> words of the criterion.

What it sent, turn 1:

> `criteria.respecify(id='ver_opt_show_py', text="If the show_python flag is enabled, the output format must be \"{command} {python_version}\" where python_version is obtained from sys.version_info.major.minor.micro and appended to the end of the normal version message.", term_refs=['line'], surface_refs=['src/click/core.py::CommandCollection'])`

What came back: the surface door refused `CommandCollection`. Turn 2 named
`custom_version_option`, and frame 202's door refused it: "The item asks for
`version_option`, and this move drops `version_option` from the surface."
Turn 3 sent the same text with "on version_option" and the surface
`src/click/decorators.py::version_option`. It landed:
`OK criteria.respecify -> {"id": "ver_opt_show_py", "respecified": true}`.

No door read the text against his words. The frame 226 check in
`criteria_respecify` reads only names that the contested text held, the
current text dropped, and the rewrite puts back (`back`, 5419-5428). Here the
current text is the contested text, so that set is empty. The frame 227 check
reads only the same words sent back, and the surface had changed. And
`_named_tokens` reads backticked spans and identifiers, not a double-quoted
format (observed: the code at 92c4f126).

The seat kept the declined format because the brief told it to keep the other
words, and the format was one of them (reasoned: the turn 1 text is s182's
text with his two clauses spliced in, every old word kept). This is a
prediction until an interview runs (section 4.3).

### 1.2 s189, the Vision Keeper's challenge

What it saw: the challenge m74 with `asks` and `resolved_refs`, both s188's
text. It did not see m71's words: the challenge carries the criterion, not the
ruling (observed: turn 1 `user`). `decisions.search` returned the principal's
`d_565d2845d4`, "default taken at signoff: The version_option includes a
show_python flag that appends the running Python version to the message."

The challenge brief says, for a `decided` item: "Author a decision with
`decisions.author` that says which work the item asks for. Give the decision
an id of its own, with refs to the item and no `supersedes`."

What it sent, turn 1:

> `decisions.author("d_74_challenge_ver_opt_show_py", "The version_option's show_python flag must append the running Python version to the message in the format \"{command} {python_version}\" where python_version is derived from sys.version_info.major.minor.micro.", refs=["ver_opt_show_py", "tk_1_version_option_show_python"], supersedes="d_565d2845d4")`

It landed: `OK decisions.author -> {"id": "d_74_challenge_ver_opt_show_py", "resolves_ledger": null}`.
The supersede door refuses only an items row (9505-9528). `d_565d2845d4` is a
decision, so `_must_exist` passed. The seat then tried `problem.assert` twice,
was refused, and re-sent the decision until the repeat door ended it.

The text is s188's criterion with "appended to the end of the normal version
message" dropped. So the decision states only the declined half (observed).

### 1.3 s190, the Developer's batch start (where the build took the format)

What it saw (observed: turn 1 `user`): `batches.expect` with "the principal
said": "Give version_option a show_python flag that appends the running
Python version to the message."; `criteria.load` with s188's text;
`tickets.load`. No decision row, no ruling, no ledger in any of its ten turns
(observed: 0 matches of `d_74` or `d_565d` in its turns).

What it wrote, turn 4, a ledger row `l_649a10bb9e`, kind `default`:

> "When True, the format becomes "{command} {python_version}" replacing the
> default message entirely."

Turn 6 says: "The criteria specify that when `show_python` is enabled, the
output format must be `"{command} {python_version}"`. This replaces the
default message entirely." It then wrote the callback branch
`echo(f"{prog_name} {python_version}", color=ctx.color)` and committed
`0252730` (observed: the `code.write` call, `git show 0252730`).

The seat read the first clause of the criterion as the format and the second
as already met. Its own ledger row names the declined behaviour in words. No
page showed that row before the merge (observed: m81's page holds the
criterion and the test only).

### 1.4 The Liaison that ruled m81, s204

The question on m81 came from s202, which copied `d_74`'s text into the page:
"The version_option's show_python flag must append the running Python
version to the message in the format "{command} {python_version}"". So the
page put the declined format to the principal as a fact (observed: the m81
page in the jsonl).

s204 saw `principal_said` whole, the four rows, and `recent_chat` with m71's
words (observed: turn 1 `user`). The answering brief says: "`contest` where
the words reject it, `revise` where the words change it." It sent, turn 1:

> `rulings.rule(rulings={"d_f422882cbd": "approve", "d_74_challenge_ver_opt_show_py": "approve", "ver_opt_show_py": "approve", "tst_ver_opt_show_py": "approve"}, words="Yes. The test should expect the Python version at the end of the normal version message, ... It should not expect only the command name and the Python version. ... give the test a fixed version string ...")`

It landed. The words reject the format in `d_74`, the criterion and the test
comment, and change the test. Each of the three takes `revise` or `contest`
by the brief (reasoned). Frame 234's line reading runs only when
`not is_clarify` (8718), so no door read a clarify verdict against its words
(observed: the code).

### 1.5 s203, the Developer's answer m80

The answer m80 carried `d_f422882cbd` and `d_74_challenge_ver_opt_show_py`.
The answer brief says "it is authoritative: do not weigh its words against
your own reading." The seat read the source and sent `code.commit` with
nothing changed (observed). The code already did what `d_74` said.

### 1.6 What merged

`git diff 517e61d a83cc50`: `src/click/decorators.py` with the
`show_python` branch that prints `"{prog_name} {python_version}"` in place of
the message, and `tests/test_version_option_show_python_flag.py`, whose
`in` assert the declined output meets. The Critic s208 passed it on the line
`python_version = f"{sys.version_info.major}..."` (observed: `verdicts`).

## 2. The chain of night 147

Candidate E of `plans/night147-read.md` is bg_1, `echo_json`. The merged code
carries three things the principal declined (observed: `git diff 2c8cd3a
d0a6687 -- src/click/utils.py`):

1. `echo_json` wraps the json error: `raise TypeError(f"Object cannot be serialized: {e}")`.
   He said at m37 "let its usual error stand", at m40 "the standard json
   module's usual error should stand", and at m65 "line 7 should not expect a
   custom "Cannot serialize" message".
2. `echo()` gained `try`/`except` around `str(message)`. He said at m62 "so
   echo itself does not change".
3. `echo_json` writes to the stream itself and never calls `echo`. He said at
   m37 "write that string through the existing echo", at m50 "pass it to the
   existing echo", and at m62 "then calls the existing echo".

The test of 1, `assert "is not JSON serializable" in str(exc_info.value)`,
passes with the wrap, because the wrap keeps the json text after the colon.
That is night 148's `in` shape again (reasoned: the test body).

### 2.1 Seam 1 on night 147, twice

**s130, relay m44 after m40's contest of `cj_serializable`.** The contested
text: "The function must handle arbitrary Python objects by converting them to
a JSON-serializable form or raising an error if serialization fails." s130
sent: "The function must raise an error if serialization fails (no conversion
of arbitrary objects)." with the surface `src/click/utils.py::echo`. It landed.
The rewrite dropped his positive clause, "the standard json module's usual
error should stand", and moved the surface to `echo` (observed: the
`criteria.respecify` call). s132's first commit `b3803fb`, 15:40:37, two
minutes after m40, carries the wrap. `c839962` and `3faf783` add the `try` in
`echo()` (observed: `git log -S`). The read's section 8 names the move to
`echo` as frame 202's shape. So items 1 and 2 entered the build through s130's
respecify (reasoned: the criterion the Developer read said "raise an error"
and named `echo`).

**s173, relay m68 after m65's contest of `cj_compact` and `cj_serializable`.**
m65: "Line 2's check is wrong because it compares against the default spaced
output, so it should check that the whole output equals the compact string
with one newline at the end." The contested text: "The output must be compact
JSON (no indentation) followed by exactly one newline character." s173 sent:
"The output must equal the default spaced JSON string followed by exactly one
newline character." It landed, with `surface_changed` (observed). The
rewrite writes the form he named as wrong. It did not reach the code, because
the Tester wrote the compact assert from m50's words and no Developer commit
followed (observed: `test_echo_compact.py`, the bg_1 log ends at 16:14:39).

s173's `cj_serializable` rewrite was right: "without converting arbitrary
objects or emitting custom messages". No Developer woke on it after 16:20,
because the test was green with the wrap (reasoned: the log, the test body).

### 2.2 Seam 3 on night 147, three times

| Ask | His words | Ruled |
|---|---|---|
| m37 clarify | "let its usual error stand ... with no special conversion. Then write that string through the existing echo" | `cj_compact`, `cj_serializable`, `cj_stream`: all `approve`. `cj_serializable` then said "by converting them" |
| m50 clarify | "pass it to the existing echo ... Change the test to check that the whole output equals that same compact string" | `cj_compact`, `tst_compact_01`: both `approve` |
| m62 clarify | "then calls the existing echo, so echo itself does not change ... please drop it" (the pager file) | `bg_1`: `approve` |

(observed: `rulings` `r_2ae46e5ccb`, `r_c394942c03`, `r_a13de9034a`)

The relay brief says "An approved criterion needs nothing." So "through the
existing echo" never reached a criterion, and item 3 merged. m62's "drop it"
is a `contest` by the answering brief's own sentence (reasoned).

### 2.3 Seam 2 on night 147

None. s161's challenge decisions carry `supersedes=None` (observed:
`tool_calls`). The challenge brief's "no `supersedes`" line landed at
81f27127 before night 147.

## 3. The three seams

| Seam | Night 148 | Night 147 | What it admitted | What a door there refuses |
|---|---|---|---|---|
| 1. `criteria.respecify` on a contest relay | s188 kept the format | s130 dropped his clause, s173 wrote the form he faulted | a text that does not say what his words say | s188, by the kept quoted literal; s130 and s173 not, by any lexical rule measured here |
| 2. `decisions.author` with `supersedes` on a principal's decision | s189 | none | a seat's decision marked as replacing his | s189's call, by the target's author |
| 3. `rulings.rule` on a clarify reply | m81, four `approve` | m37, m50, m62, six `approve` that the words fault | an `approve` on a row the words reject or change | m81's three wrong rows, if a fault reading ran on a clarify |

**Seam 1 is the seam** (reasoned: three facts).

1. The build reads the criterion and nothing else at batch start (observed:
   s190 and s132's prompts). So a declined phrase enters the build only
   through the criterion's text, and only seam 1 writes that text after a
   decline.
2. Seam 1 ran before the commit on both nights. Seam 3 ran after the commit
   on night 148. Seam 2 has no reader.
3. A fix at seam 3 alone does not hold. A `revise` at m81 wakes the
   Terminologist with the same relay brief, and s188 shows what that brief
   produces from words that decline a format (reasoned).

Seam 3 is the larger count over two nights, 4 asks against 3 respecifies. It
loses words that never became a criterion: night 147's item 3 merged through
it alone. It is a frame of its own, not this door (section 5).

Seam 2 is a door of one line and no behaviour on the build. It belongs in
the same pass for the composition's sake, not for the count (reasoned).

## 4. The design

### 4.1 The door at seam 1

Site: `criteria_respecify` in `rota/roles/api.py`, beside the frame 226
`back` check, inside `if contested and cur:`, so it runs whether or not the
surface changed.

The rule:

1. Take each double-quoted span of `contested["text"]` that holds a space or
   a brace. A bare identifier is not a literal. Night 146 kept
   `` `version_option` ``, `` `show_python` `` and `` `echo_json` `` in
   backticks 10 times, all right (observed: `scan.py`).
2. Keep the spans that the new `text` also holds verbatim.
3. Drop a span that the principal's words quote verbatim.
4. Split the span's placeholders into words: `{command}` gives `command`,
   `{python_version}` gives `python` and `version`.
5. Refuse when one sentence of `contested["words"]` holds a removal word
   (`not`, `no`, `never`, `without`, `instead of`, `rather than`) and every
   placeholder word of the span.

Step 5 keeps a format the principal did not fault. m71's first sentence holds
"not", "python" and "version", and no "command", so the rule fires on the
second sentence alone (reasoned: the words). A contest that faults only
`sys.version` leaves the format standing, as the brief's "Keep the other
words" says.

The refusal, in STE:

> the principal contested this criterion, and the rewrite keeps
> "{command} {python_version}" from the text he contested. His words:
> '<words>'. His words reject that format. Write the format his words give,
> or leave the format out.

Count on the records: 60 contested respecifies with a ruling's `texts` on
nights 145 to 148. Steps 1 to 3 keep a non-identifier literal in 1, s188.
Step 5 holds for s188 (observed: `scan.py`, by the last respecify per
criterion and ruling, 2026-10-15). So the door fires 1 in 60, with 0 false
refusals on the records. It does not fire on s130 or s173.

### 4.2 The door at seam 2, in the same pass

Site: `decisions_author`, after the items branch (9529). When `supersedes`
names a `decisions` row whose `author` is `principal` and the caller is a
seat, refuse:

> `d_565d2845d4` is the principal's decision. A seat's decision does not
> replace his. Send the same call again without supersedes.

Offer the call with `_offer` and no `supersedes`, as the items branch does.

### 4.3 The interview before a brief line

s188 had m71's words in its prompt and kept the format. By the rule of
2026-10-02, a seat that does not act on a fact in front of it is interviewed
before a brief shape. The replay: `probes/frame37/interview_turn.py` on
night 148's s188, turn 1. The questions: which words of the criterion it
kept and why, what "Keep the other words of the criterion" told it, and what
sentence would have made it leave the format out. Repeat on night 147's
s173 turn 1, the "default spaced" case, so the brief line answers two
shapes and not one.

The brief line to test, if the interview names "Keep the other words":

> Keep only the words his reply does not fault. Leave out a format, a value
> or a name that his words reject.

The line goes into the relay mode of the Terminologist's brief in place of
the second "Keep the other words of the criterion." Its two copies sit in
the ruling paragraph and in the request paragraph (observed: s188's system
prompt). The cases the change makes stale re-record at the gate.

### 4.4 The tests, red first

File: `tests/rota/test_criterion_contest.py`, with its `_criterion`,
`_ruling` and `_respecify` helpers.

1. **Red at 92c4f126, s188's landed call.** Criterion `ver_opt_show_py` with
   s182's text. Ruling `r_4c8fd5d3ad`, `contest`, m71's words, `texts` with
   s182's text. Respecify with s188's turn 3 text and the surface
   `src/click/decorators.py::version_option`. Expect `ValueError` that holds
   `{command} {python_version}` and m71's words. At the parent it lands.
2. **Admitted, the format his words give.** The same ruling, and the text
   "If the show_python flag is enabled on `version_option`, the running
   Python version as major.minor.micro from sys.version_info is appended to
   the end of the normal version message." Expect `respecified`.
3. **Admitted, a format he did not fault.** A ruling whose words are m71's
   first sentence alone, and s188's text. Expect `respecified`, because no
   sentence holds `command`.
4. **Admitted, an identifier kept.** Night 146's s411 shape: a backticked
   `version_option` in both texts. Expect `respecified`.
5. **Red at 92c4f126, s189's call.** A `decisions` row `d_565d2845d4` by
   `principal`, and a Vision Keeper's `decisions.author` with
   `supersedes='d_565d2845d4'`. Expect the refusal. At the parent it lands.
6. **Admitted.** The same call with `supersedes` on a Vision Keeper's own
   decision.

### 4.5 The price

By the anchors in `plans/operating-facts.md` (reasoned): a door text is 2
cycles, an instrument fix 3, one cycle costs the holding session about 10k.

| Step | Cycles | Tokens in agents | Behaviour it buys |
|---|---|---|---|
| The interview of s188 and s173 | 1 | about 70k, frame 193's 66.7k | the brief line is chosen from the model's words, or dropped |
| The pass: 4.1, 4.2, the six tests, the brief line if the interview names it, the gate | 1 | about 120k cold, frame 24's 77k plus a re-record | s188's text and s189's supersede are refused on the records |
| The diff review on a worktree | 1 | about 70k, frame 30 | a reader that never saw the files checks the five steps and the refusal |
| The fix pass if the review finds one | 1 | about 25k resumed | |
| Night 149's count | 0 | the read's share | the ratio below |

About 4 cycles and about 285k in agents. The ends-when's ratio stands:
merges that carry what the principal declined, from 1 of 3 on nights 147 and
148 toward 0 of the next 3. The residue rule stands: a merge that still
carries a decline is read, and the frame closes when its cause is not seam 1.

## 5. What to doubt, and the prior rulings

### 5.1 What to doubt first

1. **The door covers 1 of 3 seam 1 cases over two nights.** s130 dropped a
   clause and s173 wrote a faulted phrase in his own prose. A lexical rule
   for those was measured and is noisy: a three-word match of a fault clause
   flags 15 of 60, most of them right rewrites (observed: `scan.py`). So
   night 149 can carry a decline through seam 1 with this door in place. The
   interview is the step that answers the other two.
2. **The cause of s188's keep is a prediction.** "Keep the other words" is
   the brief sentence most likely to be the cause. No interview ran.
3. **Seam 3 is a frame of its own.** 4 clarify verdicts over two nights
   approve what the words fault, and frame 234's line reading skips every
   clarify (`not is_clarify`, 8718). Night 147's item 3 merged through seam
   3 alone. A door there needs a fault reading of a clarify reply with no
   line numbers, which is frame 234's ground. Recommended: a candidate frame
   beside frame 234, priced after this frame's night.
4. **The test cannot see the decline.** Both nights' tests assert with `in`,
   and the declined output meets it. That is candidate F, beside frame 182.
   A door at seam 1 removes the cause and leaves the blind test.
5. **s189's prompt has no ruling.** The challenge m74 carries the criterion
   and not the principal's words. So s189 could only copy s188's text. The
   supersede door stops the mark and not the text, and `d_74`'s text still
   reaches m81's page. The text is right only when seam 1 is right.
6. **Step 5's word split is new.** A placeholder named `{prog}` against his
   "program name" does not match. The records hold one format literal, so
   the rule's reach is one case.

### 5.2 The prior rulings found

No record names `supersedes` on a principal's decision (observed: grep of
`rota/LAWS.md`, `rota/DECISIONS.md`, `plans/composition.md`,
`plans/archive/`, `plans/operating-facts.md` and the briefs). Three records
answer it by effect:

- `plans/composition.md`, Flows: "The tool never rules for the Principal. It
  never settles a conflict, closes an assumption, or treats silence as
  consent." And: "Only a ratified amendment to something approved revokes
  work downstream." A seat's decision that marks his as replaced is the tool
  ruling for him, so the door follows from the composition (reasoned).
- `rota/LAWS.md`, law 1: "Journals — the transcript, the decision record, the
  ledger — may have several writers but one author per entry, append-only".
  The decision record is a journal, and a supersede by another author edits
  the standing of his entry (reasoned).
- `rota/roles/prompts/vision_keeper/challenge.md:10`: "refs to the item and
  no `supersedes`", from 81f27127, frame 221, 2026-10-14. A brief line from a
  pass, not Roman's ruling. s189 broke it, and the door admitted it.

Frame 219's ends-when asked for "a decision write under an id that holds a
principal's decision is refused or lands as a new version with the old one
kept". It covers the same id and not a supersede. Frame 219 closed on that
line on 2026-10-15 (observed: `plans/archive/stack-2026-10-15.md`).

A prior door shape for seam 1 exists: frame 221's assert door on a `decided`
item, pass 1b and 1c, refuses a text that drops or negates a name of the old
text unless his words name it. It took 7 cycles against 4 and three reviews,
two of them on false refusals from the removal-word rule (observed:
`plans/archive/stack-2026-10-14.md`). That history is the reason the door
above is narrow and is the reason to price a fix pass.
