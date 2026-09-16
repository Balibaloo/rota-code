# oauthlib — written before the first session ran

The point of this file is that it exists *first*. "The artefacts look plausible"
is unfalsifiable, and a glossary that reads well and describes nothing is the
failure mode we are actually exposed to. So: what is true about this repository,
written down while nothing has been surveyed, and checked afterwards.

Everything below was verified by reading the source at `40b0ab5`, not recalled.

**Repo** oauthlib @ `40b0ab5` · BSD-3-Clause · 75 files · 279 grains · 126 edges
· **12 areas**, pinned, all 12 under constraint zero.

---

## What the partition already says

The root area `.` — `__init__.py`, `common.py`, `signals.py`, `uri_validate.py` —
has **zero internal edges and crosses into ten other areas**. It is a facade plus
a utility belt, not a domain. `leaky()` reported it before any model ran, which
is the check doing its job.

Noted before the run: **`tick_survey` orders areas alphabetically, so `.` is
surveyed first** — the one area that is not a domain, seen before any of the
domain vocabulary that would give its contents meaning. If the first glossary is
full of plumbing terms, that is a scheduling artefact, not a model failure.

---

## Predictions

Scored afterwards as **found · missed · invented**. An invention costs more than
a miss: a missed constraint is a gap, a hallucinated one is a gate that blocks
real work forever.

### 1. `nonce` has three senses, not one

The strongest single prediction, and the one that most tests whether "one meaning
per word" survives contact with a real codebase.

- `oauth1/rfc5849/request_validator.py` — **server-side replay detection**. The
  server stores what it has seen and rejects a repeat (`validate_timestamp_and_nonce`,
  `check_nonce`, `nonce_length`).
- `openid/connect/core/grant_types/base.py` — **client-generated session binding**.
  Passed through unmodified into the ID Token; the server never checks it for
  uniqueness. Opposite direction of trust from the above.
- `common.py::generate_nonce` — **a value being manufactured**, a random 64-bit
  number concatenated with the epoch timestamp.

*Expectation:* Terminologist finds one or two. Three would be a genuinely good
result, and finding all three requires noticing across three areas that cannot
see each other's context — which is exactly what the artefacts are supposed to
make possible. If it collapses them into one entry, the design's central claim
about compounding through artefacts is in trouble.

### 2. `client` means two opposite things

`oauth2/rfc6749/clients/base.py` — a **local object you instantiate** to prepare
outgoing requests. `oauth2/rfc6749/request_validator.py::authenticate_client` —
the **remote registered application** the authorization server is authenticating.
The `clients/` directory and the `client` in `authenticate_client` sit on
opposite sides of the wire.

*Expectation:* less likely than `nonce`, because both senses are inside the
`oauth2/rfc6749` subtree and the word is ordinary enough to read past.

### 3. The specifications are cited in the source

`common.py` alone carries links to `rfc5849#section-3.3`,
`rfc6749#appendix-A`, and the OAuth MAC draft `#section-3.2.1`.
`oauth1/rfc5849/signature.py` cites down to `#section-3.4.1.3.2`.

*Expectation, researcher off:* Architect writes constraints naming RFC numbers
from directory names and docstrings, with no clause text behind them.
*Expectation, researcher on:* at least one constraint rests on a `reference`
ref, so the provenance view says `observed` with basis `world`. The reference
row's quote is real RFC text. (Before 2026-09-16: `provenance = 'cited'` with
a `source_refs`.) **This is the single comparison the two runs exist to
make.**

### 4. Real external commitments exist and are findable

The signature base string construction (`oauth1/rfc5849/signature.py`) is
byte-exact and interoperability depends on it: get the normalisation order wrong
and every other RFC 5849 implementation rejects the signature. That is an
obligation to remote peers, not to the test suite — which is precisely law 12's
test for a constraint.

*Expectation:* Architect finds *something* in `oauth1/rfc5849`. Whether it frames
it as an external commitment rather than an internal implementation detail is
the actual judgement being measured.

### 5. `estimate_type` returns a priority, not a type

`oauth2/rfc6749/tokens.py` — `BearerToken.estimate_type` returns 9 for an
`Authorization: Bearer` header and 5 for a bare access token. The numbers order
token classes against each other; they are not a type code.

*Expectation:* missed. It is the kind of local convention a survey at index depth
has no reason to open. Included precisely because I expect it to be missed — a
key made only of things I expect to be found measures nothing.

---

## What counts as an invention

- A constraint naming an RFC clause that does not say what the constraint says.
- A glossary sense not traceable to a symbol in the area being surveyed.
- A `reference` ref with no reference row behind it, or a reference row
  whose quote is not in the fetched page.
