# The channel between sessions, a read of the records, 2026-11-10

Result first:
A message reaches a receiver's model at the receiver's next model call, not at the send.
An idle receiver sees it in 0.0 to 1.5 seconds (17 of 24 messages on 2026-11-10).
A receiver in a turn sees it at its next tool round (3 messages, 2 to 23 seconds).
A receiver that waits on an AskUserQuestion dialog sees nothing until the dialog closes (4 messages: 6 minutes, 57 minutes, and 2 to rota-3d that its model never saw).
The sender gets the same "not yet read" result in every case, and only a reply proves a read.

Blind read. Sources: the session transcripts in
`C:\Users\roman\.claude\projects\d--repos-rota\`, `rota/tools/handover.py`,
the stack and its archive, and the public documentation. Times are the
transcript timestamps. The brief says that the local clock equals them.
The scripts are in this session's scratchpad, folder `r1`.

## How an arrival shows in a transcript

The receiver's transcript records each message in up to three lines:

1. A `queue-operation` line with `"operation":"enqueue"`. Its time is within 0.8 seconds of the send in 23 of the 24 cases of the day, and 1.5 seconds after it in one.
2. The model's first sight, in one of two forms:
   - an idle receiver: a `user` line that starts "Another Claude session sent a message:", which starts a new turn;
   - a receiver in a turn: an `attachment` of type `queued_command` and a `queue-operation` line with `"operation":"remove"`. The remove line has the time of the attach. The next `api-request` carries the message.
3. Nothing, when the receiver makes no model call. The enqueue line then stays the last line.

The attachment line copies the enqueue time. Its place in the file is after the tool result of the round that took it. So the first sight in the table below is the remove time, not the attachment time.

## A. The messages of 2026-11-10 among the five sessions

Session 5ee5ec0b sent and received no message among the five on this day. Its two sends went to rota-6b at 00:35 and its file ends at 02:55. One message came from outside the five: rota-f8 (c1a39439).

| # | Send | Sender | Receiver | First sight | Form | Delay | Receiver at the send | Reply in the same turn |
|---|---|---|---|---|---|---|---|---|
| 1 | 03:52:01 | rota-f8 | rota-a4 | 03:52:24 | mid-turn | 23 s | in a turn, model writing a tool call | 03:52:41 |
| 2 | 07:20:39 | rota-a4 | rota-13 | 08:17:23 | mid-turn | 56 min 44 s | AskUserQuestion open since 04:57:18 | none |
| 3 | 08:29:08 | rota-13 | rota-a4 | 08:29:09 | new turn | 0.3 s | idle since 07:28:41 (an idle compaction ran at the arrival) | 08:30:02 |
| 4 | 08:30:02 | rota-a4 | rota-13 | 08:30:02 | new turn | 0.0 s | idle since 08:29:19 | none |
| 5 | 10:16:12 | rota-13 | rota-82 | 10:16:12 | new turn | 0.3 s | idle since 10:15:44 | 10:17:02 |
| 6 | 10:17:02 | rota-82 | rota-13 | 10:17:04 | new turn | 1.5 s | idle since 10:16:23 | none |
| 7 | 11:03:12 | rota-a4 | rota-13 | 11:03:12 | new turn | 0.0 s | idle since 10:17:10 | none (forward to rota-82 at 11:03:21) |
| 8 | 11:03:21 | rota-13 | rota-82 | 11:03:21 | new turn | 0.1 s | idle since 10:56:00 | none (message to rota-a4 at 11:03:50) |
| 9 | 11:03:50 | rota-82 | rota-a4 | 11:03:50 | new turn | 0.3 s | idle since 11:03:25 | 11:04:18 |
| 10 | 11:04:18 | rota-a4 | rota-82 | 11:04:18 | new turn | 0.3 s | idle since 11:04:12 | none |
| 11 | 11:05:57 | rota-82 | rota-a4 | 11:05:57 | new turn | 0.1 s | idle since 11:04:45 | none |
| 12 | 11:24:28 | rota-a4 | rota-82 | 11:30:35 | mid-turn | 6 min 7 s | AskUserQuestion open since 11:22:31 | none |
| 13 | 12:00:55 | rota-a4 | rota-82 | 12:00:55 | new turn | 0.1 s | idle since 11:38:26 | none |
| 14 | 12:19:37 | rota-a4 | rota-82 | 12:19:37 | new turn | 0.1 s | idle since 12:13:11 | none |
| 15 | 12:41:19 | rota-a4 | rota-82 | 12:41:19 | new turn | 0.1 s | idle since 12:25:40 | 12:41:28 (to rota-a4 and rota-3d) |
| 16 | 12:41:26 | rota-82 | rota-3d | never | none | not seen | AskUserQuestion open since 12:27:14 | none |
| 17 | 12:41:28 | rota-82 | rota-a4 | 12:41:31 | mid-turn | 2.3 s | in a turn, tools running | none |
| 18 | 13:05:16 | rota-13 | rota-3d | never | none | not seen | AskUserQuestion open since 12:27:14 | none |
| 19 | 13:05:21 | rota-13 | rota-a4 | 13:05:21 | new turn | 0.0 s | idle since 12:45:47 | 13:05:39 |
| 20 | 13:05:39 | rota-a4 | rota-13 | 13:05:39 | new turn | 0.0 s | idle since 13:05:27 | none |
| 21 | 13:15:50 | rota-13 | rota-82 | 13:15:50 | new turn | 0.0 s | idle since 12:41:34 | 13:15:54 |
| 22 | 13:15:54 | rota-82 | rota-13 | 13:16:09 | mid-turn | 15.4 s | in a turn on Roman's prompt of 13:15:38 | none |
| 23 | 13:49:51 | rota-13 | rota-a4 | 13:49:51 | new turn | 0.0 s | idle since 13:05:55 | 13:50:10 |
| 24 | 13:50:10 | rota-a4 | rota-13 | 13:50:10 | new turn | 0.0 s | idle since 13:50:05 | none |

One more call carried no text. At 13:16:08 rota-13 sent rota-3d a subscription with `"notify_when_idle": true`. No idle notice shows in rota-13's transcript up to this read.

Counts for the day:

- 17 messages reached an idle receiver and started a new turn. The delay was 0.0 to 1.5 seconds.
- 3 messages reached a receiver in a turn and joined it at the next tool round: 2.3, 15.4 and 23.4 seconds.
- 2 messages reached a receiver with an open AskUserQuestion dialog. The model saw each one when Roman answered: after 6 minutes 7 seconds and after 56 minutes 44 seconds. The remove line falls 0.3 seconds after the dialog's tool result in both cases.
- 2 messages reached rota-3d during its open dialog and were never seen.
- 8 messages got a reply by message in the same turn. The reply came 4 to 53 seconds after the first sight.
- No receiver waited on a permission prompt at a send time. Every message carries `from-mode="bypass"`.

Earlier days, counts only. Over all transcripts there are 814 SendMessage calls and no CrossSessionMessage call. 631 went to subagents. 141 went to another session and got `"success":true`. Of the 141:

- 135 show a first sight in a receiver: 102 as a new turn, median 0.24 seconds, and 33 mid-turn, median 12.9 seconds, maximum 56 minutes 44 seconds. Four mid-turn cases took over 60 seconds: 56.7 minutes and 6.1 minutes (rows 2 and 12), 119 seconds and 70 seconds (2026-10-26 and 2026-10-11).
- 2 are subscriptions with no text.
- 2 are enqueued and never seen: rows 16 and 18.
- 2 show no trace in any transcript. They are named in section B.

One match is soft. A message of 2026-10-26 with the one word "released" matched at 178 seconds. A short text can match the wrong arrival, so that delay is not certain.

## B. Messages that never reach the receiver's model

Four messages. Each one is named here.

1. 2026-11-10 12:41:26, rota-82 (b49d24d2) to rota-3d (4a1d361a). Summary "Forward: rota side reads done, pointer for 363". Enqueued 12:41:27.042. Not seen.
2. 2026-11-10 13:05:16, rota-13 (7fd2421e) to rota-3d (4a1d361a). Summary "Roman's words on the sessions, a reading, a say-back request". Enqueued 13:05:16.765. Not seen.
3. 2026-11-01 18:27:40, session 3b83d22b to rota-cb. It starts "A claim for frame 330 waits for session 62bcfbfb". The sender got a held notice at 18:27:41 and an expiry notice at 18:32:41. The expiry text: "[Cross-session delivery notice] Your message to another session was not approved before expiry ... Not delivered to that session's Claude, and nothing is waiting there."
4. 2026-10-10 23:45:03, session 84ce0759 to a `uds:` pipe address. It starts "Session 84ce0759, peer rota-c5, took frame 199". No enqueue line shows in any transcript of this project. The receiver can be outside this project's folder. The records do not say.

The 10:16 message to rota-82 is row 5. It was seen in 0.3 seconds and answered at 10:17:02. A message at about 10:25 to rota-82: not found. Rota-13's transcript has no line between 10:17:10 and 11:03:12. Rota-82's transcript has no arrival between 10:16:12 and 11:03:21. No subagent transcript of rota-13 holds a SendMessage call.

The transcript of rota-3d (4a1d361a) from 12:26 to its end. The file has 206 lines, numbered 0 to 205.

- 12:26:33 to 12:26:39: the model writes its take note and runs the status tool. The result: "frame 363, line 1790: - Status 2026-11-10 12:26 (rota-3d) committed 99566d35".
- 12:26:39.645: the last `api-request`.
- 12:27:12.367 and 12:27:12.376: two assistant lines with thinking.
- 12:27:14.838: an assistant line with one tool call, `AskUserQuestion`, id `toolu_015z3n5ahc8R8igiSK1qtmL4`. The question starts "Last night you asked whether the project can change to spiral well". No tool result for this id exists in the file.
- Lines 199 to 203: bookkeeping with no time (`last-prompt`, `ai-title`, `session-owner`, `atis-latch`, `bridge-session`).
- 12:41:27.042: `queue-operation` enqueue of row 16.
- 13:05:16.765: `queue-operation` enqueue of row 18. This is the last line.

The 13:05 message appears as an enqueue line only. No dequeue, no remove, no attachment and no user line follows it. The file's last write time was 13:05:16 when this read listed it at about 14:08.

## C. The hand-off tool

The hand-off uses a claim file and a background watcher, not the message queue. The watcher polls every second (`POLL = 1.0`) and writes a heartbeat every 20 seconds (`BEAT = 20.0`). `hand` waits up to 90 seconds for the take (`CONFIRM = 90.0`). The watcher exits when the claim lands. The harness then starts a turn in the standby with a task notification.

Rota-3d shows the path at 12:25. The claim was written at 12:25:22. The watcher printed "CLAIM at 2026-11-10 12:25:23, after 42720s of blocking". The task notification started a turn at 12:25:23.811. The model ran `take` at 12:25:27.589.

Status lines in `plans/stack.md` and `plans/archive/` that state a delay:

- Sender lines: 65 hand-offs. Median 6 seconds, range 3 to 38 seconds. 21 of 65 read 6 seconds. Two read over 20 seconds: 23 seconds (2026-10-02) and 38 seconds (2026-10-25).
- The two hand-offs of 2026-11-10: 5 seconds (08:52, to rota-82) and 6 seconds (12:25, to rota-3d).
- Taker lines: 10 more. Two do not agree with the sender. Session b00cc646 wrote "30 minutes after the claim" for the claim of 02:08:14 on 2026-10-24, and the sender wrote "confirmed 14 seconds after the claim". Session 80cae596 took a vacancy "1 minute 40 seconds after the claim was posted" on 2026-10-12.

The brief `CLAUDE.md` says: "That wake was measured at 6 seconds after the claim appeared." `plans/operating-facts.md` says: "A session parked mid-turn drains nothing. One session held its inbound messages for six hours while it waited on a tool decision. A permission prompt parks a session the same way (observed: the same corpus)."

## D. What a sender can and cannot observe

From the transcripts:

- Every successful send returns one of three texts. The most common, 88 times: "(another Claude session on this machine; it is also connected via Remote Control; in that session's inbox, not yet read by its Claude — a [Cross-session delivery notice] follows if that session holds it (usually a different permission mode) or refuses it)". 30 omit the Remote Control clause. 21 name a `uds:` address in place of a name.
- Rows 16 and 18 got the same text as the messages that were seen. Row 18 returned: "“Roman's words on the sessions, a reading, a say-back request” → rota-3d (another Claude session on this machine; it is also connected via Remote Control; in that session's inbox, not yet read by its Claude — ...".
- A delivery notice comes only on a hold, a refusal or an expiry. All transcripts hold two notices of any kind: the expiry of 2026-11-01 and one idle notice of 2026-10-13.
- The subscription returns: "Subscribed — \"rota-3d\" will send one notice when it is next idle (or exits). It is delivered to you if that session runs in the same permission class as this one (or is one this session spawned); otherwise it is only logged here (this session holds other inbound peer traffic). Carry on; do not poll."
- No result or notice reports that the receiver's model read a message. The sender learns of a read only from a reply. It learns what the receiver understood only from the content of the reply.
- `ListAgents` shows each peer as `idle`, `busy` or `offline`. It was called 7 times in all transcripts, and not after 00:35 on 2026-11-10. Whether it shows a session with an open dialog as `busy`: not found.

From the documentation, https://code.claude.com/docs/en/cross-session-messaging:

- Documented: "The receiving Claude reads the message between tool calls during an active turn. When the receiving session is idle, Claude Code starts a new turn with the message."
- Documented: three outcomes at the receiver, "Delivered", "Held" and "Refused". "Delivered" means "Claude Code passes the message to the receiving Claude". The page does not say when the model reads a delivered message.
- Documented: a person at the receiver can see a queued message. "If Claude is busy and hasn't received the message yet, scroll to the end of the transcript, where the message is listed under `Waiting to be delivered`. Requires Claude Code v2.1.309 or later." The sessions here run version 2.1.319.
- Documented: the idle notice. "Idle here means the session finished a turn with nothing queued." Also: "If no notice arrives within 12 hours, Claude Code drops the subscription and tells Claude".
- Documented: a held message expires at `dialogExpiry`, "five minutes" by default. The case of 2026-11-01 expired 5 minutes after its hold.
- Documented: a message "can't answer a pending permission prompt on your behalf".
- Documented: "queues at most 50 accepted messages for Claude to read".
- Not documented: what happens to a delivered message while the receiver waits on an AskUserQuestion dialog or a permission prompt.
- Not documented: a read receipt to the sender.

From the documentation, https://code.claude.com/docs/en/remote-control:

- Documented: "**Push when actions required** for permission prompts and questions". A question dialog can push a notice to the phone.
- Documented: the Remote Control connection carries messages between sessions on different machines. The page says nothing about messages between sessions on one machine.

## E. Facts that the records cannot settle

1. Does a message held behind an open dialog reach the model when the dialog closes, or is it lost if the session ends first? Rows 2 and 12 say it arrives on the answer. Rota-3d has not closed. Measurement: answer or cancel rota-3d's dialog, then look for a `remove` line and an attachment of rows 16 and 18.
2. Does a permission prompt hold a message the same way as a dialog? No case on 2026-11-10. Measurement: send one message to a session that shows a known permission prompt, and compare the `remove` time with the time of the prompt's answer.
3. Does the idle subscription fire for a session parked on a dialog? None fired in this read. Measurement: close rota-3d's dialog and look for a "[Cross-session idle notice]" in rota-13's transcript.
4. Did Roman see rota-3d's question of 12:27:14? The transcripts do not record a push. Measurement: the phone's notification list or the Remote Control session view at claude.ai/code.
5. Does `ListAgents` show a session with an open dialog as `busy`? Measurement: one `ListAgents` call while rota-3d's dialog is open.
6. Did the receivers understand what they read? A transcript shows a read, not an understanding. Measurement: compare each reply with the message it answers, by a reader that holds neither.
