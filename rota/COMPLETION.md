# The road to done

One document for everything incomplete, asked for by the principal
(2026-08-28) to check we are progressing sensibly. It unifies the loop
ledger's debt (`LOOPS.md`), the decision register's open entries
(`DECISIONS.md`), and the plans made in session — organized as four tracks
plus the questions only the seat can answer. Done means: gauntlet stories
told — foreign repositories, zero intervention, trails that score — which is
`LOOPS.md` G4 for every loop.

What this document is *not*: a status ledger. Grades live in `LOOPS.md`,
open designs in `DECISIONS.md`; a line here is a pointer with an order
attached, and when a pointer's target closes, the line comes out.

## Track A — every loop production-grade (the ledger's debt, in order)

1. **Loop 6 → G1: interrupt and cancel.** The two steering acts that do not
   exist. Interrupt is the principal stopping the running batch (the
   machinery is `run_state` plus `lifecycle.defer` — what is missing is the
   act and its pins); cancel is a batch abandoned by ruling (needs an
   `abandoned` exit that is not deferral, because deferred work is offered
   again and cancelled work must not be). Then cases. Preemption is done.
2. **Loop 5 → G2: earn the re-survey.** The freshness machinery is built and
   pinned (`test_a_changed_file_reopens_exactly_its_area`); what is owed is
   recorded re-survey sessions and a refresh under a running batch.
3. **Loop 4 → G2: the criterion cluster re-earns.** The stated G1 debt was
   stale — `every_mode_has_a_case` is green. The real gap is the four
   delivery reds (`TE-words-already-defined`, `TS-hold-a-test`,
   `TS-criterion-no-machine`, `TS-outside-fact`) re-earning on the surface
   machinery built for them, and the one-fault-per-pass curve reaching zero
   on a live pass. (The obligation ledger's 162 open rows are a horizon
   metric, mostly reads; not this milestone.)
4. **Per-loop G3: the named chaos injuries.** The core has been hurt three
   ways and held; each loop's specific injuries are listed in `LOOPS.md`
   and none has been inflicted yet.

## Track B — the gauntlet ladder (G4's machinery)

1. **Segments** (rungs one and two standing: four cases, two green on the
   suite model, two green on the production model and red on the suite
   model as per-model records). Remaining segment classes: the
   wrong-answer-from-the-seat intake (blocked on a small harness extension —
   cases cannot yet assert "row X was *not* changed"), and one segment per
   escalation verb that has none.
2. **Composed flows**: multi-segment stories where a ruling on one trap
   invalidates the work behind another; the `grants:` key arrives here.
3. **Synthetic stories**, tiered in `stories.json`, then **foreign-repo
   stories against preregistered keys** — the runs that are simultaneously
   the test record and the product's stories.

## Track C — two models, one truth

The A/B is now a method: dispute-class behaviour (challenge upward, answer
from the brief) exists on qwen3:8b and not on llama3.1:8b, measured 5/5 vs
0/5 twice. llama remains the recording harness; capability boundaries get a
production-model arm before they are called design faults. Still to run:
the assumption-capture experiment (qwen wrote one ledger row in 134
sessions — is the register's assumption layer silent exactly where it
matters?), and the criterion-cluster reds on the qwen arm.

## Track D — debts that are not loops

- **Push scoping** (from the bloat audit): `tickets.scan` and
  `criteria.consult` push all rows; scope both to the wake's item/batch
  before a 50-item project relives the glossary incident.
- **Statements relevance** (`brief.list`): becomes load-bearing the day the
  chat interfaces arrive; parked with its register entry until then.
- **Over-production, the upstream cause**: four organs now (statements,
  tickets, batches, criteria), each guarded, none explained. One
  transcript-level investigation across all four is the open work.
- **Frontier ordering** — the register's "big one". Deliberately gated:
  onboarding runs on today's frontier and its failures are the
  specification. Unblocks when we next onboard at scale.
- **Amendment as the normal operation** and **conflicting sources**: design
  directions filed in the register, neither scheduled.

## Questions for the seat

1. **Does a production-model green count?** Three cases are red on the
   recording model and 5/5 on the production model. If the register's bar
   for dispute-class capabilities is the production model, they count
   toward G2 with the llama rows kept as records; if the bar is "both
   models", they stay red and the capability waits for a stronger recording
   model. This decides Loop 4's G2 date.
2. **When does the frontier-ordering work run?** Before the gauntlet's
   composed tier (its bugs will surface there anyway) or after the next
   at-scale onboarding (the register's stated plan)?
3. **Over-production: investigate now or keep guarding?** One analysis
   across the four organs' transcripts, versus adding the fifth guard when
   the fifth organ appears.
4. **When do the chat interfaces enter the plan?** Everything is
   CLI/table-backed by ruling; the interfaces pull statements-relevance,
   vocabulary surfacing (proposed/preliminary/adopt), and the agenda into
   scope the moment they start.
