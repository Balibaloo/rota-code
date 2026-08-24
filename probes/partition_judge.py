"""Can a 14B judge the frame? The probe before the mechanism.

The partition session proposal replaces the name-list heuristics with a
model's classification of the tree. Before building any machinery, the
judge is tested cold on six repositories -- three we hold full ground truth
for and three chosen to be hostile in ways the heuristics cannot handle:
a Go tool (fzf), documentation that IS the product (opensource.guide,
with node_modules committed), and a language no parser reads
(swift-argument-parser). If the judge cannot match ground truth on repos
we have solved by hand, the mechanism is not worth building.

    python probes/partition_judge.py [--model qwen2.5:14b]
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from probes.downstream import default_backend  # noqa: E402
from rota.llm.llm import Pins  # noqa: E402

SKIP = {".git", "__pycache__", ".rota"}

# path -> the classes a correct judge may answer. Sets of size >1 are
# genuine ambiguities where a human maintainer could rule either way.
REPOS: dict[str, dict[str, set[str]]] = {
    r"D:/tmp/rota-live/repo": {                       # cnt: the app
        "src": {"program"},
        "intentsSchema.yaml": {"boundary"},
        "manifest.json": {"boundary"},
        "assets": {"attached", "ignore"},
        "README.md": {"attached"},
        "esbuild.config.mjs": {"attached", "ignore"},
    },
    r"D:/tmp/rota-live/click": {                      # library
        "src": {"program"},
        "docs": {"attached"},
        "examples": {"attached"},
        "tests": {"attached"},
        "pyproject.toml": {"boundary"},
        ".github": {"attached", "ignore"},
    },
    r"D:/tmp/rota-live/icalendar": {                  # spec library
        "src": {"program"},
        "docs": {"attached"},
        "news": {"attached", "ignore"},
        "pyproject.toml": {"boundary"},
        ".pre-commit-config.yaml": {"attached", "ignore"},
    },
    r"D:/tmp/rota-live/fzf": {                        # Go tool
        "src": {"program"},
        "main.go": {"program"},
        "shell": {"program", "boundary"},             # the shell bindings ship
        "plugin": {"program", "attached"},
        "man": {"attached"},
        "test": {"attached"},
        "Dockerfile": {"attached", "ignore"},
        "go.mod": {"boundary"},
    },
    r"D:/tmp/rota-live/opensource.guide": {           # docs ARE the product
        "_articles": {"program"},
        "_layouts": {"program", "attached"},
        "_config.yml": {"program", "boundary", "attached"},
        "node_modules": {"ignore"},
        "test": {"attached"},
        "script": {"attached"},
        "package.json": {"boundary", "attached"},
    },
    r"D:/tmp/rota-live/swift-argument-parser": {      # no parser for the language
        "Sources": {"program"},
        "Tests": {"attached"},
        "Examples": {"attached"},
        "Package.swift": {"boundary"},
        "Plugins": {"program", "attached"},
        "CMakeLists.txt": {"attached", "boundary", "ignore"},
    },
}

SYSTEM = (
    "You classify the top level of a repository so that a survey of its "
    "meaning can be scheduled. Classes:\n"
    "  program  - the source of the thing this repository ships. If the "
    "shipped thing is documents, the documents are program.\n"
    "  attached - about the program, not of it: tests, examples, "
    "documentation describing the program, CI and tool configuration.\n"
    "  ignore   - vendored or generated: lockfiles, node_modules, build "
    "output.\n"
    "  boundary - a file whose other side is outside this repository: a "
    "package manifest a registry resolves (pyproject.toml, go.mod, "
    "Package.swift, manifest.json), a schema users write documents "
    "against. Build settings with no outside reader are attached, but a "
    "file that names the package to a registry is boundary, not program.\n"
    "Answer with exactly one line per listed entry:\n"
    "<entry>: <class> - <reason, five words at most>\n"
    "Then one final line: programs: <what this repository ships, one clause>."
)


def describe(root: Path) -> str:
    lines = []
    for entry in sorted(root.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
        if entry.name in SKIP:
            continue
        if entry.is_dir():
            suf = Counter(p.suffix or "(none)" for p in entry.rglob("*") if p.is_file())
            total = sum(suf.values())
            top = ", ".join(f"{k} x{v}" for k, v in suf.most_common(3))
            lines.append(f"{entry.name}/  ({total} files: {top})")
        else:
            lines.append(f"{entry.name}  ({entry.stat().st_size} bytes)")
    readme = next((p for p in root.iterdir()
                   if p.is_file() and p.name.lower().startswith("readme")), None)
    head = ""
    if readme:
        try:
            head = "\n".join(readme.read_text(encoding="utf-8", errors="replace")
                             .splitlines()[:10])
        except OSError:
            pass
    return ("[the repository's top level]\n" + "\n".join(lines)
            + ("\n\n[the README's first lines]\n" + head if head else ""))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen2.5:14b")
    args = ap.parse_args(argv)
    backend = default_backend()
    pins = Pins(model=args.model, temperature=0.0, num_ctx=12288)

    grand_hit = grand_all = 0
    for root, truth in REPOS.items():
        rootp = Path(root)
        if not rootp.is_dir():
            print(f"--- {rootp.name}: MISSING, skipped")
            continue
        got = backend.complete(SYSTEM, describe(rootp), pins).text
        answers: dict[str, str] = {}
        for line in got.splitlines():
            m = re.match(r"\s*(?:[-*\d.]+\s*)?`?([^\s:`]+?)`?\s*:\s*"
                         r"\**(program|attached|attach|ignore|boundary)\**",
                         line, re.I)
            if m:
                key = m.group(1).strip("`*-").rstrip("/")
                answers[key] = ("attached" if m.group(2).lower() == "attach"
                                else m.group(2).lower())
        hits, misses = [], []
        for path, allowed in truth.items():
            a = answers.get(path) or answers.get(path.rstrip("/"))
            (hits if a in allowed else misses).append((path, a, "/".join(sorted(allowed))))
        grand_hit += len(hits); grand_all += len(truth)
        prog = next((l.split(":", 1)[1].strip() for l in got.splitlines()
                     if l.lower().startswith("programs:")), "?")
        print(f"--- {rootp.name}: {len(hits)}/{len(truth)}")
        for path, a, want in misses:
            print(f"    MISS {path}: said {a!r}, truth {want}")
        print(f"    ships: {prog[:110]}")
    print(f"\n=== judge: {grand_hit}/{grand_all} across "
          f"{sum(1 for r in REPOS if Path(r).is_dir())} repositories")
    return 0


if __name__ == "__main__":
    sys.exit(main())
