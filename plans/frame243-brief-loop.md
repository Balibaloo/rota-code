# Frame 243 brief loop: brief lines on the replayed relay turns

Rota workflow, the seats. Run 2026-10-15, finished 02:27, on qwen3.5:9b,
think False, num_ctx 16384, temperature 0, one sample per seat per line.
Every replay read its database with `mode=ro`. No database was written or
copied. No file under `rota/roles/` changed. The script is
`scratchpad/f243/loop_replay.py` with `loop_extra.py` for lines 7 and 8.
The full completions are in `scratchpad/f243/loop_out_<n>.txt`.

## 0. Result

**No line moved both seats** (observed: eight lines, sixteen replays).
The best line is line 1, the interview's candidate. It moved s188 and
half of s173: `cj_compact` is right, and `cj_serializable` drops "TypeError".
Line 5 moved s173 in full and not s188.

**The replay is sensitive to whitespace, so one sample proves little**
(observed: two controls below). A change of whitespace only, with no word
changed, moved s173 to a right `cj_compact`. Line 1 moved s188 here. The
same words with one line break inside them did not move s188 in the
interview (`plans/frame243-interview.md` section 4).

## 1. Controls

| Control | s188 | s173 |
|---|---|---|
| system prompt unchanged | format kept (night reproduced) | "default spaced" (night reproduced) |
| ruling paragraph with its line breaks made spaces | format kept | compact right; serializable "raises a TypeError ... without custom message conversion" |
| two newlines added after the ruling paragraph | format kept | compact right (old text); serializable with TypeError and no custom messages: a right call |

The second and third controls change no word (observed:
`loop_out_flatcontrol.txt`, `loop_out_nlcontrol.txt`). So a move on s173 is
not evidence of a line's meaning (reasoned: s173 moved on two of two
perturbations).

## 2. The lines

Placement: "the keep sentence" is "Keep the other words of the criterion." in
the ruling paragraph ("**A ruling of the principal.**"). It is the only copy on
one line. The second copy, in the request paragraph, wraps over a line break
and stays unchanged in every line. "After Write" means the line sits right
after "Write the criterion in the principal's words." in the ruling paragraph.
The line breaks of the original paragraph are kept. Inserted text has no line
break.

| # | Line, verbatim | Where | s188 | s173 |
|---|---|---|---|---|
| 1 | "Keep only the words his reply does not fault. Leave out a format, a value or a name that his words reject." | in place of the keep sentence | moved | not moved: compact right, serializable reverts to the old text, no TypeError |
| 2 | same as 1 | first sentence of the ruling paragraph, keep sentence removed | not moved: format kept | not moved: same calls as line 1 |
| 3 | "Before you write, quote the one sentence of his reply that faults the criterion, then write the criterion so that sentence is true of it." | after Write, keep sentence stays | not moved: format kept | not moved: compact right, no respecify of `cj_serializable` |
| 4 | "His reply is the criterion's new text where it states a format, a value or a name. Copy his words for those." | after Write, keep sentence stays | not moved: the night's call byte for byte | not moved: same calls as line 1 |
| 5 | (keep sentence removed, nothing added) | ruling paragraph | not moved: format kept | moved |
| 6 | lines 3 and 4 together | after Write, keep sentence stays | not moved: format kept, and "appended to the command name" | not moved: compact right, serializable "raise an error", no TypeError, calls sent twice |
| 7 | "Keep only the words his reply does not fault. Leave out a format, a value or a name that his words reject. Write in each format, value or name that his words give." | in place of the keep sentence | not moved: no respecify on turn 1, five `glossary.lookup` calls | not moved: same texts as line 1 |
| 8 | "Leave out a format, a value or a name that his words reject." | in place of the keep sentence | not moved: the night's call byte for byte | not moved: same texts as line 1 |

Calls, verbatim (the `criteria.respecify` lines only; the other calls are in
the `loop_out` files):

