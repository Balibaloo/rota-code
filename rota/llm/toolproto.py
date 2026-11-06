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
import io
import json
import re
import tokenize
import warnings
from dataclasses import dataclass
from typing import Any

MARKER = "TOOL:"

# A result line the model wrote for itself: `OK code.source -> ...` or
# `ERROR tests.run: ...`. It lives beside MARKER because the stream reader in
# llm.py stops on it, and llm.py cannot import the runner (frame 232). On one
# line, `.match` tests the line head. The runner searches whole replies, so
# the flag stays.
INVENTED_RESULT = re.compile(r"^\s*(?:OK|ERROR)\s+[a-z_]+\.[a-z_]+\s*(?:->|:)",
                             re.MULTILINE)


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



def _rescan_args(text: str, start: int, marker: str,
                 joined: list | None = None) -> int | None:
    """A second scan of an argument list the first one could not close.

    Triple quotes are one token here, so a lone quote inside them does not
    flip the state. The answer is accepted only when `parse_args` parses
    what it encloses. When the guard on joined strings refuses the answer,
    the refusal goes into `joined`, so `extract` can send its reason."""
    i, depth = start, 1
    quote = None            # the active string delimiter: ', ", ''', or """
    while i < len(text):
        ch = text[i]
        if quote:
            if text.startswith(quote, i):
                i += len(quote)
                quote = None
                continue
            # A backslash escapes the next character in a triple value too,
            # as Python and the newline escape read it (frame 151, the
            # review of e78545a, finding 2).
            if ch == chr(92):
                i += 2
                continue
        else:
            if text.startswith("'''", i) or text.startswith('"""', i):
                quote = text[i:i + 3]
                i += 3
                continue
            if ch in ("'", '"'):
                quote = ch
            elif ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    break
        i += 1
    # The last closing bracket is not a candidate: a value that swallowed
    # its neighbours can still parse, and the refusal with its hint is worth
    # more than a call with the wrong arguments (test_toolproto_quotes).
    if depth == 0 and i < len(text):
        try:
            parse_args(text[start:i])
            return i
        except JoinedStrings as exc:
            if joined is not None:
                joined.append(exc)
            return None
        except Exception:
            return None
    return None


# A function with one of these parameters writes source or a file. Frame
# 122's second review: the third reading never yields a call to one.
_WRITES = frozenset({"text", "body", "path"})


def _third_reading(text: str, start: int) -> tuple[str, int] | None:
    """A third scan, for the two forms frame 122 read on night 115.

    Critic s86 to s88 sent each form, and the parser refused each one
    until the session ended. Neither form has a second reading.

    - An apostrophe between two letters inside a single-quoted value is
      text. Python never lets a letter follow a closing quote here.
    - A triple-quoted value inside one more quote, `"'''...'''\\"`, is the
      triple-quoted value. The outer quote must close as `\\"`. With a
      plain `"`, Python reads a string that holds the triple quotes.

    A wrong write is worse than a refusal (frame 122's review: the first
    version joined `''` into nothing). So every doubt is a refusal:

    - One of the two rules must apply, or the reading adds nothing.
    - A string value is one token. Only a comma, a closing bracket or
      white space may follow it.
    - A value that holds an apostrophe is the last argument. Only white
      space may follow its closing quote, before the closing bracket.
    - Only white space may follow the call, up to the next `TOOL:` line.
      One exception: a stray `")` after a wrapped value that closed as
      `\\"`, as s86 wrote on turns 4 to 6.

    The answer is the rewritten argument list and the offset of the
    closing bracket in `text`. It stands only when `parse_args` parses it.
    """
    out: list[str] = []
    i, depth, square = start, 1, 0
    quote = None            # the active string delimiter: ', ", ''', or """
    wrap = None             # the outer quote around a triple-quoted value
    apostrophe = False      # the open value holds an apostrophe
    used_apostrophe = False
    stray = None            # the tail a wrapped value that closed as \" allows
    used = False
    while i < len(text):
        ch = text[i]
        if quote:
            if ch == "\\":
                out.append(text[i:i + 2])
                i += 2
                continue
            if text.startswith(quote, i):
                if (quote == "'" and not wrap and out
                        and out[-1][-1:].isalnum()
                        and text[i + 1:i + 2].isalnum()):
                    out.append("\\'")
                    i += 1
                    apostrophe = used = used_apostrophe = True
                    continue
                out.append(quote)
                i += len(quote)
                if wrap:
                    if not text.startswith("\\" + wrap, i):
                        return None
                    i += 2
                    stray = wrap + ")"
                j = i
                while j < len(text) and text[j].isspace():
                    j += 1
                follow = text[j:j + 1]
                if follow not in (",", ")", "]"):
                    return None
                if apostrophe and (follow != ")" or depth != 1 or square):
                    return None
                quote = wrap = None
                apostrophe = False
                continue
            out.append(ch)
            i += 1
            continue
        head = text[i + 1:i + 4]
        if ch in "'\"" and head in ("'''", '"""') and head[0] != ch:
            wrap, quote = ch, head
            used = True
            out.append(head)
            i += 4
            continue
        if text.startswith("'''", i) or text.startswith('"""', i):
            quote = text[i:i + 3]
            out.append(quote)
            i += 3
            continue
        if ch in ("'", '"'):
            quote = ch
        elif ch == "[":
            square += 1
        elif ch == "]":
            square -= 1
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                break
        out.append(ch)
        i += 1
    if not used or depth != 0 or i >= len(text):
        return None
    after = text[i + 1:]
    following = re.search(r"\n[ \t]*" + re.escape(MARKER), after)
    tail = (after[:following.start()] if following else after).strip()
    if tail and (used_apostrophe or tail != stray):
        return None
    raw = "".join(out)
    # The rewritten list must be strict Python, because the lenient parse
    # guesses. `ast.parse` accepts a key given twice, so count the keys
    # (frame 122's second review: `path='a.py', ..., path='a'it'`).
    try:
        safe = _quote_bare_keywords(_escape_newlines_in_quotes(raw))
        keys = [k.arg for k in ast.parse(f"_f({safe})", mode="eval").body.keywords]
        parse_args(raw)
    except Exception:
        return None
    if len(keys) != len(set(keys)):
        return None
    return raw, i


