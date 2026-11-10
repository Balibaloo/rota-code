# Review of commit d3adac83, the capability count and the order in the state print, pass 1

Verdict: pick. No finding is high. Four low findings can follow in one small commit.
Worktree: `C:/Users/roman/rota_p363`, branch f363state, base 922e79e7.

## (a) The verdict on each point

1. CONFIRMED. The print exits 0 on all five stacks and prints a sentence for each gap. One gap remains: see finding 3.
2. CONFIRMED. With two head sections that hold `- Destination:`, the first by position prints. The second does not print.
3. CONFIRMED. Only `frame <n>` reads. "capability 9", "(6, D3)" and "dry run 9" do not read. "frames 182 and 171" is lost, both numbers. The stack's own Order bullet reads all six frames: 182, 171, 183, 114, 173, 364.
4. CONFIRMED. "no single capability" alone does not count. "capability 10" counts. A capability word in another sense counts in three probes. A missing page does not crash. A page that is not UTF-8 crashes. See findings 2 and 3.
5. CONFIRMED. The changed assertion still tests the leak. A leaky `doubts` reader turns the test red.
6. CONFIRMED. The `--since` output is byte-identical to the parent on two stacks and two dates. The default print differs by the two new lines only.
7. CONFIRMED. Each part goes through `cut` at 200. Only the Destination part is cut, inside its citation. The three counts survive, so the meaning does not change today. See finding 4 for a shorter form.
8. CONFIRMED. `test_tools_state.py` 40 passed. `test_f33_debts_name_open_frames.py` 6 passed. `test_status_gates.py` 20 passed.

## (b) Findings

1. `rota/tools/state.py` 335 and 381 to 393, `ORDER_FRAME` and `order_frames`. Low. CONFIRMED.
   The plural form "frames 182 and 171" reads no frame, and the print gives no sign of the loss.
   Probe 1, case 3: the bullet "frames 182 and 171, Frame 11, frame 10b, frame  12, frame 10" printed "Order: 11, 12, 10; 2 of 3 open".
   Frame 182 is in the probe stack, parked, and the count omits it.
   C46 asks for the form `frame <n>`, so the writer breaks the rule. But the stack's own numbered list uses the plural twice, at item 2 and item 4.
   Fix: read `frames <n> and <n>` and `frames <n>, <n>` too, or print "1 `frames` form not read" beside the count.

2. `rota/tools/state.py` 421 to 439, `names_capability`. Low. CONFIRMED.
   The gate is the substring "capabilit" anywhere in the line, and the names are substrings such as "budgets" and "the interview".
   Probe 4 counted these lines as naming a capability:
   - "no single capability; it cuts the token budgets of the Critic."
   - "no single capability; it fixes the interview of C36."
   - "the model's capability 0 of 5 on qwen3:8b, a measure."
   - "not capability 9, a pure instrument fix."
   - "finding F1 of the review, capability gaps." The code F1 matches.
   The F17 guard holds only for a line with no capability name in it.
   On today's stack the count is right: 4 of 16, frames 364, 361, 360, 358. Frame 363 says "no single capability" and does not count.
   Fix: return False first on "no single capability", and match a name only in the clause that holds the word or the path.

3. `rota/tools/state.py` 396 to 418, `capability_names`, through `read_lines` at 250. Low. CONFIRMED.
   A `rota/COMPLETION.md` that is not UTF-8 stops the print with a traceback and exit 1.
   Probe 4 wrote the page with the byte 0xe9 and got `UnicodeDecodeError` at line 252.
   The stack has the same failure today, but the page is a second file, and an adopting project owns its encoding.
   The docstring of `destination_line` says the line "never refuses".
   Fix: catch `OSError` and `UnicodeDecodeError` in `capability_names` and return no names.

