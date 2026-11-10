# Boundary theory read, 2026-11-10

## Result first

- The second mind holds the goal only if seven conditions hold. Part B lists the seven conditions.
- No check confirms the conditions for certain. Three separate results give that limit.
- The sender's confidence and the receiver's "I understand" are not evidence. Measurements show that both are poorly calibrated.
- The strongest evidence is correct action on a case that the record did not cover, judged by a mind that knows the goal.
- Each stronger check uses more time of the party that has the least time. Theory moves that cost. Theory does not remove it.
- The main open problem is the stop rule. No theory says how much evidence is enough before the cases that matter occur.

## How to read this page

The question: one mind works toward a goal, stops and keeps nothing. A second mind with no shared memory must continue. What must be true, and how can anyone know?

This page uses four words with one meaning each.

- The sender is the first mind. The receiver is the second mind.
- The third party knows the goal and has little time.
- The record is all written material that the sender leaves.

Each statement carries one of two marks.

- `(sourced: author year, grade)` means that the statement comes from the named source. The URL is in the source list.
- `(derived)` means that the statement is this read's own reasoning from the sourced statements.

The grade shows how this read reached the source.

- P: this read opened the primary text and found the statement there.
- A: this read saw the abstract or the publisher's record only.
- S: this read saw a secondary summary only.
- R: this read did not open the source. The statement comes from prior knowledge of the source. Treat the statement as not verified.

This page fits no project and recommends no design.

## Part A. The results, by body of theory

### A1. Communication theory

- Shannon defines the engineering problem as the reproduction of a message at another point. He states that the "semantic aspects of communication are irrelevant to the engineering problem". (sourced: Shannon 1948, P)
- Weaver names three levels. Level A, technical: how accurately do the symbols arrive? Level B, semantic: does the receiver interpret the meaning that the sender intended? Level C, effectiveness: does the received meaning lead to "the desired conduct"? (sourced: Weaver 1949, P)
- Weaver states a limit at level B. If Mr. X possibly does not understand Mr. Y, more talk by Mr. Y cannot "completely" clarify the situation "in any finite time". (sourced: Weaver 1949, P)
- Weaver gives the reason. "Do you now understand me?" answered by "Certainly I do" is "not necessarily a certification that understanding has been achieved". Mr. X possibly did not understand the question. (sourced: Weaver 1949, P)
- Weaver says that explanations reduce the difficulty "to a tolerable size, but never completely eliminated". An explanation works only in language that "has previously been made reasonably clear by usage". (sourced: Weaver 1949, P)
- Weaver states that communication "either affects conduct or is without any discernible and provable effect at all". (sourced: Weaver 1949, P)
- Each level needs the level below it. A sender can verify level A to any error rate it pays for, with an echo or a checksum. (derived)
- A sender can test level B only with more messages, and each of those messages has the same level B problem. (derived)
- A sender can observe level C only as conduct, after the fact, on a finite number of cases. (derived)

### A2. Grounding and common ground

- Clark and Brennan define the grounding criterion. The partners "mutually believe that the partners have understood what the contributor meant to a criterion sufficient for current purposes". They add that "understanding can never be perfect". (sourced: Clark and Brennan 1991, P)
- A contribution has two phases. In the presentation phase, A presents an utterance. In the acceptance phase, B gives evidence that B believes B understands. No contribution exists until both phases end. (sourced: Clark and Schaefer 1989, P)
- Clark and Schaefer list five types of evidence, "graded roughly from weakest to strongest": continued attention, start of the relevant next contribution, acknowledgement, demonstration, and verbatim display. (sourced: Clark and Schaefer 1989, P)
- The same paper separates two things. A paraphrase shows what B understands. A verbatim repetition shows what B heard. (sourced: Clark and Schaefer 1989, P)
- The need for evidence grows with the stakes: "the more complicated A's presentation, or the more demanding the current purpose, the more evidence should be needed". (sourced: Clark and Schaefer 1989, P)
- The absence of an objection is not enough. With negative evidence only, "we would often accept information we had little justification for accepting". People look for positive evidence. (sourced: Clark and Brennan 1991, P)
- Positive evidence leads to a regress, because each reply is a new presentation that needs its own acceptance. People stop the regress by convention. Each acceptance needs weaker evidence than the item it accepts. (sourced: Clark and Schaefer 1989, P)
- Least collaborative effort: the partners minimise their combined effort, not the speaker's effort alone. A speaker often presents a rough utterance and lets the partner help to repair it. (sourced: Clark and Brennan 1991, P)
- A medium has up to eight properties: copresence, visibility, audibility, cotemporality, simultaneity, sequentiality, reviewability and revisability. Letters and electronic mail have only the last two. (sourced: Clark and Brennan 1991, P)
- Grounding has eleven costs. The speaker pays formulation and production. The addressee pays reception and understanding. Both pay the other seven: start-up, delay, asynchrony, speaker change, display, fault and repair. (sourced: Clark and Brennan 1991, P)
- In a medium that is not cotemporal, repairs by the other party "become very costly indeed". The writer then revises before sending. The reader must "imagine appropriate contexts for both the sender and the message". (sourced: Clark and Brennan 1991, P)
- Mutual knowledge needs an endless chain of checks in principle. People replace the chain with evidence of copresence: the same place, the same earlier talk, or the same community. (sourced: Clark and Marshall 1981, S)

### A3. Distributed systems

