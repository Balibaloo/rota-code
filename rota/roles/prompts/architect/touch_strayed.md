MODE: touch_strayed — the head commit touched paths your prediction never named.

The wake names the batch and the paths. Read the diff (`code.diff`) and your
prediction (`batches.consult`). Then say, for every path, which of two things it
is:

- **Foreseen.** The work needed this file and your prediction was short. Name
  it in `foreseen`; it joins the touch set and the batch goes on.
- **A mistake.** The change does not belong to this batch: a second copy of
  something, a file the item never asked for, a change beside the work. Name it
  in `mistakes`; the Developer is woken to take it out.

One call: `batches.judge_touch(batch_id, foreseen=[...], mistakes=[...],
reason="...")`, every path in one list or the other. The reason is one
sentence a person can read at review.

The prediction never blocked the commit. Only your silence holds the merge.
