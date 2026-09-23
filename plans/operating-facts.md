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
- The lineage of goal 3, three repositories walked three sentences each, is tips, click and icalendar (ruled: Roman, 2026-09-17). There is no budget line in the plan: Roman deleted the notion on 2026-09-17.
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
- Do not run the gate beside a night. The two do not share a file, so nothing corrupts, but they share the machine and the timing cases flake. A gate run beside night 86 gave three new reds, all three named flaky by the gate and all three green on its own re-run, where the same commit gated clean on a quiet machine (observed 2026-09-18). Take the trusted number after the night.
- `tests/rota/test_screens.py` flaked because `pilot.pause()` does not wait for a thread worker, and the list's rows arrive from one (observed: frame 48, 2026-09-23). Textual's `wait_for_idle` reads the process CPU time in slices of 20 ms and returns at the first slice under 1 ms. A thread that waits on git or on the disk spends no CPU, so the pause returned before the rows landed whenever the fetch took more than about 150 ms: a wait of 200 ms in `cli.runs` failed two of the three named tests, and 400 ms failed all three, in the three shapes the gate had seen. The fetch takes 146 to 161 ms alone when a seed carries a commit and a root, because `_mark_moved` spawns git twice per checkout, and it took 744 ms under the suite's sixteen workers. So load raises the rate and is not the cause, and a quiet machine flakes too. Since frame 48 the file's `_settle` helper waits for the app's workers before it reads the screen, and the file passed 48 of 48 under a 2 s wait. Meta workflow. The history: three different tests in that one file flaked across five gate runs on 2026-09-19 (frame 43): `test_sorting_holds_the_view_you_had_scrolled_to` at 04:30 beside a fan-out of agents, `test_opening_a_stale_run_is_refused_with_the_reason` at 06:55 with nothing else running, and `test_marking_two_runs_compares_them` at 08:05. The gate named all three flaky and re-ran all three green. The same wait is in `test_talk.py` and `test_tui_driver.py`, and neither opens the list, so neither is in this fault.
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
- Ollama collapses an oversized prompt to half the window (finding 79, 2026-09-15; its cause corrected 2026-09-18). A prompt that fits `num_ctx` is evaluated whole. A prompt that exceeds `num_ctx` by one token is cut to `num_ctx/2 + 2`, and the server keeps the tail. The brief sits at the front, so the brief is what dies, and the model answers as a generic assistant.
- The correction of 2026-09-18: the cause is not two slots. The rule holds at one slot, on both servers, at three window sizes (observed: a replay of night 85's s110 prompt with a nonce to defeat the cache, 17220 tokens evaluated at num_ctx 40960, 6146 at 12288, 4098 at 8192; an 8415-token prompt at 12288 was not cut). A control prompt with a unique instruction first and a unique fact last returned 6146 and answered from the fact: the tail survives.
- Plan against `num_ctx/2`, not `num_ctx`. A 12288 window gives about 6100 tokens of prompt that survives an overflow. A bigger window does not repair a page that grows with the repository, and it costs VRAM per slot.
- `used = 6146` in a session's account reads as "well inside the window" and means the opposite. Read it as "the prompt was over 12288 and the server dropped the front".
- Count the tokens of a page or a prompt with `/api/generate`, `raw: true`, `num_predict: 1`, and a `num_ctx` above the text. Read `prompt_eval_count`. The count is not affected by the prompt cache: the same prompt sent twice returns the same number, and a leading nonce adds exactly its own tokens (observed 2026-09-18, frame 40: 201 twice, and 210 with a 9-token nonce). Set `num_ctx` above the text, or the overflow rule above cuts the prompt and the count reads half the window.
- The sign is `truncating input prompt limit=6146 prompt=...` in %LOCALAPPDATA%\Ollama\server.log (208 times between 2026-09-12 and 2026-09-15). OLLAMA_NUM_PARALLEL=1 is set as a user environment variable (2026-09-15 04:10, the app restarted) and in probes/titan_ollama.ps1. One slot removes the slot split. One slot does not remove the overflow rule above. Read that log line before you blame a looping session on the model or the brief.
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
- `MiMo-V2.6-Distill-Qwen-9B` Q4_K_M benched on 2026-09-23 at frame 24/38, define 9/14, turn 18.8 s, against `qwen3:8b`'s 34/38, 12/12, 12.5 s. It stays out of the register (observed: `probes/bench/RESULTS.md`, frame 67). Ollama's `think` flag reaches an `hf.co` pull, and only `think: false` answers (observed: two `/api/chat` calls, 2026-09-23 10:05).
- A `/api/chat` call keeps running on the server after the client's timeout closes the socket. The answer is computed and lost, and the next call queues behind it. Sign: the client raises `TimeoutError: timed out`, and `server.log` later prints `stop processing: n_tokens = ...` for the same task (observed: 2026-09-23, `qwen2.5:14b` and `qwen3:30b-a3b` on a 6.6k-token prompt, where 420 s was too short). Give a cold, spilled model 1200 s or more, or stream.
- Neither large local model can take the Developer's seat (observed: a replay of night 86's write turn with a raw `/api/chat` call, 2026-09-23). `qwen2.5:14b` rewrites the function with an invented signature at 471 s a turn. `qwen3:30b-a3b` thinks for 32k to 39k characters, 510 s a turn, and answers in prose with no tool call. That raw call is not the runner's call, and its "`qwen3.5:9b` stops at the tool call" result was the call's artefact (observed: frame 75, 2026-09-23).
- Through the runner's own `complete()`, with the recorded pins and a prompt whose repeat line points at an evicted source, every local model writes `confirm()` from memory and commits it in one turn (observed: `probes/frame37/replay_runner.py model=<tag>`, 2026-09-23). `qwen3.5:9b` think off invents the `code.source` result and writes, 28 s. `qwen2.5:14b` invents the same result byte for byte for 799 characters, 464 s. `gemma3:12b` skips the read and writes a signature that does not exist, 50 s. `mistral-nemo:12b` writes after a paragraph of prose, 50 s. Only `qwen3.5:9b` with think on stops at the read, 3 s, and the runner then answers that read with the same false line. So the write-from-memory fault is the structure's, and a larger model does not close it.