- Two generals can win only if both march. Their messengers can get lost. Gray proves that "no fixed length protocol exists". The last messenger of the shortest protocol can get lost, so the protocol is not the shortest. (sourced: Gray 1978, P)
- Halpern and Moses give the general result. A coordinated attack needs common knowledge. They show that "in a system in which communication is not guaranteed, common knowledge is not attainable". (sourced: Halpern and Moses 1990, P)
- Any finite depth is reachable: A knows that B knows that A knows, to any level. Common knowledge is not reachable. For a simultaneous act, "nothing less will do". (sourced: Halpern and Moses 1990, P)
- A fact can be common knowledge if the fact is common knowledge without communication. The example is a global clock that all parties can read. (sourced: Halpern and Moses 1990, P)
- A weaker aim is reachable. A protocol can make the second party act "with high probability". (sourced: Halpern and Moses 1990, P)
- The end-to-end argument: a delivery acknowledgement is not what the application needs. "What the application wants to know is whether or not the target host acted on the message." Only the target application can send that acknowledgement: "I did it", or "I didn't". (sourced: Saltzer, Reed and Clark 1984, P)
- Reliability inside the channel reduces the number of retries. It "has no effect on inevitability or correctness of the outcome". The end points must still check. (sourced: Saltzer, Reed and Clark 1984, P)
- The authors show that "no completely asynchronous consensus protocol can tolerate even a single unannounced process death". The result holds even when every message arrives exactly once. The parties cannot tell a dead process from a slow process. (sourced: Fischer, Lynch and Paterson 1985, P)
- A sender with no reply cannot tell a lost message from a lost reply. The safe act is to send again. The receiver must then make a repeated message harmless. That property is idempotence. (sourced: Helland 2012, A and S)
- Replicas give the same output if they start in the same state and run the same requests in the same order. The condition is that each command is deterministic. (sourced: Schneider 1990, P)
- Recovery has two forms. A checkpoint copies the state. A log replays the events. Replay rebuilds the state only if the log holds every non-deterministic event in the original order. (sourced: Elnozahy and others 2002, A)
- A different mind is not a deterministic copy of the first mind. A replay of the first mind's log does not rebuild the first mind's state in the second mind. (derived)

### A4. Knowledge that resists writing

- Polanyi: "We can know more than we can tell." A person recognises one face among thousands and cannot say how. (sourced: Polanyi 1966, S)
- Ryle: knowing how is not a set of known statements. To apply a rule is itself an act that a person does well or badly, so rules alone lead to a regress. (sourced: Ryle 1945, S)
- Collins followed the laboratories that tried to build a TEA laser. He reports that "no-one to whom I have spoken has succeeded in building a TEA laser using written sources" only. (sourced: Collins 1974, P)
- In that case the test of transfer was the device. A working laser made the laboratory wall smoke. No person could judge the transfer from the documents. (sourced: Collins 1974, P and S)
- The curse of knowledge: "Better-informed agents are unable to ignore private information" when they predict the judgement of less-informed agents. (sourced: Camerer, Loewenstein and Weber 1989, P)
- In the same experiments, "feedback alone has little effect". Market forces reduce the size of the curse "by approximately 50 percent". (sourced: Camerer, Loewenstein and Weber 1989, P)
- Tappers of well-known songs predicted that listeners would name half of the songs. Listeners named 3 of 120, which is 2.5%. (sourced: Newton 1990, S, by Heath and Heath 2006)
- Speakers of ambiguous sentences expected to be understood more often than they were. Overhearers who knew the intended meaning did not make the same error. (sourced: Keysar and Henly 2002, A)
- Writers of electronic mail were too confident that readers would get their tone. The study attributes the error to egocentrism. (sourced: Kruger and others 2005, A)
- Experts predicted the time and the errors of novices too low. Attempts to remove the bias mostly failed. (sourced: Hinds 1999, S)
- The illusion of explanatory depth: people rate their understanding of a device, then try to explain the device, then rate again. In pooled data the mean fell from 3.89 to 3.10 to 2.49 on a 7-point scale. (sourced: Rozenblit and Keil 2002, P)
- The fall is large for explanations, small for facts, and absent for procedures and stories. One cause is that people confuse what they can read from the visible object with what they hold. (sourced: Rozenblit and Keil 2002, P)
- A later study reduced the effect with a more specific first question. Part of the fall can come from an unclear first rating. (sourced: Silk-Eglit and Kurtz 2011, P)

### A5. Shared mental models and team cognition

- Teams coordinate without talk when the members hold compatible models of the equipment, the task, the team's way to interact, and each other. (sourced: Cannon-Bowers, Salas and Converse 1993, S)
- In 56 two-person teams in a flight simulator, similar task models and similar team models both related to better team process and performance. (sourced: Mathieu and others 2000, A)
- Transactive memory: a group stores knowledge in its members, plus a directory of who knows what. Groups trained together did better than groups whose members trained apart. (sourced: Wegner 1987, S, and Liang, Moreland and Argote 1995, S)
- Distributed cognition: the unit that remembers is the system of people and artefacts. "Speed bugs do not help pilots remember speeds; rather, they are part of the process by which the cockpit system remembers speeds." (sourced: Hutchins 1995, S)
- Situation awareness has three levels: perception of the elements, comprehension of their meaning, and projection of their near future. (sourced: Endsley 1995, S)
- One measure stops the task and asks questions with known answers. A second measure asks for a self-rating. One study reports that the self-rating followed confidence and did not correlate with the first measure. (sourced: Endsley and others 1998, S, not verified in the full text)
- Patterson and others observed handoffs in mission control, nuclear power, rail dispatch and ambulance dispatch. Every observed update was verbal, face to face and interactive. (sourced: Patterson and others 2004, P)
- The 21 strategies include: the incoming person assesses the current state before the update, the incoming person raises topics, the transfer of responsibility is unambiguous, and the outgoing person oversees the first work. (sourced: Patterson and others 2004, P)
- Read-back was "not observed during handoff updates" in any of the four settings. The settings used the other effectiveness strategies although those strategies "likely reduced the efficiency of the update". (sourced: Patterson and others 2004, P)
- A handoff also has a benefit. The incoming person "has a fresh perspective", which helps to detect fixation errors. In one set of 16 handoffs, 8 of 75 questions served to detect errors. (sourced: Patterson and others 2004, P)
- In a command simulation, company commanders matched their battalion commander's intent in 34% of 32 episodes. Another account of the same study gives 17 of 32. (sourced: Shattuck and Woods 2000, A, figures conflict)
- A structured handoff programme in nine hospitals reduced medical errors by 23% and preventable adverse events by 30%. The oral handoff took 2.4 minutes per patient before and 2.5 after. (sourced: Starmer and others 2014, A)

