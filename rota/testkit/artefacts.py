"""
Whether an artefact is worth having, checked mechanically.

Every real fault found on the first foreign repository was found by a person
reading output against predictions written beforehand. That does not scale, and
it was the only thing finding anything — an uncomfortable pair. This is the half
of that job a machine can do.

**Precision, not recall.** Nothing here can tell a true constraint from a false
one; that needs a person who knows the repository, and it is what
`ANSWER_KEY.md` is for. What these can do is refuse the ones *nobody could have
found* — a definition composed from the filename, a number that appears in no
source, a citation with nothing behind it. Each check below is a necessary
condition that a real artefact meets and a fabricated one usually does not.

Every one of them is derived from a fault that actually happened:

    echoes_the_brief      "Retention period for client tokens" x8, from a brief
                          that offered "A retention period." as an example
    restates_the_index    "DeviceApplicationServer: a class in
                          oauth2/rfc8628/endpoints/pre_configured.py"
    numbers_not_in_source "Retention period for access tokens is 30 days" x5,
                          in a repository containing no thirty
    duplicated            24 constraints carrying 6 distinct headlines
    unbacked_citations    provenance 'cited' with no reference behind it

The one deliberately not implemented is vocabulary drift — "does this constraint
use terms the glossary carries". The brief demands it and it sounds checkable,
but every phrasing of it I tried flagged ordinary English, and a check that cries
wolf on real findings costs more than the fabrications it catches.
"""
from __future__ import annotations

import json
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path

# Words that carry no evidence either way. Kept short on purpose: a long stop
# list starts deciding what counts as a finding.
NOISE = {
    "a", "an", "the", "is", "are", "was", "be", "been", "of", "for", "to", "in",
    "on", "at", "by", "with", "and", "or", "not", "this", "that", "it", "its",
    "must", "should", "can", "may", "will", "from", "as", "into", "which",
}

# Words that describe *what kind of thing* a name is, which the index already
# says. A definition made only of these has restated its own row.
GENERIC = {
    "class", "function", "module", "instance", "method", "path", "value",
    "object", "file", "attribute", "variable", "parameter", "argument",
    "constant", "field", "property", "package", "directory", "type",
}


@dataclass(frozen=True)
class Finding:
    check: str
    artefact: str
    row_id: str
    detail: str

    def __str__(self) -> str:
        return f"{self.check:22} {self.artefact}:{self.row_id}  {self.detail}"


def _authored(conn: sqlite3.Connection, sql: str) -> list:
    """
    Constraints a role wrote, which is every one except the seeded zero.

    Constraint zero is the system's own — "this area has not been surveyed",
    with derived bindings — and it tripped the echo check on its first outing,
    for the excellent reason that the scheduler and the brief use the same word
    for the same thing. Judging derived state as though a role had authored it
    is how a report earns the skim it then gets.
    """
    from ..onboarding import boot

    return list(conn.execute(sql, (boot.ZERO,)))


def _words(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z0-9_]+", (text or "").lower())
            if w not in NOISE and len(w) > 2]


def _shingles(words: list[str], n: int = 2) -> set[tuple]:
    return {tuple(words[i:i + n]) for i in range(len(words) - n + 1)}


# ---------------------------------------------------------------------------


def echoes_the_brief(conn: sqlite3.Connection, brief: str) -> list[Finding]:
    """
    The artefact repeats a phrase from the instructions that produced it.

    Architect's survey brief listed what a constraint looks like — "A retention
    period. A boundary a piece of data may not cross. An interface something
    else depends on. An ordering that another system relies on." Three of the
    four came back as headlines with the nearest grain name appended.

    Two signals, because one was not enough and finding that out is the reason
    this file tests against real output rather than invented output:

    * **Two consecutive content words.** Catches "Retention period for client
      tokens" against "A retention period." One word alone is coincidence.
    * **A short headline led by a word the brief used.** "Interface for client
      tokens" and "Ordering for client tokens" echo a *single* word each, so no
      shingle matches, and they were the two the first version missed.

    The second signal is bounded at three content words on purpose. "Ordering of
    query parameters is byte-exact" is a real oauthlib commitment led by a word
    the brief used, and flagging it would be exactly the false positive that
    teaches a reader to skim.
    """
    brief_words = set(_words(brief))
    haystack = _shingles(_words(brief))
    out = []
    for r in _authored(conn, "SELECT id, headline FROM constraints WHERE id != ?"):
        words = _words(r["headline"])
        shared = _shingles(words) & haystack
        if shared:
            phrase = " ".join(sorted(shared)[0])
            out.append(Finding("echoes-the-brief", "constraints", r["id"],
                               f"{r['headline']!r} repeats {phrase!r}"))
        elif words and len(words) <= 3 and words[0] in brief_words:
            out.append(Finding("echoes-the-brief", "constraints", r["id"],
                               f"{r['headline']!r} is the brief's {words[0]!r} "
                               f"with a grain name after it"))
    return out