## Running rota

- `python -m rota` is the only entry point (added 2026-08-19). A run is a named database in `<repo>/.rota/<name>.db`. The run records its checkout in `config.project_root`. Every verb takes the name and derives the rest from the database.
- The verbs are `rota ls | onboard <name> --root <checkout> | run | tui | cockpit | report | wipe`. Two runs against one checkout are two names, not two wipes. A comparison of a branch against its main needs two names.
- In the TUI (the seat): `alt+p` run/pause, `alt+r` wipe-and-reindex, `alt+w` wipe, `alt+b` cockpit on the current run. Bindings are `alt+` and never `ctrl+`. The Input widget holds focus, and the widget's bindings win. `ctrl+w` is the widget's delete-word. The footer shows a captured binding, and no action performs the binding (`test_every_binding_survives_the_input_having_focus` guards this rule).
- Inspect with the cockpit, not with a SQLite browser. The three useful questions are not rows. Keep a SQL prompt beside the cockpit for ad-hoc queries only.
- Idle or stuck: read `frontier`/`outstanding` (computed). What the role was shown: read the built prompt (`/prompts.json`). Why did this happen: read the `cause_id` chain.
- Wipe is a command, never `rm`. A worktree is in the target project. The only proof that the worktree is ours is a row in the database. A spawned process has the same shape. The WAL survives the file.
- `lifecycle.start` creates worktrees at dispatch. A role never creates a worktree. An onboarding-only run has no worktree.
- Old runs in `.rota/` are usually behind the schema and cannot open. `ls` says `stale` and gives the reason. The runs are not migrated on purpose. Databases here are throwaway, and `init_db` rebuilds them at boot.
- An old run database refuses a run. `init_db` compares the database's mark against `SCHEMA_MARK` in `rota/core/db.py` and refuses when the two differ, with a sentence that says the database is behind the current schema and needs a fresh onboarding. The refusal happens before any write. Nothing migrates. The mark was `refs` from 2026-09-16 and moved to `ledger-kind` on 2026-09-18 (observed: the commit at 8ebbae1). An older database still opens read-only in the cockpit.
- The warm snapshot `.rota/clickI_warm.db` carries the mark of the night that wrote it. Re-create the snapshot after the mark moves, or the next warm night stops at the door. The snapshot of 2026-09-17 is behind the `ledger-kind` mark (observed: the mark moved after it was written). A cold night is unaffected, because onboarding builds a new database.
- Profiles (2026-09-09): `rota profile list|show|check|set`, `rota onboard <run> --root <dir> --profile <name>`, `rota run <run> --model M --role tester=M`.
- A profile is a TOML file in `<project>/.rota/profiles/` (not found 2026-09-16), `~/.rota/profiles/` (`ROTA_HOME`) (not found 2026-09-16), or `rota/llm/profiles/`. The shipped `local` profile has qwen3:8b as the default and the four judging desks on qwen3.5:9b.
- Onboarding binds the profile into config `profile`. `model_routing` derives from the profile. The walk driver's manual `config.set(... "model_routing" ...)` is the old method.
- `probes/gauntlet_click.sh` on rota/foundation still defaults `REPO` to the old checkout. Export `ROTA_REPO=D:/repos/rota` for a night.
- The Bash tool's shell has the old checkout's venv on PATH and in VIRTUAL_ENV. To run the new venv, prefix PATH in POSIX form: `PATH="/d/repos/rota/.venv/Scripts:$PATH" VIRTUAL_ENV="D:\repos\rota\.venv"`.
- The shell ignores a Windows-form prefix (D:/repos/...). The old python then runs the new code (night 47's first launch, 2026-09-14). After a launch, check the process's command line.
- A night ends at GAUNTLET-DONE, not at Stuck (2026-09-14). The gauntlet script runs sentence three after sentence two sticks. Before you launch the next night, wait for the GAUNTLET-DONE line or kill the night.
- **The assistant has sign-off to run the nights the stack needs, and does not ask per night** (ruled: Roman, 2026-09-22 19:28, "You have signoff to run the nights"). Before that, frame 63's walk was asked twice in one day and held for his word each time. The hour is still the assistant's judgement: a night takes the machine for about two hours, and its setup deletes the click checkout's `.rota` and restores the checkout.
- Launch a night detached, never as a tool call. The Bash tool's timeout caps at ten minutes and a night runs about one hour when every sentence stalls (observed: night 88 ran 72 minutes and night 89 ran 58, 2026-09-21 and 2026-09-22) and about two hours when a sentence merges, so a tool call cannot hold one and a kill mid-run leaves a contaminated database. Night 87 (2026-09-19) used a launcher script in `.rota/` started by `Start-Process bash -ArgumentList '-lc','<launcher>'`, with stdout and stderr redirected into `.rota/`. The launcher exports `ROTA_REPO`, `ROTA_RUNS`, `GAUNTLET_NIGHT` and the venv PATH, so the command carries no state that a later reader must guess. Use `-lc` and not `-c`: the login profile gives Git Bash its PATH, and the launcher's own export then wins. Name Git Bash by its full path, `C:\Program Files\Git\bin\bash.exe`. A bare `bash` in `Start-Process` resolves to WSL's `bash.exe` in `System32`, which knows no `/d/` path and reports "No such file or directory" for the launcher (observed: night 90's first launch, 2026-09-23 10:50).
- **Name Git Bash by its absolute path in that command: `C:\Program Files\Git\bin\bash.exe`** (observed: night 88's first launch failed, 2026-09-21 02:51). `Start-Process bash` resolves through the Windows PATH, where `bash` is `C:\Windows\system32\bash.exe`, which is WSL. WSL mounts the drive at `/mnt/d` and not at `/d`, so the launcher is reported as "No such file or directory" while it exists. The error names the launcher and not the shell, so it reads as a missing file. Night 87's record carried the bare `bash` and it worked there, which means the resolution depends on the session's PATH and cannot be trusted.
- The night's own log tells you it started: `.rota/night<n>.log` holds "night <n> launched", then the click restore line, then "== onboard". Read those three before you call a night running (observed: night 88, 2026-09-21 02:51).
- A night from a worktree runs the worktree's code, because the venv holds no rota and no path file, so `import rota` resolves from the working directory (observed 2026-09-19, frame 43). Point `ROTA_RUNS` at the main checkout's `.rota` when you do that. A night's database is the evidence for its frame, and a worktree's `.rota` dies with the worktree.
- Night 67 launched on the Stuck line while night 66's sentence three still wrote .rota/clickI.db and the click checkout. The restore during that write gave a foreign-key failure and a contaminated start.
- A night's run database is the evidence for its frame. The night script keeps one generation only: it copies `clickI.db` to `clickI_prev.db` at every launch, so the launch after next destroys it. Copy a night's database to `<repo>/.rota/clickI_night<N>.db` as soon as you read it (observed 2026-09-18: nights 82, 83 and 84 survived only as copies in a killed peer's temporary directory, and those directories are cleaned).
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

- **`record_case_run` allocates `seq` in two statements, and four writers race it during a gate run** (observed: a design review's probe on 2026-09-22, four processes and 400 inserts each, 2 duplicate `seq` values). The gate drops `ROTA_L1` from the child's environment, the plugin forces `-n0` only under it, so the gate's suite runs `-n auto` and the four tier files write the live register from four workers. The composite primary key on `case_runs` tolerates the duplicate, so nothing fails today. A new table keyed on `seq` alone would refuse the second insert inside a tier test. A writer that needs a unique `seq` allocates it in one statement.

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
- `case_runs.load_id` is the column that answers "which load". An empty `load_id` is a pre-September recording. It is `model@int(time.time())//7200`, a two-hour bucket of wall time, so it names a period and not an actual load of the weights (observed: `rota/llm/cassettes.py:393`, 2026-09-22).
- **A sample of five is one live call.** A re-record without `ROTA_REFRESH` records a cassette on run 1, and runs 2 to 5 compose the identical prompt, hit that cassette and replay it. One invocation reports `1 recorded in 15.7s, 4 replayed in 0.0s` (observed: frame 55's re-record, 2026-09-22). So a `5/5` and a `0/5` each rest on one call, and the register's larger counts are counts of copies. 743 `qwen3:8b` rows for one case at one prompt hash hold five distinct transcripts, and one of them covers 385 rows over 27 loads and eleven days (observed: the same session). Read a count as "how many times this was replayed", never as "how many times the model was asked". Frame 66 carries the repair.
- **A full re-record of the register is therefore about 128 live calls, and not 640.** One case cost 15.7 s. The wall time is tens of minutes (reasoned: the count above, 2026-09-22).
- **The report's threshold cannot bind.** `casestatus` reads the last `runs` matching rows, which is one invocation, and that window is always unanimous. All 128 cases score 5/5 or 0/5 and none has ever scored anything else (observed: the report over the whole register, 2026-09-22).
- `L1-LI-present-the-touch` was red 0/5 on three models for a week. The list called the case a judgement boundary. The predicate wakes the Liaison with `refs=(batch, item)`. The case had no `refs:`. The prompt showed no `Refs:` line. The brief's "copy the two ids" had nothing to copy.
- With the predicate's refs in the case, `L1-LI-present-the-touch` is 5/5 on both Liaison models (2026-09-12). A register case's wake must carry what the predicate's wake carries (refs, detail). A wake that the system never produces measures nothing. Then "red on every model" reads as a model boundary when the fixture is the cause.
- Before you author or attribute a tick case, read the predicate that produces the wake. Copy the predicate's `refs` and `detail` shape into the case. Before you call a red a boundary, render the case's prompt. Check that the wake lines match the lines of a real run.
- A STALE case (no cassette for the current prompt) renders identically to a red under `--tb=no`. Classify stale-vs-red before you read a baseline.
- **The register replays at 12288 and a night runs at 16384, by design (ruled 2026-09-19, frame 43).** The window is part of the cassette key, so raising `DEFAULT_NUM_CTX` re-keys all 396 live recordings, about two hours of model time. Raising the shipped profiles re-keys none. So the profile route was taken, and the price is that the suites measure the system through a window no run uses. The register holds 18435 turns, 3513 at 8192 and 14922 at 12288, and nothing above (observed: the diff review of 2026-09-19). Every claim about the 16384 regime is arithmetic until a night renders it. `test_the_sampled_suites_do_not_pin_a_smaller_window` now compares a suite's pin against `rota.llm.setup.default_window()`, which reads the profile, so the guard cannot go green on the old number again.
- `python -m rota.tools.gate` does that classification (frame 30, 2026-09-17). It runs the suite with `--tb=no -rfE -q`, prints five lines (summary, new reds, reds gone, the stale set under the suite's model, time), stores the baseline in `.rota-gate.json` at the repo root, and re-runs new reds only for their tracebacks. Never read `.rota-gate.log`. `--baseline` re-takes the baseline. A checkout with no register gets `stale: the register is absent`. Four runs on this box: 465 s to 482 s.

Cost anchors (frame 28, written 2026-09-17 from frames 24, 26, 29 and 30; re-derive from the last three frames whenever a frame that changes the workflow closes). Meta workflow. Every row is observed from the harness usage line under an Agent result, never from the agent's own estimate.

- Agent floors, one trivial task each: general-purpose on Opus 38.3k; implementer 11.4k; reviewer 13.3k; sweeper 8.9k (frame 26).
- A reviewer with no tool call, a three-line answer: 9.6k (frame 29's probe). The reviewer type inherits the session's model, Fable; the implementer and the sweeper run on Opus (frame 26). The Agent tool fixes the type list at session start and reads a type's body at each spawn, so an edit to a definition is live without a restart (observed: the probe quoted a command line that e407e5d added after this session started).
- A reviewer pass, cold, six to eight numbered points with probes: 69k to 76k (frame 30); 61k for five points on a worktree (frame 24). A resumed second look on the fix commit: 18k (frame 30). A design review by the reviewer type on a scope report and a design record, before any code: 66k, 23 tool calls, ten findings (frame 24). A read-only database probe by the reviewer type, three databases, no worktree: 24k (2026-09-17).
- An implementer pass on Opus, cold, two new files of about 300 lines and one suite run: 74k (frame 30); 77k for one tool of 340 lines with 20 tests and a gate run (frame 24). Resumed: 7k for a docstring and three lines with one test; 40k for six fixes and ten tests (frame 30); 24k for five fixes and five tests with a gate run (frame 24).
- A suite run read inside an agent as raw pytest output: about 25k (frame 21). Through the gate: about 1k in the agent; about 6k of the assistant's context per run, call included; 8 minutes wall (frame 30).
- A tool frame in the assistant's own context, claim to close, two reviews and three implementer passes included: about 120k (frame 30; observed: `/context` 173k at close with a 45k fixed prompt).
- A design record written by the assistant: about 8k of output. A status line: about 1k (frame 30).
- A cap written in a brief does not bind (observed: the harness usage under two Agent results, frame 66, 2026-09-23): the reviewer type spent 146.7k against a 100k cap on eight points with 38 tool calls in 15 minutes, and a resumed second look read 137.9k on its line for four points and 14 calls; the implementer on Opus spent 216.9k against a 120k cap for a cold pass of 18 files, 666 insertions, 11 tests and one gate run, 163 tool calls, 54 minutes. Price a pass from these rows, and treat the cap as a request.
- `turns.user` is the whole prompt of that call, working set included, and `turns.system` is the brief. Sizes go up and down between the turns of one session. A replay of one turn is one `/api/chat` call with those two strings (observed: night 86's `s145`, 2026-09-23).
- `test_runs` keeps one row per test at the latest attempt. Earlier attempts survive only in the fix wake's text in `turns.user` (observed: night 86, 37 rows all at attempt 10, 2026-09-23).
- The night launcher leaves the run as `.rota/clickI.db` when the night ends stuck. Night 90 ended at 12:20 on 2026-09-23 and was not renamed `clickI_night90.db` (observed: `.rota/night90.log` and the directory).


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

## The build session's peers

Meta workflow. Ruled by Roman on 2026-09-17. The chain that built the tooling is archived in `plans/archive/tooling-flow-2026-09-17.md`.

- Opus builds, Fable judges. The agent types implementer and sweeper run on Opus. The reviewer inherits the session's model, Fable.
- A judging agent asked to find faults finds faults. Frame 40 asked twelve agents whether a reply to a page was reasonable. They called 29 of 32 replies unreasonable or partly so. Twelve adversaries, each told to default to "reasonable" and given a four-line materiality test, overturned 23 of the 32 (observed 2026-09-18, frame 40). Never put a single judging pass in a record. Run the adversary, and write the test it judges by: a fault counts only if it changes what a person does.
- A completeness critic earns its cost. The thirteenth agent of frame 40 read the whole set and found the worst fault of both nights, which the twelve page judges had all missed, because the fault is visible only when the page is compared with the register (observed 2026-09-18, frame 40). Check every one of its claims against the data before it enters a record. Two of its claims did not survive that check.
- A standby peer waits with no frame. Its prime: "You are a standby peer. Do not claim a frame and do not read the stack yet. Reply with your session id in one line, then wait. Reply to any message within one turn. A hand-off arrives by message from a peer: a frame number and a stack commit. When it does, follow the wake steps in CLAUDE.md and claim that frame."
- The liveness probe before a hand-off: list the peers, then send every one "Reply in one line: your session id, and whether you hold a frame or are a clean standby." A send succeeds even to a closed session, and the row stays listed, so a successful send proves nothing (observed: 2026-09-17, four rows, three replies within a minute, one row closed). The reply is the only signal. Hand off to the first clean peer that answers. Tell the others to stand by.
- **Corrected 2026-09-19 (observed: the kit's measurement of 248 cross-session messages in one machine's history, `meta/CONTRACTS.md`).** The bullet below said that a message never reaches an idle session. That sentence is false and it was measured false. A message does arrive, and fast. It is the wrong carrier for a hand-off for three other reasons, which are in the blocks under this list. The false sentence had already entered a stack status line and a commit message, so a prediction gated. The old bullet is kept here, struck, because the record of a wrong fact is worth more than its deletion.
- ~~A message drains at the receiver's next tool round. A session that sits idle at its prompt never takes one, so the send reports success and the peer's user sees nothing (observed 2026-09-18: four probes sent, one reply, and Roman saw no message in two sessions started seconds earlier). The fix is one keystroke in the receiving session, which drains the queue. A hand-off that depends on a message alone can therefore stall with no error.~~ What the four probes of 2026-09-18 actually measured is unknown. A parked session drains nothing, and a permission prompt parks a session, so the likeliest cause is a parked receiver and not an idle one.
- A peer's picture of who holds what goes stale within hours and it is confidently wrong. At the hand-off of frame 43 (2026-09-19) the one peer that answered the liveness probe reported that session 9108c499 held frames 33, 4 and 43, and told the probing session to check with it first. 9108c499 had handed frame 43 away that morning and its inbox had already refused a message with ENOINBOX, so the session was gone. The same reply named a stack commit about twenty commits behind. Meta workflow. Read the stack for who holds what. A peer's account of another peer is hearsay, and correcting it is worth a message, because an uncorrected one routes the next session into a double claim.
- The peer list shows peer names, never session ids. Roman names a peer by session id. The two cannot be matched without a probe, and a probe needs the peer to take a tool round. When a hand-off must land, give Roman the line to paste into the new session instead: the stack commit, and "follow the wake steps in CLAUDE.md" (reasoned: 2026-09-18, two named session ids could not be matched to any listed peer).
- The Agent tool fixes the list of agent types at session start and reads a type's body at each spawn. A session started before a type landed restarts before it claims a frame that needs the type. An edit to a type's body needs no restart (observed: frame 29's probe, 2026-09-17).
- A forked session keeps its transcript and gets a new session id and a new peer name. It re-claims its frames with the new id (observed: 2026-09-17, cc3d4e4e forked to 3b4093c6).

### The reserve, adopted 2026-09-19

Meta workflow. The hand-off is a file, not a message. The tool is
`rota/tools/handover.py`, adopted from the kit on 2026-09-19 with 38 tests
green in this repository. The reserve lives in `.handover/` at the repository
root, a worktree shares the same one, and `.gitignore` holds it. It is machine
state and not a record. `python rota/tools/handover.py peers` prints it. The
record of a hand-off is the status line in the stack.

A peer's name changes when its session restarts. A session id does not. So
address a peer by the session id, and record the name only so that a person
can find the window.

The context hook enrols every session that sends a prompt, in
`.handover/sessions/`, with its peer name and its context estimate. So a
session Roman only pasted into is still reachable, and `peers` shows which
standby is the cleanest. An unread claim returns to the queue as a vacancy
after fifteen minutes, so a session that wakes and cannot act does not hold a
frame still. The mechanism is proved and the fifteen minute value is not. Every
proof so far shortened the clock, so nothing has yet waited out the default on
live state (observed: the ported tests and this repository's acceptance run,
2026-09-20).

Two facts about the harness decide the whole mechanism. Both were read from
one machine's own transcripts. Re-read them on this machine before anyone
writes another rule about them.

- An idle session does receive a message, and fast. Of 248 cross-session
  messages, none was lost. 57 that landed in sessions idle for over five
  minutes drained in a median of 0.010 seconds, one across 35.8 hours
  (observed: the transcripts of five projects).
- A session parked mid-turn drains nothing. One session held its inbound
  messages for six hours while it waited on a tool decision. A permission
  prompt parks a session the same way (observed: the same corpus).

Five assertions that felt sound and were never run, all on 2026-09-20, in the
same week the rule against them was written down. Keep the list. The shape
repeats and the cost is always a rule that gates. Four are the kit's, adopted
in frame 50 and frame 52. The fifth happened in this repository.

- "Session messaging did not carry it." Written into a record and a commit
  message from one hand-off that arrived four minutes late. The message had
  arrived (observed: the transcripts, 2026-09-20).
- "The kit update is not installed in that project." A check ran before the
  update landed. A session quoted it afterwards as current, then broadcast it
  to four sessions as a rule. That rule would have stopped a session at 400k
  holding a frame it could have handed. The receiving session caught it in
  minutes (observed: the peer's reply and commit 56f2ab3, 2026-09-20).
- "That reclaim hazard is reachable from ordinary operation." Asserted from
  reading the code, then disproved by the first test written for it. A
  re-armed watcher reads the waiting claim on its first poll (observed: the
  test `test_a_re_armed_watcher_takes_an_unread_claim_at_once`, 2026-09-20).
- "The two glob implementations disagree on 30 cases, then on 171, then on 80."
  Three faults in the comparison and none in either implementation. On the
  third, every trivial case passed and the result was still wrong, because a
  trivial case tests the matchers and never tests the reading of the table. The
  comparison count caught it. The kit's frozen table is 34 patterns against 33
  paths, so any total but 1122 means the table was misread. Check the count of a
  comparison before you read its disagreements. The fourth run found 5 real ones
  (observed: a destination's own report, 2026-09-20).
- "That destination's hook carries local edits, so merge by hand." The kit wrote
  that into its own update procedure, about a file in a project nobody upstream
  had read. **rota is that destination.** Frame 50 followed the instruction and
  merged `repo_root`, `enrol`, `peer_name` and `waiting` by hand at 56f2ab3.
  Frame 52 diffed the two files: rota's hook holds no local logic at all, only
  the slot fills `Roman` and `rota/tools/handover.py`, so replacing the file
  whole was both correct and safer. The instruction sent this repository down
  the riskier path, by hand, through four functions (observed: frame 52's own
  diff of the hook against the kit at 80bd49e, 2026-09-21).
  The kit reports that the same unrun claim spread to a destination's
  `CLAUDE.md` and to a frame, neither of which diffed the file either, and that
  it read as three records agreeing for two days. Repeating an upstream
  assertion in your own words does not check it (observed: the kit's own report,
  2026-09-20). rota did not copy it, so rota carried it in one place only.

**A session's brief and slash commands are fixed when the session starts**
(observed: session 0f086f93, 2026-09-20 15:12). That session started at 02:37.
Commit f06ffbf changed `CLAUDE.md` and `.claude/commands/standby.md` at 03:10
to stop asking a standby for its peer name. At 15:12 the session still held the
02:37 text, and it armed by the old instruction. The arm failed, because the
session had no name to type. It then spent one `ListAgents` call to learn its
own name and armed again.

So a change to the brief does not reach a standby that is already armed. After
any change to `CLAUDE.md` or to a command file, the armed standbys hold the old
text until Roman restarts them. Two routes exist and neither is free. Restart
the standby, which spends its clean context. Or message it, which spends a
turn. Prefer the change that is safe under both texts, as f06ffbf was.

Three things a message cannot do, which is why the hand-off uses a file. Each
one cost a real hand-off.

- It cannot carry a session id. A peer is addressed by name, a name is
  recycled between sessions, and one session answered to two names on two
  days. A sender once broadcast a frame with the words "claim it only if your
  session id is 4286e076" (observed).
- It cannot prove it landed. Four sends to a listed but closed session
  returned success and reached nobody. One receiver woke in 68 milliseconds
  after 15.7 hours and spent its whole turn on a usage-limit notice
  (observed).
- It is not free for the receiver. A one-line liveness probe made a standby
  answer and then read the git log and the stack unprompted, in the same turn.
  The probe spends the asset it is measuring (observed). This repository saw
  the same thing on 2026-09-19.

Numbers to measure once on this machine. The values below are borrowed from
the machine the tool was built on.

- The context count is a count, not an estimate. The hook reads the last
  assistant turn's own usage from the transcript: fresh tokens, plus tokens
  written to cache, plus tokens read from cache. Where a transcript carries no
  usage the hook scales its bytes by 0.65, measured by the kit on 2026-09-20
  against a 4.7 MB transcript whose last turn reported 771,959 tokens. The kit
  shipped 0.6 until then, and rota's own first calibration on 2026-09-16 also
  gave 0.6 from a 1.6 MB transcript against about 250k in the UI. Low is the
  dangerous direction, because the ceiling decides whether a session can finish
  a frame (observed: the kit's transcript, 2026-09-20).
- **The correction is not one number and it is not always upward.** Frame 52 ran
  both hooks over three of this repository's own transcripts. Session cb5428a2
  read 246k and now reads 269k, up 9 percent. Session 0f086f93 read 160k and now
  reads 183k, up 14 percent. Session 9a9a20bf read 429k and now reads 424k, down
  1 percent. So expect a rise of about 10 percent on most windows, and treat the
  jump as a correction and never as growth (observed: frame 52's own run of the
  staged hook against the installed one, 2026-09-21).
- One word carries two meanings and stays that way (ruled: Roman in the kit,
  2026-09-20). A `claim` is the file a sender writes, and to claim a frame is to
  write your session id in its heading. A rename would touch about sixty places
  across the kit and two destinations' records, for an ambiguity that context
  resolves every time. Recorded so the next reviewer finds the ruling instead of
  the defect.
- The wake: the time from the claim file appearing to the standby's first
  turn. 6 seconds, and no longer borrowed. The kit measured it once, then twice
  more in a second project. rota measured 7 seconds on frame 43 and 4 seconds on
  frame 50 (observed: three projects, 2026-09-20).
- The cost of waiting: nothing. A process blocks, and the model spends no
  tokens until it wakes (borrowed).
- The cost of arming a standby: one command and one line of reply. Not yet
  measured here.
- The cost of a re-arm when the wait runs out: one turn per standby per
  `--wait`. At the 28800 default that is one turn per session per eight hours.
  Two standbys ran out at 10:37 and re-armed four and seven seconds later with
  no person present, and both still read about 20k after twelve and a half hours
  in the reserve (observed: a destination's hand-off log, 2026-09-20).
- How long the harness lets a background process live. A heartbeat beat 150
  times over 49.7 minutes on the kit's machine and then ended on its own
  clock. The longest gap between two beats was 22 seconds against a 20 second
  interval. The ceiling is above 50 minutes and is otherwise unknown
  (borrowed). Measure it here, then set `--wait` below it.

**All seven of the kit's update steps are installed, 2026-09-20 02:30.** The
last two needed Roman to approve them by hand. A session running in auto mode
has every edit under `.claude/settings.json` and `.claude/hooks/` refused by
the permission classifier, so those two were staged and Roman approved the
calls.

- The permission rule is `"Bash(python rota/tools/handover.py:*)"` in
  `.claude/settings.json`, which is tracked. A per-call approval expires with
  its session. This rule does not, because it is a file every session reads.
- The hook at `.claude/hooks/context_count.py` carries `repo_root`, `enrol`,
  `peer_name` and `waiting`.

Checked as the kit requires (observed: session 9a9a20bf, 2026-09-20 02:30).
The hook prints one JSON object and exits 0. It wrote its row to
`.handover/sessions/`, and `peers` read that row back and named the session.
That is acceptance line 12, so the enrolment path is proved.

**Acceptance lines 7, 8 and 9 are proved** (observed: session 9a9a20bf handed
frame 43 to session 0549dc76 at 2026-09-20 02:51, with three standbys armed).
Line 7: all three armed by the `/standby` command and `peers` showed all three
free, so no permission prompt parked any of them and the project `allow` rule
holds. Line 8: the standby woke with no keystroke, and the sender read
`CONFIRMED` 7 seconds after the claim, against the borrowed 6. Line 9: exactly
one of the three woke, and the other two still answered as free with fresh
heartbeats and no turn spent.

**Acceptance lines 10, 11 and 13 are not run.** They need an empty reserve, an
orphaned claim, and a fifteen minute wait.

**The reclaim is covered by tests from 2026-09-20, frame 50, and it is still
unrun on live machine state.** Two ported tests carry it. One shows that a
re-armed watcher reads a waiting claim on its first poll, so the feared case
never reaches the reclaim clock. The other shows that the eviction removes a
registration only when the registration predates the claim. Frame 50 did not
wake the last free standby to repeat that on the live box, because the two
tests now answer the question the live run was for (reasoned: the frame's
instruction to exercise it was written before those tests existed).

**The second live hand-off ran on 2026-09-20 at 15:12.** Session 0549dc76
handed frame 50 to session 0f086f93 at stack commit 14db40a. The sender read
CONFIRMED 4 seconds after the claim, against 7 seconds on frame 43 and the
borrowed 6.

**Read the `peers` table correctly. Two of its columns mislead.**

- **A holder's heartbeat stops by design.** The watcher exits when it delivers
  the claim, so a live session that holds a frame writes no more beats. Until
  2026-09-20 the table printed STALE there, which says a working session died.
  The table now prints `held` for a row in state `holding`. STALE still means
  dead, and only for a row whose state is `standby`.
- **The column is named `handed` from 2026-09-20, frame 50.** It names the
  frame the mailbox delivered, not the frame the session holds now. Nothing
  updates it when the session moves to the next frame. On 2026-09-20 session
  0549dc76 showed frame 43 while it held frame 46, and frame 43 was closed
  and in the archive, so the row contradicted the stack. Correct it with
  `python rota/tools/handover.py holding --sid <sid> --frame <n>`, or
  `--frame none` when the session holds no frame. The hand edit of
  `.handover/peers/<sid>.json` is no longer needed (observed: the ported
  `cmd_holding` and its test, 2026-09-20).
- **Both corrections are proved on the live table** (observed: `peers` at
  2026-09-20 15:33, with sessions 0549dc76 and 0f086f93 both in state
  `holding`). Each row read `held` and named the frame the mailbox delivered.
- **A cleared frame reads `spent` from 2026-09-21, frame 52.** A session that
  closes its frame and runs `holding --frame none` used to have "standby"
  written into its row, and its watcher had already exited when it took the
  frame. The table then printed a working session as a standby with a dead
  heartbeat, which its own legend reads as a session that died. That is the same
  fault as a holder printed STALE, in a second place. A cleared row now reads
  `spent`, and a session rejoins the reserve by arming and never by saying it
  holds nothing. A standby whose watcher really died still reads STALE.
- **A row at or past the ceiling reads `full`.** It is armed and no frame goes
  to it.

**The hand-off order is the oldest free standby under a 300k ceiling** (ruled:
Roman in the kit, 2026-09-20, installed here on 2026-09-21 in frame 52). Oldest
first spends one session before it spends a fresh one, so a workspace ends the
day with fewer part-used windows. The ceiling stops a frame from landing on a
session that must stop halfway through it, and the brief already named 300k as
the take-no-new-frame line. Three consequences, each ruled and not guessed.

- A reserve whose every standby is past the ceiling is a drought, and it is not
  an empty reserve. `hand` still exits 5 and still posts the vacancy. It also
  names each session that was too full, so the frame waits for a fresh window
  instead of landing on one that fills up mid-frame.
- A session past the ceiling leaves the reserve instead of arming, and `standby`
  exits 2 and takes its seat back. A seat no hand-off can use makes the reserve
  read larger than it is, which is the same class of lie as a row that says a
  working session died.
- An unknown estimate is eligible, and that is not a compromise. A window armed
  on its first prompt has no transcript to measure yet, and it stays unmeasured
  while it sits quiet. So unknown is the normal state of the cleanest seat there
  is (observed: a live session in a destination's reserve carried est null and
  turns zero, 2026-09-20).

This replaces rota's rule of 2026-09-20, which told the sender to read the `ctx`
column and name the cleanest row with `--to`. The tool now enforces the order,
so the hand read is gone from the brief.

**A peer message is not a record** (observed: 2026-09-20). A session from
another project reported that a hand-off from 7b95045e had gone to rota-02.
The handover log held no row for 7b95045e, and rota-02 still answered as a
free standby with a fresh heartbeat. The box is per checkout at
`<repo>/.handover`, so a hand-off in another project writes to another box.
Check the log before you act on a peer's account of a hand-off.

**The harness peer list is machine-wide and never says which repository a
session works in** (observed: `ListAgents` on 2026-09-20 listed rota
sessions beside `finance-dashboard-20` and two `meta-workflow` sessions).
This is why the old liveness probe could hand a frame across projects: a
session in another project answers "clean standby" truthfully in its own
sense, and the sender cannot tell. A peer in the kit repository reported on
2026-09-20 that this had sent a Finance Dashboard frame to a rota session
(reasoned: the peer's account, which matches what this session saw
independently when `finance-dashboard-20` probed rota peers).

**The reserve in `.handover` does not have that fault**, because it lives in
the checkout and can only offer sessions that armed in rota. That is the
reason the probe was replaced, and the replacement is installed here at
56f2ab3 and proved on frame 43 at 02:51.

**The arm command must not ask for a name** (observed: session 0549dc76,
2026-09-20 02:52). A session cannot read its own peer name until it lists its
peers, so a name typed at arm time is a guess. That session typed a
description, and its row then named nobody a message could reach, which is the
fallback route when `hand` exits 4. The tool now takes the enrolled name from
the hook's row and keeps `--name` only for a checkout with no hook. The
`/standby` command and the brief no longer ask for a name.

The two bullets above that describe the liveness probe and the standby's
pasted prime are superseded by the brief's `# Standby duty` section. They are
kept because they carry the measurements that argued for the change.

## The build session's tools

Facts about the assistant's own harness and shell, the meta workflow.

- The console codepage is cp1252. A print of a transcript with one non-Latin character dies with `UnicodeEncodeError: 'charmap' codec can't encode character`. Run python with `PYTHONIOENCODING=utf-8` (observed: 2026-09-23).
- The harness reads `.claude/agents/*.md` at session start. A `model:` edit lands in the next session. An implementer spawned after the edit reported `claude-opus-5[1m]` (observed: 2026-09-23). The build model is `claude-opus-5-5` since `82a9d09` (ruled: Roman, 2026-09-23).
- An agent on `claude-opus-5-5` dies before its first turn with `API Error: 400 Claude Code 2.1.258 does not support this model; version 2.1.280 or newer is required. Run 'claude update'` (observed: a fresh session's implementer spawn, 2026-09-23 14:47). The harness on the box was 2.1.258 until Roman updated it on 2026-09-23 between 16:50 and 17:39. After the update a fresh implementer reports `claude-opus-5-5[1m]` (observed: 2026-09-23 17:40). An agent resumed by message keeps the model it was spawned with. Do not run `claude update` from a session: it is Roman's machine state, and sessions are live.
- Run the gate without a `tail`. Its five lines print before the flaky re-run's pytest output, so a `| tail -8` shows the re-run's `FAILED` lines and `exit 1: 11 new reds, 0 of them flaky` with nothing above them, and the new-red names and the stale line are lost. Recover them from `.rota-gate.log` and `.rota-gate.json`: the new reds are the log's `FAILED` set minus the baseline's `failed`, and `rota.tools.gate._stale(model)` gives the stale set (observed: 2026-09-23 16:26, two extra commands).
- Neither the `ant` CLI nor the `anthropic` package is installed on the box. A live check of the model list is a WebFetch of `https://platform.claude.com/docs/en/about-claude/models/overview.md` (observed: 2026-09-23).
