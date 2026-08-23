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

**One change moved the number, and it was the data.** *(Falsified by `cnt_h`
— see item 9. Three things changed together; the brief carries the recall and
the data carries the precision. Left standing as written because the reasoning
below it is still right about the grain list, and only wrong about what
replaced it.)* Five mechanical fixes --
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

## 8 · The word list has a ceiling, and it is 4 of 10 — STATUS: measured, not started

**Should happen.** Every word the project is built on is offered to some session,
in the area that would teach it.

**Doesn't.** `code_vocabulary` ends `for word, n in uses.most_common(8)`. Eight
words per area, ranked by raw use. Computed over all five parseable areas of cnt,
the **union of every block any session can ever see** is:

    intent · note · setting · global · notice · plugin · opener · filtered
    template · filter · option · variable · selection · value · property
    folder · text · component · button · gathered · submit · date · validate · format

Four of the ten required terms are in it — `intent`, `template`, `variable`,
`selection`. The other six are shown to nobody, in any area, in any run.

**4 of 10 is not a plateau. It is the ceiling, and B, C and D each sat exactly on
it.** F and G scored 3, below it. Six runs of model-side improvement have been
measured against a number that was capped by an integer literal upstream.

**Three causes, and only one of them is the cut.**

*Decomposition destroys the compounds.* The operation that recovers `intent` from
`getIntentsFromFM` is the operation that ruins three of the six:

    variableType   -> ['variable']            `type` is in _NOT_VOCABULARY
    filterSet      -> ['filter']              `set` is in _NOT_VOCABULARY
    globalIntent   -> ['global', 'intent']    two rows, each an ordinary word

Area `.` shows `intent:61` and `global:17` as separate entries. The concept is on
the page, shredded into two words that each read as English. **A vocabulary of
single words cannot carry a compound term, and three of the ten are compounds.**
No cut size fixes this.

*The cut drops near misses in the one area that would have taught them.*
`frontmatter` is #10 in `src/variables/providers` at 15 uses — two slots below
the fold, in the directory where it is the frontmatter key every provider reads.
`prompt` is #14 in `src/variables` at 8.

*One is genuinely rare and frequency will never find it.* `provider` has 8 uses
in the whole repository. It is the name of a directory — `src/variables/providers`
— and naming a directory is how a codebase says "this is a kind of thing". The
path is evidence the word list does not read.

**Scored against what was actually on offer, the runs look nothing like 4 of 10.**

    run    of 10    of the 4 offered    found beyond the list
    B      4        4 of 4              —
    C      4        4 of 4              —
    D      4        3 of 4              frontmatter
    F      3        3 of 4              —
    G      3        3 of 4              —

**75 to 100 percent.** The word-list change did not take coverage from 0% to 40%;
it took it from nothing to everything available. Every run since has been
re-measuring a full house and reading it as a failing grade. The `4 → 3` between
D and G, which reads as a regression, is one word of noise against a cap.

**D found `frontmatter` and it was never on the list** — it is #10 in
`src/variables/providers`, below the fold. It came from the session opening
`frontmatter.ts`, which is the escape route this item needs: a file *name* is a
term the project chose to write down, and so is `enum TemplateVariableType`.
Declarations and paths are term sources, and neither is ranked by frequency.

**What decomposition actually added, measured against the list it replaced.**
Taking `code_index` as `code.survey` hands it over — path segments and symbol
names, nothing split on case — the *grain list already held five of the ten* as
whole tokens:

    intent · template · variable · provider · frontmatter

The decomposed word list offers four: `intent`, `template`, `variable`,
`selection`. **It offers one required term the grain list could not (`selection`,
which exists only inside identifiers) and buries two the grain list named
outright** — `provider`, which is a directory, and `frontmatter`, which is a
file. Both are below the frequency fold at 8 and 15 uses. On required terms the
trade is minus one.

And of the 24 words the five blocks offer between them, 7 are in the key and 17
are not. Sixteen of the 24 exist only inside identifiers, and exactly one of
those sixteen is a term: the other fifteen are participles and generic nouns
that decomposition manufactured — `filtered`, `gathered`, `opener`, `submit`,
`validate`, `format`, `value`, `property`, `option`, `component`, `button`.

**So decomposition is not the mistake, and its win was never vocabulary.** The
grain-list runs scored 0 of 10 while *containing* 5 of 10. Presence was never
the problem; 89 grains with `getIntentsFromFM` sitting beside `intent` read as
"define these symbols", and 21 of 28 terms obediently were symbols. What
decomposition supplied was a short ranked list of lowercase words that do not
look like things to copy. The score moved because the session stopped
transcribing, not because it learned any new words.

**Frequency is the mistake.** It is the selector bolted on beside decomposition
in the same change, and it is blind to the two loudest statements a codebase
makes about what a thing is: a directory named `providers`, and a file named
`frontmatter.ts`. A name a person chose for a *folder* outranks a name they
typed 150 times inside one function, and `most_common` cannot express that.

**Which makes the fix one change, not two.** Keep the decomposition; replace the
selector with where the name is *declared* — directory, filename, exported type,
enum member — and let frequency break ties. That recovers `provider` and
`frontmatter` on the first run, because both are already whole tokens, and it is
the same mechanism that can carry `TemplateVariableType` as one compound instead
of shredding it.

**Correction, from the `cnt_h` work.** "Shown to nobody" is too strong, and the
overstatement was mine. It is true of the *word list* — none of the six is in
any area's eight. It is not true of the run, because `code.area` hands over
source and the sessions found three of them there and wrote them down:

    d   prompt          GenericInputPrompt      "class extending Modal"
    d   provider        variable_provider       "Obsidian variable provider"
    f   variable_type   TemplateVariableType    "Obsidian TemplateVariableType"
    g   provider        variableProvider        "Function returning variable values"
    h   variable_type   TemplateVariableType    "Data type for TemplateVariables"

**The scorer was throwing these away**, because the key carried `aliases` for
`natural_date` and for nothing else — the precise under-reporting its own README
predicts. Added as `spelling_variants`, reported on a separate line, never
merged into `terms_required`: every historical score has to stay comparable, and
the senses above are labels. `"Data type for TemplateVariables"` is the
forbidden reading of the word. Counting it as found would raise recall on a row
that carries the error the probe exists to catch.

