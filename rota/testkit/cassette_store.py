"""
The cassette database, published once and fetched by anyone who needs it.

`tests/rota/cassettes.db` is not tracked. It is about 590 MB, a recording
session writes a new version most days, and 153 tracked versions had reached
57 GB of Git LFS. It also compresses eighteen to one: the same 590 MB is a
33 MB gzip, because every cassette carries its whole system prompt and the
transcripts are JSON. So the file is published as a release asset, which
GitHub stores outside the repository and serves without a quota on a public
project, and a checkout that lacks the file fetches it.

Three rules, in order of how much they cost to get wrong.

1. **A local database is never overwritten.** A re-record that has not been
   published exists in exactly one place, and that place is the file this
   module would be replacing. `pull` refuses when the target exists; `--force`
   is the operator saying they know.
2. **Every byte is checked twice.** The gzip is checked against the manifest
   before it is unpacked, and the unpacked database is checked again before it
   is moved into place. A partial download never gets a name a test would open.
3. **The manifest is the pointer, the release is the source.** The tracked
   `tests/rota/cassettes.json` says which release the suite was last measured
   against. The release carries its own copy of the manifest, so an installed
   wheel with no checkout can still find the latest one.

`pack` snapshots the database through SQLite's backup API, not a file copy: a
raw copy of a database that any process holds open comes back malformed
(`CONTRIBUTING.md`, "Checking out").
"""
from __future__ import annotations

import gzip
import hashlib
import json
import os
import shutil
import sqlite3
import sys
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

from .. import paths

DEFAULT_REPO = os.environ.get("ROTA_CASSETTE_REPO", "Balibaloo/rota-code")
ASSET = "cassettes.db.gz"
MANIFEST_ASSET = "cassettes.json"
MANIFEST = paths.REPO / "tests" / "rota" / MANIFEST_ASSET
CHUNK = 1 << 20


@dataclass
class Manifest:
    repo: str
    tag: str
    asset: str
    sha256_gz: str
    sha256_db: str
    bytes_gz: int
    bytes_db: int
    recorded: str
    cassettes: int
    case_runs: int

    @property
    def url(self) -> str:
        return f"https://github.com/{self.repo}/releases/download/{self.tag}/{self.asset}"

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=1) + "\n"

    @classmethod
    def from_json(cls, text: str) -> "Manifest":
        return cls(**json.loads(text))


# ---------------------------------------------------------------------------
# reading
# ---------------------------------------------------------------------------

def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(CHUNK), b""):
            h.update(block)
    return h.hexdigest()


def read_manifest(path: Path = MANIFEST) -> Manifest | None:
    if not path.exists():
        return None
    return Manifest.from_json(path.read_text(encoding="utf-8"))


def _counts(db: Path) -> tuple[int, int]:
    conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        cassettes = conn.execute("select count(*) from cassettes").fetchone()[0]
        runs = conn.execute("select count(*) from case_runs").fetchone()[0]
    finally:
        conn.close()
    return cassettes, runs


def _quick_check(db: Path) -> str:
    conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        return conn.execute("pragma quick_check").fetchone()[0]
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# pack: snapshot, compress, describe
# ---------------------------------------------------------------------------

def pack(db: Path = paths.DEV_DB, out_dir: Path | None = None,
         tag: str | None = None, repo: str = DEFAULT_REPO) -> tuple[Path, Manifest]:
    """
    Snapshot the database with the backup API, gzip the snapshot, and write
    the manifest to `tests/rota/cassettes.json`. Returns the gzip path and the
    manifest. Nothing is uploaded.
    """
    if not db.exists():
        raise SystemExit(f"no database at {db}")
    out_dir = out_dir or Path(tempfile.gettempdir()) / "rota-cassettes"
    out_dir.mkdir(parents=True, exist_ok=True)
    tag = tag or f"cassettes-{date.today():%Y%m%d}"

    snap = out_dir / "cassettes.snapshot.db"
    if snap.exists():
        snap.unlink()
    src = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    dst = sqlite3.connect(snap)
    try:
        src.backup(dst)
        # The source persists WAL in its header, so the snapshot would open
        # in WAL and leave -wal and -shm beside the gzip. One file ships.
        dst.execute("pragma journal_mode = delete")
    finally:
        dst.close()
        src.close()
    check = _quick_check(snap)
    if check != "ok":
        raise SystemExit(f"snapshot failed quick_check: {check}")

    gz = out_dir / ASSET
    with open(snap, "rb") as f, gzip.open(gz, "wb", compresslevel=6) as g:
        shutil.copyfileobj(f, g, CHUNK)

    cassettes, runs = _counts(snap)
    manifest = Manifest(
        repo=repo, tag=tag, asset=ASSET,
        sha256_gz=sha256_of(gz), sha256_db=sha256_of(snap),
        bytes_gz=gz.stat().st_size, bytes_db=snap.stat().st_size,
        recorded=date.today().isoformat(), cassettes=cassettes, case_runs=runs,
    )
    snap.unlink()
    MANIFEST.write_bytes(manifest.to_json().encode("utf-8"))
    (out_dir / MANIFEST_ASSET).write_bytes(manifest.to_json().encode("utf-8"))
    return gz, manifest


