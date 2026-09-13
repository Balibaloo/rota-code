# Glass Cockpit — how the system is presented

*2026-08-24, after the consistency and layout passes. The designed rendering of
this document lives as the "Glass Cockpit" artifact; this file is the version
the repo enforces against.*

In aviation, a glass cockpit replaced a wall of separate gauges with a few
displays that draw the same air data as coherent pictures. Nothing was removed
from the aircraft — the pilot stopped reading instruments and started reading
the situation. That is the move for rota's cockpit.

## The brief

Monitoring first: state at a glance, on top of arbitrary depth — everything
the cockpit already answers stays answerable, but found rather than hunted.
One design. One *staged* experience: newcomer and expert use the same surface
at different altitudes, so learning the cockpit is becoming the expert.

## Four registers

The cockpit does not show one "state"; it shows four registers of a governed
system, and every component is judged by which register it presents and
whether it presents it in that register's natural form:

| register  | question                    | natural form                         |
|-----------|-----------------------------|--------------------------------------|
| contract  | what may happen?            | spatial — the map                    |
| happening | what is happening / did?    | temporal — a timeline, never a map   |
| evidence  | what has been proven?       | a claim with its receipts attached   |
| cause     | why is this here?           | a thread walked backwards            |

The current tabs slice by data source instead (graph / live / progress), and
cause hides three clicks deep in a table row.

## The thesis

**The map is the stage. Time is the play. Evidence is the review. Cause is
the thread that ties them.** One primary surface — the team map — on which
the other registers appear as layers, moments and annotations, not sibling
destinations. The map can carry this because position is meaning here: the
layout is a hand-tended statement of the contract.

## Three altitudes, one surface

- **The pulse (0 interactions).** The map at rest wearing the live overlay,
  plus one narrated sentence. Stuck is the loudest thing on screen. Semantic
  zoom: far out, labels give way to health (role halos, artefact freshness);
  close in, the same map becomes the contract verb by verb.
- **The questions (1 interaction).** Every element answers on click, every
  lens on selection. Exists and is consistent; still owes curation — every
  view opens with its sentence, every panel leads with a judgement before a
  table.
- **The record (any depth).** Raw tables, prompts, verbatim transcripts,
  chains — reached from an element ("open in the ledger"), never by browsing.

Newcomers here are smart people who read graphs and operate systems for a
living — what they lack is not concepts but *referents*: which box is the
Liaison, what a dashed border claims, where a case lights up. So the entry is
**orientation, not instruction**: the design stories playable over the live
map as a brisk, skippable tour that points at things rather than explaining
ideas. It teaches the expert's exact surface, so nothing is unlearned, and it
never talks down.

## Time, the missing axis

Add **replay**: a scrubber under the canvas that animates the run over the
map — wakes light roles, writes pulse artefacts, messages travel edges. The
run stepper is this in embryo. The unification it buys: *monitoring is replay
with the playhead pinned to now* — live-watching and post-hoc debugging become
one surface at two playhead positions. The chat graph stops being a second
map and becomes a **thread view**: one conversation, vertical, cause above
effect.

## Cause, made visible

Select any live element → its causal thread lights across the map in the lens
vocabulary (input cyan → actor violet → output amber, repeated), because a
cause chain *is* that grammar repeated. The provenance panel remains the
thread's transcript.

## The design system

| channel       | means                                  | never                              |
|---------------|----------------------------------------|------------------------------------|
| shape + fill  | what kind of thing this is             | varies by lens                     |
| border colour | what the lens claims about it          | varies by kind                     |
| halo          | the lens speaking about an edge        | recolours the edge's identity      |
| opacity       | in scope for this question             | decoration                         |
| position      | the contract — layout is meaning       | moved by time or animation         |
| motion        | the happening, while the playhead moves| attached to structure or chrome    |
| colour ramp   | a judgement fraction (coverage)        | planned work that is merely early  |

Voice: every view opens with a sentence; tables never lead; judgements before
rows, rows before raw. One notation per fact: truth is ✓/✗, a labelled number
is a chip, a judged fraction is a graded bar, an identity is a link. Light
canvas for the system, dark chrome for the cockpit.

Form: sober. Radii are 2–4px on chrome; rounding above that is spent only
where shape carries meaning (the principal's stadium — a person, not a role).
No pill capsules on chrome; a chip is a square-cornered tag.

The URL is the query: no search box — every view state is an address
(`#/graph?lens=coverage&node=critic`) that reopens tomorrow or hands to
someone. Finding is pointing or addressing, never querying.

Time is honest: rows carry order, not wall-clock time (law 13), so the
presentation never invents timestamps. Time appears only where the OS records
it — a run file's mtime in the run selector, a process start on a claim.

## What not to do

- **No dashboard-ification** — KPI tiles are happening flattened into
  evidence; the pulse is one band and a picture.
- **No force-directed default** — position is meaning; generated layouts are
  tools, never the resting state.
- **No second vocabulary for newcomers** — the overture teaches the expert's
  surface or it teaches the wrong thing.
- **No motion as decoration** — animation is spent on exactly one meaning.

## Build order

1. **The pulse** — narrated status band; far-zoom semantic state.
   *Done when a two-second glance says idle/busy/stuck and names who is
   acting, without a click.*
2. **Replay** — scrubber + animation on the run lens; "now" as resting
   playhead; live mode is the playhead pinned there.
   *Done when last night's run can be watched happening on the map.*
3. **Cause threads** — select a live element → its chain lights on the map.
   *Done when "why is this here" is answered by pointing.*
4. **The overture** — stories as a skippable guided tour; a "tour" button.
   *Done when someone new can say what the Liaison is, having only watched.*
5. **Ledger & report** — live → the ledger (reached from elements),
   progress → the report (claims linking back to their receipts).
   *Done when no question ends at a wall of nine boxes.*
6. **The written system** — these rules distilled beside the code and
   enforced the way the lens checks already are.

## Component audit

| component            | register            | verdict                                    |
|----------------------|---------------------|--------------------------------------------|
| team map + lenses    | contract, evidence  | keep — the core; gains zoom + threads      |
| header pill/popovers | happening           | keep — grows into the pulse                |
| run/story stepper    | happening           | rework — embryo of replay                  |
| chat graph           | happening           | rework — becomes the thread view           |
| live tab grid        | record              | reframe — the ledger, reached from elements|
| progress tab         | evidence            | reframe — the report; numbers link back    |
| provenance panel     | cause               | promote — from buried feature to verb      |
| cases subtab         | evidence            | keep — navigation; tally rows link here    |
| legend/dropdowns/panel | chrome            | keep — unified in the last passes          |
