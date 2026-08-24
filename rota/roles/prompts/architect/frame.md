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
entry, each entry once — and then, in the same turn, the ending:

    surveys.attest(outcome="found", citations=[the entries you classified])

The attest is the judgement; assignments without it are a session that
never happened. `outcome="none_found"` when every prior shown is right and
the heuristic frame stands — the honest answer for a conventionally-shaped
checkout, and then the attest is the only call you make.
