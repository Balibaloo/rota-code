"""
Score a finished run against the cnt answer key.

    python probes/cnt/score.py .rota/cnt_ix.db [.rota/cnt_new.db ...]

Three sections, in increasing difficulty, and the third is not scored:

  presence        is the term in the glossary at all, under any spelling
  must_not_mean   does a recorded sense contain a word the key forbids
  constraints     were the real commitments found, and were the decoys avoided

`must_not_mean` is the only mechanical check on understanding here. It works
because the wrong answer was written down before the run, not judged after it.

Term identity is not `==`. The glossary holds whatever spelling the session
chose -- `NaturalDate` where the key says `natural_date` -- and slugifying does
not split camelCase, so the key carries `aliases` and this compares against all
of them. A scorer that assumes one spelling under-reports by exactly the terms
whose spelling the run happened to pick differently, which is the same family of
mistake as comparing `Alarm` to `alarm`.
"""
from __future__ import annotations

import re
import sqlite3
import sys
from pathlib import Path

import yaml

KEY = Path(__file__).parent / "answer_key.yaml"


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.strip().lower()).strip("_")


def spellings(term: str, spec: dict) -> list[str]:
    return [slug(n) for n in [term, *(spec.get("aliases") or [])]]


def reachable(conn) -> set[str] | None:
    """
    The words a session could have been offered, at all, in any area.

    `terms_required present` had the same defect `must_not_mean` was fixed for
    below: `4 of 10` renders two different runs identically. Four of ten
    reachable and every one found is a full house. Four of ten with six
    reachable and missed is a failure. The number was the same for six runs and
    it was the first of those the whole time.

    `code_vocabulary` offers `uses.most_common(8)` per area. Six of cnt's ten
    required terms are in no area's eight, so no session was ever shown them,
    and three of those cannot be in any list of single words at all --
    `variableType` decomposes to `variable`, `filterSet` to `filter`, because
    `type` and `set` are stopwords. The ceiling is a property of the pipeline
    and belongs in the denominator, not in the model's score.

    Imported from `rota` rather than reimplemented. A scorer carrying its own
    copy of the decomposition would drift from the thing it is measuring, which
    is the failure this whole probe exists to catch.

    Returns `None` when the repository is not on disk to be read -- unknown is
    not the same as zero, which is the point of the function.
    """
    import sys
    from collections import Counter

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    try:
        from rota.onboarding.languages import for_path
        from rota.roles.api import _tells_you_something, _words_in
    except ImportError:                                     # pragma: no cover
        return None

    row = conn.execute(
        "SELECT value FROM config WHERE key = 'project_root'").fetchone()
    if not row or not Path(row["value"]).is_dir():
        return None
    root = Path(row["value"])

    offered: set[str] = set()
    areas = [r["area"] for r in conn.execute(
        "SELECT DISTINCT area FROM code_index")]
    for area in areas:
        paths = sorted({r["grain"].split("::")[0] for r in conn.execute(
            "SELECT grain FROM code_index WHERE area = ?", (area,))})
        uses: Counter = Counter()
        shown: set[str] = set()
        for rel in (p for p in paths if for_path(p.split("/")[-1]) is not None):
            f = root / rel
            if not f.is_file():
                continue
            for line in f.read_text(encoding="utf-8",
                                    errors="replace").splitlines():
                worth = _tells_you_something(line)
                for w in set(_words_in(line)):
                    uses[w] += 1
                    if worth > 0:
                        shown.add(w)
        # `uses` counts every line; a word with no line worth showing is cut
        # after the ranking, by `if not picks: continue`. So the offer is the
        # top eight *intersected with* the words that have an example, which is
        # narrower than the top eight and has to be measured that way.
        offered.update(w for w, _ in uses.most_common(8) if w in shown)
    return offered


