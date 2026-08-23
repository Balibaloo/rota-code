MODE: survey — one area of an existing codebase, read for what it is committed to.

`[problem.baseline]` is what this program does for its user. `[code.area]` is
this area's source, and the files it imports. `[model.consult]` is what earlier
areas were found to be committed to. Read the source.

Begin your reply with two or three sentences on what this area is for and
how it works -- what comes in, what it turns into, what leaves -- and record
them: `model.describe(account=<those sentences>)`. That account is a model
row; the constraints below are the rest of it.

Then one question, and it is a counterfactual: **what here could a maintainer
rename, remove or change without anything in this repository failing — and who
outside would break, with an error or in silence?** That is what a commitment
looks like from inside: a key a user writes in files this repository never
sees, an identifier another program reaches for, a name or version a registry
knows this project by, a format something else parses.

Answer it in three lines before you write anything, for each candidate:

    RENAME WHAT:   the thing, in the source's own words, at the place it is kept
    WHO BREAKS:    who outside this repository, by name
    WHAT HAPPENS:  the error they see, or the silence they do not

A candidate whose WHO BREAKS is "a maintainer", "the tests" or "the build" is
inside, and is not a constraint. So is anyone who would have to import or name
an identifier from this repository to be affected — a type, a class, an
exported function — whatever you call them: a user of a plugin writes notes,
not its source, and a renamed type breaks nobody who never read it. What a
user writes is a key, a value, a file name, a format; what a registry knows is
an id and a version. A build script, a settings panel, a layout you would not
have chosen — nobody outside notices if those change. Most areas hold none,
and when the question has no answer you are finished, and this is the whole of
what is left to do:

    surveys.attest(outcome="none_found", citations=[the paths you read])

When it has one, `model.amend` per commitment — `headline` the RENAME WHAT,
`text` the WHO BREAKS and WHAT HAPPENS, `bindings` the paths that keep it, which
you must have opened — then `surveys.attest(outcome="found", citations=[the
paths you read])`.

`code.source` for anything `[code.area]` says it left out. Cite by the path
`[code.area]` printed above each file.
