# Frame 200 pass 5 design review, Opus, 2026-10-12

Read-only review of `plans/frame200-pass5-design.md` against the code at HEAD
402eb146 of `D:/repos/rota`. Probes under the session's scratchpad `rvd5/`:
`p_graph.py`, `graph_plus.json`, `p_samerefs.py`. No live database was opened.
Rota workflow, except where a line says meta workflow.

Verdicts: 1 HOLDS, 2 CONFIRMED, 3 CONFIRMED, 4 CONFIRMED with one red, 5 HOLDS,
6 PLAUSIBLE, 7 UNDERPRICED. Do not start as written. Start after findings 1 and
2 are folded into the design. Finding 1 matters most. A reason id in the stored
refs makes every reasoned prior invisible to the same-refs door.

## (a) The verdict on each point

1. HOLDS. The message stores no new words, and the reason is a row in the decider's name reached by a ref.
2. CONFIRMED. The Tester's challenge wake resolves the ref and shows `id`, `author`, `text` of the row.
3. CONFIRMED. Without the skip, a reasoned prior counts out of the cap and the ceiling. The skip keeps the other authors' exemption.
4. CONFIRMED for law 3. The derived set does not move. One law test turns red. The ruling's "No new edge" covers the route only.
5. HOLDS. The binder's own author check refuses a Developer overwrite. Pass 5 does not wait on frame 219.
6. PLAUSIBLE. The denominator is a query. The numerator needs the text of the Developer wakes in `turns`.
7. UNDERPRICED. The night read anchor is 270k to 330k, not 150k. The total is about 600k and 6 cycles.

### 1. Law 2

- The message keeps `body_text` as the quotes. Only `body_refs` gains an id. So the message carries no new words.
- Law 2 says "The reasoning is written into the decision record by whoever decided, and reached by following a ref" (`rota/LAWS.md:114-116`). The Developer decided to challenge, so the Developer is the decider of that reason.
- The `decisions` node says "each decision is authored by whoever made it" (`rota/design/graph.json:97-103`). The Architect, the Vision Keeper and the Terminologist write rows today with no provenance column. A Developer row is the same kind of record.
- Composition, Records: "reasoned by a seat" fits the row. The table has no mark column for any author, so pass 5 adds no new gap.
- The binder writes the row in the seat's name in one call. The `_bind_send` docstring asks for "writes a decision and refs it" (`rota/core/sandbox.py:2319-2322`). One staged write per call meets those words. The fallback A' is not needed for law 2.

### 2. The Tester's wake

- `resolve_inbound` calls `_resolve_refs(conn, out["refs"], role=wake.role, detail=wake.detail)` (`rota/core/runner.py:1703-1704`).
- A ref that hits no listed table falls to the `for ... else` branch. With `role` set, it selects `id, author, text FROM decisions` (`rota/core/runner.py:2221-2232`).
- On the wake the Tester sees `{"id": "d_...", "author": "developer", "text": <the reason>, "table": "decisions"}` in `resolved_refs`. The test's body and the whole last run sit beside it, because `role == "tester" and detail == "challenge"` (`runner.py:2215`).
- The resolver does not cut the text. The 600-character cut in the binder is the only bound.

### 3. The cap

- `_carries_decision` returns True for any row whose refs share a test with the challenge refs (`sandbox.py:1817-1823`). The probe: `_carries_decision(c, ["c1","tst1","d_own0000aa"], None)` is True for a row by `developer`.
- The lift happens in `_challenges_on` (`sandbox.py:1678`). Each reasoned prior is skipped there, so `landed` never reaches 3 or 6. The short-circuit at `sandbox.py:1856` fires only when the seat repeats an existing id in its own refs, because the door runs before the binder stages the fresh row.
- The skip needs `author` in the `SELECT` at `sandbox.py:1820` and the sending role. `_challenges_on` reads only `from_role = 'developer'` rows, so the skip there is `author != 'developer'`. Rows by `architect`, `vision_keeper`, `terminologist` and `principal` keep the exemption.

### 4. The graph edge

- The probe adds the edge and runs `check_all`: no problems. No role's `derived_contacts` moves, because `decisions` has `contact: false`.
- `latent_contacts` text changes, because the `via` list names `decisions`. Nothing pins that text.
- The new red: `test_owners_can_read_what_they_own` (`tests/rota/test_laws.py:182-207`). The probe's blind set is `[("developer", "decisions")]`. Finding 3.
- The cascade adds the Developer as an owner of `decisions` in `cascade_wakes` (`rota/core/scheduler.py:2421`). `loop.py:337` keeps those wakes as strings only, so no session wakes from it.
- The ruling's words (`plans/frame200-design.md:95-99`): "the Developer's answer mode gains `msg.challenge_tester`, and a challenge whose refs add a decision row does not count against the per-criterion cap `LANDED_CHALLENGES`. No new edge." The sentence is about the route to the Tester. "No new edge" means no message edge. A `writes` edge to a fact artefact is outside its words.
- The words "a decision row" include the sender's own row. The skip narrows them. The review of 8d090e2e, finding 7, narrowed them the same way, so the narrowing has a precedent.

### 5. The id rule and frame 219

