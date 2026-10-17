# Frame 114: history read on "writes are permitted everywhere, and an unexpected change goes to the Architect"

Date: 2026-10-17 17:02. HEAD 19c3acc5. Read-only, Opus, from
`f114/history_brief.md` in session 0e37e9d7's scratchpad. The meta
workflow (this read and the build sessions) reads the rota workflow (the
seats and their doors). The scripts are in the same scratchpad folder:
`roman_words.py`, `count2.py`, `count3.py`, `reply.py`.

**Verdict.** The records hold half of Roman's rule. Law 12 and the
touch route of 2026-09-13 say that a prediction never refuses a write and
that the Architect judges a path the prediction did not name. Two doors
that the meta workflow built later refuse a write because no criterion
names it: the unnamed-definition door of 04325814 and the fence's
criteria clause of e8e1a207. No record holds Roman's words for those
two doors, and the transcripts start on 2026-09-16, after both commits.
On the four nights, 21 refusals are of this kind: 3, 0, 1 and 17. On b4,
all 16 are of this kind, and every one refused a restore of the project's own code.

## 1. The design

The rule in the records, with marks:

- `rota/LAWS.md:337-342`, law 12 (observed: the file at HEAD; entered
  2026-08-09 in 7e3be756 and 27f02dc5, never removed by `git log -S`):
  "Architect also records an **expected touch set** per batch ... It is a
  *prediction*, never a permission — nothing rejects a diff for straying
  outside it. Its job is to make "was this change incidental?" answerable
  at review time instead of arguable. A prediction that could block work
  would quietly become a permission system nobody designed."
- `plans/composition.md:73`, Flows (observed; entered 2026-09-16 in
  9f8cbdf5, ratified page): "A prediction never blocks. Only a fact or a
  ruling gates."
- `rota/roles/prompts/architect/touch_strayed.md` (observed; entered
  2026-09-13 in cf067ce4): "MODE: touch_strayed — the head commit touched
  paths your prediction never named." ... "The prediction never blocked
  the commit. Only your silence holds the merge." The Architect says
  `foreseen` or `mistakes` for every path with `batches.judge_touch`.
- `rota/roles/prompts/developer/touch_mistaken.md` (observed; same
  commit): the Developer takes a mistake out, "restore a file the tree had
  as it stood before the batch with `code.write`", and if a criterion
  needs the file, `msg.escalate_architect`.
- `rota/roles/api.py:15883-15895`, `code.commit` (observed): "Recorded,
  never refused (law 12)." A stray path gets a `touch_strays` row with
  status `open`, and the merge gate holds until the Architect judges it.
- cf067ce4's body (observed): "Roman found the gap on 2026-09-13 after
  clickI night 32 merged `echo_json` in two files the Architect's touch
  set never named, and nothing asked." This is the nearest record of
  Roman's own call on the route. His words are not quoted (reasoned: the
  transcripts start 2026-09-16).
- `rota/ROLES.md:150-170` (observed): the Architect is "Woken by ...
  touch_strayed"; the Developer "Never builds what nobody asked for.
  Noticing something else is a scope question or a `ledger.log`, never a
  quiet fix".
- `plans/composition.md:23` and `rota/ROLES.md:249` (observed): "Sign-offs
  after that, including on merges, are opt-in." These are the Principal's
  sign-offs, not the Architect's.

The doors that refuse by criteria, with their entry:

- 04325814, 2026-09-14, "fix(desks): a definition no criterion names keeps
  its source" (observed: commit body). Built by the meta workflow after
  click nights 47 and 48, where a rewrite of `echo` broke 19 project tests.
  The body cites `plans/wake-audit.md`, finding 47, and no ruling of
  Roman (observed).
