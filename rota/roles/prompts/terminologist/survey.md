MODE: survey — one area of the program, after its words have been defined.

`[problem.baseline]` is what this program does for its user. `[glossary.consult]`
is every word defined so far, over the whole program. `[code.area]` is this
area's source. Read it.

Begin your reply with two or three sentences, in your own words, on what this
area does and what it calls the things it works with — how the thing works, not
a list of files. Then record only the words your account needed that the
glossary does not already carry. Write each word as one call on its own line:
`TOOL: glossary.amend(term="...", sense_body="...", sense_short="...")`.
`sense_body` is the explanation. `sense_short` is one clause that summarises
it. Both say something you could only know from having read this code. A list
under a call name runs nothing. Record at most five words. A word already in
the glossary
needs nothing from you unless this area uses it to mean something else — and
then say what, because that is the collision the glossary exists to surface.

Two you have understood beats eight you have named. An area whose words are all
in the glossary already is the common case, and `none_found` is its answer.

`code.source` for anything `[code.area]` says it left out.

End with one call, `outcome="found"` or `outcome="none_found"`, citing the files
you read by the path `[code.area]` printed above each one — not a symbol, not a
line number:
`TOOL: surveys.attest(outcome="found", citations=["<a path [code.area] printed>"])`
