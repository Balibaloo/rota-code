# The judges that are not Roman: what they find, at which scale, and what the session does next, 2026-11-10

Written by one read agent on Opus for session 4a1d361a, frame 363, from `plans/method/judges-read-brief-2026-11-10.md`. Two extractors on Opus wrote `plans/method/judges-read-extract-a-2026-11-10.md` and `plans/method/judges-read-extract-b-2026-11-10.md`. Those pages hold every cell in full, with its quote and its source. This page holds the rows and the counts. A script in the scratchpad counted the rows of the two pages.

## The result: cells 3 and 5

55 reviews hold 404 findings. 40 reviews are the draw, and 15 are reviews of a design outside the draw. The second views of 2026-11-10 add 7 exchanges with 27 findings, counted apart.

| Set | Reviews | Findings | line or value | function or file | approach of the pass | size or question of the frame | direction above the frame | in words |
|---|---|---|---|---|---|---|---|---|
| 40 drawn | 40 | 232 | 42 | 154 | 9 | 2 | 5 | 20 |
| 15 design reviews | 15 | 172 | 23 | 33 | 61 | 26 | 4 | 25 |
| all 55 | 55 | 404 | 65 | 187 | 70 | 28 | 9 | 45 |
| 7 second views | 7 | 27 | 0 | 0 | 2 | 4 | 7 | 14 |

| Set | repaired in the next pass | named as owed | set aside, reason | set aside, no reason | no record |
|---|---|---|---|---|---|
| 40 drawn | 154 | 27 | 13 | 4 | 34 |
| 15 design reviews | 127 | 1 | 0 | 0 | 44 |
| all 55 | 281 | 28 | 13 | 4 | 78 |

- Reviews with a finding at the scale of the frame or above: 3 of the 40 drawn (R2, R9, R23), 12 of the 15 design reviews (all but D3, D7 and D15), 15 of 55.
- Cell 7, a later fault at the same place that the review did not name: of 55, yes 10, no 19, not sure 21, not searched 5.
- The second views: 17 findings taken, 1 led to a new read, 8 with no record, 1 withdrawn by the judge itself. One reader classified these.

## The limits

- A status line is the session's own account of what it did with a finding. An earlier check found the status lines true and too sure: a doubt or a limit of an agent is often left out.
- A review page is the agent's account. Nobody checked a review against the code in this read.
- 40 of about 359 is one draw. Read every count of the draw as one draw, not as a rate.
- One reader and one pass. Each extractor read its own part once. This reader read the extracts, not the review pages, except for the second views.
- No database was opened. No gate, test, model or rota command ran.
- "Repaired" for a design review rests on the session's line "all N findings taken" in most cases. No revised design page was opened to check each finding.

## The sample

`sorted(glob("plans/*review*.md"))` gives 359 pages. Two more pages carry "review" in a subdirectory and are outside the draw: `plans/archive/architecture-review-verdict-2026-09-19.md` and `plans/method/product-review-seed-2026-11-10.md`. The draw is `random.Random(363).sample(paths, 40)` over the sorted list of the 359. The date of a page is the date of the git commit that added it. Twelve pages have no commit. They take the date of the file on disk.

The 359 pages, by date (name without `plans/` and `.md`):