- Any constraint whose "who outside would notice" cannot be answered from the
  cited text.

## What counts as a legitimate refusal

- `none_found` on an area that genuinely holds no external commitment. `.` is the
  likeliest honest `none_found` in the repository, and reporting it that way is a
  better result than manufacturing a constraint about URL encoding helpers.
- The Researcher answering "I could not reach it" for a domain the principal
  never granted.

---

## Scored after the run

**Researcher off. 79 sessions, quiescent, 873s. 36 survey records — twelve areas
times three roles, complete.** 18 glossary entries, 23 constraints, 16 items.

The machine finished. The output is not worth having yet, and those are two
different results that need saying separately.

### The predictions

| | |
|---|---|
| 1. `nonce`, three senses | **missed entirely** — not one entry mentions it |
| 2. `client`, two senses | **missed, wearing the right shape** (below) |
| 3. Specs cited in source | as predicted: RFC numbers named, no clause behind any |
| 4. Signature base string | **missed** — nothing about normalisation order |
| 5. `estimate_type` priority | missed, as predicted |

I was wrong in the optimistic direction on 1. I expected one or two senses of
`nonce` and it found none, in a repository where the word appears in three
modules with three incompatible meanings.

Prediction 2 is the interesting failure. There *are* three `client` entries — so
a count would call it a hit. All three say "an instance of «file»::Client". That
is the same sense written down three times, once per area, not the collision
between a local object you instantiate and a remote application you authenticate.
The artefact has the shape of the finding and none of its content.

### What it actually produced

**10 distinct terms across 18 entries.** `endpoint` five times, `client` three,
`token` three. `glossary.consult` is in the survey toolkit, so every session
could see what the previous ones wrote, and none of them looked. "Two senses is a
finding" was read as "always write a new row".

**Definitions that restate the index.** "DeviceApplicationServer: a class in
oauth2/rfc8628/endpoints/pre_configured.py". "endpoint: an instance or path in
OAuth protocols". The grain name goes in, a paraphrase of the grain name comes
out, and nothing that required opening the file appears anywhere.

**Vision Keeper's items are docstrings.** "This module contains client classes for
OAuth 2.0." That is not scope — it is the first line of the module, relabelled
`in_scope`.

### The inventions, which are the serious part

> "Retention period for access tokens is 30 days" — **five times.**

oauthlib has no retention policy. There is no thirty in it. This is the exact
failure the key was written to catch: a fabricated external commitment, recorded
as `observed`, citing nothing, that would gate every future change to token
handling and be argued with by everyone who met it.

"Commitment to HMAC-SHA1 signature method in OAuth 2.0", four times — HMAC-SHA1
is OAuth **1** (RFC 5849). The mechanism is real and the attribution is wrong,
which is worse than vague, because it is checkable and false.

15 distinct headlines across 23 constraints. Same no-dedup failure as the
glossary, in the artefact where a duplicate is a duplicated gate.

### What this says

The plumbing is fixed and the judgement is not. Seven scheduling faults had to go
before any of this was reachable, and none of them were about a role's reasoning
— but now that a complete run exists, everything above is about exactly that.

Three faults, in the order I would fix them:

1. **Nothing dedupes across areas.** Sessions compound through artefacts, and
   this is the first evidence that the compounding does not happen: the tool is
   there, in the toolkit, and unused.
2. **Surveys read the index and paraphrase it.** Every definition is derivable
   from the grain name alone. The instruction to open the source exists and is
   not followed, or is followed and not used.
3. **A constraint with no evidence is being written as `observed`.** Law 12's
   test — "who outside this repository would notice it being broken" — has an
   answer for the real ones and no answer for the invented ones, and nothing
   asks the question at the point of writing.

The second onboarding run, with the Researcher, is the one that bears on 3: a
constraint that must carry a clause is a constraint that cannot be invented. It
does not touch 1 or 2.

---

## Second run — predictions, written before it started

Three harness faults were fixed after the first run. Written down now so the
scoring cannot be arranged afterwards to suit whatever comes out.

**What changed.** Tool results were cut to 1200 characters before the model saw
them, so `code.source(start=0, end=400)` delivered a docstring; the cap is 6000
and a cut now says so. The survey brief's four example constraint shapes — "a
retention period", "an interface something else depends on" — are gone, replaced
by the who-outside-would-notice test. Constraint ids derive from the headline.

**The claim being tested is narrow and falsifiable:** the fabrications were
caused by the session having nothing to work from, not by the model being unable
to do the work. If that is right, giving it the file changes the output. If the
constraints come back template-shaped anyway, the truncation was incidental and I
spent a day on the wrong thing.