def _stray_quote(raw: str, params) -> tuple[str, bool] | None:
    """The argument that holds the first stray quote, read from the left.

    A quote closes a value only where a comma or the end of the list
    follows it. A closing quote with other text after it is a stray quote
    in that value. The lenient parse reads from the right, so the first
    value swallows the rest, and the old refusal named the first argument.
    Night 119, s229: the stray quote was in `why`, and the refusal named
    `citation` (frame 122, pass 4).

    The answer is the name, and whether the value opens with an extra
    quote. The answer is None on every
    doubt: a name the function lacks, no name before a value, a value
    that never closes, or text after a value that is not a quote.
    """
    i, n = 0, len(raw)
    while True:
        while i < n and (raw[i].isspace() or raw[i] == ","):
            i += 1
        if i >= n:
            return None
        m = re.match(r"([A-Za-z_]\w*)\s*=\s*", raw[i:])
        if not m:
            return None
        name, i = m.group(1), i + m.end()
        # Frame 122's fourth review: `', mode='` inside a quote is text
        # when the function has no `mode`. The stray quote then stands
        # before it, so the scan cannot name the value.
        if name not in params:
            return None
        if i >= n:
            return None
        begin = i
        if raw.startswith("'''", i) or raw.startswith('"""', i):
            end = raw.find(raw[i:i + 3], i + 3)
            if end < 0:
                return None
            i = end + 3
        elif raw[i] in "'\"":
            quote, i = raw[i], i + 1
            while i < n and raw[i] != quote:
                i += 2 if raw[i] == "\\" else 1
            if i >= n:
                return None
            i += 1
        elif raw[i] in "[{(":
            # A list or a dict. Inside it, a quote closes an item only
            # where a separator or a closing bracket follows it.
            depth, quote = 0, None
            while i < n:
                ch = raw[i]
                if quote:
                    if ch == "\\":
                        i += 2
                        continue
                    if ch == quote:
                        quote = None
                        rest = raw[i + 1:].lstrip()
                        if not rest:
                            return None
                        if rest[0] not in ",:]})":
                            return name, False
                elif ch in "'\"":
                    quote = ch
                elif ch in "[{(":
                    depth += 1
                elif ch in "]})":
                    depth -= 1
                    if depth == 0:
                        i += 1
                        break
                i += 1
            if depth != 0 or quote:
                return None
        else:
            while i < n and raw[i] != ",":
                if raw[i] in "'\"()[]{}":
                    return None
                i += 1
            continue
        rest = raw[i:].lstrip()
        if rest and rest[0] != ",":
            # Text after the closing quote of a quoted value means that
            # quote was stray. Text after a bracket is another fault.
            if raw[i - 1] not in "'\"":
                return None
            return name, _extra_quote(raw, begin)
        i = n - len(rest)


def _extra_quote(raw: str, begin: int) -> bool:
    """Whether the value at `begin` opens with exactly two or four quotes.

    Night 119, s229 turn 9 sent `quote=''def ...''`, and night 118, s241
    turn 7 sent `about_ref=''''...''''`. A seat that keeps the extra quote
    inside triple quotes is refused again (frame 122's fourth review).

    The closing run decides nothing. Frame 122's fifth review: a value can
    end with a quote of its own, `'''say 'hi''''`, and the scan can end a
    value in the next call. A run of five or more is left alone: a value
    that opens with a docstring opens with six (frame 122's sixth review).
    An empty `''` closes before a comma, so the scan never names it.
    """
    q = raw[begin]
    opening = len(raw[begin:]) - len(raw[begin:].lstrip(q))
    return opening in (2, 4)


def _open_argument(text: str, start: int) -> str | None:
    """The argument whose quoted value never ends, by the first scan's rules.

    The name is the last `name=` at the top level before that value opened.
    """
    last_key = opened_key = None
    after_comma = False
    depth = 1
    in_single = in_double = escaped = False
    i = start
    while i < len(text):
        ch = text[i]
        if escaped:
            escaped = False
        elif ch == "\\":
            escaped = True
        elif in_single:
            in_single = ch != "'"
        elif in_double:
            in_double = ch != '"'
        elif ch in "'\"":
            in_single, in_double = ch == "'", ch == '"'
            # A quote after a comma opens a new value with no name. A quote
            # inside a tuple or a call is not the named value itself.
            opened_key = None if after_comma or depth != 1 else last_key
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == "," and depth == 1:
            after_comma = True
        elif ch == "=" and depth == 1:
            m = re.search(r"([A-Za-z_]\w*)\s*$", text[start:i])
            if m:
                last_key, after_comma = m.group(1), False
        i += 1
    return opened_key if in_single or in_double else None


