"""
`ROLES.md` is checked, not remembered.

A document describing boundaries is worth having only while it is true, and
prose about a graph goes stale in exactly the way the graph cannot: silently,
and while still reading as authoritative. So every structural claim it makes is
asserted here against `design/graph.json`, which is the thing that actually
builds the namespaces.

What is deliberately *not* checked is the reasoning -- "Liaison never decides
anything" is a design position, not a fact about the graph, and it is the most
valuable line in the file. Tests keep the facts honest so the positions stay
readable.
"""
from __future__ import annotations

import collections
import re

from rota import paths
from rota.design import graph as graph_mod
from rota.core import predicates as P

DOC = paths.PACKAGE / "ROLES.md"


def _sections() -> dict[str, str]:
    """`## rolename` to the text under it."""
    text = DOC.read_text(encoding="utf-8")
    out, current = {}, None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            out[current] = ""
        elif current is not None:
            out[current] += line + "\n"
    return out


def test_every_role_has_a_section():
    have = set(_sections())
    missing = sorted(set(graph_mod.load().roles) - have)
    assert not missing, f"no boundary written for {missing}"


def test_no_section_describes_a_role_that_does_not_exist():
    g = graph_mod.load()
    known = set(g.roles) | {
        "the principal", "Ownership",
        "Known open boundaries"}
    strays = sorted(set(_sections()) - known)
    assert not strays, f"sections for non-roles: {strays}"


def test_the_ownership_table_matches_the_graph():
    """
    Single-writer is Law 1, and the three shared artefacts are rulings. Both
    halves have to be right: a shared artefact quietly listed as owned would
    read as a law being kept when it is being excepted.
    """
    g = graph_mod.load()
    writers = collections.defaultdict(set)
    for e in g.of_type("writes"):
        if e.s in g.roles:
            writers[e.t].add(e.s)

    doc = DOC.read_text(encoding="utf-8")
    for artefact, who in sorted(writers.items()):
        if len(who) == 1:
            owner = next(iter(who))
            assert re.search(rf"`{artefact}`\s*\|\s*{owner}", doc), \
                f"{artefact} is owned by {owner} and the table does not say so"
        else:
            assert re.search(rf"\*\*`{artefact}`\*\*", doc), \
                (f"{artefact} has {len(who)} writers and is not listed among "
                 f"the exceptions")


def test_each_role_lists_exactly_the_recipients_it_can_reach():
    """
    The line that goes wrong quietly. A role listed as reaching somebody it
    cannot is a brief waiting to be written against a channel that does not
    exist; one that reaches somebody unlisted is a route nobody knows is there,
    which is how the Researcher ended up wired at both ends and briefed at
    neither.
    """
    g = graph_mod.load()
    sections = _sections()
    problems = []
    for role in sorted(g.roles):
        can = {e.t for e in g.of_type("messages") if e.s == role}
        body = sections[role]
        claim = re.search(r"\*\*Reaches\*\*(.+?)\n\n", body, re.S)
        assert claim, f"{role} has no **Reaches** line"
        said = {r for r in (set(g.roles) | {"principal"}) if r in claim.group(1)}
        if said != can:
            problems.append(
                f"{role}: doc says {sorted(said)}, graph says {sorted(can)}")
    assert not problems, "\n".join(problems)


def test_each_role_lists_the_predicates_that_wake_it():
    g = graph_mod.load()
    sections = _sections()
    ticks = collections.defaultdict(set)
    for p in P.REGISTRY.values():
        if p.wakes in g.roles:
            ticks[p.wakes].add(p.name)

    problems = []
    for role in sorted(g.roles):
        claim = re.search(r"\*\*Woken by\*\*(.+?)\n\n", sections[role], re.S)
        assert claim, f"{role} has no **Woken by** line"
        text = claim.group(1)
        missing = sorted(t for t in ticks[role] if t not in text)
        if missing:
            problems.append(f"{role} is woken by {missing} and does not say so")
        # Researcher is the only role no predicate wakes, and that is a stated
        # property rather than an omission -- it acts when asked and never on
        # its own initiative.
        if not ticks[role] and "nothing" not in text:
            problems.append(f"{role} is woken by no predicate and does not say so")
    assert not problems, "\n".join(problems)


def test_every_predicate_is_either_spine_or_register():
    """
    `REGISTER.md` divides the frontier in two and the division has to stay true.

    Eleven predicates move the delivery spine forward; fourteen are open
    obligations -- something is outstanding and the predicate exists to keep
    offering it until it is not; one is message traffic. That second set was
    built one predicate at a time, correctly each time, and never looked at as
    a set, which is why its common properties went unenforced and its gaps
    stayed invisible. Nobody can see a hole in a collection nobody has drawn.

    So the collection is drawn here. A new predicate must be classified, and an
    unclassified one fails rather than quietly joining neither half -- the same
    reason drawing an edge creates a red coverage row.
    """
    import re

    from rota.core import predicates as P

    doc = (paths.PACKAGE / "REGISTER.md").read_text(encoding="utf-8")
    block = re.search(r"\*\*sixteen are register entries\*\*.*?\n\n(.*?)\n\n",
                      doc, re.S)
    assert block, "the register list is no longer where the check looks for it"
    named = set(block.group(1).split())

    every = set(P.REGISTRY)
    unknown = sorted(named - every)
    assert not unknown, f"REGISTER.md names predicates that do not exist: {unknown}"

    # Every predicate is register, spine, or the one traffic tip. The spine half
    # is not listed in the doc by name, so it is whatever is left -- which means
    # a new predicate lands in "spine" silently unless the count is pinned too.
    # The set lives in code now and the document is checked against it, rather
    # than the document being the only place the classification exists. That
    # ordering matters: `outstanding()` folds over `REGISTER_ENTRIES`, so a
    # doc-only list would have been a second source of truth for something the
    # runtime depends on.
    assert named == set(P.REGISTER_ENTRIES), (
        f"REGISTER.md and predicates.REGISTER_ENTRIES disagree: "
        f"{sorted(named ^ set(P.REGISTER_ENTRIES))}")
    # 37 with `criterion_repair` (register), 38 with `preempt` (spine: a
    # scheduling act, not an open obligation -- law 9's reorder performed by
    # the scheduler, drained the moment it fires), 39 with `cancel` (spine,
    # the same authority ending a batch whose approval was withdrawn), 40 with
    # `touch_note` (register: a batch's predicted touch is owed to the
    # principal until presented -- P4, 2026-09-03), 43 with `touch_strayed`
    # and `touch_mistaken` (spine: a stray in a batch's diff is the batch's
    # own fix loop, drained by the Architect's judgement and the Developer's
    # removal, and the merge gate holds until then -- 2026-09-13). The pin
    # forced each classification before the count moved.
    assert len(every) == 43, (
        f"{len(every)} predicates now, and the split in REGISTER.md was written "
        f"against 30. Classify the new one.")


