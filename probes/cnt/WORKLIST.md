# Under-informed: the worklist

**Under-informed is the problem. Bad output is the symptom.**

Five points where information is lost, upstream first. Each is downstream of the
ones above it, so they are taken in order and not in parallel.

The loop for each: say what should happen · find why it doesn't · fix it ·
re-run onboarding on cnt · score against `answer_key.yaml`. **If the score does
not move, stop and say why.** A fix that does not change the number is a
hypothesis that was wrong, and carrying on past it is how three dead hypotheses
got stacked on `L1-DV-fix-the-code-not-the-test`.

## What five runs established

```
run   context              brief    turns  areas  terms  terms_required  must_not_mean
new   grain list           6,950     105    5/5      8       0 of 10      5 hits
fix   grain list           6,950     195    6/6      9       0 of 10      nothing present
v0    grain list           6,950      88    4/6      1       0 of 10      nothing present
v1    grain list           6,950      88    6/6      8       0 of 10      nothing present
B     code.vocabulary      1,370     161    3/6     27       4 of 10      3 hits, 5 present
C     code.vocabulary      1,493      54    6/6     14       4 of 10      2 hits, 3 present
```

**One change moved the number, and it was the data.** Five mechanical fixes --
the indexer's suffix map, three import-resolver bugs, collision starvation, a
path dead end, label-as-sense -- left `terms_required` at 0 of 10 every time.
Replacing the pushed grain list with words-in-use moved it to 4 on the next run.

The reason is that the input was specifying the answer. A session woken to
"define this area's terms" and handed a list of symbols can only read that as
"define these", and it was right to: 21 of the 28 terms written across the first
four runs were exactly a symbol name or a path fragment, and the rest were
generic words about software. `getIntentFromTFile: a function that retrieves
intents from a TFile` is a true and accurate answer to the question that was
actually asked.

**Half of all definition work is discarded, silently.** 49 held calls in B, 55
in C, against 99 amends and 14 surviving terms. The batching hold fires on an
action written before its reads came back -- correct, and `s7` proves why: it
wrote `amend('folder')` in the same breath as `code.source(folder.ts)`, so that
definition came from the word list and not the file. The defect is that a held
call is *lost* rather than deferred. The runner says "send them again if they
are still what you want", in prose, in the middle of a wall of results, and the
model does not. `folder`, `text`, `variable` and `template` were all written
correctly and thrown away.

It also produced a false negative on the best area in the repository:
`src/variables/providers` -- `variable`x152, `folder`x47 -- had `folder` and
`variable` held, wrote `validate`, and attested `none_found`.

**Prose is inert, with one exception in a day of counting.** Six times the brief
said the right thing and nothing enforced it: open the files before defining,
the same sense twice is not two senses, citations are evidence, observed not
decided, what `sense_short` is for, the renaming test. Every one needed a gate.
The single exception is C's citation sentence -- 38 attests, zero line numbers --
and it should still be made structural, because relying on the model reading a
sentence is the bet that failed the other six times.

**My own mistakes were all the same mistake.** A `where` column reading
`file:line` cost four abandoned areas, because the model cited it verbatim. A
negative example in a brief came back as the definition of `feature`. A sentence
telling the model to strip line numbers, where a separate `grain` column would
have made it impossible to get wrong. Each time I chose prose or formatting over
structure, which is the thing this document is about.

**Sense quality is untouched by all of it.** `intent` is still "a specific action
or goal" on a plugin where an intent is a note-creation recipe declared in a
note's frontmatter. Reading is now forced and turns out to be necessary and not
sufficient -- the same shape as the survey-citation finding: a session that reads
one file and defines eight words has read, and has not understood.

## Baseline — the run this all starts from

`.rota/cnt_new.db`, commit `766c9e30`, 21 sessions, 105 turns.

```
terms_required present      0 of 10
must_not_mean hits          5
constraints required        0 of 2
decoy constraints recorded  2
empty constraint bodies     2
```