Read together, `d` is the best run anyone has done: **4 defined + 2 named, 16%
copied**.

**Measured by.** `terms_required present`, which cannot exceed 4 until this
changes and has not exceeded 4 in six runs.

**Note on what this does *not* explain.** `must_not_mean` has gone 5 → 3 → 2 →
0 → 2 → 1 across the same six runs, and D scored zero wrong with three traps
present. When a session is shown a word it now mostly gets it right. The
bottleneck moved from *the senses are wrong* to *the words never arrive*, and the
work that moved it was real. This is the next wall, not a repeal of the last one.

## 9 · The control that should have been run before B — STATUS: run; the attribution was wrong

**The claim under test.** *"One change moved the number, and it was the data."*
It is the load-bearing sentence of this document and nothing tested it.

**Three things changed between A and B, not one.** Read off the stored prompts:

                    A (v0/v1)                    B onward
    brief           8,453 chars of doctrine      2,851 chars of procedure
    term source     code.survey                  code.vocabulary
    working set     8 tools                      5 tools

The data change is the weakest of the three candidates — measured above, it
offers one required term the grain list did not and buries two it named
outright. And `must_not_mean` improved across the same boundary: a word list
decides *which* words a session sees and cannot make a definition better, so
something else was already doing that work. The B brief is where the renaming
test appears.

**The control.** `ROTA_PROMPTS=grain` — the `source/` variant with
`code.vocabulary` swapped for `code.survey`, brief 1,448 chars against 1,546,
same five-plus-`code.area` working set, same gates. One variable.

**Registered before the result, because reading it afterwards and crediting
whatever changed is the mistake this item exists to correct:**

  * **4–5 of 10.** The list was never the lever; the brief and the narrowed
    working set were. Item 8 is not a cause and its fix should not be built.
  * **0–1 of 10.** The word list does work the grain list cannot, B's
    attribution was right by luck, and item 8's declaration-ranking is worth
    building.
  * **4–5 of 10 but symbol-shaped** — `getIntentsFromFM`, path fragments —
    then the score moved and the artefacts are junk, which means
    `terms_required` is too weak to steer on and vocabulary's real contribution
    was precision rather than recall. **Check term shape, not just presence.**

**Result — `cnt_h`, and it is the third case with the number one lower.**

    run   design                         required   copied   off-key
    v1    grain list, 8,453-char brief    0 of 10     88%     6 of 8
    h     grain list, 3,057-char brief    3 of 10     37%    14 of 19
    g     word list + source              3 of 10     10%    17 of 30

**`h` and `g` tie on `terms_required` and are not remotely the same run.** One
of them defined `getRelativePath`, `App`, `assignees`, `fmValidateIntent` and
`TemplateVariableVariables_Text`. The metric the entire worklist steers by
cannot see the difference between them.

**So the change splits three ways, and it was recorded as one.**

  * *The brief and the narrowed working set carry the recall.* Same grain list,
    old brief 0 of 10, new brief 3 of 10. That is the whole of the movement the
    document credits to the data.
  * *The word list carries the precision.* Transcription 88% → 37% is the
    brief; 37% → 10% is the list. It is the only thing that stops a session
    copying symbol names, and prose demonstrably does not.
  * *The word list is worth roughly nothing on recall* — one term, `selection`,
    against two buried. Inside the noise.

**"One change moved the number, and it was the data" is wrong.** The brief moved
the number. The data moved the thing the number cannot see.

**And both lists are the same act.** `v1` transcribed symbols — 88%. `b`
transcribed nothing and instead defined what the shredder produced: `show`,
`private`, `chosen`, `filtered`, `natural`, `object`, `container` — 20 of its 27
terms are not in the key, against 6 of 8 for `v1`. Off-key sits near 75% in both
eras and the word list tripled the volume of it. **Whatever is on the list gets
defined. The list is the instruction, whichever list it is** — which is this
document's own founding insight, applied to the grain list in one paragraph and
never once applied to its replacement.

**Which is the real argument for declaration-ranking, and it is not the one made
in item 8.** Not that it recovers `provider` and `frontmatter` — that is a
recall claim and recall is not where the lever is. It is that a declaration is
the codebase asserting *this is a kind of thing*, so a list built from
declarations is a list of the project's own claims instead of a list of my
statistics. It is the first candidate list that is not purely a specification of
the answer.

**Three things the scorer now measures that it did not this morning:**
`of those offered` (the ceiling), `copied from the index` (transcription), and
`not in the key at all` (off-key volume). No run before `h` can be compared to
one after it on `terms_required` alone.

## 10 · What the runs actually differ from, and which data systems did it

**The glossary was the small gap.** Read off every file in the key rather than
`glossary_terms.yaml` alone:

    dimension                  key      best ever        
    glossary terms_required    10       4 defined + 2 named  (d)
    must_not_mean              0 hits   0                    (d, e)
    constraints required        2       0 — in all eleven runs
    items                      ~10      10 (new), 0 in the last nine
    roles executed              3       2 since v0; vision_keeper not since fix

**Two of the three onboarding roles have not run in ten runs.** `tick_survey`
gives Architect nothing until Terminologist holds a record for *every* area, and
Terminologist has never finished all six. `cnt_g` ends with six architect wakes
ready on the frontier and zero architect sessions. So `constraints`, `items`,
`constraint_bindings` and the decoys — half the answer key — have never been
evaluated on any context design. Every conclusion in items 8 and 9 is about the
one role that runs.

