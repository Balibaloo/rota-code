"""
Frame 327: the native schema showed a `list[str]` parameter as a string.

The future import makes every annotation a string, so `_json_type` read
`'list[str]'` and returned `{"type": "string"}`. qwen3.5:9b then sent
`refs='["c_734322", "tst_dcae01"]'`, a JSON string, and the `refs` door
refused it with no correct form.
"""
from __future__ import annotations

import pytest

from rota.core.db import init_db
from rota.core.sandbox import build
from rota.llm import toolschema
from rota.roles import api

ARRAY = {"type": "array", "items": {"type": "string"}}


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def _props(schema):
    return schema["function"]["parameters"]["properties"]


def _shape(prop):
    return {k: v for k, v in prop.items() if k != "description"}


def test_a_msg_function_offers_refs_as_an_array(db):
    sb = build("vision_keeper", db)
    msgs = [s for s in toolschema.schemas_for_sandbox(sb)
            if s["function"]["name"].startswith("msg__")]
    assert msgs
    for schema in msgs:
        assert _shape(_props(schema)["refs"]) == ARRAY, schema["function"]["name"]


def test_the_exec_built_challenge_keeps_its_union_and_its_array(db):
    """The exec'd `send` has its own namespace, and its annotations evaluate
    there."""
    sb = build("developer", db)
    (challenge,) = [s for s in toolschema.schemas_for_sandbox(sb)
                    if s["function"]["name"] == "msg__challenge_tester"]
    props = _props(challenge)
    assert _shape(props["refs"]) == ARRAY
    assert _shape(props["quotes"]) == {"type": "string"}
    assert _shape(props["round_no"]) == {"type": "integer"}


def test_an_api_list_parameter_is_an_array():
    adopt = toolschema.schema_for("glossary.adopt", api.glossary_adopt)
    assert _shape(_props(adopt)["ids"]) == ARRAY
    consult = toolschema.schema_for("glossary.consult", api.glossary_consult)
    assert _shape(_props(consult)["terms"]) == ARRAY


def test_an_annotation_that_does_not_evaluate_keeps_the_old_reading(caplog):
    def fn(a: NoSuchName, b: list[str]) -> dict:  # noqa: F821
        return {}

    with caplog.at_level("WARNING", logger="rota.llm.toolschema"):
        props = _props(toolschema.schema_for("x.y", fn))
    assert _shape(props["a"]) == {"type": "string"}
    assert _shape(props["b"]) == {"type": "string"}
    (warned,) = [r for r in caplog.records if r.name == "rota.llm.toolschema"]
    assert warned.levelname == "WARNING"
    assert "x.y" in warned.getMessage()
    assert "NoSuchName" in warned.getMessage()


def test_a_function_that_evaluates_warns_nothing(caplog):
    with caplog.at_level("WARNING", logger="rota.llm.toolschema"):
        toolschema.schema_for("glossary.adopt", api.glossary_adopt)
    assert not [r for r in caplog.records if r.name == "rota.llm.toolschema"]


def test_the_refs_door_names_a_list_in_a_string_and_shows_the_form(db):
    """The trial's refused call, qwen3.5:9b on the Developer challenge."""
    sb = build("vision_keeper", db)
    with pytest.raises(ValueError) as refused:
        sb.call("msg.report_liaison", refs='["c_734322", "tst_dcae01"]')
    said = str(refused.value)
    assert said == (
        "refs is a list, not a string that holds a list. You sent "
        "'[\"c_734322\", \"tst_dcae01\"]'. Send the list itself: "
        'refs=["c_734322", "tst_dcae01"]')
    assert "bare string" not in said
    assert not db.execute("SELECT 1 FROM messages").fetchall()


def test_a_list_string_that_does_not_parse_shows_the_example(db):
    sb = build("vision_keeper", db)
    with pytest.raises(ValueError) as refused:
        sb.call("msg.report_liaison", refs="[c_734322, tst_dcae01]")
    assert str(refused.value).endswith(
        'Send the list itself: refs=["s_1b9009", "c_734322"]')


@pytest.mark.parametrize("sent, form", [
    ("m_283ec8", 'refs=["m_283ec8"]'),
    ("b_9f9824, i_62de3d", 'refs=["b_9f9824", "i_62de3d"]'),
    ("b_9f9824 i_62de3d", 'refs=["b_9f9824", "i_62de3d"]'),
    ("refs: b_348da1", 'refs=["b_348da1"]'),
    ("", "refs=[]"),
])
def test_the_refs_door_lists_each_id_of_a_bare_string(db, sent, form):
    sb = build("vision_keeper", db)
    with pytest.raises(ValueError) as refused:
        sb.call("msg.report_liaison", refs=sent)
    said = str(refused.value)
    assert f"you sent a bare string, {sent!r}" in said
    assert said.endswith(f"Send a list: {form}")
    assert not db.execute("SELECT 1 FROM messages").fetchall()
