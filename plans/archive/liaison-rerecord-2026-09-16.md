# The Liaison brief re-record, 2026-09-16

Two cycles of the loop for frame 18. Cycle 1 applied fourteen rewrites (commit 51af9f1) and re-recorded 34 cases: one fell. Cycle 2 changed two paragraphs of base.md (the next commit) and re-recorded 28: all hold. Both agent reports follow verbatim.

---

# Cycle 1

# Liaison brief rewrite: apply and re-record (2026-09-16)

Status: DONE. Nothing is committed. The six prompt files are modified in the
working tree of D:\repos\rota. `tests/rota/walks.jsonl` was already modified
before this task and is not mine.

## Summary

- The fourteen changes (B1 to B5, C1, C2, L1, L2, R1 to R3, V1, V2, S1) are
  applied to `rota/roles/prompts/liaison/`. V1 is applied as written: the
  door check says YES.
- Prompt tests without a model: 48 passed. No literal word restored.
- Re-record on the Titan, qwen3:8b: 32 of 34 cases hold their baseline.
  One case went down: `L1-LI-no-report-no-question` 5/5 -> 0/5. The model
  now sends `msg.clarify_principal` on "make the dashboard better, you know
  what I mean" instead of segment + confirm. That is the brief change (B1,
  B3, B4 in base.md). Not fixed. Reported in (c).
- One case is red before and after: `L1-LI-a-question-then-a-statement-at-the-confirm-is-the-question`
  0/5 -> 0/5, identical model output. Pre-existing. Not the brief change.
- T1: I3 and I4 pass. I1 and I6 fail, and a control run under the HEAD
  brief on the same model load fails both the same way. Neither is the
  brief change. I6 is a stale test: it counts `verb == "brief"`, the
  verdict tools write `deliver`. Details in the T1 section.
- Wall clock of the re-record: 21 min 37 s (03:35:08 to 03:56:45).

Recording profile: `ROTA_MODEL=qwen3:8b`, no `ROTA_PROFILE` (think pin
None, the key every earlier qwen3:8b recording carries), recorder on the
Titan at `OLLAMA_HOST=http://127.0.0.1:11435`, `ROTA_L1=1`,
`ROTA_REFRESH=1`. `L3-ratified-statement-becomes-a-term` is pinned to
`qwen3.5:9b` by its case file (`tests/rota/cases/l3_handoffs.yaml:50`) and
recorded on that model.

Harness notes:

- `tests/rota/test_l1.py` selects `l*.yaml` cases without `first:`. `-k`
  on case ids works: the ids are the parametrize ids.
- `tests/rota/test_gauntlet.py` selects `g*.yaml` (the four G1 cases).
- `tests/rota/test_l3.py` selects `l*.yaml` cases with `first:` (the three
  L3 chains). The whole chain records, both legs.
- `tests/rota/test_t1_liaison.py` needs `ROTA_T1=1`. It records `case_runs`
  rows `I1`, `I3`, `I6`, `I4` with `num_ctx=8192`, an empty `prompt_hash`
  and no transcript. No prior row existed for these ids. No prior qwen3:8b
  cassette existed for them either (the only earlier T1 cassettes are
  llama3.1:8b, 556 rows).
- `case_runs.seq` is one per row (one per run_no). A recording is the rows
  with the latest `prompt_hash` for the case and model. The pass count is
  `passed` summed over the latest row per `run_no`.

## (a) Baseline table

Latest recording per case before any change. Source: `tests/rota/cassettes.db`
read-only, table `case_runs`. All baseline rows have seq <= 146399.

