# Night 171, W4: an unasked removal lands, and the Architect calls it foreseen

Read-only provenance read, 2026-10-27, on Opus. Sources: the copy `scratchpad/w4/n171.db` of `.rota/clickI_night171.db` (sqlite3 backup), `.rota/clickI_night171.principal.jsonl`, `rota/roles/api.py`, `rota/core/sandbox.py`, `rota/core/lifecycle.py`, `rota/core/predicates.py`, `rota/roles/prompts/architect/touch_strayed.md`, `rota/LAWS.md`, `rota/DECISIONS.md`, `plans/composition.md`, the frame 339 block of `plans/stack.md`, `plans/frame339-agency-read.md`, `plans/frame339-s128-read.md` sections 0 and 5. Line numbers are at HEAD. `git diff 9827e38a HEAD -- rota/roles/api.py` touches none of the removal code, so night 171 ran the same code (observed). No code was edited and no model ran.

## 0. The result

**The removal door worked as frame 339 built it, and the stray route let the removal through.** Frame 339 changed the door from a refusal to a record (observed: 076ea892, 2026-10-26). s164's commit landed and wrote an open `touch_strays` row with the note `removal: if sys.platform == "darwin": at line 529` (observed: register). s172 sent `foreseen=["src/click/utils.py", ...]`, the bare file path. `batches_judge_touch` folds a bare path onto every definition row of that file, so the file judgement became the removal judgement (observed: api.py 22049-22063, s172's result "foreseen": ["src/click/utils.py::get_app_dir"]). No code compares the judgement with the principal's words or the criteria. No page that he saw shows the removal, and no page writer reads the records that hold it.

## 1. What "foreseen" means, and what the Architect reads

- **The call.** `batches.judge_touch(batch_id, foreseen, mistakes, reason)`, function `batches_judge_touch`, `rota/roles/api.py` 22010-22126 (observed). A foreseen grain writes a `batch_touch` row with confidence `expected` and a `touch_strays` row with status `foreseen` (observed: 22106-22113). The merge gate `mergeable` in `rota/core/lifecycle.py` 844-851 holds only on `open` or `mistake` rows of the head commit, so `foreseen` releases the merge hold (observed).
- **The meaning in the prompt.** `rota/roles/prompts/architect/touch_strayed.md`: "Foreseen. The work needed this file and your prediction was short." "A mistake. ... a change beside the work." The mode heading is "the head commit touched paths your prediction never named" (observed). So "foreseen" is a judgement on the accuracy of the touch prediction. The prompt asks no question about whether the principal asked for the removal (reasoned: the text).
- **The fold.** `_covers` at 22049-22059: a bare path judges each open row `path::name` (frame 286, b0dbd926, 2026-10-18). s172 named the predicted file `src/click/utils.py`, and that name covered `src/click/utils.py::get_app_dir` (observed: s172 turn 2 result). Its reason talks of the file and the prediction: "aligns with the prediction to handle APPDATA/LOCALAPPDATA unset" (observed).
- **The checks in the door.** The door refuses only these cases: no open row, a name that is both foreseen and a mistake, an unjudged row, and a code-free file in a new directory (frame 306) (observed: 22034-22105). Nothing reads `criteria`, the item text, `rulings` or `granted` (observed).
- **What s172 read.** One prompt with the results pushed in (observed: s172 turn 1):
  1. The wake detail: `src/click/utils.py::get_app_dir (removal: if sys.platform == "darwin": at line 529)`.
  2. `batches.expect`: his request in full, "In get_app_dir on Windows, when APPDATA or LOCALAPPDATA is not set, use the AppData Roaming or AppData Local folder ...", and the expected touch set with `src/click/utils.py`.
  3. `code.diff` with a `[removed lines]` block that shows the darwin branch and the XDG return.
  4. `criteria.scan`: c_1 and c_3 headlines, cut at about 120 characters.
- **The gap.** The material to judge was in front of the seat. His request names Windows only, and the diff shows the macOS and XDG branches gone. A qwen3:8b seat read the file as predicted and judged it in one turn (observed). The agency read of frame 339 named this risk before the build: "The Architect is a small model. It can judge a wanted-looking removal 'foreseen' ... a removal can then merge (reasoned; not measured on any night)" (observed: `plans/frame339-agency-read.md` section 6). Night 171 is the first measure.

## 2. Provenance

