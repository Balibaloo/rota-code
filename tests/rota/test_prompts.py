"""
Prompt coverage and composition — deterministic, no model involved.

Prompts carry no authority: a piece instructing a role to do something it has no
edge for cannot succeed, because the function was never built. These cases assert
the *structure* of the prompt layer, not its wording.
"""
from __future__ import annotations

import pytest

from rota import paths
from rota.design import graph as graph_mod
from rota.roles import prompts
from rota.core.db import init_db
from rota.core.sandbox import build


# Capabilities a role has and no brief describes. Listed rather than hidden,
# because the check that was supposed to catch them searched each mode's own
# `.tools` file and therefore passed for everything.
#
# I briefed all thirteen. It cost four cases and I reverted the lot, so this is
# a measurement rather than a backlog:
#
#   AR-constrain-an-external-commitment   5/5 -> 0/5, wrote no constraint
#   DV-challenge-a-test                   5/5 -> 0/5, sent no challenge
#   DV-fix-the-code-not-the-test          5/5 -> 0/5, wrote no code
#   RS-say-what-you-tried                 3/5 -> 0/5, answered twice
#
# Every one is the same mechanism, and it is the week's most reliable finding:
# a briefed alternative inside a mode whose job is decisive becomes the exit.
# `architect/deliver` exists to write a constraint; told it may ask the
# Researcher instead, it asks. `developer/tests_failing` exists to answer one
# two-line question; given a third thing to do, it does the third thing.
#
# The usual repair is to move the capability to a mode where it does not
# compete -- which is how `developer/answer` was fixed. It does not work here:
# there is no mode whose job is asking outward. The `ask` modes are for
# answering Liaison's inquiries. So `msg.question_researcher` competes with the
# deciding action wherever it is offered, and that is a design question about
# where outward questions belong, not a wording problem. Ten of the thirteen are
# the Researcher, at both ends: five roles that may ask it and are never told,
# and the Researcher never told which channel answers. Both its edges read as
# uncovered in the matrix, which is what this looks like from the other side.
KNOWN_UNBRIEFED = {
    "architect": ("glossary.lookup", "msg.question_researcher"),
    "developer": ("msg.question_researcher",),
    "vision_keeper": ("msg.question_researcher",),
    "liaison": ("decisions.search",),
    "researcher": ("msg.answer_architect", "msg.answer_developer",
                   "msg.answer_vision_keeper", "msg.answer_terminologist",
                   "msg.answer_tester"),
    "terminologist": ("msg.question_researcher",),
    # Tester's is gone: `L1-TS-an-outside-fact-is-the-researchers` measures an
    # edge that was in the toolset and in no sentence of the brief, and five
    # runs of five asked whoever the other two clauses named. Four roles below
    # still carry the same hole and the same case has not been written for them.
}


def test_the_unbriefed_list_does_not_grow_stale():
    """
    An exemption list is only honest while every entry is still exempt. One that
    outlives its reason silences the check for a capability somebody has since
    described perfectly well.
    """
    import pathlib
    import tempfile

    conn = init_db(pathlib.Path(tempfile.mkdtemp()) / "rota.db")
    stale = {}
    for role, fns in KNOWN_UNBRIEFED.items():
        text = prompts.base(role)
        for mode in prompts.available(role):
            text += "\n" + prompts.piece(role, mode)
        described = sorted(f for f in fns if f in text)
        if described:
            stale[role] = described
    assert not stale, f"briefed now; remove from KNOWN_UNBRIEFED: {stale}"


def test_every_role_has_a_base_prompt():
    assert prompts.check_coverage() == []


def test_liaison_has_a_piece_per_inbound_verb():
    """
    Liaison's modes are enumerable from the graph, which is what makes each
    T1 case attributable to exactly one piece.
    """
    verbs = prompts.inbound_verbs("liaison")
    have = set(prompts.available("liaison"))
    missing = verbs - have
    assert not missing, f"Liaison has no piece for {sorted(missing)}"


def test_compose_includes_base_and_piece():
    composed = prompts.compose("liaison", "converse")
    assert "You are Liaison" in composed
    assert "MODE: converse" in composed


def test_liaison_converse_prompt_prioritizes_work_over_greeting():
    composed = prompts.compose("liaison", "converse")
    assert "leading greeting" in composed.lower()
    assert "work request" in composed.lower()
    assert "ignore the greeting" in composed.lower()


def test_liaison_converse_names_the_route_to_a_shipped_requests_rows():
    """The shipped line says "Ask me to show them". `converse` answers that
    ask through `ledger.list(shipped=...)` (frame 316, pass 2c)."""
    composed = prompts.compose("liaison", "converse")
    assert "ledger.list(shipped=" in composed


def test_compose_falls_back_to_base_for_unknown_mode():
    composed = prompts.compose("liaison", "not_a_verb")
    assert "You are Liaison" in composed
    assert "MODE:" not in composed


