# Operating facts

This page holds facts about the rota box, models, runs, and measurement. The facts moved from the assistant's memory on 2026-09-16. Each fact keeps its date and the name of the person who ruled it.

## Repositories and history

- The composition page is `plans/composition.md`. Read the composition page before any other rota document.
- On 2026-09-14 rota split out of Custom_AI_TUI into github.com/Balibaloo/rota-code. A bare copy is at `//ROMANHOST/Raid/Dev/bare_repos/rota-code.git`. The bare copy needs its own `safe.directory` entry. Custom_AI_TUI.git needs the same entry.
- The split work ran on a clone at `D:\repos\rota-split` (not found 2026-09-16). Roman renamed the clone to `D:\repos\rota` on 2026-09-14. Before any commit, check which checkout you are in.
- The workspace is `D:\repos\rota` (Roman, 2026-09-14 ~03:00). Commit in the workspace.
- The root commit is the old e1281f5. That commit added rota_tui/HANDOFF.md (not found 2026-09-16), TESTS.md (not found 2026-09-16), and team-graph.html (not found 2026-09-16). No commit before the root commit is part of rota.
- Every SHA changed in the split. `plans/archive/commit-map-rota-split-20260914.tsv` maps old SHAs to new SHAs (363ce42 -> 7f35bd4, 400c27b -> 09891c3). A commit made in the old checkout after the split travels as a patch. That commit adds a line to the map.
- The old checkout `D:\repos\_AI\Custom_AI_TUI` did not change. Its rota/foundation branch was 304 commits ahead of origin. Only the split pushed those commits.
- The old checkout holds the only copy of the 57 GB recording history. Treat the old checkout as an archive, not as a checkout. Do not delete the old checkout.
- `plans/archive/rota-split.md` records what moved and what did not move. The record includes stash@{0} "Stop gate" of 2026-08-30. A later change superseded that stash. The split left the stash behind.
- rota no longer imports the old TUI. The sys.path insert to the repository root is removed.
- ChatMessage is in `rota/cockpit/widgets.py`. ConfirmationModal and InputModal are in `rota/cockpit/modals.py`.
- The second seat (`plans/archive/second-seat.md`) works from its own clone, `D:\repos\rota-code-seat2` on rota/seat2. The seat never pushes. The seat logs findings in `plans/second-seat-log.md` (not found 2026-09-16). The first session merges the branch.
- Line endings need no configuration. `.gitattributes` (`* text=auto eol=lf`) overrides core.autocrlf in both directions. Do not "fix" the line endings with a renormalise commit.
- The line-ending check ran on a clone at the Git for Windows default autocrlf=true. `git ls-files --eol` gave 512 i/lf and 12 i/none. No 0x0D byte was in the index or the worktree. `git status` was clean.
- Never measure line endings with `grep -c $'\r'` in the Bash tool. ANSI-C quoting does not apply in the Bash tool. The pattern is then the literal regex `r`. That pattern counts every line with the letter r. That false reading cost an hour on 2026-09-14.
- The same command returned 0 on 2026-09-16 (session 836a1517) on files full of the letter r, and a Python count of 0x0D bytes agreed. The Bash tool's quoting differs by build. Confirm a zero with Python before you trust the grep.
- Count byte 0x0D in Python, or read `git ls-files --eol`.
- `tests/rota/cassettes.db` is gitignored in the new repository. 153 LFS versions had reached 57 GB.
- `git checkout -- tests/rota/cassettes.db` no longer restores the file. `rota cassettes pull` restores the file.
- The output of a re-record exists only on disk until `rota cassettes publish` puts the output on a release. After each re-record, back up the file beside the run databases (`.rota/cassettes_backup_<date>.db`). Then announce the re-record to every peer session that works on the split.
- Never stash or checkout cassettes.db during a replay.
- cassettes.db travels as a GitHub release asset. `rota cassettes status` compares the local file with the published file. `rota cassettes publish` (needs GITHUB_TOKEN) snapshots, gzips, and uploads the file. Then the command rewrites `tests/rota/cassettes.json`. The re-record commit includes `tests/rota/cassettes.json`.
- `rota cassettes pull` never overwrites an existing file. The operator decides when to pass `--force`.
- Copy cassettes.db with the SQLite backup API, not with `cp`. A raw copy of the 590 MB file, taken while any process holds the file open, opens. Then the copy fails with "database disk image is malformed". A suite run against such a copy reports false failures (116 instead of the real count).
- `sqlite3.connect(f"file:{src}?mode=ro", uri=True).backup(dst)` takes 26 s. To verify the copy, compare `pragma quick_check` and the row counts of `cassettes` and `case_runs` against the source.
- There is no `rota/STATUS.md` (checked 2026-08-12) (not found 2026-09-16). An earlier memory claimed that the file existed.
- `rota/MAP.md` is the map (2026-09-13). The map lists what exists and what is owed, with citations to code. `rota/COMPLETION.md` is the core list and the plan. The walk diary is `plans/archive/completion-diary.md`.
- Roman ruled on 2026-09-14 that the task stack must survive a context compaction. The stack is `D:\repos\rota\plans\stack.md`. Commit the stack like every other file. Answer "Where are we" from the stack file, never from memory.
- Three compactions in two days lost the sequence of work from "is this band-aiding" through the benchmark to the harness false pass. Roman had to ask for the stack twice. A summary is not a stack.
- The stack holds the top frame first. Each frame has why, state, ends-when, waits-on, and a dated status line. A frame changes by push, pop, or a status line with the date.
- Push a frame before you start the frame. Pop the frame when "ends when" holds. Write the status line before any compaction and at every "how far are we".
- The core session (2c) owns the frames. The core session opens, orders, and closes the frames. Roman's asks are frames marked "(Roman)". Roman can pop or reorder any frame.
- Read the stack before any work. Read the stack before you ask a peer about the peer's work.
- The validation repos, in order, are oauthlib, icalendar, cnt, click. Confidence in onboarding needs a repo that the briefs were not tuned on. Measure that repo against a key written before the run.
- oauthlib is the early-era repo. The partition fixes derive from oauthlib.
- icalendar is the control. Its preregistered answer key is `rota/ANSWER_KEY_icalendar.md`. The key was written before any session ran.
- cnt is the current repo at `D:\tmp\rota-live\repo`. Its runs are `cnt_v1` and `cnt_v1_14b`.
- The click clone of 2026-08-24 is at `D:\tmp\rota-live\click`. Run `click_v0` holds the mechanical layer only. The run has 6 areas after the examples-attach fix and zero keys. The run is docs/-heavy. click is the library-shaped stressor in `rota/ASSUMPTIONS.md`.
- Preregistered keys exist for both new repos: `probes/click/answer_key.yaml` (+ questions.py) and `probes/ical/answer_key.yaml` (+ questions.py). The keys were committed before the understanding runs. `consult.py --questions probes.<repo>.questions` measures the keys.
- Both understanding runs completed 2026-08-24. The results are in the keys' recorded_run_result sections.
- click_v0: 43 sessions, 6/10 terms, 0 traps, consult 2/8 (one flat src area capped the consult score), 0/2 required constraints, pyproject none_found.
- ical_v0: 105 sessions, 8/10 terms, 0 traps, consult ~5.5/8 including the rename question from the model layer, 0/2 substantive constraints. Half the glossary is a Vale word-list area.
- Cross-repo invariants: traps 0-for-22 since v1.0.0. Furniture areas (dot-dirs, docs) produce stamped constraints on every repo. Consult strength comes from granular areas.
- Before any click or other new-repo understanding run, write the answer key cold from the source. Commit the key. Then run. That is the method of `ANSWER_KEY_icalendar.md`. First-contact findings go into `rota/ASSUMPTIONS.md`, not into scattered notes.
- clickI build nights (2026-09-10/11) use a fresh clone at `D:\repos\_AI\sample_repos\clickI`. The driver is `gauntlet_click.sh` (three sentences, yes-only principal). The `_turns` variant sets ROTA_ONESHOT= empty.
- Nine nights produced seven doors and no merge. Night 9 got all three sentences to decided items. The next layer is the Terminologist. The Terminologist writes criteria for the account against `examples/` on a big repo. That layer is a brief matter.
- Before a night, restore the click checkout. Remove `.rota/worktrees/*`. Delete `batch/*`. Run `rm -rf .rota`.
- The Node sample (2026-09-12) is `D:\repos\_AI\sample_repos\nodeI`, a two-file library `tally` with `package.json`. `npm test` = `node --test`. The sample has one inherited test file. The first commit is e3de5c9.
- The Node sample is for the second-language work (G1, `plans/greenfield-setup.md`, "Rulings and choices, 2026-09-12"). That work starts after click merges cold. Node 26 and npm 11 are installed on Windows and WSL. cargo and go are not installed.

