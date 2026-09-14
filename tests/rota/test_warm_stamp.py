"""probes/warm_stamp.py: the warm gate and the relocate."""
import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

from rota import paths
from rota.core.db import init_db

STAMP = paths.REPO / "probes" / "warm_stamp.py"


def _run(args, env):
    full = {**os.environ, **env}
    return subprocess.run([sys.executable, str(STAMP), *args], capture_output=True, text=True,
                          cwd=str(paths.REPO), env=full)


def _snapshot(runs: Path, routing: str, root: str, monkeypatch):
    conn = init_db(runs / "clickI_warm.db")
    conn.execute("INSERT INTO config (key, value) VALUES ('model_routing', ?)", (json.dumps(routing),))
    conn.execute("INSERT INTO config (key, value) VALUES ('project_root', ?)", (root,))
    conn.commit(); conn.close()
    import importlib.util
    spec = importlib.util.spec_from_file_location("warm_stamp", STAMP)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    monkeypatch.setenv("ROTA_RUNS", str(runs))
    mod.write("clickI")


def test_a_snapshot_of_another_profile_is_a_cold_start(tmp_path, monkeypatch):
    """Night 62 (2026-09-14): a warm start from another profile's snapshot
    ran the Developer on the wrong model with no error."""
    runs = tmp_path / "runs"; runs.mkdir()
    env = {"ROTA_RUNS": str(runs)}
    _snapshot(runs, "developer=nobody:1b", str(tmp_path), monkeypatch)
    out = _run(["check", "clickI"], {**env, "GAUNTLET_PROFILE": "local-gemma-critic"})
    assert out.returncode == 1 and "COLD: the snapshot routes" in out.stdout, out.stdout + out.stderr
    assert not (runs / "clickI_warm.db").exists()


def test_relocate_points_the_run_at_the_new_checkout(tmp_path):
    runs = tmp_path / "runs"; runs.mkdir()
    conn = init_db(runs / "clickI.db")
    conn.execute("INSERT INTO config (key, value) VALUES ('project_root', 'D:/old/clickI')")
    conn.commit(); conn.close()
    out = _run(["relocate", "clickI", str(tmp_path / "new")], {"ROTA_RUNS": str(runs)})
    assert out.returncode == 0, out.stdout + out.stderr
    got = sqlite3.connect(runs / "clickI.db").execute("SELECT value FROM config WHERE key='project_root'").fetchone()[0]
    assert got == str(tmp_path / "new")
