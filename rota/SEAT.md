# The seat — the operator's interface

*A proposal. What it would take to never type a command, and one thing I built
last week that is wrong.*

The command line went in first because it was the shortest path from "this is
unusable" to "this runs". It is not the interface. This document is what the
interface would be, and it starts from the loop rather than from the verbs,
because the verbs were derived from what the code could already do and the loop
is what you actually spend the afternoon in.

**The loop is: point it at a repository, watch it work, judge what came out,
change something, run again, compare.** Six steps. Two of them have no home
anywhere — *change something* and *compare* — and those two are the whole reason
for running it twice.

---

## What forces you out to a terminal today

Precisely three things, and they have one shape in common.

| forced out | why |
| --- | --- |
| **starting a run** | it needs two names that do not exist yet: what to call the run, and where the checkout is |
| **choosing a run** | the seat opens *inside* one. There is no screen where a run is a thing you can point at |
| **comparing two runs** | nothing does this anywhere, in any interface |

The shape: **each one is an operation *about* a run rather than *within* one,
and the TUI has no level above a single run.** That is the gap. Everything
inside a run already has a key.

---

## 1 · The division of labour, as a rule rather than a habit

You already ruled that the TUI drives and the cockpit is for depth. The rule
that keeps that from eroding into two front doors that disagree:

> **The cockpit never changes state. The TUI never renders a graph.**
>
> If you want something to happen, you are in the seat. If you want to know why
> something happened, you are in the browser.

This is not tidiness. A viewer that can also act has to answer "is what I am
looking at still true", and every panel in it inherits that question. The
cockpit's value is that its answer is always yes.

The split falls out of it cleanly:

- **the seat** takes everything with an *intent* — create, run, wipe, fork, talk
- **the cockpit** takes everything with a *question* — what was this role shown,
  what caused this, what did that session actually write

---

## 2 · The seat needs a floor below it: the run list

The TUI opens in a run today, which is why the two operations that are about
runs fell out to the command line. The fix is one screen, and it is the same
rows `rota ls` already computes:

```
 rota                                                    4 runs

 ▸ ctn_v3        quiescent   v3@766c9e3    3 terms   2 cons   24 sess   2d
   ctn_master    quiescent   main@a41f2   12 terms   4 cons   31 sess   2d
   tomlkit       ready       main@8e2c1    1 term    1 cons    3 sess   1h
   oauthlib      stale       —            30 terms  24 cons   71 sess  8d
                 └ behind schema: no such column unresolved_note

 enter open   n new   f fork   d diff   w wipe   c cockpit
```

`enter` pushes the seat as a screen rather than being the app. Everything that
exists now lives there unchanged.

Two things this screen makes possible that no amount of polish inside a single
run could:

- **`d` — diff two runs**, which is the operation the whole evaluation loop
  exists to end in, and which has never had a home
- **`f` — fork**, which is where the mistake below gets fixed

---

## 3 · The mistake: `alt+r` destroys the thing you wanted to compare against

I built `alt+r` as *wipe, then index the same checkout again*. Designing this
screen is what showed it is wrong.

**A rerun is what you do after changing a brief.** The question it asks is
"did that edit help", and answering it needs the run from *before* the edit.
`alt+r` deletes exactly that. It is a rerun that destroys its own control.

The correct verb is **fork**: run again *beside* it, never over it. `ctn_v3`
stays; `ctn_v3·2` appears next to it in the list, against the same checkout at
the same commit, and the two are diffable. Wipe stays as its own key for when
you genuinely want the disk back.

This also settles what a run *is*, which the CLI never had to answer. A run's
artefacts are derived from three things — **the source, the prompts, and the
model**. Change any of them and you have a different experiment, not a newer
version of the same one. So:

> **A run is immutable in what it is about. Running again makes a new run.**

Which is Law 9's distinction one level up: the artefacts are derived and can be
recomputed, the *record that this configuration produced these artefacts* cannot.
That record is the only durable thing here, and overwriting it is the one
irreversible act in the loop.

---

## 4 · The new-run form, and the gap it closes by existing

`onboard` stayed a command because it needs two names at once. A form is honest
about that, and asking for them in a form rather than an argument list turns out
to close a real hole:

```
 new run

   name     [ ctn_v3                    ]
   repo     [ ~/src/ctn                 ]  [browse]
   branch     v3 · 766c9e3
            ⚠ 3 uncommitted files — the run will describe the tree, not the commit
   model    [ llama3.1:8b            ▾  ]

                                   [cancel]  [onboard]
```

**A run records only `project_root` and `run_state`.** Nothing records which
branch or commit was surveyed. So the two ctn runs — one on `main`, one on `v3`,
the comparison an answer key was written for — are on the record *about the
identical thing*, and the only thing separating them is that I remembered.

The form has to display the branch to be usable, and displaying it means
recording it. One row in `config`, read with `worktrees.head`, which already
exists. It is what lets the list column above say `v3@766c9e3`, what makes a
diff mean anything, and what lets an answer key say which tree it was written
against.

The uncommitted-files warning is the same argument. A survey of a dirty tree is
evidence about something no commit contains, and that is worth knowing at the
moment you press the button rather than when the numbers disagree later.

---

