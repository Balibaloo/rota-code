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

    # constraints ----------------------------------------------------------
    cons = [dict(r) for r in conn.execute(
        "SELECT id, headline, text FROM constraints WHERE id <> 'k0'")]
    bound: dict[str, set[str]] = {}
    for r in conn.execute("SELECT constraint_id, grain FROM constraint_bindings"):
        bound.setdefault(r["constraint_id"], set()).add(r["grain"])
    required = set(key["constraints_required"])
    found = {c["id"] for c in cons} & required

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
        "hits": hits, "scored": scored, "traps": len(mnm),
        "constraints_written": len(cons),
        "constraints_required_found": sorted(found),
        "constraints_required": sorted(required),
        "decoys_recorded": decoyed, "decoy_mixed": mixed,
        "empty_bodies": empty,
        "glossary_size": len(senses),
    }


def render(s: dict) -> None:
    print(f"\n=== {s['db']} ===")
    print(f"  glossary               {s['glossary_size']} terms")
    print(f"  terms_required present {len(s['terms_present'])} of "
          f"{s['terms_required']}   {s['terms_present']}")
    if s["terms_absent"]:
        print(f"    absent               {s['terms_absent']}")
    verdict = ("nothing to score — none of those terms were written"
               if s["scored"] == 0 else
               f"{s['scored']} of {s['traps']} trap terms present")
    print(f"  must_not_mean hits     {len(s['hits'])}   ({verdict})")
    for term, bad, said in s["hits"]:
        print(f"    {term:14} forbidden {bad!r:22} -> {said!r}")
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