def test_a_verb_carries_words_or_does_not_regardless_of_recipient():
    """
    One meaning per word, applied to the message vocabulary.

    Ten channels use `question` and five of them could not carry one. Which
    half a channel fell in depended on the recipient: to the Researcher it had
    a `question=` field, to anyone inside the project it had refs and nothing
    else. A Terminologist woken by `developer -> terminologist: question` was
    shown the term and its sense and no question, so it invented one, answered
    it, and the Developer got an answer to something it never asked.

    Law 2 is not in tension with this. Conclusions travel and reasoning stays
    home governs *telling*, and every pointing verb -- deliver, relay, reopen,
    elect, submit, verdict -- still carries refs and nothing else, which is
    where prose would let a wrong conclusion outrun the row it came from.
    Asking is not telling: a question is about something no artefact holds,
    which is what makes it a question.

    The rule asserted is only consistency. A verb that carries words on one
    channel carries them on all of its channels, so the next `question` edge
    somebody draws cannot quietly be a mute one -- and if `challenge` is ever
    given words, it gets them everywhere or the check fails.
    """
    g = graph_mod.load()
    by_verb = collections.defaultdict(set)
    for e in g.of_type("messages"):
        by_verb[e.v].add(bool(getattr(e, "prose", "")))

    split = {v: "some channels carry words and some do not"
             for v, kinds in by_verb.items() if len(kinds) > 1}
    assert not split, split


def test_no_section_names_a_function_its_role_lacks():
    """Same rule as the prompts: naming an unreachable call is a lie in prose."""
    import tempfile
    import pathlib

    from rota.core.db import init_db
    from rota.core.sandbox import build

    g = graph_mod.load()
    conn = init_db(pathlib.Path(tempfile.mkdtemp()) / "rota.db")
    token = re.compile(r"`([a-z_]+\.[a-z_]+)`")
    problems = []
    for role in sorted(g.roles):
        have = set(build(role, conn).functions())
        for fn in token.findall(_sections()[role]):
            if fn.split(".")[0] not in {*g.artefacts, "msg"}:
                continue
            if fn not in have:
                problems.append(f"{role}'s section names {fn}, not in its namespace")
    assert not problems, "\n".join(problems)


def test_the_loop_ledger_claims_only_what_the_build_can_check():
    """
    `LOOPS.md` is the third checked document, after `ROLES.md` and
    `REGISTER.md`, and it exists because "are the loops production grade?"
    had no answer the suite could defend. The grades are propositions:

      * every loop is graded, and no grade names a gate that does not exist;
      * a loop at G0 or better names machinery that is actually registered --
        spot-checked here for the newest loops, the way the ownership table
        is spot-checked against the graph;
      * the headline claim -- nothing is at G3 -- stays true until chaos
        tests exist, at which point this test must be extended rather than
        deleted, because the claim it guards will have changed.
    """
    doc = (paths.PACKAGE / "LOOPS.md").read_text(encoding="utf-8")

    import re as _re

    rows = _re.findall(r"^\| \d \| ([a-z /]+?) \| \*\*(G\d)\*\* \|", doc,
                       _re.MULTILINE)
    assert len(rows) == 6, f"six loops, graded: {rows}"
    assert all(g in {"G0", "G1", "G2", "G3", "G4"} for _, g in rows)

    # The graded machinery exists: the newest loops' named pieces.
    assert "criterion_repair" in P.REGISTRY, "loop 4's repair predicate"
    assert "preempt" in P.REGISTRY, "loop 6's reorder predicate"

    # G3 is claimable only with the loop's own chaos file on disk -- the
    # check extended exactly as its docstring demanded when loop 1 earned
    # it. G4 stays unclaimable until the gauntlet's story log exists.
    chaos_files = {"1": "test_chaos_onboarding.py",
                   "2": "test_chaos_inquiry.py",
                   "5": "test_chaos_staytrue.py"}
    here = paths.PACKAGE.parent / "tests" / "rota"
    for num, grade in _re.findall(r"^\| (\d) \| [a-z /]+? \| \*\*(G\d)\*\* \|",
                                  doc, _re.MULTILINE):
        if grade == "G3":
            named = chaos_files.get(num)
            assert named and (here / named).exists(), (
                f"loop {num} claims G3 with no chaos file registered here")
    claimed = {g for _, g in rows}
    assert "G4" not in claimed, "no loop has lived the gauntlet yet"
