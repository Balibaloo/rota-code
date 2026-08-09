"""
The role rename, done once and reviewably.

Four roles were named for the *subject they knew about* rather than for what they
are answerable for, which is how a job is normally named:

    client    -> principal        wanting it, and ruling on it
    interface -> liaison          the conversation with the principal
    vision    -> gatekeeper       what the project is, and isn't
    domain    -> terminologist    one meaning per word

`vision` also collided with `Vision` the artefact, the only collision at L0.

Renaming by hand across 1200 occurrences invites exactly the drift the rename is
meant to remove, so it is mechanical -- but a blind substitution is wrong twice
over: `clientX` and `getBoundingClientRect` are DOM API, and a few sentences use
the word as ordinary English. Both are protected explicitly rather than noticed
afterwards.

It also excludes itself. The first run did not, and rewrote its own rename table
into `client -> client` before finishing the other 53 files -- harmless, because
the table was already in memory, but a tool that erases its own record of what it
did is not a record.

Run once, from the repo root:

    python -m rota.tools.rename_roles
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

RENAMES = {
    "client":    "principal",
    "interface": "liaison",
    "vision":    "gatekeeper",
    "domain":    "terminologist",
}

# Identifiers that merely contain a stem and mean something else entirely.
PROTECTED = [
    "clientX", "clientY", "clientWidth", "clientHeight", "getBoundingClientRect",
    # Ordinary English, in the seam module's own docstrings.
    "satisfy one interface",
    "The interface is deliberately narrow",
    "Same interface, stdin",
]

ROOTS = [Path("rota"), Path("tests/rota")]
# `.tools` was missed on the first pass, and nothing caught it: the mode
# allowlists are data the sandbox reads, so a stale name there does not fail to
# import, it just silently narrows the working set. Five tests found it.
SUFFIXES = {".py", ".md", ".json", ".sql", ".js", ".html", ".txt", ".tools"}
SKIP_NAMES = {"AGREED.md",          # its table is *about* the legacy names
              "rename_roles.py"}    # and so is this


def targets() -> list[Path]:
    out = []
    for root in ROOTS:
        for p in sorted(root.rglob("*")):
            if p.is_dir() or "__pycache__" in p.parts:
                continue
            if p.suffix in SUFFIXES and p.name not in SKIP_NAMES:
                out.append(p)
    return out


def substitute(text: str) -> str:
    """
    Rename each stem where it is a *component* of an identifier or a word.

    `(?<![A-Za-z0-9])` and `(?![a-z0-9])` make `_` and a following capital count
    as boundaries, so `client_present` and `ClientBackend` are both caught while
    `clientele` is not. Case is preserved for the capitalised form only, which is
    all the sources use.
    """
    for i, phrase in enumerate(PROTECTED):
        text = text.replace(phrase, f"\x00{i}\x00")

    for old, new in RENAMES.items():
        text = re.sub(rf"(?<![A-Za-z0-9]){old}(?![a-z0-9])", new, text)
        text = re.sub(rf"(?<![A-Za-z0-9]){old.capitalize()}(?![a-z0-9])",
                      new.capitalize(), text)

    for i, phrase in enumerate(PROTECTED):
        text = text.replace(f"\x00{i}\x00", phrase)
    return text


def git_mv(src: str, dst: str) -> None:
    if not Path(src).exists():
        print(f"  (already moved) {src}")
        return
    subprocess.run(["git", "mv", src, dst], check=True)
    print(f"  {src} -> {dst}")


def main() -> None:
    print("moving files")
    git_mv("rota/client.py", "rota/principal.py")
    for old, new in (("domain", "terminologist"), ("interface", "liaison"),
                     ("vision", "gatekeeper")):
        git_mv(f"rota/prompts/{old}", f"rota/prompts/{new}")

    print("rewriting contents")
    changed = 0
    for path in targets():
        before = path.read_text(encoding="utf-8")
        after = substitute(before)
        if after != before:
            path.write_text(after, encoding="utf-8")
            changed += 1
            print(f"  {path}")
    print(f"{changed} files rewritten")

    stems = "|".join(RENAMES)
    print(f"\nnow check: grep -rniE '\\b({stems})\\b' rota/ tests/rota/")


if __name__ == "__main__":
    sys.exit(main())
