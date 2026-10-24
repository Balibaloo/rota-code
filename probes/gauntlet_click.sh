# The click gauntlet: onboard a fresh clickI, then three sentences with a yes-only
# principal, 24 turns a session. Restore clickI first (rota/COMPLETION.md, the
# walk log). Logs to stdout; the walk rows land in tests/rota/walks.jsonl.
# Absolute, so a copy of this script run from anywhere still runs the
# repository's driver on the repository's database. Nights 35 and 36
# (2026-09-13) ran from a scratchpad copy, found no `rota` module there,
# ran an old walk.py beside the copy, and never onboarded. The default
# path moved on 2026-09-14, when rota left Custom_AI_TUI (plans/rota-split.md).
REPO="${ROTA_REPO:-D:/repos/rota}"
cd "$REPO"
W="$REPO/probes/walk.py"
export ROTA_ONESHOT=
ollama_up() { curl -s -m 5 localhost:11434/api/tags >/dev/null || { echo "ollama down at $(date +%H:%M), restarting"; powershell -NoProfile -Command "Start-Process ollama -ArgumentList serve -WindowStyle Hidden" >/dev/null 2>&1; sleep 15; }; }
export ROTA_MAX_ITERATIONS=24
export PYTHONUNBUFFERED=1
# One live file per process: the register recorder on the Titan writes
# .rota/live.md too, and the two overwrote each other (2026-09-13).
STATE="${ROTA_RUNS:-$REPO/.rota}"; mkdir -p "$STATE"; export ROTA_RUNS="$STATE"
export ROTA_LIVE="$STATE/live_click.md"
export WALK_NIGHT="${GAUNTLET_NIGHT:-}"
export WALK_WORDS="yes that all looks right, go ahead"
# A model in the principal's seat when GAUNTLET_AGENT names one (frame 41).
export WALK_AGENT="${GAUNTLET_AGENT:-}"
# The sample repository starts every night at its base commit. Night 50
# (2026-09-14) ran on the main that night 49 had merged echo_json into, so
# the first sentence asked for what already existed and the Developer
# read nine test files it had not written. Worktrees, batch branches and
# the merge go; the base is the commit the snapshot was onboarded at.
CLICK_ROOT="${CLICK_ROOT:-D:/repos/_AI/sample_repos/clickI}"
CLICK_BASE="${CLICK_BASE:-2c8cd3a}"
# The item set. The three items of nights 49 to 162 ran for three nights
# on the same doors, and version_option risked a door fitted to one
# decorator (ruled: Roman, 2026-10-15 01:54, "I want to prevent over
# fitting"). GAUNTLET_ITEMS=163 runs three other items on click: one with
# a docstring criterion, one that replaces a base statement, and one that
# the Tester can test only through a fixture the criterion names. The
# agent principal reads the matching brief through ROTA_PRINCIPAL_BRIEF.
if [ "${GAUNTLET_ITEMS:-}" = "163" ]; then
  export ROTA_PRINCIPAL_BRIEF="$REPO/probes/principal_brief_163.md"
  S1="Give format_filename one example in its docstring: with shorten set to True, the path a/b/c.txt shows as c.txt."
  F1="the docstring changes and the code does not"
  S2="In get_app_dir on Windows, when APPDATA or LOCALAPPDATA is not set, use the AppData Roaming or AppData Local folder under the home folder instead of the bare home folder."
  F2="Roaming when the roaming flag is True, Local otherwise"
  S3="Make clear() return True when it cleared the screen and False when stdout is not a terminal."
  F3="the output does not change, only the return value"
else
  S1="Add an echo_json(obj) helper next to echo that prints an object as compact JSON on one line, followed by a newline."
  F1="keep it to the standard library json module, no new dependency"
  S2="Let confirm() take a default_on_eof flag: when stdin is closed it returns the default instead of aborting."
  F2="the flag defaults to False so nothing changes for existing callers"
  S3="Give version_option a show_python flag that appends the running Python version to the message."
  F3="the Python version comes from sys.version_info as major.minor.micro"
fi
restore_click() {
  local r="$CLICK_ROOT"
  for w in $(git -C "$r" worktree list --porcelain | grep "^worktree " | grep "/.rota/" | cut -d" " -f2); do
    git -C "$r" worktree remove --force "$w" 2>/dev/null
  done
  git -C "$r" worktree prune
  git -C "$r" checkout -q main && git -C "$r" reset -q --hard "$CLICK_BASE"
  for b in $(git -C "$r" branch --list "batch/*" | sed "s/^[+* ]*//"); do git -C "$r" branch -D -q "$b"; done
  rm -rf "$r/.rota"
  git -C "$r" clean -fdq
  echo "== click restored to $(git -C "$r" log --oneline -1)"
}
restore_click
# GAUNTLET_FROM=2 starts at the second sentence. Sentence one merged on
# nights 49 and 50 (2026-09-14); a night that measures sentences two and
# three need not spend forty minutes re-proving it.
# The last night's run database, kept beside the new one: `onboard --force`
# replaces it, and night 34's sessions were lost to night 35's start
# (2026-09-13) before they were read.
python -c "import sqlite3, os; d = os.environ['ROTA_RUNS']; os.path.exists(d + '/clickI.db') and sqlite3.connect(d + '/clickI.db').backup(sqlite3.connect(d + '/clickI_prev.db'))"
# A seam start: the night begins at the state under test, not at onboarding.
# A seam is a run database paired with the commit its batch's worktree stood
# at (plans/frame104-seam-start.md, 2026-10-01). Write the pair from the fact
# that `python probes/seam_start.py pair <db>` prints. The night skips
# onboarding, the fresh check and the three sentences, and runs one walk.
if [ -n "${GAUNTLET_SEAM_DB:-}" ] || [ -n "${GAUNTLET_SEAM_COMMIT:-}" ]; then
  [ -n "${GAUNTLET_SEAM_DB:-}" ] && [ -n "${GAUNTLET_SEAM_COMMIT:-}" ] || { echo "SEAM REFUSED: set both GAUNTLET_SEAM_DB and GAUNTLET_SEAM_COMMIT"; exit 3; }
  echo "== seam start $(date +%H:%M) from $GAUNTLET_SEAM_DB at $GAUNTLET_SEAM_COMMIT"
  python "$REPO/probes/seam_start.py" restore clickI "$GAUNTLET_SEAM_DB" "$GAUNTLET_SEAM_COMMIT" "$CLICK_ROOT" || exit 3
  export WALK_FROM_WARM=1 WALK_FROM_SEAM=1
  ollama_up
  echo "== seam walk $(date +%H:%M)"
  # The walk answers each clarify with this sentence. An empty answer lands nothing.
  WALK_PHASE=seam python "$W" clickI "" "${GAUNTLET_SEAM_ANSWER:-yes to all of it. keep it simple.}" 250
  python -m rota.tools.nightcount clickI
  echo "GAUNTLET-DONE $(date +%H:%M)"
  exit 0
