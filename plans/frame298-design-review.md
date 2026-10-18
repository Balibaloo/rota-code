# Frame 298, the design review

Read-only reviewer on Opus, 2026-10-18 12:31. Repository `D:/repos/rota` at
HEAD bbd00581. Rota workflow, reviewed by the meta workflow. Subject:
`plans/frame298-design.md`. Sources read: the investigation, the count, the
design, P4 piece 2, frame 190's design 2.2, laws 1, 3, 9, 11, 12 and 14, the
composition page, and the code at HEAD through the map tool.

**Verdict: approve the shape, amend before pass 1.** The row, the owner and
the route follow Roman's ruling of 2026-10-18. Four high findings block the
build as written: the relay refuses a `guess:` ref, the line resolves to its
row on three clocks, the measure's truth is seeded by the guess, and M3 cannot
count its own misses.

## (a) The verdict on each point

1. The row: holds. Law 1 holds with the Architect as the one writer. Law 3 adds no edge. Law 14 holds weakly, because `ver` is a counter and the class `content` is wrong (finding 9).
2. The page: a ruling can reach the wrong row at the hand-over (finding 2). "The team" matches the page convention and hides no owner Roman named.
3. The route: no path writes `contested`, and `cancel` cannot fire. The relay is refused at the send door (finding 1). The cue text has no touch-page case (finding 5).
4. The (c) residue: right by law 9 for the text half. The files half is a gap. Push the follow-up frame now (finding 8).
5. The measurement: M0, M1 and M2 compute from rows. M3 and M4 need a hand reading (finding 4). M1's truth is circular (finding 3). Five merged items take about four nights, not two (finding 6).
6. The passes: change the order to 1, 3, 2, 4 (finding 7). Pass 3 holds the wall's red case. The walk is a full night, as the design says.
7. The list of what a build needs is in section (b), finding 12.

## (b) Findings

1. **The send door refuses every relay that carries `guess:<item>`.**
   `rota/core/sandbox.py` `_bind_send.stage`, the `dangling` check (about
   line 2876), calls `api.ref_resolves` (`rota/roles/api.py:4791`) on every
   ref of every message, relays included. Severity high. CONFIRMED: the
   probe returned `guess:echo_json False`, `echo_json True`, `bg_3 True` on
   night 156's database. The design's section 3.4 never names this door.
   Every no-batch guess ruling of 2.3 and 3.1 then dies at the Liaison's
   relay. The 14 no-batch pointer faults of the count take this path.
   Fix: `ref_resolves` admits `guess:<item>` when `<item>` is a request item,
   and pass 3's test sends the relay through the real door.

2. **The guess line resolves to its row on three clocks.** The send door
   decides the stamp at send. `render_page` renders line 2 from live rows at
   every principal read (`rota/roles/principal.py:196`) and at the ruling
   (`rulings_rule`, `api.py` about 9688). `land` decides the alias from live
   rows at land. Severity high. CONFIRMED by reading: `pending_asks` calls
   `render_page` on each read, and the design's 2.1 point 3 and 3.2 point 3
   read `batch_touch` live. Case one: he reads the guess, `annotate` then
   writes batch rows, and `land` aliases his words to a batch prediction he
   never saw. Case two: he reads a batch plan, the batch is cancelled or
   merged, and his words become a guess rewrite. The alias also skips frame
   255's `built_line_faulted` check for a built batch on a direct line-2
   contest, because the guess-line door asks only for words.
   Fix: stamp the target at send, `guess:<item>` with the batch id or the
   guess `ver`, in the `stamped` row. Render and `land` read the stamp, and
   a built batch keeps frame 255's check.

3. **M1's truth is seeded by the guess it measures.** Section 1.3 pushes
   the guess into `annotate` with "Start from it". Section 5.2 then scores
   the guess against the merged batch's `batch_touch`. Severity high.
   CONFIRMED by the design's own text. The baseline index line never seeded
   `batch_touch`, so 8 of 26 against 60% compares two different truths.
   Fix: the truth is the paths of the merged head commit's diff against its
   base, read from git.

