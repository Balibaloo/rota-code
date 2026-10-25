# Frame 323: Gemma where it fails, and the Qwen fit in the briefs

Reader on Opus, 2026-10-25, from `f323_interview_brief.md`. Register copy `C:/Users/roman/rota_cassettes_f323.db`, read-only. Replays on the 3080 at 12:05 to 12:16, `num_ctx` 16384, `num_predict` 8192, think off, temperature 0, the same `system` and `user` as the cassette row.

## The verdict

**Gemma's shape, not an over-fit to Qwen.** Half of the Gemma runs fail on one serving fault: with `think: false`, `gemma4:12b-it-qat` under Ollama generates 8192 tokens and returns no text (observed: cassette rowid 60846 replayed, `done_reason` length, `eval_count` 8192, content 0 characters, thinking 0 characters, 176 s). A raw generate of the same prompt shows the hidden tokens: the empty thought channel, `<|channel>thought\n<channel|>`, again and again (observed: rowid 61277, 60 tokens; the raw template is my guess at the renderer, so read it as a sign, not proof). The same prompt with `think: true` thinks 302 tokens and calls `code.source(path='src/notify/formatting.py', ...)`, which is Qwen's passing move (observed: rowid 60846). The six interviews name no Qwen-measured rule. They name role-brief sentences, and those gaps are model-neutral. One runner text is fitted to Qwen's failure and is false for Gemma: the cut note. It tells the seat to "send less" and to write a span, after a reply that was empty.

Two counts in the brief differ from the register. The register holds 9 Developer and 4 Terminologist cases at 0 of 5, not 11 and 3 (observed: `case_runs`, model `gemma4:12b-it-qat`, grouped by case). Two of the 13 are red for every model: `L1-DV-log-the-choice-the-criteria-did-not-make` and `L1-TE-log-the-word-you-took-one-way` are 0 of 10 on `qwen3.5:9b` and on `qwen3:8b` (observed: the last 10 runs per model). So 11 cases are Gemma-specific.

## 1. What Gemma did instead

One line per case: what the case asks / what Qwen did / what Gemma did / the first error Gemma got. Qwen is `qwen3:8b` unless named.

- DV-a-wordless-answer-leaves-a-wrong-test-alone: challenge the tester with the architect's decision `d_fdd7fe` / `msg.challenge_tester` with the decision in refs / one sentence, "The answer leaves the code right as it stands.", no call / no error; the case fails on the missing message.
- DV-a-wordless-answer-on-a-right-red-test-is-carried-on: write the fix and commit / `code.source`, `code.write`, `ledger.log`, `code.commit` / `code.source`, then a `code.write` with an unescaped quote, then commit with nothing written / "a quote inside text ended it early".
- DV-build-a-clear-criterion: create `money` in `src/notify/formatting.py` and commit / probe, source, write, commit / an empty turn at the budget, seven `code.probe` calls down to `pattern='*'`, then a question to the vision keeper, which is forbidden / "your reply was cut at the output budget".
- DV-challenge-a-test-that-contradicts-its-criterion: challenge the tester / one probe, one source, `msg.challenge_tester` / probe after probe on an empty index, `code.survey` (not in its set), an empty turn, prose "I cannot find any code" / "'code.survey' is not in this role's working set", then the cut.
- DV-challenge-a-test-with-a-long-body: challenge the tester / loads, probe, source, challenge / the same reads re-sent, a question to the researcher about paths, an empty turn / "'code.survey' is not in this role's working set".
- DV-escalate-a-finding-the-loop-could-not-answer: escalate to the architect / `msg.escalate_architect(refs=["b_b1f83e"])`, the batch id only / `refs=["f_fba8ec", "k_9b6905"]`, the finding and the constraint, three times / "no file in the worktree defines 'calculate_tip' now". The door refuses the better refs. Qwen passes by citing the batch only.
- DV-give-the-new-parameters-defaults (`qwen3.5:9b`): fix `display_results` and commit / source, write, commit / `code.source` on the same spans eight times, a whole-function write, then an escalation that is forbidden / the cut, then "repeat refused: code.source".
- DV-log-the-choice-the-criteria-did-not-make: write, commit and log / no model passes / thirteen `code.probe` calls on an empty index, an empty turn, prose / the cut.
- DV-take-out-what-nobody-asked-for: ask the vision keeper about `pluralise`, or take it out / one `msg.question_vision_keeper` / `src/utils.py` paged 400 characters at a time to offset 106000 in one reply, `code.survey`, probes, commit with nothing written / the cut, then "'code.survey' is not in this role's working set".
- TE-a-new-behaviour-is-a-new-callable: specify criteria that name `split_bill` / four `criteria.specify` / the pre-run `glossary.lookup` and `tickets.scan` calls six times over / "repeat refused: glossary.lookup".
- TE-a-rung-for-a-question-the-principal-asked: answer the liaison with the glossary rows / one `msg.answer_liaison` with three refs / an answer with no row refs, a report, then lookups again / "an answer names the rows it came from, and these name none".
- TE-log-the-word-you-took-one-way: define the word and log the reading / no model passes / three `glossary.amend`, an empty turn, "I have completed my work" / the cut.
- TE-specify-criteria: specify criteria for `tk_ad9c1a` / three `criteria.specify` / the same four lookups four times / "repeat refused: tickets.scan", then the verbatim end.

