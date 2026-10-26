Verdict: d72efa4c stands for the branch. The six points hold, and three low findings stand.

# Frame 328, review of pass 3 (d72efa4c)

The reviewer read `C:/Users/roman/rota_r328c` at d72efa4c, above da89daae. The reviewer edited no tracked file. Every database opened with `?mode=ro`. No model call ran.

## (a) The points

1. The guard: CONFIRMED. A second session gets "unchanged" for the same body and the old replace path for a new body. In one session the re-encode after the note replaces the staged test.
2. The staged version: CONFIRMED. The commit INSERTs the staged values once, at version 2. `artefact_versions` moves once, and one receipt lands.
3. The normalisation: CONFIRMED, with finding 1. The four forms read as one character, and whitespace folds on both sides. The criterion half stays strict.
4. The count: CONFIRMED. The normalised check delivers 0 of the past refusals. No past refusal held an escape form.
5. The fixtures: CONFIRMED. Test 1 and test 3 hold the shape of s271 and s284.
6. The blast radius: CONFIRMED. The callers are few, and the files give 457 passed and 1 known red.

## (b) The entries

### Point 1. The guard

CONFIRMED by probes P1A to P1E. `prior` is the stored row of the id at `rota/roles/api.py` 10468. `own` needs `prior is None` at 10561.

- P1A: session s271 encodes version 1 red and commits. A second session encodes the same body. The answer is `{'unchanged': True, 'note': 'identical to what is already on file, ...'}` from line 10471.
- P1B: the second session encodes a new body. The answer is `{'id': 'tst_tk3'}`, with no version in the staged values. The commit UPDATEs the row to version 2 through `version = version + 1`.
- P1C: in one session, the re-encode after the note returns version 2. A third encode with a new body returns version 3. One staged test stays.
- P1D: after the note, an encode with a new id gets the old one-test answer. The note asks for the same id, so this answer is correct.
- P1E: with no note, a same-id re-encode with a new body gets the old one-test answer. This is open question 2 of pass 3, and the brief allows the change after the note only.

### Point 2. The staged version

CONFIRMED by probes P1C and P2. `session_commit` at `rota/core/db.py` 1196 calls `_apply_write` at 456. The row does not exist, so the write goes to the INSERT branch at 504 with the staged `version`. The staged list holds one tests write, so no INSERT of version 1 runs. `bump_version` runs once per receipt key, so `artefact_versions` for `tests` is 1, the same as a plain encode (P2). P1C showed a `receipts` count of 1 and `new_version` 1.

### Point 3. The normalisation

The function, `rota/core/sandbox.py` 1286 to 1296:

```
_ESCAPE = re.compile(r"\\(?:x([0-9a-fA-F]{2})|u([0-9a-fA-F]{4})|([0-7]{3}))")

def _unescaped(s: str) -> str:
    def _one(m: re.Match) -> str:
        hexa, uni, octal = m.groups()
        return chr(int(hexa or uni, 16) if (hexa or uni) else int(octal, 8))
    return _ESCAPE.sub(_one, s or "")
```

- P3 forms: `\x1b`, `\u001b`, `\033` and the raw byte each give `chr(27)`.
- P3 ws: `_span_of` folds each whitespace run to one space on both sides. The test half calls `_span_of` on the unescaped pair at 1580.
- P3W, a wrong line at the door: the test holds `assert r"\x1b[2J" in sys.stdout.getvalue()`. The quote `assert r"\033[2J" in sys.stdout.getvalue()` is not a line of the test. The door delivered `m1`. See finding 1.
- P3 unit: a bytes line `b"\u001b[2J"` matches a quote `b"\x1b[2J"`. A line `"ABCDEF"` matches a quote `"\x41BCDEF"`. A line `"\\x1b[2J"` matches a quote that starts at the escape.
- P3 door reorder: `in sys.stdout.getvalue() assert "\x1b[2J\x1b[H"` is refused. The span stays contiguous.
- P3 door criterion: `\x41NSI` and `\u0041NSI` in place of `ANSI` are refused. The criterion half stays strict. Extra spaces in the criterion quote are delivered, as before this commit.

### Point 4. The count on past nights

CONFIRMED by the probes `p4_refusals.py` and `p4_fl.py`. They read `turns.user` of each night, because `tool_calls` holds only `args_summary`.

