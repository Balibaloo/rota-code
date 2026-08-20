"""
Reading an argument list whose prose contains quotes.

The strict grammar is Python and it is tried first; this is only reached by
what it rejects, so nothing that parsed before parses differently.

The one rule: **a quoted value is delimited by its outermost quote, not by the
first one inside it.** `reason='"the criterion" and "assert f('SKU-1')"'` is one
string containing four quotes, and treating the third as a terminator is what
turned a Developer's challenge into a `ToolError` and a red case green.
"""
from __future__ import annotations

import ast
from typing import Any


def scan_name(text: str, i: int) -> tuple[str, int]:
    """The identifier starting at `i`, and where it ends."""
    start = i
    while i < len(text) and (text[i].isalnum() or text[i] == "_"):
        i += 1
    return text[start:i], i


def closing_quote(text: str, open_at: int, quote: str) -> int:
    """
    The partner of the quote at `open_at`: the last one that ends the value.

    Scanned from the right, which is what makes an inner quote content rather
    than a terminator. A candidate closes the value only if what follows it is
    the end of the argument list or the next `name=` — the same boundary the
    strict grammar uses, read without requiring the inside to be well-formed.
    """
    i = len(text) - 1
    while i > open_at:
        if text[i] == quote:
            rest = text[i + 1:].lstrip()
            if not rest:
                return i
            if rest.startswith(","):
                after = rest[1:].lstrip()
                name, j = scan_name(after, 0)
                if name and j < len(after) and after[j] == "=":
                    return i
        i -= 1
    return -1


def parse_args_lenient(args_str: str, literal) -> dict[str, Any]:
    """
    Split `name=value` at the top level, quoted values by their outer quote.

    Values that are *not* quoted go back through the strict parser one at a
    time, so `refs=[...]` stays a list and `round_no=3` stays an integer. A
    recipient resolving `"0"` as a round number would be a different bug
    wearing this one's clothes.
    """
    out: dict[str, Any] = {}
    i, n = 0, len(args_str)
    while i < n:
        while i < n and args_str[i] in ", \t":
            i += 1
        if i >= n:
            break
        name, i = scan_name(args_str, i)
        if not name or i >= n or args_str[i] != "=":
            raise ValueError("could not read an argument name")
        i += 1
        while i < n and args_str[i] in " \t":
            i += 1
        if i < n and args_str[i] in "\"'":
            quote = args_str[i]
            end = closing_quote(args_str, i, quote)
            if end < 0:
                raise ValueError(f"{name}= opens with {quote} and never closes")
            out[name] = args_str[i + 1:end].replace("\\n", "\n")
            i = end + 1
        else:
            start, depth = i, 0
            while i < n and not (depth == 0 and args_str[i] == ","):
                if args_str[i] in "[{(":
                    depth += 1
                elif args_str[i] in "]})":
                    depth -= 1
                i += 1
            chunk = args_str[start:i].strip()
            if not chunk:
                raise ValueError(f"{name}= has no value")
            out[name] = literal(ast.parse(chunk, mode="eval").body)
    if not out:
        raise ValueError("no arguments could be read")
    return out
