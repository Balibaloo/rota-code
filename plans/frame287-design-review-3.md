# Frame 287, design review 3: revision 4, the rulings ledger

Meta workflow. Read-only review on Opus of `plans/frame287-design.md` revision 4 (R4.0 to R4.8) at 14c35074, 2026-10-18. Line numbers are of that file at that commit.

## (a) Verdict

Revision 4 does not stand as written. The direction stands: the ledger with a `Keys:` line meets Roman's 01:27 words, and it is not wiring. Four findings decide the verdict:

- Finding 1, high. Frame 1's check is circular. The back-fill writes entries from page C's questions, and the check then searches the same questions.
- Finding 2, high. R4 claims that the 10-03 and 10-04 rules "failed on findability and not on will". Cause 1, as review 1 rewrote it, says that nobody searched. R4 fixes that cause with one more prose step, and it measures findability only. Nothing counts whether a session runs the search.
- Finding 3, high. New rulings still stay in a transcript. The ledger grows by habit, which is cause 3 and cause 5 again. The search drops the transcript extraction, which was review 2's fallback.
- Finding 4, high. The search has no stated match rule. A line-based match misses law 2's "decision record", because a line break splits the phrase. An any-word match on a question as sent floods the 3k cap.

Two lows need a fix before frame 1 is pushed. Finding 6: two back-fill agents are two writers of one record. Finding 9: the size is 219 quote blocks, not 140.

## (b) The points

### Point 1. His words of 01:27. Holds, with one gap (finding 3)

- "mimicking rota is only intented to take the good parts ... you are not rota": R4.0 item 1, "The build session is not a seat." Met.
- "you can design your context": R4.0 item 4, "the session's own to do". Met.
- "You dont have wakes, you just wait for your turn and take over the entire stack": R4.1, "one strong model that takes the whole stack on its turn". The `wake` tool leaves. Met.
- "my words being persisted for their intent": R4.0 item 2, "persisted in the repository, as the outcome and the meaning of each discussion". Met.
- "dont force them onto models": R4.0 item 3, "It is never loaded". R4.8 adds the guard against pasting entries. Met.
- "whenever a model looks for answers they are able to find the outcomes and the meaning": R4.2 and R4.3 meet this for the back-filled past. The gap is the future. Finding 3 shows that a ruling given after the back-fill is findable only if a session writes its entry by habit.

### Point 2. The earlier rulings. One crossed, two weakened

- #369 (page A line 246, "Don't make that persisted, just give yourself a habit to communicate meaning with me"). Not crossed. #369 is about the meaning of a frame. 01:27 asks for "the meaning of our discussions", which is later and narrower. R4.2 says this. Keep one entry per discussion outcome, never one entry per frame.
- 2026-10-03 and 2026-10-04 14:52. Weakened, low. R4.2 says the ledger "does not replace them". R4.3 adds "cite what it prints or that it printed nothing". Neither line says what follows a zero-hit print. Review 2 finding 4 fixed that in revision 3: the agent runs the whole 10-03 read on no hit or at the cap. R4 drops the sentence. Finding 7.
- "a conclusion goes to a record when it forms". Held in words, weak in fact. See finding 3.
- "Every record has one writer". Crossed. R4.2 names the holding session as the one writer. R4.4 has "Two Opus agents write it". Finding 6.
- 2026-10-07, agents on Opus. Held for the back-fill. The review agent of frame 1 carries no model. Name Opus there too.

### Point 3. The diagnosis. Causes 2 and 3 addressed, cause 1 not, causes 4 and 5 unnamed

- Cause 2, filed by principle: the `Keys:` line addresses it, if the keys carry the asker's words. See point 4.
- Cause 3, a dissolving read filed where no key points: the ledger addresses it for the past. For the future, see finding 3.
- Cause 1, nobody searched the law file: not addressed. Review 1 finding 4 showed by grep that `LAWS.md` already answered frame 114's key. The session did not run the grep. R4 adds a step to the history rule, which recurred four times (page B). The stack status of 01:26 says the rule "failed on findability and not on will". Review 1 finding 4 shows the opposite for frame 114. Finding 2.
- Causes 4 and 5: R4 does not name them. A case-blind grep for "cause" over R4 gives one hit, cause 2. Cause 4 is the held fact that the session did not connect. Cause 5 is the prose rule that fails at its moment. The search tool serves the moment of a question. The step that calls the tool is still prose. R4 must say this. Finding 2.

### Point 4. The entry form. Holds, with two changes

