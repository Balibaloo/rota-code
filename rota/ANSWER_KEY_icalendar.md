# icalendar — written before the first session ran

The second repository, and its whole job is to be a control. Every fix made
today was derived from oauthlib, and a fix fitted to one repository looks
exactly like a real one until it meets another. So the same discipline: what is
true here, written down while nothing has been surveyed, checked afterwards.

Everything below was verified by reading the source at `9961924`, not recalled.

**Repo** icalendar @ `9961924` · BSD · **1,731 grains, 313 edges, 9 areas**,
all 9 under constraint zero.

---

## What the partition says before anybody looks

    .                            18 grains
    src/icalendar             1,357
    src/icalendar/cal            35
    src/icalendar/parser         28
    src/icalendar/parser/ical     8
    src/icalendar/prop          229
    src/icalendar/prop/dt        19
    src/icalendar/prop/recur     11
    src/icalendar/timezone       26

**78% of the repository is one area.** That is a materially worse partition than
oauthlib's, where twelve areas split 279 grains, and it is the most interesting
thing about this run before it starts: `src/icalendar` holds `attr.py` (2,624
lines), `param.py` (849) and everything else that did not land in a subpackage.
One survey session gets 1,357 grains and a context window.

*Prediction:* the `src/icalendar` survey is thin — a couple of terms, a
constraint or none — not because the model is weak but because the area is not a
unit anybody could survey in one sitting. If it comes back with the same density
as `prop/dt` (19 grains), that density is fabricated.

`leaky()` reports `.` coupled to `src/icalendar`, the same shape as oauthlib's
root area: a facade, not a domain.

---

## Predictions

Scored afterwards as **found · missed · invented**. An invention costs more than
a miss.

### 1. `timezone` has three senses, and two of them are bound by a stated rule

The `nonce` of this repository, and a better one, because the invariant linking
the senses is written down in the source rather than inferred.

- `cal/timezone.py` — the **VTIMEZONE component**. ":rfc:`5545` components for
  timezone information." A thing that appears inside a calendar file.
- `timezone/` (the package) — the **implementation that resolves zones**.
  `tzp = TZP()`, `use_pytz()`, `use_zoneinfo()`. Nothing to do with the file
  format; it is which library does the lookup.
- `param.py::TZID` — the **parameter on a property**, whose docstring states the
  binding: *"the value of the TZID property parameter will be equal to the value
  of the TZID property for the matching time zone definition."*

*Expectation:* one or two. Three requires noticing across `cal`, `timezone` and
the root area, which cannot see each other's context — the same test oauthlib's
`nonce` posed and failed twice. The third sense is the hardest because `param.py`
lives in the 1,357-grain area.

### 2. `parameter` means two different things

`param.py` is RFC 5545 §3.2 property parameters as a **domain concept** —
accessors that read them off a component. `parser/parameter.py` is *"Functions
for parsing parameters"* — the **machinery** that turns bytes into them. Same
word, one is the thing and one is the lathe.

*Expectation:* less likely than `timezone`. Both are plausible readings of one
word and nothing forces a session to compare them.

### 3. Line folding is byte-exact and the source says who would notice

`parser/string.py::_foldline(line, limit=75, fold_sep="\r\n ")`. The strongest
external commitment in the repository and the direct analogue of oauthlib's
signature base string:

- **75 octets, not characters.** The loop measures
  `len(char.encode(DEFAULT_ENCODING))`, so a multi-byte character costs what it
  weighs. Getting this wrong produces files other clients reject.
- **CRLF plus one space or tab**, per RFC 5545 §3.1.
- A carve-out that names its own external party: *"For compatibility with
  existing clients, avoid splitting escaped values such as TEXT backslash
  escapes or RFC 6868 parameter escapes across a folded line boundary. See issue
  #1501."*

*Expectation:* this is the one I most want found, and law 12's test —
who outside this repository would notice — is answered **in the comment**. If a
survey of `src/icalendar/parser` misses it, the reading is not going deep enough.
If it finds it and cites the 75, the number is checkable and the citation is
real, which is exactly what oauthlib's fabricated "30 days" was not.

### 4. A property that failed to parse must still round-trip

`prop/broken.py::vBroken` — *"Property that failed to parse, preserving raw value
as text. The raw iCalendar string is preserved for round-trip serialization."*

A commitment not to corrupt data you did not understand. Whoever hands you a
calendar gets it back intact even where you could not read it.

*Expectation:* **missed.** `broken.py` reads like an error module and a survey at
index depth has no reason to open it. Included because a key made only of things
I expect to be found measures nothing — and unlike oauthlib's `estimate_type`,
this one is a *real external commitment*, so missing it is a recall failure that
matters rather than a curiosity.

### 5. Property ordering is a convention, not a rule

`caselessdict.py::canonsort_keys` — "Sort leading keys according to a canonical
order." RFC 5545 does not mandate property order. Round-trip stability and
diffability do.

*Expectation:* missed, and legitimately arguable as *not* a constraint, since the
party who would notice is a diff rather than a peer implementation. A session
that finds it and declines to write it up has read law 12 correctly, and I would
score that as better than writing it up.

---

## What counts as an invention

- A constraint naming an RFC clause that does not say what the constraint says.
- Any number not present in the file the constraint binds. **75 is real; 76 is
  not.** oauthlib produced "30 days" and "90" against a repository containing
  neither, five and two times over.
- A glossary sense not traceable to a symbol in the area being surveyed.
- A definition derivable from the grain name alone — the `--audit` check catches
  these mechanically now and they should be zero, not few.

## What counts as a legitimate refusal

- `none_found` on `prop/recur` or `parser/ical`. Small areas holding no external
  commitment are the honest majority.
- Declining to survey `src/icalendar` thoroughly and saying so, rather than
  producing twelve shallow terms to look busy.

---

## The comparison this run exists to make

Three faults were fixed on oauthlib today: results cut to 1200 characters, a
brief offering fillable examples, and constraint ids the model invented. A
fourth — the context budget — was caused by fixing the first.

**If those fixes were real, this run should show:** zero `--audit` findings,
constraints that cite numbers present in their bound files, and definitions
containing content no filename carries. **If they were fitted to oauthlib**, the
audit will light up on a repository none of them ever saw.

That is the whole point of a second repository, and it is a cheaper question to
answer than it looks.