# ---------------------------------------------------------------------------
# pull: fetch, verify, unpack, verify, place
# ---------------------------------------------------------------------------

def _download(url: str, dest: Path, expect_bytes: int | None = None,
              quiet: bool = False) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "rota-cassettes"})
    with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as f:
        total = int(r.headers.get("Content-Length") or expect_bytes or 0)
        got, t0, last = 0, time.time(), 0.0
        while True:
            block = r.read(CHUNK)
            if not block:
                break
            f.write(block)
            got += len(block)
            now = time.time()
            if not quiet and total and now - last > 0.5:
                last = now
                pct = got / total * 100
                rate = got / max(now - t0, 1e-6) / 1e6
                print(f"\r  {pct:5.1f}%  {got/1e6:6.1f} / {total/1e6:.1f} MB  "
                      f"{rate:5.1f} MB/s", end="", file=sys.stderr, flush=True)
        if not quiet and total:
            print(file=sys.stderr)


def _latest_manifest(repo: str) -> Manifest:
    """The manifest the newest release carries, for a checkout without one."""
    api = f"https://api.github.com/repos/{repo}/releases/latest"
    req = urllib.request.Request(api, headers={"User-Agent": "rota-cassettes",
                                               "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        release = json.load(r)
    for asset in release.get("assets", []):
        if asset["name"] == MANIFEST_ASSET:
            with urllib.request.urlopen(asset["browser_download_url"], timeout=30) as r:
                return Manifest.from_json(r.read().decode("utf-8"))
    raise SystemExit(f"latest release of {repo} ({release.get('tag_name')}) "
                     f"carries no {MANIFEST_ASSET}")


def pull(dest: Path = paths.DEV_DB, manifest: Manifest | None = None,
         force: bool = False, quiet: bool = False,
         repo: str = DEFAULT_REPO) -> Path:
    """
    Fetch the published database to `dest`. Refuses to replace an existing
    file unless `force`, because the local file may hold recordings that were
    never published.
    """
    if dest.exists() and not force:
        raise SystemExit(
            f"{dest} exists. A local database may hold recordings nobody has "
            f"published. `rota cassettes status` compares it with the manifest; "
            f"`rota cassettes pull --force` replaces it.")
    manifest = manifest or read_manifest() or _latest_manifest(repo)

    dest.parent.mkdir(parents=True, exist_ok=True)
    gz = dest.with_suffix(dest.suffix + ".gz.part")
    part = dest.with_suffix(dest.suffix + ".part")
    for stale in (gz, part):
        if stale.exists():
            stale.unlink()

    if not quiet:
        print(f"cassettes: fetching {manifest.tag} "
              f"({manifest.bytes_gz/1e6:.0f} MB gzip, {manifest.bytes_db/1e6:.0f} MB "
              f"unpacked, {manifest.cassettes} cassettes)", file=sys.stderr)
    _download(manifest.url, gz, manifest.bytes_gz, quiet=quiet)

    got = sha256_of(gz)
    if got != manifest.sha256_gz:
        gz.unlink()
        raise SystemExit(f"downloaded gzip sha256 {got[:12]} != manifest "
                         f"{manifest.sha256_gz[:12]}; nothing was placed")

    with gzip.open(gz, "rb") as g, open(part, "wb") as f:
        shutil.copyfileobj(g, f, CHUNK)
    gz.unlink()

    got = sha256_of(part)
    if got != manifest.sha256_db:
        part.unlink()
        raise SystemExit(f"unpacked database sha256 {got[:12]} != manifest "
                         f"{manifest.sha256_db[:12]}; nothing was placed")
    check = _quick_check(part)
    # A read-only open of a WAL-headered file still creates -wal and -shm.
    for side in (Path(str(part) + "-wal"), Path(str(part) + "-shm")):
        if side.exists():
            side.unlink()
    if check != "ok":
        part.unlink()
        raise SystemExit(f"unpacked database failed quick_check: {check}")

    if dest.exists():
        dest.unlink()
    for side in (dest.with_suffix(dest.suffix + "-wal"),
                 dest.with_suffix(dest.suffix + "-shm")):
        if side.exists():
            side.unlink()
    os.replace(part, dest)
    if not quiet:
        print(f"cassettes: {dest} in place ({manifest.recorded}, "
              f"{manifest.case_runs} case runs)", file=sys.stderr)
    return dest


def ensure_for_tests(dest: Path = paths.DEV_DB) -> str | None:
    """
    Called by the test session before any tier opens the database. Fetches
    only when the file is absent. Returns a one-line note for the report
    header, or None when there was nothing to say.

    A failed fetch is reported and not raised: the tiers then record or show
    STALE, which is what they did before this module existed, and a network
    error must not turn the deterministic suite red.
    """
    if dest.exists() or os.environ.get("ROTA_NO_FETCH"):
        return None
    manifest = read_manifest()
    if manifest is None:
        return f"cassettes: {dest.name} absent and no manifest; tiers will record"
    try:
        pull(dest, manifest, quiet=True)
    except (urllib.error.URLError, OSError, SystemExit) as e:
        return f"cassettes: fetch of {manifest.tag} failed ({e}); tiers will record"
    return f"cassettes: fetched {manifest.tag} ({manifest.cassettes} cassettes)"


# ---------------------------------------------------------------------------
# status and publish
# ---------------------------------------------------------------------------

def status(db: Path = paths.DEV_DB) -> int:
    manifest = read_manifest()
    if manifest is None:
        print("manifest: none (run `rota cassettes pack` after a re-record)")
    else:
        print(f"manifest: {manifest.tag}  {manifest.recorded}  "
              f"{manifest.cassettes} cassettes  {manifest.case_runs} case runs  "
              f"{manifest.bytes_gz/1e6:.0f} MB gzip")
        print(f"          {manifest.url}")
    if not db.exists():
        print(f"local:    absent ({db})")
        return 1
    cassettes, runs = _counts(db)
    local = sha256_of(db)
    print(f"local:    {cassettes} cassettes  {runs} case runs  "
          f"{db.stat().st_size/1e6:.0f} MB  sha256 {local[:12]}")
    if manifest is None:
        return 0
    if local == manifest.sha256_db:
        print("          matches the manifest byte for byte")
        return 0
    # The published snapshot is journal-mode delete and the live file is WAL,
    # so the bytes differ even when the rows are the same. Rows decide.
    if (cassettes, runs) == (manifest.cassettes, manifest.case_runs):
        print("          same rows as the published one; nothing to publish")
    elif runs >= manifest.case_runs and cassettes >= manifest.cassettes:
        print("          more rows than the published one -- `rota cassettes publish`")
    else:
        print("          fewer rows than the published one -- `rota cassettes pull --force` replaces it")
    return 0


def _gh(method: str, url: str, token: str, data: bytes | None = None,
        content_type: str = "application/json") -> dict:
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "rota-cassettes",
        "Content-Type": content_type,
    })
    with urllib.request.urlopen(req, timeout=600) as r:
        body = r.read()
        return json.loads(body) if body else {}


