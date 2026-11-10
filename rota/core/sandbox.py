"""
Per-role namespaces, built from the graph.

This is where "a missing edge is an ImportError" stops being an aspiration. A
role's namespace is *constructed* from its edges: if the graph does not grant
`critic` a read of the system model, then `model` does not exist in Critic's
sandbox — not forbidden, not guarded, simply absent. There is no check to forget
and no flag to get wrong, because the capability was never created.

Consequences worth stating:

  * The only way to give a role a new capability is to draw an edge.
  * A prompt instructing a role to do something it has no edge for cannot
    succeed — the function is not there. Prompts have no authority.
  * Consult mode drops every writer from the namespace, so a read-only session
    cannot revoke anything or invalidate any checkpoint.
"""
from __future__ import annotations

import functools
import inspect
import json
import re
import sqlite3
from pathlib import PurePath
from types import SimpleNamespace
from typing import Any, Callable, NamedTuple

from .db import guess_item, table_of, tables_of
from ..roles import api
from ..design import graph as graph_mod
from .db import author_refusal, journal_author
from .db import OWED_A_REPLY

# How many open assumptions one page to the principal may carry. The
# interview is iterative by ruling (2026-09-12); the count is a fact the
# door holds, which seven is the presenting brief's judgement.
PAGE_ASSUMPTIONS = 7

# A clarify that carries this many of the principal's words in a row, in
# their order, is their sentence pasted back to them (seat1 page 4).
QUOTE_RUN = 8