- **Law 12** (observed: `rota/LAWS.md` 337-342, from 27f02dc5, 2026-08-09, "docs: L0, and the laws, in the repo"): the touch set "is a *prediction*, never a permission — nothing rejects a diff for straying outside it. Its job is to make 'was this change incidental?' answerable at review time instead of arguable."
- **The stray route** was built at cf067ce4, 2026-09-13, "the committed diff is checked against the prediction, and the Architect judges the strays" (observed: `git log -S "def batches_judge_touch"`).
- **Roman's ruling** (observed: `rota/DECISIONS.md` 1486-1511, entered at 4f2bc79f): "File writes were always permitted everywhere, just that if there were unexpected changes then the architect is required to sign off. I thought we already discussed this, did you look into this?" (ruled: Roman, 2026-10-17 at about 16:50, in the terminal). The same entry keeps the fence's "a removal" as a backstop. The agency read shows that this word means file removal by `rmtree` and `unlink`, not a removed statement (observed: `plans/frame339-agency-read.md` line 27, `rota/core/fence.py` 38-42).
- **Removals on the stray route.** Frame 339 put statement removals on this route at 076ea892, 2026-10-26 (observed). The stack status of 2026-10-26 21:20 says "Judged here by C76: the agency read's proposal stands" (observed: `plans/stack.md`, frame 339). That is a session judgement that applies the ruling of 2026-10-17 to removals. It is not a ruling of his on removals (reasoned). The agency read records that the session first put option 1 to him at about 21:00, "The drop note becomes a row on the stopped page" (observed: agency read line 3). The records I read do not show his answer.
- **Frame 286** made the bare path cover its definition rows (observed: b0dbd926, 2026-10-18). No ruling of his is cited for the fold (reasoned: the commit's comment cites frame 286 only).
- **What must happen so that the removal is not invisible.** Law 12 asks that "was this change incidental?" be answerable "at review time". It does not name a page or a reader (observed). The composition says "no work stays invisible" and "Every open obligation stays visible and countable until something discharges it" (observed: `plans/composition.md` 8-9 and 50-51). It also says "Sign-offs after that, including on merges, are opt-in" (observed: line 23). The ruling of 2026-10-17 names the Architect as the one who signs off. No text that I found sends a judged stray or a removal to his page.
- **Does it reach his page?** No. The map tool lists no reader of `touch_strays`, `drop_notes` or a `foreseen` judgement in the page writer or `rota/roles/principal.py` (observed: `map table touch_strays`, readers are lifecycle, predicates and api only). The park page shows "The team expects to touch: ... src/click/utils.py" and not the diff or the strays (observed: m61's page).

## 3. Why the frame 339 removal door did not refuse s164

The door is designed not to refuse this case. The conditions:

1. s164 wrote in one reply and committed in the next. Completion 12 holds `code.write(... start=529, end=536)`, and completion 13 holds `code.commit` alone (observed: s164 turns).
2. The write result carried `"dropped": "This write removes or rewrites 1 statement that your text does not hold: if sys.platform == "darwin": at line 529."` and opened a `drop_notes` row (observed: register and turn 17 user text).
3. `Sandbox.begin_reply` (`rota/core/sandbox.py` 521-529, called at `rota/core/runner.py` 5087) cleared `ctx.reply_notes` before reply 13. So the `held` list in `_unread_drop_refusal` was empty (observed: the code, reasoned: the order).
4. The condition that skipped the refusal is `later = [(p, n) for p, n in later if not (opened[p]["lines"] or opened[p]["defs"])]` at api.py 21137-21138. A note of an earlier reply that names a line is dropped from the refusal, with the comment "Frame 339: the note of an earlier reply was read, so its removal lands" (observed). Then `if not held and not later: return None` at 21151.
5. `_removal_strays` (21175-21220) then found the line gone and unasked, and `code_commit` wrote the open stray row and the `removals` field (observed: 21045-21075, row on a46638f3).
6. The second commit 62199a7b: the write's note said "No note is open, and the commit is not held", because the dropped line was the batch's own line (`_base_held`, 20600-20605). `_removal_strays` raised the darwin removal again on the new head, because the a46638f3 row was still `open` and an open row is not "judged" (observed: 21198-21201, the second row).

The write door's own offer led to the span: "A write to start=529, end=536 replaces every line from 529 to 535. To make your change there send start=529, end=536 with line 529 of the file, then your text." s164 sent the span without line 529 (observed: s164's account in turn 22). The night 171 read's "the door did not fire at all" is true of refusals only. The record half of the door fired twice (observed).

## 4. bg_1's deferral and his pages

- **No page of night 171 shows the removal** (observed). In the 23 rows with `night` 171: "darwin", "macOS", "Mac OS", "Application Support" and "XDG" occur 0 times. "remov" occurs in m61 and m65 only, inside his own words "remove the open file test file". The single "XDG" row in the file is night 165's m67. `messages.body_text` on night 171 holds none of the words (observed: register).
- **The deferral is not what kept it off.** No page writer reads the records that hold the removal (section 2). The deferral then closed the last door: the shift page m_shift_get_app_dir_windows_m_p2 offered "later: put it aside until the new request is merged. Nothing more about it reaches you until then" (observed). bg_1 is `deferred` with head 62199a7b, and its head still lacks both branches (observed: `batches`).
- **If bg_1 resumes and its tests pass, the merge does not hold on the removal** (reasoned: the head row is `foreseen`, and `mergeable` holds on `open` and `mistake` only). The a46638f3 row stays `open` on an old commit, and no reader looks at it (observed: `mergeable` and `touch_strayed` read the head commit only).

## 5. Reach: every path by which an unasked base removal lands with no grant

| Path | How it lets the removal through | Night 170 | Night 171 |
|---|---|---|---|
| Per-write detection: no note | The note detector reads a same-target rewrite as a rewrite, not a removal (frame 173, 80440c1e). `_changed_kept` clears a note when every dropped line is a kept changed line. No note means no door and no stray | Used: s128's line 518, 0 `drop_notes` rows (observed: frame339-s128-read section 0). His words asked for that behaviour | Used in part: the note names only the darwin line. The XDG `return os.path.join(` left too and is not in the note (observed: note `lines` vs the diff). Why it was left out is not probed (reasoned: the text keeps a `return os.path.normpath(os.path.join(` line) |
| Per-write detection: the batch's own line | `_base_held` false gives "No note is open, and the commit is not held" | Not seen | Used on the second write. Harmless here, because `_removal_strays` re-raised the base line (observed) |
| The write door's span offer | The offer names a span wider than the change. A small model drops the first line | Not seen | Used: s164's span 529 to 536 (observed) |
| The commit door | `_unread_drop_refusal` refuses only a note of the same reply. A note with lines from an earlier reply passes by design (21137-21138) | Not used, no note | Used: write in reply 12, commit in reply 13 (observed) |
| A criterion or item text | `_asks_removal` on texts that are not his (criteria, the item) counts as asked, and no row is written (21492-21494) | Not used, no note | Not used: the row was written (observed) |
| A ruling's act | `granted(..., "remove", targets)` on the batch refs (21495) | Not used | Not used, no grant (observed) |
| The stray route: foreseen | The Architect judges a removal grain foreseen. Nothing checks the call against his words or the criteria | Not used, 0 `touch_strays` rows | Used: s172 (observed) |
| The stray route: bare path fold | A predicted file named as foreseen covers its definition rows (22049-22059) | Not used | Used: the fold carried s172's file judgement onto the removal (observed) |
| The stray route: judged grain | A grain judged foreseen is not raised again (21217), so a later removal in the same definition of the same batch lands with no row | Not used | Not used: no commit on bg_1 after s172 (observed: 2 rows) |
| The merge | `mergeable` holds on `open` and `mistake` of the head commit only. Merge sign-off is opt-in, and no page shows the diff or the strays | Used: walk 1 merged `get_app_dir` with s128's rewrite of line 518, which his words asked for (observed: `plans/night170-read.md` line 5, frame339-s128-read section 0) | Not reached: bg_1 deferred. The path is armed (reasoned) |

## 6. The code against rota's purpose

- **The code serves the ruling of 2026-10-17 in its letter.** A write lands, the unexpected change goes to the Architect, and the Architect signs off (reasoned: DECISIONS 1486-1511 against api.py 21045-21048 and 22106-22113). I find no departure from his words.
- **The code departs from the purpose on both halves** (reasoned):
  - "No work happens that the Principal did not ask for": the last check is one judgement by an 8B seat. The prompt frames the question as prediction accuracy, and the door checks the judgement against nothing. On night 171 the check passed a removal of macOS and XDG behaviour against a request that names Windows only.
  - "No work stays invisible": the removal, its note and the Architect's reason exist only in `touch_strays` and `drop_notes`. No page writer reads them, and the merge needs no sign-off from him. Law 12's "answerable at review time" holds in the register only.
- **The frame 339 change was a session judgement.** C76 applied the 2026-10-17 ruling, about file writes, to statement removals, and named the risk that night 171 measured (observed: stack 21:20, agency read section 6).

What the records leave open:

1. Whether his "the architect is required to sign off" covers a removal of behaviour that he did not ask for, or only a write to a file outside the prediction. His words of 2026-10-17 answer a question about a Developer restoring a definition.
2. Whether he answered option 1 of 2026-10-26 at about 21:00, "The drop note becomes a row on the stopped page". The stack status of 21:20 quotes no word of his.
3. Whether "review time" in law 12 means his review, the Architect's, or the Critic's.
4. Whether a `foreseen` judgement on a removal must cite a criterion or his words, and whether the bare-path fold of frame 286 should apply to a removal row.
5. Why the note left out the XDG return. This read did not probe `_changed_kept` on s164's write.
