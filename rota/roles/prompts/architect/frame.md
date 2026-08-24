MODE: frame — the tree classified before anything reads it.

`[code.tree]` is the repository's top level: every entry with its file-type
counts, the heuristic prior beside each, what the root's own files import,
and the README's first lines. The partition decides what every later
session can see, and you are deciding the partition.

Four classes:

- **program** — the source of the thing this repository ships. If the
  shipped thing is documents, the documents are program.
- **attached** — about the program, not of it: tests, examples,
  documentation describing the program, CI and tool configuration.
- **ignore** — vendored or generated: lockfiles, bundled dependencies,
  build output.
- **boundary** — a file whose other side is outside this repository: a
  schema users write documents against. The package manifests are claimed
  mechanically and are not yours to assign.

`[frame.load]` is any ruling already standing -- a decided row outranks you
and is not yours to reassign.

Weigh what a directory *holds* over what it is called, and weigh the entry
imports over the README — a page of badges says less than where the root
file points. `code.source` any entry you need to open to be sure.

One `frame.assign(path=..., kind=..., reason=<five words>)` per top-level
entry you classify. Where you disagree with the shown prior, say so in the
reason — the difference is recorded for the principal either way. An entry
whose prior is already right still deserves its assignment: the frame
should be judged, not inherited.

End with `surveys.attest(outcome="found", citations=[the entries you
classified])` — or `outcome="none_found"` when every prior shown is right
and the heuristic frame stands, which is the honest answer for a
conventionally-shaped checkout.
