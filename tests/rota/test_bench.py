"""The bench's graders must be able to fail, or they prove nothing --
each scorer is shown a passing and a failing completion and must tell
them apart. The same rule the vocabulary lint applies to itself."""
from probes.bench.run import (score_challenge, score_decline, score_define,
                              score_frame, score_orient, score_read,
                              score_recover)


def test_every_grader_can_pass_and_can_fail():
    good_bad = [
        (score_frame,
         "src/: program - the code\ndocs/: attached - documentation",
         "src/: attached - stuff\ndocs/: program - stuff",
         {"src": ["program"], "docs": ["attached"]}),
        (score_define,
         "TOOL: glossary.amend(term='text', sense_short=\"a prompt type "
         "validated by matches_regex\")",
         "TOOL: glossary.amend(term='text', sense_short=\"a string of "
         "characters\")",
         {"must_not_contain": ["string", "characters"], "is_about": ""}),
        (score_challenge,
         "TOOL: challenge.break(citation='a.ts', quote='x', why='y')",
         "TOOL: challenge.uphold(citation='a.ts', quote='x', why='y')",
         {"expected_verdict": "falsified"}),
        (score_recover,
         "TOOL: challenge.break(citation='src/intents/frontmatter.ts', "
         "quote='const fm = app.metadataCache.getFileCache(note)?.frontmatter', "
         "why='YAML, not SQLite')",
         "TOOL: challenge.break(citation='[constraints:plant1]', quote='', "
         "why='the file does not mention it')",
         {"must_differ_from": "citation='[constraints:plant1]', quote=''",
          "must_contain_any": ["frontmatter"]}),
        (score_read,
         "text, number, natural_date, note and folder, per the enum.",
         "NOT MINE",
         {"must_contain_all": ["text", "number", "natural_date", "note",
                               "folder"],
          "must_not_start": "NOT MINE"}),
        (score_decline,
         "TOOL: surveys.attest(outcome='none_found', citations=['README.md'])",
         "TOOL: glossary.amend(term='the', sense_short='a definite article')",
         {"must_contain_any": ["none_found"],
          "must_not_contain": ["glossary.amend"]}),
        (score_orient,
         "TOOL: problem.assert(id='parses', text='parses iCalendar (RFC 5545) "
         "content', kind='in_scope')",
         "It is a nice program that does things with dates.",
         {"must_contain_any": ["5545"], "must_contain_all2": ["problem.assert"]}),
    ]
    for scorer, good, bad, truth in good_bad:
        ghit, gtot = scorer(good, truth)
        bhit, btot = scorer(bad, truth)
        assert ghit == gtot > 0, f"{scorer.__name__} cannot pass its good case"
        assert bhit < btot, f"{scorer.__name__} cannot fail its bad case"


def test_a_snapshotted_brief_is_the_brief_production_sends():
    """
    Half the battery measures a model against the real composed brief and
    half against a compact hand-written probe, and both are right: the
    production frame brief asks for `frame.assign` tool calls, and parsing
    thirty-eight of those well enough to score would make the grader the
    thing under test.

    What is not right is a snapshot silently ageing. Renaming one operation
    left every `critic/challenge` fixture measuring models against a prompt
    the system no longer sends -- invisibly, because a stale prompt still
    scores. So each fixture says where its system half came from, and the
    ones that say a brief must still be that brief.
    """
    import json
    from pathlib import Path

    from rota.roles import prompts

    stale = []
    fixtures = Path(__file__).resolve().parents[2] / "probes" / "bench" / "fixtures"
    for path in sorted(fixtures.glob("*.json")):
        for fx in json.loads(path.read_text(encoding="utf-8")):
            origin = fx.get("system_from")
            assert origin, f"{fx['id']} does not say where its system came from"
            if origin == "hand":
                continue
            role, _, mode = origin.partition("/")
            spoken = role.replace("_", " ")
            want = "You are " + spoken + ".\n\n" + prompts.compose(role, mode)
            if fx["system"] != want:
                stale.append(f"{fx['id']} ({origin})")
    assert not stale, (
        "these fixtures snapshot a brief that has since changed, so the "
        "bench is scoring models on a prompt production no longer sends: "
        + ", ".join(stale))