- e8e1a207, 2026-09-10, "feat(fence): a written file reaches only what the
  criteria name" (observed). The body says: "This is a fact about the
  file, not a judgement about the code, and it is not a sandbox ... The
  fence stops the accidental case: a small model reaching for a capability
  nobody asked for." `rota/AUDIT.md`, rows 2, 4, 5 and 6, names the fence
  as the backstop against words in a repository that persuade a model
  (observed). So the fence is a trust door, not a scope door (reasoned:
  the audit's own words).

No record says that a change outside the criteria goes to the Architect
for sign-off at symbol grain. The touch route works at path grain. Since
72337142 (2026-10-13), a judged name `path::Name` judges the open stray
of its path. A stray is still raised only for a path outside the touch
set (observed: `_outside_prediction` at `api.py:15889` and the commit
body).

## 2. Roman's own words

The transcripts are 105 files from about 2026-09-16 to today. A keyword
stream of his typed messages for "sign off", "sign-off", "unexpected",
"permitted", "anywhere", "any file", "strayed", "touch set", "architect",
"restore", "prediction", "permission", "scope", "criterion names" finds
these lines (observed: `roman_words.py`, 2026-10-17 17:00):

- 2026-10-17T15:50:54Z, session 0e37e9d7: "File writes were always
  permitted everywhere, just that if there were unexpected changes then
  the architect is required to sign off. I thought we already discussed
  this, did you look into this?" The session recorded it in the stack at
  16:51 (66e328ab), marked (ruled: Roman, in his words).
- 2026-09-22T18:28:44Z, session 41cb5184: "You have signoff to run the
  nights". Not about this rule.
- 2026-09-30T21:29:04Z, session 7448850f: "If work is out of scope it can
  criticize it, good but but strictly required, however does the
  inspector not tell the builder what's wrong?" About the Critic, not a
  write door (reasoned: the context is the Critic's review).
- 2026-10-11T13:23:43Z, session be3ef742: "What if, when the principal
  opts out of review, the architect reviews assumptions with relevant
  constraints and escalates if there are issues?" This opened frame 204,
  the note categories. Its ruling of 2026-10-11 15:49 and 16:01 sends only
  a default on constrained code to the Architect's structural review
  (observed: `plans/frame204-design.md:36`). Not a write door.

No message of his rules on the unnamed-definition door or on the fence's
criteria clause (observed: the stream). His ruling on the touch route
before 2026-09-16 exists only as cf067ce4's report of it (reasoned: no
transcript is older).

## 3. The doors against the design

Counts come from the Developer turns of each night database, opened with
`mode=ro`. Each turn's new tool results are read after the previous
completion. Turns whose previous completion was not found fall back to
the largest count in one turn of the session (observed: `count3.py`,
2026-10-17 17:00). The counts are a lower bound (reasoned: 20 to 97 turns
per night did not match, and the last reply's results are not stored).
The read of night 154 counts 14 drops refusals in s341 to s388. This
read counts 9 in the 16 b4 sessions (observed: `plans/night154-read.md:211`
against `count3.py`).

| Door | Refusal text | Code at HEAD | What it refuses | What the design says | Architect route | Offered in the text |
|---|---|---|---|---|---|---|
| Fence, dynamic and other reaches | "reaches the dynamic at line 49 ... and no criterion of this batch names loading or evaluating code" | `rota/core/fence.py:144-169`, called at `api.py:14973` with `_baseline` = the working file | a new reach no criterion names | a trust door by AUDIT.md. A reach the base already made is the project's. The baseline must be the batch's base, frame 220. An unnamed new reach that is not unsafe is an unexpected change for the Architect (reasoned: Roman's words) | `msg.escalate_architect` is in `tests_failing.tools` (observed) | no. It says "name the criterion and the words it lacks in your reply, and end" |
| Unnamed definition, 04325814 | "this write changes X, and no criterion of this batch names it" | `api.py:15345-15370`, `_changed_unnamed_defs` at `api.py:16452` | a change to a definition no criterion names, unless the new source equals the base byte for byte | permitted. A change the touch set or criteria do not expect goes to the Architect (reasoned: Roman's words and law 12's "permission system nobody designed") | same | no. It says "A change to X needs a criterion that names it" |
| Drops, whole-file rewrite | "this rewrite of src/click/decorators.py drops custom_version_option, help_option" | `api.py:15322` and `15337` | a rewrite that loses names the file or the tests still use | a fact about the file: the file breaks. "Only a fact ... gates" (reasoned: composition Flows) | not needed | n/a |
| Span "falls inside" | "start=..., end=...: start=... falls inside version_option" | `api.py:14445` | a span edge inside a statement | a fact: the span cuts a statement | not needed | n/a |
| Syntax | "is not valid Python" | the parse door | a file that does not parse | a fact | not needed | n/a |

The refusals that the design routes to the Architect are the fence's
criteria refusals and the unnamed-definition refusals (reasoned: the
table). The fact doors stay.

| Night | Fence | Unnamed definition | To the Architect by design | Fact doors (drops, span, syntax, cycle) |
|---|---|---|---|---|
| 107 | 0 | 3 in 3 sessions | 3 | 2 + 3 + 5 + 0 |
| 111 | 0 | 0 | 0 | 15 + 10 + 5 + 1 |
| 112 | 0 | 1 in 1 session | 1 | 41 + 10 + 10 + 1 |
| 154 | 16 in 4 sessions, all dynamic | 1 in 1 session (s130, `__getattr__`) | 17 | 24 + 14 + 19 + 0 |
| 154, b4 alone, 16 sessions | 16 | 0 | 16 | 9 + 6 + 10 + 0 |

(observed: `count3.py` on `.rota/clickI_night107.db`, `111`, `112`,
`154`, 2026-10-17 17:00.)

Other facts from the databases (observed, same time):

- The touch route never fired on these nights for the b4 shape. Night
  154 has 0 `touch_strays` rows. b4's touch set names
  `src/click/decorators.py` and `tests/test_basic.py` at path grain, so a
  change to `version_option` inside that file is never a stray. Night 107
  has 3 open strays, night 112 has 1 judged `foreseen`.
- The Developer called `msg.escalate_architect` 8, 20, 23 and 14 times on
  nights 107, 111, 112 and 154. On b4 it escalated on the
  `ver_opt_show_py` criteria and on `inh_dcc9ea38`. So the route exists in
  the mode and the seat uses it, but no refusal points to it.
- Night 111's and night 112's large counts are drops refusals, which are
  facts about truncated rewrites. The read of 2026-10-04,
  `plans/frame114-read.md`, places their cause in import lines that no
  door guards (observed: the stack's status of 2026-10-04 14:25).

## 4. The gap

The records settle the principle: a prediction is never a permission,
only a fact or a ruling gates, and an unexpected path goes to the
Architect, who judges it foreseen or a mistake (observed: law 12,
composition Flows, cf067ce4). The records do not settle the
unnamed-definition door and the fence's criteria clause. The meta
workflow built both from night failures, without a ruling of Roman, and
both refuse a write by the criteria, which is a permission (reasoned:
law 12's last sentence names that outcome). Roman's words of today put
these two doors against the design. Write his words as a ruling under
law 12 in `rota/LAWS.md`, or in `rota/DECISIONS.md` beside 04325814's
entry, with the mark (ruled: Roman, 2026-10-17 16:50 local, 15:50:54Z in the transcript). On b4 the
contradiction did not cost the batch through the unnamed-definition
door. The fence's working-file baseline cost it, frame 220, because
every refused restore was the base's own `import importlib.metadata`
(observed: `plans/night154-read.md:214-217`).

The frame is a door fix, cause 8 by `plans/wall-guide.md` section 4
(reasoned: a door refuses a right write that the design permits). The
cheapest pass, in order:

1. Frame 220 first: the fence's baseline becomes the batch's base, the
   same `project_root` file that `_changed_unnamed_defs` already reads.
   Red test: s347's write of `decorators.py` with `import
   importlib.metadata` at line 49 is refused today and lands after.
2. Then the unnamed-definition door stops refusing. It records the change
   as an unexpected change, a `touch_strays` row at symbol grain,
   `path::name`, so the Architect's `touch_strayed` wake judges it and the
   merge holds until then. Red test: s138's `__getattr__` write on night
   107 and s130's on night 154 land, and each writes one open stray that
   `batches.judge_touch` accepts.
3. The fence keeps its refusal for a new unsafe reach (AUDIT.md), and its
   text names `msg.escalate_architect` beside the criterion route.

The question for Roman, if any, is one: does step 2 also cover the
fence's new reaches, or does the fence stay a refusal because AUDIT.md
names it as the trust backstop. Recommended: the fence stays a refusal
for network, process, removal and outside paths, and step 2 covers
definitions only (reasoned: AUDIT.md rows 2 to 6). Rate: [med].

## Usage

About 75k tokens of this agent's context at the report's write, by this
agent's estimate. Read the harness line for the real figure. No
sub-agents.
