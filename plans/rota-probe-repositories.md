# Probe repositories: the smallest thing that makes onboarding legible

## The problem with the repositories used so far

`oauthlib` and `icalendar` are real, which is their value and their cost. Nobody
holds the answer key. When a survey session wrote

> **Alarm**: an event that triggers an action

there was no way to score it without reading the RFC. It is not wrong. It is not
useful either, and "not useful" is exactly the judgement a test cannot make.
Every measurement this session had to be about *structure* — did the session open
a file, did it cite inside the area, did it write the word twice — because
structure is the only thing that was checkable. The question that matters,
**did it understand the code**, went unmeasured on every run.

A probe repository is one where that question has an answer written down in
advance.

## The two properties that make a probe work

**1. A word whose domain meaning is decidably different from its everyday one.**
This is the whole trick. If the domain sense and the general sense agree, a
session that read nothing and a session that read everything produce the same
glossary entry, and the artefact cannot tell you which one you had. When they
disagree, the failure is not weak — it is *wrong*, visibly, to anyone holding the
key.

**Strongest of all: a word that also has a common meaning in software**, because
that is the sense a model reaches for by default. `hold`, `call`, `frame`,
`credit`, `flag`, `velocity`. The predicted wrong answer is known in advance,
which turns a vibe into a scoreable prediction.

**2. A commitment that is real, findable, and stated in code — not in prose.**
The Architect's survey looks for a commitment the code keeps to something outside
itself. If the README states it, a session can pass by copying, and you have
measured reading comprehension of English. Put it in a constant, a guard clause,
or a test name. Then finding it requires opening the file.

**And one decoy each** — something shaped like a commitment that is not one (a
tunable default, an arbitrary buffer size). Constraint zero shrinking on a decoy
is a false positive, and a probe with no decoys cannot detect one.

## The list

Each is 6–12 files, 200–400 lines, with tests. Ranked by how sharply the trap
cuts.

### 1. Library loans — `hold`
- **Trap**: a *hold* is a patron's claim on the next available copy. Predicted
  wrong answer: "a lock preventing concurrent access."
- **Second trap**: `renew` is extending a loan, not re-creating a resource.
- **Commitment**: a loan may be renewed at most twice, and not at all while
  another patron has a hold. Lives in `loans.py` as a guard clause.
- **Decoy**: `PAGE_SIZE = 50` in the catalogue search.
- **Passes if**: the glossary says a hold is a claim on a copy *and* the survey
  finds the renew/hold interaction. **Fails visibly if**: `hold` is glossed as a
  lock. That is the whole test in one row.

### 2. Double-entry ledger — `credit` / `debit`
- **Trap**: the best trap word in software, because the domain meaning is the
  *reverse* of the everyday one — a credit to a liability account increases it.
  Almost everyone gets this backwards, including models, confidently.
- **Commitment**: every transaction's entries sum to zero; no entry may be
  amended after the period closes.
- **Decoy**: a `ROUNDING = 2` constant.
- **Why it is strong**: the wrong answer is not vague, it is inverted. A glossary
  that says "credit: money added to an account" is unambiguously a fail.

### 3. Chess tournament clock — `flag`
- **Trap**: to *flag* is to run out of time (a verb, an event). Predicted wrong
  answer: "a boolean marker."
- **Commitment**: a player who flags against an opponent with insufficient mating
  material draws rather than loses (FIDE 6.9) — about 30 lines, and a real
  outside commitment: the code keeps a promise to a rulebook.
- **Decoy**: a configurable increment default.

### 4. Elevator dispatch — `call`
- **Trap**: a *call* is a request from a floor. In a codebase, "call" already
  means something else to every reader, which makes this the sharpest
  within-software collision on the list.
- **Commitment**: the car does not reverse direction while calls remain ahead of
  it in the current direction.
- **Decoy**: `DOOR_DWELL_MS = 3000`.

### 5. MIDI sequencer — `velocity`
- **Trap**: *velocity* is how hard a key was struck, not how fast anything moves.
- **Commitment**: every note-on is matched by a note-off; a channel may not be
  left sounding.
- **Decoy**: a default tempo.

### 6. Bowling scorer — `frame`
- **Trap**: a *frame* is a turn. Competes with stack frame and UI frame.
- **Commitment**: a strike in the tenth frame grants two fill balls.
- **Note**: the most famous kata on the list, which is a *weakness* — the model
  has read it many times and may recall rather than read. Useful precisely as a
  control for that: compare against #4, which it has not memorised.

## What the answer key looks like

One YAML per probe, scored after onboarding:

```yaml
terms_required:
  hold:
    must_mean: ["claim", "reservation", "next available copy"]
    must_not_mean: ["lock", "mutex", "concurrent"]   # the predicted failure
commitments_required:
  - renew_limit          # a loan renews at most twice
  - renew_blocked_by_hold
decoys:
  - PAGE_SIZE            # recording this as a commitment is a false positive
```

`must_not_mean` is the part worth having. It is the only assertion on this page
that can catch a plausible answer, and plausible answers are the failure mode —
`Alarm: an event that triggers an action` would pass every structural check the
system now has.

## Two variants of each, to isolate one variable

- **With a README that explains the domain.** Establishes the ceiling: what the
  system produces when the answer is handed to it in prose.
- **Without.** The real measurement. A gap between the two is the size of the
  reading problem, stated as a number instead of an impression.

## Recommendation

Build **#1 (library loans)** first, both variants. It has the cleanest predicted
wrong answer, the commitment is a genuine interaction between two rules rather
than a lone constant, and nothing about it is memorised.

Then **#2 (ledger)**, because an inverted trap catches a different failure from a
merely unfamiliar one: #1 tests whether the session read the code, #2 tests
whether reading the code beat what it already believed.

Keep `icalendar` in the rotation regardless. The probes measure understanding;
only a real repository measures whether the system survives contact with one.
