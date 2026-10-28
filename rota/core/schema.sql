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
-- Problem statement (Vision Keeper)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS items (
    id            TEXT PRIMARY KEY,
    text          TEXT NOT NULL,
    kind          TEXT NOT NULL CHECK (kind IN ('in_scope','out_of_scope')),
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
    version       INTEGER NOT NULL DEFAULT 1,
    -- A description says what the software is and asks for nothing. So it is
    -- never cut into tickets and never owes criteria (ruled: Roman,
    -- 2026-09-24, frame 80). The Vision Keeper sets it by `problem.describe`.
    is_description INTEGER NOT NULL DEFAULT 0
);

-- What a row rests on. One row per (source, target). The pair is the row.
--
-- `src_table` names the table of the source row. `kind` names the table of
-- the target. The targets are of different kinds and SQLite has no
-- polymorphic foreign key, so `kind` does the work of one:
--   statement  -> statements.id
--   reference  -> references_.id
--   term       -> glossary_terms.id
--   grain      -> code_index.grain (`resolves` is 0 once the grain leaves
--                 the index; the index is rebuilt, so a grain is not a key)
--   ruling     -> rulings.id
--
-- One table with several writers. A refs row belongs to the artefact of its
-- source row: `db.session_commit` receipts it under (`src_table`, `src_id`),
-- so the cascade and the ruling relay see the source artefact. The views
-- below derive a row's provenance from what it reaches. The provenance
-- columns on the owner tables stay until the readers move (frame 21).
--
-- The CHECK values of `src_table` and `kind` are table names and the nouns
-- of the target kinds above, not lifecycle states. The vocabulary harvester
-- and `predicates.schema_states` skip this table. `api.stage_ref` refuses a
-- bad value before the commit.
CREATE TABLE IF NOT EXISTS refs (
    src_table  TEXT NOT NULL CHECK (src_table IN
                   ('items','glossary_terms','constraints','model_areas',
                    'frame_rulings','criteria','business_rules')),
    src_id     TEXT NOT NULL,
    kind       TEXT NOT NULL CHECK (kind IN
                   ('statement','reference','term','grain','ruling')),
    target     TEXT NOT NULL,
    resolves   INTEGER NOT NULL DEFAULT 1,   -- grains only: 0 once the grain leaves the index
    PRIMARY KEY (src_table, src_id, kind, target)
);
CREATE INDEX IF NOT EXISTS ix_refs_target ON refs(kind, target);

-- Provenance derived from what a row reaches. A row with no refs is absent
-- here. The per-table views below give such a row 'reasoned'.
--
-- Precedence: decided over observed over reasoned. `basis` says which source
-- won: a landed ruling, a ratified statement, the world (a reference row), or
-- the code (a grain that resolves). A reader that needs "cited and decided"
-- together reads `refs`, not this view.
--
-- The walk follows `term` refs: a criterion rests on a term, and the term
-- rests on a statement. The cap at 8 guards a cycle written by hand.
-- A landed ruling counts as `ruled` when it came from his keypress, with no
-- reply, or when he approved the read-back line of its reply. An unchecked
-- inference is never a record (`composition.md`, Records; the seam design,
-- 2.4). `ruled_refs_live.confirmed_by` reads the same approve.
-- The view holds no data, so `init_db` drops it and makes it again: a run
-- database then reads the count of this schema.
DROP VIEW IF EXISTS provenance;
CREATE VIEW IF NOT EXISTS provenance AS
WITH RECURSIVE reach(src_table, src_id, kind, target, resolves, depth) AS (
    SELECT src_table, src_id, kind, target, resolves, 1 FROM refs
    UNION
    SELECT r.src_table, r.src_id, t.kind, t.target, t.resolves, r.depth + 1
    FROM reach r JOIN refs t
      ON r.kind = 'term'
     AND t.src_table = 'glossary_terms' AND t.src_id = r.target
    WHERE r.depth < 8
),
basis AS (
    SELECT src_table, src_id,
        MAX(kind = 'ruling' AND EXISTS (
            SELECT 1 FROM rulings u WHERE u.id = reach.target AND u.status = 'landed'
              AND (u.reply_id IS NULL OR EXISTS (
                  SELECT 1 FROM ruled_refs c JOIN rulings cr ON cr.id = c.ruling_id
                  WHERE c.ref = 'reading:' || u.reply_id AND c.verdict = 'approve'
                    AND cr.status = 'landed'))))
          AS ruled,
        MAX(kind = 'statement' AND EXISTS (
            SELECT 1 FROM statements s WHERE s.id = reach.target AND s.status = 'ratified'))
          AS ratified,
        MAX(kind = 'reference' AND EXISTS (
            SELECT 1 FROM references_ x WHERE x.id = reach.target))
          AS world,
        MAX(kind = 'grain' AND resolves = 1) AS code
    FROM reach GROUP BY src_table, src_id
)
SELECT src_table, src_id,
    CASE WHEN ruled OR ratified THEN 'decided'
         WHEN world OR code    THEN 'observed'
         ELSE 'reasoned' END AS provenance,
    CASE WHEN ruled THEN 'ruling' WHEN ratified THEN 'statement'
         WHEN world THEN 'world'  WHEN code THEN 'code'
         ELSE 'none' END AS basis
