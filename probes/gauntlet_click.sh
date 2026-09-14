# The click gauntlet: onboard a fresh clickI, then three sentences with a yes-only
# principal, 24 turns a session. Restore clickI first (rota/COMPLETION.md, the
# walk log). Logs to stdout; the walk rows land in tests/rota/walks.jsonl.
# Absolute, so a copy of this script run from anywhere still runs the
# repository's driver on the repository's database. Nights 35 and 36
# (2026-09-13) ran from a scratchpad copy, found no `rota` module there,
# ran an old walk.py beside the copy, and never onboarded.
REPO="${ROTA_REPO:-D:/repos/_AI/Custom_AI_TUI}"
cd "$REPO"
W="$REPO/probes/walk.py"
export ROTA_ONESHOT=
ollama_up() { curl -s -m 5 localhost:11434/api/tags >/dev/null || { echo "ollama down at $(date +%H:%M), restarting"; powershell -NoProfile -Command "Start-Process ollama -ArgumentList serve -WindowStyle Hidden" >/dev/null 2>&1; sleep 15; }; }
export ROTA_MAX_ITERATIONS=24
export PYTHONUNBUFFERED=1
# One live file per process: the register recorder on the Titan writes
# .rota/live.md too, and the two overwrote each other (2026-09-13).
export ROTA_LIVE="$REPO/.rota/live_click.md"
export WALK_WORDS="yes that all looks right, go ahead"
# The sample repository starts every night at its base commit. Night 50
# (2026-09-14) ran on the main that night 49 had merged echo_json into, so
# the first sentence asked for what already existed and the Developer
# read nine test files it had not written. Worktrees, batch branches and
# the merge go; the base is the commit the snapshot was onboarded at.
CLICK_ROOT="${CLICK_ROOT:-D:/repos/_AI/sample_repos/clickI}"
CLICK_BASE="${CLICK_BASE:-2c8cd3a}"
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
echo "== onboard $(date +%H:%M)"
# The last night's run database, kept beside the new one: `onboard --force`
# replaces it, and night 34's sessions were lost to night 35's start
# (2026-09-13) before they were read.
python -c "import sqlite3, os; os.path.exists('.rota/clickI.db') and sqlite3.connect('.rota/clickI.db').backup(sqlite3.connect('.rota/clickI_prev.db'))"
if [ "${GAUNTLET_WARM:-}" = "1" ] && python "$REPO/probes/warm_stamp.py" check clickI; then
  # A warm start: the snapshot walk.py wrote at the first slicing wake of an
  # earlier night. Onboarding's sessions are already in it; the night begins
  # at slicing. The stamp check above goes cold on its own when a brief, a
  # tool list, the graph or a predicate changed, or after four warm nights.
  echo "== warm start from .rota/clickI_warm.db (onboarding skipped)"
  rm -f "$REPO/.rota/clickI.db" "$REPO/.rota/clickI.db-wal" "$REPO/.rota/clickI.db-shm"
  python -c "import sqlite3; sqlite3.connect('.rota/clickI_warm.db').backup(sqlite3.connect('.rota/clickI.db'))"
  export WALK_FROM_WARM=1
else
python -m rota onboard clickI --root "$CLICK_ROOT" --force --profile "${GAUNTLET_PROFILE:-local}" 2>&1 | tail -2
fi
# A night starts from nothing. Night 36 (2026-09-13) ran its first sentence
# in minutes on night 35's leftover database: the wipe had not happened.
[ "${WALK_FROM_WARM:-}" = "1" ] || python -c "import sqlite3, sys; n = sqlite3.connect('.rota/clickI.db').execute('SELECT COUNT(*) FROM sessions').fetchone()[0]; sys.exit(0 if n == 0 else print(f'NOT FRESH: {n} sessions already in .rota/clickI.db; the wipe did not happen') or 3)" || exit 3
ollama_up
echo "== walk 1 $(date +%H:%M)"
python "$W" clickI "Add an echo_json(obj, indent=2) helper next to echo that prints an object as JSON." "keep it to the standard library json module, no new dependency" 250
ollama_up
echo "== walk 2 $(date +%H:%M)"
python "$W" clickI "Let confirm() take a default_on_eof flag: when stdin is closed it returns the default instead of aborting." "the flag defaults to False so nothing changes for existing callers" 250
ollama_up
echo "== walk 3 $(date +%H:%M)"
python "$W" clickI "Give version_option a show_python flag that appends the running Python version to the message." "the Python version comes from sys.version_info as major.minor.micro" 250
echo "GAUNTLET-DONE $(date +%H:%M)"
