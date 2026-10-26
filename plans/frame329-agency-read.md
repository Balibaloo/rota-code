# Frame 329, the agency read: is the fix at the source?

Date: 2026-10-26. Read at 46e5c88b on `rota/foundation`. Read only, no pytest.
Register: a backup of `.rota/clickI.db` taken at about 21:05 after night 169
stopped, in this session's scratchpad as `n169_agency.db`. Meta workflow.

**Result: the fix is at one door of 5. It covers 4 of 5 instances of the reach.
The brief of `criterion_repair` still asks for the act that the door refuses.**
On night 169 that cost 7 twin refusals in 3 sessions before the seat wrote a
fact of its own (observed: section 3, instance B3).

## 1. The purpose

`criteria.respecify` closed the wall "a criterion, once written, cannot be
repaired": fd788bd1, 2026-08-26, for a Tester's unresolved question
(observed: `rota/DECISIONS.md` 1005 to 1010).
The twin door is the build session's own decision, commit 395535da of
2026-08-27, after eleven criteria for one item held two identical sentences
(observed: DECISIONS.md 843 to 848). Law 14 made the rule a law on
2026-09-01, after Roman's trial "ok lets test it out" of 2026-08-29
(ruled: Roman, 2026-08-29; observed: `rota/core/identity.py` line 10, commit
b72b76c9). Frame 306 put the fuzzy door `_near_twin` into respecify on
2026-10-24, commit 468fec42, after night 163 (observed: the commit). Commit
b0a2086e of 2026-10-09 sent his contest of a criterion row to this op. That
route is a build choice, not his words (observed: `plans/frame329-provenance.md`,
mechanism 2.3).

## 2. What exists

| Thing | Where (head 46e5c88b) | What it does for this case |
|---|---|---|
| `_staged_ticket` | `rota/roles/api.py` 5807 | Frame 329: the ticket of a staged write from the live row |
| `_staged_retired` | api.py 5825 | Frame 329: ids the session retires, no twin |
| exact twin check of `criteria.specify` | api.py 6028 to 6043 | Same words, same ticket, staged and on file |
| `_twin_refusal` | api.py 5879 | The exact-twin text, names empty sibling tickets |
| cap of `criteria.specify` | api.py 6061 to 6075 | Six per ticket, reads `ticket_id` of staged writes |
| `_near_twin` | api.py 6803 to 6855 | 0.85 overlap of `_prose_words`, staged and on file, the R2 tail |
| `criteria_respecify` | api.py 6858, `_near_twin` call 7059 | Stages `{text, surface_refs}` and no `ticket_id` (7069) |
| `criteria.retire`, `ruling_drops_line`, `_wake_allow` | api.py 6586, 6504; `rota/core/runner.py` 279 | Retire only on his drop words |
| `_ruling_answer_refusal` | `rota/core/sandbox.py` 1843, twinned set 1913 | The answer door counts a challenge after a twin refusal |
| `_respecify_record` | sandbox.py 2000 to 2027 | Keeps `respecify_refused`, `respecify_stands`, `respecify_twinned` |
| `criterion_repair.md` | `rota/roles/prompts/terminologist/` 22 to 31 | "For each criterion with contest or revise, rewrite it ... in the principal's words" |
| identity declaration | `rota/core/identity.py` 51 to 53 | Names `criteria.specify` only, a lint registry and no door |

The flag `criterion_twin` reuses frame 308's `criterion_stands` shape
(observed: sandbox.py 2015 to 2024). No overlay of staged rows exists in
`rota/`, so the fix re-derives no record that held the fact (observed: no
`_overlay` or `_merged` helper; reasoned: the frame 324 test).

## 3. The reach

The provenance places the cause: a respecify stages no `ticket_id`, so a
door that filters staged writes by ticket does not see a sibling the same
session rewrote (observed: provenance, "The result"). By wall-guide section 4
step 5 that is cause 6, "the rule did not read the rows it means", not
cause 8 (reasoned: the predicate was right and its rows were wrong). Behind
it is cause 10: his words give a row no fact of its own, and the mode holds
only a rewrite (observed: provenance, mechanism 3.6).

