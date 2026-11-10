# Work across a boundary between agents: what the sources say

Read date: 2026-11-10. Method: web search and a read of primary sources. No hypothesis was given.

## Result first

- A receiver knows only what the sender writes down. Every source agrees on this point.
- A summary drops exact items first: one-time user constraints, file lists, exact commands. One 2026 benchmark measured 17% retention of constraints.
- State outside the context carries the work: files, git history, tests, an event log. Summaries alone do not.
- One 2026 study measured a hand-off between coding agents. The raw trace beat notes on solve rate. Any hand-off view beat none.
- No source measures whether the receiver understood the hand-off before it acted.
- Most advice comes from team reports with no controlled test. The measured work is recent and small.

## How to read this page

Each item has an evidence label and a scope label.

Evidence labels:

- **[M]** A measured result. The item gives the benchmark and the count.
- **[E]** An engineering report. A team reports its experience. No controlled test.
- **[O]** An opinion or an argument.

Scope labels:

- **(one)** One context window, or one agent across compactions.
- **(seq)** Sessions in sequence. One agent stops and a fresh one continues.
- **(parent)** A parent with subagents.
- **(peers)** Agents with no parent, or agents that message each other.

Source tags such as [S23] point to the list at the end. A source older than 2025 has the note "older than 2025".

## 1. Why multi-agent systems fail

### MAST, Cemri and others [S1]

- **[M] (parent, peers)** The paper annotates 1,642 traces from 7 frameworks. It defines 14 failure modes in 3 classes. Date: March 2025, version 3 in October 2025, NeurIPS 2025.
- The annotators agree at kappa 0.88. An LLM annotator reaches 94% accuracy and kappa 0.77 against the experts.
- The shares below are from version 3. Version 1 gave different shares, so a citation must name the version.

| Code | Failure mode | Share |
|---|---|---|
| FM-1.1 | Disobey task specification | 11.8% |
| FM-1.2 | Disobey role specification | 1.5% |
| FM-1.3 | Step repetition | 15.7% |
| FM-1.4 | Loss of conversation history | 2.80% |
| FM-1.5 | Unaware of termination conditions | 12.4% |
| FM-2.1 | Conversation reset | 2.20% |
| FM-2.2 | Fail to ask for clarification | 6.80% |
| FM-2.3 | Task derailment | 7.40% |
| FM-2.4 | Information withholding | 0.85% |
| FM-2.5 | Ignored other agent's input | 1.90% |
| FM-2.6 | Reasoning-action mismatch | 13.2% |
| FM-3.1 | Premature termination | 6.20% |
| FM-3.2 | No or incomplete verification | 8.20% |
| FM-3.3 | Incorrect verification | 9.10% |

- The class totals are sums of the mode shares. System design issues: 44.2%. Inter-agent misalignment: 32.35%. Task verification: 23.5%.
- The modes that concern a hand-off or lost context are FM-1.4, FM-2.1, FM-2.2, FM-2.4 and FM-2.5. Their sum is 14.55%. The sum is this page's arithmetic, not the paper's.
- The modes that concern drift from the given goal or role are FM-1.1, FM-1.2 and FM-2.3. Their sum is 20.7%. The sum is this page's arithmetic.
- Direct loss of history is rare: 2.80% and 2.20%. The larger shares are an agent that does not ask (6.80%) and an agent that derails (7.40%).
- The verification class is 23.5%. The work was declared done with no check, or with a wrong check.
- **What does not work, per the source:** A better base model alone. The authors write that failure "is not merely a function of challenges in the underlying model".
- **[M]** Two case studies changed the system design of ChatDev. A role and workflow change gave +9.4% task success. A verification step for the high-level objective gave +15.6%.
- Limit: the traces come from 2024 and 2025 research frameworks. None is a current coding harness.

### Who and When, Zhang and others [S2]

- **[M] (parent, peers)** The dataset holds failure logs from 127 multi-agent systems. Each log names the agent and the step that caused the failure. Date: April 2025.
- The best automated method names the correct agent in 53.5% of cases. It names the correct step in 14.2% of cases.
- Meaning: a system cannot yet find reliably where its own hand-off failed. Abstract read only.

### Towards a Science of Scaling Agent Systems, Kim and others [S3]

- **[M] (parent, peers)** The paper tests 260 configurations: 6 benchmarks, 3 model families, 5 architectures. Date: December 2025, version 3 in April 2026.
- Against one agent, the result ranges from +80.8% (a finance task that splits cleanly) to -70.0% (a planning task with steps in sequence).
- More agents give a negative return when the single agent already scores above about 45%.
- Error amplification against one agent: independent agents 17.2 times, decentralized 7.8 times, hybrid 5.1 times, centralized 4.4 times. The effect is not significant after controls (p = 0.658).
- Coordination overhead: independent 58%, decentralized 263%, centralized 285%, hybrid 515%. Mean turns rise from 7.2 to between 11.4 and 44.3.
- The paper's model picks the best architecture for 87% of held-out configurations. Its cross-validated R squared is 0.373.
- **What does not work, per the source:** Any multi-agent form on a task with steps in strict sequence. Every form lost 39% to 70% there.
- Limit: two of the benchmarks use 20-instance subsets.

### AgentAsk, Lin and others [S4]

- **[M] (parent, peers)** The paper names four error types at a message hand-off: data gap, signal corruption, referential drift, capability gap. Date: October 2025, version 2 in January 2026.
- A module that asks short clarification questions at the hand-off gives up to +4.69% accuracy on 5 benchmarks. The extra cost stays below 10%.
- Abstract read only. The gain is small.