def transcribed(conn) -> tuple[list[str], int]:
    """
    Which glossary terms are a name copied out of the code index.

    The worklist's own finding about the grain-list era -- *"21 of the 28 terms
    written across the first four runs were exactly a symbol name or a path
    fragment"* -- was counted by hand, once, and never became a check. So the
    two context designs have only ever been compared on recall, which is
    `terms_required`, and recall cannot see the difference: a run can hold
    `intent` and `frontmatter` while everything around them is
    `fmValidateIntent`, `getRelativePath` and `TemplateVariableVariables_Text`.

    That is what the answer key means by a definition being *worth nothing to
    the next reader*, and it is mechanically checkable, which `must_not_mean`
    was supposed to be the only one of.

    A term counts as transcribed when it is a name the index already held **and
    it is made of more than one word**. The second half is not optional. This
    codebase names its files after its concepts -- `intent`, `note`, `folder`,
    `template`, `text` are all both domain terms and filenames -- so matching on
    the name alone scores the right answer as the failure. Measured: it called
    G 47% transcribed, on a list whose hits were `intent`, `note` and `folder`.

    Compoundness is what separates them, and it separates them completely.
    `FilteredOpenerMissingNotice`, `TemplateVariableVariablesLut`,
    `fmValidateIntent`, `getRelativePath` are things the code calls something;
    `intent` is a thing the project is about. A word the codebase chose for a
    file is the codebase naming its own ontology, which is signal. A symbol
    copied whole is a session answering the question it was handed.

    Not a substring either: `intent` inside `getIntentsFromFM` is the word being
    recovered, which is the opposite of the failure.
    """
    import re
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    try:
        from rota.roles.api import _words_in
    except ImportError:                                     # pragma: no cover
        def _words_in(t):                                   # noqa: D103
            return re.sub(r"([a-z0-9])([A-Z])", r" ", t).replace("_", " ").split()

    names: set[str] = set()
    for r in conn.execute("SELECT grain FROM code_index"):
        path, _, sym = r["grain"].partition("::")
        if sym:
            names.add(sym.lower())
        for seg in path.split("/"):
            names.add(re.sub(r"\.[a-z]+$", "", seg).lower())

    terms = [r["term"] for r in conn.execute("SELECT term FROM glossary_terms")]
    copied = [t for t in terms
              if t.lower() in names and len(set(_words_in(t))) > 1]
    return copied, len(terms)


