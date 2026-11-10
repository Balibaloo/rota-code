# Review of build 2, frames 114 and 183: three pages that a row already answered (2026-11-10)

Read-only, on Fable, from `f183_114_review_brief.md` in session 33f037c1's scratchpad. Worktree `C:/Users/roman/rota_p183` at 3e673298, commits 62c86178, bebae782 and 3e673298 on 29e263a2. The rows are dry run 8's `final.db`, copied to this session's scratchpad and probed with the new code.

## (a) Verdict

**Fix before the pick.** Two high findings, both in part 3 (W7). Parts 1 and 2 do what the brief asks on dry run 8's rows, with low findings.

1. W7 on dry run 8's shape: `pending_asks` returns `m59` only (CONFIRMED). The hold fires through the `present`-names-the-batch fallback, not the park id. The true park row `m_park_e65413c486_bg_1` is `answered`. When he answers m59, the four pages return while bg_1 stays `deferred` (CONFIRMED, finding 1).
2. W3: m52's shape is refused with his words and lands with the ruling id in refs (CONFIRMED). m57's shape is refused once by r_m46, "Line 4: drop it", a ruling about the criteria page, with one duplicate line (CONFIRMED, finding 3). The cost is one refusal per landed ruling per session, and the words are about a different question. The cost is not right as built.
3. The ruling id in refs: `_items_reached` gives an empty list for `r_m45_2`, `_reached` still reaches the item through bg_1, `batch_of_page` gives bg_1, and `render_page` skips the ref in silence (CONFIRMED). No reader breaks.
4. `prior_answers` on s190's wake: 0 entries, 0 characters, because m34's refs are three tests that no answered clarify shares (CONFIRMED). Frame 361's cut is a reply of 23,463 characters. The push adds nothing here. The modes are six, not four: `converse`, `contradiction`, `round_close`, `unresolved`, and `base` and `landing.base`, whose `mode_tools` is None (CONFIRMED, finding 5).
5. W5: on the copy taken back before m34, the escalation of the three base-red tests raises `EndRefusal`, `outbound` is empty and `unresolved` gives no wake (CONFIRMED). On the copy with m34 present, the same-refs door fires first, which is right. The mixed offer names the dropped test and the kept test (CONFIRMED).
6. The ruling of 2026-10-08 point 3 is cited in two docstrings and one comment, never in a door text (observed). The behaviour matches in part: no page. The note to him exists on the review page only, `principal.py:3651-3662`. The park page and the state page carry no such note (observed, finding 6).
7. `batch_of_page` gives bg_1 for m52, m54, m57, m58 and m59 on the copy (CONFIRMED). A page with two batch refs returns the first ref in list order (CONFIRMED).
8. The held-page line renders on the fixture and on the copy, one line per page with id and first sentence (CONFIRMED). `parse_reply` reads no line and keys on `words_keep_open` only (observed). The lines are appended to `rendered` after `order` is built, so the numbered rows do not move (observed). The landing Liaison does not see the lines (finding 4).
9. The five updated tests pin the new text, the empty offer list, `EndRefusal` on the escalation, and `_F207_FACT`. None is weakened (observed: the diff).
10. Eight new defs, none existed at 29e263a2 (CONFIRMED). The new file: 10 passed. The related set: 472 passed, 22 skipped, 6737 deselected, 1 xfailed in 274s (CONFIRMED). The gate's baseline `.rota-gate.json` holds 0 reds (observed). `casestatus --model qwen3:8b` reads "0 stale, 205 never measured" in both trees, so it counts no stale case for a door text change (observed).

## (b) Findings

