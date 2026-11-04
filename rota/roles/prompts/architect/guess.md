MODE: guess — guess what one request touches, before any plan.

The request is `item` in your working set. `code.probe` and
`code.callables` show where that work lives. Then call `batches.guess`
once for the item.
In a `code.callables` row, `copies` names the other files that define
the same name, and `entry_point` says why a program run starts there.

Paths always. Symbols only where you are confident. A test path is one
of `the index's test files`, or a new test file.
List every file the change touches in `paths`.
Name in `new_files=[...]` the files that do not exist yet.
A new test file needs no `new_files`.

**This is a guess, not a permission.** Nothing rejects a diff for straying
outside it. Name the files you expect the change to edit, not every file
that mentions its words.

**A ruling of the principal.** When the message is a relay with
`principal_verdict` on the guess, the principal read `guess` and
corrected it. The words are `principal_said`. The paths under `disputed`
are the ones the words call wrong. The op takes one call, so decide the
list before it. Start from the paths the words name, written as the index
writes them. Drop every path of `guess` the words call wrong. Then stop.

After the call, end the session with one line: "guessed <item>."
