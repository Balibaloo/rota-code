"""
Group the package by what each module *is*.

Twenty-five modules in one flat directory answers "what is in rota" and not
"what kind of thing is this". The groups below are the answer, and they are the
same distinctions the design already makes:

    design/   the wiring, and the loader that makes it authoritative
    core/     the machine — one message in, one atomic commit out
    roles/    what a role can do and what it is told
    llm/      the model seam, and the evidence of what a model did
    cockpit/  making a running system visible
    testkit/  the machinery tests are built from
    tools/    one-off migrations and analysers

`api.py` goes to `roles/` rather than `core/` because it is one function per
graph edge — it is the roles' surface, not the machine's. `harness.py` goes to
`core/` for the mirror reason: running a batch's tests is a step in the delivery
loop, not a role's choice.

Done now rather than later because cassette keys hash the prompt, and prompt
paths moving after cassettes exist would invalidate evidence for nothing.

Run once, from the repo root:

    python -m rota.tools.regroup
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

GROUPS: dict[str, tuple[str, ...]] = {
    "design": ("graph",),
    "core": ("db", "scheduler", "predicates", "loop", "runner", "sandbox",
             "boot", "config", "lifecycle", "harness"),
    "roles": ("api", "prompts", "principal", "validators"),
    "llm": ("llm", "toolproto", "toolschema", "cassettes"),
    "cockpit": ("server", "inspect_api", "traceview"),
    "testkit": ("coverage", "fixtures"),
}

# `cockpit.py` becomes `cockpit/server.py`: a package named for the thing and a
# module named for what it does, rather than `cockpit/cockpit.py`.
RENAMES = {"cockpit": "server"}

# Data that belongs with the group that reads it.
#
# `design/` is absent because the group *is* that directory — `graph.json` and
# friends already live there and `graph.py` moves in beside them. Listing it
# asked git to move a directory into itself.
ASSETS = {
    "roles": ("prompts",),          # the mode pieces
    "core": ("schema.sql",),
    "cockpit": ("viewer.html", "static"),
}

PKG = Path("rota")
TESTS = Path("tests/rota")


def home_of() -> dict[str, str]:
    """module stem -> group."""
    out = {}
    for group, mods in GROUPS.items():
        for mod in mods:
            out[mod] = group
    return out


def run(*args: str) -> None:
    subprocess.run(args, check=True)


def move() -> dict[str, str]:
    home = home_of()
    old_for = {new: old for old, new in RENAMES.items()}

    for group in GROUPS:
        (PKG / group).mkdir(exist_ok=True)
        init = PKG / group / "__init__.py"
        if not init.exists():
            init.write_text("", encoding="utf-8")
            run("git", "add", str(init))

    for mod, group in home.items():
        src = PKG / f"{old_for.get(mod, mod)}.py"
        dst = PKG / group / f"{mod}.py"
        if src.exists() and not dst.exists():
            run("git", "mv", str(src), str(dst))
            print(f"  {src} -> {dst}")

    for group, assets in ASSETS.items():
        for asset in assets:
            src, dst = PKG / asset, PKG / group / asset
            if src.exists() and not dst.exists():
                run("git", "mv", str(src), str(dst))
                print(f"  {src} -> {dst}")
    return home


# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

def rewrite(text: str, home: dict[str, str], *, own_group: str | None) -> str:
    """
    Point every import at the module's new home.

    Three forms appear in this tree, and each needs a different answer:

        from .db import X          relative, inside the package
        from . import db           relative, module as a name
        from rota.core.db import X      absolute, from tests

    A relative import stays relative when both ends land in the same group, and
    grows a dot when they do not.
    """
    def rel(mod: str) -> str:
        group = home.get(mod)
        if group is None:
            return f".{mod}"                       # not moving: paths, __init__
        return f".{mod}" if group == own_group else f"..{group}.{mod}"

    if own_group:
        # `^\s*`, not `^`. Deferred imports inside functions are indented, and a
        # start-of-line anchor walks straight past them — they then fail at call
        # time rather than import time, so the module loads, the suite collects,
        # and the failure surfaces as a session error deep in a test.
        text = re.sub(r"^(\s*)from \.(\w+) import",
                      lambda m: f"{m.group(1)}from {rel(m.group(2))} import",
                      text, flags=re.M)
        # `from . import graph as g` -> one clause per module, since they may
        # now live in different groups.
        def split_bare(m):
            clause = m.group(1)
            # A parenthesised import spans lines, so the regex sees only its
            # first fragment — splitting that leaves the continuation orphaned
            # and the file unparseable. `runner.py` was the one, and it is
            # cheaper to leave those for a person than to write a parser.
            if "(" in clause or clause.rstrip().endswith("\\"):
                return m.group(0)
            parts = [p.strip() for p in clause.split(",") if p.strip()]
            if not parts:
                return m.group(0)          # a continuation line, not an import
            lines = []
            for part in parts:
                name = part.split()[0]
                group = home.get(name)
                if group is None:
                    lines.append(f"from . import {part}")
                elif group == own_group:
                    lines.append(f"from . import {part}")
                else:
                    lines.append(f"from ..{group} import {part}")
            return "\n".join(lines)
        text = re.sub(r"^from \. import ([^\n]+)$", split_bare, text, flags=re.M)
        # `paths` moved nowhere but the importer went down a level.
        text = re.sub(r"^from \. import paths$", "from .. import paths", text, flags=re.M)
        text = re.sub(r"^from \.\. import paths$", "from .. import paths", text, flags=re.M)

    # Absolute forms, but **only on import lines and `python -m` invocations**.
    #
    # A bare `\brota\.(\w+)\b` over the whole file also rewrites string
    # literals, and it did: `tmp_path / "rota.db"` became `"rota.db"`,
    # silently renaming every test's temporary database. A module path and a
    # filename look identical to a regex; the line they sit on does not.
    def qualify(m):
        mod = m.group(1)
        group = home.get(mod)
        if group is None:
            return m.group(0)
        # Already qualified. Only bites when a module's name equals its group's
        # — `rota.llm.llm` — where a second pass reads the group as the module
        # and produces `rota.llm.llm.llm`. Re-running a migration should be a
        # no-op, and this one was not.
        if group == mod and m.string[m.end():m.end() + 1 + len(mod)] == f".{mod}":
            return m.group(0)
        return f"rota.{group}.{mod}"

    lines = []
    for line in text.split("\n"):
        stripped = line.lstrip()
        if stripped.startswith(("from rota", "import rota")) or "python -m rota." in line:
            line = re.sub(r"\brota\.(\w+)\b", qualify, line)
            # `from rota import db, llm` -> per-module: they may now differ.
            m = re.match(r"^(\s*)from rota import ([^\n]+)$", line)
            if m:
                indent, clause = m.group(1), m.group(2)
                out = []
                for part in (p.strip() for p in clause.split(",")):
                    if not part:
                        continue
                    group = home.get(part.split()[0])
                    out.append(f"{indent}from rota.{group} import {part}" if group
                               else f"{indent}from rota import {part}")
                line = "\n".join(out)
        lines.append(line)
    return "\n".join(lines)


def main() -> None:
    home = move()

    print("rewriting imports")
    targets = [p for p in PKG.rglob("*.py") if "__pycache__" not in p.parts]
    targets += [p for p in TESTS.rglob("*.py") if "__pycache__" not in p.parts]
    changed = 0
    for path in sorted(targets):
        group = path.parent.name if path.parent.name in GROUPS else None
        if path.parts[:2] == ("rota", "tools"):
            group = None                      # tools already sit one level down
        before = path.read_text(encoding="utf-8")
        after = rewrite(before, home, own_group=group)
        if after != before:
            path.write_text(after, encoding="utf-8")
            changed += 1
            print(f"  {path}")
    print(f"{changed} files rewritten")
    print("\nnow: python -m pytest tests/rota -q")


if __name__ == "__main__":
    sys.exit(main())