## 0 · `sense_short` reads as a label, and one chain follows from it — STATUS: fixed; score unmoved, two upstream blockers now dominate

**Should happen.** A glossary row carries a sentence saying what the word means
here, and a second sense costs a deliberate argument that is checked.

**Doesn't.** Measured across the 57 `glossary.amend` calls in `cnt_fix`:

```
s2  x8   term='github'      sense_short='repository'   sense_body='a collection of files and…'
s3  x10  term='github'      sense_short='repository'
s6  x3   term='repository'  sense_short='data storage'
s7       term='github'      sense='repository'   sense_short=''   sense_body='a repository on GitHub'
```

The model reads `sense_short` as a **category label**, not a sentence — github is
a repository, repository is data storage — and puts the definition in
`sense_body`. The name invites it.

Four problems that looked separate are one chain:

1. `sense_short` is filled with a label rather than a meaning.
2. A later session takes that label and passes it as `sense=`, leaving
   `sense_short` empty.
3. The duplicate guard added this morning cannot compare it. `_same_sense('')`
   is `''`, and the code does `seen.pop("", None)` first, so **an empty
   `sense_short` always passes**. The second row is written in silence.
4. Two rows now share `github`. `term_collision` fires, and costs 45 turns.

So the `github`/`repository` collision that dominated the run, the blank index
lines, and the hole in my own guard are all downstream of step 1.

**Not a dedup failure.** The derivation half is solid and should not be touched:
57 calls produced 11 rows, `s2`'s eight identical calls produced one, `s19`'s
thirty-nine across nine terms produced nine. Accidental duplication is genuinely
impossible. It is the *escape hatch* that leaks.

**The fix.**

  * Ask for the long explanation first and the one-liner after, so the short
    field is a summary of something already written rather than a category
    guessed at. The signature the model sees is derived from the implementation,
    so the parameter order is the ask.
  * Refuse an empty `sense_short` outright instead of accepting a body-only row.
    The index line is what every downstream reader is shown, and it is also what
    the duplicate guard compares — an empty one disables the backstop.

**Measured by.** `must_not_mean hits` read together with `terms_required
present`, and turns spent on `tick:term_collision`. Baselines: 0 of 10 present,
45 turns.

**Result — `cnt_v0.db`, Terminologist phase only, 14 sessions, 88 turns.**

```
glossary                  1 term    (cnt_fix: 9, cnt_new: 8)
terms_required present    0 of 10
must_not_mean             nothing to score -- none of those terms written
areas surveyed            4 of 6; src/intents and src/variables abandoned
k0 grew back to           ['.', 'src/intents', 'src/variables']
```

The phase filter works: clean stop on "no survey wakes left", 88 turns against
~190 for a full run.

**The change is not what is blocking.** The blank-`sense_short` refusal never
fired once. The `sense_body` refusal fired only on calls that were empty in both
fields -- `sense_body='', sense_short='', term='github'` -- which is a correct
refusal of a term with nothing under it. No session was stopped by the new
order.

**Blocker one: `.github` cannot be opened at all.** The model writes
`/github/ISSUE_TEMPLATE/bug_report.md`, dropping the leading dot, and `_within`
rejects it as escaping the worktree. 11 of 88 turns ended in that error. The
index stores `.github/...` and the brief renders `.github/...` correctly, so this
is the model mangling a path -- but the consequence is total: it can never open
those files, so it can never cite them, so the area cannot be closed. And
`.github` sorts first, so it is the opening move of every run.

**Blocker two: the read-evidence gate abandons areas.** Sessions cite grains
straight from the `code.survey` listing without opening them, `surveys.attest`
refuses -- correctly, it is the guard added this morning -- the session cannot
recover, and after three attempts the attempt bound quarantines the area.
`src/intents` and `src/variables` were lost that way, and constraint zero grew
back to cover three areas.

