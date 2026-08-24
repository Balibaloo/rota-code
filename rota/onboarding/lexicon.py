"""
The lexicon: the words a checkout declares, ranked by how loudly it declares them.

The define phase of onboarding wakes Terminologist one word at a time, and the
list of words is the one thing in that phase no session may choose -- a session
handed a list defines the list, whichever list it is. So the list has to come
from the repository's own claims about what its things are called, and those
claims are mechanical:-------------------------------------------------------------------------------------------------------------

    a directory name      `src/variables/providers`   -> provider
    a file name           `src/intents/frontmatter.ts` -> frontmatter
    a declared type       `enum TemplateVariableType`  -> template variable type
    an authoring key      `with_prompts:` in a schema   -> prompt

Frequency breaks ties and never decides. `provider` is used eight times in the
whole of cnt and names a directory; `value` is used two hundred times and names
nothing. Ranked by use alone, the first is below the fold and the second is on
top, which is the measured ceiling the word list had.

**Nothing here interprets.** Like the index this is a fact about the checkout,
recomputed on every onboarding and never amended by a role. What a word *means*
is the define session's job, with the concordance in front of it.

A compound is kept whole. `TemplateVariableType` is one name the project chose,
and the word list that split it into `template` and `variable` (dropping `type`
as a stopword) could not carry the concept at all -- three of cnt's ten required
terms are compounds and none of them survived decomposition.
"""
from __future__ import annotations

import json
import math
import re
import sqlite3
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from .languages import for_path

# Directory names that say where code lives, not what it is about.
GENERIC_DIRS = {
    "src", "lib", "libs", "app", "apps", "pkg", "internal", "core", "common",
    "utils", "util", "helpers", "helper", "shared", "base", "misc", "types",
    "typing", "vendor", "third_party", "scripts", "bin", "cmd", "tools",
    "assets", "static", "public", "docs", "doc", "examples", "example",
    "test", "tests", "testing", "spec", "specs", "__tests__", "fixtures",
    "node_modules", "dist", "build", "out", "target", "config", "configs",
}

# File stems that name a role in the tree rather than a thing in the product.
GENERIC_STEMS = {
    "index", "main", "mod", "init", "__init__", "__main__", "types", "utils",
    "util", "helpers", "helper", "constants", "const", "config", "settings",
    "setup", "conftest", "test", "tests", "app", "server", "client", "cli",
    "api", "base", "common", "errors", "exceptions", "version", "package",
    "manifest", "readme", "license", "changelog", "contributing", "makefile",
    "dockerfile", "tsconfig", "versions", "styles", "style", "lock",
}

# Manifests: files whose keys are a contract with something outside, and whose
# *names* say nothing about the product. Read for keys, never for a stem.
MANIFESTS = {"package.json", "manifest.json", "pyproject.toml", "setup.cfg",
             "cargo.toml", "go.mod", "composer.json", "gemfile", "pom.xml",
             "build.gradle", "deno.json", "tsconfig.json", "versions.json"}

# How loudly each kind of source names a word. A directory and a declared type
# are the project saying *this is a kind of thing*; a file name nearly so; an
# authoring-surface key is what the project asks its user to write; a function
# name is evidence the word is in use and nothing more.
WEIGHT = {"key": 4.0, "dir": 4.0, "decl_type": 3.0, "file": 3.0, "surface": 2.0,
          "decl_part": 0.5, "decl_fn": 0.5, "prose": 1.0}

# A declared compound longer than this is an implementation name, not a word
# anybody says: `TemplateVariableVariables_NaturalDate` is the interface for one
# provider's extra keys, and `template variable type` is the concept.
MAX_COMPOUND = 3

# Words that score only from functions and frequency never qualify -- they are
# the `getter`/`parser` noise every earlier list was three quarters made of.
STRUCTURAL = ("key", "dir", "file", "decl_type", "surface")

_DECL = re.compile(
    r"^\s*(?:export\s+)?(?:default\s+)?(?:abstract\s+)?(?:declare\s+)?"
    r"(?:public\s+|private\s+|protected\s+)?(?:static\s+)?(?:final\s+)?"
    r"(?P<kind>enum|interface|type|class|struct|trait|record|protocol|"
    r"function|func|fn|def|const|let|var|val)\s+(?P<name>[A-Za-z_]\w*)")

