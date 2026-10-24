# Frame 321, the provenance: the encode door reads "shows" as "prints" on a criterion about docstring text

Provenance read, 2026-10-24, at HEAD cc9e77c5. Databases night 100 to
night 164, opened `?mode=ro`. Meta workflow. No file but this one changed.

## The verdict

**The door matches every stemmed word of the criterion against a word set,
with no subject and no sentence. It was built on 2026-09-13 for night 28,
where the verb's subject was always the helper. No ruling of Roman's chose
the word set. The build never tested a "shows" about text, and the match
fires on the pieces of identifiers such as `echo_json`.**

## 1. The door today

The `uses_return` block of `tests.encode`, api.py 9938 to 9990, decides:

```
own = _words(own_row["text"] or "") if own_row else set()
own_prints = bool(PRINTS & own and not RETURNS & own)
if says_prints and not says_returns and own_prints:
    raise ValueError(f"the test uses what {uses_return} returns, and the
    criterion {criterion_id} says it prints{_kind()}")
```

(observed: api.py 9958 to 9975). `_words` is `{_stem(w) for w in
re.findall(r"[a-z]{3,}", text.lower())}`, and `_stem` cuts `ing`, `ed`,
`es`, `s` (observed: 7514 to 7524). `PRINTS` holds the forms of print,
output, display, show, write and echo, 14 words (observed: 7210 to 7212).

cr_1 v2 reads: "The docstring of format_filename includes an example where
shorten=True and the path a/b/c.txt shows as c.txt." (observed: night 164,
`criteria`, `surface_refs` `["src/click/utils.py::format_filename"]`).
"shows" stems to "show", in `PRINTS`. No `RETURNS` word is in the text. So
`own_prints` is true (reasoned: the lines above).

s210 turn 4 sent the test body
`assert format_filename("a/b/c.txt", shorten=True) == "c.txt"` and the door
answered "the test uses what format_filename returns, and the criterion
cr_1_format_filename_example says it prints: `format_filename` is a plain
function in `src/click/utils.py`" (observed: `turns` s210 seq 5, the user
field). s214 logged "format_filename prints to stdout and returns None"
(observed: `ledger` l_ee6db6b2cf). The item says "shows as c.txt in the
docstring of format_filename" and his request says "Give format_filename
one example in its docstring" (observed: `items`, s210 seq 5).

## 2. The origin

The door is commit 8234b716 of 2026-09-13 00:56, "a test that uses a
printing surface's return value logs the assumption", for clickI night 28:
"the sentence said echo_json prints an object as JSON, the one test used its
return value, the helper printed and returned None, and the Tester and
Developer ran to quarantine over it" (observed: the body). The word set,
with "show" and "shows", is in that first diff (observed: `git show`). The
workflow was the wake audit, one finding, one fix at the desk, finding 27
in `plans/frame304-provenance.md` line 96 (observed).

Two commits sharpened the door on the same shape: 4fc3d79a, 2026-09-13,
night 42, the criterion under test speaks first over a sibling that said
"return behavior"; af2f83f8, 2026-09-14, night 45, no ledger row lifts the
door when the criterion itself says prints (observed: both bodies).
88cee50c of 2026-09-24, frame 81, moved `PRINTS` to module level for the
triage wall. That wall reads verbs only, through `_verb_words`, and drops
"echo" on the request side because "echo" names a helper (observed: api.py
7256 to 7266, and the body, "with identifier tokens left out"). The encode
door kept the full-word match.

No ruling of Roman's exists on prints versus returns. `rota/DECISIONS.md`
holds one line near it: "whether "display" means return or print is a
judgement, and walk twelve climbed it to the seat as designed" (ruled: the
S0 walks, 2026-09-02, DECISIONS.md 956 to 958). The door of 2026-09-13 took
that judgement from the seat with a word set (reasoned: the two dates).
`plans/stack.md` and `rota/LAWS.md` hold no ruling on the pair (observed).

## 3. The design's own condition

