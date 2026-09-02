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

import inspect
import re
import sqlite3
from types import SimpleNamespace
from typing import Any, Callable

from ..roles import api
from ..design import graph as graph_mod


# What separates an id from prose is whitespace and length, not shape. The first
# version of this required `prefix_hex`, which is what `new_id` produces and not
# what fixtures use -- `s1`, `i1`, `g1` are ids and were refused, so two scripted
# delivery tests stopped ratifying. A guard that rejects the system's own ids is
# worse than the fabrication it was written to catch.
_ID = re.compile(r"\S{1,64}")


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
    "provenance": ("observed", "decided"),
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
    ("tests", "triage"): {"verdict": ("encodable", "cannot", "ambiguous_word",
                                      "no_machine_check", "outside_fact")},
    ("brief", "intake"): {"verdict": ("work", "chat")},
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
}


def _render_signature(fn: Callable) -> str:
    import inspect

    params = []
    for name, p in inspect.signature(fn).parameters.items():
        if p.default is inspect.Parameter.empty:
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


def validate_args(fn: Callable, kwargs: dict,
                  op: tuple[str, str] | None = None) -> str | None:
    """Return a human-readable problem, or None if the call is well formed."""
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
        return f"missing required argument(s) {missing}; accepts ({_render_signature(fn)})"

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

    checks = {**ENUMS, **(ENUMS_BY_OP.get(op or ("", "")) or {})}
    for key, allowed in checks.items():
        if key in kwargs and isinstance(kwargs[key], str) and kwargs[key] not in allowed:
            return f"{key}={kwargs[key]!r} is not one of {list(allowed)}"

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

    def __init__(self, role: str, ctx: api.Ctx, artefacts: dict[str, _Artefact]):
        self.role = role
        self.ctx = ctx
        self._artefacts = artefacts

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
        return sorted(
            f"{name}.{fn}"
            for name, art in self._artefacts.items()
            for fn in art._available
        )

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
        for name in self.functions():
            artefact, fn = name.split(".", 1)
            impl = getattr(self[artefact], fn)
            out.append(f"{name}({_render_signature(impl)})")
        return out

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
        artefact, fn = dotted.split(".", 1)
        target = getattr(self[artefact], fn)

        if pos:
            kwargs = _bind_positional(target, pos, kwargs, dotted)

        problem = validate_args(target, kwargs, op=(artefact, _attr_to_verb(fn)))
        if problem:
            raise ArgumentError(f"{dotted}: {problem}")

        return target(**kwargs)

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
            "SELECT from_role FROM messages WHERE id = ?", (source,)).fetchone()
        if row is not None:
            asker = row["from_role"]
            keep -= {k for k in keep
                     if k.startswith("msg.answer_") and k != f"msg.answer_{asker}"}

    return keep


def build(role: str, conn: sqlite3.Connection, *, mode: str = "normal",
          batch_id: str | None = None, session_id: str = "",
          area: str | None = None,
          entry_id: str | None = None, provenance: str = "decided",
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
                  provenance=provenance,
                  wake_refs=tuple(getattr(wake, "refs", ()) or ()))

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

    # The bus. One `send` per declared (recipient, verb) pair — a role literally
    # cannot address anyone the graph does not connect it to, so T0-S12's
    # rejection happens by absence rather than by a check at the wire.
    outgoing = [(e.t, e.v, e.prose) for e in g.of_type("messages") if e.s == role]
    if outgoing:
        fns: dict[str, Callable] = {}
        names: list[str] = []
        for recipient, verb, prose in sorted(set(outgoing)):
            attr = f"{_verb_to_attr(verb)}_{recipient}"
            fns[attr] = _bind_send(ctx, recipient, verb, f"msg.{attr}", prose)
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
        if conn.execute("SELECT 1 FROM messages WHERE id = ?", (ref,)).fetchone():
            continue
        if conn.execute("SELECT 1 FROM entries WHERE id = ?", (ref,)).fetchone():
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


# The tables a principal's ruling can name, each with its one writer. The
# single-writer law is what makes the relay's destination a lookup rather than
# a judgement, and `test_the_relay_split_matches_the_graph` keeps this map from
# falling behind the graph the way four hand-written lists did on the inquiry
# route.
RULED_TABLES = {
    "statements": "vision_keeper",
    "items": "vision_keeper",
    "glossary_terms": "terminologist",
    "constraints": "architect",
    "model_areas": "architect",
}