| Case id | Mode | model | prompt_hash | latest seq | passed/runs |
|---|---|---|---|---|---|
| G1-scope-sounding-words-are-not-scope-yet | converse + awaiting_confirm | qwen3:8b | 5b28e1008f5d997a | 130365 | 5/5 |
| G1-an-owners-answer-reaches-the-seat | answer | qwen3:8b | 7187d2594fa73f90 | 130375 | 5/5 |
| G1-what-the-brief-already-holds-is-answered-from-it | converse | qwen3:8b | 1a887a8c8bc60f83 | 130395 | 5/5 |
| G1-a-reply-that-answers-something-else-ratifies-nothing | converse | qwen3:8b | 1a887a8c8bc60f83 | 130385 | 5/5 |
| L1-LI-a-reply-reaches-the-desk-that-asked | answering | qwen3:8b | fe49f8ff84ae541b | 145884 | 5/5 |
| L1-LI-put-the-open-assumptions-to-a-present-principal | agenda | qwen3:8b | f8fa794ceb05bb00 | 145909 | 5/5 |
| L1-LI-relay-an-answer-without-improving-it | answer | qwen3:8b | 7187d2594fa73f90 | 145914 | 5/5 |
| L2-LI-carry-the-block-to-the-principal | report | qwen3:8b | 2c69cb95ff43348e | 145999 | 5/5 |
| L1-LI-plain-agreement-approves-every-line | landing | qwen3:8b | 6aa04884a88285b3 | 146109 | 5/5 |
| L1-LI-a-named-line-is-contested-and-the-rest-approved | landing | qwen3:8b | 6aa04884a88285b3 | 146114 | 5/5 |
| L1-LI-a-correction-in-a-sentence-contests-the-line-it-is-about | landing | qwen3:8b | 6aa04884a88285b3 | 146119 | 5/5 |
| L1-LI-a-question-about-the-page-is-answered-not-ruled | landing | qwen3:8b | 6aa04884a88285b3 | 146124 | 5/5 |
| L1-LI-a-question-then-a-statement-at-the-confirm-is-the-question | landing | qwen3:8b | 6aa04884a88285b3 | 146129 | 0/5 |
| L1-LI-approve-one-line-only-approves-that-line-alone | landing | qwen3:8b | 6aa04884a88285b3 | 146134 | 5/5 |
| L1-LI-chat-is-not-work | converse | qwen3:8b | 1a887a8c8bc60f83 | 146139 | 5/5 |
| L1-LI-segment | converse | qwen3:8b | 1a887a8c8bc60f83 | 146144 | 5/5 |
| L1-LI-ratify | verdict | qwen3:8b | 4de78f0f63100940 | 146149 | 5/5 |
| L1-LI-present-for-signoff | submit | qwen3:8b | c4e04818ffb736ec | 146154 | 5/5 |
| L1-LI-present-carries-the-uncovered-statement | submit | qwen3:8b | c4e04818ffb736ec | 146159 | 5/5 |
| L1-LI-no-report-no-question | converse | qwen3:8b | 1a887a8c8bc60f83 | 146164 | 5/5 |
| L1-LI-put-a-contradiction-back-unresolved | contradiction | qwen3:8b | f27c155ec2cbcf30 | 146169 | 5/5 |
| L1-LI-ask-for-the-confirmation-nobody-asked-for | awaiting_confirm | qwen3:8b | 338f6c2574fd0c63 | 146174 | 5/5 |
| L1-LI-relay-a-ruling-without-interpreting-it | verdict_signoff | qwen3:8b | 30ae2ac21242b2a3 | 146179 | 5/5 |
| L1-LI-two-questions-at-most-from-three-reports | round_close | qwen3:8b | 538c107f014d0f8c | 146184 | 5/5 |
| L1-LI-surface-a-quarantined-message | quarantined | qwen3:8b | c2d99a90ccd70c0a | 146189 | 5/5 |
| L1-LI-present-what-onboarding-only-observed | observed_entries | qwen3:8b | e3736e12506f469d | 146194 | 5/5 |
| L1-LI-a-question-about-the-program-goes-to-its-owners | converse | qwen3:8b | 1a887a8c8bc60f83 | 146199 | 5/5 |
| L1-LI-a-ruling-splits-by-owner | verdict_signoff | qwen3:8b | 30ae2ac21242b2a3 | 146204 | 5/5 |
| L1-LI-present-the-touch | touch_note | qwen3:8b | b65364c412170f58 | 146209 | 5/5 |
| L1-LI-say-what-the-run-could-not-see | blindspot | qwen3:8b | 90e8ad19e7ea3e9a | 146274 | 5/5 |
| L1-LI-a-question-the-roles-could-not-answer | unresolved | qwen3:8b | 455024f9e6b2bea0 | 146399 | 5/5 |
| L3-ratified-statement-becomes-scope | verdict (first leg) | qwen3:8b | 222e7bf04ace898e | 137018 | 5/5 |
| L3-ratified-statement-becomes-a-term | verdict (first leg) | qwen3.5:9b | d102c6e9e4d20696 | 137008 | 5/5 |
| L3-a-maintainers-question-reaches-the-owner | converse (first leg) | qwen3:8b | 46bd6a797470c30a | 136993 | 5/5 |

## (b) After table

Latest recording per case after the change. Every row's `prompt_hash` equals
the sha256 prefix of the instructions composed from the new files (checked
by `scratchpad/after_table.py`), and every row has seq >= 146464, so every
row is from this re-record.

