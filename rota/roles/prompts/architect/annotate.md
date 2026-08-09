MODE: annotate — predict what one batch will touch.

`tickets.scan` and `criteria.scan` for the batch, `code.probe` to see where that
work lives, then `batches.annotate`.

Paths always. Symbols only where you are confident — they are a separate argument
precisely so you are not asked to rate your own confidence item by item, which
invites rating everything high.

**This is a prediction, not a permission.** Nothing rejects a diff for straying
outside it. Its whole job is to make "was this change incidental?" answerable at
review time instead of arguable, so err towards the paths you actually expect
rather than the ones you would accept.

One batch. You are annotating from source, which is what makes the annotation
worth having and also what makes doing every batch in one session useless.
