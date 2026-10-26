# Candidate C3, the provenance read: his test verdict reaches a mode that cannot act

Date: 2026-10-26, read after 19:33. Read at commit 88464039 on
`rota/foundation`, dated 2026-10-26 19:33. Read-only. The night databases
were opened with `?mode=ro`. No model call ran and no pytest ran. The read
called `park_criterion_relay` and `ruled_test_criteria` on read-only
connections to get the mode key of each relay. Meta workflow for the read,
by the rule of 2026-10-18 (provenance before a fix).

Sources:

- The symptom records, cited and not repeated: `plans/night168-read.md`
  section 1, walk 1 (lines 57 to 75), section 2 row W4 (line 107), section 5
  row 4 and candidate C3 (lines 276 and 292 to 295); `plans/stack.md` frame
  306 (line 1597) and frame 278 (line 1874, parked).
- `rota/core/scheduler.py`: `park_verdict_page` 1902 to 1912,
  `park_verdict_criteria` 1914 to 1937, `verdict_rows` 1950 to 1967,
  `park_criterion_relay` 2009 to 2036, `ruled_clarify_criteria` 2039 to 2062,
  `ruled_test_criteria` 2065 to 2096.
- `rota/core/runner.py`: the relay mode key in `_mode_key` 375 to 390, and
  the writer of `principal_test_verdict` in `resolve_inbound` (2171), lines
  2285 to 2318.
- `rota/core/sandbox.py`: the relay split in `_bind_send.stage`, the approve
  filter 4476 to 4500, the test-row branch 4512 to 4527, the merge of the
  criteria key 4542 to 4552, the one-relay-per-owner refusal 4553 to 4559;
  `stage_park_relay` 4860 to 4910.
- `rota/roles/prompts/terminologist/relay.tools` and
  `criterion_repair.tools` (by `python -m rota.tools.map mode`).
- `rota/DECISIONS.md` 1445 to 1466 (the ruling of 2026-10-08), 990 to 1007.
  `rota/LAWS.md` and `rota/design/`: no rule on the mode of a relay.
- `plans/frame213-scope.md` 40 to 42 (route B), `plans/frame306-provenance.md`
  60 to 75 (the hop table), `plans/archive/stack-2026-10-09.md` line 39 (the
  diff review of 0baacf55, finding 2).
- `.rota/clickI_night168.db`: `messages` m41 to m58, `config` `verdict:m49`
  and `verdict:m56`, `rulings`, `tests`, `criteria`, `sessions`,
  `tool_calls` and `turns` of s139 to s141, s155 to s157, s164 to s167.
- `.rota/clickI_night160.db` to `.rota/clickI_night168.db`, 9 files:
  `messages`, `config`, `rulings`, `tests`, `sessions`, `tool_calls`.
- `git log -S "def park_criterion_relay"`, `git log -S park_criterion_relay`,
  `git log -L` on `park_criterion_relay`, `git log -S` on the test-row
  comment and on the approve filter of the split, `git show` of b0a2086e,
  172b373b, f252df24, 913f54af.

## The result

**Verdict: a gap, not a departure. The split of a relay drops an approved
criterion and keeps an approved test row, so the approved check tst_crit_3
entered the relay as crit_3, and the all-refs mode key then sent the whole
relay to `relay`, where no call reaches the Tester.** The mode key reads
every ref of the relay by design since 172b373b, and the reason holds: a term
beside a criterion needs `glossary.adopt` (observed: 172b373b body; runner.py
380 to 384). The approve filter of 4ef3bd9f predates the test-row route of
1055a2c5 by four days, and it keeps every ref that is no criterion (observed:
sandbox.py 4493 to 4497). A test row is no criterion, so route B maps an
approved test row to its criterion with no approve check (observed:
sandbox.py 4520 to 4526). No ruling, frame or review named that case
(reasoned: the search of question 1).

## 1. Which design made the mode key read every ref

