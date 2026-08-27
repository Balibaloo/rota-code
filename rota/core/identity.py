"""
Every table declares its sameness rule.

The over-production investigation (2026-08-28) found one disease behind four
organs: a model re-emits an act it already performed, and any table whose id
is model-invented turns each re-issue into a new row. Every organ that healed
did so the same way -- identity derived from content, never from the invented
id -- and each guard was built separately, by incident. This registry is the
pattern written down, and its lint is the trial run the principal asked for
("ok lets test it out", 2026-08-29): a new table fails the build until it
says what makes two of its rows the same one. LAWS.md stays untouched until
this has lived quietly for a while.

The kinds, in the vocabulary the guards actually use:

  words      same normalised words are the same row (tickets; criteria per
             ticket)
  span       the same span of the same source is the same row (statements)
  term       the id derives from the word; writing it again amends (glossary)
  slug       the id derives from the headline; a same-subject twin is refused
             toward the challenge (constraints)
  relation   the key is a relationship's cardinality, not content (batches:
             one item's open work is one batch; model_areas: one row per
             pinned area; join tables: the pair is the row)
  supersede  a later write for the same anchor replaces the staged one
             (tests, per criterion)
  content    the row IS a content hash of something external (code_index
             grains carry the source's hash; git is the precedent)
  keyed      an ordinary key-value store keyed by a declared name (config)
  journal    append-only record of events; deduplication would falsify
             history, so re-saying something is two events on purpose
  ephemeral  runtime state, torn down with what holds it; identity is the
             holder
  unkeyed    no sameness rule exists yet. Legal, counted, and honest -- the
             registry's job is to expose this, not to hide it

Each entry: kind, then where the rule is enforced or why the kind is right.
"""
from __future__ import annotations

NATURAL_KEYS: dict[str, tuple[str, str]] = {
    # ---- keyed state: the five healed organs and their relatives ----------
    "glossary_terms": ("term", "glossary.amend derives the id from the word; "
                               "a second sense must be asked for"),
    "constraints": ("slug", "model.amend derives the id from the headline; "
                            "the twin guard refuses a same-subject second "
                            "toward the challenge"),
    "statements": ("span", "brief.segment: the same span twice is the same "
                           "statement, whatever id it is given"),
    "tickets": ("words", "tickets.slice: the same words are the same ticket"),
    "criteria": ("words", "criteria.specify: same ticket, same words, one "
                          "row; a second criterion needs a second sentence"),
    "batches": ("relation", "batches.group: one item's open work is one "
                            "batch; abandoned/merged leave the game"),
    "tests": ("supersede", "a re-encode for the same criterion withdraws the "
                           "staged one; versions carry later rewrites"),
    "model_areas": ("relation", "one row per pinned area; the partition is "
                                "the writer"),
    "config": ("keyed", "declared settings only; config_history is its "
                        "journal"),

    # ---- joins: the pair is the row ---------------------------------------
    "item_statements": ("relation", "the (item, statement) pair"),
    "batch_tickets": ("relation", "the (batch, ticket) pair"),
    "constraint_bindings": ("relation", "the (constraint, grain) pair; "
                                        "constraint zero's are derived"),

    # ---- content-addressed ------------------------------------------------
    "code_index": ("content", "grains carry the source's content hash; the "
                              "indexer is the only writer"),
    "code_edges": ("content", "derived with the index, from the same parse"),
    "code_lexicon": ("content", "derived with the index; rebuilt by repin"),
    "batch_touch": ("content", "the predicted touch set, derived per batch"),

    # ---- journals: re-saying is two events, on purpose --------------------
    "entries": ("journal", "the principal's words, in order; ts_order is "
                           "the identity that matters"),
    "messages": ("journal", "sent is sent; status moves, rows never merge"),
    "sessions": ("journal", "one row per wake taken"),
    "turns": ("journal", "the transcript"),
    "tool_calls": ("journal", "the evidence log"),
    "receipts": ("journal", "what a session touched"),
    "claims": ("journal", "who held what, when"),
    "ledger": ("journal", "assumptions as made; deduping would falsify"),
    "decisions": ("journal", "reasons as given"),
    "verdicts": ("journal", "one judgement of one commit"),
    "test_runs": ("journal", "one execution, one row"),
    "survey_records": ("journal", "attestations; the latest whose hash still "
                                  "matches is the live one"),
    "survey_citations": ("journal", "what a survey opened"),
    "challenges": ("journal", "one attack on one claim"),
    "frame_rulings": ("journal", "the principal's partition rulings"),
    "config_history": ("journal", "what every setting displaced"),
    "artefact_versions": ("journal", "the version trail itself"),
    "tick_attempts": ("journal", "the quarantine counter's memory"),
    "schedule_deps": ("relation", "the (before, after) pair"),
    "batch_dep_facts": ("relation", "the (batch, grain) pair"),
    "findings": ("journal", "what the challenge pass found"),
    "references_": ("keyed", "fetched documents, keyed by source"),

    # ---- ephemeral --------------------------------------------------------
    "checkpoints": ("ephemeral", "dies with deferral; valid=0 is the record"),
    "runtime_processes": ("ephemeral", "dies with the environment"),

    # ---- the honest column ------------------------------------------------
    "items": ("unkeyed", "scope rows; no sameness rule enforced yet. The "
                         "candidate is the statement it traces from -- filed, "
                         "not built, because items have not produced an "
                         "over-production incident"),
    "business_rules": ("unkeyed", "observed-era table; no incidents, no rule "
                                  "yet"),
}