## Hardware and drives

- Roman's box has an RTX 3080 with 10 GB VRAM and 32 GB RAM. These values are measured, not assumed.
- The box has two cards since 2026-09-12. Driver 581.80 serves both cards. The RTX 3080 has 10 GB, compute 8.6, and ~123 tok/s on llama3.1:8b alone. The GTX TITAN X, Maxwell, has 12 GB, compute 5.2, and ~27 tok/s on the same model.
- The 3080 now runs at PCIe 3 x8 (was x16). The change costs a few percent in games. No software change can correct the lane count.
- The PSU is an RM850. The 3080's limit had been raised to 370 W. With the Titan at 250 W, the total is above the PSU limit under transients.
- Set 320 W on the 3080 and 200 W on the Titan (`nvidia-smi -pl`, needs admin, resets on reboot, Afterburner to persist). The Titan draws ~115 W under inference.
- The agent can switch power modes (2026-09-12). `probes/gpu_power.ps1 -Mode install`, run once by Roman elevated, registers two scheduled tasks. Roman's account owns the tasks at the highest run level. Execute is granted on the task itself.
- Run the tasks from PowerShell, not from Git Bash. Git Bash slashes break schtasks. `Start-ScheduledTask -TaskName rota-gpu-power-game` sets 3080 370 W, Titan 150 W. `... rota-gpu-power-work` sets 3080 320 W, Titan 200 W. The switch is proven in both directions.
- When Roman says he is gaming, set game mode and pause the 3080's queue. The Titan continues to work at its floor. Limits reset on reboot. After a restart, run the work task first in any queue.
- `tests/rota/cassettes.db` (about 590 MB) is on the D: HDD. WAL is on. The file was in git LFS until the split of 2026-09-14. The file is now untracked. The file moves between checkouts as a file copy.
- `ROTA_DEV_DB` points the recorder at a copy on the SSD when the HDD is the bottleneck. Symlinks on Windows need admin. Copy the file instead.
- Corruption, 2026-09-12: the rota suite ran under WSL over `/mnt/d` (a 9p mount, no byte-range locks) while `ROTA_L1=1` recorded on Windows. The record had btree errors ("Rowid out of order", "2nd reference to page"). Every recorded session failed with "database disk image is malformed".
- Recovery on 2026-09-12: `git checkout -- tests/rota/cassettes.db`. Delete the `-wal` and `-shm`. `PRAGMA integrity_check` says ok. Re-record the lost recordings.
- SQLite locking does not cross the WSL mount. One writer and one cross-mount reader are enough to corrupt the file.
- Allow one process on cassettes.db at a time. A WSL suite run and a recorder never overlap. Before you trust a red after any overlap, run `PRAGMA integrity_check`. The check takes minutes on the HDD, so run the check in the background.
- WSL is on the HDD too (measured 2026-09-14). The Ubuntu vhdx is at `D:\wsl`. fsync rate: WSL `/tmp` and `/root` 6 per second, Windows `D:` 13, Windows `C:` 279, WSL `/dev/shm` 216 000.
- The rota suite on WSL waited 22 minutes in ext4 journal waits with 16 workers idle. No code in the repo sets `TMPDIR` (observed: a grep of every `.py` file, frame 30's design review, 2026-09-17; the earlier claim that `tests/rota/conftest.py` sets `TMPDIR=/dev/shm` was stale). The git fixture's guard follows `tempfile.gettempdir()`, which reads `TMPDIR`, `TEMP`, `TMP` in that order. Export all three to move the suite's temp root. `--basetemp` alone breaks the guard. `rota/tools/gate.py` does this through one setting, `ROTA_GATE_TMP`, in the Windows form `C:/...`.
- A `rota run` under WSL writes its database at 6 fsyncs a second. Put `ROTA_HOME` on `/dev/shm` for a throwaway run, or run on Windows.
- A guessed ROTA_DEV_DB creates a new database with no warning (2026-09-14). The register is `tests/rota/cassettes.db` (`rota/paths.py`), not `.rota/cassettes.db`. A Titan chain run with `ROTA_DEV_DB=.rota/cassettes.db` recorded four cases into a fresh empty file. The peer saw an unchanged pack checksum.
- Never set `ROTA_DEV_DB` unless the variable names a copy that you made on purpose. The merge back was by rows. Keys shared with an older load kept the old completions. The moved case still needed a `ROTA_REFRESH=1` re-record.
- A night on the SSD (2026-09-15): onboarding showed no GPU use for minutes. The click checkout restore, the worktree add, the index, and the run database's WAL were all on D:. Roman ruled: move those four items for the next night.
- `ROTA_RUNS=C:/Users/roman/rota_night/state` moves the runs directory (run db, warm snapshot, live file, rota/paths.py RUNS). `CLICK_ROOT=C:/Users/roman/rota_night/clickI` moves the sample checkout (a clone of the D: checkout). The warm snapshot is in the runs directory. The first night in a new runs directory is cold.

## Models and Ollama

- `llama3.1:8b` was the only viable local model for the test suites at the first measurement. The model is 4.9 GB, has a 0.2s warm round-trip, and fits entirely in VRAM at `num_ctx=12288`. The model is now only the code default.
- An early measurement ruled out two models. `qwen3.5:9b` has native tool calling but spills ~27% to CPU once its KV cache is allocated. The model then takes >100s per turn. `gemma4:31b` needs ~20 GB and swaps until the machine stops responding.
- Since the 2026-08-25 bakeoff (probes/bench/), `qwen3:8b` with `think: false` is the understanding engine. The flag goes in the ollama payload in rota/llm/llm.py. The `/no_think` prompt prefix does NOT work.
- qwen3:8b: 5.2 GB, fits fully, ~12.5 s/turn, frame 34/38, define 12/12. The model ran the full nine-stage click spine in 11 min. The 14B took 2.5 h. Without think:false the model decodes at 0.1 tok/s and scores 0 on frame. That result is thinking contamination, not model quality.
- `qwen2.5:14b-instruct-q3_K_M` (75% GPU, 153 s/turn) keeps judgement parity. The model stays only for cross-family reads. `gemma3:12b` is the frame-specialist reserve (36/38).
- The practical budget is ~8 GB, not 10. The desktop takes ~2 GB. Only ≤5.2 GB models fit fully at 12k context. A model swap costs a reload in each direction. Queue GPU work serially.
- Never unload an Ollama model with a request that names the model. `/api/generate` loads the model to serve the request. That includes a request whose only purpose is `keep_alive: 0`. An eviction attempt then reloads 26 GB. Kill the runner process instead (`Get-Process ollama`, then stop the large process), or run `ollama stop`.
- A leftover client with an open connection makes Ollama reload the model immediately after the runner is killed. Before you conclude that the model is stuck, check for stray processes connected to port 11434.
- Fit table, 2026-09-09 (RTX 3080, 10 GB, walks at num_ctx 12288, about 1 GB of cache): qwen3.5:4b 3.4 GB fits with room. qwen3.5:9b 6.6 GB fits. qwen2.5:14b 9.0 GB spills a little. That model runs 40–90 s/turn.
- qwen3.5:27b 17 GB and qwen3.6:27b 18 GB overflow by ~8 GB. Those models would run minutes per turn. Roman asked about 3.5-4B and 3.6-27B. qwen3.5:4b and qwen3.5:9b are pulled as the candidate mechanical tier and judgement tier.
- `model_routing` takes `role=model` pairs since e6e2435.
- The register replays under qwen3:8b. The default model is not qwen3:8b (2026-09-14). `tests/rota/test_l1.py` takes the model from `ROTA_MODEL`, default `llama3.1:8b`. By 2026-09-14 the newest recording for 78 of 101 L1 cases was qwen3:8b (2635 of the last 3000 case_runs).
- A shell without `ROTA_MODEL=qwen3:8b` replays the wrong model. That shell reads about 80 cases as `STALE: no recording for the current prompt`. That message says "prompt changed", not "wrong model". The message looked like a split regression for an hour. Peer sessions carry the variable. A fresh shell does not carry the variable.
- Keep `ROTA_MODEL=qwen3:8b` for every suite run. A gate full of `STALE` is usually the wrong model, not the split. Before you call a case STALE, check `select model, max(rowid) from case_runs group by model` against the pins that the shell produces.
- The Critic's lever (2026-09-12): gemma3:12b (8.1 GB) passes every Critic register case 5/5 on one load. That includes `CR-a-test-that-encodes-nothing`, which is red on every 8B and on qwen2.5:14b-q3. The Developer score of gemma3:12b is 0.5. Only the Critic's desk moves to gemma3:12b: profile `local-gemma-critic`.
- On a 10 GB card the Critic's turns swap the resident model. On the Titan the Critic recorded at ~15 tok/s. A different model, not a bigger model, was the lever.
- Ollama halves num_ctx by default (found 2026-09-15, finding 79). With OLLAMA_NUM_PARALLEL unset the server runs two slots and splits num_ctx between the slots. A profile's 12288 is then 6146 per request. Ollama cuts a longer prompt from the front. The brief is lost first, and the model answers as a generic assistant.
- The sign is `truncating input prompt limit=6146 prompt=...` in %LOCALAPPDATA%\Ollama\server.log (208 times between 2026-09-12 and 2026-09-15). The fix is OLLAMA_NUM_PARALLEL=1 as a user environment variable (set 2026-09-15 04:10, the app restarted) and in probes/titan_ollama.ps1. Read that log line before you blame a looping session on the model or the brief.
- The Ollama Vulkan backend ignores `CUDA_VISIBLE_DEVICES`. The backend put models on the Titan regardless of the CUDA filter. The main server once spread one model across both cards and failed with "CUDA error: the launch timed out".
- User env `CUDA_VISIBLE_DEVICES=<3080 UUID>` and `OLLAMA_VULKAN=0` (setx) pin the tray app's server (port 11434) to the 3080. `probes/titan_ollama.ps1` starts a second `ollama serve` on 127.0.0.1:11435 bound to the Titan's UUID. UUIDs come from `nvidia-smi -L`. The numeric index is not stable across the two enumerations.
- Stray `llama-server.exe` runners survive a killed server and hold the card. Kill the runners by name before you restart the server.
- The register recorder goes to the Titan with `OLLAMA_HOST=http://127.0.0.1:11435` (the recorder reads the variable, no code change). A click night runs on the 3080 through the default port. That split doubles the output of a day.
- "One GPU, never a walk alongside a recorder" is now "one card each". Do not use the Ollama cross-card spread for a 30B judge on Maxwell until a measurement exists. The CUDA runner accepts compute 5.2 but timed out when spread.
- Hang, 2026-09-12 evening: a qwen3.5:9b generation on the Titan ran 25+ minutes at 95% utilisation, and no turn completed. The turn was the seat exchange's Developer at its fourth fix attempt. `ollama stop <model>` on port 11435 freed the Titan.
- Maxwell with an 8192-token cap can spend one reply on the whole cap at ~20 tok/s. Once the reply never returned. A driver on the Titan needs a per-request timeout shorter than the profile's 300 s, or a lower `max_tokens` pin for that card.
- The 3080 hangs too (night 27, 2026-09-12): a qwen3.5:9b Developer turn held the fast card at 83% for two hours, and no turn completed. That hang is not a Maxwell fault. The socket timeout never fired, because the stream sent a few bytes at a time.
- `_consume_stream` now has a wall-clock deadline equal to the backend timeout. The session then sees "no answer in 300s". If a card stays at high utilisation and the run's `turns` count does not change for more than five minutes, run `ollama stop <model>` on that server. That command frees the card.
- The deadline was not enough. tipsAZ (2026-09-13) hung seven hours in one Tester turn with the deadline in place. The wait was outside the chunk loop. Since 4715b23 a daemon `Timer` in `OllamaBackend` shuts the response socket at twice the timeout from another thread (`resp.fp.raw._sock.shutdown(2)`).
- The real cause (2026-09-13, night 31 + tipsBA, both cards) was not a hang. A reply ran to the 8192-token cap with no call. The runner's cut-note path raised `UnboundLocalError`. The session failed uncommitted.
- The loop re-dispatched the same message wake 69 times at 90 s each. The message attempt cap ran only at boot. a8ce330 fixed the cap.
- Diagnose a "hang" with `py-spy dump --pid` on the walk python and with the Ollama server.log, not with utilisation alone. `sim = 1.000` on repeated `task` lines in the log means that the client re-sent the same prompt.
- Titan timeout (2026-09-13): at 27 tok/s a cap-length reply (8192 tokens) takes five minutes. The 300 s default times out every such turn. tipsBB and tipsBC each lost three Tester turns to the timeout. `OllamaBackend` reads `ROTA_LLM_TIMEOUT` (b442e2e). Titan walk scripts export the variable as 900. The register recorder passes `timeout=300` explicitly, so the variable does not affect the recorder.
- The Titan can hang (2026-09-15 05:46). A kill of every ollama.exe process, done to restart the 3080's app, stopped the Titan's `ollama serve` in the middle of a run. The Titan restarted at one slot with the full 12288 window.
- Every request then failed with `CUDA error: the launch timed out and was terminated`. Even a six-token prompt at two slots failed, with the card cool and idle. That failure is a hung context under WDDM. A reboot is the fix.
- Two rules follow from that hang. Stop only the 3080's server (its parent is `ollama app.exe`, the Titan's parent is powershell). Keep the Titan at `-Parallel 2` (probes/titan_ollama.ps1 default). The Titan's register prompts are short, and the runner flags a cut prompt.
- Both servers can be down after an idle day (2026-09-15 23:48). Night 81 failed its onboarding on "no ollama at localhost:11434". The night script's ollama_up restart runs only after the onboarding step.
- Before a night or a re-record, curl both /api/tags. Start the 3080's server with `Start-Process ollama -ArgumentList serve -WindowStyle Hidden`. Start the Titan's server with `powershell -File probes/titan_ollama.ps1`.