- 2026-10-11 (15): frame169-review-1, frame195-design-review, frame195-review-1b, frame197-review-1, frame200-design-review, frame200-review-1, frame200-review-2, frame200-review-2e, frame200-review-3, frame200-review-p3, frame203-review-1, frame204-design-review, frame204-review-1, frame204-review-1b, frame207-review-1
- 2026-10-12 (16): frame200-pass5-design-review, frame200-review-4, frame200-review-4b, frame200-review-5, frame200-review-5b, frame200-review-5e, frame204-review-1d, frame204-review-1e, frame204-review-1f, frame204-review-1g, frame204-review-1h, frame209-review-1, frame210-review-1, frame215-review-1, frame215-review-1b, frame215-review-1c
- 2026-10-13 (12): frame173-review-1, frame200-review-5g, frame204-review-2, frame213-review-1, frame213-review-2, frame225-review-1, frame225-review-1c, frame225-review-1d, frame226-review-1, frame226-review-1c, frame229-review-1, frame232-review-1
- 2026-10-14 (19): frame202-review-1, frame202-review-2, frame202-review-3, frame221-review-1, frame221-review-2, frame233-review-1, frame233-review-2, frame233-review-3, frame233-review-4, frame234-review-1, frame234-review-2, frame234-review-3, frame234-review-4, frame237-review-1, frame237-review-2, frame237-review-3, frame238-review-1, frame239-review-1, frame240-review-1
- 2026-10-15 (20): frame129-review-1, frame129-review-1b, frame187-review-1, frame230-review-1, frame243-review-1, frame243-review-2, frame243-review-3, frame244-review-1, frame244-review-2, frame245-review-1, frame246-review-1, frame246-review-1b, frame255-review-1, frame255-review-2, frame256-review-1, ladder-review-2026-10-15, wall-guide-review, wall-method-fit-review, wall-method-review-2, wall-method-review
- 2026-10-16 (16): frame129-review-2, frame222-review-1, frame222-review-2, frame250-review-1, frame250-review-2, frame254-review-1, frame258-review-1, frame258-review-2, frame261-review-1, frame266-review-1, frame266-review-2, frame266-review-3, frame267-review-1, frame267-review-2, frame267-review-3, frame274-review-1
- 2026-10-17 (26): frame140-review-1, frame143-review-1, frame220-review-2, frame223-review-1, frame266-review-4, frame266-review-5, frame273-review-1, frame274-review-2, frame277-review-1, frame277-review-2, frame277-review-3, frame278-review-1, frame278-review-2, frame278-review-3, frame282-review-1, frame282-review-2, frame283-review-1, frame283-review-2, frame283-review-3, frame283-review-4, frame283-review-5, frame283-review-6, frame283-review-7, frame287-design-review-1, frame287-design-review-2, frame290-review-1
- 2026-10-18 (17): frame143-review-2, frame220-review-1, frame286-review-1, frame286-review-2, frame286-review-3, frame287-design-review-3, frame296-review-1, frame297-review-1, frame297-review-2, frame297-review-3, frame297-review-4, frame298-design-review, frame298-review-1, frame298-review-2, frame298-review-3, frame298-review-4, frame298-review-5
- 2026-10-21 (4): frame201-review-1, frame201-review-2, frame201-review-3, frame301-review-1
- 2026-10-23 (28): frame201-review-4, frame272-review-1, frame272-review-2, frame283-review-w1a-2, frame283-review-w1a-3, frame283-review-w1a-4, frame283-review-w1a-5, frame283-review-w1a-6, frame283-review-w1a, frame302-review-1, frame302-review-2, frame303-review-1, frame304-review-1, frame304-review-2, frame304-review-3, frame305-review-1, frame305-review-2, frame305-review-3, frame305-review-4, frame306-review-1, frame306-review-2, frame308-review-1, frame308-review-2, frame308-review-3, frame308-review-4, frame308-review-5, frame309-review-1, frame309-review-2
- 2026-10-24 (27): frame201-review-5, frame257-review-1, frame257-review-2, frame281-review-1, frame283-review-8, frame303-review-2, frame304-review-4, frame305-review-teamnote-2, frame305-review-teamnote, frame306-review-3, frame306-review-w2, frame306-review-wa, frame308-review-6, frame311-review-1, frame312-review-1, frame312-review-w5, frame313-review-s317-2, frame313-review-s317, frame315-review-1, frame316-review-1, frame316-review-2, frame316-review-w3, frame317-review-1, frame318-review-1, frame318-review-2, frame319-review-1, frame320-review-1
- 2026-10-25 (10): frame283-review-wb, frame283-review-wd, frame306-review-wc1, frame318-review-3, frame321-review-1, frame322-review-1, frame324-review-p1, frame325-review-p1, frame326-review-p1, frame327-review-p1
- 2026-10-26 (15): frame315-review-residue, frame322-review-2, frame322-review-p3, frame326-residue-review-1, frame328-residue-review, frame328-review-p1, frame328-review-p2b, frame328-review-p3, frame328-review-p4, frame329-review-p1, frame330-review-p1, frame335-review-p1, frame339-review-p1, frame340-review-p1, frames336-338-review-p1
- 2026-10-27 (14): f19-review-p1, f20-review-p1, f25-review-p1, f31-review-p1, f37-review-p1, f7-review-p1, frame324-review-build, frame330-review-p5, frame343-review-p1, row4-review-p1, rulings-seam-design-review, rulings-seam-review-p1, rulings-seam-review-p5, w3-review-p1
- 2026-10-28 (19): f1-review-p1, f16-review-p1, f2-review-p2, f2-review-p2f, f22-review-p1, f23-review-p1, f37-review-p2, f4-review-p1, f5-review-p1, f7-review-p2, f7-review-p3, hiw-review-p1, p12-review-p1, p7-review-p1, p89-review-p1, seam-review-p1, w10-review-p1, w11-review-p1, w8-review-p1
- 2026-10-29 (7): f345-review-p1, f345-review-p3, f345-review-p5, f345-review-p6, f345-review-p7, f345-review-p8, w14-review-p1
- 2026-10-30 (21): f344-review-p1, f345-review-p10, f345-review-p11, f345-review-p12, f345-review-p13, f345-review-p14, f345-review-p15, f345-review-p15c, f345-review-p4, f345-review-p9, f346-review-p1, f347-review-p1, f347-review-p3, f347-review-p4, f348-review-p1, f348-review-p2, f348-review-p3, f348-review-p4, f349-review-p1, f349-review-p2, f349-review-p3
- 2026-10-31 (11): f348-review-p5, f348-review-p6, f348-review-p7, f354-review-p1, f354-review-p2, f354-review-p3, f354-review-p4, f354-review-p5, f355-review-p1, f355-review-p2, f355-review-p3
- 2026-11-01 (13): f278-f357-review-p1, f278-review-p2, f330-review-p1, f330-review-p2, f354-review-p10, f354-review-p6, f354-review-p7, f354-review-p8, f354-review-p9, f356-review-p1, f356-review-p2, f356-review-p3, f357-review-p2
- 2026-11-02 (4): f330-review-p3, f330-review-p4, f330-review-p5, f360-review-p1
- 2026-11-03 (4): design-onboarding-review-2026-11-03, f361-review-p1, f362-review-p1, f362-review-slice-p1
- 2026-11-04 (8): f362-review-pass5, f362-review-shape-design, f362-review-shape-s1, f362-review-shape-s2, f362-review-shape-s5, f362-review-slice-p2, f362-review-slice-p3, f362-review-split
- 2026-11-06 (7): design-contested-record-review-2026-11-06, design-false-claim-review-2026-11-06, f360-claim-review-2026-11-06, f362-owed-contest-review-2026-11-06, f362-push-review-2026-11-06, f362-reply-record-review-2026-11-06, f362-test-doors-review-2026-11-06
- 2026-11-08 (4): design-false-claim-amend-review-2026-11-08, f360-review-h1-p1, f362-removal-review-2026-11-08, f362-review-slice2-p1
- 2026-11-10 (10): f173-review-p1, f173-review-p2, f182-review-p1, f182-review-p2, f183-114-review-p1, f363-moment-review-2026-11-10, f363-putdown-review-p1, f363-putdown-review-p1b, f363-review-p1, meta-review-2026-11-10
- untracked, file date 2026-10-28 or 2026-11-02 (12): f10-review-p1, f13-review-p1, f15-review-p1, f2-review-p1, f22-review-p2, f24-review-p1, f26-review-p1, f33-review-p1, f35-review-p1, f357-review-p3, f358-review-p1, f8-review-p1

