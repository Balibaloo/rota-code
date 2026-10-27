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

A `removal:` note quotes each base line that the commit removed. A quoted
`def` or `class` line stands for the whole definition.

**Judge a removal by the request.** For a row with a `removal:` note, do
not ask whether your prediction was short. Ask whether the request or an
approved criterion asks for that behaviour to go. If one does, the removal
is foreseen. If none does, the removal is a mistake. Name the row by its
full name, `path::name`. A file path alone does not judge a removal.

Example: the request says "on Windows, use the AppData folder when APPDATA
is not set". The note quotes `if sys.platform == "darwin":`. The request
names Windows only, and no criterion names macOS. So the removal is a
mistake: `mistakes=["src/click/utils.py::get_app_dir"]`.

The prediction never blocked the commit. Only your silence holds the merge.
