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

    # `unresolved`: the rung answers the role that asked, and nobody else.
    #
    # Gatekeeper can reach Developer and Tester, so both channels are in the
    # mode, and woken to a thread between Tester and Terminologist it answered
    # Developer five runs out of five. Developer is not in the thread. The asker
    # is on the wake -- it is the sender of the message the wake refers to -- so
    # the other channel is not a temptation to resist, it is a capability with
    # no situation.
    if str(getattr(wake, "kind", "")) == "tick:unresolved" and getattr(wake, "refs", None):
        row = conn.execute(
            "SELECT from_role FROM messages WHERE id = ?", (wake.refs[0],)).fetchone()
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
    return Sandbox(role, ctx, artefacts)


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
        # again. L1 caught Gatekeeper answering a question twice, and once
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
        # exactly one question to Gatekeeper. `llama3.1:8b` asked Terminologist
        # -- one question, wrong owner. `qwen2.5` asked Researcher,
        # Terminologist *and* Gatekeeper: it found the right recipient and
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
        if verb == "question":
            asked = [m["to_role"] for m in ctx.outbound if m["verb"] == "question"]
            if asked and recipient not in asked:
                raise ValueError(
                    f"you have already asked {asked[0]}. Deciding who owns this "
                    f"block is the judgement this mode is for, and you have made "
                    f"it; asking a second role does not confirm it, it produces "
                    f"two answers about one thing")

        duplicate = any(m["to_role"] == recipient and m["verb"] == verb
                        for m in ctx.outbound)
        if duplicate:
            raise ValueError(
                f"you have already sent {verb} to {recipient}; saying it again "
                f"with different refs is a second answer to one question, and "
                f"the recipient has to reconcile them. Your work here is done")

        msg_id = new_id("m", ctx.conn, offset=len(ctx.outbound))
        ctx.outbound.append({
            "id": msg_id, "to_role": recipient, "verb": verb,
            "body_refs": list(refs or []), "body_text": text,
            "round_no": round_no, "cause_id": ctx.trigger,
        })
        _CALL_LOG.setdefault(id(ctx), []).append((label, f"refs={refs or []}"))
        return {"id": msg_id, "to": recipient, "verb": verb}

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
        def send(refs: list[str], question: str, round_no: int = 0):
            if not question:
                raise ValueError(
                    f"{label} needs {prose}=: refs say what you are asking "
                    f"about, and nothing says what you are asking")
            return stage(refs, round_no, text=question)

        # Two reasons a channel carries words, and they used to be conflated.
        # The Researcher shares no database, so an id means nothing at the far
        # end. Every other question channel shares the whole database and still
        # needs words, because a question is about something no artefact holds
        # -- that is what makes it a question. The doc says whichever applies.
        doc = (f"Ask {recipient} a question of fact about something outside this "
               f"repository. It has never seen this project, so say what you "
               f"need to know in words. refs: list of ids, may be empty."
               if recipient == "researcher" else
               f"Ask {recipient} a question. The refs say what it is about; "
               f"`question=` says what you need to know about them, which no "
               f"row holds. refs: list of ids.")
    else:
        def send(refs: list[str], round_no: int = 0):
            return stage(refs, round_no)

        doc = f"Send a {verb!r} message to {recipient}. refs: list of ids."

    send.__name__ = label.replace(".", "_")
    send.__doc__ = doc
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
