"""
The artefact-quality checks, against the artefacts that motivated them.

Every string in this file was produced by a real session on oauthlib. That
matters more than usual: a fabrication detector tested on fabrications I invented
is a detector tuned to my imagination, and the failure it has to catch is one
that already fooled me once.

Each check is also asserted *not* to fire on a good artefact, because a
fabrication detector that flags real findings is worse than none — it trains you
to skim the output, which is exactly how the twenty-four constraints got past a
reader in the first place.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import init_db
from rota.testkit import artefacts


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def _constraint(conn, id, headline, text="", provenance="observed",
                bindings=(), source_refs=()):
    conn.execute(
        "INSERT INTO constraints (id, headline, text, provenance, source_refs) "
        "VALUES (?,?,?,?,?)",
        (id, headline, text, provenance, json.dumps(list(source_refs))))
    for g in bindings:
        conn.execute("INSERT INTO constraint_bindings (constraint_id, grain, "
                     "grain_kind) VALUES (?,?,'path')", (id, g))


def _term(conn, id, term, short, provenance="observed", source_refs=(), body=""):
    conn.execute(
        "INSERT INTO glossary_terms (id, term, sense_short, sense_body, "
        "provenance, source_refs) VALUES (?,?,?,?,?,?)",
        (id, term, short, body, provenance, json.dumps(list(source_refs))))


# ---------------------------------------------------------------------------


BRIEF = (
    "What you are looking for is narrow and specific: a commitment the code is "
    "keeping to something outside itself. A retention period. A boundary a piece "
    "of data may not cross. An interface something else depends on. An ordering "
    "that another system relies on."
)


def test_a_headline_built_from_the_brief_is_caught(db):
    """
    The exact output, and the exact brief that produced it. Three of the four
    illustrations came back as headlines with the nearest grain name appended,
    which is `<brief example>` + `<what it could see>` and not a claim about
    OAuth at all.
    """
    _constraint(db, "c1", "Retention period for client tokens")
    _constraint(db, "c2", "Interface for client tokens")
    _constraint(db, "c3", "Ordering for client tokens")

    found = {f.row_id for f in artefacts.echoes_the_brief(db, BRIEF)}
    assert found == {"c1", "c2", "c3"}


def test_a_real_constraint_is_not_caught_by_the_echo_check(db):
    """
    The signature base string is the strongest genuine commitment in oauthlib
    and shares ordinary words with the brief. Flagging it would make the check
    worthless — a detector that fires on findings teaches you to skim.
    """
    _constraint(db, "c1",
                "The signature base string is byte-exact per RFC 5849 s3.4.1")
    _constraint(db, "c2",
                "Percent-encoding follows RFC 3986 unreserved characters only")

    assert artefacts.echoes_the_brief(db, BRIEF) == []


def test_a_definition_that_only_restates_its_own_name(db):
    """Verbatim from the run: the grain name goes in, a paraphrase comes out,
    and nothing that required opening the file appears anywhere."""
    _term(db, "deviceapplicationserver", "DeviceApplicationServer",
          "a class in oauth2/rfc8628/endpoints/pre_configured.py")
    _term(db, "endpoint", "endpoint", "an instance or path in OAuth protocols")

    caught = {f.row_id for f in artefacts.restates_the_index(db)}
    assert "deviceapplicationserver" in caught


def test_a_definition_that_required_reading_is_left_alone(db):
    """The `nonce` sense the answer key predicted and both runs missed. If the
    check cannot tell this from the one above, it is measuring length."""
    _term(db, "nonce", "nonce",
          "a value the server stores and rejects on repeat, guarding replay")

    assert artefacts.restates_the_index(db) == []


def test_a_number_in_no_file_the_constraint_binds(db, tmp_path):
    """
    "Retention period for access tokens is 30 days", five times, against a
    repository with no retention policy and no thirty in it.

    The cheapest high-confidence fabrication check there is: a real commitment
    to a number has the number written down somewhere.
    """
    (tmp_path / "tokens.py").write_text(
        "class BearerToken:\n    def estimate_type(self):\n        return 9\n",
        encoding="utf-8")

    _constraint(db, "c1", "Retention period for access tokens is 30 days",
                bindings=["tokens.py"])
    _constraint(db, "c2", "estimate_type returns 9 for a bearer header",
                bindings=["tokens.py"])

    found = artefacts.numbers_not_in_source(db, tmp_path)
    assert [f.row_id for f in found] == ["c1"], \
        "the real number was flagged, or the invented one was not"
    assert "30" in found[0].detail


def test_duplicates_are_reported_per_artefact(db):
    """24 constraints, 6 headlines. Both ids derive from content now, so this
    should be empty in practice — kept because "should be impossible" is the
    state a check exists to confirm."""
    _constraint(db, "c1", "Tokens expire")
    _constraint(db, "c2", "tokens expire")

    found = artefacts.duplicated(db)
    assert len(found) == 1 and found[0].artefact == "constraints"


def test_cited_with_nothing_behind_it(db):
    """Law 11 makes provenance explicit so a claim can be checked. A row saying
    it was cited and naming no reference has used the strongest word available
    to mean the weakest thing."""
    _constraint(db, "c1", "Base string per RFC 5849", provenance="cited")
    _constraint(db, "c2", "Ports per RFC 2818", provenance="cited",
                source_refs=["r_missing"])

    found = {f.row_id: f.detail for f in artefacts.unbacked_citations(db)}
    assert set(found) == {"c1", "c2"}
    assert "no source_refs" in found["c1"]
    assert "r_missing" in found["c2"]


def test_an_observed_constraint_needs_no_reference(db):
    """`observed` means found in the code and is the normal case for a survey.
    Demanding a URL for it would push every session toward inventing one."""
    _constraint(db, "c1", "Base string is byte-exact", provenance="observed")
    assert artefacts.unbacked_citations(db) == []


def test_audit_runs_every_check_and_a_clean_run_is_silent(db, tmp_path):
    """The shape the scoring actually uses. A clean run must produce nothing at
    all, or the report becomes noise nobody reads."""
    (tmp_path / "signature.py").write_text(
        "# RFC 5849 section 3.4.1.1\ndef base_string(): ...\n", encoding="utf-8")
    _constraint(db, "c1", "The signature base string follows RFC 5849 3.4.1",
                text="Normalisation order is byte-exact; peers reject a "
                     "signature built any other way.",
                bindings=["signature.py"])
    _term(db, "nonce", "nonce",
          "a value the server stores and rejects on repeat, guarding replay")

    assert artefacts.audit(db, tmp_path, brief=BRIEF) == []


def test_constraint_zero_is_not_judged_as_if_a_role_wrote_it(db):
    """
    The audit's own first false positive, caught by running it against the real
    run rather than against invented rows.

    Constraint zero is seeded by the system — "this area has not been surveyed",
    bindings derived from the survey records — and it tripped the echo check for
    the excellent reason that the scheduler and the brief use the same word for
    the same thing. A report that flags derived state as authored earns the skim
    it then gets, which is how twenty-four constraints got past a reader in the
    first place.
    """
    from rota.onboarding import boot

    db.execute("INSERT INTO constraints (id, headline, provenance) VALUES (?,?,?)",
               (boot.ZERO, boot.ZERO_HEADLINE, "observed"))
    db.execute("INSERT INTO constraint_bindings (constraint_id, grain, grain_kind) "
               "VALUES (?,?,'path')", (boot.ZERO, "src/billing"))

    brief = "You are looking for a commitment. Name the area you surveyed."
    assert artefacts.echoes_the_brief(db, brief) == []
    assert artefacts.audit(db, ".", brief=brief) == []


def test_a_file_path_is_not_a_glossary_term(db):
    """
    Fourteen of twenty-six terms in the second oauthlib run were paths. That is
    the index copied into the glossary with the columns relabelled.

    `restates_the_index` should have caught them and did not, which is the more
    useful half: it compares a definition against its term, and when the term
    *is* the path, the definition's prose reads as novel content. A check aimed
    at the definition cannot see a fault in the subject.

    Half of that blind spot has since closed. `_name_words` splits a name into
    the words it is made of, so `AccessTokenEndpoint` now subtracts *access*,
    *token* and *endpoint* from its own definition and `p2` is caught twice
    over. `p1` still is not, and that is the case that keeps the two checks
    apart: *protocol*, *implementation* and *handling* are real words that a
    reader could have written, and nothing about the definition gives the fault
    away. Only looking at the subject does.
    """
    _term(db, "p1", "oauth1/rfc5849/errors.py",
          "OAuth 1.0 protocol implementation error handling")
    _term(db, "p2", "oauth1/rfc5849/endpoints/access_token.py::AccessTokenEndpoint",
          "OAuth 1.0 access token endpoint class")
    _term(db, "ok", "nonce",
          "a value the server stores and rejects on repeat, guarding replay")

    assert {f.row_id for f in artefacts.restates_the_index(db)} == {"p2"}, \
        "p1 must stay invisible to this check, or the path check has no reason " \
        "to exist separately"
    caught = {f.row_id for f in artefacts.a_term_is_a_word(db)}
    assert caught == {"p1", "p2"}


def test_a_constraint_with_no_body_is_a_title(db):
    """
    Eight of eleven in the second run, including the one bound to
    `signature.py::sign_hmac_sha256_with_client` — it read the right file, under
    a rule that made it read, and wrote a title. Reading was made compulsory;
    saying something was not.
    """
    _constraint(db, "c1", "OAuth1 RFC5849 Signature Methods Commitment", text="")
    _constraint(db, "c2", "Base string is byte-exact",
                text="Normalisation order per RFC 5849 3.4.1.3.2; peers reject "
                     "a signature built any other way.")

    caught = {f.row_id for f in artefacts.a_constraint_needs_a_body(db)}
    assert caught == {"c1"}


def test_a_qualifier_does_not_rescue_a_restatement(db):
    """
    Twelve of icalendar's twenty-four terms carried a `sense_short` of exactly
    this shape — `date_class`: "specific date class", `datetime_object`:
    "specific datetime object" — the name said back with an adjective in front.

    Two faults let that through, and the strings here isolate the first. The
    check subtracts the term's own words and a set of generic kind-nouns, then
    asks what remains. `class`, `object` and `type` were all in that set;
    `specific` was not, so it survived as the one "novel" word and carried the
    definition past on its own. `_words` also tokenises on `[a-z0-9_]+`, so
    `date_class` stayed a single token and the term's own words were never
    subtracted at all.

    In the run itself those rows also had bodies, which is what actually kept
    them clean — so fixing this check does not catch them, and the fault that
    does is [test_one_meaning_written_under_many_names].
    """
    _term(db, "date_class", "date_class", "specific date class")
    _term(db, "datetime_object", "datetime_object", "specific datetime object")
    _term(db, "date_representation", "date_representation",
          "specific date representation")
    _term(db, "ok", "nonce",
          "a value the server stores and rejects on repeat, guarding replay")

    caught = {f.row_id for f in artefacts.restates_the_index(db)}
    assert caught == {"date_class", "datetime_object", "date_representation"}


def test_one_meaning_written_under_many_names(db):
    """
    Sixteen of icalendar's twenty-four terms were two concepts.

    This is this morning's fix showing where the pressure went. Deriving the id
    from the term made *"the same word written twice"* impossible, and the run
    duplicated meanings under different names instead: `date_class`,
    `date_instance`, `date_object`, `date_representation`, `date_type` and
    `date_value`, four of them defined in the same sentence to the character.
    Then the same six again with `datetime`.

    `duplicated` cannot see it. It groups by `term`, and the ids derive from the
    term, so distinct names are distinct rows by construction — the check
    confirms an invariant that the schema already guarantees, which is why its
    docstring says it should always be empty. Nothing was looking at the senses.

    Set equality rather than a similarity threshold: these rows do not need
    fuzziness to be caught, and a threshold is a knob that would have to be
    defended against every legitimately-related pair in a real glossary.
    """
    _term(db, "date_class", "date_class", "specific date class",
          body="a class representing a single date")
    _term(db, "date_object", "date_object", "specific date object",
          body="a class or value representing a single date")
    _term(db, "date_value", "date_value", "specific date value",
          body="a value representing a single date")
    _term(db, "date_time", "date_time", "value combining date and time information",
          body="a value that represents both a date and a time")
    _term(db, "nonce", "nonce",
          "a value the server stores and rejects on repeat, guarding replay")

    caught = {f.row_id for f in artefacts.one_sense_under_many_terms(db)}
    assert caught == {"date_class", "date_object", "date_value"}, \
        "date_time says something the other three do not, and must survive"


def test_a_term_with_no_sense_is_a_word(db):
    """
    The counterpart `a_constraint_needs_a_body` did not have. A guard rather
    than a scar — no run has produced a senseless term, because `sense_short` is
    a required argument — but required means positionally present, not filled,
    and the glossary was the one artefact where writing nothing cost nothing.
    """
    _term(db, "empty", "timezone", "")
    _term(db, "blank", "parameter", "   ")
    _term(db, "ok", "nonce",
          "a value the server stores and rejects on repeat, guarding replay")

    caught = {f.row_id for f in artefacts.a_term_needs_a_body(db)}
    assert caught == {"empty", "blank"}


def test_a_term_cannot_be_written_without_a_sense(db, tmp_path):
    """
    The audit catching it afterwards is the second line; refusing the write is
    the first. `sense_short` being a required argument only guarantees it was
    passed, and `""` passes.
    """
    from rota.core import sandbox as sandbox_mod
    from rota.onboarding import boot
    from rota.testkit import gitfixture

    repo = gitfixture.make(tmp_path)
    try:
        conn = init_db(tmp_path / "g.db")
        boot.onboard(conn, repo.root)
        sb = sandbox_mod.build("terminologist", conn, session_id="s1",
                               area="src/billing")

        with pytest.raises(ValueError, match="sense"):
            sb.call("glossary.amend", term="charge", sense_short="")

        sb.call("glossary.amend", term="charge",
                sense_short="an authorisation the gateway has already accepted")
        assert any(t == "glossary_terms" for t, _, _ in sb.ctx.writes)
    finally:
        gitfixture.cleanup(repo)


def test_a_number_living_in_the_path_is_not_invented(db, tmp_path):
    """
    The audit's own false positive: "6749 absent from
    oauth2/rfc6749/endpoints/base.py". It is the RFC number and it is right
    there in the directory name. A check that accuses has to be right.
    """
    d = tmp_path / "oauth2" / "rfc6749" / "endpoints"
    d.mkdir(parents=True)
    (d / "base.py").write_text("class BaseEndpoint: pass\n", encoding="utf-8")

    _constraint(db, "c1", "Endpoints follow RFC 6749",
                bindings=["oauth2/rfc6749/endpoints/base.py"])
    _constraint(db, "c2", "Tokens are retained 30 days",
                bindings=["oauth2/rfc6749/endpoints/base.py"])

    found = {f.row_id for f in artefacts.numbers_not_in_source(db, tmp_path)}
    assert found == {"c2"}, "the RFC number in the path was read as an invention"
