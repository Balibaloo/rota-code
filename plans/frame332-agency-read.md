# Frame 332, the agency read

Read only, 2026-10-26, at head 46e5c88b. No pytest ran. No register was opened. Frame 332 has no commit, no pass and no record. Its fix is proposed only, so this read takes the Site line, the Ends-when line and the status line of frame 326 at 2026-10-25 23:21 as the fix.

Verdict first: **at one door of 15**. The proposed lint refuses 8 of the 15 debt containers in the suite and the gate. It passes 4 that name a closed frame or the wrong frame, and it cannot see 3 that carry no marker word (reasoned: sections 3 and 4).

## 1. The purpose

The mechanism on the Site line is a lint that does not exist yet (observed: no commit names frame 332, `git log --grep`). It serves the Records line of the composition, "Every open obligation stays visible and countable until something discharges it" (ruled: Roman, ratified 2026-09-16, `plans/composition.md` line 50). The wall it answers is fault C of frame 326: d207a0bd of 2026-09-12 withdrew `ledger.log` and wrote the owed mode in its commit message, and the case kept a YAML comment "Red until that mode exists" that no reader saw (observed: `plans/frame326-provenance.md` lines 22, 49 to 56). Frame 323's table then counted the case as a model failure (observed: the same record, line 54). The session proposed the lint in the terminal reply of 2026-10-25 23:1x, and Roman answered "ok" at 23:21 (ruled: Roman, 2026-10-25 23:21, `plans/stack.md` lines 1405 and 1406). His "ok" covers "must name a frame on the stack". The Ends-when line adds "or in the archive" (observed: `plans/stack.md` line 1312 against line 1406). No ruling covers the addition (reasoned: no record found for it).

## 2. What exists

| Thing | Where | What it does |
|---|---|---|
| Frame lookup | `rota/tools/rulings.py` 244 to 263, `query_frame` | Finds frame N on the stack, then in `plans/archive/*.md` |
| Frame parser | `rota/tools/state.py` 31 (`HEAD`), 170 (`parse`), 373 (`archives_since`) | Reads every open frame heading on `plans/stack.md` |
| A frame field on a debt | `rota/testkit/scenes.py` 1190 to 1209, `Call.held`; rows at 1309, 1317, 1329, 1335 | A wrong row names the frame that holds it |
| The field rendered as a mark | `tests/rota/scene_tests.py` 43 and 103 to 105, `reason=f"held by {...}"`; `known={"I4": "frame 130"}` in two scene files | A strict xfail whose reason names the frame |
| The `red:` field and its reader | `tests/rota/cases/l1_generators.yaml` 14; `rota/tools/casestatus.py` 619, `red_by_construction`; `tests/rota/test_l1.py` 218 | A case red by construction, set apart from the counts, run as xfail (5f6b81c6, 2026-10-25) |
| A shrink-only debt set | `tests/rota/test_case_reachability.py` 212 to 227 and 291 to 305, `OWED` and `OWED_CEILING` | Ten case ids excused, guarded by a count (14bf6317, 2026-10-25) |
| A pinned backlog | `tests/rota/test_edge_coverage.py` 87 to 93, `BACKLOG` | Three message edges with no case, asserted equal |
| A known-findings set | `tests/rota/conftest.py` 147 to 175, `KNOWN_REFUSED_OFFERS`; `unhide` 294 to 308 | 17 refused offers allowed; a new finding in an xfail turns red |
| The known reds | `rota/tools/gate.py` 381 to 389; `.rota-gate.json` `failed` | 32 node ids at f9f5cd19, no frame per id |
| Red-to-frame prose | `plans/gate150607c1-reds.md`, the column "Hold as a known red under frame 326" | The only place a known red meets a frame |

(observed: each file and line named.) The code already holds one structured form, `held` with "frame N", and one resolver (reasoned: the first four rows).

## 3. The reach

The cause the frame places: a debt marker can name no frame, so the stack does not count the debt (observed: the heading, line 1310). The code shows a wider gap. No debt container has a frame field that a test checks against the open stack (reasoned: the table above, only the scene rows carry one, and nothing checks it). The instances, by container:

Names no frame:
1. `tests/rota/cases/l1_generators.yaml` 14 `red:` and its comment at 24. Frame 334 owns the mode (observed: `plans/stack.md` line 1328).
2. `tests/rota/test_chaos_confirm.py` 163, xfail "owed on a vocabulary decision".
3. to 6. `tests/rota/test_frame234_verdict_lines.py` 885, 898, 939, 945, four xfails "residue". Frame 234 closed on 2026-10-15 (observed: `plans/archive/stack-2026-10-15.md`).
7. `tests/rota/test_l1.py` 259, `skipif(True, reason="the obligation set is not yet fully covered")`.
8. `tests/rota/test_roles_doc.py` 275, "G4 stays unclaimable until the gauntlet's story log exists".
9. `tests/rota/test_edge_coverage.py` 87 to 93, `BACKLOG`: two edges with no frame, one with frame 107, closed (observed: `plans/archive/stack-2026-10-02.md`).
10. `tests/rota/conftest.py` 147, `KNOWN_REFUSED_OFFERS`, 17 entries, no frame per entry.

