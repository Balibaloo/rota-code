# Frame 274, review 2: pass 1b at 6553d0f1

Read-only diff review on the worktree `C:/Users/roman/rota_r274b` at 6553d0f1 (observed: 2026-10-17).
Verdict: accept. Findings: 0 high, 2 low. The test file passes 21 of 21.

## (a) Verdicts

1. The description case: CONFIRMED. Case 1b contests `how_it_works` at 6553d0f1, as at the base. At db1296e1 the item stayed `draft`. The two predicates match on every item row.
2. The three right cases and the red case: CONFIRMED. Cases (a), (b) and the red case hold by probe. Case (c) holds by test 471 and by a read of `page_request`.
3. The hunk alone: CONFIRMED. No circular import exists. A module-level import is safe, and the gain is negligible.

## (b) Findings

1. LOW, CONFIRMED. `rota/roles/principal.py:1987` imports `_is_description` inside the loop. `principal.py:26` already imports `new_id` from `rota.core.runner` at module level. `import rota.core.runner` does not load `rota.roles.principal` (probe 3). So a module-level import is safe. The local import costs one `sys.modules` lookup per carried note, so the cost is negligible. The local form matches `off_page` (line 946) and `page_request` (line 918). Fix: none needed. Optionally move `_is_description` into the line 26 import.
2. LOW, PLAUSIBLE, outside the points. `off_page` (line 953) sets `req` to None when `current_request(conn, unread=False)` is empty. The carrier (line 1986) calls `page_request` with no such gate. In a run where no request is open, `off_page` keeps a note of an earlier request on the page. The carrier then still skips its contest when the page reaches a newer request. The two disagree only when every request is closed. No case renders that shape. Pass 1 introduced the difference, not pass 1b. Fix: gate `page_req` on `current_request(conn, unread=False)` as `off_page` does, or record why the carrier differs.

Point 1, the predicate check. `off_page` exempts a row when `all(_is_description(conn, i) for i in _items_reached(conn, ref))`. The carrier exempts `row["about_ref"]` when `_is_description` holds for that ref. For an item ref, `_items_reached` gives the item itself, so the sets match. A note's `about_ref` that is not an item (a statement or a test) gives False in both. Both read the same column, and both give False on a run database that predates `is_description`. So no row shape exists that one exempts and the other does not.

Point 2, case (c). `page_request` (lines 915 to 935) returns the newest request that any ref reaches. A note on the page reaches its own `about_ref`. So a page gives None only when no ref reaches a request item that is open and not a description. Then a note's `about_ref` is a description, an item with no statement, or an aside item. The first two give `owner` None. For all three, `page_req is None` keeps the carrier. Test 471 (`..._on_a_page_with_no_request`) passes and covers the account page.

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/1cf2843b-91ea-4332-96ca-93eb8010ff0b/scratchpad/r274b/`.

1. `probe.py` is review 1's probe, extended to load three versions: the base (`principal_base.py`, from db1296e1~1), pass 1 (`principal_p1.py`, from db1296e1) and the worktree at 6553d0f1. Results on the `_two_requests` fixture:
   - 1a own item, page e_p2: `contested` in all three.
   - 1b note about `how_it_works`, page e_p2: base `contested`, pass 1 `draft`, pass 1b `contested`.
   - 1c item with no statement: `contested` in all three.
   - 1d description-only page with a note about `echo_json`: the page resolves to e_p1, so `contested` in all three.
   - 3, the m59/m60 red shape, page e_p2, note about `echo_json`: base `contested`, pass 1 and pass 1b `approved`.
   - In every case the note resolves with a decision that starts `overruled at signoff`, and the verdict keeps `l1: contest`.
2. `probe_c.py` tried to build a page with no request around a note of e_p1. The note itself reaches e_p1, so `page_request` gave e_p1 each time. This supports the read of point 2, case (c).
3. `python -c "import rota.roles.principal"` loads clean. `import rota.core.runner` leaves `rota.roles.principal` out of `sys.modules`.
4. `ROTA_MODEL=qwen3:8b python -m pytest tests/rota/test_signoff_assumptions.py -q`: 21 passed in 4.29 s. The red-case test (line 396) asserts the relay: the message stays open, the verdict carries `l_a5ef6d4cd8: contest`, and the owner is `developer`.

## (d) Usage

The harness line holds the exact count. Estimate: about 25k input tokens and 6k output tokens, about 31k in total.
