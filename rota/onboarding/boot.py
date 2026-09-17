"""
Onboarding, from a checkout to a schedulable world.

One entry point, shared by the CLI and by every test that needs an onboarded
database. The steps are separable and each is a pure function of the one before,
so a re-run on a later commit produces the same answer without remembering that
it ran — which is the same property the frontier has, for the same reason.

    index      what exists, and what depends on what        (mechanical)
    partition  areas, from directories, checked by the graph (mechanical)
    lexicon    the words the checkout declares, ranked       (mechanical)
    zero       one constraint over everything unsurveyed     (mechanical)
    orient     what the program does for its user            (one session)
    define     what each declared word means here            (one per word)
    survey     what each area adds, and what it is bound to  (per area, per role)

Constraint zero is the piece that makes the last step honest. Before a codebase
has been looked at, the true statement about it is "this may be committed to
things nobody here knows about" — so onboarding writes exactly that, bound to
every area, and every completed survey shrinks its binding by one area. It is
never removed by judgement and no role can write it: an area stops being covered
by it when somebody has looked, and only then.
"""
from __future__ import annotations

from ..core.worktrees import GIT

import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

from ..core import db
from . import areas as areas_mod
from . import indexer
from . import lexicon as lexicon_mod

ZERO = "k0"

ZERO_HEADLINE = "this area has not been surveyed"

ZERO_TEXT = (
    "Nobody has read this area yet, so what it is committed to is unknown. "
    "Treat a change here as touching commitments that have not been written "
    "down: it is not a prohibition, it is the absence of the information that "
    "would let anyone say. Surveying the area removes it from this constraint, "
    "including a survey that finds nothing — that is a result."
)


@dataclass
class OnboardReport:
    index: indexer.IndexReport
    areas: int
    unsurveyed: int
    leaky: list
    words: int = 0
    stresses: list = field(default_factory=list)


def checkout_of(root: str | Path) -> tuple[str, str]:
    """
    The branch and commit a checkout is on, or two empty strings.

    Not an error when there is no git. A tree can be onboarded without being a
    repository, and refusing would make the indexer care about version control,
    which is not its job.
    """
    import subprocess

    out = []
    for args in (("rev-parse", "--abbrev-ref", "HEAD"), ("rev-parse", "HEAD")):
        try:
            got = subprocess.run([*GIT, "-C", str(root), *args],
                                 capture_output=True, text=True, timeout=10)
            out.append(got.stdout.strip() if got.returncode == 0 else "")
        except (OSError, subprocess.SubprocessError):
            out.append("")
    return out[0], out[1]


def onboard(conn: sqlite3.Connection, root: str | Path) -> OnboardReport:
    """Index, partition, and put everything under constraint zero."""
    report = indexer.build(conn, root)
    proposal = areas_mod.propose(conn)
    count = areas_mod.pin(conn, proposal)
    # The areas exist now, so each one's content can be stamped. The freshness
    # rule reads the stamp, not the index, because the index follows the
    # running batch's worktree while a batch runs.
    indexer.stamp_area_hashes(conn)
    words = lexicon_mod.build(conn, root)
    conn.execute("INSERT OR REPLACE INTO config (key, value) VALUES "
                 "('project_root', ?)", (str(Path(root)),))
    # And *when*. Written here rather than in `cli.onboard` for the reason
    # below: every path that makes a run comes through this function, and a
    # date that only some runs carried would be worse than no date at all.
    db.mark_created(conn)
    # And *which tree*. This lived in `cli.onboard`, so `rota onboard` and the
    # new-run form recorded it while the seat's own onboard key did not --
    # `tui._do_onboard`, `fixtures` and `onboard_run` all call this function
    # directly. Two runs made different ways were differently identifiable,
    # which is worse than neither recording it: a comparison's header would be
    # right only sometimes.
    #
    # Empty rather than absent when there is no git: a directory can be
    # onboarded without being a repository, and the run then honestly describes
    # a tree rather than a commit.
    branch, commit = checkout_of(root)
    for key, value in (("project_branch", branch), ("project_commit", commit)):
        conn.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                     (key, value))
    unsurveyed = refresh_constraint_zero(conn)
    out = OnboardReport(index=report, areas=count, unsurveyed=unsurveyed,
                        leaky=proposal.leaky(), words=words.words)
    out.stresses = stresses(conn, out)
    return out


