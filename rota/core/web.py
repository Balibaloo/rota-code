"""
The one place this system reaches outside itself.

Three properties, in the order they matter:

**Nothing is reachable that was not granted.** `research_allowlist` is empty by
default, so a fresh engagement fetches nothing at all. A capability that reaches
outside the engagement has to be granted, never merely not-forbidden.

**Every fetch is recorded, so every fetch replays.** The cache is the same idea as
the LLM cassettes: keyed by URL, holding the body and the hash, so a case that
exercises the Researcher runs offline and byte-identically. Without it the
Researcher would be the one role whose tests need the network, which would break
the property the whole suite rests on.

**No page ever enters a prompt whole.** `extract` returns a bounded passage the
way `code.source(path, start, end)` does. The index/body split is what keeps a
working set viable over a large codebase and it is what keeps one over a large
document too — an RFC is longer than the context window and the interesting part
of it is four paragraphs.

The wall clock lives here rather than on the artefact, per law 13: no date,
duration or timestamp column exists in `schema.sql`. This is evidence, not an
artefact, so it may carry one — and a human reading a cached page wants to know
when it was read, even though nothing the system *does* needs to.
"""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import time
from urllib.parse import urlparse

MAX_BYTES = 2_000_000          # a page bigger than this is not a document
PASSAGE = 1_400                # characters returned around a match
CACHE_DDL = """
CREATE TABLE IF NOT EXISTS web_cache (
    url          TEXT PRIMARY KEY,
    body         TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    status       INTEGER NOT NULL,
    fetched_at   REAL NOT NULL
)
"""


class NotAllowed(Exception):
    """The domain is not on the allowlist. Not an error the session recovers
    from by retrying — it is a fact to report back to whoever asked."""


def domain_of(url: str) -> str:
    return (urlparse(url).hostname or "").lower().lstrip("www.")


def allowed(url: str, allowlist: list[str]) -> bool:
    """
    A domain matches if it equals an entry or is a subdomain of one.

    Subdomains match on purpose — `datatracker.ietf.org` under `ietf.org` — and
    the suffix check is anchored on a dot so that `evil-ietf.org` does not pass
    for `ietf.org`, which is the mistake this kind of check is famous for.
    """
    host = domain_of(url)
    if not host:
        return False
    for entry in allowlist:
        entry = entry.lower().lstrip(".")
        if host == entry or host.endswith("." + entry):
            return True
    return False


def ensure_cache(conn: sqlite3.Connection) -> None:
    conn.execute(CACHE_DDL)


def cached(conn: sqlite3.Connection, url: str) -> dict | None:
    ensure_cache(conn)
    row = conn.execute(
        "SELECT url, body, content_hash, status, fetched_at FROM web_cache "
        "WHERE url = ?", (url,)).fetchone()
    return dict(row) if row else None


def store(conn: sqlite3.Connection, url: str, body: str, status: int) -> dict:
    ensure_cache(conn)
    digest = hashlib.sha256(body.encode("utf-8", "replace")).hexdigest()[:16]
    conn.execute(
        "INSERT INTO web_cache (url, body, content_hash, status, fetched_at) "
        "VALUES (?, ?, ?, ?, ?) ON CONFLICT(url) DO UPDATE SET "
        "body = excluded.body, content_hash = excluded.content_hash, "
        "status = excluded.status, fetched_at = excluded.fetched_at",
        (url, body, digest, status, time.time()))
    return {"url": url, "body": body, "content_hash": digest, "status": status}


def _strip(html: str) -> str:
    """Markup out, text through. Not a parser — an RFC is served as plain text
    and an HTML spec is mostly prose; anything cleverer is a dependency."""
    if "<" not in html:
        return html
    text = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", html)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    for entity, char in (("&nbsp;", " "), ("&amp;", "&"), ("&lt;", "<"),
                         ("&gt;", ">"), ("&quot;", '"'), ("&#39;", "'")):
        text = text.replace(entity, char)
    return re.sub(r"[ \t]{2,}", " ", text)


def extract(body: str, terms: str = "", fragment: str = "") -> str:
    """
    A bounded passage, chosen by what was asked for.

    A whole RFC does not fit in a working set and four paragraphs of it usually
    answer the question. Where the URL names a fragment — `#section-3.4.1.3.2`,
    which is exactly how the codebases that cite specifications write them down —
    that anchor is the best available guess at which four.
    """
    text = _strip(body).strip()
    needles = [n for n in ([fragment] if fragment else []) + terms.split() if len(n) > 2]
    for needle in needles:
        at = text.lower().find(needle.lower().replace("-", " "))
        if at < 0:
            at = text.lower().find(needle.lower())
        if at >= 0:
            start = max(0, at - PASSAGE // 4)
            return text[start:start + PASSAGE]
    return text[:PASSAGE]


def fetch(conn: sqlite3.Connection, url: str, allowlist: list[str],
          *, offline: bool = False) -> dict:
    """
    One page, from the cache if it is there and from the network if not.

    `offline` is what the test suite runs under: a cache miss raises rather than
    reaching out, so a case that forgot to record its page fails loudly instead
    of passing on one machine and hanging on another.
    """
    hit = cached(conn, url)
    if hit:
        return hit
    if offline:
        raise NotAllowed(
            f"{url} is not in the fetch cache and this session is offline; "
            f"record it before the case can run")
    if not allowed(url, allowlist):
        raise NotAllowed(
            f"{domain_of(url)} is not on research_allowlist — the principal "
            f"grants domains, and nothing outside them is reachable")

    import urllib.request

    request = urllib.request.Request(
        url, headers={"User-Agent": "rota/0 (+research)", "Accept": "*/*"})
    with urllib.request.urlopen(request, timeout=20) as response:
        raw = response.read(MAX_BYTES)
        status = getattr(response, "status", 200)
    return store(conn, url, raw.decode("utf-8", "replace"), status)


def record_from(path) -> int:
    """Load a JSON list of {url, body} into a cache database. How a case's pages
    get into the suite without the suite ever reaching the network."""
    import pathlib

    from .db import connect

    data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    conn = connect(data["db"])
    for page in data["pages"]:
        store(conn, page["url"], page["body"], page.get("status", 200))
    conn.commit()
    return len(data["pages"])
