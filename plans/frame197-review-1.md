# Review of 76521304, frame 197 pass 1 (rulings door, argument key and batch line)

Worktree: C:/Users/roman/rota_r195p1 at 76521304. Read only. No model called.

## (a) Verdicts

1. CONFIRMED (partial defect). Both texts name the fault, and the s263 text names line 5. The s94 text shows a placeholder for words, and the door admits that placeholder as the contest's words.
2. CONFIRMED. The shown call is refused at the next door. The conftest line hides a frame 144 finding and has no strict xfail.
3. NOT A DEFECT. No other refusal of rulings.rule records an offer. The cockpit reads no offer. Recording these two is optional.

## Point 1: the two texts against the real calls

CONFIRMED. The s94 replay (probe A1) gives: `rulings has a key words, and words is its own argument, not a line of the page: rulings.rule(rulings={"2": "contest", "8": "contest"}, words="<the principal's words>")`.
The text names the misplacement. It names no line, which is correct, because the fault is the key and not a line.
A seat at temperature 0 sends a different call from this text. The seat probably copies the shown call to the byte, with the placeholder.
Probe A2 then gets the unnamed-lines refusal. Probe A3 sends the full map with `words="<the principal's words>"`, and the ruling LANDS. The rulings row stores `"<the principal's words>"`.
So the copied path loses the principal's words again, which is the night 138 loss the frame fixes. The seat had M12 in its map, so the door knew the words.
s263 replay (B2): `line 5: bg_3 is the change's line ... contest the item version_option_show_python, line 1. Otherwise approve line 5`. The text names the line. The text names one different call, 5 to approve, and the test shows that call lands.
Fix: show the seat's own value of the misplaced key as words. Do not show a placeholder.

## Point 2: the shown call and the conftest line

CONFIRMED. The shown call holds lines 2 and 8 only. The next door refuses it with `lines 1, 3, 4, 5, 6, 7 have no ruling`.
Frame 135's law says that a refusal names only a call the doors admit. Frame 144's follow check exists to catch a refused offer, and this offer is one.
The conftest comment says that each line of KNOWN_REFUSED_OFFERS is a finding held by a strict xfail in `test_offers_followed.py`. The commit adds no xfail. The line silences the instrument for a door the commit wrote.
The scope's item 4 reasoned that the second refusal is sufficient. That reasoning costs the seat one more turn, and night 139 shows that a seat can end at the repeat door.
The door's own rule already says "A line the reply does not contest is approve". A full map that fills the unnamed lines with approve is that rule applied, and not a new choice.
Fix: show the full map, the seat's lines as sent and each other line as approve, with the seat's words. Remove the conftest line.

## Point 3: offers and facts on the batch-line refusals

NOT A DEFECT. In rulings_rule (7241-7470), only the new `_argument_key` calls `_offer` or `_fact`. The other ten refusals record neither.
`_offer` and `_fact` record only when `api.RECORD` is on, which is under pytest. No file under rota/ other than api.py reads `ctx.offers` or `ctx.facts`. The cockpit does not depend on them.
The follow check therefore does not see "approve line 5". The new test sends that call and asserts that it lands, so the path has coverage.
Recording them gives the instrument the same coverage for free. The lack is consistent with the rest of the door.
Fix (optional): wrap "approve line {key}" in `_offer` with the map with the key set to approve, and record `ref` as a `_fact`.

## (b) Findings

1. rota/roles/api.py:7233-7237. High. CONFIRMED by probe A3: the shown call carries `words="<the principal's words>"`, and the door lands a contest with that placeholder as words. Fix: put the seat's own value of `rulings["words"]` in the shown call.
2. rota/roles/api.py:7233-7237 and tests/rota/conftest.py:170-175. High. CONFIRMED by probe A2 and by the test's own assert: the offered call is refused, and the conftest line silences frame 144's check with no strict xfail. Fix: offer the full map with the unnamed lines as approve, and remove the conftest line.
3. rota/roles/api.py:7420-7422. Low. CONFIRMED by probe B1: a seat that keys the change line by its ref (`"bg_3"`) gets "approve the line" with no number, though `order` knows it is line 5. Fix: take the line from `order.index(ref) + 1` when the key is the ref.
4. rota/roles/api.py:7346. Low (outside the points). CONFIRMED by probe C1: a bad word on a key before `words` gets the word refusal, and the misplacement is named only on the next call. Fix: scan the map for argument keys before the loop.

## Closing line

One more pass: the shown call becomes the full map with the unnamed lines as approve and the seat's own words, and the KNOWN_REFUSED_OFFERS line goes.

## (c) Probes

- rv197/test_probe197.py, run with pytest from the worktree root. The probe imports the `db` fixture, `_m11` and `_m141` from tests/rota/test_frame193_pass1.py.
- A1 to A3: s94's call to the byte, then the shown call copied, then the full map with the placeholder words. The probe reads the stored words.
- B1, B2: s263's call with the key `bg_3`, then with the key `5`.
- C1, C2: a bad word before `words`, and a nested `rulings` key.
- tests/rota/test_frame193_pass1.py: 10 passed. The gate was not run, because no point needed it.

## (d) Usage

The harness reports the tokens. My estimate is about 30k input and 6k output, about 36k total, under the 40k cap.