### A6. Goals and intent

- Each act has many correct descriptions. Low-level descriptions say how. High-level descriptions say why. People move to a lower level when the act becomes difficult. (sourced: Vallacher and Wegner 1987, A)
- A work system is a hierarchy of means and ends. The level above a function gives its reason. The level below gives its means. (sourced: Rasmussen 1985, S)
- Goals are not a stack that keeps itself. A suspended goal decays under newer goals. The goal returns only when a cue primes it. (sourced: Altmann and Trafton 2002, P)
- An agent divides its attention between tasks. A reward on one measured task causes "some reallocation of attention away from other tasks". (sourced: Holmstrom and Milgrom 1991, P)
- They find that "the desirability of providing incentives for any one activity decreases with the difficulty of measuring performance in any other activities". A fixed wage with no measure can be the best contract. (sourced: Holmstrom and Milgrom 1991, P)
- Organisations often reward one behaviour and hope for a different behaviour. (sourced: Kerr 1975, S)
- Goodhart: a statistical regularity tends to collapse when someone uses it for control. Strathern: "When a measure becomes a target, it ceases to be a good measure." Campbell: a social indicator used for decisions becomes subject to "corruption pressures". (sourced: Goodhart 1975, S, Strathern 1997, S, and Campbell 1979, S)
- A contract cannot list every future case. The party that holds the remaining rights decides the cases that the contract does not list. (sourced: Grossman and Hart 1986, R)
- One task list fits more than one goal, because each task has more than one "why" above it. (derived)
- A measure can cross the boundary as a number or a test. The goal crosses only as an understanding. If only the measure crosses, the receiver's work serves the measure. (derived)

### A7. Tests of understanding in education

- The revised taxonomy has six levels: remember, understand, apply, analyse, evaluate and create. Retention tests the first level. Transfer needs the other five. (sourced: Anderson and Krathwohl 2001, S, and Mayer 2002, A)
- Rote learning means that the learner retains the material and cannot use it on a new problem. (sourced: Mayer 2002, A)
- People read a story with a solution. About 30% then used the solution on a new problem without a hint. About 80% used the solution after a hint. The baseline was about 10%. (sourced: Gick and Holyoak 1980 and 1983, S)
- The limit in that work was to notice that the old knowledge applies. The knowledge was present. (sourced: Gick and Holyoak 1983, S)
- Researchers do not agree on what far transfer is. One taxonomy sorts transfer by content and by context to make studies comparable. (sourced: Barnett and Ceci 2002, A)
- Repeated tests gave better transfer than repeated study. On inference questions in a new domain the scores were 68% and 44%. (sourced: Butler 2010, S)
- Readers judge their own understanding of a text poorly. The mean correlation between the judgement and the test score is about .27. (sourced: Maki 1998, S, and Dunlosky and Lipko 2007, S)
- Physicians checked recall or comprehension for 15 of 124 new concepts, which is 12%. Patients whose physician checked had better blood sugar control. The visits were not longer. (sourced: Schillinger and others 2003, A)
- A review found a positive effect of teach-back in 19 of 20 studies. (sourced: Talevski and others 2020, A)
- Read-back of telephoned laboratory results found 29 errors in 822 calls, which is 3.5%. (sourced: Barenfanger and others 2004, A)

### A8. Memory, identity and records

- Otto has Alzheimer's disease and uses a notebook. Clark and Chalmers argue that the notebook holds Otto's beliefs, because it has the same function as memory. (sourced: Clark and Chalmers 1998, P)
- They give four conditions. The notebook is a constant in Otto's life. The information is directly available. Otto "automatically endorses it". Otto consciously endorsed it at some time in the past. They call the fourth condition arguable. (sourced: Clark and Chalmers 1998, P)
- Twin Otto wrote a wrong address in his notebook. He believes the wrong address and walks to the wrong street. (sourced: Clark and Chalmers 1998, P)
- Clive Wearing has severe amnesia and kept a journal. He wrote that he was awake for the first time, then crossed out the earlier entries. He did not accept his own writing as his own. (sourced: Sacks 2007, P)
- A pager that sent timed prompts helped more than 80% of the people who completed a 16-week trial. In one subgroup the rate of completed tasks went from 47% to 72%. (sourced: Wilson and others 2001, A and S)
- A record functions as memory only when the reader endorses it. A record that the reader endorses without a check also carries the writer's errors. (derived)
- A prompt that arrives at the correct moment did what a stored note did not. Availability of a record is not the same as its use at the moment of need. (derived, from Wilson 2001 and Altmann and Trafton 2002)

## Part B. The smallest set of conditions

All of part B is derived. Each line names the sourced results that it uses.

### B0. What "holds the goal" means

- The receiver holds the goal when it chooses what the goal requires, on a case that neither mind met before. (derived, from Weaver's level C and Mayer's transfer)
- A receiver that can repeat the record does not yet hold the goal. A receiver that finishes the listed tasks does not yet hold the goal. (derived, from Mayer 2002 and Holmstrom and Milgrom 1991)

### B1. Delivery