def _owner_of_ref(conn, ref: str) -> str | None:
    """The role that writes the table holding `ref`, or None if no table does."""
    for table, owner in RULED_TABLES.items():
        if conn.execute(f"SELECT 1 FROM {table} WHERE id = ?", (ref,)).fetchone():
            return owner
    return None


# The rows a challenge can quote, and the column that holds their words.
_QUOTABLE = (("criteria", "text"), ("tests", "body"), ("items", "text"),
             ("tickets", "text"), ("glossary_terms", "sense_short"),
             ("constraints", "text"))


def _quotes_span(source: str, text: str, n: int = 12) -> bool:
    """A contiguous span of the source appears verbatim in the message.

    Whitespace-normalised on both sides, because a quote copied across a line
    wrap is still a quote. Twelve characters is enough that matching by
    accident stops happening and short enough that any honest quote clears it.
    """
    src = " ".join((source or "").split())
    msg = " ".join((text or "").split())
    if len(src) <= n:
        return bool(src) and src in msg
    return any(src[i:i + n] in msg for i in range(len(src) - n + 1))


def _challenge_evidence(ctx: api.Ctx, recipient: str, refs, text: str) -> None:
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
    rows: dict[str, tuple[str, str]] = {}
    for r in refs or []:
        for table, col in _QUOTABLE:
            hit = ctx.conn.execute(
                f"SELECT {col} AS words FROM {table} WHERE id = ?",
                (r,)).fetchone()
            if hit:
                rows[r] = (table, hit["words"] or "")
                break

    if recipient == "tester":
        crit = [r for r, (t, _) in rows.items() if t == "criteria"]
        test = [r for r, (t, _) in rows.items() if t == "tests"]
        if not crit or not test:
            missing = "no criterion" if not crit else "no test"
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
                if row:
                    hint = (f". {test[0]}'s criterion is "
                            f"{row['criterion_id']}: send "
                            f"refs=['{row['criterion_id']}', '{test[0]}']")
            raise ValueError(
                f"a challenge to the tester names both sides of the conflict "
                f"in refs -- the criterion and the test -- and yours names "
                f"{missing}{hint}")
        if ctx.batch_id:
            ok = ctx.conn.execute(
                "SELECT 1 FROM batch_tickets bt "
                "JOIN criteria c ON c.ticket_id = bt.ticket_id "
                "WHERE bt.batch_id = ? AND c.id = ?",
                (ctx.batch_id, crit[0])).fetchone()
            if not ok:
                raise ValueError(
                    f"{crit[0]!r} is not a criterion of this batch. The "
                    f"conflict you may challenge is between this batch's "
                    f"test and this batch's criterion")
        for r in (crit[0], test[0]):
            if not _quotes_span(rows[r][1], text):
                raise ValueError(
                    f"quotes= must copy {r}'s exact words and what you sent "
                    f"is not in the {rows[r][0]} row. Quote, not paraphrase: "
                    f"the span of each side your challenge stands on, "
                    f"verbatim -- both rows are in front of you")
        return

    # A quoted test is the Tester's dispute, whoever the challenge names.
    # Measured on the register (CR-a-test-that-encodes-nothing, 2026-09-01):
    # the Critic saw the vacuous test, quoted its body verbatim beside the
    # criterion -- exactly the tester channel's evidence -- and addressed the
    # Developer, whose diff is not what the quote disputes. A test has one
    # writer; the row the quote comes from names the desk.
    quoted_tests = [r for r, (t, words) in rows.items()
                    if t == "tests" and _quotes_span(words, text)]
    if quoted_tests and recipient != "tester":
        crit = [r for r, (t, _) in rows.items() if t == "criteria"]
        pair = [*crit[:1], quoted_tests[0]]
        raise ValueError(
            f"you quoted {quoted_tests[0]}'s body, and a test is the Tester's "
            f"to defend or rewrite -- the {recipient} did not write it. Send "
            f"the same dispute on the tester channel: "
            f"msg.challenge_tester(refs={pair!r}, quotes=...)")

    # Every other channel: whatever text-bearing rows the refs name, at least
    # one must actually be quoted. Vacuously legal when the refs carry no
    # quotable row, because bounded strictness beats a guard with no exit.
    if rows and not any(_quotes_span(words, text)
                        for _, words in rows.values()):
        some = next(iter(rows))
        raise ValueError(
            f"quotes= must contain the disputed row's own words and what you "
            f"sent quotes none of your refs. Copy the span you dispute from "
            f"{some} verbatim, not a paraphrase")


