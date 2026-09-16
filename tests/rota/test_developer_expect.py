"""The Developer's wake carries what the batch is for and where the change
is expected. Read 2026-09-13 from a tipsI wake: one ticket line, four
criteria, nothing else."""
from rota.core.db import init_db
from rota.core.runner import push_working_set
from rota.core.sandbox import build
from rota.core.scheduler import Wake
from rota.roles import prompts
from rota.testkit.fixtures import seed_provenance, seed_ref


def _seed(conn):
    conn.execute("INSERT INTO entries (id, author, ts_order, text) VALUES "
                 "('e1','principal',1,'Split the bill: ask how many people are paying and print each share.')")
    conn.execute("INSERT INTO statements (id, span_entry, span_start, span_end, text, status) VALUES "
                 "('s1','e1',0,70,'Split the bill: ask how many people are paying and print each share.','ratified')")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) VALUES "
                 "('i1','each person pays an equal share of the total with tip','in_scope','approved',1,1)")
    seed_provenance(conn, "items", "i1", "decided")
    seed_ref(conn, "items", "i1", "statement", "s1")
    conn.execute("INSERT INTO batches (id, item_id, status) VALUES ('b1','i1','running')")
    conn.execute("INSERT INTO batch_touch (batch_id, grain, grain_kind, confidence) VALUES "
                 "('b1','main.py','path','expected'), ('b1','calculate_shares','symbol','possible')")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk1','i1','print each share')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES ('c1','tk1','each share is equal')")
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('b1','tk1')")
    conn.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) VALUES "
                 "('tst_1','b1','c1','tests/test_share.py','def test_share():\n    assert True\n')")
    conn.commit()


def test_batches_expect_names_the_item_the_words_the_touch_and_the_tests(tmp_path):
    db = init_db(tmp_path / "rota.db"); _seed(db)
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    out = sb.call("batches.expect")
    assert out["item"] == "each person pays an equal share of the total with tip"
    assert out["the principal said"] == ["Split the bill: ask how many people are paying and print each share."]
    assert out["expected to touch"] == ["main.py"]
    assert out["might touch"] == ["calculate_shares"]
    assert [t["path"] for t in out["tests"]] == ["tests/test_share.py"]


def test_the_batch_start_wake_pushes_it_without_being_asked(tmp_path):
    db = init_db(tmp_path / "rota.db"); _seed(db)
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    pushed = push_working_set("developer", sb, Wake("developer", "tick:batch_start", refs=("b1",)))
    assert "batches.expect" in pushed, sorted(pushed)
    assert pushed["batches.expect"]["expected to touch"] == ["main.py"]
