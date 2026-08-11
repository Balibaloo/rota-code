"""
The Researcher's plumbing, with no model involved.

The role's *judgement* is L1's business — whether it reads a clause correctly and
declines to overreach. What is checked here is the containment, because that is
the part that has to hold whether the model is good or bad:

  * nothing is reachable that was not granted
  * nothing goes out that was not asked about
  * every fetch replays, so this is not the one role whose tests need a network
  * a wrong answer stays a wrong row, and cannot become a constraint by itself
"""
from __future__ import annotations

import pathlib
import tempfile

import pytest

from rota.core import sandbox as sandbox_mod, web
from rota.core.db import init_db
from rota.core.runner import run_session
from rota.core.scheduler import Wake
from rota.design import graph as graph_mod
from rota.llm.llm import Pins, ScriptedBackend
from rota.testkit import fixtures

RFC = "https://www.rfc-editor.org/rfc/rfc6749#section-4.1.3"
BODY = ("4.1.3.  Access Token Request\n\n   redirect_uri\n         REQUIRED, if "
        "the \"redirect_uri\" parameter was included in the authorization "
        "request as described in Section 4.1.1, and their values MUST be "
        "identical.\n")


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


# ---------------------------------------------------------------------------
# The allowlist
# ---------------------------------------------------------------------------

def test_nothing_is_reachable_by_default():
    """A capability that reaches outside the engagement is granted, never merely
    not-forbidden. An empty allowlist reaches nothing at all."""
    assert not web.allowed("https://www.rfc-editor.org/rfc/rfc6749", [])


def test_a_subdomain_of_a_granted_domain_is_granted():
    assert web.allowed("https://datatracker.ietf.org/doc/html/rfc6749", ["ietf.org"])


def test_a_domain_that_merely_ends_in_a_granted_one_is_not():
    """The mistake this kind of check is famous for. `evil-ietf.org` shares a
    suffix with `ietf.org` and has nothing to do with it, so the match is
    anchored on a dot."""
    assert not web.allowed("https://evil-ietf.org/rfc6749", ["ietf.org"])
    assert not web.allowed("https://ietf.org.attacker.test/x", ["ietf.org"])


def test_a_refusal_is_a_result_not_a_crash(db):
    """A domain outside the allowlist is a fact to report back to whoever asked,
    not a failure to retry out of. The session carries on."""
    sb = sandbox_mod.build("researcher", db, session_id="s1")
    out = sb.call("web.fetch", url="https://example.test/x")
    assert "refused" in out and "allowlist" in out["refused"]


# ---------------------------------------------------------------------------
# Replay
# ---------------------------------------------------------------------------

def test_a_cached_page_is_served_without_a_network(db):
    web.store(db, RFC, BODY, 200)
    got = web.fetch(db, RFC, allowlist=[], offline=True)
    assert got["body"] == BODY


def test_a_missing_page_offline_fails_loudly(db):
    """Rather than reaching out. A case that forgot to record its page should
    fail on every machine, not pass on the one with a network."""
    web.ensure_cache(db)
    with pytest.raises(web.NotAllowed):
        web.fetch(db, RFC, allowlist=["rfc-editor.org"], offline=True)


def test_the_hash_changes_when_the_page_does(db):
    first = web.store(db, RFC, BODY, 200)
    second = web.store(db, RFC, BODY + "\n   (revised)\n", 200)
    assert first["content_hash"] != second["content_hash"], \
        "a page changing under a citation is the drift event; the hash is how it shows"


# ---------------------------------------------------------------------------
# Bounded reads
# ---------------------------------------------------------------------------

def test_a_page_is_never_returned_whole(db):
    """An RFC is longer than any working set and four paragraphs of it answer the
    question — the same index/body split that keeps a working set viable over a
    large codebase keeps one over a large document."""
    huge = ("filler. " * 4000) + "the redirect_uri values MUST be identical" + (" tail." * 4000)
    passage = web.extract(huge, "redirect_uri")
    assert len(passage) <= web.PASSAGE
    assert "MUST be identical" in passage, "it should return the part that was asked for"


def test_the_url_fragment_picks_the_passage(db):
    """`#section-4.1.3` is exactly how a codebase that cites a specification
    writes it down, so the anchor is a free guess at which part matters."""
    body = ("preamble " * 200) + "4.1.3. Access Token Request: values MUST be identical"
    assert "MUST be identical" in web.extract(body, "", "section-4.1.3")


def test_markup_does_not_reach_the_prompt():
    assert "<script>" not in web.extract("<html><script>x=1</script><p>hello</p>")


# ---------------------------------------------------------------------------
# Containment
# ---------------------------------------------------------------------------