TYPE_KINDS = {"enum", "interface", "type", "class", "struct", "trait",
              "record", "protocol"}

_KEY = re.compile(r"^\s*[\"']?(?P<key>[A-Za-z_][\w\-]*)[\"']?\s*:")


# English function words the code-oriented stopword list never needed. Only
# the prose harvest sees them: a README speaks sentences, so its frequency
# table is grammar first and names second.
_PROSE_FUNCTION_WORDS = frozenset("""
    you your yours can could will would should shall may might must are is was
    were been being have has had having do does did doing see also when then
    than that this these those there here how what which who whom whose why
    where all any both each few more most other some such only own same very
    just because while about against between into through during before after
    above below again further once the and but nor not for with its they them
    their example note new use used using make made create creating chose
    chosen choose shown show available called selected select selection add
    added adding want wanted like first second next last different section
    list click expand enter entered set setting per each etc
""".split())


def prose_names(text: str, family: set[str], stop: set[str],
                floor: int = 4, cap: int = 8) -> list[tuple[str, int]]:
    """
    The words a README uses as names for things the code never says.

    Measured on the consult probe: the glossary held `intents_to` and its
    definition answered the question -- asked with the README's word, "recipe"
    -- and no lookup could connect them, because no artefact carried the
    prose's vocabulary. The claims of a README stay a check; its *names* are
    data.

    Three gates, all mechanical: said at least `floor` times outside code
    fences; emphasised at least once -- a heading, bold, or double quotes,
    which is a README marking its own vocabulary; absent from every code
    word's family. Capped best-first, because each survivor costs a define
    session, and whether it names anything is that session's judgement, not
    this function's.
    """
    prose = re.sub(r"```.*?```", " ", text, flags=re.S)
    prose = re.sub(r"`[^`]*`", " ", prose)
    prose = re.sub(r"<[^>]+>|https?://\S+", " ", prose)
    emphasised = " ".join(
        re.findall(r"^#+ .*$", prose, flags=re.M)
        + re.findall(r"\*\*([^*]+)\*\*", prose)
        + re.findall(r'"([^"\n]{2,60})"', prose))
    emph = {singular(w.lower())
            for w in re.findall(r"[A-Za-z][A-Za-z_-]{2,}", emphasised)}
    counts: Counter = Counter()
    for w in re.findall(r"[A-Za-z][A-Za-z_-]{2,}", prose):
        w = singular(w.lower())
        if w not in stop and w not in _PROSE_FUNCTION_WORDS:
            counts[w] += 1
    out = [(w, n) for w, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
           if n >= floor and w in emph and w not in family]
    return out[:cap]


def parts(name: str) -> list[str]:
    """
    An identifier as the words it is made of, keeping every part.

    Unlike `api._words_in`, which drops stopwords because it ranks vocabulary,
    this keeps `type` in `TemplateVariableType` and `set` in `filterSet`: a
    compound is a name the project chose, and its parts are its parts. Only
    true noise goes -- one-letter fragments and digits.
    """
    spaced = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", name)
    spaced = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", spaced)
    out = []
    for w in re.split(r"[^A-Za-z]+", spaced):
        w = w.lower()
        if len(w) >= 2:
            out.append(w)
    return out


def singular(word: str) -> str:
    if word.endswith("ies") and len(word) > 5:
        return word[:-3] + "y"
    if word.endswith("ses") and len(word) > 5:
        return word[:-2]
    if word.endswith("s") and not word.endswith("ss") and len(word) > 4:
        return word[:-1]
    return word


def compound(name: str) -> str:
    """`TemplateVariableType` -> `template variable type`; last part singular."""
    ps = parts(name)
    if not ps:
        return ""
    ps[-1] = singular(ps[-1])
    return " ".join(ps)


@dataclass
class Entry:
    word: str
    sources: set = field(default_factory=set)
    grains: set = field(default_factory=set)
    uses: int = 0

    def score(self) -> float:
        s = sum(WEIGHT[k] for k in self.sources if k in WEIGHT)
        # Frequency is a tie-break: at most +2, and only once something
        # structural has put the word on the list at all.
        if self.uses and self.sources & set(STRUCTURAL):
            s += min(2.0, math.log10(self.uses + 1))
        return round(s, 3)


@dataclass
class LexiconReport:
    words: int
    compounds: int
    top: list[str]