The design reviews outside the draw: 19 pages are reviews of a design or of a rule by name or by first lines. The first 15 in path order are D1 to D15. The cap of 15 left out four reviews of frame 251: `wall-guide-review.md`, `wall-method-fit-review.md`, `wall-method-review-2.md` and `wall-method-review.md`. Two drawn pages are also of this class: R9, the ladder review, and R23, the meta review.

## Cells 1 to 5 and 7, one row for each review

R1 to R40 are the draw in its order. "Given" lists the diff, the brief, the frame's line, the goal of the frame and the destination, and "-" means "not found" or "no". The scale marks are L (a line or a value), F (a function or a file), A (the approach of the pass), S (the size or the question of the frame), D (the direction above the frame) and W (in words). The next acts are rep (repaired), owed, asideR (set aside with a reason), asideN (set aside with no reason) and none (no record). "Asked by: rule" means rule C53 of `plans/method/reference.md` section 6, by the extractor's match. No line that asked for a review names a rule. The quoted line of cell 1 is in the extract pages.

| # | Page | Date | Frame and pass | Kind | Asked by | Given | Findings by scale | Next acts | Verdict, in its words (cut) | Cell 7 |
|---|---|---|---|---|---|---|---|---|---|---|
| R1 | `f361-review-p1.md` | 2026-11-03 | frame 361, passes 1 and 1b, second look on pass 1c | diff review | rule | diff brief - goal - | 9: L1 F7 W1 | rep 7 asideR 1 none 1 | "Verdict: fix. The code does what the ruling asks. The default moves 38 tests to red, an ... | no |
| R2 | `f20-review-p1.md` | 2026-10-27 | frame 344's audit, fix F20 with F21, pass 1 | diff review | rule | diff brief - goal - | 6: L3 F2 S1 | rep 6 | "Verdict: the reader and the lift hold. One high finding is about scope, and five low fi ... | yes |
| R3 | `frame303-review-1.md` | 2026-10-23 | frame 303, pass 1 | diff review | rule | diff brief - goal - | 6: F5 A1 | rep 4 asideN 2 | "Accept for the night." | not sure |
| R4 | `f356-review-p3.md` | 2026-11-01 | frame 356, pass 3 | diff review | rule | diff brief - - - | 3: L1 F2 | asideR 3 | "Verdict: the claim holds on dry1's copy and the real click source. The review has 0 hig ... | no |
| R5 | `frame204-review-1b.md` | 2026-10-11 | frame 204, pass 1b, the second look | diff review | rule | diff brief - - - | 1: F1 | rep 1 | "STANDS: 7 of 7 findings fixed, 0 high, 1 low new (N1), 34 cases newly stale." | yes |
| R6 | `f344-review-p1.md` | 2026-10-30 | frame 344, the Critic's review loop, pass 1 with re-checks ... | diff review | rule | diff brief - - - | 10: L3 F5 A1 W1 | rep 8 asideR 1 asideN 1 | "Verdict: NOT READY. The review has 2 high findings and 5 low findings." p1b: "Verdict: ... | no |
| R7 | `f345-review-p15c.md` | 2026-10-30 | frame 345, pass R6 | other: a classification of deletions | own choice | diff brief - - - | 4: F4 | rep 1 owed 1 none 2 | "Counts: 35 delete, 9 re-pin, 1 skip, 45 in total." | no |
| R8 | `frame298-review-5.md` | 2026-10-18 | frame 298, pass 5, with a re-run at pass 5b | diff review | rule | diff brief - - - | 3: F2 W1 | rep 2 asideR 1 | "Verdict: points 2, 3 and 4 hold. Point 1 fails with one high finding." At d2e85f79: "Ve ... | no |
| R9 | `ladder-review-2026-10-15.md` | 2026-10-15 | frame 243, before pass 1 | rule review | Roman | - brief line goal dest | 9: S1 W8 | rep 9 | "The list of kinds is close to complete and the ruling behind it is right. The two rules ... | not sure |
| R10 | `frame257-review-1.md` | 2026-10-24 | frame 257, passes 1 and 1b | diff review | rule | diff brief - goal - | 6: L4 F2 | rep 2 none 4 | "51b29993 goes on the branch after the gate." | no |
| R11 | `f345-review-p10.md` | 2026-10-30 | frame 345, pass R2, with re-check p10b | diff review | rule | diff brief - - - | 4: L1 F1 A1 W1 | rep 3 none 1 | "Verdict: NOT READY." p10b: "Verdict: READY for the land." | not sure |
| R12 | `frame266-review-1.md` | 2026-10-16 | frame 266, pass 1 | diff review | rule | diff brief - - - | 3: L1 F2 | rep 2 asideN 1 | "Verdict: pass 1b. One high finding blocks the accept." | yes |
| R13 | `f354-review-p7.md` | 2026-11-01 | frame 354, pass 8 | diff review | rule | diff brief - - - | 5: L2 F3 | rep 5 | "Verdict: the claim holds, with 0 high and 5 low findings." | no |
| R14 | `frame197-review-1.md` | 2026-10-11 | frame 197, pass 1 | diff review | rule | diff brief - goal - | 4: L2 F2 | rep 2 owed 2 | "One more pass: the shown call becomes the full map with the unnamed lines as approve an ... | not sure |
| R15 | `frame234-review-1.md` | 2026-10-14 | frame 234, pass 1 | diff review | rule | diff brief - goal - | 10: L5 F3 W2 | rep 9 none 1 | "Verdict: revise. The door refuses the four night-146 over-contests. It also refuses fou ... | yes |
| R16 | `f363-putdown-review-p1b.md` | 2026-11-10 | frame 363, pass 1b of the put-down tool | diff review | rule | diff brief - - - | 2: F2 | owed 2 | "Verdict: accept. The seven repairs hold, and the stack bytes are right on every case." | not searched |
| R17 | `f26-review-p1.md` | 2026-10-28 | frame 344's audit, fixes F26 and F28, pass 1 | diff review | rule | diff brief - goal - | 4: F4 | rep 3 none 1 | "Result: both moves are clean, hold no foreign hunk and stale no recorded case." | not sure |
| R18 | `f349-review-p3.md` | 2026-10-30 | frame 349, pass 3 | diff review | rule | diff brief - - - | 1: F1 | owed 1 | "Verdict: ready to close." | no |
| R19 | `f5-review-p1.md` | 2026-10-28 | frame 344's audit, fix F5, pass 1 | diff review | rule | diff brief - - - | 5: L1 F3 A1 | rep 5 | "Result: the move to one function is clean and holds no foreign hunk. The rule inside th ... | no |
| R20 | `frame297-review-2.md` | 2026-10-18 | frame 297, pass 2 | diff review | rule | diff brief - - - | 8: L1 F6 A1 | rep 4 none 4 | "Verdict: not ready. Three high findings stand." The page then lists four high findings, ... | no |
| D1 | `design-contested-record-review-2026-11-06.md` | 2026-11-06 | frame 362, the design before slice 1 | design review | rule | - brief - - - | 9: L1 F2 A3 S1 W2 | rep 8 none 1 | "Verdict: revise, then build." | not sure |
| D2 | `design-false-claim-amend-review-2026-11-08.md` | 2026-11-08 | frame 360, the design amendment H0 to H11 | design review | rule | - brief - - - | 14: L4 F2 A4 S1 W3 | rep 14 | "Verdict: revise. 2 high, 7 medium, 5 low." | not searched |
| D3 | `design-false-claim-review-2026-11-06.md` | 2026-11-06 | frame 360, the design before slice 1 | design review | rule | - brief - - - | 8: L1 F1 A4 W2 | rep 8 | "Verdict: revise before the build. 8 findings: 5 high, 3 low, two of the low ones outsid ... | yes |
| D4 | `design-onboarding-review-2026-11-03.md` | 2026-11-03 | frame 362, the onboarding design | design review | rule | - brief - - - | 12: L1 A5 S3 W3 | rep 12 | "Revise. High 4, medium 5, low 3. The direction of design B stands." | yes |
| D5 | `f362-review-shape-design.md` | 2026-11-04 | frame 362, the shape layer design | design review | rule | - brief - - - | 10: F3 A4 S1 W2 | rep 8 none 2 | "Verdict: revise. The four facts are cheap and mechanical, and their counts hold on the ... | not sure |
| D6 | `f363-moment-review-2026-11-10.md` | 2026-11-10 | frame 363, the moment design | design review | rule | - brief - - dest | 16: L5 F2 A1 D3 W5 | rep 8 owed 1 none 7 | "Verdict: build with fixes." | not searched |
| D7 | `frame195-design-review.md` | 2026-10-11 | frame 195, the design before pass 1 | design review | rule | - brief - - - | 7: L2 F4 W1 | rep 7 | "Verdict: start the build after the fixes below." | no |
| R21 | `frame282-review-1.md` | 2026-10-17 | frame 282, pass 1 | diff review | rule | diff brief - goal - | 3: L1 F1 W1 | rep 2 none 1 | "stands. Two lows, no high." | yes |
| R22 | `f355-review-p1.md` | 2026-10-31 | frame 355, pass 1 | diff review | rule | diff brief - - - | 5: F4 A1 | rep 5 | "the claim holds for a transient outage, with 1 high and 4 low findings." | no |
| R23 | `meta-review-2026-11-10.md` | 2026-11-10 | frame 363, before any pass | other: a meta review | Roman | - - - - dest | 5: D5 | rep 2 owed 3 | "Rota went from never run alone to measured eight times, and the destination is not reac ... | not searched |
| R24 | `p12-review-p1.md` | 2026-10-28 | frame: fix P12 for wall W12, sprint 32 row 4, frame number ... | diff review | rule | diff brief - - - | 6: L1 F5 | rep 4 owed 1 none 1 | "READY. ... None of them blocks the land." | yes |
| R25 | `f354-review-p5.md` | 2026-10-31 | frame 354, pass 6 | diff review | rule | diff brief - - - | 4: F4 | rep 2 asideR 1 none 1 | "the claim holds on the Liaison path, with 1 high and 3 low findings." | no |
| R26 | `frame296-review-1.md` | 2026-10-18 | frame 296, pass 1 | diff review | rule | diff brief - goal - | 5: F3 A1 W1 | rep 1 owed 2 asideR 1 none 1 | "accept with low findings." | no |
| R27 | `frame302-review-2.md` | 2026-10-23 | frame 302, passes 2 and 2b | diff review | rule | diff brief - - - | 5: L2 F2 W1 | rep 2 asideR 1 none 2 | "accept for the branch." | not sure |
| R28 | `frame220-review-2.md` | 2026-10-17 | frame 220, pass 1b | diff review | rule | diff brief - - - | 4: L2 F2 | rep 4 | "pass 1b stands, with two lows and one outside low." | yes |
| R29 | `frame267-review-1.md` | 2026-10-16 | frame 267, pass 1 | diff review | rule | diff brief - goal - | 6: L1 F5 | rep 4 none 2 | "pass 1b for one high." | not sure |
| R30 | `f356-review-p1.md` | 2026-11-01 | frame 356, pass 1 | diff review | rule | diff brief - - - | 5: L1 F3 A1 | rep 4 asideR 1 | "the claim holds for a top-level dotted name such as `click.pause`, and it does not hold ... | no |
| R31 | `w11-review-p1.md` | 2026-10-28 | frame: fix W11, sprint 33 row 3, frame number not found; p ... | diff review | rule | diff brief - - - | 9: L1 F7 W1 | rep 6 none 3 | "NOT READY. The commit stops the s130 crash, and its tests prove it. One high stays" | no |
| R32 | `frame226-review-1c.md` | 2026-10-13 | frame 226, pass 1c, with a second look on pass 1d | diff review | rule | diff brief - - - | 4: L1 F3 | rep 3 asideR 1 | "accept with one high finding." Second look: "accept." | yes |
| R33 | `frame315-review-residue.md` | 2026-10-26 | frame 315, residue pass 1, with a second look at 2383c991 | diff review | rule | diff brief - - - | 10: F9 A1 | rep 5 owed 3 none 2 | "does not stand for the branch." Second look: "stands for the branch." | not sure |
| R34 | `f183-114-review-p1.md` | 2026-11-10 | frames 114 and 183, build 2, with a second look at b74c8d9f | diff review | rule | diff brief - goal - | 9: L1 F8 | rep 5 owed 2 none 2 | "Fix before the pick." Second look: "pick." | not searched |
| R35 | `frame222-review-2.md` | 2026-10-16 | frame 222, pass 1d | diff review | rule | diff brief - goal - | 4: L1 F3 | owed 4 | "accept with four low findings." | no |
| R36 | `frame309-review-1.md` | 2026-10-23 | frame 309, pass 1 | diff review | rule | diff brief - - - | 5: L1 F3 W1 | rep 2 none 3 | "do not accept as is. Accept after repair 1, which is one call." | no |
| R37 | `f362-review-slice-p1.md` | 2026-11-03 | frame 362, slice pass 1, the harvester | diff review | rule | diff brief - - - | 9: F9 | rep 4 owed 5 | "fix." | not sure |
| R38 | `frame200-review-1.md` | 2026-10-11 | frame 200, pass 1, with a second look on pass 1b | diff review | rule | diff brief - goal - | 7: L1 F6 | rep 6 owed 1 | "one more pass, three high and three low, all confirmed" (status 10:50). Second look: "s ... | no |
| R39 | `frame339-review-p1.md` | 2026-10-26 | frame 339, pass 1, with looks on 1b and 1c | diff review | rule | diff brief - - - | 11: L3 F7 W1 | rep 8 asideR 1 none 2 | "Stands with fixes." Look 1b: "Does not stand." Look 1c: "Stands." | not sure |
| R40 | `f362-owed-contest-review-2026-11-06.md` | 2026-11-06 | frame 362, slice 1 of the owed contest, with looks 2, 3 an ... | diff review | rule | diff brief - - - | 13: F13 | rep 12 asideR 1 | "sound for the measured case, with gaps. Merge after findings 1 and 2 are decided." Look ... | not sure |
| D8 | `frame200-design-review.md` | 2026-10-11 | frame 200, before pass 1 | design review | rule | - - - goal - | 7: A5 S2 | rep 7 | "Do not start as written. Change 5 matters most." | not sure |
| D9 | `frame200-pass5-design-review.md` | 2026-10-12 | frame 200, pass 5 design | design review | rule | - brief - goal - | 8: F6 S1 W1 | rep 8 | "not as written, 2 high, 6 low" (status 15:57) | not sure |
| D10 | `frame204-design-review.md` | 2026-10-11 | frame 204, design pass 1 | design review | rule | - brief - - - | 9: F1 A4 S2 W2 | rep 8 none 1 | "do not start as written, 3 high, 6 low" (status 15:34) | not sure |
| D11 | `frame287-design-review-1.md` | 2026-10-17 | frame 287, design revision 1 | design review | Roman and rule | - brief - goal dest | 20: L2 F1 A10 S5 D1 W1 | rep 10 none 10 | "The design does not stand as written. The direction stands" | not sure |
| D12 | `frame287-design-review-2.md` | 2026-10-17 | frame 287, design revision 2 | design review | rule | - brief - - dest | 13: L4 A5 S2 W2 | rep 7 none 6 | "The design does not stand as written, but it is close." | not sure |
| D13 | `frame287-design-review-3.md` | 2026-10-18 | frame 287, design revision 4 | design review | rule | - brief - goal - | 13: L2 A7 S4 | rep 6 none 7 | "Revision 4 does not stand as written. The direction stands" | not sure |
| D14 | `frame298-design-review.md` | 2026-10-18 | frame 298, the design | design review | rule | - - - goal - | 12: F4 A3 S4 W1 | rep 8 none 4 | "approve the shape, amend before pass 1." | not sure |
| D15 | `rulings-seam-design-review.md` | 2026-10-27 | frame: the rulings seam, sprint 33 row 1, worktree rota_p3 ... | design review | rule | - - - - - | 14: L1 F7 A6 | rep 8 none 6 | "The design stands with changes." | not sure |

