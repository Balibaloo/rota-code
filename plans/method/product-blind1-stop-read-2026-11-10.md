# Blind run 1: why the seat's reply to m8 was refused

One reader, 2026-11-10. Rota at `787d7112` (`rota_blind1` clone, HEAD checked). Records in
`C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/5ee5ec0b-9675-4645-967d-eab60d0ca52e/scratchpad/blind1/` (below: `B/`).
Scratch copies in `C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/1efd37b1-058e-4b19-8ab1-e1a6c654a389/scratchpad/blind1stop/` (below: `X/`).

## Result

1. `rota sign blind1 m8 --say` can never land, because `cmd_sign` lands only through `pump`, and `pump` offers only `pending_asks`, which drops every `converse` row (observed).
2. Rota's own agenda printed that exact command for m8: `reply with: rota sign blind1 m8 --say '...'` (`rota/cli.py` 787) (observed).
3. The driver built the command itself, but in the form that the agenda prints, so the driver followed rota's instruction (observed).
4. m8 is a question that the Liaison sent as `converse`, the verb that rota classes "displayed, not asked" (observed).
5. The open gate at that moment was m4, and `rota sign blind1 m4 --say` lands a reply on a scratch copy (observed). The driver never offered m4 again, because it asks a page once per key (observed).
6. No earlier dry run had a Liaison `converse` to the Principal, so no dry run tested this path (observed).
7. Turns 3 and 4 ran 0 sessions because the frontier is empty: the signoff of the request item `bill_amount_rejection` waits on the open present m4 (observed).
8. The stop is rota's first: it printed a command that its own door refuses. The driver adds a second fault, because it did not offer the open gate m4 again (reasoned).

## 1. The row m8, and m2 and m4

Rows from `B/runs/blind1.db` (same in `B/copies/t3.db`):

| id | verb | from | to | status | cause | thread | refs | body_text |
|---|---|---|---|---|---|---|---|---|
| m2 | confirm | liaison | principal | answered | m1 | m1 | `["s1"]` | NULL |
| m4 | present | liaison | principal | open | m3 | m3 | the five description items | NULL |
| m8 | converse | liaison | principal | open | m6 | m3 | the same five items | "Does 'nothing is built' mean that the current state of the code is what you want to keep, or that you want me to proceed with the changes described in the previous turn?" |

- m8 has the verb `converse`. m2 is a `confirm` and m4 is a `present`. Both are gates (observed).
- m8 is on the thread of m4 (m3). Its cause is m6, the seat's reply to m4. Session s33 (liaison, trigger m6, `wake_detail` converse) wrote m8 (observed, `sessions` table).
- m8 carries prose in `body_text`. m2 and m4 carry no text, and `render_page` builds their pages (observed).

## 2. The command for m8, and where the driver took it

- The driver ran `python -m rota.cli sign blind1 m8 --say "<words>"`. `B/blind_answer.py` 144 to 148 (`def sign`) builds the argument list `["-m", "rota.cli", "sign", run, mid, "--say", words]` (observed).
- The driver took the id m8 from `pending_replies(conn)` (`blind_answer.py` 117). It labels such a page "The lead says this to you. No answer is needed, but you can reply." (122 to 124) (observed).
- The driver did not copy a printed line. It built the command by itself (observed).
- The command matches the line that rota printed for m8 at the end of turn 2 (`B/turns/t2.txt` 70): `reply with: rota sign blind1 m8 --say '...'` (observed).
- The recipe names the same door: "Its words land through `rota sign <run> <id> --say`, the door that every dry run used" (`plans/dry-blind1/recipe.md` 5) (observed).

## 3. The code path at 787d7112