That is also why every session wrote the same term. Fifteen `glossary.amend`
attempts across nine sessions, all of them `workflow`: with nothing opened there
was nothing else to define, and the pushed glossary already showed `workflow`
sitting there.

**What I cannot rule out.** `cnt_fix` got 9 terms and this got 1, and the
difference is that `src/variables` succeeded there and was abandoned here. Same
model, same repository. It may be variance, and it may be that adding a
paragraph to `survey.md` cost a session that was already marginal. The clean
single-variable test is to revert the brief edit alone and re-run this phase.

**Deferred, and why.** Ordering areas by size rather than alphabetically was
going to be item 0. It fixes no defect — it reallocates budget, nothing more,
and the claim that it "seeds the glossary with product vocabulary first" is
wrong, because every session is shown the whole glossary regardless. `.github`
did take 64 survey turns plus the 45 above, out of ~190, on 3 grains of 89. But
if this chain is fixed those 45 do not happen, and the budget may suffice
without reordering. Revisit only if budget is still binding after a clean run.

## 0b · A mistyped path was a dead end — STATUS: fixed and verified; score unmoved

**Was.** `code.source('/github/ISSUE_TEMPLATE/bug_report.md')` — the leading dot
copied as a slash — refused by `_within` as escaping the worktree. Terminal: not
openable, so not citable, so `surveys.attest` refuses, so the area is
quarantined after three attempts.

**Now.** A miss is checked against the index first: exactly one grain the
request could be naming, or nothing. The result says which spelling was read and
`ctx.opened` records that one, so the citation resolves. Ambiguity stays refused
— `accounts.py` under both `auth` and `billing` is a misread, and a misread is
worse than an error. `code.write` keeps `_within` unhelped.

**Result — `cnt_v1.db`, Terminologist phase, 12 sessions, 88 turns.**

```
                              cnt_v0      cnt_v1
escapes-the-worktree turns        11           0
areas surveyed                4 of 6      6 of 6
areas abandoned                    2           0
k0 covers                          3           1
glossary terms                     1           8

terms_required present        0 of 10     0 of 10
must_not_mean            nothing to score  nothing to score
```

The mechanism is fixed. Nothing was abandoned, every area closed, and the
lenient resolution fired twice.

**The score did not move, for the third run running.** What the glossary holds:
`FilteredOpenerMissingNotice` (twice — a live collision), `ISSUE_TEMPLATE`,
`TemplateVariable`, `TemplateVariableVariables`, `TemplateVariableVariablesLut`,
`feature_request`, `release`. Identifiers and GitHub-infrastructure words. Not
one of `intent`, `template`, `prompt`, `variable`, `provider`, `frontmatter`.

**What three runs now say.** Three mechanical blockers found and fixed —
starvation by an unparked collision, label-as-sense, a path dead end — and
`terms_required present` has been 0 of 10 every time. Coverage improves, cost
improves, abandonment goes to zero, and the artefact does not change at all.

That is what items 4 and 5 predicted and they are still not started. The brief
still never says what the project is: `Obsidian` 0, `plugin` 0, `note` 0,
`template` 0 in an 8,050-character prompt. And the unit of work still cannot
hold the answer — `intent` is declared in `intentsSchema.yaml`, parsed in
`src/intents`, stored in `src/settings`, extended in `src/templates`, filled
from `src/variables`, so no area-shaped question reaches it.

Everything fixed so far was beneath the question. Nothing has yet been aimed at
it.

**Minor, noted not chased.** `k0` still binds `.` although `.` was surveyed
`none_found` — constraint zero was recomputed at session 15 and the survey
landed at 17.

## 1 · A reported collision was offered again forever — STATUS: fixed and verified; score unmoved

**Should happen.** A role that has done the only thing its mode permits is not
offered that work again.

