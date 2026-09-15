MODE: survey — one area of an existing codebase, read for what it is committed to.

`[problem.baseline]` is what this program does for its user. `[code.area]` is
this area's source, and the files it imports. `[model.consult]` is what earlier
areas were found to be committed to. Read the source.

Begin your reply with two or three sentences on what this area is for and
how it works -- what comes in, what it turns into, what leaves -- and record
them: `model.describe(account=<those sentences>)`. That account is a model
row; the constraints below are the rest of it.

Then one question, and it is a counterfactual: **what here could a maintainer
rename, remove or change without this area failing — and who outside the
area would break, with an error or in silence?** Outside the area is another
area of this repository that calls or imports it, a test that patches a name
in it, a program that imports this package, a user who writes a key, a file
or a format this area parses, a registry that knows this project by a name
and a version. A commitment is a name at a place: a function and its
parameters and their defaults, an exception a caller catches, a module-level
name a caller patches, a helper two areas share, a name a package exports.

Answer it in three lines before you write anything, for each candidate:

    RENAME WHAT:   the thing, in the source's own words, at the place it is kept
    WHO BREAKS:    who outside this repository, by name
    WHAT HAPPENS:  the error they see, or the silence they do not

A candidate whose WHO BREAKS is only "a maintainer" or "the build" is
inside, and is not a constraint. A build script, a settings panel, a layout
you would not have chosen — nobody outside notices if those change. Name
the surface as `path::symbol` in the headline, and cite the line that keeps
it in `source_refs`. An area with no caller, no test and no importer holds
none, and when the question has no answer you are finished, and this is
the whole of what is left to do:

    surveys.attest(outcome="none_found", citations=[the paths you read])

When it has one, `model.amend` per commitment — `headline` the RENAME WHAT,
`text` the WHO BREAKS and WHAT HAPPENS, `bindings` the paths that keep it, which
you must have opened — then `surveys.attest(outcome="found", citations=[the
paths you read])`.

`code.source` for anything `[code.area]` says it left out. Cite by the path
`[code.area]` printed above each file.
