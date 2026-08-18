# Stage 3Bd — the environment

*A proposal. Four questions, four answers.*

*One of them was marked as yours to rule on — whether an environment survives a
deferral — and it turned out Law 9 had already answered it and I had read the
wrong half of the existing split. It is answered below rather than asked. What
is left for you is not a design question but a go-ahead: this is the only stage
that touches the real machine.*

An environment is the first thing in this system that **outlives the session that
made it**. Everything else here is a pure function: wake, act, commit, end. A
process is not. It is still running when the session that started it has been
garbage-collected, it holds a port that another batch will want, and it can
survive the crash of the thing that was supposed to clean it up.

That is why this stage is the only one with a warning attached rather than a
plan: it is the one place the system spawns processes and can damage something
outside its own database.

## What exists today

| piece | state |
| --- | --- |
| `runtime_processes` (pid, batch_id, command) | table exists, **written by nothing** |
| `boot.reap_processes` | kills every recorded pid at boot, then forgets |
| `worktrees.py` | a worktree per batch, created by the scheduler, never by a role |
| `lifecycle.start / defer / merge` | the hooks an environment would attach to |

So the reaper is written and the spawner is not, which is the safe order to have
built them in and is why nothing has gone wrong yet.

**One thing already wrong in what exists.** `reap_processes` kills by pid, and a
pid is reused by the operating system. After a crash and a reboot, a recorded pid
is overwhelmingly likely to belong to something else, and this code sends it
`SIGTERM`. It is guarded only by "not ours" being indistinguishable from "already
gone" — both are swallowed. Whatever else this stage decides, a recorded process
needs a second fact that survives restart and identifies it: start time, or a
command-line match, or both. This is the cheapest fix on the page and it is a
fix to shipped code.

---

## 1 · Separation — what an environment belongs to

**Proposal: one environment per batch, and its lifetime is the worktree's.**

A batch already owns a worktree, has a lifecycle with real hooks, and is the unit
the scheduler dispatches. An environment per *run* would mean a fresh one for
every test invocation, which is defensible for isolation and wrong for cost: the
thing being started is a database, a server, a queue, and starting it per run
turns a test suite into an integration harness.

Consequence, and the reason this answer settles the port question: **port
allocation belongs to the scheduler, not the batch.** Two batches must never
reach each other's ports, and a batch cannot guarantee that, because it cannot
see the other one. The scheduler already knows every live batch. It assigns a
port range at `batch_start` and records it, the same way the worktree path is
recorded, and the environment is told what it was given rather than choosing.

This is the same shape as `batch_id` defaulting from the wake and `area` from the
scheduler: *a value the system knows should never be one a role has to get
right.*

## 2 · Boundary — what is inside it, and what is merely near it

**Proposal: inside means this system started it and recorded it. Nothing else is
ever inside.**

The line has to be drawn before teardown is written, because teardown is where
crossing it does the damage. Three cases:

- **a process this batch spawned** — inside. Recorded at spawn, killed at
  teardown.
- **a database the whole machine shares** — outside, permanently. It was running
  before the batch and will be running after. A batch may *connect* to it, and
  connecting is not owning.
- **a container or service this batch started that a second batch then
  connected to** — inside the batch that started it. The second batch has a
  connection, not a claim, and teardown does not consult it.

The rule that makes this checkable is the one `worktrees.py` already uses and
states in its own docstring: **nothing removes what it did not create**, and the
proof of creation is two independent facts, not one. There it is "recorded on the
batch *and* under the state directory, because either alone can be satisfied by
an accident". Here it should be "recorded in `runtime_processes` *and* still
matching the command and start time we recorded" — which is also the pid-reuse
fix above, arriving for the same reason.

## 3 · Toolkit — the verbs a role gets

**Proposal: `env.start`, `env.status`, `env.logs`. No stop, no reach.**

- **no `env.stop`** — stopping is lifecycle, exactly as worktree teardown is.
  A role that can stop its environment can leave a batch half-dead, which is the
  state Law 9 names and forbids. If a role wants a clean slate it is asking for
  a restart, and a restart is `env.start` on a batch whose environment the
  scheduler tore down.
- **no batch argument anywhere.** Same rule as every other namespace in this
  system: the capability to reach another batch's environment does not exist
  rather than being refused. `env.status` reports on the session's own batch
  because that is the only batch it can name.
- **`env.logs` is a read of something outside the database**, which makes it the
  same kind of thing as `code.source`, and it should be recorded the same way —
  a session that claims a runtime fact should be checkable against having looked.

Which roles get these is a graph question and Law 3 answers it mechanically:
whoever writes or reads the artefact the environment serves. Developer and Tester
are the obvious two, and I would not draw a third without a case that needs it.

## 4 · Hooks — where lifecycle attaches

**Proposal: spawn on `batch_start`, tear down on every terminal state and at
boot.**

- **spawn** at `batch_start`, beside worktree creation, because it is the same
  kind of decision and belongs in the same place.
- **teardown** on merge, on abandonment, and **on deferral** — but only of the
  processes. The allocation survives.

  I had this the other way round and marked it as the one decision that was
  yours. It is not; Law 9 already answers it, and I was reading the wrong half
  of the existing split.

  The worktree survives a deferral and the checkpoint does not, and that line is
  not worktree-versus-checkpoint arbitrarily — it is **durable product versus
  derived state**. Commits survive because they cannot be recomputed. A
  checkpoint dies because it can.

  A running process is derived state by that test. Everything it holds — a
  seeded database, a warm cache, a bound port — is reproducible from the
  worktree by starting it again. So an environment is a checkpoint, not a
  worktree, and the ruling already exists.

  What survives is the **port range**, as a row on the batch. Resuming
  re-spawns onto the same ports. That costs one row, and it avoids what keeping
  the processes would cost: a deferral has no upper bound, so an environment
  held across one holds ports and memory indefinitely for work that may not
  resume this week. It would also need a "how long is too long", and this system
  is not designed around caps.

  The real loss is a slow setup re-run on resume. That is the right cost to pay
  rather than hold a machine hostage to a deferred batch.
- **crash teardown cannot be a session's own responsibility**, because a session
  that has crashed is not running. This is why `boot.reap_processes` exists and
  why it is the *only* correct place for it: boot is the one moment the system
  knows nothing of its own is running.

## What this stage must not become

A permission system nobody designed. `batch_touch` already has this warning
written against it — "a prediction that could block work would quietly become a
permission system" — and an environment is a far more tempting place for it,
because it is where the system touches the real machine. `env.status` reports.
It does not gate.

## The order I would build it in

1. **the pid-reuse fix**, alone and first. It is a fix to shipped code, it is
   small, and it is the only item here that reduces risk instead of adding
   surface.
2. **port allocation in the scheduler**, with no spawner. Allocation is pure
   bookkeeping and can be tested without starting anything.
3. **`env.start` and the record**, with teardown at boot only. At this point an
   orphan is possible but bounded: it dies at the next boot.
4. **teardown on terminal states**, which closes the window.
5. **`env.status` and `env.logs`**, last, because they are the only two that are
   not on the critical path for anything.

Steps 1 and 2 are worth doing whatever you decide about the rest, and neither of
them can spawn anything.

## What is still yours

Nothing in the four questions, now that the deferral one has answered itself.
What is left is the decision to start: this is the only stage that touches the
real machine, and the last item on the list above is the first one that can
leave something running. Steps 1 and 2 cannot, and I would take those without
asking.