# Suffixes expected to carry no symbols: prose, config, styles, scripts-in-
# passing. Everything else without a parser is code this system cannot read.
_EXPECTED_UNPARSED = {".md", ".rst", ".txt", ".yaml", ".yml", ".toml", ".json",
                      ".cfg", ".ini", ".css", ".scss", ".less", ".html",
                      ".svg", ".xml", ".sql", ".sh", ".ps1", ".bat", ".env",
                      ".editorconfig", ".gitignore", ".gitattributes", ""}


def stresses(conn: sqlite3.Connection, report: OnboardReport) -> list[str]:
    """
    The assumptions this checkout is about to stress, said while the operator
    is looking.

    ASSUMPTIONS.md is the register; these are its mechanical tripwires, read
    against one checkout at the one moment the numbers are fresh. Each breaks
    *silently* downstream -- path-only grains survey as "almost nothing",
    a missing README just never fires reconcile -- where nothing names the
    cause. An info line for the language mix, a warning per tripped wire.
    """
    from collections import Counter

    from .languages import BY_SUFFIX

    out: list[str] = []
    mix = ", ".join(f"{k} {v}" for k, v in sorted(
        report.index.languages.items(), key=lambda kv: (-kv[1], kv[0])))
    if mix:
        out.append(f"languages: {mix}")

    odd: Counter = Counter()
    for r in conn.execute("SELECT grain FROM code_index WHERE grain_kind = 'path'"):
        name = r["grain"].rsplit("/", 1)[-1]
        suffix = ("." + name.rsplit(".", 1)[-1].lower()) if "." in name else ""
        if suffix not in BY_SUFFIX and suffix not in _EXPECTED_UNPARSED:
            odd[suffix or name] += 1
    for suffix, n in odd.most_common():
        if n >= 3:
            out.append(f"{n} {suffix} files have no parser: their symbols, "
                       f"imports and vocabulary are invisible (ASSUMPTIONS.md)")

    keys = conn.execute("SELECT COUNT(*) FROM code_lexicon WHERE sources "
                        "LIKE ?", ('%"key"%',)).fetchone()[0]
    if keys > 60:
        out.append(f"{keys} authoring keys, and the define phase owes every "
                   f"one: expect that many sessions, or bring a triage rule")

    if not conn.execute(
            "SELECT 1 FROM code_index WHERE grain_kind = 'path' "
            "AND grain LIKE 'readme%' AND grain NOT LIKE '%/%' "
            "LIMIT 1").fetchone():
        out.append("no root README: reconcile has nothing to check and the "
                   "prose holds no names")

    docs_prose = conn.execute(
        "SELECT COUNT(*) FROM code_index WHERE grain_kind = 'path' "
        "AND (grain LIKE 'docs/%' OR grain LIKE 'doc/%') "
        "AND (grain LIKE '%.md' OR grain LIKE '%.rst' OR grain LIKE '%.txt')"
    ).fetchone()[0]
    if docs_prose >= 10:
        out.append(f"{docs_prose} prose files under docs/: reconcile reads "
                   f"each against the account, one session per file, and a "
                   f"disagreement is a page for you")

    from .areas import is_attached
    root_src = [r["grain"] for r in conn.execute(
        "SELECT grain FROM code_index WHERE grain_kind = 'path' AND area = '.'")
        if not is_attached(r["grain"])]
    if len(root_src) > 20:
        out.append(f"the root catch-all holds {len(root_src)} source files: "
                   f"whatever did not fold anywhere else is what one survey "
                   f"session will be asked to characterise")

    if report.areas == 1 and report.index.files > 20:
        out.append(f"one area holds all {report.index.files} files: a flat "
                   f"tree asks each survey to characterise the whole program "
                   f"from one window")
    return out


