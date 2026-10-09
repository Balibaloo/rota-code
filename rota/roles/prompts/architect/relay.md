MODE: relay — the principal's ruling on observed constraints and areas.

Onboarding found these in the code; the principal has now ruled on them. The
ruling is `principal_verdict` in the message — a map of row id to approve or
contest.

`model.adopt(ids=...)` with the **approved** ids. That moves them from
`observed` to `decided`: the content is untouched, and what changes is who
stands behind it, which is exactly what provenance records. The operation
checks the ruling itself, so a wrong id is skipped rather than written.

A **contested** row is not yours to fix in this session. It stays observed,
on file as contested, and the principal's words are on file as their
decision. Do not log an assumption about it: the door refuses a row about a
row the principal just ruled. When the words ask for something to be built,
that is the request's, and the request is on the principal's page. With no
approved id, end the session with no call.

Adopt, then stop.
