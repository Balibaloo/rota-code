# A retried tick says which attempt it is

Frame 58, a retried tick re-runs the identical session. Design record,
revision 2, 2026-09-23. Rota workflow throughout, except where a line
says meta. Section 9 lists what the design review changed.

## 1. The fault, in one paragraph

A tick wake that fails is dispatched again, up to `tick_attempt_cap`
times, three by default (observed: `rota/core/config.py:121`,
2026-09-23). The retry sends the same prompt at temperature zero, so the
model gives the same answer and the retry is the first session again.
On night 88 four wakes ran three times each, and every turn of each
triple is identical, user and completion (observed: the design review's
probe of `.rota/clickI_night88.db`, 2026-09-23). A retry that writes
can diverge after the write, as night 87's `tests_failing` sessions did,
so the fault is the prompt and not every turn. `tick_batch_start` writes
"attempt n of 3" into its wake's detail on a stalled re-fire and says in
a comment that the second session is therefore not the first one
verbatim (observed: `rota/core/scheduler.py:325-335`). The prompt never
shows that detail, because `DETAIL_SHOWN` in `rota/core/runner.py:239`
holds `tick:tests_missing` alone. `tick:boundary` and `tick:challenge`
write no detail at all. So every retry of every tick kind reproduces the
failure at the price of a full session.

## 2. The scope

Five places, read on 2026-09-23 (observed: the map tool and the files).

- `rota/core/scheduler.py:32`, `class Wake`, a frozen dataclass with
  `role`, `kind`, `message_id`, `refs` and `detail`.
- `rota/core/scheduler.py:1337`, `note_dispatch`, which counts one
  dispatch of a tick wake in `tick_attempts` and returns the new count.
  Messages return 0 and have their own bound.
- `rota/core/loop.py:296-310`, the one place a tick wake is counted and
  then run: `note_dispatch(conn, result.wake)` at `:298`, then
  `run_session(conn, result.wake, ...)` at `:307`. The scheduler actions
  at `loop.py:258-271` are counted too and run no session, so no prompt
  exists there. `run_session` has three callers, and the other two are
  the register's fixtures (observed: the design review, 2026-09-23).
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
    result.wake = replace(result.wake, attempt=n)
```

`loop.py:23` imports `dataclass` and `field` only, so `replace` joins
that import.

This is the one door for every tick kind. The count is a fact of
`tick_attempts`, written at the same moment, so the number the role
reads is the number the quarantine counts. No predicate has to compute
its own attempt, and no kind can forget to.

### 3.3 One sentence in the prompt

In `build_prompt`, after the subject lines and before the detail door,
for a tick wake whose `attempt` is two or more:

```
This is attempt 2 of 3 on this wake. The earlier attempt did not clear
this wake, so the same answer will not clear it. Do something the
earlier attempt did not.
```

The cap comes from `config_mod.get(sb.ctx.conn, "tick_attempt_cap")`.
`runner.py:28` already imports `config` as `config_mod`, and the sandbox
holds the connection at `sb.ctx.conn` (observed: `rota/core/sandbox.py:262`
and `rota/roles/api.py:40`, the design review). Never a literal.
The sentence says "did not clear this wake" and not "recorded nothing",
because a retry can have written: on night 87 the third attempt of
`developer|tick:tests_failing|bg_1` followed a second that wrote two
rows and still did not clear the wake (observed: the design review's
probe, 2026-09-23). The sentence is
outside `DETAIL_SHOWN`, because it is not a kind's detail. It is a fact
of the dispatch, and it holds for every kind. `DETAIL_SHOWN` and its
rule stay as they are.

### 3.4 `tick_batch_start` keeps its detail

The stalled path in `tick_batch_start` keeps "attempt n of 3: the last
session ended with nothing written and nothing committed". Its number
and the dispatcher's agree, because both are the table's count plus
one. The "3" is a literal at `scheduler.py:334` today. It becomes
`config.get(conn, "tick_attempt_cap")`, so the two sentences read one
cap. The text is unchanged at the default. The detail stays hidden by
`DETAIL_SHOWN`, as today, and `tests/rota/test_batch_start_attempt.py`
stays green. Showing that
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
- It does not cover a repeat that the counter never sees.
  `liaison|tick:quarantined` ran 51 times in night 87 and `tick:agenda`
  36 times, and no such key holds attempts above 1, because `reported=1`
  drains the wake and the next fire is a fresh key (observed: the design
  review's probe of ten night databases, 2026-09-23). Whether those are
  identical sessions is not checked. They are a frame of their own.
- It does not re-measure `DETAIL_SHOWN`'s rule. Night 84 shows the bare
  `observed_entries` reply on all three attempts with an empty detail,
  so the comment's cause at `runner.py:234-239` is incomplete (observed:
  the same probe). A later frame re-measures the rule.

## 5. The acceptance

1. The four-kind test and the door test pass.
2. The gate at the closing commit: zero new reds beyond the eleven frame
   66 recorded, and the stale line unchanged, because no first-attempt
   prompt moved.
3. One night from a worktree at the closing commit shows a retried tick
   whose turns differ from the first attempt's, with the first differing
   line named in the status. That is the walk the brief asks for, since
   the frame touches the prompt and a predicate's caller. If a
   `liaison|tick:observed_entries` retry runs in that night, the status
   names it and reads the refs shape of its reply, bracketed or bare.

## 9. What revision 2 changed

The design review of 2026-09-23 (one reviewer pass, 87k on the harness
line) confirmed the door's coverage, the frozen dataclass, the cap's
reach, the cassette keys, the four triples and the Liaison population.
It found one design fault and six record faults.

- The sentence no longer says the earlier attempt recorded nothing. A
  retry can write and still not clear the wake. Section 3.3.
- "Byte for byte" is true of the four triples and not of every retry.
  Section 1.
- Four line ranges corrected. Section 2 and section 1.
- The cap attribute is named, `config_mod.get(sb.ctx.conn, ...)`, and
  the `replace` import. Sections 3.2 and 3.3.
- `tick_batch_start`'s literal 3 reads the config cap. Section 3.4.
- Two repeats outside the counter and the incomplete `DETAIL_SHOWN`
  cause are named as out of scope. Section 4.
- The walk reads an `observed_entries` retry if one runs. Section 5.

## 6. Estimate

Priced at the push: 40k with its tests. This record: about 15k in this
context. Design review: one agent pass. Implementer: one pass, about
100k on the harness line, because the diff is one field, one door, one
sentence and two tests. Diff review: one pass. The night: wall time on
the 3080, and about 20k in this context to read its result.