def test_prompts_never_name_a_function_the_role_lacks(tmp_path):
    """
    A prompt naming an unreachable function is a lie the model will act on.

    Checked mechanically: any `msg.x_y` or `artefact.verb` token appearing in a
    role's prompts must exist in that role's namespace.
    """
    import re

    conn = init_db(tmp_path / "rota.db")
    g = graph_mod.load()
    token = re.compile(r"\b([a-z_]+\.[a-z_]+)\b")

    problems = []
    for role in g.roles:
        available = set(build(role, conn).functions())
        text = prompts.base(role)
        for mode in prompts.available(role):
            text += "\n" + prompts.piece(role, mode)

        for match in token.findall(text):
            artefact = match.split(".")[0]
            # only check tokens that look like our namespace, not prose like "e.g."
            if artefact not in {*g.artefacts, "msg"}:
                continue
            if match not in available:
                problems.append(f"{role} prompt names {match}, not in its namespace")

    assert not problems, "\n".join(sorted(set(problems)))


def test_every_mode_has_a_piece():
    """
    A role's modes are enumerable — one per inbound verb, one per predicate that
    wakes it — which is what makes a T1 failure attributable to exactly one
    piece. A mode with no piece silently falls back to the base, and the session
    runs with instructions for a job it is not doing.
    """
    import collections

    from rota.core import predicates as P

    g = graph_mod.load()
    ticks = collections.defaultdict(set)
    for p in P.REGISTRY.values():
        if p.wakes in g.roles:
            ticks[p.wakes].add(p.name)

    missing = {
        role: sorted((prompts.inbound_verbs(role) | ticks[role])
                     - set(prompts.available(role)))
        for role in sorted(g.roles)
    }
    missing = {r: m for r, m in missing.items() if m}
    assert not missing, missing


def test_every_piece_names_its_own_mode():
    """
    The mode key *is* the filename. A header reading "MODE: intake" on
    `converse.md` is a second name for one thing, which is the drift this whole
    vocabulary pass removed everywhere else — and it is load-bearing here,
    because scripted backends match on the header.
    """
    problems = []
    for role in sorted(graph_mod.load().roles):
        for mode in prompts.available(role):
            first = prompts.piece(role, mode).splitlines()[0]
            if not first.startswith(f"MODE: {mode}"):
                problems.append(f"{role}/{mode}.md opens {first!r}")
    assert not problems, "\n".join(problems)


def test_a_mode_narrowing_cannot_widen_the_role():
    """
    The graph grants the ceiling; a mode may only narrow it. A `.tools` file
    naming something outside the role's namespace would be a prompt granting a
    capability, which is the one thing prompts must never do.
    """
    conn = init_db(__import__("tempfile").mkdtemp() + "/rota.core.db")
    problems = []
    for role in sorted(graph_mod.load().roles):
        have = set(build(role, conn).functions())
        for mode in prompts.available(role):
            for fn in prompts.mode_tools(role, mode) or []:
                if fn not in have:
                    problems.append(f"{role}/{mode}.tools names {fn}")
    assert not problems, "\n".join(problems)


def test_every_tools_file_names_only_what_the_graph_granted():
    """
    The silent half of the rule above, and the trap it leaves.

    `rota/core/sandbox.py:506-515` drops a name the graph did not grant without
    a word, so a `.tools` line for an ungranted op is a no-op that ships green.
    The test above catches it for a mode, because `available()` enumerates the
    role's `*.md` files -- and that glob cannot see the A/B variants under
    `<role>/<name>/`, whose `.tools` files replace a mode's when `ROTA_PROMPTS`
    names them. This walks the files instead of the modes.
    """
    import pathlib
    import tempfile

    conn = init_db(pathlib.Path(tempfile.mkdtemp()) / "rota.db")
    root = paths.PACKAGE / "roles" / "prompts"
    granted: dict[str, set[str]] = {}
    problems, seen = [], 0
    for tools in sorted(root.rglob("*.tools")):
        rel = tools.relative_to(root)
        role = rel.parts[0]
        have = granted.setdefault(role, set(build(role, conn).functions()))
        for line in tools.read_text(encoding="utf-8").splitlines():
            fn = line.strip()
            if not fn or fn.startswith("#"):
                continue
            seen += 1
            if fn not in have:
                problems.append(f"{rel.as_posix()} names {fn}, which the graph "
                                f"never granted {role}")
    assert seen > 100, f"the walk found almost nothing: {seen}"
    assert not problems, "\n".join(problems)


