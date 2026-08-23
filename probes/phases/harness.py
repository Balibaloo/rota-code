"""
Prototype harness: run candidate onboarding *phase structures* over one
repository and write their outputs where a person can read them.

Not the rota loop. No sessions, no wakes, no attest -- each phase is one model
call with a context this file assembles. The question it exists to answer is
which *sequence of phases* builds the most complete understanding, and that is
settled by reading the outputs, not by a score.

Everything shared lives here so the pipelines differ only in their phases.
"""
from __future__ import annotations

import re
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from rota.core.runner import _render
from rota.llm.llm import Pins, default_backend
from rota.roles.api import Ctx, code_concordance, _words_in

DB = ".rota/cnt_t.db"
ROOT = Path("D:/tmp/rota-live/repo")
OUT = Path(__file__).parent / "out"
PINS = Pins(model="llama3.1:8b", temperature=0.0)

REQUIRED = ["intent", "template", "prompt", "variable", "variable_type",
            "provider", "frontmatter", "global_intent", "selection", "filter_set"]
PROBE_AS = {"variable_type": "TemplateVariableType", "global_intent": "globalIntents",
            "filter_set": "filterSet"}


def db():
    c = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    c.row_factory = sqlite3.Row
    return c


def ctx(conn):
    return Ctx(conn=conn, role="terminologist", writes=[], opened=set(), batch_id=None)


def ask(system: str, user: str) -> str:
    return default_backend().complete(system, user, PINS).text.strip()


# ---------------------------------------------------------------- context ----

def files(conn) -> list[str]:
    return sorted({r["grain"].split("::")[0] for r in
                   conn.execute("SELECT grain FROM code_index")})


def source(rel: str, cap: int = 2600) -> str:
    f = ROOT / rel
    return f.read_text(encoding="utf-8", errors="replace")[:cap] if f.is_file() else ""


def entry_points(conn) -> list[str]:
    """Declared, never inferred: fan_in cannot find a boundary nothing inside calls."""
    found = []
    for cfg in ("esbuild.config.mjs", "package.json", "manifest.json", "pyproject.toml"):
        body = source(cfg, 4000)
        found += re.findall(r'entryPoints:\s*\[\s*"([^"]+)"', body)
        found += [m for m in re.findall(r'"main":\s*"([^"]+)"', body)
                  if (ROOT / m).is_file()]
    return list(dict.fromkeys(found)) or ["src/main.ts"]


def reach(conn, start: list[str], hops: int = 2) -> list[str]:
    """The files an entry point can arrive at. Computed, not asked for."""
    seen, frontier = set(), set(start)
    for _ in range(hops):
        nxt = set()
        for f in frontier - seen:
            seen.add(f)
            for r in conn.execute("SELECT dst FROM code_edges WHERE src = ?", (f,)):
                nxt.add(r["dst"])
        frontier |= nxt
    return [f for f in sorted(seen | frontier) if (ROOT / f).is_file()]


def concordance(conn, term: str) -> str:
    return _render(code_concordance(ctx(conn), term=PROBE_AS.get(term, term)))


def areas(conn) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for r in conn.execute("SELECT grain, area FROM code_index WHERE area IS NOT NULL"):
        out.setdefault(r["area"], []).append(r["grain"].split("::")[0])
    return {a: sorted(set(f)) for a, f in out.items()}


def write(pipeline: str, name: str, body: str) -> None:
    d = OUT / pipeline
    d.mkdir(parents=True, exist_ok=True)
    (d / name).write_text(body, encoding="utf-8")
    print(f"  wrote {pipeline}/{name}  ({len(body)} chars)")
