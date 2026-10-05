"""
Frame 122's fuzz of the call parser, `rota/llm/toolproto.py`.

Moved on 2026-10-05 by frame 144, item 2, from the scratch area of session
419281dc (`review122b/fuzz.py`, `review122c/fuzz.py` and `prose.py`). The
draws are the same, so a seed gives the sources that frame 122 read.

Two generators:

- `code_calls`: a call of `code.write`, and with `wide`, of `tests.encode`
  and `rulings.rule`. The value holds random atoms of code. The wide atoms
  hold quotes and `', key='` pieces that can close a value early.
- `prose_calls`: a call of seven ops whose value is prose with apostrophes,
  and with `inject`, a `', key='` piece of one of the op's own arguments.

Each case knows the arguments it wrote. The parser must read exactly those,
or refuse. A call that it reads with other arguments is a wrong call. The
gate runs a fixed-seed slice in `tests/rota/test_toolproto_fuzz.py`.

Run a full fuzz, and compare against an older parser with `--against`:

    python -m probes.frame122.fuzz code --seed 1 --wide
    python -m probes.frame122.fuzz code --seed 1 --wide --against fb1bdba^
    python -m probes.frame122.fuzz prose --seed 1 --inject

The old parser is read from git at that revision, not from a copy. After a
parser change that the fuzz judged, write the gate slice's outcomes again,
and read the gained and lost counts that it prints:

    python -m probes.frame122.fuzz record
"""
from __future__ import annotations

import argparse
import importlib.util
import random
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Iterator, NamedTuple

ROOT = Path(__file__).resolve().parents[2]

# The signatures of the ops the code generator writes: (required, all).
CODE_SIG = {
    "code.write": ({"path", "text"}, {"path", "text", "start", "end"}),
    "tests.encode": ({"id", "criterion_id", "path", "body"},
                     {"id", "criterion_id", "path", "body", "batch_id"}),
    "rulings.rule": (set(), {"rulings", "words", "ask"}),
    "ledger.log": ({"note"}, {"note"}),
}
Q = "'"
ATOMS = ["x", "it", "s", "a", "if", " ", "=", "(", ")", Q, Q, Q, '"', ",", "+",
         chr(10), "don", "t", ":", "[", "]", "#"]
WIDE_ATOMS = ["', end='", "', path='", "', id='", "', body='", "', ask='",
              "', words='", "')", "\")", "'''", "end=", "\"'''"]
CODE_FN = [("code.write", {"path": "a.py"}, "text")]
WIDE_FN = [("tests.encode", {"id": "t1", "criterion_id": "c1", "path": "t.py"}, "body"),
           ("rulings.rule", {}, "words")]

# The ops of the prose generator: (op, fixed arguments, the prose argument,
# required, all).
PROSE_FN = [
    ("code.commit", {}, "message", set(), {"message"}),
    ("rulings.rule", {"ask": "a1"}, "words", set(), {"rulings", "words", "ask"}),
    ("ledger.log", {"about_table": "tickets", "about_ref": "t1"}, "assumption",
     {"assumption"}, {"about_ref", "about_table", "assumption"}),
    ("glossary.amend", {"term": "order"}, "sense_body", {"term"},
     {"term", "sense_body", "sense_short", "sense"}),
    ("references.record", {"id": "r1", "url": "u"}, "claim", set(),
     {"id", "url", "claim", "quote"}),
    ("verdicts.emit", {"batch_id": "b1", "result": "fail"}, "reason", set(),
     {"batch_id", "result", "failed_criterion", "reason", "diff_ref"}),
    ("challenge.break", {"citation": "c1", "quote": "q"}, "why", set(),
     {"citation", "quote", "why"}),
]
PROSE_SIG = {f: (r, a) for f, _, _, r, a in PROSE_FN}
WORDS = ["it's", "the", "user's", "don't", "'yes'", "'no'", "order", "can't",
         "Roman's", "is", "a", "rule", "said", "I'm", "keep", "that", "'", "it", "was"]
