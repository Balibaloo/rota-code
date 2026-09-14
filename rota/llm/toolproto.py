"""
The `TOOL:` text protocol.

Salvaged from Custom_AI_TUI's ChatController (the scanner's quote/paren tracking
is sound and hard-won) and rewritten around dotted names, pydantic validation and
explicit error results.

Doctrine: a malformed call must produce an *error*, never a misparse. A model that
writes garbage should be told so and given another turn; a model whose garbage is
silently reinterpreted as a different valid call is how a role writes something
nobody asked for.

Form:
    TOOL: artefact.verb(key='value', other=3)
    TOOL: artefact.verb({"key": "value"})

Both are accepted because small local models drift between them mid-session.
"""
from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass
from typing import Any

MARKER = "TOOL:"


@dataclass(frozen=True)
class ToolCall:
    name: str
    args: dict[str, Any]
    raw: str = ""
    # Positional arguments, bound against the real signature at dispatch. The
    # parser cannot bind them itself because it does not know what it is
    # calling; rejecting them outright cost two cases every run.
    pos: tuple[Any, ...] = ()


@dataclass(frozen=True)
class ToolError:
    raw: str
    reason: str


# JSON's spelling of the three keywords, and Python's. Models blend the two
# syntaxes constantly — Python keyword arguments carrying `true` rather than
# `True` — because half the tool-calling world is JSON and nothing in the prompt
# says which dialect this is. It is not ambiguous, and it is not worth a fatal
# error: one `default_taken=true` poisoned an entire L3 chain. The Vision Keeper
# spent every remaining turn apologising for it and never sent the message the
# chain existed to test.
_WORDS = {"true": True, "false": False, "null": None,
          "True": True, "False": False, "None": None}


def _bare_path(node: ast.AST) -> bool:
    """`a.b`, `a/b.c`, `a/b/c.d`: names joined by dots and slashes, nothing
    else. A number, a call or a string inside it is not a path."""
    if isinstance(node, ast.Name):
        return True
    if isinstance(node, ast.Attribute):
        return _bare_path(node.value)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        return _bare_path(node.left) and _bare_path(node.right)
    return False


def _literal(node: ast.AST) -> Any:
    """
    `ast.literal_eval`, plus two tolerances, and nothing else.

    Still never `eval`: an LLM-authored argument list is untrusted input, so
    this walks a fixed set of node types and refuses everything else. A model
    writing `body=criteria.load(id='b1')[0]['body']` — which they do — gets a
    tool error, not a nested dispatch.
    """
    if isinstance(node, ast.Name):
        # A bare word. `true`/`false`/`null` mean what JSON means by them;
        # anything else is a string that lost its quotes, which is by far the
        # commonest way a small model malforms an id: `refs=m_dead_75b4f6`.
        return _WORDS[node.id] if node.id in _WORDS else node.id
    if isinstance(node, (ast.Attribute, ast.BinOp)) and _bare_path(node):
        # A path that lost its quotes: `code.source(main.py, 0, 400)`,
        # `code.prose(path=docs/license.md)`. Python reads the first as an
        # attribute and the second as a division; the model meant a file.
        # tipsBE and clickI nights 38 to 40 (2026-09-13) lost turns to
        # "malformed node or string" on exactly this.
        return ast.unparse(node).replace(" ", "")
    if isinstance(node, (ast.List, ast.Tuple)):
        return [_literal(e) for e in node.elts]
    if isinstance(node, ast.Dict):
        if any(k is None for k in node.keys):
            raise ValueError("dict unpacking is not supported")
        return {_literal(k): _literal(v) for k, v in zip(node.keys, node.values)}
    if isinstance(node, ast.Call):
        # `surface_refs=[code.surface(hint='x')]` -- a call composed inline
        # where a value goes. Measured killing L3-scope five runs straight:
        # the model understood *where the data comes from* and not *that it
        # must fetch first*, and the generic malformed-node error never told
        # it. The docstring above always named this case; now the refusal
        # teaches the sequence.
        called = ast.unparse(node.func)
        raise ValueError(
            f"{called}(...) is a call, and arguments take values, not calls. "
            f"Call {called} on its own line first, read what it returns, "
            f"then pass those results as plain strings")

    # A bare name where a value goes is the string it spells. S0 walk
    # thirty-three: the Critic wrote `verdicts.emit(b1, pass, ...)` three
    # sessions running, and the verdict on a green batch never landed.
    # Ids and enum words are strings; nothing else a bare name could mean
    # is a value the sandbox would accept.
    if isinstance(node, ast.Name):
        return node.id
    value = ast.literal_eval(node)
    # `text=...` means "and so on", and `literal_eval` is delighted to hand back
    # Python's Ellipsis for it. It survives the sandbox, survives the write, and
    # dies at commit as `Object of type ellipsis is not JSON serializable` --
    # taking a session that was otherwise sound. A placeholder is not a value.
    if value is Ellipsis:
        raise ValueError("`...` is a placeholder, not a value; write the value")
    return value


