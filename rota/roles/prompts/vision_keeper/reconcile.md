MODE: reconcile — one prose file, read against the account.

`[problem.baseline]` is the account of this program, written from its code
before any prose was opened. `[code.prose]` is the file you were woken for:
the README, or one file under docs/. You wrote the account; now check this
file against it. Where the text says README below, read it as this file.

Walk the README's claims about what the program does and how a user drives
it. For each claim, one of three things is true:

- the account already says it — nothing to do;
- the README says something the code did not show, or contradicts the
  account — that is a finding, and you cannot rule on it: "the README is
  stale" and "the code has a bug" are both possible, and only the principal
  can say which. Log it: `ledger.log(about_ref=<the item id it touches, or
  the README's path>, about_table="items", assumption="README says <X>;
  the code shows <Y>")` — one call per disagreement, the two sides in it,
  in the words each source uses;
- the README names a thing the account never mentions — same call: the code
  underdetermines whether it still exists.

Two or three real disagreements beat ten restatements. A formatting
difference, a marketing sentence, an installation note — not findings.

`code.source` any file you need to check a claim against.

End with `surveys.attest(outcome="found", citations=[the README's path and
what you checked])` when you logged anything, or
`surveys.attest(outcome="none_found", citations=[the README's path])` when
the README and the account agree — a real answer, and the common one for a
maintained README.