Counts over all 296 Gemma runs (observed: `cnt.py` on the copy):

- 148 runs got the cut note at least once, and 104 runs ended on it. By seat: Developer 66 of 105, Tester 36 of 70, Critic 22 of 39, Terminologist 24 of 82. Qwen's rate on the same note is below 1%.
- The cut turns are empty, not long. 149 of 1581 Gemma cassettes hold an empty completion, and only 5 hold more than 8000 characters. The register keeps one row per prompt, so 149 is a floor of the 175 cut events (reasoned).
- 39 runs ended on "repeated its previous turn verbatim twice".
- 6 runs wrote a whole file where a span was asked, out of 31 runs with a `code.write`. Whole-file writes are not the Developer's wall.
- 5 runs made no call. All 5 are Developer runs.
- Re-sent reads are the second wall: "repeat refused" fired 147 times on `glossary.lookup`, 108 on `code.probe`, 80 on `code.source` and 40 on `tickets.scan`. Most re-send a call that the prompt lists under "Already run for you".

## 2. The interviews

Each failing turn was replayed, then asked the question of the brief in a second turn. Answers are verbatim, cut at 400 characters. They are read against the record, never as proof (`plans/operating-facts.md`, line 142). Files: `scratchpad/f323i/r_<name>.json`.

1. DV build, rowid 60853. Shape reproduced: the same question to the vision keeper. "The sentence in the brief that led to my reply was: "The criteria are the specification; the ticket text is context." Because `code.probe` returned nothing for the path specified in the criteria, I interpreted the absence of the file as a potential scope error or a path mismatch rather than an instruction to create a new file. To have led to the `code.write` call, the brief could have included: "If a file specified in the criteria does not exist, create it.""
2. DV challenge-contradicts, rowid 60996. Shape reproduced: "I cannot find any code" and five `code.source` calls. "The sentence that led to my reply was: "Answering from the test and the criterion alone means answering about words whose meaning you did not look up, and the answer that comes out is almost always 'the criterion is silent', which is a description of what you read rather than of what is there." The one sentence that would have led me to the `msg.challenge_tester` call is: "Does this test assert w[hat its criterion asks for?]""
3. DV take-out, rowid 60708. Shape reproduced in part: the replay wrote only the first line of the night's paging, `code.source(... start=0, end=400)`. It quoted the "Two honest answers" block, then: "The sentence that led to my reply (the `code.source` call) was: "You are developer. This is a single session..."" and proposed: "If the rename of `plural` to `pluralise` is not explicitly required by the criteria, ask the Vision Keeper if it is within scope."
4. DV wordless, rowid 60652. Shape reproduced word for word. "The prompt instructions for the `msg.challenge_tester` tool state: "If the answer is a decision row that says the test does not encode the criterion, send `msg.challenge_tester` with that row's id in refs, beside the criterion and the test." The architect's decision `d_fdd7fe` explicitly states: "c_230e19 holds, and tst_12b03e does not encode it." To have triggered the call, the instruction sho[uld have been: ... **even if the answer also states the code is correct.**]"
5. TE specify, rowid 61497. Shape reproduced: the same four lookups. "The sentence that led to my reply was: "Ask for everything you need to know in one go -- several questions cost one turn. But once you have asked anything, stop: what you do about the answers is next turn's work, and anything you write now was decided without them." Because I had not yet found the terms "delete", "account_page", or "button" in the glossary, I was attempting to gather the necessary"
6. TE log-word, rowid 61276. Shape reproduced: three `glossary.amend` and a report, no `ledger.log`. "The sentence in the system instructions that led to my reply (and the omission of the ledger) was: "If it is undefined and unambiguous, define it with glossary.amend." Because the statement was a simple imperative without conflicting contexts, I treated the terms as unambiguous. To have triggered a `ledger.log` call, the instr[uctions would need to specify that a choice must be recorded even when no collision exists.]"

