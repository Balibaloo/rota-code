# The recipe of blind run 1

## Result

Blind run 1 is the dry-run loop of `plans/dry2-recipe-2026-11-02.md` and of dry run 8, with one change: a headless Claude agent answers each page in the Principal seat, and the session only runs the commands. The agent gets `principal_brief.md` and the pages, and nothing else. It has no tools, so it cannot read the code. Its words land through `rota sign <run> <id> --say`, the door that every dry run used. The subject is a fresh clone of tipsI at `ff1f65f`, the commit that the blind test pins. The request is `request.md`. The key is `key.md`, and nobody opens it for scoring before the run ends.

## The parts

- `S` is `C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/5ee5ec0b-9675-4645-967d-eab60d0ca52e/scratchpad/blind1`. It holds the scripts, the run and the record.
- `$S/blind_env.sh`: the environment. One card, port 11434, no router, profile `local`, `ROTA_ONESHOT` unset, as dry run 8.
- `$S/blind_start.sh <commit>`: turn 1. It clones tipsI fresh to `$S/tips` at `ff1f65f` on `master`, removes the `origin` remote, clones rota to `$S/rota_blind1` at the commit, onboards, posts the request, runs to rest and prints the agenda. It refuses to start when `$S/tips` or the run database exists.
- `$S/blind_answer.py`: the seat driver. It reads the open pages from the run database read-only, sends each one to the agent, and lands the words with `rota sign --say`. Its record is `$S/seat/exchange.jsonl` and `$S/seat/exchange.md`.
- `$S/blind_turn.sh <N> [--max-pages K] [--no-run]`: turn N. It copies the database to `$S/copies/tN.db`, runs the seat driver, runs to rest and prints the agenda.
- `$S/probe/probe_t3.py <checkout>`: the hidden probe of `key.md`. Run it only after the run ends.

## The commands

Run these in Git Bash. Write each turn's output to `$S/turns/tN.txt`.

1. Check that the GPU is free. No gate, night, dry run or live measure may use it:
   `curl -s http://localhost:11434/api/ps` must print `{"models":[]}`, and
   `wmic process where "name='python.exe'" get commandline | grep -i "rota"` must show no `rota.tools.gate`, `rota run` or `rota.cli run`.
2. Choose the rota commit `<COMMIT>`, the head of `rota/foundation` at the start. Record it in the stack's status line.
3. For a run from zero, move the probe's material aside first:
   `mv $S/tips $S/tips_probe; mv $S/runs $S/runs_probe; mv $S/seat $S/seat_probe; mv $S/turns $S/turns_probe; mv $S/copies $S/copies_probe`
   Skip this step to continue the probe's run instead. The probe answered one page and ran nothing after it.
4. Turn 1:
   `mkdir -p $S/turns; bash $S/blind_start.sh <COMMIT> > $S/turns/t1.txt 2>&1`
   The output must show `ff1f65f rota: deliver b_1`, `onboard exit 0`, the `posted:` line and `run exit 0`.
5. Turn N, from 2 on:
   `bash $S/blind_turn.sh N > $S/turns/tN.txt 2>&1`
   The seat step prints each page, the agent's answer and `sign exit 0: reply sent: <id>`. Read the agenda at the end of the output.
6. Repeat step 5 until one of these holds:
   - The agenda prints a line that a change was merged, or a tips commit `rota: deliver` above `ff1f65f` exists (`git -C $S/tips log --oneline -3`).
   - The seat step prints `open pages to answer: 0` and the agenda says that nothing waits and nothing builds. This is rest with no merge.
   - Twelve turns pass. This is the turn cap, and it is a finding.
7. After the end, score with the key, in this order:
   1. `git -C $S/tips log --oneline ff1f65f..master` and `git -C $S/tips diff --stat ff1f65f master`.
   2. `cd $S/probe && python -I probe_t3.py $S/tips`.
   3. Read `$S/seat/exchange.md` for the pages he saw. Count the derivable questions of `key.md` field 5.
   4. Open `key.md` and classify the run by its field 6.

## The rules of the seat

- The session does not answer a page itself, and does not edit an answer. The agent's words land as they are.
- The session does not add facts to the brief during the run. A change to the brief is a new run, and the record carries the brief's hash in each call row.
- An agent error lands nothing, and the page is asked again on the next turn. Two errors on one page in one turn are a finding.
- The words `(nothing)` on a page that asks something are asked once more with a reminder. On a line that asks nothing, they land nothing.

## Why this driver

- `probes/agent_principal.py` is the walk's backend. Its imports load on today's code, but it runs inside `probes/walk.py` with the click brief, not inside the `rota run` and `rota sign` loop of the dry runs. Its `call_model` is the base of the seat driver.
- `probes/seat.py` steps the loop itself and not through `rota run --all`. It writes a row to `tests/rota/walks.jsonl` at each end, and it waits on reply files that a second process must write.
- The seat driver keeps the loop that dry runs 1 to 8 measured, so a blind run compares with them line for line.

## Doubts

- The agent model is `opus`, which resolved to `claude-opus-5-5` on 2026-11-10. A weaker model answers less like a careful person. A stronger answer from the seat helps rota, so the run measures rota with a good Principal, not with an average one.
- The brief says that the prompt already refuses a negative bill and that the calculation does not. A person who uses the program knows this from use. Without that sentence, an "already done" page would get an "ok".
- The key has one writer, not the two that section 3 of the blind page asks for.
