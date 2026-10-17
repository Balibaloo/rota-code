# Frame 286, review 3: commit 64fa6b6a

Review of the touch_mistaken sentence fix. Read-only. No test ran. Rota workflow.

## (a) Verdicts

1. Stands. Each of the three sentences gives one instruction. The word counts are 18, 6 and 3. The paragraph follows the restore-then-commit procedure of the paragraph above it.
2. Stands, with one low gap (finding 1). The sentence names `code.write`, the span of the definition and "Keep the rest of the file". `code_write` exists at `rota/roles/api.py:14016-14017`, with `start: int = 0, end: int = -1`. Any span other than 0 and -1 replaces those lines only.
3. Stands. `--numstat` shows `3 2 rota/roles/prompts/developer/touch_mistaken.md` and no other file. The file keeps LF endings: 0 CRLF before and after.

## (b) Findings

1. `rota/roles/prompts/developer/touch_mistaken.md:10-12`, low, PLAUSIBLE. "over its span" does not say where the span numbers come from. `code_write`'s docstring says the Developer copies `start` and `end` from `code.source`. `batches.strays` (`api.py:16498`) returns only `path, status, note`, so it gives no span and no base text. `batch_start.md:27` names the `code.source` source of the numbers, but this prompt does not. The gap was already in pass 1b, so this commit does not add it. Fix: write "over the lines `code.source` shows for it" in place of "over its span".
2. Same lines, low, PLAUSIBLE. "the base source" is a new term. The paragraph above says "as it stood before the batch" for the same thing, so one meaning has two words, against the STE word rule. Fix: write "the definition as it stood before the batch".

## (c) Probes

- `git show 64fa6b6a`, `git show 64fa6b6a:<prompt>` and `--numstat`: the diff and the file.
- `python -m rota.tools.map fn code_write` and `fn batches_strays`, then reads of `api.py:14016-14040` and `16497-16506`.
- A `python -c` byte count of CRLF and LF on the prompt at `64fa6b6a^` and `64fa6b6a`. The result is 0/15 and 0/16.

## (d) Usage

About 9k input tokens and 2k output tokens, about 11k in total. This is my own estimate. Read the harness line for the real figure.
