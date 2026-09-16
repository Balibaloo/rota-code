# Agent briefs

Written 2026-09-16, frame 19. The assistant that builds rota spawns three
kinds of agent. Each kind has one job and one skeleton. Copy the skeleton,
fill the angle brackets, cite the pointers. Do not re-derive what a report
in `plans/archive/` already holds: cite the report.

The three kinds, sized to the judgement each needs:

- A **reader** reads one document or one code area in full, judges every
  item against one page or one question, and returns a table with a verdict
  per item. Full-capacity model. One document per agent, in parallel, no
  shared context. Readers recur only when a document or the page changes.
- A **lander** applies a report that already holds the exact old and new
  text, or a change set with file and line. It runs the named tests, checks
  the line endings, and returns the diff. No judgement, so a small model is
  enough. A diff under about 30 lines the assistant applies itself.
- A **recorder** implements one fix brief, re-records the touched cases on
  the named host and model, and returns the before and after table with the
  transcript of every case that moved. Full-capacity model, because reading
  what the model sent is a judgement.

The assistant diagnoses and writes the fix brief. An agent never decides
what to change and changes it in the same pass.

## Rules every brief carries

1. Write the report file before you finish. The report is the only output.
   Write partial progress into it as you go, so a stopped run leaves a
   record.
2. Do not commit. The assistant commits.
3. Copy old text from the file, byte for byte, not from a report. A report's
   blockquote markers are not in the file.
4. The repository is LF. Before you finish, count 0x0D bytes with Python:
   `python -c "print(open('<file>','rb').read().count(b'\r'))"` must print 0.
   Do not trust a grep for the carriage return in the Bash tool alone.
5. Edit with the Edit tool. A patch that contains a backslash never goes
   through a bash heredoc. A file longer than a screen goes through the
   Write tool. See `plans/operating-facts.md`, the line-ending and heredoc
   facts.
6. Read what the model sent before trusting any number about it. A red on
   every run whose transcript shows the model never saw the changed words
   is not the change.
7. Do not stop your turn while a batch runs. A background process is not
   your child, and your turn ends with no result. Wait in the foreground.
8. Touch only the files the brief names. Another agent may hold the rest.

## Fixed pointers

- The page: `plans/composition.md`. It wins over every other doc.
- The facts: `plans/operating-facts.md`. Cite the section a brief needs, not
  the file. Sections used by recorders: the cassettes and their backup
  (`cassettes.db`, the SQLite backup API, one process at a time), the two
  GPUs and the recorder host, and the model pins.
- The register: `tests/rota/cases/*.yaml`. The live pass state is the
  `case_runs` table in `tests/rota/cassettes.db` (case_id, model,
  prompt_hash, run_no, passed, problems, seq, transcript, load_id). The
  latest recording of a case is its highest `seq`.
- The case runner: `tests/rota/test_l1.py`. Flags: `ROTA_L1=1` runs the
  model-backed cases, `ROTA_REFRESH=1` re-records, `ROTA_MODEL` picks the
  model (default `llama3.1:8b`; the register's current model is
  `qwen3:8b`), `ROTA_PROFILE` picks a profile, `-k` selects by case id
  (substring words, not underscores). `tests/rota/test_t1_liaison.py` runs
  the four model-backed Liaison tests with `ROTA_T1=1`.
- The recorder host: the Titan, `OLLAMA_HOST=http://127.0.0.1:11435`. The
  3080 on 11434 runs nights. Before a run: `curl -s localhost:11434/api/tags`
  and `curl -s localhost:11435/api/tags` both answer, and no other pytest or
  recorder runs (PowerShell: `Get-CimInstance Win32_Process -Filter
  "name='python.exe'"`).
- Backups: copy `tests/rota/cassettes.db` with the SQLite backup API to
  `.rota/cassettes_backup_<date>-<frame>-before.db` before a re-record, and
  to `...-after.db` after. Never `cp` an open database.