def test_a_reading_mode_can_search_before_it_reads():
    """
    Night 86, s10: the Vision Keeper on `reconcile` has six ops and one of them
    looks at code, a whole-file dump. With no way to search it guessed eight
    filenames and pulled every one at 400 lines, four times over -- 63,023
    characters of results for two sentences that cite one file.

    The `.tools` line alone would not have reached it. The graph grants the
    verb and the sandbox drops what the graph did not grant.
    """
    import pathlib
    import tempfile

    conn = init_db(pathlib.Path(tempfile.mkdtemp()) / "rota.db")
    # Three reading modes are deliberately not here, each held out by its own
    # measurement on qwen3:8b (2026-09-19):
    #
    #   terminologist/criteria    names a surface a test would call, and a new
    #                             behaviour's surface does not exist yet. With
    #                             a search it named `calculate_tip` from the
    #                             index: 0/5, L1-TE-a-new-behaviour-is-a-new-
    #                             callable.
    #   terminologist/survey      probed and never read: 0/5,
    #                             L1-TE-survey-an-area-for-its-terms.
    #   architect/survey          wrote no constraint at all: 0/5,
    #                             L1-AR-survey-an-exported-name.
    #
    # All three are pushed the source they work from -- `[code.area]`, or the
    # callables list. A mode whose prompt already carries the code does not
    # need a search, and the paragraph that offers one costs it its output.
    for role, mode in (("vision_keeper", "reconcile"), ("vision_keeper", "orient"),
                       ("vision_keeper", "reorient"), ("vision_keeper", "survey"),
                       ("critic", "challenge"), ("terminologist", "define"),
                       ("terminologist", "term_collision"),
                       ("architect", "boundary"), ("architect", "frame")):
        sb = build(role, conn, mode=mode, allow=prompts.mode_tools(role, mode))
        assert "code.probe" in sb.functions(), f"{role}/{mode} cannot search"
        assert "code.probe" in prompts.compose(role, mode), \
            f"{role}/{mode} holds the tool and never names it"


def test_the_reconcile_and_triage_briefs_name_the_ref_and_the_literal_source():
    """
    Frame 204's interviews (2026-10-12). The reconcile seat took `about_ref`
    from a directory name (VK4). The Tester invented a header name and
    triaged `encodable` (TS1). Each sentence sits before the call it governs.
    """
    # The facts, not the wording: the sentence before the call and the
    # dictated call both offer the item id and `@prose` (review 1e, L3 and L4).
    reconcile = prompts.compose("vision_keeper", "reconcile")
    call = reconcile.index("Log it:")
    sentence = reconcile[reconcile.rindex("can say which.", 0, call):call]
    template = reconcile[call:reconcile.index('kind="conflict")`', call)]
    for part in (sentence, template):
        assert "@prose" in part
    # Whole words, because "item" and "id" alone pass on "never an item id"
    # (review 1f, L4).
    # A re-wrap moves the line breaks, so the words are read joined
    # (review 1g, L2).
    sentence, template = " ".join(sentence.split()), " ".join(template.split())
    assert "that item's id" in sentence
    assert "the item id" in template
    assert '"items"' in template

    # The new Tester sentence comes before the `encodable` line, and it
    # agrees with the literal door and the triage door (review 1e, H1 and L2).
    triage = prompts.compose("tester", "tests_missing")
    verdict = triage.index("could a machine check this sentence?**")
    sentence = triage[verdict:triage.index("`encodable` and you", verdict)]
    assert "`invented`" in sentence
    # Another party's spec is the triage door's `outside_fact`, which routes
    # to the Researcher. `cannot` stays the Terminologist's.
    assert "`outside_fact`" in sentence
    assert "msg.question_researcher" in sentence
    assert "`cannot`" not in sentence
    # A re-wrap of the paragraph moves the line breaks (review 1f, L4).
    assert "is an assumption, and the encode records it" in " ".join(triage.split())


@pytest.mark.parametrize("mode", ["tests_failing", "answer"])
def test_the_developer_reason_asks_for_the_fact_not_the_fix(mode):
    """Frame 200, pass 5b: the probe's Developer looped on "name the call the
    test must use" and sent nothing. The reason is the error and the line."""
    flat = " ".join(prompts.compose("developer", mode).split())
    # Pass 5d: the probe's Tester moved only on a reason that wrote out the
    # callable that takes the argument, so the reason names it too.
    assert ('reason="<the error, the test, the line, and the call that '
            'takes the argument>"') in flat
    assert "reason=None" not in flat
    # Pass 5f: 4 of 5 reasons named `runner.invoke`, the test's own call. The
    # reason names the raising frame's function instead. Pass 5g: the error
    # carries the test, because night 144's Tester fixed the sibling test.
    assert ("`reason=` holds three facts in one sentence: the error the test "
            "got, with the test's id or its file and test name, the line of "
            "the test that raises it, and the function in the last frame of "
            "the traceback, the one that raises, as `name(...)` with the "
            "argument its error asks for.") in flat
    assert ("Do not name the call in the test, and do not write a fix, a "
            "design or a verdict on the criterion.") in flat
    assert ('For example: "the line `runner.invoke(cmd, [\'--version\'])` '
            "of `tst_version_01` "
            "fails with RuntimeError 'Try passing package_name', raised in "
            '`version_option(package_name=...)`".') in flat
    assert "the callable whose signature takes the argument" not in flat
    assert "name the call or the argument the test must use" not in flat