def score(db_path: str | Path) -> dict:
    key = yaml.safe_load(KEY.read_text(encoding="utf-8"))
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row

    senses = {slug(r["term"]): f'{r["sense_short"] or ""} {r["sense_body"] or ""}'
              for r in conn.execute(
                  "SELECT term, sense_short, sense_body FROM glossary_terms")}

    # presence -------------------------------------------------------------
    mnm = key["must_not_mean"]
    present, absent = [], []
    for term in key["terms_required"]:
        names = spellings(term, mnm.get(term, {}))
        (present if any(n in senses for n in names) else absent).append(term)

    # Named but not defined. See `spelling_variants` in the key: separate from
    # `terms_required` so every historical score stays comparable, and reported
    # beside it so the blindness is visible rather than silent.
    variants = key.get("spelling_variants") or {}
    named = [t for t in absent
             if {slug(n) for n in variants.get(t, [])} & set(senses)]

    # How many of them any session was ever offered. See `reachable`.
    # Only for a run that actually used the word list. `reachable` describes
    # what `code_vocabulary` would have offered, which is a counterfactual for a
    # design that never called it -- and a counterfactual rendered as a
    # denominator is the same silent wrong reading this whole file is being
    # fixed for. A grain-list run is measured on recall and shape, not on this.
    used_vocab = conn.execute(
        "SELECT 1 FROM tool_calls WHERE fn = 'code.vocabulary' LIMIT 1").fetchone()
    offered = reachable(conn) if used_vocab else None
    if offered is None:
        within = unreachable = None
    else:
        def could(t):
            # The term's own spellings, never their parts. Splitting
            # `variable_type` and accepting it because `variable` is offered
            # would score the compound as reachable on the strength of the word
            # that replaced it -- which is the exact conflation being measured.
            return any(n in offered for n in spellings(t, mnm.get(t, {})))
        within = [t for t in key["terms_required"] if could(t)]
        unreachable = [t for t in absent if t not in within]

    # must_not_mean --------------------------------------------------------
    # A zero here means two different things and used to render as one. On the
    # run after the indexer fix it read `must_not_mean: 0` against a baseline of
    # 5, which looks like every trap avoided and was in fact none of those terms
    # written at all. `scored` is how many of them the glossary actually holds,
    # and it is printed on the same line so the zero cannot be read alone.
    hits, scored = [], 0
    for term, spec in mnm.items():
        for name in spellings(term, spec):
            if name not in senses:
                continue
            scored += 1
            said = senses[name].lower()
            bad = next((b for b in spec["not"] if b.lower() in said), None)
            if bad:
                hits.append((term, bad, senses[name].strip()[:60]))
            break

    # synthesis ------------------------------------------------------------
    # A row that supersedes several is a sense composed from readings; a row
    # that supersedes one is a duplicate collapsed. The two are different acts
    # and reporting them as one number would hide which happened -- the same
    # reason `named, not defined` sits on its own line.
    superseded: dict[str, list[str]] = {}
    for r in conn.execute("SELECT id, superseded_by FROM glossary_terms "
                          "WHERE superseded_by IS NOT NULL"):
        superseded.setdefault(r["superseded_by"], []).append(r["id"])
    composed = []
    for keep, gone in sorted(superseded.items()):
        row = conn.execute("SELECT sense_short FROM glossary_terms WHERE id = ?",
                           (keep,)).fetchone()
        composed.append((keep, len(gone), (row["sense_short"] if row else "") or ""))

    # transcription --------------------------------------------------------
    copied, written = transcribed(conn)

    # What was written that the key does not recognise at all. The two designs
    # fail differently and each metric above sees only one of them. The grain
    # list transcribes symbols -- `TemplateVariableVariablesLut`, 88% of v1.
    # The word list transcribes nothing and instead defines what the shredder
    # produced: `show`, `private`, `chosen`, `filtered`, `natural`, `object`.
    # Both are the same act. Whatever is on the list gets defined, and the list
    # is therefore the instruction, whichever list it is.
    known = {slug(n) for n in [*key["terms_expected"], *key["must_not_mean"],
                               *key["terms_required"]]}
    known |= {k.replace("_", "") for k in known}
    off_key = sorted({r["term"] for r in conn.execute(
        "SELECT term FROM glossary_terms") if slug(r["term"]) not in known})

    # constraints ----------------------------------------------------------
    cons = [dict(r) for r in conn.execute(
        "SELECT id, headline, text FROM constraints WHERE id <> 'k0'")]
    bound: dict[str, set[str]] = {}
    for r in conn.execute("SELECT constraint_id, grain FROM constraint_bindings"):
        bound.setdefault(r["constraint_id"], set()).add(r["grain"])
    required = set(key["constraints_required"])
    # The key's own matching_note says it for terms: identity is not `==`.
    # A required constraint's id is a prediction slug; a run's id derives
    # from whatever headline the session wrote. `constraints_required_match`
    # gives each required commitment word-groups: one constraint matches when
    # every group intersects its headline+text. The frontmatter contract was
    # found -- "fails silently without providing an error message", the exact
    # missing fact -- and scored 0 under id equality.
    match = key.get("constraints_required_match") or {}
    found = {c["id"] for c in cons} & required
    for rid, groups in match.items():
        for c in cons:
            toks = set(re.findall(r"[a-z0-9_]+",
                                  f"{c['headline']} {c['text'] or ''}".lower()))
            if all(toks & {w.lower() for w in g} for g in groups):
                found.add(rid)
                break

    # A constraint is a decoy when every grain it governs is one. Mixed
    # bindings are reported separately rather than scored: a commitment bound
    # to three real files and a build script is a different mistake from one
    # bound to the build script alone, and calling them the same number hides
    # which happened.
    decoys = set(key["constraint_decoys"])
    decoyed = [c["id"] for c in cons
               if bound.get(c["id"]) and bound[c["id"]] <= decoys]
    mixed = [c["id"] for c in cons
             if bound.get(c["id"]) and not bound[c["id"]] <= decoys
             and bound[c["id"]] & decoys]
    empty = [c["id"] for c in cons if not (c["text"] or "").strip()]

    return {
        "db": str(db_path),
        "terms_present": present, "terms_absent": absent,
        "terms_required": len(key["terms_required"]),
        "terms_reachable": within, "terms_unreachable": unreachable,
        "terms_named": named,
        "hits": hits, "scored": scored, "traps": len(mnm),
        "constraints_written": len(cons),
        "constraints_required_found": sorted(found),
        "constraints_required": sorted(required),
        "decoys_recorded": decoyed, "decoy_mixed": mixed,
        "empty_bodies": empty,
        "glossary_size": len(senses),
        "copied": copied, "written": written, "off_key": off_key,
        "composed": composed,
    }