# A swallowed argument inside a string: `, words='` or `, words=` at its end.
_NEXT_ARGUMENT = re.compile(r",\s*([A-Za-z_]\w*)\s*=\s*(?:['\"\[{(\d]|$)")


def _missing_close(text: str, start: int,
                   params: set | None
                   ) -> tuple[str | None, bool, str, int, str] | None:
    """The string whose closing quote is missing, by the first scan's rules.

    Night 151, s226 turns 2 to 6 sent `5: "approve}, words='...'`. The
    string ran from `"approve` into `words`, and the refusal said a quote
    inside closed it early. The seat looked for an inner quote five times.
    A string that holds `, name=` holds the next argument, so its own
    closing quote is missing. The answer is the argument that holds the
    string, whether the string sits inside a bracket, the string's text
    from its quote up to the swallowed name, the quote's offset after the
    open bracket, and the swallowed `, name=`. A name the function lacks
    is code in a value, not an argument.
    """
    last_key = None
    after_comma = False
    brackets: list[str] = []
    quote = None
    opened, opened_key, inner = 0, None, False
    escaped = False
    i = start
    while i < len(text):
        ch = text[i]
        if escaped:
            escaped = False
        elif ch == "\\":
            escaped = True
        elif quote is not None:
            if ch == quote:
                closer, quote = quote, None
                follow = text[i + 1:].lstrip()[:1]
                for m in _NEXT_ARGUMENT.finditer(text, opened + 1, i):
                    # `f(a, b='x')` in a value ends a string at `b=`. Only
                    # a name the function takes passes with no value after,
                    # and only when words, not a comma, follow the quote.
                    bare = m.end() == i and m.group(0)[-1] not in "'\"[{(0123456789"
                    if bare and (not params or follow in ",)]}:"):
                        continue
                    if params and m.group(1) not in params:
                        continue
                    # `donif=` before the string is a piece of a value.
                    if params and opened_key and opened_key not in params:
                        return None
                    # The text before the string must read as the start of
                    # the call. Else a quote inside an earlier value closed
                    # it early, as `text='itx', tit:'`, and the string is
                    # a piece of that value (frame 266, the fuzz slice).
                    shut = "".join({"(": ")", "[": "]", "{": "}"}[b]
                                   for b in reversed(opened_brackets))
                    # A number stands for the string. Two strings side by
                    # side join, so a string there would hide `'a''`.
                    try:
                        ast.parse(f"f({text[start:opened]} 0{shut})")
                    except (SyntaxError, ValueError):
                        return None
                    # The head stops before the swallowed `, name=`, so the
                    # seat sees where the quote belongs (review 1, finding 3).
                    head = text[opened:min(m.start(), opened + 20)].rstrip()
                    return (opened_key, inner, head, opened - start,
                            f", {m.group(1)}=")
                # A string that ends where no value can end, as `'it'x`,
                # had a quote inside close it early. The strings after it
                # are its pieces, so no missing quote can be read (frame
                # 266: the fuzz slice moved 424 reads before this check).
                if follow and follow not in ",)]}:" + closer:
                    return None
        elif ch in "'\"":
            quote, opened = ch, i
            opened_brackets = list(brackets)
            # A string inside a dict or a list belongs to the argument
            # that holds the bracket. A bare string after a comma has none.
            inner = bool(brackets)
            opened_key = last_key if inner or not after_comma else None
        elif ch in "([{":
            brackets.append(ch)
        elif ch in ")]}":
            if not brackets:
                return None
            brackets.pop()
        elif ch == "," and not brackets:
            after_comma = True
        elif ch == "=" and not brackets:
            m = re.search(r"([A-Za-z_]\w*)\s*$", text[start:i])
            if m:
                last_key, after_comma = m.group(1), False
        i += 1
    return None


_COUNT_WORDS = ("none", "one", "two", "three")


def _short_close(text: str, start: int,
                 params: set | None) -> tuple[str, str, int, int] | None:
    """The last argument whose closing quote run is shorter than its open.

    Night 152, s245 to s247 sent `why='''...'')` fourteen times. The old
    refusal named a quote inside the value or a backslash, and neither was
    there. The seat believed it had put three quotes at each end. The
    answer is the key, the quote, the opening count and the closing count.
    Any doubt gives None, and the old text stays (frame 266, pass 2).
    """
    # The call ends where the next call starts on a new line.
    nxt = re.search(r"\n[ \t]*" + re.escape(MARKER), text[start:])
    region = text[start:start + nxt.start() if nxt else len(text)].rstrip()
    if not region.endswith(")"):
        return None
    body = region[:-1]
    # The first scan's rules, as in _open_argument, with the offset of the
    # `=` that names the value the last open quote belongs to.
    last_key = opened_key = None
    eq_at = opened_eq = None
    after_comma = False
    depth = 1
    in_single = in_double = escaped = False
    for i, ch in enumerate(body):
        if escaped:
            escaped = False
        elif ch == "\\":
            escaped = True
        elif in_single:
            in_single = ch != "'"
        elif in_double:
            in_double = ch != '"'
        elif ch in "'\"":
            in_single, in_double = ch == "'", ch == '"'
            opened_key = None if after_comma or depth != 1 else last_key
            opened_eq = eq_at
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == "," and depth == 1:
            after_comma = True
        elif ch == "=" and depth == 1:
            m = re.search(r"([A-Za-z_]\w*)\s*$", body[:i])
            if m:
                last_key, after_comma, eq_at = m.group(1), False, i + 1
    if not (in_single or in_double) or opened_key is None or opened_eq is None:
        return None
    # The value must open with its quote run right after `key=`.
    s = opened_eq + len(body[opened_eq:]) - len(body[opened_eq:].lstrip())
    q = body[s:s + 1]
    if q not in ("'", '"'):
        return None
    opening = len(body[s:]) - len(body[s:].lstrip(q))
    if opening not in (1, 3):
        return None
    value = body[s + opening:]
    closing = len(value) - len(value.rstrip(q))
    core = value[:len(value) - closing]
    if closing >= opening or not core.strip():
        return None
    # A backslash before the close, or a full run inside the value, is a
    # fault the old text names. One quote inside a one-quote value is too.
    if core.endswith("\\") or q * opening in core:
        return None
    # A `, name=` inside the value can be the next argument, so the value
    # may not be the last one. A name the function lacks is code in a
    # value. Either way the short run is not a sure fault (the fuzz slice).
    if _NEXT_ARGUMENT.search(core) or (params and opened_key not in params):
        return None
    return opened_key, q, opening, closing


