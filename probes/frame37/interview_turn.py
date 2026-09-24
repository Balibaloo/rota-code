"""A targeted exit interview of one night session, by probe.

Replays the prompt of one turn of one session as a single call with no
tools, and appends recall questions. The answers are read against the
record, never taken as evidence on their own (the rule of
`rota/testkit/interview.py`: ask about inputs, never about reasons).

    python probes/frame37/interview_turn.py --db .rota/clickI_night91.db \
        --sid s154 --questions probes/frame37/q_developer.txt [--seq N]
        [--model qwen3.5:9b] [--think true|false|none] [--timeout 600]

Defaults: the session's last turn, the session's own model and window,
the think pin from the session's `pins_json`. One question per line in
the questions file. Output flushes per call. Ruled: Roman, 2026-09-24,
a manual interview by probe before any automated one.
"""
import argparse, json, sqlite3, sys, time, urllib.request

PREAMBLE = (
    "That session has ended and nothing you say now is recorded as work. "
    "You are not being asked to continue it, to justify it, or to do it "
    "better. Answer only from what was actually in front of you, and say "
    "you do not know rather than reconstructing something plausible. "
    "Call no tool. Answer each question on its own numbered line."
)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--sid", required=True)
    ap.add_argument("--seq", type=int, default=None)
    ap.add_argument("--questions", required=True)
    ap.add_argument("--model", default=None)
    ap.add_argument("--think", default=None, choices=["true", "false", "none"])
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--host", default="http://127.0.0.1:11434")
    a = ap.parse_args()

    c = sqlite3.connect(f"file:{a.db}?mode=ro", uri=True)
    c.row_factory = sqlite3.Row
    s = c.execute("select * from sessions where id=?", (a.sid,)).fetchone()
    if s is None:
        print(f"no session {a.sid}")
        return 2
    seq = a.seq
    if seq is None:
        seq = c.execute("select max(seq) from turns where session_id=?",
                        (a.sid,)).fetchone()[0]
    t = c.execute("select system, user, completion from turns where "
                  "session_id=? and seq=?", (a.sid, seq)).fetchone()
    if t is None:
        print(f"no turn {seq} in {a.sid}")
        return 2
    called = [r["fn"] for r in c.execute(
        "select fn from tool_calls where session_id=? order by seq", (a.sid,))]
    model = a.model or s["model"]
    num_ctx = s["num_ctx"] or 12288
    pins = json.loads(s["pins_json"] or "{}")
    think = {"true": True, "false": False, "none": None}[a.think] \
        if a.think else pins.get("think")

    questions = [q.strip() for q in open(a.questions, encoding="utf-8")
                 if q.strip()]
    body = [t["user"].rstrip(), "", "-------- 8< --------",
            "The session above has ended.",
            f"What it called, in order: {', '.join(called) or 'none'}", "",
            PREAMBLE, ""]
    body += [f"{i}. {q}" for i, q in enumerate(questions, 1)]
    user = "\n".join(body)

    req_body = {"model": model, "stream": False,
                "messages": [{"role": "system", "content": t["system"]},
                             {"role": "user", "content": user}],
                "options": {"temperature": 0.0, "num_ctx": num_ctx}}
    if think is not None:
        req_body["think"] = think
    req = urllib.request.Request(
        f"{a.host}/api/chat", data=json.dumps(req_body).encode(),
        headers={"Content-Type": "application/json"})
    print(f"interview {a.sid} turn {seq} of {s['wake_kind']} "
          f"({(s['wake_detail'] or '')[:40]}), role {s['role']}, model {model}, "
          f"think {think}, num_ctx {num_ctx}, prompt {len(user)} chars, "
          f"{len(called)} calls on record", flush=True)
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=a.timeout) as r:
            out = json.loads(r.read())
    except Exception as e:  # noqa: BLE001 - a probe reports and stops
        print(f"ERROR {type(e).__name__}: {str(e)[:200]}")
        return 1
    m = out["message"]
    content = m.get("content", "") or ""
    thinking = m.get("thinking", "") or ""
    print(f"{time.time() - t0:.0f}s, prompt {out.get('prompt_eval_count')} tok, "
          f"out {out.get('eval_count')} tok, thinking {len(thinking)} chars",
          flush=True)
    print("---- questions ----")
    for i, q in enumerate(questions, 1):
        print(f"{i}. {q}")
    print("---- answers ----")
    print(content.strip())
    print("---- recorded completion, head ----")
    print((t["completion"] or "")[:600])
    return 0


if __name__ == "__main__":
    sys.exit(main())