| Case id | Mode | model | prompt_hash | after | before | changed |
|---|---|---|---|---|---|---|
| G1-scope-sounding-words-are-not-scope-yet | converse + awaiting_confirm | qwen3:8b | a8149b646d8e0b50 | 5/5 | 5/5 | same |
| G1-an-owners-answer-reaches-the-seat | answer | qwen3:8b | 569283f2414c17aa | 5/5 | 5/5 | same |
| G1-what-the-brief-already-holds-is-answered-from-it | converse | qwen3:8b | 357b6836a1aab5eb | 5/5 | 5/5 | same |
| G1-a-reply-that-answers-something-else-ratifies-nothing | converse | qwen3:8b | 357b6836a1aab5eb | 5/5 | 5/5 | same |
| L1-LI-a-reply-reaches-the-desk-that-asked | answering | qwen3:8b | 28c333f9520a7ac0 | 5/5 | 5/5 | same |
| L1-LI-put-the-open-assumptions-to-a-present-principal | agenda | qwen3:8b | 27e97025709059b0 | 5/5 | 5/5 | same |
| L1-LI-relay-an-answer-without-improving-it | answer | qwen3:8b | 569283f2414c17aa | 5/5 | 5/5 | same |
| L2-LI-carry-the-block-to-the-principal | report | qwen3:8b | d700d540d255124e | 5/5 | 5/5 | same |
| L1-LI-plain-agreement-approves-every-line | landing | qwen3:8b | 6b5cbeabd094816d | 5/5 | 5/5 | same |
| L1-LI-a-named-line-is-contested-and-the-rest-approved | landing | qwen3:8b | 6b5cbeabd094816d | 5/5 | 5/5 | same |
| L1-LI-a-correction-in-a-sentence-contests-the-line-it-is-about | landing | qwen3:8b | 6b5cbeabd094816d | 5/5 | 5/5 | same |
| L1-LI-a-question-about-the-page-is-answered-not-ruled | landing | qwen3:8b | 6b5cbeabd094816d | 5/5 | 5/5 | same |
| L1-LI-a-question-then-a-statement-at-the-confirm-is-the-question | landing | qwen3:8b | 6b5cbeabd094816d | 0/5 | 0/5 | same (red before and after) |
| L1-LI-approve-one-line-only-approves-that-line-alone | landing | qwen3:8b | 6b5cbeabd094816d | 5/5 | 5/5 | same |
| L1-LI-chat-is-not-work | converse | qwen3:8b | 357b6836a1aab5eb | 5/5 | 5/5 | same |
| L1-LI-segment | converse | qwen3:8b | 357b6836a1aab5eb | 5/5 | 5/5 | same |
| L1-LI-ratify | verdict | qwen3:8b | a78749ccc197e180 | 5/5 | 5/5 | same |
| L1-LI-present-for-signoff | submit | qwen3:8b | 9dd0e021a95086ed | 5/5 | 5/5 | same |
| L1-LI-present-carries-the-uncovered-statement | submit | qwen3:8b | 9dd0e021a95086ed | 5/5 | 5/5 | same |
| L1-LI-no-report-no-question | converse | qwen3:8b | 357b6836a1aab5eb | 0/5 | 5/5 | DOWN |
| L1-LI-put-a-contradiction-back-unresolved | contradiction | qwen3:8b | e886758d9bfe7836 | 5/5 | 5/5 | same |
| L1-LI-ask-for-the-confirmation-nobody-asked-for | awaiting_confirm | qwen3:8b | cd38510fc6c410bc | 5/5 | 5/5 | same |
| L1-LI-relay-a-ruling-without-interpreting-it | verdict_signoff | qwen3:8b | 5df50dacd25c2b53 | 5/5 | 5/5 | same |
| L1-LI-two-questions-at-most-from-three-reports | round_close | qwen3:8b | 6a8181c5a7499f8d | 5/5 | 5/5 | same |
| L1-LI-surface-a-quarantined-message | quarantined | qwen3:8b | fb4b612f3e600fd0 | 5/5 | 5/5 | same |
| L1-LI-present-what-onboarding-only-observed | observed_entries | qwen3:8b | 1fb9ac3cce780bdd | 5/5 | 5/5 | same |
| L1-LI-a-question-about-the-program-goes-to-its-owners | converse | qwen3:8b | 357b6836a1aab5eb | 5/5 | 5/5 | same |
| L1-LI-a-ruling-splits-by-owner | verdict_signoff | qwen3:8b | 5df50dacd25c2b53 | 5/5 | 5/5 | same |
| L1-LI-present-the-touch | touch_note | qwen3:8b | 9954d15c0335599e | 5/5 | 5/5 | same |
| L1-LI-say-what-the-run-could-not-see | blindspot | qwen3:8b | 8c2e8b88229f9a4a | 5/5 | 5/5 | same |
| L1-LI-a-question-the-roles-could-not-answer | unresolved | qwen3:8b | af92a3961dec153d | 5/5 | 5/5 | same |
| L3-ratified-statement-becomes-scope | verdict (first leg) | qwen3:8b | 9392b789f4ced1eb | 5/5 | 5/5 | same |
| L3-ratified-statement-becomes-a-term | verdict (first leg) | qwen3.5:9b | 0c5ac0d74ca22149 | 5/5 | 5/5 | same |
| L3-a-maintainers-question-reaches-the-owner | converse (first leg) | qwen3:8b | a0a85b01061bffb4 | 5/5 | 5/5 | same |

Totals: 32 same, 1 down, 0 up. The one "same" red was red at baseline.

## (c) Cases that went down, or stayed red

### L1-LI-no-report-no-question (converse): 5/5 -> 0/5. DOWN. The brief change.

Case: `tests/rota/cases/l1_liaison.yaml:138-162`. Entry: "make the dashboard
better, you know what I mean". Expects `statements >= 1`. Forbids a
`clarify` message to the principal and writes to `entries`, `items`.

All five runs sent the same three calls. The last model turn, verbatim, is
identical in runs 1 to 5 (seq 146515 to 146519):

```
TOOL: msg.clarify_principal(refs=["e_m_in_3bf132"], question="Could you clarify what you mean by 'make the dashboard better'?")
```

Session summary of each run: `called: ['brief.list', 'transcript.quote',
'msg.clarify_principal']`, `wrote: {}`, `sent: [['principal', 'clarify']]`.

Problems column, each run:
`["expected writes to statements (>=1), got 0", "forbidden message clarify to principal"]`

Under the old brief (before-backup, seq 146160 to 146164) all five runs sent:

```
TOOL: brief.intake(verdict='work')
TOOL: brief.segment(id='s1', span_start=0, span_end=33, text='make the dashboard better, you know what I mean')
TOOL: msg.confirm_principal(refs=['s1'])
```