## The second views between sessions, 2026-11-10

This reader read these records directly: frame 364 and frame 363 in `plans/stack.md` (lines 1713 to 1735 and 1764 to 1814), and `plans/method/product-map-2026-11-10.md`, sections "Step 6: the second view on the one design" and "The list of turns against this map". `plans/method/boundary-synthesis-2026-11-10.md` holds no second view by these words. The peer rota-82 is likely session b49d24d2. This reader did not check that.

| # | Time | Judge, on whose work | Thing judged | Asked by | Findings and scale | Next act |
|---|---|---|---|---|---|---|
| V1 | 08:29 to 08:31 | 1efd37b1 (rota-a4) on 7fd2421e (rota-13) | `plans/method/meta-design-2026-11-10.md`, read whole, and 32 lines of its map | own choice: "Session 1efd37b1 ... proposes that this session writes the one design and that it reviews the design as the second view. Taken." (08:17) | 6: D4 A2, map lines 757 to 782 | 1 taken: "it corrects this session's judgement, because only step 6, the intake by the step, waits on the run's measure" (08:31); 5 no record in the frame's lines |
| V2 | 10:39 to 11:03 | rota-82 on 1efd37b1 | the product map, read whole, as gap 6 | own choice: "The order of the seven gaps, (reasoned: this session)" (10:39) | 4: S4, the completeness of frame 364's review | 3 no record by the judged session; 1 withdrawn by the judge: "the line of 10:40, that the product review is not a design, is out of date" (11:03) |
| V3 | 14:21 | 7fd2421e on 4a1d361a (rota-3d) and 1efd37b1 | the two say-backs | not found | 1: D1, "This session wrote 'no carrier but its records'" and the boundary reads "speak against it" | taken: "this session takes the correction: the goal is less of Roman at each turn, and not records alone" (14:21) |
| V4 | 14:22 | 1efd37b1 on 4a1d361a | `plans/method/turns-list-brief-2026-11-10.md` | not found | 5: W5, a column or a source of the brief | taken: "the brief is sound, no column is cut, and five changes are taken" (14:22) |
| V5 | 15:18 to 15:19 | 1efd37b1 and 4a1d361a on each other's work | the rota columns of the list, and the map | arranged: "Session 1efd37b1 reads the rota columns against its map when the list lands." (14:22) | 3: W2 (two points of 4a1d361a on the map), D1 ("the fix of one turn can be a wall of the next") | 2 taken into the map, lines 1261 to 1278; 1 led to a new read, `plans/method/chains-read-brief-2026-11-10.md` (15:19) |
| V6 | 16:12 | 1efd37b1 and 7fd2421e on 4a1d361a | `plans/method/one-turn-2026-11-10.md` | not found | 6: W5 (four statements too strong, and "step 10 was wrong as written"), D1 (three of five needs "are each a record at a step") | taken: "The corrections, all taken into the page" (16:12) |
| V7 | 16:13 to 16:14 | 4a1d361a on 1efd37b1 | `plans/method/moved-count-brief-2026-11-10.md` | arranged: "It goes to that session first, and this session launches after its view." (16:13) | 2: W2, a grade and three sources of the brief | taken: "both changes are in" (16:14) |

