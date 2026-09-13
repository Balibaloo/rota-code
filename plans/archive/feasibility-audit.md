# Phase 4 — feasibility audit (bottom up)

Companion to [quality-dependency.md](quality-dependency.md), whose choke
ranking sets the order here. Per mode: does brief + pushed context +
namespace + harness let a **mid-capacity model** produce the quality type
phase 3 assigned? Empirical record (case_runs, 91,661 rows) outranks my
judgment wherever both exist.

## Baseline classification (corrects the earlier "9 failed")

Of the suite's 9 non-passing model cases, **4 are STALE** (no cassette for
the current prompt — unknown, not bad; caused by the in-flight
`vision_keeper/slicing.md` brief rewrite and related edits):
`L3-scope-becomes-a-ticket`, `DV-fix-the-code`, `VK-amend-a-contested-item`,
`CR-fail-names-its-criterion`. Re-earned 2026-09-02: the first three came
back **green** — the in-flight slicing rewrite measures green on its
downstream cases — and `CR-fail-names-its-criterion` came back **0/5 red**
with the guard-overreach cause below (P11).
**5 are true reds**, all matching COMPLETION.md's attributed list:
`TS-apply-a-term` (transcription), `LI-present` (both models invent label
refs), `TE-words-already-defined`, `CR-a-test-that-encodes-nothing`
(judgment), `L3-a-challenge-reaches-the-role` (judgment).

## Tranche 1 — the done-chain (S5/D3): Tester and Critic

**Tester `tests_missing` (triage + encode) — ADEQUATE, and the model case
for the whole design.** The brief carries the worked encode shape (the
measured lever that recovered `TS-encode`: 5 greens after 7 reds), the
collapsed can/cannot triage with the ladder behind it, the sharp desks as
optional refinements, and the honesty line ("a routed criterion is a job
done, not a job dodged"). Namespace complete: every instructed act has its
tool, all three question channels present. Precision demands are carried by
door guards (executable bar, harness facts, invented-literal detector), so
what's left to the model is within the measured 8B envelope.

**Critic `review` — two chronic reds, one under-specified three-way fork,
and a measured guard overreach (P11).** The mode's namespace offers three
acts — `verdicts.emit`, `msg.challenge_tester`, `msg.challenge_developer` —
and the brief differentiates only the first two; `challenge_developer` gets
no sentence anywhere in base or mode brief. The two reds are the two sides
of that gap:

- `CR-a-test-that-encodes-nothing` (12 straight): the model emits a verdict
  (headline act) where the state calls for `challenge_tester`.
- `CR-fail-names-its-criterion` (re-earned 2026-09-02, 0/5): the model
  produces the **correct** verdict — fail, criterion named — four times,
  and a walk-born guard refuses it each time because the model also sent an
  unguided `challenge_developer` first: "you have already challenged the
  developer this session… a verdict on top of it would judge what you just
  said is in dispute." The case was green before that guard existed. This
  is the guards-share-signals interaction measured on the register: a guard
  built for the walks locks a register case out of its expected act.

Resolution is a design ruling, not an audit edit — three candidates, each
with different blast radius: (a) narrow the guard (a challenge naming the
same criterion as the fail is not "in dispute" — the established overreach
class, two removed last pass); (b) brief the three-way fork (when is
`challenge_developer` the act — likely only the something-nobody-asked-for
judgment); (c) drop `challenge_developer` from review's tools if it has no
situation the verdict doesn't cover — SYSTEM.md's own "a capability with no
situation" standard. Whichever lands must re-earn both cases on one load.

**Outcome (ruled R13, re-recorded 2026-09-03):** recipient-scoped guard +
brief sentence landed. `CR-fail-names-its-criterion` **re-earned green**.
`CR-a-test-that-encodes-nothing` stays red in its pre-existing attributed
shape — the model emits the fail verdict *first* (following the brief's
numbered order), then challenges the tester too late; my sentence governs
`challenge_developer` and never touched this. Two levers remain, unruled:
reorder the brief so per-criterion step one is "does its test encode it? if
not — challenge and stop, before any verdict"; or the structural fork (a
mandatory per-test claim before `verdicts.emit`). The re-record also
**exposed a mis-authored chain**: `L3-a-failed-verdict-turns-into-a-fix`
declared its second leg as a message handoff and had only ever passed via
the old guard forcing `challenge_developer` — the wrong route wearing the
right name. Re-declared as `tick: verdict_failed` per the harness's own
doctrine; re-earning.

**Critic `challenge` — EXEMPLARY.** Quote-bar on both verdicts, the
`vacuous` door for claims that commit to nothing, absence-breaks defined
with their quote shape. Nothing to recommend.

## Tranche 2 — constraint completeness (S2): Architect survey and boundary

**Both briefs are the strongest audited.** Survey's counterfactual template
(RENAME WHAT / WHO BREAKS / WHAT HAPPENS) converts a completeness-type
vigilance problem — the hardest quality type for a mid model — into
per-candidate structured discrimination, with the inside/outside test
spelled out on examples. Boundary mode re-asks the same question outside-in
(the other side's mistakes, silence-as-finding), a designed second pass
over the same hole. `none_found` requires citations, so laziness can't
starve constraint zero. S2's residue is real but bounded: a `none_found`
that should have found, on both passes, survives — acknowledged, and
covered during development by preregistered answer keys (earned on two
foreign repos).

## The exit-map (P7's generality probe, mechanical)

Every judgment-bearing mode was checked for a door out (question / escalate
/ cannot / report). Nearly all have one: tester modes carry three question
channels everywhere, developer modes carry the ladder, critic challenge has
`vacuous`, exhausted modes carry the full escalation set. **One live gap:
`vision_keeper/slicing.tools` is `tickets.slice problem.consult ledger.log`
— no message channel at all — while the in-flight brief rewrite adds "if
the item cannot be built without deciding one of those, that is a question
for the seat, not a ticket." The brief instructs an act the namespace
cannot perform.** A model following it can only log a ledger row or comply
silently; `msg.*` doesn't exist in that sandbox. The edit needs a door (or
the sentence rephrased to name the ledger row) before it lands — finding
P10.

## Tranche 4 — Liaison converse / contradiction (S3's neighbours)

**Both ADEQUATE.** Converse is the richest judgment mode in the system and
carries its scars well: the mandatory intake fork (work|chat claim — walk
one's fix), a priority-ordered three-way classification, exact-span
segmentation, mutual exclusivity, worked examples per branch. Contradiction
mode is minimal and correct: route both statements verbatim, add no
opinion. The S3 residue is confirmed from this side: the contradiction-
*marking* act — who sets a statement `contradicted` — is briefed nowhere;
only the handling of an already-marked one is.

## S1 disclosure (R11) — measured, then mechanized

Built as push (`resolve_inbound` hands the submit session
`uncovered_statements`) + brief + case. First recording: **0/5** — the model
read the block and presented the items alone. Second pass moved the
enumeration into the sandbox's present binding ("added, never substituted",
the observed_entries rule: what the session cannot be trusted to enumerate
arrives enumerated) — the case and its sibling then passed from the
*existing* cassettes, since the fix was mechanics, not prompt. The brief
paragraph stays: the refs are mechanical, the presentation is the model's.

## Remaining (parked, with reasons)

3. Vision Keeper `slicing` proper — brief mid-rewrite in the worktree;
   judge after it lands (its downstream cases already re-earned green, and
   P10 names the door it needs).
4. The `LI-present` and `TE-words-already-defined` reds — attributed by the
   project (resolution guard honest-red / transcription); nothing this
   audit would add without fresh transcripts.
