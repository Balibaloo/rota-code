# The loops, and what each has earned

Six loops carry the claim; this ledger says how far each can be trusted, and
the suite checks every claim it makes. The precedent is `REGISTER.md`: a
document describing reality is worth having only while it is true, so the
grades below are propositions the build evaluates, not status prose. Claiming
a gate a loop has not earned is a failing test; building past a gate without
recording it moves a pinned count.

## The gates

| gate | the claim | who checks it |
|---|---|---|
| **G0 wired** | every link exists and has fired live at least once | the loop's named predicates and modes are registered; its arc test passes |
| **G1 pinned** | deterministic tests, and an L1 case for every mode the loop added | `every_mode_has_a_case`, scoped by the rows below |
| **G2 earned** | the loop's cases green in the recorded corpus — **on two separate recording passes**, because a score is a fact about a load | `case_runs`, by the case ids below |
| **G3 endures** | survives being hurt: sessions killed mid-flight, messages corrupted, work concurrent | the loop's named chaos tests pass |
| **G4 lived** | zero-intervention gauntlet scenarios, on repositories not authored for the test | the gauntlet log |

Nothing is at G3 yet, and that is the honest headline of this file — though
the *core* has now been hurt three ways and held (`test_chaos.py`): a model
dying mid-session leaves the world exactly as it was, with the death counted
and the wake re-offered; the scheduler killed between steps re-derives the
identical frontier, because there is nothing a scheduler is except a fresh
call; and a backend speaking garbage burns turns without writing a world.
The scheduler's "stateless, disposable" is an outcome now. What G3 still
means per loop is the *specific* injuries below — the core surviving is the
floor, not the grade.

## The ledger

| # | loop | grade | evidence |
|---|---|---|---|
| 1 | understanding | **G2** | onboarding arc on click and cnt against preregistered keys; survey/orient/define cases green |
| 2 | inquiry | **G2** | fan-out, composition, ladder, repair; quality measured stage by stage against the consult key |
| 3 | intent / signoff | **G2** | observed exit live at scale (81 rows decided); eager and lazy election; the seat |
| 4 | delivery | **G0** | eight live passes, every structural link fired once; the wall named (criteria must carry a callable surface) |
| 5 | stay true | **G1** | a changed file reopens exactly its area; `rota refresh` |
| 6 | steering | **G1** | preempt, interrupt (`rota interrupt`, a pause) and cancel (revoked approval ends the batch, terminal) all pinned deterministically; the loop adds no model modes |

## What each loop still owes, by gate

- **1 → G3**: kill a survey mid-area; corrupt an attest; onboard two runs
  concurrently against one checkout.
- **2 → G3**: kill an owner mid-round and assert the harvest still composes;
  a corrupted answer message must not reach the principal.
- **3 → G3**: two principals ruling at once; a verdict for a present that was
  re-presented meanwhile; kill the adopt session after the relay.
- **4 → G1**: ~~the criteria-surface build~~ — built: criteria carry
  `surface_refs`, vetted at both doors, pushed as candidates, delivered to the
  Tester (`test_criteria_surface.py`); challenges now pay their reading up
  front too (`test_challenge_evidence.py`). Still owed: cases for the delivery
  modes that have none. The one-fault-per-pass curve reaching zero *is* this
  loop's path through the gates.
- **5 → G2**: ~~record the re-survey sessions~~ (recorded, green, one load
  — the earn-twice gate wants a second); ~~a refresh under a running batch~~
  — pinned four ways, and building it found the refresh silently disarming
  tripwires: a rebuilt index strands references to vanished grains, so
  `rota refresh` now reports every orphaned binding, touch prediction and
  criterion surface instead of leaving them quietly dead.
- **6 → G2**: the steering acts on the recorded corpus — a preemption and
  a cancellation observed in a recorded delivery run rather than a fixture.

## The gauntlet (G4's data source)

The stories in `design/stories.json` are the scenarios; a gauntlet run is one
story driven end to end on a foreign repository against a preregistered key,
scored on the artefact trail — every criterion traced to a term, every test to
a criterion, every assumption a sentence, every decision a reason — with
planted traps the trail must surface. Only zero-intervention runs count, and
each passing run is simultaneously the test record and the story the tool's
capability is told in.

Zero-intervention does not mean the principal surface goes untested — the
principal's ruling (2026-08-27, refined 08-28): communicating with the
principal in complicated situations is itself a system function, and the
system's tables are where that complexity actually lives. The second class
scripts the principal — scripted answers standing in for a human, the way
`OneShot` already stands in on the signing path — and its cases are **flow
segments, not stories**: the principal says one thing, and the case pins the
pipeline it must travel — verified against the tables, escalated to the role
that owns it, and *brought back to the seat*, never just accepted. What is
tested is the coherence of the parts.

The spec's settled points, each a case class rather than a rubric:

  * **both failure directions are cases** — silent overreach (deciding what
    needed the seat) and punting (escalating what the grant list already
    authorized); the story key carries the grants so both are mechanical;
  * **the hard work is the fixtures**: realistic, complex table states with
    expectations of what the system should do. No generic present-shape
    rubric — each case says what *this* situation demanded;
  * **the principal's words stay bounded** in the main body — plain requests,
    plainly phrased. What the seat says is not where the complexity lives;
    what the tables hold is. Wild requests are an edge tier, not the corpus;
  * **coverage builds across the scale** — segment cases first, composed
    flows next (a ruling on one trap invalidating the work behind another),
    full stories on foreign repositories last, tiered in `stories.json` the
    way the register already tiers T1 against L3.
