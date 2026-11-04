MODE: commitments — the witness lines of one area, each stated or declined.

`[model.witnesses]` holds lines where this project promises something to
the outside. Each line prints its id, its path, its line number and the
quoted line. `[code.area]` is this area's source.

For each line, ask who outside this repository notices when the line
changes, and what must hold. Then state it with one call:

    model.amend(witness="<its id>", party="<who outside notices>", behaviour="<what must hold, with each name the line holds>")

Send only these three arguments. The headline, the text and the bindings
come from the line. A line that promises nothing to the outside gets no
call. Who outside is never only "a maintainer" or "the build". Where two
lines contradict, state the one the code does. A constraint that lost its
witness line prints the form that restates it.

When each line is stated or declined:

    surveys.attest(outcome="found", citations=[the paths [code.area] printed that you read])

When you stated none, attest `outcome="none_found"` with the same citations.
