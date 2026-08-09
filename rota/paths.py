"""
Where things are. One anchor, stated once.

Ten modules each computed their own location from `__file__` — usually
`parent`, sometimes `parents[1]`, once `parents[2]`. That works exactly as long
as nothing moves, and fails *silently* when something does: a path built from
the wrong number of `parents` still resolves, it just points somewhere empty, so
the schema loads as blank or the prompt directory reads as a role with no modes.

This is the same principle as everything else here. A fact stated in ten places
is a fact that will disagree with itself; the reorganisation is the moment it
would have.
"""
from __future__ import annotations

from pathlib import Path

# This file lives at the package root, and that is the only assumption made.
PACKAGE = Path(__file__).resolve().parent
REPO = PACKAGE.parent

SCHEMA = PACKAGE / "schema.sql"
DESIGN = PACKAGE / "design"
PROMPTS = PACKAGE / "prompts"

VIEWER = PACKAGE / "viewer.html"
STATIC = PACKAGE / "static"

# Instrumentation, not artefacts: these live beside the repo, not inside the
# package, because they are about a run rather than about the system.
COVERAGE_FILE = REPO / ".rota-coverage.json"
DEV_DB = REPO / ".rota" / "dev.db"

# The design documents this was built from. Outside the package on purpose —
# they are the source, not the product.
DOCS = REPO / "rota_tui"