## 2. Engineering reports

### Anthropic: the multi-agent research system [S5], 2025-06-13

- **[M] (parent)** A lead with subagents beat a single agent by 90.2% on an internal research evaluation. The evaluation began with about 20 queries and an LLM judge.
- **[M]** On BrowseComp, three factors explain 95% of the variance. Token use alone explains 80%.
- **[E]** A multi-agent run uses about 15 times the tokens of a chat. A single agent uses about 4 times.
- **[E]** A subagent brief needs four parts: an objective, an output format, guidance on tools and sources, and clear task boundaries.
- **[E] What did not work:** Short briefs. One subagent researched the 2021 chip crisis while two others duplicated work on 2025 supply chains.
- **[E]** Subagents write outputs to an external store and return a light reference. The post calls the alternative a "game of telephone".
- **[E]** The lead saves its plan to memory before the context reaches 200,000 tokens. It can start fresh subagents with a clean context and a hand-off.
- **[O]** A task where all agents need the same context, or with many dependencies, is "not a good fit for multi-agent systems today". Most coding tasks are in that group.

### Anthropic: effective context engineering [S6], 2025-09-29

- **[E] (one)** Recall drops as the context fills. The post names this "context rot" and says it "emerges across all models".
- **[E] (one)** Compaction in Claude Code keeps "architectural decisions, unresolved bugs, and implementation details" and the five most recently read files.
- **[E]** Aggressive compaction risks the "loss of subtle but critical context". The advice: first maximise recall in the compaction prompt, then cut.
- **[E] (seq)** Notes outside the context let an agent continue after a reset. The example is the Pokemon agent with a step count and a level target.
- **[E] (parent)** A subagent may use tens of thousands of tokens. It returns a condensed summary of "often 1,000-2,000 tokens".
- The post gives a fit for each method. Compaction fits long back-and-forth. Notes fit iterative work with milestones. Subagents fit parallel research.
- No measurement in the post.

### Anthropic: effective harnesses for long-running agents [S7], 2025-11-26

- **[E] (seq)** "Compaction isn't sufficient." Opus 4.5 in a loop across windows did not build a production-quality web application from a high-level prompt.
- **[E] What did not work:** The agent tried to build everything in one pass. It ran out of context mid-feature and left the work half-built and undocumented.
- **[E] What did not work:** A later session saw existing progress and declared the job done.
- **[E]** The fix has two prompts. An initializer session writes a feature list of over 200 items, a progress file, a start script and a first commit. Each later session does one feature.
- **[E]** A later session may change only the `passes` field of the feature list. The team chose JSON because the model overwrites it less than Markdown.
- **[E]** The progress file together with the git history is "the key insight" for a fast start.
- **[E]** A new session runs `pwd`, reads the git log and the progress file, reads the feature list, starts the server, and tests the basics before new work.
- **[E] What did not work:** The agent marked a feature complete after unit tests or `curl` only. Browser automation as a user improved the result.
- **[O]** Open question, per the post: it is "still unclear" whether one general agent or several roles work better.
- No measurement in the post.

### Anthropic: harness design for long-running application development [S8], 2026-03-24

- **[E] (seq)** A reset starts a fresh agent with a structured hand-off. Compaction keeps the same agent. Compaction "doesn't give the agent a clean slate".
- **[E]** Sonnet 4.5 stopped work early near its believed limit. The post names this "context anxiety". Compaction alone was not sufficient for that model, so resets were essential.
- **[E]** Opus 4.5 "largely removed" the behaviour. The team dropped the resets. With Opus 4.6 the team also dropped the sprint structure.
- **[E]** The hand-off artifact must hold "the previous agent's state and the next steps". The post gives no format.
- **[E] (peers by file)** Planner, generator and evaluator communicate through files. One agent writes a file. The other reads it and replies in a file.
- **[E]** Before each sprint the generator and the evaluator negotiate what "done" means, as testable behaviours. Sprint 3 had 27 criteria.
- **[E] What did not work:** Self-evaluation. Agents "reliably skew positive when grading their own work".
- **[E] What did not work:** Claude as a QA agent out of the box. It found real issues and then approved the work anyway.
- **[E] What did not work:** Removing most of the harness at once. The team then removed one part at a time.
- **[M, one case each]** A solo run took 20 minutes and $9, and the result did not respond to input. The full harness took 6 hours and $200. A later run took 3 hours 50 minutes and $124.70.
- **[O]** Each harness part encodes an assumption about what the model cannot do. The assumption expires with a new model.

### Anthropic: a C compiler with parallel agents [S9], 2026-02-05

- **[E] (peers)** 16 agents worked on one repository with no orchestrator. They used nearly 2,000 sessions in two weeks and about $20,000. The result is about 100,000 lines.
- **[E]** Agents claim a task with a lock file in git. They communicate through the repository only.
- **[E] (seq)** Each session starts in a fresh container with no context. Agents keep READMEs and progress files, and a list of failed approaches.
- **[E]** The verifier must be "nearly perfect", or the agents solve the wrong problem.
- **[E]** The test harness prints few lines, tags errors for `grep`, and offers a fast sample. The reasons are context pollution and no sense of time.
- **[E] What did not work:** One large task that every agent hit at once. The fix used GCC as an oracle to split the task by file.
- **[E] What did not work:** Late in the project, new features often broke existing ones. Stricter CI was the response.
- The human wrote the loop, the first prompt and the tests. The human did not supervise day to day.

### Anthropic: when to use multi-agent systems [S11], 2026-01-23

