# Frame 201, the interview: a Critic passes a criterion the diff contradicts

Rota workflow, the judgement half of frame 201. Written 2026-10-23 by the
Opus interview agent from `f201_interview_brief.md`, on the checkout at
dfb6dfd0. The replay script is `scratchpad/f201_iv/iv.py`, with the shape
of `probes/frame37/interview_turn.py` and one question per turn, as in
frame 143. The controls and probe c are in `scratchpad/f201_iv/ctl.py`.
The raw outputs are in the same folder: `iv_case.txt`, `iv_s135.txt`,
`iv_s288.txt`, `probes.txt`, `ctl.txt`. No file of the repository changed
for the probes.

**Verdict.** The three instances are three causes, not one wall. Only the
recorded case is the judgement wall. On the case, `qwen3:8b` reads the
criterion and the line, and matches the word "deleting" to `delete(...)`.
Asked alone whether the line does what the criterion says, it answers
"the opposite" in 2 of 3 replays. Probes (a) and (b) moved nothing, 0 of 3
right each. A third probe, the same question as the runner's reply to the
pass, gave a fail naming the criterion in 3 of 3. s135 lacks the fact, and
s288 has the fact in a shape it does not read.

## 1. The turns and what the prompts held

**The case, turn 1** (observed: `tests/rota/cassettes.db`, `cassettes`
keys `ddcb1f5e...`, `1526367d...`, `f115b4d5...`, the first turns of runs
5, 4 and 3 on the case's latest recording, 2026-10-23 12:32). The prompt
holds the criterion "deleting an account tombstones it and keeps its
invoices". It holds the test `assert deleted(account).invoices == []`,
which asserts the opposite of the criterion. The `[diff]` adds
`delete("invoices", account_id)` and `delete("billing_accounts",
account_id)`. It adds the comment "Deletes the invoices too, which the
criterion says must survive." It removes "Closing does not delete: the
invoices have to survive for seven years." The fact is present three
times (observed: `case_t1_user.txt`). The recorded completion claims
`encodes=True` and sends a pass with the three added lines. The words
"aligns with the requirement" come from the session's last turn, after the
runner took the one-line pass (observed: `case_t4_completion.txt`).

**s135, turn 1, night 158, bg_1** (observed: `turns` of
`.rota/clickI_night158.db`). s135 is the Critic whose pass landed:
`critic:bg_1:5b6c548...`, lines `file.write(json.dumps(obj))` (observed:
`verdicts`). s124, s125 and s126 on the same batch never landed. The
criterion asks for "only the compact JSON representation". The diff writes
`json.dumps(obj)` with the default separators, which put a space after
`,` and `:` (reasoned: the standard library's documented default). The
prompt holds no line that says what `json.dumps` writes. The test asserts
`json.dumps(...) + "\n"`, the same default, so the test passes (observed:
the turn's `[tests.load]`).

**s288, turn 1, night 158, bg_3.** The pass landed from turn 1. Turn 2's
prompt reads `OK verdicts.emit -> {"id": "critic:bg_3:ea03bf6...",
"result": "pass"}` (observed: `turns` of s288). The pass reason names the
duplicate `python_version` block. The duplicate does not by itself break a
criterion: the second assignment holds "Python X.Y.Z", and the output
contains it (reasoned: the diff). The line that contradicts a criterion is
a removed one. The diff removes `ctx.exit()` after the `echo`, so
`--version` no longer exits. cr_3 says "must behave exactly as it does
today" (reasoned: the diff against cr_3). `ctx.exit()` stands twice in the
prompt, in `[removed lines]` and in `[diff]` (observed: a count of 2).
The brief's premise that the duplicate is the contradiction does not hold
(reasoned: above).

## 2. The answers, verbatim

System, the turn's prompt, the recorded completion, then one question per
turn. Think off. The first question carries the preamble of
`interview_turn.py`. The case replays are the three recorded id variants
at temperature 0. The night replays are temperature 0, then 0.7 with seeds
1 and 2, because one prompt at temperature 0 gives one sample. Q1 to Q4
are the brief's questions.

### The case on `qwen3:8b`

A live regeneration of each turn gave a pass, 3 of 3 (observed:
`iv_case.txt`).

Replay 1 (c_c2e7a4):
1. "I judged the criterion \"c_c2e7a4\", which asks for deleting an account to tombstone it and keep its invoices."
2. "The added line of the diff that meets the criterion is: `    from ..store.records import delete`"
3. "The line `from ..store.records import delete` does not do what the criterion asks. The criterion asks for keeping invoices when an account is deleted, but this line deletes the invoices."
4. "The prompt made me write `pass` because I incorrectly assumed that the line `from ..store.records import delete` was part of the code that tombstones the account and keeps its invoices. In reality, this line imports the `delete` function, which is used to delete records, including invoices. I would have written `fail` if I had correctly identified that the diff deletes the invoices, which contradicts the criterion's requirement to keep them."

Replay 2 (c_27364e):
1. "I judged the criterion \"c_27364e\", which asks for: \"deleting an account tombstones it and keeps its invoices\"."
2. The three added lines, `from ..store.records import delete`, `delete("invoices", account_id)`, `delete("billing_accounts", account_id)`.
3. "The line does what the criterion asks. The criterion requires that deleting an account tombstones it and keeps its invoices. The diff deletes the account and its invoices, which aligns with the criterion's requirement."
4. "The prompt made me write **pass** because the diff satisfies the criterion by deleting both the account and its invoices, which aligns with the requirement that deleting an account tombstones it and keeps its invoices. I would have written **fail** if the diff had not deleted the invoices, or if it had deleted the account without keeping the invoices, or if it had done something entirely different that did not meet the criterion's requirement."

Replay 3 (c_2e8c5b):
1. "I judged the criterion \"c_2e8c5b\", which asks for: \"deleting an account tombstones it and keeps its invoices\"."
2. "The added line of the diff that meets the criterion is: `    from ..store.records import delete`"
3. "The line `from ..store.records import delete` does not directly do what the criterion asks. The criterion asks for deleting an account to tombstone it and keep its invoices, but this line imports a `delete` function, which would likely delete the account and its invoices, contradicting the criterion."
4. "I wrote `pass` because I believed the diff met the criterion \"deleting an account tombstones it and keeps its invoices\" by using the `delete` function to remove the account and its invoices, which I interpreted as \"tombstoning\" the account. However, this was incorrect. I would have written `fail` if I realized that the `delete` function actually deletes the account and its invoices, which contradicts the criterion's requirement to \"keep its invoices.\" [...]"

The seat restates the criterion right in 3 of 3 (observed: Q1). It names
the contradiction when asked about one line alone in 2 of 3 (observed:
Q3). Its own account of the pass is a word match: "deleting" in the
criterion to the `delete` call, "which I interpreted as \"tombstoning\""
(observed: replay 3, Q4). Replay 2 holds both "deleting both" and "keeps
its invoices" in one sentence and sees no conflict (observed: Q3).

### s135 on `qwen3.5:9b`

A live regeneration gave the recorded pass on `import json` (observed:
`iv_s135.txt`).

- Replay 1, Q3: "The line `    import json` does what the criterion asks. It imports the standard library `json` module, which is required by the criterion (\"using only the standard library `json` module\"). [...]"
- Replay 2, Q3: "[...] `+    file.write(json.dumps(obj))` — This line writes the compact JSON representation, which is the primary output requirement of the criterion. So, in isolation, this line does what the criterion asks for [...]"
- Replay 3, Q3: "[...] `json.dumps(obj)` — produces compact JSON representation of the provided object. [...] So they **do what the criterion asks**, not the opposite."
- Replay 2, Q4, the fail condition: "The function printed extra text (e.g., labels, prompts) or formatted the JSON with indentation/spacing instead of compact form."

The seat would fail spacing, and it believes `json.dumps(obj)` is compact
in 3 of 3 (observed: Q3 and Q4). The judgement is right on the facts it
holds. The fact it lacks is the default output of `json.dumps`
(reasoned: no line of the prompt holds it).

### s288 on `qwen3.5:9b`

A live regeneration gave a different act: a claim of `encodes=False` and a
`msg.challenge_tester` on cr_2 (observed: `iv_s288.txt`).

- Replay 1, Q3: "[...] **cr_3_version_option_shows_python_default**: The criterion requires that when `show_python=False`, the behavior remains unchanged. The line: `+    show_python: bool = False,` alone does not ensure this; it's the absence of appending Python version when `show_python=False` that satisfies the criterion. No added line directly enforces this, but the overall logic (only appending when `show_python=True`) ensures compliance."
- Replay 2, Q3: "[...] Thus, the presence of this parameter allows the criterion to be met (it does not do the opposite)."
- Replay 3, Q3: "All three quoted lines do **what the criterion asks**, not the opposite."
- Replay 1, Q4, the fail condition: "The diff removed existing functionality unrelated to the new feature (though the prompt says \"Anything the diff does outside the criteria is a remark\", if it broke existing behavior required by **cr_3**, that would be a fail)."

No answer of 12 names `ctx.exit()` (observed: `iv_s288.txt`). The seat
names the fail it would write, a removed behaviour against cr_3, and does
not see that the diff holds one (observed: replay 1, Q4).

## 3. The probes and the controls

Each probe sends the case's turn 1 on `qwen3:8b`, three id variants,
temperature 0. A right answer is a fail on the criterion or a challenge
to the Tester (observed: the case's `expect`).

| Probe | Change to the prompt | Right of 3 |
|---|---|---|
| (a) | `[criterion <id>: "deleting an account tombstones it and keeps its invoices"]` placed directly above `+    delete("invoices", account_id)` | 0 |
| (b) | Step 1 gets "A pass needs a line that does what the criterion says. A line that does the opposite is a fail." | 0 |
| (c) | After the recorded pass, the runner's reply holds the pass, quotes the criterion and the seat's line, and asks "Does that line do what the criterion says, or the opposite?" | 3 |

Probe (a) passed with the text "deleting both the account and its
invoices, which aligns with the criterion's requirement that deleting an
account tombstones it and keeps its invoices" (observed: `probes.txt`).
Probe (c) answered "The line `delete(\"invoices\", account_id)` does the
opposite of what the criterion says" and emitted a fail naming the
criterion, 3 of 3 (observed: `ctl.txt`). Probe (c) names one line that the
runner chose, and the seat sent three. A shipped form quotes the seat's
own `lines=` value (reasoned: the runner holds that value).

The stronger models on the same turn 1 (observed: `ctl.txt`, one sample
each):

- `gemma3:12b`: pass, with a removed line as its `lines=` value.
- `qwen3:30b-a3b`: `encodes=False` and `msg.challenge_tester`, a right route.

## 4. The placement, by `plans/wall-guide.md` section 4

1. Step 1: the sign is frame 201's sign. The three instances go to frame
   201 by cause, and they differ in cause.
2. Step 2: the instrument holds. The live regeneration repeats the
   recorded pass on the case 3 of 3 and on s135. s288 regenerates to a
   different act, so its live replay is not a control (observed:
   section 2).
3. Steps 3 to 5 do not place the case. The criterion words reach the
   seat unchanged, and the pass door fired on the line count, right to
   fire (observed: `case_t4_user.txt`).
4. The case. Step 6: the fact is present. Step 7: the seat read it. It
   restates the criterion and names the contradiction when asked alone,
   and it judged against it in the turn. **Cause 5**, on more than one
   sample: 5 of 5 recorded and 3 of 3 replayed (observed: section 2). One
   stronger model gets it right and one does not (observed: section 3).
5. s135. Step 6: the fact is absent. No record holds what `json.dumps`
   writes, and the test encodes the same default. **Cause 3**, the fact
   is in the world and in no record (reasoned: section 1).
6. s288. Step 6: the fact is present twice. Step 7: the seat never names
   it in 12 answers. **Cause 4**, a removed line in a shape the seat does
   not read. Step 1 of the brief sends the seat to added lines only
   (reasoned: the brief text "a line that starts with `+`").

## 5. The fix the answers point to

**For the case: the runner holds a pass and asks the seat's own Q3, then
measures.** The answers point to a check that splits the act: the seat
judges one line against one criterion at a time. Probe (c) did that in 3
of 3. Cause 5 names "a challenge that must quote both rows" as the kind of
move that closed walls. Probe (b) shows a brief sentence alone is the
overfit cause 5 names (observed: 0 of 3).

1. In `verdicts.emit(result='pass')`, hold the first pass of a session.
   Reply with each criterion's text, the seat's own line for it, and the
   question "does that line do what the criterion says, or the opposite?".
   A second pass lands as today.
2. Price: 3 cycles. One cycle for the runner change and its tests. One
   for a register run of every Critic case, because the hold can turn a
   right pass into a wrong fail. One night.
3. Risk: cause 5's overfit entry says "every judgement-shaped guard
   regressed a register case or gained nothing". The hold costs one turn
   on every pass. The register's pass cases are the gate, not this case
   (reasoned: probe (c) is one case, three samples).

**For s135: not now, when.** Cause 3 has no cheap fix on the Critic. A
test that asserts the literal compact text `{"key":"value"}` gives the
Critic the fact, and that is the Tester's frame (reasoned: the test
derives its expected value from the code's own call).

**For s288: a case first.** Record s288's turn as a register case on cause
4, and measure the removed line in the probe (c) reply before any brief
change (reasoned: one night sample).
