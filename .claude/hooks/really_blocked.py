"""Stop hook: one push-back per response, asking whether the stop is real.

Blocks the first stop of a turn with the standing question; `stop_hook_active`
is set on the retry, which passes, so this can never loop.

Scoped per session: this is a shared worktree with several Claude Code
sessions open at once, and only the session(s) deliberately grinding
rota/COMPLETION.md's queue should be force-nudged to keep going. Every
other session (interactive work, one-off questions) should stop when it
wants to. `loop_session_ids.txt`, one CLAUDE_CODE_SESSION_ID per line, is
the allowlist; a session not listed there (or a missing/empty file) passes
through untouched.
"""
import json
import os
import sys

HOOKS_DIR = os.path.dirname(os.path.abspath(__file__))
ALLOWLIST_PATH = os.path.join(HOOKS_DIR, "loop_session_ids.txt")

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

if data.get("stop_hook_active"):
    sys.exit(0)

try:
    with open(ALLOWLIST_PATH, "r", encoding="utf-8") as f:
        allowed_session_ids = {line.strip() for line in f if line.strip()}
except FileNotFoundError:
    allowed_session_ids = set()

if data.get("session_id") not in allowed_session_ids:
    sys.exit(0)

print(json.dumps({
    "decision": "block",
    "reason": (
        "Standing instruction: before ending your response, ask whether "
        "you are actually blocked. If not, continue with the next item "
        "on the current plan (rota/COMPLETION.md is the queue). If "
        "really blocked, state precisely what only the user can "
        "resolve, then stop."
    ),
}))