def test_the_researcher_can_write_nothing_but_its_own_record(db):
    """The whole containment in one assertion. A wrong answer stays a wrong row;
    it cannot become a constraint that blocks real work forever, because the
    function that would do that was never built for this role."""
    sb = sandbox_mod.build("researcher", db, session_id="s1")
    writes = {f for f in sb.functions()
              if not f.startswith(("msg.", "references.load", "web."))}
    assert writes == {"references.record"}, sorted(writes)


def test_the_researcher_cannot_run_anything(db):
    sb = sandbox_mod.build("researcher", db, session_id="s1")
    assert not [f for f in sb.functions() if f.startswith("code.")]


def test_only_roles_that_can_cite_may_ask(db):
    """Law 3 derives this — a role may ask because it reads `references`. Critic
    judges against internal criteria and owns nothing to cite into; Liaison's
    outside is the principal, not the web."""
    g = graph_mod.load()
    askers = {e.s for e in g.of_type("messages")
              if e.t == "researcher" and e.v == "question"}
    assert askers == {"terminologist", "architect", "gatekeeper", "developer", "tester"}
    assert "critic" not in askers and "liaison" not in askers


def test_nobody_can_ask_the_web(db):
    """`web` is a fact artefact: reading it yields evidence, not judgement, so it
    generates no contact and there is nobody to ask."""
    g = graph_mod.load()
    assert not g.contactable("web")


# ---------------------------------------------------------------------------
# The question channel
# ---------------------------------------------------------------------------

def test_a_question_to_the_researcher_carries_words(db):
    """The one declared exception to law 2, and it is structural: the recipient
    shares no database, so an id means nothing at its end."""
    sb = sandbox_mod.build("architect", db, session_id="s1")
    sig = [s for s in sb.signatures() if "question_researcher" in s]
    assert sig == ["msg.question_researcher(refs, question, round_no=0)"]


def test_every_other_channel_still_refuses_words(db):
    sb = sandbox_mod.build("architect", db, session_id="s1")
    for sig in sb.signatures():
        # The *parameters*, not the name — `msg.question_terminologist` has the
        # word in its verb and takes no words at all, which is the point.
        params = sig.split("(", 1)[1]
        if sig.startswith("msg.") and "researcher" not in sig:
            assert "question" not in params, f"prose leaked onto {sig}"


def test_a_question_with_no_words_is_refused(db):
    sb = sandbox_mod.build("architect", db, session_id="s1")
    with pytest.raises(ValueError, match="shares no artefact"):
        sb.call("msg.question_researcher", refs=[], question="")


# ---------------------------------------------------------------------------
# End to end, scripted
# ---------------------------------------------------------------------------

def test_a_session_fetches_records_and_answers(db):
    web.store(db, RFC, BODY, 200)
    db.execute(
        "INSERT INTO messages (id, thread_id, from_role, to_role, verb, body_refs, "
        "body_text, seq) VALUES ('m_in','t1','architect','researcher','question','[]',"
        "'what does 4.1.3 require of redirect_uri', 1)")

    outcome = run_session(
        db, Wake(role="researcher", kind="message", message_id="m_in",
                 detail="question"),
        backend=ScriptedBackend([
            f"TOOL: web.fetch(url='{RFC}', looking_for='redirect_uri')",
            f"TOOL: references.record(id='ref1', url='{RFC}', "
            f"claim='redirect_uri must be identical to the authorization request', "
            f"quote='their values MUST be identical')\n"
            f"TOOL: msg.answer_architect(refs=['ref1'])",
            "done",
        ]), pins=Pins(model="scripted"), native_tools=False)

    assert outcome.committed, outcome.errors
    row = db.execute("SELECT * FROM references_ WHERE id = 'ref1'").fetchone()
    assert row["content_hash"], "a recorded source carries the hash of what was read"
    assert row["asked_by"] == "architect", \
        "attributed to who wanted to know, not to who looked it up"
    assert db.execute(
        "SELECT 1 FROM messages WHERE from_role='researcher' AND to_role='architect'"
    ).fetchone()


def test_the_cap_stops_it_reading_forever(db):
    """A third scarcity, and deliberately not `loop_cap`: that one spends compute
    and this one spends somebody else's server."""
    from rota.core import config

    config.set(db, "research_cap", 1)
    for n in range(3):
        web.store(db, f"https://rfc-editor.org/{n}", BODY, 200)
    sb = sandbox_mod.build("researcher", db, session_id="s1")

    assert "passage" in sb.call("web.fetch", url="https://rfc-editor.org/0")
    sb.call("web.fetch", url="https://rfc-editor.org/1")
    refused = sb.call("web.fetch", url="https://rfc-editor.org/2")
    assert "refused" in refused and "research_cap" in refused["refused"]
