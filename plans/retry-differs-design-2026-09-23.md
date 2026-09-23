# A retried tick says which attempt it is

Frame 58, a retried tick re-runs the identical session. Design record,
revision 1, 2026-09-23. Rota workflow throughout, except where a line
says meta.

## 1. The fault, in one paragraph

A tick wake that fails is dispatched again, up to `tick_attempt_cap`
times, three by default (observed: `rota/core/config.py:121`,
2026-09-23). The retry sends the same prompt at temperature zero, so the
model gives the same answer and the retry is the first session again,
byte for byte (observed: night 88, four sessions run three times, hashed
per turn, frame 58's body, 2026-09-21). `tick_batch_start` writes
"attempt n of 3" into its wake's detail on a stalled re-fire and says in
a comment that the second session is therefore not the first one
verbatim (observed: `rota/core/scheduler.py:327-335`). The prompt never
shows that detail, because `DETAIL_SHOWN` in `rota/core/runner.py:239`
holds `tick:tests_missing` alone. `tick:boundary` and `tick:challenge`
write no detail at all. So every retry of every tick kind reproduces the
failure at the price of a full session.

## 2. The scope

Five places, read on 2026-09-23 (observed: the map tool and the files).

- `rota/core/scheduler.py:32`, `class Wake`, a frozen dataclass with
  `role`, `kind`, `message_id`, `refs` and `detail`.
- `rota/core/scheduler.py:1338`, `note_dispatch`, which counts one
  dispatch of a tick wake in `tick_attempts` and returns the new count.
  Messages return 0 and have their own bound.
- `rota/core/loop.py:296-306`, the one place a tick wake is counted and
  then run: `note_dispatch(conn, result.wake)`, then `run_session(conn,
  result.wake, ...)`. The scheduler actions at `loop.py:258-270` are
  counted too and run no session, so no prompt exists there.
- `rota/core/runner.py:318`, `build_prompt`, which composes the user
  prompt from the wake. The detail door is at `:351-359`.
- The register's cases call `run_session` with a wake they build
  (observed: `rota/testkit/fixtures.py:1066` and `:1148`). They never
  pass through `loop.step`.

## 3. The repair

### 3.1 One field on the wake

`Wake` gains `attempt: int = 1`. The first dispatch of a wake is attempt
1, and the field says so without being set. A retried wake carries the
count the table already holds. The field is not in `__str__`, so the
loop's own log lines do not change.

### 3.2 One door at dispatch

In `loop.step`, the return of `note_dispatch` is kept, and a count of
two or more marks the wake:

```python
n = note_dispatch(conn, result.wake)
if n >= 2:
    result.wake = dataclasses.replace(result.wake, attempt=n)
```

This is the one door for every tick kind. The count is a fact of
`tick_attempts`, written at the same moment, so the number the role
reads is the number the quarantine counts. No predicate has to compute
its own attempt, and no kind can forget to.

### 3.3 One sentence in the prompt

In `build_prompt`, after the subject lines and before the detail door,
for a tick wake whose `attempt` is two or more:

```
This is attempt 2 of 3 on this wake. The earlier attempt ended with
nothing recorded, so the same answer ends the same way. Do something
the earlier attempt did not.
```

The cap comes from `config.get(conn, "tick_attempt_cap")`, read through
the sandbox's connection, and never from a literal. The sentence is
outside `DETAIL_SHOWN`, because it is not a kind's detail. It is a fact
of the dispatch, and it holds for every kind. `DETAIL_SHOWN` and its
rule stay as they are.

### 3.4 `tick_batch_start` keeps its detail

The stalled path in `tick_batch_start` keeps "attempt n of 3: the last
session ended with nothing written and nothing committed". Its number
and the dispatcher's agree, because both are the table's count plus
one. The detail stays hidden by `DETAIL_SHOWN`, as today, and
`tests/rota/test_batch_start_attempt.py` stays green. Showing that
reason to the Developer is a separate change, because the rule says a
kind joins `DETAIL_SHOWN` with a register case that carries its detail.

### 3.5 The tests

One parametrised test over the four kinds the frame names:
`tick:batch_start` for the developer, `tick:tests_missing` for the
tester, `tick:boundary` for the architect and `tick:challenge` for the
critic. For each, `build_prompt` is called on the wake at attempt 1 and
on `replace(wake, attempt=2)`, and the test asserts the two user prompts
differ and the second names "attempt 2 of 3". The model is
`test_a_tick_wake_says_its_detail_to_the_role` in
`tests/rota/test_night46_context.py:92`.

One test on the door: two calls of `loop.step` on one undrained wake,
with a backend that answers nothing, and the second session's user
prompt carries the sentence and the first's does not. If `step` is too
wide to drive in a unit test, the test drives `note_dispatch` and the
replace in the same way `step` does, and says so.

## 4. What this design does not do, and why

- It does not add the sentence to attempt 1. A first prompt stays byte
  for byte what it is today, so no cassette key moves for a first
  attempt. The register's cases build their wakes and call `run_session`
  directly, so the dispatcher door never touches them (observed: section
  2). The gate's stale line is the check.
- It does not write the attempt on the session row. The night's check
  reads the turns, where a retried session's prompt hash differs from
  the first attempt's. No schema change.
- It does not open `DETAIL_SHOWN` for any kind. That rule has a
  measured reason (click night 47, 2026-09-14) and a stated price of
  entry.
- It does not touch messages. A message retry has its own bound and its
  own detail.

## 5. The acceptance

1. The four-kind test and the door test pass.
2. The gate at the closing commit: zero new reds beyond the eleven frame
   66 recorded, and the stale line unchanged, because no first-attempt
   prompt moved.
3. One night from a worktree at the closing commit shows a retried tick
   whose turns differ from the first attempt's, with the first differing
   line named in the status. That is the walk the brief asks for, since
   the frame touches the prompt and a predicate's caller.

## 6. Estimate

Priced at the push: 40k with its tests. This record: about 15k in this
context. Design review: one agent pass. Implementer: one pass, about
100k on the harness line, because the diff is one field, one door, one
sentence and two tests. Diff review: one pass. The night: wall time on
the 3080, and about 20k in this context to read its result.