1. **High. `rota/roles/principal.py:272-316`, `_with_parked_batch`.** The hold lasts only while an open `present` page names the batch. On dry run 8 the park row `m_park_e65413c486_bg_1` is `answered` (seq 60, refs `["bg_1"]`), and m59 is an ordinary present made with `park` False, which its `reading:` refs prove (`sandbox.py:5109`). CONFIRMED: `test_a_parked_batch_with_no_open_park_page_holds_no_page` shows the four pages return when m59 closes, and bg_1 stays `deferred`. His one reply to m59 brings W7 back. Fix: hold on `batches.status = 'deferred'` alone, and name the held pages on the state page's parked line (`principal.py:694`), so a resting park still shows them.
2. **High. `rota/roles/principal.py:288-294`, `park_page`.** Any open `present` whose refs name the batch counts as the park page, so a criteria page or a verdict page on a deferred batch takes the held lines. PLAUSIBLE: m31, the criteria page, names bg_1 and would match if open. Fix: match `park_ask_id(conn, batch)` only, and fall back to the state page of finding 1.
3. **Low. `rota/core/sandbox.py:3500-3524`, `_landed_ruling_refusal`.** The door lists every `ruled_refs` row on a shared ref, with duplicates. CONFIRMED on the copy: m52's refusal carries r_m45_2 and r_m46, m57's carries r_m46 three times, two on `tst_c3`. The words "Line 4: drop it" answer no question of m57. Fix: dedupe by ruling and ref, and keep rulings whose `ask_id` is a clarify, or the newest ruling per ref.
4. **Low. `rota/roles/principal.py:210-214` and `rota/core/runner.py:2739`.** The held line lives in `pending_asks` only. The landing Liaison renders the page through `render_page`, so a reply "show me m52" lands against a page with no m52 line. PLAUSIBLE from the two call sites. Fix: add the line in `_park_page` or `render_page`.
5. **Low. `rota/core/runner.py:2621-2624`.** `allow is None` admits `base` and `landing.base`, so the push runs on six Liaison modes, and the report names four. PLAUSIBLE from `mode_tools`. Fix: name the six in the comment, or test the tool against `allow or []`.
6. **Low. `rota/core/sandbox.py:2362-2364`, `_escalation_admitted`.** A mixed set returns False, so `_escalation_or_step` offers the end step where the escalation door would take the rest. CONFIRMED: the mixed set is False, the green test alone is True. Fix: strip the base-red refs and admit the rest.
7. **Low, outside the points. `rota/core/sandbox.py:3437-3455`, `_base_red_refs`.** It compares test ids, and `drop_base_reds` compares nodes. The report names this. Fix: read nodes, or record the choice in the docstring.

## (c) Probes

All under `C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/33f037c1-f639-4fa5-8bd4-0cc91eeff019/scratchpad/rev183/`, run with `PYTHONPATH=C:/Users/roman/rota_p183` from the worktree root, on `dry8.db`, a copy of dry run 8's `final.db`.

- `p1_pending.py`: `pending_asks`, `batch_of_page` and `park_ask_batch` on the five pages, and m59's rendered tail.
- `p2_rows.py`: s187, s190, s199, m59, m34, every landed `ruled_refs` row, s199's tool call, the presents that name bg_1.
- `p4_prior.py`: the Liaison modes with `msg.clarify_principal`, and `resolve_inbound` on `tick:unresolved` m34.
- `p3_doors.py`: `_items_reached` and `_reached` with a ruling id, the m99 render, two batch refs, the m52 and m57 shapes at the clarify door, the W5 door with m34 present, `unresolved`.
- `p5_w5.py`: the W5 door with the rows taken back before seq 34, `project_tests_fact`, `_escalation_admitted` on a mixed set.
- `p6_s199.py`: the park rows and s199's turn.
- Bash: `git diff 29e263a2 3e673298`, the new defs against 29e263a2, pytest on the new file and the related set, `.rota-gate.json`, `casestatus --model qwen3:8b`.

## (d) Counts and time

- Tests: 10 new, all green. Related set 472 passed, 22 skipped, 1 xfailed, 274s. Five older tests updated, none weakened.
- Findings: 2 high, 5 low. 5 CONFIRMED, 2 PLAUSIBLE, 1 of the low outside the points.
- Time: about 35 minutes, ended 01:46 on 2026-11-10.

## (e) Not read

