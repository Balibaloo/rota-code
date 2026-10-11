"""
A new rota database per test, copied from one built once per process.

`init_db` on a new file runs the whole schema, and each statement commits
on its own. That cost 140ms a setup, and 1158 setups were about 20% of the
suite's worker time. `init_db` on a copy of a built database cost 4.8ms
(observed: frame 203's count, 2026-10-11).

The test process calls `init_db` through this wrapper. The wrapper copies the
template to a new file and then calls the real `init_db` on the copy. So a
test gets what the real `init_db` gives on that file, and an existing file
or `:memory:` goes to the real `init_db` untouched.

`rota/core/db.py` stays as it is. A run never pays the cost per database,
and a template in production would be one more file to keep current.
"""
from __future__ import annotations

import hashlib
import inspect
import shutil
import sys
from pathlib import Path

from ..core import db as _db
from .gitfixture import template

_REAL = _db.init_db
_NAME = "rota.db"


def _key() -> tuple[str, str]:
    """The template's key. A change to the schema file or to `init_db`
    makes a new key, so the next new database comes from a new template."""
    digest = hashlib.sha256(Path(_db.SCHEMA_PATH).read_bytes())
    digest.update(inspect.getsource(_REAL).encode("utf-8"))
    return (_NAME, digest.hexdigest())


def _build(base: Path) -> None:
    # Closed, so that WAL mode leaves no `-wal` file beside the template.
    _REAL(base / _NAME).close()


def template_path() -> Path:
    """The template database for the current schema, built when absent."""
    base, _ = template(_key(), _build)
    return base / _NAME


def init_db(path):
    """`init_db`, with a new file started as a copy of the template."""
    if str(path) == ":memory:":
        return _REAL(path)
    target = Path(path).expanduser()
    if target.exists():
        return _REAL(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(template_path(), target)
    conn = _REAL(path)
    # A fresh `init_db` leaves its pages in the `-wal` file, and the copy
    # leaves an empty one. The indexer reads an empty file as text, so an
    # onboarding of the test's directory found one area more. One write of
    # an unchanged header page fills the `-wal` file as a fresh run does.
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    conn.execute(f"PRAGMA user_version = {int(version)}")
    return conn


def install() -> None:
    """Bind the wrapper wherever the real `init_db` is bound now.

    A module imported later reads `rota.core.db.init_db`, which is the
    wrapper from here on."""
    for name, module in list(sys.modules.items()):
        if name != "rota" and not name.startswith("rota."):
            continue
        if getattr(module, "init_db", None) is _REAL:
            module.init_db = init_db