def _no_close_bracket(text: str, start: int) -> str | None:
    """The last key of a call whose values all close and whose `)` is absent.

    Night 152, s290 sent `code.write(path=..., text='''...''')` twice with
    no `)`. The old refusal told the seat to use triple quotes, and the
    value had them. The answer is the missing bracket. The arguments must
    parse as they are, so any other fault gives None (frame 266, pass 2b).
    """
    # The call ends where the next call starts on a new line.
    nxt = re.search(r"\n[ \t]*" + re.escape(MARKER), text[start:])
    region = text[start:start + nxt.start() if nxt else len(text)].rstrip()
    # The text says "after the closing quotes", so the call ends on one.
    if not region.endswith(("'", '"')):
        return None
    # parse_args repairs a call, and a repair can read an open list as
    # the value of a string. Python's own parser repairs nothing.
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            call = ast.parse(f"f({region})", mode="eval").body
    except (SyntaxError, ValueError):
        return None
    if (not isinstance(call, ast.Call) or call.args or not call.keywords
            or any(k.arg is None for k in call.keywords)):
        return None
    last = call.keywords[-1]
    if not (isinstance(last.value, ast.Constant)
            and isinstance(last.value.value, str)):
        return None
    return last.arg


def _open_inner(text: str, start: int, key: str
                ) -> tuple[str | None, str, str, int, str] | None:
    """The inner string of a dict or list value that never closes.

    Night 153, s257 to s259 sent `lines={'k': 'base_message += f", ...})`
    four times each. The key text said the value of lines never ends, and
    the seat looked at lines and not at the string inside it. The answer
    is the inner key, the quote, the string's head, and its offset after
    the open bracket. Any doubt gives None, and the old text stays (frame
    266, pass 3).
    """
    # The call ends where the next call starts on a new line.
    nxt = re.search(r"\n[ \t]*" + re.escape(MARKER), text[start:])
    end = start + nxt.start() if nxt else len(text)
    # The seat ended the call with `)`, so the string swallowed the close.
    # A completion cut short has no `)`, and its fault is the cut.
    if not text[start:end].rstrip().endswith(")"):
        return None
    last_key = None
    brackets: list[tuple[str, int, str | None]] = []
    quote = None
    opened = 0
    escaped = False
    for i in range(start, end):
        ch = text[i]
        if escaped:
            escaped = False
        elif ch == "\\":
            escaped = True
        elif quote is not None:
            if ch == quote:
                quote = None
        elif ch in "'\"":
            quote, opened = ch, i
        elif ch in "([{":
            brackets.append((ch, i, last_key))
        elif ch in ")]}":
            if not brackets:
                return None
            brackets.pop()
        elif ch == "=" and not brackets:
            m = re.search(r"([A-Za-z_]\w*)\s*$", text[start:i])
            if m:
                last_key = m.group(1)
    if quote is None or not brackets:
        return None
    # The outer bracket must be the value of the key the scan named, and
    # it must open right after `key=`.
    outer, at_outer, owner = brackets[0]
    if outer not in "[{" or owner != key:
        return None
    if not re.search(re.escape(key) + r"\s*=\s*$", text[start:at_outer]):
        return None
    # The text before the string must read as the start of the call. Else
    # a quote inside an earlier string closed it early (as _missing_close).
    shut = "".join({"(": ")", "[": "]", "{": "}"}[b[0]]
                   for b in reversed(brackets))
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            ast.parse(f"f({text[start:opened]} 0{shut})")
    except (SyntaxError, ValueError):
        return None
    # A `, name=` inside the string can be the next argument, so the
    # string may have swallowed it, and the fault is not sure.
    if _NEXT_ARGUMENT.search(text, opened + 1, end):
        return None
    inner = re.search(r"""(['"])((?:(?!\1).)*)\1\s*:\s*$""",
                      text[brackets[-1][1] + 1:opened])
    inner_key = inner.group(0).rstrip()[:-1].rstrip() if (
        inner and brackets[-1][0] == "{") else None
    head = text[opened:min(end, opened + 20)].rstrip()
    # The bracket that holds the string tells a dict key from a list item.
    return inner_key, quote, head, opened - start, brackets[-1][0]