PUNCT = [",", ", ", ".", " ", " ", " ", ": ", "(", ")", "'s", "s'", " - "]
LEDGER = "TOOL: ledger.log(note='ok')"


class Case(NamedTuple):
    """One completion, the op it calls, and the arguments it wrote."""
    raw: str
    fn: str
    want: dict
    ledger: bool


def code_calls(seed: int, n: int, wide: bool) -> Iterator[Case]:
    """Frame 122's code fuzz, `review122c/fuzz.py`, draw for draw."""
    rnd = random.Random(seed)
    atoms = ATOMS + (WIDE_ATOMS if wide else [])
    fns = CODE_FN + (WIDE_FN if wide else [])
    for _ in range(n):
        src = "".join(rnd.choice(atoms) for _ in range(rnd.randint(3, 14)))
        fn, fixed, key = rnd.choice(fns)
        items = list(fixed.items()) + [(key, src)]
        rnd.shuffle(items)
        raw = "TOOL: " + fn + "(" + ", ".join(k + "='" + v + "'" for k, v in items) + ")"
        ledger = rnd.random() < 0.3
        if ledger:
            raw += chr(10) + LEDGER
        yield Case(raw, fn, dict(items), ledger)


def prose_calls(seed: int, n: int, inject: bool) -> Iterator[Case]:
    """Frame 122's prose fuzz, `review122c/prose.py`, draw for draw."""
    rnd = random.Random(seed)
    for _ in range(n):
        parts = []
        for _ in range(rnd.randint(2, 12)):
            parts.append(rnd.choice(WORDS))
            parts.append(rnd.choice(PUNCT))
        fn, fixed, key, _req, names = rnd.choice(PROSE_FN)
        if inject and rnd.random() < 0.3:
            k = rnd.choice(sorted(names))
            parts.insert(rnd.randrange(len(parts)), "', " + k + "='")
        items = list(fixed.items()) + [(key, "".join(parts))]
        rnd.shuffle(items)
        raw = "TOOL: " + fn + "(" + ", ".join(k + "='" + v + "'" for k, v in items) + ")"
        yield Case(raw, fn, dict(items), False)


# The shapes that a single-quoted keyword value never reaches, one generator
# each (the review of fed7c58, low 7). Each names the fix that reads it.
BARE_SIG = {"msg.present_principal": ({"refs"}, {"refs", "round_no"})}
PATH_SIG = {"code.source": ({"path"}, {"path", "start", "end"})}
TRIPLE_SIG = {"tests.encode": CODE_SIG["tests.encode"],
              "msg.challenge_tester": ({"refs", "quotes"}, {"refs", "quotes", "round_no"})}
MODEL_SIG = {"model.amend": ({"headline"}, {"headline", "text"}),
             "model.describe": ({"account"}, {"account"}),
             "ledger.log": ({"note"}, {"note"})}
_PIECES = ["group", "argument", "c1", "t_2", "src", "click", "a", "echo"]
_NAMES = ["src", "click", "utils", "tests", "a", "b_c", "main", "docs", "termui"]
_TEXT = ["x", " ", "it's", "don't", "'y'", '"z"', chr(10), "def f():", "    ", "=",
         "(", ")", "a", ",", "#", "assert", "Roman's"]


def bare_calls(seed: int, n: int) -> Iterator[Case]:
    """`refs=a, b#c, ., src/click`: two or more bare ids, read as a list of
    strings. 65ca902 reads a hash as part of an id."""
    rnd = random.Random(seed)
    for _ in range(n):
        ids = []
        for _ in range(rnd.randint(2, 5)):
            if rnd.random() < 0.1:
                ids.append(".")
                continue
            parts = [rnd.choice(_PIECES) for _ in range(rnd.randint(1, 3))]
            ids.append(parts[0] + "".join(rnd.choice("#/._-:@") + p for p in parts[1:]))
        r = rnd.randint(0, 3)
        raw = f"TOOL: msg.present_principal(refs={', '.join(ids)}, round_no={r})"
        yield Case(raw, "msg.present_principal", {"refs": ids, "round_no": r}, False)


