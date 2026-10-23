# Frame 272, review 2 of pass 1b (1e0a306f on b230820f)

Verdict: do not accept as it stands. One small fix makes the pass acceptable for the branch. The record holds the order at the reply, not at the read. One key per page also maps a second reply with the first reply's order.

## (a) The claim, point by point

1. The record: partly true. For the night seat it is the same list. For a page he answers twice, the second reply can get the wrong list. For the TUI and the CLI, the list comes from the reply tick, not the read.
2. The present page id: the landing carries `page_id`. An earlier reply names "of page m105" and keeps `page: m105`. Nine of 166 recorded cases go stale. All nine are landing cases.
3. The diff: three hunks in the code and one test file. Each hunk does what it says. The three test files pass, 26 of 26, with `-n 0`.

## (b) Findings

1. A page he answers twice uses the first reply's order. Severity high for the frame, low for the night. PLAUSIBLE.
   - `rota/roles/principal.py:1899`: `land` writes `order:<page id>` with `INSERT OR IGNORE`.
   - A reply keeps its page open, and `pump` offers the page again at each tick (`principal.py:1808`).
   - `pending_asks` renders the page again each tick (`principal.py:192-198`). The second reply reads that new render.
   - `_recent_chat` keeps one order per page (`rota/core/runner.py:2567`), so it maps the second reply with the first order.
   - A page shown again after a stale ruling has the same message id and the same problem. A page sent as a new message has a new id and is safe.
   - Review 1 measured 73 of 693 rows that moved on nights 158 and 159. Rows move during a night.
   - Fix: key the record by the reply, `order:<reply msg id>`, and read it with `r["id"]` in `_recent_chat`.
2. The TUI and the CLI record the order at the reply tick, not at the read. Severity low for the night, high for the frame claim. PLAUSIBLE.
   - The night seat gets the Ask in `backend.respond(ask)`, and `land` gets the same object (`principal.py:1808-1812`). For the night, the list is the one it read.
   - The TUI shows the Ask from the first tick (`rota/cockpit/tui.py:167`, `show_ask`). Later it gives the answer to a new Ask from a new `pending_asks` (`tui.py:163`).
   - The CLI prints the agenda in one command (`rota/cli.py:722`). `pump(conn, OneShot())` renders the page again in a later command (`cli.py:845`).
   - The fix for finding 1 does not close this window.
   - Fix: let `QueuedPrincipal.submit` put the shown Ask's `order` on the Answer, and let `land` record the order from the Answer first.
3. A database with no record gives raw line numbers again. Severity low for new nights, high for a replay of an old run database. CONFIRMED.
   - Probe `wake_s239.py` deletes the `order:` rows. The earlier reply then reads "Line 1 is wrong ... Line 2 should say ...".
   - Only the key `page: m105` against `landing.page_id: m116` tells the seat that line 1 is not line 1 of the present page.
   - At b230820f the same reply had its lines named, with rows from today's render.
   - Every night database from before 1e0a306f has no record. None of the 9 landing cases has an earlier-page reply, so the suite does not test this path.
   - Fix: on a missing record, write "line N of page <id>" with no row, so the text names the other page.
4. Nine recorded cases go stale. Severity low for the night, low for the frame. CONFIRMED.
   - Probe `inbound_hash.py` hashes `resolve_inbound` for each case at both commits. 9 of 159 single-session cases changed. A second run at 1e0a306f changed 0, so the page id is stable.
   - The nine are all `L1-LI-*` cases in `tests/rota/cases/l1_landing.yaml`, and each has a landing. The 7 chain cases were not composed. Their count is open.
   - Fix: re-record the nine landing cases with the fix of finding 1, in one recording.
5. Outside the points. The present page's `landing.lines` still comes from today's render (`runner.py:2331`), not from the record. Severity low. PLAUSIBLE.
   - `apply_rulings` lands through `_page_order`, which also uses today's render (`principal.py:1831`). The landing and the ruling therefore use the same list.
   - The window is short, because the landing wake follows the reply. The seat then reads his present-page numbers against a list he possibly did not see.
   - Fix: none in this frame. Name the window in the frame's open questions.

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/b85289fd-418f-43a1-a641-15dad2620cfa/scratchpad/r272b/`.

- `base/` holds `git archive b230820f rota tests`. It is the parent tree, and it changes no git state.
- `inbound_hash.py` seeds each case in memory and hashes `resolve_inbound`. The output is `h_old.json`, `h_new.json` and `h_new2.json`. 9 changed and 0 varied between runs.
- `wake_s239.py` builds the s239 fixture and prints the landing and `recent_chat`, first with the record and then without it.
- `cases_chat.py` counts landing cases with a reply to an earlier page. The count is 0 of 9.
- `cs_new.txt` and `cs_old.txt` hold the `casestatus` output. Both show 166 never measured, because the worktree has no register. I did not use them.
- `pytest -n 0` ran on `test_frame272_recent_chat_pages.py`, `test_chat_intake.py` and `test_principal_reply.py`: 26 passed in 14 s.
- I did not open a night database. The night order of finding 1 comes from the code and from review 1's count.

## (d) Usage

Input tokens: about 26k. Output tokens: about 6k. Total: about 32k. The run went slightly past the 30k cap.
