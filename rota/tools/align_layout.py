"""
Snap the hand-dragged layout onto the grid it is already nearly on.

The positions in `layout.json` were made by dragging nodes and pressing save, so
things meant to line up are a few pixels apart:

    x: ... -747, -745 ...  774, 778 ...  858, 864, 880 ...  1454, 1460, 1465
    y: ...  762, 763, 769, 772 ...  989, 995 ...  1070, 1077 ...

Bowed edges hide that completely. Orthogonal routing does the opposite: a 3px
mismatch turns a straight run into a Z with a visible kink, which reads as a
bug rather than as a near miss. `refPath` already draws a straight line only
when the two centres agree within 6px, so pairs that miss by 7 are getting a
spurious dogleg today.

**Clustered, not rounded.** Snapping to a fixed grid splits any pair that
straddles a boundary -- 869 and 871 land in different cells and end up further
apart than they started. Single-linkage clustering under a tolerance moves
things together only when they were already together.

    python -m rota.tools.align_layout --dry-run
    python -m rota.tools.align_layout
"""
from __future__ import annotations

import argparse
import json
import sys

from rota import paths

# How far apart two coordinates can be and still mean "the same column".
#
# 14px against a 152px node: a seventh of its width. Wide enough to catch the
# 1454/1460/1465 group, narrow enough that two nodes deliberately staggered by
# a third of a box stay staggered.
TOLERANCE = 14.0


def clusters(values: list[float], tol: float) -> dict[float, float]:
    """Map each value to the mean of the run it belongs to.

    Single-linkage: sort, and start a new group wherever the gap to the
    previous value exceeds the tolerance. A long chain of near-misses collapses
    to one column, which is the intent -- three nodes at 1454, 1460 and 1465
    were one column when they were dragged.
    """
    out: dict[float, float] = {}
    if not values:
        return out
    ordered = sorted(values)
    run = [ordered[0]]
    for v in ordered[1:]:
        if v - run[-1] <= tol:
            run.append(v)
        else:
            centre = round(sum(run) / len(run))
            out.update({v: centre for v in run})
            run = [v]
    centre = round(sum(run) / len(run))
    out.update({v: centre for v in run})
    return out


def align(layout: dict[str, dict], tol: float = TOLERANCE) -> tuple[dict, list[str]]:
    xs = clusters([p["x"] for p in layout.values()], tol)
    ys = clusters([p["y"] for p in layout.values()], tol)

    moved, out = [], {}
    for node, p in layout.items():
        nx, ny = xs[p["x"]], ys[p["y"]]
        out[node] = {"x": nx, "y": ny}
        if (nx, ny) != (p["x"], p["y"]):
            moved.append(f"  {node:22} {p['x']:>6},{p['y']:>6}"
                         f"  ->  {nx:>6},{ny:>6}")
    return out, moved


def columns(layout: dict[str, dict]) -> tuple[int, int]:
    return (len({p["x"] for p in layout.values()}),
            len({p["y"] for p in layout.values()}))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--tolerance", type=float, default=TOLERANCE)
    args = ap.parse_args(argv)

    path = paths.REPO / "rota" / "design" / "layout.json"
    layout = json.loads(path.read_text(encoding="utf-8"))
    before = columns(layout)
    aligned, moved = align(layout, args.tolerance)
    after = columns(aligned)

    print(f"{len(layout)} nodes, tolerance {args.tolerance:g}px")
    print(f"  columns {before[0]} -> {after[0]}     rows {before[1]} -> {after[1]}")
    print(f"  {len(moved)} nodes move")
    for line in moved:
        print(line)

    if args.dry_run:
        print("\ndry run: nothing written")
        return 0

    path.write_text(json.dumps(aligned, indent=1, sort_keys=True) + "\n",
                    encoding="utf-8")
    print(f"\nwritten to {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