def _stop() -> set[str]:
    from ..roles.api import _FRAME_WORDS, _NOT_VOCABULARY
    return set(_NOT_VOCABULARY) | set(_FRAME_WORDS)


def build(conn: sqlite3.Connection, root: str | Path) -> LexiconReport:
    """
    Read the index and the source it names; write `code_lexicon`.

    Replaces rather than accumulates, the same as the index: a lexicon is a
    function of the checkout and a re-run on a later commit must produce the
    answer for that commit.
    """
    root = Path(root)
    stop = _stop()
    entries: dict[str, Entry] = {}

    def touch(word: str, source: str, grain: str = "") -> None:
        word = word.strip()
        if not word or word in stop:
            return
        if " " not in word and (len(word) < 3 or word in stop
                                or singular(word) in stop
                                or (word.endswith("s") and word[:-1] in stop)):
            return
        e = entries.setdefault(word, Entry(word))
        e.sources.add(source)
        if grain:
            e.grains.add(grain)

    from .areas import is_attached

    # Tests and examples are indexed and findable, but their names are not
    # the program's vocabulary: on the first library measured, `color`,
    # `inout` and `naval` -- demo-app directories -- outranked half the real
    # API because a directory is the loudest structural signal there is.
    paths = [r["grain"] for r in conn.execute(
        "SELECT grain FROM code_index WHERE grain_kind = 'path' ORDER BY grain")
        if not is_attached(r["grain"])]
    fan_in = {r["grain"]: r["fan_in"] for r in conn.execute(
        "SELECT grain, fan_in FROM code_index WHERE grain_kind = 'path'")}
    has_symbols = {r["g"] for r in conn.execute(
        "SELECT DISTINCT substr(grain, 1, instr(grain, '::') - 1) AS g "
        "FROM code_index WHERE grain_kind = 'symbol'")}

    uses: Counter = Counter()
    bigrams: Counter = Counter()

    for rel in paths:
        segs = rel.split("/")
        # Nothing under a dot-directory. `.github/workflows/release.yml` is a
        # CI file whose keys are GitHub's vocabulary -- `uses`, `runs-on`,
        # `steps` -- and it put `uses` on cnt's list above `provider`.
        if any(seg.startswith(".") for seg in segs[:-1]):
            continue
        # Directories. Every component but the last, and not the generic ones.
        for d in segs[:-1]:
            if d.lower() in GENERIC_DIRS or d.startswith("."):
                continue
            for w in (singular(p) for p in parts(d)):
                touch(w, "dir", rel)
        # The file's stem.
        name = segs[-1]
        stem = name.rsplit(".", 1)[0] if "." in name else name
        # `esbuild.config.mjs`, `vite.config.ts`, `.eslintrc`: tooling, whose
        # stem names a tool and not a thing in the product.
        tooling = ".config" in stem.lower() or stem.lower().endswith(("rc", ".conf"))
        if (stem.lower() not in GENERIC_STEMS and name.lower() not in MANIFESTS
                and not name.startswith(".") and not tooling):
            ps = parts(stem)
            if len(ps) == 1:
                touch(singular(ps[0]), "file", rel)
            elif len(ps) > 1:
                touch(compound(stem), "file", rel)
                for w in (singular(p) for p in ps):
                    touch(w, "file", rel)

        f = root / rel
        if not f.is_file():
            continue
        try:
            body = f.read_text(encoding="utf-8", errors="replace")
        except OSError:                                     # pragma: no cover
            continue

        is_code = for_path(name) is not None
        if is_code:
            for line in body.splitlines():
                m = _DECL.match(line)
                if m:
                    kind, sym = m.group("kind"), m.group("name")
                    ps = parts(sym)
                    if kind in TYPE_KINDS:
                        # The head noun is what was declared; the rest of the
                        # name qualifies it. `FilteredOpenerMissingNotice`
                        # declares a notice, and `filtered` is not a type.
                        if 1 < len(ps) <= MAX_COMPOUND:
                            touch(compound(sym), "decl_type", rel)
                        if ps:
                            touch(singular(ps[-1]), "decl_type", rel)
                            for w in (singular(p) for p in ps[:-1]):
                                touch(w, "decl_part", rel)
                    else:
                        for w in (singular(p) for p in ps):
                            touch(w, "decl_fn", rel)
                # Every identifier word, for frequency and for bigrams.
                for ident in re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}", line):
                    ps = [singular(p) for p in parts(ident)]
                    for w in ps:
                        if w not in stop and len(w) >= 3:
                            uses[w] += 1
                    for a, b in zip(ps, ps[1:]):
                        # Both parts words: `intents_to` split to (intent, to)
                        # and the orientation's "intents_to" promoted "intent
                        # to" as a term of the project.
                        if (a not in stop and b not in stop
                                and len(a) >= 3 and len(b) >= 3):
                            bigrams[(a, b)] += 1
        else:
            # The authoring surface: a data file the code reads, or a manifest.
            # Its keys are what the project asks a user (or a registry) to
            # write, and the answer key's own vocabulary is written from that
            # side.
            # A manifest's keys are a contract with a registry, not vocabulary
            # -- `version`, `main`, `devDependencies` -- so they are left to the
            # Architect. JSON counts only when the code imports it; YAML and
            # TOML at all, because a schema is usually one of those.
            surface = rel not in has_symbols and name.lower() not in MANIFESTS and (
                fan_in.get(rel, 0) > 0
                or name.lower().endswith((".yaml", ".yml", ".toml")))
            if surface:
                for line in body.splitlines()[:400]:
                    m = _KEY.match(line)
                    if not m:
                        continue
                    key = m.group("key")
                    if key.lower() in MANIFESTS or len(key) < 3:
                        continue
                    for w in (singular(p) for p in parts(key)):
                        touch(w, "surface", rel)
                    # And the key itself, verbatim: `intents_to` split into
                    # `intents` + a stopword and the authoring grammar never
                    # became a candidate term. What a user literally types is
                    # a word of the project in its own spelling.
                    if "_" in key or "-" in key:
                        touch(key.lower().replace("-", "_"), "key", rel)

    for word, e in entries.items():
        e.uses = uses.get(word, 0) if " " not in word else sum(
            uses.get(w, 0) for w in word.split())

    # The prose's own names, after the code has said everything it will.
    # Family is computed from the code entries as they stand, so a README
    # that says "invoices" adds nothing to a lexicon that declares `Invoice`.
    readme = next((rel for rel in paths if "/" not in rel
                   and re.match(r"(?i)readme(\.|$)", rel)), None)
    if readme and (root / readme).is_file():
        family: set[str] = set()
        for word in entries:
            family.add(singular(word))
            family.update(singular(w) for w in parts(word))
        try:
            text = (root / readme).read_text(encoding="utf-8", errors="replace")
        except OSError:                                     # pragma: no cover
            text = ""
        for w, n in prose_names(text, family, stop):
            e = entries.setdefault(w, Entry(w))
            e.sources.add("prose")
            e.grains.add(readme)
            if not e.uses:
                e.uses = n

    # Bigrams are kept for the scheduler, which decides at frontier time whether
    # an orientation item names one of them -- `global intent` is two ordinary
    # words until the account of the program says "global intents" and the
    # code says `globalIntents` thirty times.
    conn.execute("DELETE FROM code_lexicon")
    rows = []
    for word, e in entries.items():
        if not (e.sources & set(STRUCTURAL) or "prose" in e.sources):
            continue
        rows.append((word, json.dumps(sorted(e.sources)),
                     sorted(e.grains)[0] if len(e.grains) == 1 else
                     (json.dumps(sorted(e.grains)[:4]) if e.grains else ""),
                     e.score(), e.uses, 1 if " " in word else 0))
    conn.executemany(
        "INSERT INTO code_lexicon (word, sources, grain, score, uses, compound) "
        "VALUES (?, ?, ?, ?, ?, ?)", rows)
    conn.execute("INSERT OR REPLACE INTO config (key, value) VALUES "
                 "('lexicon_bigrams', ?)",
                 (json.dumps([[a, b, n] for (a, b), n in bigrams.most_common(400)
                              if n >= 3]),))

    ranked_rows = sorted(rows, key=lambda r: (-r[3], r[0]))
    return LexiconReport(words=len(rows), compounds=sum(r[5] for r in rows),
                         top=[r[0] for r in ranked_rows[:20]])


def ranked(conn: sqlite3.Connection) -> list[dict]:
    """Every lexicon row, highest score first. Pure read."""
    return [dict(r) for r in conn.execute(
        "SELECT word, sources, grain, score, uses, compound FROM code_lexicon "
        "ORDER BY score DESC, word")]