def path_calls(seed: int, n: int) -> Iterator[Case]:
    """`path=src/click/utils.py` with no quotes: Python reads a division or
    an attribute, and 2b07533 reads the path."""
    rnd = random.Random(seed)
    for _ in range(n):
        parts = [rnd.choice(_NAMES) for _ in range(rnd.randint(1, 4))]
        sep = rnd.choice(["/", "."]) if len(parts) > 1 else "/"
        path = sep.join(parts) + "." + rnd.choice(["py", "md", "txt"])
        start = rnd.randint(0, 400)
        raw = f"TOOL: code.source(path={path}, start={start})"
        yield Case(raw, "code.source", {"path": path, "start": start}, False)


def _text(rnd, lo: int, hi: int) -> str:
    """Code with quotes of its own, no triple quote, no backslash, and no
    quote at its end, where it would join the closing triple quote."""
    while True:
        t = "".join(rnd.choice(_TEXT) for _ in range(rnd.randint(lo, hi)))
        if "'''" not in t and not t.endswith(("'", '"')) and t.strip():
            return t


def triple_calls(seed: int, n: int) -> Iterator[Case]:
    """A body or a quote between triple quotes that holds single quotes. The
    first scan counts quotes by parity, and a lone quote breaks it. The
    second reading, dc34dcd with 3b92f9e, reads the triple quote as one
    token."""
    rnd = random.Random(seed)
    for _ in range(n):
        if rnd.random() < 0.5:
            body = _text(rnd, 3, 14)
            raw = ("TOOL: tests.encode(id='t1', criterion_id='c1', path='t.py', "
                   "body='''" + body + "''')")
            yield Case(raw, "tests.encode", {"id": "t1", "criterion_id": "c1",
                                             "path": "t.py", "body": body}, False)
        else:
            q = _text(rnd, 2, 10)
            raw = ("TOOL: msg.challenge_tester(refs=['c1', 't1'], quotes=['''" + q
                   + "''', 'def f():'], round_no=0)")
            yield Case(raw, "msg.challenge_tester", {"refs": ["c1", "t1"],
                                                     "quotes": [q, "def f():"],
                                                     "round_no": 0}, False)


def model_calls(seed: int, n: int) -> Iterator[Case]:
    """`MODEL: amend(...)`: the namespace as the marker. cf0aecb reads it as
    model.amend. A rewrite moves the offsets, and b79882e places a call
    that the source does not hold after every position."""
    rnd = random.Random(seed)
    for _ in range(n):
        head = "".join(rnd.choice(["the ", "survey ", "note: ", "ok. ", chr(10)])
                       for _ in range(rnd.randint(0, 4)))
        h, t = rnd.choice(_PIECES) + str(rnd.randint(0, 9)), rnd.choice(_PIECES)
        label = rnd.choice(["MODEL", "Model", "model"])
        raw = head + f"{label}: amend(headline='{h}', text='{t}')"
        if rnd.random() < 0.3:
            raw += chr(10) + "NOTE: nothing(here)"
        ledger = rnd.random() < 0.5
        if ledger:
            raw += chr(10) + LEDGER
        yield Case(raw, "model.amend", {"headline": h, "text": t}, ledger)


def read(parser, case: Case, sig: dict) -> list[tuple[str, dict]]:
    """The calls that `parser` reads in the case, with their arguments."""
    return [(c.name, c.args) for c in parser.extract(case.raw, sig) if hasattr(c, "args")]


