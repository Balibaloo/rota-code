"""
The second build of the scene `merged_then_next`, in a file of its own.

The build meets the first build's rows, and lands the scene's right calls
through whole sessions (`scenes.LANDINGS`). A file of its own lets the
gate's workers build it beside the first build (the review of 7a056ce0,
finding 8). `tests/rota/scene_tests.py` says how the two builds meet.
"""
from __future__ import annotations

from tests.rota.scene_tests import make_again

globals().update(make_again("merged_then_next"))