Cell 2 for the second views: V1 names what it read. No other line names what the judge was given. Cell 7 is "not searched" for all seven, because they are of the last three days.

## Cell 6: the findings at the scale of the frame or above, and the next line

- R2 F1: "So this commit does not change the end of night 170." Next (15:27): "Pass 1b on the same implementer, cap 60k: a key lifts when a row its seat reads for the subject moves".
- R9 F5: "Frame 243's new design is a word rule in another coat". Next (02:05): "Decided here: pass 1 is the supersede door, rung 1, and the record shape, rung 5".
- R23 F1: "The fault is in the conversion of a placed wall into a built fix." Next (00:35): "The order stands at the stack's head, 97198fe8". F3: "A session steers at the scale its instruments show." Next (00:57): "4 of 16 held frames name a capability". F5: "No read of dry runs 4 to 8 places a wall as a model's limit". Next (00:52): "the meta review's sentence on the model's limit is corrected". F2 and F4: the next line is the order of 00:35.
- D1 F8: "Design C mends 6 cases of the contest path, not cause 8." Next (10:36): "Decided: one rule in place of a row per kind".
- D2 F6: "The reach and the price miss the wiring that the probe patched." Next: commit f9e2614f, "all 14 findings taken". No status line records the result.
- D4 F1, F2, F7: "The page omits the `lazy` election that exists." "The cost basis is wrong by about three times." "The slice is under-priced." Next (01:03): "two sessions of slices, the first the icalendar commitments at 16 to 19 cycles".
- D5 F7: "Step 3 is priced too low (low)." Next (00:37): "Shape layer 24 to 26 cycles priced, with the slice 36 to 41, about three sessions."
- D6 F1, F6, F7 (direction): "the sprint boundary is where Roman rules a placement"; "The test is degenerate and has no exit"; "'Repeats' needs judgement on prose." Next: F1 in `plans/method/reference.md` 425 to 427 with no status line; F6 and F7 (00:52): "Taken: the Destination line is three counts".
- D8 F6, F7: "Two of the four counts are queries on the night's database." "A night on pass 1 alone does not measure the frame." Next (06:30): "The fixes are folded into `plans/frame200-design.md`."
- D9 F5: "The night read is priced at 150k against 270k to 330k." Next (16:01): "6 to 7 cycles, 600k to 700k, one night".
- D10 F5, F8: "The predicate holds almost nothing on the four nights." "Pass 1 does not price its re-records". Next (15:40): "pass 1 names 57 stale cases at about 6 card hours".
- D11 F4, F5, F10: "Cause 2 is refuted for frames 114 and 115." "The 15 of 19 line measures little." "Section 6 answers "next" and not "future management"." Next (19:13): "cause 1 rewritten as the unsearched law file". F15, F16 and F17: the next line names none of them.
- D12 F2: "Cause 1 is shown for frame 114 and not for frame 115." Next (19:25): "frame 115 placed under cause 2". F12: "The end check is still the frame 114 case". Next: no record.
- D13 F1, F2: "Frame 1's check is circular." "R4 fixes cause 1 with prose". Next (01:39): "frame 1 becomes a pilot with a baseline count before any ledger". F9 and F10: no record. Revision 6 removed the ledger (01:58).
- D14 F3, F4, F6, F8: "M1's truth is seeded by the guess it measures." "M3 counts the cue's misses with no instrument that can see them." "Five merged items take about four nights." "The (c) residue is a known wall, not a prediction." Next (12:40): "Frame 299 is pushed from section 7.1 for the (c) replies, next sprint."