FROM basis;

-- One per owner table, so a reader can join on the id alone.
CREATE VIEW IF NOT EXISTS item_provenance AS
SELECT i.id, COALESCE(p.provenance, 'reasoned') AS provenance,
       COALESCE(p.basis, 'none') AS basis
FROM items i LEFT JOIN provenance p
  ON p.src_table = 'items' AND p.src_id = i.id;

CREATE VIEW IF NOT EXISTS term_provenance AS
SELECT g.id, COALESCE(p.provenance, 'reasoned') AS provenance,
       COALESCE(p.basis, 'none') AS basis
FROM glossary_terms g LEFT JOIN provenance p
  ON p.src_table = 'glossary_terms' AND p.src_id = g.id;

CREATE VIEW IF NOT EXISTS constraint_provenance AS
SELECT c.id, COALESCE(p.provenance, 'reasoned') AS provenance,
       COALESCE(p.basis, 'none') AS basis
FROM constraints c LEFT JOIN provenance p
  ON p.src_table = 'constraints' AND p.src_id = c.id;

CREATE VIEW IF NOT EXISTS area_provenance AS
SELECT a.id, COALESCE(p.provenance, 'reasoned') AS provenance,
       COALESCE(p.basis, 'none') AS basis
FROM model_areas a LEFT JOIN provenance p
  ON p.src_table = 'model_areas' AND p.src_id = a.id;

CREATE VIEW IF NOT EXISTS frame_provenance AS
SELECT f.id, COALESCE(p.provenance, 'reasoned') AS provenance,
       COALESCE(p.basis, 'none') AS basis
FROM frame_rulings f LEFT JOIN provenance p
  ON p.src_table = 'frame_rulings' AND p.src_id = f.id;

