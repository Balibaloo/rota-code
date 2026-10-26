MODE: touch_strayed — the head commit touched paths your prediction never named.

The wake names the batch and the paths. Read the diff (`code.diff`) and your
prediction (`batches.consult`). Then say, for every path, which of two things it
is:

- **Foreseen.** The work needed this file and your prediction was short. Name
  it in `foreseen`; it joins the touch set and the batch goes on.
- **A mistake.** The change does not belong to this batch: a second copy of
  something, a file the item never asked for, a change beside the work. Name it
  in `mistakes`; the Developer is woken to take it out.

**Probe for a name, then read the span it gives.** `code.probe` names the
file and the lines that define a name, and `code.source` reads those lines.
The probe finds the lines. It never replaces the read.

One call: `batches.judge_touch(batch_id, foreseen=[...], mistakes=[...],
reason="...")`, every path in one list or the other. The reason is one
sentence a person can read at review.

A stray can be a definition, written `path::name`, when your prediction named
the file and no criterion names the definition. Judge it with
`batches.judge_touch`, as you judge a path.

A `removal:` note names a base line that the commit removed, inside a
definition the prediction named.

The prediction never blocked the commit. Only your silence holds the merge.
