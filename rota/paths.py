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

import os
from pathlib import Path

# This file lives at the package root, and that is the only assumption made.
PACKAGE = Path(__file__).resolve().parent
REPO = PACKAGE.parent

# Each asset lives with the group that reads it. When the package was
# regrouped, this file was the only one that had to change — which was the
# point of writing it.
SCHEMA = PACKAGE / "core" / "schema.sql"
DESIGN = PACKAGE / "design"
PROMPTS = PACKAGE / "roles" / "prompts"
PROFILES = PACKAGE / "llm" / "profiles"      # the shipped run profiles

VIEWER = PACKAGE / "cockpit" / "viewer.html"
STATIC = PACKAGE / "cockpit" / "static"

# Instrumentation, not artefacts: these live beside the repo, not inside the
# package, because they are about a run rather than about the system.
COVERAGE_FILE = REPO / ".rota-coverage.json"

# How long the model tiers took, per machine, never committed. A duration is a
# fact about this GPU on this day at this thermal state, and putting it beside
# the cassettes would make it look like evidence about the prompts. Kept because
# one run's number answers "how long will this take" and a series answers the
# better question: whether it is getting slower.
TIMINGS_FILE = REPO / ".rota-timings.json"

# Cassettes are *evidence*, not runtime state, so they live with the tests and
# not in `.rota/`. `.rota/` is the state directory, which is correct for a
# database about a running project and wrong for a record of what a model did
# on a given prompt.
#
# The file is not tracked by Git. It is about 590 MB and a recording session
# writes a new version most days, so 153 versions had reached 57 GB of LFS.
# `rota/README.md` says how to get one. Overridable because the repo may live
# on a slow drive: point ROTA_DEV_DB at an SSD and the recorder's write storm
# moves with it.
DEV_DB = Path(os.environ.get("ROTA_DEV_DB",
                             REPO / "tests" / "rota" / "cassettes.db"))

# The case files, for the same reason: they are the authority on what a case is,
# so a tool reading recorded runs can tell a live case from a renamed one.
CASES = REPO / "tests" / "rota" / "cases"

# The design documents this was built from: HANDOFF.md and TESTS.md, filed
# beside the other documents at the top of the package. They lived outside
# it as `rota_tui/` until the split of 2026-09-14, when that name stopped
# meaning anything. The graph they describe is `design/team-graph.html`.
DOCS = PACKAGE
