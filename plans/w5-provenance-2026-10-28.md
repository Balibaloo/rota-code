# W5 of night 173, the provenance read

Meta workflow, read on 2026-10-28 by the rule of 2026-10-18, provenance before a fix. Sources: the code at 4df513f5, `git log`, `.rota/clickI_night173.db` opened `?mode=ro`, `plans/w5-w10-count-2026-10-28.md`, `plans/facts-2026-10-27.md` and `plans/stack.md`. No code was edited. No fix is proposed.

**The result.** Two rules meet, and each is correct alone.

1. The page lands on a thread of its own, so the harvest never sees it. The `round_close` wake names its thread, `t_p1`, in its refs. `trigger_message` (`rota/core/runner.py` 1960-1974) takes a ref as the trigger only when the ref is a message id. No message has the id `t_p1`, so the trigger is None. The page's `cause_id` is the trigger (`rota/core/sandbox.py` 4873), and `_thread_of` (`rota/core/db.py` 811-840) gives a message with no cause its own id as its thread. So `harvested` in `tick_round_close` stays 0 (observed: m78, m82, m86 hold `cause_id` None and `thread_id` equal to their own id. Reasoned: the three functions).
2. The report m71 can never settle. Its refs are `format_filename`, a `glossary_terms` row, and `s3`, a ratified statement. `report_is_settled` (`rota/core/scheduler.py` 124-171) reads only items and statements, and returns False for every other row: "A glossary sense, a constraint, a criterion: real rows with no terminal marker of this kind. Unsettled". At the night's end `format_filename` has provenance `decided` and `s3` is `ratified` (observed: `term_provenance`, `statements`). So no ruling and no relay can settle m71 (reasoned).

The wake's thread name is a property of the night driver. The walk writes every message of his into one thread, `t_p1`, that names no message: `probes/walk.py` 50 and 279, `probes/seat.py` 47 and 138, `probes/agent_principal.py` 385, `rota/testkit/scenes.py` 284 (observed). The TUI writes `thread_id` equal to the message id, `rota/tools/talk.py` 80-84 (observed). At the TUI the wake's ref is a message id, so the page joins the round's thread and the harvest counts it (reasoned: `trigger_message` and `_thread_of`). This difference between the driver and the TUI is not in the records.

## 1. The wake

**What raises it.** `tick_round_close`, `rota/core/scheduler.py` 184-225, through the predicate `round_close`, `rota/core/predicates.py` 579-583, band `gate`. For each thread that holds a Liaison `deliver`, it wakes the Liaison when three things are true (observed: the code):

- No message on the thread is `open` with `to_role != 'liaison'`.
- No Liaison `clarify` or `present` is on the thread (`harvested` is 0).
- `open_reports(conn, thread)` is not empty.

