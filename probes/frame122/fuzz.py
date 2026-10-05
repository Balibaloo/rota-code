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


def outcome(parser, case: Case, sig: dict) -> str:
    """`right`: the parser reads the case's call as written, and no wrong
    call. `wrong`: it reads a call with other arguments. `refused`: neither."""
    calls = read(parser, case, sig)
    if wrong(case, calls):
        return "wrong"
    return "right" if any(name == case.fn for name, _ in calls) else "refused"


# The gate's slice: (kind, seed, count, the wide or inject flag). Frame 122's
# gains are the prose with apostrophes, and its wide code fuzz found the
# wrong calls (observed: frame 144 pass 3, the transitions from fb1bdba^,
# 2026-10-05).
SLICES = [("code", 1, 1500, False), ("code", 1, 2500, True),
          ("prose", 1, 2500, True), ("prose", 2, 1000, False)]
SLICE_FILE = ROOT / "tests" / "rota" / "fixtures" / "toolproto_fuzz_slice.json"


def slice_cases(kind: str, seed: int, n: int, flag: bool) -> tuple[Iterator[Case], dict]:
    if kind == "code":
        return code_calls(seed, n, flag), CODE_SIG
    return prose_calls(seed, n, flag), PROSE_SIG


def slice_key(kind: str, seed: int, n: int, flag: bool) -> str:
    return f"{kind}-{seed}-{n}-{'wide' if kind == 'code' and flag else 'inject' if flag else 'plain'}"


def slice_outcomes(parser) -> dict[str, dict[str, list[int]]]:
    """For each slice, the indices of the cases read right and read wrong.
    The rest are refused."""
    out = {}
    for s in SLICES:
        cases, sig = slice_cases(*s)
        got: dict[str, list[int]] = {"right": [], "wrong": []}
        for i, case in enumerate(cases):
            o = outcome(parser, case, sig)
            if o in got:
                got[o].append(i)
        out[slice_key(*s)] = got
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
    now = slice_outcomes(new)
    for key, got in now.items():
        was = before.get(key, {"right": [], "wrong": []})
        for o in ("right", "wrong"):
            gained = sorted(set(got[o]) - set(was[o]))
            lost = sorted(set(was[o]) - set(got[o]))
            print(f"{key} {o}: {len(got[o])}, gained {len(gained)}, lost {len(lost)}")
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