**Doesn't.** `scheduler.waiting_on` derives waiting from `messages WHERE verb =
'question' AND status = 'open'`. `term_collision` mode's entire working set is
`glossary.consult`, `glossary.lookup`, `msg.report_liaison` — one productive
verb, and it writes verb `report`. So the one mode that can only report can
never be seen as waiting.

Measured: s3 sent `msg.report_liaison` with both refs on turn 3, its first
opportunity, exactly as briefed. Three messages went out — `m3`, `m5`, `m7` —
all verb `report`. `waiting_on('terminologist')` returns `[]`. The wake fired
six more times and three of those sessions burned the full 12-turn cap with
nothing left to try.

`waiting_filter`'s own docstring describes this outcome for a different
predicate: *"the role is woken with identical state, asks again -- the duplicate
guard refuses it -- hedges, and repeats until `loop_cap` is spent."*

**Measured by.** Turns spent on `tick:term_collision` in a run containing a
duplicate term. Baseline for that run: 44 of 71, 61%.

**Where the fix went, and where it did not.** Not `waiting_on`. Widening it to
count `report` would have been wrong: `waiting_filter` suppresses every band but
traffic for a role, so a Terminologist that reported a collision in one area
could not survey another. A report is not a question — you do not need an answer
to carry on.

It went in the predicate, because `contradiction` — the twin `term_collision`'s
own docstring names — has had exactly this check all along and terminates
because of it:

```python
asked = conn.execute(
    "SELECT COUNT(*) n FROM messages WHERE status='open' AND to_role='principal' "
    "AND verb='clarify'").fetchone()["n"]
return [] if asked else [Wake(...)]
```

`term_collision` was built as the glossary's `contradiction` and copied the
intent without the check. So it now reads open messages' `body_refs` alongside
`decisions.refs` and skips a term already in front of somebody. Eight lines, one
function, no schema change, no new column, no new verb — the durable fact is the
open message, which is why the `conflicted` flag was not needed.

By refs rather than `contradiction`'s cruder "any open clarify exists", so one
reported collision does not hide every other, and a third sense joins the open
case instead of raising a new one.

**Re-run result — `cnt_fix.db`.** The starvation is gone and the artefacts are
no better.

```
                        cnt_ix (before)     cnt_fix (after)
tick:survey            2 sessions / 18     20 sessions / 133
survey records                    0                     13
areas surveyed                    0 of 6                 6 of 6
tick:term_collision    6 sess / 44 turns   6 sess / 45 turns

scored against answer_key.yaml
terms_required present            0 of 10               0 of 10
must_not_mean hits                --                     0   <- absence, not a pass
constraints required found        0 of 2                0 of 2
empty constraint bodies           --                     1
```

**The `0` on `must_not_mean` is not a pass.** None of `text`, `number`,
`natural_date`, `note` or `folder` were written at all, so there was nothing to
score. It reads as an improvement on the baseline's 5 and is not one — the two
lines have to be read together, and `terms_required present 0 of 10` is the one
that says so. A flaw in the instrument, not in the run.

What the glossary holds instead: `getRelativePath`, `getVariableValues`, `path`,
`symbol`, `TemplateVariable`, `GenericInputPrompt` — symbol names again — plus
`github` and `repository`, both of them twice with an empty `sense_short` on the
second row. One of the two constraints is `"Variables area has not been
surveyed"` with an empty body, which is constraint zero's own text written back
as a finding.

**So item 1 is fixed and the number it was aimed at moved; the number that
matters did not.** That is the expected shape — item 1 was a starvation bug, not
a quality one. Items 4 through 7 are untouched and are where quality lives. The
run also hit the 40-session limit without reaching quiescence.

**Still open here, and a new observation.** `term_collision` cost the same 45
turns, for a different reason: sessions woken for `repository`
(`wake_refs=["repository","repository#data_storage"]`) reported
`refs=['github','github#repository']` — the wrong term's ids, three times. So
`github` parked correctly and `repository` never did, because nothing ever
referenced it. The guard behaved exactly as specified; the refs were wrong. The
system knows what it woke the role for and does not check that the report is
about that, and in this mode there is exactly one thing to report — so
`msg.report_liaison` could default its refs to the wake's. Not done; it is a new
fix.

