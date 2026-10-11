# Frame 203 count: git calls per test and the ten heaviest fixtures

The count agent's report, Opus, 2026-10-11 13:55 to 14:22, session be3ef742, 124.5k on the harness line against 120k. Returned whole because the harness refused the report write; the facts are in frame 203's status line of 2026-10-11 14:25 in `plans/stack.md`, and the raw JSON, the plugin `c203_count.py` and the probe diff are under the session scratchpad `c203/`. Meta workflow.

Headline: on the whole suite at `-n 4` (610s wall, 2309s worker time), `init_db` per test costs about 20% (1158 setups, 140ms each, 4.8ms on a copied template), child `python -m pytest` processes about 21%, git about 16% (6362 calls). A git template on `test_verdict_lines.py`: 36.9s to 22.0s median, 311 to 131 git calls. 16 workers on 8 physical cores. Two single tests take 55s and 13s alone.