- Night 163 has no `msg.challenge_tester` call. Nights 164, 165 and 166 have 34, 107 and 12 rows in `tool_calls`.
- The `_cites` test half refused 0 calls. The two `quotes=` refusals of the old wording name the criteria row (s143 and s273, night 165).
- The red-line door, `_red_line_refusal` at 1178, refused 4 calls on the test side, all in night 165: s143, s273 twice, s275. This commit does not change that door.
- No refused quote holds an escape form. s143 and s273 sent a paraphrase or the criterion only. s275 quoted `result = clear()`, and the run fails at `assert result == True`.
- The normalised check delivers 0 of the 4. Each of the 4 was a wrong quote.

### Point 5. The fixtures

CONFIRMED by a read of `tests/rota/test_frame328_restage.py`.

- Test 1: the first encode of `TST_TK3_V1` runs for real against a `clear` that writes `\033[2J\033[1;1H`. The run is red, and the test asserts the note text. The re-encode with the same id passes and lands as version 2.
- Test 3: the quote is `TK3_LIVE`, and the row holds the same string, so the criterion half is verbatim. The record skips the middle of the live text, so the middle of the fixture is a reconstruction. The shape does not depend on that middle.
- Test 3: the row holds raw ESC bytes, and the quote holds `\x1b` or `\u001b` as text. The quote also holds ` in sys.stdout.getvalue()`, so it passes the red-line door, as s284 seq 16 did.

### Point 6. The blast radius

CONFIRMED by grep and the run.

- `_unescaped` and `_escaped_view` have callers only in `_quote_refusal` (1343, 1348) and `_cites` (1580).
- `_challenge_evidence` has callers at sandbox 3650 and 5315. Only the tester branch uses `_cites`.
- `encode_noted` is written at api 17309 and read at api 10565. The guard is inline in `tests_encode`, so `tests.encode` is its only route.
- The run covers `test_frame328_restage.py`, the three frame 328 files, `test_challenge_evidence.py`, `test_invoke_door.py` and `test_desk_guards.py`. The result is 1 failed, 457 passed in 120 s.
- The red is `test_invoke_door.py::test_a_session_with_no_batch_reads_the_root`. Pass 3 found it red on HEAD too.

## (c) Findings

1. `rota/core/sandbox.py` 1580. Low. CONFIRMED by P3W: the door delivered a quote of a line that the test does not hold. The unescape applies inside raw strings and bytes literals, and it turns `\x41` into a letter. Fix: decode only an escape whose character is a control character, and skip raw and bytes literals.
2. `rota/roles/api.py` 10648. Low. CONFIRMED by P1C: two re-encodes after the note land the row at version 3, and the table never held versions 1 and 2. Fix: keep the number at 2, or record the rule beside open question 1 of pass 3.
3. Outside. `rota/core/sandbox.py` 1225. Low. CONFIRMED by the P3 door probe: the red-line refusal shows the failing line with raw ESC bytes, so the seat reads `assert "[2J[H"`. Fix: pass the failing line through `_escaped_view` in that refusal.

## (d) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/ad481e08-d0cc-4317-a992-02d5208ea7e8/scratchpad/`.

- `probe_f328.py`: 12 pytest probes on the fixture of `test_frame328_restage.py`, run from the worktree root. All 12 passed and printed P1A to P3W.
- `p4_refusals.py` and `p4_fl.py`: read-only scans of `clickI_night163.db` to `clickI_night166.db`. They pair each `TOOL: msg.challenge_tester(` with its `OK` or `ERROR` line in `turns.user`.
- The run of the seven test files, from the worktree root, with `ROTA_MODEL=qwen3:8b`.

## (e) The counts

- Points: 6 of 6 CONFIRMED.
- Findings: 0 high, 0 med, 3 low.
- Point 4: 0 test-half refusals by `_cites`, 4 test-side refusals by the red-line door, 0 delivered by the normalised check.
- Tests: 457 passed, 1 failed, the known red.

## (f) Usage

The harness gives no per-agent token line. The estimate is about 60k input and 12k output, about 72k in total. That is over the cap of about 40k in the brief. The main costs were the diff, `tests_encode` and the night scans.