## Cell 7: the ten "yes" answers

- R2: "F20 with F21 PARTIAL, two own-rule reads unnamed, render_state principal.py:396 and parked scheduler.py:2349" (2026-10-27 19:43).
- R5: "Pass 1 does not hold yet: five seats changed behaviour under the pass's brief text" (2026-10-12 02:50).
- R12: night 153, "a dict value whose inner single-quoted string never closes ... the refusal was the generic text" (2026-10-17 03:39).
- R15: frame 345's design R "took the meaning doors out as one form" (2026-10-30 10:46).
- R21: `_line_reading` "faults lines 1 and 4 on 'I approved two lines, lines 1 and 4, not one'" (2026-10-28 02:22).
- R24: "_gave_up_words already holds the key's words but no page calls it" (2026-10-31 14:27).
- R28: "no committed test pins the base read ... and `_base_text` runs twice per `.py` write" (2026-10-26 05:28).
- R32: "`_WORDS_FAULT` misses 'isn't right' and 'should just say'" (2026-10-24 00:57).
- D3: "principal._built_words still says 'and the tests check the claim'" (2026-11-08 09:41).
- D4: "the lazy election has no exit, 240 rows deferred" and "B is priced at 77 to 86 cycles at the actual rate" (2026-11-03 01:27).

