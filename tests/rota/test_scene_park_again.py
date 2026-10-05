"""
S3 and S4, the park, built a second time.

The park is the slowest scene: twenty harness runs and five commits. Its
second build is in this file, so that a second worker builds it beside
`test_scene_park.py` (the review of 906b765, finding 12).
"""
from __future__ import annotations

from tests.rota.scene_tests import make

NAME = "park"

globals().update(make(NAME, parts=("again",)))
