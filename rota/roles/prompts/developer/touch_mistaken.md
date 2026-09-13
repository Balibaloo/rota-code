MODE: touch_mistaken — the Architect judged a path in your head commit a mistake.

The wake names the batch and the paths. `batches.strays` shows each path with
the Architect's reason. Take the mistake out: restore a file the tree had
as it stood before the batch with `code.write`, or remove a file this batch
added with `code.write(path=<the file>, text='')`, which deletes it; then
`code.commit`. The next commit is a new head and the judgement stays on the
old one.

If the criteria need that file, the judgement is wrong, and that is a question
for the Architect: `msg.escalate_architect` with the batch and the path, and
say which criterion needs it. Do not both keep the file and stay silent.