The three entries are in section (c). The form holds frame 114 and frame 204. Frame 115 strains the form at `Said:`. Law 2 predates the transcripts (first record 2026-09-16, page A), so no verbatim words and no session exist for its substance. His 10-04 14:34 words say only "we have already discussed this". The form needs "Said: none in the transcripts, the ruled text is law n".

The grep test:

- Frame 204: the question words are the answer words. "notes", "merge", "default" and "park" are in the answers of 10-11 and 10-12. A grep on the question hits the `Keys:` line from either side.
- Frame 114: the 10-17 question is "May a Developer restore a definition its own batch broke". "restore", "repair" and "project file" give 0 hits in `LAWS.md` (probe 2). Only the asker's words make the hit, so the `Keys:` line must carry them.
- Frame 115: the questions say "answer", "prose", "words", "where does the answer go". `grep -ci prose rota/LAWS.md` gives 0. Law 2 says "finding", "decision record" and "ref". The `Keys:` line must carry "answer", "prose" and "edge gains prose". Probe 3 found a second gap. The 10-04 14:29 question says "decision record", which is in law 2. A line grep misses law 2, because the phrase breaks across lines 114 and 115. Finding 4.

Who writes the asker's words: today only the back-fill agent can, and only because page C hands it the questions. That is finding 1. In the future, the writer is the holding session at the moment Roman says "we already discussed this", or when a later read finds the record a search missed. R4 has no such step. Fix: add one line to the history rule. "When a record held the answer to a sent question, append the question's words to that entry's `Keys:`." Finding 5.

### Point 5. The back-fill. The method is sound. The size is wrong. A cheaper first step exists

- Marking: R4.4 marks the entry "(observed: the source)" and the `Means:` line "(reasoned)". R4.8 keeps every `Means:` line (reasoned) until a session confirms it "with him or from a transcript turn". Sound. Confirmation with him on about 150 lines costs his attention, which the composition calls the scarcest budget. Expect most lines to stay (reasoned). Say so, and make the search print the mark.
- Size: page A holds 219 quote blocks, not about 140 (probe 4). The extraction holds 779 records, 626 typed and 153 answers. `CLAUDE.md` carries 30 "ruled:" marks, the guide 35, and the 40 memory files about 58. Page C adds 25 rows, about 10 distinct answers.
- Entry count (reasoned): about 110 to 140 from page A and the extraction, after grouping by discussion. About 60 to 80 from the brief, the guide and memory, half of them already in page A. About 10 from page C. Total about 150 to 200 entries. At about 180 tokens an entry, the ledger is about 27k to 36k tokens, about 110k to 150k characters.
- Token cost (reasoned from the anchors): reads A to D cost 120k to 148k each on the harness line against caps of 80k to 100k. "A cap written in a brief does not bind" (operating-facts, frame 66). Agent 1 reads page A, 68k characters, and `compact.txt`, 151k characters, and writes about 120 entries: about 200k to 300k. Agent 2 reads 200k characters of page C, the brief, the guide and memory, and writes about 80 entries: about 150k to 220k. The review adds about 100k to 130k. Frame 1 then costs about 450k to 650k on the agents and about 4 cycles, about 12k, in the session.
- The cheaper first step, about 1 cycle and 50k to 80k:
  1. Run a paragraph-level search with no ledger over `LAWS.md`, `DECISIONS.md`, `ROLES.md`, the archive and the night reads, on the seven answers' questions as sent (page A, A111 to A114, and page C). The misses name the keys the ledger must add.
  2. Write a pilot of about 20 entries from sources dated before 2026-10-01, by an agent that never sees page C.
  3. Search the pilot with page C's questions. Run the full back-fill only if the pilot finds more answers than the search with no ledger.
- This was revision 3's prototype bet (section 9). R4 drops the bet and gives no reason. Review 1 finding 4's fix said "Run the back-fill only for the misses the prototype names".

### Point 6. The search tool. Worth building, if it carries a match rule

Plain `grep -rn` fails in three ways that the tool can fix:

- The hard wrap. Law 2's "decision record" spans a line break, so a line grep misses it (probe 3). The tool must match over a paragraph or an entry with the whitespace joined.
- Many words. A question as sent has 10 to 20 words. Any-word matching floods: "answer" hits 1,059 archive lines, "file" 1,207 and "developer" 745 (probe 2). All-word or phrase matching hits nothing. The tool must drop stop words and rank by the count of distinct query words matched, with the `Keys:` line weighted first.
- The order of print. Ledger entries print first, then the law, the decision, the role and the archive, each with its own share of the cap.

