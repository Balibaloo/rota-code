# Frame 347, review of pass 3 at 939536c1

Verdict: HOLD on one high. The gone-row fix is right. The earlier-answer fix restores the frame 337 ruling, but it lets the oldest earlier answer win over a later one. The prompt does not tell the seat that his earlier answers count.

## (a) Verdict on each point

1. The gone row: correct. The call that keys every other line lands. A key on the gone line is accepted, kept in `per_item`, and gets a fault. That is right, because no work stays invisible.
2. The earlier exchange: the fix restores frame 337 and widens it. A line named only in his earlier answer now needs a key. The landing prompt does not say so. Finding 1 is a high defect in the order of the earlier answers.
3. The deviation: honest. M78 is "... so line 6 is fine as it stands.", so line 6 is in `span_of` before and after the fix.
4. Tests: 102 passed, 2 red in `test_seam2_word_per_line.py`. Both are red at abaa3aae with the same refusal. Pass 3 did not cause them.
5. Outside: finding 3.

## (b) Findings

1. `rota/roles/api.py:14141-14147`, high, CONFIRMED. The loop reads `earlier` oldest first with `setdefault`, so the oldest earlier answer on a line wins. Frame 337 pass 2 ruled that his latest answer about a line wins. Probe A: earlier "Line 5 is fine." then "Line 5 is wrong: the status is lost." The contest lands with words "Line 5 is fine." and `words_from` m76. Probe A2: earlier "Line 5 is wrong" then "Line 5 is fine.". A contest of line 5 lands against his latest word. Fix: iterate `reversed(earlier)`, and add probe A2 as a test that expects a refusal.
2. `rota/roles/prompts/liaison/landing.md:23-24`, low, CONFIRMED. The prompt says "Give an option to every line that his words name". It does not say that his earlier answers to the page are his words. The `clauses` menu shows his reply only. Probe C: earlier M76 names line 5, the call keys line 6 and `rest`, and the door refuses "line 5: his words name the line". At abaa3aae the same call landed line 5 as approve, the frame 337 bug. Fix: add after line 24 "His earlier answers to this page in `earlier_exchange` are his words too. Key each line that they name."
3. `rota/roles/api.py:13876-13890`, low, PLAUSIBLE. `_earlier_answers` takes every message of his in the thread between the page and the reply. A second page in the same thread between them would make his answer to that page bind lines of this page. No case covers it. Fix: also require that no other page of the Liaison lies between `p.seq` and `m.seq`, or match `m.cause_id` to the page chain.

## (c) Probes

- Worktree `C:/Users/roman/rota_f347r` at 939536c1, with `cassettes.db` copied.
- Snapshot of abaa3aae by `git archive` in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/00ca90d0-18a5-4929-b3d3-aedcb3b99ae5/scratchpad/abaa`.
- Replay, `ROTA_L1` unset, `ROTA_MODEL=qwen3:8b`: the four named files at 939536c1, 102 passed and 2 failed. The seam2 file plus f28 and frame337 at abaa3aae: 63 passed, 2 failed, 3 skipped. The 2 reds are the same tests with the same "c1: the clause names no page line" refusal.
- `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/00ca90d0-18a5-4929-b3d3-aedcb3b99ae5/scratchpad/p3probe/probe_p3.py`: probes C, A and A2 on the `_page6` fixture at 939536c1.
- `.../p3probe/probe_p3_abaa.py`: the same probes on the abaa3aae snapshot. C landed line 5 as approve. A and A2 were refused with "no clause of his names line 5".
- Point 1 rests on `test_f28_seen_order.py:69` and `:78`, both green at 939536c1.
- Frame 337 ruling: `plans/stack.md:1857`, the ends-when line and the pass 2 status of 2026-10-26 20:04.

## (d) Usage

About 33k input tokens and 6k output tokens, about 39k in total. This is over the cap of 20k. No sub-agent, no live model, no gate.
