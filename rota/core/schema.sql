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
--   * Index/body split on glossary_terms and constraints. An edge's `depth` says
--     which half it gets: `index` is the id plus one line, `body` is the prose
--     as well, and almost everything reads at index depth and fetches bodies
--     singly. This is what keeps an 8k working set viable at any artefact size.

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- ---------------------------------------------------------------------------
-- Transcript and brief (Liaison)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS entries (
    id          TEXT PRIMARY KEY,
    author      TEXT NOT NULL,              -- 'principal' | 'liaison'
    text        TEXT NOT NULL,
    ts_order    INTEGER NOT NULL,           -- sequence, not a timestamp
    version     INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS statements (
    id              TEXT PRIMARY KEY,
    span_entry  TEXT NOT NULL REFERENCES entries(id),
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
    kind          TEXT NOT NULL CHECK (kind IN ('in_scope','out_of_scope')),
    provenance    TEXT NOT NULL CHECK (provenance IN ('observed','decided','cited')),
    approval      TEXT NOT NULL DEFAULT 'draft'
                  CHECK (approval IN ('draft','pending','approved','contested')),
    approval_ver  INTEGER,                  -- version the approval was granted at
    -- Priority lives here, not on batches: it is a property of what the
    -- principal wants, and what they want is an item. It is also what makes
    -- batches single-writer, and gives law 9's "priority moves batches whole"
    -- for free -- there is no per-batch number to disagree with.
    -- Changing it is not an amendment: it touches no approved content, so
    -- `problem.prioritize` writes with amends=False and trips no revocation.
    priority      INTEGER NOT NULL DEFAULT 0,
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
    provenance   TEXT NOT NULL CHECK (provenance IN ('observed','decided','cited')),
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
    provenance           TEXT NOT NULL CHECK (provenance IN ('observed','decided','cited')),
    -- Where a `cited` constraint came from. Glossary terms already carried this;
    -- constraints are where external obligations actually land, so a constraint
    -- that cannot point at the clause it encodes is the one that most needed to.
    source_refs          TEXT NOT NULL DEFAULT '[]',
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
    outcome     TEXT NOT NULL CHECK (outcome IN ('found','none_found')),
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

-- ---------------------------------------------------------------------------
-- References (Researcher). What an outside source says, and where.
--
-- The Researcher owns this and nothing else, which is what makes over-indexing
-- structurally impossible: it writes rows here, and a claim only enters the
-- model if a role that owns an artefact chooses to cite one.
--
-- `quote` is not decoration. Everywhere else conclusions travel and reasoning
-- stays home -- but for an external source the passage IS the evidence, and
-- without it nobody can check whether the Researcher read it correctly.
--
-- No retrieval date, per law 13: nothing the system does with staleness needs
-- one. "The page changed" is a `content_hash` comparison; "it has been a year"
-- is a time judgement law 13 says the system does not get to make. The wall
-- clock lives in the fetch cache, which is evidence like the cassettes rather
-- than an artefact.
CREATE TABLE IF NOT EXISTS references_ (
    id            TEXT PRIMARY KEY,
    url           TEXT NOT NULL,
    claim         TEXT NOT NULL,            -- the index row: one line, always loaded
    quote         TEXT,                     -- the passage it rests on, fetched singly
    content_hash  TEXT NOT NULL DEFAULT '', -- drift: the page changed under a citation
    asked_by      TEXT NOT NULL,            -- the role whose question produced it
    version       INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX IF NOT EXISTS ix_references_url ON references_(url);

-- What Architect expects a batch to touch. A *prediction*, never a permission:
-- nothing rejects a diff for straying outside it. Its job is to make "was this
-- change incidental?" answerable at review time instead of arguable.
--
-- Paths are recorded always; symbols only where Architect is confident, and the
-- confidence is written down rather than implied. A symbol that no longer
-- resolves against the code index drops silently, the same way an unresolvable
-- constraint binding does — a stale prediction should decay, not accumulate
-- into noise that makes the whole set untrustworthy.
CREATE TABLE IF NOT EXISTS batch_touch (
    batch_id    TEXT NOT NULL REFERENCES batches(id),
    grain       TEXT NOT NULL,
    grain_kind  TEXT NOT NULL CHECK (grain_kind IN ('path','symbol','table','route')),
    confidence  TEXT NOT NULL DEFAULT 'expected'
                CHECK (confidence IN ('expected','possible')),
    PRIMARY KEY (batch_id, grain)
);

-- Architect's structural verdict on one batch, one row per constraint checked.
--
-- It is a row and not a message. The old design pushed findings to Critic,
-- which was the system's only declared contact exception -- underivable because
-- Critic must not read the model, so the conclusion had to be pushed to it
-- precisely because it could not fetch it. With the review order flipped
-- (harness, then Critic, then Architect) Architect's judgement is a *gate*
-- rather than an input, so it has nobody to tell: the merge predicate reads it,
-- and the scheduler is not a role. Critic's starvation survives intact and law
-- 3 now derives every message edge with no exceptions at all.
--
-- `grain` is the addressable thing the finding is about -- the same vocabulary
-- as constraint bindings, so a finding can be traced to what triggered it. It
-- carries no reasoning: law 2, conclusions travel, reasoning stays home.
CREATE TABLE IF NOT EXISTS findings (
    id            TEXT PRIMARY KEY,
    batch_id      TEXT NOT NULL REFERENCES batches(id),
    constraint_id TEXT NOT NULL REFERENCES constraints(id),
    commit_sha    TEXT,                      -- the diff this finding judged
    status        TEXT NOT NULL CHECK (status IN ('satisfied','violated')),
    grain         TEXT NOT NULL,
    version       INTEGER NOT NULL DEFAULT 1
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

CREATE TABLE IF NOT EXISTS batches (         -- Architect, sole writer
    id        TEXT PRIMARY KEY,
    item_id   TEXT NOT NULL REFERENCES items(id),
    worktree  TEXT,
    head_commit TEXT,                        -- last commit the DB has a receipt for
    status    TEXT NOT NULL DEFAULT 'pending'
              CHECK (status IN ('pending','running','deferred','merged')),
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

-- Every judgement records the commit it judged.
--
-- Without it each gate guards itself with "does a row exist for this batch",
-- which fires once per batch ever -- so a batch that failed review could never
-- pass: review would not re-fire because a verdict existed, the harness would
-- not re-run because test_runs existed, and the Developer bounced on
-- verdict_failed until the livelock guard tripped. The question is never "has
-- this been judged", it is "has anything happened since".
CREATE TABLE IF NOT EXISTS test_runs (       -- the mechanical gate before Critic
    id          TEXT PRIMARY KEY,
    batch_id    TEXT NOT NULL REFERENCES batches(id),
    test_id     TEXT NOT NULL REFERENCES tests(id),
    commit_sha  TEXT,                        -- the diff this run judged
    result      TEXT NOT NULL CHECK (result IN ('pass','fail','error')),
    -- What the harness said. The word alone left Developer reading the test
    -- body and guessing what red looked like -- the assertion that fired, the
    -- value it got. From a criterion and a body there is nothing to tell "the
    -- code is wrong" from "the test is wrong".
    output      TEXT NOT NULL DEFAULT '',
    attempt     INTEGER NOT NULL DEFAULT 1
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
    commit_sha        TEXT,                  -- the diff this verdict judged
    diff_ref          TEXT,
    result            TEXT NOT NULL CHECK (result IN ('pass','fail')),
    failed_criterion  TEXT REFERENCES criteria(id),
    version           INTEGER NOT NULL DEFAULT 1
);

-- ---------------------------------------------------------------------------
-- Runtime: messages, sessions, receipts, checkpoints, claims.
-- ---------------------------------------------------------------------------

-- Roots are principal entries, gate events and ticks, so cause_id is nullable
-- and cause_kind records which kind of root a message hangs from.
CREATE TABLE IF NOT EXISTS messages (
    id          TEXT PRIMARY KEY,
    cause_id    TEXT REFERENCES messages(id),
    cause_kind  TEXT NOT NULL DEFAULT 'message'
                CHECK (cause_kind IN ('message','conversation','gate','tick','receipt')),
    thread_id   TEXT NOT NULL,
    from_role   TEXT NOT NULL,
    to_role     TEXT NOT NULL,
    verb        TEXT NOT NULL,
    body_refs   TEXT NOT NULL DEFAULT '[]',
    -- Empty on every channel but one. Law 2 keeps prose off messages because a
    -- role that wants to explain itself writes a decision and refs it -- which
    -- works because sender and recipient share a database, so an id means
    -- something at both ends.
    --
    -- The Researcher shares nothing. It has never seen an artefact, a batch or
    -- a line of this codebase, and that ignorance is the containment: it cannot
    -- leak what it does not have. So refs are meaningless to it, and a question
    -- with no words is no question. The exception is declared on the graph edge
    -- (`prose: question`) rather than special-cased on a role name, so it is
    -- one fact in one place and any second one has to be declared too.
    body_text   TEXT,
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
    mode         TEXT NOT NULL DEFAULT 'normal' CHECK (mode IN ('normal','readonly')),
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

-- Law 4 bounds failure, and it used to bound it only for messages: a crashed
-- session raises its trigger's attempt count and past `message_attempt_cap` the
-- message is quarantined. A *tick* had no equivalent, and the first foreign
-- repository found the hole in six sessions.
--
-- A survey session read the area, wrote three glossary terms, and never called
-- `surveys.attest`. `tick_survey` drains on `survey_records`, so nothing
-- drained, so the identical wake was produced again — same role, same area,
-- forever. It never looked broken: the system was busy, committing, and writing
-- artefacts. It would simply never have reached area two of twelve.
--
-- Worse than a dead end, which at least reports quiescence. This is a livelock,
-- and the only reason it was caught is that somebody was watching the counters
-- rather than the exit code.
CREATE TABLE IF NOT EXISTS tick_attempts (
    tick_key    TEXT PRIMARY KEY,      -- role + kind + refs
    attempts    INTEGER NOT NULL DEFAULT 0,
    quarantined INTEGER NOT NULL DEFAULT 0,
    -- Whether the principal has been told. Without it the quarantine report is
    -- itself a dead end: `tick_quarantined` counts abandoned things, nothing
    -- clears the count, so it fires every pass forever -- and on the first
    -- foreign repository it was bounded by the very mechanism it exists to
    -- report, three sessions in. A report that cannot be discharged is not a
    -- report, it is an alarm nobody can switch off.
    reported    INTEGER NOT NULL DEFAULT 0
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
    -- Which batch was suspended. Invalidation on preemption is per *batch* --
    -- the batch is what got displaced -- and without this the question could
    -- only be answered by joining back through the session that made it.
    batch_id     TEXT REFERENCES batches(id),
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
