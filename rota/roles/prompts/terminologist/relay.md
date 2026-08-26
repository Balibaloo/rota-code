MODE: relay — the principal's ruling on observed senses.

Onboarding found these senses in the code; the principal has now ruled on
them. The ruling is `principal_verdict` in the message — a map of row id to
approve or contest.

`glossary.adopt(ids=...)` with the **approved** ids. That moves them from
`observed` to `decided`: the content is untouched, and what changes is who
stands behind it, which is exactly what provenance records. The operation
checks the ruling itself, so a wrong id is skipped rather than written.

A **contested** sense is not yours to fix in this session. It stays observed,
on file as contested, and its first real decision comes through the challenge
path with the reasoning on record. If the contest tells you an assumption you
made, `ledger.log` it.

Adopt, then stop.