def _escaped_open(text: str, start: int, key: str) -> tuple[str, int] | None:
    """The head of a double-quoted value that holds `\\"` and never closes.

    Night 153, s276 sent `reason="... \\"'name' is not installed\\" ...)`
    four times. Each `\\"` is a quote inside the value, so the value never
    closes. The key text said a quote inside closed it early, and the seat
    read each `\\"` as a close. The answer is the head of the value and
    its offset after the open bracket. Any doubt gives None (frame 266,
    pass 3).
    """
    nxt = re.search(r"\n[ \t]*" + re.escape(MARKER), text[start:])
    end = start + nxt.start() if nxt else len(text)
    # As in _open_inner: a completion cut short has no `)` at its end.
    if not text[start:end].rstrip().endswith(")"):
        return None
    m = None
    for m in re.finditer(r"(?:^|[,(\s])" + re.escape(key) + r"\s*=\s*",
                         text[start:end]):
        pass
    if m is None:
        return None
    s = start + m.end()
    # One plain quote opens the value. Three open a triple-quoted value.
    if text[s:s + 1] != '"' or text[s:s + 2] == '""':
        return None
    value = text[s + 1:end]
    if '\\"' not in value:
        return None
    # Every quote inside the value has a backslash before it, so none of
    # them closes it. A plain quote anywhere means the value can close.
    escaped = False
    for ch in value:
        if escaped:
            escaped = False
        elif ch == "\\":
            escaped = True
        elif ch == '"':
            return None
    # The text before the value must read as the start of the call.
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            ast.parse(f"f({text[start:s]} 0)")
    except (SyntaxError, ValueError):
        return None
    if _NEXT_ARGUMENT.search(value):
        return None
    return text[s:min(end, s + 20)].rstrip(), s - start


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
    #
    # Frame 362, dry run 6c: the list is first read as it is written. The
    # two rewrites exist to make a list parse, so a list that Python reads
    # needs neither. Their scans are not Python's: s186's `'''\` and a line
    # break became a literal `\n`, and s194's `pass` after `\\'` became
    # `'pass'` (frame 155). A list that Python reads holds no bare `pass`,
    # and its line breaks in strings are already the value's line breaks,
    # so the rewrites can change no wanted value of such a list.
    try:
        written = ast.parse(f"_f({args_str})", mode="eval")
    except (SyntaxError, ValueError):
        written = None
    safe = args_str
    if written is None or not isinstance(written.body, ast.Call):
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
    _refuse_joined_strings(args_str, safe)
    call = expr.body
    if not isinstance(call, ast.Call):
        raise ValueError("not a call expression")

    out: dict[str, Any] = {}
    for kw in call.keywords:
        if kw.arg is None:
            raise ValueError("**kwargs is not supported")
        out[kw.arg] = _literal(kw.value)
    return out, tuple(_literal(a) for a in call.args)


class JoinedStrings(ValueError):
    """The strict read joined two string literals that the seat did not
    write as two. `extract` sends this reason to the seat as it is."""


def _adjacent_strings(safe: str) -> bool:
    """Whether two string literals stand side by side in the list."""
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(f"_f({safe})").readline))
    except (tokenize.TokenError, SyntaxError):
        return False
    skip = (tokenize.NL, tokenize.NEWLINE, tokenize.COMMENT)
    prev = None
    for tok in tokens:
        if tok.type in skip:
            continue
        if tok.type == tokenize.STRING and prev == tokenize.STRING:
            return True
        prev = tok.type
    return False


