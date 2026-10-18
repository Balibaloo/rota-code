"""
The rulings search: which record already answers a question.

    python -m rota.tools.rulings single writer
    python -m rota.tools.rulings file rota/roles/api.py
    python -m rota.tools.rulings door criteria.specify
    python -m rota.tools.rulings law 12
    python -m rota.tools.rulings frame 244

Frame 287 counted the questions that went to Roman with the answer
already in a record. The search reads the records in a fixed order and
prints a few lines, so an agent finds a prior ruling before it asks.

The search keeps no cache, like `rota/tools/map.py`. The records change
in every frame, and one run reads them in well under a second. The
search never refuses: a zero hit prints the two files to read whole.

The match folds case and joins whitespace, so a phrase that a record
breaks across two lines still matches. A query of several words matches
a record unit when every word matches inside that one unit.
"""
from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from .. import paths

# About 3,000 tokens. A longer print costs the reader more than a second,
# narrower query does.
CAP_CHARS = 12_000
BODY_PER_SOURCE = 10
HEADING_CHARS = 100
SKIP_ENV = "ROTA_RULINGS_SKIP"

_HEADING = re.compile(r"^(#{1,3})\s+(.*\S)\s*$")
_KEYS = re.compile(r"^\s*[-*]?\s*Keys:\s*(.*)$")
_LAW = re.compile(r"^#{2,4}\s+(\d+)\.\s+(.*\S)")
_FRAME = re.compile(r"^###\s+(\d+)\.\s")


@dataclass
class Unit:
    """One record unit: a ledger entry, a law, a decision, a frame or a
    section of a read. A unit starts at a heading of level 1 to 3."""
    path: str
    line: int
    heading: str
    lines: list[str] = field(default_factory=list)
    keys: str = ""

    @property
    def text(self) -> str:
        return _fold(" ".join(self.lines))


@dataclass
class Source:
    name: str
    units: list[Unit]


def _fold(text: str) -> str:
    return " ".join(text.split()).casefold()