def _bind_send(ctx: api.Ctx, recipient: str, verb: str, label: str,
               prose: str = "") -> Callable:
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

    def stage(refs: list[str], round_no: int = 0, text: str | None = None):
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
        if isinstance(refs, str):
            raise ValueError(
                f"refs is a list of ids and you sent one id as a bare string, "
                f"{refs!r}. A string is a sequence of characters here, so this "
                f"would travel as one ref per letter")

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
        dangling = [r for r in (refs or []) if not api.ref_resolves(ctx, r)]
        if dangling:
            raise ValueError(
                f"{dangling[0][:40]!r} names no row -- not in any table, not "
                f"written this session. Refs are ids from the rows you were "
                f"given or the tools you called; if you mean a thing with no "
                f"row, the thing to send is the row that talks about it")

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

        # One open question per criterion. `tests_missing` fires per batch
        # while any criterion lacks a test, so the mode meets its own routed
        # criteria again on the next wake -- and a re-asked question forks
        # the thread the ladder is already climbing. The triage's next-step
        # says this too; here it stops being skippable.
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
        if verb == "challenge":
            _challenge_evidence(ctx, recipient, refs, text or "")
        if verb in ("challenge", "escalate"):
            # And the same challenge twice is the same argument twice. S0
            # walk eight: nine rounds of challenge, answer, harness, with
            # identical refs every round -- a livelock the attempt cap
            # cannot see because every message is a fresh cause. A held
            # answer means the two of you disagree; the door is above.
            import json as _json
            prior = ctx.conn.execute(
                "SELECT m.id FROM messages m JOIN messages a ON a.cause_id = m.id "
                "WHERE m.from_role = ? AND m.to_role = ? AND m.verb = ? "
                "AND m.body_refs = ? AND a.verb = 'answer' ORDER BY m.seq DESC "
                "LIMIT 1", (ctx.role, recipient, verb,
                            _json.dumps(list(refs or [])))
            ).fetchone()
            if prior:
                # Walk ten: escalate, answer, escalate, answer, three times
                # on one pair of refs, with the fix written into the reply
                # as prose in between. The Architect answered; the answer is
                # the material now.
                if verb == "escalate":
                    door = ("act on the answer -- code.write the change it "
                            "points at and commit; if it truly did not land, "
                            "the attempt cap carries this batch to the ladder")
                elif recipient == "tester":
                    door = "msg.escalate_architect"
                else:
                    door = "schedule.unresolved"
                raise ValueError(
                    f"you sent {verb} to {recipient} on exactly these refs "
                    f"already ({prior['id']}) and they answered. Sending it "
                    f"again is the same argument again -- {door}")

        # The intake fork, armed by the mode: a converse to the principal is
        # either the reply to work (refs carry what intake produced) or a
        # declared chat. Undeclared-and-bare is the measured S0 failure --
        # the greeting answered, the request gone.
        if (verb == "converse" and recipient == "principal"
                and getattr(ctx, "intake", "unarmed") != "unarmed"):
            if ctx.intake is None:
                raise ValueError(
                    "claim the branch first: brief.intake(verdict='work') "
                    "if they asked for anything at all, 'chat' if not. An "
                    "unclaimed reply is how a request dies politely")
            if ctx.intake == "work" and not refs:
                raise ValueError(
                    "you claimed work, so the reply carries refs -- the "
                    "statements you segmented (brief.segment their words, "
                    "then confirm). A bare reply would answer the greeting "
                    "and lose the request")

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
        if verb == "report" and getattr(ctx, "lookup_misses", None) and not any(
                w[0] == "glossary_terms" for w in ctx.writes):
            missing = sorted(ctx.lookup_misses)[0]
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
            prior = [m for m in ctx.outbound if m["verb"] == "question"]
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
        if verb == "present" and getattr(ctx, "wake_refs", None):
            refs += [r for r in ctx.wake_refs
                     if isinstance(r, str) and r and r not in refs]
        # And the same for a ruling's relay, with a stronger warrant: the
        # ruling's refs are the rows the principal ruled on, and the model
        # was choosing among them -- relaying one of two, five runs of five,
        # so half the ruling never reached its owner. Which rows a relay
        # carries is a fact about the wake, not the session's to trim.
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
                refs += [r for r in given
                         if isinstance(r, str) and r and r not in refs]
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

        # One message gets one answer. `api.refuse_second_answer` holds the
        # rule and says why; the three channels that carry an intake answer
        # declare which one they are, and the second is refused rather than
        # reconciled afterwards.
        answer = ({"converse": "chat", "confirm": "work"}.get(verb)
                  if recipient == "principal" else
                  "inquiry" if verb == "ask" else None)
        if answer:
            api.refuse_second_answer(ctx, answer)

        duplicate = any(m["to_role"] == recipient and m["verb"] == verb
                        for m in ctx.outbound)
        if duplicate:
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
            for ref in refs:
                owner = _owner_of_ref(ctx.conn, ref) or recipient
                split.setdefault(owner, []).append(ref)
            already = {m["to_role"] for m in ctx.outbound if m["verb"] == "relay"}
            split = {o: r for o, r in split.items() if o not in already}
            if not split:
                raise ValueError(
                    "every owner these rows belong to has its relay already; "
                    "saying it again is a second answer. Your work here is done")
            recipients = sorted(split)

        msg_id = new_id("m", ctx.conn, offset=len(ctx.outbound))
        for n, to_role in enumerate(recipients):
            ctx.outbound.append({
                "id": msg_id if n == 0
                else new_id("m", ctx.conn, offset=len(ctx.outbound)),
                "to_role": to_role, "verb": verb,
                "body_refs": split.get(to_role, list(refs or [])) if split
                else list(refs or []),
                "body_text": text,
                "round_no": round_no, "cause_id": ctx.trigger,
            })
        _CALL_LOG.setdefault(id(ctx), []).append((label, f"refs={refs or []}"))
        out = {"id": msg_id, "to": recipient, "verb": verb}
        if len(recipients) > 1:
            # Said back, so the session knows it has finished asking. Left
            # unsaid, the model reaches for the other two and meets the
            # duplicate guard, which costs turns and reads as a refusal of
            # something it was told to do.
            out["to"] = recipients
            out["note"] = ("asked every owner; which of them holds the answer "
                           "is not yours to work out. Your work here is done")
        if split:
            out["to"] = {o: split[o] for o in recipients}
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
        ann = "str | list" if verb == "challenge" else "str"
        src = (
            f"def send(refs: list[str], {arg}: {ann}, round_no: int = 0):\n"
            f"    if isinstance({arg}, list):\n"
            f"        {arg} = ' ... '.join(str(x) for x in {arg})\n"
            f"    if not {arg}:\n"
            "        raise ValueError(f'{_label} needs {_prose}=: {_why}')\n"
            f"    return _stage(refs, round_no, text={arg})\n"
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
                            f"this session, and a {own} row is a different "
                            f"thing from it -- if this one would only say "
                            f"that you made that edit, the edit is already "
                            f"the record and nothing more is owed")
                    raise ValueError(
                        f"{kwargs['id']!r} is already a row of {table}; an "
                        f"artefact id is unique across every artefact table, "
                        f"or every ref to it is ambiguous. Prefix it with "
                        f"what it is -- c_ for a criterion, tst_ for a test "
                        f"-- and send again")
        try:
            return impl(ctx, **kwargs)
        except Exception as exc:
            # The session's own refusals, kept where a later call can see
            # them. `surveys.attest` reads this to tell "nothing to write"
            # from "the write was refused", which are different results.
            refusals = getattr(ctx, "refusals", None)
            if refusals is not None:
                refusals.append((label, str(exc)))
            raise

    wrapper.__name__ = label.replace(".", "_")
    wrapper.__doc__ = impl.__doc__
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