The 3k cap is right for a print that an agent reads before it opens files. It is right only with a ranking. Without one, the "first hits" are in file order, and frame 114's entry can fall past the cap on a common word. Add `rota/ROLES.md` to the scope, because page C row 64's answer is `ROLES.md:150-170` and R4.3's list omits the file. Add the transcript extraction as the last source (finding 3). Print `Supersedes:` on a match, because frame 204's 10-11 "Every default" is superseded on 10-12.

### Point 7. The context design of R4.5. Not wiring. No wake under another name

- The status tool is a writer that the session calls. It stamps the clock and commits by pathspec. It decides nothing about what reaches a model. Not wiring.
- The take print, `stack held`, is a view that the session calls at the take. It is revision 3's `wake take` without the moment or the push. Not wiring. R4.2 says "The take reads what it reads today", and R4.5 changes the take read to the print. Make the two lines agree (finding 11).
- One risk: the print shows the last three status lines. Frame 287's ruling of 01:27 drops out of view after three more status lines. Print every status line marked "ruled" as well, or the entry headings the frame cites. Low.
- Nothing of the withdrawn `wake` tool survives under another name. `wake ask`, `wake push`, `wake night`, `wake close` and `wake next` are gone. The note deletion at close is one call in `handover.py`, by hand until then.

### Point 8. The frames of R4.6. The order is right. Two ends-when lines are not observable. Frame 1's check is not honest

- The order holds. Frame 1 writes only new files. Frame 2 writes `status.py`, `stack.py` and `handover.py`. They share no file. Frame 3 edits `CLAUDE.md` and points at both, so it waits on both.
- Frame 1: "the ledger holds the back-fill of R4.4" is not countable. Name a count of entries or the list of sources covered. The check fails on finding 1.
- Frame 2: "a taker ... state reply cites no line the print did not give" waits on a hand-off that nobody schedules. Name the wait. The line also scores as a failure a taker that reads the stack when it needs to. Use: "the state reply names every held frame's open wait and its last ruling, from the print".
- Frame 3: "under 5k tokens by `wc`". `wc` counts characters, not tokens. Write "under 20,000 characters by `wc -c`". "He rules the lines he wants changed" is a wait on Roman. Put it on a `Waits on:` line.
- Frame 1's check, seven answers and four keys to one entry, is not sufficient. The seven answers are page C's rows, and R4.4's second bullet writes an entry for each with the question in view. The search then finds what the writer wrote to be found. Four of the eleven checks are frame 114 keys. The check has no noise measure: it never counts the other entries on the first screen. Finding 1.

### Point 9. R4.7. A question rated low, not a notice. It does not gate frame 1

The composition's build-session paragraph reads "Its records are this page, the stack, and the memory directory." Roman ratified the page. `CLAUDE.md` lists "a change touches the composition" as an escalation trigger. So the sentence goes to him as a question. The rating is low. The sentence follows his item 2 ruling of 01:27, and no edit before frame 3 depends on it. The list already omits `plans/archive/`, the guide and `operating-facts.md`, so the sentence describes and does not gate. Frame 1 does not touch `composition.md`, so frame 1 can start. Send the sentence as `[low]` with the brief diff of frame 3, on a 20-minute timer. Do not call it a notice.

### Point 10. What R4.8 does not doubt

- That a session runs the search at all (finding 2). Measure it: of the next questions to Roman, the share that carry a "rulings search:" line, against page C's baseline of 25 of 103 answered by a record or a read.
- That the frame 1 check is circular (finding 1).
- That the ledger grows after the back-fill (finding 3).
- That the ledger and `rota/DECISIONS.md` both record one rota-workflow ruling. Frame 114's ruling of 2026-10-17 is already in `DECISIONS.md`, near line 1501. Two records of one fact drift. For a rota-workflow ruling, keep `Said:` and `Means:` in `DECISIONS.md`, and give the ledger entry `Keys:` and `Rule:` only.
- That the 3k cap cuts the answer on a common word (finding 4).
- That the `Said:` lines persist words he typed in anger. A153 holds "youre pissing me off". 01:27 asks for his words "for their intent". Quote the part that carries the ruling, and point at the session and time for the rest.

### Point 11. Overfit. Partial, low

The ledger shape generalises. Frame 204's answers sat in one transcript, which is cause 3, and the form holds them. The example in R4.2 and four of the eleven checks of frame 1 are the frame 114 story: law 12, 04325814, `api.py` and frame 114. Review 1 finding 17 and review 2 finding 12 asked for held-out questions. Rows 64, 89 and 102 are not door questions. Use them as the held-out set, with entries written before the agent sees page C.

### Findings