def parse_args(args_str: str) -> tuple[dict[str, Any], tuple[Any, ...]]:
    """
    Parse the argument list. JSON object form, or Python keyword form.

    Returns the keyword arguments and any positional ones. Positionals used to
    be rejected here, which was the parser enforcing a rule it had no standing
    to enforce: whether `tests.encode('t1', 'c1', ...)` is well formed depends
    on the signature, and the parser does not know the signature. The sandbox
    does, so it binds them there.
    """
    args_str = args_str.strip()
    if not args_str:
        return {}, ()

    if args_str.startswith("{"):
        parsed = json.loads(args_str)
        if not isinstance(parsed, dict):
            raise ValueError("JSON tool arguments must be an object")
        return parsed, ()

    # Newlines inside a quoted argument would break the expression, so they
    # are escaped before parsing and restored by literal_eval. Newlines
    # *between* arguments are whitespace and stay whitespace: the first
    # version escaped every newline, so a call written one argument per line
    # -- which is how qwen2.5 writes every call -- had `\n` outside any
    # string, failed the strict parse, and fell to the lenient one, which
    # took `term` to be everything to the closing bracket.
    safe = _quote_bare_keywords(_escape_newlines_in_quotes(args_str))
    try:
        expr = ast.parse(f"_f({safe})", mode="eval")
    except SyntaxError:
        # **A prose argument has to be able to carry code, and code is quotes.**
        #
        # The Developer's brief asks it to quote the test body it disputes, so
        # the argument it produces looks like
        #
        #     reason='"the criterion says ..." and "assert f('SKU-1', 25) == ..."'
        #
        # and `ast` stops at `'SKU-1'`, because the inner quote closes the outer
        # one. The call became a `ToolError`, the message was never sent, and
        # `L1-DV-fix-the-code-not-the-test` turned green *because the model
        # could not speak* — a case passing for an accident rather than a
        # reason, produced by an instruction this protocol could not carry.
        #
        # So the instruction stays sayable and the protocol widens. Strict
        # parsing is tried first and is unchanged; only what it rejects reaches
        # here, so nothing that parsed before parses differently now.
        return _parse_args_lenient(safe), ()
    call = expr.body
    if not isinstance(call, ast.Call):
        raise ValueError("not a call expression")

    out: dict[str, Any] = {}
    for kw in call.keywords:
        if kw.arg is None:
            raise ValueError("**kwargs is not supported")
        out[kw.arg] = _literal(kw.value)
    return out, tuple(_literal(a) for a in call.args)


_BARE_KEYWORDS = ("pass",)


def _quote_bare_keywords(text: str) -> str:
    """`result=pass` is a verdict, not a statement. Outside quotes only, so a
    prose argument that mentions passing is left alone."""
    out: list[str] = []
    quote = None
    esc = False
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if quote:
            out.append(ch)
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == quote:
                quote = None
            i += 1
            continue
        if ch in ("'", '"'):
            quote = ch
            out.append(ch)
            i += 1
            continue
        matched = False
        for kw in _BARE_KEYWORDS:
            end = i + len(kw)
            before = text[i - 1] if i > 0 else ""
            after = text[end] if end < n else ""
            if (text.startswith(kw, i) and not (before.isalnum() or before == "_")
                    and not (after.isalnum() or after == "_")):
                out.append(f"'{kw}'")
                i = end
                matched = True
                break
        if not matched:
            out.append(ch)
            i += 1
    return "".join(out)


def _escape_newlines_in_quotes(text: str) -> str:
    out, quote, esc = [], None, False
    for ch in text.replace("\r\n", "\n").replace("\r", "\n"):
        if quote:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == quote:
                quote = None
            if ch == "\n":
                out.append("\\n")
                continue
        else:
            if ch in ("'", '"'):
                quote = ch
            elif ch == "\n":
                out.append(" ")
                continue
        out.append(ch)
    return "".join(out)


def _parse_args_lenient(args_str: str) -> dict:
    """The quote-tolerant fallback. Lives in `_lenient` so the strict grammar
    here stays the thing you read first."""
    from ._lenient import parse_args_lenient

    return parse_args_lenient(args_str, _literal)


def _scan_name(text: str, i: int) -> tuple[str, int]:
    start = i
    while i < len(text) and (text[i].isalnum() or text[i] in "_."):
        i += 1
    return text[start:i], i


_BARE_LIST = None


