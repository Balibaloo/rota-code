MODE: orient — the whole program, before anything in it has been named.

`[code.front]` is what a person opening this repository reads first: what it
says it is, what a user writes to drive it, and where it starts. Read it.

**Begin your reply with an account of how the program works for the person
using it**, four or five sentences, in your own words: what the user writes
and where, what the program reads first, what that turns into, and what comes
out at the end. Name things by the names the user-facing files use — the keys
a user types are part of the product, not identifiers. How the thing works,
not a list of what it contains.

Then record the account itself as the first item -- `problem.assert(id=
"how_it_works", text=<the account, whole>, kind="in_scope")` -- so that what
you understood travels, not only its headlines. Then the behaviours that account
needed, one `problem.assert` each, `kind="in_scope"`: a sentence saying what
happens, for whom, from what, keeping the names the user-facing files use. Give
each an id of your own that names the behaviour, not a file or a function. Four
to eight. Each must still be true if every identifier in the code were renamed;
the words a user writes stay.

You are writing "the program does this", never "we meant it to". Everything
here is observed, and the first time anyone disagrees with one it becomes a
ruling the principal makes — which is the point.

`code.source` any file `[code.front]` names and did not show, if the front
leaves the program unexplained.

Then `surveys.attest(outcome="found", citations=[the paths you read])`, and
stop. If the front shows a tree with no product in it — a library of helpers,
scripts around something else — `surveys.attest(outcome="none_found",
citations=[the paths you read])` is the answer and costs nothing.