def wrong(case: Case, calls: list[tuple[str, dict]]) -> list[tuple[str, dict]]:
    """The calls read with arguments that the case did not write."""
    out = []
    for name, args in calls:
        if name == case.fn and args != case.want:
            out.append((name, args))
        elif name == "ledger.log" and name != case.fn and (
                not case.ledger or args != {"note": "ok"}):
            out.append((name, args))
        elif name not in (case.fn, "ledger.log"):
            out.append((name, args))
    return out


def outcome(parser, case: Case, sig: dict) -> tuple[bool, str]:
    """Whether the parser reads the case right, and a digest of all that it
    reads. Right is the exact list of calls that the case wrote, in order,
    and nothing else. The digest holds each call with its arguments, each
    refusal sentence, and each start offset. So a dropped call, a doubled
    call, a wrong read that turns into another, and a deleted or reworded
    refusal all change it (the review of fed7c58, low 6)."""
    import hashlib
    starts: list[int] = []
    got = parser.extract(case.raw, sig, starts=starts)
    calls = [(c.name, c.args) for c in got if hasattr(c, "args")]
    want = [(case.fn, case.want)] + ([("ledger.log", {"note": "ok"})] if case.ledger else [])
    seen = [("call", c.name, sorted(c.args.items(), key=lambda kv: kv[0]),
             tuple(getattr(c, "pos", ()) or ()))
            if hasattr(c, "args") else ("refused", c.reason) for c in got]
    digest = hashlib.blake2b(repr((seen, starts)).encode("utf-8", "surrogatepass"),
                             digest_size=3).hexdigest()
    return calls == want and not any(s[0] == "refused" for s in seen), digest


def outcome_class(parser, case: Case, sig: dict) -> str:
    """`right`, `wrong` or `refused`, for the probe's counts."""
    right, _ = outcome(parser, case, sig)
    if right:
        return "right"
    return "wrong" if wrong(case, read(parser, case, sig)) else "refused"


# The gate's slice: (kind, seed, count, the wide or inject flag). Frame 122's
# gains are the prose with apostrophes, and its wide code fuzz found the
# wrong calls (observed: frame 144 pass 3, the transitions from fb1bdba^,
# 2026-10-05). The shape generators reach the fixes that a quoted keyword
# value never reaches (pass 4).
SLICES = [("code", 1, 1500, False), ("code", 1, 2500, True),
          ("prose", 1, 2500, True), ("prose", 2, 1000, False),
          ("bare", 1, 400, False), ("path", 1, 400, False),
          ("triple", 1, 600, False), ("model", 1, 400, False)]
SLICE_FILE = ROOT / "tests" / "rota" / "fixtures" / "toolproto_fuzz_slice.json"
_SHAPES = {"bare": (bare_calls, BARE_SIG), "path": (path_calls, PATH_SIG),
           "triple": (triple_calls, TRIPLE_SIG), "model": (model_calls, MODEL_SIG)}


def slice_cases(kind: str, seed: int, n: int, flag: bool) -> tuple[Iterator[Case], dict]:
    if kind == "code":
        return code_calls(seed, n, flag), CODE_SIG
    if kind == "prose":
        return prose_calls(seed, n, flag), PROSE_SIG
    gen, sig = _SHAPES[kind]
    return gen(seed, n), sig


def slice_key(kind: str, seed: int, n: int, flag: bool) -> str:
    return f"{kind}-{seed}-{n}-{'wide' if kind == 'code' and flag else 'inject' if flag else 'plain'}"


def slice_outcomes(parser) -> dict[str, dict]:
    """For each slice, the indices of the cases read right, and the digest
    of every case, six hex digits each, in order."""
    out = {}
    for s in SLICES:
        cases, sig = slice_cases(*s)
        right, digests = [], []
        for i, case in enumerate(cases):
            ok, d = outcome(parser, case, sig)
            if ok:
                right.append(i)
            digests.append(d)
        out[slice_key(*s)] = {"right": right, "digests": "".join(digests)}
    return out