def repin(conn: sqlite3.Connection, root: str | Path) -> int:
    """
    Recompute the frame-dependent layers after the rulings changed.

    The judge session or a principal's ruling writes `frame_rulings`; this
    re-runs the partition and the lexicon over the ruled table and rebinds
    constraint zero. Deterministic and idempotent: same rulings, same frame.
    The hazard `areas.pin` names -- a partition changing under a
    half-finished survey -- is the caller's to respect: re-pin before the
    surveys, or re-earn what a changed area invalidates.
    """
    from . import areas as areas_mod
    from . import lexicon as lexicon_mod

    proposal = areas_mod.propose(conn)
    count = areas_mod.pin(conn, proposal)
    lexicon_mod.build(conn, root)
    refresh_constraint_zero(conn)
    # Last, over the re-pinned partition: an area that changed name or content
    # must carry the hash of what it holds now. Every main-checkout refresh
    # comes through here, so this is the one place the stamp is renewed.
    indexer.stamp_area_hashes(conn)
    return count


def refresh_constraint_zero(conn: sqlite3.Connection) -> int:
    """
    Bind constraint zero to exactly the areas nobody has surveyed.

    Derived, never accumulated. The bindings are recomputed from the surveys
    that exist rather than deleted one at a time as they arrive, so a survey
    that is rolled back with its session takes its shrinkage with it — the
    binding cannot drift from the evidence, because it is a function of it.

    If the project has no indexed areas yet, there is no real project to survey,
    so there is no meaningful `k0` to create or present.

    An area holds code, or it binds nothing. Constraint zero says "what this
    area is committed to is unknown". A commitment is something code makes. A
    README, a licence and a `.gitignore` promise nothing a change could break.
    An area of pure prose is not unread ground. It is ground with nothing on
    it. Measured as the principal (tips5, tips7, 2026-09-04): a new project
    whose only file was `README.md` indexed one prose area. `k0` existed and
    bound to it. The walk stopped to ask the principal to approve a paragraph
    of internal doctrine on a repository with no code. Symbol grains are the
    test. `_EXPECTED_UNPARSED` already uses the same signal.
    """
    coded = [r["area"] for r in conn.execute(
        "SELECT DISTINCT area FROM code_index "
        "WHERE area IS NOT NULL AND grain_kind = 'symbol' ORDER BY area")]
    if not coded:
        conn.execute("DELETE FROM constraint_bindings WHERE constraint_id = ?", (ZERO,))
        conn.execute("DELETE FROM refs WHERE src_table = 'constraints' AND src_id = ?",
                     (ZERO,))
        conn.execute("DELETE FROM constraints WHERE id = ?", (ZERO,))
        return 0

    conn.execute(
        "INSERT OR IGNORE INTO constraints (id, headline, text, is_global) "
        "VALUES (?, ?, ?, 0)",
        (ZERO, ZERO_HEADLINE, ZERO_TEXT))

    surveyed = {r["area"] for r in conn.execute(
        "SELECT DISTINCT area FROM survey_records")}
    remaining = [area for area in coded if area not in surveyed]

    conn.execute("DELETE FROM constraint_bindings WHERE constraint_id = ?", (ZERO,))
    conn.executemany(
        "INSERT INTO constraint_bindings (constraint_id, grain, grain_kind) "
        "VALUES (?, ?, 'path')", [(ZERO, area) for area in remaining])
    # The same areas as grain refs. Constraint zero rests on the ground
    # nobody has read, and the relation says so beside the bindings. Derived
    # the same way: recomputed whole, so it cannot drift from the surveys.
    conn.execute("DELETE FROM refs WHERE src_table = 'constraints' AND src_id = ?",
                 (ZERO,))
    conn.executemany(
        "INSERT INTO refs (src_table, src_id, kind, target) "
        "VALUES ('constraints', ?, 'grain', ?)", [(ZERO, area) for area in remaining])
    return len(remaining)


def is_onboarded(conn: sqlite3.Connection) -> bool:
    return bool(conn.execute(
        "SELECT 1 FROM code_index LIMIT 1").fetchone())
