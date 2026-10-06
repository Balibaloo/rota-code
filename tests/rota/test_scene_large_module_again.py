"""
The second build of the scene `large_module`, in a file of its own.

The build meets the first build's rows. The scene has no landings yet, so
the test compares the two builds only. A file of its own lets the gate's
workers build it beside the first build (the review of 7a056ce0, finding
8). `tests/rota/scene_tests.py` says how the two builds meet.
"""
from __future__ import annotations

from tests.rota.scene_tests import make_again

globals().update(make_again("large_module"))
