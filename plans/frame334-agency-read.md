# Frame 334, the agency read: the Terminologist's word-sense generator

Date: 2026-10-26. Read at 46e5c88b on `rota/foundation`. Read only. No pytest ran. The register was read from a copy of `C:/Users/roman/rota_cassettes_f323.db` in this agent's scratchpad.

Sources: the frame 334 block and the frame 326 block in `plans/stack.md`; `plans/frame326-provenance.md`; `plans/method/handoff-66edc387.md`; `plans/a1-seed-interview-at-intent.md`; `plans/frame204-review-1b.md`; commits c12ed6c2, d207a0bd, cf2898b0, f6ac0c5b, 882aa65e; transcript 66edc387, 2026-10-25 23:09 to 23:21; `plans/composition.md`; `plans/wall-guide.md` section 4.

## The result

The frame waits on a read that exists, and its design cannot make its own red test green (observed: cf2898b0, `l1_generators.yaml` 9 to 45, `predicates.py` 348). The "L3 question" was answered on 2026-09-12 at 15:22: the word-sense paragraph was not the cause of the L3 red (observed: cf2898b0). The cause the code shows is wider. Every shared base brief tells a mode to call `ledger.log`, and 25 modes do not hold the call (observed: a render of every mode, section 3).

## 1. The purpose

The mechanism is the word-sense branch of `terminologist/deliver`: take one sense of a word that could mean two things, define it, and log the taking with `ledger.log` against the ratified statement (observed: c12ed6c2, 2026-09-09). The wall was tipsAD: "rounded up to the nearest cent" and a glossary sense of "nearest unit" went unreconciled for 71 questions (observed: `l1_generators.yaml` 25 to 28). The commit is Level 2, piece 3, "the generators", of the A1 plan (observed: `a1-seed-interview-at-intent.md` 80 to 91). The A1 plan rests on Roman's ruling of 2026-09-03, "a usability priority", and on law 8, "nothing ships whose assumptions the principal never saw" (ruled: Roman, 2026-09-03, plan lines 1 and 26 to 30). The Terminologist's branch is a build decision, not a ruling (reasoned: no ruling names it). d207a0bd withdrew the paragraph and the tool at 14:48 on 2026-09-12, because it read the branch as the cause of the red on `L3-ratified-statement-becomes-a-term`. cf2898b0 corrected that reading 34 minutes later: "The paragraph was not that red's cause; it stays withdrawn for the tool-in-the-list reason" (observed: both commits). "Generator" in these records means a desk that writes assumption rows for the signoff page (observed: `l1_generators.yaml` 1 to 7, COMPLETION goal 5). No record names a generator that writes senses from the glossary, as the frame's title says (observed: grep of `plans/` and `rota/`).

## 2. What exists

| What | Where | What it does for this frame |
|---|---|---|
| The L3 answer | cf2898b0; `l3_handoffs.yaml` 45 to 50 | The paragraph is neutral on the bar model. The case is 2384 of 2384 on qwen3.5:9b, last run 2026-10-24 (observed: `case_runs`). |
| A wake keyed on two glossary senses | `rota/core/predicates.py` 348 to 581, f6ac0c5b 2026-08-14 | Wakes the Terminologist for one word with its senses as refs. In delivery it fires at once (observed: the comment at 377 to 380). This is the cause key that d207a0bd names. |
| The sense-taking line in the shared base | `terminologist/base.md` 41 to 43, fdad09df 2026-08-10 | "`ledger.log` when you pick one sense and the material did not settle it." Every mode on the default base renders it. |
| Modes that hold the call | `terminologist/criteria.tools`, `answer.tools`, `criterion_repair.tools` | A sense taken at criteria time is logged today (observed: the files). |
| The signoff present hook | `rota/core/sandbox.py` 4063 to 4073, c12ed6c2 | Carries open ledger rows about ratified statements onto the page. No mode with a brief shape writes such a row now (reasoned: the VK logs about `items`, and the Terminologist deliver lacks the call). |
| The kinds strip | `rota/roles/prompts.py` 100 to 120, 882aa65e 2026-10-11 | Drops the kind words where the mode lacks `ledger.log`. It keeps the sentence that names the call. |
| The role-level lint | `tests/rota/test_prompts.py` 124 to 152, 9a109336 2026-08-09 | Checks that a prompt names no call outside the role. It reads the role, not the mode. |
| The red marker | `l1_generators.yaml` 14 to 18, frame 326 | Sets `L1-TE-log-the-word-you-took-one-way` apart from the table. |
| The Architect's half | `architect/deliver.tools` holds `ledger.log` since 7da68101; `l1_generators.yaml` 47 to 53 | The tool is there with no brief shape. Its case was withdrawn on 2026-09-09. |

## 3. The reach

The frame places the cause as "an owed mode, never built" (observed: the frame block and the reply of 2026-10-25 23:10). The code shows three gaps under that sign.

Gap A, a brief names a call the mode lacks. The base brief lists "What you can reach, whatever woke you" for the whole role. Modes narrow the set since 7da68101, one day after the lint at `test_prompts.py` 124 was written for the role (observed: both commits). A render of every mode finds `ledger.log` named in 25 modes that lack it (observed: `compose` against `mode_tools`):