- The path that wrote `m_park_e65413c486_bg_1` at seq 60 after m59 at seq 59, and why `park` was False for s199's present.
- `_stage_ruling` at `api.py:14358`: whether a ruling id in a clarify's refs becomes a `ruled_refs` row when he answers.
- The eight-words quote door at `sandbox.py` about 3925 against a seat that pastes the refusal's quoted words back.
- `held_asks` and `_close_asks_about` against `batch_of_page`. The report's open question 2 stands.

## (f) Usage

About 108k input tokens, about 13k output tokens, about 121k total. Over the 60k cap. The cause was six probe rounds on the copy.

## Second look, b74c8d9f

Verdict: pick. The three commits close high 1, high 2 and the lows. One low stays open, finding 1 below.

(a) Points
1. Confirmed on the copy. `pending_asks` gives `m59` only. With `m59` answered and `bg_1` deferred it gives nothing. With `bg_1` running it gives `m52, m54, m57, m58`. The `m59` page names the four under "These pages wait until the batch resumes".
2. Read. `_tells_the_stop` admits two kinds: the park row by `park_ask_batch(id)`, and a `present` whose `stalled:<id>` config key names the batch. No other page kind on a deferred batch shows. A page on a deferred batch with no stopping page open is hidden. The state page says "Stuck: bg_1 stops here" and names no page. See finding 1.
3. Confirmed on the copy. The door joins `messages` on `r.ask_id` and keeps `clarify` and `converse` asks. `m57` gets None, `r_m46` is on `m31`, a present. `m52` gets `r_m45_2` on `bg_1` once, with his words. The second send gets None. `m54` and `m58` get None.
4. Confirmed on `w5`. The words are "inh_16dcb40b was red before this change, so send msg.escalate_architect on the rest." The offer's refs are `["inh_02554f55"]`. The words name the dropped test only. The kept test is in the refs, not in the words. Low, see finding 2.
5. Not from these commits. `instructions_for` is equal for all 196 l-cases at 3e673298 and b74c8d9f. The STALE is a cassette miss at a turn, `test_l1.py:195`. No cassette under qwen3:8b carries "already ruled on these rows", "red before this change, so send" or "These pages wait until the batch", so no text of the three commits reached a recorded turn. The register shows 10 l-cases re-recorded at 01:33-01:35, all on the challenge path, 9 green and `L1-DV-log-the-choice-the-criteria-did-not-make` 0/5. `casestatus.status("qwen3:8b")` at b74c8d9f reads 155 green, 20 PROV, 31 FAIL, 0 STALE. The moved text sits in a build 2 commit before 3e673298. The gate's re-record is the right discharge for the 9 green. The 0/5 case and the three open misses, `L1-TE-specify-criteria` and two L3 chains, need a read, not a re-record.
6. Clean. `_deferred_batch`, `_tells_the_stop`, `held_pages` and the seven test names do not exist at 3e673298. `held_pages` has one caller, `render_page`. The new file passes 16. The `-k` selection with `-n 0` passes 385, skips 20, xfails 1.

(b) Findings
1. Low. `rota/roles/principal.py:712-760`, `parked_line`. CONFIRMED: with `m59` answered the state page is "Stuck: bg_1 stops here. It breaks ... A new commit on the change starts it again." and `pending_asks` is empty. The four clarifies wait unnamed. Nothing is lost, they return on resume, and their answers reach a parked team. PLAUSIBLE: a batch `deferred` and not `parked` gets no Stuck line, so its pages hide with no line at all. Fix: give `parked_line` the held pages of the batch through a batch-keyed `held_pages`.
2. Low. `rota/core/sandbox.py:3269-3275`. The offer says "the rest" and names no kept test. Fix: write the kept refs in the words.

(c) Probes, in the scratchpad `C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/33f037c1-f639-4fa5-8bd4-0cc91eeff019/scratchpad/`: `p1.py` point 1 on `dry8.db`, `p2.py` the state page, `p3b.py` the door on the four rows, `p5b.py` and `p5c.py` the instruction dump and diff, `p5d.py` to `p5h.py` the register, read-only by uri. Worktrees `C:/Users/roman/rota_f183r2` and `C:/Users/roman/rota_f183base`.
(d) Usage: about 130k input, 10k output, 140k total.
