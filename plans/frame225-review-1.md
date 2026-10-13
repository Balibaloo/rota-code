# Frame 225, review 1: commit fca24dbc, the fold of a contested note

Verdict: stands, with one high finding for the holder to judge. The fix repairs night 144's case. It also drops the principal's contest of a non-default note when the answer names no ruling for the item.

Rota workflow throughout. Worktree C:/Users/roman/rota_rv225 at fca24dbc. Reviewer: read-only agent, 2026-10-13.

## (a) Verdicts on the numbered points

1. Holds. The column is TEXT NOT NULL DEFAULT 'default' with an eight-word CHECK (schema.sql:566-569). A NULL or empty kind cannot exist in a current row. The `or "default"` branch is dead but harmless.
2. Holds for the new rule as written, with two low caveats. Every ledger.log row carries a seat-named kind. The Critic's two writers and frame_assign write no kind, so they land as default. Night 143's 37 Vision Keeper conflict rows are reconcile notes. The new rule changes the outcome for 10 of them.
3. Holds. CONFIRMED by probe: scope note contested, echo_json approved. The item reads approved, the verdict keeps approve, L9 is resolved, and the decision starts "overruled at signoff".
4. Holds. CONFIRMED by probe: default note contested, echo_json approved. The item reads contested and the verdict carries contest. The unchanged A1 test also inserts with no kind, so it reads default.
5. Two of three tests are red without the fix. CONFIRMED by running the parent's land() on the same fixtures. The scope test and the conflict test fail on the parent. The default test passes on the parent too, so it guards A1 and proves nothing about the fix.
6. Holds, with one low finding on the comments. The SELECT reads the new column correctly. The CR count of the commit is 0.
7. No reader waits on a contested non-default note. The finding goes the other way: the contest leaves nothing waiting, and the scope hold releases. See finding 1.

## (b) Findings

1. rota/roles/principal.py:1830. Severity high. PLAUSIBLE for the merge consequence, CONFIRMED for the fold.
   The probe landed {"L9": "contest"} alone on a scope, conflict, invented and finding note. Each time the item stayed draft, the relay refs were [], and L9 resolved. So the principal's words reach only a decision row that no predicate reads. A resolved scope row leaves HOLDING_KINDS in lifecycle._batch_notes (lifecycle.py:484-506), so the batch's scope hold releases. The batch can then merge with the scope change the principal contested. The design gives scope to the Vision Keeper with the principal final (frame204-design.md, table row 4). The old rule routed that contest to the Vision Keeper through the contested loop. Night 144's defect was narrower: the note's contest overwrote an explicit ruling on the item in the same answer.
   Fix: keep A1 for default, and for any other kind contest the item only when the answer names no ruling for the item: `if (is_default or row["about_ref"] not in answer_rulings) and ...`, with answer_rulings taken from per_item before the loop. The holder decides whether conflict and finding notes keep the new behaviour, because test 3 asserts it for conflict.

2. rota/roles/api.py:7979 (LOG_KINDS order) and api.py:10779, 10832, 10992. Severity low. PLAUSIBLE.
   The fold now makes the kind a routing fact, and the kind is a seat's word with a tie-break that puts default fifth. A note that fits default and scope becomes scope, and loses A1. Night 143 (D:/repos/rota/.rota/clickI_night143.db, read 2026-10-13) held 37 Vision Keeper conflict rows, all reconcile "the README says" notes. 36 were contested, and 10 of them are about decided items. The parent fold contested those 10 items. The new fold leaves them alone. That is likely the better outcome for a reconcile note, but no case renders it. The Critic's challenge_break and challenge_vacuous write default where the design names finding, so their contests still take the A1 path.
   Fix: stamp kind='finding' in the two Critic writers, and add one case for a contested reconcile conflict note about a decided item.

3. rota/roles/principal.py:1772-1778 and 1825-1829. Severity low. CONFIRMED by reading.
   The block comment above the fold still says that a contest "contests the row the assumption was about" for every note. The new comment calls every non-default note "a seat's claim about the record". The design's invented kind is "a value you chose", which is a choice and not a claim. The commit message names "an older row with no kind", and no such row can exist under the schema mark.
   Fix: say in the block comment that the fold applies to default only, and drop the claim about older rows.

4. Outside the points. rota/roles/principal.py:1810-1832. Severity low. PLAUSIBLE.
   The Critic's ledger rows have about_ref "items:X", a table-prefixed ref. item_provenance has no such id, so the observed guard never applies, and a contest writes per_item["items:X"]. This is unchanged by the commit, because those rows are default.
   Fix: resolve the prefixed ref to its row before the observed and stamped checks, or route Critic rows as finding per finding 2.

## (c) Probes

- C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/80cae596-3d3e-44f8-a0fe-b9ff034a378c/scratchpad/rv225/probe.py. The probe loads land() at fca24dbc and the parent's principal.py from principal_old.py beside it. The probe builds the test file's fixtures on a fresh init_db. The probe lands two answers for five kinds on both versions, and prints the verdict, the item approval, the ledger status, the decision and the relay refs.
- A read-only sqlite query on D:/repos/rota/.rota/clickI_night143.db: ledger counts by kind, author and status, and the provenance and decisions of the conflict rows. Result: 37 conflict rows, 24 observed, 10 decided, 3 with no provenance, and 36 "overruled at signoff".
- git show fca24dbc piped to grep -c for CR: 0.

## (d) Usage

Input tokens: about 60k. Output tokens: about 6k. Total: about 66k. The harness line holds the exact count.