- Condition: the record reaches the receiver complete, and the receiver reads it. (derived)
- Why: Weaver's levels B and C stand on level A. (derived)
- When absent: the receiver acts on a part of the record. No party knows which part is missing. (derived)
- Check: an echo, a checksum, or a read-back of the exact items. Read-back found errors in 3.5% of calls. (derived, from Barenfanger 2004)
- Limit: the sender can know that the record arrived. The two minds cannot both know that both know, over an unreliable channel. (derived, from Halpern and Moses 1990)
- Limit: delivery is not reading, and reading is not action. Only later conduct shows the last two. (derived, from Saltzer, Reed and Clark 1984)

### B2. Shared code

- Condition: the words, the names and the references in the record mean the same thing to the receiver as to the sender. (derived)
- Why: the record points at things that the sender saw. The receiver must "imagine appropriate contexts" for the writer. (derived, from Clark and Brennan 1991)
- When absent: the receiver builds a different meaning that is still coherent. Each sentence reads well, so no party sees an error. (derived)
- Check: the receiver restates the record in its own words. The receiver points at the thing that each name refers to. A new reader marks each term that it had to guess. (derived)
- Limit: no check confirms this condition for certain. Each check is a new message with the same problem. Checks make the problem smaller. (derived, from Weaver 1949)

### B3. The goal above the tasks

- Condition: the receiver has the reason for the work, the test for "done", and the limits that the work must not break. (derived)
- Why: a task list is a set of means. More than one goal fits the same list. The first case that the list does not cover forces a choice. (derived, from Vallacher and Wegner 1987 and Grossman and Hart 1986)
- When absent: the receiver completes the tasks and stops, or continues the tasks after they stop serving the goal. At a fork the receiver chooses the easier path. (derived)
- When absent and a measure came with the tasks: the receiver serves the measure. (derived, from Goodhart 1975 and Holmstrom and Milgrom 1991)
- Check: remove the task list and ask for the next step and its reason. Ask which result ends the work. Ask what the receiver refuses to do although the measure would pass. (derived)
- Check: compare each answer with the answer of a mind that knows the goal. In one study such a comparison matched in 34% of episodes. (derived, from Shattuck and Woods 2000)
- Limit: no check confirms this condition for certain. A finite set of answers fits more than one goal. The judge must hold the goal. (derived)

### B4. Current state

- Condition: the receiver has a correct picture of the work now. The picture covers the completed parts, the parts in progress, the rejected attempts, and what occurs next if nobody acts. (derived, from Endsley 1995)
- Why: a correct goal with a wrong state gives a wrong act. An "incorrect or incomplete model of the system's state" is the first named cost of a failed handoff. (derived, from Patterson and others 2004)
- When absent: the receiver repeats completed work, undoes it, repeats a rejected attempt, or continues a half-completed step. (derived)
- Check: this condition is the easiest to check, because most of the state is in the world. Stop and ask questions with known answers. (derived, from Endsley 1995)
- Check: the receiver looks at the world itself, then compares its picture with the sender's summary. A difference shows an error in one of the two. (derived, from Patterson and others 2004)
- Limit: the rejected attempts and their reasons exist only in the record. The sender's summary carries the sender's blind spots and errors. (derived, from Camerer and others 1989 and Clark and Chalmers 1998)
- Limit: a step that was in progress at the stop has an unknown result. The receiver must be able to repeat the step without harm. (derived, from Helland 2012)

### B5. The unwritten part

- Condition: the receiver has the skills and the distinctions that the sender used and did not state. (derived)
- Why: the record holds what the sender could tell and believed necessary to tell. The curse of knowledge removes the items that seem obvious to the sender. (derived, from Polanyi 1966 and Camerer and others 1989)
- When absent: the receiver follows the record correctly and the work fails with no visible cause. The receiver can also feel that it understands. (derived, from Collins 1974 and Rozenblit and Keil 2002)
- Check: only performance on a real part of the work shows this condition. A question does not. The receiver does not know what it lacks, and the sender does not know what it omitted. (derived)
- Limit: no check confirms this condition before the work. The evidence grows only with practice and feedback. (derived, from Collins 1974)
- This condition can hold in three ways. The receiver had the same training. The receiver rebuilds the skill by practice with feedback. The two minds work together for a period. (derived)

### B6. Ownership

- Condition: the receiver takes the goal as its own reason to act. All parties agree which mind is responsible from which moment. (derived)
- Why: a record functions as belief only if the reader endorses it. An agent with a different aim uses the gaps in the record. (derived, from Clark and Chalmers 1998 and Holmstrom and Milgrom 1991)
- When the moment is unclear: no mind acts, or two minds act on the same work. The transfer of responsibility is a coordinated act between two parties. (derived, from Gray 1978 and Patterson and others 2004)
- When the receiver does not adopt the goal: the receiver treats the record as orders and does the minimum that passes. Or the receiver distrusts the record and starts again. (derived, from Sacks 2007)
- Check for the moment: one event in one place that all parties can read. Messages alone cannot give the two minds common knowledge of the moment. (derived, from Halpern and Moses 1990)
- Check for adoption: observe what the receiver does when the goal and the easy path differ, and when no party checks. (derived)
- Limit: no check confirms adoption for certain. Adoption shows only in conduct across time. (derived)

### B7. Known gaps and a path to repair

- Condition: the receiver can tell what it does not know. The receiver can reach a source that knows: the sender while the sender runs, the third party, or feedback from the world. (derived)
- Why: conditions B2, B3 and B5 never hold completely, because "understanding can never be perfect". Errors exist at the moment of transfer. (derived, from Clark and Brennan 1991)
- Why: a record with no reply is a presentation phase with no acceptance phase. (derived, from Clark and Schaefer 1989)
- When absent: the errors stay and grow, because "faults tend to snowball". The receiver is confident and wrong. (derived, from Clark and Brennan 1991 and Dunlosky and Lipko 2007)
- Check: ask the receiver for its open questions and its least certain points. Count the repairs that occurred. Verify that the channel carried one real question and one real answer. (derived)
- Limit: zero questions is negative evidence only. It does not show that the receiver understood. (derived, from Clark and Brennan 1991)