-- ---------------------------------------------------------------------------
-- Glossary and rules (Terminologist). Index/body split.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS glossary_terms (
    id           TEXT PRIMARY KEY,
    term         TEXT NOT NULL,
    sense_short  TEXT NOT NULL,             -- the index row: one line, always loaded
    sense_body   TEXT,                      -- fetched singly, never in bulk
    -- Which area the session that wrote this sense was surveying. Evidence,
    -- never authority: two senses written while reading the same area are one
    -- thing described twice, and two written from different areas are the word
    -- doing different work in two places. That is what a disambiguation
    -- session needs in order to tell a duplicate from a collision, and it is
    -- all this column is for.
    --
    -- Not ownership. Ownership is not in the data: `TemplateVariable` is
    -- declared in `src/variables` and the word is used 152 times in
    -- `src/variables/providers`, so counting hands it to the wrong area; and
    -- `folder`, `text` and `note` as prompt types are declared in
    -- `intentsSchema.yaml`, which has no symbols at all. Deciding which sense
    -- survives is a judgement, and computing it from a frequency was reaching
    -- for the available number instead of the right one.
    area         TEXT,
    -- The row this one replaced, when a disambiguation session ruled them the
    -- same word said twice. Superseded rather than deleted: sameness is a
    -- judgement we are delegating and cannot verify, so the losing sense stays
    -- readable and the merge stays reversible.
    superseded_by TEXT REFERENCES glossary_terms(id),
    version      INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX IF NOT EXISTS ix_glossary_term ON glossary_terms(term);

CREATE TABLE IF NOT EXISTS business_rules (
    id         TEXT PRIMARY KEY,
    text       TEXT NOT NULL,
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
    rationale_decision   TEXT REFERENCES decisions(id),
    is_global            INTEGER NOT NULL DEFAULT 0,
    version              INTEGER NOT NULL DEFAULT 1
);

-- Bindings are rows, not a JSON blob: the structural trigger is a join.
-- A constraint with zero bindings is global — missing bindings must always mean
-- "always visible", never "invisible".
CREATE TABLE IF NOT EXISTS model_areas (     -- Architect: what each area is for
    id          TEXT PRIMARY KEY,             -- the area path
    account     TEXT NOT NULL,
    version     INTEGER NOT NULL DEFAULT 1
);

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
    -- The area's aggregate content as this survey saw it, stamped at attest
    -- time from the index rows the session read. The latest record whose
    -- area_hash no longer matches the area's current aggregate is a survey
    -- of a tree that is gone, and the area counts as unread again.
    area_hash   TEXT NOT NULL DEFAULT '',
    -- Which tree this was a survey *of*. DECISIONS.md names this as the one
    -- blocker on re-surveying: `tick_survey` fires on areas with no record and
    -- nothing fires on an area whose code changed since its record, and the
    -- predicate cannot be written before the column exists.
    --
    -- Read from `config.project_commit` rather than from git at attest time,
    -- because a survey reads grains from `code_index` and `code_index` was
    -- built at that commit. Asking git would record where the tree happens to
    -- be standing, which is not what was surveyed.
    --
    -- Empty when the project is not a checkout, so a predicate can tell
    -- "surveyed at an unknown commit" from "surveyed at this one".
    commit_sha  TEXT NOT NULL DEFAULT '',
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

-- The Architect's guess of the code one request item touches, before any
-- batch exists. P4 piece 2 in its judged form (ruled: Roman, 2026-10-18,
-- "the architect owns the guess"). A prediction, never a permission (law 12).
-- A correction writes a new set beside the old one, so the Architect's own
-- guess stays countable.
CREATE TABLE IF NOT EXISTS touch_guesses (
    item_id     TEXT NOT NULL REFERENCES items(id),
    item_ver    INTEGER NOT NULL,           -- the item's version at the write
    ruling_id   TEXT NOT NULL DEFAULT '',   -- the ruling a rewrite rests on; '' for the Architect's own
    grain       TEXT NOT NULL,
    grain_kind  TEXT NOT NULL CHECK (grain_kind IN ('path','symbol')),
    confidence  TEXT NOT NULL DEFAULT 'expected'
                CHECK (confidence IN ('expected','possible')),
    PRIMARY KEY (item_id, item_ver, ruling_id, grain)
);

-- The paths a commit touched that the batch's predicted touch set never
-- named: detected divergence, one row per path per commit, written by
-- `code.commit` in the committing session's own transaction. The Architect
-- judges each: foreseen (the prediction grows) or a mistake (the Developer
-- is woken to take it out). The merge waits on the judgement. Law 12 holds:
-- the prediction never blocks a commit; only the unjudged stray holds the
-- merge, and only until somebody says which it is.
CREATE TABLE IF NOT EXISTS touch_strays (
    batch_id    TEXT NOT NULL REFERENCES batches(id),
    commit_sha  TEXT NOT NULL,
    path        TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'open'
                CHECK (status IN ('open','foreseen','mistake')),
    note        TEXT,
    PRIMARY KEY (batch_id, commit_sha, path)
);

-- The `dropped` notes of a batch's worktree that no write or ledger note has
-- closed yet: one row per batch and path, written by `code.write`. Frame 283:
-- night 154's s340 and s388 committed the dropped lines away in a later
-- reply. A retry session on the same worktree reads the row, so the note
-- outlives its session. `lines` is JSON: [definition, line, count before].
-- `defs` is JSON: the definitions a whole-file write dropped.
CREATE TABLE IF NOT EXISTS drop_notes (
    batch_id    TEXT NOT NULL REFERENCES batches(id),
    path        TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'open'
                CHECK (status IN ('open','restored')),
    note        TEXT NOT NULL,
    lines       TEXT NOT NULL DEFAULT '[]',
    defs        TEXT NOT NULL DEFAULT '[]',
    whole       TEXT NOT NULL DEFAULT '[]',
    noted      TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (batch_id, path)
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
    fan_in      INTEGER NOT NULL DEFAULT 0,
    sym_kind    TEXT NOT NULL DEFAULT '',    -- for symbols: function|class|interface|type|enum|struct|trait|module
    -- What the file held when the index was built; path grains only, '' for
    -- the rest. The freshness predicate compares aggregates of this column,
    -- which is what keeps it a pure query -- the filesystem was consulted
    -- once, by the indexer, and the database remembers.
    content_hash TEXT NOT NULL DEFAULT '',
    -- Where the definition is, in the file the grain names; symbol grains
    -- only, 0 and 0 for the rest. The parser has the span and threw it away,
    -- so a seat that probed a name could only read the file at 400 lines a
    -- time. The two numbers are what `code.source(path, start, end)` takes:
    -- 0-based, and the end is one line past the definition.
    line_start  INTEGER NOT NULL DEFAULT 0,
    line_end    INTEGER NOT NULL DEFAULT 0
);

-- Each area's aggregate content, as main last stood. Stamped by onboarding and
-- by every refresh of the main checkout, and read by the freshness rule to ask
-- whether an area moved since a survey attested it. It is a table rather than a
-- live aggregate of `code_index` because the index describes the running
-- batch's worktree between a commit and the merge, and a batch's own files must
-- not reopen a survey. Mechanical like the index: rebuilt, never decided, and
-- no role writes it.
CREATE TABLE IF NOT EXISTS area_hashes (
    area TEXT PRIMARY KEY,
    hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS code_edges (      -- dependency graph, input to partitioning
    src   TEXT NOT NULL,
    dst   TEXT NOT NULL,
    PRIMARY KEY (src, dst)
);

-- The words the checkout declares, ranked by how loudly it declares them.
-- Mechanical like the index and rebuilt with it: a directory name, a file
-- name, a declared type, an authoring-surface key. The define phase of
-- onboarding wakes Terminologist once per row here, in score order, so the
-- list of words no session ever chooses is the project's own list.
CREATE TABLE IF NOT EXISTS code_lexicon (
    word      TEXT PRIMARY KEY,              -- 'intent', 'template variable type'
    sources   TEXT NOT NULL DEFAULT '[]',    -- JSON: which kinds of evidence name it
    grain     TEXT NOT NULL DEFAULT '',      -- where, when one place says so
    score     REAL NOT NULL DEFAULT 0,
    uses      INTEGER NOT NULL DEFAULT 0,
    compound  INTEGER NOT NULL DEFAULT 0     -- more than one word, kept whole
);

-- ---------------------------------------------------------------------------
-- Backlog: three tables, one writer each. Law 1 means one writer per *row*;
-- per-table ownership is the strict form of that, and it is what closes the
-- old "backlog has three writers" risk.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS tickets (         -- Vision Keeper
    id       TEXT PRIMARY KEY,
    item_id  TEXT NOT NULL REFERENCES items(id),
    text     TEXT NOT NULL,
    version  INTEGER NOT NULL DEFAULT 1,
    -- The item's version when the ticket was sliced. A ticket below the
    -- newest `item_ver` of its item is retired. NULL is unknown, and an
    -- unknown ticket is never retired and never sliced again.
    item_ver INTEGER
);

CREATE TABLE IF NOT EXISTS criteria (        -- Terminologist
    id         TEXT PRIMARY KEY,
    ticket_id  TEXT NOT NULL REFERENCES tickets(id),
    text       TEXT NOT NULL,
    -- The callables a test of this criterion would exercise: symbol grains
    -- from the code index. The Tester is black-box by charter, so the
    -- criterion is its only material, and a criterion naming no surface left
    -- it structurally stuck -- every stable red in the delivery cluster sat
    -- downstream of that. A name to call is intent's vocabulary, not
    -- implementation, which is why this does not breach the charter.
    surface_refs TEXT NOT NULL DEFAULT '[]',
    version    INTEGER NOT NULL DEFAULT 1,
    -- The ruling that dropped the criterion's line. A retired criterion is
    -- read by no tick and shows on no page as live. It stays with its
    -- ruling, so the record keeps it (frame 306, pass 1b).
    retired_by TEXT
);

CREATE TABLE IF NOT EXISTS batches (         -- Architect, sole writer
    id        TEXT PRIMARY KEY,
    item_id   TEXT NOT NULL REFERENCES items(id),
    worktree  TEXT,
    head_commit TEXT,                        -- last commit the DB has a receipt for
    status    TEXT NOT NULL DEFAULT 'pending'
              CHECK (status IN ('pending','running','deferred','merged','abandoned')),
    -- The first port of this batch's reserved range, assigned by the scheduler
    -- at dispatch. Two batches must never reach each other's ports and a batch
    -- cannot guarantee that, because it cannot see the other one -- the same
    -- reasoning that puts the worktree outside the role's hands.
    --
    -- It survives a deferral even though the processes do not. A port range is
    -- a number in a row and holds nothing; re-spawning onto the same ports is
    -- what makes resuming a deferred batch continuing rather than starting over.
    port_base INTEGER,
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
    -- NULL for a test the repository already had. The batch inherits the
    -- repository's own tests at start, so the harness runs them with the
    -- batch's and a merge cannot break what the tree already proved.
    -- tipsY (2026-09-09): tests green, Critic pass, and the merged program
    -- read the tip percentage and ignored it; the repo's own tip test was
    -- in the tree and never ran.
    criterion_id  TEXT REFERENCES criteria(id),
    path          TEXT NOT NULL,
    body          TEXT NOT NULL,
    version       INTEGER NOT NULL DEFAULT 1,
    -- The ruling that dropped the test's check line. A retired test is read
    -- by no tick and shows on no page. It stays with its ruling, so the
    -- record keeps it (frame 306, W-A).
    retired_by    TEXT
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

-- Every run that `record_test_run` records, kept. `test_runs` holds the live
-- run per test, because the review gate and the hold guard read it so. Two
-- deletes keep it live, and night 159's table lost 663 results to them
-- (frame 307). No code deletes from this table, and no gate or guard reads
-- it. `seq` is the key, because `new_id` counts from `test_runs` and can
-- give a deleted run's id again. The table has no foreign keys, so a
-- journal row never blocks a delete elsewhere. `seq` also orders the runs.
-- The table has no clock column, by `test_schema_has_no_clock.py`.
CREATE TABLE IF NOT EXISTS test_run_journal (
    seq         INTEGER PRIMARY KEY AUTOINCREMENT,
    id          TEXT NOT NULL,               -- the id of the live row
    batch_id    TEXT NOT NULL,
    test_id     TEXT NOT NULL,
    commit_sha  TEXT,
    result      TEXT NOT NULL CHECK (result IN ('pass','fail','error')),
    output      TEXT NOT NULL DEFAULT '',
    attempt     INTEGER NOT NULL DEFAULT 1
);

-- ---------------------------------------------------------------------------
-- Journals: multi-writer, one author per entry, append-only.
-- ---------------------------------------------------------------------------

-- `kind` is the class of the row, stamped by the door that wrote it. A
-- predicate reads the column, never the prose: the diff review of 6895000
-- found `term_collision` matching the parking sentence as a substring of
-- model-written text, so a paraphrase re-opened the loop and wrote a new
-- row every cycle. An `assumption` is the ordinary row. An
-- `unaddressed_answer` row says the principal's answer did not address the
-- row the question was about. The ordinary class is `default`, after
-- `default_taken`: the word `assumption` is the artefact's noun already, and
-- one word carries one job (`tests/rota/test_vocabulary.py`).
--
-- Frame 204 adds the words of its grid (`plans/frame204-design.md`,
-- section 8). A seat names one at log time. `blocked` and `fault` never
-- land here: the door writes them to `faults`, and the CHECK refuses them,
-- so a raw writer cannot put a fault on a page (frame 204's review 1,
-- finding L5). The grid's `unaddressed`
-- cell is `unaddressed_answer`, which `ledger.unaddressed` writes (section
-- 7). A second word for it would collide with the operation's name
-- (`tests/rota/test_vocabulary.py`).
CREATE TABLE IF NOT EXISTS ledger (
    id             TEXT PRIMARY KEY,
    about_ref      TEXT NOT NULL,
    about_table    TEXT NOT NULL,
    default_taken  TEXT NOT NULL,
    kind           TEXT NOT NULL DEFAULT 'default'
                   CHECK (kind IN ('default','unaddressed_answer','invented',
                                   'scope','gap','finding','conflict',
                                   'other')),
    -- 'parked': the row's item merged with the row open. No page shows it,
    -- and the shipped line counts it (frame 204's design, section 4).
    status         TEXT NOT NULL DEFAULT 'open'
                   CHECK (status IN ('open','resolved','parked')),
    author         TEXT NOT NULL,
    version        INTEGER NOT NULL DEFAULT 1
);

-- A fault report to the people who build rota (frame 204, section 7). A
-- seat that meets a door that failed, or a record that names a row that
-- does not exist, says so through `ledger.log(kind='fault')` or
-- `kind='blocked'`. No page shows the row, and no seat answers it. The
-- composition's Records line rules that it stays countable: the cockpit,
-- the night report and the state view read the open rows. The door writes
-- the row, and `rota.tools.faults close` writes `status` and `closed_by`,
-- one writer per column as on `ledger`. `closed_by` holds the number of the
-- build frame that fixed the cause. A discharged fault is `resolved`, the
-- ledger's word for a discharged row, because `closed` is a graph noun
-- already (`tests/rota/test_vocabulary.py`).
CREATE TABLE IF NOT EXISTS faults (
    id          TEXT PRIMARY KEY,
    session_id  TEXT NOT NULL DEFAULT '',
    call        TEXT NOT NULL,
    text        TEXT NOT NULL,
    kind        TEXT NOT NULL DEFAULT 'fault' CHECK (kind IN ('fault','blocked')),
    author      TEXT NOT NULL,
    seq         INTEGER NOT NULL,
    status      TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open','resolved')),
    closed_by   TEXT
);

-- The principal's reply to a page, read as a ruling by the Liaison.
--
-- The seat is text. A person answers a confirm or a present in their own
-- words. No parser reads the words: the Liaison does, with the page in front
-- of it, and records what it read here, one row per reply. The row is the
-- record of the reading, and `principal.land` is the one door the ruling
-- goes through, after the session commits. `per_item` maps each rulable row
-- to approve, contest or revise. `words` are the principal's, carried whole.
CREATE TABLE IF NOT EXISTS rulings (
    id          TEXT PRIMARY KEY,
    ask_id      TEXT NOT NULL REFERENCES messages(id),
    reply_id    TEXT REFERENCES messages(id),
    per_item    TEXT NOT NULL DEFAULT '{}',
    words       TEXT NOT NULL DEFAULT '',
    status      TEXT NOT NULL DEFAULT 'open'
                CHECK (status IN ('open','landed','stale')),
    verdict_id  TEXT REFERENCES messages(id),
    version     INTEGER NOT NULL DEFAULT 1,
    -- The text of each criterion the ruling contests or revises, as it stood
    -- when the principal ruled: a JSON map of criterion id to text. No other
    -- record keeps a criterion's old text. Night 144's s546 put back the
    -- contested flag, and no door could see it (frame 226).
    texts       TEXT NOT NULL DEFAULT '{}'
);

-- One row per ruling and ref: what the principal's reply ruled on one row.
--
-- `principal.ruling_rows` is the one builder. The Liaison's `rulings.rule`
-- stages its rows, and `land` and `_land_shift` insert the rows of a verdict
-- that came straight from the seat. So every path that writes a `rulings`
-- row writes its rows here (the seam design, 1.3, and its review, finding 6).
-- A row never changes after its insert, and the trigger below refuses an
-- update: a later write cannot overwrite a reading (`composition.md`,
-- Records). The id hashes `ruling_id` and `ref`. `act` null grants nothing,
-- because silence is not consent. `init_db` back-fills the rows of an older
-- `rulings` row from its `per_item`, with `source` 'backfill'.
CREATE TABLE IF NOT EXISTS ruled_refs (
    id          TEXT PRIMARY KEY,
    ruling_id   TEXT NOT NULL REFERENCES rulings(id),
    ref         TEXT NOT NULL,
    line        INTEGER,
    -- The stored words of `RULING_WORDS` and `SHIFT_WORDS` (the review,
    -- finding 6). `ruling_rows` holds the list, not a CHECK: a CHECK word
    -- is a state, and `contest` and `revise` are graph nouns, so the
    -- vocabulary lint refuses the CHECK.
    verdict     TEXT NOT NULL,
    act         TEXT CHECK (act IS NULL OR act IN
                            ('drop','keep','rewrite','add','remove')),
    target_kind TEXT CHECK (target_kind IS NULL OR target_kind IN
                            ('row','check','sentence','identifier',
                             'source_line','path','request')),
    target      TEXT,
    words       TEXT NOT NULL DEFAULT '',
    words_from  TEXT REFERENCES messages(id),
    old_text    TEXT,
    ref_version INTEGER,
    -- The source of the row: the Liaison's reading, the seat's keypress,
    -- the back-fill of an older row (the review, finding 7), or the verdict
    -- that `land` computed and the relays read (fact F1).
    source      TEXT NOT NULL DEFAULT 'reading'
                CHECK (source IN ('reading','keypress','backfill','landed')),
    -- A `landed` row names the keypress or reading row it derives from, so
    -- its provenance is that row's provenance (law 11). Else null.
    derived_from TEXT REFERENCES ruled_refs(id)
);
CREATE INDEX IF NOT EXISTS ruled_refs_by_ref ON ruled_refs (ref, ruling_id);
CREATE TRIGGER IF NOT EXISTS ruled_refs_never_change
BEFORE UPDATE ON ruled_refs
BEGIN
    SELECT RAISE(ABORT, 'a ruled_refs row never changes after its insert');
END;

-- The rows of `ruled_refs` with what is derived and not stored.
--
-- `status` is `open` while the ruling is open and `stale` when its ask
-- closed before it landed, as `rulings.status` says. A landed row is
-- `superseded` when a newer landed ruling rules the same ref. It is
-- `outdated` when the ref now has a higher version than `ref_version`.
-- Else it is `landed`. The order is `rulings.rowid`, because the hash id
-- gives none (the review, finding 8). `confirmed_by` names the reply of a
-- landed approve of `reading:<this row's reply id>`. `provenance` is
-- `decided` for a keypress row, a confirmed row, or a landed row that
-- derives from a keypress row, else `reasoned`.
CREATE VIEW IF NOT EXISTS ruled_refs_live AS
SELECT b.*,
       CASE WHEN b.source = 'keypress' OR b.confirmed_by IS NOT NULL
                 OR EXISTS (SELECT 1 FROM ruled_refs d
                            WHERE d.id = b.derived_from
                              AND d.source = 'keypress')
            THEN 'decided' ELSE 'reasoned' END AS provenance
FROM (
    SELECT rr.*, rr.rowid AS row_seq, r.ask_id AS ask_id, r.reply_id AS reply_id,
           r.verdict_id AS verdict_id, r.status AS ruling_status,
           r.rowid AS ruling_seq, r.words AS reply_words,
           CASE
               WHEN r.status = 'stale' THEN 'stale'
               WHEN r.status = 'open' THEN 'open'
               WHEN EXISTS (
                   SELECT 1 FROM ruled_refs n JOIN rulings nr ON nr.id = n.ruling_id
                   WHERE n.ref = rr.ref AND nr.status = 'landed'
                     AND nr.rowid > r.rowid) THEN 'superseded'
               WHEN rr.ref_version IS NOT NULL AND COALESCE(
                   (SELECT version FROM items WHERE id = rr.ref),
                   (SELECT version FROM criteria WHERE id = rr.ref),
                   (SELECT version FROM statements WHERE id = rr.ref),
                   (SELECT version FROM tickets WHERE id = rr.ref),
                   (SELECT version FROM tests WHERE id = rr.ref),
                   (SELECT version FROM batches WHERE id = rr.ref),
                   (SELECT version FROM ledger WHERE id = rr.ref),
                   (SELECT version FROM constraints WHERE id = rr.ref),
                   (SELECT version FROM glossary_terms WHERE id = rr.ref),
                   (SELECT version FROM model_areas WHERE id = rr.ref),
                   (SELECT version FROM frame_rulings WHERE id = rr.ref),
                   rr.ref_version) > rr.ref_version THEN 'outdated'
               ELSE 'landed'
           END AS status,
           (SELECT COALESCE(cr.reply_id, cr.verdict_id)
            FROM ruled_refs c JOIN rulings cr ON cr.id = c.ruling_id
            WHERE c.ref = 'reading:' || r.reply_id AND c.verdict = 'approve'
              AND cr.status = 'landed'
            ORDER BY cr.rowid DESC LIMIT 1) AS confirmed_by
    FROM ruled_refs rr JOIN rulings r ON r.id = rr.ruling_id
) b;

-- The principal's answer to the shift question, one row per answer, and the
-- automatic resume when the request the park waited behind is delivered or
-- dropped. An item is set aside while its newest row is `park` or `drop`.
-- `land` writes the `shift` rows and `scheduler.resume_behind` writes the
-- `request` rows, so each row has one writer (frame 193's design, 2.F.3 and
-- 2.F.4). The id hashes the item and the cause (law 14).
CREATE TABLE IF NOT EXISTS item_parks (
    id          TEXT PRIMARY KEY,
    item_id     TEXT NOT NULL REFERENCES items(id),
    kind        TEXT NOT NULL CHECK (kind IN ('park','now','drop','resume')),
    -- `shift` is a row from the principal's answer, `request` a resume by
    -- `resume_behind`. The word `principal` is a graph node and stays one.
    by          TEXT NOT NULL CHECK (by IN ('shift','request')),
    cause_id    TEXT NOT NULL,
    seq         INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_item_parks_item ON item_parks(item_id, seq);

CREATE TABLE IF NOT EXISTS decisions (
    id               TEXT PRIMARY KEY,
    author           TEXT NOT NULL,
    text             TEXT NOT NULL,
    resolves_ledger  TEXT REFERENCES ledger(id),
    supersedes       TEXT REFERENCES decisions(id),
    refs             TEXT NOT NULL DEFAULT '[]',
    version          INTEGER NOT NULL DEFAULT 1
);

-- `reason` carries the Critic's objection to the Developer (night 101; ruled by Roman, frame 88, 2026-09-30).
CREATE TABLE IF NOT EXISTS verdicts (
    id                TEXT PRIMARY KEY,
    batch_id          TEXT NOT NULL REFERENCES batches(id),
    commit_sha        TEXT,                  -- the diff this verdict judged
    diff_ref          TEXT,
    result            TEXT NOT NULL CHECK (result IN ('pass','fail')),
    failed_criterion  TEXT REFERENCES criteria(id),
    reason            TEXT,
    lines             TEXT,                  -- a pass's JSON: criterion id to added line (frame 170)
    version           INTEGER NOT NULL DEFAULT 1
);

-- The Critic's ruling on a finding filed after its pass. Ruled by Roman on
-- 2026-09-27: only the Critic can reopen a green, signed-off batch. A
-- `verdicts` row cannot hold the ruling, because its id is one per commit and
-- a second row would overwrite the pass. Keyed by finding and commit, because
-- `findings.find` overwrites a finding's row by id across commits.
-- `finding_id` carries no foreign key: `findings` is the Architect's artefact,
-- and a key across the boundary would need a cascade edge nobody needs.
CREATE TABLE IF NOT EXISTS finding_rulings (
    id          TEXT PRIMARY KEY,
    finding_id  TEXT NOT NULL,
    commit_sha  TEXT NOT NULL,
    ruling      TEXT NOT NULL CHECK (ruling IN ('upheld','dismissed')),
    reason      TEXT NOT NULL,
    session_id  TEXT,
    at          TEXT NOT NULL DEFAULT (datetime('now')),
    version     INTEGER NOT NULL DEFAULT 1
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
    -- What the asker still cannot proceed without, once an answer has landed
    -- and not helped. The only thing on the register that no query can produce:
    -- the row says `answered` and the answer is in `body_text` on the reply, and
    -- neither of them knows it left the asker where it was.
    --
    -- It is on the question rather than in a table of its own because it is a
    -- property of that question -- what it was really asking, said again by the
    -- one role that found out the hard way. Nothing else can carry it: the
    -- question's own `body_text` is the asker's first attempt at the words, and
    -- overwriting it would destroy the evidence that the two differ.
    unresolved_note TEXT,
    status      TEXT NOT NULL DEFAULT 'open'
                -- 'unresolved': answered, and the asker says it did not land.
                -- Not open (nobody owes a reply to a question already answered)
                -- and not answered (the obligation is not discharged), so it is
                -- its own state rather than a flag on either.
                -- A Tester's triage can create a question unresolved, with the
                -- note, and nobody owes that question a reply.
                CHECK (status IN ('open','answered','unresolved','quarantined'))
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
    prompt_hash  TEXT,
    -- the whole pin set, so a new pin is additive and never a column; and
    -- the adapter that ran it, never an endpoint or a key
    pins_json    TEXT NOT NULL DEFAULT '{}',
    backend      TEXT,
    -- What woke it. `trigger_msg` answers this only for a message, and in an
    -- onboarding run nothing is a message: 24 of 24 sessions on the last real
    -- one were ticks, so the record of why any of them ran was a null column.
    --
    -- Asking "why is this term here" then stopped at "a terminologist wrote
    -- it", one step short of the answer, in exactly the case the question is
    -- asked about. The wake is already in hand where the session is built; it
    -- was simply not carried.
    wake_kind    TEXT NOT NULL DEFAULT '',
    wake_detail  TEXT NOT NULL DEFAULT '',
    -- And its refs, because that is where the *subject* is. A survey wake is
    -- `Wake(role, "tick:survey", refs=(area,))` -- the area is in `refs` and
    -- `detail` is empty, so recording detail alone answers "a survey tick"
    -- and loses "of what", which is the half the question is about.
    -- JSON, like `messages.body_refs`, because it is the same kind of thing.
    wake_refs    TEXT NOT NULL DEFAULT '[]',
    -- A hash of the composed brief this session actually ran against.
    --
    -- `prompt_hash` covers the whole prompt, working set and all, so it differs
    -- between two sessions that read the same brief and cannot answer "were
    -- these two runs told the same thing". That question is the whole of *did
    -- that edit help*: the artefacts derive from the source, the prompts and
    -- the model, and the first and third were recorded while the second was not.
    briefs_hash  TEXT NOT NULL DEFAULT ''
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

-- What the model was shown and what it said, one row per round-trip.
--
-- `tool_calls` records what a session *did*; this records what it was told and
-- what it replied, which is the thing that turned out to be missing every time
-- a session behaved oddly. The provenance panel had to admit it in prose --
-- "the working set pushed into this prompt is not retained" -- and a rebuilt
-- brief is not the prompt: it is how "the sentence was in there, so the role
-- ignored it" survives a week, when the sentence was in fact absent.
--
-- Named `turns` because that is what a session is a conversation of. The
-- cassettes have carried exactly this for the test corpus all along, keyed by
-- prompt hash; this is the same record for a *run*, where there is no case id
-- and the question is about the project rather than about a prompt.
--
-- Deleted with its session by the same transaction that writes it. A transcript
-- outliving a rolled-back session would be a record of something that did not
-- happen, and the most convincing kind, because it reads like an eyewitness.
CREATE TABLE IF NOT EXISTS turns (
    session_id  TEXT NOT NULL REFERENCES sessions(id),
    seq         INTEGER NOT NULL,
    system      TEXT NOT NULL,
    user        TEXT NOT NULL,
    completion  TEXT NOT NULL,
    ms          INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (session_id, seq)
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
-- Processes this system started, and enough to prove one is still ours.
--
-- A pid alone is not an identity. The operating system reuses them, so after a
-- crash and a reboot a recorded pid overwhelmingly belongs to something else --
-- and `boot.reap_processes` sends it SIGTERM. The only thing standing between
-- that and killing a stranger was an `except` treating "not ours" and "already
-- gone" as one outcome.
--
-- `started_at` is the second fact. A pid and its start time together are unique
-- for as long as the machine is up and cannot be coincidentally re-created: the
-- kernel will not hand the same pid to a process that started at the same
-- moment. Same rule as `worktrees.py` uses before removing anything -- two
-- independent facts, because either alone can be satisfied by an accident.
CREATE TABLE IF NOT EXISTS runtime_processes (
    pid        INTEGER PRIMARY KEY,
    batch_id   TEXT NOT NULL REFERENCES batches(id),
    command    TEXT NOT NULL,
    -- Process creation time as the OS reports it. Text, not a number: the unit
    -- differs by platform and nothing here does arithmetic on it, only equality.
    started_at TEXT
);

-- Phase config: caps are read from here, never hard-coded.
-- The frame, as judged and as ruled. The partition's heuristics are the
-- default; a row here overrides them for everything under `prefix`. The
-- judge session rests its row on a grain ref, so `frame_provenance` says
-- observed. A principal's ruling rests the row on a ruling ref, so the view
-- says decided, and decided outranks the judge. v2's first stage;
-- probes/partition_judge.py is the measurement that earned it.
-- The Critic's verdicts on understanding claims. `stands` is a claim that
-- survived an attempt to kill it; `falsified` carries the line of source
-- that killed it, and the ledger holds the consequence for the principal.
-- Standing comes from surviving challenge, never from who wrote a row.
CREATE TABLE IF NOT EXISTS challenges (
    id        TEXT PRIMARY KEY,              -- claim ref: <table>:<row id>
    -- stands: a line supports it. falsified: a line defeats it. unfounded:
    -- no line could do either -- the claim commits to nothing, which is a
    -- disease of its own (measured: identifier tautologies churned three
    -- sessions each, unverdictable under the two-verdict gate).
    verdict   TEXT NOT NULL CHECK (verdict IN ('stands','falsified','unfounded')),
    citation  TEXT NOT NULL DEFAULT '',      -- the grain that decided it
    quote     TEXT NOT NULL DEFAULT '',      -- the line, in the source's words
    why       TEXT NOT NULL DEFAULT '',
    version   INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS frame_rulings (
    id       TEXT PRIMARY KEY,               -- a path or directory prefix
    -- `surface` is the class the boundary phase surveys; the value shares
    -- the @surface: prefix's word on purpose.
    kind     TEXT NOT NULL CHECK (kind IN ('program','attached','ignore','surface')),
    reason   TEXT NOT NULL DEFAULT '',
    version  INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS config (
    key    TEXT PRIMARY KEY,
    value  TEXT NOT NULL
);

-- What each declared setting used to be, and who moved it, and why.
--
-- `config` is deliberately the principal's direct-edit space -- the one store
-- outside artefact law, so "humans do not edit artefacts" never comes under
-- pressure -- but a knob that forgets its past turns "why is the challenge
-- phase off on this run?" into archaeology. Append-only; written by
-- `config.set` whenever a declared setting actually changes. Read by the
-- principal months later, by an operator debugging a run, and by staleness
-- checks that need to know whether a choice predates what it governs. Never
-- read by roles.
CREATE TABLE IF NOT EXISTS config_history (
    key       TEXT NOT NULL,
    old_value TEXT,           -- NULL on first set: there was nothing before
    new_value TEXT NOT NULL,
    author    TEXT NOT NULL DEFAULT 'principal',
    at        TEXT NOT NULL DEFAULT (datetime('now'))
);
