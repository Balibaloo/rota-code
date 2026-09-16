# The decision register: rulings

This file holds the principal's rulings. Each ruling is one dated paragraph.
The argument behind each ruling is in `plans/archive/completion-diary.md` and in the git history of `rota/DECISIONS.md`.
Rewritten 2026-09-13.
Rulings R1 to R17 of the responsibility audit (2026-09-02 and 03) are in
`plans/archive/responsibility-audit.md`. `rota/COMPLETION.md` cites R2 by number.

---

## Settled

### The researcher owns nothing shared

(undated in source) "It answers a message and writes only its own `references` rows. The **asking** role decides whether to cite, and citing means writing into the artefact that role already owns." A role can ask if it can cite. Law 3 derives the contact list from that edge. See MAP.md.

### The researcher is never woken by a predicate

(undated in source) "Predicates are defined by what they drain. The researcher owns nothing shared, so a predicate waking it would have nothing to drain and would fire forever." External push works through the owner. The drift predicate wakes the role whose artefact cited the reference. That role asks.

### A new role is justified by a trust boundary, not a capability

(undated in source) Git history is read tools on the roles that need it. The internet is a role, because it is not local, hermetic or replayable.

### Drift is scoped to exactly what has been cited

(undated in source) "Commits are the unit. Diff to files, files to grains, grains to citations, citation to the artefact, artefact to its owner — and the owner is woken." The watched set is derived, never configured. Drift resolves at path granularity until line spans are persisted in `code_index`. See MAP.md.

### No deployment role

(undated in source) "It splits three ways: a **gate the principal owns**, an **environment concern** under 3Bd, and **runtime observation** under Tester." Deployment is a gate rather than an act.

### Declarative infrastructure only

(undated in source) "The file is a diff, writing it satisfies a criterion, `plan` or `what-if` is the test, Critic reviews, and `apply` is the principal's gate." Credentials belong to the environment, not the role.

### The domain allowlist is configuration, not an artefact

(undated in source) An allowlist is a cap. Law 7 puts caps in `config.py`, owned by the principal. An unlisted domain is not an error path. It folds into the researcher's ordinary "I could not find out, and here is what I tried" answer.

### Research spends a third kind of scarcity

(undated in source) "`loop_cap` spends compute. `interrupt_cap` spends the principal. A research cap spends the outside world — rate limits, and trust surface." A third scarcity gets a third cap.

### Fetched text is never instruction

(undated in source) "Queries are **constructed** from the question, never forwarded." Context the asker puts into a question is for the researcher's understanding and must not reach the wire.

### The researcher does not know the system

(undated in source) "No batches, no criteria, no constraints. Questions from roles, answers with sources."

### Git: do not rebase mid-batch

(undated in source) A verdict is a judgement on a specific commit. "Reconcile at merge; an unclean merge is a wake, not a silent auto-resolve." "PR versus auto-merge is a config switch, not an architecture decision."

### Test files are indexed but not partitioned

(undated in source) Roles can read tests as evidence. Test directories do not become areas of their own.

### The first target is oauthlib, as a fork

(undated in source) "Fork only. No PR is opened against oauthlib." `gh` is out of scope. "icalendar is second, once test partitioning is fixed." "Upstreaming can be decided later on the merits of an actual diff."

### Onboarding is three questions before it is a pass over areas

(undated in source) Orient, then define, then the per-area survey. "Strict phases, derived from the rows by `scheduler.onboarding_phase`, each written with the previous phase's artefact in front of it." "The per-area Vision Keeper pass is withdrawn (not deleted)." `onboarding_phases` is a setting, so `survey` alone stays runnable. See MAP.md.

### Onboarding runs twice

(undated in source) "Once with the researcher unavailable to survey modes, once with it available."

### The operator's interface: the seat drives, the cockpit answers

Four rulings. Argued in SEAT.md.

(undated in source) "**The cockpit is read-only, always. The TUI drives.**" Everything with an intent is the seat's. Everything with a question is the browser's. The run list is the seat's.

(undated in source) "**A run that cannot be read is named, not migrated.**" `ls` reports `stale` and the reason and touches nothing. Databases stay throwaway. No migration path is promised.

(undated in source) "**Closing the seat stops the run, so quitting takes a confirmation.**" The confirmation must be cancellable. `src/ui/modals.py` is the thing to reuse.

(undated in source) "**A survey is a receipt for a tree, and must be signed like one.**" Survey records carry the commit their evidence was gathered at. See MAP.md.

