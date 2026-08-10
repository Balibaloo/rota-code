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

import sqlite3
from types import SimpleNamespace
from typing import Any, Callable

from ..roles import api
from ..design import graph as graph_mod


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
    "outcome":    ("constraints_found", "none_found"),
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
    ("findings", "find"): {"status": ("satisfied", "violated")},
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


def _verb_to_attr(verb: str) -> str:
    """`set approval` -> `set_approval`. Graph verbs are prose; Python is not."""
    return verb.replace(" ", "_").replace("-", "_")


def _attr_to_verb(attr: str) -> str:
    """Back the other way, so per-operation rules can be keyed by graph verb."""
    return attr.replace("_", " ")


def build(role: str, conn: sqlite3.Connection, *, mode: str = "normal",
          batch_id: str | None = None, session_id: str = "",
          area: str | None = None,
          entry_id: str | None = None, provenance: str = "decided",
          allow: list[str] | None = None,
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
                  batch_id=batch_id, area=area, entry_id=entry_id, provenance=provenance)

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
    outgoing = [(e.t, e.v) for e in g.of_type("messages") if e.s == role]
    if outgoing:
        fns: dict[str, Callable] = {}
        names: list[str] = []
        for recipient, verb in sorted(set(outgoing)):
            attr = f"{_verb_to_attr(verb)}_{recipient}"
            fns[attr] = _bind_send(ctx, recipient, verb, f"msg.{attr}")
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

    artefacts = {
        name: _Artefact(name, fns, available[name]) for name, fns in grouped.items()
    }
    return Sandbox(role, ctx, artefacts)


def _bind_send(ctx: api.Ctx, recipient: str, verb: str, label: str) -> Callable:
    """
    Stage an outbound message.

    Conclusions travel; reasoning stays home. `refs` carries ids — the recipient
    follows them to whatever it is permitted to read. There is no prose field on
    purpose: a role that wants to explain itself writes a decision and refs it.
    """
    from .runner import new_id

    def send(refs: list[str], round_no: int = 0):
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
        # again. L1 caught Gatekeeper answering a question twice, and once
        # eleven times: the model finishes, does not notice it has finished, and
        # says it again. Telling it afterwards is weaker than making it
        # impossible.
        duplicate = any(
            m["to_role"] == recipient and m["verb"] == verb
            and m["body_refs"] == list(refs or [])
            for m in ctx.outbound
        )
        if duplicate:
            raise ValueError(
                f"you have already sent {verb} to {recipient} with these refs; "
                f"your work for this session is done")

        msg_id = new_id("m", ctx.conn, offset=len(ctx.outbound))
        ctx.outbound.append({
            "id": msg_id, "to_role": recipient, "verb": verb,
            "body_refs": list(refs or []), "round_no": round_no,
            "cause_id": ctx.trigger,
        })
        _CALL_LOG.setdefault(id(ctx), []).append((label, f"refs={refs or []}"))
        return {"id": msg_id, "to": recipient, "verb": verb}

    send.__name__ = label.replace(".", "_")
    send.__doc__ = f"Send a {verb!r} message to {recipient}. refs: list of ids."
    return send


def _bind(impl: Callable, ctx: api.Ctx, label: str) -> Callable:
    """Bind the session context away and record the call as evidence.

    The tool_calls log is a first-class assertion target: "Developer re-read
    exactly the receipt-touched entries" is a query over this.
    """
    import inspect

    def wrapper(**kwargs):
        args_summary = ", ".join(f"{k}={v!r}"[:60] for k, v in sorted(kwargs.items()))
        _CALL_LOG.setdefault(id(ctx), []).append((label, args_summary))
        return impl(ctx, **kwargs)

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
