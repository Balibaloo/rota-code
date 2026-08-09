"""
The cockpit's front end, checked as far as it can be without a browser.

A syntax error in `graphview.js` does not fail anything — the page loads, the
graph silently does not draw, and the first sign is a blank canvas that looks
like "no data". It has happened twice: once an escaped newline collapsed inside
a template literal, once a backtick in an SVG comment closed one early.

So: parse it, and assert the two contracts the renderer and the markup share.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

STATIC = Path(__file__).resolve().parents[2] / "rota" / "static"
VIEWER = Path(__file__).resolve().parents[2] / "rota" / "viewer.html"


@pytest.mark.skipif(not shutil.which("node"), reason="node not on PATH")
@pytest.mark.parametrize("name", ["graphview.js", "panels.js"])
def test_the_script_parses(name):
    out = subprocess.run(["node", "--check", str(STATIC / name)],
                         capture_output=True, text=True)
    assert out.returncode == 0, out.stderr


def test_every_element_the_scripts_write_to_exists():
    """
    `getElementById(...)` naming an id the markup does not have fails silently —
    the assignment throws into nothing and the panel is simply never filled.
    That is exactly how the header popups came to be empty boxes.
    """
    sources = {name: (STATIC / name).read_text(encoding="utf-8")
               for name in ("graphview.js", "panels.js")}
    sources["viewer.html"] = VIEWER.read_text(encoding="utf-8")

    # Ids come from the markup *and* from the scripts, which inject most of the
    # controls. Either is a legitimate place to declare one; declaring it
    # nowhere is the failure.
    ids = {i for src in sources.values()
           for i in re.findall(r'id="([\w-]+)"', src)}

    missing = []
    for name, src in sources.items():
        for used in re.findall(r"getElementById\('([\w-]+)'\)", src):
            if used not in ids:
                missing.append(f"{name} writes to #{used}, which nothing creates")
    assert not missing, "\n".join(missing)


def test_the_header_popups_are_populated_not_just_shown():
    """
    They were wired to hover and never given content, so hovering produced a
    styled empty box — and the detail arrived separately as an OS tooltip from a
    `title` attribute nobody meant to keep. Two mechanisms, one of them blank.
    """
    src = (STATIC / "panels.js").read_text(encoding="utf-8")
    for pop in ("pop-state", "pop-tick"):
        assert f"getElementById('{pop}').innerHTML" in src, \
            f"#{pop} is shown on hover but nothing fills it"

    assert ".title =" not in src, \
        "a native tooltip is back; it cannot be laid out and duplicates the popup"


def test_the_key_covers_every_shape_the_renderer_draws():
    """
    A key that omits a shape teaches that the shape means nothing. `derived` was
    drawn for a year before it was listed.
    """
    src = (STATIC / "graphview.js").read_text(encoding="utf-8")
    shapes = set(re.findall(r"^  (\w+):\s*\{w:", src, re.M))
    keyed = set(re.findall(r'\{kind:"(\w+)"\}', src))
    assert shapes <= keyed, f"drawn but not in the key: {sorted(shapes - keyed)}"


def test_the_key_covers_every_edge_type():
    src = (STATIC / "graphview.js").read_text(encoding="utf-8")
    types = set(re.findall(r"^  (\w+):\s*\{c:'#", src, re.M))
    keyed = set(re.findall(r'\{edge:"(\w+)"\}', src))
    assert types == keyed, f"edge types and key disagree: {types ^ keyed}"


def test_every_key_row_says_what_the_thing_is():
    """
    The point of the key is not the colour. Someone reading it wants to know
    what a journal *is*, and a row that only names one has answered the easy
    half of the question.
    """
    src = (STATIC / "graphview.js").read_text(encoding="utf-8")
    block = src.split("const LEGEND = [")[1].split("\n];")[0]
    rows = re.findall(r'\["([^"]+)",\s*\{[^}]+\},\s*"([^"]*)"\]', block)
    assert rows, "the key is no longer a declared table"

    thin = [label for label, why in rows if len(why) < 25]
    assert not thin, f"key rows with no real description: {thin}"


def test_no_legacy_vocabulary_in_the_ui():
    """
    "Blast radius" is borrowed from incident response, where it means how much
    got damaged — the wrong reading entirely, since nothing is damaged and
    owners are woken in order. "Inhabit" read as a mood rather than a filter.
    Both are gone from anything a person sees.
    """
    seen = []
    for path in (STATIC / "graphview.js", STATIC / "panels.js", VIEWER):
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith(("//", "*", "/*", "<!--")):
                continue                     # commentary may explain the history
            if re.search(r"blast radius|>inhabit<|inhabiting", line, re.I):
                seen.append(f"{path.name}: {stripped[:80]}")
    assert not seen, "\n".join(seen)