1. **Frame 1's check is circular.** Design line 163 with lines 124-127. High. CONFIRMED by the text. R4.4's second bullet writes an entry for each of page C's 25 answered questions. The check of line 163 searches with the same questions' words. The writer knows the test. Fix: write the pilot entries from sources dated before 2026-10-01, by an agent that never sees page C, then test on page C as held-out.
2. **R4 fixes cause 1 with prose, and it calls the failure findability.** Design lines 105-109 and the stack status of 2026-10-18 01:26. High. CONFIRMED against review 1 finding 4, where `grep -i permission rota/LAWS.md` lands in law 12, and against page B's four recurrences of the history rule. R4 names neither cause 4 nor cause 5. Fix: name causes 1, 4 and 5 as not addressed, and add an ends-when ratio, the share of questions to Roman that carry a "rulings search:" line against page C's baseline.
3. **The ledger grows by habit only, and the search drops the transcripts.** Design lines 132-135 and 95-99. High. PLAUSIBLE by page C section 1, group 3: frame 204's answers stayed in one session's `AskUserQuestion` results for 32 hours under the rule "a conclusion goes to a record when it forms". Fix: the search reads the regenerated extraction of his words as its last source, from one fixed local path, as review 2 finding 8 asked.
4. **The search has no match rule, and a line grep misses law 2.** Design lines 95-102. High. CONFIRMED by probe 3: "decision record" gives 3 hits in `LAWS.md` with the whitespace joined and 2 hits by line, and the lost hit is law 2. Probe 2 shows "answer" at 1,059 archive lines. Fix: match per paragraph with the whitespace joined, drop stop words, rank by distinct words matched with `Keys:` first, and cap each source.
5. **Nothing writes the asker's words onto the `Keys:` line after the back-fill.** Design lines 78-85. Low. PLAUSIBLE by point 4: frame 114's "restore" and "repair" and frame 115's "answer" and "prose" are absent from the laws that answer them. Fix: one line in the history rule, "when a record held the answer to a sent question, append the question's words to that entry's `Keys:`".
6. **Two back-fill agents write one record.** Design line 113 against line 59. Low. CONFIRMED by the text against the composition, "Every record has one writer". Fix: each agent writes a staging file in the scratchpad, and the holding session merges and commits `plans/rulings.md`.
7. **No step follows a zero-hit print.** Design lines 105-108. Low. CONFIRMED by the text: revision 3's sentence for the whole 10-03 read on no hit or at the cap is gone. Fix: restore that sentence in R4.3.
8. **The form has no `Said:` for a ruling that predates the transcripts.** Design line 82. Low. CONFIRMED: law 2 and law 12 predate 2026-09-16, the first transcript record. Fix: allow "Said: none in the transcripts, the ruled text is law n".
9. **The back-fill size is 219 quote blocks, not about 140.** Design line 123. Low. CONFIRMED by probe 4. Fix: write 219 blocks and 779 records, and price frame 1 at about 450k to 650k on the agents.
10. **Two ends-when lines are not observable as written.** Design lines 163-165. Low. CONFIRMED by the text: "holds the back-fill" has no count, frame 2's taker waits on an unnamed hand-off, and `wc` measures no tokens. Fix: as in point 8.
11. **R4.2 and R4.5 disagree on the take.** Design line 91 against lines 147-149. Low. CONFIRMED by the text. Fix: write "the take reads the print of R4.5 and nothing from the ledger".
12. **`ROLES.md` is outside the search scope.** Design line 95. Low. CONFIRMED: page C row 64's answer is `rota/ROLES.md:150-170`, one of frame 1's seven answers. Fix: add `rota/ROLES.md` to R4.3's sources.

Outside the points:

13. **The design header still says "Revision 2".** Design line 5. Low. CONFIRMED by the text. Fix: name revision 4 and its date in the header.

## (c) The three sample entries of point 4

Frame 114. The question as sent on 10-04 (A111): "A developer broke a project file earlier in the same piece of work. What may a later developer do to that file?" On 10-17 (row 99): "May a Developer restore a definition its own batch broke".

    ### R114. A Developer may write any file; the Architect signs off an unexpected change after it, and no door refuses a write for straying (2026-10-17, rota workflow)
    - Keys: law 12; LAWS.md:325-342; DECISIONS 2026-10-17; expected touch set, prediction, permission, stray, touch_strays, _outside_prediction, batches_judge_touch; unnamed-definition door, 04325814, fence, e8e1a207; rota/roles/api.py, code.commit; frames 114, 220, 286; broke, broken, restore, repair, partial repair, project file, definition, own batch, later developer, may a developer, allowed, refuse
    - Situation: A Developer broke a definition earlier in its batch, and the unnamed-definition door refused the repair. Sessions asked five times in three sessions whether the repair is allowed.
    - Said: "File writes were always permitted everywhere, just that if there were unexpected changes then the architect is required to sign off." (2026-10-17 16:50, session 0e37e9d7)
    - Means: (reasoned, until confirmed) A door refuses a write only when the file would break. A change outside the prediction goes to the Architect. Rules out a door that refuses a restore because no criterion names the definition.
    - Rule: rota/LAWS.md law 12; rota/DECISIONS.md 2026-10-17; frame 286 for the door
    - Supersedes: none