def _bracket_bare_lists(text: str) -> str:
    """
    `refs=l_1, l_2, l_3` rewritten as `refs=[l_1, l_2, l_3]`.

    clickI night 21 (2026-09-12): woken with seven ledger ids on the wake,
    the Liaison copied them exactly and sent them unbracketed, three turns
    running, "could not read an argument name" each time, and the agenda
    was quarantined. Two or more bare ids in a row, ended by the next
    `name=` or the closing bracket, are a list; a quoted value never
    matches, and `start=1, end=2` does not either because `end` is
    followed by `=`. A slash is part of an id: click night 47 (2026-09-14),
    the observed refs ended `., src/click`, the run broke at the slash, and
    the Liaison's present was refused three times to quarantine.
    """
    import re

    global _BARE_LIST
    if _BARE_LIST is None:
        _BARE_LIST = re.compile(
            r"(?P<key>\b[A-Za-z_][A-Za-z0-9_]*=)"
            r"(?P<ids>[A-Za-z0-9_.@:/-]+(?:\s*,\s*[A-Za-z0-9_.@:/-]+)+)"
            r"(?=\s*(?:,\s*[A-Za-z_][A-Za-z0-9_]*\s*=|\)))")
    # Quoted as it is bracketed: a bare `.` or `src/click` is not Python,
    # and the ids are strings by the model's own reading of the wake.
    def quoted(m):
        ids = ", ".join(repr(x.strip()) for x in m.group("ids").split(","))
        return f"{m.group('key')}[{ids}]"
    return _BARE_LIST.sub(quoted, text)


_BLOCK_ARG = None  # compiled on first use; the module avoids import-time regex


def _inline_blocks(text: str) -> str:
    """
    `key=[key]` + a following raw block, rewritten as the quoted value it is.

    The prompt renders long text results as `[text]` + raw lines, and models
    mirror the shape back when *sending* long text: `code.write(path=...,
    text=[text]` with the source following in the open. The paren scan cannot
    survive arbitrary code, so the call was a ToolError every time -- while
    the model, shown its own turns, reasonably believed it had used the
    house style.

    Narrow on purpose: only `name=[name]` (the label matching the argument),
    only as the last thing on its call line, and the block runs to the next
    `TOOL:` line or the end of the completion. A lone `refs=[...]` list never
    matches -- the sentinel is the *name in brackets*, nothing else.
    """
    import re

    global _BLOCK_ARG
    if _BLOCK_ARG is None:
        _BLOCK_ARG = re.compile(
            r"^(?P<head>\s*TOOL:[^\n]*?(?P<name>[A-Za-z_][A-Za-z0-9_]*)"
            r"=)\[(?P=name)\]\s*\)?\s*$",
            re.MULTILINE)

    out = []
    pos = 0
    for m in _BLOCK_ARG.finditer(text):
        block_start = m.end()
        nxt = text.find("\nTOOL:", block_start)
        block_end = nxt if nxt != -1 else len(text)
        block = text[block_start:block_end].strip("\n")
        if not block:
            continue
        # Trailing lone parenthesis lines belong to the call, not the value.
        lines = block.split("\n")
        while lines and lines[-1].strip() in (")", "')", '")'):
            lines.pop()
        value = "\n".join(lines)
        quoted = "'" + value.replace("\\", "\\\\").replace(
            "'", "\\'").replace("\n", "\\n") + "'"
        out.append(text[pos:m.start()])
        out.append(m.group("head") + quoted + ")")
        pos = block_end
    if not out:
        return text
    out.append(text[pos:])
    return "".join(out)


