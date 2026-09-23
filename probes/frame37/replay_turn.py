"""Replay s145 turn 6 (night 86's Developer write) on models given as
argv: model:think:timeout, e.g. qwen3.5:9b:true:300 qwen3:30b-a3b:true:1800.
think may be true, false or none. Output flushes per call."""
import json, sqlite3, sys, time, urllib.request

DB = ".rota/clickI_night86.db"
SID, SEQ = "s145", 6
SUBS = [
    ("When confirm() is invoked with default_on_eof=True and stdin is closed (EOF), confirm() must return the provided default value rather than raising an EOFError or aborting.",
     "When stdin is closed (EOF) and default_on_eof is True, confirm() returns the provided default value instead of raising an exception or aborting."),
    ("When confirm() is invoked with default_on_eof=False (or omitted) and stdin is closed, confirm() must raise an EOFError to signal the abrupt termination of input.",
     "When stdin is closed (EOF) and default_on_eof is False, confirm() behaves as before by raising an exception or aborting."),
    ("The default_on_eof parameter must be accepted by confirm() and stored in the context for the duration of the prompt operation.",
     "confirm() accepts a boolean argument named default_on_eof."),
]
c = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
system, user, recorded = c.execute(
    "select system, user, completion from turns where session_id=? and seq=?", (SID, SEQ)).fetchone()
user_sub = user
for old, new in SUBS:
    user_sub = user_sub.replace(old, new)


def call(model, think, user_text, timeout):
    body = {"model": model, "stream": False,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user_text}],
            "options": {"temperature": 0.0, "num_ctx": 12288}}
    if think is not None:
        body["think"] = think
    req = urllib.request.Request("http://127.0.0.1:11434/api/chat", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        out = json.loads(r.read())
    m = out["message"]
    return m.get("content", ""), m.get("thinking", "") or "", time.time() - t0, out.get("eval_count"), out.get("prompt_eval_count"), out.get("load_duration", 0) / 1e9


def judge(text):
    w = text.find("code.write")
    seg = text[w:] if w >= 0 else ""
    return {"has_write": w >= 0, "keeps_text_param": "text: str" in seg, "keeps_abort": "abort: bool" in seg,
            "renames_to_message": "message: str" in seg, "adds_flag": "default_on_eof: bool" in seg,
            "raises_EOFError": "raise EOFError" in seg, "isatty": "isatty()" in seg,
            "reads_more": text.count("TOOL: code.source"), "challenges": "challenge" in text}


def prefix_match(a, b):
    n = 0
    for x, y in zip(a, b):
        if x != y:
            break
        n += 1
    return n

print("recorded:", judge(recorded), "| recorded head:", recorded[:120].replace("\n", " | "), flush=True)
for spec in sys.argv[1:]:
    model, think, timeout = spec.rsplit(":", 2)
    think = {"true": True, "false": False, "none": None}[think]
    for label, txt in (("as recorded", user), ("night 70 criteria", user_sub)):
        try:
            content, thinking, dt, ev, pe, load = call(model, think, txt, int(timeout))
        except Exception as e:
            print(f"\n=== {model} think={think} | {label}: ERROR {type(e).__name__}: {str(e)[:160]}", flush=True)
            continue
        print(f"\n=== {model} think={think} | {label}: {dt:.0f}s (load {load:.0f}s), prompt {pe} tok, out {ev} tok, content {len(content)} chars, thinking {len(thinking)} chars", flush=True)
        print("   ", judge(content), "| prefix match with recorded:", prefix_match(content, recorded), flush=True)
        print("    head:", content[:400].replace("\n", " | "), flush=True)
        w = content.find("code.write")
        if w >= 0:
            print("    write:", content[w:w + 700].replace("\n", " | "), flush=True)
        if thinking:
            print("    thinking head:", thinking[:300].replace("\n", " | "), flush=True)