- `cmd_sign` (`rota/cli.py` 847 to 901) calls `pump(conn, OneShot())`. `OneShot.respond` answers only the ask whose id is `args.ask` (866 to 868). If `pump` creates nothing, line 894 raises `f"{args.ask} is not an open gate; `rota agenda {args.name}` lists them"` (observed).
- `pump` (`rota/roles/principal.py` 3564 to 3582) offers only `for ask in pending_asks(conn)` (observed).
- `pending_asks` (`principal.py` 171 to 208) selects `status = 'open' AND to_role = 'principal' AND verb != 'converse'` (186 to 189). Its docstring says: "`converse` replies from Liaison are displayed, not asked ... so they do not become a principal gate" (174 to 175). A shift ask returns alone, and held asks and merged touch notes drop out (190 to 199) (observed).
- An open gate is therefore an open row to the Principal with any verb except `converse`, not held (reasoned from the code).
- In `B/copies/t3.db`, the open rows to the Principal are m4 (`present`) and m8 (`converse`). Only m4 meets the condition. No shift ask and no held ask exists (`held_asks` returned an empty set on `X/c`) (observed).
- On `X/a`, `rota sign blind1 m8 --say "test words"` printed `m8 is not an open gate; `rota agenda blind1` lists them` and exit 1 (observed).
- Today's `rota/cli.py` is the same as at `787d7112`. Today's `pending_asks` still has `verb != 'converse'` (`git diff 787d7112 HEAD`) (observed).

## 4. Does rota offer a way to answer m8?

What the person is told:

- The agenda heading is `said to you (no answer needed, but you can reply):` (`cli.py` 783). The line under m8 is `reply with: rota sign blind1 m8 --say '...'` (787) (observed).
- The `sign` help says "answer one gate from the agenda" and `--say` says "answer a clarify in words instead" (`cli.py` 1016, 1021) (observed).
- So the agenda tells him to use a command that refuses this row (observed).

The ways that exist at 787d7112:

1. `rota sign blind1 m4 --say '...'`, a reply on the open page m4. On `X/b` it printed `reply sent: m13  (next: rota run blind1)` and exit 0. Row m13 is principal to liaison `converse`, cause m4, thread m3, open. m4 stays open, because `words_keep_open` is true for a `present` (`principal.py` 163). m8 stays `open` (observed).
2. The TUI. `show_replies` (`rota/cockpit/tui.py` 526 to 533) shows a Liaison `converse` and calls `mark_answered` on it. So the TUI closes m8 when it shows it. The person's next free text goes to the oldest pending ask (`submit`, 184 to 194), which is m4. With no pending ask, the text opens a new request through `open_with` (1080 to 1096) (reasoned from the code, not run).
3. No other command, flag or free reply exists on the command line. The subcommands are `ls`, `onboard`, `run`, `refresh`, `agenda`, `interrupt`, `adopt`, `sign`, `profile`, `cassettes`, `tui`, `cockpit`, `report`, `diff`, `wipe` (`cli.py` 965 to 1069) (observed).

What I ran on copies, all with rota from `B/rota_blind1` and `OLLAMA_HOST=http://127.0.0.1:1`:

- `X/a/blind1.db`, `X/b/blind1.db`, `X/c/blind1.db`: each a `sqlite3` backup of `B/copies/t3.db`.
- `ROTA_RUNS=X/a python -m rota.cli agenda blind1 --limit 3`, then `... sign blind1 m8 --say "test words"`.
- `ROTA_RUNS=X/b python -m rota.cli sign blind1 m4 --say "test words to m4"`.
- On `X/c`: `all_wakes`, `scheduler.frontier_readonly`, `signoff_drafts`, `tick_signoff`, `tick_round_close`, `open_reports`, `held_asks`, `touch_notes`. None of these calls a model.

## 5. How the earlier dry runs passed a page of this kind