- Prompt composition: `rota/roles/prompts.py`. A role's `base.md` is
  composed into every mode of that role except where a `<mode>.base.md`
  exists (the Liaison's `landing` composes on `landing.base.md`). A change
  to `base.md` re-hashes every other mode's prompt, so every case of the
  role re-records.
- Case-to-mode maps: the Liaison's 34 cases and their modes are the table
  "Cases that exercise the Liaison" in
  `plans/archive/placement-liaison-2026-09-16.md`. For another role, derive
  the map once: grep `tests/rota/cases/*.yaml` for `role: <role>`, read the
  `prompt:`, `tick:` or inbound verb of each case, and write the table into
  the frame's report so the next brief cites it.
- Tests without a model that pin prompt words: `tests/rota/test_prompts.py`,
  `tests/rota/test_roles_doc.py` (ROLES.md against the graph),
  `tests/rota/test_docs.py`, `tests/rota/test_identity.py`,
  `tests/rota/test_vocabulary.py`.

## Skeleton: reader

    You work in the git repository D:/repos/rota. Read-only: do not edit any
    file under the repository. Write your report to <report path>.

    Task: place every item of <document> under a line of <page>, or answer
    <one question> from <code area>.

    Steps:
    1. Read <page> in full. It wins.
    2. Read <document> in full. Split it into items: <paragraph, bullet,
       heading, sentence>. Number them in file order with the line number.
    3. For each item give exactly one verdict: PLACES (quote the page line),
       DETAIL (name the section), CONTRADICTS (quote both, propose the new
       wording in Simplified Technical English, fewest words that remove the
       denial), ORPHAN (propose delete or move, one reason).
    4. Report: a summary line with counts, one table (Item | Line | Verdict |
       Page line or section | Proposed change), then "Proposed changes" as
       old text -> new text per file, then <the scoping facts the lander or
       recorder needs: tests that pin words, cases per mode>.

    Constraints: do not fit the page to the document. Where the page is
    silent, say DETAIL or ORPHAN. Report only from the files named. Write
    the report file before you finish.

## Skeleton: lander

    You work in the git repository D:/repos/rota. Edit exactly <the files>.
    Do not commit. Write a short report to <report path>.

    Task: apply items <list> of <report>, section <name>, to <file>. Do not
    apply <held items>: they wait on <ruling>.

    Steps:
    1. Read the section. For each item read the file around the cited
       lines and copy the old text from the file, byte for byte.
    2. Apply each with the Edit tool. Wrap at the file's line width.
    3. Count 0x0D bytes with Python; the count must be 0.
    4. Run: <tests that parse or pin the file>. Paste the last five lines.
       If a test asserts a literal phrase you changed, restore the phrase
       and say so.
    5. Run git diff --stat <file>.

    Report: each item applied yes or no with its landed line, the 0x0D
    count, the test tail, the diff stat, any phrase restored.

## Skeleton: recorder

    You work in the git repository D:/repos/rota. Edit exactly <the brief
    files>. Do not commit. Write your report to <report path> and write
    partial progress into it as you go.

    Context: <the red, its case id and file:line, what the model sent, the
    diagnosis in two sentences>.

    The fix, <n> paragraphs in <file> (copy the old text from the file):
    Old: <...>  New: <...>

    Steps:
    1. Apply the edits. Count 0x0D bytes with Python; must be 0.
    2. Run <prompt tests without a model>; paste the tail.
    3. Re-record. `curl -s localhost:11435/api/tags` must answer. Confirm
       no other pytest or recorder runs. Back up cassettes.db with the
       SQLite backup API to .rota/cassettes_backup_<date>-<frame>-before.db.
       Environment: OLLAMA_HOST=http://127.0.0.1:11435, ROTA_MODEL=qwen3:8b,
       ROTA_L1=1, ROTA_REFRESH=1. Re-record <the cases>, one foreground
       Bash call per case file, timeout up to 600000 ms, repeat a call that
       times out, select by case id with -k. <If base.md changed: every
       case of the role except the modes with their own base.> Then <the
       model-backed Python tests> with <flag>. Then back up to ...-after.db.
       Do not stop your turn while a batch runs.
    4. After-table from tests/rota/cassettes.db, read-only: for each case
       the pass count of the latest recording (highest seq for case_id and
       model, passed summed over run_no), with a "changed" column against
       <the baseline>. For every case that went down: the last model turn
       from the transcript column, verbatim, trimmed to 40 lines, and the
       problems column.
    5. Report sections: (a) the diff, (b) the prompt test tail, (c) the
       after-table, (d) the transcripts, (e) the Python test results, (f)
       wall-clock time, (g) the 0x0D count. Finish only when all seven
       sections exist.

    Rules: read what the model sent before trusting a number about it. You
    measure. You do not change the brief beyond the named paragraphs, and
    you do not change a case. If Ollama hangs past 20 minutes on one turn,
    stop that batch, note it, continue.

## Costs measured in frame 18

| Kind | Job | Tokens | Time |
|---|---|---|---|
| reader | LAWS, 87 items | 96k | 9 min |
| reader | ROLES, 70 items | 77k | 6 min |
| reader | Liaison brief, 175 items, 19 files | 149k | 14 min |
| reader | checkpoint check, every reader and writer of one table | 115k | 6 min |
| lander | ROLES, 32-line diff, full model | 76k | 5 min |
| lander | LAWS, 10 items, small model | 74k | 2 min |
| recorder | 34 cases, stopped three times waiting | 222k | 35 min |
| recorder | 28 cases, foreground batches | 120k | 27 min |

A recorder cycle of 28 Liaison cases on qwen3:8b takes about 20 minutes
of wall clock on the Titan.