### The scope role is Vision Keeper

2026-08-23. "**Decided 2026-08-23: the role is `vision_keeper`, "Vision Keeper" in prose**". Recordings made against the old briefs are invalid and were re-earned. Old run databases are re-onboarded rather than migrated.

### Intake has three answers and its brief offered two

(undated in source) "**Decided: an ordered test, not a default.** Three questions asked in order, stopping at the first yes -- does it ask for something the program does not do yet; is it a question about the program as it already is; otherwise chat -- with the first test given the discriminator that separates the two hard cases: work is *told* to you, a question is *asked* of you." One message gets one answer. "`answers_given` names the three answers once and each channel declares which one it is." See MAP.md.

### The worked example decided it, and one example was the answer

(undated in source) "One corrected example and no three-owner block scores at least as well as the shipped brief on both models in both passes, and strictly better on `qwen3:8b`'s chat column. That is what shipped."

### Two models disagreeing is a diagnostic, not a portability problem

(undated in source) Prompts should not be model dependent. The rule is a check, not a policy. "helps both -> ship it". "helps one, hurts the other -> do not ship. It is emphasis, not a fix, and the structural form has not been found yet". "helps neither -> the diagnosis was wrong". "No per-model brief mechanism is needed and none should be built." `llama3.1:8b` stays the recording model. `qwen3:8b` stays the second detector.

### A guard is only fair when the escape it assumes is built

(undated in source) "A refusal is bounded only if the session can satisfy it **or say why it cannot**, and both have to be reachable in the mode, not merely in the graph." The refusal "an answer must name the rows it came from" is narrowed to answers to Liaison. The escapes are derived from the graph by tests. See MAP.md.

### Pushing more of the artefact is not the same as pushing the right part

(undated in source) "**A session starved of the thing it is being asked about answers from nothing, and a session given more of what it already had answers from the extra.**" The push of constraint bodies was reverted (undated in source). "Not settled as "never push constraint bodies"".

### An inquiry reaches every owner, because choosing one is not Liaison's to do

(undated in source) "**Decided: it is not a choice, so the choice is gone.** One `msg.ask_*` call stages the ask to every owner the graph allows this role to ask." The cost of three read-only sessions per question is paid knowingly.

### The hedge was carrying the answer

The refusal of a relay that ends in a question mark was tried and reverted (undated in source). "So the trailing question was not the disease."

### A confirmation names a statement, or it is refused

(undated in source) "**Resolved by the channel.** `msg.confirm_principal` refuses any ref that is not a statement -- on file or staged this session -- with the way back named: segment first, confirm the ids." A new refusal goes in with a re-record and not beside one.

### The message that opens with something other than itself

(undated in source) The question-mark cue does not ship. It helps one model and hurts the other. "The brief that ships is the one measured back when `w-sso` was still failing, unchanged." The open fixture, `w-sso` on `qwen3:8b`, is not open as a brief question. "The next attempt should be structural or should not be made."

### The election is a real choice, and the lazy half is blocked on the ledger

(undated in source) The stories define the election: "confirm the whole baseline up front, or lazily as work first touches each area. The principal's call, not the system's." The lazy path was blocked on the ledger's prose field. The ruling of 2026-08-26 below unblocks it.

### The ledger's prose field is named like a flag

A guard that refuses non-strings was tried twice and reverted twice (undated in source). 2026-08-26. "**Decided 2026-08-26: the parameter is `assumption`.**" "The parameter is the model-facing surface and the only thing renamed: the schema column stays `default_taken`, so old run databases stay readable." Whether the id hash should name the field at all stays open.

---

## Amendments the settled column forces on LAWS.md

### Law 11 — provenance gains a third value

(undated in source) "Proposed: **`cited`** — found outside the repository, attributable to a source, and the only kind of claim that can become false without anyone touching the project." This is a schema change, not a convention.

### Law 13 — the retrieval date

(undated in source) "Resolution without amending the law: **the date is for a human, not the system.**" `references` carries `content_hash` and a retrieval sequence. The real timestamp lives in the fetch cache, which is evidence and therefore outside the law.

---

## Open

### Six things filed past at speed, written down before they vanish

2026-08-28. Ruled: "determine root causes instead of fixing". The law every healed organ rediscovered: "**identity derives from content, never from a model-invented id**". Proposed for the seat: write the identity rule into LAWS.md as a law.

(undated in source) The silent worktree skip is left as-is knowingly. `batches.worktree = NULL` still cannot say why.