### B8. Why the set is the smallest

- Each condition can fail while the other six hold. (derived)
- B3 without B4 gives a correct aim from a wrong position. B4 without B3 gives a correct position and no aim. (derived)
- B3 and B4 without B5 give a correct plan that the receiver cannot do. (derived)
- All of B1 to B5 without B6 give a capable mind that serves a different aim. (derived)
- All of B1 to B6 without B7 give a correct start that drifts, because no error at transfer gets a repair. (derived)

### B9. The conditions that no check confirms for certain

- B2, B3, B5 and the adoption part of B6 are states inside the receiver. No check confirms them for certain. (derived)
- Reason 1, the regress: each piece of evidence is a message that needs interpretation. People stop the regress by convention, not by proof. (derived, from Weaver 1949 and Clark and Schaefer 1989)
- Reason 2, the channel: common knowledge is not reachable over a channel that can lose messages. (derived, from Halpern and Moses 1990)
- Reason 3, finite tests: the goal covers cases that nobody foresaw. A finite set of probes cannot cover those cases. (derived, from Gick and Holyoak 1983 and Grossman and Hart 1986)
- Reason 4, the known test: a check that the receiver knows and is rewarded on stops measuring the condition. (derived, from Goodhart 1975)
- B1 and B4 are different. An observer can check them against the world to a high probability. (derived)

## Part C. Evidence that a receiver understood, weakest first

All ranks are derived. Each line names its sources.

- Not evidence: the sender's belief that the record is clear. Senders overestimate, and they cannot ignore what they know. (derived, from Camerer and others 1989, Newton 1990 and Keysar and Henly 2002)
- Rank 1, silence. No objection is negative evidence only. (derived, from Clark and Brennan 1991)
- Rank 2, a delivery receipt. The receipt shows level A and says nothing about action. (derived, from Saltzer, Reed and Clark 1984)
- Rank 3, the receiver continues to attend, or starts work. This is the weakest positive evidence in conversation. (derived, from Clark and Schaefer 1989)
- Rank 4, the receiver says "I understand". Weaver rejects this as a certification. Self-judged understanding correlates about .27 with test scores. (derived, from Weaver 1949 and Dunlosky and Lipko 2007)
- Rank 5, a verbatim read-back. It shows what the receiver received. It is strong evidence for exact items and weak evidence for meaning. (derived, from Clark and Schaefer 1989 and Barenfanger 2004)
- Rank 6, a restatement in the receiver's own words. It shows level B for the stated content. A receiver can produce it from the record with no ability to use it. (derived, from Schillinger 2003 and Mayer 2002)
- Rank 7, questions from the receiver that find a gap or an error in the record. Only a model of the work produces an expectation that the record can fail. (derived, from Patterson and others 2004)
- Rank 8, an explanation of the reason for each part. The attempt to explain shows gaps that a self-rating hides. (derived, from Rozenblit and Keil 2002)
- Rank 9, a prediction on a new case, compared with the answer of a mind that knows the goal. This is a transfer test and a test of projection. (derived, from Mayer 2002, Endsley 1995 and Shattuck and Woods 2000)
- Rank 10, correct action on a real case that the record did not cover, judged by a mind that knows the goal. This is level C, and the end-to-end "I did it". (derived, from Weaver 1949 and Saltzer, Reed and Clark 1984)
- Rank 11, correct action across many different cases, with the receiver's own errors found and repaired, where the receiver did not know the check. This rank is the strongest and is still not proof. (derived, from Butler 2010 and Goodhart 1975)
- Each rank falls when the receiver knows the check before the check and gains from a pass. (derived, from Goodhart 1975 and Holmstrom and Milgrom 1991)
- Ranks 1 to 6 need no judge who holds the goal. Ranks 9 to 11 need one. That need is the main cost. (derived)

## Part D. The costs

All of part D is derived. Each line names its sources.

| Item | Sender pays | Receiver pays | Third party pays |
|---|---|---|---|
| B1 delivery | Small. A send and a wait for the echo. | Small. An echo. | None. |
| B2 shared code | Formulation: definitions, plain names, revision. | Understanding: must rebuild the context. | Time to settle a term that the two minds read differently. |
| B3 goal above tasks | Must state reasons, the test for done, the limits. The sender often holds these without words. | Must rebuild the reason for each task. | Highest. Only the third party can confirm the goal when the sender is gone. |
| B4 current state | A summary, made while capacity remains. | A look at the world of its own, plus the comparison. | None, if the state is in the world. |
| B5 unwritten part | Cannot pay alone. The sender does not see what it omits. | Practice time with feedback. | Feedback on the first real work, if no other source exists. |
| B6 ownership | Must stop cleanly and say so. | Must accept responsibility for errors that it inherits. | One act: to name the holder where all can read it. |
| B7 repair path | Must stay reachable, which uses the end of its capacity. | Must ask, and must admit gaps. | Answers to the questions that only it can answer. |
| Ranks 1 to 6 | Low. | Low. | None. |
| Ranks 7 to 8 | Answers, while the sender runs. | Moderate. Must build a model before it speaks. | Low. |
| Ranks 9 to 11 | Can write probe cases. Cannot judge them after it stops. | Real work under observation. | High. Must judge, or must name a judge that holds the goal. |

Costs that theory says no party can avoid:

- Certainty has no finite price. No protocol of fixed length gives it. Each real transfer stops at "a criterion sufficient for current purposes". (derived, from Gray 1978 and Clark and Brennan 1991)
- The total cost of grounding moves between parties and does not go to zero. A medium with no fast reply moves the cost to the writer before sending, or to the reader later. (derived, from Clark and Brennan 1991)
- After the sender stops, each repair that needs the sender's knowledge falls on the receiver and the third party. (derived)
- More effort by the sender alone does not find the gaps in the record. Feedback alone had little effect on the curse of knowledge. A different reader must find the gaps. (derived, from Camerer and others 1989 and Hinds 1999)
- Skill moves by practice and contact, not by more text. (derived, from Collins 1974)
- A judge of the strong ranks must hold the goal. If only the third party holds the goal, the strong ranks use the third party's time. (derived)
- A safe takeover of a half-completed step costs repeated work. The other choice is a step that possibly never completes. (derived, from Helland 2012 and Fischer, Lynch and Paterson 1985)
- A checkpoint costs the sender a summary and loses the reasons. A log costs the receiver reading time and does not rebuild the sender's state. (derived, from Elnozahy and others 2002 and Schneider 1990)

Costs that the measurements show can be small:

- A fixed structure for the handoff reduced errors and did not make the handoff longer. (derived, from Starmer and others 2014)
- A check of the listener's recall did not make the visit longer. (derived, from Schillinger and others 2003)
- Both results come from trained people in one profession. Those people had a shared code before the handoff. (derived)

## Part E. Open problems and contradictions

All of part E is derived.

1. The stop rule. "Sufficient for current purposes" has no measure. The cost of an error is unknown until the unforeseen case occurs, and that is after the check. This is the main open problem.
2. The choice of probe cases. The sender knows the hard cases best. The sender is also the worst judge of what the receiver lacks. No theory says who writes the probes.
3. Verbatim display. Clark and Schaefer rank a verbatim display as the strongest evidence. Education ranks repetition as the lowest level. The two agree only if "strongest" refers to exact items and not to meaning.
4. One-way grounding. Least collaborative effort assumes a partner who repairs. The theory says little about a writer whose reader comes after the writer stops. It predicts only more revision before sending.
5. Trust against doubt. A record functions as memory only if the reader endorses it automatically. The same automatic trust carries Twin Otto's error. No theory gives the correct quantity of trust.
6. Overlap against a fresh view. Shared mental model work says that more overlap gives better coordination. Handoff studies say that a fresh view finds fixation errors. No theory says what a handoff must not transfer.
7. Log against checkpoint. The replay result needs a deterministic reader. No result says how much history a non-deterministic reader needs to rebuild the reasons.
8. The size of the unwritten part. Polanyi and Ryle say that some knowledge cannot be told. Other philosophers say that knowing how is a form of knowing that (Stanley and Williamson 2001, R). No method measures the untellable part of a given goal.
9. Replacement with zero overlap. Team studies measure members who train or work together. The sources here do not measure a member who replaces another with no shared time.
10. Minds that are programs. The measurements of sender overconfidence, of the illusion of explanatory depth, and of poor self-judgement come from people. These sources do not say if the numbers hold for a program that reasons.
11. Checks that survive being known. Goodhart's law says that a known check degrades. No source here says which checks degrade slowly, or why.
12. Identity. The extended mind covers one agent and its own notebook. A different mind fails the condition of past endorsement. The theory does not say if the receiver continues the first effort or starts a second effort with the same aim.

## Part F. Five questions for a real handover

All of part F is derived. Each question names the conditions that it tests.

1. Remove the task list. Can the receiver say the next step and its reason on a case that the record does not cover, and does a mind that knows the goal agree? (B3, B5)
2. Which terms and which unstated steps did the receiver have to guess, and what does the receiver say that it does not know? (B2, B7)
3. Did the receiver's picture of the current state come from its own look at the world, and does that picture agree with the sender's summary? (B4)
4. Which mind is responsible now, do all parties give the same answer from the same place, and what occurs if two minds act on the same work? (B1, B6)
5. Which rank of part C does the evidence reach, who judged it, and did the receiver know the check before the check? (all conditions, and B9 reason 4)

## Limits of this read

- The grades S and R mark statements that this read did not verify in the primary text.
- These figures come from abstracts or summaries, not from the full papers: Newton's 2.5%, Shattuck and Woods' 34%, Gick and Holyoak's 30% and 80%, Butler's 68% and 44%, the .27 correlation, and Hinds' result.
- The finding on self-rated situation awareness comes from one search summary. Treat that finding as not verified.
- Most measurements here come from people in conversation, in classrooms and in control rooms. Part E item 10 states the gap.

## Sources

Communication theory

- Shannon, C. E. (1948). A mathematical theory of communication. Bell System Technical Journal 27. https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf
- Weaver, W. (1949). The mathematics of communication. Scientific American 181(1). https://monoskop.org/images/b/b3/Weaver_Warren_1949_1973_The_Mathematics_of_Communication.pdf

Grounding

- Clark, H. H. and Brennan, S. E. (1991). Grounding in communication. In Resnick, Levine and Teasley (Eds.), Perspectives on Socially Shared Cognition, 127-149. APA. https://web.stanford.edu/~clark/1990s/Clark,%20H.H.%20_%20Brennan,%20S.E.%20_Grounding%20in%20communication_%201991.pdf
- Clark, H. H. and Schaefer, E. F. (1989). Contributing to discourse. Cognitive Science 13, 259-294. https://web.stanford.edu/~clark/1980s/Clark,%20H.H.%20_%20Schaefer,%20E.F.%20_Contributing%20to%20discourse_%201989.pdf
- Clark, H. H. and Marshall, C. R. (1981). Definite reference and mutual knowledge. In Joshi, Webber and Sag (Eds.), Elements of Discourse Understanding, 10-63. Cambridge University Press. https://philarchive.org/archive/CLADKA

Distributed systems