def extract(text: str, signatures: dict | None = None) -> list[ToolCall | ToolError]:
    """
    Find every `TOOL:` call in a completion, in order.

    Quote- and paren-aware, so an argument containing `)` or a nested call does
    not truncate the scan. Anything that cannot be parsed becomes a ToolError
    carrying the raw text — the model sees its own mistake.
    """
    results: list[ToolCall | ToolError] = []
    text = _bracket_bare_lists(_inline_blocks(text))
    cursor = 0

    while True:
        marker = text.find(MARKER, cursor)
        if marker == -1:
            return results

        i = marker + len(MARKER)
        while i < len(text) and text[i].isspace():
            i += 1

        name, i = _scan_name(text, i)
        if not name:
            results.append(ToolError(text[marker:marker + 60], "no function name after TOOL:"))
            cursor = marker + len(MARKER)
            continue

        while i < len(text) and text[i].isspace():
            i += 1
        # Square brackets where the parentheses go. A define session wrote
        # `TOOL: glossary.amend [term="note", sense_body="..."]` on every one
        # of its twelve turns and was told "missing required argument 'term'"
        # on every one of them -- true, unhelpful, and unlearned. The brackets
        # come from the prompt itself: pushed results are labelled
        # `[code.concordance]`, and the model carried the shape over. The
        # arguments are there and unambiguous; several groups (`[path] [start=0]`)
        # are one list. Read them as the parentheses they stand for.
        if i < len(text) and text[i] == "[" and "." in name:
            groups: list[str] = []
            j = i
            while j < len(text) and text[j] == "[":
                depth_b, k, in_s, in_d, esc = 0, j, False, False, False
                while k < len(text):
                    ch = text[k]
                    if esc:
                        esc = False
                    elif ch == "\\":
                        esc = True
                    elif in_s:
                        in_s = ch != "'"
                    elif in_d:
                        in_d = ch != '"'
                    elif ch == "'":
                        in_s = True
                    elif ch == '"':
                        in_d = True
                    elif ch == "[":
                        depth_b += 1
                    elif ch == "]":
                        depth_b -= 1
                        if depth_b == 0:
                            break
                    k += 1
                if k >= len(text):
                    groups = []
                    break
                groups.append(text[j + 1:k].strip())
                j = k + 1
                while j < len(text) and text[j] in " 	":
                    j += 1
            if groups:
                raw_args = ", ".join(g for g in groups if g)
                try:
                    args, pos = parse_args(raw_args)
                except Exception as exc:
                    results.append(ToolError(
                        f"{MARKER} {name}[{raw_args[:80]}]",
                        f"could not parse arguments: {exc}. Arguments go in "
                        f"round brackets: {name}({raw_args[:60]})"))
                else:
                    results.append(ToolCall(name=name, args=args, pos=pos,
                                            raw=f"{name}({raw_args})"))
                cursor = j
                continue
        if i >= len(text) or text[i] != "(":
            # `TOOL: model.consult` with no parentheses is a call to a function
            # whose arguments are all optional, and it was a parse error. One
            # Architect session spent every one of its twelve turns on it: seven
            # rejections reading "missing argument list", for a call that needed
            # no arguments, and it never reached the write it was woken for.
            #
            # Parsed as `name()` now, so a genuinely incomplete call fails at
            # `validate` instead, which knows the signature and can say *which*
            # argument is missing. A format complaint that cannot name the thing
            # it wants teaches nothing, and the model duly did not learn.
            #
            # The dot is what keeps this honest. Every function here is
            # `artefact.verb`, and without the check `TOOL: TOOL: TOOL:` parsed
            # its own marker as a zero-argument call to `TOOL`.
            if "." in name:
                results.append(ToolCall(name=name, args={}, raw=f"{MARKER} {name}"))
            else:
                results.append(ToolError(f"{MARKER} {name}", "missing argument list"))
            cursor = i if i > cursor else cursor + len(MARKER)
            continue

        depth = 0
        in_single = in_double = escaped = False
        args_start = i + 1
        args_end = None
        while i < len(text):
            ch = text[i]
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif in_single:
                if ch == "'":
                    in_single = False
            elif in_double:
                if ch == '"':
                    in_double = False
            else:
                if ch == "'":
                    in_single = True
                elif ch == '"':
                    in_double = True
                elif ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                    if depth == 0:
                        args_end = i
                        break
            i += 1

        if args_end is None:
            # Say why, or the model retries the same call. tipsAH (2026-09-09):
            # ten writes of main.py refused as "unterminated argument list",
            # the model's own guess was "a multi-line string", and the cause
            # was a quote inside the text closing the string early.
            results.append(ToolError(
                f"{MARKER} {name}(...",
                "unterminated argument list: a quote inside a quoted argument "
                "ended the string early, or a bracket is unbalanced. Source "
                "has quotes of its own: put it between triple quotes, "
                "text='''...''', with the lines as they are, no escaping"))
            cursor = marker + len(MARKER)
            continue

        raw_args = text[args_start:args_end]
        try:
            args, pos = parse_args(raw_args)
        except Exception as exc:
            results.append(ToolError(f"{MARKER} {name}({raw_args[:80]})",
                                     f"could not parse arguments: {exc}"))
        else:
            sig = (signatures or {}).get(name)
            # `_param_sets` hands (required, all); a bare set is accepted too.
            params = sig[1] if isinstance(sig, tuple) and len(sig) == 2 else sig
            swallowed = _swallowed_argument(args, params)
            if swallowed:
                # L1-DV-apply-the-answer (2026-09-12): llama wrote a
                # possessive `'s` inside single-quoted source, the string
                # ended there, the rest of the text rode along inside
                # `path`, and the call was refused for a missing `text`
                # with no word about the quote. Say which quote, and name
                # the block form that needs no quoting at all.
                key, other = swallowed
                # The hint names the argument that carries the source, the
                # longest string, not the one the quote happened to close:
                # night 23, "put criterion_id between triple quotes" for a
                # test whose body broke the list.
                longest = max((k for k, v in args.items() if isinstance(v, str)),
                              key=lambda k: len(args[k]), default=key)
                results.append(ToolError(
                    f"{MARKER} {name}({raw_args[:80]})",
                    f"a quote inside {key} ended it early and the arguments "
                    f"after it ({other}=...) were read as part of {key}. Source "
                    f"has quotes of its own; open {longest} with three single "
                    f"quotes, write every line of the value as it is, and close "
                    f"with three single quotes. No escaping, and no placeholder: "
                    f"the value is the whole text, sent again in full"))
            else:
                results.append(ToolCall(name=name, args=args, pos=pos,
                                        raw=f"{name}({raw_args})"))
        cursor = args_end + 1