## The gate: the status lines with "new red" on the frames of the 40 drawn reviews

The extractors found such lines on 29 of the 33 frames and fixes of the draw. They found none for frames 257, 282 and 114, and none in frame 220's own lines. Most lines read "N new reds, the known K and the flaky ...", and the next act is an accept, a commit or the next review. These lines named a real new red or a fault of the gate, with the next act:

- Frame 362 for R1 (03:52, 2026-11-03): "4 new reds, 2 flaky in test_l3_rulings, 2 real". Next: "12 cases re-recorded".
- Frame 204 for R5 (02:50, 2026-10-12): "new reds 19, 11 flaky". Next: "A read runs now on Opus".
- Frame 297 for R20 (20:33, 2026-10-18): "2 new reds". Next: "Pass 7 runs on the same implementer, cap 30k".
- Frame 356 for R4 (07:02, 2026-11-01): "new reds 1, real". Next: "The fix goes to the same implementer by message, then the gate again."
- Frame 355 for R22 (18:20, 2026-10-31): "new reds 1, real, test_the_mark_has_one_writer". Next: the fix by message, and the gate again.
- Frame 354 for R25 (21:12, 2026-10-31): "new reds 1, real". Next: "One sentence goes into the landing brief by message".
- Frame 302 for R27 (15:17, 2026-10-23): "new reds 2". Next: "the three commits are reverted on the branch before night 159".
- Frame 309 for R36 (19:25, 2026-10-23): "1 real, test_schema_has_no_clock ... Not accepted on this gate. Pass 1c is sent".
- Frame 339 for R39 (00:20, 2026-10-27): "8 new reds, 0 stale". Next: "The two red cases are read before any fix, by C76".
- Frame 226 for R32 (16:48, 2026-10-13): "piped through tail so its stale line is unread". Next (17:07): the gate again, "Validating at fbde40e6."

