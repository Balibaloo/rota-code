MODE: touch_mistaken — the Architect judged a path in your head commit a mistake.

The wake names the batch and the paths. `batches.strays` shows each path with
the Architect's reason. Take the mistake out: restore the file as it stood
before the batch, or remove the file you added, with `code.write`, then
`code.commit`. The next commit is a new head and the judgement stays on the
old one.

If the criteria need that file, the judgement is wrong, and that is a question
for the Architect: `msg.escalate_architect` with the batch and the path, and
say which criterion needs it. Do not both keep the file and stay silent.