def render(s: dict) -> None:
    print(f"\n=== {s['db']} ===")
    print(f"  glossary               {s['glossary_size']} terms")
    print(f"  terms_required present {len(s['terms_present'])} of "
          f"{s['terms_required']}   {s['terms_present']}")
    if s["terms_named"]:
        print(f"    named, not defined   {len(s['terms_present'])}+"
              f"{len(s['terms_named'])} = "
              f"{len(s['terms_present']) + len(s['terms_named'])} of "
              f"{s['terms_required']}  {s['terms_named']}  (the code's own "
              f"spelling, sense usually a label)")
    if s["terms_reachable"] is not None:
        # The denominator, on the same line as the numerator, for the same
        # reason `scored` sits beside `must_not_mean hits`: `4 of 10` rendered
        # a full house and a failure identically for six runs.
        hit = [t for t in s["terms_present"] if t in s["terms_reachable"]]
        print(f"    of those offered     {len(hit)} of "
              f"{len(s['terms_reachable'])}"
              f"   <- the score the run earned")
        beyond = [t for t in s["terms_present"] if t not in s["terms_reachable"]]
        if beyond:
            print(f"    found off the list   {beyond}  (read, not ranked)")
    if s["terms_absent"]:
        print(f"    absent               {s['terms_absent']}")
    if s["terms_unreachable"]:
        print(f"    never offered        {s['terms_unreachable']}"
              f"  <- no area's top 8 holds these; not the session's failure")
    verdict = ("nothing to score — none of those terms were written"
               if s["scored"] == 0 else
               f"{s['scored']} of {s['traps']} trap terms present")
    print(f"  must_not_mean hits     {len(s['hits'])}   ({verdict})")
    for term, bad, said in s["hits"]:
        print(f"    {term:14} forbidden {bad!r:22} -> {said!r}")
    for keep, n, short in s["composed"]:
        act = "synthesised from" if n > 1 else "merged with"
        print(f"  {act:18s} {n}   {keep}: {short[:54]!r}")
    if s["written"]:
        pct = 100 * len(s["copied"]) / s["written"]
        print(f"  copied from the index  {len(s['copied'])} of {s['written']} "
              f"terms ({pct:.0f}%)  {s['copied'][:6]}")
    if s["written"]:
        print(f"  not in the key at all  {len(s['off_key'])} of {s['written']} "
              f"  {s['off_key'][:8]}")
    print(f"  constraints written    {s['constraints_written']}"
          f"  (empty bodies: {len(s['empty_bodies'])})")
    print(f"  required found         {len(s['constraints_required_found'])} of "
          f"{len(s['constraints_required'])}  {s['constraints_required_found']}")
    print(f"  decoys recorded        {len(s['decoys_recorded'])}  "
          f"{s['decoys_recorded']}")
    if s["decoy_mixed"]:
        print(f"    partly on a decoy    {s['decoy_mixed']}")


if __name__ == "__main__":
    paths = sys.argv[1:] or [".rota/cnt_new.db"]
    for p in paths:
        render(score(p))
    print()
