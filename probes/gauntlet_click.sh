# The click gauntlet: onboard a fresh clickI, then three sentences with a yes-only
# principal, 24 turns a session. Restore clickI first (rota/COMPLETION.md, the
# walk log). Logs to stdout; the walk rows land in tests/rota/walks.jsonl.
P="$(cd "$(dirname "$0")" && pwd)"
cd "$P/.."
W="$P/walk.py"
export ROTA_ONESHOT=
ollama_up() { curl -s -m 5 localhost:11434/api/tags >/dev/null || { echo "ollama down at $(date +%H:%M), restarting"; powershell -NoProfile -Command "Start-Process ollama -ArgumentList serve -WindowStyle Hidden" >/dev/null 2>&1; sleep 15; }; }
export ROTA_MAX_ITERATIONS=24
export WALK_WORDS="yes that all looks right, go ahead"
echo "== onboard $(date +%H:%M)"
python -m rota onboard clickI --root "${CLICK_ROOT:-D:/repos/_AI/sample_repos/clickI}" --force --profile local 2>&1 | tail -2
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
