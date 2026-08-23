"""
The second role rename, done once and reviewably: `gatekeeper` -> `vision_keeper`.

The first rename (`rename_roles.py`) turned `vision` into `gatekeeper` because
the role is answerable for what the project is and is not -- the gate. The name
said the gate and hid the other half: identity, purpose, the non-goals, the
rejection log, the account of what a program is *for* that onboarding opens
with. The original design called the role Vision; "Vision Keeper" says both
halves and keeps the gate.

Two-word name, so three spellings, chosen by where the word sits:

    identifier  gatekeeper        -> vision_keeper     (ids, code, data, code spans)
    title       Gatekeeper        -> Vision Keeper     (prose, briefs, labels)
    case ids    GK-               -> VK-

Compounds (`wake_gatekeeper`, `msg.question_gatekeeper`) take the identifier
form by the boundary rule. Lowercase stays the identifier in markdown too: the
docs write role ids in lowercase and the docs tests check them against the
graph, so there is no "vision keeper" prose form -- a lowercase role name is
its id wherever it appears.

Excludes itself and the first tool, because a tool that rewrites its own
rename table erases the record of what it did.

Run once, from the repo root:

    python -m rota.tools.rename_vision_keeper
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

OLD, ID, TITLE = "gatekeeper", "vision_keeper", "Vision Keeper"

ROOTS = [Path("rota"), Path("tests/rota"), Path("probes"), Path("plans")]
SUFFIXES = {".py", ".md", ".json", ".sql", ".js", ".html", ".txt", ".tools", ".yaml", ".yml"}
SKIP_NAMES = {"AGREED.md", "rename_roles.py", "rename_vision_keeper.py", "team-graph.html"}

LOWER = re.compile(r"(?<![A-Za-z0-9])gatekeeper(s?)(?![a-z0-9])")
UPPER = re.compile(r"(?<![A-Za-z0-9])Gatekeeper(s?)(?![a-z0-9])")
CASEID = re.compile(r"\bGK-")


def _ids(text: str) -> str:
    text = LOWER.sub(lambda m: ID + m.group(1), text)
    text = UPPER.sub(lambda m: TITLE + m.group(1), text)
    return CASEID.sub("VK-", text)


def substitute_markdown(text: str) -> str:
    """Markdown uses lowercase role ids in prose too (ROLES.md's "Reaches ..."
    lines are checked against the graph), so lowercase is the identifier
    everywhere and only the capitalised word becomes the title."""
    return _ids(text)


def substitute(path: Path, text: str) -> str:
    if path.suffix == ".md":
        return substitute_markdown(text)
    return _ids(text)


def targets() -> list[Path]:
    out = []
    for root in ROOTS:
        if not root.exists():
            continue
        for p in sorted(root.rglob("*")):
            if p.is_dir() or "__pycache__" in p.parts or ".git" in p.parts:
                continue
            if p.suffix in SUFFIXES and p.name not in SKIP_NAMES:
                out.append(p)
    return out


def git_mv(src: str, dst: str) -> None:
    if not Path(src).exists():
        print(f"  (already moved) {src}")
        return
    subprocess.run(["git", "mv", src, dst], check=True)
    print(f"  {src} -> {dst}")


def main() -> None:
    print("moving files")
    git_mv("rota/roles/prompts/gatekeeper", "rota/roles/prompts/vision_keeper")
    print("rewriting contents")
    changed = 0
    for path in targets():
        before = path.read_text(encoding="utf-8")
        after = substitute(path, before)
        if after != before:
            path.write_text(after, encoding="utf-8")
            changed += 1
            print(f"  {path}")
    print(f"{changed} files rewritten")
    print("\nnow check: rg -n 'gatekeeper|Gatekeeper|\\bGK-' rota tests/rota probes plans")


if __name__ == "__main__":
    sys.exit(main())
