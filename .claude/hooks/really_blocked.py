"""Stop hook: one push-back per response, asking whether the stop is real.

Blocks the first stop of a turn with the standing question; `stop_hook_active`
is set on the retry, which passes, so this can never loop.
"""
import json
import sys

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

if data.get("stop_hook_active"):
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