def test_the_tester_puts_the_argument_where_the_reason_row_says():
    """Frame 200, pass 5b: the Tester weighed the criterion over the row and
    moved `package_name` from one wrong call to another."""
    flat = " ".join(prompts.compose("tester", "challenge").split())
    assert ("When the reason row, the Developer's ref whose `table` is "
            "`decisions`, names the callable that takes an argument, the next "
            "body puts that argument on that callable, because the row "
            "outranks the traceback for where an argument goes.") in flat
    # Frame 281, ruled 2026-10-24 13:44: the row says where an argument
    # goes, never which input the test sets. Night 162's s309 read the row
    # as naming the input and passed a value found on the machine.
    assert ("A claim in the row that an argument is required is the "
            "Developer's reading. The criterion and the paragraph on inputs "
            "the criterion leaves open decide which input the test sets, and "
            "with what value.") in flat
    assert "outranks the criterion's wording" not in flat
    # Pass 5d: the traceback names `runner.invoke`, the wrong call.
    assert "on the call the traceback names" not in flat


def test_a_test_sets_every_input_the_criterion_leaves_open():
    """Frame 281, ruled 2026-10-24 13:44: a test brings its own value for
    every input the criterion leaves open. Night 162's Testers passed names
    found on the machine, and a test passed only where that name was
    installed. The paragraph sits in the base, so every Tester wake reads
    it."""
    rule = ("A test sets every input of its call that the criterion leaves "
            "open, with a value of its own, and logs the choice. A value the "
            "test finds on the machine, such as an installed package, the "
            "clock or an environment variable, is not set by the test.")
    kind = ("Where the criterion names a kind of value and not the value, "
            "the test asserts the kind, as a pattern, and not a literal the "
            "criterion does not give.")
    for mode in ("tests_missing", "challenge", "answer"):
        flat = " ".join(prompts.compose("tester", mode).split()).replace("**", "")
        assert rule in flat, mode
        assert kind in flat, mode


def test_the_open_input_rule_sits_at_the_step_that_writes_the_call():
    """Frame 281, pass 1b: the base paragraph alone moved 0 of 8 replays.
    Frame 223's interview 2 found that text at the point of decision moves
    the seat and a distant sentence does not. So each step that writes a
    call line carries the rule in the imperative."""
    challenge = " ".join(prompts.compose("tester", "challenge").split())
    assert ("When the failure names an input the call did not set, set that "
            "input with a value you choose, and log the choice. Do not take a "
            "name the error suggests, and do not take a name you find "
            "installed. The paragraph on inputs the criterion leaves open "
            "above gives the rule.") in challenge
    missing = " ".join(prompts.compose("tester", "tests_missing").split())
    assert ("Set every input of that call that the criterion leaves open with "
            "a value you choose, and log the choice. Do not take a name you "
            "find installed, as the paragraph on inputs the criterion leaves "
            "open above says.") in missing
    # Review 1, finding 3: the pointer uses the base paragraph's own words.
    assert "open inputs" not in challenge + missing


def test_the_tester_edits_the_test_the_reason_row_names():
    """Frame 200, pass 5g: on night 144 the row named a function that two
    tests call, and the Tester fixed the sibling test. The next body goes on
    the challenged test alone."""
    flat = " ".join(prompts.compose("tester", "challenge").split())
    assert ("The next body goes on the test the row names, and on no other "
            "test, even when another test calls the same function.") in flat


def test_every_operation_is_offered_by_some_mode():
    """
    A `.tools` narrowing can only remove. Today every role still has at least
    one un-narrowed mode, so nothing is stranded — but the moment the last one
    gets a `.tools` file, any operation missing from every list becomes present
    in the namespace and offered by nothing.
    """
    import pathlib
    import tempfile

    conn = init_db(pathlib.Path(tempfile.mkdtemp()) / "rota.db")
    stranded = {}
    for role in sorted(graph_mod.load().roles):
        modes = prompts.available(role)
        if any(prompts.mode_tools(role, m) is None for m in modes):
            continue                      # an un-narrowed mode offers everything
        offered = {fn for m in modes for fn in (prompts.mode_tools(role, m) or [])}
        offered |= set(SUPERSEDED.get(role, ()))
        offered |= set(WAKE_OFFERED.get(role, ()))
        missing = sorted(set(build(role, conn).functions()) - offered)
        if missing:
            stranded[role] = missing
    assert not stranded, stranded


