# The seed of the product review, 2026-11-10

Written by session 7fd2421e for the session that Roman opens for the
review of rota, the product. This page is the hand-over. Read it whole
before any other act.

## What Roman asked, in his words

- "were picking back up an in depth review of the project, slowly,
  slowly" (2026-11-10, about 02:52).
- "not smaller in scope, slower in exploration, larger in scope"
  (2026-11-10, to session 5ee5ec0b).
- "Yeah keep going slow, small, large scale" (2026-11-10).
- "How should I spin up the rota review in a new session?" (2026-11-10
  03:26).
- "Yes but align with me" (2026-11-10 03:21), after he gave a session the
  ownership of its review.

## The two reviews

Two reviews run side by side. Each has one session.

1. The meta workflow: how the build sessions choose, build, measure and
   close work. Session 7fd2421e holds it as frame 363. Its map is
   `plans/method/meta-map-2026-11-10.md`.
2. The product: rota itself. You hold it.

The meta review can explain how the build is steered. It cannot say
whether rota's own design can reach the destination. That is your
question.

## Your question

Can rota, as it is designed, reach its destination? The destination is in
`plans/composition.md`: "a careful person runs rota alone on a small
Python repository and gets a merged change they can read. Honest about
where small models stop". The target capabilities are in
`rota/COMPLETION.md`, "Core, by capability".

For each part of the product: what the part is meant to do, what the runs
show that it does, and the evidence. One part of the answer is where the
small model stops.

This page gives you no finding and no hypothesis on purpose.

## The method, ruled by Roman

1. Write a blurry map of the whole product first, as a few masses. Use
   `plans/method/product-map-2026-11-10.md`. The map holds no finding and
   no fix.
2. Show the map to Roman in plain words. He corrects the masses.
3. Go deeper one mass at a time. Use one blind reader per mass, an agent
   that gets no hypothesis. Draw cases at random with a seed where a draw
   is possible.
4. Before each step, write the expected result on your frame. After the
   step, compare, and write the compare in the map. Choose the next step
   only then.
5. Then the connections between the masses, with one reader that tries to
   break them.
6. Only then, what to change. That step joins the meta review, as one
   design of the whole.

One step is one act. Hold the whole scope. The pace of understanding is
slow, and the size of the question is not small.

## Do not

- Do not change code, a rule, a tool or the order of the stack.
- Do not start a night, a dry run, the gate or a probe against a model.
  Session 13b7eef8 uses the 3080 for the gate of frame 182. A read of the
  recorded runs needs no GPU. If a new run is the only way to answer a
  question, tell Roman first.
- Do not read `plans/method/meta-*.md`, `plans/meta-review-2026-11-10.md`
  or the section "The redirect, 2026-11-10" of `plans/stack.md` before
  Roman has corrected your map. Your value is a second view. A view that
  starts from the first one repeats it.
- Do not read `plans/stack.md` whole. Agents keep the bulk out of your
  context.

## Where the evidence is

- The design: `plans/composition.md`, `rota/LAWS.md`, `rota/DECISIONS.md`,
  `rota/COMPLETION.md`, `plans/seat-exchange.md`.
- The runs: the 23 pages `plans/dry*-read-*.md` for dry runs 1 to 8, and
  the night reads that the stack and `plans/archive/` name.
- The walls: `plans/wall-guide.md`, `plans/walls-root-read-2026-11-08.md`.
- The blind test: `plans/understanding-test-blind-2026-11-03.md`, and
  `plans/dry-blind1/` with the request and the key of blind run 1. That
  run merged nothing and stopped at the third page. Nobody has read why.
  Its turn record is `blind1/turn_record.md` in
  `C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/5ee5ec0b-9675-4645-967d-eab60d0ca52e/scratchpad/`.
- The facts and the measurements: `plans/operating-facts.md`. Read the
  section that a step needs.
- The code: `rota/roles/`, `probes/`. An agent reads the code, not you.

## Known limits of the records

Every record of a run is written by a build session about its own work.
A status line can state a reason that was written after the choice.
Prefer a run's database, a diff or a test result to a sentence when both
exist.

## The frame, and the join

Roman assigns your frame. Frame 364 holds blind run 1, and session
7fd2421e holds that frame now. If Roman gives you frame 364, write your
session id in its heading and write a status line with
`python -m rota.tools.status 364 --sid <your session id> --text "..."`.

The two reviews join at step 6. Until then, send session 7fd2421e a
message only for a fact that changes its map, and expect the same from
it. Session 7fd2421e keeps context free to answer a question about this
page.

Reply to Roman first with your reading of his ask, in a few lines. Then
write the blurry map.