def publish(gz: Path, manifest: Manifest, token: str | None = None) -> int:
    """
    Create the release (or reuse one with the same tag), upload the gzip and
    the manifest beside it, and mark it latest. Needs a token with `contents`
    write on the repository, from `GITHUB_TOKEN`. Without one, prints the two
    `gh` commands that do the same and returns 2.
    """
    token = token or os.environ.get("GITHUB_TOKEN")
    side = gz.parent / MANIFEST_ASSET
    side.write_bytes(manifest.to_json().encode("utf-8"))
    if not token:
        print("GITHUB_TOKEN is not set. Publish by hand:")
        print(f"  gh release create {manifest.tag} --repo {manifest.repo} "
              f"--title {manifest.tag} --latest "
              f"--notes 'cassettes {manifest.recorded}: {manifest.cassettes} "
              f"cassettes, {manifest.case_runs} case runs' "
              f"{gz} {side}")
        print(f"  git add {MANIFEST.relative_to(paths.REPO)} && git commit")
        return 2

    api = f"https://api.github.com/repos/{manifest.repo}"
    notes = (f"Cassette database recorded {manifest.recorded}: "
             f"{manifest.cassettes} cassettes, {manifest.case_runs} case runs, "
             f"{manifest.bytes_db/1e6:.0f} MB unpacked.\n\n"
             f"Fetch with `rota cassettes pull`, or by hand: download "
             f"`{ASSET}`, check sha256 `{manifest.sha256_gz}`, gunzip to "
             f"`tests/rota/cassettes.db`.")
    try:
        release = _gh("POST", f"{api}/releases", token, json.dumps({
            "tag_name": manifest.tag, "name": manifest.tag, "body": notes,
            "make_latest": "true"}).encode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code != 422:
            raise
        release = _gh("GET", f"{api}/releases/tags/{manifest.tag}", token)
        for asset in release.get("assets", []):
            if asset["name"] in (ASSET, MANIFEST_ASSET):
                _gh("DELETE", f"{api}/releases/assets/{asset['id']}", token)

    upload = release["upload_url"].split("{")[0]
    for path, ctype in ((gz, "application/gzip"), (side, "application/json")):
        print(f"uploading {path.name} ({path.stat().st_size/1e6:.0f} MB)")
        _gh("POST", f"{upload}?name={path.name}", token, path.read_bytes(), ctype)
    print(f"published {manifest.url}")
    print(f"commit {MANIFEST.relative_to(paths.REPO)} so the checkout points at it")
    return 0