# Reads the onboarding phases replaced and no main-tree mode offers any more.
# Listed rather than deleted, with the measurement that retired each:
#
#   code.survey       the grain list. 88% of the glossary transcribed from it
#                     (WORKLIST item 9); `code.area` hands over the source.
#   code.vocabulary   the word list. Capped recall at 4 of 10 (item 8) and
#                     added about one term over the grain list (item 9); the
#                     lexicon and `code.concordance` do its two jobs.
#
# The edges stay on the graph because the ablation variants under
# `prompts/terminologist/{grain,vocab,source}/` offer them, and those are the
# measured controls the retirement rests on. Removing the edges removes the
# ability to re-run the ablation; that is a deletion to make deliberately,
# with the variants, not a side effect of a lint.
SUPERSEDED = {
    "terminologist": ("code.survey", "code.vocabulary"),
    "architect": ("code.survey",),
}

# Operations that no `.tools` file lists, because one wake adds them. The
# wake that offers the operation names it in its own line, so no brief needs
# it. A line in the brief would change every recorded prompt of the mode.
# `criteria.retire` comes on a criterion relay whose ruling drops a line
# (frame 306, pass 1b, `runner._wake_allow`).
WAKE_OFFERED = {
    "terminologist": ("criteria.retire",),
}


def test_every_operation_is_mentioned_in_some_prompt():
    """
    Not redundant — *unbriefed*. The role has the function and is never told
    when to use it, which is the static half of the L1 question: before asking
    whether a role chooses the right action, check it was told the action exists.

    Three of the original nineteen were whole jobs nobody described: Liaison's
    `msg.ask_*` are the entire readonly-inquiry route of law 10,
    `problem.prioritize` is law 9's priority lever, and `ledger.log` appeared
    only in Developer's brief though three other roles had it.

    Then it stopped working, and read as though it never had. The text being
    searched included each mode's `.tools` file, so every offered function was
    "mentioned" -- by the list that offers it. The check could only fail for a
    function no mode offered at all, which is a different property, already
    covered, and not the one in the name.

    Thirteen capabilities were hiding behind that, and `KNOWN_UNBRIEFED` below
    is what happened when I tried to brief them.
    """
    import pathlib
    import tempfile

    from rota.core.runner import push_working_set

    g = graph_mod.load()
    conn = init_db(pathlib.Path(tempfile.mkdtemp()) / "rota.db")
    unbriefed = {}
    for role in sorted(g.roles):
        sb = build(role, conn)
        # A pushed read arrives whether or not anyone mentions it -- the opening
        # prompt carries the rows and says so -- and a brief reciting its whole
        # toolbox is a worse brief. Everything else has to be named by somebody:
        # a message channel nobody describes is a route that exists and is never
        # taken, and that is precisely what happened to the Researcher, wired at
        # both ends and briefed at neither.
        pushed = set(push_working_set(role, sb, None, g))
        text = prompts.base(role)
        for mode in prompts.available(role):
            text += "\n" + prompts.piece(role, mode)
        missing = sorted(f for f in sb.functions()
                         if f not in text and f not in pushed
                         and f not in KNOWN_UNBRIEFED.get(role, ())
                         and f not in WAKE_OFFERED.get(role, ()))
        if missing:
            unbriefed[role] = missing
    assert not unbriefed, unbriefed


def test_a_mode_names_no_function_it_does_not_offer():
    """
    Narrowing is enforcement; prose is not.

    A mode file that names `code.write` is either briefing the model to use it —
    in which case the tool list must offer it — or warning the model off it, in
    which case naming it is a mistake of a subtler kind: the narrowing already
    made the call impossible, and all the sentence achieves is putting a
    function the model cannot call into the model's head.

    Both faults were live. Developer's `tests_failing` and `verdict_failed` said
    "fix the code" with no `code.write` in reach. Vision Keeper's `signoff` and
    Liaison's `verdict` spent a paragraph each forbidding a function the tool
    list had already withheld.
    """
    import re

    # The tool's own functions: what any mode of any role offers. A dotted
    # name outside that set, `builtins.input` or `sys.stdin` in the Tester's
    # stream line, is Python the brief quotes, not a function of the tool
    # (2026-09-14: rewording `builtins.input` to "the built-in `input`" to
    # pass this test took qwen3.5:9b from 5/5 to 0/15 on the stream act).
    known = set()
    for role in graph_mod.load().roles:
        for mode in prompts.available(role):
            known.update(prompts.mode_tools(role, mode) or ())

    named_but_absent = {}
    for role in sorted(graph_mod.load().roles):
        for mode in prompts.available(role):
            offered = prompts.mode_tools(role, mode)
            if offered is None:
                continue                  # un-narrowed: the role's whole namespace
            named = set(re.findall(r"`([a-z_]+\.[a-z_]+)`", prompts.piece(role, mode)))
            missing = sorted((named & known) - set(offered))
            if missing:
                named_but_absent[f"{role}/{mode}"] = missing
    assert not named_but_absent, named_but_absent