The comment says "Only when the material's own words say the surface prints,
writes or shows" (observed: api.py 9948 to 9949). The code tests no subject.
The three loop cases all had the helper as the verb's subject: night 28,
"echo_json prints the object as JSON, indented"; night 42, "echo_json prints
the object as JSON with the given indent" beside "the docstring describes
the arguments and the return behavior"; night 45, the same text with a
ledger row (observed: `tests/rota/test_desk_guards.py` 4001 to 4030 and
5034 to 5055). Night 42's sibling named a docstring and never reached the
door, because "return" is a `RETURNS` word. Frame 177's
`tests/rota/test_prints_door_kind.py`, night 128, has "shows" as the
command's output, and its fix read the function's kind, not the sentence
(observed: the file's docstring). No test holds a "shows" about text in a
docstring, a page or a message. The build did not test its condition.

## 4. The count

Over nights 100 to 164, the refusal "says it prints" stands in the turn
text of 137 sessions on 125 distinct criteria. The turn text repeats a
refusal across turns, so 1683 strings is an upper bound (observed: the
`turns` tables). Grouped by the word that fired, with the door's stemmer:

| Fired on | Criteria | Session-criterion pairs | Subject of the verb |
|---|---|---|---|
| an identifier piece only: "echo" of `echo_json`, "show" of `show_python` | 57 | 90 | none, no prose PRINTS word |
| "output", mostly as a noun | 48 | 101 | the surface's output in every sampled text |
| "print", "printing" | 8 | 10 | the surface, 1 about raising instead of printing |
| "output" and "print" | 7 | 8 | the surface |
| "write" | 1 | 4 | the surface |
| "show" as a prose verb | 1 | 9 | the path, in a docstring: cr_1 of night 164 |

Two more criteria moved their text since. "writes" stems to "writ", not in
`PRINTS`, so "writes" fires only through "echo" (reasoned: `_stem`). Ten
readings:

- 1: n100 `echo_json_compact`, "`echo_json` ... writes its JSON to the
  stream". Subject the surface. Fired on "echo".
- 2: n102 `cr_show_python_default`, "If `show_python` is not explicitly
  set, it defaults to false". No PRINTS verb. Fired on "show".
- 3: n100 `echo_json_compact_2`, "must not emit any ANSI ... the output is
  pure JSON". The surface's output, as a noun.
- 4: n102 `cr_show_python_append`, "When `version_option` is invoked ...
  the output message must include". The command's output. A factory case.
- 5: n109 `echo_json_compact_3`, "raising a `TypeError` ... rather than
  printing a fallback". Subject the surface, about raising.
- 6, 7, 8: n138 `c_1` "then prints it on a single line", n149
  `echo_json_helper` "must not print any additional text", n146
  `echo_json_support_compact` "must write a string ... to the stream".
  Subject the surface in all three.
- 9: n136 `c3`, "`echo_json(obj)` must not introduce any new
  dependencies". No PRINTS verb. Fired on "echo".
- 10: n164 cr_1, "the path a/b/c.txt shows as c.txt" in "The docstring of
  format_filename". Subject the path. The sentence names a docstring.

Subject the surface in 6 of 10, its output as a noun in 2, no PRINTS verb
in 2, the path in 1 (reasoned: the readings above).

## 5. The repair's shape

- Candidate P, prose words only: strip identifier tokens before the match
  and stem both sides, as the triage wall of frame 81 does. Keeps 1, 3 to
  8, 10. Releases 2, 9 and the 57 identifier-only criteria. Does not
  release cr_1. Without the stem fix, reading 1 is released too.
- Candidate S, the subject: the clause's subject is the surface, "it" or
  "the function". Keeps 1, 5 to 8. Releases 2, 9, 10. Undecided on 3 and
  4, "output" as a noun, the largest group. Needs a parse of model prose.
- Candidate D, the docstring sentence: the PRINTS word does not count when
  its sentence, or the item's text, names a docstring, help text or
  documentation. Keeps 1 to 9. Releases 10 only. See section 3 on night 42.

The page favours D for cr_1, with P beside it for the identifier leak,
which is the larger count. S is the design's own condition, and it is not
a door's fact (reasoned: `plans/wall-guide.md` 408, cause 8).

Usage: about 108k on the counter, against a cap of 80k.