**The data systems, and what each measurably did.** From the stored prompts, not
from memory:

    run  terminologist's code tools              defined  +named  copied  off-key
    v1   survey                                    0/10    0/10     88%     75%
    b    vocabulary source                         4/10    4/10      0%     74%
    c    vocabulary source                         4/10    4/10      0%     64%
    d    area source                               4/10    6/10     16%     76%
    e    area source (+depth-1 imports)            4/10    5/10      0%     68%
    f    area source vocabulary                    3/10    4/10     15%     65%
    g    area source vocabulary (+disambiguation)  3/10    4/10     10%     57%
    h    area source survey                        3/10    4/10     37%     74%

  * `code.survey` — the grain list. 88% transcription. Also the **Architect's
    only code tool**, and the Architect is where both required constraints live.
  * `code.vocabulary` — kills transcription outright (0%), worth about one term
    of recall, and imposes the 4-of-10 ceiling of item 8.
  * `code.area` — the source itself. **`d` and `e` never called
    `code.vocabulary` at all**, and `d` is the best run anyone has: 6 of 10,
    zero `must_not_mean` hits. Item 8's ceiling is a property of the *word-list
    designs*, not of the system, and `d` is above it.
  * depth-1 imports (`e`) — 4.5KB of source in the prompt taught the model to
    *write tool results*. Killed, correctly.
  * the indexer keeping every tracked file — the four domain files, area `.`
    from 4 grains to 17. Also produced the first collision, whose livelock took
    61% of a run. It is the **only** data system here that changed what the
    Architect can see, and its measured effect was a stall.
  * disambiguation (`g`) — best off-key of any run at 57%, nothing destroyed,
    three real collisions. Costs about one term of recall against `d`.

**Off-key never moves.** 64–76% in every design that scores at all, `d` and `g`
included. Seven data systems, and not one of them changed the proportion of the
glossary that is not about this project. That is the invariant nobody has
attacked.

**Best set tried so far: `d`.** `code.area` + `code.source`, the short brief,
the five-tool working set, the read gate — and no word list. Best recall, only
run with zero wrong traps, 117 turns. **Best set not yet tried: `d` plus `g`'s
disambiguation**, which is a correctness property `d` lacks and costs nothing
that `d` measures. Neither has ever reached the Architect.

**Caveat that applies to the whole table.** One run per design, differences of
one term, a model that produces a second-person collapse in 13 turns of 105.
`d` over `g` is not a result, it is the best guess available — and the honest
next step is repeat runs of `d` before building anything on top of it.

## 11 · Two tools disagreeing about what an area is — STATUS: fixed, in the `cnt_j` run

**The richest area in the repository has now been lost twice, to two unrelated
citation rules, in two different designs.**

*`cnt_d`.* Sessions cited `["TemplateVariableType", "TemplateVariableVariables"]`
— the declarations they had just read. `attest` wants grains "spelled as they
were listed for you", and its own comment states the precondition: *"cheap for a
session that looked — `code.survey` has just handed it the list."* `d`'s working
set is `code.area` and `code.source`. Nothing listed them. Three sessions,
thirty-six turns, `src/variables` and `src/variables/providers` quarantined.
**Fixed:** a bare symbol resolves to its grain when the match is unambiguous and
inside the area. Ambiguity stays unresolved rather than guessed at, and the
record stores the grain it resolved to — writing `TokenStore` with `resolves=1`
would file a citation naming no row.

*`cnt_i`.* Same area, different rule. `code.area` hands over "the area's own
files, **and the ones it imports**", and argues the case: *"a file the area
imports is part of what the area means, wherever it sits."* `attest` required
every citation to sit under the area's path. The session woken for
`src/variables/providers` was shown `src/variables/index.ts`, read it, cited it,
and was refused twelve times across three sessions. **Fixed:** a cited import
counts when the edge is in the index. In `cnt_j` that area closes in two turns.

Both are the same shape and it is the shape this document keeps finding: a gate
whose justification names a tool that the design it now runs under does not
have. The gate was right when it was written and nobody re-read it.

## 12 · `sense=` has never once been used correctly — STATUS: fixed, untested in a run

Every non-empty value passed to `glossary.amend(sense=)` across twelve runs:

    area x24 · code.area() x5 · repository x3 · data storage x3 · survey x2 ·
    error x1 · and three whole sentences, one of which swallowed `, sense_body=`

Nine runs carry a row with a bogus tag — `templates#area`, `templates#survey`,
`github#repository`, `workflow#code_area_`, `filteredopenermissingnotice#error`.
**Not one names a second meaning.** The hatch whose docstring says "deliberate
duplication costs one argument" has a zero percent correct-use rate, and every
accidental payment costs a real row and a real collision.

It is not carelessness. Asked for a word naming *which* sense this is, a session
reaches for the most available noun, and the most available nouns are the mode
it was woken in and the tool it just called — the same reach that produced
`why="term_collision"` on `glossary.same`. Guarded on shape: not a call, not a
sentence, not a word from the frame. `nonce`'s `binding` still costs one
argument.

## 13 · D + disambiguation, run twice — STATUS: precision won, the run still cannot finish

    run                     def   +nm   mnm   copied  off-key  items  roles  sess
    D   area+source         4/10  6/10  0/3     16%     76%      0      2     14
    G   vocab+disambig      3/10  4/10  1/5     10%     56%      0      2     19
    I   D+disambiguation    4/10  4/10  0/2      0%     56%      8      4     49
    J   I + citation fix    3/10  3/10  0/2      0%     43%      0      3     34

**Precision improves monotonically and it is not a small effect.** `d` wrote 25
terms of which 6 are in the key — 24%. `j` wrote 16 of which 9 are — 57%. Copied
identifiers go 16% → 0%. Zero wrong traps in both.

**Recall falls one term and the glossary halves.** Fewer, cleaner. Whether that
is the right trade is a judgement, not a measurement, and one run each.

**`i` is the first run since `fix` to reach the Vision Keeper** — 10 architect and
6 vision_keeper sessions, and 8 items, the first items in nine runs. They are not
good items (`getRelativePath`, `src/variables/index.ts` as ids) but the phase
ran. `j` did not reach it.

**The blocker is now the session budget, not the context design.** Onboarding
cnt is 18 role-area pairs. Measured cost per terminologist area: `new` 1.0,
`fix` 1.6, `j` 1.6, `g` 2.0, `d` 2.8. At 1.6 the survey pass alone is ~29
sessions before a single collision. The default limit is 40. **This is why
`constraints` and `items` are zero in every run and always were** — not that
the roles cannot do it, but that the budget is spent before they are reached.
The A-era ran all three roles inside 21 sessions by doing each one badly.