- The binder stages straight into `ctx.writes` and does not pass `decisions_author` (`rota/roles/api.py:8507-8511`). So frame 219's refusal in `api.py` would not cover the binder path. The binder needs its own check, and the design has one (3.1 item 3).
- A content id of 10 hex characters collides with another author's row only when that author chose the same id. Today `decisions_author` takes a seat's id freely. So the realistic case is the reverse: a Vision Keeper or an Architect copies a Developer's id from `decisions.search`. Finding 8.
- Pass 5 does not need frame 219 first.

### 6. The ends-when ratio

- The denominator is a query. Join `sessions.trigger_msg` to `messages` with `from_role = 'developer'`, `verb = 'challenge'`, and a `body_refs` id in `decisions` with `author = 'developer'`. The bodies come from `tool_calls` of `tests.encode` in that session.
- The numerator is not in a table. `harness.run` deletes the runs at the same commit (`rota/core/harness.py:154-156`). In bg_5 the head did not move after attempt 1, so `test_runs` held one run. The red of each body is in the next Developer wake's `[tests.load]` block in `turns`, as the cycle read did.
- "Red at the test's own assertion with the version message in the output" is a text match on that block. Name `turns` as the source, and write the match rule before the night.

### 7. The price

- The night read: `plans/operating-facts.md:368` says a night read costs about 270k to 330k on Opus (observed 272.3k). The design prices 150k. Night 143's cycle read, 206.6k, is a cycle read and not a night read.
- The implementer at 180k fits pass 4b's 182.1k. The review at 70k fits the anchor at `operating-facts.md:233`.
- This review and the resumed look on its fixes are cycles too. About 60k plus about 18k.
- Corrected: 6 to 7 cycles, about 600k to 700k in agents, one night.

## (b) Findings

1. `rota/core/sandbox.py:1358-1390` and `2148`, high, CONFIRMED. `_same_refs_rows(..., as_set=True)` compares the seat's refs with each prior's stored `body_refs`. The doors see the seat's refs before the binder appends the reason id. A reasoned prior stores `[c, tst, d_...]`, so it never matches `[c, tst]`. The probe matched `m1` (no id) and not `m2` (with id), both open. So the open-prior wait, the "they answered" refusal and the one re-send per version all go silent. Only the cap remains. Fix: compare refs with the sender's own `decisions` ids removed, in `_same_refs_rows` and in the `exact` test at `sandbox.py:1884`.
2. `rota/core/sandbox.py:1032`, `1139`; `rota/roles/api.py:8114-8116`, `13394-13396`, high, PLAUSIBLE. Four refusal hints and offers write `msg.challenge_tester(refs=..., quotes=...)` with no `reason=`. Two are gated by `_challenge_admitted`. If that check runs the reason door, the hints vanish. If it does not, each hint names a call the reason door refuses, which breaks frame 135's law. Two sites are in `api.py`, which the design's site omits and which is frame 219's site. Fix: name every hint site, decide whether `_challenge_admitted` runs the reason door, and add `api.py` to the site, with frame 219 ordered.
3. `tests/rota/test_laws.py:182-207`, low, CONFIRMED. The new `writes` edge makes the pair developer and `decisions` a blind writer, so `test_owners_can_read_what_they_own` turns red. Fix: add a `reads` edge developer to `decisions`, or an exemption with the derived-id reason that the ledger line uses.
4. `rota/core/sandbox.py:1012`, low, PLAUSIBLE. `_answer_mode_challenge_refusal` admits when `_holds_decision(refs)` holds, whatever the author. A Developer that puts its own existing id in refs bypasses the Architect's row route of pass 2e. The probe: `_holds_decision` is True on a `developer` row. Fix: apply the same author skip at that door and at the `keep` list at `sandbox.py:1130`.
5. `plans/frame200-pass5-design.md`, section 8, low, CONFIRMED by the anchor. The night read is priced at 150k against 270k to 330k. Fix: price cycle 5 at about 300k, and count this review and its second look.
6. `plans/frame200-pass5-design.md`, section 7 item 2, low, CONFIRMED by a read of `harness.py:154-156`. Per-body runs are not in `test_runs` when the head does not move. Fix: name `turns` and the `[tests.load]` block as the numerator's source, with the text rule.
7. `rota/core/identity.py:96`, low, CONFIRMED by read. `decisions` is declared a journal, "reasons as given", while the design cites law 14 for a content id. Fix: update the declaration to say the Developer's reason row keys on content.
8. `rota/core/db.py:463-478` with `rota/roles/api.py:8507`, low, PLAUSIBLE. A Vision Keeper or an Architect that copies a Developer's id overwrites the row by `UPDATE`. The author then changes, so `_carries_decision` exempts that prior again, and the Tester reads the other seat's text. Fix: record the dependency on frame 219 in section 3.3, and add a test that an overwrite does not lift the cap.

## (c) Probes

- `scratchpad/rvd5/p_graph.py`: loads `graph.json`, adds the design's edge to a copy at `scratchpad/rvd5/graph_plus.json`, runs `check_all`, compares `derived_contacts` and `latent_contacts`, and computes the blind-writer set of `test_laws.py`. Output: no problems, no contact moved, latent text changed, one blind pair (developer, decisions), and the Developer reads no `decisions`.
- `scratchpad/rvd5/p_samerefs.py`: an in-memory database with two open Developer challenges, one with a reason id. It calls `_same_refs_rows`, `_carries_decision` and `_holds_decision` from HEAD. Output: matched m1 only, `_carries_decision` True, `_holds_decision` True.

## (d) Usage

Estimated from the context counter, not from the harness line. Input about 105k, output about 12k, total about 117k.