_SWALLOW = None


def _swallowed_argument(args: dict, params=None) -> tuple[str, str] | None:
    """The key whose string value carries `', name=` where `name` is one of
    the function's own parameters -- a quote in the value closed it early
    and the next argument was read as text.

    `params` is the function's parameter names. Without them the door
    stays shut: source carries `", nargs=-1` and `', default=` of its own
    (clickI night 20, 2026-09-12: every write of a click helper refused
    for a swallowed `nargs`), and only the signature tells a parameter
    from a keyword in the file.
    """
    import re

    global _SWALLOW
    if _SWALLOW is None:
        _SWALLOW = re.compile(r"""['"]\s*,\s*([A-Za-z_][A-Za-z0-9_]*)\s*=""")
    if not params:
        return None
    for key, value in args.items():
        if isinstance(value, str):
            for m in _SWALLOW.finditer(value):
                other = m.group(1)
                if other in params and other not in args:
                    return key, other
    return None


def _labelled(text: str, allowed: set[str]) -> list[tuple[int, ToolCall, int]]:
    """
    `GLOSSARY.AMEND: id = 1 term = "Charge"` — the marker used as a label.

    A whole class of sessions committed empty like this, with no error logged
    anywhere, because the model read

        TOOL: artefact.verb(key='value')

    and took `TOOL:` for a slot to fill with the tool's name. On a line where
    every other token is a placeholder that is a fair reading, and the result is
    the worst failure shape there is: three well-formed intentions, none of them
    parsed, and a session that looks like a role deciding to do nothing.

    Arguments arrive without brackets or commas, as loose `key = value` pairs
    running to the next key or the end of the line. Values may be quoted or
    bare; a bare one runs until the next `word =`, because prose values are
    common here and `sense_short = billing entity` means both words.
    """
    out: list[tuple[int, ToolCall, int]] = []
    names = "|".join(sorted((re.escape(a) for a in allowed), key=len, reverse=True))
    if not names:
        return out

    # An argument list wraps across lines in real output, so a call runs from
    # its label to the next label or the next blank line — not to end of line.
    # Two spellings of a label: `glossary.amend:` and `[glossary.amend]` --
    # the second is the prompt's own push-block label, which qwen2.5:14b
    # reproduced for every call it made, followed by `key: value` lines, and
    # three one-turn sessions wrote nothing and the word was abandoned.
    # `` `surveys.attest`, outcome="found", citations=[...] `` -- the name in
    # backticks, a comma where the colon goes, the keys in backticks too. One
    # 14B session wrote every call that way and nothing parsed. Backticks
    # around a name at line start or around a key before `=` are stripped
    # before the label is looked for, and a comma after the name is a label as
    # a colon is; prose like "glossary.amend, which ..." has no `key=` behind
    # it and produces no call.
    labels = [(m.start(), (m.group(1) or m.group(2)).lower(), m.end())
              for m in re.finditer(
                  rf"(?im)^[ \t]*(?:\[({names})\][ \t]*:?|({names})[ \t]*[:,])", text)]

    for i, (start, name, from_) in enumerate(labels):
        if name not in allowed:                      # matched in another case
            continue
        to = labels[i + 1][0] if i + 1 < len(labels) else len(text)
        chunk = text[from_:to]
        if gap := re.search(r"\n[ \t]*\n", chunk):
            chunk = chunk[:gap.start()]
        # And never past a marked call: `TOOL: x()` on the next line is its
        # own call, not this label's `TOOL = x()` argument.
        if MARKER in chunk:
            chunk = chunk[:chunk.index(MARKER)]
        # Where this block ends in the text -- the blank line or the marker,
        # not the next label -- so a bare call below it is not counted as
        # inside it.
        to = from_ + len(chunk)

        # `glossary.amend:template_select_modal sense_body='...' sense_short='...'`
        # -- the word glued to the label, then the keyword arguments. A bare
        # token between the label and the first `key=` is the call's first
        # positional argument; the sandbox binds it against the signature,
        # which is how `term` gets its value. One 14B session wrote every
        # amend this way, twice, and closed its area with nothing.
        # The token may be followed by `key=` pairs, by a quoted headline
        # (`glossary.amend: normalizedIntentName "A standardized name ..."`,
        # with `sense_body:` and `sense_short:` lines under it), or by the end
        # of the line. The quoted headline is dropped: the lines under it
        # carry the sense, and a missing body is refused by name.
        # Or by a dash and a headline: `` glossary.amend: `intentnote` -- A file
        # containing ... `` with the lines under it. The token may wear
        # backticks; the headline after a quote or a dash is dropped.
        pos: tuple[Any, ...] = ()
        if lead := re.match(
                r"[ \t]*`?([^\s=,()'\"\[\]:`]+)`?"
                r"(?=[ \t]*,[ \t]*\w+[ \t]*=|[ \t]+(?:\w+[ \t]*=|[\"'\u2014\u2013-])"
                r"|[ \t]*(?:\n|$))", chunk):
            pos = (lead.group(1),)
            chunk = chunk[lead.end():]
            # `glossary.amend: is_under, sense_body="..."` -- a comma between
            # the glued word and the keywords.
            chunk = re.sub(r"^[ \t]*,", "", chunk)
            if headline := re.match(r"[ \t]*[\"'\u2014\u2013-][^\n]*(?=\n|$)", chunk):
                chunk = chunk[headline.end():]

        # A table under the label: a header row of parameter names, then one
        # row per call -- `term | sense_body | sense_short` and the rows under
        # it, which is how llama3.1:8b wrote every amend of one survey session,
        # three sessions running, and the area was abandoned. The header names
        # the keys, so each row is a complete call.
        table = re.match(
            r"[ \t]*\n?[ \t]*\|?[ \t]*(\w+(?:[ \t]*\|[ \t]*\w+)+)[ \t]*\|?[ \t]*\n",
            chunk)
        if table:
            header = [h.strip() for h in table.group(1).split("|")]
            rows_text = chunk[table.end():]
            for line in rows_text.split("\n"):
                line = line.strip()
                if not line or set(line) <= set("|-: "):
                    continue
                cells = [c.strip() for c in line.strip("|").split("|")]
                if len(cells) < 2:
                    continue
                row_args = {k: v for k, v in zip(header, cells) if v}
                if row_args and set(row_args) >= {header[0]}:
                    out.append((start, ToolCall(
                        name=name, args=row_args,
                        raw=f"{name}({' | '.join(cells)[:60]})"), to))
            continue

        args: dict[str, Any] = {}
        for a in re.finditer(
                r"""(?s)(\w+)[ \t]*=[ \t]*("[^"]*"|'[^']*'|.+?(?=\s+\w+[ \t]*=|\Z))""",
                chunk):
            raw = a.group(2).strip()
            if raw[:1] in "\"'" and raw[-1:] == raw[:1]:
                args[a.group(1)] = raw[1:-1]
            else:
                args[a.group(1)] = _WORDS.get(raw, raw)

        # The other spelling of the same shape: one `key: value` per line under
        # the label, which is how a per-area session wrote every amend in one
        # run -- `glossary.amend:` then `term: ...`, `sense_body: ...`,
        # `sense_short: ...` -- and committed nothing. Keys at line start only,
        # so a colon inside prose or a URL does not split a value.
        if not args:
            for a in re.finditer(
                    r"(?ms)^[ \t]*(\w+)[ \t]*:[ \t]*(.+?)(?=\n[ \t]*\w+[ \t]*:|\Z)",
                    chunk):
                raw = a.group(2).strip()
                if not raw:
                    continue
                if raw[:1] in "\"'" and raw[-1:] == raw[:1]:
                    args[a.group(1)] = raw[1:-1]
                else:
                    args[a.group(1)] = _WORDS.get(raw, raw)

        # A name followed by arguments is an intention; a name followed by a
        # sentence is the model narrating. Only the first may dispatch.
        if args:
            out.append((start, ToolCall(name=name, args=args, pos=pos,
                                        raw=f"{name}({' '.join(chunk.split())[:60]})"),
                        to))
    return out