**What "1 report(s)" counts.** `len(open_reports(...))`. `open_reports`, scheduler.py 174-181, returns each `report` on the thread for which `report_is_settled` is False. On night 173 the thread `t_p1` holds five reports, m47, m48, m49, m71 and m72 (observed: `messages`). The refs of m47, m48 and m72 are `s1` or `s3`, and of m49 `s2`. Each is a ratified statement, so each is settled (reasoned: `report_is_settled`). The one report counted is m71 (observed: the wake's input in s224 turn 1 lists only m71).

**What closes a round.** No call closes a round. The round stops waking in one of two ways (observed: the code):

- A Liaison `clarify` or `present` lands on the thread of the round.
- Every report on the thread becomes settled.

A session that ends with no message leaves the round open, and the wake fires again. The quarantine at 3 attempts is the only limit (observed: `tick_attempts` row `liaison|tick:round_close|t_p1`, attempts 3, quarantined 1).

**Provenance.**

- 210649a7, 2026-08-09, "feat(scheduler): schema, atomic session commit, scheduler and boot", is the first commit of the tick and of `harvested` (observed: `git log -L184,225`).
- c7d45089, 2026-08-13, "fix(roles): Liaison was being asked to decide, and punished for it", added `report_is_settled` and `open_reports`. Its message names the livelock: "harvested counted Liaison's own messages, so a correctly silent round was never marked harvested and round_close fired on it forever" (observed). The fix stopped the wake for a round with all reports settled. It kept the rule that a round with one unsettled report closes only by a Liaison message on the thread (reasoned).
- 612aced8 and 35a61dad renamed words only (observed).
- d3508220, 2026-08-26, "fix(sandbox): the ladder that catches a non-answer had never run", wrote `_thread_of` as it is now. Its docstring names "`round_close`'s harvest" as a reader keyed on `thread_id` (observed: db.py 827-829).

**Design intent.** The tick's docstring: "A round exists for one reason: dedupe. Two roles reporting the same blocker in different vocabulary must become one question, which is impossible if Liaison wakes per report. Waiting is the feature." No frame or ruling in `plans/` names the tick (observed: the stack search in section 6). The commits name no frame (observed).

## 2. The page

**The page is the only route that the mode gives.** `rota/roles/prompts/liaison/round_close.tools` holds `ledger.list`, `msg.present_principal`, `msg.clarify_principal`, `brief.list`, `schedule.consult` and `transcript.quote` (observed). No call closes the round. The prompt says "Every report in front of you is still asking for something" and "If something needs a ruling: turn it into at most two questions and send one `msg.clarify_principal`" (observed: `round_close.md`). The wiring tells the seat that m71 asks for something, so a clarify is the prompt's own answer (reasoned).

**The seat did not try a close, and nothing refused its page.** Each of s216, s220 and s224 called `brief.list`, `ledger.list`, `schedule.consult`, then `msg.clarify_principal(refs=["format_filename", "s3"], ...)` (observed: `tool_calls`). Each session ran one turn, and the clarify landed (observed: `turns`, `messages`).

**Why the question repeats.** Three observations.

1. The round wake shows no earlier page and no reply. `_resolve_round`, runner.py 3807-3845, gives `thread`, `reports`, `about` and `resolved_refs` (observed: the code, and s224 turn 1 holds none of m78, m79, m82, m83). The report wake has a block for this, runner.py 2276-2300: "What the principal has already said about these rows. A report about a row the principal answered once is not a new question" (observed). The round wake has no such block (observed).
2. The retry note tells the seat to change its answer. s224 turn 1 opens with "3 of 3 on this wake. The earlier attempt did not clear this wake, so the same answer will not clear it. Do something the earlier attempt did not" (observed: runner.py 915-921). The seat had one route, so it changed the words (reasoned).
3. Both repeat doors match the same words only. The door at sandbox.py 3791-3812 compares the normalised text. `answered_question`, `rota/roles/api.py` 840-867, compares `_said` of the text. m86 says "glossary term" where m82 says "sense_short field", so both doors pass (observed: the texts. Reasoned: the doors).

## 3. The thread

**Why each page opens its own thread.** The thread rule is `_thread_of`, db.py 811-840: the message's `thread_id` if set, else the thread of its cause, else its own id (observed). The page writer stages `"cause_id": ctx.trigger` and no `thread_id`, sandbox.py 4864-4873 (observed). `ctx.trigger` is `trigger_message(conn, wake)`, runner.py 4848 (observed). On a `round_close` wake the only ref is `t_p1`, which is not a message id, so the trigger is None (observed: `sessions.trigger_msg` None for s216, s220, s224. Reasoned: the function). So the page has no cause and takes its own id as its thread (observed: m78, m82, m86).

His answer m83 has `cause_id` m82 and thread m82 (observed). The round's harvest reads thread `t_p1`, and m83 is not on it (reasoned). His answer does reach the repeat door: `answered_question` finds a reply by `cause_id` or `thread_id` (observed: api.py 861-864). The door missed m86 for the reason in section 2, point 3, not for the thread (reasoned).

**Commit.** d3508220 set the thread rule (observed). 231afe4c, 2026-08-09, is the first commit with `ctx.trigger` in the sandbox (observed: `git log -S`). The narrow trigger rule of `trigger_message` says "every other tick carries artefact ids, so a session woken by one is replying to nothing and gets None" (observed: its docstring). That sentence does not name `round_close`, whose ref is a thread id (reasoned).

The brief named `rota/roles/principal.py` as the page writer. The page writer is `_bind_send` in `rota/core/sandbox.py`, and the thread rule is in `rota/core/db.py` (observed: the map tool). `principal.py` reads the thread. It does not set it (observed: `grep`).

## 4. The relay

**The call and the table.** `problem.set_approval(id='s3', approval='approved')` and `problem.prioritize(id='s3', ...)` in s219, s223 and s227 (observed: `tool_calls`). The refusal comes from the call wrapper, sandbox.py 5065-5103, that runs before every call with an `id` argument (observed). It maps the namespace `problem` to its own table, `items`, finds `s3` in `statements`, and refuses: "'s3' is already a row of statements; an artefact id is unique across every artefact table ... Give this items row an id of its own" (observed). The wrapper's comment says "Refused at birth" (observed). `set_approval` changes an existing row and is not a birth (reasoned).

**Why the Vision Keeper gets `s3`.** His rulings r_m79_2, r_m83_2 and r_m87_2 approve `format_filename` and `s3` (observed: the count). The relay split routes each ref to the writer of its table by `RULED_TABLES`, sandbox.py 905-911: `"statements": "vision_keeper"` (observed). So m81, m85 and m89 carry `["s3"]` to the Vision Keeper, and the wake opens its `relay` mode (observed: `messages`, `sessions.wake_detail` "relay").

**The brief does not tell it to create.** `rota/roles/prompts/vision_keeper/relay.md` speaks of items only: "The principal has ruled per item. Apply each ruling with `problem.set_approval`, using the item id you were given" and "**Use the ids you were given.** `problem.set_approval` changes an existing row, so an id you invented is a call that cannot land" (observed). `relay.tools` holds `problem.set_approval` and `problem.prioritize` only (observed). The seat used the id it was given, as the brief says (observed). The refusal text, not the brief, tells it to give a new id (observed: the wrapper). s219's last turn then reasons that it "must create a new item with a distinct id, such as s4 or s5" (observed: s219 turn 3). The `relay` mode has no call for a statement, and `s3` was already `ratified`, so the relay had nothing to do (reasoned).

**The Terminologist skip.** `glossary.adopt` skips a row whose provenance is not `observed`, api.py 2693-2695 (observed). `format_filename` had provenance `decided` (observed: `term_provenance`). So the skip is correct, and the term was already ruled (reasoned).

**m71 does not wait on the relays.** The count says "m71 stays unsettled because the relays fail". By the code, m71 stays unsettled because `report_is_settled` returns False for a glossary ref. A relay that landed would not change that (reasoned: scheduler.py 165-168). This corrects the count's sentence.

## 5. The reach

**Wakes that can send him a clarify more than once on one open thing.**

| Wake | File and function | What stops a repeat | Reach |
|---|---|---|---|
| `tick:round_close` | scheduler.py `tick_round_close` | A page on the round's thread, or all reports settled. Neither happens when the wake ref names no message, or a report names a glossary, constraint or criterion row | The site of W5. On every night and scene, because the walk's thread is `t_p1` (reasoned) |
| `tick:contradiction` | predicates.py `contradiction`, 275-293 | An `open` clarify to him. An answered clarify does not stop it while the statement stays `contradicted` | Can repeat after each answer (reasoned). Not counted on nights 170 to 173 |
| `tick:unresolved` to the Liaison | predicates.py `unresolved`, 1160-1283 | `_woken_for` wakes the Liaison once per message | Once per message (observed: the code). Not a repeat |
| message wake, mode `report` | runner.py `resolve_inbound`, report block 2268-2300 | One wake per report. The prior-answers block shows his replies on the same rows | One page per report. Several reports on one row can each draw a page (reasoned) |
| message wake, modes `converse`, `contradiction`, `unresolved` | `rota/roles/prompts/liaison/*.tools` | One wake per message | Not a tick repeat (reasoned) |

Five Liaison modes hold `msg.clarify_principal`: `contradiction`, `converse`, `report`, `round_close` and `unresolved` (observed: `grep` of the `.tools` files). Two of them are woken by a tick that can fire again on the same state, `round_close` and `contradiction` (reasoned).

The two repeat doors are the same for every mode: sandbox.py 3791-3812 and api.py `answered_question` 840-867. Both match the same words only, so a reworded question passes on every wake (observed: the code).

**Wakes that read "N report(s)" or an open report.**

- scheduler.py `report_is_settled`, 124-171: the definition of an open report.
- scheduler.py `open_reports`, 174-181: its two callers are below.
- scheduler.py `tick_round_close`, 184-225: the detail "N report(s)".
- runner.py `_resolve_round`, 3807-3845: the round wake's input.
- scheduler.py `open_tips`, the report filters at 86-96: a report in a broadcast thread does not tip. A report to an `ask` does not tip.
- runner.py `resolve_inbound`, 2268-2300: the sibling reports and his prior answers on a report wake.

**The drivers that write a thread that names no message.** `probes/walk.py` 50 and 279, `probes/seat.py` 47 and 138, `probes/agent_principal.py` 385, `rota/testkit/scenes.py` 284 (observed). The tests seed thread `t1` and insert the harvest message on it by SQL, `tests/rota/test_predicates.py` 220-298 (observed). No test sends a page through the door on a `round_close` wake and then asks the predicate again (reasoned: the tests read. Not proved by a full search).

**Why nights 170 to 172 had no wake.** At their end `open_reports` returned no row for any broadcast thread (observed: the count). So no report on a quiet thread named a glossary, constraint or criterion row there (reasoned: `report_is_settled`). The refs of the reports of nights 170 to 172 were not read here: not in the records.

## 6. Match against what exists

- **F20**, "A quarantined key, the stalled seat and the lift": it explains the quarantine at attempt 3 and the stall after it. It names no harvest and no thread (observed: `plans/facts-2026-10-27.md` 213-221).
- **F22**, "The table an id lives in": "Which table holds a given id." It names `_owner_of_ref` sandbox.py 911 among 28 readers (observed: 233-241). It matches the relay route of section 4, where `s3` lives in `statements` and the `relay` mode handles `items`. It does not name `report_is_settled`, which is a fourth reader of "which table holds this ref" and is not in its list (reasoned: the list names `_table_of_ref`, `_table_of`, `_owner_of_ref` and `_must_exist`).
- No fact of the facts page names `report_is_settled`, `open_reports`, `round_close`, `harvest` or `_thread_of` (observed: `grep`, no match).
- `plans/stack.md`: no heading and no Site line names `round_close`, `report_is_settled`, `open_reports`, `_thread_of` or the harvest (observed: `grep`). The only lines are the sprint row 4, "W5, the `round_close` tick asks him three clarify questions and closes no round, under F20 and F22" (stack.md 45), and the status lines of 2026-10-28 (stack.md 1590, 1593, 1617).
- The F20 row "Nights since 160" names "168 W5, frame 330" (observed: facts 221). Frame 330 is "A running batch whose `tests_failing` key is quarantined keeps the one batch seat" (observed: stack.md 1770). That W5 letter is a different wall on night 168 (reasoned: its heading).
- No frame names a fix for the page's thread on a tick wake, or for a glossary ref in `report_is_settled`: not in the records.
- The design intent for a round that the seat answers with silence while one report stays unsettled: not in the records. c7d45089 removed the livelock only for a round with all reports settled (observed).