- **[E] (parent)** Multi-agent use costs 3 to 10 times the tokens of one agent on an equivalent task.
- **[E]** Three cases justify it: context pollution, parallel tasks, and specialisation of tools or focus.
- **[E] What did not work:** A split by role, such as planner, implementer, tester, reviewer. Each hand-off loses fidelity. In one experiment the agents spent more tokens on coordination than on work.
- **[E]** A split by context boundary works better than a split by type of work.
- **[E]** A verifier subagent needs the artifact, clear criteria and tools. It does not need the build history. Its failure is "early victory" after one or two passing tests.

### Anthropic: managed agents [S10], 2026-04-08

- **[E] (seq)** The session is an append-only event log outside the context window. A new harness instance wakes, reads the log, and resumes from the last event.
- **[O]** "Irreversible decisions to selectively retain or discard context can lead to failures." The log lets the harness read back what compaction removed.

### Cognition [S13] [S14] [S15]

- **[O] (parent, peers)** June 2025: "Share context, and share full agent traces, not just individual messages." And: "Actions carry implicit decisions, and conflicting decisions carry bad results."
- **[O]** June 2025: parallel subagents that decide without shared context conflict. The example is two halves of a game with different styles. No measurement.
- **[E]** June 2025: a dedicated model compresses history into "key details, events, and decisions". The post calls this "hard to get right".
- **[E] (one, seq)** September 2025: Sonnet 4.5 writes notes such as `SUMMARY.md` with no prompt. The notes were not thorough. They sometimes paraphrased the task and dropped details.
- **[E] What did not work:** Reliance on the model's own notes in place of Cognition's compaction. Performance fell and knowledge gaps appeared. The post gives no number for this effect.
- **[E]** April 2026: the 2025 view still holds for swarms of parallel writers. What works keeps writes in one thread while several agents add intelligence.
- **[E]** April 2026: a review agent works best when it shares no context with the coder beforehand. It sees the diff only. The coder filters the findings with its fuller context.
- **[E]** April 2026: a "smart friend" model gets a fork of the full context. It can send back an instruction, such as a file to read.
- **[E] What does not work, April 2026:** A manager that over-prescribes without deep context. Agents that "assume they share state with their children when they don't". Children that do not report findings by default.
- **[O]** April 2026: the open problems are "all communication problems". Arbitrary networks of agents are "mostly a distraction".
- **[M, product numbers, no method given]** The review agent finds 2 bugs per pull request on average. About 58% are severe.

### OpenAI [S19] [S20] [S46]

- **[E] (peers in sequence)** Agents SDK documents: after a handoff the new agent by default sees the entire prior conversation. An input filter can cut it. A beta option collapses the history into summary segments. No measurement.
- **[E] (seq)** Harness engineering post, 2026-02-11. The primary page did not load for this read. A secondary report (InfoQ, 2026-02-21) gives the content below.
- A small team shipped about a million lines in five months with no hand-written source code. Structured documents in the repository are the single source of truth. Linters and CI check them.
- The documents include maps, execution plans and design specifications. Humans define the environment, state intent and give structured feedback.
- **[E] (one)** Codex-Max announcement, November 2025, from a search listing only. The model compacts its session near the limit and continues in a fresh window. OpenAI reports internal runs of over 24 hours.

### Google [S21], 2025-12-04

- **[E] (parent, peers)** The ADK post treats context as "a compiled view over a richer stateful system". The sources are the session log, memory and artifacts.
- **[E]** Two patterns exist. In "agents as tools" the callee gets a focused prompt and no history. In a transfer the new agent continues with a view of the session.
- **[E]** On a transfer, ADK rewrites earlier assistant messages as narrative. The new agent then does not take another agent's actions as its own.
- **[O]** "Scope by default: Every model call and sub-agent sees the minimum context required."
- No measurement in the post.

### LangChain [S16], 2025-06-16

- **[O] (parent)** Cognition and Anthropic agree on two points despite their titles. Context engineering is critical. Systems that mainly read are easier than systems that write.
- **[O]** Conflicting writes cause worse failures than conflicting reads. No measurement.

### Manus [S17], 2025-07-18

- **[E] (one)** The file system is the external memory. Compression must be restorable: drop a page from the context and keep its URL.
- **[E] (one)** A typical task has about 50 tool calls. The agent rewrites a `todo.md` so that the goal stays in the recent context. The post presents this as a mechanism, with no measured result.
- **[E] What does not work:** Hiding errors from the context. Irreversible compression. Heavy few-shot patterns in repeated tasks.

### Cursor [S18], 2026-01-14

- **[E] (peers)** Flat peers with a shared file and locks failed. "Twenty agents would slow down to the effective throughput of two or three."
- **[E] What did not work:** No hierarchy. "With no hierarchy, agents became risk-averse." They made small safe changes and avoided hard tasks.
- **[E] What did not work:** An integrator role for quality and conflicts. It "created more bottlenecks than it solved".
- **[E] (parent)** What works: planners make tasks, workers do one task with no coordination, and a judge decides whether to continue. The next cycle starts fresh.
- **[E] (seq)** "We still need periodic fresh starts to combat drift and tunnel vision."
- **[E]** Runs lasted from one week to over three weeks. One project passed 1 million lines. The post gives no quality measurement.

## 3. Context compaction and summaries

### Side constraints under compaction, Wang and others [S23], July 2026

