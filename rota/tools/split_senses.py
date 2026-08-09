"""
One name, one job: split the seven words that were carrying two meanings each.

Found mechanically by `python -m rota.tools.vocabulary --analyse`, which reports
a collision when the same word appears as more than one *kind* of thing — an
operation and a state, a node and a verb. Every one of them was survivable in
isolation and none of them was survivable in a prompt, where the reader has no
type information and no way to ask.

    consult   operation / message verb / session mode
              -> the operation keeps it (a role consults its own artefact)
              -> the message verb becomes `ask`
              -> the session mode becomes `readonly`, which says what it *is*
                 rather than what it was for

    brief     artefact / message verb
              -> the artefact keeps it; the verb becomes `deliver`
              (`broadcast` is the informal name for delivering to all three, not
               a wire verb — three edges, one each)

    index     operation / reach value
              -> the reach value keeps it; `brief.index` becomes `brief.list`,
                 matching `ledger.list`, which already did it right

    batch     operation / reach value
              -> the reach value keeps it; `batches.batch` becomes
                 `batches.group`, which is the actual act

    scope     item kind / ordinary English
              -> the kinds become `in_scope` / `out_of_scope`, freeing "scope"
                 to mean what everyone already thinks it means. `non_goal` goes
                 with it: the opposite of in-scope is out-of-scope, and naming
                 it after goals invited the question of whose

    utterance journal row / message cause
              -> a journal holds *entries*; the cause becomes `conversation`

    amend     owner's operation / principal's ruling
              -> the operation keeps it (amending is something the owner does);
                 the ruling becomes `revise`, which is a request for that act
                 rather than the act

Run once, from the repo root:

    python -m rota.tools.split_senses
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOTS = [Path("rota"), Path("tests/rota")]
SUFFIXES = {".py", ".md", ".json", ".sql", ".js", ".html", ".tools"}
SKIP = {"AGREED.md", "rename_roles.py", "split_senses.py",
        "amend_graph.py", "amend_graph2.py"}   # historical records, left alone

GRAPH = Path("rota/design/graph.json")


# ---------------------------------------------------------------------------
# graph.json is structural: `consult` and `brief` are told apart by edge type,
# not by anything in the text, so a textual pass cannot see the difference.
# ---------------------------------------------------------------------------

EDGE_VERBS = [
    # (edge type, old verb, new verb)
    ("messages", "consult", "ask"),
    ("messages", "brief",   "deliver"),
    ("writes",   "batch",   "group"),
    ("reads",    "index",   "list"),
]

EDGE_NOUNS = {
    "utterance":                        "entry",
    "scope, non-goals":                 "in-scope and out-of-scope items",
    "scope + non-goals":                "in-scope and out-of-scope items",
    "per-item approve / contest / amend": "per-item approve / contest / revise",
    "amend or restart":                 "revise or restart",
}


def fix_graph() -> None:
    g = json.loads(GRAPH.read_text(encoding="utf-8"))
    changed = 0
    for e in g["edges"]:
        for etype, old, new in EDGE_VERBS:
            if e["type"] == etype and e.get("v") == old:
                e["v"] = new
                changed += 1
        if e.get("n") in EDGE_NOUNS:
            e["n"] = EDGE_NOUNS[e["n"]]
            changed += 1
    GRAPH.write_text(json.dumps(g, indent=2, ensure_ascii=False) + "\n",
                     encoding="utf-8")
    print(f"graph.json: {changed} edge fields")


# ---------------------------------------------------------------------------
# Everything else is textual, but ordered: the specific forms must land before
# the general ones, or `utterances` becomes `entrys` and `mode="consult"` gets
# rewritten by the rule meant for `problem.consult()`.
# ---------------------------------------------------------------------------

SUBS: list[tuple[str, str]] = [
    # --- utterance -> entry -------------------------------------------------
    (r"'message','utterance','gate','tick','receipt'",
     "'message','conversation','gate','tick','receipt'"),
    (r"\bspan_utterance\b", "span_entry"),
    (r"\butterance_id\b", "entry_id"),
    (r"\brecord_utterance\b", "record_entry"),
    (r"\butterance_for\b", "entry_for"),
    (r"\butterances\b", "entries"),
    (r"\bUtterances\b", "Entries"),
    (r'"utterance:', '"entry:'),
    (r'f"utterance:', 'f"entry:'),
    (r"\bu_m1\b", "e_m1"),
    (r'"u_\{', '"e_{'),
    (r"f'u_\{", "f'e_{"),
    (r"\butterance\b", "entry"),
    (r"\bUtterance\b", "Entry"),

    # --- session mode consult -> readonly -----------------------------------
    (r"\bConsultWriteError\b", "ReadonlyWriteError"),
    (r"mode\s*=\s*\"consult\"", 'mode="readonly"'),
    (r"mode\s*==\s*\"consult\"", 'mode == "readonly"'),
    (r"'normal','consult'", "'normal','readonly'"),
    (r"\bMODE: consult\b", "MODE: readonly"),
    (r"\bs_consult\b", "s_readonly"),
    (r"\btest_consult_", "test_readonly_"),
    (r"\btest_i4_consult_", "test_i4_readonly_"),
    (r"\bconsult-mode session", "readonly session"),
    (r"\bconsult mode\b", "readonly mode"),
    (r"\bconsult session", "readonly session"),
    (r"\bconsult writes\b", "readonly writes"),
    (r"\bconsult disturbed\b", "readonly disturbed"),
    (r"\bconsult-mode\b", "readonly"),

    # --- message verbs ------------------------------------------------------
    (r"\bmsg\.consult_", "msg.ask_"),
    (r"\bmsg\.brief_", "msg.deliver_"),

    # --- operations ---------------------------------------------------------
    (r'@op\("brief", "index"\)', '@op("brief", "list")'),
    (r"\bbrief_index\b", "brief_list"),
    (r"\bbrief\.index\b", "brief.list"),
    (r'@op\("batches", "batch"\)', '@op("batches", "group")'),
    (r"\bbatches_batch\b", "batches_group"),
    (r"\bbatches\.batch\b", "batches.group"),
    (r'verb in \("consult", "index"\)', 'verb in ("consult", "list")'),

    # --- item kinds ---------------------------------------------------------
    (r"kind IN \('scope','non_goal'\)", "kind IN ('in_scope','out_of_scope')"),
    (r'\("scope", "non_goal"\)', '("in_scope", "out_of_scope")'),
    (r'kind: str = "scope"', 'kind: str = "in_scope"'),
    (r"kind='scope'", "kind='in_scope'"),
    (r'"kind": "scope"', '"kind": "in_scope"'),
    (r"kind = 'scope'", "kind = 'in_scope'"),
    (r"'scope','decided'", "'in_scope','decided'"),
    (r"'scope', 'decided'", "'in_scope', 'decided'"),
    (r'"non_goal"', '"out_of_scope"'),
    (r"'non_goal'", "'out_of_scope'"),

    # --- the principal's ruling --------------------------------------------
    (r"approve\|contest\|amend", "approve|contest|revise"),
    (r"approve, contest or amend", "approve, contest or revise"),
    (r"approve, contest, or amend", "approve, contest, or revise"),
]

COMPILED = [(re.compile(p), r) for p, r in SUBS]


def targets() -> list[Path]:
    out = []
    for root in ROOTS:
        for p in sorted(root.rglob("*")):
            if p.is_dir() or "__pycache__" in p.parts:
                continue
            if p.suffix in SUFFIXES and p.name not in SKIP and p != GRAPH:
                out.append(p)
    return out


def main() -> None:
    fix_graph()

    if Path("rota/prompts/gatekeeper/consult.md").exists():
        subprocess.run(["git", "mv", "rota/prompts/gatekeeper/consult.md",
                        "rota/prompts/gatekeeper/readonly.md"], check=True)
        print("  gatekeeper/consult.md -> readonly.md")

    changed = 0
    for path in targets():
        before = path.read_text(encoding="utf-8")
        after = before
        for pattern, repl in COMPILED:
            after = pattern.sub(repl, after)
        if after != before:
            path.write_text(after, encoding="utf-8")
            changed += 1
            print(f"  {path}")
    print(f"{changed} files rewritten")
    print("\nnow check: python -m rota.tools.vocabulary --analyse")


if __name__ == "__main__":
    sys.exit(main())