4. `rota/tools/state.py` 466 to 478, `destination_line`. Low. CONFIRMED.
   The real line is 525 characters. The Next part and the Destination part carry no label and run together: "to a merge. merges on the fold sentence 0".
   The Destination part is 219 characters, and `cut` stops it at "(observed: `plans/dry8-read-2026-...". That leaves an open parenthesis and an open backtick.
   The three counts come before the cut today. A writer who puts a count last after a long clause loses that count.
   With the `CITED` marks removed, the Destination part is 164 characters and needs no cut.
   Fix: remove `CITED` marks before the cut, label each part, and print the three parts on three lines, as below.

       Against the destination (The redirect, 2026-11-10 00:32): Order 182, 171, 183, 114, 173, 364; 6 of 6 open.
         Next: build, because five build rows are open. Frame 364 runs beside the build, for a fact no run holds: whether the pages alone carry a written request to a merge.
         Destination: merges on the fold sentence 0, the same as dry runs 4 to 7. Step 3 of the long term plan reached, step 4 not. Walls that match frames placed and not built: 7 of 16.

   C46 says that `state` prints "the Destination and Next lines", so separate lines also match the words of the rule.
   Cut the heading after its date, at its second comma. The date tells the reader the age of the order.

5. `rota/tools/state.py` 442 to 445, `sentence`. Low. CONFIRMED.
   An empty `- Next:` and an empty `- Destination:` print ". ." with no word.
   Probe 1, case 1c3, printed "Against the destination (Order A): . . Order: 10; 1 of 1 open."
   Fix: print "empty Next bullet." for an empty part, as the missing form does.

6. Outside the points. `rota/tools/state.py` 476 to 479. Low. PLAUSIBLE.
   The count "6 of 6 open" mixes build rows and measure rows. The Next rule of C46 turns on whether a build row is open.
   The print cannot show that fact, so the reader must trust the words of the Next bullet.
   The reason: the Order bullet marks the kinds only in prose, "build rows" and "Measure rows", so the reader has no key to split on.
   Fix: none now. Record the gap in the frame, and split the count only if C46 gives each row a fixed marker.

Checked and clean. No other tool parses the print. A grep for "Live things", "Against the destination" and "By capability:" in py, sh, json and ps1 files finds `state.py` and its test only. `status.py` imports `state` but does not call `render`. A head section after `## Stack` prints "no order section". A file with no `## Stack` reads its sections and exits 0. The new print costs about 25 ms more on the real stack.

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/5ee5ec0b-9675-4645-967d-eab60d0ca52e/scratchpad/p363/`.

- `probe1.py` wrote ten stacks in temporary directories and ran `python -m rota.tools.state --stack` on each. It printed the exit code and the two new lines. The stacks: no head section, a Destination with no Next, an empty Order, an Order with no frame, empty bullets, a head section after `## Stack`, an empty file, no `## Stack`, two sections, and the frame forms. Points 1, 2 and 3, findings 1 and 5.
- `probe4.py` ran `names_capability` on twelve Sprint lines with the real names from `rota/COMPLETION.md`. It also ran the print with no page, and with a page that holds the byte 0xe9. Point 4, findings 2 and 3.
- `probe5.py` replaced `state.doubts` with a reader that does not stop at the next heading. It ran `test_the_claim_names_the_sender_and_its_doubts_print` with `-n 0`. The result was 1 failed, at line 167. Point 5.
- `state_parent.py` is `git show 922e79e7:rota/tools/state.py`. The parent and the commit each ran `--since 2026-11-01` and `--since 2026-10-01` on the worktree stack and on `D:/repos/rota/plans/stack.md`. `cmp` found all four pairs identical. A `diff` of the default print on the worktree stack showed the two new lines and the time line only. Point 6.
- An inline `python -c` probe measured the parts on the real stack: heading 88, Destination 219, Order 174, Next 158 characters. Without the `CITED` marks, the Destination part is 164 characters. Point 7.
- The three test files ran with `ROTA_MODEL=qwen3:8b` and `-q`. Point 8.

## (d) Usage

Input tokens: about 75,000. Output tokens: about 11,000. Total: about 86,000. These counts are estimates, because the harness gives no exact count.