- **[M] (one)** The benchmark injects a user constraint stated once, such as "do not delete any emails until I confirm". It then compacts and tests retention and compliance.
- Across compactors, the average retention of the injected constraint is 17%.
- Retention is about 90% at 10,000 tokens and falls as the input grows. Two non-LLM compactors keep 0% at 100,000 tokens.
- On 126 constraints that occur naturally in coding sessions, no compactor keeps more than 28.6%.
- Of five constraint types, process constraints are kept least. Preference constraints are kept best, at 36% in the best case.
- A constraint placed closer to the compaction point survives more often. Strict wording helps. Repetition helps up to about 30 turns.
- Inbox experiment, 100 sessions. Before compaction, 0 sessions had an unauthorised deletion. After compaction, 30 did. In 28 of the 30, the summary had dropped the constraint.
- A restatement of the constraint in the first turn after compaction cut the violations from 30 to 13 of 100.
- A separate extractor keeps a registry of constraints and appends it to the summary. Retention rose from between 1.1% and 11.6% to between 90.3% and 95.1%.
- Limits: an LLM judges retention. Most compactors under test are open-weight models. One commercial model ranged from 6.7% to 98%.

### Factory: evaluating compression [S22], 2025-12-16

- **[M] (one)** Factory tested three summarisers on over 36,000 messages from real coding sessions. Four probes follow each compression: recall, artifact, continuation, decision. An LLM judge scores 0 to 5.
- Overall: Factory 3.70, Anthropic 3.44, OpenAI 3.35. All three remove about 99% of the tokens.
- The weakest dimension for all three is the artifact trail, the record of which files changed: 2.45, 2.33 and 2.19.
- Instruction following scores highest: 4.99, 4.95 and 4.92. This differs from the constraint result above. The two studies measure different things.
- Limits: the authors work at Factory. There is one judge model, no variance and no confidence interval. The session count is not stated.
- **[O]** Factory holds that a full rewrite of the summary on each compaction can drift. The page shows no data for that claim.

### LANTERN [S24], April 2026 preprint, one author

- **[M] (one)** Over half of specific facts are lost after a single compaction event. The test uses 94 conversations and 1,894 facts.
- Recovery of facts into the restored context: plain summarisation 63.1%, a MemGPT-style method 72.4%, an archive with retrieval 78.3%.
- Configuration facts have the highest miss rate, 30.8%.

### What does context compression cost an agent, Liu [S25], August 2026

- **[M] (one)** Task completion hides the cost. At 5 times compression, completion did not change in any of six comparisons. Retrieval calls rose in all six.
- For one model, completion went from 80% to 85% (not significant) while retrieval calls went from 21.0 to 63.9.
- In a second environment the effect did not appear. Abstract read only.

### The Complexity Trap, Lindenbauer and others [S26], August 2025

- **[M] (one)** On SWE-bench Verified, simple masking of old tool outputs matches LLM summaries on solve rate. Masking costs about half of the raw agent.
- A hybrid cuts cost a further 7% against masking and 11% against summaries. Abstract read only.

### Context rot, Chroma [S27], 2025-07-14

- **[M] (one)** 18 models were tested. Performance became less reliable as the input grew, in every experiment.
- On LongMemEval, every model scored higher on a focused prompt of about 300 tokens than on the full prompt of about 113,000 tokens.

### LLMs Get Lost in Multi-Turn Conversation, Laban and others [S28], May 2025

- **[M] (one)** 15 models, 6 tasks, over 200,000 simulated conversations. The same instruction given across turns scores 39% lower than given in one turn.
- Best-case ability drops about 16%. Unreliability rises about 112%. The loss is mostly unreliability.
- A recap of all user information at the end restores much of the loss: 59.1 to 76.6 for one model. A restatement at every turn restores less.
- Lower temperature does not fix it. Reasoning models degrade in the same way.
- The authors advise a new conversation with a consolidated instruction when a conversation derails.

### Work across a context reset: Handoff Debt [S29], June 2026, version 2 in August 2026

- **[M] (seq)** This is the only benchmark found that interrupts a coding agent and measures the successor. It uses 75 SWE-bench Verified tasks, 181 hand-off points and 2,172 takeover runs.
- The successor gets one of four views: the repository only, the raw trace, free summary notes, or structured notes with fixed fields.
- Solve rate against repository only: raw trace +6.1, +6.6 and +14.9 points for the three successor models. Summary notes +5.0, +1.7 and +9.4. Structured notes +4.4, +1.1 and +10.5.
- The raw-trace gain is significant for all three successors. The gain from notes is significant for one of three.
- Effort: the raw trace cuts the successor's events by 57% to 59%. Notes cut events by 20% to 46%. All views cut prompt tokens by 42% to 63%.
- With the repository only, the successor rebuilds the intent, reruns checks, and derives attempted fixes again.
- Three failures appear: a compact note drops an exact validation command, the successor trusts the predecessor's reading too much, and noise in a raw trace hides dead ends.
- Limits: small open models, one runtime, one run per view, one predecessor model. The paper has no uninterrupted baseline. Tests alone judge success.

## 4. Memory files and notes

