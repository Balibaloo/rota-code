# Frame 324: what the Terminologist saw at s280 of night 167

Read-only gathering, 2026-10-29. Sources: the register
`C:/Users/roman/rota_n167g/.rota/clickI.db` (tables `sessions`, `turns`,
`tool_calls`), `plans/night167-read.md` lines 71 to 78, 98 and 127,
`plans/night167-walk2-read.md` lines 82, 99 and 110, and `rota/roles/api.py`
and `rota/onboarding/areas.py` at head b3018844 and at night 167's commits
40b16f78 and 4bb2656b.

## 1. What s280 saw

s280 is a Terminologist on `qwen3.5:9b`, woken by relay m152 with the
principal's words "make the test expect the output clear writes today, then
check that it returns True" (observed: `sessions` seq 280, `turns` seq 1).
The prompt held a pre-run `code.callables` table with three columns, `grain |
sym_kind | fan_in`, and no kind column. Its first row was
`examples/termui/termui.py::clear | function | 0`. The library's
`src/click/termui.py::clear | function | 0` was row 9, with the same shape and
no mark. Rows 13 on were `tests/test_arguments.py::test_*`. The runner's
account at turn 3 reads "cut the candidate symbols: 865 of 885 rows not shown"
(observed: `turns` s280 seq 1 and seq 3). The pre-run `criteria.consult`
showed tk_2 and tk_3 with headlines only, and no surface (observed: the same
prompt). Nothing in the prompt said which `clear` is program code
(observed: no "program", "attached" or "kind" in the 6794-character user text).

## 2. What it called and what refused it

s280 ran 10 calls, the first 8 pre-run (observed: `tool_calls` s280). Its own
two calls at seq 9 and 10: `criteria.respecify(id='tk_3_clear_screen_return_success',
surface_refs=['examples/termui/termui.py::clear'], text='When stdout is a
terminal, clear() must emit the exact ...')` and `msg.answer_tester`. Nothing
refused s280. The door answered `{"respecified": true, "surface_changed": true,
"from": ["src/click/termui.py::clear"], "to": ["examples/termui/termui.py::clear"]}`
(observed: `turns` s280 seq 2). The refusals fell on the Tester after it.
s281 turn 3 and s283 turn 4: `ERROR tests.encode: the surface
'examples/termui/termui.py::clear' lives in termui.py and this test imports
from click.termui. Import the surface from its own module`. s281 turn 4, the
other door: "the batch's other tests import click -- one program, one name. Import
from click like the others; a second module is a second program" (observed:
`turns` s281 and s283). The seat took the first `clear` it was shown, and the
listing's order came from the index, which writes `examples/` before `src/`
(reasoned: the row order of the table, and `plans/frame324-provenance.md`).

## 3. Did the ruled partition reach the prompt

Night 167: no. `rota/roles/api.py` at 40b16f78 and at 4bb2656b holds no
`_frame_ranked`, and `rota/onboarding/areas.py` at both commits has no
`kind_of` (observed: `git show <sha>:<file> | grep -c`). The `code.callables`
listing of that code sorted by `fan_in DESC` alone, and every fan-in was 0, so
the index order decided (reasoned: the table shows all fan-in 0 and `examples/`
first). Head b3018844: yes. The one reader is `kind_of` in
`rota/onboarding/areas.py` line 82. It reads `frame_rulings` through
`ruling_for` and falls back to `is_attached`. `code_callables` at `api.py`
18909 passes its rows through `_frame_ranked` (`api.py` 17052), which adds a
`kind` column and sorts `program, surface, attached, ignore`. `code_probe`
(`api.py` 17067) does the same and its cut note says "the program's rows, then
the attached rows". The surface door in `_vet_surface` (`api.py` 5508 to 5547)
reads `kind_of` and refuses an attached callable that has a program twin. A bare
name with several rows goes to `_program_rank` (`api.py` 5436), which lists the
program rows first: "names N symbols in the index, and M of them are program
code. Write one as path::name, the program's first". Commit dfc16500 of
2026-10-27 landed this (observed: `git log -S "_frame_ranked"`). At head, s280's
listing would show `src/click/termui.py::clear | program` before
`examples/termui/termui.py::clear | attached`, and the qualified `examples/`
respecify would be refused with the program twin named (reasoned: the code at
5532 to 5547; the review `plans/frame324-review-build.md` reports the same on
night 167's real index).

## 4. What the second half's build still needs

Nothing in code: the head lists candidates for a bare name at both doors.
The second clause needs a count only: Architect sessions that repeat a bare
symbol on nights 172 to 175, which the night 175 read did not count
(observed: frame 324's status of 2026-10-29 00:43).
