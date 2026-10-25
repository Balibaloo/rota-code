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


def test_an_annotation_that_does_not_evaluate_keeps_the_old_reading():
    def fn(a: NoSuchName, b: list[str]) -> dict:  # noqa: F821
        return {}

    props = _props(toolschema.schema_for("x.y", fn))
    assert _shape(props["a"]) == {"type": "string"}
    assert _shape(props["b"]) == {"type": "string"}