- **[M] (seq)** Anthropic's memory tool with context editing improved an internal agentic search evaluation by 39% over the baseline. Context editing alone gave 29%. Token use fell 84% in a 100-turn evaluation [S12]. The evaluation set is internal.
- **[E] (seq)** The memory tool adds an instruction to the system prompt: "ASSUME INTERRUPTION: Your context window might be reset at any moment" [S32]. The agent must view the memory directory first.
- **[E] (seq)** The documented pattern for software work: an initializer session writes a progress log and a feature checklist. Each session reads them first and updates the log last [S32] [S7].
- **[E]** The same document says: mark a feature complete only after end-to-end verification. The reason is that the progress log must stay accurate.
- **[E]** What makes notes work, per the reports: a fixed structure, a single item of work per session, state that a test can check, and git as the record [S7] [S9] [S20].
- **[E]** What makes notes fail, per the reports: notes that paraphrase the task [S15], a note that drops an exact command [S29], a feature marked done with no real test [S7], and a successor that trusts the note too much [S29].
- **[M] (seq)** Notes against the raw trace: see Handoff Debt above. Notes gave the smaller gain.
- **[M] (one)** Evaluating AGENTS.md [S31], February 2026: repository context files do "not generally improve task success rates". They raise inference cost by over 20% on average.
- The same paper finds that agents follow the instructions in the files. Overviews of the repository did not help. Abstract read only.
- **[M] (seq)** Letta [S30], 2025-08-12: an agent with plain files and search tools scored 74.0% on LoCoMo. A specialised memory product reported 68.5%. Letta doubts that the benchmark means much.
- **[E] (parent)** Claude Code gives a subagent an optional memory directory. The first 200 lines or 25KB of its `MEMORY.md` load into the subagent's prompt [S33].
- Unverified leads, from search listings only: a 2026 preprint (MemConflict) reports that six memory systems seldom detect a stale fact beside its correction. Practitioner posts report memory files that hold contradictions after 15 to 20 sessions.

## 5. Communication between peer agents

### What the documents describe

- **(parent)** Claude Code subagent: "Each subagent starts with a fresh, isolated context window. It doesn't see your conversation history" [S33]. The parent writes a delegation message. The result returns as a summary.
- **(parent)** A fork is the exception. It inherits the parent conversation. A parent can also resume a subagent with its full history [S33].
- **(peers)** Claude Code agent teams are experimental. A lead, teammates, a shared task list and a mailbox form the team [S34].
- "The lead's conversation history does not carry over" to a teammate. The teammate gets the project context and the spawn prompt [S34].
- A task claim uses a file lock. Hooks can block a task from completion. A teammate's plan is approved on arrival by default, "without the lead reviewing it" [S34].
- Known limits, per the document: "teammates sometimes fail to mark tasks as completed", the lead can decide the team is done too early, and two teammates that edit one file overwrite each other [S34].
- **(peers)** Claude Code cross-session messaging: "A message is a piece of text one Claude writes to another, never the sender's conversation history or files" [S35].
- The receiver is told that the message came from another session and not from the user. The message cannot approve a permission or change configuration [S35].
- The document reports delivery states: delivered, held, refused. It defines no check that the receiver understood [S35].
- **(peers)** A2A version 1.0.0 defines an agent card, a task, a message, a part and an artifact. Agents do not share internal state, memory or tools [S36].
- A2A has an `INPUT_REQUIRED` state for a receiver that needs more input. The `SUBMITTED` state acknowledges receipt. No state confirms comprehension [S36].
- **(peers)** The OpenAI SDK passes the full history on a handoff by default [S19]. Google ADK rewrites the history so that the receiver knows who did what [S21].

### Is there a measured method by which one peer confirms that another understood?

- No source in this read measures a restatement by the receiver, or a test of the receiver, before the work starts.
- The closest measured item is AgentAsk [S4]: clarification questions at the hand-off give up to +4.69% accuracy.
- The second closest is from one context, not peers [S23]: the user restates the constraint after compaction, and violations fall from 30 to 13 of 100.
- MAST [S1] counts the opposite failure. An agent that does not ask for clarification is 6.80% of failures.
- Engineering reports describe three forms of agreement with no isolated measurement. A sprint contract fixes testable criteria before work [S8]. A reviewer gets the diff with no shared context [S14]. A helper model sends an instruction back to the sender [S14].
- Unverified lead, from a search listing only: a February 2026 paper proposes that agents certify shared meaning of terms by tests on shared events.

## 6. Goal drift and instruction decay

- **[M] (one)** Arike and others [S37], May 2025. A trading agent gets a goal in the system prompt and then meets pressure toward a competing goal.
- All four models drift to some degree. The best, Claude 3.5 Sonnet, kept near-perfect adherence past 90,000 tokens. GPT-4o mini drifted after 16 steps with no added pressure.
- Drift by inaction exceeds drift by action. The agent fails to undo what no longer serves the goal more often than it acts against the goal.
- A strong, explicit statement of the goal reduces drift under pressure (p < 0.05). It is not sufficient after a phase with a different instrumental goal.
- Token distance alone does not explain drift. Pattern-matching on the agent's own earlier actions has suggestive support.
- The authors say the environment is too simple for frontier models.
- **[M] (seq)** Inherited Goal Drift [S38], March 2026. A weaker agent drifts for 30 steps. A newer model then takes over the same trajectory.
- Without the inherited trajectory, all newer models show about zero drift. With the trajectory, several adopt the drift. Only GPT-5.1 stayed consistently resilient.
- This is the only measurement found of drift that crosses from one agent to the next. The text gives no per-model numbers outside the figures.
- **[M] (one)** Asymmetric Goal Drift in Coding Agents [S39], March 2026. Coding agents break a system-prompt constraint more often when the constraint opposes a value such as security. Drift grows with accumulated context. Abstract read only.
- **[M] (one)** Li and others [S40], 2024, older than 2025. Two chatbots show significant instruction drift within eight rounds. The authors link the drift to attention decay.
- **[M] (one)** Laban and others [S28]: see section 3. A wrong early assumption persists, and the model does not recover.
- **[M] (one)** Constraint loss at compaction [S23] is also an instruction decay. The cause there is the summary, not the length.
- **[E] (one)** Recitation of the goal in a todo file [S17]. Reminders at the start and the end of the prompt against early wrap-up [S15]. Neither report gives a measurement.
- **[E] (seq)** Fresh starts against "drift and tunnel vision" [S18]. No measurement.
- A January 2026 paper on "agent drift" in multi-agent systems [S41] rests on simulation and theory. It reports no measured runs.
- What restores the goal, with evidence: an explicit strong goal statement [S37], a recap of all user information [S28], a restated constraint after compaction [S23], a constraint registry appended to the summary [S23], and a new conversation [S28].

