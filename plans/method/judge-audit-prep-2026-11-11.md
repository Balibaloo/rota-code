# The material for the blind audit of a judge, prepared 2026-11-11

## Result first

1. The material holds 35 hand-offs: 14 corrected, 7 approved and 14 not watched. Each hand-off has one stretch file and one pack file under a code of four letters.
2. One approved hand-off is lost. A3, be3ef742 to c81dd240, frame 200, has no taker transcript on disk now.
3. The earlier scans missed the queued prompts of Roman. A queued prompt is text that he typed while the session worked. Over the 89 hand-offs with a transcript, the scan finds 34 queued prompts in 17 hand-offs.
4. Four hand-offs that the earlier pages count as "typed nothing" were watched. A13 and A38 hold a queued prompt, and A79 and A81 hold a dialog answer. So 52 of 93 hand-offs were watched in the first three hours, not 48.
5. The leak check finds no leak in the final files. A stranger can guess the not watched group from the length of the stretch. The corrected and approved groups are hard to tell apart.

## Method

1. The groups come from `t1/rows.json` of the kinds page. Corrected means one typed correction or more that is not a machine pause. Approved means the test of "went best". Both counts match the page.
2. The pool for not watched starts from the 45 of the page. The rescan removes 2 with a queued prompt, 2 with a dialog answer and 2 with no transcript. That leaves 39.
3. The draw sorts the 39 by take time and runs `random.seed(20261111)` and `random.sample(pool, 14)`.
4. The 35 hand-offs are sorted by take time and shuffled with the same seed. The codes come from the same random state, so the code order shows no group or date.
5. A corrected stretch ends just before his first correction that is not a machine pause. An approved stretch ends just before his first approval. A not watched stretch ends at three hours, or at the end of the session if that comes first.
6. Three corrected stretches held a queued prompt before the cut. The labels follow the rules of the kinds page, method item 5. A87 at 3.8 and A67 at 91.2 are "question", so they stay in the stretch as a ROMAN block. A29 at 87.4 rejects the design that it quotes and asks a question, so its label is "correction, question". The cut of A29 moves from 118.4 to 87.4.
7. A stretch holds ROMAN, SESSION, TOOL, RESULT and PEER blocks with the caps of the brief. Queued prompts and dialog answers before the cut are ROMAN blocks. A stretch over 70,000 characters keeps the first 15,000 and the last 55,000, with one line that counts what is left out.
8. A pack holds the brief, the intent page, the note, the memory index, the handed frames, the hook lines and Roman's earlier messages. Each git text is the last commit before the take, with the local offset of the date.
9. The note is the last commit at or before the later of the take and the post time plus 120 seconds. No selected note was committed after the take.
10. The memory index is the t2 copy for 5 sessions. For the other 30 it is the first copy in the session's own transcript, before the take.
11. The handed frames are the receipt's frame, plus each frame whose stack heading names the sender and whose number the note names. The pack has at most 8 frames.
12. Section 7 of a pack lists every message that Roman typed in the session before the take. It does not judge which of them is a standing instruction.
13. Hook lines count as distinct after each digit is replaced. The first copy of each goes to the pack.

## Counts

- Stretch sizes: 19,616 to 70,121 characters. 21 stretches are truncated: 8 corrected, 2 approved and 11 not watched.
- No stretch is short. The fewest tool calls in one stretch is 24.
- One stretch has the flag "second take", A51. Its taker took an earlier receipt.
- The key holds each code's hand-off, group, take, cut, minutes, tool calls, characters, flags and the message at the cut. It also holds his later messages with their labels, the queued prompts and dialog answers in the stretch, and the method of each pack.
- The key holds every later queued prompt too. A queued prompt after the cut carries the label "unlabelled", because nobody labelled it.

## Checks

1. The script `a1/scripts/s3_check.py` searches every S_ and P_ file for the label words as words, the group words and the hand-off's own A and H id. It also searches for each later message of Roman of 15 characters or more.
2. The script compares the time of each stretch entry with the cut. It compares each commit date in a pack, the memory copy and each message of section 7 with the take.
3. The first run found one leak. In A29 the queued prompt sits later in the file than its time stamp, so three entries came after Roman typed. The build now drops every entry at or after the cut time. The second run finds no problem.
4. The words "correction" and "approval" occur in the session's own text 101 times over all files. They come from the record and are not labels. Their count follows the length of the files, not the group.
5. 26 later messages are shorter than 15 characters, for example "pause" and "Yeah". The search cannot test them.

## The read as a stranger

1. A corrected stretch of 8.5 minutes reads as plain work and ends on a status reply. Nothing in it shows what Roman said next.
2. An approved stretch ends after the session explains two options and gives a recommendation. A stranger can expect a ruling next, but not its sense.
3. A not watched stretch runs to minute 45.2 and ends on an open dialog that nobody answers. A stranger can read the silence.
4. The span gives the not watched group away. In 11 of 14 the last entry comes after minute 140, and none holds a ROMAN block. Of the 21 corrected and approved stretches, 2 have a last entry after minute 140, and 13 hold a ROMAN block.

## Limits

- The approved group has 7, not 8. The not watched draw is from 39, not 45.
- The labels of the three queued prompts are one reader's judgement, with no second reader. Later queued prompts have no label.
- A stretch keeps the order of the record. A queued prompt shows where the session received it, and its own time can be earlier than the entry above it.
- An uncommitted edit of the brief, the note or the stack at the take does not show.
- A message that Roman typed in the sender's terminal is not in the taker's record.
- The judge sees the span of each stretch, so a blind read of the not watched group is not blind. A comparer can cut every stretch to an equal span, or leave that group out.
- The files are in the scratchpad folder `a1`, which is not in git.
