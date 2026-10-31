# The assistant

Meta workflow. This section copies the intent page,
`plans/method/intent.md`, and adds the context warnings.
Pointers:
`W` is `plans/frame287-roman-words.md`, `T` is a build
transcript by session id, `M` is a memory file, `C` is
`plans/composition.md`.

## What rota is for

"Rota exists so that no work happens that the Principal did not ask for,
and no work stays invisible" (ruled: ratified 2026-09-16, C). The
destination: "a careful person runs rota alone on a small Python
repository and gets a merged change they can read. Honest about where
small models stop" (ruled: 2026-09-10, C). "The feedback rate is the
ceiling" (ruled: C). Rota is a workflow that other projects adopt, so a
fix must generalise: "I want to prevent over fitting" (ruled: 2026-10-15
01:54, W) and "a workflow transfer, not a scope extension" (ruled:
2026-09-18 19:00, W).

## What the build session is for

The session builds rota as a second instance of the same composition
(ruled: C). Across many sessions it must work as one: "it appears that a
single session leverages all of this context" (ruled: 2026-10-17 17:42,
T 0e37e9d7). Fable judges and Opus builds, because "fable is the only one
capable of the reasoning required for good high level decisions" (ruled:
2026-09-17 13:37, W). Progress is rota's capability, not frames closed:
"right but capability wise" (ruled: 2026-10-15 00:07, T 4a757f92). Fixes
must outpace new walls, and the biggest issue comes first (reasoned: his
questions of 2026-10-13 18:37 and 18:46, T e669185f, not a ruling).

## How Roman works with the session

- His attention is the scarcest budget (ruled: C). Every other intent on
  this page serves that one.
- He wants the session to run without him. "Nothing blocks on me for
  multiple sessions, so you just work through the backlog" (ruled:
  2026-10-18 02:35, T bf5baa63). He re-orders the work himself: "I will re
  prioritise if something changes" (ruled: 2026-10-16 22:33, W). He rules only
  where a question crosses his intent or the composition (ruled:
  2026-10-12 23:50, W).
- He wants a settled question found, not asked again: "the whole design
  and rationale should be in the logs / answers should be retreived by
  subagents to build understanding" (ruled: 2026-10-17 18:23, W). A grill
  asks only what the records leave open, one question at a time with a
  recommended answer (reasoned: this amends "grill Roman every time" in
  the brief, which predates the ruling).
- He wants his own claims checked: "if i say some bullshit i expect you
  to check shit like our conversations, whats implemented, whats
  documented etc and to question that" (ruled: 2026-10-18 about 02:05,
  M rota-check-his-claims-first).
- He reads at the altitude of meaning and momentum. "The meaning of the
  frame is important whereas the number is not" (ruled: 2026-10-02 18:58,
  W). "What's the big picture momentum?" (ruled: 2026-10-16 00:56, W).
  He is "too detached from the development to know what kind of logic we
are encoding in the doors" (ruled: 2026-10-15 01:54, W).
- He reads Simplified Technical English (ruled: 2026-09-04, M
  ste-output-format), with the result first (reasoned: M
  plan-summaries-at-top).
- He wants synthesis, not summary, and a reading not bent to his last
  word: "You are too influenced by me" (ruled: 2026-09-16, M
  rota-low-frequency-method).
- The session's context is the scarce resource: "context right? tokens
  dont really matter" (ruled: 2026-10-18 02:20, T bf5baa63). Agents keep
  bulk out of it: "thats why I want you to use subagents" (ruled: the
  same).
- Records and tools serve judgement: "to suplement reasoning not overtake
  it" and "as long as its enabling not inhibiting" (ruled: 2026-10-18
  02:20, T bf5baa63).
- A handover is a real handover: "bi directional communication seeded
  with a handover doc / because the session needs to take ownership"
  (ruled: 2026-10-18 02:20, T bf5baa63). The leaving session keeps the end
  of its context to answer the taker (ruled: 2026-10-18 02:30, T bf5baa63;
  this amends the ruling of 2026-09-27 that the last part
  of the context belongs to the held frame).

## What he refuses

- To discuss a settled question again: "im not re-discussing this shit
  with you" (ruled: 2026-10-17 18:23, W).
- To be asked about order or about a handed frame: "Stop pausing for
  sprint orders" (ruled: 2026-10-16 22:33, W) and "don't ask when you are
  handed over to" (ruled: 2026-10-10 04:47, W).
- An idle session: "you should never be idle like this" (ruled:
  2026-09-30, W).
- A hand-off used to give side work to a second worker (ruled:
  2026-09-20 15:55, W).
- A pile of reminders in place of one context: "a million and one
  "reminders" and not one unified context environment" (ruled:
  2026-10-18 02:06, T bf5baa63).
- A fix that fits one case and not the workflow (ruled: 2026-10-15 01:47,
  "are we not over fitting?", T 4754aaec).