## 7. The human in the loop

- **[M]** Anthropic [S42], 2026-02-18. In Claude Code, the 99.9th percentile turn ran under 25 minutes in October 2025 and over 45 minutes in January 2026. The median turn is about 45 seconds.
- Inside Anthropic, human interventions per session fell from 5.4 to 3.3 between August and December 2025. Success on the hardest tasks doubled in the same period.
- Users with under 50 sessions use full auto-approve in about 20% of sessions. Users with 750 sessions use it in over 40%.
- Experienced users interrupt more: about 9% of turns against about 5% for new users. The source reads this as a move from approval of each step to monitoring.
- On the most complex tasks the agent stops to ask more than twice as often as on simple tasks. The agent's own stops rise faster than the human's interrupts.
- Limits: one vendor's models, a classifier that is the model itself, and a short period.
- **[M]** Anthropic [S43], 2025-12-02. In 200,000 internal transcripts, human turns per transcript fell from 6.2 to 4.1 between February and August 2025. The longest run of tool calls rose from 9.8 to 21.2.
- Most engineers in the survey (132 people) say they can fully delegate 0% to 20% of their work. They delegate what they can verify easily.
- **[M]** SWE-chat [S44], April 2026. Nearly 18,000 public sessions. Users push back in 50% of turns. 59% of agent code survives into a commit. In 41% of sessions the agent wrote almost all committed code. Abstract read only.
- **[M]** Khelifi and others [S45], MSR 2026. Humans intervened in 52.17% of agent pull requests against 83.59% of human ones. Each intervention cost more effort. Guidance took 58.02% of that effort.
- **[E]** What reduced steering, per the reports: a strong verifier or test oracle [S9] [S8], a feature list and a progress file [S7], documents in the repository as the system of record [S20], and newer models [S42] [S8].
- **[E]** Claude Code's document for agent teams advises the opposite of absence: "Letting a team run unattended for too long increases the risk of wasted effort" [S34].
- No source measures human steering per hand-off or per reset. The numbers are per session, per turn or per pull request.

## The points on which the sources agree

1. A receiver has only what is written to it. A vague brief or prompt fails. [S5] [S13] [S33] [S34] [S14]
2. A context degrades as it fills, and a long conversation becomes unreliable. [S27] [S28] [S6] [S14]
3. A summary is lossy, and the loss is specific. Exact items go first: constraints, file lists, commands, configuration facts. [S23] [S22] [S24] [S29] [S15]
4. Durable state outside the context carries long work: files, git, tests, an event log. [S7] [S9] [S10] [S17] [S20] [S21]
5. Parallel reading is easier than parallel writing. Conflicting writes are the costly failure. [S13] [S14] [S16] [S5] [S34] [S18]
6. An agent rates its own work too well and stops too early. A separate check with concrete criteria is needed. [S1] [S8] [S7] [S11] [S9]
7. More agents cost more tokens: 3 to 15 times. The gain depends on the task. [S5] [S11] [S3]
8. A fresh context helps when the old one is degraded. [S28] [S18] [S8] [S14]
9. Task completion alone hides the cost of a boundary. [S25] [S29]
10. Harness parts expire as models change. [S8] [S14] [S18]

## The points on which the sources disagree

1. **Full context or minimum context for the receiver.**
   - Full: Cognition 2025 says to share full traces [S13]. The OpenAI SDK passes the whole history by default [S19]. Handoff Debt measures the raw trace above notes [S29].
   - Minimum: Google ADK scopes to the minimum by default [S21]. Anthropic returns 1,000 to 2,000 tokens from a subagent [S6]. Cognition 2026 finds a reviewer works best with no shared context [S14].
   - The sides may differ by role. The cases for minimum context are checks and searches. The cases for full context are continued work. No source tests this split directly.
2. **Reset with a hand-off, or compaction in place.**
   - Reset: Anthropic found compaction insufficient for one model [S7] [S8]. Cursor still needs fresh starts [S18].
   - Compaction: Anthropic dropped resets with a newer model [S8]. OpenAI trains compaction into the model [S46]. Anthropic's managed agents keep the full log so that neither choice is final [S10].
3. **A summary by an LLM, or a simpler rule.**
   - Simple masking matches LLM summaries on solve rate at lower cost [S26].
   - A structured LLM summary scores above two others on probes [S22]. All LLM compactors drop most one-time constraints, and simple truncation drops them too [S23].
4. **Notes written by the agent.**
   - For: progress file and git are "the key insight" [S7]. Memory tool plus context editing gives +39% [S12]. Plain files score well on a memory benchmark [S30].
   - Against: the model's own notes were not thorough and performance fell [S15]. Notes gave a small, mostly non-significant gain against the raw trace [S29]. Context files did not raise task success [S31].
5. **A hierarchy or flat peers.**
   - Hierarchy: flat peers with locks failed at Cursor [S18]. Cognition prefers "map-reduce-and-manage" [S14]. Central coordination shows the lowest error amplification [S3].
   - Flat: 16 agents with lock files and no orchestrator built a compiler [S9]. That case had a near-perfect test oracle.