def _unlabelled(text: str, signatures: dict,
                taken: list[tuple[int, int]]) -> list[tuple[int, ToolCall]]:
    """
    Bare argument lines with no function named at all -- and exactly one
    function in the working set that takes exactly those keys.

    qwen2.5:14b ended every survey session with

        outcome="found"
        citations=["src/intents/index.ts", "src/variables/index.ts"]

    or, the next run, the same on one line --

        outcome="found", citations=["src/intents/index.ts"]

    and nothing else: the attestation, minus the words `surveys.attest`. The
    arguments name the function when only one function takes them, and the
    sandbox's signatures say which. Two functions that could both take the keys
    is ambiguity, and ambiguity is not parsed. A block is consecutive lines
    that each begin `key =` or `key:`; each line is read as an argument list,
    so the one-line spelling and the one-per-line spelling are the same block.
    A block that sits under a label line, or inside a call already taken, is
    that call's arguments and is not read twice.
    """
    if not signatures:
        return []
    out: list[tuple[int, ToolCall]] = []
    head_re = re.compile(r"^[ \t]*([A-Za-z_]\w*)[ \t]*(=|:)[ \t]*(.+?)[ \t]*$")
    names = "|".join(sorted((re.escape(n) for n in signatures), key=len, reverse=True))
    label_re = re.compile(
        rf"(?i)^[ \t]*(?:\[(?:{names})\][ \t]*:?|(?:{names})[ \t]*:)[ \t]*$")

    def inside(pos: int) -> bool:
        return any(a <= pos < b for a, b in taken)

    def line_args(line: str) -> dict:
        m = head_re.match(line)
        if not m or "(" in m.group(1):
            return {}
        if m.group(2) == "=":
            try:
                kw, pos = parse_args(line.strip().rstrip(","))
                if kw and not pos:
                    return kw
            except Exception:
                pass
        raw = m.group(3).strip().rstrip(",")
        try:
            return {m.group(1): _literal(ast.parse(raw, mode="eval").body)}
        except Exception:
            return {m.group(1): _WORDS.get(raw, raw.strip("\"'"))}

    lines = text.split("\n")
    pos, i = 0, 0
    while i < len(lines):
        block: dict = {}
        start_pos, j = pos, i
        while j < len(lines):
            kw = line_args(lines[j])
            if not kw:
                break
            for k, v in kw.items():
                # `citations="a"` then `citations="b"` on the next line: one
                # key, written once per value, is that key's list.
                if k in block:
                    prev = block[k]
                    block[k] = (prev if isinstance(prev, list) else [prev]) + (
                        v if isinstance(v, list) else [v])
                else:
                    block[k] = v
            j += 1
        under_label = i > 0 and bool(label_re.match(lines[i - 1]))
        if len(block) >= 2 and not inside(start_pos) and not under_label:
            keys = set(block)
            fits = [name for name, (req, all_) in signatures.items()
                    if req <= keys <= all_]
            if len(fits) == 1:
                out.append((start_pos, ToolCall(
                    name=fits[0], args=block,
                    raw=f"{fits[0]}({', '.join(sorted(keys))})")))
        step = max(1, j - i)
        for k in range(i, i + step):
            pos += len(lines[k]) + 1
        i += step
    return out


