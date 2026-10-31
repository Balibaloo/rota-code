MODE: reconcile — the prose files you hold, read against the account.

`[problem.baseline]` is the account of this program, written from its code
before any prose was opened. `[code.prose]` holds the files you were woken
for: the README, files under docs/, or both. When it holds more than one,
its `files` line names them, and a `----- <path> -----` line starts each
one. You wrote the account; now check each file against it, one file at a
time. Where the text says README below, read it as the file you check.

Walk the README's claims about what the program does and how a user drives
it. For each claim, one of three things is true:

- the account already says it — nothing to do;
- the README says something the code did not show, or contradicts the
  account — that is a disagreement to log, and you cannot rule on it: "the README is
  stale" and "the code has a bug" are both possible, and only the principal
  can say which. A claim about one item takes that item's id, and a claim
  about no item takes `about_ref="@prose"`, never a directory name. Log it:
  `ledger.log(about_ref=<the item id it touches, or "@prose">,
  about_table=<"items" for an item id, or the README's path for "@prose">,
  assumption="README says <X>;
  the code shows <Y>", kind="conflict")` — one call per disagreement, the
  two sides in it, in the words each source uses;
- the README names a thing the account never mentions — same call: the code
  underdetermines whether it still exists.

Two or three real disagreements beat ten restatements. A formatting
difference, a marketing sentence, an installation note — not findings.

`code.source` any file you need to check a claim against.

**Probe for a name, then read the span it gives.** `code.probe` names the
file and the lines that define a name, and `code.source` reads those lines.
The probe finds the lines. It never replaces the read.

Close each file you hold with its own attest, one row per file. End a file
with `surveys.attest(outcome="found", citations=[the README's path and
what you checked])` when you logged anything about it, or
`surveys.attest(outcome="none_found", citations=[the README's path])` when
the README and the account agree — a real answer, and the common one for a
maintained README. Then check the next file. The session ends when every
file you hold has its attest.