2026-08-27. At the interview, on whether the system may tune its own meta-config. The principal's floor: "approval is the minimum." Roles stay config-blind and config-mute, and the design rule is to keep not building that door. "State may heal itself under caps (quarantine, deferral — already true); policy may at most be *proposed*, by mechanical detectors, as evidence-bearing trail rows that wait on a ruling."

2026-08-27. Vocabulary, same interview. "Human-facing surfaces say *proposed* / *preliminary* for what onboarding extracts, and *adopt* for the accepting act — `rota adopt` (elect kept as an alias), matching `glossary.adopt` and `model.adopt`. The internal stamp stays `provenance='observed'`". `config_history` shipped memo-free on the principal's one-line review: "it will never be used".

### Harness facts are refused at the door; judgement stays with the roles

2026-09-02. A fact about the harness is refused at the door. A judgement stays with a desk and climbs to the seat. "The line is kept deliberately: whether "display" means return or print is a judgement". See MAP.md.

### The triage collapses to can/cannot; the ladder does the diagnosis

2026-09-01. "**Ruled 2026-09-01, built the same day.** The seat's words: the new ladder "is a displacement of the difficulty, but worth trying to see if it opens up more novel solutions."" `tests.triage` accepts `cannot` as a complete verdict routing to the Terminologist. One open question per criterion. See MAP.md.

### A criterion, once written, cannot be repaired

(undated in source) `criterion_repair` is register entry #25. "A tester's unresolved criteria-ref question wakes the Terminologist in a writing mode, once per question; `criteria.respecify` is the door". See MAP.md. 2026-08-29. `hold-a-test-that-is-right` is held. The case declares its bar model. The recording model's red stays as its per-model record.

### The delivery wall, named: a criterion must carry a callable surface

2026-08-26. "**Built, 2026-08-26.**" Criteria carry their surface the way they already carry their terms. `criteria.surface_refs` is vetted at both doors against the symbol index. "A name with no neighbour is greenfield intent and kept." See MAP.md.

### The frontier, when several things are ready

2026-08-28. "**Ruled and built, 2026-08-28.** The principal reversed the gating — "the frontier ordering should be logical, do before onboarding"". "The rule is **band, then declared order, then age**." No sort key in the scheduling path reads a predicate's name. See MAP.md.

### Over-production has a ticket flavour, and no guard can tell it from work

(undated in source) Two guards stay: "a ticket is its text", and "the same words are the same ticket". `L1-VK-slice` "stays red as the register's record of it, at 4 against a measured bar of 1..2, rather than the fixture being tuned until it looks better."

### Re-surveying

2026-08-27. "**Built, 2026-08-27, by content rather than commit.**" Survey records stamp the area hash they attested against. `rota refresh` is the operator door. See MAP.md.

### What deterministic checks cannot catch, and what stands there instead

2026-08-29. The principal's correction: "deterministic checks can't catch all errors here." "The system's claim was never "no errors" — it is "no invisible, unattributable, irreversible errors"". The gauntlet outranks every lint.

### The world-audit, and what its first pass found

2026-08-29. Built from the principal's worry: "bugs in this system will only show with extended use and be really hard to spot." `rota.tools.audit` runs the laws as propositions over any run database, read-only. `LEGACY_LABELS` is history, not exemption. "A new label joining that set is a regression that must argue its case." See MAP.md.

### Challenging a test costs less than fixing the code

2026-08-26. "**Ruled and built, 2026-08-26.** The principal's whole ruling: "why is this not obvious?"" `challenge` carries `quotes=` on all five of its channels. The binder refuses a paraphrase. The developer to tester channel must name and quote both sides. See MAP.md.

---

## Assumptions

### The seed interview runs at intent-time, and the signoff page is its first moment

2026-09-03. "Ruled 2026-09-03 ("lets do this now, this is a usability priority")." "Two things ruled. The interview runs at intent-time too: a statement gets the account first (`how_it_works`, the item orient already writes for a repository), and what the words left silent is logged where a desk had to assume it. And the page the principal signs carries those assumptions". Approve is the keypress that takes the default. Contest with words goes back to the desk that assumed it. "No new artefact, mode, predicate, edge, or gate". ""Derive it" stays the default and nothing waits on a question". Design and build order: `plans/a1-seed-interview-at-intent.md`.

### The seat's four pages are one surface (2026-09-12)

2026-09-12. Roman ruled: "the interview, the touch guess at signoff, an amendment, and a conflict between sources are four kinds of page at one seat, answered in words through one door (`principal.land`). Not four features."