def test_a_paragraph_that_invites_a_log_names_the_words_its_mode_offers():
    """
    Frame 204's review 1, finding H1: 15 of 16 brief lines that invite
    `ledger.log` named no word, and two dictated a call the door refuses.

    A paragraph of the composed brief that names `ledger.log` names every
    word of the mode's `.tools` line, or it dictates one `kind=` the mode
    offers. A dictated word the mode refuses is red either way.
    """
    import re

    from rota.roles.api import LOG_KINDS

    wrong = {}
    for role in sorted(graph_mod.load().roles):
        for mode in prompts.available(role):
            words = prompts.mode_kinds(role, mode)
            if not words:
                continue
            assert prompts.KINDS_SLOT not in prompts.compose(role, mode)
            for para in prompts.compose(role, mode).split("\n\n"):
                if "ledger.log" not in para:
                    continue
                dictated = re.findall(r"""kind=["']([a-z_]+)["']""", para)
                named = {w for w in LOG_KINDS if re.search(rf"\b{w}\b", para)}
                ok = (set(dictated) <= set(words)) and (
                    bool(dictated) or set(words) <= named)
                if not ok:
                    wrong.setdefault(f"{role}/{mode}", []).append(para[:80])
    assert not wrong, wrong


def test_the_criterion_repair_brief_says_where_a_surface_lives():
    """
    Frame 215, night 142: s536 took the first row of `[code.callables]`, a
    module in `examples/`, outside the batch's files. The sentence follows
    the list's own line, so the seat reads both together.
    """
    repair = prompts.compose("terminologist", "criterion_repair")
    head = repair.index("`[code.callables]` lists the candidates")
    sentence = " ".join(repair[head:head + 400].split())
    # Frame 324, pass 1b: the list ranks by the frame's kind first.
    assert ("The list shows the program's rows first, and `kind` marks each "
            "row. Inside one kind, a name the note says comes first, then "
            "fan-in. The order is not fit: the surface is a callable "
            "in a file the batch expects to touch or the request names.") in sentence


def test_a_mode_without_the_log_names_no_kind_words():
    """
    Frame 204's review 1b, finding N1: a shared base rendered the kinds
    sentence in 24 modes that do not offer `ledger.log`, with all nine words.

    The relay modes lost the call in frame 204. Their brief must not name
    the words, because the words invite the call that the door refuses.
    """
    for role in ("architect", "terminologist", "vision_keeper"):
        assert "ledger.log" not in (prompts.mode_tools(role, "relay") or ["ledger.log"])
        text = prompts.compose(role, "relay")
        assert prompts.KINDS_SLOT not in text, role
        assert "Its `kind=` is" not in text, role
        assert "`conflict`, `scope`" not in text, role


def test_every_mode_narrows():
    """
    An un-narrowed mode is the role's whole namespace, which is what the
    narrowing exists to prevent.

    Fifteen modes had no tool list, and they were the small ones — `answer`,
    `ask`, `elect`, `reopen` — the modes whose whole job is one message. Liaison
    woken to relay an answer had seventeen functions and used nine of them,
    including two messages to roles the mode has nothing to do with.

    A mode may legitimately want everything the role has. It then says so by
    listing it, because "I meant this" and "I never wrote the file" should not
    look the same.
    """
    bare = sorted(f"{role}/{mode}"
                  for role in sorted(graph_mod.load().roles)
                  for mode in prompts.available(role)
                  if prompts.mode_tools(role, mode) is None)
    assert not bare, f"{len(bare)} mode(s) with no tool list: {bare}"


def test_no_brief_offers_a_menu_of_fillable_examples():
    """
    Illustrations are pedagogy for a capable reader and a template for a small
    model with nothing else to work from.

    Architect's survey brief said what a constraint looks like: "A retention
    period. A boundary a piece of data may not cross. An interface something else
    depends on. An ordering that another system relies on." Four illustrations,
    well meant. Three of them came back as constraint headlines:

        Retention period for client tokens   x8
        Interface for client tokens          x3
        Ordering for client tokens           x3

    That is not a hallucination about OAuth. It is `<brief example>` + `<nearest
    grain name>`, and it happened because the session had nothing else -- results
    were being cut to 1200 characters, so the source never arrived and the only
    material in the prompt was the grain list and these four phrases.

    Both halves are fixed, and this pins the half that lives in the prose: a run
    of three or more short bare noun phrases reads as a list to be completed. Say
    what makes something a constraint, or give one worked example with its
    reasoning attached -- but do not hand over a form.
    """
    import re

    sentence = re.compile(r"[^.!?]+[.!?]")
    menus = {}
    for role in sorted(graph_mod.load().roles):
        for mode in prompts.available(role):
            flat = " ".join(prompts.piece(role, mode).replace("*", " ").split())
            run, longest = [], []
            for raw in sentence.findall(flat):
                s = raw.strip()
                if re.match(r"^(A|An)\s", s) and len(s) <= 70:
                    run.append(s)
                    longest = max(longest, run, key=len)
                else:
                    run = []
            if len(longest) >= 3:
                menus[f"{role}/{mode}"] = longest
    assert not menus, "\n".join(f"{k}: {v}" for k, v in menus.items())