def _rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def split_units(path: Path, root: Path) -> list[Unit]:
    """Cut one markdown file at each heading of level 1 to 3. A level 4
    heading stays inside its unit, because a frame or a law owns it."""
    rel = _rel(path, root)
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    units: list[Unit] = []
    current = Unit(rel, 1, rel)
    in_fence = False
    for number, line in enumerate(text.splitlines(), start=1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        heading = None if in_fence else _HEADING.match(line)
        if heading:
            if current.lines:
                units.append(current)
            current = Unit(rel, number, heading.group(2), [heading.group(2)])
            continue
        current.lines.append(line)
        keys = _KEYS.match(line)
        if keys and not current.keys:
            current.keys = _fold(keys.group(1))
    if current.lines:
        units.append(current)
    return units


def sources(root: Path | None = None, wide: bool = False) -> list[Source]:
    """The scope, in the order of print. The ledger goes first when it
    exists and the environment does not leave it out. `wide` adds the
    composition page, CLAUDE.md and the other `plans/*.md` files last."""
    root = root or paths.REPO
    out: list[Source] = []
    ledger = root / "plans" / "rulings.md"
    if ledger.exists() and os.environ.get(SKIP_ENV) != "1":
        out.append(Source("plans/rulings.md", split_units(ledger, root)))
    for name in ("LAWS.md", "ROLES.md", "DECISIONS.md"):
        out.append(Source(f"rota/{name}", split_units(root / "rota" / name, root)))
    groups = (
        ("briefs", sorted((root / "rota" / "roles" / "prompts").glob("**/*.md"))),
        ("plans/archive", sorted((root / "plans" / "archive").glob("*.md"))),
        ("night reads", sorted((root / "plans").glob("night*-read.md"))),
    )
    for name, files in groups:
        units: list[Unit] = []
        for f in files:
            units.extend(split_units(f, root))
        out.append(Source(name, units))
    if wide:
        # Frame 293's probe: three of seven answers sat in these files.
        # They stay opt-in until a count shows what they cost the print.
        plans_dir = root / "plans"
        kept = {"rulings.md", "composition.md"}
        rest = [f for f in sorted(plans_dir.glob("*.md"))
                if f.name not in kept and not re.fullmatch(r"night.*-read\.md", f.name)]
        for name, files in (("plans/composition.md", [plans_dir / "composition.md"]),
                            ("CLAUDE.md", [root / "CLAUDE.md"]),
                            ("plans/*.md", rest)):
            units = []
            for f in files:
                units.extend(split_units(f, root))
            out.append(Source(name, units))
    return out


# ---------------------------------------------------------------------------
# The match
# ---------------------------------------------------------------------------

def word_matcher(words: list[str]):
    folded = [_fold(w) for w in words if _fold(w)]
    return lambda text: bool(folded) and all(w in text for w in folded)


def named_matcher(kind: str, number: str):
    """A record names "law 2" and not "law 21". "Laws 2 and 3" names
    law 2 too."""
    pattern = re.compile(rf"\b{kind}s? {re.escape(number)}(?!\d)")
    return lambda text: bool(pattern.search(text))


def _short(heading: str) -> str:
    heading = " ".join(heading.split())
    if len(heading) <= HEADING_CHARS:
        return heading
    return heading[:HEADING_CHARS - 3] + "..."


def search(srcs: list[Source], match, label: str) -> list[str]:
    """Key hits first, over every source, then the body hits per source.
    A unit that hits on its key line does not print again as a body hit."""
    keyed: list[Unit] = []
    bodies: list[tuple[Source, list[Unit]]] = []
    for src in srcs:
        hits = []
        for unit in src.units:
            if unit.keys and match(unit.keys):
                keyed.append(unit)
            elif match(unit.text):
                hits.append(unit)
        # A unit whose heading carries the query is the record about it.
        # It prints before a unit that only mentions the query.
        hits.sort(key=lambda u: 0 if match(_fold(u.heading)) else 1)
        bodies.append((src, hits))
    if not keyed and not any(hits for _, hits in bodies):
        return [f"nothing matched {label}; read rota/LAWS.md and "
                f"plans/composition.md whole"]
    lines = [f"KEY {_short(u.heading)} {u.path}:{u.line}" for u in keyed]
    for src, hits in bodies:
        lines.extend(f"{_short(u.heading)} {u.path}:{u.line}"
                     for u in hits[:BODY_PER_SOURCE])
        if len(hits) > BODY_PER_SOURCE:
            lines.append(f"... {len(hits) - BODY_PER_SOURCE} more in {src.name}")
    return _capped(lines, keyed, bodies)


def _capped(lines, keyed, bodies) -> list[str]:
    total = sum(len(line) + 1 for line in lines)
    if total <= CAP_CHARS:
        return lines
    out, used = [], 0
    for line in lines:
        if used + len(line) + 1 > CAP_CHARS:
            break
        out.append(line)
        used += len(line) + 1
    out.append(f"cap of {CAP_CHARS} characters reached; hits per source:")
    if keyed:
        out.append(f"  keys {len(keyed)}")
    out.extend(f"  {src.name} {len(hits)}" for src, hits in bodies if hits)
    return out


# ---------------------------------------------------------------------------
# The forms
# ---------------------------------------------------------------------------

def query_words(words: list[str], root: Path | None = None, wide: bool = False) -> str:
    return "\n".join(search(sources(root, wide),word_matcher(words), " ".join(words)))


def query_name(name: str, root: Path | None = None, wide: bool = False) -> str:
    """`file` and `door`: a word search on the path's tail or the name.
    The backtick form is a substring of the bare name, so one match
    covers both."""
    tail = name.replace("\\", "/").rstrip("/").rsplit("/", 1)[-1]
    return "\n".join(search(sources(root, wide),word_matcher([tail]), tail))


def query_law(number: str, root: Path | None = None, wide: bool = False) -> str:
    root = root or paths.REPO
    head: list[str] = []
    for unit in split_units(root / "rota" / "LAWS.md", root):
        law = _LAW.match("### " + unit.heading)
        if law and law.group(1) == number:
            body = [l.strip() for l in unit.lines[1:] if l.strip()][:5]
            head = [f"LAW {unit.heading} {unit.path}:{unit.line}"]
            head.extend(f"  {l}" for l in body)
            break
    if not head:
        head = [f"no law {number} in rota/LAWS.md"]
    rest = search(sources(root, wide),named_matcher("law", number), f"law {number}")
    return "\n".join(head + rest)


def query_frame(number: str, root: Path | None = None, wide: bool = False) -> str:
    root = root or paths.REPO
    files = [root / "plans" / "stack.md",
             *sorted((root / "plans" / "archive").glob("*.md"), reverse=True)]
    head: list[str] = []
    for f in files:
        for unit in split_units(f, root):
            frame = _FRAME.match("### " + unit.heading)
            if frame and frame.group(1) == number:
                head = [f"FRAME {_short(unit.heading)} {unit.path}:{unit.line}"]
                site = next((l.strip() for l in unit.lines if "Site:" in l), "")
                if site:
                    head.append(f"  {site[:300]}")
                break
        if head:
            break
    if not head:
        head = [f"no frame {number} in plans/stack.md or plans/archive"]
    rest = search(sources(root, wide),named_matcher("frame", number), f"frame {number}")
    return "\n".join(head + rest)


USAGE = ("usage: python -m rota.tools.rulings [--wide] <words...> | file <path> | "
         "door <name> | law <n> | frame <n>")


def main(argv: list[str] | None = None, root: Path | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    wide = "--wide" in args
    args = [a for a in args if a != "--wide"]
    if not args:
        print(USAGE)
        return 2
    form, rest = args[0], args[1:]
    if form in ("law", "frame") and len(rest) == 1 and rest[0].isdigit():
        text = (query_law if form == "law" else query_frame)(rest[0], root, wide)
    elif form in ("file", "door") and len(rest) == 1:
        text = query_name(rest[0], root, wide)
    else:
        # A form word with the wrong argument is a word search. The
        # search never refuses.
        text = query_words(args, root, wide)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
