# Review of frame 348, commit a4a2f1aa on rota/foundation, pass 1

Verdict: not ready to close. The refusal holds on the recorded case, but two high findings break law 6 at its edges. A misread earlier answer forces a contest on a line he called fine. A reply that mentions a line in passing re-opens an approve on a line he called wrong. Counts: 2 high, 2 low.

Worktree: C:/Users/roman/rota_f348 at a4a2f1aa, removed after the review. Parent a5abab6b, read through `git checkout a5abab6b -- rota/roles/api.py` in the worktree, restored after each probe.

## (a) Verdicts on the points

1. Fails at the edge. "Line 2 is not wrong." reads matched, not faulted, so that example holds. "Line 2 was wrong before, now it is fine." reads faulted [2]. The approve is refused, and `other <quote>` then lands contest on c1 (finding 1).
2. Yes, it can. The reply "I looked at line 2 again." puts line 2 in `mentioned`. The earlier "Line 2 is wrong." then binds nothing, and the approve of line 2 lands with the reply's words (finding 2).
3. No deadlock. The refusal fires on every call, and so does the "missing" refusal when the call omits line 2. Two exits stay open: add or other with a quote, and `rulings.rule(ask=...)`. The probe's ask returned `{'id': 'm79', 'to': 'principal', ...}`, so the mode holds the ask.
4. Two hunks reach past the three claims. The strip loop (api.py 14242-14247) removes every earlier-named line from the reply's clauses, faulted or not (finding 3). The strip mutates `clauses` before `ask_lines` is built, so a question fallback no longer holds earlier-named lines. That second effect is PLAUSIBLE only. No probe ran on it, and the ask exit still covers it.
5. `test_frame337_earlier_answers.py`: 5 passed. L3R replay (no ROTA_L1, ROTA_DEV_DB on a scratchpad copy of cassettes.db): 3 failed, 22 passed. Of the 24 old cases, 22 pass and 2 stay red (L3R-n171-m27-m28, L3R-n172-m76-m77). The parent api.py gives the same 3 reds, so no old case moved. The new case L3R-n175-m11-m14 stays red at 0 of 3.

## (b) Findings

1. `rota/roles/api.py:14237`, the faulted flag of `bound`, and the refusal at 14444-14453. Severity high. CONFIRMED.
   The flag trusts `_line_reading`, and that reader faults "Line 2 was wrong before, now it is fine.".
   Probe: approve on line 2 was refused, then "2": "other now it is fine." landed c1 contest.
   Before this pass a misread fault only chose a span. Now it refuses a verdict, and the one option left contradicts his words.
   Fix: refuse approve only when the newest earlier clause reads faulted and holds no agreement word after the reference, else send the seat to ask.
2. `rota/roles/api.py:14218-14220`, `mentioned` built from `_mentioned_lines`. Severity high. CONFIRMED.
   `_mentioned_lines` counts any reference, with no verdict, as "see line 3" shows (faulted [] matched []).
   Probe: earlier "Line 2 is wrong.", reply "I looked at line 2 again.", call "2": "approve". Result: c1 approve.
   The same held for "Line 2, line 3 and line 4 are about the tip.".
   Fix: let the reply take a line from an earlier fault only when `_line_reading` of the reply clause puts the line in faulted or matched.
3. `rota/roles/api.py:14242-14247`, the strip loop. Severity low. CONFIRMED. Outside the claims.
   The loop strips every line in `bound`, also a line the earlier answer called fine.
   Probe: earlier "Line 2 is fine.", reply with no line, call {"c1": "approve"}. The parent landed approve on all six refs. This commit refuses with "line 2: his words name the line, and the call gives it no option", on every call.
   Fix: strip only the lines whose `bound` flag is True.
4. `rota/roles/api.py:14449-14453`, the refusal text. Severity low. CONFIRMED.
   The text says "line 2 takes no approve" and then "Line 2, kind request, takes approve; add <quote>; other <quote>".
   A small model reads the list as the menu and can send approve again.
   Fix: drop approve and ok from the option list that this refusal prints.

## (c) Probes

All probes ran from the worktree root with `ROTA_MODEL=qwen3:8b` and `-n 0`, and were deleted after the run.

- `tests/rota/test_probe348.py`: `_line_reading` on 11 phrases, approve after 4 earlier phrases, approve after 3 passing replies, the repeat refusal, three calls that omit line 2, and one ask.
- `tests/rota/test_probe348b.py`: the misread earlier answer with approve and then other, and "Line 2 is fine." with c1 approve and rest approve. The second test ran at this commit and with the parent api.py.
- `test_frame337_earlier_answers.py` as is.
- `test_l3_rulings.py` at this commit and with the parent api.py, with `ROTA_DEV_DB` on the scratchpad copy `f348_cassettes.db`. The replay writes run rows through `record_case_run`, so the real cassettes.db stayed untouched.

## (d) Usage

Input tokens: about 52k. Output tokens: about 9k. Total: about 61k. The cap of 30k was exceeded by the replay setup and the parent comparison.