fi
echo "== onboard $(date +%H:%M)"
# Warm is the default (ruled: Roman, 2026-09-24, "why is this not always
# on?"). The stamp check goes cold by itself when a hard file moved, and
# every fifth night is cold. Set GAUNTLET_COLD=1 when the frame's walk covers
# onboarding, or when a soft file moved: the runner, the desks or the
# sandbox. A warm night keeps onboarding's sessions from before that change,
# and the stamp only logs it. GAUNTLET_WARM=0 also forces cold.
if [ "${GAUNTLET_COLD:-}" != "1" ] && [ "${GAUNTLET_WARM:-1}" != "0" ] && python "$REPO/probes/warm_stamp.py" check clickI; then
  # A warm start: the snapshot walk.py wrote at the first slicing wake of an
  # earlier night. Onboarding's sessions are already in it; the night begins
  # at slicing. The stamp check above goes cold on its own when a brief, a
  # tool list, the graph or a predicate changed, or after four warm nights.
  echo "== warm start from $STATE/clickI_warm.db (onboarding skipped)"
  rm -f "$STATE/clickI.db" "$STATE/clickI.db-wal" "$STATE/clickI.db-shm"
  python -c "import sqlite3; import os; d = os.environ['ROTA_RUNS']; sqlite3.connect(d + '/clickI_warm.db').backup(sqlite3.connect(d + '/clickI.db'))"
  python "$REPO/probes/warm_stamp.py" relocate clickI "$CLICK_ROOT" || exit 3
  export WALK_FROM_WARM=1
else
python -m rota onboard clickI --root "$CLICK_ROOT" --force --profile "${GAUNTLET_PROFILE:-local}" 2>&1 | tail -2
fi
# A night starts from nothing. Night 36 (2026-09-13) ran its first sentence
# in minutes on night 35's leftover database: the wipe had not happened.
[ "${WALK_FROM_WARM:-}" = "1" ] || python -c "import sqlite3, sys; import os; n = sqlite3.connect(os.environ['ROTA_RUNS'] + '/clickI.db').execute('SELECT COUNT(*) FROM sessions').fetchone()[0]; sys.exit(0 if n == 0 else print(f'NOT FRESH: {n} sessions already in .rota/clickI.db; the wipe did not happen') or 3)" || exit 3
# After the fresh check, which counts sessions: onboarding alone, then the snapshot: no sentence in it, so a warm night
# can start at any sentence (GAUNTLET_FROM). The yes-only principal answers
# onboarding's pages the same way.
# Onboarding replays a wake whose whole prompt is recorded in the night
# cassette (frame 233). GAUNTLET_REPLAY=0 runs it live and records. The walks
# get neither variable, so a walk never reads or writes the night cassette.
# The agent principal answers a recorded onboarding page from the principal
# record, a copy of the last night's `clickI.principal.jsonl`.
NIGHT_CASSETTES="${GAUNTLET_NIGHT_CASSETTES:-$STATE/night_cassettes.db}"
PRINCIPAL_REPLAY="${GAUNTLET_PRINCIPAL_REPLAY:-$STATE/clickI.principal.jsonl}"
[ "${WALK_FROM_WARM:-}" = "1" ] || WALK_PHASE=onboarding WALK_ONBOARD_ONLY=1 WALK_REPLAY="${GAUNTLET_REPLAY:-1}" ROTA_NIGHT_CASSETTES="$NIGHT_CASSETTES" ROTA_PRINCIPAL_REPLAY="$PRINCIPAL_REPLAY" python "$W" clickI "" "" 250
ollama_up
if [ "${GAUNTLET_FROM:-1}" -le 1 ]; then
echo "== walk 1 $(date +%H:%M)"
WALK_PHASE="sentence 1" python "$W" clickI "$S1" "$F1" 250
fi
ollama_up
if [ "${GAUNTLET_FROM:-1}" -le 2 ]; then
echo "== walk 2 $(date +%H:%M)"
WALK_PHASE="sentence 2" python "$W" clickI "$S2" "$F2" 250
fi
ollama_up
if [ "${GAUNTLET_FROM:-1}" -le 3 ]; then
echo "== walk 3 $(date +%H:%M)"
WALK_PHASE="sentence 3" python "$W" clickI "$S3" "$F3" 250
fi
python -m rota.tools.nightcount clickI
echo "GAUNTLET-DONE $(date +%H:%M)"