1. "**The interview is iterative, most important first.** The page shows the assumption that changes the most, or the few that all do. The answer lands, the desks re-derive, and the next page shows what is still open. An answer that settles three questions removes all three. Nothing is asked twice."
2. "**Hold at intent time only.** No batch starts until the first page is answered. After that, nothing waits on a page."
3. "**Amendment at level 2 now, level 3 measured.** An amended item cancels a running batch built from it and re-batches. A merged batch stays, and the amendment is a new batch on top. Level 3, invalidate by touch (only the criteria the amendment touches are re-tested), is the upgrade, gated on a walk that shows level 2 wasting real work. Level 1 (restart all) and level 4 (propagate through findings to every owner) are recorded and not chosen."
4. "**Conflicting sources always ask.** Two documents in the repository that disagree are put to the principal, never resolved by recency or by preferring code. Roman's reason: a conflict page that never appears on a repository with conflicts shows the tool is failing."

### The seat as an exchange (2026-09-12)

2026-09-12. "Ruled: the seat is tested as an exchange with the Liaison, in both directions, with the agent as the principal." What that finds is pinned as page-sequence cases. Design and findings in `plans/seat-exchange.md`. "Roman at the TUI with his own sentences stays the final test, after click merges cold."

### The principal's flow: five rulings (2026-09-13)

2026-09-13. On `plans/principal-flow.md`. Roman ruled:

1. "**Click first.** Stage 1 (one ticket per Developer session, the slice read, `batches.depend`, the worked example) waits for click's first cold merge on the batch unit, which is the control. If click's last red is the Developer session being too large for one call, that red is stage 1's case and the switch happens then."
2. "**There is no silence.** A page is a hold or a note. A hold waits on a keypress and the batch defers; a note waits on nobody, stays owed on the register, and a contest after the work is an amendment under law 9. No predicate reads a clock, wall or step. "Silence approves" is gone. On the plan path the slice read is a note."
3. "**The shape holds the memory, not the repository.** Rows are the callables a criterion or a design page ever named, observed from the index when a page first names them. The index keeps the rest."
4. "**The Critic's cost is accepted.** The relief is band order: the Developer's next ticket is offered before the Critic's review of the last, so reviews queue and the model swap is per batch. The price, a fail on ticket 1 found after ticket 3, is measured against the other order on tipsI before either is chosen."
5. "**Defaults are measured by a person first.** Hold at design time and default to the plan path do not ship as defaults until Roman has driven one batch on each path at the TUI."

---

## To check before this replaces DECISIONS.md (drafted 2026-09-13)

The draft keeps 59 rulings in 226 lines from 1,425. Nineteen entries need a
person's eye; source line numbers are DECISIONS.md at commit 09acac6.

1. Lines 33 to 201, the Settled column: the source never says who decided
   them. Kept as undated rulings. If only Roman's rulings belong here, most
   of the column goes.
2. Lines 323 to 345, the worked example: a brief-tuning outcome, kept.
3. Lines 618 to 649, "Should we build this?": dropped, no ruling.
4. Lines 651 to 672, the election: quoted from the design stories, kept.
5. Lines 750 to 758, law 11: the source says "Proposed"; kept with that word.
6. Lines 808 to 820, the fourth organ: dropped, a build and no ruling.
7. Lines 853 to 871, deferred-eager rows and rulings in config: dropped as open.
8. Lines 859 to 866, the worktree skip: kept, unsure whose decision.
9. Lines 926 to 959, harness facts refused at the door: kept, dated 2026-09-02.
10. Line 995 names a one-model ruling the source never records; not invented.
11. Lines 1039 to 1076, the delivery wall: built 2026-08-26, no ruling; kept.
12. Lines 1112 to 1129, keeping `L1-VK-slice` red: kept, undated.
13. Lines 226 to 244 and 1131 to 1154, survey commit versus content hash: both kept.
14. Lines 1194 to 1221, the world audit: Roman's worry is quoted; kept.
15. Lines 1223 to 1227, conflicting sources: dropped, the 2026-09-12 ruling covers it.
16. Lines 1156 to 1165 and 1281 to 1293: dropped as open items.
17. Lines 1295 to 1319, the assumptions list: dropped; the heading stays.
18. Lines 175 to 193, onboarding: the source says three phases, the build has four.
19. Lines 144 to 156, git: the `batch_dep_facts` sentence dropped as a consequence.