def _longest_word_run(a, b):
    """The longest run of words that `a` and `b` share, in order."""
    best, best_end = 0, 0
    prev = [0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        cur = [0] * (len(b) + 1)
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                cur[j] = prev[j - 1] + 1
                if cur[j] > best:
                    best, best_end = cur[j], i
        prev = cur
    return a[best_end - best:best_end]


# What separates an id from prose is whitespace and length, not shape. The first
# version of this required `prefix_hex`, which is what `new_id` produces and not
# what fixtures use -- `s1`, `i1`, `g1` are ids and were refused, so two scripted
# delivery tests stopped ratifying. A guard that rejects the system's own ids is
# worse than the fabrication it was written to catch.
_ID = re.compile(r"\S{1,64}")


def _listed_refs(text: str) -> list[str]:
    """
    The ids in a bare `refs` string, one per item, for the refusal's form.

    The string splits on commas and whitespace. Quotes and brackets around
    a token go, and a label such as `refs:` goes (frame 327, review 1, H1).
    """
    tokens = [t.strip("'\"[]()") for t in re.split(r"[,\s]+", text)]
    return [t for t in tokens if t and not t.endswith((":", "="))]


class SandboxError(RuntimeError):
    pass


class MissingImplementation(SandboxError):
    """The graph declares an edge with no body behind it."""


class ArgumentError(SandboxError):
    """The model called a real function with arguments it cannot accept."""


# Values the schema constrains with CHECK. Validated at the sandbox boundary so a
# bad enum is a tool error the model can correct, not an IntegrityError that
# rolls back an otherwise sound session.
ENUMS: dict[str, tuple[str, ...]] = {
    "approval":   ("draft", "pending", "approved", "contested"),
    "kind":       ("in_scope", "out_of_scope"),
    "outcome":    ("found", "none_found"),
    "result":     ("pass", "fail"),
    "author":     ("principal", "liaison"),
}

# Where one argument name means different things in different operations, the
# operation has to say which. `status` is the case: a statement's status and a
# finding's status share a column name and share nothing else.
#
# The flat map above had `status` twice, and Python kept the second silently —
# the sort of collision the vocabulary pass exists to remove, hiding in the code
# that enforces vocabulary. A name-keyed map cannot express two senses, so the
# senses that need distinguishing are keyed by operation instead.
# A statement's status is not here because no operation takes it as an argument
# — `segment` and `ratify` each write one fixed value. Listing it would be a
# rule guarding a door nobody can walk through, which is how the duplicate got
# in unnoticed in the first place.
ENUMS_BY_OP: dict[tuple[str, str], dict[str, tuple[str, ...]]] = {
    # The frame's kinds are not the backlog's: a classification of the tree,
    # not an item's scope.
    ("frame", "assign"): {"kind": ("program", "attached", "attach",
                                   "ignore", "ignored", "boundary",
                                   "surface")},
    ("findings", "find"): {"status": ("satisfied", "violated")},
    # The Critic's two answers to a finding filed after its pass (frame 88).
    ("verdicts", "rule"): {"ruling": ("upheld", "dismissed")},
    ("tests", "triage"): {"verdict": ("encodable", "cannot", "ambiguous_word",
                                      "no_machine_check", "outside_fact",
                                      "contradicts_request")},
    # `chat` is gone: the principal's words always land on a row (ruled:
    # Roman, 2026-10-08, the park ask is a page with rows, point 4).
    ("brief", "intake"): {"verdict": ("work",)},
    # None: the op's own door reads the argument. `ledger.log` takes two
    # words in one `kind` and keeps the first by the tie-break, and a word
    # it refuses gets section 8's three questions (frame 204). The flat
    # `kind` above is the backlog's and would refuse every word here.
    ("ledger", "log"): {"kind": None},
}

# What a refused enum value says, where the list of values alone does not
# say where the call goes instead.
ENUM_REFUSALS: dict[tuple[str, str, str, str], str] = {
    ("brief", "intake", "verdict", "chat"): (
        "the principal's words always land on a row. Words about a row: "
        "msg.clarify_principal(refs=[<the row>], question=...). A question "
        "about the program: the asks. A request: verdict='work'"),
}

# What to say when a *particular* wrong argument is offered, where listing the
# signature demonstrably does not help.
#
# One entry, and it earned its place: `ledger.log(id=...)` was rejected 170
# times across two cases, the same call re-sent turn after turn against an error
# that already printed the correct signature. `id` means "this row's own id"
# everywhere else in the namespace, and the ledger derives its own — so the
# model is not misreading the signature, it is reading a word that means
# something different here. Naming the substitute is what breaks the loop.
ARG_HINTS_BY_OP: dict[tuple[str, str], dict[str, str]] = {
    ("ledger", "log"): {
        "id": "the ledger derives its own id from the assumption; if you mean "
              "what the assumption is about, that is about_ref",
    },
    # Frame 170. The Critic's brief teaches `quotes=` for a challenge, so a
    # seat can send it on a pass. The pass names its lines in `lines=`.
    ("verdicts", "emit"): {
        "line": "a pass names its lines in lines=, a dict of each criterion "
                "id to its added line: lines={'<criterion id>': '<the line>'}",
        "quotes": "a pass names its lines in lines=, a dict of each criterion "
                  "id to its added line: lines={'<criterion id>': '<the line>'}",
    },
}


# The arguments that the survey mode's signature leaves out. The door still
# takes them, so a recorded call keeps its answer (frame 362, pass 4c).
SURVEY_HIDDEN = {"model.amend": ("party", "behaviour", "witness")}

# The mirror for the commitments mode. Its door fills the headline, the text,
# the bindings and the source refs from the witness line, so the signature leaves them out
# and the door drops them when they come (frame 362, pass 4e: 7 of 10
# refusals of the four state cases were on these arguments).
COMMITMENTS_HIDDEN = {"model.amend": ("headline", "text", "bindings",
                                      "source_refs")}
HIDDEN_BY_MODE = {"survey": SURVEY_HIDDEN, "commitments": COMMITMENTS_HIDDEN}


def _render_signature(fn: Callable, hidden: tuple[str, ...] = ()) -> str:
    import inspect

    params = []
    # A verb can show a slot in place of its default (frame 200, pass 5b).
    shown = getattr(fn, "__shown__", None) or {}
    for name, p in inspect.signature(fn).parameters.items():
        if name in hidden:
            continue
        if name in shown:
            params.append(f"{name}={shown[name]}")
        elif p.default is inspect.Parameter.empty:
            params.append(name)
        else:
            params.append(f"{name}={p.default!r}")
    return ", ".join(params)


def _bind_positional(fn: Callable, pos: tuple, kwargs: dict,
                     dotted: str) -> dict:
    """
    Name the positional arguments, in declaration order.

    Small models write `tests.encode('t1', 'c1', 'test_close.py', '...')`
    perfectly often, and the signature is right there in the prompt they were
    given. Refusing it was a rule with nothing behind it — every rejection was
    a call whose intent was completely determined.

    Too many, or one that collides with a keyword already supplied, is still an
    error: those are genuinely ambiguous rather than merely informal.
    """
    import inspect

    names = list(inspect.signature(fn).parameters)
    if len(pos) > len(names):
        raise ArgumentError(
            f"{dotted}: {len(pos)} positional arguments for "
            f"({_render_signature(fn)})")

    named = dict(zip(names, pos))
    clash = sorted(set(named) & set(kwargs))
    if clash:
        raise ArgumentError(
            f"{dotted}: {clash} given both by position and by name")
    return {**named, **kwargs}


_SCALARS = {int: "int", bool: "bool", float: "float"}
# The value that a refusal of the scalar door offers in place of the text.
_SCALAR_EXAMPLE = {"int": 1, "float": 1.0, "bool": True}
# The words that a model writes for a truth value. JSON's spelling and
# Python's both occur, as in `toolproto._WORDS`.
_BOOL_WORDS = {"true": True, "false": False, "True": True, "False": False,
               "1": True, "0": False}


def _scalar_kind(ann) -> str | None:
    """`int`, `bool` or `float` when `ann` declares that scalar alone or with
    None, else None. A string annotation is read too, because the binder's
    signature keeps the string when `eval_str` fails."""
    if isinstance(ann, str):
        parts = [s.strip() for s in ann.split("|") if s.strip() != "None"]
        if len(parts) == 1 and parts[0] in _SCALARS.values():
            return parts[0]
        return None
    if ann in _SCALARS:
        return _SCALARS[ann]
    import types
    import typing
    if isinstance(ann, types.UnionType) or typing.get_origin(ann) is typing.Union:
        rest = [a for a in typing.get_args(ann) if a is not type(None)]
        if len(rest) == 1 and rest[0] in _SCALARS:
            return _SCALARS[rest[0]]
    return None


def _scalar_from_text(kind: str, text: str):
    """The value of `kind` that `text` spells, or None when it spells none."""
    import math
    s = text.strip()
    if kind == "bool":
        return _BOOL_WORDS.get(s)
    try:
        v = int(s) if kind == "int" else float(s)
    except ValueError:
        return None
    # `float('nan')` succeeds, and no column means a value that is no number.
    return v if kind == "int" or math.isfinite(v) else None


def _scalar_refusal(name: str, value: str, kind: str, dotted: str) -> str:
    what = "a word" if any(ch.isalpha() for ch in value) else "text"
    if kind == "bool":
        return (f"{name}={value!r} is {what} where {dotted} takes true or "
                f"false; send {name}=true or {name}=false")
    if kind == "int":
        return (f"{name}={value!r} is {what} where {dotted} takes a whole "
                f"number; send {name}=1, {name}=2 or another whole number")
    return (f"{name}={value!r} is {what} where {dotted} takes a number; "
            f"send {name}=1.0, {name}=2.5 or another number")


def _must_exist_table(op: tuple[str, str]) -> str | None:
    """The table whose row the op's `id` must name, read from the op's own
    `_must_exist(ctx, "<table>", id)` call. None when the op holds none."""
    impl = api.REGISTRY.get(op)
    if impl is None:
        return None
    try:
        src = inspect.getsource(impl)
    except (OSError, TypeError):
        return None
    m = re.search(r"""_must_exist\(ctx,\s*["'](\w+)["'],\s*id\)""", src)
    return m.group(1) if m else None


def _scalar_id_fault(ctx, op, kwargs: dict) -> tuple[str, Any] | None:
    """The id half of a call that the scalar door refuses: the words that
    name what is wrong with `id`, and the id that the offer carries.

    The id door of `_bind` and `_must_exist` run after the binder. An offer
    that keeps a wrong id is refused by the next door (frame 164's review,
    finding 1: 5 of 6 refusals on nights 113 to 126). So one refusal names
    both facts. An id of a ticket, a criterion or a batch resolves to its
    item, and the offer carries that item. Any other wrong id is the seat's
    to choose, so the offer carries `api.INVENT`, as the id door's does.
    """
    conn = getattr(ctx, "conn", None)
    rid = kwargs.get("id")
    if conn is None or not op or not isinstance(rid, str):
        return None
    own = _ID_TABLES.get(op[0])
    clash = next((t for t in _ID_TABLES.values() if t != own and conn.execute(
        f"SELECT 1 FROM {t} WHERE id = ?", (rid,)).fetchone()), None)
    must = _must_exist_table(op)
    if clash is None and (must is None or conn.execute(
            f"SELECT 1 FROM {must} WHERE id = ?", (rid,)).fetchone()):
        return None
    where = must or own
    if where is None:
        return None             # no table the id belongs to, so no fact
    item =_item_of(conn, clash, rid) if clash and where == "items" else None
    if item is not None:
        api._fact(ctx, "row", item)
        return (f". The id is wrong too: {rid!r} is a row of {clash}, not of "
                f"{where}, and its item is {item!r}. Send id={item!r} with "
                f"the number", item)
    have = [r[0] for r in conn.execute(
        f"SELECT id FROM {where} ORDER BY id LIMIT 6")]
    for h in have:
        api._fact(ctx, "row", h)
    what = f"a row of {clash}, not of {where}" if clash else f"no row of {where}"
    rows = (f"; {where} rows are {have}" if have
            else f"; there are no {where} rows at all")
    return (f". The id is wrong too: {rid!r} is {what}{rows}. Send the id of "
            f"a row of {where} with the number", api.INVENT)


def _item_of(conn, table: str, rid: str) -> str | None:
    """The items row that a tickets, batches or criteria row belongs to."""
    if table in ("tickets", "batches"):
        row = conn.execute(f"SELECT item_id FROM {table} WHERE id = ?",
                           (rid,)).fetchone()
    elif table == "criteria":
        row = conn.execute(
            "SELECT t.item_id FROM criteria c JOIN tickets t "
            "ON t.id = c.ticket_id WHERE c.id = ?", (rid,)).fetchone()
    else:
        return None
    if row is None or row[0] is None or conn.execute(
            "SELECT 1 FROM items WHERE id = ?", (row[0],)).fetchone() is None:
        return None
    return row[0]


def validate_args(fn: Callable, kwargs: dict,
                  op: tuple[str, str] | None = None, ctx=None) -> str | None:
    """Return a human-readable problem, or None if the call is well formed.

    `ctx` records the call that a refusal offers (frame 144). A caller that
    has no session passes none, and the sentence is the same."""
    import inspect

    sig = inspect.signature(fn)
    accepted = set(sig.parameters)

    unknown = sorted(set(kwargs) - accepted)
    if unknown:
        hints = ARG_HINTS_BY_OP.get(op or ("", "")) or {}
        said = "; ".join(hints[u] for u in unknown if u in hints)
        return (f"unexpected argument(s) {unknown}; "
                f"accepts ({_render_signature(fn)})"
                + (f" — {said}" if said else ""))

    # `is None` as well as absent. A native tool call can send an explicit null
    # for a required field, which passes a presence check and then dies at the
    # database — `criteria.ticket_id` NOT NULL, inside the transaction, taking
    # the session with it. A required argument that arrived null is a missing
    # argument, and it should come back as the tool error it is.
    missing = sorted(
        name for name, p in sig.parameters.items()
        if p.default is inspect.Parameter.empty
        and (name not in kwargs or kwargs[name] is None)
    )
    if missing:
        said = f"missing required argument(s) {missing}; accepts ({_render_signature(fn)})"
        # Frame 204: a missing `kind` gets the door's three questions, so
        # the seat learns the word from the refusal and not by guessing.
        if op == ("ledger", "log") and "kind" in missing:
            said += " -- " + api.ledger_kind_door(ctx)
        return said

    # A container where a scalar was declared. It passes every check above,
    # stages cleanly, and dies at the database as `type 'dict' is not
    # supported` -- inside the transaction, taking a session that was otherwise
    # sound. Three cases lost every run to this.
    #
    # The annotation is the authority: `path: str` means a string, and a model
    # that sends `{"file": "x.py"}` has made a recoverable mistake, not a fatal
    # one. Parameters annotated for lists are left alone.
    for name, p in sig.parameters.items():
        if name not in kwargs or not isinstance(kwargs[name], (dict, list)):
            continue
        ann = str(p.annotation)
        if "list" not in ann and "dict" not in ann and "Any" not in ann:
            # `question=["one question"]`: a one-element list around a scalar
            # is completely determined and unwraps; two elements is a real
            # ambiguity and stays a refusal.
            if isinstance(kwargs[name], list) and len(kwargs[name]) == 1:
                kwargs[name] = kwargs[name][0]
                continue
            kind = type(kwargs[name]).__name__
            return (f"{name} was given a {kind}; it takes a single value "
                    f"({_render_signature(fn)})")

    # Text where a number or a truth value is declared. SQLite's affinity
    # keeps a word in an INTEGER column as text, and the scheduler's sort
    # then crashes every step (frame 164: night 126, s249 sent
    # priority='high'). Text that the type reads is converted here. Any
    # other text is a refusal that names the form the argument takes.
    dotted = f"{op[0]}.{_verb_to_attr(op[1])}" if op else fn.__name__
    # Every scalar word is read before the door offers. The offer fixed the
    # first word only, and the same door refused the next one on resend (the
    # second look at passes 4c to 4e, low D: `code.source(start='top',
    # end='bottom')`).
    said, offer = "", None
    for name, p in sig.parameters.items():
        kind = _scalar_kind(p.annotation)
        if kind is None or not isinstance(kwargs.get(name), str):
            continue
        got = _scalar_from_text(kind, kwargs[name])
        if got is not None:
            kwargs[name] = got
            if offer is not None:
                offer[name] = got
            continue
        said += ("; " if said else "") + _scalar_refusal(
            name, kwargs[name], kind, dotted)
        offer = {**(offer if offer is not None else kwargs),
                 name: _SCALAR_EXAMPLE[kind]}
    if offer is not None:
        wrong = _scalar_id_fault(ctx, op, kwargs)
        if wrong:
            said += wrong[0]
            offer["id"] = wrong[1]
        # `_scalar_id_fault` judges the id. The other ids that the op's
        # `_must_exist` reads, and the enum words, go through the shared
        # offer check (frame 211).
        checks = ((api._exist_check(ctx, op, skip=("id",)),) if op else ()) + (
            lambda a: (lambda e: None if e is None else (f"; {e}", None))(
                _enum_problem(op, a)),)
        return api._offer_checked(ctx, said, dotted, offer, checks)

    return _enum_problem(op, kwargs)


def _enum_problem(op, kwargs: dict) -> str | None:
    """The refusal of the first argument whose word is not one of its enum,
    or None."""
    checks = {**ENUMS, **(ENUMS_BY_OP.get(op or ("", "")) or {})}
    for key, allowed in checks.items():
        if allowed is None:
            continue
        if key in kwargs and isinstance(kwargs[key], str) and kwargs[key] not in allowed:
            said = ENUM_REFUSALS.get((*(op or ("", "")), key, kwargs[key]))
            return said or f"{key}={kwargs[key]!r} is not one of {list(allowed)}"
    return None


class NotInWorkingSet(AttributeError):
    """
    Raised when a role reaches for something outside its edges.

    Subclasses AttributeError so it reads like an ordinary namespace miss to the
    model, and can be reported back as a tool error rather than a crash.
    """


class _Artefact(SimpleNamespace):
    def __init__(self, name: str, fns: dict[str, Callable], available: list[str]):
        super().__init__(**fns)
        object.__setattr__(self, "_name", name)
        object.__setattr__(self, "_available", available)

    def __getattr__(self, item: str):
        raise NotInWorkingSet(
            f"{self._name}.{item} is not in this role's working set; "
            f"available: {sorted(self._available)}"
        )

    def __repr__(self) -> str:
        return f"<artefact {self._name}: {', '.join(sorted(self._available))}>"


class Sandbox:
    """
    One role's entire world.

    `functions()` is what the prompt advertises and what the TOOL: parser
    dispatches against — the two cannot drift, because both read this.
    """

    def __init__(self, role: str, ctx: api.Ctx, artefacts: dict[str, _Artefact],
                 order: list[str] | None = None):
        self.role = role
        self.ctx = ctx
        self._artefacts = artefacts
        # The mode's own order for its functions, when it has one. The list
        # was alphabetical, which put `msg.converse_principal` above
        # `rulings.rule` in `landing`, and both 8B models took the first
        # function whose arguments matched the inbound fields (2026-09-10).
        # A mode's `.tools` file names its functions in the order of its job.
        self._order = list(order or [])

    def __getattr__(self, item: str):
        raise NotInWorkingSet(
            f"{item!r} is not in {self.role}'s working set; "
            f"available: {sorted(self._artefacts)}"
        )

    def __getitem__(self, name: str) -> _Artefact:
        try:
            return self._artefacts[name]
        except KeyError as exc:
            raise NotInWorkingSet(
                f"{name!r} is not in {self.role}'s working set; "
                f"available: {sorted(self._artefacts)}"
            ) from exc

    def functions(self) -> list[str]:
        names = sorted(
            f"{name}.{fn}"
            for name, art in self._artefacts.items()
            for fn in art._available
        )
        if self._order:
            rank = {n: i for i, n in enumerate(self._order)}
            names.sort(key=lambda n: (rank.get(n, len(rank)), n))
        return names

    def signatures(self) -> list[str]:
        """
        Advertised call signatures, derived from the implementations.

        Names alone are not enough. A cold 8B model given `TOOL: problem.assert(...)`
        will confidently call it with only an id, and the resulting TypeError is
        the harness's fault, not the model's. Signatures come from the same
        functions the sandbox dispatches to, so the advertisement cannot drift
        from what is actually callable.
        """
        out = []
        # The survey asks for surfaces, and the commitments mode states the
        # witness lines. The cold load filled `party`, `behaviour` and
        # `witness` on survey calls, and the three changed the survey's system
        # text from the green one (the review of pass 4b, points 4 and 5).
        hide = (HIDDEN_BY_MODE.get(api._wake_mode_key(self.ctx), {})
                if self.ctx is not None else {})
        for name in self.functions():
            artefact, fn = name.split(".", 1)
            impl = getattr(self[artefact], fn)
            out.append(f"{name}({_render_signature(impl, hide.get(name, ()))})")
        return out

    def begin_reply(self) -> None:
        """Start the next reply of the seat.

        The seat has read every result of the reply before, so a `dropped`
        note of that reply no longer stops a commit (frame 140).
        """
        notes = getattr(self.ctx, "reply_notes", None)
        if notes is not None:
            notes.clear()

    def call(self, dotted: str, *pos, **kwargs) -> Any:
        """
        Dispatch `artefact.verb(*pos, **kwargs)`, validating arguments first.

        Validation happens here rather than at the database, because an invalid
        value that reaches SQLite raises inside the transaction and takes the
        whole session down — one bad enum from the model and an otherwise good
        session never happened. Caught here it is an ordinary tool error the
        model can see and correct on its next turn.

        Positional arguments are bound here for the same reason the parser does
        not reject them: this is the only place that knows the signature.
        """
        if "." not in dotted:
            raise NotInWorkingSet(f"{dotted!r} is not a function name")
        # The offers and the facts are the current call's: a refusal names
        # its own calls and quotes its own facts. Cleared before any check,
        # so a call that fails the argument check keeps none of the last
        # call's (frame 144's review of c888968, point 9).
        offers = getattr(self.ctx, "offers", None)
        if offers is not None:
            del offers[:]
        facts = getattr(self.ctx, "facts", None)
        if facts is not None:
            del facts[:]
        artefact, fn = dotted.split(".", 1)
        target = getattr(self[artefact], fn)

        if pos:
            kwargs = _bind_positional(target, pos, kwargs, dotted)
        # The commitments mode asks for the witness, the party and the
        # behaviour only. The door writes the headline from the witness line,
        # and the signature of the other modes stays as recorded (frame 362,
        # pass 4b).
        dropped: list[str] = []
        if dotted == "model.amend" and api._wake_mode_key(self.ctx) == "commitments":
            dropped = [a for a in COMMITMENTS_HIDDEN[dotted] if a in kwargs]
            kwargs = {**{a: v for a, v in kwargs.items() if a not in dropped},
                      "headline": ""}

        problem = validate_args(target, kwargs, op=(artefact, _attr_to_verb(fn)),
                                ctx=self.ctx)
        if problem:
            try:
                raise ArgumentError(f"{dotted}: {problem}")
            except ArgumentError as exc:
                # The argument check runs before the respecify wrapper, so
                # the answer door quotes this refusal too (frame 308,
                # review 2, F2).
                if dotted == "criteria.respecify":
                    _note_respecify_refusal(self.ctx, kwargs.get("id"), str(exc))
                # The scalar door offers a call, so the follow check of
                # frame 144 reads this refusal too. Raised first, so the
                # exception carries the binder's line as its door.
                if _ON_REFUSAL is not None and (offers or facts):
                    _ON_REFUSAL(self, dotted, dict(kwargs), exc,
                                list(offers or ()), list(facts or ()))
                raise

        try:
            out = target(**kwargs)
            if dropped and isinstance(out, dict):
                said = (f"dropped {', '.join(dropped)}: the commitments mode "
                        f"fills them from the witness line")
                out = {**out, "note": f"{out['note']} {said}" if out.get("note")
                       else said}
            return out
        except ValueError as exc:
            # The follow check of frame 144. The hook is None in a session,
            # so a seat meets the same refusal as before.
            if _ON_REFUSAL is not None and (offers or facts):
                _ON_REFUSAL(self, dotted, dict(kwargs), exc, list(offers or ()),
                            list(facts or ()))
            raise

    def call_key(self, dotted: str, pos=(), kwargs=None) -> str:
        """
        A canonical name for "this call, asked again".

        The repeat detector compared raw argument lists, so `brief.list()` and
        `brief.list(since_version=0)` were two different calls -- though zero is
        the default and the rows are identical. That mattered far more than it
        looks, because the pushed working set is run with *no arguments at all*:
        the prompt tells every session "already run for you ... calling any of
        these again returns the same thing and costs you a turn", and any
        session that spelled a default out loud was charged full freight for
        rows it had already been given, and had its real action held behind a
        read it already held.

        Spelling out a default is the normal thing for a small model to do. So
        the sentence in the prompt was false for the commonest way of being
        wrong about it.
        """
        kwargs = dict(kwargs or {})
        try:
            artefact, fn = dotted.split(".", 1)
            target = getattr(self[artefact], fn)
            if pos:
                kwargs = _bind_positional(target, pos, kwargs, dotted)
                pos = ()
            params = inspect.signature(target).parameters
            kwargs = {
                k: v for k, v in kwargs.items()
                if not (k in params
                        and params[k].default is not inspect.Parameter.empty
                        and v == params[k].default)
            }
        except Exception:
            # An unresolvable name or an unbindable argument list is the
            # parser's problem, not this function's. Fall through to a key made
            # of what was actually said: it still matches an identical repeat.
            pass
        return f"{dotted}({sorted(kwargs.items(), key=repr)}{tuple(pos)})"


def _verb_to_attr(verb: str) -> str:
    """`set approval` -> `set_approval`. Graph verbs are prose; Python is not."""
    return verb.replace(" ", "_").replace("-", "_")


def _attr_to_verb(attr: str) -> str:
    """Back the other way, so per-operation rules can be keyed by graph verb."""
    return attr.replace("_", " ")


def situational(conn: sqlite3.Connection, role: str, mode: str, wake,
                available: dict[str, list[str]]) -> set[str]:
    """
    Narrow the namespace by the situation, not only by the mode.

    The mode says what a role may do when woken *for this reason*. It cannot say
    which of two permitted channels this particular wake calls for, because the
    mode is the same every time and the wake is not — so a session ends up
    holding both and only prose distinguishing them. Prose has not
    distinguished anything here in six measured attempts.

    The scheduler has always reasoned this way. `rests_on_a_collision` refuses
    to *offer* Tester a batch whose criteria turn on a word with two live
    senses, because a test written from the wrong sense passes and pins the
    wrong promise. That reasoning stopped at the session boundary, and this is
    it continuing past.

    Returns the dotted names to keep. Rules go here rather than in a prompt
    because absence is the only instruction that has ever held.
    """
    keep = {f"{a}.{fn}" for a, fns in available.items() for fn in fns}

    # You answer the role that asked, and nobody else.
    #
    # Measured on `unresolved`, and stated here for every wake that carries a
    # message because the reasoning was never about that tick. Vision Keeper can
    # reach Developer and Tester, so both channels sat in the mode, and woken to
    # a thread between Tester and Terminologist it answered Developer five runs
    # out of five. Developer is not in the thread. The asker is on the wake --
    # it is the sender of the message the wake refers to -- so the other channel
    # is not a temptation to resist, it is a capability with no situation.
    #
    # Terminologist is why it generalised: three roles can ask it what a word
    # means, and its brief said "`msg.answer_developer` (or the asking role)",
    # which names one instance and parenthesises the rest. Derived, there is
    # nothing left to get right.
    #
    # A wake with no message behind it narrows nothing. Deriving from nothing
    # would strip a role's whole reply surface and read as a role choosing
    # silence, which is worse than the failure this prevents.
    source = getattr(wake, "message_id", None)
    if source is None and getattr(wake, "refs", None):
        source = wake.refs[0]
    if source is not None:
        row = conn.execute(
            "SELECT from_role, verb, body_refs FROM messages WHERE id = ?",
            (source,)).fetchone()
        if row is not None:
            asker = row["from_role"]
            # A principal's ruling on a criterion reaches the Terminologist as
            # the Liaison's relay. Nobody asked, and the Tester encodes the
            # ruled words next, so the answer goes to the Tester. The asker
            # rule left the repair no answer at all (observed: the case
            # L1-TE-a-ruled-criterion-is-respecified-and-the-tester-told, 0/5,
            # 2026-10-09; frame 142's design, 2.A, step 7).
            reader = asker
            from .scheduler import park_criterion_relay

            if role == "terminologist" and park_criterion_relay(conn, source):
                reader = "tester"
            keep -= {k for k in keep
                     if k.startswith("msg.answer_") and k != f"msg.answer_{reader}"}
            # Frame 107. The Critic's verdict landed before its question to
            # the Terminologist. The Developer can commit a new head before
            # the answer arrives. Then a verdict from this wake judges a diff
            # nobody reviewed, so the wake holds no verdicts (ruled: Roman,
            # 2026-10-01: the Critic's doubt about a criterion goes to the
            # Terminologist, the writer of the criteria).
            if role == "critic" and asker == "terminologist":
                keep -= {k for k in keep if k.startswith("verdicts.")}

    return keep


def build(role: str, conn: sqlite3.Connection, *, mode: str = "normal",
          batch_id: str | None = None, session_id: str = "",
          area: str | None = None,
          entry_id: str | None = None,
          onboarding: bool = False,
          allow: list[str] | None = None,
          wake: object | None = None,
          g: graph_mod.Graph | None = None) -> Sandbox:
    """
    Construct `role`'s namespace from its graph edges.

    Reads become read functions, writes become write functions. In readonly mode
    the writes are simply not built — the session physically cannot write, which
    is a stronger guarantee than refusing at commit time.
    """
    g = g or graph_mod.load()
    if role not in g.roles:
        raise SandboxError(f"{role!r} is not a role in the graph")

    ctx = api.Ctx(conn=conn, role=role, mode=mode, session_id=session_id,
                  batch_id=batch_id, area=area, entry_id=entry_id,
                  onboarding=onboarding,
                  wake_refs=tuple(getattr(wake, "refs", ()) or ()),
                  wake_kind=getattr(wake, "kind", "") or "")

    grouped: dict[str, dict[str, Callable]] = {}
    available: dict[str, list[str]] = {}

    for edge in g.edges:
        if edge.s != role or edge.type not in ("reads", "writes"):
            continue
        if mode == "readonly" and edge.type == "writes":
            continue                      # read-only inquiry is free, and cannot cost
        if not edge.model_callable:
            continue                      # owned by the role, performed by the system

        impl = api.REGISTRY.get((edge.t, edge.v))
        if impl is None:
            raise MissingImplementation(
                f"graph declares {role} {edge.type} {edge.t} ({edge.v}) "
                f"but no implementation is registered for ({edge.t!r}, {edge.v!r})"
            )

        attr = _verb_to_attr(edge.v)
        grouped.setdefault(edge.t, {})[attr] = _bind(impl, ctx, f"{edge.t}.{attr}")
        available.setdefault(edge.t, []).append(attr)

    if role == "terminologist" and "respecify" in grouped.get("criteria", {}):
        grouped["criteria"]["respecify"] = _respecify_record(
            ctx, grouped["criteria"]["respecify"])

    # The bus. One `send` per declared (recipient, verb) pair — a role literally
    # cannot address anyone the graph does not connect it to, so T0-S12's
    # rejection happens by absence rather than by a check at the wire.
    outgoing = [(e.t, e.v, e.prose, e.reason_row)
                for e in g.of_type("messages") if e.s == role]
    if outgoing:
        fns: dict[str, Callable] = {}
        names: list[str] = []
        for recipient, verb, prose, reason_row in sorted(set(outgoing)):
            attr = f"{_verb_to_attr(verb)}_{recipient}"
            fns[attr] = _bind_send(ctx, recipient, verb, f"msg.{attr}", prose,
                                   reason_row)
            if role == "terminologist" and recipient == "tester" and verb == "answer":
                fns[attr] = _ruling_answer_door(ctx, f"msg.{attr}", fns[attr])
            names.append(attr)
        grouped["msg"] = fns
        available["msg"] = names

    if allow is not None:
        # A narrowing, never a widening: anything named that the graph did not
        # grant is simply absent, so a bad mode file cannot invent a capability.
        keep = set(allow)
        grouped = {
            artefact: {fn: impl for fn, impl in fns.items()
                       if f"{artefact}.{fn}" in keep}
            for artefact, fns in grouped.items()
        }
        grouped = {a: f for a, f in grouped.items() if f}
        available = {a: sorted(f) for a, f in grouped.items()}

    if wake is not None:
        keep = situational(conn, role, mode, wake, available)
        grouped = {
            artefact: {fn: impl for fn, impl in fns.items()
                       if f"{artefact}.{fn}" in keep}
            for artefact, fns in grouped.items()
        }
        grouped = {a: f for a, f in grouped.items() if f}
        available = {a: sorted(f) for a, f in grouped.items()}

    artefacts = {
        name: _Artefact(name, fns, available[name]) for name, fns in grouped.items()
    }
    # The mandatory fork arms with the mode, not with usage: a mode that
    # offers `tests.triage` requires the branch claim before any encode --
    # otherwise an encode with no triage at all would sail past a gate that
    # only exists once somebody knocks.
    if "triage" in (grouped.get("tests") or {}):
        ctx.triaged = {}
    # And the intake fork the same way: a converse mode that offers the
    # claim requires it before a reply to the principal.
    if "intake" in (grouped.get("brief") or {}):
        ctx.intake = None
    # A survey stamps the tree it read, not the tree at attest time. The
    # hash is captured here, when the session is built for its area -- a
    # concurrent refresh mid-session must not let the record claim currency
    # for content nobody surveyed.
    if area:
        from ..roles.api import area_content_hash

        ctx.area_hash_at_wake = area_content_hash(conn, area)
    # A door that names a next call reads the session's working set here.
    # The review of 4968ea7 (2026-10-05): a refusal told a Developer in mode
    # `exhausted` to change the code, and `code.write` is not in that mode.
    ctx.working_set = frozenset(f"{a}.{fn}" for a, fns in grouped.items()
                                for fn in fns)
    return Sandbox(role, ctx, artefacts)


def _names_no_source(conn, refs) -> bool:
    """
    Whether these refs cite nothing an answer could have come *from*.

    Three kinds of ref are echoes rather than sources. A **message** is the
    conversation, and the recipient was already in it. An **entry** is the
    principal's own words -- on the inquiry route it is the question itself. And
    **constraint zero** is the row bound to everything no survey has reached, so
    citing it is a role saying it has not looked, which is a fact about the run.

    Anything else is a row somebody owns, wrote, and can be held to.
    """
    from ..onboarding.boot import ZERO

    for ref in refs or ():
        if not isinstance(ref, str) or ref == ZERO:
            continue
        # `db.tables_of` finds the row. A `reading:` ref names a reply, so it
        # is the conversation too (F22).
        if tables_of(conn, ref, among=("messages", "entries")):
            continue
        return False
    return True


def _relaying_a_non_answer(ctx: api.Ctx) -> bool:
    """
    Whether the answer this session was woken by cited nothing of substance.

    False when the wake was not an answer at all, or there is nothing to read:
    both are "no reason to refuse a relay" rather than a finding about it.
    """
    import json

    row = ctx.conn.execute(
        "SELECT verb, body_refs FROM messages WHERE id = ?",
        (ctx.trigger,)).fetchone()
    if row is None or row["verb"] != "answer":
        return False
    try:
        refs = json.loads(row["body_refs"] or "[]")
    except (TypeError, ValueError):
        return False
    return _names_no_source(ctx.conn, refs)


# The split key of a relay that carries criteria ruled as lines of a page.
# It keeps them apart from the Terminologist's other relay, and the suffix
# never reaches a message.
CRITERIA_RELAY = ":criteria"
# The same for the batch lines of a touch note. A relay of batches alone
# keys `annotate`, and a constraint beside it keeps `relay`, because
# `annotate` holds no `model.adopt` (frame 190's design, 2.2).
BATCH_RELAY = ":batches"
# A code line of a request goes to the Architect's `guess` mode, apart from
# a batch, because the guess is a set of its own (frame 298's design, 3.4).
GUESS_RELAY = ":guesses"


# The tables a principal's ruling can name, each with its one writer. The
# single-writer law is what makes the relay's destination a lookup rather than
# a judgement, and `test_the_relay_split_matches_the_graph` keeps this map from
# falling behind the graph the way four hand-written lists did on the inquiry
# route.
#
# A `refs` row is never a ruling's subject. The ruling names the source row,
# and the owner of a refs row is the owner of its `src_table`, which this map
# already resolves.
RULED_TABLES = {
    "statements": "vision_keeper",
    "items": "vision_keeper",
    "glossary_terms": "terminologist",
    "constraints": "architect",
    "model_areas": "architect",
}


def _owner_of_ref(conn, ref: str) -> str | None:
    """The role that writes the table holding `ref`, or None if no table does."""
    # A code line's key names the Architect's guess (frame 298's design, 3.4).
    # The key must name an item that exists (F22 review, finding 6).
    if guess_item(ref) is not None:
        return "architect" if table_of(conn, ref) else None
    # `db.table_of` finds the row, and this map names its writer (F22). The
    # scope's order picks one owner when an id lives in two tables, as the
    # order of the map did before F22.
    table = table_of(conn, ref, among=(*RULED_TABLES, "batches", "ledger"))
    if table in RULED_TABLES:
        return RULED_TABLES[table]
    # A batch line is the Architect's prediction of what the change touches.
    # The relay split looks a ref up by table, and a batch is no ruled table,
    # so the rule stands here (frame 190's design, 2.2).
    if table == "batches":
        return "architect"
    # A ledger row is a journal entry -- one author per entry (law 1) -- and
    # the author is who acts on a ruling about it: an overruled assumption
    # goes back to the desk that assumed it.
    if table == "ledger":
        return journal_author(conn, "ledger", ref)
    return None


# The rows a challenge can quote, and the column that holds their words.
# Frame 333, item 2: the Architect's brief asks for "the exact span of each"
# statement, so a statement is a row the door checks.
_QUOTABLE = (("criteria", "text"), ("tests", "body"), ("items", "text"),
             ("tickets", "text"), ("glossary_terms", "sense_short"),
             ("constraints", "text"), ("statements", "text"))


def _code_only(source: str) -> str:
    """A test body without its comments: the lines a quote of the test
    can stand on. A `#` comment is dropped from the hash on; docstrings
    stay, a quote of one is at least a quote of the file."""
    out = []
    for line in (source or "").splitlines():
        stripped = line.split("#", 1)[0] if "#" in line and not line.lstrip().startswith(("'", '"')) else line
        if stripped.strip():
            out.append(stripped)
    return chr(10).join(out)


#: Two words that frame a value inside a render, so that each view can be
#: cut back out. Letters pass JSON and a table cell unchanged.
_VIEW_OPEN, _VIEW_SHUT = "QvwOpenQ", "QvwShutQ"
#: A render limit that cuts no view.
_NO_CUT = 1 << 62


@functools.lru_cache(maxsize=512)
def _rendered_views(source: str) -> tuple[str, ...]:
    """Each view of a row that `runner._render` shows a seat.

    F19: the views come from the render, so a new form of a result is a
    new view here with no second list. A result shows a value as itself,
    as a field of a block or of JSON, inside a JSON list, or as a cell of
    a table.
    """
    from .runner import _render
    v = f"{_VIEW_OPEN}{source}{_VIEW_SHUT}"
    views: list[str] = []
    for shape in (v, {"text": v}, {"rows": [v]}, [{"text": v}, {"text": v}]):
        text = _render(shape, _NO_CUT)
        start = text.find(_VIEW_OPEN) + len(_VIEW_OPEN)
        end = text.find(_VIEW_SHUT, start)
        if start >= len(_VIEW_OPEN) and end >= 0:
            view = text[start:end]
            if view not in views:
                views.append(view)
    return tuple(views)


@functools.lru_cache(maxsize=512)
def _shown_views(source: str) -> tuple[str, ...]:
    """Each view of a row that a seat was shown, and the values that the
    call stores when the seat copies a view into it.

    Frame 328, item 2: one reader of the views replaces one decoder per
    night. F19: `runner._render` gives each view, and `api._call_values`
    gives what each parse path stores from it.
    """
    views: list[str] = []
    for v in _rendered_views(source):
        for f in (v, *api._call_values(v)):
            if isinstance(f, str) and f.strip() and f not in views:
                views.append(f)
    return tuple(views)


def _quote_forms(quote: str) -> tuple[list[str], list[str]]:
    """The quote's forms at the escape level of the seat's text, and the
    values that the call stores from that text.

    F19: `api._call_values` gives each stored value, so the door keeps no
    rule of the call syntax of its own. Night 168 W2 sent `\\\\` for one
    backslash, and night 167 sent `\\'` and `\\x1b`. `_outer_marks` gives
    the forms with an outer quote mark dropped. Each form is still a
    verbatim reading of the seat's text.

    The decoded form is the strict value only. The review of F19 pass 1,
    finding 6: the lenient path stores `\\\\n` as a backslash and a line
    break, a value that no seat meant."""
    quote = quote or ""
    stored = [quote, *_outer_marks(quote)]
    decoded: list[str] = []
    for value in api._call_values(quote)[:1]:
        for f in (value, *_outer_marks(value)):
            if isinstance(f, str) and f not in stored and f not in decoded:
                decoded.append(f)
    return stored, decoded


def _quote_pairs(quote: str, source: str) -> list[tuple[str, tuple[str, ...]]]:
    """Each form of the quote with the views of the source that it meets.

    A value that the call stores meets the rendered views only. The review
    of frame 328 pass 3, finding 1: read through the call on both sides,
    a quote of `\\033` met a row that holds `\\x1b`, and neither is a span
    of the other."""
    stored, decoded = _quote_forms(quote)
    every, rendered = _shown_views(source), _rendered_views(source)
    return [(f, every) for f in stored] + [(f, rendered) for f in decoded]


def _quote_reads(quote: str, source: str, table: str = "",
                 floor: int | None = None, run: str = "",
                 holds: bool = False) -> bool:
    """The quote is a `_span_of` one view of the source that the seat was
    shown (ruled: Roman, 2026-08-26, a contiguous span of the disputed
    row, verbatim, on all five channels).

    Frame 333, pass 1b: this one function decides on every channel. A
    test row is its code, because a comment pays no reading (click night
    58). `run` is the latest run of the test, which the seat was shown as
    a view of the test, so a quote of its `E` line reads that test.

    With `holds`, one view of the whole source is a span of the quote
    instead. The red line door asks that the quote hold the failing line
    (frame 333, item 3). F18: the door reads the same forms, views and
    compare, so it keeps no compare of its own."""
    floor = QUOTE_MIN if floor is None else floor
    if table == "tests":
        quote, source = _code_only(quote), _code_only(source)
    sources = [source or ""] + ([run] if run else [])
    for s in sources:
        for f, views in _quote_pairs(quote, s):
            if holds:
                if any(_span_of(v, f, 0) for v in views):
                    return True
                continue
            # A line break that the call decoded from the seat's `\n` must
            # meet a line break (frame 328, review 1, finding 4).
            lined = f.count("\n") > quote.count("\n")
            if any(_span_of(f, v, floor, lined) for v in views):
                return True
    return False


def _run_view(ctx: api.Ctx, test_id: str) -> str:
    """The lines that the latest run of the test names: its `>` lines and
    its `E` lines, without the mark. Empty when the test has no run."""
    # The test's own batch only: an inherited test keeps its id across
    # batches (frame 210, fact F4).
    run = ctx.conn.execute(
        "SELECT output FROM latest_runs WHERE test_id = ? "
        "AND batch_id = (SELECT batch_id FROM tests WHERE id = latest_runs.test_id)",
        (test_id,)).fetchone()
    lines = ((run["output"] or "") if run else "").splitlines()
    return chr(10).join(ln[1:].strip() for ln in lines
                        if ln.startswith(">") or re.match(r"E\s", ln))


def _reads_row(ctx: api.Ctx, quote: str, rid: str, rows: dict,
               floor: int | None = None) -> bool:
    """`_quote_reads` on the row `rid` of rows, with its run when the row
    is a test."""
    table, words = rows[rid]
    return _quote_reads(quote, words, table, floor,
                        _run_view(ctx, rid) if table == "tests" else "")


def _quoted_rows(ctx: api.Ctx, refs) -> dict[str, tuple[str, str]]:
    """The quotable rows that refs name, as {id: (table, words)}."""
    rows: dict[str, tuple[str, str]] = {}
    for r in refs or []:
        if not isinstance(r, str):
            continue
        # `db.table_of` finds the row, and `_QUOTABLE` names its words (F22).
        table = table_of(ctx.conn, r, among=tuple(dict(_QUOTABLE)))
        hit = table and ctx.conn.execute(
            f"SELECT {dict(_QUOTABLE)[table]} AS words FROM {table} "
            f"WHERE id = ?", (r,)).fetchone()
        # A `guess:` ref names its item, and its own id holds no row.
        if hit:
            rows[r] = (table, hit["words"] or "")
    return rows


def _rows_quote_refusal(ctx: api.Ctx, rows: dict, quotes: list) -> str | None:
    """The refusal of quotes that are not each a span of one row of rows,
    or of a row with no quote, or None.

    Frame 333, item 1: the window of 2026-08-27 passed any 12 characters
    of a row in the joined text, so prose around a span went through."""
    def _shown(q: str) -> str:
        return q if len(q) <= 80 else q[:77] + "..."

    tail = (" Quote, not paraphrase: send quotes= as a list of strings, and "
            "each string copies the words you dispute from one row, "
            "verbatim.")
    for q in quotes:
        if not any(_reads_row(ctx, q, r, rows) for r in rows):
            short = len(" ".join(q.split())) < QUOTE_MIN
            said = (f"quotes= holds `{_shown(q)}`, and it is shorter than "
                    f"{QUOTE_MIN} characters. Copy {QUOTE_MIN} characters or "
                    f"more, or the whole row." if short else
                    f"quotes= holds `{_shown(q)}`, and it is not a span of "
                    f"the live text of {' or of '.join(rows)}.")
            return said + tail
    for r in rows:
        if not any(_reads_row(ctx, q, r, rows) for q in quotes):
            return (f"quotes= holds no span of the live text of {r}, and "
                    f"refs names {r}. Each row of refs needs a quote of its "
                    f"own." + tail)
    return None


def _answer_evidence(ctx: api.Ctx, refs, text: str, quotes=None) -> None:
    """The Tester's answer to a challenge quotes the criterion it stands on.

    Only when the wake was a challenge: the trigger message's verb says so.
    Each quote is a span of one quotable row of refs, and one quote is a
    span of a criterion of refs (frame 333, item 3). The exit for a test
    that asserts more than its criterion is `tests.encode`, and this door
    names it."""
    trig = ctx.conn.execute(
        "SELECT verb FROM messages WHERE id = ?", (getattr(ctx, "trigger", None),)).fetchone()
    if not trig or trig["verb"] != "challenge":
        return
    crit = [(r, row["text"]) for r in (refs or [])
            for row in [ctx.conn.execute("SELECT text FROM criteria WHERE id = ?", (r,)).fetchone()]
            if row]
    if not crit:
        raise ValueError(
            "an answer to a challenge names the criterion the test stands on "
            "in refs, beside the test, and yours names no criterion")
    quotes = _quote_list(text, quotes)
    rows = _quoted_rows(ctx, refs)
    loose = next((q for q in quotes if not any(
        _reads_row(ctx, q, r, rows) for r in rows)), None)
    if loose is not None or not any(
            _reads_row(ctx, q, r, rows) for q in quotes for r, _ in crit):
        held = loose if loose is None or len(loose) <= 80 else loose[:77] + "..."
        said = ("" if held is None else
                f"quotes= holds `{held}`, and it is not a span of the live "
                f"text of {' or of '.join(rows)}. Each quote is one span, "
                f"and ")
        raise ValueError(
            f"{said}an answer that keeps the test carries the criterion's words: "
            f"quotes= copying the span of {crit[0][0]} your assertion comes "
            f"from, verbatim. If the test asserts more than the criterion "
            f"asks, the exit is tests.encode, not an answer")


def _answer_refs(ctx: api.Ctx) -> list:
    """The refs of the answer that woke a Developer, or [] on another wake."""
    import json as _json
    if ctx.role != "developer" or not getattr(ctx, "trigger", None):
        return []
    row = ctx.conn.execute("SELECT verb, body_refs FROM messages WHERE id = ?",
                           (ctx.trigger,)).fetchone()
    if row is None or row["verb"] != "answer":
        return []
    try:
        refs = _json.loads(row["body_refs"] or "[]")
    except (TypeError, ValueError):
        return []
    return [r for r in refs if isinstance(r, str)] if isinstance(refs, list) else []


def _answer_decisions(ctx: api.Ctx) -> list:
    """The decision rows that the answer which woke a Developer holds. The
    Developer's own reason row is not the answer's decision (frame 200,
    pass 5, fix 4)."""
    return [r for r in _answer_refs(ctx)
            if _holds_decision(ctx.conn, [r], exclude_author=ctx.role)]


def _challenge_sides(ctx: api.Ctx, refs) -> list:
    """The criterion and the test that `refs` name, as [criterion, test].

    A test knows its criterion, and a criterion with one test knows its test.
    Return [] when the two sides cannot both be named.
    """
    crit = test = None
    for r in refs or []:
        if not isinstance(r, str):
            continue
        # `db.tables_of` finds the row, and the side is the table (F22).
        held = tables_of(ctx.conn, r, among=("criteria", "tests"))
        if crit is None and "criteria" in held:
            crit = r
        elif test is None and "tests" in held:
            test = r
    if test and not crit:
        row = ctx.conn.execute("SELECT criterion_id FROM tests WHERE id = ?",
                               (test,)).fetchone()
        crit = row["criterion_id"] if row else None
    elif crit and not test:
        ids = [r["id"] for r in ctx.conn.execute(
            "SELECT id FROM tests WHERE criterion_id = ?", (crit,))]
        test = ids[0] if len(ids) == 1 else None
    return [crit, test] if crit and test else []


def _answer_mode_challenge_refusal(ctx: api.Ctx, refs, text: str = "",
                                   reason=None,
                                   spans: list | None = None) -> str | None:
    """
    The Developer's challenge from an answer wake carries a decision row.

    Design 200 change 4 gave the answer mode `msg.challenge_tester` as the
    route of the Architect's decision row to the Tester. The interview of
    the s282 case (`plans/frame200-interviews.md`) found the seat sent it
    with refs that resolved to a criterion and a test only. Return the
    refusal, or None outside an answer wake or when a ref is a decision.
    """
    if ctx.role != "developer" or not getattr(ctx, "trigger", None):
        return None
    trig = ctx.conn.execute("SELECT verb, body_text FROM messages WHERE id = ?",
                            (ctx.trigger,)).fetchone()
    if trig is None or trig["verb"] != "answer":
        return None
    # The seat's own reason row is not the row route of pass 2e (frame 200,
    # pass 5, fix 4).
    if _holds_decision(ctx.conn, refs, exclude_author=ctx.role):
        return None
    held = _answer_decisions(ctx)
    if held:
        # The review of pass 2e, finding 2: the evidence door dictated
        # refs=[c, tst], and this door then ended the session on that call.
        # Frame 135's law: a refusal names a call that the doors admit.
        sides = _challenge_sides(ctx, refs) or _challenge_sides(
            ctx, _answer_refs(ctx))
        said = (f"no ref of this challenge is a decision row, and the answer "
                f"{ctx.trigger} holds the decision {', '.join(held)}. ")
        if not sides:
            # No exact call is derivable, so the text names the three parts.
            slot = (f", and {REASON_SLOT}"
                    if _takes_reason(ctx.role, "tester", "challenge") else "")
            return (said + f"Send msg.challenge_tester with the criterion, "
                    f"the test and the decision {', '.join(held)} in "
                    f"refs{slot}.")
        offered = list(dict.fromkeys(sides + held))
        args = {"refs": offered}
        if text:
            # The quotes as sent, because the joined text is one quote now.
            args["quotes"] = spans if spans else text
        # Frame 200, pass 5, fix 2: the call names reason=, with the seat's
        # own words when the reason door admits them, else the slot.
        slot = ""
        if _takes_reason(ctx.role, "tester", "challenge"):
            args["reason"] = _reason_offered(ctx.conn, reason, text, sides)
            slot = ", " + _reason_arg(ctx.conn, reason, text, sides)
        return api._offer(
            ctx, said + f"Send msg.challenge_tester(refs={offered}{slot}): the "
            f"criterion {sides[0]}, the test {sides[1]} and the decision "
            f"{', '.join(held)}, with the same quotes.",
            "msg.challenge_tester", args)
    # law 2: judgement crosses a role boundary only as ids and states
    # The review of 8d090e2e, finding 9: both Tester answers to a Developer
    # challenge on nights 138 and 139 carried text. "No words" is a fact
    # only of an answer whose text is empty.
    said = ("The answer carries the rows you sent back and no words. "
            if not (trig["body_text"] or "").strip() else "")
    return _Ending(
        f"no ref of this answer is a decision row. {said}If you still read "
        f"the test as wrong, say so in one sentence and end. {END_STEP} "
        f"{_end_form(ctx, _unique_refs(refs))}")


def _rowless_answer_refusal(ctx: api.Ctx, refs) -> str | None:
    """
    The Architect's answer to the Developer adds a row to the cause's refs.

    The cause is the message that woke the session, or the row that a
    `tick:unresolved` wake names. A row this session wrote counts as added,
    so `model.amend` and `findings.find` on a row of the cause still answer.
    Return the refusal, or None when the answer adds a row or has no cause.
    """
    import json as _json
    cause = getattr(ctx, "trigger", None)
    if not cause and getattr(ctx, "wake_kind", "") == "tick:unresolved":
        cause = next(iter(ctx.wake_refs or ()), None)
    row = ctx.conn.execute("SELECT body_refs FROM messages WHERE id = ?",
                           (cause,)).fetchone() if cause else None
    if row is None:
        return None
    try:
        theirs = set(_json.loads(row["body_refs"] or "[]"))
    except (TypeError, ValueError):
        theirs = set()
    written = {w[1] for w in ctx.writes}
    added = [r for r in (refs or []) if isinstance(r, str) and r != cause
             and (r not in theirs or r in written)
             and not ctx.conn.execute("SELECT 1 FROM messages WHERE id = ?",
                                      (r,)).fetchone()]
    if added:
        return None
    said = (f"refs={list(refs or [])} add no row to the refs of {cause}, so "
            f"the Developer gets back the rows it sent. ")
    # The review of 8d090e2e, finding 3: the escalate brief says "model.amend,
    # and say so with msg.answer_developer". 0 of 6 such answers on nights
    # 138 and 139 cited the row they wrote, so the refusal names those rows.
    # The review of pass 2c, finding 3: `model.amend` stages a
    # `constraint_bindings` id like `k_new:src/x.py`, which names no row a
    # ref can cite. So only rows of the three answer tables are offered.
    mine = list(dict.fromkeys(
        w[1] for w in ctx.writes
        if isinstance(w[1], str) and w[1] != cause
        and w[0] in ("constraints", "findings", "decisions")))
    if mine:
        return api._offer(
            ctx, said + f"This session wrote {', '.join(mine)}. Send "
            f"msg.answer_developer(refs={mine}).",
            "msg.answer_developer", {"refs": mine})
    return (said + "Write what you found with decisions.author, then send "
            "msg.answer_developer with the decision's id in refs.")


def _arrange_fault_of(ctx: api.Ctx, ref: str, output: str) -> dict | None:
    """`runner.arrange_fault` on a stored test's red run, or None."""
    import json as _json

    from .runner import arrange_fault
    row = ctx.conn.execute(
        "SELECT t.body, t.path, c.text, c.surface_refs, b.worktree "
        "FROM tests t LEFT JOIN criteria c ON c.id = t.criterion_id "
        "LEFT JOIN batches b ON b.id = t.batch_id WHERE t.id = ?",
        (ref,)).fetchone()
    if row is None:
        return None
    try:
        refs = _json.loads(row["surface_refs"] or "[]")
    except ValueError:
        refs = []
    surface = {str(s).rsplit("::", 1)[-1] for s in refs}
    return arrange_fault(row["body"] or "", row["path"] or "", output,
                         surface, row["text"] or "", row["worktree"] or "")


def _red_line_refusal(ctx: api.Ctx, refs, text: str,
                      quotes=None) -> str | None:
    """The refusal of a challenge whose quote misses the line a red test
    fails at, or None when the quote holds that line or no run names one.

    The failing line is the run's first `>` line that is in the test's
    body, else the test's first `assert` line. The run's error line counts as the same line.
    Night 142's m83 quoted the `expected` line of inh_echo_04 and left out
    the `.strip()` that made it red. The Vision Keeper s185 then wrote a
    false decision from the quote (frame 213). A run that fails in the
    test's own arrange step also admits a quote of the raising line, the
    stub's line or its error, whatever the refs count (frame 304).
    Frame 333, item 3: one quote holds the whole line. The window of 12
    characters passed a quote of part of the line.
    """
    from . import harness

    quoted = _quote_list(text, quotes)
    for ref in refs or []:
        if not isinstance(ref, str):
            continue
        test = ctx.conn.execute("SELECT body FROM tests WHERE id = ?", (ref,)).fetchone()
        # The test's own batch only (frame 210, fact F4).
        run = ctx.conn.execute(
            "SELECT result, output FROM latest_runs WHERE test_id = ? "
            "AND batch_id = (SELECT batch_id FROM tests WHERE id = latest_runs.test_id)",
            (ref,)).fetchone() if test else None
        if not run or run["result"] not in ("fail", "error"):
            continue
        out = (run["output"] or "").splitlines()
        # The `>` line is where the run failed, whatever it holds. The
        # body's first assert stands in only when the run marks no line
        # of the body (the review of f252df24, finding 2). A `>` line of
        # library code names no line the seat can quote (the review of
        # 126b8c4e, finding 5).
        body = {ln.strip() for ln in _code_only(test["body"] or "").splitlines()
                if ln.strip()}
        marked = next((ln[1:].strip() for ln in out
                       if ln.startswith(">") and ln[1:].strip() in body), None)
        # The short form puts the line under `path:N: in name`, with no
        # `>`. Night 167's tr110 failed at collection that way, and the
        # window matched the line's words in the `E` line by chance.
        marked = marked or next(
            (nxt.strip() for ln, nxt in zip(out, out[1:])
             if re.match(r"\S.*?\.py:\d+: in \S", ln) and nxt.strip() in body),
            None)
        first = next((ln.strip() for ln in _code_only(test["body"] or "").splitlines()
                      if ln.strip().startswith("assert")), None)
        line = marked or first
        # Fact F5: `harness.error_line` is the one reader of the line.
        said = harness.error_line(run["output"]) or None
        if not line and not said:
            continue
        if any(_quote_reads(q, s, holds=True) for q in quoted
               for s in (line, said) if s):
            continue
        # Frame 304, night 159: s185 quoted the `FakeStdin` stub and the
        # call that read it, and this door wanted the assert line. A run
        # that fails in the test's own arrange step fails at that line.
        fault = _arrange_fault_of(ctx, ref, run["output"] or "")
        if fault and any(_quote_reads(q, s, holds=True) for q in quoted for s in
                         (fault["quote"], fault["error"]) if s):
            continue
        # Frame 328, review of pass 3, finding 3: tst_tk3's line holds raw
        # ESC bytes, and a seat reads them as `assert "[2J[H"`.
        named = " or ".join(f"`{_escaped_view(s)}`" for s in (line, said) if s)
        return (f"{ref} is red, and its run names the line it fails at: {named}. "
                f"quotes= copies that line verbatim, because a quote of "
                f"another line of the test names the wrong conflict")
    return None


#: The fewest characters a challenge quote holds, after whitespace
#: normalisation, unless it is the whole row. The window of 2026-08-27 had
#: the same length. Frame 328, review 1: with no floor, `["in", "a1"]` landed.
QUOTE_MIN = 12


def _lined(s: str) -> str:
    """Whitespace normalised, but a run that holds a line break stays one."""
    return re.sub(r"\s+", lambda m: "\n" if "\n" in m.group() else " ",
                  (s or "").strip())


def _span_of(quote: str, source: str, floor: int = QUOTE_MIN,
             lined: bool = False) -> bool:
    """The quote is a contiguous span of the source, whitespace-normalised,
    of `floor` characters or the whole source.

    Two forms of the same span count too, because each comes from the
    call's syntax, not from the seat's words. Night 119's s250 put the span
    inside quote marks. Night 126's s172 wrote a `"` of the row as `'` inside
    its double-quoted string.

    `lined` says that the call decoded a line break of the quote from the
    seat's `\\n`, as night 124's s144 copied a body from the prompt's JSON.
    That line break matches only where the row breaks the line (review 1,
    finding 4). F19 pass 1b: `api._call_values` decodes the quote, so this
    function keeps no decoder of its own.
    """
    src = " ".join((source or "").split())
    raw = (quote or "").strip()
    forms = [raw]
    if len(raw) > 2 and raw[0] == raw[-1] and raw[0] in "\"'`":
        forms.append(raw[1:-1])

    def _swap(s: str) -> str:
        return s.replace("'", '"')

    for f in forms:
        if not lined:
            q = " ".join(f.split())
            if (q and (len(q) >= floor or q == src)
                    and (q in src or _swap(q) in _swap(src))):
                return True
            continue
        lined_f = _lined(f)
        if not lined_f or (len(lined_f) < floor
                           and lined_f != _lined(source)):
            continue
        # A space of the quote may stand for a wrap of the row. A decoded
        # line break must meet a line break.
        pattern = "".join("[ \n]" if t == " " else "\n" if t == "\n"
                          else re.escape(t)
                          for t in re.split(r"( |\n)", _swap(lined_f)) if t)
        if re.search(pattern, _swap(_lined(source))):
            return True
    return False


def _outer_marks(text: str) -> list[str]:
    """The text with one outer quote mark dropped, the likelier reading
    first.

    Frame 328, the residue, night 167 walk 3: s327 and s336 to s338 sent
    `'When ... returns \\'c.txt\\'.` and `... \\'c.txt\\''.`. One mark
    opens the quote and none closes it, or the closing mark stands before
    a `.`. `_span_of` strips an outer mark only as a pair, and the seat
    cannot type that pair. Each form only drops one mark at the start and
    one mark, or a mark and a `.`, at the end. So a form is still a
    verbatim span of the seat's text, and the floor still holds.

    F19: this rule stays beside `api._call_values`, because no parse path
    reads a value with one unpaired mark.
    """
    d = (text or "").strip()
    mark = d[:1] if d[:1] in "'\"" else ""
    # A form whose inner marks pair up is the likelier reading, so the
    # refusal shows that form.
    first, rest = [], []
    if mark:
        for end in (len(d) - 1, len(d) - 2):
            if end > 1 and d[end] == mark and d[end + 1:] in ("", "."):
                inner = d[1:end]
                (first if inner.count(mark) % 2 == 0 else rest).append(inner)
                break
        (first if d[1:].count(mark) % 2 == 0 else rest).append(d[1:])
    end_mark = (d[-1:] if d[-1:] in "'\"" else
                d[-2:-1] if d.endswith(".") and d[-2:-1] in "'\"" else "")
    if end_mark and not mark:
        cut = d[:-1] if d.endswith(end_mark) else d[:-2]
        if cut.count(end_mark) % 2 == 0:
            rest.append(cut)
    forms: list[str] = []
    for f in first + rest:
        if f.strip() and f != d and f not in forms:
            forms.append(f)
    return forms


def _escaped_view(s: str) -> str:
    """The text with each control character shown as `\\xNN`, so that a
    refusal can show a raw byte."""
    return "".join(f"\\x{ord(ch):02x}" if ord(ch) < 32 and ch not in "\n\t"
                   else ch for ch in s)


def _quote_list(text: str, quotes=None) -> list[str]:
    """The quotes of a challenge, one string per quote.

    The binder hands its list on, so an elided quote `A ... B` is one quote,
    and it is not a span (review 1, finding 5). A stored message holds only
    the joined text, so that text splits back on the binder's " ... " mark.
    """
    if isinstance(quotes, dict):
        quotes = list(quotes.values())
    if isinstance(quotes, str):
        quotes = [quotes]
    if isinstance(quotes, (list, tuple)):
        return [str(q) for q in quotes if str(q).strip()]
    return [q for q in " ".join((text or "").split()).split(" ... ")
            if q.strip()]


def _quote_refusal(row: str, table: str, quote: str, crit: str,
                   test: str, short: bool = False, both: bool = False) -> str:
    """The refusal of a challenge quote that is not in its row's live text."""
    shown = quote if len(quote) <= 80 else quote[:77] + "..."
    if short:
        said = (f"quotes= holds `{shown}`, and it is shorter than "
                f"{QUOTE_MIN} characters. Copy {QUOTE_MIN} characters or "
                f"more, or the whole row.")
    elif both:
        said = (f"quotes= holds `{shown}` as the quote of {row}. Each row "
                f"needs a quote of its own.")
    elif quote:
        said = (f"quotes= holds `{shown}`, and it is not in the live text "
                f"of {row}.")
    else:
        said = f"quotes= holds no span of the live text of {row}."
    if table == "tests":
        said += " A comment of the test does not count."
    if quote:
        # The residue of frame 328: the seat sees the form the door
        # compared, so a refusal of the old text is not read as a syntax
        # one. F19: the form is the value that the call stores.
        value = (api._call_values(quote) or (quote,))[0]
        dropped = _outer_marks(value)
        read = " ".join((dropped or [value])[0].split())
        if read != " ".join(quote.split()):
            read = _escaped_view(read if len(read) <= 80 else read[:77] + "...")
            said += (" The door also reads the quote as the call stores it "
                     "from your text, with each escape read as Python reads "
                     "it.")
            if dropped:
                said += (" It drops one outer quote mark at each end, and a "
                         "`.` after the closing quote mark.")
            said += (f" Read that way, the quote is `{read}`, and the "
                     f"{'code' if table == 'tests' else 'live text'} of "
                     f"{row} holds no such span.")
    return (f"{said} Quote, not paraphrase: copy a contiguous span of each "
            f"row, verbatim, from the rows in front of you. Send quotes as a "
            f"list of two strings: one copied from {crit}, one copied from "
            f"{test}")


def _green_at_head_refusal(ctx: api.Ctx, refs) -> str | None:
    """
    The refusal of a Developer challenge on a test that passes at the
    batch's head, or None.

    Frame 328, night 166: m83 and m88 named tst_c1 while its last run at
    a0295dff passed. The Tester s202 then rewrote a green test. The tests a
    Developer may challenge are the red ones, so the door reads the test's
    last run at the head commit. Other roles do not meet this door.
    """
    if ctx.role != "developer" or not ctx.batch_id:
        return None
    test_id = next((r for r in refs or [] if isinstance(r, str) and
                    ctx.conn.execute("SELECT 1 FROM tests WHERE id = ?",
                                     (r,)).fetchone()), None)
    if test_id is None:
        return None
    run = ctx.conn.execute(
        "SELECT tr.result, tr.output, b.head_commit FROM latest_runs tr "
        "JOIN batches b ON b.id = tr.batch_id "
        "WHERE tr.test_id = ? AND tr.batch_id = ? "
        "AND tr.commit_sha = b.head_commit", (test_id, ctx.batch_id)).fetchone()
    if not run or run["result"] != "pass":
        return None
    last = next((ln.strip() for ln in reversed((run["output"] or "").splitlines())
                 if ln.strip()), "pass")
    from ..roles.api import guard_words

    # A guard test names its commitment and the behaviour (pass 3c).
    red = [f"{r['test_id']} ({r['criterion_id'] or guard_words(ctx.conn, r['commitment_id'])})"
           for r in ctx.conn.execute(
        "SELECT DISTINCT tr.test_id, t.criterion_id, t.commitment_id FROM latest_runs tr "
        "JOIN tests t ON t.id = tr.test_id "
        "WHERE t.batch_id = ? AND tr.batch_id = t.batch_id "
        "AND tr.result IN ('fail', 'error') "
        "AND (t.criterion_id IS NOT NULL OR t.commitment_id IS NOT NULL)",
        (ctx.batch_id,))]
    then = (" The failing tests of this batch: " + ", ".join(red[:3]) + "."
            if red else " No test of this batch with a criterion fails.")
    return (f"{test_id} passes on the batch's head {run['head_commit'][:8]}: "
            f"its last run there says `{last}`. A challenge disputes a red "
            f"test, and this test is green.{then}")


def _challenge_evidence(ctx: api.Ctx, recipient: str, refs, text: str,
                        reason=None, quotes=None) -> None:
    """
    A challenge quotes the thing it disputes.

    Challenging costs one call carrying an id; fixing costs reading, writing
    and committing. When two outcomes cost that differently, which one you get
    is decided by noise -- so the challenge is made to pay the reading up
    front. `quotes=` must copy the disputed rows' own words, and on the
    tester channel both sides of the claimed conflict must be named and
    quoted. None of this says the challenge is *right*; `challenge.uphold`
    holds the same line one loop earlier -- either verdict carries the line
    it stands on.
    """
    rows = _quoted_rows(ctx, refs)

    if recipient == "tester":
        crit = [r for r, (t, _) in rows.items() if t == "criteria"]
        test = [r for r, (t, _) in rows.items() if t == "tests"]
        if not crit or not test:
            missing = "no criterion" if not crit else "no test"
            # The review of pass 2e, finding 1: a hint of [c, tst] dropped
            # the decision row, and the answer-mode door refused that call.
            # So a hint keeps the decision rows the seat sent, and the ones
            # the waking answer holds. Frame 135's law: a hint names a call
            # that every door admits.
            # The seat's own reason row is not kept: the binder adds it again
            # (frame 200, pass 5, fix 4).
            keep = list(dict.fromkeys(
                [r for r in refs or []
                 if _holds_decision(ctx.conn, [r], exclude_author=ctx.role)]
                + _answer_decisions(ctx)))
            reasoned = _takes_reason(ctx.role, recipient, "challenge")

            def _send(c: str, t: str) -> str:
                # Frame 200, pass 5, fix 2: the hint names reason=, with the
                # seat's own words when the reason door admits them.
                slot = (", " + _reason_arg(ctx.conn, reason, text, [c])
                        if reasoned else "")
                return f"send refs={[c, t] + keep}{slot}"
            # Name the exact repair when it is derivable: a test knows its
            # own criterion. Measured (S0 walk four): the Developer chose
            # the right door with the right quotes three sessions running
            # and died on refs=['t1','t1'] every time -- the general
            # sentence did not correct it, so the refusal now writes the
            # call out.
            hint = ""
            if test and not crit:
                row = ctx.conn.execute(
                    "SELECT criterion_id FROM tests WHERE id = ?",
                    (test[0],)).fetchone()
                if row and row["criterion_id"]:
                    hint = (f". {test[0]}'s criterion is "
                            f"{row['criterion_id']}: "
                            f"{_send(row['criterion_id'], test[0])}")
                elif row:
                    # click night 47 (2026-09-14): "send refs=['None', ...]"
                    # was sent as written, four turns, on nineteen of the
                    # project's own tests. Frame 207: the base run, not a
                    # constant, says whether it passed before this batch.
                    fact = project_tests_fact(ctx, [test[0]])
                    hint = (f". {test[0]} has no criterion: it is the project's "
                            f"own test and " + (fact or
                            "it passed before this batch. A "
                            "challenge has no side there. Read code.diff and "
                            "restore what your change broke"))
            # The other direction of the same derivation. Measured the day
            # the Critic's structural fork landed: `verdicts.claim_encodes`
            # correctly named the criterion, the challenge that followed
            # named only it, died on this refusal, and was never retried --
            # the model moved on to emitting a verdict instead. A criterion
            # under review knows its own test the same way a test knows its
            # criterion; unambiguous when there is exactly one.
            elif crit and not test:
                ids = [r["id"] for r in ctx.conn.execute(
                    "SELECT id FROM tests WHERE criterion_id = ?", (crit[0],))]
                if len(ids) == 1:
                    hint = (f". {crit[0]}'s test is {ids[0]}: "
                            f"{_send(crit[0], ids[0])}")
            if not hint and ctx.batch_id:
                # clickI night 26 (2026-09-12): woken for a failing test,
                # the Developer named a criterion with no test of its own
                # and was refused with no way forward. The failing tests
                # of the batch are a fact the wake already carries.
                failing = ctx.conn.execute(
                    "SELECT DISTINCT tr.test_id, t.criterion_id FROM latest_runs tr "
                    "JOIN tests t ON t.id = tr.test_id "
                    "WHERE t.batch_id = ? AND tr.batch_id = t.batch_id "
                    "AND tr.result IN ('fail', 'error')",
                    (ctx.batch_id,)).fetchall()
                # A test with no criterion is the project's own, broken by
                # the diff. click night 47 (2026-09-14): the hint said
                # "send refs=['None', 'inh_5f7b1750']" and the Developer
                # sent exactly that, four turns, on nineteen such tests.
                owned = [r for r in failing if r["criterion_id"]]
                if owned:
                    hint = ". The failing tests of this batch: " + "; ".join(
                        _send(r["criterion_id"], r["test_id"])
                        for r in owned[:3])
                elif failing:
                    fact = project_tests_fact(
                        ctx, [r["test_id"] for r in failing])
                    hint = (f". The {len(failing)} failing test(s) have no criterion: "
                            f"they are the project's own and " + (fact or
                            "passed before this "
                            "batch. A challenge has no side there. Read code.diff "
                            "and restore what your change broke"))
            raise ValueError(
                f"a challenge to the tester names both sides of the conflict "
                f"in refs -- the criterion and the test -- and yours names "
                f"{missing}{hint}")
        if ctx.batch_id:
            ok = ctx.conn.execute(
                "SELECT 1 FROM batch_tickets bt "
                "JOIN criteria c ON c.ticket_id = bt.ticket_id "
                "WHERE bt.batch_id = ? AND c.id = ?"
                + api._live_rows(ctx.conn, "c.retired_by"),
                (ctx.batch_id, crit[0])).fetchone()
            if not ok:
                raise ValueError(
                    f"{crit[0]!r} is not a criterion of this batch. The "
                    f"conflict you may challenge is between this batch's "
                    f"test and this batch's criterion")
        # law 3: fact artefacts generate no contact; nobody to ask
        # The project's own test has no criterion and no side to challenge.
        # Click night 55 (2026-09-14): a challenge paired ce_2 with
        # test_termui's prompt test, which the Developer's own rewrite had
        # broken; the Tester woken by it wrote nothing, and the message
        # sat unresolved on top of the fix loop.
        owner = ctx.conn.execute(
            "SELECT criterion_id FROM tests WHERE id = ?", (test[0],)).fetchone()
        if owner is not None and not owner["criterion_id"]:
            # Frame 207: the base run, not a constant, says whether the
            # test passed before this batch.
            fact = project_tests_fact(ctx, [test[0]])
            raise ValueError(
                f"{test[0]} has no criterion: it is the project's own test and "
                + (fact or "it passed before this batch. A challenge has no "
                   "side there. Read code.diff and restore what your change "
                   "broke"))
        # ruling: DECISIONS 1290, a contiguous span of the disputed row, verbatim
        # Frame 328, night 166: m82 and m88 quoted c_1's contested old text.
        # The 12-character window found "When shorten" in the live text, and
        # the test side matched on the other side's quote. So each quote must
        # stand inside its own row's live text, whitespace-normalised.
        quotes = _quote_list(text, quotes)
        # The disputed artefact is the test, and its words are what the bar
        # is for. A criterion quote that is another criterion of this batch,
        # verbatim, is real evidence misfiled -- and walks twenty-three to
        # twenty-seven measured the alternative: told whose words they were,
        # the Developer sent the identical call nine times across three
        # sessions. The challenge goes through; the Tester reads both quotes.
        siblings = [o["text"] or "" for o in ctx.conn.execute(
            "SELECT c.text FROM criteria c "
            "JOIN batch_tickets bt ON bt.ticket_id = c.ticket_id "
            "WHERE c.id != ? AND bt.batch_id = ?"
            + api._live_rows(ctx.conn, "c.retired_by"),
            (crit[0], ctx.batch_id or ""))]
        # The test's side is its code. Click night 58 (2026-09-14): the
        # Tester had pasted the criterion sentence into a comment, so the
        # criterion quote spanned the test row too, and a challenge with an
        # empty test-side quote went through; the Tester woken by it had
        # nothing to defend.
        crit_words = [rows[crit[0]][1]] + siblings
        test_words = rows[test[0]][1]
        run = _run_view(ctx, test[0])

        # Frame 333, pass 1b: each half reads through `_quote_reads`, the
        # one reader of every channel. The seat forms of night 167 and
        # frame 335 live there.
        def _cites(q: str, floor: int = QUOTE_MIN) -> tuple[bool, bool]:
            return (any(_quote_reads(q, s, "criteria", floor)
                        for s in crit_words),
                    _quote_reads(q, test_words, "tests", floor, run))

        # Review 1, finding 2: a quote of a few characters pays no reading.
        short = next((q for q in quotes
                      if not any(_cites(q)) and any(_cites(q, 0))), None)
        if short is not None:
            raise ValueError(_quote_refusal(
                "", "", short, crit[0], test[0], short=True))
        sides = [_cites(q) for q in quotes]
        on_crit = [i for i, s in enumerate(sides) if s[0]]
        on_test = [i for i, s in enumerate(sides) if s[1]]
        loose = [q for q, s in zip(quotes, sides) if not any(s)]
        for i, (r, on) in enumerate(((crit[0], on_crit), (test[0], on_test))):
            if on:
                continue
            q = (quotes[i] if i < len(quotes) and quotes[i] in loose
                 else loose[0] if loose else "")
            raise ValueError(_quote_refusal(r, rows[r][0], q, crit[0], test[0]))
        # Review 1, finding 2: one quote never stands for both rows.
        if not any(i != j for i in on_crit for j in on_test):
            raise ValueError(_quote_refusal(
                f"{crit[0]} and of {test[0]}", "", quotes[on_crit[0]],
                crit[0], test[0], both=True))
        if loose:
            raise ValueError(_quote_refusal(f"{crit[0]} or of {test[0]}", "",
                                            loose[0], crit[0], test[0]))
        return

    # No redirect by who is quoted. A rule that sent a quoted test to the
    # Tester (from CR-a-test-that-encodes-nothing's transcript) bought that
    # case nothing and sent the L3 failed-verdict chain from 5/5 to 0/5:
    # at review the tests are green by construction, so nothing mechanical
    # separates "the test is vacuous" from "the diff is wrong", and the
    # desk is the Critic's judgement to make.
    # Every other channel: each quote is a span of one quotable row of refs,
    # and each such row has a quote (ruled: Roman, 2026-08-26, "on all five
    # of its channels", DECISIONS.md 1294). Vacuously legal when the refs
    # carry no quotable row, because bounded strictness beats a guard with
    # no exit.
    if rows:
        said = _rows_quote_refusal(ctx, rows, _quote_list(text, quotes))
        if said is not None:
            raise ValueError(said)


_BUILDERS = ("tester", "developer")


def _unbuilt_refusal(ctx, recipient: str, verb: str, refs) -> None:
    """
    Refuse a message to a Tester or a Developer, or a question from one,
    when no change of the item has a commit.

    A Tester or a Developer woken on such a message has no door that lets it
    work. Night 173's s112 answered before any batch existed, and
    `tests.encode` refused the woken Tester s113 12 times. Night 169's s113
    asked with no batch (m30), and the answer m31 woke s115 into the same
    refusal (W10, the review of fe1d300c). The batch fact is
    `api.built_batch`, the reader `tests.encode` uses.
    """
    trigger = getattr(ctx, "trigger", None)
    woke = ctx.conn.execute("SELECT from_role FROM messages WHERE id = ?",
                            (trigger,)).fetchone() if trigger else None
    # A tick that wakes a Tester or a Developer names its batch. Only a
    # message wake leaves the asker with no batch, as night 169's s113.
    asker = (verb in OWED_A_REPLY and ctx.role in _BUILDERS
             and woke is not None)
    if recipient not in _BUILDERS and not asker:
        return
    # A message with no refs names no item, so the batch fact has no subject.
    refs = [r for r in refs if isinstance(r, str)]
    if not refs:
        return
    # The scheduler named the batch, so the session works inside it.
    if getattr(ctx, "batch_id", None):
        return
    if not asker:
        # A reply to the recipient's own question lands. That question passed
        # this door, so the asker held a batch.
        if woke and woke["from_role"] == recipient:
            return
        if refs and ctx.conn.execute(
                "SELECT 1 FROM messages m, json_each(m.body_refs) j WHERE "
                "m.from_role = ? AND m.to_role = ? AND m.status = 'unresolved' "
                "AND j.value IN (SELECT value FROM json_each(?))",
                (recipient, ctx.role, json.dumps(refs))).fetchone():
            return
    # The item's criteria, reached from a criterion, ticket, item or batch ref.
    crit = sorted({row["id"] for r in refs for row in ctx.conn.execute(
        "SELECT c.id FROM criteria c JOIN tickets t ON t.id = c.ticket_id "
        "WHERE c.id = ? OR c.ticket_id = ? OR t.item_id = ? OR c.ticket_id IN "
        "(SELECT ticket_id FROM batch_tickets WHERE batch_id = ?)", (r, r, r, r))})
    # A criterion staged in this session has no row yet. Its ticket is in
    # the staged write (frame 306: specify, then the note to the Tester).
    staged = {i: rest[0].get("ticket_id") for t, i, *rest in ctx.writes
              if t == "criteria" and rest and isinstance(rest[0], dict)}
    # The item's tickets, reached from a criterion, ticket, item or batch
    # ref. An item can have a batch before it has a criterion.
    tickets = {row["id"] for r in refs for row in ctx.conn.execute(
        "SELECT t.id FROM tickets t WHERE t.id = ? OR t.item_id = ? OR t.id IN "
        "(SELECT ticket_id FROM criteria WHERE id = ?) OR t.id IN "
        "(SELECT ticket_id FROM batch_tickets WHERE batch_id = ?)", (r, r, r, r))}
    tickets |= {staged[r] for r in refs if staged.get(r)}
    built = [b for b in (api.built_batch(ctx.conn, None, t, need_commit=True) for t in sorted(tickets))
             if b]
    if any(b["status"] != "merged" for b in built):
        return
    # A test of an abandoned or deferred batch is one the Tester rewrites.
    # Night 142's walk 1 heard "has written no test of it" over such a test,
    # four times (frame 213).
    written = [t for c in crit for t in ctx.conn.execute(
        "SELECT t.id, t.criterion_id, t.batch_id, b.status FROM tests t "
        "LEFT JOIN batches b ON b.id = t.batch_id WHERE t.criterion_id = ? "
        "ORDER BY t.id", (c,))]
    if recipient == "tester" and any(
            t["status"] in ("abandoned", "deferred") for t in written):
        return
    if recipient == "tester" and written:
        t = written[0]
        raise ValueError(
            f"{t['id']} is the test of {t['criterion_id']}, and its "
            f"batch {t['batch_id']} is {t['status'] or 'gone'}. The "
            f"Tester rewrites a test when its change has a commit or "
            f"has stopped. Your work here is done")
    # A merged change is built, so a reopen after the merge reaches the
    # Developer (the coordinator's ruling on pass 1b).
    if built:
        return
    # At most three ids, so the text stays under 25 words (the review's low p2-3).
    ids = ", ".join(refs[:3]) + (f" and {len(refs) - 3} more" if len(refs) > 3 else "")
    if asker:
        raise ValueError(
            f"No change built from {ids} has a commit yet, and you hold no "
            f"batch, so there is nothing to ask about. Stop here.")
    raise ValueError(
        f"No change built from {ids} has a commit yet, so the "
        f"{recipient.capitalize()} has nothing to work on. Stop here.")


def _escalation_over_removed_grain(ctx, refs) -> None:
    import re as _re
    from pathlib import Path as _P

    if not ctx.batch_id:
        return
    row = ctx.conn.execute("SELECT worktree FROM batches WHERE id = ?",
                           (ctx.batch_id,)).fetchone()
    if not (row and row["worktree"]):
        return
    root = _P(row["worktree"])
    # The same fact for a name that is still defined but changed shape:
    # the register (2026-09-10), llama escalated over display_results
    # gaining two required parameters, which is what the finding says.
    drift = api._signature_drift(ctx, root)
    if drift:
        raise ValueError(
            "the finding stands on a fact about your tree, and the Architect "
            "read the same diff. " + " ".join(drift) + ". Then code.commit")
    for ref in refs:
        f = ctx.conn.execute(
            "SELECT grain, constraint_id FROM findings WHERE id = ? "
            "AND batch_id = ? AND status = 'violated'", (ref, ctx.batch_id)).fetchone()
        if not f:
            continue
        grain = (f["grain"] or "").split("::")[-1]
        if not _re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", grain):
            continue
        # F13 (rule C76): `definers_of` decides, with the session's staged
        # writes for the index's lag. No second rule walks the worktree.
        if not api.definers_of(ctx.conn, grain, api.staged_writes(ctx)):
            raise ValueError(
                f"the finding {ref} is about {grain!r}, which constraint "
                f"{f['constraint_id']} binds, and no file in the worktree "
                f"defines {grain!r} now. That is what the finding says, and "
                f"the Architect read the same diff. Restore the name: define "
                f"{grain} again, or a wrapper under that name, and code.commit")


def _reply_to_read(ctx: api.Ctx) -> bool:
    """True when the principal's words answer an ask this session still owes a
    reading for. That is the `answering` mode, and nothing else: a `verdict`
    message carries a ruling `principal.land` already wrote."""
    trigger = getattr(ctx, "trigger", None)
    row = ctx.conn.execute(
        "SELECT from_role, verb FROM messages WHERE id = ?",
        (trigger,)).fetchone() if trigger else None
    if row is None or row["from_role"] != "principal" or row["verb"] != "converse":
        return False
    return api._ask_of(ctx) is not None


#: How many challenges on one version of the refs may stand unanswered before
#: the door refuses the next one. Two gives a stochastic Tester one more wake
#: (ruled: the judging session, 2026-10-05, frame 132's design, question 2).
#: The bound's sentence says "neither", so it names two priors.
UNANSWERED_CHALLENGES = 2


def _refs_key(refs, as_set: bool = False) -> list:
    """The refs as the door compares them: a sorted list, or a sorted set."""
    return sorted(set(refs)) if as_set else sorted(refs)


def _same_refs_rows(conn: sqlite3.Connection, role: str, recipient: str,
                    verb: str, refs, as_set: bool = False,
                    drop_own: bool = False) -> list:
    """
    The messages that `role` sent to `recipient` with `verb` on these refs,
    newest first. Each row carries the id and the refs of its newest answer
    row, from any role.

    The refs match as a sorted list. Frame 111's design review (2026-10-02):
    the same refs in another order escaped the door. With `as_set`, they
    match as a set, so a repeated ref is the same refs (the review of
    b2ed55b, 2026-10-05). With `drop_own`, both sides match without the
    `decisions` rows that `role` wrote (frame 200, pass 5, fix 1).
    """
    import json as _json

    def _mine_out(got):
        return _without_own_reasons(conn, got, role) if drop_own else got
    try:
        want = _refs_key(_mine_out(refs or []), as_set)
    except TypeError:
        want = _refs_key(refs or [])
    rows = []
    for row in conn.execute(
            "SELECT m.id, m.body_refs, m.status, a.id AS answer_id, "
            "a.body_refs AS answer_refs FROM messages m "
            "LEFT JOIN messages a ON a.id = ("
            "  SELECT x.id FROM messages x WHERE x.cause_id = m.id "
            "  AND x.verb = 'answer' ORDER BY x.seq DESC LIMIT 1) "
            "WHERE m.from_role = ? AND m.to_role = ? AND m.verb = ? "
            "ORDER BY m.seq DESC", (role, recipient, verb)):
        try:
            if _refs_key(_mine_out(_json.loads(row["body_refs"] or "[]")),
                         as_set) != want:
                continue
        except (TypeError, ValueError):
            continue
        rows.append(row)
    return rows


def _sent_this_session(ctx: api.Ctx, recipient: str, verb: str) -> list[dict]:
    """
    The rows of `verb` to `recipient` that this session staged, oldest
    first. An empty list when the session sent none.

    The triage verdict's row is the op's, not the model's send. A question the
    model sends after the verdict is its first (frame 81).

    This is the one reader of what the session sent (F24). A door that asks
    the question calls it, so no door keeps a triage row the others drop.
    """
    return [m for m in (getattr(ctx, "outbound", None) or [])
            if m.get("to_role") == recipient and m.get("verb") == verb
            and m.get("route") != "triage"]


def _ruling_answer_refusal(ctx: api.Ctx, refs) -> str | None:
    """
    The refusal of the Terminologist's first answer to the Tester under a
    ruling relay, when the answer's refs omit a criterion that the ruling
    marks `contest` or `revise`. None when the door has nothing to say.

    Frame 308, night 158's s220: the ruling marked cr_2 `revise` and cr_3
    `contest`. s220 answered with cr_3 alone, and the one-answer door then
    closed every later answer, so cr_2's fix reached no seat. The one-answer
    rule of 2026-08-14 stays: a role says two things to one role in one
    message's refs. So the door speaks at the first answer.

    When the refs carry every ruled criterion, the door refuses that first
    answer while a criterion the relay contests or revises has no landed
    respecify in the session (frame 308, pass 2b, night 159's s382 and
    s398). The refusal quotes the last respecify refusal of the criterion.
    """
    if ctx.role != "terminologist" or not isinstance(refs, list):
        return None
    if _sent_this_session(ctx, "tester", "answer"):
        return None
    relay = api._principal_relay(ctx)
    if relay is None:
        return None
    relay_refs, verdict = relay
    ruled: list[str] = []
    for r in relay_refs:
        if verdict.get(r) not in ("contest", "revise"):
            continue
        # A retired criterion asks for no answer (frame 306, pass 1c).
        if ctx.conn.execute("SELECT 1 FROM criteria WHERE id = ?"
                            + api._live_rows(ctx.conn, "retired_by"),
                            (r,)).fetchone():
            ruled.append(r)
            continue
        # A ruled test asks its criterion in the same one answer, so the
        # Tester rewrites the test (frame 308, review 1, F4).
        test = ctx.conn.execute("SELECT criterion_id FROM tests WHERE id = ?",
                                (r,)).fetchone()
        if test and test["criterion_id"]:
            ruled.append(test["criterion_id"])
    ruled = list(dict.fromkeys(ruled))
    given = [r for r in refs if isinstance(r, str)]
    # A refusal names a call only where the doors admit that call (frame 135).
    # The park door of `_bind_send` refuses an answer on criteria that no
    # change with a commit is built from, so this door then stays silent.
    from .scheduler import park_criterion_relay

    def _parked(ids) -> bool:
        # The batch fact is `api.built_batch`, the one predicate (W10, the
        # review's low p2-1). A retired criterion holds no live change.
        def _live_built(r) -> bool:
            b = api.built_batch(ctx.conn, r, need_commit=True)
            return bool(b and b["status"] != "merged" and ctx.conn.execute(
                "SELECT 1 FROM criteria c WHERE c.id = ?"
                + api._live_rows(ctx.conn, "c.retired_by"), (r,)).fetchone())
        return park_criterion_relay(ctx.conn, getattr(ctx, "trigger", None)) and not any(
            _live_built(r) for r in ids)
    missing = [r for r in ruled if r not in given]
    # The answer carries a criterion by its ref, so the Tester reads the row
    # as it stands. Night 159's s382 and s398 answered while no respecify had
    # landed, and the Tester read the text he had ruled on. The key is the
    # landed write, not the refusal before it (frame 308, review 2, F1 to F3).
    # A "The criterion stands" refusal counts as landed (review 2's fix).
    stands = set(getattr(ctx, "respecify_stands", None) or ())
    # A criterion that this session challenged to the Vision Keeper counts as
    # written. The twin door sends the seat to that challenge, and a second
    # order to rewrite invites a paraphrase twin (frame 329, review 1, F1).
    # Only a twin refusal of the respecify opens the route. A challenge in
    # place of a rewrite lets the Tester read the contested words, as on
    # night 159 (frame 329, review 1b, F5).
    twinned = getattr(ctx, "respecify_twinned", None) or set()
    stands |= {r for m in _sent_this_session(ctx, "vision_keeper", "challenge")
               for r in m.get("body_refs") or ()
               if isinstance(r, str) and r in twinned}
    unwritten = [r for r in relay_refs
                 if verdict.get(r) in ("contest", "revise") and r in ruled
                 and r not in stands
                 and not api.ruling_asks_no_new_words(ctx, r)
                 and not any(w[0] == "criteria" and w[1] == r
                             for w in ctx.writes)]
    # A ruling that drops a criterion's line asks for no rewrite. No op of
    # this mode retires a criterion, and frame 192 owns the drop route. So
    # the refusal names the drop and names no call (frame 308, review 4,
    # point 2, and frame 135).
    dropped = {r: n for r in unwritten
               if (n := api.ruling_drops_line(ctx, r)) is not None}
    # A dropped line needs no answer. The door does not demand it, and it
    # refuses only an answer that carries its old text (frame 308, pass 3c,
    # point 1). The ledger of what was dropped is frame 192's.
    missing = [r for r in missing if r not in dropped]
    unwritten = [r for r in unwritten if r not in dropped]
    dropped = {r: n for r, n in dropped.items() if r in given}
    # A clarify page has no line numbers, so its drop names the row alone.
    drop_said = " ".join(
        (f"The principal's ruling drops {cid}." if n == api.DROPS_THE_ROW
         else f"The principal's ruling drops line {n}, which is {cid}.")
        + f" Your answer "
        f"carries {cid} as it stands now. Do not rewrite {cid}. No call in "
        f"this mode drops a criterion." for cid, n in dropped.items())
    unwritten = [r for r in unwritten if r not in dropped]
    if not missing:
        # The missing-refs door speaks first, so s220's text stays as night
        # 158 showed it.
        if (not unwritten and not dropped) or _parked(ruled):
            return None
        if not unwritten:
            return drop_said
        ids = ", ".join(unwritten)
        said = (getattr(ctx, "respecify_refused", None) or {})
        quoted = " ".join(f"Your last respecify of {cid} was refused with: "
                          f"{said[cid]!r}." for cid in unwritten if cid in said)
        return " ".join(s for s in (
            f"No respecify of {ids} has landed in this session.",
            f"The principal's ruling in the relay is on {ids}.",
            f"Your answer carries {ids} as it stands now.",
            quoted,
            f"Respecify {ids} first with a corrected criteria.respecify call.",
            drop_said,
            "" if dropped else
            "Then answer once with msg.answer_tester, with these refs: "
            f"{[r for r in given if api.ref_resolves(ctx, r)]!r}") if s)
    # A dangling ref in the route meets the dangling guard of `_bind_send`
    # (frame 308, review 1, F1).
    full = [r for r in given if api.ref_resolves(ctx, r)] + missing
    if _parked(full):
        return None
    ids = ", ".join(missing)
    route = (f"Send one msg.answer_tester with every ruled criterion in refs: "
             f"{full!r}")
    said = (f"Your answer leaves out {ids}. The principal's ruling in the "
            f"relay names {ids} too.")
    if dropped:
        # The full answer still carries the dropped line, so the text offers
        # no call (frame 135).
        rewrite = (f" No respecify of {', '.join(unwritten)} has landed in "
                   f"this session. Respecify {', '.join(unwritten)} first with "
                   f"a corrected criteria.respecify call." if unwritten else "")
        return f"{said}{rewrite} {drop_said}"
    if unwritten:
        # The full answer still meets the landed-respecify check, so the
        # text offers no call (frame 135). The seat respecifies first.
        return (f"{said} No respecify of {', '.join(unwritten)} has landed "
                f"in this session. Respecify {', '.join(unwritten)} first "
                f"with a corrected criteria.respecify call. Then {route[0].lower()}"
                f"{route[1:]}")
    return api._offer(ctx, f"{said} {route}", "msg.answer_tester",
                      {"refs": full})


def _note_respecify_refusal(ctx: api.Ctx, cid, why: str) -> None:
    """Keep `why` as the last refusal of the respecify of `cid`, so the
    answer door can quote it (frame 308, pass 2)."""
    if not isinstance(cid, str):
        return
    if getattr(ctx, "respecify_refused", None) is None:
        ctx.respecify_refused = {}
    ctx.respecify_refused[cid] = why


def _respecify_record(ctx: api.Ctx, respecify: Callable) -> Callable:
    """Keep the last refusal of each criterion's respecify on `ctx`, so the
    answer door can quote it (frame 308, pass 2). `ctx.refusals` keeps no
    arguments, so it cannot name the criterion."""
    import functools

    @functools.wraps(respecify)
    def record(*args, **kwargs):
        try:
            return respecify(*args, **kwargs)
        except Exception as exc:
            cid = kwargs.get("id", args[0] if args else None)
            _note_respecify_refusal(ctx, cid, str(exc))
            # "The criterion stands": the ruling asked for no new words, so
            # the criterion counts as landed (frame 308, review 2).
            if getattr(exc, "criterion_stands", False) and isinstance(cid, str):
                if getattr(ctx, "respecify_stands", None) is None:
                    ctx.respecify_stands = set()
                ctx.respecify_stands.add(cid)
            # A twin refusal: the twin door named the challenge as the way
            # out (frame 329, review 1b, F5).
            if getattr(exc, "criterion_twin", None) and isinstance(cid, str):
                if getattr(ctx, "respecify_twinned", None) is None:
                    ctx.respecify_twinned = set()
                ctx.respecify_twinned.add(cid)
            raise

    return record


def _ruling_answer_door(ctx: api.Ctx, label: str, send: Callable) -> Callable:
    """Put `_ruling_answer_refusal` in front of the Terminologist's answer to
    the Tester. `_bind_send` stays as it is (frame 308, point 4)."""
    import functools

    @functools.wraps(send)
    def door(refs, *args, **kwargs):
        said = _ruling_answer_refusal(ctx, refs)
        if said:
            # Logged as `stage` logs a send before its guards: the register
            # subtracts the refused count from the log.
            _CALL_LOG.setdefault(id(ctx), []).append((label, f"refs={refs or []}"))
            raise ValueError(said)
        return send(refs, *args, **kwargs)

    return door


def _escalation_admitted(ctx: api.Ctx, refs) -> bool:
    """
    True when `msg.escalate_architect` on these refs passes the two repeat
    doors of `_bind_send`, the duplicate guard and the same-refs door.

    A refusal names a call only where the doors admit that call (frame 135,
    `plans/operating-facts.md`, rulings on briefs and doors). For the
    Developer, any escalation on the same refs, open or closed, refuses.
    A mode that lacks the escalation admits none, so its three callers name
    no escalation there (the review of frame 349's pass 1, finding 1).
    """
    if not api._holds(ctx, "msg.escalate_architect"):
        return False
    if _sent_this_session(ctx, "architect", "escalate"):
        return False
    return _same_refs_refusal(ctx, "architect", "escalate", refs) is None


def _base_quote(output: str) -> str:
    """The line of a red base run that says why: its error line (fact F5),
    else its last line."""
    from .harness import error_line

    lines = [ln.strip() for ln in (output or "").splitlines() if ln.strip()]
    said = error_line(output) or (lines[-1] if lines else "no output")
    return said[:200].rstrip(".")


def project_tests_fact(ctx: api.Ctx, ids: list[str], *,
                       offer: bool = True) -> str | None:
    """
    What the batch's base run says about the project's red tests `ids`, or
    None when the base run passed every one and no newest run in this
    batch passed. On None the caller says its own "passed before this
    batch" sentence.

    Frame 207, night 140: the doors said "passed before this batch" from a
    constant, and `inh_f3b0c3db` was red at bg_2's base. Now the sentence
    comes from the record `harness.record_base_run` wrote. A test that is
    red at the base is not the Developer's to fix. The escalation is the
    admitted call for it, so the text names that call exactly.
    """
    from . import harness

    base = harness.base_run(ctx.conn, ctx.batch_id) if ctx.batch_id else None
    rows = base or {}
    ids = list(dict.fromkeys(ids))
    # Fact F4, night 170: this text told s201 to restore inh_fe7f4bfc, and
    # that test passed 7 of 7 runs of b_3. A test green on its newest run
    # in this batch is broken by no change, so the text says so. The run
    # must be at the batch's head. A head that no harness ran is not known
    # to be green (the F4 review, low 2).
    green = [i for i in ids if ctx.batch_id and ctx.conn.execute(
        "SELECT 1 FROM latest_runs r JOIN batches b ON b.id = r.batch_id "
        "WHERE r.batch_id = ? AND r.test_id = ? AND r.result = 'pass' "
        "AND r.commit_sha = b.head_commit", (ctx.batch_id, i)).fetchone()]
    ids = [i for i in ids if i not in green]
    red = [i for i in ids if isinstance(rows.get(i), dict)
           and rows[i].get("result") in ("fail", "error")]
    passed = [i for i in ids if isinstance(rows.get(i), dict)
              and rows[i].get("result") == "pass"]
    unknown = [i for i in ids if i not in red and i not in passed]
    if not red and not unknown and not green:
        return None
    parts = []
    if green:
        parts.append(f"{', '.join(green)} passed on {'its' if len(green) == 1 else 'their'} "
                     f"newest run in this batch, so your change broke nothing "
                     f"there. A challenge has no side on the project's own test")
    if red:
        quote = _base_quote(rows[red[0]].get("output", ""))
        parts.append(
            f"the base run at this batch's start found {', '.join(red)} red "
            f"too. The base run said: {quote}. Your diff did not break "
            f"{'it' if len(red) == 1 else 'them'}, and the fix is not yours")
        # Frame 135's law: `_escalation_admitted` asks the mode, so
        # developer/answer, which lacks the escalation, gets the end.
        if _escalation_admitted(ctx, red):
            said = f"Send msg.escalate_architect(refs={red!r})"
            if offer:
                api._offer(ctx, said, "msg.escalate_architect",
                           {"refs": red})
            parts.append(said)
        elif api._holds(ctx, "msg.escalate_architect"):
            parts.append("You escalated these refs already. End the "
                         "session with no call")
        else:
            parts.append("End the session with no call")
    if passed:
        parts.append(f"{', '.join(passed)} passed before this batch. Read "
                     f"code.diff and restore what your change broke")
    if unknown:
        # A push can hold 34 project rows (night 113), so a long list is a count.
        named = (', '.join(unknown) if len(unknown) <= 3
                 else f"{len(unknown)} of these tests")
        parts.append(f"no base run of {named} is on record. A "
                     f"challenge has no side there. Read code.diff and find "
                     f"what your change broke")
    return ". ".join(p[0].upper() + p[1:] if n else p
                     for n, p in enumerate(parts))


def _waits_refusal(verb: str, recipient: str, waiting_id: str,
                   ctx: api.Ctx | None = None, refs=None) -> str:
    """The refusal of a Developer's second copy of a message still open.

    Frame 200: after a challenge in this session, `code.write` and
    `code.commit` refuse, so the step is `END_STEP` and not the change.
    """
    if ctx is not None and _sent_this_session(ctx, "tester", "challenge"):
        once = _unique_refs(refs)
        return _Ending(
            f"you sent {verb} to {recipient} on exactly these refs already "
            f"({waiting_id}) and it waits for an answer. The answer comes "
            f"to a later wake. {END_STEP} {_end_form(ctx, once)}")
    way = ("write the change that makes it pass"
           if verb == "challenge" else
           "write the change that makes it pass, and commit it")
    return (f"you sent {verb} to {recipient} on exactly these refs "
            f"already ({waiting_id}) and it waits for an answer. "
            f"A second copy is the same question twice, and the "
            f"answer comes to a later wake. Until then: code.source "
            f"the code the test calls and {way}, or end the session "
            f"with no call")


def _moved_since_woken(conn: sqlite3.Connection, msg_id: str, refs) -> bool:
    """
    True when a row of `refs` has a receipt from a session at or after the
    first session that `msg_id` woke. False when `msg_id` woke no session.

    No row stores the version that a challenge saw. The receipt is the
    smallest record that exists, so the door needs no new column (frame
    132's design, section 3.1). A repaired criterion is a new version of the
    conflict too. Only the two sides of the conflict count: the review of
    4968ea7 (2026-10-05) reopened the door with a `batches` receipt whose
    `row_id` was the test's id.
    """
    return _receipt_since_woken(conn, msg_id, refs, ("tests", "criteria"))


def _receipt_since_woken(conn: sqlite3.Connection, msg_id: str, refs,
                         tables: tuple) -> bool:
    """
    True when a row of `refs` has a receipt of one of `tables` from a session
    at or after the first session that `msg_id` woke.
    """
    ids = [r for r in refs or [] if isinstance(r, str)]
    if not ids or not tables:
        return False
    marks = ",".join("?" * len(ids))
    names = ",".join("?" * len(tables))
    return conn.execute(
        f"SELECT 1 FROM receipts r JOIN sessions s ON s.id = r.session_id "
        f"WHERE r.table_name IN ({names}) "
        f"AND r.row_id IN ({marks}) AND s.seq >= ("
        f"  SELECT MIN(w.seq) FROM sessions w WHERE w.trigger_msg = ?) "
        f"LIMIT 1", (*tables, *ids, msg_id)).fetchone() is not None


#: The step of a refusal that tells the session to stop. A refusal that ends on
#: it is raised as `api.EndRefusal`, so the runner can read the step from the
#: refusal's class and not from its words (frame 153).
END_STEP = "End the session with no call."

#: The reply that takes `END_STEP`, which the refusal names after the step
#: (frame 165). `{on}` names the refused challenge's tests.
END_FORM = ("Your whole next reply is this one line, and no TOOL: line: "
            "Nothing more is owed{on} in this session.")


class _Ending(str):
    """A refusal's text whose step is `END_STEP`, followed by `END_FORM`. The
    class carries the fact to the place that raises it."""


def _code_step(ctx: api.Ctx) -> str:
    """
    The step toward the code, or the end of the session when the session
    cannot write code.

    The review of 4968ea7 (2026-10-05): 7 of the 141 refused challenges of
    nights 113 to 123 came from mode `exhausted`, where `code.write` answers
    `NotInWorkingSet`. A context that `build` did not make holds no working
    set, and it keeps the step toward the code.

    law 7: every cap is a ruling, declared in config; the door breaks this law, see frame287-door-laws.md, Contradicts
    """
    working = getattr(ctx, "working_set", None)
    if working is not None and "code.write" not in working:
        return END_STEP
    # Frame 200: after a challenge in this session, `code.write` and
    # `code.commit` refuse, so a step toward the code contradicts them.
    if _sent_this_session(ctx, "tester", "challenge"):
        return END_STEP
    return CODE_STEP


#: The step toward the code. Frame 278: `_escalation_or_step` reads it by
#: value, to offer the Architect's decision in its place.
CODE_STEP = "Make one real change to the code the test calls."


# law 7: every cap is a ruling, declared in config; the door breaks this law, see frame287-door-laws.md, Contradicts
#: How many challenges of the Developer may land on one body of a criterion's
#: tests, counted across its tests' ids and across the other refs.
#: A moved test deletes its own runs and lifts the batch's tick quarantine
#: (`db.py:579-610`), so on a batch of one test the attempt cap starts again
#: at each move (the review of 4968ea7, 2026-10-05). Nights 113 to 124 hold at
#: most two landed challenges per criterion, and no green criterion had more
#: than one. The floor is 3 (ruled: the judging session, 2026-10-05, frame
#: 132's pass 2).
LANDED_CHALLENGES = 3

#: How many challenges of the Developer may land on one criterion across all
#: bodies of its tests. A reworded body deletes the test's runs and lifts the
#: batch's quarantine (`db.py:606-635`), so it restarts the attempt cap. The
#: count per body then restarts too, and the step budget of the night was the
#: only bound (the review of bef80289, finding 3: 8 of 8 landed).
LANDED_CHALLENGES_CEILING = 2 * LANDED_CHALLENGES


def _test_is_red(conn: sqlite3.Connection, refs) -> bool:
    """True when a test of `refs` has its newest run at fail or error."""
    for ref in refs or []:
        row = conn.execute(
            "SELECT tr.result FROM latest_runs tr JOIN tests t ON t.id = tr.test_id "
            # The test's own batch only: an inherited test keeps its id
            # across batches (frame 210).
            "WHERE tr.test_id = ? AND tr.batch_id = t.batch_id", (ref,)).fetchone()
        if row is not None and row["result"] in ("fail", "error"):
            return True
    return False


def _unique_refs(refs) -> list:
    """The refs in their order, each once."""
    try:
        return list(dict.fromkeys(refs or []))
    except TypeError:
        return list(refs or [])


def _criteria_of_tests(conn: sqlite3.Connection) -> dict:
    """Each test id, with its criterion id or None."""
    return {r["id"]: r["criterion_id"]
            for r in conn.execute("SELECT id, criterion_id FROM tests")}


def _criteria_named(conn: sqlite3.Connection, refs, test_crit: dict) -> set:
    """The criteria that `refs` name, directly or through a test."""
    named = {r for r in _unique_refs(refs) if isinstance(r, str)
             and conn.execute("SELECT 1 FROM criteria WHERE id = ?",
                              (r,)).fetchone()}
    named |= {test_crit[r] for r in _unique_refs(refs)
              if isinstance(r, str) and test_crit.get(r)}
    return named


def _cap_keys(conn: sqlite3.Connection, refs, test_crit: dict) -> list:
    """
    What the cap counts for `refs`, in the order of the refs: each criterion
    that the refs name, directly or through a test, as `("criterion", id)`.
    A test with no criterion counts for itself, as `("test", id)`.
    """
    keys = []
    for r in _unique_refs(refs):
        if not isinstance(r, str):
            continue
        if r in test_crit:
            key = (("criterion", test_crit[r]) if test_crit[r]
                   else ("test", r))
        elif conn.execute("SELECT 1 FROM criteria WHERE id = ?", (r,)).fetchone():
            key = ("criterion", r)
        else:
            continue
        if key not in keys:
            keys.append(key)
    return keys


def _challenges_on(conn: sqlite3.Connection, key: tuple,
                   test_crit: dict) -> list:
    """
    The Developer's challenges to the Tester that count for `key`, whatever
    their other refs, newest first. Each item is the row's id and its refs.
    A challenge counts for a criterion when its refs hold the criterion or
    a test of the criterion.
    """
    import json as _json
    kind, ident = key
    out = []
    for row in conn.execute(
            "SELECT id, cause_id, body_refs FROM messages "
            "WHERE from_role = 'developer' AND to_role = 'tester' "
            "AND verb = 'challenge' ORDER BY seq DESC"):
        try:
            have = _json.loads(row["body_refs"] or "[]")
        except (TypeError, ValueError):
            continue
        if not isinstance(have, list):
            continue
        strs = [r for r in have if isinstance(r, str)]
        # Design 200 change 4 (ruled: Roman, 2026-10-11 06:30): a challenge
        # that carries the Architect's decision row is the row's route to the
        # Tester, and it does not count against the cap. The Developer's own
        # reason row is no such route (frame 200, pass 5).
        if _carries_decision(conn, strs, row["cause_id"], "developer"):
            continue
        if ident in strs or (kind == "criterion" and any(
                test_crit.get(r) == ident for r in strs)):
            out.append((row["id"], have))
    return out


def _counted_tests(refs, key: tuple, test_crit: dict) -> list:
    """
    The tests whose body the cap's count for `key` is about: the tests of
    the criterion that `refs` name, else every test of the criterion. A key
    of one test is that test.
    """
    kind, ident = key
    if kind != "criterion":
        return [ident]
    named = [r for r in _unique_refs(refs)
             if isinstance(r, str) and test_crit.get(r) == ident]
    return named or [t for t, c in test_crit.items() if c == ident]


#: The shortest quoted line that can tie a challenge to one body. A shorter
#: fragment, such as `assert result`, holds in any version of a test (the
#: review of bef80289, finding 5).
QUOTED_LINE_MIN = 20


def _flat(text: str | None) -> str:
    """`text` with each run of whitespace made one space."""
    return " ".join((text or "").split())


def _sender_prompt(conn: sqlite3.Connection, msg_id: str) -> str | None:
    """
    The first prompt of the Developer session that sent `msg_id`, flat and
    with its JSON escapes undone, or None when no turn is on file.

    No row stores a test's old body (frame 200, pass 4b). The prompt shows
    the failing tests as the sender saw them. A message stores no session,
    and one session commits at a time, so the sender is the last Developer
    session before the first session that `msg_id` woke. Only the first
    turn is read: a later turn can echo the challenge's own quotes.
    """
    woke = conn.execute("SELECT MIN(seq) AS s FROM sessions WHERE trigger_msg = ?",
                        (msg_id,)).fetchone()
    if woke is None or woke["s"] is None:
        return None
    sender = conn.execute(
        "SELECT id FROM sessions WHERE role = 'developer' AND seq < ? "
        "ORDER BY seq DESC LIMIT 1", (woke["s"],)).fetchone()
    if sender is None:
        return None
    turn = conn.execute("SELECT user FROM turns WHERE session_id = ? "
                        "ORDER BY seq LIMIT 1", (sender["id"],)).fetchone()
    if turn is None:
        return None
    # Night 142's prompts show a body inside a JSON string: `\"` and `\n`.
    text = (turn["user"].replace("\\n", "\n").replace('\\"', '"')
            .replace("\\'", "'").replace("\\\\", "\\"))
    return _flat(text)


def _quoted_body_gone(conn: sqlite3.Connection, msg_id: str, tests) -> bool:
    """
    True when the challenge `msg_id` is about a body that no test of `tests`
    holds now. Three facts must hold:

    - a `tests` receipt on `tests` landed after the prior's wake;
    - a line that the prior quoted stood exactly in the body that the
      sender's prompt showed;
    - no test of `tests` holds that line now.

    The challenge door joins the quotes with " ... " into `body_text`. A
    test holds a line when the whole line reads its body by `_quote_reads`
    (F18). A 12-character
    window is not used, because it matches `result.output` across any two
    versions of night 142's test. A quote that matched only by such a
    window is not exact, so it keeps counting (the review of
    bef80289, finding 4). A line under QUOTED_LINE_MIN or a line of the
    criterion's words ties the prior to no body. When no line is tied, the
    prior keeps counting.
    """
    if not _receipt_since_woken(conn, msg_id, tests, ("tests",)):
        return False
    row = conn.execute("SELECT body_text FROM messages WHERE id = ?",
                       (msg_id,)).fetchone()
    crit = " ".join(_flat(r["text"]) for r in conn.execute(
        "SELECT c.text FROM criteria c JOIN tests t ON t.criterion_id = c.id "
        f"WHERE t.id IN ({','.join('?' * len(tests))})", tuple(tests)))
    # Each part keeps its line breaks for the body compare. `_quote_reads`
    # cuts a comment per line, and a flat part is one line, so the cut
    # dropped the code after the first `#` (review of F18 pass 1, finding 1,
    # nights 161 m100 and 168 m38).
    parts = [(_flat(part).strip("'\"` "), part.strip("'\"` "))
             for part in ((row["body_text"] if row else None) or "").split(" ... ")]
    parts = [(line, part) for line, part in parts
             if len(line) >= QUOTED_LINE_MIN and line not in crit]
    if not parts:
        return False
    seen = _sender_prompt(conn, msg_id)
    parts = [(line, part) for line, part in parts
             if seen is not None and line in seen]
    if not parts:
        return False
    # F18: the live body holds a line when `_quote_reads` says so, the one
    # reader of a quote against a row (ruled: Roman, 2026-08-26).
    for test in tests:
        got = conn.execute("SELECT body FROM tests WHERE id = ?",
                           (test,)).fetchone()
        body = (got["body"] if got else None) or ""
        if any(_quote_reads(part, body, "tests", floor=QUOTED_LINE_MIN)
               for _line, part in parts):
            return False
    return True


def _holds_decision(conn: sqlite3.Connection, refs,
                    exclude_author: str | None = None) -> bool:
    """True when `refs` name a `decisions` row. A row by `exclude_author`
    does not count."""
    # Fact F23: the author comes from the one reader.
    return any(isinstance(r, str) and conn.execute(
        "SELECT 1 FROM decisions WHERE id = ?", (r,)).fetchone()
        and journal_author(conn, "decisions", r) != exclude_author
        for r in refs or [])


def _without_own_reasons(conn: sqlite3.Connection, refs, role: str) -> list:
    """
    `refs` without the `decisions` rows that `role` wrote.

    Frame 200, pass 5, fix 1: the binder adds the sender's reason row to the
    stored refs after the doors ran. The same-refs door compares the refs
    without that row, so a reasoned prior still matches the seat's refs.
    """
    return [r for r in refs or [] if not (
        isinstance(r, str) and journal_author(conn, "decisions", r) == role)]


# law 2: the reasoning is reached by following a ref
#: The reason slot that every hint writes for `msg.challenge_tester`. The
#: seat fills it, because mechanics cannot write the seat's judgement (frame
#: 200, pass 5, fix 2). Pass 5g adds the test, because night 144's reasons
#: named a function that two tests call, and the Tester fixed the sibling.
REASON_SLOT = ('reason="<the error, the test, the line, and the call that '
               'takes the argument>"')

# The slot before pass 5g. A run database of night 144 still holds hints
# with it, so a seat can copy it as its reason (review 5g, finding 2).
_REASON_SLOTS_OLD = ("the error, the line, and the call that takes the "
                     "argument",)

#: The fewest words a reason may have. A shorter one names no call that the
#: test must make (frame 200, pass 5, section 3.1).
REASON_WORDS_MIN = 6

#: The most characters of a reason the row keeps, as `_THREAD_ANSWER_CHARS`
#: keeps of an answer's words.
REASON_CHARS = 600

#: How many words of a reason's first sentence the verdict door reads. Past
#: the head, "passes" is part of a fact, as in "so it never passes".
REASON_HEAD_WORDS = 4

# A reason whose head is a verdict on the test or the criterion (frame 200,
# pass 5b, item 4). "passes" with an object is a fact, as in "the test
# passes package_name to invoke" (review 5b, finding 1). Pass 5g refuses
# "passes for me", "with the current code", "in CI", "cleanly", "fine" and
# "green" (review 5e, low 3). Pass 5h matches the tails and not the bare
# prepositions, because "passes in the args list" is a fact (review 5g,
# finding 3). The door reads the reason in lower case.
_REASON_VERDICT = re.compile(
    r"\bpasses(?=\s*(?:$|[.,;!?]|on\b|as\b|already\b|now\b|today\b"
    r"|for me\b|with the current code\b|in ci\b|cleanly\b|fine\b|green\b))"
    r"|\bis (?:met|correct)\b")

# What every reason refusal says. It is the one part of a challenge that the
# Tester cannot read in the test (frame 200, pass 5, section 3.1). Pass 5b
# asks for the fact and not the fix, because the probe's Developer looped on
# the fix.
_REASON_SAID = ("reason= names the test by its id, the error it got and the "
                "line of the test that raises it. It is the one part of a "
                "challenge the Tester cannot read in the test.")


def _takes_reason(sender: str, recipient: str, verb: str) -> str:
    """The table where the edge `sender` to `recipient` stores a reason, or
    "". The edge declares it, so no door knows a role name."""
    return next((e.reason_row for e in graph_mod.load().of_type("messages")
                 if e.s == sender and e.t == recipient and e.v == verb
                 and e.reason_row), "")


def _reason_problem(conn: sqlite3.Connection, reason, quotes: str,
                    refs) -> str | None:
    """
    The first fact that makes `reason` no reason, or None.

    The doors, in order: no reason, the slot text sent back, fewer than
    REASON_WORDS_MIN words, and a copy of the quotes or of the criterion.
    The quotes already travel, so a copy tells the Tester nothing new.
    """
    words = (reason or "").split() if isinstance(reason, str) else []
    if not words:
        return "a challenge to the tester carries reason=, and yours has none."
    flat = " ".join(words).lower()
    slots = (REASON_SLOT.split("=", 1)[1].strip('"<>').lower(),
             *_REASON_SLOTS_OLD)
    if flat.removeprefix("reason=").strip("\"'<> ") in slots:
        return ("reason= is still the slot text. Name the error the test got, "
                "the test's id, and the line of the test that raises it.")
    if len(words) < REASON_WORDS_MIN:
        return (f"a challenge to the tester carries a reason= of "
                f"{REASON_WORDS_MIN} words or more, and yours has {len(words)}.")
    # Frame 200, pass 5b: a verdict is no fact. The probe's Developer argued
    # the test right or wrong in a loop, and never named the error.
    # The lookahead reads the whole sentence, so a head cut after "passes"
    # does not hide its object.
    first = re.split(r"[.!?;:]\s", flat, maxsplit=1)[0]
    said = _REASON_VERDICT.search(first)
    if said and len(first[:said.start()].split()) < REASON_HEAD_WORDS:
        return ("reason= says the test passes or the criterion is met. Name "
                "the error the test got, the test's id, and the line of the "
                "test that raises it.")
    bare = flat.strip("\"'` .")
    crit = " ".join(_flat(r["text"]).lower() for r in conn.execute(
        "SELECT text FROM criteria WHERE id IN "
        f"({','.join('?' * len(refs or []))})",
        tuple(r for r in refs or [] if isinstance(r, str)))) if refs else ""
    if bare in _flat(quotes).lower() or (crit and bare in crit):
        return ("reason= copies the quotes or the criterion. The quotes "
                "already travel, and reason= names the error the test got, "
                "the test's id, and the line of the test that raises it.")
    return None


def _reason_offered(conn: sqlite3.Connection, reason, quotes: str, refs):
    """The reason an offer carries: the seat's own words when the reason
    door admits them, else `api.INVENT`, the slot the seat fills. Fix 2.3
    of frame 200's pass 5: the offer is then the exact call."""
    if _reason_problem(conn, reason, quotes, refs) is None:
        return reason
    return api.INVENT


def _reason_arg(conn: sqlite3.Connection, reason, quotes: str, refs) -> str:
    """The reason as a hint writes it: the seat's own words when the reason
    door admits them, else REASON_SLOT."""
    got = _reason_offered(conn, reason, quotes, refs)
    return REASON_SLOT if got is api.INVENT else f"reason={got!r}"


def _stage_reason(ctx: api.Ctx, table: str, refs, quotes: str,
                  reason, spans: list | None = None) -> tuple[str, str]:
    """
    Stage the reason of a challenge as the sender's own row of `table`, and
    return its id and a note for the sender, which is "" unless the reason
    was cut.

    Frame 200, pass 5: law 2 keeps words off a message, and law 2 says the
    reasoning is written into the decision record by whoever decided. The id
    derives from the reason and its two refs (law 14), so the same reason on
    the same refs is one row. Raise the refusal when the reason door refuses,
    or when the id is another author's row.
    """
    import hashlib

    from .runner import cut_note

    sides = _challenge_sides(ctx, refs) or [r for r in _unique_refs(refs)
                                            if isinstance(r, str)][:2]
    problem = _reason_problem(ctx.conn, reason, quotes, sides)
    if problem is not None:
        if problem.startswith("a challenge to the tester carries"):
            problem += " " + _REASON_SAID
        once = _unique_refs(refs)
        # Frame 135's law: the refusal names a call that every door admits
        # once the seat fills the slot.
        raise ValueError(api._offer(
            ctx, f"{problem} Send msg.challenge_tester(refs={once}, "
            f"{REASON_SLOT}) with the same quotes.",
            "msg.challenge_tester",
            # The quotes as sent: the joined text is one quote now, and the
            # quote door refuses it (frame 328, review 1, finding 5).
            {"refs": once, "quotes": spans if spans else quotes,
             "reason": api.INVENT}))
    text, note = " ".join(reason.split()), ""
    if len(text) > REASON_CHARS:
        note = cut_note("your reason", len(text) - REASON_CHARS, len(text),
                        "characters", f"The Tester reads the first "
                        f"{REASON_CHARS} characters in the row.")
        text = text[:REASON_CHARS] + chr(10) + cut_note(
            "the reason", len(text) - REASON_CHARS, len(text), "characters",
            "Nothing returns the rest. Act on what is shown.")
    rid = "d_" + hashlib.sha256(
        f"{text}|{'|'.join(sides)}".encode()).hexdigest()[:10]
    # Frame 219's shape: a seat that writes under another author's id
    # overwrites that author's record. The door reads the commit's rule
    # (fact F23), so the seat hears the refusal before the commit.
    row = {"author": ctx.role, "text": text, "refs": json.dumps(sides),
           "supersedes": None, "resolves_ledger": None}
    refused = author_refusal(ctx.conn, table, rid, ctx.role, row)
    if refused:
        # The id hashes the words, so the text names the reason's id. The
        # remedy then reads as the way to a new id (review of pass 1, 8).
        raise ValueError(f"the reason's id {refused} Write the reason in "
                         f"your own words.")
    if not any(w[0] == table and w[1] == rid for w in ctx.writes):
        ctx.writes.append((table, rid, row))
    return rid, note


def _carries_decision(conn: sqlite3.Connection, refs, cause: str | None,
                      exclude_author: str | None = None) -> bool:
    """
    True when `refs` hold a decision row that the challenge carries: a ref of
    the answer `cause`, or a decision that cites a test of `refs`.

    The ruling of 06:30 exempts "a challenge whose refs add a decision row".
    Any decision id can reach the Developer through `rulings_line`, so an
    unrelated one does not pass the cap (the review of 8d090e2e, finding 7).
    A row by `exclude_author`, the sender, is its own reason and not a route
    of another seat's row. It does not pass the cap (frame 200, pass 5).
    """
    import json as _json

    def _ids(raw) -> set:
        try:
            got = _json.loads(raw or "[]")
        except (TypeError, ValueError):
            return set()
        return {r for r in got if isinstance(r, str)} if isinstance(got, list) else set()

    strs = [r for r in refs or [] if isinstance(r, str)]
    carried = set()
    if cause:
        row = conn.execute("SELECT body_refs FROM messages WHERE id = ?",
                           (cause,)).fetchone()
        carried = _ids(row["body_refs"]) if row else set()
    tests = {r for r in strs if conn.execute(
        "SELECT 1 FROM tests WHERE id = ?", (r,)).fetchone()}
    for r in strs:
        hit = conn.execute("SELECT refs FROM decisions WHERE id = ? "
                           "AND author IS NOT ?", (r, exclude_author)).fetchone()
        if hit and (r in carried or tests & _ids(hit["refs"])):
            return True
    return False


def architect_decision_on(conn: sqlite3.Connection, role: str,
                          tests) -> tuple | None:
    """
    The Architect's decision row on a red test, as the thread of `role`
    holds it: `(decision id, test id, criterion id)`, or None.

    The thread is the challenges and escalations of `role` that name the test,
    and the answers to them. A decision counts when an answer names it, its
    author is the Architect, and its refs name the test. Frame 278, night 153:
    m144 named `dec_1_tst_ver_opt_show_py`, and the later wakes never saw it.
    The key is the table, the author and the test ref, never the words.

    law 3: a message routes to the writer of the artefact holding the answer
    """
    import json as _json

    def _ids(raw) -> list:
        try:
            got = _json.loads(raw or "[]")
        except (TypeError, ValueError):
            return []
        return [r for r in got if isinstance(r, str)] if isinstance(got, list) else []

    for test in [t for t in tests or [] if isinstance(t, str)]:
        found = conn.execute(
            "SELECT m.body_refs AS asked, a.body_refs AS answered FROM messages m "
            "JOIN messages a ON a.cause_id = m.id AND a.verb = 'answer' "
            "WHERE m.from_role = ? AND m.verb IN ('challenge', 'escalate') "
            "ORDER BY a.seq DESC", (role,)).fetchall()
        for row in found:
            if test not in _ids(row["asked"]):
                continue
            for ref in _ids(row["answered"]):
                hit = conn.execute(
                    "SELECT refs FROM decisions WHERE id = ? AND author = "
                    "'architect'", (ref,)).fetchone()
                if hit and test in _ids(hit["refs"]):
                    crit = conn.execute(
                        "SELECT criterion_id FROM tests WHERE id = ?",
                        (test,)).fetchone()
                    return ref, test, crit["criterion_id"] if crit else None
    return None


def decision_challenge_call(found: tuple, role: str) -> tuple[str, dict]:
    """The challenge that carries the Architect's decision to the Tester: the
    call as a hint writes it, and its arguments. Roman ruled the route on
    2026-10-11 06:30, so the cap does not count a decision ref."""
    dec, test, crit = found
    refs = [r for r in (crit, test, dec) if r]
    args: dict = {"refs": refs}
    slot = ""
    if _takes_reason(role, "tester", "challenge"):
        args["reason"] = api.INVENT
        slot = ", " + REASON_SLOT
    return f"msg.challenge_tester(refs={refs}{slot})", args


#: True while `decision_step` asks the same-refs door. The door's refusal
#: can call `decision_step` again, and the nested ask must not recurse.
_ASKING_DOOR = False


def _decision_challenge_admitted(ctx: api.Ctx, refs: list) -> bool:
    """True when the same-refs door admits the challenge on `refs`. The ask
    records no offer and no fact, because the step decides what it offers.
    Review 3 of frame 278: a `row` fact from `_end_form` stayed behind, and
    `_ON_REFUSAL` could fire on a refusal that had no facts."""
    global _ASKING_DOOR
    offers = getattr(ctx, "offers", None)
    kept = len(offers) if offers is not None else 0
    facts = getattr(ctx, "facts", None)
    kept_facts = len(facts) if facts is not None else 0
    _ASKING_DOOR = True
    try:
        return _same_refs_refusal(ctx, "tester", "challenge", refs) is None
    finally:
        _ASKING_DOOR = False
        if offers is not None:
            del offers[kept:]
        if facts is not None:
            del facts[kept_facts:]


def decision_step(ctx: api.Ctx, tests) -> tuple[str, dict] | None:
    """
    The step that offers the challenge with the Architect's decision: the
    sentence and the call's arguments, or None.

    Frame 135's law: a refusal names only a call that the doors admit. Review
    1 of frame 278 found the answered challenge offered again, and review 2
    found the open one offered again. So the step asks the door itself.
    """
    if _ASKING_DOOR:
        return None
    found = architect_decision_on(ctx.conn, ctx.role, tests)
    if not found:
        return None
    call, args = decision_challenge_call(found, ctx.role)
    if not _decision_challenge_admitted(ctx, args["refs"]):
        return None
    return (f"The Architect's decision {found[0]} is about the test "
            f"{found[1]}. Send {call}.", args)


def _challenge_cap_refusal(ctx: api.Ctx, rows: list, refs) -> str | None:
    """
    The cap on the Developer's landed challenges on one criterion. Return the
    refusal, or None below the cap. It runs only where the door would admit,
    so the other refusals keep their sentences.

    The review of 4de1555 (2026-10-05): a count per test id let a Tester that
    stored a new test id each round reopen the count, and one criterion
    paired with each test of the batch got 3 per test. So the cap counts per
    criterion, whatever the test ids and the other refs. A challenge is
    refused when any criterion that it names is at the cap. A test with no
    criterion counts for itself. Refs that name neither keep the count of
    the same refs.

    Frame 200, night 142 (2026-10-12): the cap counted m331 to m333, which
    quoted an assertion that version 6 no longer held, and refused the
    challenge on version 6. A landed challenge is a claim about the body it
    quoted. So a prior counts out only when a `tests` receipt on a test of
    the criterion landed after its wake, its quoted line stood exactly in
    the body its sender saw, and no test of the criterion holds that line
    now (`_quoted_body_gone`). A prior with no words keeps counting. The
    chains of the reviews of 4968ea7 and 4de1555 keep the quoted line, so
    they stay at the cap. Across all bodies, LANDED_CHALLENGES_CEILING
    landed challenges on a criterion end the count, and the step is the
    escalation.

    law 7: every cap is a ruling, declared in config; the door breaks this law, see frame287-door-laws.md, Contradicts
    """
    # Design 200 change 4 (ruled: Roman, 2026-10-11 06:30): the Architect's
    # decision row reaches the Tester through this challenge. The cap does
    # not stop it, and the graph gains no edge. The sender's own reason row
    # does not lift the cap (frame 200, pass 5).
    if _carries_decision(ctx.conn, refs, getattr(ctx, "trigger", None),
                         ctx.role):
        return None
    # The stored refs hold the sender's reason row, and the seat's refs do
    # not, so both sides drop it (frame 200, pass 5, fix 1).
    try:
        own = _refs_key(_without_own_reasons(ctx.conn, refs, ctx.role),
                        as_set=True)
    except TypeError:
        own = None
    test_crit = _criteria_of_tests(ctx.conn)
    keys = _cap_keys(ctx.conn, refs, test_crit)
    key, priors, tests = None, [(r["id"], None) for r in rows], []
    ceiling = False
    for k in keys:
        on = _counted_tests(refs, k, test_crit)
        landed = _challenges_on(ctx.conn, k, test_crit)
        if len(landed) >= LANDED_CHALLENGES_CEILING:
            key, priors, tests, ceiling = k, landed, on, True
            break
        # A prior on another test of the criterion is read against that
        # test's body too (the review of bef80289, finding 1).
        every = ([t for t, c in test_crit.items() if c == k[1]]
                 if k[0] == "criterion" else [k[1]])
        counted = [(mid, have) for mid, have in landed
                   if not _quoted_body_gone(ctx.conn, mid, every)]
        if len(counted) >= LANDED_CHALLENGES:
            key, priors, tests = k, counted, on
            break
    if key is None and (keys or len(priors) < LANDED_CHALLENGES):
        return None
    ids = ", ".join(mid for mid, _ in reversed(priors))
    exact = all(have is None or _refs_key(
        _without_own_reasons(ctx.conn, have, ctx.role), as_set=True) == own
        for _, have in priors)
    if exact:
        where = "on exactly these refs"
    elif key[0] == "criterion":
        where = f"on {key[1]} or a test of {key[1]}"
    else:
        where = f"with {key[1]} in the refs"
    fact = (f"you sent challenge to tester {where} "
            f"{len(priors)} times already ({ids})")
    if ceiling:
        # The Tester changed the body each round, so a change to the code
        # is not the step (the review of bef80289, finding 3).
        return _escalation_or_step(ctx, refs, fact + ".", END_STEP)
    # The sentence says only what the rows hold (the reviews of b2ed55b and
    # 4de1555): the test changed only on a `tests` receipt on a test that
    # this call reads, and the criterion changed only on a criteria receipt
    # on the counted criterion. A counted prior with a `tests` receipt after
    # it still holds its quoted line, or quoted nothing (frame 200, night
    # 142). A chain that the cap stops moved a row at least once, so the
    # short form is a guard.
    criteria = [key[1]] if key and key[0] == "criterion" else []
    test_changed = any(
        _receipt_since_woken(ctx.conn, mid, tests, ("tests",))
        for mid, _ in priors)
    criterion_changed = any(
        _receipt_since_woken(ctx.conn, mid, criteria, ("criteria",))
        for mid, _ in priors)
    red = _test_is_red(ctx.conn, tests)
    step = _code_step(ctx)
    if test_changed and red:
        fact += ", and the test changed and is still red."
        # The Tester kept the disputed line. A change to the code is the
        # step only while another test of the batch is red (the review of
        # bef80289, finding 7).
        if not _other_test_red(ctx.conn, tests):
            step = END_STEP
    elif criterion_changed and red:
        fact += ", and the criterion changed and the test is still red."
    else:
        fact += "."
    return _escalation_or_step(ctx, refs, fact, step)


def _other_test_red(conn: sqlite3.Connection, tests) -> bool:
    """
    True when a test outside `tests` has its newest run in the batch of
    `tests` at fail or error.
    """
    # Fact F4: the newest run per test, not the newest attempt. A test that
    # the newest attempt did not run keeps the red of its own newest run.
    ids = [t for t in tests or [] if isinstance(t, str)]
    if not ids:
        return False
    marks = ",".join("?" * len(ids))
    return conn.execute(
        f"SELECT 1 FROM latest_runs r WHERE r.batch_id IN ("
        f"  SELECT batch_id FROM tests WHERE id IN ({marks})) "
        f"AND r.result IN ('fail', 'error') "
        f"AND r.test_id NOT IN ({marks}) LIMIT 1",
        (*ids, *ids)).fetchone() is not None


def _escalation_or_step(ctx: api.Ctx, refs, fact: str, step: str) -> str:
    """
    The refusal's step: the escalation when the doors admit it, recorded as
    an offer, or `step`.

    The challenge door compares the refs as a set, and the escalation door
    compares a sorted list. So the escalation is asked and offered on the
    refs with each ref once (the review of 4de1555, 2026-10-05: 12 of 12
    escalations with a repeated ref landed past a closed escalation).
    """
    once = _unique_refs(refs)
    # law 3: a message routes to the writer of the artefact holding the answer
    # Frame 278, night 153: s283 met the step toward the code, and the
    # Architect had found the fault in the test. The decision's route is
    # the challenge that carries it, so the step offers that challenge.
    offer = None
    if step == CODE_STEP and ctx.role == "developer":
        tests = [r for r in once if isinstance(r, str) and ctx.conn.execute(
            "SELECT 1 FROM tests WHERE id = ?", (r,)).fetchone()]
        offer = decision_step(ctx, tests)
        # Review 1 of frame 278, finding 2: a challenge on the test alone
        # met a second escalation offer after the Architect decided.
        mine = _without_own_reasons(ctx.conn, once, ctx.role)
        if offer and mine and set(mine) <= set(tests):
            return api._offer(ctx, f"{fact} {offer[0]}", "msg.challenge_tester",
                              offer[1])
    if _escalation_admitted(ctx, once):
        return api._offer(
            ctx, fact + " Send msg.escalate_architect on the same refs.",
            "msg.escalate_architect", {"refs": once})
    if step == END_STEP:
        return _Ending(fact + " " + step + " " + _end_form(ctx, once))
    if offer:
        return api._offer(ctx, f"{fact} {offer[0]}", "msg.challenge_tester",
                          offer[1])
    return fact + " " + step


def _end_form(ctx: api.Ctx, refs: list) -> str:
    """
    The reply that takes the step to end, named with the refused challenge's
    test ids.

    Frame 165, night 126: the seats met the step in 11 turns and sent a call
    in 10. Interviewed in their own context, s172 and s168 read the step
    right and had no form to send for it. s168 gave the refused challenge as
    the way to end. In the same prompt, a refusal that named its reply,
    `send refs=[...]`, was taken in one turn. Each id is a fact that frame
    144's check reads.
    """
    tests = [r for r in refs if isinstance(r, str) and ctx.conn.execute(
        "SELECT 1 FROM tests WHERE id = ?", (r,)).fetchone()]
    named = []
    # A loop and not a generator, so each fact's site names this function
    # (frame 165's review of 04407eff, finding 3).
    for r in tests or [r for r in refs if isinstance(r, str)]:
        named.append(api._fact(ctx, "row", r))
    on = ", ".join(named)
    return END_FORM.format(on=f" on {on}" if on else "")


def _judged_by(conn: sqlite3.Connection, msg_id: str, role: str) -> str | None:
    """The id of the newest answer that `role` sent to `msg_id`, or None."""
    row = conn.execute(
        "SELECT id FROM messages WHERE cause_id = ? AND verb = 'answer' "
        "AND from_role = ? ORDER BY seq DESC LIMIT 1",
        (msg_id, role)).fetchone()
    return row["id"] if row else None


def _encodes_refused(conn: sqlite3.Connection, msg_id: str) -> bool:
    """
    True when the Tester sessions that `msg_id` woke called `tests.encode`
    for a criterion of the challenge's refs, and stored no row of `tests`.

    Night 124 (2026-10-05): the constant-assertion door refused all 4 of
    s141's encodes, and s141 then answered m64 with m65. The door read m65
    as a judgement while the test stood at version 1 (ruled: the holding
    session, 2026-10-05, frame 132's pass 3, from the review's count). The
    review of 4de1555 found the rule fired on a refused encode of another
    criterion's test. So the encode must name a criterion of the refs, read
    from `criterion_id` in the call's summary. An unreadable summary does
    not fire the rule.
    """
    import json as _json
    row = conn.execute("SELECT body_refs FROM messages WHERE id = ?",
                       (msg_id,)).fetchone()
    try:
        refs = _json.loads(row["body_refs"] or "[]") if row else []
    except (TypeError, ValueError):
        refs = []
    if not isinstance(refs, list):
        return False
    wanted = _criteria_named(conn, refs, _criteria_of_tests(conn))
    tried = any(
        _encoded_criterion(r["args_summary"]) in wanted
        for r in conn.execute(
            "SELECT t.args_summary FROM tool_calls t "
            "JOIN sessions s ON s.id = t.session_id "
            "WHERE s.trigger_msg = ? AND s.role = 'tester' "
            "AND t.fn = 'tests.encode'", (msg_id,)))
    if not tried:
        return False
    return conn.execute(
        "SELECT 1 FROM receipts r JOIN sessions s ON s.id = r.session_id "
        "WHERE s.trigger_msg = ? AND s.role = 'tester' "
        "AND r.table_name = 'tests' LIMIT 1", (msg_id,)).fetchone() is None


#: `criterion_id='...'` in a call's summary. The summary cuts each argument
#: at 60 characters (`Sandbox.call`), so an id of more than 44 characters
#: loses its closing quote and does not match.
_ENCODED_CRITERION = re.compile(r"(?:^|, )criterion_id='([^']*)'(?=, |$)")


def _encoded_criterion(summary: str | None) -> str | None:
    """The criterion id that an encode's summary names, or None."""
    found = _ENCODED_CRITERION.findall(summary or "")
    return found[0] if len(found) == 1 else None


def _tester_judged(conn: sqlite3.Connection, msg_id: str) -> str | None:
    """
    The Tester's answer to the challenge `msg_id`, or None when the Tester
    did not judge it. An answer after refused encodes is no judgement.
    """
    answer = _judged_by(conn, msg_id, "tester")
    if answer and _encodes_refused(conn, msg_id):
        return None
    return answer


def _challenge_repeat_refusal(ctx: api.Ctx, rows: list, refs) -> str | None:
    """
    The same-refs door for the Developer's challenge to the Tester. Return
    the refusal, or None when the door admits the challenge.

    The newest prior on the same refs decides (frame 132's design, section
    3.1). An open prior waits. A prior after which a row of the refs moved
    admits. A prior that the Tester answered refuses. A prior with neither
    admits, until two such priors stand on one version. Each admit stops at
    `LANDED_CHALLENGES` landed challenges on one quoted body of a criterion
    of the refs, and at `LANDED_CHALLENGES_CEILING` across all bodies.
    """
    if not rows:
        # The review of b2ed55b (2026-10-05): a new refs list beside the same
        # test had no prior, so the cap never ran on it.
        return _challenge_cap_refusal(ctx, rows, refs)
    prior = rows[0]
    if prior["status"] == "open":
        return _waits_refusal("challenge", "tester", prior["id"], ctx, refs)
    # law 7: any touch after the first must reframe, never repeat the question
    # Frame 145, night 122 (2026-10-05): the Tester stored version 2 of the
    # test, and the challenge of version 2 met "they answered". A receipt
    # since the prior's first wake makes this a challenge of a new version.
    if _moved_since_woken(ctx.conn, prior["id"], refs):
        return _challenge_cap_refusal(ctx, rows, refs)
    # S0 walk eight: nine rounds of challenge, answer and harness on the same
    # refs. The Tester judged this version, so the same challenge is the same
    # argument. Each sentence states one fact and one step (frame 135).
    answer = _tester_judged(ctx.conn, prior["id"])
    if answer:
        fact = (f"you sent challenge to tester on exactly these refs already "
                f"({prior['id']}) and they answered ({answer}). Sending it "
                f"again is the same argument again.")
        return _escalation_or_step(ctx, refs, fact, _code_step(ctx))
    # Frame 132, nights 119 and 123 (2026-10-05): the Tester's session wrote
    # nothing and sent nothing, the Architect's rung answered with no words,
    # and the door read that rung as the Tester's answer. An unanswered
    # challenge admits one re-send per version (ruled: the judging session,
    # 2026-10-05, option 1). The count stops at a judged or a moved prior,
    # because the priors before it are about another version or a judgement.
    unanswered = [prior]
    for row in rows[1:]:
        if row["status"] == "open":
            continue
        if (_moved_since_woken(ctx.conn, row["id"], refs)
                or _tester_judged(ctx.conn, row["id"])):
            break
        unanswered.append(row)
        if len(unanswered) >= UNANSWERED_CHALLENGES:
            break
    if len(unanswered) < UNANSWERED_CHALLENGES:
        return _challenge_cap_refusal(ctx, rows, refs)
    fact = (f"you sent challenge to tester on exactly these refs already "
            f"({unanswered[1]['id']}, then {unanswered[0]['id']}), and the ")
    # law 7: any touch after the first must reframe, never repeat the question
    # Night 124 (2026-10-05): a prior can count as unanswered beside the
    # Tester's answer row, when every encode of its session was refused.
    # "Answered neither" is then false, so the sentence states the encodes.
    if any(_judged_by(ctx.conn, r["id"], "tester") for r in unanswered):
        fact += ("test did not change. The Tester sent changes to the test, "
                 "and none landed.")
    else:
        fact += "Tester answered neither and did not change the test."
    # The Developer can write no test, and the ladder climbed twice already.
    # An ended session lets the tick cap carry the batch on (frame 132's
    # design, section 3.4).
    return _escalation_or_step(ctx, refs, fact, END_STEP)


def _landed_ruling_refusal(ctx: api.Ctx, refs, text: str,
                           arg: str = "question") -> str | None:
    """The refusal of a clarify on rows that a landed ruling covers, or None.

    The tie is a shared ref through `ruled_refs`, never a test of sense. Dry
    run 8's m52 asked m30's question again on bg_1, and r_m45_2 held his
    answer (frames 183 and 114, build 2, W3). The seat reads his words once.
    A clarify that names the ruling in its refs has read it and lands. The
    door shows each ruling once per session, so a second send lands too.
    """
    refs = [r for r in refs or () if isinstance(r, str)]
    if not refs:
        return None
    shown = getattr(ctx, "rulings_shown", None)
    if shown is None:
        shown = set()
        ctx.rulings_shown = shown
    marks = ",".join("?" * len(refs))
    rows = [r for r in ctx.conn.execute(
        "SELECT rr.ruling_id, rr.ref, rr.verdict, rr.words FROM ruled_refs rr "
        "JOIN rulings r ON r.id = rr.ruling_id "
        f"WHERE r.status = 'landed' AND rr.ref IN ({marks}) "
        "ORDER BY rr.rowid", refs)
        if r["ruling_id"] not in refs and r["ruling_id"] not in shown]
    if not rows:
        return None
    shown.update(r["ruling_id"] for r in rows)
    lines = []
    for r in rows:
        said = " ".join((r["words"] or "").split())
        lines.append(f"{r['ruling_id']} on {r['ref']}, {r['verdict']}"
                     + (f": \"{said}\"" if said else ""))
    ids = list(dict.fromkeys(r["ruling_id"] for r in rows))
    offered = refs + [i for i in ids if i not in refs]
    said = (f"the principal already ruled on these rows. {'. '.join(lines)}. "
            f"If that answer settles your question, act on it and send no "
            f"clarify. If it does not, send the clarify again with "
            f"{', '.join(ids)} in refs, to show that you read the ruling")
    return api._offer(ctx, said, "msg.clarify_principal",
                      {"refs": offered, arg: text})


def _same_refs_refusal(ctx: api.Ctx, recipient: str, verb: str,
                       refs) -> str | None:
    """
    The door on a challenge or an escalation with the same refs as an earlier
    one from this role. Return the refusal, or None when the door admits.

    `stage` raises the refusal. `_escalation_admitted` asks the same function
    before a sentence names an escalation, so the two cannot disagree.

    Frame 200, night 142 (2026-10-12): m335 answered m334 about an older
    body of the test, and s491 t11's escalation on the new body met it. An
    answered escalation blocks a new one only while no `tests` receipt on a
    test of the refs landed after the prior's wake. The prior's answer is
    about the body that the prior quoted.

    law 7: any touch after the first must reframe, never repeat the question
    """
    # Only the Developer's challenge to the Tester reads who answered and
    # whether the test moved, and only it compares the refs as a set. Every
    # other sender and verb keeps its branch (ruled: the judging session,
    # 2026-10-05, frame 132's question 4).
    if ctx.role == "developer" and recipient == "tester" and verb == "challenge":
        # The stored refs hold the sender's reason row, so the compare drops
        # it on both sides (frame 200, pass 5, fix 1).
        rows = _same_refs_rows(ctx.conn, ctx.role, recipient, verb, refs,
                               as_set=True, drop_own=True)
        return _challenge_repeat_refusal(ctx, rows, refs)
    rows = _same_refs_rows(ctx.conn, ctx.role, recipient, verb, refs)
    # A prior is answered when an answer row names it. For the
    # Developer, a prior that the dispatch closed with no answer row
    # counts too, as an answer with no row. Night 109 (2026-10-03):
    # the Architect turned escalation m97 into a challenge to the
    # Vision Keeper. m97 read 'answered' with no answer row, and the
    # pending branch below refused 11 escalations all night.
    import json as _json
    prior = waiting = None
    # A prior on an older body of the test does not block (frame 200,
    # night 142). An open prior still waits.
    tests = ([r for r in _unique_refs(refs) if isinstance(r, str)
              and ctx.conn.execute("SELECT 1 FROM tests WHERE id = ?",
                                   (r,)).fetchone()]
             if verb == "escalate" else [])
    for row in rows:
        closed = ctx.role == "developer" and row["status"] != "open"
        if tests and (row["answer_id"] is not None or closed) and \
                _receipt_since_woken(ctx.conn, row["id"], tests, ("tests",)):
            continue
        if row["answer_id"] is not None or closed:
            prior = row
            break
        if waiting is None and row["status"] == "open":
            waiting = row
    if prior:
        # Walk ten: escalate, answer, escalate, answer, three times
        # on one pair of refs, with the fix written into the reply
        # as prose in between. The Architect answered; the answer is
        # the material now.
        # Night 106 (2026-10-02): s223 and s224 met "act on the
        # answer", and the answer m116 held no words and no new row.
        # The next write met the stdin door again. So the door names
        # the rows the answer added, or says that it added none.
        if verb == "escalate":
            try:
                answer_refs = _json.loads(prior["answer_refs"] or "[]") or []
            except (TypeError, ValueError):
                answer_refs = []
            if not isinstance(answer_refs, list):
                answer_refs = []          # the JSON text `null`, or a scalar
            own = set(refs or [])
            added = [r for i, r in enumerate(answer_refs)
                     if isinstance(r, str) and r not in own
                     and r not in answer_refs[:i]]
            # Frame 200, the review of 2e6afd1c, finding 3: after a
            # challenge in this session `code.write` and `code.commit`
            # refuse, so the step is the end and not the change.
            challenged = _sent_this_session(ctx, "tester", "challenge")
            if added and challenged:
                return _Ending(
                    f"you sent {verb} to {recipient} on exactly these "
                    f"refs already ({prior['id']}) and they answered "
                    f"({prior['answer_id']}): the answer points at "
                    f"{', '.join(added)}. {END_STEP} "
                    f"{_end_form(ctx, _unique_refs(refs))}")
            if added:
                return (
                    f"you sent {verb} to {recipient} on exactly these "
                    f"refs already ({prior['id']}) and they answered "
                    f"({prior['answer_id']}): the answer points at "
                    f"{', '.join(added)} -- code.source those rows, "
                    f"write the change they call for, and commit")
            # A closed prior with no answer row names its status.
            answer_id = prior["answer_id"] or prior["status"]
            if challenged:
                return _Ending(
                    f"you sent {verb} to {recipient} on exactly these refs "
                    f"already ({prior['id']}) and they answered "
                    f"({answer_id}) with no row beyond your own "
                    f"refs. Sending it again is the same argument again. "
                    f"{END_STEP} {_end_form(ctx, _unique_refs(refs))}")
            return (
                f"you sent {verb} to {recipient} on exactly these refs "
                f"already ({prior['id']}) and they answered "
                f"({answer_id}) with no row beyond your own "
                f"refs. Sending it again is the same argument again. "
                f"The attempt cap carries this batch to the ladder: "
                f"make one real change to the code the test calls, or "
                f"end the session with no call")
        # law 6: exhaustion escalates one rung at a time
        # The Developer's one verb to the Tester, `challenge`, returns
        # above through `_challenge_repeat_refusal`, so the Developer's
        # rung is never met here. The senders here, the critic and the
        # answerers of the Tester, hold no op to name: the text names the
        # answer and the end (the review of frame 349's pass 2, finding 3).
        return (
            f"you sent {verb} to {recipient} on exactly these refs "
            f"already ({prior['id']}) and they answered. Sending it "
            f"again is the same argument again. Do not send this "
            f"{verb} again. Act on the answer, or end the session with "
            f"no call.")
    # A challenge with no answer yet is a question still open. Night
    # 108 (2026-10-02): s307 to s328 sent one challenge each on the
    # refs of m190 while the Tester answered none. Nine landed, and
    # the door read only answered priors. The Developer's text names
    # the code, so the door holds for the Developer only. Only an open
    # prior waits: the schema's open status is 'open'.
    if ctx.role == "developer" and waiting:
        return _waits_refusal(verb, recipient, waiting["id"], ctx, refs)
    return None


def _refuse_confirm_off_entry(ctx: api.Ctx, refs: list, staged: set) -> None:
    """
    Refuse a converse confirm that skips the words that woke the session.

    Night 138's s270 woke on new words about `confirm()` and confirmed s1,
    a statement of an earlier entry about `echo_json`. No statement formed
    for the new words, so the shift question never fired (frame 193's
    design, 2.G.2). The check holds only on a converse wake, where the
    intake claim is armed, and only when the trigger is a principal message.

    law 8: L1 fidelity: the principal ratifies the segmented statements
    """
    entry = getattr(ctx, "entry_id", None)
    if (not refs or not entry or not ctx.trigger
            or getattr(ctx, "intake", "unarmed") == "unarmed"):
        return
    row = ctx.conn.execute("SELECT from_role FROM messages WHERE id = ?",
                           (ctx.trigger,)).fetchone()
    if row is None or row["from_role"] != "principal":
        return
    if any(w[0] == "statements" and len(w) > 2 and isinstance(w[2], dict)
           and w[2].get("span_entry") == entry for w in ctx.writes):
        return
    if ctx.conn.execute("SELECT 1 FROM statements WHERE span_entry = ?",
                        (entry,)).fetchone():
        return
    said = ctx.conn.execute("SELECT text FROM entries WHERE id = ?",
                            (entry,)).fetchone()
    words = " ".join(((said["text"] if said else "") or "").split()).casefold()
    # Words said again are the earlier statement's words. When the trigger
    # entry holds them, the segment door refuses them and names this confirm,
    # so this door admits it. Every ref from another entry must be said again,
    # as whole words (the review of a9de65d5, finding 4).
    for ref in refs:
        if ref in staged:
            # A staged statement of this entry returned above, so this one
            # spans another entry.
            text = next((w[2].get("text") or "" for w in ctx.writes
                         if w[0] == "statements" and w[1] == ref
                         and len(w) > 2 and isinstance(w[2], dict)), "")
        else:
            stmt = ctx.conn.execute(
                "SELECT span_entry, text FROM statements WHERE id = ?",
                (ref,)).fetchone()
            if stmt is None or stmt["span_entry"] == entry:
                continue
            text = stmt["text"] or ""
        text = " ".join(text.split()).casefold()
        if not text or not re.search(rf"(?<!\w){re.escape(text)}(?!\w)", words):
            break
    else:
        return
    raise ValueError(
        f"The words that woke you, `{entry}`, have no statement. Segment them "
        f"with `brief.segment` and confirm that statement. If they ask for "
        f"nothing, call no confirm.")


def _wake_key_parts(ctx: api.Ctx) -> dict[str, str]:
    """Each `|` part of a rowless quarantined key in the wake's refs, mapped
    to its key. The first key keeps a part that two keys share."""
    from .scheduler import rowless_key

    out: dict[str, str] = {}
    for key in getattr(ctx, "wake_refs", None) or ():
        if isinstance(key, str) and rowless_key(ctx.conn, key):
            for part in _key_pieces(key):
                out.setdefault(part, key)
    return out


def _key_pieces(key: str) -> list[str]:
    """The role, the kind and each ref of a tick key, the empty ones left out."""
    # `key_parts` is the one splitter of a tick key (fact F20).
    from .scheduler import key_parts

    role, kind, refs = key_parts(key)
    return [p for p in (role, kind, *refs) if p]


def _bind_send(ctx: api.Ctx, recipient: str, verb: str, label: str,
               prose: str = "", reason_row: str = "") -> Callable:
    """
    Stage an outbound message.

    Conclusions travel; reasoning stays home. `refs` carries ids — the recipient
    follows them to whatever it is permitted to read. There is no prose field on
    purpose: a role that wants to explain itself writes a decision and refs it.

    `prose` names the one channel where that does not hold, and the graph edge
    declares it rather than this function knowing a role name. A message to the
    Researcher crosses to something that shares no database, no artefact and no
    knowledge of this project — that ignorance is the containment — so an id
    means nothing at the far end and a question with no words is no question.
    """
    from .runner import new_id

    def stage(refs: list[str], round_no: int = 0, text: str | None = None,
              reason: str | None = None, spans: list | None = None):
        # Logged first, before any guard, as `_bind` logs a tool call: the
        # register subtracts the refused count from the log, so a reach
        # that a guard threw out must be in the log or a landed send
        # scores as none (qwen2.5:14b, 2026-09-14, the forbidden challenge).
        _CALL_LOG.setdefault(id(ctx), []).append((label, f"refs={refs or []}"))
        # The park message is a page built from the records, whatever the
        # session typed: the item and its criteria, or the batch alone for
        # a note. The model chooses nothing on it (ruled: Roman, 2026-10-08,
        # the park ask is a page with rows). The wake's second ref is the
        # batch.
        park = (getattr(ctx, "wake_kind", "") == "tick:park_ask"
                and recipient == "principal" and verb == "present"
                and len(ctx.wake_refs or ()) == 2)
        if park:
            from .scheduler import park_rows

            refs = park_rows(ctx.conn, ctx.wake_refs[1])
        # The shift question is a page the door builds from the wake: the
        # earlier item and the new request's statement. The model chooses
        # nothing on it (frame 193's design, 2.F.2).
        shift = (getattr(ctx, "wake_kind", "") == "tick:request_shift"
                 and recipient == "principal" and verb == "present"
                 and len(ctx.wake_refs or ()) == 2)
        if shift:
            from ..roles.principal import current_request, shift_ask_id

            refs = list(ctx.wake_refs)
            cur = current_request(ctx.conn, unread=False)
            shift_id = shift_ask_id(refs[0], cur["id"] if cur else "none")
            if ctx.conn.execute("SELECT 1 FROM messages WHERE id = ?",
                                (shift_id,)).fetchone() or any(
                    m.get("id") == shift_id for m in ctx.outbound):
                raise ValueError(
                    "the principal already has this question. Send nothing "
                    "more, and stop")
        # Required, not defaulted. A message carries refs and nothing else —
        # there is no prose field on purpose — so `refs=None` advertised a
        # legal call that communicates the fact that something happened and
        # not one thing about what. Liaison took the offer: five runs of
        # `TOOL: msg.confirm_principal()`, a confirmation request naming no
        # statement to confirm. Missing arguments are already a tool error the
        # model can correct, so this costs a turn rather than a session.
        # One session may not send the same message twice.
        #
        # Not a cap on messages — Liaison delivering the same statements to
        # three roles is three recipients and entirely correct. This is the same
        # recipient, the same verb, the same refs, which is one message sent
        # again. L1 caught Vision Keeper answering a question twice, and once
        # eleven times: the model finishes, does not notice it has finished, and
        # says it again. Telling it afterwards is weaker than making it
        # impossible.
        # A ref is an id, and only an id. Models offer `refs=[{"id": "g_1b9009"}]`
        # and `refs=[{"term": "report", "refs": []}]` -- reasonable-looking, and
        # fatal: the row is stored as-is and the *recipient* dies resolving it
        # ("cannot use 'dict' as a dict key"), a session killed by a message
        # somebody else composed, with the traceback pointing at the innocent
        # role. Refused here it costs the sender one turn and it can see why.
        # A bare string is the failure this guard was blind to, because it is
        # made of strings. `refs="m_283ec8"` passes the check below -- every
        # character is a `str` -- and is then stored as `["m","_","2","8",...]`,
        # a message whose refs are eight single letters that resolve to nothing.
        # Silent at both ends, which is the worst kind, and Liaison did it five
        # runs out of five.
        # A native seat sent `refs='["c_734322", "tst_dcae01"]'`, a list
        # inside a string, and the old text called it one bare id. A small
        # model follows a refusal literally, so the text states the true
        # fault and shows the form (frame 327, wall guide cause 9).
        # The form shows the seat's own ids, because a seat copies the form
        # literally. A fixed example sent ids that name no row, and one
        # element that held `b_9f9824, i_62de3d` sent two ids as one
        # (frame 327, review 1, findings H1 and L2).
        if isinstance(refs, str):
            if refs.lstrip().startswith("["):
                try:
                    sent = json.loads(refs)
                except ValueError:
                    sent = None
                if not (isinstance(sent, list)
                        and all(isinstance(r, str) for r in sent)):
                    sent = ["s_1b9009", "c_734322"]
                raise ValueError(
                    f"refs is a list, not a string that holds a list. You "
                    f"sent {refs!r}. Send the list itself: "
                    f"refs={json.dumps(sent)}")
            raise ValueError(
                f"refs is a list of ids and you sent a bare string, "
                f"{refs!r}. A string is a sequence of characters here, so this "
                f"would travel as one ref per letter. Send a list: "
                f"refs={json.dumps(_listed_refs(refs))}")

        # A list of one-element lists is unambiguous, unlike the dicts below,
        # and it is what a model does when it builds refs one at a time. Liaison
        # sent `[["g_69d1e1"], ["g_2d422b"]]` -- both senses of the colliding
        # word, correctly identified -- had it refused, and retried carrying
        # one. Refusing something recoverable cost the ref it had already found.
        if isinstance(refs, list) and any(
                isinstance(r, list) and all(isinstance(x, str) for x in r)
                for r in refs):
            flat = []
            for r in refs:
                flat.extend(r) if isinstance(r, list) else flat.append(r)
            refs = flat

        bad = [r for r in (refs or []) if not isinstance(r, str)]
        if bad:
            raise ValueError(
                f"refs are ids and nothing else; you sent {bad[0]!r}. Send the "
                f"id on its own -- whatever you wrapped it in cannot travel, "
                f"because the far end resolves ids against the tables and has "
                f"nowhere to put the rest.")

        # An id has a shape, and prose does not have it. Refused the message id
        # above, the next thing Liaison reached for was the statement's *text*
        # as a ref -- which travels, resolves to nothing at the far end, and
        # looks like a well-formed message from every angle except the one that
        # matters. Checking the shape rather than the row keeps this honest for
        # ids written in this same session, which are not in any table yet.
        malformed = [r for r in (refs or []) if not _ID.fullmatch(r)]
        if malformed:
            raise ValueError(
                f"refs are ids, and {malformed[0][:40]!r} is not one. An id "
                f"looks like `s_1b9009` and comes from the rows you were given "
                f"or the tools you called -- the words of the thing are not a "
                f"handle on it")

        # And an id is a promise that a row exists. The shape check above
        # was `\S{1,64}` -- any word passed -- and the world-audit found the
        # cost: 258 refs across the historical runs that resolve to nothing
        # at the recipient, every one composed in good faith ('term_1',
        # 'work_stalled') and every one silently meaningless at the far end.
        # Legal is: a row that exists, a row this session staged, an entry,
        # or an @-prefixed non-row subject. Refused here it costs a turn and
        # the sender can trade the label for the id it actually holds.
        # A part of a quarantined key in the wake waits for the merge below,
        # which reads it as the key (frame 354, pass 4).
        key_parts_woke = (_wake_key_parts(ctx)
                          if verb == "present" and recipient == "principal"
                          else {})
        dangling = [r for r in (refs or []) if not api.ref_resolves(ctx, r)
                    and r not in key_parts_woke]
        if dangling:
            raise ValueError(
                f"{dangling[0][:40]!r} names no row -- not in any table, not "
                f"written this session. Refs are ids from the rows you were "
                f"given or the tools you called; if you mean a thing with no "
                f"row, the thing to send is the row that talks about it")
        # A signoff submit carries every draft its wake named (frame 261).
        api.refuse_signoff_without_draft(ctx, recipient, verb, refs)
        # A signoff submit carries the items its wake named and no other
        # (frame 316, W3 of night 163).
        kept = api.signoff_own_refs(ctx, recipient, verb, refs)
        signoff_dropped = [r for r in refs or [] if r not in kept]
        signoff_woke = [r for r in (getattr(ctx, "wake_refs", ()) or ())
                        if isinstance(r, str)]
        refs = kept

        # The principal is the one recipient that does not share the database.
        # They have seen the transcript and whatever came out of it; they have
        # never seen a message, do not know the roles by name and cannot be
        # shown a row they have no way to resolve. Every brief on this channel
        # already says "the statement or item it is about, not a message id" and
        # it went out as a message id anyway -- the referent a role reaches for
        # is the one it is looking at, and it was looking at the thread.
        #
        # Refused here rather than asked for again, because asking again has
        # been measured: the same instruction stated outright in the mode's own
        # brief moved it 0/5 to 0/5.
        # Never the same question twice. `interrupt_cap` states it: never
        # repeat the question, reframe or offer a default. No code read it.
        # Clarify only: a confirm or a present is a gate on rows, and its
        # A reopen says an approved item changed under a batch. That is a
        # fact in the items table: the approval is older than the version,
        # or gone. tipsAT (2026-09-12): the Vision Keeper, woken by a
        # challenge, authored a decision that the item was already built
        # and sent reopen for it; the Developer was woken to elect on an
        # amendment that never happened, and the batch stalled there.
        if verb == "reopen" and refs:
            unchanged = []
            for r in refs:
                row = ctx.conn.execute(
                    "SELECT approval, approval_ver, version FROM items WHERE id = ?",
                    (r,)).fetchone()
                if row is None:
                    # law 9: a ratified amendment drops the item to pending, stops batches
                    # clickI night 22: reopen sent for a statement id. A
                    # reopen names the amended item; nothing else can be
                    # amended under a batch. The item after a revocation is a
                    # draft, so the text says no state (observed: the
                    # ten-reds record, 2026-09-24).
                    raise ValueError(
                        f"{r} is not an item. A reopen names the item "
                        f"that changed under the batch; a statement or a "
                        f"message is not one, and nothing else can reopen a batch")
                if row["approval"] == "approved" and (
                        row["approval_ver"] or 0) >= (row["version"] or 0):
                    unchanged.append(r)
            if unchanged:
                raise ValueError(
                    f"{unchanged[0]} is approved at its current version; nothing "
                    f"changed under the batch, so there is nothing to reopen. A "
                    f"reopen follows an amendment, never a decision")
        # law 8: a lineage's open assumptions are presented at its gates
        # A page carries at most seven open assumptions. clickI night 17
        # (2026-09-12): reconcile read 37 prose files and the first page
        # put 27 assumptions to the principal in one go. Roman ruled the
        # interview iterative, most important first, a page after an
        # answer showing only what is still open (DECISIONS.md, "The
        # seat's four pages are one surface"). Which seven is the brief's
        # judgement; the count is the door's. The rows left out stay open
        # and the agenda puts them on the next page.
        if recipient == "principal" and verb == "present" and refs:
            open_rows = [r for r in refs if ctx.conn.execute(
                "SELECT 1 FROM ledger WHERE id = ? AND status = 'open'", (r,)).fetchone()]
            if len(open_rows) > PAGE_ASSUMPTIONS:
                raise ValueError(
                    f"a page carries at most {PAGE_ASSUMPTIONS} open assumptions "
                    f"and this one carries {len(open_rows)}. Send the "
                    f"{PAGE_ASSUMPTIONS} whose answer changes the most; the "
                    f"rest stay open and go on the next page after the "
                    f"principal answers this one")
        if recipient == "principal" and verb == "clarify" and text:
            words = " ".join(text.split())
            from .scheduler import park_ask_batch

            for row in ctx.conn.execute(
                    "SELECT id, body_text, status FROM messages WHERE to_role = 'principal' "
                    "AND verb = 'clarify' AND body_text IS NOT NULL ORDER BY seq"):
                # A closed park ask was about an earlier park. A re-park states
                # the same facts, so its words match, and the refusal ran the
                # wake to its cap (observed: frame 87's review of b23d17b,
                # 2026-09-30).
                if (park and row["status"] != "open"
                        and park_ask_batch(row["id"])):
                    continue
                if " ".join((row["body_text"] or "").split()) == words:
                    # A question the principal answered gets the answered
                    # door's step: read the reply, then rule or end. "Reframe
                    # it" invited the same question in new words, which both
                    # doors then passed (the review of eee89bc8, fix 2).
                    api.refuse_answered_question(ctx, text)
                    raise ValueError(
                        f"you have already put these words to the principal, in "
                        f"{row['id']}. Asking twice spends the one budget that "
                        f"cannot be topped up, and reads as not having heard. "
                        f"Reframe it: decompose the question, or name a default "
                        f"they can veto. Or take the default and log the assumption")

        # A clarify that pastes the principal's own sentence back to them.
        # seat1 page 4 (2026-09-12): "The principal said that 3 is wrong:
        # each share is the total with tip divided by the number of people,
        # and every share is equal. Does this mean ..." The reply had gone
        # to its owner, the owner had answered, and the Liaison asked the
        # principal what they had said. Whether a question is worth asking
        # is judgement. That eight words in a row are the principal's is a
        # fact the entries hold. A short quote that anchors a question passes.
        # The refusal names brief.segment. Night 163's s145 met this refusal
        # four times on a new request and only tried other clarifies, because
        # the text named no other route (frame 320, cause 9).
        if recipient == "principal" and verb == "clarify" and text:
            asked = re.findall(r"[a-z0-9']+", text.lower())
            # His words of a message read through `said`, the one reader
            # (night 172, wall W7). An entry of no message, as intake's,
            # still counts.
            from ..roles.principal import said as his_words

            heard = [r["text"] for r in ctx.conn.execute(
                "SELECT text FROM entries WHERE author = 'principal'")]
            heard += [his_words(ctx.conn, r["id"]) for r in ctx.conn.execute(
                "SELECT id FROM messages WHERE from_role = 'principal'")]
            for one in heard:
                run = _longest_word_run(asked, re.findall(r"[a-z0-9']+", (one or "").lower()))
                if len(run) >= QUOTE_RUN:
                    # Only a mode that holds brief.segment is told to use it.
                    # Four Liaison modes hold this door and not brief.segment
                    # (frame 320, review 1, finding 4).
                    route = ("A sentence of theirs that asks for work is a "
                             "request: segment it with brief.segment, not a "
                             "clarify. "
                             if "brief.segment" in api._wake_mode_tools(ctx)
                             else "")
                    raise ValueError(
                        f"'{' '.join(run[:QUOTE_RUN])} ...' is the principal's own "
                        f"sentence, pasted back to them. They know what they said, "
                        f"and reading it to them again is not an answer to it. "
                        f"{route}Ask "
                        f"the one thing you do not know, in your words. If the "
                        f"reply was an answer to a role, that role reads it, not "
                        f"the principal")

        # A role's own bookkeeping is not a question for the principal. Asked
        # as the principal (tips5): "The item_id 'i_1' is invalid ... is there
        # a specific item_id that should be used instead?" A failed call became
        # a question. Whether a question is about the project is judgement and
        # stays the brief's. This is arithmetic: the question quotes an id and
        # the id names no row. Quoted on purpose, so prose with a short word in
        # it is untouched.
        if recipient == "principal" and text:
            for token in re.findall(r"['\"`]([a-z][a-z0-9_]{1,30})['\"`]", text):
                if token in (refs or []) or api.ref_resolves(ctx, token):
                    continue
                # ruling: DECISIONS 1445, a principal's word earns a Liaison question
                # A word the principal wrote is theirs to be asked about.
                # clickI night 29 (2026-09-13): "default_on_eof" is the flag
                # in the principal's own sentence, and the clarify about it
                # was refused as the Liaison's bookkeeping.
                if ctx.conn.execute(
                        "SELECT 1 FROM entries WHERE author = 'principal' "
                        "AND instr(lower(text), ?) > 0 LIMIT 1", (token.lower(),)).fetchone():
                    continue
                # A quoted English word is a word. tipsAM (2026-09-10): the
                # ladder reached the Liaison, its clarify said the criterion
                # names no term for 'share', and the door read 'share' as a
                # row id three sessions running. An id has a prefix and an
                # underscore or a digit; a word has neither.
                if "_" not in token and not any(ch.isdigit() for ch in token):
                    continue
                raise ValueError(
                    f"{token!r} names no row, so this question is about your own "
                    f"bookkeeping, not about the project. The principal cannot see "
                    f"it, did not cause it, and cannot fix it. Put the difficulty "
                    f"to the owner of what you were working on, or report it. Ask "
                    f"the principal only what needs their authority")

        if recipient == "principal" and refs:
            unresolvable = [r for r in refs if ctx.conn.execute(
                "SELECT 1 FROM messages WHERE id = ?", (r,)).fetchone()]
            if unresolvable:
                raise ValueError(
                    f"{unresolvable[0]!r} is a message, and the principal has "
                    f"never seen one. Refs on this channel are the statement or "
                    f"item the question is about -- what they said, in the "
                    f"words they used, which is the only thing they can "
                    f"recognise at their end")

        # On the inquiry route refs are not a citation, they are the
        # question. `msg.ask_*` has no prose field -- law 2 -- so the entry id
        # is the whole of how the principal's words reach the owner: the
        # resolver expands it into `principal_said`, and an ask without it
        # wakes a role to answer nothing, which looks from every angle like the
        # route working.
        #
        # It went unseen because the brief's only worked example of the route
        # was `msg.ask_terminologist(refs=[], question=...)` -- a call that is
        # refused for the argument and, corrected the obvious way, sends the
        # empty one. Measured on `llama3.1:8b`: four asks out of four carried no
        # refs, twice over.
        #
        # Satisfiable, which is what separates this from a gate: `entry_id` is
        # in the session's prompt and the message says so.
        if verb == "ask" and not refs:
            raise ValueError(
                "an ask carries the question in its refs and you sent none. "
                "This channel has no words of its own -- put `entry_id`, the "
                "transcript entry holding what the principal said, in refs, "
                "and the owner reads it as `principal_said`")

        # A held test whose run reached stdin is not a hold, it is the
        # harness fact again. Walk seventeen: the Developer challenged
        # tst_1 with the OSError in the message, the Tester answered holding
        # its ground, and the test cannot pass however the code is written
        # -- `prompt_for_name()` reads input, and the test calls it bare.
        # The fact was refused at encode when the test called input()
        # itself; through a function it is only visible in the run, so the
        # run is where it is refused.
        if verb == "answer" and ctx.role == "tester":
            for r in (refs or []):
                run = ctx.conn.execute(
                    "SELECT output FROM latest_runs WHERE test_id = ? "
                    "AND batch_id = (SELECT batch_id FROM tests WHERE id = latest_runs.test_id)",
                    (r,)).fetchone()
                if run and "reading from stdin while output is captured" in (run["output"] or ""):
                    raise ValueError(
                        f"{r}'s last run reached input() through the code it "
                        f"calls -- pytest captures stdin, so this test cannot "
                        f"pass against any implementation. That is not a "
                        f"hold: re-encode it feeding the name in "
                        f"(monkeypatch.setattr('builtins.input', lambda _='': "
                        f"'Alice')) or asserting on the function that takes "
                        f"the name as an argument")

        # law 7: any touch after the first must reframe, never repeat the question
        # One open question per criterion. `tests_missing` fires per batch
        # while any criterion lacks a test, so the mode meets its own routed
        # criteria again on the next wake -- and a re-asked question forks
        # the thread the ladder is already climbing. The triage's next-step
        # says this too; here it stops being skippable.
        # The answer-must-carry-something door (clickI night 29, 2026-09-13)
        # stood here: an answer to a challenge with the question's own refs
        # and no write was refused. Measured worse the same day: the two
        # Tester hold cases went 0/5 on "you wrote nothing this session",
        # because a hold is an answer in words with the same refs, and on
        # click the Tester's every answer was refused until the challenge
        # was quarantined. Whether an answer says anything is judgement,
        # and the brief holds it.

        if verb == "question" and ctx.role == "tester":
            for r in (refs or []):
                if not ctx.conn.execute(
                        "SELECT 1 FROM criteria WHERE id = ?", (r,)).fetchone():
                    continue
                prior = ctx.conn.execute(
                    "SELECT id FROM messages WHERE from_role = 'tester' "
                    "AND verb = 'question' AND status IN ('open', 'unresolved') "
                    "AND body_refs LIKE ?", (f'%"{r}"%',)).fetchone()
                if prior:
                    raise ValueError(
                        f"{r} already has your open question, {prior['id']}, "
                        f"and the answer will wake you. Asking again forks the "
                        f"thread -- encode the other criteria or end")

        # A report from a batch's own wake names the batch. Measured on the
        # register (AR-a-dead-end, 2026-09-01): the Architect found the right
        # door on the ninth turn and sent it carrying the constraint it had
        # been reading -- the *why* -- and not the batch, the *what*; the
        # seat received a report about nothing it could act on. Only when
        # the wake itself was the batch: a role woken for a batch and
        # reporting is reporting on that batch.
        if (verb == "report" and ctx.batch_id
                and ctx.batch_id in (ctx.wake_refs or ())
                and ctx.batch_id not in (refs or [])):
            raise ValueError(
                f"you were woken for batch {ctx.batch_id} and a report from "
                f"here is about it: add '{ctx.batch_id}' to refs -- keep "
                f"what you have, the batch is the subject and the rest is "
                f"the reason")

        # A challenge pays its reading up front: quote both sides on the
        # tester channel, quote the disputed row everywhere else.
        if verb == "challenge" and recipient == "tester":
            said = _answer_mode_challenge_refusal(ctx, refs, text or "", reason,
                                                  spans)
            if said is not None:
                # The review of pass 2e, finding 2: an answer that holds a
                # decision row gets the call, and the session goes on.
                raise (api.EndRefusal if isinstance(said, _Ending)
                       else ValueError)(said)
        if verb == "challenge":
            _challenge_evidence(ctx, recipient, refs, text or "", reason,
                                quotes=spans)
        # ruling: DECISIONS 1248, an answer that keeps the test quotes the criterion
        # The Tester's answer to a challenge pays the same reading. Night 80
        # (2026-09-15): the answer said "the developer is right, the test
        # asserts more than the criterion asks" and the test stood; the
        # Developer then bent the code to it, fourteen writes, quarantine.
        # An answer that keeps the test carries the criterion's words the
        # assertion comes from; a concession is tests.encode (Roman).
        if verb == "answer" and ctx.role == "tester":
            _answer_evidence(ctx, refs, text or "", quotes=spans)
        if verb in ("challenge", "escalate"):
            # And the same challenge twice is the same argument twice. S0
            # walk eight: nine rounds of challenge, answer, harness, with
            # identical refs every round -- a livelock the attempt cap
            # cannot see because every message is a fresh cause. A held
            # answer means the two of you disagree; the door is above.
            # The door is a module function, so a replay on a night's
            # database runs the same code (frame 132's pass 1).
            said = _same_refs_refusal(ctx, recipient, verb, refs)
            if said is not None:
                # Night 125's s158 obeyed the step, and the runner's
                # owed-call nudge then sent it back to the refused call. The
                # class tells the runner that this refusal ends the session.
                raise (api.EndRefusal if isinstance(said, _Ending)
                       else ValueError)(said)
        # After the same-refs door, so a repeat still meets the refusal
        # that ends the session (frame 165's end form).
        if verb == "challenge":
            red = _red_line_refusal(ctx, refs, text or "", quotes=spans)
            if red:
                raise ValueError(red)
        # After the same-refs door too, for the same end form.
        if verb == "challenge" and recipient == "tester":
            green = _green_at_head_refusal(ctx, refs)
            if green:
                raise ValueError(green)
        if verb == "question" and refs:
            # A question answered twice on the same rows is not a third
            # question. tipsAB (2026-09-09): the Tester asked the
            # Terminologist about one criterion's term 71 times in nine
            # wordings, alternating two ref sets so the exact-refs door
            # above never fired, and the Terminologist answered 65 times
            # with the same ref and no words. Overlap, not equality, and
            # two answers are the bound; the ladder is the exit.
            import json as _json
            answered = 0
            for row in ctx.conn.execute(
                    "SELECT m.body_refs FROM messages m JOIN messages a ON a.cause_id = m.id "
                    "WHERE m.from_role = ? AND m.to_role = ? AND m.verb = 'question' "
                    "AND a.verb = 'answer'", (ctx.role, recipient)):
                try:
                    prior_refs = set(_json.loads(row["body_refs"] or "[]"))
                except (TypeError, ValueError):
                    continue
                if prior_refs & set(refs):
                    answered += 1
            if answered >= 2:
                # Frame 107. The Critic holds no schedule.reask. Its
                # verdict lands first on the criterion as written. So a
                # third question has nothing left to change (ruled: Roman,
                # 2026-10-01: the Critic's doubt about a criterion goes to
                # the Terminologist, the writer of the criteria).
                if ctx.role == "tester":
                    # Frame 135's law: tester/answer and challenge hold the
                    # questions and lack tests.triage, so they get the end.
                    door = "end the session with no call"
                    if api._holds(ctx, "tests.triage"):
                        door = ("tests.triage(criterion_id=..., "
                                "verdict='cannot') with the reason: the "
                                "criterion goes to repair")
                elif ctx.role == "critic":
                    door = "the verdict stands as written: end the session"
                else:
                    # `schedule.unresolved` was renamed `schedule.reask`
                    # (the review of frame 349's pass 2, finding 1).
                    door = "end the session with no call"
                    if api._holds(ctx, "schedule.reask"):
                        door = ("schedule.reask(what_is_missing=...) with "
                                "the reason: what the two answers left open")
                raise ValueError(
                    f"{recipient} has answered {answered} questions of yours "
                    f"on these rows and they did not settle it. A third "
                    f"question is the same question. The exit is {door}")

        # law 7: any touch after the first must reframe, never repeat the question
        # The principal said these words before, and a Liaison message
        # answered them. A second answer is the loop of night 132 (frame
        # 142's design, 2.C, point 6). `rulings.rule(ask=...)` asks the same
        # in `api.rulings_rule`.
        if verb in ("clarify", "converse", "confirm") and recipient == "principal":
            api.refuse_repeated_sentence(ctx)
        # And a question the principal already answered is not asked again
        # (frame 142, night 135's read, fix 4).
        if verb in ("clarify", "converse") and recipient == "principal":
            api.refuse_answered_question(ctx, text)
        # A clarify on rows that his landed ruling covers reads the ruling
        # first. The doors above compare exact words and exact ref lists only
        # (frames 183 and 114, build 2, W3). The park page is a built page.
        if (verb == "clarify" and recipient == "principal" and not park
                and not shift):
            ruled = _landed_ruling_refusal(
                ctx, refs, text or "",
                prose if prose.isidentifier() else "question")
            if ruled:
                raise ValueError(ruled)

        # The intake fork, armed by the mode: a converse to the principal is
        # the reply to work, and its refs carry what intake produced.
        # Undeclared-and-bare is the measured S0 failure -- the greeting
        # answered, the request gone. The `chat` claim is gone (ruled: Roman,
        # 2026-10-08, the park ask is a page with rows, point 4).
        # A clarify keeps no guard here. A greeting's route is one clarify
        # on the entry with no intake (frame 142's design, 2.C). A guard
        # that refused it once made the model send the same clarify twice
        # and never read the entry (the delta review of 4ef3bd9f, finding 3).
        # Whether a request lands with no clarify is a case,
        # L1-LI-a-request-lands-as-a-statement-and-draws-no-clarify, not a door.
        if (verb == "converse" and recipient == "principal"
                and getattr(ctx, "intake", "unarmed") != "unarmed"):
            if ctx.intake is None:
                raise ValueError(api._offer(
                    ctx,
                    "claim the branch first: brief.intake(verdict='work') "
                    "if they asked for anything at all. An unclaimed reply "
                    "is how a request dies politely",
                    "brief.intake", {"verdict": "work"}))
            if ctx.intake == "work" and not refs:
                raise ValueError(
                    "you claimed work, so the reply carries refs -- the "
                    "statements you segmented (brief.segment their words, "
                    "then confirm). A bare reply would answer the greeting "
                    "and lose the request")
            # The refs must be statements. Measured on tipsI (2026-09-09): a
            # second sentence into a merged run was claimed as work, the reply
            # ref'd the entry and said "Got it, anything else?", and the
            # request died with the door satisfied. An entry is not a
            # statement. The state the session holds decides: work claimed,
            # nothing segmented, nothing ref'd that is a statement.
            if (ctx.intake == "work"
                    and not any(w[0] == "statements" for w in ctx.writes)
                    and not any(ctx.conn.execute(
                        "SELECT 1 FROM statements WHERE id = ?", (r,)).fetchone()
                        for r in (refs or []))):
                raise ValueError(
                    "you claimed work and segmented nothing. The refs name "
                    "the entry, and an entry is not a statement. brief.segment "
                    "the request into statements first, then confirm them. "
                    "A reply that only acknowledges loses the request")

        # Recipient and verb, not refs. Matching on refs too caught the exact
        # repeat and missed the expensive one: Terminologist answered a
        # Developer's question correctly, then sent the same answer again with
        # one ref added, then again with it removed. Three answers to one
        # question, which the recipient has to reconcile, and the guard let two
        # of them through because the lists differed.
        #
        # Safe by inspection as well as by argument: no case in the suite
        # expects two messages of one verb to one role, and the broadcast is
        # three recipients rather than three messages. A role with two genuinely
        # separate things to say to the same role says them in one message's
        # refs, which is what refs are.
        # "There is nothing to add" is a result. It is not a result when you
        # looked something up, found nothing, and defined nothing.
        #
        # The ruling that a role woken by a message may say it has nothing to do
        # is right, and putting it in `terminologist/deliver.md` made it the exit
        # from that mode's actual work -- Terminologist consulted, looked up,
        # and reported instead of defining the undefined term, five runs out of
        # five. A briefed alternative inside a decisive mode becomes the exit,
        # for the fourth time in one session.
        #
        # The two situations differ by state the session already holds, so the
        # brief does not have to arbitrate and demonstrably could not.
        # A lookup of nothing is not a miss. Register 2026-09-13: two
        # Terminologist cases 0/5 on "you looked up '' and the glossary had
        # nothing" after a `glossary.lookup(term='')`.
        misses = sorted(m for m in (getattr(ctx, "lookup_misses", None) or ())
                        if str(m).strip())
        if verb == "report" and misses and not any(
                w[0] == "glossary_terms" for w in ctx.writes):
            missing = misses[0]
            raise ValueError(
                f"you looked up {missing!r} and the glossary had nothing, and "
                f"you have defined nothing. There is something to add, and it "
                f"is that")

        # One question per session, and choosing who owns the block is the work.
        #
        # Measured on `L1-TS-a-criterion-no-machine-could-check`, which wants
        # exactly one question to Vision Keeper. `llama3.1:8b` asked Terminologist
        # -- one question, wrong owner. `qwen2.5` asked Researcher,
        # Terminologist *and* Vision Keeper: it found the right recipient and
        # declined to commit to it. Two models, and neither was defeated by the
        # sentence; what neither did was pick.
        #
        # This is the system's own principle seen from the sending end. Two
        # roles blocked on one ambiguity are two discoveries, which is why
        # reports arriving at Liaison are grouped by shared refs -- and one role
        # asking three roles about one block is the same waste with one author,
        # plus three sessions spent and three answers to reconcile.
        #
        # Safe by inspection: no case in the suite expects two questions to
        # different roles from one session. The only fixture naming two is an
        # `any_of`, where they are alternatives.
        #
        # It refuses the *later* question, and that was the wrong end. A
        # session's first tool call is its reflex: measured on the case this
        # comment was written against, the Tester looked a whole clause up in
        # the glossary, got nothing back, read that as an undefined word and
        # asked Terminologist on turn two -- then three turns later worked out
        # that the sentence was the problem, called `msg.question_vision_keeper`,
        # and was refused for a decision it had already improved on. First is
        # not the same as decided.
        #
        # So the question is replaced rather than the caller refused. Nothing
        # else staged in a session is append-only -- a write can be superseded,
        # a re-encode is reported and dropped -- and the commit is atomic, so
        # the outbound set is the session's final state and not its first draft.
        # One question still leaves, which is the whole of what the guard was
        # for; the one that leaves is the one it settled on.
        replaced = ""
        withdrawn: list[str] = []
        if verb == "question":
            # One question per criterion. The diff review's probe landed two
            # rows for one criterion, and the open one woke a second
            # Terminologist session (frame 81).
            for m in ctx.outbound:
                if m.get("route") == "triage" and set(refs or []) & set(m["body_refs"]):
                    raise ValueError(
                        f"already asked -- {m['id']} carries {m['body_refs'][0]} "
                        f"to the Terminologist. Encode the others or end the "
                        f"session")
            # The triage verdict's own question stays. It carries verified
            # spans, and a later question is about another criterion (frame 81).
            prior = [m for m in ctx.outbound if m["verb"] == "question"
                     and m.get("route") != "triage"]
            if prior and recipient not in {m["to_role"] for m in prior}:
                replaced = prior[0]["to_role"]
                for m in prior:
                    ctx.outbound.remove(m)

            # A guard used to stand here withdrawing any test staged for a
            # criterion this question names: asking who owns a criterion and
            # encoding it are contradictory claims about one row, and a session
            # making both leaves a test on file reporting as coverage of the
            # thing it just said was unencodable.
            #
            # It is gone because it decided the contradiction by *order*, and
            # order is not the discriminator. In the two cases it was written
            # for, the encode was a reflex on turn one and the question was what
            # the session reached having read something -- so the question won.
            # In `L1-TS-encode-a-criterion` the encode was correct and complete
            # and the question was the noise, and the rule destroyed the work:
            # a case green for months went to 0/5.
            #
            # Which of the two is worth keeping turns on whether the test is any
            # good, which is exactly what this system cannot judge here, and
            # picking either end of the session to trust is picking the wrong
            # one half the time.

        # A report carries what it was delivered, whatever else it carries.
        #
        # `report_is_settled` is what makes "I have nothing to add" free: every
        # ref in a terminal state and the report is struck out before Liaison's
        # round_close sees it, costing the principal nothing. It decides that by
        # looking at the refs, so a report about the wrong row cannot be decided
        # at all -- it survives, and reaches a person.
        #
        # Measured on `L1-TE-the-words-are-already-defined`, where the session
        # did the entire job right: looked up all four words of the statement it
        # was handed, found every one already on file in the sense used, and
        # reported `refs=[g_09b6f2]` -- the glossary sense it had just confirmed,
        # not the statement. A sense has no terminal marker, so a session with
        # nothing to ask was going to ask.
        #
        # Same reasoning as `batch_id` defaulting from the wake and `area` from
        # the scheduler: which delivery a report answers is a fact about the
        # session, and a value the session already knows should not be one the
        # role has to supply correctly. Added, never substituted -- what it
        # found is still its own to report.
        refs = list(refs or [])
        # A present of the wake's rows carries the wake's rows. Same rule as
        # the report's trigger refs and the relay's ruling refs -- added,
        # never substituted -- and for the same reason at one remove: the
        # `observed_entries` mode cannot read the tables whose rows it
        # presents, so what it cannot enumerate must arrive enumerated.
        if (verb == "present" and getattr(ctx, "wake_refs", None) and not park
                and not shift):
            refs += [r for r in ctx.wake_refs
                     if isinstance(r, str) and r and r not in refs]
        # A small model split the key `critic|tick:challenge|@claim:...` on
        # its bars, and the door refused 'critic' (frame 354, the cold run of
        # pass 3, s58). Ruled for pass 4: the key stays the ref the seat
        # sees, and the door reads a part as the key, once. A part that
        # names a row is read so too: `@claim:...` alone landed two refs for
        # one stopped step (review p3 of frame 354, finding 3).
        if key_parts_woke:
            matched = {key_parts_woke[r] for r in refs if r in key_parts_woke}
            parts = {p for k in matched for p in _key_pieces(k)}
            mapped: list[str] = []
            for r in refs:
                r = r if r not in parts else key_parts_woke.get(r, r)
                if r in parts:
                    continue            # another part of a matched key
                if r not in mapped:
                    mapped.append(r)
            refs = mapped
        # A page with no ref numbers no line. All three wake merges have
        # landed here, so an empty list is the session's and the wake's both.
        # Frame 354: the Principal saw m3, a page with no lines.
        if verb == "present" and recipient == "principal" and not refs:
            held = [f"wake refs {list(ctx.wake_refs)}" if getattr(
                        ctx, "wake_refs", None) else "no wake refs"]
            if getattr(ctx, "trigger", None):
                held.append(f"the trigger {ctx.trigger}")
            if getattr(ctx, "batch_id", None):
                held.append(f"the batch {ctx.batch_id}")
            raise ValueError(
                "a present shows the principal numbered lines, and its refs "
                "are the lines. You sent no refs. Your seat holds "
                + ", ".join(held) + ". Put the ids of the rows you present "
                "in refs")
        # A submit's present carries the uncovered statements by the same
        # rule: which ratified statements no item reflects is a fact about
        # the state, computed by the system, never the session's to trim.
        # Ruled 2026-09-03 with the disclosure itself; measured the same
        # day: shown the block in its working set, the model presented the
        # items alone, five of five.
        if verb == "present" and ctx.trigger:
            row = ctx.conn.execute(
                "SELECT verb, body_refs FROM messages WHERE id = ?",
                (ctx.trigger,)).fetchone()
            if row is not None and row["verb"] == "submit":
                from ..core.db import refs_of
                from ..roles.principal import uncovered_statements

                # law 8: signoff is per-item approval, presented as one document
                # A submit page shows the submitted items' rows and no other
                # item's. Night 163's s152 copied six items onto m48, and his
                # contest of item 1's rows cancelled bg_1 (frame 316, W3).
                sent = set(refs_of(row["body_refs"]))
                if sent:
                    refs = [r for r in refs if r in sent or not ctx.conn.execute(
                        "SELECT 1 FROM items WHERE id = ?", (r,)).fetchone()]

                uncovered = [r["id"] for r in uncovered_statements(ctx.conn)]
                refs += [r for r in uncovered if r not in refs]
                # And the lineage's open assumptions, by the same rule and
                # law 8's own sentence: "a lineage's open assumptions are
                # presented at its gates: nothing ships whose assumptions the
                # principal never saw." A ledger row about a presented row
                # rides with it, added never substituted, so the page the
                # principal signs carries what was assumed where their words
                # were silent. Ruled 2026-09-03 (A1, intent-time): the signoff
                # page is the seed interview's first moment.
                # The rows this hook adds obey the page rule the door below
                # holds the model to: seven a page, the rest on the next.
                # seat2 on click (2026-09-12): the hook put nineteen
                # reconcile rows under one signoff page, past the door, and
                # the person at the seat said "I am not reading nineteen of
                # those". Oldest first; the brief orders what the model sends.
                room = PAGE_ASSUMPTIONS - sum(1 for r in refs if ctx.conn.execute(
                    "SELECT 1 FROM ledger WHERE id = ? AND status = 'open'", (r,)).fetchone())
                if refs and room > 0:
                    marks = ",".join("?" * len(refs))
                    # A lazy row waits for its first touch, as on the agenda,
                    # so it rides no signoff page (frame 361, pass 1b).
                    from .predicates import LAZY_WORDS

                    assumed = [r["id"] for r in ctx.conn.execute(
                        "SELECT id FROM ledger WHERE status = 'open' "
                        f"AND about_ref IN ({marks}) "
                        "AND substr(default_taken, 1, ?) != ? ORDER BY rowid",
                        (*refs, len(LAZY_WORDS), LAZY_WORDS))]
                    added = [r for r in assumed if r not in refs][:room]
                    refs += added
                    room -= len(added)
                # And what the other desks assumed about the words themselves.
                # The Terminologist and the Architect log against the ratified
                # statement, which is the lineage's root and is not on the
                # page once items cover it (Level 2, 2026-09-09). Those rows
                # ride the signoff too: a word taken one way, a place a
                # behaviour was put, before anything is sliced.
                lineage = [r["id"] for r in ctx.conn.execute(
                    "SELECT l.id FROM ledger l JOIN statements s ON s.id = l.about_ref "
                    "WHERE l.status = 'open' AND s.status = 'ratified' ORDER BY l.rowid")]
                if room > 0:
                    refs += [r for r in lineage if r not in refs][:room]
        # law 8: signoff is per-item approval, presented as one document
        # And the request's own rows, by the same rule: added, never
        # substituted. Night 136's 49 agenda pages carried no line of the
        # request, so the principal's words landed on a seat's row and never
        # on the item (frame 190's design, 2.1). Which rows are the request
        # is a fact about the state. The park page keeps its own rows.
        # The stamped rows are recorded apart, because an approve lands on a
        # row the wake put on the page and never on a row the door added.
        # Night 133's m212, an account page, approved the contested confirm
        # item that the door stamped (the diff review of 358fed11, finding
        # 1). A quarantined wake records its keys, so a re-render of any
        # other page never reads a key that came later (finding 4).
        notes: dict[str, str] = {}
        account_off: list[str] = []
        if verb == "present" and recipient == "principal" and not park and not shift:
            import json as _json
            from ..roles.principal import (_stalled_keys, code_targets, request_rows,
                                           sent_attempts)

            # A row the model named is not the wake's row. A Liaison that named
            # a contested item on an agenda page let "ok" approve it, so the
            # stamp is every request row that the wake did not name (the
            # delta review of 2c602d1b, finding 4).
            rows = request_rows(ctx.conn, refs)
            woke = set(getattr(ctx, "wake_refs", None) or ()) | api._wake_refs(ctx)
            refs += [r for r in rows if r not in refs]
            stamped = [r for r in rows if r not in woke]
            # The door decides once what each code line shows, and every
            # later read uses the record. A live lookup at the read sent a
            # live batch's correction to the guess (frame 298's design, 2.1;
            # review 2, finding 1).
            code = code_targets(ctx.conn, refs)
            refs += [k for k in code if k not in refs]
            stamped += [k for k in code if k not in stamped]
            if code:
                notes["code"] = _json.dumps(code)
            if stamped:
                notes["stamped"] = _json.dumps(stamped)
            # The quarantined keys of the page's batches as they stand at the
            # send, from any wake. A quarantined batch put to the principal
            # by another wake opened "Before I build this" (the delta review
            # of 2c602d1b, finding 2).
            batches = [r for r in refs if ctx.conn.execute(
                "SELECT 1 FROM batches WHERE id = ?", (r,)).fetchone()]
            keys = _stalled_keys(ctx.conn, batches) if batches else []
            # A quarantined key with no row rides as its own ref, and no
            # batch names it. The page numbers it from this record (frame 354).
            from ..core.scheduler import rowless_key

            keys += [r for r in refs if r not in keys and rowless_key(ctx.conn, r)]
            if keys:
                notes["stalled"] = _json.dumps(keys)
                # The count of each key at the send, beside the keys. A later
                # lift deletes the row, and dry4's m63 then said "after 0
                # attempts" (frame 360, wall 14). The page reads this record.
                counts = sent_attempts(ctx.conn, keys)
                if counts:
                    notes["attempts"] = _json.dumps(counts)
            # No ref rides a page unnumbered. A row the page does not number
            # leaves the refs, so a ruling of the page closes every row it
            # holds, and the dropped row stays open and countable (frame
            # 193's design, 2.F.7).
            from ..roles.principal import off_page

            off = off_page(ctx.conn, refs)
            if off:
                from ..roles.principal import account_rows

                # The account's rows it drops go out on the account's own
                # page, so no row waits unseen. Night 133's m283 sign-off
                # dropped how_it_works and 3 descriptions (the review of P9,
                # p3, finding 2).
                account_off = account_rows(ctx.conn, [r for r in refs if r in off])
                refs = [r for r in refs if r not in off]
                if stamped:
                    kept = [r for r in stamped if r not in off]
                    if kept:
                        notes["stamped"] = _json.dumps(kept)
                    else:
                        notes.pop("stamped", None)
                if code:
                    code = {k: v for k, v in code.items() if k not in off}
                    if code:
                        notes["code"] = _json.dumps(code)
                    else:
                        notes.pop("code", None)
        # A confirm page is about one request too, and its refs and its
        # numbered rows are one set, as on a present (P8; ruled: Roman,
        # 2026-10-28 09:10, frame 344).
        if verb == "confirm" and recipient == "principal" and not park and not shift:
            from ..roles.principal import off_page

            off = off_page(ctx.conn, refs, confirm=True)
            if off:
                refs = [r for r in refs if r not in off]
        # A clarify about an item he dropped asks him again. Dry1's m108,
        # m112 and m114 did (frame 357, pass 2).
        if verb == "clarify" and recipient == "principal":
            from ..roles.principal import dropped_items

            gone = sorted(set(refs or ()) & dropped_items(ctx.conn))
            if gone:
                raise ValueError(
                    f"the principal dropped {', '.join(gone)}, so no page "
                    f"asks about it again. Send nothing about it")
        # And the same for a ruling's relay, with a stronger warrant: the
        # ruling's refs are the rows the principal ruled on, and the model
        # was choosing among them -- relaying one of two, five runs of five,
        # so half the ruling never reached its owner. Which rows a relay
        # carries is a fact about the wake, not the session's to trim.
        wake_refs: set[str] = set()
        if verb == "relay" and ctx.trigger:
            row = ctx.conn.execute(
                "SELECT body_refs FROM messages WHERE id = ?",
                (ctx.trigger,)).fetchone()
            if row is not None:
                import json as _json
                try:
                    given = _json.loads(row["body_refs"] or "[]")
                except (TypeError, ValueError):
                    given = []
                wake_refs = {r for r in given if isinstance(r, str)}
                refs += [r for r in given
                         if isinstance(r, str) and r and r not in refs]
            # A clarify ruling can rule a row the reply does not carry, one
            # the asker named. Its contest or revise travels too (frame 306,
            # review 1, finding 4).
            # The staged `ruled_refs` rows are the record of that ruling.
            clarify = set()
            for w in ctx.writes or []:
                if w[0] != "rulings":
                    continue
                ask = ctx.conn.execute("SELECT verb FROM messages WHERE id = ?",
                                       (w[2].get("ask_id"),)).fetchone()
                if ask is not None and ask["verb"] == "clarify":
                    clarify.add(w[1])
            refs += [w[2]["ref"] for w in ctx.writes or []
                     if w[0] == "ruled_refs" and w[2].get("ruling_id") in clarify
                     and w[2].get("verdict") in ("contest", "revise")
                     and w[2]["ref"] not in refs]
        # The reading comes before the relay. The answering mode asks for two
        # calls in one turn, the relay second, and the runner ends the session
        # on the first outbound message. A session that relayed first ended
        # with no ruling and no ledger row, which is the night-84 loop exactly
        # (the diff review of 6895000). The order is the door's now.
        #
        # The principal's words, not the principal's verdict. A `verdict`
        # message is already ruled: `principal.land` wrote the ruling at the
        # keypress, and `verdict_signoff` relays it with nothing left to read.
        # Only a `converse` reply to an open ask is a reading this seat owes.
        if (verb == "relay" and ctx.role == "liaison"
                and _reply_to_read(ctx)
                and not any(w[0] in ("rulings", "ledger")
                            for w in (ctx.writes or []))):
            raise ValueError(
                "read the reply before you relay it. This message answers a "
                "question you asked, and the relay carries what the principal "
                "ruled. Call rulings.rule with the rows the words settle, or "
                "ledger.unaddressed for a row the answer says nothing about. "
                "Then send the relay")
        if verb == "report" and ctx.trigger:
            row = ctx.conn.execute(
                "SELECT body_refs FROM messages WHERE id = ?",
                (ctx.trigger,)).fetchone()
            if row is not None:
                import json as _json
                try:
                    given = _json.loads(row["body_refs"] or "[]")
                except (TypeError, ValueError):
                    given = []
                refs += [r for r in given
                         if isinstance(r, str) and r and r not in refs]

        # An owner that could not answer has not answered, and relaying that
        # to the principal spends the one budget in this system that cannot be
        # topped up while two owners who might know have not been asked.
        #
        # `k0` is constraint zero: the row bound to everything no survey has
        # reached. An answer whose refs are the question and `k0` is an owner
        # saying "not surveyed" -- a fact about the run, not the answer that
        # was asked for. Measured on the click database: Architect answered
        # `refs: ["e_m5", "k0"]` and the principal was told the area had not
        # been surveyed while Terminologist, which held the term the question
        # was about, was never asked.
        #
        # Derived rather than declared, and only here. `schedule.reask` exists
        # because in general "the answer did not land" is invisible to a query
        # -- the row says answered and only the asker knows. On this route it
        # is visible, because the owner cites the row that means it.
        if (recipient == "principal" and verb == "converse"
                and getattr(ctx, "trigger", None)):
            if _relaying_a_non_answer(ctx):
                raise ValueError(
                    "the answer you are relaying cites nothing it came from -- "
                    "only the question, the thread, or constraint zero, which "
                    "is the row for everything no survey has reached. That is "
                    "an owner saying it does not know, and the other owners "
                    "have not been asked. Say what is still missing with "
                    "schedule.reask; asking them is free and the principal's "
                    "attention is not")

        # An answer names what it came from.
        #
        # `refs` are the whole payload -- law 2, conclusions travel and
        # reasoning stays home -- so an answer citing only the question, the
        # thread, or constraint zero has told the asker nothing they can
        # follow. Measured on the click run: a rung woken by the `unresolved`
        # ladder read its glossary properly, three lookups deep, and answered
        # `refs: ["e_m5"]` -- the question, handed back. The asker cannot relay
        # that and cannot act on it.
        #
        # Bounded to the one channel where it is not a matter of taste.
        #
        # Liaison relays to the principal, who has never seen a row and cannot
        # be shown one they cannot resolve -- the guard above refuses a message
        # id on that channel for exactly that reason. So an answer to Liaison
        # citing only the question or the thread hands it something it is
        # forbidden to pass on and cannot act on. Every other answer stays
        # between roles that share a database, where the recipient can look
        # around for itself.
        #
        # Narrowed after measuring the wider version. Held to citing a source on
        # *every* channel, Vision Keeper spent all twelve turns of
        # `L1-VK-the-last-rung-rules-or-sends-it-up` re-reading its artefacts
        # and re-sending an empty answer, five runs out of five, and committed
        # nothing at all. Satisfiable in principle is not satisfiable, and this
        # system's own law says a gate the model cannot satisfy is a loop.
        #
        # The escape stays open where it is needed: `msg.report_liaison` is how
        # an owner says its artefact does not hold the answer, and the three
        # roles that can be asked by Liaison are exactly the three that have one.
        if (verb == "answer" and recipient == "liaison"
                and _names_no_source(ctx.conn, refs)):
            raise ValueError(
                "an answer names the rows it came from, and these name none -- "
                "only the question, the thread, or constraint zero. Cite what "
                "you read: the terms, items or constraints your answer rests "
                "on. If your artefact does not hold it, that is a report and "
                "not an answer")
        # The Terminologist answers from the glossary. Three runs of five
        # read "there are no terms in the glossary" and sent an answer
        # anyway. The brief says report then, so the door names the report.
        # It stands after the echo door, whose refusal is more specific.
        # A criterion counts as well: the criterion_repair mode answers with
        # the criterion it rewrote, and that row is the Terminologist's own.
        if verb == "answer" and ctx.role == "terminologist":
            cited = [r for r in (refs or []) if tables_of(
                ctx.conn, r, among=("glossary_terms", "criteria"))
                or any(w[0] == "criteria" and w[1] == r for w in ctx.writes)]
            # A criterion that this session specified counts too. The
            # criteria mode sends a note about a check to the Tester after
            # the behaviour lands (frame 306, review 1, finding 1).
            if not cited:
                # The Terminologist holds one report edge, to the Liaison.
                # The door named msg.report_<recipient>, a tool that does not
                # exist. That defect is older than frame 107, and frame 107's
                # review found it (ruled: Roman, 2026-10-01: the Critic's
                # doubt about a criterion goes to the Terminologist, the
                # writer of the criteria). An answer to the Critic cites the
                # criterion, not a term.
                carries = ("an answer to the Critic carries the criterion"
                           if recipient == "critic"
                           else "an answer from the glossary carries a term")
                source = "The criteria do" if recipient == "critic" else "The glossary does"
                said = (f"{carries}, and refs={list(refs or [])} names none. "
                        f"{source} not carry this")
                # A refusal names only a call the session holds (frame 135's
                # law). The criteria mode holds no report edge, and the
                # offer met NotInWorkingSet on the docstring case (frame
                # 322, pass 3b). A context that `build` did not make holds
                # no working set, and it keeps the report.
                working = getattr(ctx, "working_set", None)
                if working is None or "msg.report_liaison" in working:
                    raise ValueError(api._offer(
                        ctx,
                        f"{said}: send msg.report_liaison"
                        f"(refs={list(refs or [])}) with the same refs.",
                        "msg.report_liaison", {"refs": list(refs or [])}))
                # glossary.amend is the call that writes a term down.
                if "glossary.amend" in working:
                    raise ValueError(api._offer(
                        ctx,
                        f"{said}: write the term down with glossary.amend, "
                        f"then cite its id in refs.",
                        "glossary.amend", {}))
                raise ValueError(f"{said}.")

        # Frame 115, design 200 change 4: law 2 keeps words off this channel,
        # so an answer that hands back the escalation's own rows tells the
        # Developer nothing. 10 of 10 such answers on nights 138 and 139 had
        # no words. The row route stays inside law 2: a decision carries them.
        if verb == "answer" and ctx.role == "architect" and recipient == "developer":
            said = _rowless_answer_refusal(ctx, refs)
            if said is not None:
                raise ValueError(said)

        # A confirmation points at what is being ratified, and the only
        # thing that can be is a statement.
        #
        # Handed "morning. we need SSO, but only if it works with our LDAP",
        # `qwen3:8b` sent `msg.confirm_principal(refs=['e_m_in'])` on turn one,
        # before segmenting anything -- so the principal was asked to ratify
        # the sentence they had just said, no statement existed to ratify, and
        # the session committed nothing. Both passes, and it was the last
        # intake fixture failing.
        #
        # Staged counts as well as stored: `brief.segment` writes into
        # `ctx.writes` and the row is not in any table until the commit, which
        # is the whole reason the refs check elsewhere in this function looks at
        # shape rather than existence.
        if recipient == "principal" and verb == "confirm":
            staged = {w[1] for w in ctx.writes if w[0] == "statements"}
            for ref in refs or ():
                if ref in staged:
                    continue
                if ctx.conn.execute("SELECT 1 FROM statements WHERE id = ?",
                                    (ref,)).fetchone():
                    continue
                raise ValueError(
                    f"{ref!r} is not a statement, and a confirmation asks the "
                    f"principal to ratify one. Cut what they said into "
                    f"statements with brief.segment first, and confirm those "
                    f"ids -- the entry is what they said, not what you read "
                    f"in it")
            _refuse_confirm_off_entry(ctx, refs or [], staged)

        # law 8: L1 fidelity: the principal ratifies the segmented statements
        # A contested statement is not delivered. Night 138's s273 and the
        # pass 3 recordings delivered it after the ratify door refused it
        # (frame 193's design, 2.G.6). Only verdict mode offers a deliver.
        if verb == "deliver" and ctx.role == "liaison":
            from ..roles.principal import contested_statement

            # The confirm pages alone, as the wake reads them. A clarify's
            # approve lifted the doors and left the wake hidden (the review
            # of a9de65d5, finding 3).
            for ref in refs or ():
                ruling = contested_statement(ctx.conn, ref, confirm_only=True)
                if ruling:
                    raise ValueError(api.contested_refusal(ref, ruling))

        # One message gets one answer. `api.refuse_second_answer` holds the
        # rule and says why; the three channels that carry an intake answer
        # declare which one they are, and the second is refused rather than
        # reconciled afterwards.
        answer = ({"converse": "chat", "confirm": "work"}.get(verb)
                  if recipient == "principal" else
                  "inquiry" if verb == "ask" else None)
        if answer:
            api.refuse_second_answer(ctx, answer)

        # The triage verdict's row is the op's, not the model's send. A
        # question the model sends after the verdict is its first (frame 81).
        if _sent_this_session(ctx, recipient, verb):
            raise ValueError(
                f"you have already sent {verb} to {recipient}; saying it again "
                f"with different refs is a second answer to one question, and "
                f"the recipient has to reconcile them. Your work here is done")

        # An inquiry reaches every owner. Which one holds the answer is not
        # the asker's to know -- that is the whole reason the question is
        # routed rather than answered -- so there is no choice here to get
        # wrong, and no way to ask only one.
        #
        # Measured before this: all eight maintainer questions went to exactly
        # one owner. The one naming `intents_to` went to Architect and never to
        # Terminologist, which holds the term. The brief has said "ask every
        # owner that might hold part of the answer" since it shipped.
        #
        # The ladder still handles what it is for -- somebody new speaking when
        # an answer did not land -- but it no longer has to carry the fan-out,
        # which it only ever did when the non-answer was detectable. A
        # confident wrong answer stopped it dead.
        # An escalation over a finding whose grain the diff removed is the
        # finding restated. The register (2026-09-10): given a constraint
        # binding `calculate_tip` and a diff that renamed it, llama3.1:8b
        # escalated 5/5 instead of restoring the name. Whether the name is
        # still defined in the worktree is a fact about the files.
        if verb == "escalate" and recipient == "architect":
            _escalation_over_removed_grain(ctx, refs or [])
        # One check, for every pair that reaches a Tester or a Developer and
        # for the question a Tester or a Developer sends (W10).
        _unbuilt_refusal(ctx, recipient, verb, refs or [])
        recipients = [recipient]
        if verb == "ask":
            g = graph_mod.load()
            owners = sorted({e.t for e in g.of_type("messages")
                             if e.s == ctx.role and e.v == "ask"})
            already = {m["to_role"] for m in ctx.outbound if m["verb"] == "ask"}
            recipients = [r for r in owners if r not in already]

        # A ruling's relay is routed by ownership, not by the recipient the
        # model named. Told to split by table, Liaison broadcast an items-only
        # ruling to all three owners and sent a mixed one wholly to Vision
        # Keeper, five of five each way -- and unlike the ask, this is not
        # even a judgement to remove: a row's table is in the database and the
        # single-writer law gives each table one writer, so every ref's
        # destination is a lookup. Refs whose table is unknown stay with the
        # named recipient rather than being dropped.
        split: dict[str, list[str]] = {}
        if verb == "relay" and refs:
            # A criterion row of a park page goes to its writer, the
            # Terminologist (ruled: Roman, 2026-10-08, the park ask is a page
            # with rows, point 2). A criterion that reached a ruling another
            # way, through a ledger row's `about_ref`, keeps the old route
            # (the diff review of b0a2086e, finding 1).
            from .scheduler import park_verdict_page, park_verdict_rows, ruled_rows

            on_park = park_verdict_page(ctx.conn, ctx.trigger) is not None
            # law 2: judgement crosses a role boundary only as ids and states
            # Only the contested and revised lines of a park page travel. An
            # approved criterion in the relay reached `criterion_repair`,
            # where only the brief kept it unchanged (the diff review of
            # 0baacf55, finding 2). The item went to the Vision Keeper on
            # every contest of night 132's bg_2, though only a criterion was
            # ruled (the delta review of 4ef3bd9f, finding 2). The item is
            # line 1 of the page (frame 142's design, 2.A), so a contest of
            # the item still goes to its owner.
            # None means no verdict rules these rows, so a test row keeps
            # the route of frame 213.
            ruled: list[str] | None = None
            if on_park:
                ruled = park_verdict_rows(ctx.conn, ctx.trigger)
                refs = [r for r in refs if r in ruled]
            # Every page now carries the request's criteria, so the filter of
            # the park page holds for a criterion on every page: an approved
            # criterion reaches no relay (frame 190's design, 2.F,
            # amendment 1). His ruling is the verdict's map or the `rulings`
            # record of a converse reply, so the filter runs on both. Night
            # 164's m94 kept four approved criteria on a converse reply
            # (frame 338).
            elif ruled_rows(ctx.conn, ctx.trigger, ctx.writes) is not None:
                ruled = ruled_rows(ctx.conn, ctx.trigger, ctx.writes) or []
                given = list(refs)
                refs = [r for r in refs if r in ruled or not ctx.conn.execute(
                    "SELECT 1 FROM criteria WHERE id = ?", (r,)).fetchone()]
                # The trigger's own refs join the relay above, so they always
                # survive the filter. The guard counts only a ruled row or a
                # ref the session chose (the relay read of 2026-10-29,
                # finding 3).
                chosen = [r for r in refs if r in ruled or r not in wake_refs]
                if len(refs) < len(given) and not chosen:
                    raise ValueError(
                        "the principal approved these criteria as they stand, so "
                        "no owner has anything to change. Your work here is done")
            # A criterion goes to its writer, the Terminologist, on every
            # page. Off the park page, `_owner_of_ref` knew no criterion and
            # the contested line went nowhere (the diff review of 358fed11,
            # finding 3; frame 190's design, 2.2.7). A criterion ruled as a
            # line of its page travels in its own relay, which keys
            # `criterion_repair`. A term beside it keeps `relay`, because the
            # repair mode holds no `glossary.adopt`.
            from .scheduler import park_verdict_criteria

            lines = set(park_verdict_criteria(ctx.conn, ctx.trigger))
            for ref in refs:
                # law 3: contacts derive from read and write edges; no second list
                # A test row of a ruling travels as its criterion, to the
                # criterion's writer. The principal never rules on a test
                # (ruled: Roman, 2026-10-08, the park ask is a page with
                # rows, point 2). A relay straight to the Tester is a new
                # edge in the graph, which Roman has not ruled. Night 144's
                # m402 took the revise of a test row to the Vision Keeper
                # (frame 213, route B).
                test = ctx.conn.execute(
                    "SELECT criterion_id FROM tests WHERE id = ?", (ref,)).fetchone()
                if test and test["criterion_id"]:
                    # An approved test row adds no criterion, as an approved
                    # criterion adds none. Night 168's m50 took crit_3 through
                    # the approved tst_crit_3, and the relay keyed `relay`,
                    # where no call reaches the Tester (frame 338).
                    if ruled is not None and ref not in ruled:
                        continue
                    split.setdefault("terminologist" + CRITERIA_RELAY, []).append(
                        test["criterion_id"])
                    continue
                # `db.tables_of` finds the row (F22).
                held = tables_of(ctx.conn, ref)
                if ref in lines:
                    owner = "terminologist" + CRITERIA_RELAY
                elif "criteria" in held:
                    owner = "terminologist"
                elif guess_item(ref) is not None:
                    owner = "architect" + GUESS_RELAY
                elif "batches" in held:
                    owner = _owner_of_ref(ctx.conn, ref) + BATCH_RELAY
                else:
                    owner = _owner_of_ref(ctx.conn, ref) or recipient
                split.setdefault(owner, []).append(ref)
            # A criterion and its ruled test name one row twice.
            split = {o: list(dict.fromkeys(r)) for o, r in split.items()}
            # A criterion goes to the Terminologist in one relay. The relay
            # takes the reply's refs too, so on night 158 cr_2 came through
            # tst_02 under the criteria key and again on its own. Each relay
            # woke `criterion_repair` (frame 306, pass 1b).
            keyed = set(split.get("terminologist" + CRITERIA_RELAY, []))
            if keyed and "terminologist" in split:
                split["terminologist"] = [r for r in split["terminologist"]
                                          if r not in keyed]
                if not split["terminologist"]:
                    del split["terminologist"]
            already = {m["to_role"] for m in ctx.outbound if m["verb"] == "relay"}
            split = {o: r for o, r in split.items()
                     if o.split(":", 1)[0] not in already}
            if not split:
                raise ValueError(
                    "every owner these rows belong to has its relay already; "
                    "saying it again is a second answer. Your work here is done")
            recipients = sorted(split)

        # Frame 200, pass 5: the reason of a challenge travels as the
        # sender's own row, reached by a ref (law 2). The door runs after
        # every other door, so an earlier hint can carry the slot first.
        reason_note = ""
        if reason_row:
            rid, reason_note = _stage_reason(ctx, reason_row, refs,
                                             text or "", reason, spans)
            if rid not in (refs or []):
                refs = list(refs or []) + [rid]

        # Each reply of his that the team read and he has not confirmed rides
        # the page as its read-back line. The refs hold the line, so a later
        # render numbers the same lines (the seam design, 2.3, and its
        # review, finding 3). A shift page and a park page take no approve,
        # so they carry none (finding 2). A reading rides the page of its own
        # request only. Night 172's m47 read back e_p1's answers on e_p2's
        # confirm page (P8; ruled: Roman, 2026-10-28 09:10, frame 344).
        if (recipient == "principal" and verb in ("present", "confirm")
                and not park and not shift):
            from ..roles.principal import readings_owed

            refs = list(refs or [])
            refs += [r for r in readings_owed(ctx.conn, refs) if r not in refs]
        msg_id = new_id("m", ctx.conn, offset=len(ctx.outbound))
        if shift:
            msg_id = shift_id
        if park:
            # The id marks the park and names the batch, so the predicate
            # asks once per park and a commit closes this ask.
            from .scheduler import park_ask_id

            msg_id = park_ask_id(ctx.conn, ctx.wake_refs[1])
        if account_off:
            from ..roles.principal import account_page_refs

            # The account's page goes first, so the request's page stays
            # the call's own message (ruled: Roman, 2026-10-28 09:10).
            shown = account_page_refs(ctx.conn, account_off)
            if shown:
                ctx.outbound.append({
                    "id": new_id("m", ctx.conn,
                                 offset=len(ctx.outbound) + len(recipients)),
                    "to_role": "principal", "verb": "present",
                    "body_refs": shown, "body_text": None,
                    "round_no": round_no, "cause_id": ctx.trigger})
        for n, to_role in enumerate(recipients):
            staged = {
                "id": msg_id if n == 0
                else new_id("m", ctx.conn, offset=len(ctx.outbound)),
                "to_role": to_role.split(":", 1)[0], "verb": verb,
                "body_refs": split.get(to_role, list(refs or [])) if split
                else list(refs or []),
                "body_text": text,
                "round_no": round_no, "cause_id": ctx.trigger,
            }
            # The split key stays on the staged relay and never reaches the
            # message, so `stage_park_relay` finds the criteria relay by it.
            if split:
                staged["split"] = to_role
            # A note asks nothing, so it is written closed. An open note went
            # to `pump`, the principal answered it, and the answer woke the
            # Liaison on a page with no question (frame 142's design review,
            # finding 1).
            if park and refs == [ctx.wake_refs[1]]:
                staged["status"] = "answered"
            if notes:
                staged["config"] = {f"{k}:{staged['id']}": v for k, v in notes.items()}
            ctx.outbound.append(staged)
        out = {"id": msg_id, "to": recipient, "verb": verb}
        if reason_note:
            out["note"] = reason_note
        if len(recipients) > 1:
            # Said back, so the session knows it has finished asking. Left
            # unsaid, the model reaches for the other two and meets the
            # duplicate guard, which costs turns and reads as a refusal of
            # something it was told to do.
            out["to"] = recipients
            out["note"] = ("asked every owner; which of them holds the answer "
                           "is not yours to work out. Your work here is done")
        if split:
            out["to"] = {}
            for o in recipients:
                out["to"].setdefault(o.split(":", 1)[0], []).extend(split[o])
            out["note"] = ("routed each row to the owner of its table; there "
                           "was nothing to choose. Your work here is done")
        if withdrawn:
            out["note"] = (
                f"the test you staged for that criterion ({', '.join(withdrawn)}) "
                f"has been withdrawn. You cannot ask who owns a criterion and "
                f"encode it in the same breath; the question is the one that "
                f"stands.")
        if replaced:
            # Said, not done silently. The session that changed its mind here
            # narrated "the previous one was not answered" and asked again —
            # it needs to know the earlier question is gone rather than
            # unanswered, or it spends its remaining turns chasing it.
            out["note"] = (f"this replaces the question to {replaced}, which "
                           f"will not be sent. One block, one owner, and you "
                           f"have named {recipient}.")
        if signoff_dropped:
            # Said, so the drop of frame 316's W3 is never silent (review
            # finding 3).
            left = (f"left out {', '.join(signoff_dropped)}: this signoff was "
                    f"woken for {', '.join(signoff_woke)}, and a signoff page "
                    f"carries only the items that woke it")
            out["note"] = f"{out['note']}. {left}" if "note" in out else left
        return out

    # Two signatures, because the model is shown exactly what it may pass and an
    # advertised `**kwargs` is an invitation to invent one. The prose channel
    # names its argument outright; every other channel cannot take words at all.
    #
    # `prose` is that argument's *name*, not a description of it. Setting it to
    # "note" on the principal channels produced an error reading "needs note=",
    # against a parameter called `question` -- so the model passed `note=`, was
    # told it was unexpected, and fell back to positional, sending integers
    # where refs go. One word with two meanings, in the binder that exists to
    # stop exactly that, and it cost `L1-LI-present-what-onboarding-only-observed`
    # five runs out of five.
    if prose:
        # The parameter is *named* from the graph, which is what the comment
        # above always claimed and the code did not do: the argument was
        # hardcoded `question` on every prose channel whatever the edge said.
        #
        # It went unnoticed while `question` was the only value. The chat work
        # added `liaison -> principal: converse` with `prose='reply'`, and
        # Liaison's brief tells it -- three times, once in prose and twice in
        # worked examples -- to call `msg.converse_principal(reply='...')`.
        # That call could not succeed: `reply` was an unexpected argument on a
        # function that wanted `question`. A prompt naming an argument the
        # function does not have is the failure this repository has measured
        # most often, and here the graph, the brief and the binder each had a
        # different name for one thing.
        #
        # Built by exec because a parameter name is not otherwise a runtime
        # value, and `validate_args` reads the real signature -- annotations
        # included, which is how `refs` is allowed to be a list.
        arg = prose if prose.isidentifier() else "question"
        ns: dict = {"_stage": stage, "_label": label, "_prose": prose}
        why = ("the words are the whole message here" if verb == "converse"
               else "a challenge with no quote has not read what it disputes"
               if verb == "challenge"
               else "refs say what you are asking about, and nothing says "
                    "what you are asking")
        ns["_why"] = why
        # A plural-named field invites a list, and for quotes a list of
        # spans is unambiguous -- join it. `question=` keeps the scalar
        # annotation: two questions really are two messages, and refusing
        # that ambiguity is validate_args doing its job.
        # A dict of labelled spans is the same thing with names on it.
        # qwen2.5:14b sent `quotes={"criterion": ..., "diff": ...}` and the
        # door crashed on `.split` instead of reading the spans (2026-09-09).
        ann = "str | list | dict" if verb == "challenge" or arg == "quotes" else "str"
        # An answer's words are optional at the binder: the Tester answers
        # questions as well as challenges, and only the answer to a challenge
        # must quote the criterion (_answer_evidence reads the trigger).
        default = " = None" if verb == "answer" else ""
        # Frame 200, pass 5: an edge with a reason row takes reason=. The
        # default is None, so the reason door refuses a missing reason with
        # the call written out, after every other door.
        extra = ", reason: str | None = None" if reason_row else ""
        passed = ", reason=reason" if reason_row else ""
        src = (
            f"def send(refs: list[str], {arg}: {ann}{default}{extra}, round_no: int = 0):\n"
            # Frame 328, review 1, finding 5: the challenge door reads the
            # quotes as sent, so an elided quote stays one quote.
            f"    _spans = (list({arg}.values()) if isinstance({arg}, dict) else\n"
            f"              list({arg}) if isinstance({arg}, list) else\n"
            f"              [{arg}] if isinstance({arg}, str) else None)\n"
            f"    if isinstance({arg}, dict):\n"
            f"        {arg} = ' ... '.join(str(v) for v in {arg}.values())\n"
            f"    if isinstance({arg}, list) and any(not str(x).strip() for x in {arg}):\n"
            # law 13: no date appears in a prompt
            # Click night 58 found the empty entry. The seat reads the
            # refusal, so the refusal names no night and no date.
            "        raise ValueError('quotes= has an empty entry: each side of a challenge is a span copied from its row, and an empty string quotes nothing')\n"
            f"    if isinstance({arg}, list):\n"
            f"        {arg} = ' ... '.join(str(x) for x in {arg})\n"
            f"    if not {arg}:\n"
            "        raise ValueError(f'{_label} needs {_prose}=: {_why}')\n"
            f"    return _stage(refs, round_no, text={arg}, spans=_spans{passed})\n"
        )
        exec(src, ns)  # noqa: S102 - the name is the graph's, not a session's
        send = ns["send"]

        # Two reasons a channel carries words, and they used to be conflated.
        # The Researcher shares no database, so an id means nothing at the far
        # end. Every other question channel shares the whole database and still
        # needs words, because a question is about something no artefact holds
        # -- that is what makes it a question. The doc says whichever applies.
        if recipient == "researcher":
            doc = (f"Ask {recipient} a question of fact about something outside this "
                   f"repository. It has never seen this project, so say what you "
                   f"need to know in words. refs: list of ids, may be empty.")
        elif verb == "converse":
            doc = (f"Send a natural-language {verb!r} to {recipient}. "
                   f"`{prose}=` carries the words; refs may be empty.")
        elif verb == "challenge":
            doc = (f"Dispute a row {recipient} owns. refs name the disputed "
                   f"rows; `quotes=` copies their exact words -- the span of "
                   f"each row your challenge stands on, verbatim, not a "
                   f"paraphrase.")
            if reason_row:
                # Frame 200, pass 5: the reason is stored as your row, and
                # the message refs it.
                doc += (" `reason=` names the error the test got and the "
                        "line of the test that raises it. It is stored as "
                        "your decision row, and the message refs it.")
        else:
            doc = (f"Ask {recipient} a question. The refs say what it is about; "
                   f"`{prose}=` says what you need to know about them, which no "
                   f"row holds. refs: list of ids.")
    else:
        def send(refs: list[str], round_no: int = 0):
            return stage(refs, round_no)

        doc = f"Send a {verb!r} message to {recipient}. refs: list of ids."

    send.__name__ = label.replace(".", "_")
    send.__doc__ = doc
    if reason_row:
        # Frame 200, pass 5b, item 2: the TOOL line shows the slot, because
        # `reason=None` reads as optional to the seat.
        send.__shown__ = {"reason": REASON_SLOT.split("=", 1)[1]}
    return send


# The artefact tables whose rows travel as refs; an id colliding across any
# two of them makes every ref to it ambiguous.
# Keyed by ARTEFACT name (what a label carries), valued by table: `problem`
# writes items and `brief` writes statements, and the first version keyed
# by table refused problem.prioritize(id='i1') for colliding with the very
# row it updates.
_ID_TABLES = {"brief": "statements", "problem": "items",
              "tickets": "tickets", "criteria": "criteria",
              "tests": "tests", "batches": "batches"}


def _bind(impl: Callable, ctx: api.Ctx, label: str) -> Callable:
    """Bind the session context away and record the call as evidence.

    The tool_calls log is a first-class assertion target: "Developer re-read
    exactly the receipt-touched entries" is a query over this.
    """
    import inspect

    def wrapper(**kwargs):
        args_summary = ", ".join(f"{k}={v!r}"[:60] for k, v in sorted(kwargs.items()))
        _CALL_LOG.setdefault(id(ctx), []).append((label, args_summary))
        # An artefact id is unique across artefact tables -- Law 14 at the id
        # level. Walked live (S0 five): tickets, criteria and tests all ended
        # up sharing t1/t2/t3, each role copying the table before it, and a
        # challenge naming the test resolved to the criterion -- every ref in
        # the system became ambiguous. Refused at birth, where it costs one
        # turn and the message names a free shape.
        if "id" in kwargs and isinstance(kwargs.get("id"), str):
            own = _ID_TABLES.get(label.split(".", 1)[0])
            for table in _ID_TABLES.values():
                if table != own and ctx.conn.execute(
                        f"SELECT 1 FROM {table} WHERE id = ?",
                        (kwargs["id"],)).fetchone():
                    mine = any(t == table and rid == kwargs["id"]
                               for t, rid, *_ in ctx.writes)
                    if mine:
                        raise ValueError(
                            f"{kwargs['id']!r} is the {table} row you wrote "
                            f"this session, and a {own or label.split('.', 1)[0]} "
                            f"row is a different "
                            f"thing from it -- if this one would only say "
                            f"that you made that edit, the edit is already "
                            f"the record and nothing more is owed")
                    # The hint used to read "prefix it with what it is,
                    # c_ for a criterion, tst_ for a test": tipsAX
                    # (2026-09-12), the Vision Keeper writing a decision
                    # took it literally and named the decision c_tst_s1,
                    # and a later session made an item of that id. Name
                    # the artefact being written, not two others.
                    what = own or label.split(".", 1)[0]
                    raise ValueError(api._offer(
                        ctx,
                        f"{kwargs['id']!r} is already a row of {table}; an "
                        f"artefact id is unique across every artefact table, "
                        f"or every ref to it is ambiguous. Give this {what} "
                        f"row an id of its own, a short name for what it "
                        f"says, and send again",
                        label, {**kwargs, "id": api.INVENT}))
        try:
            return impl(ctx, **kwargs)
        except Exception as exc:
            # The session's own refusals, kept where a later call can see
            # them. `surveys.attest` reads this to tell "nothing to write"
            # from "the write was refused", which are different results.
            refusals = getattr(ctx, "refusals", None)
            if refusals is not None:
                # The path decides whether a refused write meant a change
                # to the program or to a test (frame 360, review p1, F2).
                refusals.append((label, str(exc), type(exc).__name__,
                                 kwargs.get("path")))
            raise

    wrapper.__name__ = label.replace(".", "_")
    wrapper.__doc__ = impl.__doc__
    if getattr(impl, "__shown__", None):
        wrapper.__shown__ = impl.__shown__
    # Expose the real signature with `ctx` bound away, so both the advertisement
    # in the prompt and the argument validation see what the model sees.
    #
    # eval_str resolves annotations that `from __future__ import annotations`
    # leaves as strings. Without it every parameter types as `str` in the JSON
    # schema, and a model told span_start is a string will send "0".
    try:
        sig = inspect.signature(impl, eval_str=True)
    except (NameError, TypeError):
        sig = inspect.signature(impl)
    wrapper.__signature__ = sig.replace(
        parameters=[p for n, p in sig.parameters.items() if n != "ctx"]
    )
    return wrapper


# Call log keyed by context identity; drained into the session result on commit.
_CALL_LOG: dict[int, list[tuple[str, str]]] = {}


def drain_calls(ctx: api.Ctx) -> list[tuple[str, str]]:
    return _CALL_LOG.pop(id(ctx), [])


def stage_park_relay(ctx: api.Ctx) -> None:
    """
    Stage the relay of a park verdict's contested criteria to the
    Terminologist, when no relay of the session carries them.
    """
    # The door makes this relay, and the brief is not the gate. The
    # verdict_signoff brief says a criterion has no relay, so a session that
    # obeyed it left the corrected criterion with nobody, and the parked line
    # still said the team rewrites it (the delta review of 172b373b,
    # finding 1; ruled: Roman, 2026-10-08, the park ask is a page with rows,
    # point 2).
    from .runner import new_id
    from .scheduler import park_verdict_criteria, verdict_rows

    if getattr(ctx, "role", None) != "liaison" or not getattr(ctx, "trigger", None):
        return
    # A ruled test row travels as its criterion (frame 213, route B). A
    # verdict that contests a check line alone staged no relay, so its
    # criterion reached no Tester (frame 330, pass 4). The query reads the
    # test rows only, so a criterion row of the verdict never hides a test's
    # criterion (review p4 of frame 330, low 1).
    tested = [r["criterion_id"] for r in ctx.conn.execute(
        "SELECT criterion_id FROM tests WHERE criterion_id IS NOT NULL AND id IN "
        "(SELECT value FROM json_each(?))",
        (json.dumps(verdict_rows(ctx.conn, ctx.trigger) or []),))]
    contested = list(dict.fromkeys(
        park_verdict_criteria(ctx.conn, ctx.trigger) + tested))
    if not contested:
        return
    held = [m for m in ctx.outbound
            if m["verb"] == "relay" and m["to_role"] == "terminologist"]
    # A relay of terms keeps its terms, so a term ruled beside a criterion
    # still reaches `relay` (frame 190's design, 2.2.7).
    # The criteria relay is the one the split keyed apart. A relay of terms
    # with a criterion that is no line of the page sorted first, and its
    # terms were replaced (the delta review of 2c602d1b, finding 6).
    crit = [m for m in held if m.get("split") == "terminologist" + CRITERIA_RELAY]
    for m in held:
        if m not in crit:
            m["body_refs"] = [r for r in m["body_refs"] if r not in contested]
    if crit:
        # The relay carries the contested and revised criteria alone. An
        # approved criterion never enters it (the diff review of 0baacf55,
        # finding 2), and nor does any other ref (the delta review of
        # 4ef3bd9f, finding 2).
        # A ruled test row travels as its criterion (frame 213, route B), so
        # that criterion stays beside the contested lines.
        crit[0]["body_refs"] = list(dict.fromkeys(
            list(contested) + [r for r in tested if r in crit[0]["body_refs"]]))
        for m in crit[1:]:
            ctx.outbound.remove(m)
        return
    ctx.outbound.append({
        "id": new_id("m", ctx.conn, offset=len(ctx.outbound)),
        "to_role": "terminologist", "verb": "relay",
        "body_refs": list(contested), "body_text": None,
        "round_no": 0, "cause_id": ctx.trigger,
    })


def check_implementations(g: graph_mod.Graph | None = None) -> list[str]:
    """Boot assertion: every declared read/write edge has a body behind it."""
    g = g or graph_mod.load()
    missing = []
    for edge in g.edges:
        if edge.type not in ("reads", "writes"):
            continue
        if (edge.t, edge.v) not in api.REGISTRY:
            missing.append(f"{edge.s} {edge.type} {edge.t} ({edge.v})")
    return sorted(set(missing))


def check_no_orphan_implementations(g: graph_mod.Graph | None = None) -> list[str]:
    """The mirror: an implementation no edge grants is dead capability."""
    g = g or graph_mod.load()
    declared = {
        (e.t, e.v) for e in g.edges if e.type in ("reads", "writes")
    }
    return sorted(
        f"{artefact}.{verb}" for (artefact, verb) in api.REGISTRY
        if (artefact, verb) not in declared
    )


# The follow check of frame 144. A refusal that names a call records it as
# an `api.Offer`. A test with no model sends that call through `dry_run`, and
# the doors must admit it (frame 135's law: a refusal names only a call that
# the doors then admit). Nothing in a session calls these. `_ON_REFUSAL` is
# None there, and `tests/rota/conftest.py` sets it under pytest only.
_ON_REFUSAL: Callable | None = None

# The ops whose effect is outside `ctx`, and what a dry run does with each.
# `code.write` writes the disk, and `api._code_write` has a dry mode that
# stops before it (frame 136). `code.commit` runs git, and `web.fetch` reads
# the network. Neither has a dry mode, so a dry run does not send them.
_DRY_SKIPS = {
    "code.commit": "code.commit runs git, and git has no dry mode here",
    "web.fetch": "web.fetch reads the network",
}


# Taken at import, so that a test which spies on `api._code_write` counts
# its own calls and not the follow check's.
_CODE_WRITE = api._code_write


class DrySkipped(Exception):
    """A dry run met an op whose effect it cannot hold back."""


# The types whose value a dry run cannot change in place. A path and a row
# of sqlite3 are values, and `copy.deepcopy` cannot copy a row (frame 144's
# review of 8726a13, low 5).
_IMMUTABLE = (str, int, float, bool, type(None), tuple, frozenset, bytes,
              PurePath, sqlite3.Row)
# The leaves that hold no mutable part, so a deep copy keeps them as they are.
_LEAVES = (str, int, float, bool, type(None), bytes, PurePath, sqlite3.Row)


def _deep(v, memo: dict):
    """A deep copy of `v` that keeps a leaf of `_LEAVES` as it is, at any
    depth. `memo` keeps the aliases, as in `copy.deepcopy`."""
    import copy

    if isinstance(v, _LEAVES):
        return v
    if id(v) in memo:
        return memo[id(v)]
    if type(v) is list:
        out: Any = []
        memo[id(v)] = out
        out.extend(_deep(x, memo) for x in v)
    elif type(v) is dict:
        out = {}
        memo[id(v)] = out
        out.update((_deep(k, memo), _deep(x, memo)) for k, x in v.items())
    elif type(v) in (set, frozenset, tuple):
        out = type(v)(_deep(x, memo) for x in v)
        memo[id(v)] = out
    elif isinstance(v, tuple) and hasattr(v, "_make"):
        # A namedtuple can hold a row, and deepcopy cannot copy a row (the
        # review of fed7c58, low 8).
        out = v._make(_deep(x, memo) for x in v)
        memo[id(v)] = out
    elif (not hasattr(type(v), "__deepcopy__")
          and (hasattr(v, "__dict__") or _slots(v))):
        # A plain object: its attributes go through this function, so a row
        # inside it stays the same row.
        out = copy.copy(v)
        memo[id(v)] = out
        if hasattr(v, "__dict__"):
            vars(out).clear()
            vars(out).update(_deep(vars(v), memo))
        for s in _slots(v):
            if hasattr(v, s):
                object.__setattr__(out, s, _deep(getattr(v, s), memo))
    else:
        return copy.deepcopy(v, memo)
    return out


def _slots(v) -> list[str]:
    """The `__slots__` names of `v`'s type and its bases."""
    out = []
    for c in type(v).__mro__:
        s = c.__dict__.get("__slots__", ())
        out += [s] if isinstance(s, str) else [x for x in s
                                                if x not in ("__dict__", "__weakref__")]
    return out


def _ctx_snapshot(ctx: api.Ctx) -> tuple[dict, dict, dict]:
    """The attributes of `ctx`: the objects, a shallow copy of each list,
    dict and set, and one deep copy of them all. One deep copy keeps the
    aliases between attributes. `conn` stays out: no op writes the database
    (the check is in `dry_run`). An attribute of a mutable type that this
    function does not know raises, because its restore would be a guess
    (frame 144's review of c888968, point 4)."""
    import copy

    keep = dict(vars(ctx))
    for k, v in keep.items():
        if k != "conn" and not isinstance(v, _IMMUTABLE + (list, dict, set)):
            raise TypeError(f"ctx.{k} is a {type(v).__name__}, and a dry run "
                            f"cannot restore it")
    shallow = {k: copy.copy(v) for k, v in keep.items()
               if isinstance(v, (list, dict, set))}
    deep = _deep({k: v for k, v in keep.items() if k != "conn"}, {})
    return keep, shallow, deep


def _same(a, b, seen: set | None = None) -> bool:
    """Whether `a`, the object now, holds what its deep copy `b` held. An
    object whose type keeps the default `==` compares by identity, so its
    attributes are compared instead. Then an unchanged object of a type that
    the dry run does not know keeps its identity (frame 144's review of
    8726a13, low 5)."""
    if a is b:
        return True
    if type(a) is not type(b):
        return False
    seen = set() if seen is None else seen
    if (id(a), id(b)) in seen:
        return True
    seen.add((id(a), id(b)))
    if isinstance(a, (list, tuple)):
        return len(a) == len(b) and all(_same(x, y, seen) for x, y in zip(a, b))
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(_same(a[k], b[k], seen) for k in a)
    if type(a).__eq__ is object.__eq__:
        sa = getattr(a, "__dict__", None)
        sb_ = getattr(b, "__dict__", None)
        names = _slots(a)
        if (sa is None or sb_ is None) and not names:
            return False
        if sa is not None and not _same(sa, sb_, seen):
            return False
        # An object with `__slots__` has its values outside `__dict__`
        # (the review of fed7c58, low 8).
        gone = object()
        return all(_same(getattr(a, s, gone), getattr(b, s, gone), seen)
                   if hasattr(a, s) or hasattr(b, s) else True for s in names)
    try:
        return bool(a == b)
    except Exception:                                      # noqa: BLE001
        return False


def _ctx_restore(ctx: api.Ctx, keep: dict, shallow: dict, deep: dict) -> None:
    """Put each attribute back as it was. A list, a dict or a set keeps its
    identity, because the runner and the tests hold `ctx.writes` itself. An
    element keeps its identity too, unless the dry run changed it in place,
    and then its deep copy goes back."""
    for k in list(vars(ctx)):
        if k not in keep:
            delattr(ctx, k)
    for k, orig in keep.items():
        if k in shallow:
            s, d = shallow[k], deep[k]
            if isinstance(orig, list):
                orig[:] = [se if _same(se, de) else de for se, de in zip(s, d)]
            elif isinstance(orig, dict):
                orig.clear()
                orig.update({x: (s[x] if _same(s[x], d[x]) else d[x]) for x in s})
            else:
                orig.clear()
                orig.update(s)
        setattr(ctx, k, orig)


def _fill(args: dict, n: int) -> dict:
    """The offer's arguments, with a fresh id for each `api.INVENT` on an id.
    An invented text or body is the seat's own work, and no fresh value
    stands for it, so the offer is not sent."""
    out = {}
    for k, v in args.items():
        if v is api.INVENT and k == "reason":
            # The reason door reads only the call's own reason, so a stand-in
            # that it admits sends the other doors the seat's call (frame
            # 200, pass 5, fix 2).
            out[k] = (f"x_follow{n} stands in for the seat's reason: the "
                      f"quoted line cannot pass on right code")
            continue
        if v is api.INVENT:
            if k != "id" and not k.endswith("_id"):
                raise DrySkipped(f"the {k} of the offered call is the seat's to write")
            v = f"x_follow{n}_{k}"
        out[k] = v
    return out


def _raise_site(exc: BaseException) -> str:
    """The door that raised `exc`: the statement and its callers up to the
    op, by `api.door_of`. A helper that raises for several doors gives one
    identity per caller (frame 144's review of 8726a13, low 4)."""
    tb, frames = exc.__traceback__, []
    while tb is not None:
        frames.append((tb.tb_frame.f_code, tb.tb_lineno))
        tb = tb.tb_next
    return api.door_of(reversed(frames))


class DryResult(NamedTuple):
    """What a dry run found. `step` is the index of the refused call, 0 for
    the offered op itself, and `site` is the statement that refused it."""
    admitted: bool
    refusal: str | None = None
    call: str | None = None
    step: int | None = None
    site: str = ""


def dry_run(sb: Sandbox, op: str, args: dict, then: tuple = ()) -> DryResult:
    """Send `op(**args)`, then each call of `then`, through the real doors,
    and put `ctx` back as it was.

    The calls run on the real `ctx`, and `_ctx_restore` undoes what they
    staged. Raises `DrySkipped` for an op in `_DRY_SKIPS`, and
    `RuntimeError` when a call changed the database, because the restore
    cannot undo that.
    """
    calls = [(op, args)] + list(then)
    for name, kw in calls:
        if name in _DRY_SKIPS:
            raise DrySkipped(_DRY_SKIPS[name])
    calls = [(name, _fill(kw, n)) for n, (name, kw) in enumerate(calls)]
    ctx = sb.ctx
    keep, shallow, deep = _ctx_snapshot(ctx)
    log = _CALL_LOG.get(id(ctx))
    log_len = None if log is None else len(log)
    changes = ctx.conn.total_changes
    refused = None
    try:
        for n, (name, kw) in enumerate(calls):
            try:
                if name == "code.write":
                    # The disk is outside `ctx`, so the write runs in its own
                    # dry mode, after the binder's argument check.
                    target = getattr(sb["code"], "write")
                    problem = validate_args(target, kw, op=("code", "write"))
                    if problem:
                        raise ArgumentError(f"code.write: {problem}")
                    _CODE_WRITE(ctx, kw["path"], kw["text"],
                                kw.get("start", 0), kw.get("end", -1), dry=True)
                else:
                    sb.call(name, **kw)
            except (ValueError, SandboxError, NotInWorkingSet) as exc:
                refused = DryResult(False, f"{type(exc).__name__}: {exc}",
                                    f"{name}({kw!r})", n, _raise_site(exc))
                break
    finally:
        _ctx_restore(ctx, keep, shallow, deep)
        if log is None:
            _CALL_LOG.pop(id(ctx), None)
        else:
            del log[log_len:]
        if ctx.conn.total_changes != changes:
            raise RuntimeError(f"the dry run of {op} changed the database")
    return refused or DryResult(True)


def _params(sb: Sandbox, op: str) -> set | None:
    """The argument names of `op`, from the seat's own function when the
    mode holds it and from the registry otherwise. None when neither does."""
    art, _, fn = op.partition(".")
    try:
        target = getattr(sb[art], fn)
    except (NotInWorkingSet, AttributeError):
        impl = api.REGISTRY.get((art, _attr_to_verb(fn)))
        if impl is None:
            return None
        target = impl
    return set(inspect.signature(target).parameters) - {"ctx"}


def _span_as_it_is(sb: Sandbox, o) -> dict | None:
    """The arguments of an unsent `code.write` offer with its text replaced
    by the lines that its span holds now. None when the offer holds no span
    or the file is absent."""
    a = o.args
    if o.op != "code.write" or a.get("text") is not api.INVENT:
        return None
    start, end = a.get("start"), a.get("end")
    if not (type(start) is int and type(end) is int and 0 <= start <= end):
        return None
    lines = _worktree_lines(sb.ctx, a.get("path", ""))
    if lines is None or end > len(lines):
        return None
    held = lines[start:end]
    return {**a, "text": "\n".join(held) + "\n" if held else ""}


def held_calls(sb: Sandbox) -> tuple[str, set[str]]:
    """The seat's mode and the calls it holds: the sandbox's own functions,
    narrowed by the wake's `.tools` file when the mode has one.

    A sandbox that a test builds with no wake holds the whole graph of its
    role. The doors read the runtime list through `api._wake_mode_set`, so
    the follower reads the same list, the page acts of a criterion relay
    included (the audit of 2026-10-27, F25; the review of f4951389,
    finding 1)."""
    mode = api._wake_mode_key(sb.ctx)
    have = set(sb.functions())
    narrowed = api._wake_mode_set(sb.ctx)
    return mode, have if narrowed is None else have & set(narrowed)


def follow(sb: Sandbox, dotted: str, kwargs: dict, exc: BaseException,
           offers: list) -> list[dict]:
    """Send each offer of one refusal through `dry_run`. Returns one record
    per offer: the door, the sentence, the refusal, the offered call, and
    the second refusal, which is None when the doors admitted the call.

    Three facts of the offer are checked too: its sentence is in the
    refusal, each argument it names is a parameter of its op (`bad_args`),
    and the seat's mode holds each call it names (`not_in_mode`). A dry run
    that skips its op never reaches the working set, so the mode check
    stands apart from it (frame 135's law; the audit of 2026-10-27, F25).

    A step `api.AGAIN` is the refused call, unchanged. It fails when the
    door that refused it first refuses it again. Another door's refusal of
    it is a fact about the seat's own arguments, which the first call meets
    as well. The door is the raising statement, never the text: the literal
    door names six literals of eight, and the call again meets the same
    door for the other two (frame 144's review of c888968, point 1).
    """
    first = _raise_site(exc)
    mode, held = held_calls(sb)
    # The runtime refuses an op outside the seat's list before any door. So
    # a door that refuses the seat's op met a seat whose list holds it, and
    # an offer of the same op is held. A test sandbox can key another mode
    # than its seat's list (the review of f4951389, finding 2).
    held = held | {dotted}
    out = []
    for o in offers:
        then = tuple((dotted, kwargs) if step == api.AGAIN else step
                     for step in o.then)
        rec = {"door": o.site, "said": o.said, "call": f"{dotted}({kwargs!r})",
               "refusal": str(exc), "raised_at": first,
               "offer": f"{o.op}({o.args!r})",
               "then": [c[0] for c in then], "second": None, "skipped": None,
               "said_in_refusal": o.said in str(exc)}
        bad = []
        for op, args in [(o.op, o.args)] + [s for s in o.then if s != api.AGAIN]:
            names = _params(sb, op)
            if names is not None:
                bad += [f"{op}: {a}" for a in args if a not in names]
        rec["bad_args"] = bad
        # The step AGAIN is the seat's own op, which `held` holds above.
        rec["mode"] = mode
        rec["not_in_mode"] = [op for op in [o.op] + [s[0] for s in o.then
                                                    if s != api.AGAIN]
                              if op not in held]
        try:
            try:
                res = dry_run(sb, o.op, o.args, then)
            except DrySkipped as why:
                rec["skipped"] = str(why)
                same = _span_as_it_is(sb, o)
                if same is None:
                    out.append(rec)
                    continue
                # The text is the seat's to write, and the span is the
                # door's. The span goes to the doors with the lines it holds
                # now, so a door that judges the span alone reads it (frame
                # 144's review of 8726a13, low 6).
                rec["span_only"] = True
                res = dry_run(sb, o.op, same)
        except Exception as crash:                         # noqa: BLE001
            # A crash of one offer is that offer's record. The other offers
            # of the refusal keep theirs (the review of fed7c58, low 9).
            rec["second"] = f"the check crashed: {crash!r}"
            out.append(rec)
            continue
        if not res.admitted:
            if (res.step > 0 and o.then[res.step - 1] == api.AGAIN
                    and res.site != first):
                rec["note"] = f"the call again met another door: {res.refusal}"
            else:
                rec["second"] = res.refusal
                rec["second_call"] = res.call
                rec["second_at"] = res.site
        out.append(rec)
    return out


def _worktree_lines(ctx: api.Ctx, path: str) -> list[str] | None:
    """The current lines of `path` in the batch's worktree, or None."""
    try:
        target = api._within(api._batch_worktree(ctx), path)
    except Exception:                                      # noqa: BLE001
        return None
    if not target.is_file():
        return None
    return target.read_text(encoding="utf-8", errors="replace").splitlines()


def _line_holds(line: str, where: dict) -> tuple[bool, str]:
    """Whether `line` is the line that a `line` fact names. The door records
    the line's text from the syntax tree or the parser, never from the number,
    so a number that counts from 1 reads false (frame 144's review of
    8726a13, high 2).

    The quote must start the stripped line and end at a word boundary, so
    `@dec` does not pass on `@decorate(1)` (the review of fed7c58, low 4).
    A docstring's line starts with its quotes, and its words follow them.
    Those words are cut at 30 characters, so they need no boundary."""
    text = line.strip()
    doc = where.get("docstring")
    if doc:
        m = re.match(r"[rRbBuUfF]{0,2}(\"\"\"|'''|\"|')", text)
        if not m:
            return False, f"the line is {text[:60]!r}, which opens no string"
        text = text[m.end():].lstrip()
    quote = (where.get("quote") or "").strip()
    if quote:
        quote = quote.splitlines()[0].strip()
        # Outside a docstring, the line's head up to its first bracket must
        # be the quote's head, as the decorator door cuts it. A word
        # boundary let `@dec` pass on the line `@dec.b` (the review of
        # ee17f70, low 3).
        if not text.startswith(quote) or (
                not doc and _head_to_bracket(text) != _head_to_bracket(quote)):
            return False, f"the line is {line.strip()[:60]!r}, not {quote!r}"
    return True, ""


def _head_to_bracket(s: str) -> str:
    """The text before the first `(`, as the decorator door records its
    quote."""
    return s.split("(")[0].rstrip()[:60]


def _compiled_line(text: str) -> int | None:
    """The line, counted from 0, at which `compile` refuses `text`, or None
    when it compiles. Python 3.14 gives no `exc.text` for an error of the
    compile stage, so the check compiles the text itself (the review of
    fed7c58, low 3)."""
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            compile(text, "<fact>", "exec", dont_inherit=True)
        except SyntaxError as exc:
            return (exc.lineno or 1) - 1
    return None


def _stmt_span(n, lines: list[str]) -> tuple[int, int]:
    """A statement's span in code.source numbering, as `_code_write` counts
    it: a decorated def starts at its first decorator."""
    import ast
    if isinstance(n, ast.match_case):
        k = n.pattern.lineno - 1
        while k > 0 and not re.match(r"\s*case(?![\w.])", lines[k]):
            k -= 1
        return k, _stmt_span(n.body[-1], lines)[1]
    decs = getattr(n, "decorator_list", None) or []
    return min([n.lineno] + [d.lineno for d in decs]) - 1, n.end_lineno


def _span_holds(lines: list[str], lo: int, hi: int, where: dict) -> tuple[bool, str]:
    """Whether `(lo, hi)` is the syntax tree's span of the statement that the
    refusal names: its type `node`, its `name`, or the point after the
    top-level definition `end_of`. A fact that names none of them is held to
    its bounds only (frame 144's review of 8726a13, high 2)."""
    import ast
    if not any(k in where for k in ("node", "name", "end_of")):
        return True, ""
    try:
        tree = ast.parse("\n".join(lines))
    except Exception:                                      # noqa: BLE001
        return False, "the file does not parse"
    if "end_of" in where:
        name = where["end_of"]
        if name is None:
            ok = lo == hi == len(lines)
            return ok, "" if ok else f"the file ends at {len(lines)}"
        ends = [n.end_lineno for n in tree.body if getattr(n, "name", None) == name]
        ok = lo == hi and hi in ends
        return ok, "" if ok else f"{name} ends at {ends}"
    # A statement named by its type carries its first line. A `match_case`
    # has no line of its own, so `api._head_of` gives it none. Any other
    # empty head is a door that lost its quote, and the check reads it
    # false (the review of ee17f70, low 4).
    if "node" in where and not where.get("head") and where["node"] != "match_case":
        return False, f"the fact names a {where['node']} and no first line"
    seen = []
    for n in ast.walk(tree):
        if not isinstance(n, (ast.stmt, ast.match_case)):
            continue
        if "node" in where and type(n).__name__ != where["node"]:
            continue
        if where.get("name") is not None and getattr(n, "name", None) != where["name"]:
            continue
        # The first line tells a nested statement of the same type from the
        # one named (the review of fed7c58, low 10).
        if where.get("head") and api._head_of(lines, n) != where["head"]:
            continue
        span = _stmt_span(n, lines)
        if span == (lo, hi):
            return True, ""
        seen.append(span)
    return False, f"the statement named has the spans {seen[:4]}"


def _challenge_admitted(ctx: api.Ctx, refs: list, quotes: list) -> bool:
    """
    True when `msg.challenge_tester` on these refs, with these quotes,
    passes the evidence door, the two repeat doors and the green-test door
    of `_bind_send`.

    The revert door names the challenge only where the doors admit it
    (frame 135's law, frame 149's review of 9278be2, finding 5).
    """
    if _sent_this_session(ctx, "tester", "challenge"):
        return False
    try:
        _challenge_evidence(ctx, "tester", refs, " ... ".join(quotes),
                            quotes=quotes)
    except ValueError:
        return False
    return (_same_refs_refusal(ctx, "tester", "challenge", refs) is None
            and _green_at_head_refusal(ctx, refs) is None)


def _stored_runs(ctx: api.Ctx, sha: str) -> dict:
    """The latest stored result of each test of the batch at `sha`. The
    fact checks read the rows here, and not through the door's reader."""
    # Fact F4 leaves this read on `test_runs`. It reads the runs of a past
    # commit, HEAD~1 too, and a later run can supersede those runs. The
    # order is the view's own, `rowid`, scoped to the commit (the F4
    # review, low 4). The query is its own, so the check stays apart from
    # the door's reader (frame 149).
    latest: dict = {}
    for r in ctx.conn.execute(
            "SELECT test_id, result FROM test_runs "
            "WHERE batch_id = ? AND commit_sha = ? ORDER BY rowid",
            (ctx.batch_id, sha)):
        latest[r["test_id"]] = r["result"]
    return latest


def _runs_hold(ctx: api.Ctx, runs: dict, where: dict) -> tuple[bool, str]:
    """Whether `runs` are the stored runs of the commit that a revert
    refusal names. The check reads git and `test_runs` itself, and does not
    call the door's own reader (frame 149)."""
    import subprocess
    from . import worktrees
    try:
        tree = api._batch_worktree(ctx)
    except Exception:                                      # noqa: BLE001
        return False, "the batch has no worktree"
    p = subprocess.run([*worktrees.GIT, "-C", str(tree), "rev-parse", "--verify", "-q",
                        where["at"]], capture_output=True, text=True)
    sha = p.stdout.strip() if p.returncode == 0 else None
    # A name that git cannot resolve names no commit. None equal to None
    # read true before (the review of 9278be2, finding 3).
    if sha is None:
        return False, f"git resolves no commit at {where['at']}"
    if sha != where.get("sha"):
        return False, f"{where['at']} is {sha}, not {where.get('sha')}"
    stored = _stored_runs(ctx, sha)
    if stored != dict(runs):
        return False, f"the stored runs at {sha} are {stored}"
    return True, ""


def _both_hold(ctx: api.Ctx, kind: str, value, where: dict) -> tuple[bool, str]:
    """Whether a `both` or `turns_red` fact of the revert door follows from
    the stored runs of `head` and `back`, computed again here (the review
    of 9278be2, finding 4)."""
    h, b = _stored_runs(ctx, where["head"]), _stored_runs(ctx, where["back"])
    both = set(h) & set(b)
    if kind == "both":
        want = (len(both), sum(1 for t in both if h[t] != "pass"),
                sum(1 for t in both if b[t] != "pass"))
    else:
        want = sorted(t for t in both if h[t] == "pass" and b[t] != "pass")
    ok = tuple(value) == tuple(want)
    return ok, "" if ok else f"the stored runs give {want}"


def check_facts(sb: Sandbox, facts: list) -> list[dict]:
    """Check each fact that a refusal quotes against the state (frame 144,
    change 1(d)). Returns one record per fact, with `ok` and the reason.

    The kinds, each recorded by `api._fact` at the door:

    - `row`: the id names a row, stored or staged this session.
    - `test_path`: the tests row `id` is stored or staged at the path.
    - `file`: the path is a file of the worktree, or with `absent`, is not.
    - `lines`: the file has this many lines now.
    - `line`: the line number is inside the text the sentence speaks of, the
      file now or the `text` given, and that line holds the `quote` that the
      door took from the tree or the parser (`_line_holds`).
    - `line_text`: line `n` of the file now starts with the quoted words.
    - `span`: `(lo, hi)` is the tree's span of the statement that the
      sentence names (`_span_holds`).
    - `arg`: the name is a parameter of `op`.
    - `runs`: the commit `at` names in the worktree is `sha`, and the latest
      run of each test of the batch at `sha` is the result given
      (`_runs_hold`).
    - `both`: `(N, X, Y)`, the tests that ran at `head` and at `back`, and
      how many fail at each. `turns_red`: the tests of those that pass at
      `head` and fail at `back`. Both are computed again (`_both_hold`).
    """
    ctx = sb.ctx
    out = []
    for f in facts:
        w = dict(f.where)
        ok, why = True, ""
        if f.kind == "row":
            staged = any(t != "ledger" and rid == f.value for t, rid, *_ in ctx.writes)
            ok = staged or api.ref_resolves(ctx, f.value)
            why = "" if ok else "no stored or staged row has this id"
        elif f.kind == "test_path":
            row = ctx.conn.execute("SELECT path FROM tests WHERE id = ?",
                                   (w["id"],)).fetchone()
            staged = [r[2].get("path") for r in ctx.writes
                      if r[0] == "tests" and r[1] == w["id"]]
            ok = (row is not None and row["path"] == f.value) or f.value in staged
            why = "" if ok else f"tests row {w['id']} is not at this path"
        elif f.kind == "file":
            lines = _worktree_lines(ctx, f.value)
            ok = (lines is None) if w.get("absent") else (lines is not None)
            why = "" if ok else ("the file exists" if w.get("absent")
                                 else "no such file in the worktree")
        elif f.kind in ("lines", "line", "line_text", "span"):
            text = w.get("text")
            lines = (text.splitlines() if text is not None
                     else _worktree_lines(ctx, w["path"]))
            if lines is None:
                ok, why = False, "the file the sentence speaks of is absent"
            elif f.kind == "lines":
                ok = f.value == len(lines)
                why = "" if ok else f"the file has {len(lines)} lines"
            elif f.kind == "line" and text is not None:
                # The line of a refusal of the parser: compile the text again.
                at = _compiled_line(text)
                ok = at == f.value
                why = "" if ok else f"compile refuses the text at line {at}"
                if ok and 0 <= f.value < len(lines):
                    ok, why = _line_holds(lines[f.value], w)
            elif f.kind == "line":
                ok = 0 <= f.value < len(lines)
                why = "" if ok else f"the text has {len(lines)} lines"
                if ok:
                    ok, why = _line_holds(lines[f.value], w)
            elif f.kind == "line_text":
                n = w["n"]
                ok = 0 <= n < len(lines) and lines[n].rstrip().startswith(f.value)
                why = "" if ok else f"line {n} is not the quoted text"
            else:
                lo, hi = f.value
                ok = 0 <= lo <= hi <= len(lines)
                why = "" if ok else f"the text has {len(lines)} lines"
                if ok:
                    ok, why = _span_holds(lines, lo, hi, w)
        elif f.kind == "arg":
            names = _params(sb, w["op"])
            ok = names is None or f.value in names
            why = "" if ok else f"{w['op']} has no argument {f.value}"
        elif f.kind == "runs":
            ok, why = _runs_hold(ctx, f.value, w)
        elif f.kind in ("both", "turns_red"):
            ok, why = _both_hold(ctx, f.kind, f.value, w)
        else:
            ok, why = False, f"unknown kind {f.kind}"
        out.append({"kind": f.kind, "value": f.value, "where": {
            k: v for k, v in w.items() if k != "text"}, "site": f.site,
            "ok": bool(ok), "why": why})
    return out