### Predicted, in descending confidence

1. **Zero constraints headlined "Retention period …", "Interface …" or
   "Ordering …".** The menu is gone. If any survive, they are being generated
   from somewhere I have not found.
2. **No invented numbers.** "Retention period for access tokens is 30 days"
   appeared five times; oauthlib contains no thirty. Any numeral in a constraint
   must appear in the file it binds.
3. **Distinct headlines rise, total rows fall.** 24 rows / 6 headlines becomes
   fewer rows and *more* distinct ones — dedup removes the copies, real reading
   supplies variety. Fewer than 8 distinct would mean reading changed nothing.
4. **Glossary definitions stop restating the index.** "DeviceApplicationServer:
   a class in oauth2/rfc8628/endpoints/pre_configured.py" says nothing the path
   does not. At least half the definitions should contain a content word that
   appears nowhere in the grain name or its path.
5. **At least one constraint in `oauth1/rfc5849` about signature construction** —
   key prediction 4, missed in both prior runs, and the strongest real external
   commitment in the repository. This is the one I would most like to be right
   about and am least sure of.

### Predicted to still fail

6. **`nonce` still collapses to one sense, or is missed.** Three senses across
   three areas that cannot see each other's context. Reading more of each file
   does not by itself make a session notice the other two, and nothing in the
   loop asks it to compare. If this *does* come out right, the compounding claim
   is in better shape than I think it is.
7. **`estimate_type` still missed.** Local convention, no reason to open it.

### The other half of the prediction

The 1200-character cut applied to *every* read in the system, not only the
Architect's. So the L1 and L3 re-record should move some results that have
nothing to do with surveying. **If nothing moves, this fix is smaller than I have
been claiming** and the artefact improvement, if any, came from the brief rewrite
and the dedup instead.

---

## Scored: second run, after the harness fixes

**62 sessions, 446s, and it stopped two thirds through** — Vision Keeper's entire
pass never ran, because abandoning one area settled *after* the frontier had
already answered. That is a scheduling fault, fixed separately, and it means the
artefacts below are 23 of 36 surveys rather than a complete run.

### The predictions

| | |
|---|---|
| 1. No "Retention period / Interface / Ordering" headlines | **hit** — none |
| 2. No invented numbers | **hit** — "30 days" and "90" are gone |
| 3. Rows fall, distinct headlines rise | **hit** — 24/6 became 11/11 |
| 4. Definitions stop restating the index | **miss** — half the glossary is paths |
| 5. A constraint about signature construction | **miss in substance** (below) |
| 6. `nonce` still collapses or is missed | missed, as predicted |
| 7. `estimate_type` missed | missed, as predicted |

The audit went from **29 findings to 4**, and the Architect now reads before it
binds — 10 of 11 constraints bind files the session actually opened, which is
enforced rather than asked for.

### What it is still doing

**Eight of eleven constraints have no text at all.** A headline and nothing else.
The three with text restate the path: "This code implements the endpoints
specified in Section 7 of the OAuth 2 RFC 6749" — and §7 is *Accessing Protected
Resources*, so the one citable claim in the set is wrong.

Prediction 5 is the sharpest result of the run. It produced `OAuth1 RFC5849
Signature Methods Commitment`, bound to
`signature.py::sign_hmac_sha256_with_client`. It **read the right file and wrote
nothing about it.** The refusal made it read; nothing made it say anything.

**The template moved rather than went.** Every headline is now `<area name>
Commitment`, taken from the brief's own phrase "a commitment the code is keeping
to something outside itself". Removing four illustrations removed those four
illustrations. The behaviour underneath — compose a headline from the names in
front of you — is unchanged, and it will find whatever noun the brief leaves
lying around.

### Two faults in the audit, found by reading it

The tool built to replace reading was caught by reading, which is worth
recording rather than quietly fixing.

* **False positive.** "6749 absent from `oauth2/rfc6749/endpoints/base.py`" — it
  is the RFC number and it is in the *path*. The check looks only at contents.
* **False negative, and the costlier one.** Zero `restates-the-index` findings
  against a glossary half made of `oauth1/rfc5849/errors.py → "OAuth 1.0
  protocol implementation error handling"`. The check compares a definition
  against its term, and when the term *is* a path the prose reads as novel.

### The two rules this run says to write

Both trivial, both would have caught it:

1. **A glossary term is a word, not a file path.** Fourteen of twenty-six terms
   are paths. A path has no sense to define.
2. **A constraint with no text is not a constraint.** Eight of eleven. A headline
   alone cannot be checked, argued with, or satisfied.