**Ten of `j`'s 34 sessions were collisions, and about 60% of those were
self-inflicted.** Across `i` and `j`, of the distinct collisions raised:

    #root (area '.')     2 of 5   2 of 4
    sense= mis-fill      1 of 5   1 of 4
    real cross-area      2 of 5   1 of 4

Item 12's guard removes the `sense=` row outright and was not in either run.
The `#root` rows are area `.` — which `tick_survey`'s own comment calls "what
did not belong anywhere else by construction… the one area whose vocabulary is
least likely to be the project's" — minting a second sense for every common
word, each costing up to three sessions. **Left open deliberately**: refusing
`.`'s sense lets the earlier one win silently, and *nothing wins silently* is
what the disambiguation design rests on. Minting the row without raising a
collision is the option that neither destroys nor spends, and it is a decision
rather than a bug fix.

## 14 · The Vision Keeper, examined for the first time — STATUS: one guard added

`cnt_i` is the first run in nine to reach this role, so this is the first
evidence about it there has ever been. Six sessions, all six areas, and **8
items — the first items since `fix`**.

Two of the eight are sentences about code: `id='src/variables/index.ts'` ("This
file exports several functions and types") and `id='getRelativePath'` ("Returns
the relative path of a given path"). The other six — `release_workflow`,
`settings_behaviour`, `intent-processing` — are about the product.

`items.yaml` states the test and names the failure: *"it would still be true if
every identifier were renamed"*, and *"A sentence about a function is not an
item."* The vision_keeper brief says it too, in its own words: *"a behaviour
composed from names is a guess wearing an observation's provenance."* **Seventh
time prose was right and nothing held it.**

**Guarded on the id, not the text.** Renaming does not catch this one: rename
`getRelativePath` to anything and "returns the relative path" stays true, which
is exactly why it says nothing about *this* product. Naming the item after the
code is the tell, and the id is checked against `code_index` — the same check
the scorer's `copied from the index` makes after the fact, moved to write time.

**Not fixed, and deliberately not fixed with prose:** the brief has no renaming
test in it. Adding one would be the eighth sentence in the list above.

**Also unexamined and now visible:** `problem.assert` was called 9 times in one
session and the read gate refused a batch of them for citing files it had not
opened. The Architect's side is worse -- `cnt_j`'s only two constraints have
empty bodies, which `surveys.attest` already refuses for `found` and which
therefore arrived some other way. Neither is chased here; both are the first
things to look at once a run reliably reaches these roles.

## 15 · The Terminologist, made to work — STATUS: three fixed and verified, two fixed and running

    run                def    mnm  copied  off-key  terms  areas  quar  amends
    D  baseline       4/10   0/3     16%     76%      25    4/6     2     161
    K  guards         3/10   0/2      5%     47%      19    5/6     3     311
    L  +frame         3/10   0/2      0%     47%      17    5/6     5      96
    M  +plurals       3/10   0/2      7%     28%      14    5/6     3     113
    N  +sense ignored 4/10   0/2      0%     42%      26    5/6     4      89
    O  +cite list     3/10   0/2     30%     73%      26    6/6     1      58
    P  +paths         4/10   1/3      0%     36%      19    6/6     1      38

**`cnt_p` against the baseline: same recall, zero transcription against 16%,
off-key halved, every area surveyed instead of four, one abandonment instead of
two, and 38 amend calls instead of 161.** The survey pass is six areas in six
sessions with nothing quarantined -- the first time that has happened.

The one regression is a `must_not_mean` hit: area `.` defined `intent` as
"template with specific action". The bucket rule stops `.`'s rows raising
collisions and does nothing about `.` writing English, which is item 5's
problem and not this one's.

The remaining quarantine is the `intent` collision, and it is the merge-argument
limit recorded below -- the session chose the right two rows and could not say
why they were the same.

**Off-key was the invariant.** Item 10 recorded it at 64--76% across every
design tried and called it "the thing nobody has attacked". It is now **28%** --
four terms of fourteen: `getter`, `parser`, `intent_object`,
`variable_provider_variable_parsers`. `cnt_m`'s glossary contains **no plurals
at all**.

**Transcription is gone (16% → 0%), off-key is down a third (76% → 47%), one
more area closes, and the run costs a third of the calls it did.** Recall is the
one axis that has not moved, and every remaining lever on it is below.

**The retry storms were one bug.** `cnt_k` made 311 amend calls to `d`'s 161 --
and **292 of them came from three sessions on `.github`**, 74, 109 and 109
apiece. All three opened *"This area appears to be a survey of the `.github`
directory"* -- the mode's own name, because the prompt says `MODE: survey` --
then tried to define `survey` and `area`. The read gate refused them with
"nothing you read this session says 'survey'", which is true and reads as *read
more*, so they read more and tried again until the area was quarantined.
`.github` has almost no project vocabulary and `none_found` was right all along.
Frame words are now refused as *terms*, in words that say so and name the ending
that was available. **`.github` now closes in one session**, and the amend count
fell to 96.

**Plurals were a second row all along.** The id derivation promises that writing
a word twice amends it -- earned on oauthlib, twelve sessions and five
`endpoint`s -- and it was never true across a plural, because the slug is not
stemmed while `_words_in` is. The `src/intents` session, in the area that
declares what an Intent *is*, wrote `intents`, `templates` and `variables`
beside the existing `intent`, `template` and `variable`. **Three of the eight
off-key terms in `cnt_l` are exactly these.** A plural now amends the singular
when the singular exists, and does not otherwise.

**A guard that refused where it should have ignored, and it was mine.** The
first `sense=` shape check raised. `cnt_m`'s `.github` sessions answered
`sense='survey'`, were refused, and **re-sent the identical call twelve times
for `templates` and nine apiece for `ISSUE_TEMPLATE` and `bug_report.md`** --
94 amend calls, nothing written, area quarantined. The refusal ends "drop
`sense` and amend the entry you have" and the model does not drop it.

Dropping it is the right reading anyway: across twelve runs `sense` never once
named a real second meaning, so a malformed one carries nothing worth
preserving. It is now **ignored, with a note on the result that landed**, and
the call becomes the plain amend it should have been. Two ordering bugs came
with it and are worth recording because both were silent: the id was derived
before the tag was cleared, so clearing it changed nothing; and the
duplicate-sense guard ran first, so the tag was never reached. Provenance words
still fall through to the duplicate guard, which owns the message earned for
them.

**A collision refusal that named the wake instead of the ids.** Woken for
`template, template#src_variables_providers`, three `cnt_k` sessions called
`glossary.same(drop='templatevariable', keep='intent#src_variables_providers')`
-- wrong term, non-existent id -- identically each time. The refusal said "both
ids come from the wake that woke you", which a session that has lost them cannot
act on. It now lists the words with more than one live sense, and their ids.

**One loss is not a gate defect and no fix is proposed.** `src` was quarantined
in `cnt_l` after three sessions that cited `TAbstractFile` and
`TemplateVariable` ten times over, interleaved with *"As for your call to
`surveys.attest`, you are correct in citing the two grains..."* -- the
second-person collapse, the model answering itself as the system. I checked
before building the obvious fix: **`TemplateVariable` is declared in
`src/variables/index.ts` and no grain in area `src` imports it, and
`TAbstractFile` is not in the index at all.** Extending symbol resolution to
imports would have changed nothing, and shipping it would have hidden the real
cause behind a plausible one.

## 16 · I put a list of grains in an error message and the session defined it

The founding finding of this document -- *"the input was specifying the answer"*,
21 of 28 terms exactly a symbol name -- reproduced by me, in a refusal string,
after spending the day citing it.

Four runs lost `src/variables/providers`, each to a different citation spelling:
bare symbols (`d`), a file from a neighbouring area (`i`), symbols declared
elsewhere (`l`), enum members as `TemplateVariableType.text` (`n`). Three
resolution rules were added and a fourth form arrived anyway, so I stopped
resolving and made the refusal say what *would* work: the grains the session had
opened. `ctx.opened` is exactly the set that satisfies the check and the session
is the only one who cannot see it.

**It worked, and it poisoned the glossary.** `cnt_o` is the first run ever to
survey **6 of 6 areas with zero quarantines**. Session 5, turn by turn:

    t1-t3  [before the refusal]  TemplateVariable, Template
    t4     [after the refusal]   Template, TemplateVariableType,
                                 TemplateVariableVariables,
                                 variableProviderVariableParsers,
                                 variableProviderVariableGetters

Five identifiers in one turn, and they are the names the refusal listed.
Transcription went **0% -> 31%**, the worst since the grain-list era, and eleven
of sixteen terms at that point were identifiers.

**It also raised the score, which is the part worth keeping.** `cnt_o` names
`variable_type` and `provider` -- for the first time in any `d`-design run --
because it transcribed `TemplateVariableType` and
`variableProviderVariableParsers`. Recall went up *because* quality went down.
That is exactly why `named, not defined` is reported on its own line and never
merged into `terms_required`, decided this morning for a different reason.

**Fixed by listing paths.** A path answers the question actually asked -- what
may I cite -- and nobody defines `src/variables/providers/index.ts` as a word.
Running as `cnt_p`.

**The rule this is the fourth instance of:** any list of symbols put in front of
a session told to define an area's terms is a specification of the answer, and
it does not stop being one because it arrived inside a refusal.

---

## 17 · What the transcripts said, and one gate firing in a mode with no code

Read end to end from `cnt_p` rather than counted.

**Source arrived as escaped JSON.** `_render` fell through to `json.dumps`, so
`code.area` and `code.source` handed over files with every newline a literal
`
`, every em-dash `—`, every quote `\"`. **Every file every survey
session has read, in every run in this repository**, under a design whose whole
premise is handing over source as source. A dict carrying long text now renders
as text with the scalars on a header line.

**An area lost its budget to its neighbours.** `sorted({**own, **imported})` by
fan-in alone, so a file half the repository depends on outranked the files the
session was woken for. `src/variables/providers` was shown
`src/variables/index.ts` and `src/notice/index.ts` before its own `index.ts`,
and `not_shown` held all five provider implementations. Own files now rank
first: measured, that area goes from two foreign files plus its index to its
index plus `text.ts`, and `src/variables` gains `templateVariables.ts`.

**The brief promised a listing that does not exist.** *"Citations are grain
names, spelled as they were listed for you"* -- `d`'s working set has no
`code.survey`, so nothing ever listed them. That one sentence is the root of all
four citation failures chased in item 11: bare symbols, a neighbour's file,
foreign symbols, enum members. It now says to cite the path `[code.area]` prints
above each file.

**The escape hatch is never used.** `code.area` names what it withheld and the
brief says to `code.source` it. Across `cnt_p`'s six survey sessions there was
**one** genuine fetch of a withheld file, repeated five times. The five provider
files were named in `not_shown` and fetched by nobody.

**And it mostly does not matter, which is the finding.** Of the ten files the
key names, eight were shown to some session in `cnt_p`. `providers/index.ts`
alone carries `enum TemplateVariableType` with all five members *and* both
lookup tables mapping each type to a parser and a getter -- which is
`variable_type` and `provider` entire. The session read it and wrote `parsers`
and `getters`, accurately, from those two tables. It had the material and named
the concept by its halves. Only `filter_set` and `selection` need a file nobody
ever opened.

**The read gate fired in modes with no code in them.** Built for survey --
"against the words actually read" -- and applied everywhere. `deliver` wakes the
Terminologist on a ratified statement, "let users delete their account", and the
job is to say what `delete` means here; there is nothing to `code.source`.
`L1-TE-amend-glossary` failed 0 of 5, every run refused with *"nothing you read
this session says 'delete'"* after producing a correct call. **The case had been
stale since before today and nothing reported it.** Scoped to sessions that have
an `area`, which the context already carries and only a survey sets.

**Re-recording found it.** 25 L1 cases were stale because the cassette key
includes the user turn and the user turn carries tool results. Eighteen were
stale only, and passed on replay. Seven were real, four of them Terminologist.

## 18 · The design has a name now, and promoting it is not a one-liner

`d` was a letter in an A/B sequence. The design's distinguishing mechanic is one
instruction no other variant carries -- *"Begin your reply with a short account,
in your own words, of what this area does and what it calls the things it works
with, then record the words your account needed"* -- so it is **`account`**, and
`ROTA_PROMPTS=account` is what runs it.

**It cannot simply become the default.** `compose` is `base(role) + piece(role,
verb)` and there is no per-mode base, so a variant's `base.md` replaces the base
for *every* mode of that role. `account/base.md` is **five lines against the
default's forty-five**, and the default base carries doctrine the other six
terminologist modes -- `answer`, `ask`, `criteria`, `deliver`, `question`,
`term_collision` -- have only ever run with.

And item 9 measured that **the brief is what carries the recall**. Promoting
`survey.md` and `survey.tools` alone would hand the survey mode the 45-line base
back and would not reproduce any number in item 15.

So the options are: cut the shared base and re-measure the other six modes, give
`compose` a per-mode base, or leave `account` as the variant it is. Not a
decision to take from one repository's numbers.

**Nothing deleted.** `vocab/` is B and C, `source/` is F and G, `grain/` is the
control that falsified this document's central claim. Keeping a variant costs a
directory; deleting a measured control costs the ability to re-run the ablation
that produced item 9.

## 19 · The third relation, and the first context shaped like a word

**The glossary had two relations between rows and needed three.** Two senses
that differ are a *collision*, kept apart by the area rule. One sense written
twice is a *duplicate*, collapsed by `glossary.same`. Neither describes what a
survey pass actually produces:

    intent               [src]            note with properties and templates
    intent#src_intents   [src/intents]    custom actions in Obsidian
    intent#src_variables [src/variables]  function or action in a plugin
    intent#root          [.]              template with specific action

No two say the same thing, so they are not duplicates. There is one intent in
this codebase, so they are not a collision. They are four sessions each seeing
the word in one place and writing what it looked like from there -- **citations,
not definitions** -- and the key's sense is in none of them and composable from
all of them. The missing operation is **synthesis**.

**`code.concordance(term)` -- the first context in this system shaped like a
word.** Every context the role has been given is shaped like a *place*: an
area's grains, an area's words, an area's source. A meaning is not shaped like a
place, which is item 5 stated as a data problem instead of a scheduling one. The
same index and edges, pivoted on the word: declarations first, then the files
that use it with their most telling lines, then the imports between those files.

Measured for `intent` on cnt: 13 files, 5 areas, 27 edges, 3.7KB rendered --
comparable to `code.area`'s budget. Among the declarations:

    src/intents/frontmatter.ts:21
        const newIntents: Intent[] = (fm?.intents_to || []).map(...)

which is half the key's sense of the word, verbatim -- *"declared in another
note's frontmatter under `intents_to`"* -- on a line **no survey session was
ever shown**, because `frontmatter.ts` is one area and the word belongs to five.

**`glossary.synthesise(ids, sense_short, sense_body)`.** Writes the sense the
readings add up to; supersedes the partials whole, so they stay readable and it
stays reversible. **No argument is required for it**, deliberately:
`glossary.same` asks the session to say why two senses are the same and five
runs proved this model cannot -- `different provenance`, `same sense`, `same
term`, `term_collision`. What is checked is the shape of the result: more than
one row, one word, and a sense that is not one of the partials restated. That
last has its own test, because restating the best-reading row and superseding
the rest is the likeliest way to fake it.

**First run, `cnt_q`: it synthesised `tick`.** Woken for `['template',
'template#src_intents', ...]`, it read the first line of its prompt -- *"You
were woken by: tick:term_collision"* -- and called

    glossary.synthesise(ids=['tick'], sense_short='a signal or event',
                        sense_body='a tick is a unit of time, often used in finance')

forty-two times, then tried `ids=['tick', 'tock']`. The word it was woken about
appeared only on the `Refs:` line, and **the readings themselves were not in the
prompt at all** -- reachable only by a call the model had to think of. The brief
said "each row below" and there were no rows below.

**Three fixes, each a pattern already earned elsewhere in this system.**

  * `Ctx.wake_refs`. The subject travels the way `ctx.area` does for a survey:
    the scheduler decides what a session is about and the role never guesses.
    `term_collision` had no equivalent and had been running without one.
  * `glossary.lookup()` with no term returns the wake's rows, which is what
    makes it **pushable**. `push_working_set`'s own docstring is the argument:
    "if the session already holds everything a read needs, making the model ask
    for it is a turn spent on nothing." It was written about Critic, which woke
    with an empty prompt and asked to be handed its own working set.
  * `code.concordance()` defaults to the wake's word, so it pushes too.

A synthesis session now opens with the four readings *and* the concordance,
neither asked for. And `synthesise` refuses ids outside the wake by **naming
what the wake held** -- "is not a glossary id" was true and did not say which
ids were, the same defect fixed in `glossary.same` two items ago.

**The trigger needed two fixes to carry the whole family.** `GROUP BY term`
groups on the spelling a session typed, so `cnt_p`'s `intent` wake carried two
of four rows; and the `.` rule was dropping `intent#root` from the refs as well
as from the count. Now grouped on the stemmed term, with `.` material but not a
trigger.

**And the obvious grouping was wrong.** Grouping on the id family looked
equivalent -- the plural rule already files `intents` under the `intent` id --
and it holds only because `glossary.amend` derives ids from terms. Every fixture
in the suite writes ids directly, so two senses of `issue_template` under `g1`
and `g2` stopped colliding at all. Four tests caught it; nothing in a run would
have.

## 20 · Synthesis works, and its first output was a concatenation

**`cnt_r` is the first run in which the step ran at all.** 6 of 6 areas, nothing
quarantined, three compositions landed, provenance `observed`, partials
superseded and readable, `must_not_mean` 0, and 4 + 1 named = **5 of 10**.

And all three results are the readings welded together:

    templates <- 3   "customizable note or document structure"
    intent    <- 2   "template or instruction for organizing and processing notes"
    variable  <- 1   "template placeholder or variable used in templates"

`templates` is arguably worse than one of its own partials -- "Pre-defined
template for generating new notes" -- and `variable` is circular. **None of the
three carries a single word from the concordance that was pushed into the prompt
beside them.** The readings are a short table at the top; the evidence is 3.7KB
below it; the most available thing won, again.

**Summing partial views of a word gives a vaguer word, not a truer one.** That
is the failure this step is uniquely prone to and the previous guard could not
see it: a concatenation is identical to no single partial, so it passed.

**The guard that fits, and it is checkable where the merge argument was not.** A
synthesised sense must carry a content word that the concordance holds and the
readings do not. Validated against the measured data before it shipped: for
`intent` the concordance holds 53 content words and the readings 26, so 47 are
available; the produced sense brings in **none** of them, and the key's --
"a recipe for making a note, declared in another note's frontmatter under
`intents_to`" -- brings in `declared`, `frontmatter`, `intent`.

**The refusal names none of the candidates**, on item 16's evidence: a list of
words a sense could contain, placed in a refusal, is the same act as the list of
grains that got defined verbatim.

**Two bugs in the guard, both mine, both found by writing its test properly.**
It was wrapped in `except Exception`, which swallowed an `AttributeError` from a
context with no `batch_id` -- so **the guard was silently off and its own test
passed by not raising**, which is the shape this whole document is about. Now
gated on the index existing, with real errors left to surface. And `keep` was
read one line before it was assigned.

## 21 · What actually changes a definition, measured four ways

Probes, not runs: one word, temperature 0, `llama3.1:8b`, same forced shape --
*"In this project, an intent is ..."*, twenty words, "not the program itself and
not the user's goal".

    concordance only   "a user's goal or action ... in src/intents/frontmatter.ts"   trap
    + trace            "a user's goal or action ... a type in src/intents/index.ts"  trap
    + cartography      "a template or prompt for creating a new note ... written
                        down in the ... field of the global note's frontmatter.
                        Running one produces a new note"
    + both             as cartography

    key                "a recipe for making a note, declared in another note's
                        frontmatter under `intents_to`"

**The whole-program account is the active ingredient. The call trace is inert
and mildly dilutes it.** Both trace variants keep "a user's goal or action",
which is the reading `must_not_mean` exists to catch.

The reason is visible in the outputs: a trace is a list of `file :: function`,
so it says the thing lives in TypeScript. An intent lives in a *note*. Prose
about what the program does for its user is where that fact is, and it is the
one context that displaces the everyday reading of the word.

**The trace is still buildable and was worth testing.** Handed the computed
reach -- entry point plus two hops of `code_edges`, 11 files, 17.8KB, once per
repository rather than run E's 4.5KB on every area -- the model crosses files
correctly and names the real frontmatter-parsing chain. Asked to *fetch* files
itself it never does: given only `main.ts` it guessed `getIntentsFromTFile` into
`src/intents.ts` (it is `frontmatter.ts`) rather than asking. Same rule as
everywhere -- compute the reach, do not ask the model to reach.

**So the proposed pipeline loses its most expensive step.** Not
`orient -> behaviour -> trace -> name -> define`, but
`orient+behaviour -> name -> define`, with the trace available for the per-area
detail pass if it earns a place there.

**One residual error, and it is checkable.** Every cartography variant writes
`intents_imported_from` where the key says `intents_to` -- the import field
mistaken for the declaration field. `const newIntents: Intent[] = (fm?.intents_to
|| [])` is in the concordance it was handed. Checking a claim against evidence is
the shape this model is reliably good at, which is the argument for a checker
tier that every guard written today is already an instance of.

## 22 · The components, tested

Probes with hand-assembled context, `llama3.1:8b`, temperature 0. Not a system:
no turns, no tool calls, no attest.

**Generation works, on all ten.** Cartography + concordance + a forced shape --
*"In this project, a X is ..."*, twenty words, "not the program itself and not
the user's goal" -- defines every required term, **including the six no run has
ever found**, with **zero `must_not_mean` hits** against a baseline of five of
five wrong.

    good      intent (gets `intents_to` right) - frontmatter - global_intent
              - variable_type (names the enum)
    partial   template - variable - selection - filter_set
    wrong     prompt ("a template or set of instructions") - provider
              ("supplies data to other parts of the code")

The two wrong ones are the English readings, which is the failure the whole probe
exists to catch -- but four right and four close, against four generic senses and
six absences today.

**The checker does not work as a gate.** Asked to judge an entry against the
concordance, `holds | wrong | too general`:

    provider     (wrong)  -> too general                                 correct
    prompt       (wrong)  -> wrong, citing `with_prompts`                correct
    frontmatter  (good)   -> wrong                                       false positive
    intent       (good)   -> too general, BECAUSE = the entry restated   false positive

Two of four. It finds both real errors -- and rejects both correct entries, with
no reasoning on one of them. **The asymmetry is backwards for a gate**: it would
delete good work. As a *flagger* ordering candidates for a person it has value;
deciding is not a thing it can do.

**Which is survivable, and the graph already says why.** The glossary node:
"Entries carry provenance: ratified by the principal, or *observed -- extracted
from an onboarded codebase and awaiting confirmation*." An unverified but much
better glossary is what `observed` is for. What changes is what the principal is
handed: ten entries with two bad ones, instead of four generic ones and six
absences.

**What is still untested is the thing that has cost every design today**: whether
a cold twelve-turn session assembles this material for itself. The material
produces the answers. Every failure in items 11 to 21 was a session failing to
reach material that was already there.

## 23 · Eight phase structures, prototyped and read

`probes/phases/`. Each pipeline is a sequence of model calls over contexts the
harness assembles -- no sessions, no wakes -- ending in the same deliverable so
they can be read side by side. Scored by hand against the key's `sense_short`.

    A  per-area (today)   good 3  partial 5  poor 2
    B  account-first      good 2  partial 6  poor 2
    C  bottom-up          good 1  partial 8  poor 1
    D  question-first     good 4  partial 6  poor 0
    E  spiral             good 3  partial 7  poor 0
    F  declaring-file     -- file picking too naive to score fairly
    H  challenge          won `variable_type`
    I  user-surface       won `prompt`
    J  D + I + H combined good 2  partial 7  poor 1

**No structure dominates, and the wins are attributable to mechanisms.**

    intent, variable, provider, global_intent   D   maintainer's questions
    template, prompt                            J/I authoring surface
    variable_type                               H   falsification
    frontmatter                                 B   whole-repo account
    selection                                   A   area source
    filter_set                                  none

  * **questions** force *where does this live*. D is the only structure with no
    `poor` answer, and it produced the closest match in eighty outputs:
    `global_intent` = "an intent stored in a specific note designated by the
    plugin's settings" against the key's "an intent loaded from the note at
    `globalIntentsNotePath`".
  * **the authoring surface** -- `intentsSchema.yaml`, what a user types into
    their own note -- supplies the key's *own* vocabulary. It is the only source
    that produced `with_prompts` and `with_templates`, and every sense in the
    answer key is written from that side.
  * **falsification** forces specificity. Twenty attempts named
    `TemplateVariableType`; only the challenge pass named its members.
  * **the spiral** removes wrongness and adds no insight -- E has no `poor` and
    no unique win.

**Combining by concatenation makes it worse.** `J` put all three contexts in one
call and scored below `D`: vaguer answers, and the instruction leaked into the
output ("It is a thing in the code, not the program itself..." appeared *in* a
definition). The mechanisms are additive as **phases producing artefacts**, not
as context stuffed into one prompt -- which is the model rota already has, at a
grain it has never used.

**One common-mode defect, worth more than the ranking.** `code.concordance`
listed declarations in file order, so `intent` showed seven lines from
`frontmatter.ts` and buried `export type Intent` in `index.ts`. All five
first-generation pipelines wrote "declared in `src/intents/frontmatter.ts`".
Ranked by whether the declaration declares *the word*, and every pipeline's
locations corrected at once.

**And a tension it exposed.** After that fix the definitions became code-true and
less product-true: `export type Intent` is where the *type* is declared,
`intents_to` in a note's frontmatter is where an *intent* is declared. Both are
answers to "where is it written down". The key wants the second.

## 24 · The front is shared; the question is not

Item 23 tested one phase -- how the *glossary* gets built. The system owes two
more artefacts, and neither was in any of the eight pipelines.

**The shared front does not transfer.** Handed the same authoring surface and
maintainer's answers and asked for commitments, it produced:

    "Provide a way for users to generate notes based on templates or intents"
    "Load global intents from a specific note and allow users to reload them"

Behaviour statements -- **items wearing a constraint's name**. Zero of the two
required, though it named none of the four decoys either.

**Changing the question found one of them.** Asked the counterfactual instead --
*"what could a maintainer rename here without anything here failing, and who
outside would break, with an error or in silence?"* -- with the schema and
`providers/note.ts`:

    RENAME WHAT: `matches_regex`
    WHO BREAKS: users who have notes with a `matches_regex` variable type in
                their own notes ... will not be recognized

That is `the_frontmatter_schema_is_a_public_contract`, found at one instance
rather than stated generally. A constraint is a **counterfactual**, and
description never reaches one however good the description is.

**And it missed the other with the evidence in hand.** `providers/note.ts` line
35, inside the 56 lines it was given:

    const filteredOpener = (app as any).plugins.plugins["filtered-opener"];
    if (!filteredOpener) { new FilteredOpenerMissingNotice(); }
    await filteredOpener.api_getNote({ name: variable.filter_set_name, ...

An explicit dependency on another program's API, unnamed. One of two, with the
right question and the right file.

**So the unit is the question, not the artefact.** Rota gives all three survey
roles the *same* question -- "survey this area" -- and three different tables to
write into. The measurement says the artefacts differ because the questions do:

    glossary     what is this, where is it written, what is it for      works
    constraints  what breaks silently if this is renamed                half
    items        untested

## Not on this list either: the merge argument

`glossary.same` requires `why` to say what the two senses have in common, in
their own words. Measured across `cnt_i`, `cnt_j`, `cnt_k`, `cnt_m` and `cnt_p`,
the reasons offered are:

    'different provenance'   argues difference -- refused
    'different sense'        argues difference -- refused
    'same sense'             names neither sense -- refused
    'same term'              names neither sense -- refused
    'term_collision'         the mode's own name -- refused
    'both describe Obsidian' names the *term*, not what the senses say

**`cnt_p` picked the right rows every time** -- `intent#root` against
`intent#src_variables`, `obsidian#src_variables_providers` against `obsidian`.
The id confusion that quarantined `cnt_k` is gone. What is left is that it
cannot say why, and the last one above is a merge that should probably happen:
"note-taking app with customization options" and "Note-taking software" do say
the same thing.

**Not relaxed, deliberately.** Allowing the term to count as shared content
makes the check vacuous -- the two rows are the same word by construction, so
"both are about X" is always available and always says nothing. And the
asymmetry it protects was earned: wrongly calling two senses *different* costs
the principal a glance, wrongly calling them the *same* destroys an ambiguity
nobody can recover. Weakening a safeguard to get a discharge is trading the
thing for the number.

So: `llama3.1:8b` can identify the right two rows and cannot argue their
sameness. Tracked here with the second-person collapse, for the same reason --
so it is not credited to, or blamed on, anything above. The options are the same
two: a stronger model for this one mode, or a shape that does not ask for an
argument.

## Not on this list, and not under-information

The second-person collapse. `s8` turns 8, 9 and 10 are byte-identical and turn 8
opens with the system's own wake line. It begins at **turn 2, 2,535 characters**
— 13 of 105 turns across 6 of 21 sessions. `llama3.1:8b` does not reliably hold
"I am the one being asked" past one exchange. No amount of information fixes it;
the options are a stronger model for the understanding roles or a prompt shape
that does not invite continuation. Tracked separately so it is not credited to,
or blamed on, anything above.
