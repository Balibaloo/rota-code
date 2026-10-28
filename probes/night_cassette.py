"""
The night's recorded wakes: the backend wrap of frame 233, step 1.

An onboarding wake whose whole prompt matches a recording takes the recorded
reply and spends no GPU. Night 145 against night 144 gave 85 of 85 identical
first replies to identical prompts (plans/night-reuse-investigation.md, part
4 D). The key is `cassettes.key_for`: the model, the temperature, `num_ctx`,
the protocol, the whole system text and the user text.

`probes/walk.py` runs on import, so a test cannot import it. The wrap lives
here, and the walk calls `wrap` once where it builds its backend.
"""
from __future__ import annotations

import os
from pathlib import Path

from rota import paths
from rota.llm import llm
from rota.llm.cassettes import RecordingBackend, open_dev_db

#: The phase the gauntlet gives the onboarding walk (`gauntlet_click.sh`).
ONBOARDING = "onboarding"

def cassette_path() -> Path:
    """The night's own file. Never the register's `tests/rota/cassettes.db`:
    the register is a release asset, and frame 66 found that a replay under a
    new load read there as a new experiment."""
    return Path(os.environ.get("ROTA_NIGHT_CASSETTES")
                or paths.RUNS / "night_cassettes.db")


class NightBackend(RecordingBackend):
    """
    `RecordingBackend` with a name per session and the card's endpoint.

    The runner writes `getattr(backend, "name")` to `sessions.backend` once,
    after the last turn. So the name reports the calls since the previous
    read: `cassette:<inner>` when every call hit, the inner name when one call
    ran live or no call ran. The column then counts the replayed sessions, as
    the frame's ends-when asks. The walk calls `begin` before each step,
    because a failed session never reads the name.

    The replay is valid for the text protocol only. The key holds the
    protocol and not the native tool schemas, so a changed schema keeps the
    key (frame 233's review, finding 2). The night runs the text protocol.
    """

    def __init__(self, inner: llm.Backend, dev_conn, *, replay: bool):
        super().__init__(inner, dev_conn, replay=replay)
        self._calls = 0
        self._hits = 0

    def begin(self) -> None:
        """Start the count of one session (frame 233's review, finding 1)."""
        self._calls = self._hits = 0

    @property
    def name(self) -> str:
        inner = getattr(self.inner, "name", "")
        whole = self._calls and self._hits == self._calls
        self._calls = self._hits = 0
        return f"cassette:{inner}" if whole else inner

    # `loop._spill_endpoint` does not follow a wrap, so the wrap shows the
    # server it calls. Otherwise a night reads no card (investigation, 2.5).
    @property
    def host(self):
        return getattr(self.inner, "host", None)

    @property
    def default(self):
        return getattr(self.inner, "default", None)

    def complete(self, system, user, pins, tools=None):
        # The stop reason travels in the `cassettes` row, so the replay
        # returns it as the suite's replay does. Night 147 replayed five cut
        # replies as whole, and the runner ran the blocked call (frame 233).
        before = self.hits
        result = super().complete(system, user, pins, tools=tools)
        self._calls += 1
        self._hits += self.hits - before
        return result


def wrap(backend: llm.Backend | None, phase: str) -> llm.Backend | None:
    """
    The walk's backend for one phase.

    A walk phase gets the backend unchanged. The principal's answers make the
    walks differ, so a replayed walk session would count as a new sample when
    it is not one (investigation, part 4 D, Risk). Onboarding always records.
    Onboarding replays only when `WALK_REPLAY=1`, so a night can run live and
    refresh the recordings, as `MAX_WARM` does for the warm start.
    """
    if phase != ONBOARDING:
        return backend
    path = cassette_path()
    # A missing file is an empty cassette: sqlite creates it on connect.
    path.parent.mkdir(parents=True, exist_ok=True)
    replay = os.environ.get("WALK_REPLAY") == "1"
    return NightBackend(backend or llm.default_backend(), open_dev_db(path),
                        replay=replay)