- Gray, J. (1978). Notes on data base operating systems. In Operating Systems: An Advanced Course, LNCS 60, 393-481. Springer. https://jimgray.azurewebsites.net/papers/dbos.pdf
- Halpern, J. Y. and Moses, Y. (1990). Knowledge and common knowledge in a distributed environment. Journal of the ACM 37(3), 549-587. https://arxiv.org/abs/cs/0006009
- Saltzer, J. H., Reed, D. P. and Clark, D. D. (1984). End-to-end arguments in system design. ACM Transactions on Computer Systems 2(4), 277-288. https://web.mit.edu/Saltzer/www/publications/endtoend/endtoend.pdf
- Fischer, M. J., Lynch, N. A. and Paterson, M. S. (1985). Impossibility of distributed consensus with one faulty process. Journal of the ACM 32(2), 374-382. https://www.cs.princeton.edu/courses/archive/spring22/cos418/papers/flp.pdf
- Helland, P. (2012). Idempotence is not a medical condition. ACM Queue 10(4), 30-46. https://doi.org/10.1145/2181796.2187821
- Schneider, F. B. (1990). Implementing fault-tolerant services using the state machine approach: a tutorial. ACM Computing Surveys 22(4), 299-319. https://www.cs.cornell.edu/fbs/publications/SMSurvey.pdf
- Elnozahy, E. N., Alvisi, L., Wang, Y.-M. and Johnson, D. B. (2002). A survey of rollback-recovery protocols in message-passing systems. ACM Computing Surveys 34(3), 375-408. https://doi.org/10.1145/568522.568525

Knowledge that resists writing

- Polanyi, M. (1966). The Tacit Dimension. Doubleday. Summary read at https://en.wikipedia.org/wiki/Polanyi%27s_paradox
- Ryle, G. (1945). Knowing how and knowing that. Proceedings of the Aristotelian Society 46, 1-16. https://doi.org/10.1093/aristotelian/46.1.1
- Collins, H. M. (1974). The TEA set: tacit knowledge and scientific networks. Science Studies 4(2), 165-186. https://research.engineering.nyu.edu/~jbain/scitechsoc/readings/74Collins.pdf
- Camerer, C., Loewenstein, G. and Weber, M. (1989). The curse of knowledge in economic settings: an experimental analysis. Journal of Political Economy 97(5), 1232-1254. https://www.cmu.edu/dietrich/sds/docs/loewenstein/CurseknowledgeEconSet.pdf
- Newton, E. L. (1990). The rocky road from actions to intentions. Doctoral dissertation, Stanford University. Reported in Heath, C. and Heath, D. (2006). The curse of knowledge. Harvard Business Review. https://hbr.org/2006/12/the-curse-of-knowledge
- Keysar, B. and Henly, A. S. (2002). Speakers' overestimation of their effectiveness. Psychological Science 13(3), 207-212. https://pubmed.ncbi.nlm.nih.gov/12009039/
- Kruger, J., Epley, N., Parker, J. and Ng, Z.-W. (2005). Egocentrism over e-mail: can we communicate as well as we think? Journal of Personality and Social Psychology 89(6), 925-936. https://pubmed.ncbi.nlm.nih.gov/16393025/
- Hinds, P. J. (1999). The curse of expertise: the effects of expertise and debiasing methods on predictions of novice performance. Journal of Experimental Psychology: Applied 5(2), 205-221. https://doi.org/10.1037/1076-898X.5.2.205
- Rozenblit, L. and Keil, F. (2002). The misunderstood limits of folk science: an illusion of explanatory depth. Cognitive Science 26(5), 521-562. https://pmc.ncbi.nlm.nih.gov/articles/PMC3062901/
- Silk-Eglit, G. and Kurtz, K. J. (2011). Types of cognitive content and the role of relational processing in the illusion of explanatory depth. Proceedings of the Cognitive Science Society 33. https://escholarship.org/uc/item/582378mf
- Stanley, J. and Williamson, T. (2001). Knowing how. Journal of Philosophy 98(8), 411-444. https://doi.org/10.2307/2678403

Team cognition and handoffs

- Cannon-Bowers, J. A., Salas, E. and Converse, S. (1993). Shared mental models in expert team decision making. In Castellan (Ed.), Individual and Group Decision Making, 221-246. Erlbaum. Summary read in Lim and Klein (2006), https://faculty.wharton.upenn.edu/wp-content/uploads/2012/05/Lim_Klein_Team_mental_models_2006.pdf
- Mathieu, J. E., Heffner, T. S., Goodwin, G. F., Salas, E. and Cannon-Bowers, J. A. (2000). The influence of shared mental models on team process and performance. Journal of Applied Psychology 85(2), 273-283. https://doi.org/10.1037/0021-9010.85.2.273
- Wegner, D. M. (1987). Transactive memory: a contemporary analysis of the group mind. In Mullen and Goethals (Eds.), Theories of Group Behavior, 185-208. Springer. Summary read at https://en.wikipedia.org/wiki/Transactive_memory
- Liang, D. W., Moreland, R. and Argote, L. (1995). Group versus individual training and group performance: the mediating role of transactive memory. Personality and Social Psychology Bulletin 21(4), 384-393. https://doi.org/10.1177/0146167295214009
- Hutchins, E. (1995). Cognition in the Wild. MIT Press. Also Hutchins, E. (1995). How a cockpit remembers its speeds. Cognitive Science 19, 265-288. https://courses.ischool.berkeley.edu/i290-3/s05/papers/How_a_cockpit_remembers_its_speeds.pdf
- Endsley, M. R. (1995). Toward a theory of situation awareness in dynamic systems. Human Factors 37(1), 32-64. https://doi.org/10.1518/001872095779049543
- Endsley, M. R., Selcon, S. J., Hardiman, T. D. and Croft, D. G. (1998). A comparative analysis of SAGAT and SART for evaluations of situation awareness. Proceedings of the Human Factors and Ergonomics Society 42, 82-86. https://doi.org/10.1177/154193129804200119
- Patterson, E. S., Roth, E. M., Woods, D. D., Chow, R. and Gomes, J. O. (2004). Handoff strategies in settings with high consequences for failure: lessons for health care operations. International Journal for Quality in Health Care 16(2), 125-132. https://www.interruptions.net/literature/Patterson-IntJQualHealthCare04.pdf
- Shattuck, L. G. and Woods, D. D. (2000). Communication of intent in military command and control systems. In McCann and Pigeau (Eds.), The Human in Command, 279-291. Springer. https://link.springer.com/chapter/10.1007/978-1-4615-4229-2_19
- Starmer, A. J. and others (2014). Changes in medical errors after implementation of a handoff program. New England Journal of Medicine 371, 1803-1812. https://doi.org/10.1056/NEJMsa1405556

