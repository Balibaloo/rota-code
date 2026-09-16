# Placement: the Liaison brief under plans/composition.md

Date: 2026-09-16. Source files: `plans/composition.md` (134 lines) and the 19
prompt files in `rota/roles/prompts/liaison/*.md` (601 lines by `wc -l`).
The `.tools` files are wiring and are not placed. Read-only pass. No repo file
was changed.

Notation: `P<n>` is line `n` of `plans/composition.md`. An item id is
`<file>.<k>`, numbered in file order. The `File:line` column gives the lines
the item covers.

## Summary

175 items. 92 PLACES, 67 DETAIL, 13 CONTRADICTS, 3 ORPHAN.

Per file (items: PLACES / DETAIL / CONTRADICTS / ORPHAN):

| File | Items | PLACES | DETAIL | CONTRADICTS | ORPHAN |
|---|---|---|---|---|---|
| base.md | 20 | 9 | 6 | 5 | 0 |
| agenda.md | 10 | 7 | 3 | 0 | 0 |
| answer.md | 10 | 7 | 2 | 0 | 1 |
| answering.md | 7 | 3 | 4 | 0 | 0 |
| awaiting_confirm.md | 3 | 2 | 1 | 0 | 0 |
| blindspot.md | 9 | 4 | 4 | 0 | 1 |
| contradiction.md | 3 | 2 | 1 | 0 | 0 |
| converse.md | 26 | 11 | 13 | 2 | 0 |
| landing.base.md | 5 | 3 | 2 | 0 | 0 |
| landing.md | 13 | 4 | 7 | 2 | 0 |
| observed_entries.md | 5 | 3 | 2 | 0 | 0 |
| quarantined.md | 4 | 2 | 2 | 0 | 0 |
| report.md | 8 | 5 | 3 | 0 | 0 |
| round_close.md | 16 | 9 | 4 | 3 | 0 |
| submit.md | 7 | 5 | 2 | 0 | 0 |
| touch_note.md | 5 | 2 | 3 | 0 | 0 |
| unresolved.md | 6 | 5 | 1 | 0 | 0 |
| verdict.md | 11 | 5 | 4 | 1 | 1 |
| verdict_signoff.md | 7 | 4 | 3 | 0 | 0 |

The 13 contradictions fall into five groups:

1. The three standing laws in `base.md` (items base.2, base.8, base.10). The
   page names them at P131-132. They deny P26-27 (infer, then check), P28-29
   (judges the route) and P29-30 (may originate a question).
2. The model picks the owner of an inquiry (base.14, converse.13,
   converse.15). P31 says the wiring decides. The door already fans one ask
   out to every owner (`rota/core/sandbox.py:1748`, and the case
   `L1-LI-a-question-about-the-program-goes-to-its-owners` expects all three).
   The brief is stale against its own wiring.
3. Silence as consent (landing.9, round_close.14). P75 denies it.
4. The Liaison as the verbatim recorder (base.6, verdict.5). P27 says the
   wiring records the words before the Liaison wakes. `verdict.tools` has no
   entry, segment or confirm tool, so verdict.5 also fails P35.
5. Residue of "never decide" and "never invent" in mode files (landing.3,
   round_close.4, round_close.11).

Three internal findings that the page does not settle but the re-record must
know: `blindspot.md:21-26` shows a worked example that `blindspot.md:29-30`
says the door refuses (a tick id as `about_ref`); `verdict.md:26` names the
modes "signoff" and "harvest", which are `submit` and `round_close`; and
`converse.md:72` already lets the Liaison ask a clarifying question, which
`base.md:21` forbids.

Scope note for the re-record: `landing` composes on `landing.base.md`, not on
`base.md` (`rota/roles/prompts.py:72-83`). A `base.md` change re-records every
Liaison case except the six in `l1_landing.yaml`.

## Placement table