- 1 s188: `criteria.respecify(id='ver_opt_show_py', text="If the show_python flag is enabled, the output must be the standard version message followed by a space and the Python version string constructed from sys.version_info.major.minor.micro.", term_refs=['line'], surface_refs=['sys.version_info'])`
- 1 s173: `criteria.respecify(id='cj_compact', text='The output must be compact JSON (no indentation) followed by exactly one newline character.', term_refs=None, surface_refs=None)` and `criteria.respecify(id='cj_serializable', text='The function must raise an error if serialization fails (no conversion of arbitrary objects).', term_refs=None, surface_refs=None)`
- 2 s188: `criteria.respecify(id='ver_opt_show_py', text="If the show_python flag is enabled, the output format must be \"{command} {python_version}\" where python_version is obtained from sys.version_info as major.minor.micro and appended to the end of the normal version message.", term_refs=['line'], surface_refs=['src/click/core.py::Command'])`
- 2 s173: the two calls of 1 s173, byte for byte.
- 3 s188: `criteria.respecify(id='ver_opt_show_py', text="If the show_python flag is enabled, the output must be \"{command} {python_version}\" where python_version is obtained from sys.version_info.major.minor.micro, appended to the end of the normal version message.", term_refs=None, surface_refs=['src/click/decorators.py::version_option'])`
- 3 s173: `criteria.respecify(id='cj_compact', text='The output must equal the compact JSON string followed by exactly one newline character.', term_refs=['line'])` and no second respecify.
- 4 s188: the night's call, byte for byte.
- 4 s173: the two calls of 1 s173, byte for byte.
- 5 s188: `criteria.respecify(id='ver_opt_show_py', text="If the show_python flag is enabled, the output must be \"{command} {python_version}\" where python_version is obtained from sys.version_info as major.minor.micro, appended to the end of the normal version message.", term_refs=None, surface_refs=None)`
- 5 s173: `criteria.respecify(id='cj_compact', text='The output must equal the compact JSON string with exactly one newline character appended.', term_refs=['line'], surface_refs=['src/click/utils.py::echo_json'])` and `criteria.respecify(id='cj_serializable', text='The function must raise a TypeError if serialization fails, relying on the standard json module behavior without custom messages or str conversion.', term_refs=[], surface_refs=['src/click/utils.py::echo_json'])`
- 6 s188: `criteria.respecify(id='ver_opt_show_py', text="If the show_python flag is enabled, the output must be \"{command} {python_version}\" where python_version is obtained from sys.version_info.major.minor.micro and appended to the command name.", term_refs=['line'], surface_refs=['src/click/core.py::CommandCollection'])`
- 6 s173: `criteria.respecify(id='cj_compact', text='The whole output stream must contain exactly the compact JSON representation of the object, followed by exactly one newline character, and no other content.', term_refs=None, surface_refs=None)` and `criteria.respecify(id='cj_serializable', text='The function must raise an error if serialization fails.', term_refs=None, surface_refs=None)`, both sent twice.
- 7 s188: no respecify. `glossary.lookup` for version, major, minor, micro and sys.version_info.
- 7 s173 and 8 s173: the two texts of 1 s173, with `surface_refs=['src/click/utils.py::echo_json']`.
- 8 s188: the night's call, byte for byte.

## 3. The two seats under the best line, line 1

- s188 (moved): `criteria.respecify(id='ver_opt_show_py', text="If the show_python flag is enabled, the output must be the standard version message followed by a space and the Python version string constructed from sys.version_info.major.minor.micro.", term_refs=['line'], surface_refs=['sys.version_info'])`. The format literal is gone, and the version goes after the normal message. The `surface_refs` value is not a callable from the list, so a later check can refuse it.
- s173 (half): `cj_compact` is the right compact text. `cj_serializable` reverts to its pre-relay text, so "TypeError stands" and "no custom message" are lost.

## 4. What moves the seat

**No line moved both seats, and the loop names no line that would**
(reasoned from the calls and the controls):

1. s188 moved once in eight lines, under line 1 only. The same words with one
   line break inside them did not move it in the interview. Lines 2 and 8 hold
   the same rejecting sentence and did not move it. So the move does not
   survive a change of the sentence's place or its wrapping (observed: lines 1,
   2, 8 and the interview's section 4).
2. s173 moved on two controls that change no word. So the night's call on s173
   sits at a tipping point at temperature 0, and any perturbation moves
   `cj_compact` (observed: the two controls, and lines 1, 2, 4, 5, 7 and 8 all
   wrote the compact text).
3. The lines that say "keep only the unfaulted words" (1, 2, 7) and line 8 make
   s173 keep the old `cj_serializable` text and drop his "TypeError". The removal
   of the keep sentence (line 5) keeps "TypeError" (observed). So a keep or
   leave-out sentence of these forms works against his additions on s173, and
   its absence leaves the format on s188.
4. Lines 3, 4 and 6 add a sentence after "Write the criterion in the
   principal's words." and leave the keep sentence. None moved s188 (observed).
   This agrees with the interview: the model reads the format as compatible
   with his words, so an instruction to copy or quote his words does not reach
   it.

Reading for the frame (reasoned): the brief loop does not replace the door at
seam 1 for s188. Line 5, the removal of the keep sentence, is the one line
here that gave s173 a fully right call, and s173 also moves on noise. Any line
taken from this loop needs several samples per seat, at a temperature above 0
or over prompt perturbations, before it counts as a move.

Register lines written by this read: 0.