def restates_the_index(conn: sqlite3.Connection) -> list[Finding]:
    """
    A definition derivable from the name being defined.

    "DeviceApplicationServer: a class in oauth2/rfc8628/endpoints/pre_configured
    .py" says nothing the path does not, and it is what comes out of defining
    from the grain list instead of from the source.

    The file path is the load-bearing part, and the first version of this check
    missed it entirely: the path words are not in the *term*, so they read as
    novel content. A path quoted in a definition is a citation of where the name
    lives, not a statement of what it means, so it is struck out before the
    definition is weighed. What has to remain is one content word that could
    only have come from reading.
    """
    out = []
    for r in conn.execute(
            "SELECT id, term, sense_short, sense_body FROM glossary_terms"):
        given = set(_words(r["term"])) | set(_words(r["id"]))
        prose = f"{r['sense_short']} {r['sense_body'] or ''}"
        prose = re.sub(r"\S*[/\\]\S*|\S+\.[a-z]{1,4}\b", " ", prose)
        said = set(_words(prose))
        novel = said - given - GENERIC
        if not novel:
            out.append(Finding("restates-the-index", "glossary_terms", r["id"],
                               f"{r['term']}: {r['sense_short'][:70]!r} adds nothing "
                               f"the name and its path do not already say"))
    return out


def numbers_not_in_source(conn: sqlite3.Connection, root: Path) -> list[Finding]:
    """
    A constraint asserting a number that appears in none of the files it binds.

    "Retention period for access tokens is 30 days", five times, against a
    repository with no retention policy and no thirty in it. This is the
    cheapest high-confidence fabrication check there is: a real commitment to a
    number has the number written down somewhere.
    """
    out = []
    for r in _authored(conn,
            "SELECT id, headline, text FROM constraints WHERE id != ?"):
        claimed = set(re.findall(r"\b\d+\b", f"{r['headline']} {r['text'] or ''}"))
        if not claimed:
            continue
        bound = [b["grain"] for b in conn.execute(
            "SELECT grain FROM constraint_bindings WHERE constraint_id = ?",
            (r["id"],))]
        corpus = ""
        for grain in bound:
            f = root / grain.split("::", 1)[0]
            if f.is_file():
                corpus += f.read_text(encoding="utf-8", errors="replace")
        missing = sorted(n for n in claimed
                         if not re.search(rf"\b{re.escape(n)}\b", corpus))
        if missing and bound:
            out.append(Finding("number-not-in-source", "constraints", r["id"],
                               f"{r['headline']!r} claims {', '.join(missing)}, "
                               f"absent from {', '.join(bound)}"))
    return out


def duplicated(conn: sqlite3.Connection) -> list[Finding]:
    """
    The same thing written down more than once.

    A duplicated glossary entry is clutter. A duplicated constraint is a
    duplicated *gate* — each enters range at review, each must be satisfied or
    argued with, and satisfying the first does nothing for the rest. Both ids
    derive from content now, so this should be empty; it is kept because "should
    be impossible" is the state a check exists to confirm.
    """
    out = []
    for table, column in (("constraints", "headline"), ("glossary_terms", "term")):
        for r in _authored(conn,
                f"SELECT {column} v, COUNT(*) n, GROUP_CONCAT(id) ids "
                f"FROM {table} WHERE id != ? GROUP BY LOWER({column}) HAVING n > 1"):
            out.append(Finding("duplicated", table, r["ids"],
                               f"{r['v']!r} written {r['n']} times"))
    return out


def unbacked_citations(conn: sqlite3.Connection) -> list[Finding]:
    """
    `provenance = 'cited'` with nothing behind it.

    Law 11 makes provenance explicit so that a claim can be checked. A row that
    says it was cited and names no reference has used the strongest word
    available to mean the weakest thing.
    """
    have = {r["id"] for r in conn.execute("SELECT id FROM references_")}
    out = []
    for table in ("constraints", "glossary_terms"):
        for r in _authored(conn,
                f"SELECT id, provenance, source_refs FROM {table} "
                f"WHERE provenance = 'cited' AND id != ?"):
            refs = json.loads(r["source_refs"] or "[]")
            dangling = [x for x in refs if x not in have]
            if not refs:
                out.append(Finding("unbacked-citation", table, r["id"],
                                   "provenance 'cited' with no source_refs"))
            elif dangling:
                out.append(Finding("unbacked-citation", table, r["id"],
                                   f"source_refs name no such reference: "
                                   f"{', '.join(dangling)}"))
    return out


def audit(conn: sqlite3.Connection, root: Path, brief: str = "") -> list[Finding]:
    """Every check, in the order a reader should meet them."""
    out = list(duplicated(conn))
    out += numbers_not_in_source(conn, Path(root))
    out += restates_the_index(conn)
    out += unbacked_citations(conn)
    if brief:
        out += echoes_the_brief(conn, brief)
    return out