def _refuse_joined_strings(args_str: str, safe: str) -> None:
    """Refuse a strict read that joins two string literals, when Python
    refuses the list as written.

    A stray quote can close a value early. The escaped list can still
    parse, because Python joins the string literals that stand side by
    side. The read then answers a wrong value, such as `, c=` inside `a`.
    Frame 122's rule: a wrong write is worse than a refusal (frame 151,
    the review of e78545a, finding 1).

    The guard reads tokens, not a count of triple quotes. A count also
    counts a `'''` inside a `"` value, and refused right reads (the review
    of 9cb2bcbc, finding 1). A list that Python reads as written keeps its
    read. The lenient read keeps its path, because a guard there refused
    47 right reads of the fuzz slice."""
    if not _adjacent_strings(safe):
        return
    try:
        ast.parse(f"_f({args_str})", mode="eval")
        return
    except SyntaxError:
        pass
    raise JoinedStrings(
        "a quote inside a value closed it early, and the text after that "
        "quote was read as a second string. Remove the extra quote. Open "
        "and close each value with the same three quotes")


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
    # A triple quote is one token, as Python and `_rescan_args` read it.
    # Frame 151: a scan that counted each quote alone left the value after
    # a lone quote, and read the next line break as a space.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    out, quote, esc, i = [], None, False, 0
    while i < len(text):
        ch = text[i]
        if quote:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif text.startswith(quote, i):
                out.append(quote)
                i += len(quote)
                quote = None
                continue
            if ch == "\n":
                out.append("\\n")
                i += 1
                continue
        else:
            if text.startswith("'''", i) or text.startswith('"""', i):
                quote = text[i:i + 3]
                out.append(quote)
                i += 3
                continue
            if ch in ("'", '"'):
                quote = ch
            elif ch == "\n":
                out.append(" ")
                i += 1
                continue
        out.append(ch)
        i += 1
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
    the Liaison's present was refused three times to quarantine. A hash is
    part of an id: click night 84 (2026-09-17), the survey of `src/click`
    wrote second-sense rows like `group#src_click`, the Liaison copied 56
    refs bare, the rewrite never matched, and the present was refused
    three times to quarantine before session 1.
    """
    import re

    global _BARE_LIST
    if _BARE_LIST is None:
        _BARE_LIST = re.compile(
            r"(?P<key>\b[A-Za-z_][A-Za-z0-9_]*=)"
            r"(?P<ids>[A-Za-z0-9_.@:/#-]+(?:\s*,\s*[A-Za-z0-9_.@:/#-]+)+)"
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


def _namespace_labels(text: str, signatures: dict | None) -> str:
    """
    `MODEL: amend(headline=...)` -- the namespace as the marker, the verb as
    the call. The survey brief says `model.amend(...)` inline and qwen3:8b
    (the survey spike, 2026-09-15) wrote every call that way, in prose, and
    the area closed with nothing done. The spelling is unambiguous when the
    namespace and verb name a function the session has: only then is the
    line rewritten to `TOOL: namespace.verb(`; prose like `NOTE: ...` has no
    such function and is left alone.
    """
    if not signatures:
        return text
    allowed = {n.lower() for n in signatures}
    pat = re.compile(r"(?im)^[ \t]*([A-Za-z_]+)[ \t]*:[ \t]*([A-Za-z_][A-Za-z0-9_]*)[ \t]*\(")

    def fix(m):
        name = f"{m.group(1).lower()}.{m.group(2).lower()}"
        return f"{MARKER} {name}(" if name in allowed else m.group(0)
    return pat.sub(fix, text)


def _source_starts(source: str, scanned: str, results: list, where: list[int]) -> list[int]:
    """Each result's start in the text `extract` was given.

    The scan runs over the rewritten text, so a rewrite moves every later
    call. The rewrites are rare and the common case is one string, where the
    scan's own offsets are exact. When a rewrite did happen, the raw locates
    the call, and then its marker and name do. The cursor moves past each
    find, so a duplicate never resolves to an earlier copy.

    A call found neither way goes after every position in the text, and so
    does every call after it. The rewritten offset is never used: a rewrite
    that shortened the text put a commit written after an invented result
    at 123 against the invention's 127, and the commit ran (the diff review
    of frame 77, 2026-09-23). Placed last, the call is held whenever the
    turn invented a result, and the order of the calls is kept.
    """
    if scanned == source:
        return list(where)
    out: list[int] = []
    cursor = 0
    lost = False
    for item, at in zip(results, where):
        raw = getattr(item, "raw", "") or ""
        found = -1 if lost or not raw else source.find(raw, cursor)
        if found < 0 and not lost:
            # The marker and the name, and not the name alone: a name in the
            # prose ahead of the invention would place the call before it.
            name = getattr(item, "name", "") or ""
            if not name:
                named = re.match(rf"\s*{re.escape(MARKER)}\s*([\w.]+)", raw)
                name = named.group(1) if named else ""
            hit = (re.compile(rf"{re.escape(MARKER)}[ \t]*{re.escape(name)}\b")
                   .search(source, cursor) if name else None)
            found = hit.start() if hit else -1
        if found < 0:
            lost = True
            out.append(len(source))
            continue
        out.append(found)
        cursor = found + 1
    return out


def extract(text: str, signatures: dict | None = None, *,
            starts: list[int] | None = None) -> list[ToolCall | ToolError]:
    """
    Find every `TOOL:` call in a completion, in order.

    Quote- and paren-aware, so an argument containing `)` or a nested call does
    not truncate the scan. Anything that cannot be parsed becomes a ToolError
    carrying the raw text — the model sees its own mistake.

    `starts`, when given, is filled with each result's start offset in `text`.
    The runner reads the offsets to hold the calls a seat wrote after a tool
    result it made up (frame 77).
    """
    results: list[ToolCall | ToolError] = []
    where: list[int] = []
    source = text
    text = _bracket_bare_lists(_inline_blocks(_namespace_labels(text, signatures)))
    cursor = 0

    def add(item, at: int) -> None:
        results.append(item)
        where.append(at)

    while True:
        marker = text.find(MARKER, cursor)
        if marker == -1:
            if starts is not None:
                starts.extend(_source_starts(source, text, results, where))
            return results

        i = marker + len(MARKER)
        while i < len(text) and text[i].isspace():
            i += 1

        name, i = _scan_name(text, i)
        if not name:
            add(ToolError(text[marker:marker + 60], "no function name after TOOL:"), marker)
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
                    add(ToolError(
                        f"{MARKER} {name}[{raw_args[:80]}]",
                        f"could not parse arguments: {exc}. Arguments go in "
                        f"round brackets: {name}({raw_args[:60]})"), marker)
                else:
                    add(ToolCall(name=name, args=args, pos=pos,
                                 raw=f"{name}({raw_args})"), marker)
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
                add(ToolCall(name=name, args={}, raw=f"{MARKER} {name}"), marker)
            else:
                add(ToolError(f"{MARKER} {name}", "missing argument list"), marker)
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

        joined: list[JoinedStrings] = []
        if args_end is None:
            # Second reading: triple-quoted strings as one token, then the
            # last closing bracket of this call's region. Night 72
            # (2026-09-15): a challenge carrying a test's source in a quoted
            # argument died here three sessions running, the same call each
            # time. The fallback holds only when the arguments then parse.
            args_end = _rescan_args(text, args_start, MARKER, joined)
        sig = (signatures or {}).get(name)
        # `_param_sets` hands (required, all); a bare set is accepted too.
        params = sig[1] if isinstance(sig, tuple) and len(sig) == 2 else sig

        def third_call() -> int | None:
            """Add the call by the third reading, and return its end."""
            # A wrong `why` is a sentence that a door or a reader checks.
            # A wrong `text` is a file on disk, so writers get no guess.
            if not params or _WRITES & set(params):
                return None
            third = _third_reading(text, args_start)
            if third is None:
                return None
            raw3, end3 = third
            args3, pos3 = parse_args(raw3)
            if _swallowed_argument(args3, params):
                return None
            # A name the function lacks means a quote in the source opened
            # a false argument (frame 122's fuzz: `'',a='if` in a text).
            if params and any(k not in params for k in args3):
                return None
            add(ToolCall(name=name, args=args3, pos=pos3,
                         raw=f"{name}({raw3})"), marker)
            return end3

        if args_end is None:
            end3 = third_call()
            if end3 is not None:
                cursor = end3 + 1
                continue
            # Say why, or the model retries the same call. tipsAH (2026-09-09):
            # ten writes of main.py refused as "unterminated argument list",
            # the model's own guess was "a multi-line string", and the cause
            # was a quote inside the text closing the string early.
            key = _open_argument(text, args_start)
            # A writer's source holds `print(x, end='')`, and `end` is a
            # name of code.write. So a writer gets no guess, as in
            # third_call (frame 266, review 1, finding 1).
            missing = (None if params and _WRITES & set(params)
                       else _missing_close(text, args_start, params))
            # A write's value can end on a real `'')`, so a write keeps the
            # old text, as above (frame 266, pass 2).
            short = (None if joined or missing or not key or key in _WRITES
                     or (params and _WRITES & set(params))
                     else _short_close(text, args_start, params))
            # Only the shape that got the generic text asks for the bracket.
            bracket = (None if joined or missing or short or key
                       else _no_close_bracket(text, args_start))
            # The key branch alone asks for the inner string or the escaped
            # quote, and a write keeps its old text (frame 266, pass 3).
            keyed = not (joined or missing or short or not key
                         or key in _WRITES
                         or (params and _WRITES & set(params)))
            inner = _open_inner(text, args_start, key) if keyed else None
            escaped = (None if not keyed or inner
                       else _escaped_open(text, args_start, key))
            if joined:
                # The rescan closed the list, and the guard on joined strings
                # refused it. The hint below would name a value that is
                # already between triple quotes (the review of 9cb2bcbc,
                # finding 3), so send the guard's reason.
                reason = f"could not parse arguments: {joined[0]}"
            elif missing:
                # Frame 266, night 151: s226 read "a quote inside closed it
                # early" five times and never found `"approve}`. Show the
                # seat its own text where the string opens. The texts below
                # stay byte for byte, because recorded prompts carry them.
                owner, inner, head, at, swallowed = missing
                whose = (f"a string in the value of {owner}" if owner and inner
                         else f"the value of {owner}" if owner else "a value")
                reason = (
                    f"unterminated argument list: {whose} starts at "
                    f"character {at} after the open bracket. The string "
                    f"`{head}` has no closing quote before `{swallowed}`, so "
                    f"it runs on into the next argument. Put the closing "
                    f"quote where that value ends, and change nothing else")
            elif short:
                # Frame 266, night 152: s245 to s247 closed `'''` with `''`
                # fourteen times and read a cause that was not there. Name
                # the two counts and the one step.
                owner, q, opening, closing = short
                shut = _COUNT_WORDS[closing]
                if opening == 3:
                    reason = (
                        f"unterminated argument list: the value of {owner} "
                        f"opens with three quotes, `{q * 3}`, and ends with "
                        f"{shut} before the closing bracket. Put three "
                        f"quotes before `)`, the same number as at the start.")
                else:
                    reason = (
                        f"unterminated argument list: the value of {owner} "
                        f"opens with one quote, `{q}`, and ends with "
                        f"{shut} before the closing bracket. Put the same "
                        f"quote before `)`, or put the whole value between "
                        f"three single quotes at each end.")
            elif inner:
                # Frame 266, night 153: s257 to s259 read "the value of
                # lines never ends" four times each and sent the same dict.
                # Name the string inside the dict that never closes.
                inner_key, q, head, at, holder = inner
                # A string in a dict with no closed key before it is a key
                # that never closes (frame 266, review 5, low 1).
                whose = (f"the value of {inner_key} inside {key}" if inner_key
                         else f"a key of the dict in {key}" if holder == "{"
                         else f"an item of the list in {key}")
                reason = (
                    f"unterminated argument list: a string inside the value "
                    f"of {key} never closes. The string `{head}` is {whose}, "
                    f"and it starts at character {at} after the open "
                    f"bracket. Put the closing quote `{q}` where that inner "
                    f"value ends, and change nothing else.")
            elif escaped:
                # Frame 266, night 153: s276 read each `\"` in its value as
                # the close four times. Say what `\"` is, and the one step.
                head, at = escaped
                reason = (
                    f"unterminated argument list: the value of {key} never "
                    f"closes. It starts at character {at} after the open "
                    f"bracket, as `{head}`. Each `\\\"` inside it is an "
                    f"escaped quote, part of the value, and not its close. "
                    f"Put a plain `\"` where the value ends. Better, because "
                    f"the value holds quotes: put the whole value between "
                    f"three single quotes at each end, with no backslashes.")
            elif key:
                # Frame 122, night 115: the old hint named `text=`, and the
                # Critic put triple quotes on `quote`. The apostrophe that
                # broke the list was in `why`. Name the argument.
                reason = (
                    f"unterminated argument list: the value of {key} never "
                    f"ends. Either a quote inside {key} closed it early, or "
                    f"its closing quote has a backslash before it. Put a "
                    f"value with quotes or line breaks between triple "
                    f"quotes, three single quotes at each end. Write the "
                    f"value as it is, with no backslashes:\n"
                    # A placeholder, not sample code: a seat copies an
                    # example's content (frame 122's review).
                    f"{key}='''the text, with its quotes and line breaks "
                    f"as they are'''")
            elif bracket:
                # Frame 266, night 152: s290 read the triple quote hint
                # twice, and its value had triple quotes. Name the bracket.
                reason = (
                    f"unterminated argument list: the call to {name} has no "
                    f"closing bracket. The value of {bracket} closes, and no "
                    f"`)` follows it. Put `)` after the closing quotes, and "
                    f"send the call again in full.")
            else:
                reason = (
                    "unterminated argument list: a quote inside a quoted "
                    "argument ended the string early, or a bracket is "
                    "unbalanced. Source has quotes of its own: put it between "
                    "triple quotes, text='''...''', with the lines as they "
                    "are, no escaping")
            add(ToolError(f"{MARKER} {name}(...", reason), marker)
            cursor = marker + len(MARKER)
            continue

        raw_args = text[args_start:args_end]
        try:
            args, pos = parse_args(raw_args)
        except Exception as first_exc:
            # Frame 109, night 105: the first scan read `can't` inside a
            # `'''` value as a quote and closed the list early. The rescan
            # reads `'''` as one token, so ask it before the refusal.
            rescan_end = _rescan_args(text, args_start, MARKER)
            if rescan_end is not None and rescan_end != args_end:
                args_end = rescan_end
                raw_args = text[args_start:args_end]
                args, pos = parse_args(raw_args)
                exc = None
            else:
                exc = first_exc
        else:
            exc = None
        # A list that fails here may still have the third reading. Night
        # 115, s86 turn 4: a stray `")` after the call closed the wrapped
        # value, and `why` rode along inside `quote`.
        end3 = None
        if exc is not None or _swallowed_argument(args, params):
            end3 = third_call()
        if end3 is not None:
            args_end = end3
        elif exc is not None:
            add(ToolError(f"{MARKER} {name}({raw_args[:80]})",
                          f"could not parse arguments: {exc}"), marker)
        else:
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
                found = _stray_quote(raw_args, params)
                if found:
                    # Night 119, s229: the refusal named `citation`, the
                    # stray quote was in `why`, and the Critic put triple
                    # quotes on `quote`. Name the value that holds it.
                    stray, extra = found
                    write = (
                        f"Remove the extra quote at the start or the end of "
                        f"{stray}. Write the rest of the value as it is"
                        if extra else "Write the whole value as it is")
                    add(ToolError(
                        f"{MARKER} {name}({raw_args[:80]})",
                        f"a quote inside {stray} ended it early, and the text "
                        f"after that quote is not an argument. Put the value "
                        f"of {stray} between triple quotes, three single "
                        f"quotes at each end. {write}, with no backslashes:\n"
                        f"{stray}='''the text, with its quotes and line "
                        f"breaks as they are'''\n"
                        # A seat copies a placeholder line (frame 122's
                        # fourth review), so the old warning follows it.
                        f"No escaping, and no placeholder: the value is the "
                        f"whole text, sent again in full"), marker)
                    cursor = args_end + 1
                    continue
                add(ToolError(
                    f"{MARKER} {name}({raw_args[:80]})",
                    f"a quote inside {key} ended it early and the arguments "
                    f"after it ({other}=...) were read as part of {key}. Source "
                    f"has quotes of its own; open {longest} with three single "
                    f"quotes, write every line of the value as it is, and close "
                    f"with three single quotes. No escaping, and no placeholder: "
                    f"the value is the whole text, sent again in full"), marker)
            else:
                add(ToolCall(name=name, args=args, pos=pos,
                             raw=f"{name}({raw_args})"), marker)
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
                    signatures: dict | None = None, *,
                    with_offsets: bool = False):
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

    The default return is the list of calls. With `with_offsets`, the return is
    `(calls, starts, scanned)`: a parallel list of each call's start offset, and
    the text those offsets index into. The backtick pass below rewrites the
    completion, so the caller searches `scanned` and not its own copy. The
    calls themselves are the same either way (frame 77).
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

    marked_starts: list[int] = []
    marked = extract(text, signatures, starts=marked_starts)

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
        # The scan's own offsets, and not `find(raw)`. The raw is rebuilt from
        # the parse, so 16 of 1,263 recorded `code.write` calls were not found
        # in the text at all, and 744 duplicate raws resolved to the first copy
        # (the design review of frame 77, finding 5).
        positioned += list(zip(marked_starts, marked))
        ordered = sorted(positioned, key=lambda pair: pair[0])
        if with_offsets:
            return [c for _, c in ordered], [i for i, _ in ordered], text
        return [c for _, c in ordered]

    # No marker: labelled blocks, bare calls outside them, and bare argument
    # lines beside both -- the amends as labels and the attest as a bare call
    # was one session's whole output, and the attest was being dropped.
    found += [(i, c) for i, c, _ in labelled_all]
    found += _unlabelled(text, signatures or {}, bare_spans + labelled_spans)
    ordered = sorted(found, key=lambda pair: pair[0])
    if with_offsets:
        return [c for _, c in ordered], [i for i, _ in ordered], text
    return [call for _, call in ordered]


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