## 5 · Watching: the question is "is this going anywhere", and a log cannot answer it

The seat shows a ticker of sessions and the outstanding register. The register
is the good half — it is state rather than scrollback. The ticker is a log, and
a log is what a livelock hides in: the `reopen ↔ elect` loop looked *healthy*,
because every line was a different message and every line was new.

Three things would have shown it in seconds, and all three are folds over
machinery that now exists:

- **delta per session, not just the line.** A session that committed nothing is
  the signal, and it is currently indistinguishable from one that did.
  `terms +1 · items +0 · —` beside each row.
- **time since the last *productive* session.** One number. The single best
  "is it stuck" indicator, and it needs no new state.
- **chain depth, before the cap fires.** `edge_repeats` already counts how many
  times a causal chain has repeated its own edge — that is what `quarantine_looping`
  reads. Showing it climbing (`reopen→elect ×7`) surfaces the livelock *while it
  is happening*, rather than at the cap.

The third is the one worth having. A bound that only speaks when it fires tells
you what already went wrong; the same number displayed tells you what is going
wrong.

---

## 6 · The cockpit: it has every piece and no path through them

Its two questions are the ones the register cannot answer — *what was this role
shown* and *what caused this*. Both are served today, as separate panels you
navigate between by knowing what you are looking for.

What is missing is not a panel. It is **one flow, backwards, from a bad
artefact**:

```
  glossary: "intent — a specific action or task"
    ↓ written by
  session s_14  ·  terminologist  ·  tick:survey(tomlkit)
    ↓ was shown
  [the built prompt, verbatim]        ← was the source in here at all?
    ↓ woken by
  wake tick:survey  ←  m_9  ←  m_4  ←  your first sentence
```

That is the path I walked by hand for the intake bug and again for the survey
question, both times by writing a throwaway script to print a prompt. Every
edge in it is already an endpoint. Making it a click is the difference between
a tool that can answer "why is this term wrong" and a tool where the answer is
recoverable by someone who knows the schema.

**And the one link that closes the loop without breaking the read-only rule:**
each brief should name the file it came from. `roles/prompts/terminologist/survey.md`,
as text you can see. The cockpit does not edit it — the loop is *look at what
the role was shown → open that file in your editor → fork the run*, and the
cockpit's job is only to tell you which file. That keeps the viewer pure and
still ends the trip somewhere useful.

---

## 7 · What a diff of two runs actually is

Not a row diff — the ids differ by construction and would report everything as
changed. It is a comparison of what was *found*:

| | |
| --- | --- |
| **terms** | matched on the term string. In A only, in B only, and same term with a different sense — the third is the interesting one |
| **constraints** | same, matched on headline |
| **areas** | surveyed in one and not the other, and outcome per area |
| **audit** | the mechanical findings, which are already computed |
| **cost** | sessions to quiescence, wall time, and how many sessions committed nothing |

The header states what differed in the inputs — same source, different prompts;
same prompts, different commit — which is the only thing that makes the
comparison mean anything, and which is only knowable if §4 is built.

**A bigger idea, flagged and not proposed:** the answer keys are prose. If a
prediction were a checkable line rather than a paragraph, a diff could score
both runs against the key automatically, and "did that edit help" would be a
number instead of a reading. That is a real change to what an answer key *is*,
it deserves its own argument, and it is not part of this.

---

## 8 · Two questions I cannot settle for you

**Does closing the seat stop the run?** I think yes, and that it should be
*said* in the interface rather than engineered around. The loop runs in the
app's worker thread today, so closing the window pauses it — and that is already
correct: "the frontier *is* the state; reconstructing it is the entire
recovery." The scheduler is disposable by design, so pausing costs nothing and
resuming is just running again. The alternative — a run that keeps going
headless after you close the window — buys very little and adds a process whose
lifetime nobody owns, which is the exact thing §3Bd is careful about.

**How does the list know a run is live?** It cannot, today. A session holds a
claim while it runs, and `reap_claims` treats *live* and *died-mid-session* as
one condition, deliberately — a claim whose session never committed is stale by
definition. That is the right rule at boot and the wrong one for a list, which
wants to show `running` without lying. It is the same problem `runtime_processes`
solved for spawned processes and by the same means: a pid is not an identity,
pid plus start time is. Applying that to claims is a small change with a real
consequence — two seats open on one run currently fight silently — and I would
want your go-ahead before touching the claim table, because it is load-bearing
for every session commit.

---

## What I would build, in order

1. **the run list**, with the seat pushed as a screen. Nothing new underneath —
   it is `rota ls` with a cursor, and it is what makes the next three possible.
2. **branch and commit recorded at onboarding**, then shown. One config row,
   and every comparison afterwards depends on it.
3. **fork, and `alt+r` retired.** The current key destroys its own control, and
   that is worth fixing before the list makes it easy to press.
4. **the two "is it stuck" numbers** in the seat — time since a productive
   session, and chain depth. Both are folds over existing machinery.
5. **the backward chain** in the cockpit, and briefs naming their file.
6. **diff**, last, because it is the only one that needs all of the above to say
   anything true.

1 through 3 are the ones that end the trips to the terminal. 4 through 6 are
what make the loop worth being in.