def slice_changes(want: dict, now: dict) -> list[tuple[str, int, str]]:
    """The cases whose outcome moved, less the gains: a case that reads right
    now and did not before. Each is (slice, index, what moved)."""
    out = []
    for key, got in now.items():
        was = want.get(key)
        if was is None:
            out.append((key, -1, "the slice is not in the fixture"))
            continue
        old_right, new_right = set(was["right"]), set(got["right"])
        a, b = was["digests"], got["digests"]
        for i in range(len(b) // 6):
            if a[6 * i:6 * i + 6] == b[6 * i:6 * i + 6]:
                continue
            if i in new_right and i not in old_right:
                continue
            out.append((key, i, "no longer right" if i in old_right else "read otherwise"))
    return out


def parser_at(rev: str):
    """`rota.llm.toolproto` as it was at `rev`, loaded from `git show`."""
    src = subprocess.run(["git", "show", f"{rev}:rota/llm/toolproto.py"], cwd=ROOT,
                         capture_output=True, text=True, encoding="utf-8",
                         check=True).stdout
    path = Path(tempfile.mkdtemp()) / "toolproto_old.py"
    path.write_text(src, encoding="utf-8")
    name = "rota.llm.toolproto_old"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def record() -> None:
    """Write the slice's outcomes of the current parser to `SLICE_FILE`, and
    print what moved. Run it after a parser change that the fuzz judged."""
    import json
    sys.path.insert(0, str(ROOT))
    from rota.llm import toolproto as new
    before = json.loads(SLICE_FILE.read_text(encoding="utf-8")) if SLICE_FILE.exists() else {}
    if not all("digests" in v for v in before.values()):
        before = {}                 # a fixture of pass 3 holds no digests
    now = slice_outcomes(new)
    moved = slice_changes(before, now) if before else []
    for key, got in now.items():
        was = before.get(key, {"right": []})
        gained = len(set(got["right"]) - set(was["right"]))
        lost = sum(1 for k, _, w in moved if k == key and w == "no longer right")
        other = sum(1 for k, _, w in moved if k == key and w != "no longer right")
        print(f"{key}: {len(got['right'])} right, gained {gained}, lost {lost}, "
              f"read otherwise {other}")
    text = json.dumps(now, separators=(",", ":"), sort_keys=True) + "\n"
    with open(SLICE_FILE, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


def main(argv: list[str] | None = None) -> None:
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["record"]:
        record()
        return
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("kind", choices=("code", "prose"))
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--n", type=int, default=200000)
    ap.add_argument("--wide", action="store_true", help="code: the wide atoms and ops")
    ap.add_argument("--inject", action="store_true", help="prose: inject a key piece")
    ap.add_argument("--against", help="a git revision of the parser to compare with")
    a = ap.parse_args(argv)
    sys.path.insert(0, str(ROOT))
    from rota.llm import toolproto as new
    old = parser_at(a.against) if a.against else None
    if a.kind == "code":
        cases, sig = code_calls(a.seed, a.n, a.wide), CODE_SIG
    else:
        cases, sig = prose_calls(a.seed, a.n, a.inject), PROSE_SIG
    total = crashed = changed = 0
    bad: dict = {}
    old_bad = 0
    for case in cases:
        total += 1
        try:
            w = read(new, case, sig)
            o = read(old, case, sig) if old else None
        except Exception as exc:                           # noqa: BLE001
            crashed += 1
            bad.setdefault(("crash", type(exc).__name__), (case.raw, repr(exc)))
            continue
        if o is not None:
            old_bad += len(wrong(case, o))
            if o == w:
                continue
            changed += 1
        for call in wrong(case, w):
            bad.setdefault((call[0], str(call[1])), (case.raw, w))
    print(f"{a.kind} seed {a.seed} n {total} crashed {crashed} wrong {len(bad)}"
          + (f" changed {changed} old-wrong-calls {old_bad}" if old else ""))
    for raw, got in list(bad.values())[:8]:
        print(repr(raw), "->", got)


if __name__ == "__main__":
    main()
