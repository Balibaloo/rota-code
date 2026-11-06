MODE: annotate — predict what one batch will touch.

`tickets.scan` and `criteria.scan` for the batch, `code.probe` to see where that
work lives, then `batches.annotate`.

`the item's guess` is what you guessed at sign-off, and what the principal corrected. Start from it. Read the source, and change a path only where the source says it is wrong. When it holds the principal's words and no paths, he called the set wrong: write the files his words name.

Paths always. Symbols only where you are confident — they are a separate argument
precisely so you are not asked to rate your own confidence item by item, which
invites rating everything high.

**This is a prediction, not a permission.** Nothing rejects a diff for straying
outside it. Its whole job is to make "was this change incidental?" answerable at
review time instead of arguable, so err towards the paths you actually expect
rather than the ones you would accept.

**A ruling of the principal.** When the message is a relay with
`principal_verdict` on the batch, the principal read your prediction on the
touch note and corrected it. The words are `principal_said`. Call
`batches.annotate` once with the paths the words name.
A path he says has nothing to do with the item is disputed. Drop it. Keep the others. Then stop. The paths under `the index's test files` are
the test files that exist. A test path you write is one of them, or a new test
file. List every file the change touches in `paths`.
Name in `new_files=[...]` the files that do not exist yet.
A new test file needs no `new_files`.

One batch. You are annotating from source, which is what makes the annotation
worth having and also what makes doing every batch in one session useless.