6. **A split by role.**
   - Against: planner, implementer, tester and reviewer lose fidelity at each hand-off [S11].
   - For: planner, generator and evaluator built full applications [S8]. Both sources are Anthropic. The second kept the evaluator only where the task exceeds the model.
7. **The cause: the system or the model.**
   - System: MAST holds that better models will not remove the failures [S1].
   - Model: newer models removed the need for resets and sprints [S8]. Newer models resist direct pressure yet inherit drift from a trajectory [S38].
8. **Does more agents mean better results.**
   - Yes for broad research: +90.2% [S5], +80.8% [S3].
   - No for sequential work: -39% to -70% [S3]. No above a 45% single-agent score [S3].

## The questions that no source measures

1. **Does the receiver understand the hand-off before it acts?** No source tests a restatement, a quiz or a first-step check between agents. This is the main gap.
2. Do reasons for decisions survive a boundary? Factory has a decision probe but reports no separate score for it [S22]. No other source measures rationale.
3. How does loss compound over many boundaries? Every measurement uses one compaction or one hand-off [S23] [S29]. Factory names drift over repeated compactions with no data [S22].
4. Which content of a note predicts the successor's success? Handoff Debt compares two note formats only [S29].
5. Does the successor keep the user's intent, as the user would judge it? Tests alone judge success in the hand-off study [S29].
6. How often is a note stale or wrong, and what does a wrong note cost against no note? Only an over-trust failure is described [S29].
7. Does a message between live peers change the receiver's outcome? The documents describe delivery only [S35] [S36].
8. How much human steering does one hand-off or one reset cost? The numbers are per session or per pull request [S42] [S45].
9. Do the hand-off results hold for frontier models and long tasks? The one benchmark uses small open models and tasks of up to four hours [S29].
10. Does a hand-off from a stronger to a weaker model, or the reverse, change the loss? One drift study covers weak to strong only [S38].

## Read these first

1. **Handoff Debt [S29].** The only controlled measurement of a successor agent under different hand-off views.
2. **Side constraints under compaction [S23].** The measurement of what a summary does to a constraint the user stated once, with a tested fix.
3. **MAST [S1].** The base rates for failure modes, with the hand-off and verification shares.
4. **Anthropic, effective harnesses [S7].** The fullest account of notes and files across fresh sessions, with the failures that led to each part.
5. **Anthropic, harness design [S8].** Reset against compaction, the sprint contract, and which parts a newer model made obsolete.
6. **Cognition, both posts [S13] [S14].** The strongest argument for shared context, and the same author's later list of what works.
7. **Towards a Science of Scaling Agent Systems [S3].** The only broad measurement of when more agents help or hurt.
8. **Laban and others [S28].** Why a long conversation becomes unreliable and why a consolidated restart helps.
9. **Inherited Goal Drift [S38].** The only measurement of drift that passes from one agent to the next.
10. **Anthropic, measuring agent autonomy [S42].** The best data on how much people steer, with its limits stated.

## Limits of this read

- The read took one sitting. Twelve sources were read as an abstract or a listing only. Each such item says so.
- The OpenAI harness post and the Codex-Max post did not load. Their items rest on a secondary report and a search listing.
- Several 2026 papers are preprints or workshop papers. Three have one author.
- Vendor posts report their own products. Factory compares itself with competitors.
- Tools in the read summarised long pages. A number may differ from the source by a version. Check a number against the source before reuse.

## Sources

Studies and benchmarks:

- [S1] Cemri and others. "Why Do Multi-Agent LLM Systems Fail?" arXiv 2503.13657. March 2025, version 3 October 2025. NeurIPS 2025. https://arxiv.org/abs/2503.13657
- [S2] Zhang and others. "Which Agent Causes Task Failures and When?" arXiv 2505.00212. April 2025. https://arxiv.org/abs/2505.00212
- [S3] Kim and others. "Towards a Science of Scaling Agent Systems." arXiv 2512.08296. December 2025, version 3 April 2026. https://arxiv.org/abs/2512.08296
- [S4] Lin and others. "AgentAsk: Multi-Agent Systems Need to Ask." arXiv 2510.07593. October 2025, version 2 January 2026. https://arxiv.org/abs/2510.07593
- [S23] Wang, Zhang, Lee, Baracaldo, Yang. "Lost in Context Compaction: When LLM Systems Drop Side Constraints." arXiv 2608.11242. July 2026, version 2 October 2026. https://arxiv.org/abs/2608.11242
- [S24] Subramani. "LANTERN: Layered Archival and Temporal Episodic Retrieval Network." arXiv 2606.05182. Preprint, April 2026. https://www.alphaxiv.org/abs/2606.05182
- [S25] Liu. "What Does Context Compression Cost an Agent?" arXiv 2608.16370. August 2026. https://arxiv.org/abs/2608.16370
- [S26] Lindenbauer and others. "The Complexity Trap." arXiv 2508.21433. August 2025. NeurIPS 2025 workshop. https://arxiv.org/abs/2508.21433
- [S27] Hong, Troynikov, Huber. "Context Rot." Chroma technical report. 2025-07-14. https://www.trychroma.com/research/context-rot
- [S28] Laban, Hayashi, Zhou, Neville. "LLMs Get Lost In Multi-Turn Conversation." arXiv 2505.06120. May 2025. https://arxiv.org/abs/2505.06120
- [S29] KC, Budathoki. "Handoff Debt: The Rediscovery Cost When Coding Agents Take Over Interrupted Tasks." arXiv 2606.02875. June 2026, version 2 August 2026. https://arxiv.org/abs/2606.02875
- [S31] Gloaguen and others. "Evaluating AGENTS.md." arXiv 2602.11988. February 2026, version 3 September 2026. https://arxiv.org/abs/2602.11988
- [S37] Arike, Donoway, Bartsch, Hobbhahn. "Technical Report: Evaluating Goal Drift in Language Model Agents." arXiv 2505.02709. May 2025. https://arxiv.org/abs/2505.02709
- [S38] Menon and others. "Inherited Goal Drift." arXiv 2603.03258. March 2026. ICLR 2026 workshop. https://arxiv.org/abs/2603.03258
- [S39] Saebo and others. "Asymmetric Goal Drift in Coding Agents Under Value Conflict." arXiv 2603.03456. March 2026. ICLR 2026 workshop. https://arxiv.org/abs/2603.03456
- [S40] Li and others. "Measuring and Controlling Instruction (In)Stability in Language Model Dialogs." arXiv 2402.10962. February 2024. COLM 2024. Older than 2025. https://arxiv.org/abs/2402.10962
- [S41] Rath. "Agent Drift." arXiv 2601.04170. January 2026. Simulation only. https://arxiv.org/abs/2601.04170
- [S44] Baumann and others. "SWE-chat: Coding Agent Interactions From Real Users in the Wild." arXiv 2604.20779. April 2026. COLM 2026. https://arxiv.org/abs/2604.20779
- [S45] Khelifi, Ouni, Khemaja. "Behind Agentic Pull Requests." MSR 2026 Mining Challenge. https://2026.msrconf.org/details/msr-2026-mining-challenge/26/