- **The key.** `park_criterion_relay` was added on 2026-10-09 01:21 in
  172b373b, "a criterion repair runs only on a park page's ruling", for frame
  142, from the diff review of b0a2086e, finding 1 (observed: `git log -S
  "def park_criterion_relay"`; the commit body; `plans/frame142-pass1.md`
  175). Its premise: every Terminologist relay that named a criterion went to
  `criterion_repair`, a term beside a criterion among them, so the repair
  mode runs only on "a relay whose every ref is a criterion" (observed: the
  commit body). b0a2086e of 00:48 the same night built the park page and the
  first route to `criterion_repair` from Roman's ruling of 2026-10-08
  (observed: `git log -L`).
- **The commits since.** 67751385, 2026-10-09, frame 142 pass 2, the door
  stages the park relay. 2c602d1b, 2026-10-09, frame 190, a criterion ruled
  on any page. f252df24, 2026-10-13, frame 213 pass 1b, the key accepts a
  criterion whose test row the ruling contests or revises. 6e72b8b9,
  2026-10-23, frame 306 repair 1, a clarify reply's ruled criteria (observed:
  `git log -L`). Each commit widened the ruled set. None of them changed the
  "every ref" test (observed: scheduler.py 2030 to 2036).
- **The split that feeds the key.** 4ef3bd9f and b9a370cd, 2026-10-09 03:00
  and 03:39, frame 142 pass 2b, keep approved criteria out of the relay, from
  the diff review of 0baacf55, finding 2: "the relay door widens a relay the
  session sends to the verdict's full refs" (observed:
  `plans/archive/stack-2026-10-09.md` 39; `git log -S` on the filter). The
  filter drops a ref only when the ref is a criterion (observed: sandbox.py
  4496). 1055a2c5, 2026-10-13 16:46, frame 213 pass 1, route B, then sent
  each test ref as its criterion (observed: `git log -S` on the comment;
  sandbox.py 4512 to 4527). 913f54af, 2026-10-23, frame 306 pass 1b, records
  the same widening: "A relay takes the refs of the reply that woke the
  Liaison" (observed: the commit body).
- **The rule on which mode a test verdict's relay takes.** None in
  `rota/DECISIONS.md`, `rota/LAWS.md` or `rota/design/` (observed: grep for
  `criterion_repair`, `test row`, `route B`). The route is frame 213's scope
  fix, route B: "route a `tests` row of a ruling to its criterion's writer as
  a criterion relay" (observed: `plans/frame213-scope.md` 40 to 42). The mode
  is a build choice of f252df24, not a ruling (reasoned).

## 2. What rule should route a test verdict

- **The seat and the mode.** A ruled test row goes to its criterion's
  writer, the Terminologist, in `criterion_repair` (observed: f252df24;
  scheduler.py 2065 to 2096; reasoned: the ruling of 2026-10-08, point 2,
  quoted in question 5). `criterion_repair` holds `criteria.respecify` and
  `msg.answer_tester`. `relay` holds `glossary.adopt` and `glossary.lookup`
  only (observed: the two `.tools` files).
- **The call that closes it.** `msg.answer_tester`. The Tester's wake then
  carries `principal_test_verdict` and `principal_said` from the ruling's
  chain (observed: runner.py 2285 to 2318). The Tester's `tests.encode` on
  the test row is the act (observed: s141). `principal_test_verdict` is no
  ledger table. It is a key of the wake's pushed message, and
  `resolve_inbound` is its only writer (observed: grep, one site).
- **A mix of ruled and unruled refs.** A default nobody named. The key
  returns false when one ref is outside the ruled set, and the relay takes
  `relay` whole (observed: scheduler.py 2030 to 2036). The reason of
  172b373b covers a term or an `about_ref` criterion beside a ruled one, not
  an approved criterion (observed: the commit body). An approved criterion
  was meant never to reach the relay (observed: sandbox.py 4887 to 4893,
  "An approved criterion never enters it"). So the mixed case should not
  exist, and it exists only through the approved test row (reasoned).

## 3. What the records show

- m49: his verdict on page m47, `tst_crit_1` and `tst_crit_2` revise,
  `tst_crit_3` approve, every criterion approve (observed: `config`
  `verdict:m49`; `rulings` r_40eb207b1c).
- s156, Liaison, mode normal: `msg.relay_architect(["tst_crit_1",
  "tst_crit_2"])`, then `(["tst_crit_3"])`, refused as "every owner these rows
  belong to has its relay already" (observed: `turns` seq 1 and 3).