Gap A, the same input missing (staged criteria writes read by `ticket_id`):

- A1. Exact twin check of specify, api.py 6028 to 6043. Fixed.
- A2. `_near_twin`, api.py 6813 to 6822. Fixed.
- A3. The cap, api.py 6068. Left, harmless: the file read counts the row (observed: review 1, F2).
- A4. `_twin_refusal`'s `written`, api.py 5894. Left, harmless: a row on file covers its ticket (observed: `scheduler.py` 459 to 467).

Gap B, the same rule not covering the case (a contest whose fact a sibling holds):

- B1. The refusal of `_near_twin` named no act. Fixed by R2 (api.py 6836 to 6855).
- B2. The answer door refused every answer after a challenge. Fixed (sandbox.py 1906 to 1918).
- B3. The brief, `criterion_repair.md` 22 to 26, asks one rewrite per
  contested row in his words. Left. Night 169: his contest of crit_3 said
  "AppData Roaming if the roaming flag is True and ... Local if it is not,
  never under .config". s121, s128 and s145 sent that rewrite, and the door
  refused it 7 times at 0.941 against crit_2. crit_1 and crit_2 together hold
  that fact (observed: `turns` of the three sessions; `_prose_words` on the
  texts). s145 then wrote "must never be under ... .config", and crit_3 holds
  it at version 2 (observed: `criteria`).
- B4. `identity.py` 51 to 53 names one writer. Not counted: no door reads the map (observed: grep).

Gap C, 0.85 lets night 166's paraphrase pass at 0.82. Not counted: left on purpose (observed: provenance, open point 2).

**Count: 5 instances that act, A1, A2, B1, B2, B3.** A3, A4 and B4 are the
same shape and do no harm (reasoned: above).

## 4. The fix against the reach

The built fix, 1db6d00b, f153c773 and a875a798, covers A1, A2, B1 and B2. It does not touch the brief, so B3 stays (observed: `git diff 1db6d00b~1 a875a798`). The second clause holds 0 of 5, 0 of 4 and 0 of 1 tickets on nights 167 to 169 (observed: `plans/night167-read.md` 118, `plans/night168-read.md` 127, the backup). The status of 20:47, "crit_3 still says .config", was true at 20:44, and s145 landed new words later (observed: crit_3 version 2).

## 5. The proposal

Same fix, and one sentence more at B3. The door then catches what the brief
let through, and the brief no longer asks for it.

1. Keep A1, A2, B1 and B2 as built (observed: section 4).
2. In `criterion_repair.md` after line 25, add: "When his words give a
   criterion only a fact that another criterion of the ticket holds, do not
   write that fact again" (reasoned: night 169, B3; night 166, s194).
3. Add: "Write the fact that only this line holds, or send
   `msg.challenge_vision_keeper` with the criterion", the R2 tail's own acts
   (observed: api.py 6842 to 6849).
4. Name no retire (ruled: composition, "The tool never rules for the Principal"; provenance, open point 1).
5. Price: a door text shape, 2 cycles, about 20k of the holding session, an implementer resumed at 7k to 24k, a review at 61k to 76k, one gate with re-records, a night (observed: `plans/operating-facts.md` 239 to 247).

## 6. The doubt

- A brief sentence can change nothing for a 9b seat, and the tail already worked once in 3 sessions (reasoned: B3).
- I did not replay s121, s128 or s145 with the sentence, and I did not read the cassette scenes that hold the refusal text.
- I checked other tables only by a grep of `w[2].get(...) ==`, and found no partial rewrite read by a key (observed: api.py, sandbox.py).

## Verdict

`at one door of 5`: the fix covers 4 of 5 instances, A1, A2, B1 and B2.
B3 stays: the `criterion_repair` brief still asks a rewrite in his words when
a sibling holds the fact, and night 169 paid 7 refusals in 3 sessions for it.