def extract_lenient(text: str, allowed: set[str],
                    signatures: dict | None = None) -> list[ToolCall | ToolError]:
    """
    `extract`, plus fallbacks for completions that mishandle the marker.

    Small local models omit the prefix constantly — they emit a bare
    `transcript.append(id='u1', ...)` on its own line. Strict parsing turns that
    into a silent no-op session: nothing parses, nothing is written, and the
    session commits empty, which is the worst possible failure because it looks
    like success.

    The fallbacks are narrow enough to stay safe: a call is only recognised if
    its name is **already in the role's working set**. Prose cannot accidentally
    match `criteria.load(...)`, and a hallucinated function still fails
    validation rather than sneaking through. Marker-prefixed calls always win;
    the fallbacks only run when the completion has no markers at all.
    """
    # `` `surveys.attest`, outcome="found" `` -- the name in backticks, a comma
    # where the colon goes, the keys in backticks too: one 14B session wrote
    # every call that way and nothing parsed. Backticks around a working-set
    # name at line start, or around a key before `=`, are stripped before any
    # pass looks; every pass then sees the same text and the same positions.
    if allowed and ("`" in text or any(ch.isupper() for ch in text)):
        names = "|".join(sorted((re.escape(a) for a in allowed), key=len, reverse=True))
        text = re.sub(rf"(?im)^([ \t]*)`({names})`", r"\1\2", text)
        text = re.sub(r"`(\w+)`(?=[ \t]*=)", r"\1", text)
        # `[glossary.amend term="..." sense_body="..."]` -- the whole call
        # inside one bracket. The opening becomes a label; the stray closing
        # bracket after the final quote matches no argument and is inert.
        text = re.sub(rf"(?im)^([ \t]*)\[({names})[ \t]+", r"\1\2: ", text)
        # `MODEL.AMEND(headline=...)` -- the name in capitals, one root-area
        # session, two constraints written and none taken. A working-set name
        # at line start, in any case, is that name.
        text = re.sub(rf"(?im)^([ \t]*)({names})(?=[ \t]*[\(:\[,])",
                      lambda m: m.group(1) + m.group(2).lower(), text)

    marked = extract(text, signatures)

    # Marked calls used to win outright: if the completion had any `TOOL:`
    # line, a bare `name(...)` elsewhere in it was prose. Measured otherwise on
    # the first orientation session of the phase design: four
    # `problem.assert(id=..., text=..., kind='in_scope')` lines, each complete
    # and well-formed, written as bullets under an account, and one marked
    # `surveys.attest` at the end. The attest ran, the four items did not, and
    # the record said the program had nothing in it. A bare call that names a
    # function in the working set and parses is a call; the position check
    # below keeps it from double-counting the marked ones, and validation still
    # refuses anything outside the namespace.
    spans = []
    if marked:
        for m in marked:
            raw = getattr(m, "raw", "") or ""
            i = text.find(raw) if raw else -1
            if i >= 0:
                spans.append((i, i + len(raw)))

    def inside_marked(pos: int) -> bool:
        return any(a <= pos < b for a, b in spans)

    labelled_all = [] if marked else _labelled(text, allowed)
    labelled_spans = [(a, b) for a, _, b in labelled_all]

    def inside_labelled(pos: int) -> bool:
        return any(a <= pos < b for a, b in labelled_spans)

    # Collect with positions and sort by them: call order is semantic. An intake
    # session must append the entry before segmenting it, so returning calls
    # in name order would invert the only sequence that matters.
    found: list[tuple[int, ToolCall]] = []
    bare_spans: list[tuple[int, int]] = []
    for name in sorted(allowed, key=len, reverse=True):
        start = 0
        while True:
            idx = text.find(name + "(", start)
            if idx == -1:
                break
            if idx > 0 and (text[idx - 1].isalnum() or text[idx - 1] in "_."):
                start = idx + 1                      # part of a longer identifier
                continue
            if inside_marked(idx) or inside_labelled(idx):
                start = idx + 1                      # already taken as a marked call
                continue
            # Beside marked calls, a bare one counts only at the start of its
            # own line -- after a bullet or a number, as the orientation wrote
            # them -- and never mid-sentence. "prose mentioning
            # transcript.append(id='x') inline" is prose, and the marked-calls
            # rule existed to keep it so; a list of complete calls under an
            # account is not prose, and it was being thrown away.
            if marked:
                line_start = text.rfind("\n", 0, idx) + 1
                lead = text[line_start:idx]
                if lead.strip(" \t*-+•0123456789.)"):
                    start = idx + 1
                    continue
            parsed = extract(f"{MARKER} {text[idx:]}")
            if parsed and isinstance(parsed[0], ToolCall):
                found.append((idx, parsed[0]))
                bare_spans.append((idx, idx + len(parsed[0].raw)))
                start = idx + len(parsed[0].raw)
            else:
                start = idx + 1

    if marked:
        # Marked, bare and labelled together, in text order. Errors among the
        # marked calls keep their place: the model sees its own mistake either
        # way. A labelled block is taken on the same terms as a bare call --
        # at line start, which the label regex already requires.
        positioned: list[tuple[int, object]] = list(found)
        labelled_here = [(i, c, e) for i, c, e in _labelled(text, allowed)
                         if not inside_marked(i)]
        positioned += [(i, c) for i, c, _ in labelled_here]
        taken = spans + bare_spans + [(i, e) for i, _, e in labelled_here]
        positioned += _unlabelled(text, signatures or {}, taken)
        cursor = 0
        for m in marked:
            raw = getattr(m, "raw", "") or ""
            i = text.find(raw, cursor) if raw else -1
            if i < 0:
                i = cursor
            positioned.append((i, m))
            cursor = max(cursor, i + 1)
        return [c for _, c in sorted(positioned, key=lambda pair: pair[0])]

    # No marker: labelled blocks, bare calls outside them, and bare argument
    # lines beside both -- the amends as labels and the attest as a bare call
    # was one session's whole output, and the attest was being dropped.
    found += [(i, c) for i, c, _ in labelled_all]
    found += _unlabelled(text, signatures or {}, bare_spans + labelled_spans)
    return [call for _, call in sorted(found, key=lambda pair: pair[0])]


def validate(call: ToolCall, allowed: set[str]) -> ToolError | None:
    """Reject anything outside the role's namespace before dispatch."""
    if "." not in call.name:
        return ToolError(call.raw, f"{call.name!r} is not an artefact.verb name")
    if call.name not in allowed:
        return ToolError(
            call.raw,
            f"{call.name!r} is not in this role's working set; "
            f"available: {', '.join(sorted(allowed))}",
        )
    return None
