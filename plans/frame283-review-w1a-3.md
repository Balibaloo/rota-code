# Frame 283, W1 a, review 3: pass 3 at abe03230

Worktree `C:/Users/roman/rota_r283`, parent ee3cbcd0. Read-only. No gate ran and no case was re-recorded.

Verdict: accept for the night. The three closures of point 1 hold by probe. The predicate residue of point 2 is real, but no text of nights 140 to 158 reaches it. The texts of point 3 agree.

## (a) The claim, point by point

1. Closed. Seq 20 lands one `faults` row, the drop note stays `open`, and seq 17 and 23 get the ledger text. The three forbidding sentences admit nothing. "Remove the ctx.exit() call." admits. A ruled removal commits in the same reply. No item is open.
2. The residue is acceptable for the night. Of 11 shapes, the door refuses 5 right rulings and admits 5 wrong ones. The 9 new shapes give 4 and 4. No sentence of the 141 removal sentences of nights 140 to 158 names a removed statement in a way that the door reads. Record a clause-scope fix as an open item of frame 283. Do not block the night on it.
3. Met. The ledger text and the later-reply commit refusal end in the same three sentences, word for word. Each sentence has 19 words or fewer. Each text holds the fact, one step and the escalate route. The same-reply refusal differs, see finding 3.

## (b) Findings

1. **The negation scope is the whole sentence prefix, so a reason clause refuses a right ruling.** `rota/roles/api.py:16893` (`_NEGATION_WORDS`) and `16905` (`s[:m.start()]`). Low for the night. CONFIRMED.
   - Probe Q2: "The ctx.exit() call is not reached after echo, so please remove ctx.exit()." is refused. So are "Keep the echo, and take ctx.exit() out of the callback.", "It isn't needed after echo, so you can drop ctx.exit()." and "The callback still calls ctx.exit(), which I asked you to drop."
   - These are the principal's real shapes: nights 140, 143, 144 and 147 give a negated reason, then "so please drop it".
   - "The callback must no longer call ctx.exit()." is refused too, as the pass said.
   - The refusal is the safe side. The seat gets the escalate route, and the Architect carries the ask.
   - Fix: read only the words between the last clause break (comma, "so", "and", "which", colon) and the removal word.
2. **A sentence that names the removal as a fault or a consequence admits it.** `rota/roles/api.py:16897-16911` (`_removal_asked`). Low for the night, high for the frame. CONFIRMED.
   - Probe Q2 and P1s: "Removing ctx.exit() is a bug." admits, and the commit lands in the same reply.
   - Probe Q2: "Fix the callback rather than drop ctx.exit().", "You were wrong to drop ctx.exit().", "The callback no longer calls ctx.exit() after echo, and that is the bug." and "Without ctx.exit(), the program runs the command after it prints the version." admit.
   - The shapes come from nights 144, 147, 146 and 149. The "without" rule admits a statement name that follows "without", whatever the sentence says.
   - Probe Q1: 141 unique removal sentences on nights 140 to 158, and 72 with no negation before the word. One names a statement word, "continue" on night 153, and it admits nothing. So the night exposure measured zero.
   - Fix: admit only an imperative or a request form ("remove", "please drop", "you can take out") at the start of its clause. Refuse "rather than", "wrong to" and a gerund subject.
3. **The same-reply commit refusal carries no escalate route and states its fact twice.** `rota/roles/api.py:16739-16751`. Low. CONFIRMED.
   - Probe P4: the text is five sentences. Sentence 1 and sentence 3 both say that the seat did not read the note. The steps say "write the lines back" with no `msg.escalate_architect`.
   - The later-reply text and the ledger text give the escalate route. So a seat that commits in the write's reply hears a different route first.
   - Fix: drop the third sentence, and end the `held` step with the shared route sentences.
4. **Review 2's findings 3, 5 and 7 stay open by the brief's scope.** Low. CONFIRMED by reading.
   - The page-line number rule is still at `16929`. No merge reader of `drop_notes` exists. The ledger door list has no bound on its first sentence.
   - The pass names the two discard paths that write `restored` with the line gone (pass 3, fix 5). The commit door reads the tree, so the row admits nothing tonight.
   - Fix: carry the three items as open items of frame 283, each with its own ends-when.

Outside the points: none found beyond finding 3.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/81fe1025-ee88-45f4-8210-744972761835/scratchpad/r3/`. Each ran from `C:/Users/roman/rota_r283` with `D:/repos/rota/.venv/Scripts/python.exe`.

- T0: `tests/rota/test_frame283_removal_on_ruling.py`, 17 passed.
- P1, `test_r3_probe.py::test_p1_s279`: the s279 replay. Seq 17 and 23 equal the ledger text. Seq 20 returns `call`, `fault` and `note`, and stages one `faults` row of kind `fault`. The path keeps one `open` note. Seq 16, 19 and 26 equal the first refusal.
- P1s, `test_r3_probe.py::test_p1_sentences`: seven criteria, then a write and a commit in one reply. Refused: "Do not remove ctx.exit().", both "Never drop" forms, "The option must call ctx.exit().", "must no longer". Committed: "Remove the ctx.exit() call." and "Removing ctx.exit() is a bug.".
- P3, `test_r3_probe.py::test_p3_texts`: the sentences and word counts of the first refusal, the ledger text and the commit door refusal. The longest sentence has 19 words.
- P4, `test_r3_held.py`: the same-reply refusal of an unruled removal, sentence by sentence.
- Q1, `q1_nights.py`, output `q1.out`: every sentence with a removal word in `_ruling_texts` of every batch of nights 140 to 158, read-only, with its negation state.
- Q2, `q2_shapes.py`: `_asks_removal` on the two named sentences and nine shapes from Q1, rewritten to name `ctx.exit()`.

## (d) Usage

- Input: about 45k tokens of context at the end. The harness gives no exact split.
- Output: about 8k tokens.
- Total: about 53k tokens. Sub-agents: none.