def test_a_read_only_mode_offers_no_writes():
    """
    Three `ask` prompts told the model "you have no write functions in this
    mode; they were not built into your namespace, so there is nothing to
    resist." With no tool list that was simply untrue — Terminologist kept
    `glossary.amend` and `decisions.author` throughout.

    A prompt that claims a structural guarantee has to have one.
    """
    import pathlib
    import tempfile

    conn = init_db(pathlib.Path(tempfile.mkdtemp()) / "rota.db")
    leaks = {}
    for role in sorted(graph_mod.load().roles):
        for mode in ("ask",):
            if mode not in prompts.available(role):
                continue
            offered = set(prompts.mode_tools(role, mode) or [])
            writes = {f for f in offered
                      if f in build(role, conn).functions()
                      and not f.startswith("msg.")
                      and f.split(".")[1] not in (
                          "consult", "load", "list", "lookup", "search",
                          "scan", "probe", "quote", "read", "diff", "source",
                          "shape")}
            if writes:
                leaks[f"{role}/{mode}"] = sorted(writes)
    assert not leaks, leaks


def test_no_brief_narrates_its_own_edit_history():
    """
    A `.md` under `prompts/` is read by the role. Notes to the next maintainer
    are not.

    `developer/answer.md` carried one: "This brief used to say 'carry on' and
    name no call at all, which leaves the tool list to say what the work is --
    and the two tools that stand out in a list you were given for writing code
    are the two for asking another question." Provenance for me, addressed to
    nobody in the session -- and it spent two sentences naming the two calls the
    case forbids and describing them as the ones that stand out. The case failed
    5/5 on `forbidden call to msg.question_vision_keeper`.

    The test is deliberately narrow. Self-reference is not the fault: the
    paragraph in `developer/batch_start.md` beginning "A session that has done
    its job" says "this brief" and is load-bearing, because it is addressed to
    the reader about the reader. Past-tense *edit history* has no reader in the
    session at all, which makes it the one signal that separates the two voices
    without judgement. Reasoning about a change belongs in the commit message,
    where the next maintainer is actually looking.
    """
    import re

    history = re.compile(
        r"(?i)\b(used to (say|read|name)|previously (said|read)|"
        r"an earlier (version|draft)|this brief (used|said))\b")
    narrated = {}
    for path in sorted(paths.PROMPTS.glob("*/*.md")):
        hits = history.findall(path.read_text(encoding="utf-8"))
        if hits:
            narrated[f"{path.parent.name}/{path.name}"] = [h[0] for h in hits]
    assert not narrated, narrated


def test_a_brief_names_at_least_one_of_its_own_calls():
    """
    A brief that names no call leaves the tool list to say what the work is.

    Five separate defects came out of comparing briefs against their `.tools`
    files, and this is the shape that bit twice. `developer/answer` said "apply
    it, carry on with the batch" and mentioned none of its nine tools; the
    session picked from the list, and the two that stand out among code tools
    are the two for asking another question. `tester/answer` was two sentences
    and named none of six, so an answer arrived, was understood, and was never
    encoded -- leaving the criterion as untested as before the question.

    Not "every tool must be mentioned": most reads arrive pushed and a brief
    that recited its whole toolbox would be a worse brief. One is the floor. A
    mode whose brief cannot name a single call it exists to make is a mode whose
    work is defined by a list the model has to guess the point of.
    """
    silent = []
    for tools_path in sorted(paths.PROMPTS.glob("*/*.tools")):
        brief_path = tools_path.with_suffix(".md")
        if not brief_path.exists():
            continue
        tools = [line.strip() for line in
                 tools_path.read_text(encoding="utf-8").splitlines()
                 if line.strip() and not line.strip().startswith("#")]
        brief = brief_path.read_text(encoding="utf-8")
        if tools and not any(fn in brief for fn in tools):
            silent.append(f"{brief_path.parent.name}/{brief_path.name} "
                          f"names none of its {len(tools)} tools")
    assert not silent, "\n  " + "\n  ".join(silent)


