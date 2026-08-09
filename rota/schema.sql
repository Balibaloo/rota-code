-- rota schema.
--
-- Derived from TESTS.md §4 (the fixture definitions are the requirements list)
-- plus the amendments agreed before implementation. Every table here must be
-- able to represent every fixture in TESTS.md; where it could not, that was
-- raised as a spec challenge rather than papered over by widening a column.
--
-- Conventions:
--   * Ordering is expressed by integer sequence columns. Time is not a concept:
--     no dates, durations or deadlines appear anywhere in this file.
--   * Every state artefact carries a per-row version. artefact_versions carries
--     the per-table version bumped on each committed write.
--   * Index/body split on glossary_terms and constraints: `full` scope means the
--     full *index* (id + one line), never the full text. Bodies are fetched
--     singly. This is what keeps an 8k working set viable at any artefact size.

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- ---------------------------------------------------------------------------
-- Transcript and brief (Liaison)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS utterances (
    id          TEXT PRIMARY KEY,
    author      TEXT NOT NULL,              -- 'principal' | 'liaison'
    text        TEXT NOT NULL,
    ts_order    INTEGER NOT NULL,           -- sequence, not a timestamp
    version     INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS statements (
    id              TEXT PRIMARY KEY,
    span_utterance  TEXT NOT NULL REFERENCES utterances(id),
    span_start      INTEGER NOT NULL,
    span_end        INTEGER NOT NULL,
    text            TEXT NOT NULL,
    status          TEXT NOT NULL CHECK (status IN
                        ('proposed','ratified','superseded','contradicted','clarified')),
    supersedes      TEXT REFERENCES statements(id),
    version         INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX IF NOT EXISTS ix_statements_status ON statements(status);

-- ---------------------------------------------------------------------------
-- Problem statement (Gatekeeper)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS items (
    id            TEXT PRIMARY KEY,
    text          TEXT NOT NULL,
    kind          TEXT NOT NULL CHECK (kind IN ('scope','non_goal')),
    provenance    TEXT NOT NULL CHECK (provenance IN ('observed','decided')),
    approval      TEXT NOT NULL DEFAULT 'draft'
                  CHECK (approval IN ('draft','pending','approved','contested')),
    approval_ver  INTEGER,                  -- version the approval was granted at
    version       INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS item_statements (   -- refs: problem derives from brief
    item_id       TEXT NOT NULL REFERENCES items(id),
    statement_id  TEXT NOT NULL REFERENCES statements(id),
    PRIMARY KEY (item_id, statement_id)
);

-- ---------------------------------------------------------------------------
-- Glossary and rules (Terminologist). Index/body split.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS glossary_terms (
    id           TEXT PRIMARY KEY,
    term         TEXT NOT NULL,
    sense_short  TEXT NOT NULL,             -- the index row: one line, always loaded
    sense_body   TEXT,                      -- fetched singly, never in bulk
    provenance   TEXT NOT NULL CHECK (provenance IN ('observed','decided')),
    source_refs  TEXT NOT NULL DEFAULT '[]',
    version      INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX IF NOT EXISTS ix_glossary_term ON glossary_terms(term);

CREATE TABLE IF NOT EXISTS business_rules (
    id         TEXT PRIMARY KEY,
    text       TEXT NOT NULL,
    term_refs  TEXT NOT NULL DEFAULT '[]',
    version    INTEGER NOT NULL DEFAULT 1
);

-- ---------------------------------------------------------------------------
-- System model (Architect). Index/body split; bindings drive both the
-- structural-review trigger and binding-filtered index reads.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS constraints (
    id                   TEXT PRIMARY KEY,
    headline             TEXT NOT NULL,     -- the index row
    text                 TEXT,              -- fetched singly
    provenance           TEXT NOT NULL CHECK (provenance IN ('observed','decided')),
    rationale_decision   TEXT REFERENCES decisions(id),
    is_global            INTEGER NOT NULL DEFAULT 0,
    version              INTEGER NOT NULL DEFAULT 1
);

-- Bindings are rows, not a JSON blob: the structural trigger is a join.
-- A constraint with zero bindings is global — missing bindings must always mean
-- "always visible", never "invisible".
CREATE TABLE IF NOT EXISTS constraint_bindings (
    constraint_id  TEXT NOT NULL REFERENCES constraints(id),
    grain          TEXT NOT NULL,           -- path, symbol, table or route
    grain_kind     TEXT NOT NULL CHECK (grain_kind IN ('path','symbol','table','route')),
    resolves       INTEGER NOT NULL DEFAULT 1,  -- 0 once the grain leaves the index
    PRIMARY KEY (constraint_id, grain)
);

CREATE TABLE IF NOT EXISTS survey_records (
    id          TEXT PRIMARY KEY,
    area        TEXT NOT NULL,
    outcome     TEXT NOT NULL CHECK (outcome IN ('constraints_found','none_found')),
    refs        TEXT NOT NULL DEFAULT '[]',
    version     INTEGER NOT NULL DEFAULT 1
);

-- Citations make "surveyed" evidence rather than a claim: each cited grain is
-- validated against the code index, so a lazy surveyor cannot starve constraint
-- zero by asserting none_found everywhere.
CREATE TABLE IF NOT EXISTS survey_citations (
    survey_id   TEXT NOT NULL REFERENCES survey_records(id),
    grain       TEXT NOT NULL,
    resolves    INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (survey_id, grain)
);

-- Mechanical index of the codebase (tree-sitter/ripgrep). Not an artefact any
-- role writes: it is rebuilt, never decided.
CREATE TABLE IF NOT EXISTS code_index (
    grain       TEXT PRIMARY KEY,
    grain_kind  TEXT NOT NULL CHECK (grain_kind IN ('path','symbol','table','route')),
    area        TEXT,                        -- partition assignment, pinned by decision
    fan_in      INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS code_edges (      -- dependency graph, input to partitioning
    src   TEXT NOT NULL,
    dst   TEXT NOT NULL,
    PRIMARY KEY (src, dst)
);

-- ---------------------------------------------------------------------------
-- Backlog: three tables, one writer each. Law 1 means one writer per *row*;
-- per-table ownership is the strict form of that, and it is what closes the
-- old "backlog has three writers" risk.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS tickets (         -- Gatekeeper
    id       TEXT PRIMARY KEY,
    item_id  TEXT NOT NULL REFERENCES items(id),
    text     TEXT NOT NULL,
    version  INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS criteria (        -- Terminologist
    id         TEXT PRIMARY KEY,
    ticket_id  TEXT NOT NULL REFERENCES tickets(id),
    text       TEXT NOT NULL,
    term_refs  TEXT NOT NULL DEFAULT '[]',
    version    INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS batches (         -- Architect (priority: Gatekeeper)
    id        TEXT PRIMARY KEY,
    item_id   TEXT NOT NULL REFERENCES items(id),
    worktree  TEXT,
    head_commit TEXT,                        -- last commit the DB has a receipt for
    status    TEXT NOT NULL DEFAULT 'pending'
              CHECK (status IN ('pending','running','deferred','merged')),
    priority  INTEGER NOT NULL DEFAULT 0,
    version   INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS batch_tickets (
    batch_id   TEXT NOT NULL REFERENCES batches(id),
    ticket_id  TEXT NOT NULL REFERENCES tickets(id),
    PRIMARY KEY (batch_id, ticket_id)
);

-- Architect declares dependency *facts*; the scheduler derives the order.
CREATE TABLE IF NOT EXISTS batch_dep_facts (
    before_batch  TEXT NOT NULL REFERENCES batches(id),
    after_batch   TEXT NOT NULL REFERENCES batches(id),
    reason        TEXT,
    PRIMARY KEY (before_batch, after_batch)
);

-- Derived schedule. No role writes this — ordering carries no judgement beyond
-- the declared deps, so there is nothing for a role to decide.
CREATE TABLE IF NOT EXISTS schedule_deps (
    before_batch  TEXT NOT NULL REFERENCES batches(id),
    after_batch   TEXT NOT NULL REFERENCES batches(id),
    PRIMARY KEY (before_batch, after_batch)
);

-- ---------------------------------------------------------------------------
-- Tests (Tester). Criteria made executable, written before the diff exists.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS tests (
    id            TEXT PRIMARY KEY,
    batch_id      TEXT NOT NULL REFERENCES batches(id),
    criterion_id  TEXT NOT NULL REFERENCES criteria(id),
    path          TEXT NOT NULL,
    body          TEXT NOT NULL,
    version       INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS test_runs (       -- the mechanical gate before Critic
    id        TEXT PRIMARY KEY,
    batch_id  TEXT NOT NULL REFERENCES batches(id),
    test_id   TEXT NOT NULL REFERENCES tests(id),
    result    TEXT NOT NULL CHECK (result IN ('pass','fail','error')),
    attempt   INTEGER NOT NULL DEFAULT 1
);

-- ---------------------------------------------------------------------------
-- Journals: multi-writer, one author per entry, append-only.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS ledger (
    id             TEXT PRIMARY KEY,
    about_ref      TEXT NOT NULL,
    about_table    TEXT NOT NULL,
    default_taken  TEXT NOT NULL,
    status         TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open','resolved')),
    author         TEXT NOT NULL,
    version        INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS decisions (
    id               TEXT PRIMARY KEY,
    author           TEXT NOT NULL,
    text             TEXT NOT NULL,
    resolves_ledger  TEXT REFERENCES ledger(id),
    supersedes       TEXT REFERENCES decisions(id),
    refs             TEXT NOT NULL DEFAULT '[]',
    version          INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS verdicts (
    id                TEXT PRIMARY KEY,
    batch_id          TEXT NOT NULL REFERENCES batches(id),
    diff_ref          TEXT,
    result            TEXT NOT NULL CHECK (result IN ('pass','fail')),
    failed_criterion  TEXT REFERENCES criteria(id),
    version           INTEGER NOT NULL DEFAULT 1
);

-- ---------------------------------------------------------------------------
-- Runtime: messages, sessions, receipts, checkpoints, claims.
-- ---------------------------------------------------------------------------

-- Roots are principal utterances, gate events and ticks, so cause_id is nullable
-- and cause_kind records which kind of root a message hangs from.
CREATE TABLE IF NOT EXISTS messages (
    id          TEXT PRIMARY KEY,
    cause_id    TEXT REFERENCES messages(id),
    cause_kind  TEXT NOT NULL DEFAULT 'message'
                CHECK (cause_kind IN ('message','utterance','gate','tick','receipt')),
    thread_id   TEXT NOT NULL,
    from_role   TEXT NOT NULL,
    to_role     TEXT NOT NULL,
    verb        TEXT NOT NULL,
    body_refs   TEXT NOT NULL DEFAULT '[]',
    round_no    INTEGER NOT NULL DEFAULT 0,
    seq         INTEGER NOT NULL,
    -- A crashed session leaves its trigger on the frontier. Without a bound,
    -- the scheduler wakes the same role with the same message forever.
    attempts    INTEGER NOT NULL DEFAULT 0,
    status      TEXT NOT NULL DEFAULT 'open'
                CHECK (status IN ('open','answered','quarantined'))
);
CREATE INDEX IF NOT EXISTS ix_messages_cause  ON messages(cause_id);
CREATE INDEX IF NOT EXISTS ix_messages_status ON messages(status);
CREATE INDEX IF NOT EXISTS ix_messages_to     ON messages(to_role);

CREATE TABLE IF NOT EXISTS sessions (
    id           TEXT PRIMARY KEY,
    role         TEXT NOT NULL,
    trigger_msg  TEXT REFERENCES messages(id),
    mode         TEXT NOT NULL DEFAULT 'normal' CHECK (mode IN ('normal','consult')),
    committed    INTEGER NOT NULL DEFAULT 0,
    seq          INTEGER NOT NULL,
    -- pins: a result without them is not a result
    model        TEXT,
    temperature  REAL,
    num_ctx      INTEGER,
    prompt_hash  TEXT
);

-- Law 6's cycle collapse depends on a role never having two live sessions.
-- The primary key on `role` makes that impossible rather than merely intended.
--
-- No foreign key on session_id: a claim is taken *before* the session runs, and
-- the sessions row is only written when it commits. That ordering is the point —
-- a claim with no session row is exactly what boot reaps as stale.
CREATE TABLE IF NOT EXISTS claims (
    role        TEXT PRIMARY KEY,
    session_id  TEXT NOT NULL,
    message_id  TEXT REFERENCES messages(id)
);

CREATE TABLE IF NOT EXISTS receipts (
    session_id   TEXT NOT NULL REFERENCES sessions(id),
    table_name   TEXT NOT NULL,
    row_id       TEXT NOT NULL,
    new_version  INTEGER NOT NULL,
    PRIMARY KEY (session_id, table_name, row_id)
);

CREATE TABLE IF NOT EXISTS checkpoints (
    session_id   TEXT PRIMARY KEY REFERENCES sessions(id),
    role         TEXT NOT NULL,
    working_set  TEXT NOT NULL,              -- [[table, version], ...]
    valid        INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS tool_calls (
    session_id     TEXT NOT NULL REFERENCES sessions(id),
    fn             TEXT NOT NULL,
    args_summary   TEXT NOT NULL DEFAULT '',
    seq            INTEGER NOT NULL,
    PRIMARY KEY (session_id, seq)
);

CREATE TABLE IF NOT EXISTS artefact_versions (
    table_name  TEXT PRIMARY KEY,
    version     INTEGER NOT NULL DEFAULT 0
);

-- Processes spawned by a batch's environment. §9 forbids half-dead
-- environments; on restart these are orphans and must be reaped.
CREATE TABLE IF NOT EXISTS runtime_processes (
    pid       INTEGER PRIMARY KEY,
    batch_id  TEXT NOT NULL REFERENCES batches(id),
    command   TEXT NOT NULL
);

-- Phase config: caps are read from here, never hard-coded.
CREATE TABLE IF NOT EXISTS config (
    key    TEXT PRIMARY KEY,
    value  TEXT NOT NULL
);