Frame 115. The questions as sent on 10-04 (A112, A114): "The architect has an answer for the developer and no place to write it. Where does the answer go?" and "The architect answers a developer by pointing at a decision record. May the developer read that record?" Row 15: "Architect's answer to a Developer carries no words; edge gains prose?"

    ### R115. The Architect's answer travels as a finding with a ref; its reasoning stays in the decision record, which the Developer reads by the ref (law 2, before 2026-09-16, rota workflow)
    - Keys: law 2; LAWS.md:112-119; conclusions travel, reasoning stays home; finding, constraint_id, no why column; decision record, ref, follow a ref; answer, architect's answer, answer to the developer, where does the answer go, no place to write, words, prose, edge gains prose, the answer edge from architect to developer, may the developer read; frame 115
    - Situation: The Architect had an answer for a Developer, and the edge carried no text. Sessions asked three times whether the edge gains prose.
    - Said: none in the transcripts, the ruled text is law 2. On the repeat: "we have already discussed this, use a subagent to search our decisions logs" (2026-10-04 14:34, session 419281dc)
    - Means: (reasoned, until confirmed) No message carries prose reasoning. The Developer follows the ref to the decision record. Rules out a prose field on the answer edge.
    - Rule: rota/LAWS.md law 2
    - Supersedes: none

The words "answer", "prose", "words" and "edge gains prose" are the asker's words. The holding session writes them when Roman says "we have already discussed this". Today only the back-fill agent can write them, from page C, which is finding 1.

Frame 204. The questions as sent on 10-12 (rows 59 to 61): "Notes still open at the merge; what happens", "A default shipped unshown; park at the merge?", "Architect review, park at merge, or both".

    ### R204b. The Architect reviews every open note and escalates or resolves it, and an unreviewed note blocks the work (2026-10-12, rota workflow)
    - Keys: frame 204; plans/frame204-design.md; note, notes, seat's note, open notes, non-blocking notes, note kinds, default, defaults, shipped default, unshown default, park, park at the merge, merge, blocks the work, architect review, escalate, resolve
    - Situation: A shipped request left notes open at the merge. Sessions asked nine times in three sessions what the notes are for and who reviews them.
    - Said: "Architect reviews some categories of notes if I don't and escalates or resolves no?" (2026-10-11 15:43, session c81dd240); "Every default" (2026-10-11 15:59, session c81dd240); "yeah but not just defaults, the architect reviews all notes and escalates and thats what blocks the work" (2026-10-12 23:31, session 31e55586)
    - Means: (reasoned, until confirmed) Every note goes to the Architect, not only the defaults. The Architect escalates or resolves it, and an open note blocks the merge.
    - Rule: plans/frame204-design.md
    - Supersedes: R204a, "Every default" (2026-10-11 15:59)

Here the question's words and the answer's words are the same, so a grep hits either way. The `Supersedes:` field carries the change from 10-11 to 10-12, and the search must print it.

## (d) Probes and usage

Probes, all read-only, run from D:/repos/rota at 14c35074:

1. `git rev-parse`, `grep -n` outlines, and `sed` and `awk` reads of the design, review 1, review 2, pages A and C, and frame 287's status lines in `plans/stack.md`.
2. A loop of `grep -ci` over `rota/LAWS.md`, `rota/DECISIONS.md` and `plans/archive/*.md` for 18 question words. Examples, in that order: "answer" 14, 65 and 1,059; "prose" 0, 12 and 122; "restore" 0, 1 and 97; "project file" 0, 0 and 0.
3. A `python -c` probe that joins the whitespace of `rota/LAWS.md` and counts "decision record": 3 joined, 2 by line. The lost hit is law 2, lines 114 and 115.
4. `grep -c` on page A's quote headings gave 219. The "ruled:" counts were 30 in `CLAUDE.md`, 35 in `plans/wall-guide.md`, and about 58 over 40 memory files. `wc -c` gave the source sizes.
5. `git log -1 04325814` and a grep for 04325814 in the stack and `DECISIONS.md`. The key is the door's commit, "fix(desks): a definition no criterion names keeps its source".

Usage: about 75k input tokens and about 12k output tokens, about 87k in total (reasoned: this agent's own count; read the harness line for the true figure).