Goals and intent

- Vallacher, R. R. and Wegner, D. M. (1987). What do people think they're doing? Action identification and human behavior. Psychological Review 94(1), 3-15. https://doi.org/10.1037/0033-295X.94.1.3
- Rasmussen, J. (1985). The role of hierarchical knowledge representation in decisionmaking and system management. IEEE Transactions on Systems, Man, and Cybernetics 15(2), 234-243. https://doi.org/10.1109/TSMC.1985.6313353
- Altmann, E. M. and Trafton, J. G. (2002). Memory for goals: an activation-based model. Cognitive Science 26(1), 39-83. https://www.interruptions.net/literature/Altmann-CogSci02.pdf
- Holmstrom, B. and Milgrom, P. (1991). Multitask principal-agent analyses: incentive contracts, asset ownership, and job design. Journal of Law, Economics, and Organization 7, 24-52. https://gwern.net/doc/economics/1991-holmstrom.pdf
- Kerr, S. (1975). On the folly of rewarding A, while hoping for B. Academy of Management Journal 18(4), 769-783. https://doi.org/10.5465/255378
- Goodhart, C. A. E. (1975). Problems of monetary management: the U.K. experience. Papers in Monetary Economics, Reserve Bank of Australia. Summary read at https://en.wikipedia.org/wiki/Goodhart%27s_law
- Strathern, M. (1997). 'Improving ratings': audit in the British university system. European Review 5(3), 305-321. https://doi.org/10.1002/(SICI)1234-981X(199707)5:3<305::AID-EURO184>3.0.CO;2-4
- Campbell, D. T. (1979). Assessing the impact of planned social change. Evaluation and Program Planning 2(1), 67-90. https://doi.org/10.1016/0149-7189(79)90048-X
- Grossman, S. J. and Hart, O. D. (1986). The costs and benefits of ownership: a theory of vertical and lateral integration. Journal of Political Economy 94(4), 691-719. https://doi.org/10.1086/261404

Tests of understanding

- Anderson, L. W. and Krathwohl, D. R. (Eds.) (2001). A Taxonomy for Learning, Teaching, and Assessing. Longman. Read by Mayer (2002).
- Mayer, R. E. (2002). Rote versus meaningful learning. Theory Into Practice 41(4), 226-232. https://doi.org/10.1207/s15430421tip4104_4
- Gick, M. L. and Holyoak, K. J. (1980). Analogical problem solving. Cognitive Psychology 12, 306-355. https://deepblue.lib.umich.edu/handle/2027.42/23210
- Gick, M. L. and Holyoak, K. J. (1983). Schema induction and analogical transfer. Cognitive Psychology 15, 1-38. https://doi.org/10.1016/0010-0285(83)90002-6
- Barnett, S. M. and Ceci, S. J. (2002). When and where do we apply what we learn? A taxonomy for far transfer. Psychological Bulletin 128(4), 612-637. https://doi.org/10.1037/0033-2909.128.4.612
- Butler, A. C. (2010). Repeated testing produces superior transfer of learning relative to repeated studying. Journal of Experimental Psychology: Learning, Memory, and Cognition 36(5), 1118-1133. https://doi.org/10.1037/a0019902
- Maki, R. H. (1998). Test predictions over text material. In Hacker, Dunlosky and Graesser (Eds.), Metacognition in Educational Theory and Practice, 117-144. Erlbaum. Read by Dunlosky and Lipko (2007).
- Dunlosky, J. and Lipko, A. R. (2007). Metacomprehension: a brief history and how to improve its accuracy. Current Directions in Psychological Science 16(4), 228-232. https://doi.org/10.1111/j.1467-8721.2007.00509.x
- Schillinger, D. and others (2003). Closing the loop: physician communication with diabetic patients who have low health literacy. Archives of Internal Medicine 163(1), 83-90. https://pubmed.ncbi.nlm.nih.gov/12523921/
- Talevski, J. and others (2020). Teach-back: a systematic review of implementation and impacts. PLoS ONE 15(4), e0231350. https://pubmed.ncbi.nlm.nih.gov/32287296/
- Barenfanger, J. and others (2004). Improving patient safety by repeating (read-back) telephone reports of critical information. American Journal of Clinical Pathology 121(6), 801-803. https://doi.org/10.1309/9DYM6R0TM830U95Q

Memory, identity and records

- Clark, A. and Chalmers, D. (1998). The extended mind. Analysis 58(1), 7-19. https://consc.net/papers/extended.html
- Sacks, O. (2007). The abyss. The New Yorker, 24 September 2007. Copy read at https://cse.buffalo.edu/~rapaport/575/F08/sacks07-nykr.pdf
- Wilson, B. A., Emslie, H. C., Quirk, K. and Evans, J. J. (2001). Reducing everyday memory and planning problems by means of a paging system: a randomised control crossover study. Journal of Neurology, Neurosurgery and Psychiatry 70(4), 477-482. https://doi.org/10.1136/jnnp.70.4.477