Verified against the livelocked database itself: `term_collision` now returns
`[]` on `cnt_ix.db`, and `outstanding` still carries the word under
`awaiting_principal` — parked, not discharged. `survey` appears in `outstanding`
for the first time. Regression test in `test_predicates.py`, proved to fail with
the guard reverted. 923 deterministic tests pass.

## 2 · ~~A term collision has no discharge without the principal~~ — STATUS: not a defect

**Withdrawn on measurement.** I read `term_collision`'s discharge condition —
a row in `decisions` — saw that no role which can write one runs during
onboarding, and concluded the obligation was permanently undischargeable. I did
not check whether it had reached the party who writes decisions. It had:

```
m3  terminologist -> liaison    report    answered   refs=[both ids]
m4  liaison       -> principal  clarify   open       refs=[both ids]
m6  liaison       -> principal  clarify   open       refs=[both ids]

outstanding:  awaiting_principal  owners=['principal']  refs=[... issue_template#...]
```

The routing worked end to end untouched. `awaiting_principal` is the correct
resting state: a collision is a judgement call, it is parked with the one who
makes it, and the run can go quiescent with it on the agenda. That is what
onboarding is for — `observed` facts, and the decisions handed up.

**No code required.** It folds into item 1, which also explains `m4` *and* `m6`:
the Liaison forwarded twice because the Terminologist reported twice, because
the wake kept firing. The churn duplicated the principal's agenda as well as
burning the turns.

**Left over, and not a loop.** `outstanding` lists `term_collision` under
`owners=['terminologist']` while the item is with the principal, so the register
names a role that has no verb to deliver it. An ownership label, worth a line
when item 1 is done.

## 3 · The indexer drops the domain — STATUS: fixed, evaluation blocked

**Should happen.** A survey of an area sees what a person opening that directory
would see.

**Doesn't.** `indexer.walk` keeps a file only when `languages.for_path`
recognises its suffix, and `BY_SUFFIX` is built from the tree-sitter language
list. `intentsSchema.yaml`, `README.md`, `manifest.json` and `versions.json` are
dropped before anything else in the system exists. `intentsSchema.yaml` is
`import`ed by `src/intents/frontmatter.ts` — a build dependency of the parser,
not documentation beside it.

**Measured by.** `terms_required present`, and whether any run finds
`the_frontmatter_schema_is_a_public_contract`.

**Fixed.** `walk` keeps every tracked file; `build` indexes one with no parser
as a path grain with no symbols, excluding lockfiles, minified bundles and
anything that fails to decode as UTF-8. Three separate resolver bugs surfaced
while checking the result and were fixed with it:

  * `as_posix` does not collapse `..`, so every candidate from a `../` import
    contained a literal `..` and matched nothing, in any language;
  * `/index.ts` was missing from the suffix list while `/index.js` was there, so
    every TypeScript barrel import failed;
  * `target[:2]` was tested against `"../"` — two characters against three — so
    `../anything` never took the relative branch at all and fell through to the
    Python dotted-relative one, which read `..` as a package separator.

Measured on cnt: the four domain files are indexed, `intentsSchema.yaml` carries
fan_in 1 because `frontmatter.ts` imports it, area `.` goes from 4 grains to 17,
edges 10 → 47, unresolved 60 → 23 (the remainder are external packages).

**Evaluation blocked — and the cause is not what it first looked like.** My
first reading was that indexing every text file made `.github/` a sixth area
that drowned the run. Measured, that is wrong. `.github` is **3 grains of 89**
and got **one** survey session.

What consumed the run was a **term-collision livelock**: 44 of 71 turns, 61%,
across six sessions, every one of them on the single term `issue_template`.
Three of those hit the 12-turn cap.