## Running rota

- `python -m rota` is the only entry point (added 2026-08-19). A run is a named database in `<repo>/.rota/<name>.db`. The run records its checkout in `config.project_root`. Every verb takes the name and derives the rest from the database.
- The verbs are `rota ls | onboard <name> --root <checkout> | run | tui | cockpit | report | wipe`. Two runs against one checkout are two names, not two wipes. A comparison of a branch against its main needs two names.
- In the TUI (the seat): `alt+p` run/pause, `alt+r` wipe-and-reindex, `alt+w` wipe, `alt+b` cockpit on the current run. Bindings are `alt+` and never `ctrl+`. The Input widget holds focus, and the widget's bindings win. `ctrl+w` is the widget's delete-word. The footer shows a captured binding, and no action performs the binding (`test_every_binding_survives_the_input_having_focus` guards this rule).
- Inspect with the cockpit, not with a SQLite browser. The three useful questions are not rows. Keep a SQL prompt beside the cockpit for ad-hoc queries only.
- Idle or stuck: read `frontier`/`outstanding` (computed). What the role was shown: read the built prompt (`/prompts.json`). Why did this happen: read the `cause_id` chain.
- Wipe is a command, never `rm`. A worktree is in the target project. The only proof that the worktree is ours is a row in the database. A spawned process has the same shape. The WAL survives the file.
- `lifecycle.start` creates worktrees at dispatch. A role never creates a worktree. An onboarding-only run has no worktree.
- Old runs in `.rota/` are usually behind the schema and cannot open. `ls` says `stale` and gives the reason. The runs are not migrated on purpose. Databases here are throwaway, and `init_db` rebuilds them at boot.
- Run databases from before 2026-09-16 (the `refs` relation, code through 056995d) open read-only in the cockpit and refuse a run. `init_db` refuses a database whose owner tables still carry a `provenance` column, with a sentence that says to start a fresh run. The warm snapshot `.rota/clickI_warm.db` is re-created the same day.
- Profiles (2026-09-09): `rota profile list|show|check|set`, `rota onboard <run> --root <dir> --profile <name>`, `rota run <run> --model M --role tester=M`.
- A profile is a TOML file in `<project>/.rota/profiles/` (not found 2026-09-16), `~/.rota/profiles/` (`ROTA_HOME`) (not found 2026-09-16), or `rota/llm/profiles/`. The shipped `local` profile has qwen3:8b as the default and the four judging desks on qwen3.5:9b.
- Onboarding binds the profile into config `profile`. `model_routing` derives from the profile. The walk driver's manual `config.set(... "model_routing" ...)` is the old method.
- `probes/gauntlet_click.sh` on rota/foundation still defaults `REPO` to the old checkout. Export `ROTA_REPO=D:/repos/rota` for a night.
- The Bash tool's shell has the old checkout's venv on PATH and in VIRTUAL_ENV. To run the new venv, prefix PATH in POSIX form: `PATH="/d/repos/rota/.venv/Scripts:$PATH" VIRTUAL_ENV="D:\repos\rota\.venv"`.
- The shell ignores a Windows-form prefix (D:/repos/...). The old python then runs the new code (night 47's first launch, 2026-09-14). After a launch, check the process's command line.
- A night ends at GAUNTLET-DONE, not at Stuck (2026-09-14). The gauntlet script runs sentence three after sentence two sticks. Before you launch the next night, wait for the GAUNTLET-DONE line or kill the night.
- Night 67 launched on the Stuck line while night 66's sentence three still wrote .rota/clickI.db and the click checkout. The restore during that write gave a foreign-key failure and a contaminated start.
- In rota a broken hop and a working hop produce the same observable output: a committed session and a well-formed message (measured 2026-08-26). Three of the five faults found that day were invisible from every surface except the per-turn transcript. Each fault had existed for months behind a system that looked green.
- An `ask` sent with `refs=[]` woke an owner with an empty inbox. The owner still sent a well-formed `answer` from memory.
- Refs that named a transcript entry resolved to nothing (`_resolve_refs` had no `entries` row). Again the owner sent a well-formed `answer` from memory.
- A stray `converse` made the commit path discard every statement the session had written: `sessions.committed = 1`, `receipts` empty.
- When a rota hop looks like it works, check the result that the hop was for, not that the hop happened. `SELECT seq, user, completion FROM turns WHERE session_id = ?` is the only view that shows what the model received and what the model said. `messages` and `sessions.committed` agree with you in both cases.
- Check `receipts` against the writes that you expected. Empty `receipts` on a committed session means that something dropped the writes.
- The same property makes cases lie. `L3-a-maintainers-question-reaches-the-owner` passed while the question reached nobody. The case asserted that an answer was sent, not that the answer named anything. Assert on refs into the artefact that the role owns. That assertion is the difference between "it replied" and "it replied from somewhere".
- Never let a fixture give a message and its entry matching ids. `entry_for` looks up `e_{message_id}` and matches by accident. That accident hides exactly this class of bug.
- Night 31 (2026-09-13) was the worst case of this shape. A session that raised (`UnboundLocalError` on the first-iteration cut-note path) was never written at all. The run looked frozen with the card at full load. The loop re-dispatched the same wake 69 times.
- Since 2026-09-13 a failed session leaves a `sessions` row with `committed = 0` and its error as the last `turns` row (`db.session_fail`). Wake gates that ask "did a session already run for this" filter `committed = 1`. The message attempt cap runs in `loop.step` after a failed session, not only at boot.
- `probes/walk.py` prints `FAILED <wake>: <error>` flushed. The script stops after 30 min with no committed session. Diagnose a frozen run with `py-spy dump --pid` on the walk python and with `sim = 1.000` repeats in the Ollama server.log, never with utilisation alone.
- The pylint check used-before-assignment does not catch the loop-scoped pattern that caused night 31. The test with a scripted backend catches the pattern.
- The last turn's refusals are invisible (2026-09-13). A session's refusals are in the next turn's prompt. A session that ends immediately after a turn of refused calls (turns=1, receipts empty, committed=1) shows no ERROR line in `probes/wake_dump.py`.
- Night 43's reconcile sessions looked clean, and every call was refused. Read `receipts` for the session. Empty receipts after write calls mean refusals. Replay the session in a sandbox to see the refusals.

## The register and measurement

- The live failure list comes from the `case_runs` table in `tests/rota/cassettes.db`. The query is `SELECT case_id, COUNT(*) runs, SUM(passed) p, MAX(seq) s FROM case_runs GROUP BY case_id, model, prompt_hash ORDER BY s DESC`.
- Group by `(model, prompt_hash)` and keep the newest group per case. `pass_rate_history()` in `rota/llm/cassettes.py` does the same.
- `problems` and `transcript` on each row hold the failure reason and the role's actual tool calls. Those columns separate a bad brief from a broken fixture without a re-run.
- A new derivation of the failure list costs a full live suite run against the local model. The table has every recorded run, including the transcripts. Query the table before you run anything.
- A `0/N` is a different kind of result from a low pass rate. 0 usually means that the case is impossible as fixtured, not that the role is unreliable. Open the transcript first.
- Live pass/fail is the `case_runs` table, never a status line in a document (2026-09-13).
- Ollama at temperature 0 is deterministic within a model load, and not across two loads. A bench score is a fact about a load, not only about a model. The llama.cpp batching/KV layout and the model that was resident before both move the score.
- The measurement of 2026-08-26 used the challenge battery with the identical prompt, byte for byte, same model, same pins. `llama3.1:8b` scored 3 of 4 in one process and 1 of 4 in another process an hour later. Three repeats inside each process were identical every time.
- Never compare numbers taken in different runs. Any A/B over prompts or names must interleave its arms in one process on one loaded model. Run the whole set twice to show that the result replicated. `scratchpad/ab_replicate.py` (not found 2026-09-16) is the shape.
- Wide gaps survive the drift (frame 34/38 vs 5/38 is real). Narrow gaps do not survive. A 4-item battery moved 2 items across loads. `challenge 2/3` vs `3/3` in the bakeoff table ranks nothing.
- Grow small batteries before you read them. Prefer a name/format that scores the same under every load over a name/format that scores well once.
- `probes/bench/run.py` evicts between candidates. That eviction does not make the columns comparable. Each model is measured under its own fresh load.
- Register evidence, 2026-09-09, from `case_runs.load_id`. Ollama 0.33.3 was unchanged since Aug 30. The app server and a manual `ollama serve` were both tried. `L1-VK-the-account-before-the-behaviours` passed 20/20 on load `@248394` and 0/45 on `@248459` + `@248460`. `L1-DV-fix-what-the-verdict-names` was green on 18 loads and red on `@248383` and `@248460`, with the same briefs and the same prompts.
- The manual server on 127.0.0.1:11434 was stopped on 2026-09-09. The app's server on 0.0.0.0:11434 stays.
- Boundary cases flip per load. The red signature is one shape: the model re-reads until the verbatim-repeat guard ends the session. The six to eight register reds of 2026-09-09 are this shape, not code. A runner-transcript nudge against the shape changed behaviour on passing cases. The nudge was reverted.
- Record every case on ONE load for comparable numbers. Never attribute a flip to a brief without a second load. Never edit runner transcript text without a register run first.
- `case_runs.load_id` is the column that answers "which load". An empty `load_id` is a pre-September recording.
- `L1-LI-present-the-touch` was red 0/5 on three models for a week. The list called the case a judgement boundary. The predicate wakes the Liaison with `refs=(batch, item)`. The case had no `refs:`. The prompt showed no `Refs:` line. The brief's "copy the two ids" had nothing to copy.
- With the predicate's refs in the case, `L1-LI-present-the-touch` is 5/5 on both Liaison models (2026-09-12). A register case's wake must carry what the predicate's wake carries (refs, detail). A wake that the system never produces measures nothing. Then "red on every model" reads as a model boundary when the fixture is the cause.
- Before you author or attribute a tick case, read the predicate that produces the wake. Copy the predicate's `refs` and `detail` shape into the case. Before you call a red a boundary, render the case's prompt. Check that the wake lines match the lines of a real run.
- A STALE case (no cassette for the current prompt) renders identically to a red under `--tb=no`. Classify stale-vs-red before you read a baseline.
- `python -m rota.tools.gate` does that classification (frame 30, 2026-09-17). It runs the suite with `--tb=no -rfE -q`, prints five lines (summary, new reds, reds gone, the stale set under the suite's model, time), stores the baseline in `.rota-gate.json` at the repo root, and re-runs new reds only for their tracebacks. Never read `.rota-gate.log`. `--baseline` re-takes the baseline. A checkout with no register gets `stale: the register is absent`. Four runs on this box: 465 s to 482 s.

Cost anchors (frame 28, written 2026-09-17 from frames 26 and 30; re-derive from the last three frames whenever a frame that changes the workflow closes). Meta workflow. Every row is observed from the harness usage line under an Agent result, never from the agent's own estimate.

- Agent floors, one trivial task each: general-purpose on Opus 38.3k; implementer 11.4k; reviewer 13.3k; sweeper 8.9k (frame 26).
- A reviewer on Opus with no tool call, a three-line answer: 9.6k (frame 29's probe). The Agent tool fixes the type list at session start and reads a type's body at each spawn, so an edit to a definition is live without a restart (observed: the probe quoted a command line that e407e5d added after this session started).
- A reviewer pass on Opus, cold, six to eight numbered points with probes: 69k to 76k. A resumed second look on the fix commit: 18k (frame 30).
- An implementer pass on Opus, cold, two new files of about 300 lines and one suite run: 74k. Resumed: 7k for a docstring and three lines with one test; 40k for six fixes and ten tests (frame 30).
- A suite run read inside an agent as raw pytest output: about 25k (frame 21). Through the gate: about 1k in the agent; about 6k of the assistant's context per run, call included; 8 minutes wall (frame 30).
- A tool frame in the assistant's own context, claim to close, two reviews and three implementer passes included: about 120k (frame 30; observed: `/context` 173k at close with a 45k fixed prompt).
- A design record written by the assistant: about 8k of output. A status line: about 1k (frame 30).

## The cockpit

- One writer per state axis (2026-08-24): the lens changes only through `setLens()` in graphview.js. `setLens()` clears `GV.blast` and closes the case (`GV.caseId`, moved out of panels.js's old `CASE_ID`). `setLens()` opens the lens's home subtab (story/run → steps, coverage → coverage, design/case → none).
- Do not set `GV.source` directly from new code.
- Stage listeners attach once in `gvWireStage()`. `gvControls()` is rebuilt freely and must never touch `window`/`document` listeners. Before that rule, the listeners accumulated, and wheel zoom compounded with each settings click.
- Layouts are plural. `layout.json` is `main`. Other layouts are in `rota/design/layouts/<name>.json` through `GET/POST /layout.json?name=` + `/layouts.json`. The client generates `auto: flow/grid/force`. Those layouts own no file until saved-as.
- `placeStrays` parks the nodes that a layout omits. Those nodes do not vanish.
- Layout files are excluded on purpose from `source_fingerprint()` and the watchfiles filter (`is_layout_file`). Before that exclusion, every "save layout" reloaded the page and restarted the server under the page. Do not remove that exclusion to "simplify" the code.
- The provenance "WHAT IT WAS SHOWN" prefers recorded `turns` (verbatim) over the rebuilt brief. `provenance_check.js` picks its fifth needle by whether the session recorded turns.
- Dropdowns are the custom `dd()` component (graphview.js), not native selects. Callers write the `<div class="dd" id="...">` wrapper with the id literal in source. `test_every_element_the_scripts_write_to_exists` reads source text and cannot see interpolated ids. The layout dropdown carries per-row deletes and a "+ add layout…" action row.
- The inspector panel starts collapsed by contract (`PANEL` in panels.js). `showTab(t, quiet)` has the quiet flag. With the flag, the localStorage tab restore does not open the panel at load. Only the width persists, never the open-state.
- The key is at the bottom left. The legend is mode-aware (chat has its own legend).
- Pill states (2026-08-26): QUIESCENT / WORK PENDING / NO RUNNER / STUCK. STUCK requires a held claim plus stillness. Frontier-nonempty + still + no claim is NO RUNNER. In that state no process runs the db. The fix is `rota run`, not a debugger.
- Claims carry no pid in the current schema. Presence is the whole signal. Stillness is server-side `quiet_secs` = seconds since the newer of db/-wal mtime (never -shm, because readers touch -shm). Thresholds are 30s (NO RUNNER) and 180s (STUCK). The STUCK threshold covers two slow 90s local turns.
- The schema gate (`prepare_db`, `_switch_run`) runs `init_db` only when the read-only drift check finds a missing item. An unconditional init_db stamps the WAL. That stamp resets the clock that the pill reads.
- Coverage bars use `gradeColor` (stop→warn→ok ramp anchored to the palette). Milestone bars stay two-tone on purpose. Early planned work is not a fault.
- The cable (owner's judgement, 2026-08-26): a role↔artefact pair can carry both a read and a write. Such a pair draws as ONE connection of two strands at every zoom. Each strand is ±2.2px and keeps its kind's colour/dash/head/label/click. This rule amends the old "never fold across types" note. The strands keep the intent of the old note.
- A pair that carries exactly one line (both directions counted) draws straight, never bowed. `lens_check` asserts both cable rules.
- A lint bans `.title =` in panels.js. Use `setAttribute('title', …)`.
- Visual preferences (2026-08-24): sober, low radii, 2–4px on chrome, no pill capsules. Use larger rounding only where the shape carries meaning (the principal's stadium). Newcomers are smart. Give orientation, not instruction.
- There is no node search. The URL is the query (`#/graph?lens=…&node=…`, written through `syncHash`/`applyHash` in panels.js).
- No row timestamps ever (law 13). Rows carry order, not wall time. Time appears only where the OS records time (run-file mtimes in the header run selector).
- The run selector is the header `#rundb` dropdown. `GET /runs.json` lists sibling `.db`s newest-first. `POST /run?name=` switches the served run in place (schema-drift → 409).
- `rota cockpit` with no name delegates to the server's chooser. The chooser picks the newest run that opens. The chooser skips behind-schema siblings by name and does not refuse them. The schema moves under runs when parallel work edits schema.sql.
- The design direction is in `plans/cockpit-presentation.md` and the "Glass Cockpit" artifact.
- Verify with `node tests/rota/lens_check.js` (needs a cockpit serving). The script also checks the three layout generators and placeStrays. `node tests/rota/provenance_check.js <table> <row>` verifies provenance on a row that exists.
- Run `node tests/rota/lens_check.js` before you claim that a cockpit change works. The script reports how many edges each lens lights, in what states, and whether every key row resolves to an element. A green `node --check` is necessary and not sufficient for a viewer change.
- The coverage lens "looked broken" three separate times while the logic under the lens was correct. The faults were no positive mark, then a halo too faint to see, then key rows that resolved to nothing. A read of the code proved nothing every time.
- A scripted edit once shipped a call to a function that had never been written. `node --check` passes that call. Only the lens check caught the call.
- Assert that the anchor matched before any scripted `str.replace` on source. One session had three silent no-ops. One of the no-ops was that broken reference.

## Rulings on briefs and doors

- Roman ruled prompts over guards. No rule bounds an LLM judgement. On 2026-09-02, after ~35 S0 walks and ~30 guards, Roman said: "these deterministic checks I'm not so sure about their quality, the system prompt is where the real work is I believe".
- Earlier Roman said "slicing should be an intelligent LLM operation" (no rule bounds tickets). Roman also said "I'm not sure a deterministic guard is able to fix this" (the criterion-word detector, reverted).
- The walks showed that every judgement-shaped guard regressed a register case or gained nothing. The mutation probe showed that the loop-level tests do not notice when guards vanish. The model sees only the brief.
- Prompt structure (headline act, worked example, no escape hatch) moved the 8B. Fences did not move the 8B.
- Before you add a guard, ask whether the brief's structure can carry the rule. Prefer the brief unless the rule is a fact about the harness (stdin, imports, stale runs) or state semantics. Do not bound LLM judgements (slicing, triage, review) by rule.
- Measure brief changes with the register case that owns the behaviour plus a cold walk.
- The shared prose is every desk's prompt (2026-09-12). One sentence added to the runner's tool-format prose (teaching the `text=[text]` block form) changed the hash of every mode.
- The measurement of the same day: that sentence took the Terminologist's survey case from 770/780 to 0/20 on llama and 0/5 on qwen3.5:9b. No call ever used the form. The sentence was reverted.
- A change to the format prose of `runner.py` is a brief change on eight desks at once. The change owes a re-record of the whole register, not only of the mode the change was written for. The parser's refusal is the place for a transport hint.
- A door unblocked each of the Level 1 walks tipsJ..tipsS (2026-09-09). Each door holds a fact that an 8B model cannot see and that Python enforces silently. The facts are all in `api.py`.
- Doors of 2026-09-09, in `code.write`: a whole-file write drops a name that the tests, the criteria's surfaces, or other files import. A file defines one name twice, and Python keeps the last definition. An entry point loses its `__main__` guard.
- Also in `code.write`: the Developer writes a test file. The harness runs the database's copy. The merge carries the file.
- More doors of 2026-09-09: a surface ref `path::name` compared whole against bare call names (`tests.encode`). A test named as a surface (`criteria.specify`). A ledger row about a ledger row, or a rota row under another table's name (`ledger.log`).
- More doors of 2026-09-09: a frame ruling's body is `reason`. The frame cites paths that the frame need not open (`surveys.attest`). A claim that cites nothing, because the load is the reading (`challenge.load`). The Critic's ledger id over 64 chars (`_challenge_ledger_id`).
- More doors of 2026-09-09: a merged batch is done (`tests_missing`). A batch with no worktree cannot be written to (`_batch_worktree`). A stale worktree at a new batch's path.
- Before you write a door, ask: would this door refuse a correct act by a stronger model? If yes, the check is a judgement. A judgement belongs in the brief and is measured on the register.
- If the check names a state of the file or the database that is wrong under every model, the check is a door. The door's message names the exact call that passes.
- A refusal that names one argument at a time makes an 8B model flip between two fixes (criteria id / ticket id). Name both arguments in one message.
- Read a quarantined session's refusals in the next turn's `user` text. A single-turn session stores no refusals.
- Doors added 2026-09-10/11 (the merge re-earned, tipsAP): the fence (`core/fence.py`, reaches and dependency manifests). A root file may not carry a stdlib name. Criteria go to the wake's item.
- More doors of 2026-09-10/11: the surface must name the callable that the item names in words (`_surface_names_what_the_item_names`). Constraint zero (k0) cannot be violated. An empty commit under a finding names the signature drift.
- More doors of 2026-09-10/11: an escalation over a removed or drifted name is refused. A deliver waits for onboarding. An assert that replaces the account's words is refused.
- More doors of 2026-09-10/11: a running batch with no commit re-owes its start. A quoted word in a clarify is a word. A new batch never inherits an old run's branch.
- More doors of 2026-09-10/11: git runs with hooks off. A batch commit excludes `.venv` and `.rota`. Each door is a fact about files, the index, or the database.
- Doors of 2026-09-12 (all facts, no judgement): the 2048-token output cap cut a whole-file write. The parser called the cut a quote error. Now the cap is 8192. The runner names a cut reply. `code.write` takes the span that `code.source` showed.
- More doors of 2026-09-12: a quote inside quoted source swallowed the next argument. The parser now names the quote and the `text=[text]` block form. The runner derived a converse session's entry by name `e_<msg>`. The runner now uses the message's own ref.
- More doors of 2026-09-12: a page to the principal carries at most seven open assumptions (`sandbox.PAGE_ASSUMPTIONS`, and the brief chooses which seven). A `reopen` needs the item's version above its approval. The drops-definitions refusal names the appending span `start=N, end=N`.
- More doors of 2026-09-12: reconcile wakes once per prose file (`@prose:<path>`).
- On 2026-09-12 the ruled Critic review order and a brief sentence that teaches the block form both measured worse on 8B. Both were reverted. Doors held. Prose did not hold.
- When you add a guard to rota's sandbox or ops, look for existing guards that key on the same signal. Make the guards agree. Guards run in binder-then-op order. A refusal's repair text is an instruction that the model follows literally. Two guards on one signal that disagree turn the first guard into a lesson on how to evade the second guard.
- Measured 2026-09-01: the cross-table id guard (Law 14) fired first on a Vision Keeper that passed an item's id as a decision id. The guard's hint said "prefix it with what it is". The model did so: `c_` + item id. The older "minuting your own edit" guard, keyed on id equality, no longer matched.
- A case green across five loads went 0/5. The cause was a hint, not a model. After any guard, re-record L1+L3 before you accept the guard. Read the per-load history of every case that flips (case_runs, grouped by load_id) before you attribute the flip to the model.
- Key semantic guards on the subject (the row written this session) rather than on the literal id. Make a collision hint say what the collision means when the colliding row is the session's own write.
- A guard inferred from one transcript can be a wall elsewhere (2026-09-02). Two walk-era guards each sent a green register case 5/5 -> 0/5. Neither guard gained the case that the guard was written for. One guard scoped the post-send notice away from build modes. One guard redirected a challenge that quotes a test to the Tester.
- If a guard's distinction is not mechanical in every mode where the guard fires, the guard is a hidden judgement. Leave the judgement to the desk. At review the tests are green by construction.
- Third instance, 2026-09-02 (responsibility audit): the verdict-after-challenge guard sent `CR-fail-names-its-criterion` 0/5. The model produced the correct fail-naming-its-criterion verdict four times. The guard refused each verdict. The model had first called `msg.challenge_developer`, a tool in review's namespace that no brief sentence governs.
- The compound shape is unguided tool + sequencing guard = mode locked out of its required act (findings P10/P11 in plans/archive/responsibility-audit.md).
- A brief that closes on an unconditional escape hatch scores ~7% median. Every other ending style scores ~80%. The measurement (2026-08-12) covered 60 L1/L2/L3 cases, grouped by the ending of the mode brief's final paragraph.
- Terminal ending ("one submit, then stop"): 9 cases, mean 81%, median 83%. Prohibition ending ("do not ..."): 9 cases, mean 75%, median 80%.
- Ordinary action ending: 34 cases, mean 67%, median 76%. Unconditional escape hatch: 8 cases, mean 31%, median 7%.
- An escape hatch is a closing "if it is none of those, hand it on / ask / escalate on". Examples: `architect/escalate.md`, `developer/answer.md`, `vision_keeper/contested.md`.
- Treat the escape-hatch result as a lead, not as a result. The broader claim "the last paragraph becomes the default action" is disconfirmed. Prohibition endings score well. With role held constant, the effect reverses in places. The Architect's escape-hatch brief beats the Architect's other briefs (64% vs 57%).
- Liaison's two cases at 5.6% carry almost the whole headline number. A separate finding showed that the tick-wake harness bug starved those two cases, not their ending.
- Read the brief's last paragraph early when a case is near 0 and the transcript shows a reasonable act that was not asked. Rule out a starved fixture first. The two clearest "escape hatch" failures were starved fixtures.
- The sharper signal from the same table is per-role: developer 50%, tester 39%, researcher 33%, against terminologist 78% and liaison 94%.
- The reverse also fails (2026-09-09). `architect/boundary.md` ends on `none_found` as the last sentence. The Architect on a live walk never took that exit (pyproject.toml, three sessions, quarantine). A move of the none_found decision to the front took the register case from 5/5 to 0/5 on the same load, interleaved.
- With the exit first, llama3.1:8b amended five times and never attested. The change was reverted. A first-paragraph exit is not a cure for a last-paragraph exit. The live failure was qwen3:8b, and the register is llama3.1:8b. The lever for the walk is unmeasured.
- A tool added to a mode's `.tools` file changes what the model does on the plain case. Three measurements, all 5/5 on one load, show the same shape.
- `decisions.author` added to Vision Keeper relay: the plain relay wrote 14 decisions. Relay tools added to Terminologist relay: adopt wrote 2 rows (reverted).
- Relay tools added to Liaison `converse` for the "answering a clarify" branch (2026-09-09): qwen3:8b relayed a plain question to the Vision Keeper. G1 went 10/10 to 0/5.
- The fix was a new mode `answering`, keyed in `runner._mode_key` on the cause verb (`converse` caused by `clarify`). `verdict_signoff` and `batch_start`-from-`elect` are keyed the same way.
- An 8B model reads the tool list as the list of what this session is for. A tool that only one branch needs invites use on every other branch.
- When a brief gains an "if X is in the message" branch that needs tools the mode does not have, do not add the tools. Add a mode: brief, `.tools`, `_mode_key` branch, an `obligations.py` line, and a register case with `prompt: <mode>` (test_edge_coverage demands the case). Re-earn the old mode's cases after the split.
- A bare id in the prompt carries no table. The owner is a fact about the table. Resolve the rows that the brief must route on (`about_rows` with `table`). Do not list owners in the brief.
- Read what the model sent before you trust any number about the model. The missing item is a fact or a judgement. A fact becomes a tool result. A judgement becomes a measurement that you bring with a proposed wording. (Agreed with Roman, 2026-09-15.)
- Roman's rule: the model's capability is sound until disproven. The model is the last suspect, not an innocent one. On 2026-09-14/15 the instrument, the wake, the brief, and a mode's tool list were each wrong before the model. The model was never wrong.
- Disproof has a shape. The facts are in front of the model. The wording is measured. The load is the same. No run does the act.
- Finding 79 (2026-09-15): four nights of a looping Developer were sessions whose brief the server had cut (Ollama halves num_ctx across two slots). The instrument was the wall. The model was never the wall. Twice Roman had to propose the spike himself.
- Three times in one hour on 2026-09-15 a score lied while the transcript was clear. source_refs held reference ids, not lines. The harness could not read constraint_bindings. The parser did not read `MODEL: amend(`.
- When a night sticks, read the transcript. Name what the role produced. A fact (a file list, a span, a reply edge, a tool in a mode's list) becomes a door or a structural test. Unit-test the door or test, then replay the register.
- Read a judgement across nights first. Spike the judgement only when the model produced the act on some load. The spike is wording A against wording B on one model load (Ollama unloads an idle model in about five minutes).
- Take the scoring rule from the good answers. Check the rule against the tool's own field. The report is numbers plus a wording, never the open question. Start a spike without asking. Stop when a door is built before the measurement that asked for the door.

## The principal flow

- On 2026-09-12 Roman saw a talk on humanlayer's "Why Software Factories Fail" (wsff.md in github.com/humanlayer/advanced-context-engineering-for-coding-agents). Roman asked for a redesign of the principal's flow from that talk.
- The design is `plans/principal-flow.md`. The design has six pages (cut+path, product, commitments, design, slice read, got-it) and three paths (oneshot, plan, full). The design holds at intent and design time.
- rota held the principal only at the cut and signoff. The three moments that decide the shape of code (design, slice, merge read) had no page.
- Two approaches failed. `merge_gate=review` waits on a page that nothing presents. The grouping brief's "declare a dependency fact" has no tool (`batch_dep_facts` has no writer).
- Treat the plan as the frame for pre-build work. The plan amends ruling 2 of 2026-09-12 (hold at intent only) and R7 (touch note never blocks) on the plan and full paths.
- The build order is deterministic pieces first, then one brief sentence at a time on the register.