Names a frame that counts nothing:
11. to 13. `tests/rota/test_offers_followed.py` 120, 187, 227, "finding of frame 144". Frame 144 closed on 2026-10-07. Frame 148 holds the findings (observed: `plans/stack.md` line 2751 and 2754).
14. `tests/rota/test_case_reachability.py` 212 and the skip at 287, "owed since frame 326". Frame 331 discharges the set (observed: `plans/stack.md` line 1304).

Carries no marker:
15. The gate's known reds, 32 node ids in `.rota-gate.json` at f9f5cd19, 34 reds at the gate of 4dc36732 (observed: the file; `plans/stack.md` line 1418).

Count: 15 containers, 46 single debts inside them (10 + 17 + 3 + 32, overlap L1-TE once, reasoned). Seven containers name an open frame correctly: the four scene rows, the two `known` I4 rows, and `test_frame250_verdict_faults.py` 125 (observed: frames 130, 138, 146, 166, 250 on the stack).

## 4. The fix against the reach

The proposed lint reads three texts by word: test markers, "until" comments and commits with "owed" (observed: the Site line). Against the reach:

- It refuses 1 to 8, eight containers (reasoned: each holds a marker or the word "until" and no frame).
- It passes 9, 10 and 15. A Python set and a gate baseline hold no marker and no "until" (reasoned: the Site's three texts).
- It passes 11 to 13, because frame 144 is in the archive, and the Ends-when accepts the archive (observed: line 1312).
- It passes 14, because frame 326 is on the stack, though frame 331 owns the debt (reasoned: "names a frame" does not check that the frame owns it).

So it covers 8 of 15. Its first run also reads text that is no debt. 69 Python comments hold "until", and most are history such as "Until frame 65 this" (observed: `grep`, `rota/llm/llm.py` 64). 47 commits hold the word "owed", 33 name no frame, and most use the product's own word, such as the owed-call nudge (observed: `git log -P --grep='\bowed\b'`). A commit cannot change, so the lint needs an allowlist of old commits, which is one more debt container (reasoned). The lint fits the form of fault C's origin, a commit and a comment, and not the containers the suite uses (reasoned: sections 1 and 3).

## 5. My proposal

I would not propose the same fix (reasoned: 8 of 15, and the archive and word rules). Mine, at the outcome and the sets, where every suite debt already shows:

1. One reader `open_frames()` in `rota/tools/state.py` from `parse` (line 170). It reads `plans/stack.md` only, because an archived frame counts nothing (observed: frame 144, items 11 to 13; Roman's "on the stack", line 1406).
2. One form, `held by frame N`, the form `scene_tests.py` 43 already renders. A hook beside `unhide` in `conftest.py` 294 fails an xfailed report whose reason lacks it or names no open frame. The two debt skips, items 7 and 14, become xfails (reasoned: the scene rows, section 2).
3. `red:` takes a `held:` frame, and `test_l1.py` 218 renders it (observed: `casestatus.py` 619).
4. `OWED`, `BACKLOG` and `KNOWN_REFUSED_OFFERS` become maps from an id to a frame, and one test checks each value with `open_frames()` (observed: the three sets, section 2).
5. The gate stores `held: {node id: frame}` in the baseline at `gate.py` 389 and prints `unheld: k` for a known red with no open frame. No commit lint and no "until" lint, because the stack is the count (ruled: composition line 50; reasoned: section 4).

Price: one implementer pass on Opus, about 75k (anchor: a cold pass of about 300 lines with one suite run, 74k, frame 30), one review, 61k to 76k, and a resumed fix, about 24k. That is 3 cycles, the instrument-fix shape, about 30k of the holding session's context at 10k a cycle (observed: `plans/operating-facts.md` lines 241 to 247). The frame priced 1 cycle (observed: line 1313).

## 6. The doubt

- I did not read the terminal reply of 23:1x itself. If it named the archive, the Ends-when is not a departure (reasoned: only the stack line holds his words).
- I did not check which of the 32 known reds an open frame already names in prose. Some do, for example frames 326 and 306 in `plans/gate150607c1-reds.md`, so item 15 may be partly held (reasoned).
- I classified "until" and "owed" hits by sample, not one by one, and I ran nothing. The counts 69 and 33 are upper bounds for debt hits (reasoned).

## Verdict

`at one door of 15`: the lint covers 8 of 15 containers, items 1 to 8. It leaves `BACKLOG`, `KNOWN_REFUSED_OFFERS` and the gate's 32 known reds, which carry no marker, the three frame 144 xfails, which name a closed frame, and `OWED`, which names frame 326 where frame 331 owns the debt.