- architect, 9: annotate, ask, boundary, frame, grouping, guess, relay, structural_review, touch_strayed (`architect/base.md`).
- terminologist, 5: ask, deliver, question, relay, unresolved (`terminologist/base.md` 41).
- tester, 1: challenge (`tester/base.md`).
- vision_keeper, 10: ask, challenge, contested, elect, propose, question, relay, reorient, signoff, unresolved (`vision_keeper/base.md`).

Over every call, 56 modes name 301 calls outside their set. `terminologist/deliver` names five: `brief.list`, `criteria.consult`, `ledger.log`, `msg.answer_tester`, `msg.challenge_vision_keeper` (observed: the same render). A wake adds some answer verbs, so 301 is an upper bound (reasoned: `sandbox.py` 655 to 692, per frame 326's read).

Gap B, an owed generator held only in words: the Terminologist deliver (the red case) and the Architect deliver (the withdrawn case) (observed: `l1_generators.yaml` 9 to 53). Count 2.

Gap C, records that carry the superseded L3 reading: `l1_generators.yaml` 19 to 24, `plans/frame326-provenance.md` 52, `plans/method/handoff-66edc387.md` 30 to 32, and the frame block's "Waits on" line (observed: the four texts). Count 4.

Total reach: 25 modes for the call this frame is about, 2 owed generators and 4 stale texts, 31 instances (reasoned: the sum).

## 4. The fix against the reach

The frame proposes a new mode keyed by "a statement word with two glossary senses at deliver time" (observed: d207a0bd, the A1 plan 152 to 157). It covers 1 of 31: the Terminologist's generator. It leaves the 25 invitations, because `terminologist/deliver` keeps `base.md` 41 whatever a new mode does. It leaves the Architect's half and the 4 texts. Its red test cannot go green by the design. The case seeds no glossary row for `archive` (observed: `l1_generators.yaml` 29 to 35). So a scheduler key on glossary senses never wakes on it. The key it names already exists as `term_collision` (observed: `predicates.py` 348). Whether an undefined word could mean two things is a judgement inside the seat, not a fact the scheduler can see (reasoned).

## 5. The proposal

Not the same fix. Five lines, at the renderer and its lint:

1. Rewrite the frame's wait from cf2898b0 and `case_runs` 2384 of 2384. The L3 question is read, and nothing waits (observed: cf2898b0).
2. Move the lint at `test_prompts.py` 124 to `compose(role, mode)` against `mode_tools(role, mode)`, and allow the answer verbs a wake adds. It goes red on the modes of section 3 (reasoned: 7da68101 narrowed modes after 9a109336).
3. In `prompts.base` and `fill_kinds`, `prompts.py` 68 to 120, drop each base sentence whose bold call the mode lacks. This widens 882aa65e from the kind words to the call (observed: `frame204-review-1b.md` N1 named the older invitation, and the fix took only the words).
4. Measure the Terminologist deliver once on qwen3.5:9b with c12ed6c2's paragraph and `ledger.log` restored: the L3 term case, `L1-TE-log-the-word-you-took-one-way` and `L1-TE-amend-glossary`, 5 runs each. Restore the branch if all three hold (reasoned: c12ed6c2 held amend-glossary at 5 of 5, and cf2898b0 found the paragraph neutral).
5. If the measurement fails, retire the case with its `red:` reason. A sense taken still gets its row at criteria time (observed: `criteria.tools`, `base.md` 41).

Price, from the anchors in `plans/operating-facts.md` 239 to 247. Lines 2 and 3 are a door text: 2 cycles, an implementer pass of about 74k and a review of about 70k on Opus. Line 4 is 1 cycle of about 40k to 60k on the register. Line 1 is a status line. In all about 4 cycles, about 40k of the holding session's context and about 200k agent tokens. Caution: line 3 changes the prompt of up to 56 modes. Every case in those modes goes stale, and the re-records need the card (reasoned: a prompt change makes a case stale).

## 6. The doubt

- The 301 count is not classified. Some named calls sit in "do not call" sentences or come with the wake. The 25 `ledger.log` modes are exact (observed: the render).
- I did not count refused `ledger.log` calls on nights or in the register. A zero count makes gap A cosmetic, and line 3 then buys little for its re-record cost.
- I did not run `python -m rota.tools.rulings` on the tool-in-the-list rule. Its memory is not in `memory/archive/` (observed: frame 326's read), so its weight against a measurement is unknown.

## Verdict

`wrong premise`. The frame waits on an L3 question that cf2898b0 answered on 2026-09-12: "The paragraph was not that red's cause; it stays withdrawn for the tool-in-the-list reason." The mode it owes is keyed on two glossary senses, `term_collision` already wakes on that key, and the red test seeds no sense. The cause by the code is a shared base brief that names `ledger.log` in 25 modes that lack it, under a lint that checks the role and not the mode. Against that reach, the frame's fix covers 1 of 31.