- No dry run had one. Rows with `from_role='liaison' AND to_role='principal' AND verb='converse'`: 0 in `.rota/dry1.db` to `dry4.db`, `dry1_frozen.db`, `dry1_before_rerun_2026-11-01.db`, and in the dry5, dry6, dry6b, dry6b_after_turn4, dry7 and dry8 databases of `plans/method/product-seat-population-2026-11-10.md` (observed).
- Those runs sent the Principal only `clarify`, `confirm` and `present` (observed, verb counts per database). A question there came as `clarify`, which `pending_asks` offers, so `sign --say` landed (reasoned).
- The night runs had such rows: 40 of 128 `.rota/*.db` files. Example: `clickI_night121.db` m167, liaison to principal `converse`, "Do you want a commit that fixes the change, or a contest of confirm_default_on_eof?". The reply m_p4 (cause m167, thread `t_p1`) came from the walk, not from `rota sign` (observed).
- The walk lands such a reply by its own SQL: `answer_replies` (`rota/testkit/scenes.py` 265 to 287) sets the row `answered` and inserts `m_p<n>` with cause the row. It does not go through `pump` (observed).
- So no seat path through `rota sign` was ever measured on a Liaison `converse` (reasoned).

## 6. The agent's words

- Its reply to m4 (`B/seat/exchange.jsonl` row 3): "Line 5 is wrong: today the calculation accepts a negative bill with no error (only the prompt refuses it and asks again), and a bill of zero is fine, so "positive" is not right either. Also, what does "nothing is built" mean after 'ok'? I still want the change made." (observed)
- Its reply to m8 in turn 3 (row 5): "I want you to go ahead with the change I asked for: the calculation should refuse a negative bill with an error, the same way it refuses a bad tip percentage, while a bill of zero keeps working. Please fix line 5 first so the page describes today's program correctly." (observed)
- Its reply to m8 in turn 4 (row 7): "I want you to go ahead with the change: the calculation should refuse a negative bill with an error, the same way it refuses a bad tip percentage, and a bill of zero should keep working." (observed)
- m8 does not answer the agent's question. The agent asked what the page's words "nothing is built" mean. m8 asks the agent what the agent meant by those words, which are rota's words (observed by comparison of the texts).
- m8 also says nothing about the line 5 correction. The agent had already written "I still want the change made" (observed).

## 7. Why turns 3 and 4 ran 0 sessions

- `all_wakes` and `frontier_readonly` on `X/c` return `[]`, with `principal_present` false and true (observed).
- The request item `bill_amount_rejection` is `draft`, with no tickets and no batches (observed, `items`, `tickets`, `batches`).
- `signoff_drafts` returns `bill_amount_rejection` and the five description items. `tick_signoff` returns `[]`, because one open `submit` or `present` exists: m4 (`rota/core/scheduler.py` 602 to 628, the count at 623 to 627) (observed).
- m12 (terminologist to liaison `report`, open) tips nobody. `open_tips` drops a report to Liaison on a thread with a Liaison `deliver` (`scheduler.py` 95 to 97). `tick_round_close` finds no open report, because m12 names `s1`, which is `ratified` (observed).
- The architect's guess for `bill_amount_rejection` ran in s38, and the critic ran in s39. Nothing else is owed (observed, `sessions`).
- So the scheduler waits on the Principal's answer to m4. A landed reply to m8 would not have released it, because m4 stays open until the Liaison lands a ruling on it (reasoned from `tick_signoff` and `land`).

## 8. Verdict

1. The stop is rota's, with a second fault in the driver (reasoned).
2. The deciding fact: the agenda prints `reply with: rota sign blind1 m8 --say '...'` for m8, and `cmd_sign` can only reach rows of `pending_asks`, which excludes `converse` (observed).
3. A second rota fault is that the Liaison put a question to the Principal as a `converse`, the verb that rota labels "no answer needed" (observed).
4. The driver's fault: it did not offer the open gate m4 again after one landed reply (`blind_answer.py` 175 to 176). A reply on m4 lands, as the copy `X/b` shows (observed).
5. The run waited on a ruling for m4 in both turns. The refusal of m8 hid that wait from the seat (reasoned).
6. I could not establish what the Liaison does with a second reply on m4, or with the agent's words as a reply on m4, because that needs a model run (not established).