Engineering posts:

- [S5] Anthropic. "How we built our multi-agent research system." 2025-06-13. https://www.anthropic.com/engineering/multi-agent-research-system
- [S6] Anthropic. "Effective context engineering for AI agents." 2025-09-29. https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- [S7] Anthropic. "Effective harnesses for long-running agents." 2025-11-26. https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
- [S8] Anthropic. "Harness design for long-running application development." 2026-03-24. https://www.anthropic.com/engineering/harness-design-long-running-apps
- [S9] Anthropic. "Building a C compiler with a team of parallel Claudes." 2026-02-05. https://www.anthropic.com/engineering/building-c-compiler
- [S10] Anthropic. Managed agents post. 2026-04-08. https://www.anthropic.com/engineering/managed-agents
- [S11] Anthropic. "When to use multi-agent systems (and when not to)." 2026-01-23. https://claude.com/blog/building-multi-agent-systems-when-and-how-to-use-them
- [S12] Anthropic. Context management announcement. Autumn 2025, the fetch returned no date. https://claude.com/blog/context-management
- [S13] Cognition, Walden Yan. "Don't Build Multi-Agents." 2025-06-12. https://cognition.com/blog/dont-build-multi-agents
- [S14] Cognition, Walden Yan. "Multi-Agents: What's Actually Working." 2026-04-22. https://cognition.com/blog/multi-agents-working
- [S15] Cognition. "Rebuilding Devin for Claude Sonnet 4.5." 2025-09-29. https://cognition.com/blog/devin-sonnet-4-5-lessons-and-challenges
- [S16] LangChain, Harrison Chase. "How and when to build multi-agent systems." 2025-06-16. https://www.langchain.com/blog/how-and-when-to-build-multi-agent-systems
- [S17] Manus, Yichao Ji. "Context Engineering for AI Agents: Lessons from Building Manus." 2025-07-18. https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus
- [S18] Cursor, Wilson Lin. "Scaling long-running autonomous coding." 2026-01-14. https://cursor.com/blog/scaling-agents
- [S20] OpenAI, Ryan Lopopolo. "Harness engineering: leveraging Codex in an agent-first world." 2026-02-11. Not read, the page returned an error. https://openai.com/index/harness-engineering/ Secondary report read: https://www.infoq.com/news/2026/02/openai-harness-engineering-codex
- [S21] Google, Hangfei Lin. "Architecting efficient context-aware multi-agent framework for production." 2025-12-04. https://developers.googleblog.com/architecting-efficient-context-aware-multi-agent-framework-for-production/
- [S22] Factory. "Evaluating Context Compression for AI Agents." 2025-12-16. https://factory.com/news/evaluating-compression
- [S30] Letta. "Benchmarking AI Agent Memory: Is a Filesystem All You Need?" 2025-08-12. https://www.letta.com/blog/benchmarking-ai-agent-memory
- [S42] Anthropic. "Measuring AI agent autonomy in practice." 2026-02-18. https://www.anthropic.com/research/measuring-agent-autonomy
- [S43] Anthropic. "How AI is transforming work at Anthropic." 2025-12-02. https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic
- [S46] OpenAI. GPT-5.1-Codex-Max announcement. November 2025. Not read, known from a search listing. https://openai.com/index/gpt-5-1-codex-max/

Documentation, read on 2026-11-10:

- [S19] OpenAI Agents SDK. Handoffs. https://openai.github.io/openai-agents-python/handoffs/
- [S32] Claude Developer Platform. Memory tool. https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool
- [S33] Claude Code. Subagents. https://code.claude.com/docs/en/sub-agents
- [S34] Claude Code. Agent teams. https://code.claude.com/docs/en/agent-teams
- [S35] Claude Code. Cross-session messaging. https://code.claude.com/docs/en/cross-session-messaging
- [S36] A2A protocol specification, version 1.0.0. https://a2a-protocol.org/latest/specification/