def test_an_unresolved_rung_can_answer_every_asker_that_reaches_it():
    """
    The ladder picks a rung by the graph; the mode narrows by a hand-written
    list; nothing checked that the two agree.

    `predicates.unresolved` is careful about this and says why: it reads
    reply-capability off the graph because "waking a rung that cannot speak to
    the asker would produce a session with nothing it could do -- a silence
    indistinguishable from the answer landing". It then hands the wake to a mode
    whose `.tools` file decides what is actually built, and those files name one
    asker each: `architect/unresolved.tools` offers `msg.answer_developer` and
    nothing else, because Developer was the only asker when it was written.

    Liaison became an asker when the inquiry route started working, and the
    ladder for a Liaison question is exactly the three artefact owners. Every
    one of them would have woken unable to reply.

    Same shape as `situational`'s note about a brief that "names one instance
    and parenthesises the rest" -- and the same fix: derive it, then a list that
    falls behind the graph fails here instead of going quiet in production.
    """
    from rota.core.predicates import Wake
    from rota.core.scheduler import ONBOARDING_TICKS  # noqa: F401  (import guard)

    g = graph_mod.load()
    can_answer: dict[str, set[str]] = {}
    for e in g.of_type("messages"):
        if e.v == "answer":
            can_answer.setdefault(e.t, set()).add(e.s)

    problems = []
    for asker, rungs in sorted(can_answer.items()):
        for rung in sorted(rungs):
            tools = prompts.mode_tools(rung, "unresolved")
            if tools is None:
                continue          # un-narrowed: the role keeps everything
            if f"msg.answer_{asker}" not in tools:
                problems.append(
                    f"{rung} is a rung for {asker} and its unresolved mode "
                    f"cannot answer them")
    assert not problems, "\n".join(problems)


def test_a_mode_that_answers_liaison_can_also_say_it_cannot():
    """
    The guard that requires an answer to Liaison to name a row is only fair if
    the session has somewhere else to put "my artefact does not hold this".

    It did not. `architect/ask.tools` offered `msg.answer_liaison` and no
    report, so an owner asked about an unsurveyed area could neither answer
    with a source nor say it had none: it reached for `answer` four times, was
    refused four times, and the thread died with the principal still waiting.
    Measured on the click run, which is also where the guard was added -- the
    two together made a gate the model could not satisfy, which is exactly what
    law 4 says produces a loop.

    ONBOARDING's own description of this route has said so from the start:
    "owners answer from artefacts, drill to source when they cannot, and write
    back; **'cannot determine' becomes a report**."
    """
    problems = []
    for role in ("architect", "terminologist", "vision_keeper"):
        for mode in prompts.available(role):
            tools = prompts.mode_tools(role, mode)
            if tools is None or "msg.answer_liaison" not in tools:
                continue
            if "msg.report_liaison" not in tools:
                problems.append(f"{role}/{mode} answers liaison and cannot "
                                f"report that it has nothing")
    assert not problems, "\n".join(problems)


def test_a_mode_that_encodes_holds_the_exits_the_guard_names():
    """
    The parroting guard refuses a restated criterion and names the way out:
    question the Terminologist if the words cannot become an assertion, the
    Vision Keeper if no machine could check the promise. Live on the delivery
    rung, the Tester took the named exit at last -- and was told
    "'msg.question_terminologist' is not in this role's working set", because
    `tester/answer` held `tests.encode` without the channels its own refusal
    points to. A guard is only fair when the escape it assumes is reachable in
    the mode, and this derives it for every mode that can meet the guard.
    """
    problems = []
    for mode in prompts.available("tester"):
        tools = prompts.mode_tools("tester", mode)
        if tools is None or "tests.encode" not in tools:
            continue
        for exit_ in ("msg.question_terminologist", "msg.question_vision_keeper"):
            if exit_ not in tools:
                problems.append(f"tester/{mode} encodes and lacks {exit_}")
    assert not problems, "\n".join(problems)


def test_worked_example_ids_cannot_collide():
    """A worked example is a stronger lever than a guard's refusal --
    measured on walk six, where the Tester followed the brief's id='t1'
    into the cross-table collision three sessions straight while the
    Terminologist, taught only by the refusal, minted distinct ids the
    same walk. So every id an example mints carries its artefact's own
    unambiguous prefix, and an example that fights the binder fails here
    before any model meets it."""
    import re

    PREFIX = {"brief": "s", "criteria": "c", "tests": "tst",
              "tickets": "tk", "problem": "i", "batches": "b"}
    problems = []
    from rota import paths

    for path in sorted((paths.PACKAGE / "roles" / "prompts").rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        for artefact, verb, ident in re.findall(
                r"([a-z_]+)\.([a-z_]+)\(id='([a-z0-9_]+)'", text):
            want = PREFIX.get(artefact)
            if want and not re.match(rf"^{want}\d|^{want}_", ident):
                problems.append(
                    f"{path.parent.name}/{path.name}: {artefact}.{verb} "
                    f"example mints id={ident!r}; the unambiguous prefix "
                    f"for {artefact} is {want!r}")
    assert not problems, "; ".join(problems)