The mechanism, and it is a rota defect rather than an indexing one:

1. A Terminologist surveying `.github` wrote two senses of `issue_template` —
   bug report and feature request. Reasonable; they are two things.
2. `term_collision` fires: two rows share a term and no decision refers to them.
3. `term_collision` mode **forbids amending the glossary**, deliberately —
   *"Collapsing two senses is a decision, and you are not in a mode where
   decisions are available."*
4. So the role does the only thing left and reports to the Liaison. A report is
   not a decision.
5. The predicate discharges on a decision referencing the ids, or on the
   glossary coming back to one sense. Neither happens.
6. **The principal never runs during onboarding.** `decisions: 0`, `ledger: []`.
7. So it fires again, and again.

One session tried to end it by writing a third row — `issue_template: "template
used for bug reports and feature requests"`, the merged sense. That is the right
instinct and it made things worse: three rows sharing the term instead of two,
and still no decision.

**So any glossary collision created during onboarding is an unbounded wake
source.** The baseline never hit it because it happened to produce no
collisions. The indexer change did not cause this; it produced the first
collision and the livelock did the rest.

Excluding `.github` would hide this rather than fix it, so it is now item 0
below and the indexer stays as it is until that is settled.

**Still true and still worth doing later:** `.editorconfig`, `.eslintrc` and
`.npmrc` are noise in area `.`, and `SKIP_DIRS` already holds five directories
whose common property is a leading dot. That is a tidying, not a fix.

## 4 · The brief never says what the project is — STATUS: not started

**Should happen.** A session knows what the program does before being asked what
its words mean.

**Doesn't.** Counted in one 8,050-character system prompt: `Obsidian` 0,
`plugin` 0, `note` 0, `template` 0, `purpose` 0. A Terminologist receives role
instructions and 26 identifiers.

**Measured by.** `must_not_mean hits`, which is the direct test of whether a
session had enough context to reject the everyday reading of a word.

## 5 · The unit of work cannot hold the answer — STATUS: not started

**Should happen.** Something asks what the program is for, once, and owns the
answer.

**Doesn't.** Every survey wake is for an area, and an area is a folded
directory. `intent` is declared in `intentsSchema.yaml`, parsed in
`src/intents`, stored in `src/settings`, extended in `src/templates` and filled
from `src/variables`. No area contains it. No area-shaped question can produce
it, and none did.

**Measured by.** Whether `intent`, `template` and `prompt` appear at all.

## 6 · Absence is silent — STATUS: not started

**Should happen.** A session can tell the difference between "this area holds
four things" and "this area holds four things I am willing to show you".

**Doesn't.** `code.survey` returns an area's grains as though they were its
contents. The Architect woken for `.` saw a build script and a version bumper,
with nothing indicating that four files in the same directory were withheld,
and wrote "Commitment to an external system in esbuild.config.mjs" — the only
answer available in the room it was in.

**Measured by.** `decoy constraints recorded`.

## 7 · Nothing downstream can detect under-information — STATUS: not started

**Should happen.** A run that learned nothing does not report success.

**Doesn't.** Every gate checks that an act occurred — files opened, paths real,
a field non-empty — and none checks what was known. The baseline run ends with
`k0` fully discharged, `outstanding` showing only `awaiting_principal`, and an
empty frontier.

**Measured by.** Whether the baseline database, replayed, produces any signal at
all that something went wrong.

---

## Not on this list, and not under-information

The second-person collapse. `s8` turns 8, 9 and 10 are byte-identical and turn 8
opens with the system's own wake line. It begins at **turn 2, 2,535 characters**
— 13 of 105 turns across 6 of 21 sessions. `llama3.1:8b` does not reliably hold
"I am the one being asked" past one exchange. No amount of information fixes it;
the options are a stronger model for the understanding roles or a prompt shape
that does not invite continuation. Tracked separately so it is not credited to,
or blamed on, anything above.
