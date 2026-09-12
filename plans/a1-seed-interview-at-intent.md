# A1 — the seed interview at intent-time (ruled 2026-09-03, "a usability priority")

The audit's universe opens with A1, *eliciting what the principal wants,
including the things he did not think to say and the things he will only
recognise when shown*, and calls it "an active craft, not transcription" and
"the named permanent choke point at the root." The allocation grades it
PARTIAL: recording strong, elicitation designed but unimplemented. The design
is the seat's seed interview (SEAT.md, 2026-08-25), whose principles are fixed
and whose moments were onboard-time and agenda-time. **Ruled 2026-09-03: it
runs at intent-time too.** "I want a CRM" is the same craft at a third moment.

Measured the same day, as the principal: "tip calculator pls" was read by
three desks as three different programs, the one that shipped had no way to
run it, and every question put to the principal was about the system's
internals (confirm the echo, constraint zero, an invalid item id) while the one
question that decided what got built -- what are the inputs -- was never asked.

## What already exists (nothing here is new vocabulary)

- **The account.** `how_it_works` is the first item Vision Keeper writes, for
  a repository (orient) and, since 2026-09-03, for a statement (deliver). It is
  the whole, put to the principal before anything is sliced.
- **The question bank.** A ledger row is "what was assumed where the words
  were silent, and what it would cost to be wrong", authored by the desk that
  assumed it, resolved only by a decision naming it (law 11). Vision Keeper's
  deliver brief now logs one per silent point; the other desks follow.
- **The gate.** Signoff already blocks slicing until the principal rules on
  the items, "presented as one document" (law 8). Law 8 also says "a lineage's
  open assumptions are presented at its gates: nothing ships whose assumptions
  the principal never saw" -- and that sentence was never built. No ledger row
  reached the page; `render_refs` could not render one.
- **The ruling loop.** approve / contest with a reason, relayed to the owner
  with the reason (`resolve_inbound`'s cause-hop, 2026-09-03), the owner amends
  (`contested.md`), the amended row is re-presented.
- **The doctrine.** `interrupt_cap`: never the same question twice; every
  re-touch reframes or offers a new default. "Derive it" is always an answer
  and silence means it (SEAT.md): nothing waits on a question.

## The design

The signoff page is the interview. Each open assumption about a presented row
rides on the page beside the row it is about, rendered as *assumed: <sentence>*.
The principal rules on it with the verdict they already give:

| they say | what happens | where |
|---|---|---|
| approve | the default is taken: a decision row, author `principal`, `resolves_ledger` = the row, written at the keypress; the row is resolved; the owner is not woken for it | `principal.land` |
| contest, with words | the default is overruled at the keypress: a decision under the principal's name, carrying the words, resolves the row; and the row the assumption was about is contested, so its owner amends it through the contested loop with `principal_said` in front of it | `principal.land`; then `contested.md` as today |
| nothing | it stays open: the agenda's material, and a later gate's | as today |

Proportionality falls out: three words yield one account and two assumptions;
a CRM yields a page. Ranking and price come from the ledger sentence itself
("what it would cost to be wrong"); ordering on the page is by the lineage the
assumption hangs from. The eager/lazy election, when built, decides whether the
principal is offered the assumptions before slicing (eager, the default the
principal asked for) or at the later gates (lazy); until then, signoff is the
one moment, and it already exists.

What this deliberately is not: a new artefact, a new mode, a new predicate, a
new message edge, or a blocking step beyond the gate that already blocks. It
does not change what a desk may ask a peer (law 10, "spend the free thing
first"); it changes what the principal is shown at the moment they already
rule.

## Build order, each piece measured

1. **Mechanics (deterministic).** The present hook adds the lineage's open
   ledger rows to a submit's present (the uncovered-statements rule, extended);
   `render_refs` renders a ledger row as *assumed: ...*; `_owner_of_ref` maps a
   ledger id to its author; `land()` takes an approved default as a resolving
   decision and drops it from the relay's refs. Pinned in
   `tests/rota/test_signoff_assumptions.py`.
2. **The owner's half -- none, by measurement.** The first draft gave
   `relay.md` an overruled-assumption act and `relay.tools` the
   `decisions.author` call; measured 2026-09-03, the model authored fourteen
   decisions a session, five of five, on the plain approve case too. The tool
   in the list was the invitation. Both rulings on an assumption close at the
   keypress instead, and a contested assumption contests its row, which the
   contested loop already amends from `principal_said`.
3. **The generators (briefs, register).** Vision Keeper first: the deliver
   brief carries the literal `ledger.log(about_ref="how_it_works", ...)`
   shape, and `L1-VK-the-account-before-the-behaviours` expects `ledger
   1..4` -- green on the recording model 2026-09-03 (the sentence form had
   logged nothing on qwen3:8b in the tips6 walk; the literal shape is the
   lever, as with every worked example here). A paragraph that separated an
   assumption from an outside fact (the Researcher's) was tried and removed
   on 2026-09-09: with it the account case went 5/5 -> 0/5 (the model read
   and never wrote) and the outside-fact case stayed 0/5. The Researcher
   route from deliver is an open register red. It needs a different lever
   than another sentence. Then Terminologist (criteria) and Architect
   (deliver), one case each.
4. **Never twice.** The `unresolved` ladder put the identical clarify to the
   principal twice in one run (tips5, 2026-09-03), against the interrupt-cap
   doctrine. A derived reask whose words did not change is refused toward a
   default. Deterministic.
5. **Cold walks.** "tip calculator pls" (one account, two assumptions on the
   page, one round) and "a CRM for a small plumbing business" (a page, more
   than one round).

Owed alongside, separately: the Tester's script-shaped test (S0 3.29), which
is what stopped tips5 from delivering once the understanding was right; and the
regression the account-first brief caused in
`L1-VK-an-outside-fact-is-the-researchers` (a default the principal was silent
on is logged; a fact that lives outside the project is asked of the Researcher
-- one sentence, then re-record).

## Rulings, 2026-09-12

1. The interview is iterative, most important first. One page shows the
   assumption that changes the most, or the few that all do. The answer
   lands, the desks re-derive, the next page shows what is still open.
   An answer that settles three questions removes all three. Nothing is
   asked twice.
2. Hold at intent time only. No batch starts until the first page is
   answered. After that, nothing waits on a page.
3. The interview, the touch guess at signoff, amendment and conflicting
   sources are one surface: pages in words, answered in words, one door.
   Design each as a kind of page, never as a feature with its own verb.

The ranking, "which assumption changes the most", is a judgement and
lives in the brief of the desk that presents. The door holds only the
facts: which assumptions are open, which the last answer resolved.
