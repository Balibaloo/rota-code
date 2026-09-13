"""What a wake pushes, read as the person doing the job would (the wake
audit, plans/wake-audit.md)."""
from rota.core.db import init_db
from rota.core.runner import push_working_set
from rota.core.sandbox import build
from rota.core.scheduler import Wake
from rota.roles import prompts


def test_the_slicing_wake_sets_its_item_apart_from_the_account(tmp_path):
    """clickI night 35 (2026-09-13): woken for one item and shown five, the
    Vision Keeper sliced all five and four were refused."""
    db = init_db(tmp_path / "rota.db")
    for i, text in (("how_it_works", "the program is a CLI toolkit"),
                    ("echo_json", "add an echo_json helper next to echo")):
        db.execute("INSERT INTO items (id, text, kind, provenance, approval, approval_ver, version) "
                   "VALUES (?, ?, 'in_scope', 'decided', 'approved', 1, 1)", (i, text))
    db.commit()
    sb = build("vision_keeper", db, mode="slicing",
               allow=prompts.mode_tools("vision_keeper", "slicing"))
    pushed = push_working_set("vision_keeper", sb, Wake("vision_keeper", "tick:slicing", refs=("echo_json",)))
    account = pushed["problem.consult"]
    assert [r["id"] for r in account["to slice, this wake"]] == ["echo_json"]
    assert account["the rest of the account, not this wake's"] == ["how_it_works"]
