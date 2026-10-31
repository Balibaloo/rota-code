# dry1, the second wall: repeated presents and no plan (read 2026-10-31)

Read only. Database `D:/repos/rota/.rota/dry1.db` (copy), code at 5bf28154 in `C:/Users/roman/rota_dry1`.

## Result

1. s1 repeats because messages m4 and m5 stay `quarantined` for ever. The `quarantined` predicate re-wakes the Liaison on s1 from them. The ratify of s1 in s78 lifted the wake's tick key, so the wake bought three more presents (m16, m18, m19).
2. how_it_works repeats because the s1 page in s80 had no request item. `request_rows` then gives the account row, and `account_page_refs` re-sends a row unless an *open* page shows it. The function never reads the landed approve r_m10.
3. The run waits for `tick:signoff` on the draft item `click_pause_returns_true_on_key`. `tick_signoff` fires only with no open `present`, and five are open (m3, m16 to m19). So no submit, no approve, no ticket, no criteria.
4. Root of cause 1: m4 and m5 were quarantined by Ollama timeouts, not by the model. Sessions s38 to s45 all end `LLMUnavailable ... no answer in 300s`, and the attempt cap counted them.
5. Reach in nights 170 to 175: 0 exact re-presents. The wall is new with dry1. No frame names it. Frames 240 and 253 are the nearest class.

## Q1. Why s1 repeats after m9

- The `liaison<-message` sessions of run 3: s76 (m9), s77 (m10), s78 (m11).
- s76 on m9 saw s1 `status: proposed` and wrote nothing: "A ref of any other table (a statement) has no relay here; leave it."
- s77 on m10 called `msg.relay_vision_keeper(how_it_works)` twice. s79 (Vision Keeper) set how_it_works approved.
- s78 on m11 called `brief.ratify(s1)` and delivered s1 to the Architect, the Terminologist and the Vision Keeper (m13, m14, m15).
- m16, m18 and m19 come from s80, s81 and s82. Each one is `tick:quarantined`, detail "2 abandoned", refs `["s1"]`. Each brief said only "You were woken by: tick:quarantined / Refs: s1". Each one called `msg.present_principal(refs=['s1'])` once.
- `predicates.quarantined` (line 1718) counts every message with `status='quarantined'` and puts its refs on the wake. m4 (refs s1) and m5 (refs []) give n=2 and refs [s1]. The predicate drains only on a status change, and no code moves a quarantined message.
- `loop.py:335` sets `reported=1` on quarantined *tick keys* only. A quarantined message is never marked as told.
- The wake stops only when its own key `liaison|tick:quarantined|s1` reaches the cap. Run 2 spent s44 to s46 to reach it. s78's ratify moved s1, `db._lift_quarantines` lifted every key that names s1, and the wake came back for s80 to s82.
- Side effect: the key is quarantined again, so the two later critic quarantines (`constraints:command`, `constraints:argument`, `reported=0`) are never said to the principal.

Cause, one sentence: the landed ruling r_m4 should have closed m4, m5 should have been retried after the outage, and instead both stay quarantined while the ratify of s1 re-opened the wake that reads them.

## Q2. Why how_it_works repeats at m17

- No session called present on how_it_works. The send door wrote m17 inside s80's present of s1 (`sandbox.py` 4875, `account_off`).
- At s80 the request item did not exist yet (s106 wrote it). So `request_rows(['s1'])` reached no item and returned `["how_it_works"]` (principal.py 1735). `off_page` dropped it from the s1 page, and `account_rows` sent it to the account page.
- `account_page_refs` (principal.py 1677) skips a row only when an open page to the principal shows it. m7 was answered, so how_it_works was owed again. In s81 and s82, m17 was open, so no further account page.
- m7 in run 2 is the same path, from s46.

Cause, one sentence: `account_page_refs` reads open pages and not landed rulings, so an approved how_it_works at its current version is shown again.

## Q3. What the run waits for

- `slicing` (predicates 586) needs an item with `approval='approved'` and no ticket. `criteria` needs a ticket. The run has 0 tickets and 0 criteria.
- The request item `click_pause_returns_true_on_key` (written by s106) is `draft`, with 3 description items, also draft.
- `signoff` (`scheduler.tick_signoff`, 593) wakes the Vision Keeper on draft items only when no `submit` or `present` is open. m3, m16, m17, m18 and m19 are open. So signoff never fires, and the principal never sees the item.
- The 15 critic challenges wrote 8 `challenges` rows and 2 ledger rows. s92 to s97 wrote nothing and quarantined two keys. s110 falsified the request item against `termui.py`, which is correct for a change not made yet. None of them wrote an approval or a ticket.
- s83 and s84 (survey) wrote constraints and model areas. s86 to s88 (boundary) wrote surface surveys. s109 (guess) wrote 5 `touch_guesses` rows on the request item. All are onboarding or plan input. None opens the signoff gate.
- They did not consume the gate. The gate is closed by the open pages. They consumed the run's sessions while it was closed.

## Q4. Reach

| Night | presents | with an already approved ref | same refs re-presented | how_it_works alone after approve | `tick:quarantined` sessions |
|---|---|---|---|---|---|
| 170 | 12 | 8 | 0 | 0 | 2 |
| 171 | 14 | 12 | 0 | 0 | 4 |
| 172 | 13 | 9 | 0 | 0 | 4 |
| 173 | 11 | 7 | 0 | 0 | 3 |
| 174 | 11 | 7 | 0 | 0 | 2 |
| 175 | 16 | 12 | 0 | 0 | 7 |
| dry1 | 7 | 4 | 4 (m16, m17, m18, m19) | 1 (m17) | 7 |

- A page with an approved ref beside new rows is normal in the nights (an item with new criteria). No night re-sends the same refs. No night has a quarantined message, and no night has an `LLMUnavailable` session.
- Stack headings with "present", "repeat" or "quarantin": 240 (a quarantined tick outlives the approve of its item), 253 (a quarantine's key reaches the principal twice), 307 (the night report misses a re-presented page). None covers a quarantined *message* that a later ruling should close, or the account page against a landed approve.

## Q5. m5 on m3

m5 reached nothing: the three Liaison sessions on m5 (s41 to s43) failed on the Ollama timeout, m5 is `quarantined`, and only the entry `e_m5` holds its words.

## Fix lines

1. A session that ends `LLMUnavailable` does not count toward the attempt cap, and it re-dispatches when the model answers. Reach: m4, m5 and the whole repeat chain in dry1, 0 in nights 170 to 175. About 1 cycle.
2. A landed ruling on a quarantined message's ask closes the message as answered. Also mark a quarantined message as told after one report, like a tick key. Reach: m16, m18, m19, and the unreported critic keys. About 1 to 2 cycles.
3. `account_page_refs` drops a row approved at its current version. Reach: m17 and m7 in dry1, 0 in the nights. About 1 cycle with a test.
4. After fixes 1 to 3, re-run dry1 from the copy. m3 then gets m5 handled, the pages close, and signoff can fire. Do not change the signoff gate before that run shows a need.

## Usage

About 50k tokens. Read: the dry1 tables, `predicates.quarantined`, `guess`, `signoff`, `slicing`, `scheduler.tick_signoff`, `signoff_drafts`, `quarantine_stalled`, `db._lift_quarantines`, `loop.py` 320 to 345, `sandbox.py` 4360 to 4420 and 4845 to 4910, `principal.account_page_refs`, `request_rows`. The map tool was not run: `.venv/Scripts/python.exe` is absent in the worktree. Scripts in the scratchpad.
