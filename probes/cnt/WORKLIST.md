# Under-informed: the worklist

**Under-informed is the problem. Bad output is the symptom.**

Five points where information is lost, upstream first. Each is downstream of the
ones above it, so they are taken in order and not in parallel.

The loop for each: say what should happen · find why it doesn't · fix it ·
re-run onboarding on cnt · score against `answer_key.yaml`. **If the score does
not move, stop and say why.** A fix that does not change the number is a
hypothesis that was wrong, and carrying on past it is how three dead hypotheses
got stacked on `L1-DV-fix-the-code-not-the-test`.

## Baseline — the run this all starts from

`.rota/cnt_new.db`, commit `766c9e30`, 21 sessions, 105 turns.

```
terms_required present      0 of 10
must_not_mean hits          5
constraints required        0 of 2
decoy constraints recorded  2
empty constraint bodies     2
```

## 0 · `sense_short` reads as a label, and one chain follows from it — STATUS: next

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

**Deferred, and why.** Ordering areas by size rather than alphabetically was
going to be item 0. It fixes no defect — it reallocates budget, nothing more,
and the claim that it "seeds the glossary with product vocabulary first" is
wrong, because every session is shown the whole glossary regardless. `.github`
did take 64 survey turns plus the 45 above, out of ~190, on 3 grains of 89. But
if this chain is fixed those 45 do not happen, and the budget may suffice
without reordering. Revisit only if budget is still binding after a clean run.

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