4. **M3 counts the cue's misses with no instrument that can see them.** A
   row tells a pointer fault only when a reader classes the words. The only
   classifier is the cue, and the cue cannot count its own misses. M4 has
   the same need. Severity high, because M3 is the ratio part of the
   ends-when (5.4 point 2). PLAUSIBLE: the count's classes were hand
   readings (`plans/frame298-count.md` section 1).
   Fix: 5.3 lists every line-1 contest or revise that wrote `contested`, with
   its words, and the night read classes each by hand with the count's rules.

5. **The cue's refusal has no text for a touch or stopped page.** Those
   pages carry no guess ref by 2.1, so the cue takes the "no guess line"
   text: "The team has not guessed that code yet. Rule the key
   guess:<item>". The page shows "The team expects to touch" on line N.
   Severity low. CONFIRMED by reading: the count's 8 batch-line rows (42 to
   91) all contested the item on such a page, and 3.3 gives two texts only.
   The two texts also hard-code "line 1" and "line 2". The count's rows 35,
   87, 88 and 92 had the item on line 2. Fix: three texts built from the
   order, and the touch-page text names the batch line's number.

6. **Five merged items take about four nights.** The design says "a night
   holds about three merged items (observed: 26 over 21 nights)". 26 over 21
   is 1.24 a night. Severity low. CONFIRMED: merged batches per night over
   nights 136 to 156 read 2,1,1,2,1,1,0,1,0,0,0,3,3,1,0,2,3,2,2,0,1. Night 156
   merged one. Fix: write "about four nights" in 5.2, and let the escalation
   wait on the item count, not on a night count.

7. **Pass 2 makes the Liaison cassettes record under a door that refuses
   line 2.** Pass 2 inserts a numbered line on every present, so every
   Liaison case whose prompt holds a page goes stale and is re-recorded.
   Pass 3 then changes the door and the refusal texts, and the same cases go
   stale again. Severity low. PLAUSIBLE: the design's pass 2 review point
   names "the re-records of the Liaison cases whose prompt carries a page".
   A probe registered a gate-band predicate shaped like `touch_guess` before
   `signoff`. Across 12 frontier-stepping test files it fired 0 times in 347
   tests, so the suite does not see the new frontier order at all.
   Fix: order the passes 1, 3, 2, 4, and add a pass 1 frontier test with
   `signoff` and `touch_guess` both owed.

8. **The (c) residue is a known wall, not a prediction.** 18 rows of the
   count lie in class (c). The investigation shows the Vision Keeper's
   amendment carrying files words into the request text twice (s111, s327).
   Law 9 is right for the text half: a correction of the request's text is
   an amendment. The files half rides into that amendment. Severity low.
   CONFIRMED from the records. CLAUDE.md rules that a wall a read names is
   fixed or stays an open frame with its reason. Fix: push the follow-up
   frame now. Its cheap shape: when the cue's `files` and `content` are both
   true, the door requires a guess-line ruling beside the line-1 ruling.

9. **`touch_guesses` declares class `content`, and its key holds a
   counter.** `identity.py` defines `content` as "the row IS a content hash
   of something external". `ver` is "one more than the highest", so a second
   relay of one ruling writes a second version. Severity low. PLAUSIBLE:
   the "every owner has its relay already" door holds one session, not two.
   Fix: class `relation`, key (item_id, item_ver, ruling_id or an empty
   string, grain), with `ver` derived at read for the order.

10. **One `batches.guess` call per session meets a relay with two items.**
    The split sends every `guess:` ref of a verdict in one Architect relay.
    The op refuses the second call. Severity low. PLAUSIBLE: 4 of 97
    rulings in the count ruled two request items. Fix: refuse a second call
    for the same item, not a second call.