Attribution: converse composes on base.md, so the model saw B1 ("reading
what the principal means, then checking that reading with them"), B3
("you may raise one of your own"; "Every question names its row") and B4
("Infer, then check"). converse.md lines 72 to 77 still say a vague request
is work, segmented in the words used. The model now checks its reading with
the principal by a clarify that names the entry row. The case's own comment
(lines 153 to 156) encodes the old law: "asking about it is inventing a
question nobody raised". The case and the new brief disagree. This needs a
ruling, not a fix by me: either the case changes (a clarify that names its
row is allowed when the words are vague), or base.md gets a sentence that a
vague work request is segmented, not clarified.

### L1-LI-a-question-then-a-statement-at-the-confirm-is-the-question (landing): 0/5 -> 0/5. Not the brief change.

Red at baseline with the same output. The last model turn, verbatim,
identical in runs 1 to 5 (seq 146480 to 146484):

```
TOOL: rulings.rule(rulings={"1": "contest"}, words="before I say yes: does each person pay an equal share, or their own order? I mean an equal share of the total including the tip.")
```

Problems column, each run:
`["expected message {'to': 'principal', 'verb': 'converse', 'count': 1}, got 0 match(es)", "forbidden write to rulings: ['r_...']"]`

The baseline transcript (seq 146129) has the same call shape and the same
two problems. landing composes on `landing.base.md`, so this wake never saw
the base.md changes. It saw L1 and L2 in landing.md, and its behaviour did
not move. Pre-existing red.

## T1 tests (tests/rota/test_t1_liaison.py, ROTA_T1=1, qwen3:8b, Titan)

| Test | case_runs id | Result | problems |
|---|---|---|---|
| test_i1_segmentation_at_principal_granularity | I1 | FAILED | s1 span [17,68] out of bounds for 56-char entry |
| test_i3_harvest_dedupes_and_traces | I3 | PASSED | |
| test_i6_no_reports_means_no_questions | I6 | FAILED | broadcast reached nobody, expected all three |
| test_i4_readonly_writes_nothing_and_bumps_nothing | I4 | PASSED | |

No baseline exists for these four ids on any model in `case_runs`, and no
qwen3:8b cassette existed for them before this run. So I ran a control: the
same two tests under the HEAD versions of base.md, converse.md and
verdict.md, through the `ROTA_PROMPTS=ctrl` variant door
(`rota/roles/prompts.py:_variant`), with `ROTA_DEV_DB` pointed at
`scratchpad/ctrl_dev.db`. cassettes.db was not touched. The variant
directory was removed after the run and `git status` shows only the six
intended files plus the pre-existing walks.jsonl. The control took 29 s.

Control result: I1 FAILED with `s1 span [18,69] out of bounds for 56-char
entry`. I6 FAILED with `broadcast reached nobody, expected all three`. Both
reds are the same under the old brief. Neither is the brief change.

What the model sent (from the cassettes; the T1 tests record no transcript):

I1, new brief (cassette rowid 22314):
```
TOOL: brief.segment(id='s1', span_start=17, span_end=68, text='we need SSO, but only if it works with our LDAP')
TOOL: msg.confirm_principal(refs=['s1'])
```
I1, old brief (control): `span_start=18, span_end=69`, same text. The
entry is "morning! we need SSO, but only if it works with our LDAP" (56
chars); the correct span is [9,56]. qwen3:8b miscounts the offset after a
leading greeting under both briefs. `L1-LI-segment` (5/5 both times) has a
different entry and the model's offsets there are right.

I6, new brief (cassette rowid 22318) and old brief (control), the same:
```
TOOL: brief.ratify(id="s1")
TOOL: msg.deliver_vision_keeper(refs=["s1"], round_no=0)
TOOL: msg.deliver_terminologist(refs=["s1"], round_no=0)
TOOL: msg.deliver_architect(refs=["s1"], round_no=0)
```
The model broadcasts to all three. `test_i6` (line 219) counts messages
with `m["verb"] == "brief"`. The verdict mode's tools are `msg.deliver_*`
(`verdict.tools`), which write the verb `deliver`. No Liaison tool writes a
message verb `brief` (`brief.*` in api.py is a tool namespace, not a message
verb). The test is stale against the wiring. It cannot pass with any brief.
Not fixed: reported.

## (d) V1 door check

Result: YES. The Liaison in verdict mode is shown the ruling words, `revise`
included. V1 is applied as written.

Evidence:

- `rota/roles/principal.py:44`: `per_item: dict[str, str]` maps a ref to
  `approve|contest|revise`.
- `rota/roles/principal.py:720-729` (`land`): the per-item ruling, less the
  approved rows closed at the keypress, is stored in `config` under the key
  `verdict:<msg_id>`. A `revise` is always in it.
- `rota/roles/principal.py:805-808`: `verdict_for(conn, message_id)` reads
  that key back.
- `rota/core/runner.py:703-705`: the wake builder puts
  `out["principal_verdict"] = verdict_for(conn, trigger)` into the message
  the Liaison sees.

Caveat: the case `L1-LI-ratify` (`tests/rota/cases/l1_liaison.yaml:64-83`)
seeds an inbound `verdict` message and no `config` row, so its wake carries
no `principal_verdict`. The re-record of that case does not exercise the
`revise` sentence. The two L3 verdict chains and test_i6 seed the same way.

## (e) Prompt tests without a model

Command: `python -m pytest tests/rota/test_prompts.py tests/rota/test_intake_fork.py tests/rota/test_principal_reply.py tests/rota/test_signoff_assumptions.py -q`

Tail:

```
bringing up nodes...
bringing up nodes...

................................................                         [100%]
48 passed in 5.78s
```

No literal word had to be restored. converse.md lines 29 to 31 are untouched.
base.md line 1 still reads "You are Liaison."

## (f) Diff stat and CR counts

`git diff --stat rota/roles/prompts/liaison/`:

```
 rota/roles/prompts/liaison/base.md        | 38 ++++++++++++++++---------------
 rota/roles/prompts/liaison/blindspot.md   | 10 +-------
 rota/roles/prompts/liaison/converse.md    |  8 +++----
 rota/roles/prompts/liaison/landing.md     | 11 ++++-----
 rota/roles/prompts/liaison/round_close.md | 12 +++++-----
 rota/roles/prompts/liaison/verdict.md     | 13 ++++++-----
 6 files changed, 43 insertions(+), 49 deletions(-)
```

The fourteen changes: B1 to B5 in base.md, C1 and C2 in converse.md, L1 and
L2 in landing.md, R1 to R3 in round_close.md, V1 and V2 in verdict.md, S1 in
blindspot.md. Old text was copied from the files, not from the report.
Paragraphs were re-wrapped at each file's width. The full diff is in the
working tree, not committed.

CR counts: `grep -c $'\r' rota/roles/prompts/liaison/*.md` gives 0 for all
19 files. A Python count of byte 0x0D gives 0 for all 19 files.
`git ls-files --eol` shows `i/lf w/lf` for all 19 files.

## (g) Wall-clock time of the re-record

Start 03:35:08, end 03:56:45: 21 min 37 s total. Sum of the eleven batch
durations: 1207 s (20 min 7 s). The rest is the gaps between foreground
calls. The control run (29 s, 03:59:42 to 04:00:11) is not in this figure.

| Batch | Start | End | Duration | Result |
|---|---|---|---|---|
| landing (6) | 03:35:08 | 03:37:05 | 117 s | 5 passed, 1 failed (red at baseline) |
| l1_liaison (6) | 03:37:06 | 03:40:21 | 195 s | 5 passed, 1 failed: L1-LI-no-report-no-question |
| g1_segments (4) | 03:40:43 | 03:42:35 | 112 s | 4 passed |
| l1_answering (1) | 03:42:44 | 03:43:14 | 30 s | 1 passed |
| l1_answers (2) | 03:43:24 | 03:44:01 | 37 s | 2 passed |
| l1_exhausted (1) | 03:44:10 | 03:44:58 | 48 s | 1 passed |
| l1_liaison2 (9) | 03:45:06 | 03:49:10 | 244 s | 9 passed |
| l1_survey (1) | 03:49:22 | 03:50:07 | 45 s | 1 passed |
| l1_unresolved (1) | 03:50:07 | 03:50:24 | 17 s | 1 passed |
| l3_handoffs (3) | 03:50:34 | 03:55:41 | 307 s | 3 passed (includes the qwen3.5:9b swap) |
| t1 (4) | 03:55:50 | 03:56:45 | 55 s | 2 passed, 2 failed (I1, I6) |

No Ollama hang. No turn came near 20 minutes. Load id of every qwen3:8b row:
`qwen3:8b@248545`.

## Re-record pre-flight and mechanics (step 5)

- `curl localhost:11434/api/tags` and `curl localhost:11435/api/tags` both
  answered with the same 18 models. `localhost:11435/api/ps` held no model
  before the run and holds `qwen3:8b` after it.
- `Get-CimInstance Win32_Process -Filter "name='python.exe'"`: 0 processes
  before the run. No pytest, no recorder, no llama-server.
- Backups, both made with the SQLite backup API from a read-only connection
  and verified against the source (`pragma quick_check` ok, same counts):
  - `.rota/cassettes_backup_2026-09-16-liaison-before.db`: 18038 cassettes,
    144110 case_runs, max seq 146459. 15.8 s.
  - `.rota/cassettes_backup_2026-09-16-liaison-after.db`: 18102 cassettes,
    144284 case_runs, max seq 146633. 5.8 s.
- `--collect-only` with the `-k` expressions selected exactly 6 landing, 6
  l1_liaison, 9 l1_liaison2, 6 other L1/L2, 4 G1, 3 L3 cases and the 4 T1
  tests. No extra case by substring.
- Batch mechanics: the first two batches (landing, l1_liaison) ran from the
  serial script `scratchpad/rerecord.sh` in a background shell. On the
  coordinator's instruction at 03:37 I stopped that script's shell only
  (pid 5156; pytest 23512 untouched, it finished and wrote its rows), waited
  for it in the foreground, then ran every later batch as one foreground
  call per case file with `scratchpad/batch.sh` (same environment; it
  refuses to start while another python.exe runs). One process held
  cassettes.db at a time throughout. Logs: `scratchpad/rerecord.log` and
  `scratchpad/rerecord_<batch>.log`.
- After-table script: `scratchpad/after_table.py`, output
  `scratchpad/after_table.out`.


---

# Cycle 2

# Liaison brief cycle 2: two paragraphs in base.md, apply and re-record (2026-09-16)

Status: DONE. Nothing is committed. Only `rota/roles/prompts/liaison/base.md`
is edited. `tests/rota/walks.jsonl` was modified before this task and is not
mine. No case file changed.

## Summary

- The two paragraphs are applied as written. base.md holds no 0x0D byte.
- Prompt tests without a model: 22 passed.
- Re-record on the Titan, qwen3:8b, load `qwen3:8b@248545` (the same load as
  cycle 1): all 28 non-landing Liaison cases are 5/5. `L1-LI-no-report-no-question`
  goes UP from 0/5 to 5/5. All five runs send `brief.segment` + `msg.confirm_principal`.
  No case went down. 27 same, 1 up.
- T1: I3, I4, I6 pass. I1 fails, as in cycle 1, but with a new shape. The model
  sends `msg.confirm_principal(refs=['s1'])` with no segment, gets the "names no
  row" error, then sends `msg.clarify_principal` asking what "SSO" refers to.
  In cycle 1 on the same load it segmented (span wrong) and confirmed. Details in (e).
- Wall clock of the re-record: 18 min 55 s (04:07:44 to 04:26:39).

Two observations for the reviewer, neither a fail by the case's own terms:

1. The five passing runs of `L1-LI-no-report-no-question` skip `brief.intake`.
   converse.md line 2 says to call `brief.intake(verdict='work')` when the message
   asks for anything. The old-brief run (seq 146164) called it. `L1-LI-segment`
   calls it this run. The case does not require it.
2. Those runs write `span_end=41` for a 47-character text. The old-brief run
   wrote `span_end=33`. `brief.segment` accepts the span. The case checks the
   statement count only. Pre-existing miscount, not a cycle-2 change.

## (a) Diff of base.md

`git diff rota/roles/prompts/liaison/base.md`:

```
diff --git a/rota/roles/prompts/liaison/base.md b/rota/roles/prompts/liaison/base.md
index 644eb7a..6c4a8e1 100644
--- a/rota/roles/prompts/liaison/base.md
+++ b/rota/roles/prompts/liaison/base.md
@@ -19,14 +19,16 @@ system. It exists so that later interpretations can be checked against something
 Greetings, asides, hedges, repetition — all of it goes in exactly as written. Never
 tidy, summarise or correct a principal's words.
 
-**Every question names its row.** You carry questions that other roles reported,
-and you may raise one of your own. A question that names no row is nothing to ask,
-however vague the principal was being. What a vague statement means is not yours to
-settle; it is Vision Keeper's or Terminologist's to report on.
-
-**Infer, then check.** You read what the principal means, and you check that
-reading with them before it stands. You do not settle what a term means, what is
-in scope, or whether something is feasible — those belong to another role.
+**Every question names its row.** You carry questions that other roles reported.
+You may raise one of your own, and only about a row that exists: a statement, an
+entry, an item. A vague ask is not a question to raise. Segment it in the words
+they used and confirm the cut. What a vague statement means is not yours to
+settle; the roles that own those words ask their own questions.
+
+**Infer, then check.** You read what the principal means, and your check is the
+confirm of that reading. Asking them to explain themselves before you have a
+reading is not a check. You do not settle what a term means, what is in scope,
+or whether something is feasible — those belong to another role.
 
 **Conclusions travel; reasoning stays home.** Messages carry ids, not essays. When
 you send refs, the recipient follows them.
```

Old text was copied from the file. The new lines are 81 characters or shorter.
The file's longest line is 85 characters and is pre-existing.

## (b) Prompt test tail

Command: `python -m pytest tests/rota/test_prompts.py -q -p no:cacheprovider`

```
bringing up nodes...
bringing up nodes...

......................                                                   [100%]
22 passed in 3.62s
```

## (c) After-table

Source: `tests/rota/cassettes.db`, read-only, table `case_runs`. For each case:
the latest row's model and `prompt_hash`, then `passed` summed over the latest
row per `run_no` for that case, model and hash. "fresh hash" means the row's
`prompt_hash` equals the sha256 prefix of the instructions composed from the
working tree now (`scratchpad/after_table_c2.py`). "this run" means seq >= 146634
(the before-backup holds max seq 146633). Every row is yes / yes. "cycle 1" is
section (b) of `liaison-apply-report.md`.

| Case id | Mode | model | prompt_hash | latest seq | after | cycle 1 | changed |
|---|---|---|---|---|---|---|---|
| G1-scope-sounding-words-are-not-scope-yet | converse + awaiting_confirm | qwen3:8b | 7847bd7f619b419e | 146713 | 5/5 | 5/5 | same |
| G1-an-owners-answer-reaches-the-seat | answer | qwen3:8b | d0ae76436d0847c5 | 146718 | 5/5 | 5/5 | same |
| G1-what-the-brief-already-holds-is-answered-from-it | converse | qwen3:8b | c49f32c559cd4907 | 146728 | 5/5 | 5/5 | same |
| G1-a-reply-that-answers-something-else-ratifies-nothing | converse | qwen3:8b | c49f32c559cd4907 | 146723 | 5/5 | 5/5 | same |
| L1-LI-a-reply-reaches-the-desk-that-asked | answering | qwen3:8b | 5752ca3c69e40a22 | 146733 | 5/5 | 5/5 | same |
| L1-LI-put-the-open-assumptions-to-a-present-principal | agenda | qwen3:8b | 7cc597af2665bc0f | 146738 | 5/5 | 5/5 | same |
| L1-LI-relay-an-answer-without-improving-it | answer | qwen3:8b | d0ae76436d0847c5 | 146743 | 5/5 | 5/5 | same |
| L2-LI-carry-the-block-to-the-principal | report | qwen3:8b | 73c795526e4be134 | 146748 | 5/5 | 5/5 | same |
| L1-LI-chat-is-not-work | converse | qwen3:8b | c49f32c559cd4907 | 146638 | 5/5 | 5/5 | same |
| L1-LI-segment | converse | qwen3:8b | c49f32c559cd4907 | 146643 | 5/5 | 5/5 | same |
| L1-LI-ratify | verdict | qwen3:8b | 1128358335e90f5b | 146648 | 5/5 | 5/5 | same |
| L1-LI-present-for-signoff | submit | qwen3:8b | 93a63e795a0b3633 | 146653 | 5/5 | 5/5 | same |
| L1-LI-present-carries-the-uncovered-statement | submit | qwen3:8b | 93a63e795a0b3633 | 146658 | 5/5 | 5/5 | same |
| L1-LI-no-report-no-question | converse | qwen3:8b | c49f32c559cd4907 | 146663 | 5/5 | 0/5 | UP |
| L1-LI-put-a-contradiction-back-unresolved | contradiction | qwen3:8b | 2523266b2fe0a7d7 | 146668 | 5/5 | 5/5 | same |
| L1-LI-ask-for-the-confirmation-nobody-asked-for | awaiting_confirm | qwen3:8b | b88edc468b63d4c6 | 146673 | 5/5 | 5/5 | same |
| L1-LI-relay-a-ruling-without-interpreting-it | verdict_signoff | qwen3:8b | 43f770035af8f9a5 | 146678 | 5/5 | 5/5 | same |
| L1-LI-two-questions-at-most-from-three-reports | round_close | qwen3:8b | 167199169594f156 | 146683 | 5/5 | 5/5 | same |
| L1-LI-surface-a-quarantined-message | quarantined | qwen3:8b | 4f5a2647254882e4 | 146688 | 5/5 | 5/5 | same |
| L1-LI-present-what-onboarding-only-observed | observed_entries | qwen3:8b | db4de0c689d9cc32 | 146693 | 5/5 | 5/5 | same |
| L1-LI-a-question-about-the-program-goes-to-its-owners | converse | qwen3:8b | c49f32c559cd4907 | 146698 | 5/5 | 5/5 | same |
| L1-LI-a-ruling-splits-by-owner | verdict_signoff | qwen3:8b | 43f770035af8f9a5 | 146703 | 5/5 | 5/5 | same |
| L1-LI-present-the-touch | touch_note | qwen3:8b | e93addc35c5c7109 | 146708 | 5/5 | 5/5 | same |
| L1-LI-say-what-the-run-could-not-see | blindspot | qwen3:8b | 88a46f3ff154738a | 146753 | 5/5 | 5/5 | same |
| L1-LI-a-question-the-roles-could-not-answer | unresolved | qwen3:8b | 5da4bcfc2485b262 | 146758 | 5/5 | 5/5 | same |
| L3-ratified-statement-becomes-scope | verdict (first leg) | qwen3:8b | 7b90fd013ce07635 | 146773 | 5/5 | 5/5 | same |
| L3-ratified-statement-becomes-a-term | verdict (first leg) | qwen3.5:9b | f6377d49cb161b31 | 146768 | 5/5 | 5/5 | same |
| L3-a-maintainers-question-reaches-the-owner | converse (first leg) | qwen3:8b | 2188703c70c161b7 | 146763 | 5/5 | 5/5 | same |

Totals: 27 same, 1 up, 0 down. Load id of every qwen3:8b row this run:
`qwen3:8b@248545` (139 rows). The qwen3.5:9b leg: `qwen3.5:9b@248545` (5 rows).
The six l1_landing.yaml cases were not re-recorded. Landing composes on
`landing.base.md` and never sees base.md.

## (d) Transcripts

### L1-LI-no-report-no-question (converse): 0/5 -> 5/5. UP.

The last model turn is identical in runs 1 to 5 (seq 146659 to 146663), verbatim:

```
TOOL: brief.segment(id='s1', span_start=0, span_end=41, text='make the dashboard better, you know what I mean')
TOOL: msg.confirm_principal(refs=['s1'])
```

Problems column, each run: `[]`.

Session summary, each run: `called: ['brief.list', 'brief.segment',
'msg.confirm_principal']`, `wrote: {'statements': 1}`, `sent: [['principal', 'confirm']]`.

For comparison, cycle 1 (seq 146515 to 146519) sent
`TOOL: msg.clarify_principal(refs=["e_m_in_3bf132"], question="Could you clarify what you mean by 'make the dashboard better'?")`
with `called: ['brief.list', 'transcript.quote', 'msg.clarify_principal']`.
The old brief (seq 146160 to 146164) sent `brief.intake(verdict='work')`, then
`brief.segment(id='s1', span_start=0, span_end=33, ...)` + `msg.confirm_principal(refs=['s1'])`.

No other case went down. No other transcript is required.

## (e) T1 results

`tests/rota/test_t1_liaison.py`, `ROTA_T1=1`, qwen3:8b, Titan, load `qwen3:8b@248545`.
case_runs rows seq 146774 to 146777. These rows carry no transcript, so the
model turns below come from the `cassettes` table.

| Test | case_runs id | Result | assertion message |
|---|---|---|---|
| test_i1_segmentation_at_principal_granularity | I1 | FAILED | see below |
| test_i3_harvest_dedupes_and_traces | I3 | PASSED | |
| test_i6_no_reports_means_no_questions | I6 | PASSED | |
| test_i4_readonly_writes_nothing_and_bumps_nothing | I4 | PASSED | |

I1 assertion message (three problems):

```
AssertionError: expected 1 statement(s) at principal granularity, got 0
  clarify sent during intake — Liaison must not ask
  no confirm sent to the principal
```

I1 entry: `"morning! we need SSO, but only if it works with our LDAP"`.

What the model sent this run, cassette rowid 22587 then 22588, verbatim:

Turn 1 (rowid 22587), after the pre-run `brief.list -> []`:
```
TOOL: msg.confirm_principal(refs=['s1'])
```
The tool answered:
`ERROR msg.confirm_principal: 's1' names no row -- not in any table, not written this session. Refs are ids from the rows you were given or the tools you called; if you mean a thing with no row, the thing to send is the row that talks about it`

Turn 2 (rowid 22588):
```
TOOL: msg.clarify_principal(refs=['e_m1'], question='does "SSO" refer to a specific system or protocol?')
```

What the model sent in cycle 1 on the same load, cassette rowid 22313 then 22314:
```
TOOL: brief.intake(verdict='work')
```
```
TOOL: brief.segment(id='s1', span_start=17, span_end=68, text='we need SSO, but only if it works with our LDAP')
TOOL: msg.confirm_principal(refs=['s1'])
```
Cycle 1 failed on the span only (`s1 span [17,68] out of bounds for 56-char entry`).

Reading: I1 is red before and after. The shape moved. The model no longer
segments the I1 entry. It confirms a statement that does not exist, and when
the wiring refuses, it asks the principal a terminology question about "SSO".
The load id is the same as in cycle 1, and the only Liaison prompt file that
changed between the two runs is base.md, so the two paragraphs moved this
output. The same paragraphs moved `L1-LI-no-report-no-question` the other way.
The two entries differ: I1 opens with the greeting "morning! ". One recording,
one run, temperature 0. I did not change the test or the brief.

I1 system prompt check, `cassettes.system` column: rowid 22314 (cycle 1) holds
"you check that reading with them" and not "confirm of that reading". Rowid
22587 (cycle 2) holds "confirm of that reading" and "A vague ask is not a
question to raise", and not the old sentence. The I1 wake saw the new paragraphs.

I6 passes this run because commit 51af9f1 changed the test to count
`verb == "deliver"` (line 219). The model still broadcasts to all three roles
(rowid 22595: `brief.ratify(id="s1")` then `msg.deliver_vision_keeper`,
`msg.deliver_terminologist`, `msg.deliver_architect`). No clarify.

I3 passes on structural assertions: at least one clarify, at most two, refs
carried. The injected reports carry refs `["s1"]` and no body, so the clarify
question is the model's own words ("The statement 'let people close their
account' is ratified. Does this mean the account closure feature is now active,
or is further development required?"). The same was true in cycle 1.

## (f) Wall-clock time

Re-record start 04:07:44, end 04:26:39: 18 min 55 s. Sum of the ten batch
durations: 1040 s (17 min 20 s). The rest is the gaps between foreground calls.
No Ollama hang. No turn came near 20 minutes.

| Batch | Cases | Start | End | Duration | Result |
|---|---|---|---|---|---|
| c2_l1_liaison | 6 | 04:07:44 | 04:10:42 | 177 s | 6 passed |
| c2_l1_liaison2 | 9 | 04:10:53 | 04:14:53 | 238 s | 9 passed |
| c2_g1_segments | 4 | 04:15:02 | 04:16:57 | 114 s | 4 passed |
| c2_l1_answering | 1 | 04:17:06 | 04:17:20 | 13 s | 1 passed |
| c2_l1_answers | 2 | 04:17:31 | 04:18:08 | 36 s | 2 passed |
| c2_l1_exhausted | 1 | 04:18:17 | 04:19:18 | 60 s | 1 passed |
| c2_l1_survey | 1 | 04:19:26 | 04:20:11 | 44 s | 1 passed |
| c2_l1_unresolved | 1 | 04:20:19 | 04:20:36 | 17 s | 1 passed |
| c2_l3_handoffs | 3 | 04:20:45 | 04:25:22 | 276 s | 3 passed |
| c2_t1 | 4 tests | 04:25:32 | 04:26:39 | 65 s | 3 passed, 1 failed (I1) |

Logs: `scratchpad/rerecord_c2_<batch>.log`.

## (g) 0x0D count

`python -c "b=open('rota/roles/prompts/liaison/base.md','rb').read(); print(b.count(b'\r'))"`
gives 0. The file is 3019 bytes.

## Pre-flight and mechanics

- `curl -s localhost:11435/api/tags` answered with 18 models. `/api/ps` held no
  model before the run.
- `Get-CimInstance Win32_Process -Filter "name='python.exe'"`: 0 processes before
  the run. `batch.sh` refuses to start while another python.exe runs, so one
  process held cassettes.db at a time.
- Environment: `OLLAMA_HOST=http://127.0.0.1:11435`, `ROTA_MODEL=qwen3:8b`,
  `ROTA_L1=1`, `ROTA_REFRESH=1`, `ROTA_PROFILE` and `ROTA_DEV_DB` unset,
  `ROTA_T1=1` for the T1 batch only.
- `--collect-only` with the `-k` expressions selected exactly 6, 9, 4, 1, 2, 1,
  1, 1, 3 cases (28) and the 4 T1 tests. No extra case by substring.
- Backups, SQLite backup API from a read-only connection, verified against the
  source (`pragma quick_check` ok, same counts):
  - `.rota/cassettes_backup_2026-09-16-liaison-c2-before.db`: 18102 cassettes,
    144284 case_runs, max seq 146633. 6.6 s.
  - `.rota/cassettes_backup_2026-09-16-liaison-c2-after.db`: 18166 cassettes,
    144428 case_runs, max seq 146777. 6.4 s.
- `git status --short` at the end: `M rota/roles/prompts/liaison/base.md` and
  the pre-existing `M tests/rota/walks.jsonl`. Nothing else.
- After-table script: `scratchpad/after_table_c2.py`, output
  `scratchpad/after_table_c2.out`.