## 3. The Qwen fit in the briefs and doors

The grep of `rota/roles/prompts/` finds no sentence that names Qwen. "Measured on" appears six times, all on Liaison and Vision Keeper live runs, none on a Developer or Terminologist brief. The Qwen-shaped texts are in the runner and the backend:

- The cut note, `rota/core/runner.py` line 5254: "Send less in one reply ... write the span you changed". Measured on clickI night 16, a 688-line whole-file write. For Gemma the reply was empty, so the note is false. Named by Gemma: no.
- The verbatim end, `runner.py` line 5444 and `db.py` line 1032. Measured on a 14B survey session (reasoned: `qwen2.5:14b`, the 14B of that time). It is model-neutral and fires correctly on Gemma's loops. Named: no.
- The span-write rule, `developer/batch_start.md` lines 20 to 28. Worded for whole-file cuts. Gemma pages from the top against it in one case. Named: no.
- The think flag, `rota/llm/llm.py` `THINK_DEFAULT = False`, worded for "the qwen3 family". It is the cause of the empty turns on Gemma. Named: no, and a model cannot see it.
- The text protocol's turn rule, `runner.py` line 508, "Ask for everything you need to know in one go ... once you have asked anything, stop". Model-neutral in origin. Named: yes, once, by the Terminologist (answer 5) as the reason to re-send lookups.

The sentences Gemma names are role content: the Developer's "criteria are the specification", the `tests_failing.md` call to look before answering, the `answer.md` order of the wordless rule before the decision-row rule, and the Terminologist `deliver.md` list, which has no ledger rule. None of them was measured on Qwen.

## 4. Three model-neutral changes

**Change 1: an empty reply at the budget is the backend's fault, not the seat's.** When `done_reason` is `length` and the content is empty, the runner records `empty at the output budget` and does not send the cut note. The profile then pins `think: true` for `gemma4:12b-it-qat`, as it already can per model (`think_for`). This moves the five cases with the cut on 5 of 5 runs, and up to 148 of 296 runs. The risk for Qwen is nil on the text, because a Qwen cut carries content and keeps today's note. The think pin costs Gemma time: two of three think-on replays thought past 3000 tokens. A replay checks `ACT-TS-three-criteria-one-per-reply` and `ACT-DV-edit-inside-the-function` on `qwen3.5:9b`, which hold most of Qwen's recorded cut notes.

**Change 2: a file the criterion names is the batch's to create.** Add one sentence to `developer/batch_start.md` step 4: "A path the criterion names and `code.probe` does not find is a file you create with `code.write`." This moves `L1-DV-build-a-clear-criterion`, and on the same empty index it may move `L1-DV-log-the-choice-the-criteria-did-not-make`. The sentence stays in the batch-start mode, because the challenge modes forbid `code.write`. The risk for Qwen is a new file where a path was mistyped. A replay checks `L1-DV-build-a-clear-criterion` and `L1-DV-read-the-map-not-the-whole-file` on both Qwen models.

**Change 3: a door names a next step that the seat can take.** Two door texts send Gemma back to reading. The `code.source` miss names `code.survey`, which the Developer does not hold (29 Gemma errors, and Qwen hits it too). The repeat refusal says only "The answer is in this prompt". Change the miss to name `code.probe` and to say that an empty index means the bodies in `tests.load` are the code to judge. Change the refusal to name the mode's write call, for example `criteria.specify` in the criteria tick. This moves the two challenge cases, `L1-DV-take-out-what-nobody-asked-for`, `L1-TE-specify-criteria` and `L1-TE-a-new-behaviour-is-a-new-callable`. The risk for Qwen is a moved prompt hash on every case that meets the refusal, and a seat that writes too early. A replay checks `L1-DV-give-the-new-parameters-defaults` and `ACT-TS-five-criteria-one-per-reply`, which meet the refusal most often.

Not chosen: the wordless-rule order in `developer/answer.md` and the missing ledger rule in `terminologist/deliver.md`. The second one is red on every model, so it is a case or brief question, not a model question. The escalation door that refuses refs to a function the fixture lacks is a fixture question.

The evidence that decides the verdict: 148 of 296 runs meet one fault that no brief sentence causes and that `think: true` removes on the replayed turn. In the remaining failures, Gemma names role sentences, never the five Qwen-measured rules.