11. **The guess relay lacks the working set that the batch relay needed.**
    `resolve_inbound` (`rota/core/runner.py` about 1997) pushes `touch` with
    the disputed paths taken out for a batch relay. The frame 190 interview
    found that the seat kept a listed path over `principal_said` without it.
    `_resolve_refs` returns nothing for `guess:<item>`, so the seat also gets
    no item id or text. Severity low. PLAUSIBLE: the design's 3.4 point 5
    pushes only the index's test files. Fix: push the current guess and the
    item row for a guess relay, through `disputed_paths`.

12. **What a build needs and the design does not say.** Severity low.
    CONFIRMED for the mode key by the `tick:` branch of `_mode_key`. Fix:
    add each item below to the design before pass 1.
    - The mode key. `_mode_key` turns `tick:touch_guess` into the mode
      `touch_guess`, not `guess`. Name the predicate `guess`, or add a key.
    - The `guess.md` brief whole: the working-set key names, the refusal
      texts of the op, and the one-line reply after the call.
    - The Liaison's landing brief: one line that line 2 is the code the
      request touches, and files words go there. The design edits only
      `verdict_signoff.md`.
    - The `signoff` side: whether `tick_signoff` or the Vision Keeper's
      submit brief names the guess. The design says nothing waits on it.
    - The op's schema: `batches.guess(item_id: str, paths: list[str],
      symbols: list[str] | None)`, its entry in the tools manifest, the
      grain-kind check for a symbol, and the `ver` read inside the commit.
    - The register: the `REGISTER.md` row, the `REGISTER_ENTRIES` count in
      `tests/rota/test_predicates.py:902` (29 to 30), and the obligation
      lint in `rota/testkit/obligations.py`.
    - The instrument: the hand-read list of finding 4, the git truth of
      finding 3, and the M0 rule for "a sign-off page", a present whose
      cause is a `submit`.
    - P4 piece 2 asks for a case that "runs on both models". The design
      names `qwen3.5:9b` only.

**Outside the points.** Findings 1, 9, 10 and 11 lie outside the text of the
numbered points. Finding 1 is the one that blocks the route.

What holds, checked: no path writes `contested` from a `guess:` key, because
the `UPDATE items ... WHERE id = ?` of `land` matches no item for it.
`cancel` reads only `items.approval` and `approval_ver`, so the guess route
cannot fire it. Law 3 needs no edge: the Architect writes and reads
`batches`, and the Liaison already relays to the Architect. A
`touch_guesses` receipt feeds `cascade_wakes`, whose result `loop.py:337`
stores as text and never dispatches.

## (c) Probes

All files are under the scratchpad of session 6977407c, directory `f298r`.

1. `f298probe.py`, a pytest plugin. It registers a gate-band predicate
   shaped like `touch_guess`, one seq before `signoff`, and logs each fire.
   It ran with `ROTA_MODEL=qwen3:8b` over `test_delivery`, `test_frontier`,
   `test_request_page`, `test_steering`, `test_touch_note`,
   `test_predicates`, `test_signoff_assumptions`, `scene_tests`,
   `test_greenfield`, `test_arc_synthetic`, `test_talk` and
   `test_intake_fork`. Result: 347 passed, 4 xfailed, 0 fires. The baseline
   of the first 7 files without the plugin: 303 passed, 4 xfailed.
2. `python -c` on `.rota/clickI_night156.db?mode=ro`: `api.ref_resolves`
   on `guess:echo_json`, `echo_json` and `bg_3`. Result: False, True, True.
3. `python -c` over `.rota/clickI_night136.db` to `night156.db`, read-only:
   merged batches per night. Result: 26 merged over 21 nights.
4. The map tool on the tables `batch_touch`, `batches`, `receipts` and
   `artefact_versions`, and on `_owner_of_ref`, `_mode_key`,
   `request_rows`, `land`, `rulings_rule` and `_line_refusal`.
5. `python -c` on `rota.design.graph`: the edges at `batches` and the
   read, write and message edges of the Architect.

## (d) Usage

Input about 165k tokens, output about 14k tokens, total about 179k
(reasoned: the session budget counter, not the harness line). The cap was
about 100k. The relay door and the probe of finding 7 took the excess.
