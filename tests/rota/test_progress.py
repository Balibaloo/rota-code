"""probes/progress.py: the block is facts of the run database."""
import importlib.util
import json
import os
import time

from rota import paths
from rota.core.db import init_db


def _mod():
    spec = importlib.util.spec_from_file_location("progress", paths.REPO / "probes" / "progress.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def test_the_block_reads_the_stage_the_count_and_the_reference(tmp_path, monkeypatch):
    monkeypatch.setenv("ROTA_RUNS", str(tmp_path))
    m = _mod()
    conn = init_db(tmp_path / "clickI.db")
    for n, (role, kind, detail) in enumerate([("liaison", "message", "present"), ("developer", "tick:tests_failing", "attempt 2")], 1):
        conn.execute("INSERT INTO sessions (id, role, wake_kind, wake_detail, committed, seq, mode, model) VALUES (?, ?, ?, ?, 1, ?, 'normal', 'm')", (f"s{n}", role, kind, detail, n))
    conn.commit()
    m.finish("clickI", "sentence 2", 42, 10.0, "merged", "70")
    out = m.render("clickI", "sentence 2", 0, time.time() - 120, "[m9] present: x -> 'yes'")
    assert "stage: fix loop (attempt 2 of 3)" in out
    assert "wakes: 2 so far / 42 on night 70 (merged) = 4%; left: about 40" in out
    assert "minutes: 2 so far / 10 on night 70" in out
    assert "last page: [m9] present: x -> 'yes'" in out and "last wake: developer:tick:tests_failing attempt 2" in out
    ref = json.loads((tmp_path / "progress_ref_clickI.json").read_text())
    assert ref["sentence 2 / merged"]["wakes"] == 42