## Table 1: findings by scale and by kind of judge

| Kind | Reviews | Findings | L | F | A | S | D | W |
|---|---|---|---|---|---|---|---|---|
| diff review (drawn) | 37 | 214 | 42 | 150 | 9 | 1 | 0 | 12 |
| classification of deletions (R7) | 1 | 4 | 0 | 4 | 0 | 0 | 0 | 0 |
| rule review (R9) | 1 | 9 | 0 | 0 | 0 | 1 | 0 | 8 |
| meta review (R23) | 1 | 5 | 0 | 0 | 0 | 0 | 5 | 0 |
| design review (D1 to D15) | 15 | 172 | 23 | 33 | 61 | 26 | 4 | 25 |
| second view (V1 to V7) | 7 | 27 | 0 | 0 | 2 | 4 | 7 | 14 |

The gate holds no finding by scale. Its lines name a test or a count.

## Table 2: next acts by scale

| Scale | Set | repaired | owed | set aside, reason | set aside, no reason | no record |
|---|---|---|---|---|---|---|
| L | drawn / design | 28 / 13 | 3 / 0 | 1 / 0 | 1 / 0 | 9 / 10 |
| F | drawn / design | 102 / 25 | 20 / 1 | 8 / 0 | 3 / 0 | 21 / 7 |
| A | drawn / design | 7 / 46 | 1 / 0 | 1 / 0 | 0 / 0 | 0 / 15 |
| S | drawn / design | 2 / 20 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 6 |
| D | drawn / design | 2 / 4 | 3 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| W | drawn / design | 13 / 19 | 0 / 0 | 3 / 0 | 0 / 0 | 4 / 6 |

## Table 3: reviews by what the judge was given, and by who asked

| Kind | Reviews | diff | brief | frame's line | goal of the frame | destination | asked by a rule | by Roman | own choice |
|---|---|---|---|---|---|---|---|---|---|
| diff review (drawn) | 37 | 37 | 37 | 0 | 13 | 0 | 37 | 0 | 0 |
| R7, R9, R23 | 3 | 1 | 2 | 1 | 1 | 2 | 0 | 2 | 1 |
| design review | 15 | 0 | 12 | 0 | 5 | 3 | 14 | 1 with a rule (D11) | 0 |
| all 55 | 55 | 38 | 51 | 1 | 19 | 5 | 51 | 3 | 1 |
| second view | 7 | 0 | not found | not found | not found | not found | 0 | 0 | 2, and 2 arranged, 3 not found |

## What this read could not find

- The briefs of the reviews in the session scratchpads. Nobody opened them. "Brief yes" means that the page or the status line shows numbered points.
- A line that names the rule that asked for a review. "Rule" is the extractors' match to C53.
- A record that a reviewer got the frame's heading line, except for R9.
- The status line that started R10, R24, R31, R32, R38, R40, D13, D14 and D15.
- The frame numbers of fix P12 (R24), fix W11 (R31) and the rulings seam (D15).
- A gate line for frames 257, 282 and 114, and in frame 220's own lines.
- R1 F3: the second look says "Not fixed", and the status line of 02:26 says it was marked fixed. The read did not settle the conflict.
- R20: the verdict says "Three high findings stand", and the page lists four.
- D2: no status line records the result. Commits 7f43e4f2 and f9e2614f are the record.
- D14 F7, F10, F11 and F12: the status line counts "twelve amendments" and names no finding.
- Cell 7 of D8 to D15 rests on each frame's own block only.
- R34: the page says "on Fable", and the status line says "on Opus".
- Both extractors went past the cap of 250k tokens: part a used 367,878 and part b used 321,248.
- While it searched for the second views, this reader saw the session's written expectation for this read in frame 363 of `plans/stack.md`. The counts come from the extract pages by a script, not from that line.

## A reading, apart from the tables

Both extractors wrote a reading in a last section of their pages. This page does not repeat them and adds none.