| Item | File:line | Verdict | Page line or section | Proposed change |
|---|---|---|---|---|
| base.1 | base.md:1 | PLACES | P25 "the one seat that faces the Principal" | none |
| base.2 | base.md:3-5 | CONTRADICTS | P26-27 "It infers intent, then checks and clarifies with the Principal"; P28-29 "It judges the route" | Brief: "one of two things: recording what the principal said, or carrying other roles' questions... You never do the third thing... deciding what any of it means. Other roles interpret; you do not." Change B1 |
| base.3 | base.md:7-10 | PLACES | P26 "It carries words both ways" | none |
| base.4 | base.md:10-12 | PLACES | P25 (one seat faces the Principal; roles' talk to each other does not pass through it) | none |
| base.5 | base.md:14 | DETAIL | The parties, Liaison (framing: "Standing law, in force in every mode") | none |
| base.6 | base.md:16 | CONTRADICTS | P27-28 "The wiring records the words verbatim before the Liaison wakes" | Brief heading "Record verbatim." tells the model to record. Case `L1-LI-segment` forbids `entries` writes: "a second entry is the fabrication this cost a session". Change B2 (optional, two words) |
| base.7 | base.md:16-19 | PLACES | P106-107 "The verbatim words and the confirmed reading are two records" (never tidy, summarise or correct) | none |
| base.8 | base.md:21-22 | CONTRADICTS | P29-30 "It may originate a question the Principal did not raise, and the question names the row it is about" | Brief: "Never invent a question. You carry questions that other roles reported. If no role reported a blocker, there is nothing to ask". Change B3 |
| base.9 | base.md:23-24 | DETAIL | Flows P74 "The tool never rules for the Principal" (a vague statement is not the Liaison's to settle) | Rides with B3 ("solve" becomes "settle") |
| base.10 | base.md:26-28 | CONTRADICTS | P26-27 "It infers intent, then checks and clarifies" | Brief: "Never interpret... If you find yourself reasoning about the subject matter rather than about the wording, stop". Change B4 |
| base.11 | base.md:30-31 | PLACES | P48-49 "Conclusions cross a boundary. Reasoning stays where it was made, reachable by a pointer" | none |
| base.12 | base.md:34 | DETAIL | P34-35 "Capability comes from wiring" (heading: what you can reach) | none |
| base.13 | base.md:36-38 | PLACES | P20-21 "They can interrogate any detail through the Liaison" | none |
| base.14 | base.md:38-39 | CONTRADICTS | P31 "The wiring decides whom an inquiry reaches" | Brief: "Send it to the role that owns the answer: `msg.ask_vision_keeper` for scope, `msg.ask_terminologist` for a term, `msg.ask_architect` for the system." The door fans one ask to every owner. Change B5 |
| base.15 | base.md:39-40 | PLACES | P71 "A question changes nothing" (read-only sessions, asking revokes nothing) | none |
| base.16 | base.md:40 | PLACES | P78 "Every claim cites a source" ("Never answer from your own reading") | none. Note: landing.md:16 answers from the page, which is a record the Liaison holds |
| base.17 | base.md:42-43 | DETAIL | P20-21 (`schedule.consult`: only the Principal asks what is next) | none |
| base.18 | base.md:45-47 | DETAIL | P27-28 (`transcript.quote` recovers the verbatim record) | none |
| base.19 | base.md:49-50 | DETAIL | P60-61 "A record's identity derives from its content" (`brief.list` dedupe) | none |
| base.20 | base.md:52-54 | PLACES | P37-38 "Each seat wakes cold, acts once, and ends. Nothing accumulates in a conversation" | none |
| agenda.1 | agenda.md:1 | DETAIL | Records P50-51 (mode line) | none |
| agenda.2 | agenda.md:3-5 | PLACES | P50-51 "Every open obligation stays visible and countable" (one `msg.present_principal` over the ledger rows) | none |
| agenda.3 | agenda.md:7-10 | DETAIL | P30 "the question names the row it is about" (refs are the rows' own ids, not `about_ref`) | none |
| agenda.4 | agenda.md:12-13 | PLACES | P18 "They rule" (approve or contest a line) | none |
| agenda.5 | agenda.md:13 | PLACES | P62 "A ruling is a record" (an approved line becomes a decision) | none |
| agenda.6 | agenda.md:13-14 | DETAIL | P69 "Intent flows down" (a contested line returns to its desk) | none |
| agenda.7 | agenda.md:14-15 | PLACES | P71 "A question changes nothing" (an answer does not close a row) | none |
| agenda.8 | agenda.md:17-18 | PLACES | P23 "Sign-offs after that... are opt-in"; P73 "Only a fact or a ruling gates" | none |
| agenda.9 | agenda.md:18-20 | PLACES | P74-75 "never... closes an assumption"; P50 | none |
| agenda.10 | agenda.md:22 | PLACES | P37 "acts once, and ends" | none |
| answer.1 | answer.md:1 | DETAIL | P70 "Evidence flows up" (mode line) | none |
| answer.2 | answer.md:3-7 | PLACES | P70 "Evidence flows up the same path"; P78 (refs of every row the reply rests on) | none |
| answer.3 | answer.md:9-13 | PLACES | P28-29 "It judges the route: which question next and what to show" (pick and join; drop owners beside the point) | none |
| answer.4 | answer.md:15-19 | ORPHAN | none (history of the relay going out on the question channel) | Keep. A measured failure the brief guards against; CLAUDE.md exempts measured forms in briefs |
| answer.5 | answer.md:21-23 | PLACES | P71 "A question changes nothing" (read-only, nothing revoked) | none |
| answer.6 | answer.md:25-26 | PLACES | P47 "Every record has one writer" (the owner said what it said) | none |
| answer.7 | answer.md:28-31 | PLACES | P28-29 "which question next" (`schedule.reask` instead of relaying a non-answer) | none |
| answer.8 | answer.md:31-34 | PLACES | P21-22 "Their attention is the scarcest budget" (spend the free thing first) | none |
| answer.9 | answer.md:36-38 | DETAIL | P31 (the wiring picks whom `schedule.reask` reaches); P48 (`what_is_missing` in words) | none |
| answer.10 | answer.md:40-42 | PLACES | P13-14 "Honest about where small models stop" (nobody here knows) | none |
| answering.1 | answering.md:1 | DETAIL | P69 (mode line) | none |
| answering.2 | answering.md:3-6 | PLACES | P26 "It carries words both ways" (the Principal's words back to the desk) | none |
| answering.3 | answering.md:8-11 | DETAIL | P69 "Intent flows down: Principal, Liaison, records, seats" (owner lookup by `table`; a candidate for the wiring under P34) | none |
| answering.4 | answering.md:12-17 | DETAIL | P69 (table-to-owner bullets; a lookup, not a judgement) | none |
| answering.5 | answering.md:19-21 | PLACES | P47 "Every record has one writer" (the owner, not the asker); P37 | none |
| answering.6 | answering.md:23-27 | PLACES | P21-22 attention (a second confirm spends it); measured tips5 folded in | none |
| answering.7 | answering.md:29-30 | DETAIL | P37 "acts once" (relay the answer only; the Principal resends a new request) | none. Caution: the untaken request is not surfaced, which is near P50 "Nothing stops quietly". The verbatim words stay in the chat, so no record is lost |
| awaiting_confirm.1 | awaiting_confirm.md:1 | DETAIL | P28 (mode line) | none |
| awaiting_confirm.2 | awaiting_confirm.md:3-4 | PLACES | P28 "The Liaison's confirmed reading is a second record" | none |
| awaiting_confirm.3 | awaiting_confirm.md:6-8 | PLACES | P50 "Nothing stops quietly" (it stalled; put it in front of them) | none |
| blindspot.1 | blindspot.md:1 | DETAIL | P13-14 (mode line) | none |
| blindspot.2 | blindspot.md:3-7 | PLACES | P28-29 "what to show" (the judgement of which gaps the Principal must know) | none |
| blindspot.3 | blindspot.md:9-11 | DETAIL | P40-43 (the structure's model of the project, observed from the code; `surveys.consult`) | none |
| blindspot.4 | blindspot.md:13-16 | PLACES | P28-29 "what to show" (weigh each fact by what it hides) | none |
| blindspot.5 | blindspot.md:18-19 | DETAIL | P29-30 (the Liaison originates a row; `ledger.log`) | Says `about_table="items"`; blindspot.7 says `model_areas`. Change S1 aligns them (optional) |
| blindspot.6 | blindspot.md:21-26 | ORPHAN | none | Delete. The example's `about_ref` is a tick id; blindspot.md:29-30 says a tick names no row and the door refuses it. Change S1 |
| blindspot.7 | blindspot.md:28-30 | PLACES | P30 "the question names the row it is about" (an area row; a tick or counter names no row) | none |
| blindspot.8 | blindspot.md:32-35 | PLACES | P13-14 "Honest about where small models stop" (say the actual thing) | none |
| blindspot.9 | blindspot.md:37-39 | DETAIL | P50-51 (the obligation is discharged visibly: `surveys.attest`) | none |
| contradiction.1 | contradiction.md:1 | DETAIL | P74 (mode line) | none |
| contradiction.2 | contradiction.md:3-5 | PLACES | P74 "It never settles a conflict"; P18 "They rule" | none |
| contradiction.3 | contradiction.md:7-10 | PLACES | P74 "never settles a conflict" (do not rank or say which you think they meant) | none. P26 lets the Liaison infer and check, but a reading of which of two rulings stands is settling a conflict |
| converse.1 | converse.md:1 | PLACES | P26 "It infers intent" (did they ask for anything?) | none |
| converse.2 | converse.md:2 | DETAIL | P26-28 (`brief.intake` verdict work or chat is the reading) | none |
| converse.3 | converse.md:4-6 | PLACES | P27-28 "The wiring records the words verbatim before the Liaison wakes" | none |
| converse.4 | converse.md:8-11 | DETAIL | P57 "A seat restarts from records" (`recent_chat` is history from records) | none |
| converse.5 | converse.md:13-14 | PLACES | P26 "It infers intent" (decide what the current message is) | none |
| converse.6 | converse.md:16-18 | DETAIL | P26 (test 1: work) | none |
| converse.7 | converse.md:19-21 | DETAIL | P20-21 "interrogate any detail through the Liaison" (test 2: a question) | none |
| converse.8 | converse.md:22 | DETAIL | P26 (test 3: chat) | none |
| converse.9 | converse.md:24-27 | DETAIL | P26 (order of the tests; work is told, a question is asked) | none |
| converse.10 | converse.md:29-31 | DETAIL | P26 (a leading greeting is not a category) | none. `tests/rota/test_prompts.py:104-108` asserts the words "leading greeting", "work request", "ignore the greeting". Keep them |
| converse.11 | converse.md:33-35 | DETAIL | P26 "carries words both ways"; P37 (chat: one `msg.converse_principal`) | none |
| converse.12 | converse.md:37-41 | PLACES | P78 "Every claim cites a source"; P20-21 (you do not know it and you do not guess it) | none |
| converse.13 | converse.md:41-42 | CONTRADICTS | P31 "The wiring decides whom an inquiry reaches" | Brief: "Route it, with one ask per owner that could hold part of it". Change C1 |
| converse.14 | converse.md:44-49 | DETAIL | P31 (what each owner holds; harmless once C1 removes the choice) | none |
| converse.15 | converse.md:51-52 | CONTRADICTS | P31 "The wiring decides whom an inquiry reaches" | Brief: "Ask every owner that might hold part of the answer, not just the likeliest one." The model is told to judge who holds it. Change C2 |
| converse.16 | converse.md:52-54 | PLACES | P71 "A question changes nothing" (read-only; nothing here to confirm) | none |
| converse.17 | converse.md:56-60 | PLACES | P28 "The Liaison's confirmed reading is a second record" (cut at principal granularity) | none |
| converse.18 | converse.md:61-65 | DETAIL | P28 (examples of one and two statements) | none |
| converse.19 | converse.md:67-70 | PLACES | P37 "acts once, and ends" (never two of the three in one session) | none |
| converse.20 | converse.md:72-73 | PLACES | P26-27 "checks and clarifies with the Principal" (`msg.clarify_principal` when ambiguous) | none. This line already permits a Liaison-originated question, against base.md:21. P30 wants the question to name its row: pass `refs=[entry_id]` if the door accepts empty refs today |
| converse.21 | converse.md:73-77 | PLACES | P74 "never rules for the Principal" (what a vague request should mean is not yours to settle) | none |
| converse.22 | converse.md:79-82 | DETAIL | P27-28; P60 (statement text exactly; spans into the entry) | none |
| converse.23 | converse.md:84 | PLACES | P28 "confirmed reading is a second record" (one `msg.confirm_principal`) | none |
| converse.24 | converse.md:86-99 | DETAIL | P26-28 (worked examples e_m1 to e_m3) | none |
| converse.25 | converse.md:101-103 | DETAIL | P31 (example e_m4: one ask; the door fans it out) | none. Consistent with C1 |
| converse.26 | converse.md:105 | PLACES | P37 "acts once" | none |
| landing.base.1 | landing.base.md:1 | PLACES | P25 "the one seat that faces the Principal" | none |
| landing.base.2 | landing.base.md:3-4 | PLACES | P62-63 "The Principal rules, the Liaison writes it" | none |
| landing.base.3 | landing.base.md:5-7 | DETAIL | P62-63; P27 (the wiring recorded the words; do not record them again) | none. "do not check them with anyone" means other roles; landing.md:14-21 still checks with the Principal by `ask` |
| landing.base.4 | landing.base.md:9-11 | DETAIL | P62-63 (`rulings.rule`, or `ask` one sentence) | none |
| landing.base.5 | landing.base.md:13-14 | PLACES | P37-38 "wakes cold, acts once, and ends" | none |
| landing.1 | landing.md:1 | DETAIL | P62 (mode line) | none |
| landing.2 | landing.md:3-4 | DETAIL | P62-63 (`landing` holds the page, the lines, the reply) | none |
| landing.3 | landing.md:4-7 | CONTRADICTS | P26 "It infers intent" (in every mode) | Brief: "In this mode, and only here, you read the words for what they rule. The standing law 'other roles interpret' does not apply". "Only here" denies inference elsewhere, and the law it excepts is one the page drops. Change L1 |
| landing.4 | landing.md:7-8 | PLACES | P62-63 (write the decision down, line by line); P27 (do not record the reply again) | none |
| landing.5 | landing.md:10-12 | DETAIL | P62-63 (`rulings` map approve, contest, revise, plus `words`; or `ask`) | none |
| landing.6 | landing.md:14-17 | PLACES | P71 "A question changes nothing" ("A question rules nothing"); P20-21 (answer from the page) | none |
| landing.7 | landing.md:17-21 | PLACES | P26-27 "infers intent, then checks and clarifies with the Principal" (say which lines you read as approved and ask if that is right) | none. This is the page's Liaison in full |
| landing.8 | landing.md:23 | DETAIL | P62-63 (otherwise the reply is a ruling) | none |
| landing.9 | landing.md:25-26 | CONTRADICTS | P75 "never... treats silence as consent" | Brief: "The reply agrees, or says nothing against the line: `approve`." A line the reply says nothing about is approved. Case `L1-LI-approve-one-line-only-approves-that-line-alone` (3/5) forbids approving the unmentioned lines. Change L2 |
| landing.10 | landing.md:27-30 | DETAIL | P62-63 (contest rules) | none. Caution: "contests line 3 and approves the others" reads a whole-page reply with one exception; case `L1-LI-a-named-line-is-contested-and-the-rest-approved` pins it |
| landing.11 | landing.md:31-32 | DETAIL | P62-63 (`revise`) | none |
| landing.12 | landing.md:34-35 | DETAIL | P62-63 (a correction counts against its line only; every line gets a ruling) | none |
| landing.13 | landing.md:37-39 | PLACES | P62-63 "A ruling is a record"; P69 (the owner of a contested line hears the words); P37 | none |
| observed_entries.1 | observed_entries.md:1 | DETAIL | P58-59 (mode line) | none |
| observed_entries.2 | observed_entries.md:3-5 | PLACES | P58-59 "A record says whether it was observed from the code or the world, or decided by the Principal" | none |
| observed_entries.3 | observed_entries.md:7-8 | DETAIL | P30; P37 (one `msg.present_principal`, every id in the wake's refs) | none |
| observed_entries.4 | observed_entries.md:9-12 | PLACES | P58-59; P18 "They rule" (observations awaiting a first decision) | none |
| observed_entries.5 | observed_entries.md:14-16 | PLACES | P21-22 "Their attention is the scarcest budget" (one page, not eleven; measured tipsK) | none |
| quarantined.1 | quarantined.md:1 | DETAIL | P50 (mode line) | none |
| quarantined.2 | quarantined.md:3-6 | DETAIL | P50-51 (the mechanism that set the message aside) | none |
| quarantined.3 | quarantined.md:8-10 | PLACES | P20 "strategic altitude" (name the stalled work, not the mechanism); P50 | none |
| quarantined.4 | quarantined.md:12-14 | PLACES | P9 "no work stays invisible"; P52-53 "Outstanding work is re-derived from the records each pass" | none |
| report.1 | report.md:1 | DETAIL | P70 (mode line) | none |
| report.2 | report.md:3-5 | PLACES | P18 "They rule" (the only step left is a person); P70 | none |
| report.3 | report.md:7-9 | DETAIL | P83-85 The ceiling (the attempt bound is the loop); P37 | none |
| report.4 | report.md:11-14 | PLACES | P48-49 "Conclusions cross a boundary. Reasoning stays where it was made" (a report is refs) | none |
| report.5 | report.md:16-19 | PLACES | P20 "strategic altitude"; P28-29 "what to show" (translate out of the roles' vocabulary) | none. Translation is interpretation; the page permits it, base.md:26 forbids it (fixed by B4) |
| report.6 | report.md:21-22 | PLACES | P74 "never settles a conflict" (put the choice to the Principal); P28-29 | none |
| report.7 | report.md:24 | DETAIL | P30 (one `msg.clarify_principal` with the report's refs) | none |
| report.8 | report.md:26-33 | PLACES | P62 "A ruling is a record" (the answer is on file); P21-22 attention (measured tipsG) | none |
| round_close.1 | round_close.md:1 | DETAIL | P54 (mode line) | none |
| round_close.2 | round_close.md:3-5 | DETAIL | P21-22; P54 (the round waits so dedupe is possible) | none |
| round_close.3 | round_close.md:7-10 | DETAIL | P33-34 "The structure... decides what happens next" (finished is a lookup; settled reports never reach you) | none |
| round_close.4 | round_close.md:10 | CONTRADICTS | P28-29 "It judges the route" | Brief: "and decisions are not yours." A blanket denial; the page names "never decide" at P131-132. Change R1 (optional, low weight) |
| round_close.5 | round_close.md:10-11 | DETAIL | P54 (what you have is the round's business) | none |
| round_close.6 | round_close.md:13-18 | PLACES | P54 "The unit per pass is a question"; P30 (the shared ref makes two reports one question) | none |
| round_close.7 | round_close.md:20-21 | PLACES | P28-29 "which question next and what to show" | none |
| round_close.8 | round_close.md:23-24 | PLACES | P28-29 "which question next"; P21 (at most two questions, the most unblocking first) | none |
| round_close.9 | round_close.md:25-27 | PLACES | P20 "strategic altitude" (translate) | none |
| round_close.10 | round_close.md:27-30 | PLACES | P30 "the question names the row it is about" (their own words, not a report id) | none |
| round_close.11 | round_close.md:30-32 | CONTRADICTS | P29-30 "It may originate a question the Principal did not raise, and the question names the row it is about" | Brief: "if no report raised it, you invented it, so delete it." Change R2 |
| round_close.12 | round_close.md:34-37 | PLACES | P28-29 "what to show"; P48 (organise, do not summarise; every conclusion keeps its refs) | none |
| round_close.13 | round_close.md:39-41 | PLACES | P28-29 "which question next"; P26-27 (reframe: decompose into smaller choices) | none |
| round_close.14 | round_close.md:40-41 | CONTRADICTS | P75 "never... treats silence as consent" | Brief: "put a concrete default to them that they can veto." A veto-able default stands unless they object. Change R3 (one word) |
| round_close.15 | round_close.md:41-42 | PLACES | P21-22 attention (do not repeat a failed question) | none |
| round_close.16 | round_close.md:44-46 | PLACES | P21-22 "Their attention is the scarcest budget" (do not manufacture something to say) | none |
| submit.1 | submit.md:1 | DETAIL | P22-23 (mode line) | none |
| submit.2 | submit.md:3-5 | PLACES | P22 "Approval of intent is required before work starts" (one document, read whole) | none |
| submit.3 | submit.md:7-10 | PLACES | P50-51; P74-75 "closes an assumption" (open assumptions travel with their items) | none |
| submit.4 | submit.md:12-13 | PLACES | P75 "never... treats silence as consent" (disclosure is not ratification) | none |
| submit.5 | submit.md:15-21 | PLACES | P28-29 "which question next and what to show"; P21 (the assumption that changes the most goes first) | none |
| submit.6 | submit.md:23-27 | PLACES | P9 "no work stays invisible"; P18 (uncovered statements beside the items) | none |
| submit.7 | submit.md:29-30 | DETAIL | P30; P37 (one `msg.present_principal` with every ref) | none |
| touch_note.1 | touch_note.md:1 | DETAIL | P20 (mode line) | none |
| touch_note.2 | touch_note.md:3-7 | DETAIL | P73 "A prediction never blocks"; P40-43 (the Architect's predicted touch) | none |
| touch_note.3 | touch_note.md:9-13 | DETAIL | P30 (the two ids on the `Refs:` line); P27 (read out as words, not retyped) | none |
| touch_note.4 | touch_note.md:15-19 | PLACES | P73 "A prediction never blocks. Only a fact or a ruling gates"; P23 opt-in | none |
| touch_note.5 | touch_note.md:21 | PLACES | P37 "acts once" | none |
| unresolved.1 | unresolved.md:1 | DETAIL | P70 (mode line) | none |
| unresolved.2 | unresolved.md:3-6 | PLACES | P50-51 "Every open obligation stays visible... until something discharges it" | none |
| unresolved.3 | unresolved.md:8-11 | PLACES | P21-22 attention; P28-29 (worth their attention because the roles already tried) | none |
| unresolved.4 | unresolved.md:13-16 | PLACES | P30 "the question names the row it is about"; P20 (their words, not a message id) | none |
| unresolved.5 | unresolved.md:18-20 | PLACES | P28-29 "what to show" (translate the note, not the failed original) | none |
| unresolved.6 | unresolved.md:22-24 | PLACES | P74 "never settles a conflict"; P18 (let them rule on the disagreement) | none |
| verdict.1 | verdict.md:1 | DETAIL | P62-63 (mode line) | none |
| verdict.2 | verdict.md:3 | DETAIL | P62-63 (two steps) | none |
| verdict.3 | verdict.md:5-6 | PLACES | P28 "confirmed reading is a second record"; P62-63 (`brief.ratify`) | none |
| verdict.4 | verdict.md:8-9 | PLACES | P60-61 "A record's identity derives from its content" (never mutated in place) | none |
| verdict.5 | verdict.md:9-10 | CONTRADICTS | P27 "The wiring records the words verbatim before the Liaison wakes"; P35 "No brief grants what is not wired" | Brief: "Append it as a new entry, segment it into replacement statements, and confirm those." `verdict.tools` has no entry, segment or confirm tool; case `L1-LI-ratify` forbids `entries` writes. Change V1 |
| verdict.6 | verdict.md:10-12 | PLACES | P27-28 verbatim record; P60 (the original stays, superseded) | none |
| verdict.7 | verdict.md:14-19 | DETAIL | P69 "Intent flows down: Principal, Liaison, records, seats" (deliver to all three) | none |
| verdict.8 | verdict.md:21-23 | PLACES | P31 (analogue: the wiring, not the Liaison, decides whom it reaches; broadcast to all three) | none |
| verdict.9 | verdict.md:25-26 | DETAIL | P37 (not presenting or asking in this mode) | none |
| verdict.10 | verdict.md:26-27 | ORPHAN | none | Reword or delete. "signoff" and "harvest" are not Liaison modes; the files are `submit` and `round_close`. Change V2 (optional) |
| verdict.11 | verdict.md:29-31 | PLACES | P69 (ratified intent flows down; the check happened at confirm); P71 | none |
| verdict_signoff.1 | verdict_signoff.md:1 | DETAIL | P62 (mode line) | none |
| verdict_signoff.2 | verdict_signoff.md:3-8 | DETAIL | P69 (owner lookup by table; a candidate for the wiring under P34) | none |
| verdict_signoff.3 | verdict_signoff.md:10-13 | DETAIL | P69 (the table is the owner; other tables have no relay) | none |
| verdict_signoff.4 | verdict_signoff.md:13-15 | PLACES | P48-49 "Conclusions cross a boundary... reachable by a pointer" (ids alone, never the resolved row); P37 | none |
| verdict_signoff.5 | verdict_signoff.md:17-19 | PLACES | P47 "Every record has one writer" (you do not apply the ruling; approval is the owners' artefact) | none |
| verdict_signoff.6 | verdict_signoff.md:19-21 | PLACES | P62-63 "A ruling is a record" (the reading was written at landing; here it is carried); P69 | none |
| verdict_signoff.7 | verdict_signoff.md:23 | PLACES | P37 "acts once" | none |

## Proposed brief changes

Old text -> new text, per file. Required changes remove a contradiction with
the page. Optional changes fix an internal fault or a stale name. Every
change re-records the cases in "Cases touched".

### base.md

B1 (required), lines 3-5:

Old:
> Everything you do is one of two things: **recording what the principal said**, or **carrying other roles' questions to them**. You never do the third thing that looks tempting — deciding what any of it means. Other roles interpret; you do not.

New:
> Everything you do is one of two things: **reading what the principal means, then checking that reading with them**, or **carrying questions to them and their answers back**. You never do the third thing that looks tempting — ruling in their place. The principal rules; you do not.

B2 (optional), line 16:

Old:
> **Record verbatim.** The transcript is the one un-interpreted thing in the system.

New:
> **The words stay verbatim.** The transcript is the one un-interpreted thing in the system.

B3 (required), lines 21-24:

Old:
> **Never invent a question.** You carry questions that other roles reported. If no role reported a blocker, there is nothing to ask, however vague the principal was being. A vague statement is not your problem to solve; it is Vision Keeper's or Terminologist's to report on.

New:
> **Every question names its row.** You carry questions that other roles reported, and you may raise one of your own. A question that names no row is nothing to ask, however vague the principal was being. What a vague statement means is not yours to settle; it is Vision Keeper's or Terminologist's to report on.

B4 (required), lines 26-28:

Old:
> **Never interpret.** You do not decide what a term means, what is in scope, or whether something is feasible. If you find yourself reasoning about the subject matter rather than about the wording, stop — that thought belongs to another role.

New:
> **Infer, then check.** You read what the principal means, and you check that reading with them before it stands. You do not settle what a term means, what is in scope, or whether something is feasible — those belong to another role.

B5 (required), lines 38-39:

Old:
> Send it to the role that owns the answer: `msg.ask_vision_keeper` for scope, `msg.ask_terminologist` for a term, `msg.ask_architect` for the system.

New:
> Send it with one ask — `msg.ask_vision_keeper`, `msg.ask_terminologist` or `msg.ask_architect`; the wiring carries it to every owner.

Note on B5: the door already does this (`rota/core/sandbox.py:1748`, note
"asked every owner"). The brief change describes the wiring. It does not add
capability.

### converse.md

C1 (required), lines 41-42:

Old:
> Route it, with one ask per owner that could hold part of it:

New:
> Route it with one ask; the wiring carries it to every owner. The owners are:

C2 (required), lines 51-52:

Old:
> Ask **every** owner that might hold part of the answer, not just the likeliest one. An owner whose artefact does not carry it says so, and that costs nothing:

New:
> One ask reaches **every** owner; you do not pick the likeliest one. An owner whose artefact does not carry it says so, and that costs nothing:

Do not touch lines 29-31. `tests/rota/test_prompts.py:104-108` asserts the
words "leading greeting", "work request" and "ignore the greeting".

### landing.md

L1 (required), lines 4-7:

Old:
> In this mode, and only here, you read the words for what they rule. The standing law "other roles interpret" does not apply: nobody but you saw the page, and the principal has decided. Your job is to write the decision down, line by line.

New:
> You read the words for what they rule: nobody but you saw the page, and the principal has decided. Your job is to write the decision down, line by line.

L2 (required), lines 25-26:

Old:
> - The reply agrees, or says nothing against the line: `approve`. "ok", "yes", "looks right", "fine, go ahead", "approved" approve every line.

New:
> - The reply agrees with the line, or with the page as a whole: `approve`. "ok", "yes", "looks right", "fine, go ahead", "approved" approve every line.

Note on L2: line 28 ("A reply that says line 3 is wrong contests line 3 and
approves the others") stays. It reads a whole-page reply with one exception,
and case `L1-LI-a-named-line-is-contested-and-the-rest-approved` pins it. A
reply of "approve 1 only" agrees with neither line 2 nor the page as a whole,
which is what `L1-LI-approve-one-line-only-approves-that-line-alone` needs.

### round_close.md

R1 (optional), line 10:

Old:
> because whether a role has finished is a lookup and not a decision, and decisions are not yours.

New:
> because whether a role has finished is a lookup and not a decision, and the wiring does the lookup.

R2 (required), lines 30-32:

Old:
> Checking you can point at the report that raised it is how you know the question is real, not what you send: if no report raised it, you invented it, so delete it.

New:
> Checking you can point at the row it is about is how you know the question is real, not what you send: if it names no row, delete it.

R3 (required), lines 40-41:

Old:
> or put a concrete default to them that they can veto.

New:
> or put a concrete default to them to approve or contest.

### verdict.md

V1 (required), lines 8-12:

Old:
> **Reworded statements are not edited.** A statement is never mutated in place — the principal's rewording is *new material*. Append it as a new entry, segment it into replacement statements, and confirm those. The original stays exactly as it was, superseded rather than overwritten, because the record of what they first said is the thing the transcript exists to protect.

New:
> **Reworded statements are not edited.** A statement is never mutated in place — the principal's rewording is *new material*. The wiring has already recorded it, and the ruling on that line is `revise`. The original stays exactly as it was, superseded rather than overwritten, because the record of what they first said is the thing the transcript exists to protect.

Note on V1: check that the verdict wake shows the `revise` words to the
Liaison before the re-record. If it does not, the sentence "and the ruling on
that line is `revise`" is a claim the model cannot check, and the door owns
the fix.

V2 (optional), lines 26-27:

Old:
> Presenting belongs to signoff and clarifying to harvest; reaching for either here means you have mistaken which mode you are in.

New:
> Presenting belongs to `submit` and clarifying to `round_close`; reaching for either here means you have mistaken which mode you are in.

### blindspot.md

S1 (optional), lines 18-26:

Old:
> For each gap that matters, one entry, `ledger.log(about_ref=<the path or subject>, about_table="items", assumption=...)`. Written out, an entry from a real run reads:
> (example block, lines 22-26, whose `about_ref` is a tick id)

New:
> For each gap that matters, one entry with `ledger.log`.

Reason: lines 28-30 give the shape (`about_ref="@<area>"`,
`about_table="model_areas"`) and say a tick names no row and is refused. The
example names a tick and the header names a different table.

### Files with no proposed change

agenda.md, answer.md, answering.md, awaiting_confirm.md, contradiction.md,
landing.base.md, observed_entries.md, quarantined.md, report.md, submit.md,
touch_note.md, unresolved.md, verdict_signoff.md.

## Cases that exercise the Liaison

Case files (from `grep -il liaison tests/rota/cases/*.yaml`) with the mode
each Liaison wake uses. The mode comes from `prompt:`, `tick:`, or the inbound
verb.

| Case file | Case id | Mode |
|---|---|---|
| g1_segments.yaml | G1-scope-sounding-words-are-not-scope-yet | converse, then tick awaiting_confirm |
| g1_segments.yaml | G1-an-owners-answer-reaches-the-seat | answer |
| g1_segments.yaml | G1-what-the-brief-already-holds-is-answered-from-it | converse |
| g1_segments.yaml | G1-a-reply-that-answers-something-else-ratifies-nothing | converse |
| l1_answering.yaml | L1-LI-a-reply-reaches-the-desk-that-asked | answering |
| l1_answers.yaml | L1-LI-put-the-open-assumptions-to-a-present-principal | agenda |
| l1_answers.yaml | L1-LI-relay-an-answer-without-improving-it | answer |
| l1_exhausted.yaml | L2-LI-carry-the-block-to-the-principal | report |
| l1_landing.yaml | L1-LI-plain-agreement-approves-every-line | landing |
| l1_landing.yaml | L1-LI-a-named-line-is-contested-and-the-rest-approved | landing |
| l1_landing.yaml | L1-LI-a-correction-in-a-sentence-contests-the-line-it-is-about | landing |
| l1_landing.yaml | L1-LI-a-question-about-the-page-is-answered-not-ruled | landing |
| l1_landing.yaml | L1-LI-a-question-then-a-statement-at-the-confirm-is-the-question | landing |
| l1_landing.yaml | L1-LI-approve-one-line-only-approves-that-line-alone | landing |
| l1_liaison.yaml | L1-LI-chat-is-not-work | converse |
| l1_liaison.yaml | L1-LI-segment | converse |
| l1_liaison.yaml | L1-LI-ratify | verdict |
| l1_liaison.yaml | L1-LI-present-for-signoff | submit |
| l1_liaison.yaml | L1-LI-present-carries-the-uncovered-statement | submit |
| l1_liaison.yaml | L1-LI-no-report-no-question | converse |
| l1_liaison2.yaml | L1-LI-put-a-contradiction-back-unresolved | contradiction |
| l1_liaison2.yaml | L1-LI-ask-for-the-confirmation-nobody-asked-for | awaiting_confirm |
| l1_liaison2.yaml | L1-LI-relay-a-ruling-without-interpreting-it | verdict_signoff |
| l1_liaison2.yaml | L1-LI-two-questions-at-most-from-three-reports | round_close |
| l1_liaison2.yaml | L1-LI-surface-a-quarantined-message | quarantined |
| l1_liaison2.yaml | L1-LI-present-what-onboarding-only-observed | observed_entries |
| l1_liaison2.yaml | L1-LI-a-question-about-the-program-goes-to-its-owners | converse |
| l1_liaison2.yaml | L1-LI-a-ruling-splits-by-owner | verdict_signoff |
| l1_liaison2.yaml | L1-LI-present-the-touch | touch_note |
| l1_survey.yaml | L1-LI-say-what-the-run-could-not-see | blindspot |
| l1_unresolved.yaml | L1-LI-a-question-the-roles-could-not-answer | unresolved |
| l3_handoffs.yaml | L3-ratified-statement-becomes-scope | verdict (first leg) |
| l3_handoffs.yaml | L3-ratified-statement-becomes-a-term | verdict (first leg) |
| l3_handoffs.yaml | L3-a-maintainers-question-reaches-the-owner | converse (first leg) |

The other case files that match the grep (l1_architect, l1_gatekeeper,
l1_gatekeeper2, l1_generators, l1_judgement, l1_researcher, l1_terminologist,
l1_tester, l1_touch) name the Liaison only as a message sender or recipient.
They wake another role.

Python tests that wake a Liaison prompt with a model:

| Test file | Test | Mode |
|---|---|---|
| test_t1_liaison.py | test_i1_segmentation_at_principal_granularity | converse |
| test_t1_liaison.py | test_i3_harvest_dedupes_and_traces | report |
| test_t1_liaison.py | test_i6_no_reports_means_no_questions | verdict |
| test_t1_liaison.py | test_i4_readonly_writes_nothing_and_bumps_nothing | answer |

Python tests that compose or build a Liaison prompt without a model. They
break on text or tool-list changes, not on model behaviour:

- `test_prompts.py`: `test_compose_includes_base_and_piece` asserts "You are
  Liaison" and "MODE: converse". `test_liaison_converse_prompt_prioritizes_work_over_greeting`
  asserts "leading greeting", "work request", "ignore the greeting" in the
  composed converse prompt. `test_liaison_has_a_piece_per_inbound_verb` needs
  a `.md` per inbound verb.
- `test_intake_fork.py`: builds converse and answer sandboxes from the mode
  tool lists.
- `test_principal_reply.py`: builds landing from the mode tool list.
- `test_signoff_assumptions.py`: wakes submit.
- `test_touch_note.py`: the touch_note predicate.

The remaining 40 `.py` files that match the grep name the Liaison as a
message endpoint in fixtures. They do not compose its brief.

## Cases touched, per changed prompt file

| Changed file | Changes | Cases to re-record |
|---|---|---|
| base.md | B1-B5 | Every Liaison case except `l1_landing.yaml`: g1_segments.yaml (4), l1_answering.yaml (1), l1_answers.yaml (2), l1_exhausted.yaml (1), l1_liaison.yaml (6), l1_liaison2.yaml (9), l1_survey.yaml (1), l1_unresolved.yaml (1), l3_handoffs.yaml (3 first legs); test_t1_liaison.py (4 tests). Keep line 1 for test_prompts.py |
| converse.md | C1, C2 | g1_segments.yaml: G1-scope-sounding-words-are-not-scope-yet, G1-what-the-brief-already-holds-is-answered-from-it, G1-a-reply-that-answers-something-else-ratifies-nothing; l1_liaison.yaml: L1-LI-chat-is-not-work, L1-LI-segment, L1-LI-no-report-no-question; l1_liaison2.yaml: L1-LI-a-question-about-the-program-goes-to-its-owners; l3_handoffs.yaml: L3-a-maintainers-question-reaches-the-owner; test_t1_liaison.py I1. test_prompts.py text assertions stay green if lines 29-31 stay |
| landing.md | L1, L2 | l1_landing.yaml (6 cases). test_principal_reply.py reads the tool list only |
| round_close.md | R1-R3 | l1_liaison2.yaml: L1-LI-two-questions-at-most-from-three-reports |
| verdict.md | V1, V2 | l1_liaison.yaml: L1-LI-ratify; l3_handoffs.yaml: L3-ratified-statement-becomes-scope, L3-ratified-statement-becomes-a-term; test_t1_liaison.py I6 |
| blindspot.md | S1 | l1_survey.yaml: L1-LI-say-what-the-run-could-not-see |

The base.md changes dominate the re-record. B1, B3 and B4 are the misfits the
page names, so the base.md re-record happens in any case. B2 and B5 ride in
the same re-record at no extra cost.
