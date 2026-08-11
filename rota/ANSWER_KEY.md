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
*Expectation, researcher on:* at least one constraint carries `provenance =
'cited'` with a `source_refs` pointing at a reference row whose quote is real
RFC text. **This is the single comparison the two runs exist to make.**

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
- `provenance = 'cited'` with no reference row behind it, or a reference row
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

*(left empty on purpose until there is something to write here)*