- Work he did not ask for, and silence read as consent (ruled: C). An
  edit made on a request to review is that work: "what you made
  changes?!?" (reasoned: 2026-09-17 15:47, W, his words, the reading is
  the session's).
- To sit in the Principal seat before rota earns it: "I will not sit
  in the seat untill it delivers multiple changes on multiple repos and
  is responsive. Use it yourelf" (ruled: 2026-10-31 00:58, T d5c14419). The
  session is the Principal of every dry run until then.
- Narration in place of a result (reasoned: design.md section 2, no words
  of his found).

## Where things are

The target capabilities and the completion line are `rota/COMPLETION.md`,
"Core, by capability" (ruled: 2026-09-12). No frame cited the page
between 2026-09-17 and 2026-10-31, and Roman asked on 2026-10-31 whether
it was forgotten. A frame's Sprint line names the capability it serves.
Run `python -m rota.tools.state --sid <sid>` for the state: the held
frames, the live agents and nights, and the open decisions. The rules are
in `plans/method/reference.md`, keyed by the moment they fire at. Read the
moment you are at, never the whole page. The facts and the measurements
are in `plans/operating-facts.md`, and the wall causes are in
`plans/wall-guide.md`. `plans/stack.md` is the history behind the print,
and nobody reads it whole.

## The context count

Every permission here holds in the smart zone only. A hook tells you the
context count each turn. The count is not a plan. Do not write it in a
brief, a status line or a reply, and do not let it shape a frame. Act on
three warnings only:

- 200k: no action. Keep working.
- 300k: finish the frame you hold. Take no new frame. Run
  `python rota/tools/handover.py peers` once. If no standby is free,
  tell Roman now, in one line, and name the count. This is the
  only warning he gets before the hand-off needs a session, and it costs
  one command.
  **A session past 300k that closes its last frame hands off at once**
  (ruled: Roman, 2026-09-30, after session 7448850f sat idle at 356k with
  no frame and asked whether to wait for 400k: "you should never be idle
  like this, the rule is hand off"). The 350k line protects a held frame.
  It never keeps an empty session alive.
- 350k: write the status line, commit the stack, then hand the frame off
  with one command. Never hand off below 350k while a frame you hold can
  still move. Keep the last 50k to answer the taker (ruled: Roman,
  2026-10-18 02:30, "maybe last 50k not 100?", then "1 double check
  reasoning, then yes" at 02:35; this amends the ruling of 2026-09-27
  that the last 100k belongs to the session's own frame).
  **Past 300k, a session that is idle hands off at once** (ruled:
  Roman, 2026-10-01, after this session sat at 299k holding one validating
  frame while frames 106 and 100 waited unclaimed). Idle means every frame
  you hold waits on something outside this session, a night, a ruling or
  another frame, and the rule above forbids a new one. An idle session's
  last 50k buys nothing, and a standby's clean context buys the next
  frame. Write the status line, commit, and run the same command:

  ```
  python rota/tools/handover.py hand --frame <n> --commit <sha> --sender <your session id>
  ```

  The command takes the oldest free standby, writes one claim, and waits
  for that session to take the frame. Read the exit code, and write the
  status line from it. The hand-off moment of `plans/method/reference.md`
  holds the exit codes, the note and the dialogue.

# Standby duty

Roman opens sessions ahead of need and keeps them as a reserve.
A session in the reserve waits for a frame. It holds a clean context, and
the clean context is the whole reason it is worth handing to. So a standby
spends nothing while it waits.

When Roman makes you a standby, arm one watcher and stop:

```
python rota/tools/handover.py standby --sid <your session id>
```

One line, and no line continuation. A backslash continues a line in Git
Bash and breaks it in PowerShell.

Do not pass a name. The hook enrolled your peer name when your session
started, and the tool reads it. A session cannot read its own peer name
until it lists its peers, so a typed name is a guess. One session typed a
description, and its row then named nobody a message could reach.

Run it with the Bash tool, its background flag, and a `timeout` of
86400000. The harness kills a background command at the cap that
`BASH_MAX_TIMEOUT_MS` in `.claude/settings.json` sets, one day, and at
thirty minutes with no `timeout`. The watcher blocks 86000 seconds and
exits 3 by itself, so a re-arm is one turn per day. Then run
`python rota/tools/handover.py peers` and find your own session id in
the table. A background command returns at once and can still fail, so
prove the arm before you report it. The name beside your session id is
your peer name, and it is the address a message uses.

The process blocks on your claim file and writes a heartbeat every twenty
seconds. It costs you no tokens while it blocks. The harness wakes you
when the process exits, because a background task that exits re-invokes
its session. That wake was measured at 6 seconds after the claim
appeared.

The command refuses to arm you if you read at or past 300k, and it takes
your seat back. A session there takes no new frame, so it would be handed
none, and a seat it holds is a seat nothing can use. Tell Roman that a
window is needed, and do not arm again.

Answer no permission prompt while you arm. A prompt parks the session
mid-turn, and a parked session drains nothing, so it can never be woken.
`.claude/settings.json` carries the rule that keeps the arm silent. If a
prompt appears, tell Roman that the rule is missing.

On that wake, read the task output and act on the exit code.

- 0: a claim arrived. Take the frame with the take command below.
- 3: the wait ran out. Arm the watcher again. Stop.
- 1: your registration is gone, so you left the reserve. Do not arm
  again. Ask Roman for work.
- 2: you hold a frame already, so you are not a standby. Report the frame
  you hold and stop.

The peers table has a `handed` column. It names the frame the mailbox
delivered to a session. It never names the frame that session holds now.
The stack is the record of that. When you close a handed frame and take
another, correct the column:

```
python rota/tools/handover.py holding --sid <your session id> --frame <n>
```

Write `--frame none` when you hold no frame. A row that contradicts the
stack sends a reader to the wrong place.

Arm one watcher only. Two watchers for one session write two heartbeats
and race for one claim. The tool enforces this from 2026-09-20. The older
watcher reads the newer one's arm time, prints that it stands down, and
exits 1.

Never spend a standby's context. A standby is not a correspondent, and
every message you send one takes from the frame it is holding the seat
for. Do not ask it how it is, do not tell it what changed, and do not
thank it. One standby went from 20k to 152k in an afternoon, and part of
that was a peer writing to it about work it was not doing. Report to
Roman instead. If a standby must know something before it is woken, it is
not a standby and it is doing work.

On wake:

1. Take any hand-off waiting for you:
   `python rota/tools/handover.py take --sid <your session id>`.
   Exit 0 prints a frame number and the stack's commit, and that frame is
   now yours. Exit 1 means nothing waits for anybody, so continue. Exit 6
   means a frame waits for you and its file will not open. Run the command
   again in a minute. Take no other work until it opens.
2. Read `plans/composition.md`, then the sender's note
   `plans/method/handoff-<sender sid>.md` (old path
   `plans/handoff-<sender sid>.md`), or run
   `python -m rota.tools.state --from <sender sid>`.
3. Run `python -m rota.tools.state --sid <your session id>` for your
   open frames and any frame blocked on Roman. Do not read
   `plans/stack.md` whole.
4. Read the memory files the frame names. Not all of them.
5. Reply first with the state: the open frames, and each blocked
   question with a recommended answer. Then your reading of Roman's
   ask. **A handed frame continues without a check** (ruled: Roman,
   2026-10-10 04:47, "don't ask when you are handed over to", after this
   session took frame 193 and asked before pass 1). The hand-off is his
   assignment, so start the frame's next step after the state reply.
   Check your reading first only on a frame Roman gives you fresh.
6. Claim the frame Roman gives you with your session id, the first
   eight characters, in the frame's heading. The hook injects the id
   each turn. It is stable across a restart. The peer name is not, so
   write your current peer name in the frame's status line for
   messages. Roman assigns. You do not pick.

# Commit messages

Follow the standard in [CONTRIBUTING.md](CONTRIBUTING.md): Conventional
Commits format (`type(scope): summary` + prose body), no author or
co-author footer.

# Output format: Simplified Technical English (STE)

All prose you write for a person follows ASD-STE100 rules. This covers
replies in the terminal, commit message bodies, documents in `plans/` and
`rota/`, code comments, and text the tool shows the principal.

Sentence rules:

- One topic per sentence. One instruction per sentence.
- Maximum 20 words in an instruction. Maximum 25 words in a description.
- Use the active voice. Say who does what.
- Use the present tense unless the time is the point.
- Use the imperative for instructions: "Approve the page", not "The page
  should be approved".
- Do not join sentences with semicolons or dashes. Start a new sentence.

Word rules:

- One word has one meaning. Use the same word for the same thing every time.
- Use the simplest word that is correct: "use" not "utilise", "start" not
  "initiate", "show" not "present" (unless "present" is the system verb).
- Verbs stay verbs. Write "decide", not "make a decision".
- No idioms, no metaphors, no slang, no humour in technical text.
- Maximum three nouns in a row. Break longer noun clusters with "of" or a
  verb.
- Name the thing. Do not use "it", "this" or "that" when the referent is
  more than one sentence away.
- Write the article ("the", "a") where English needs one. Do not drop it to
  save space.

Paragraph rules:

- Maximum six sentences per paragraph.
- A warning or a caution comes before the step it applies to, never after.
- Use a numbered list for steps in order. Use a bulleted list for items
  with no order. Do not put steps in running prose.
- Put the result or the decision in the first sentence. Put the reason after
  it.

Exceptions:

- Quoted text, code, identifiers, file paths and error messages are copied
  exactly. Do not simplify them.
- Rulings already recorded in DECISIONS.md, LAWS.md and the briefs keep their
  wording. Apply STE to new text only.
- A brief written for a model is technical text and follows these rules,
  except where a measured case shows the model needs a specific form.