- m50: relay to the Terminologist, refs crit_1, crit_2, crit_3, cause m49
  (observed: `messages`). `ruled_test_criteria(m49)` is crit_1 and crit_2.
  `park_criterion_relay(m50)` is false (observed: the function on the
  read-only file).
- s157, Terminologist, mode `relay`: `glossary.adopt(["crit_1", "crit_2",
  "crit_3"])` twice, refused as "'crit_1' is not a row of glossary_terms"
  (observed: `tool_calls`; `turns`). No Tester wake followed.
- m56: his verdict on page m53, the same three test rulings and a contest of
  line l_66c4aea55f (observed: `config` `verdict:m56`).
- s165, Liaison: the same two relay calls and a third to the Developer
  (m58). The `tst_crit_3` call was refused (observed: `turns`).
- m57 and s166: the same shape as m50 and s157, one `glossary.adopt`, the
  same refusal (observed: `messages`; `tool_calls`; `turns`).
- s140, the one-ref case: m41 revised `tst_crit_3` alone, m42 carried
  crit_3 alone, `park_criterion_relay(m42)` is true, and s140 sent
  `msg.answer_tester` m43. s141, the Tester, encoded `tst_crit_3` four times
  (observed: `messages`; `tool_calls`; the function).

## 4. How often

**7 of 19 Terminologist relays of a ruled test row ended with no acting
call, all 7 in `relay` mode, on 3 of 9 nights** (observed: the 9 files of
nights 160 to 168). An acting call is `msg.answer_tester` or
`criteria.respecify` in the session the relay woke. A relay counts when the
ruling on its cause contests or revises a test row with a criterion.

| Night | Relays | No acting call | Mode | The relays |
|---|---|---|---|---|
| 160 | 0 | 0 | | |
| 161 | 4 | 1 | relay | m197, s361 |
| 162 | 2 | 0 | | |
| 163, 164 | 0 | 0 | | |
| 165 | 3 | 0 | | |
| 166 | 0 | 0 | | |
| 167 | 7 | 4 | relay | m53, m59 (refs c_1 to c_5, one ruled test), m161, m165 |
| 168 | 3 | 2 | relay | m50, m57 |

No relay keyed `criterion_repair` and ended with no acting call. Night 167's
m53 and m59 show the same wide ref set: five criteria against one ruled test
(observed: `body_refs`). The read did not trace the cause of the extra refs
of m197, m161 and m165 (reasoned: the cap).

## 5. Whether a design departure stands

The ruling of 2026-10-08 covers where his test words go: "A contest or a
revision moves the criterion's version, the Tester rewrites the test from
the ruled words, and the batch is re-derived from the records. The
principal never rules on a test" (ruled: Roman, 2026-10-08 23:25,
`DECISIONS.md` 1459 to 1465). The build meant to meet it: route B carries a
ruled test row as its criterion to `criterion_repair`, and the one-ref case
of s140 met it (observed: f252df24; s140, s141). On night 168 the build
missed it by a defect in the split, not by a choice against the ruling
(reasoned: question 1). So no departure stands. Frame 306 holds the wider
sign that his page words do not reach the criterion. The page that lets him
rule a test line apart from its criterion is that frame's question
(observed: `plans/stack.md` 1597; `plans/frame306-provenance.md` 60).

## The repair

In the split's test-row branch, send a test row's criterion only when the
verdict contests or revises that test row, and drop an approved test row as
the filter drops an approved criterion (sandbox.py 4493 to 4497 and 4520 to
4526). The mode key stays as it is, because its reason of 172b373b still
holds for a term beside a criterion. Red test, from night 168's rows: the
split of s156's first relay call gives a criteria relay with refs crit_1 and
crit_2, `park_criterion_relay` on m50 is true, and s157 keys
`criterion_repair`, which holds `msg.answer_tester`.

## Usage

One agent on Opus, about 70k tokens of context against a cap of 50k. Not
read: where the refs of m197, m161 and m165 came from, and the exact line
that widens a relay call to the reply's refs. The read takes that widening
from 913f54af and the review of 0baacf55.
