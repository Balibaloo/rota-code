"""Hidden probe B of dry run 9: fold a long line at a space.

Run from a folder outside the subject repository:

    python probe-b.py <merged icalendar checkout> [--no-tests] [--no-diff]

The interpreter needs pytest, pytz, tzdata and python-dateutil for the
test step. The script prints PASS, or FAIL and the first failure, then
every other failure it found.
"""

import os
import re
import subprocess
import sys

sys.stdout.reconfigure(errors="backslashreplace")
ROOT = sys.argv[1]
RUN_TESTS = "--no-tests" not in sys.argv
RUN_DIFF = "--no-diff" not in sys.argv
BASE = "99619246"
SEP = "\r\n "
LIMIT = 75
MAX_PIECE = LIMIT - 1  # 74 content octets per piece, as at the base
UNFOLD = re.compile(r"\r\n[ \t]")

sys.path.insert(0, os.path.join(ROOT, "src"))
fails = []


def fail(msg):
    fails.append(msg)


def octets(text):
    return len(text.encode("utf-8"))


def pieces(folded):
    return folded.split(SEP)


def unfold(folded):
    return UNFOLD.sub("", folded)


def fold_points(folded):
    """Positions in the unfolded text where a fold landed."""
    pos = 0
    points = []
    for piece in pieces(folded)[:-1]:
        pos += len(piece)
        points.append(pos)
    return points


def common_checks(label, line, folded, limit=LIMIT):
    """Round trip, octet limit, no empty piece, no split UTF-8 sequence."""
    if unfold(folded) != line:
        fail(f"{label}: unfold of the folded text is not the input")
        return False
    for i, piece in enumerate(pieces(folded)):
        if piece == "":
            fail(f"{label}: piece {i} is empty")
        if octets(piece) > limit - 1:
            fail(f"{label}: piece {i} has {octets(piece)} octets, limit {limit - 1}")
        try:
            piece.encode("utf-8")
        except UnicodeEncodeError:
            fail(f"{label}: piece {i} is not valid UTF-8, a sequence is split")
    if "\r\n\t" in folded:
        fail(f"{label}: the fold separator uses a tab, base uses CRLF and one space")
    return True


def no_word_split(label, line, folded, allow=None):
    """Every fold lands next to a space. `allow` is a run of characters
    where a fold inside a word is allowed, because the word is longer than
    the limit."""
    for pos in fold_points(folded):
        before = line[pos - 1] if pos > 0 else " "
        after = line[pos] if pos < len(line) else " "
        if before == " " or after == " ":
            continue
        if allow is not None and before == allow and after == allow:
            continue
        fail(
            f"{label}: a fold splits a word at offset {pos}, "
            f"between {before!r} and {after!r}"
        )
        return


try:
    from icalendar import Calendar, Event
    from icalendar.parser.content_line import Contentline
    from icalendar.parser.string import _foldline
except Exception as exc:  # noqa: BLE001
    print(f"FAIL: cannot import the fold from {ROOT}: {exc!r}")
    sys.exit(1)

# 1. A long line of words folds at a space and no word is split.
LOREM = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
    "Vestibulum convallis imperdiet dui posuere."
)
WORDS = "DESCRIPTION:" + " ".join(f"word{i:02d}" for i in range(40))
for label, line in (("lorem", LOREM), ("words", WORDS)):
    folded = _foldline(line)
    if SEP not in folded:
        fail(f"{label}: the line did not fold")
        continue
    if common_checks(label, line, folded):
        no_word_split(label, line, folded)

# 2. Multi-octet characters: no split sequence, octets counted, nothing lost.
for label, char in (("e-acute x80", "é"), ("CJK x80", "日")):
    line = char * 80
    folded = _foldline(line)
    if SEP not in folded:
        fail(f"{label}: the line did not fold")
        continue
    common_checks(label, line, folded)

CYR_WORDS = "DESCRIPTION:" + " ".join(["слово"] * 20)
folded = _foldline(CYR_WORDS)
if SEP not in folded:
    fail("cyrillic words: the line did not fold")
elif common_checks("cyrillic words", CYR_WORDS, folded):
    no_word_split("cyrillic words", CYR_WORDS, folded)

# 3. A single word longer than the limit still folds and nothing is lost.
LONG_WORD = "DESCRIPTION:" + "x" * 200
folded = _foldline(LONG_WORD)
if len(pieces(folded)) < 3:
    fail("long word: fewer than 3 pieces for 212 octets")
common_checks("long word", LONG_WORD, folded)

MIXED = "DESCRIPTION:" + "y" * 100 + " tail word here and more words after"
folded = _foldline(MIXED)
if common_checks("mixed", MIXED, folded):
    no_word_split("mixed", MIXED, folded, allow="y")

# 4. The escape rule of issue 1501 still holds, with and without spaces.
ESCAPES = [r"\n", r"\N", r"\,", r"\;", r"\\", "^n", "^^", "^'"]
for limit in range(60, 91):
    for esc in ESCAPES:
        prefix = "DESCRIPTION:" + "a" * (limit - len("DESCRIPTION:") - 2)
        line = prefix + esc + "after fold"
        folded = _foldline(line, limit=limit)
        if SEP not in folded:
            fail(f"escape {esc!r} limit {limit}: the line did not fold")
            break
        if esc[0] + SEP + esc[1] in folded:
            fail(f"escape {esc!r} limit {limit}: the fold splits the escape")
            break
        common_checks(f"escape {esc!r} limit {limit}", line, folded, limit)
        if esc in (r"\\", "^^"):
            # The base pops a trailing backslash or caret as a prefix even
            # when it closes a pair, so the base itself splits these two at
            # some boundaries. Not asked to change, so not checked here.
            continue
        spaced = "DESCRIPTION:" + "ab " * ((limit - 14) // 3) + esc + " after fold"
        folded = _foldline(spaced, limit=limit)
        if esc[0] + SEP + esc[1] in folded:
            fail(f"escape {esc!r} with spaces, limit {limit}: the fold splits the escape")
            break
        common_checks(f"escape {esc!r} with spaces, limit {limit}", spaced, folded, limit)
    if fails and fails[-1].startswith("escape"):
        break

# 5. Small limits and the kept assertions of test_fold_line.
if _foldline("foo") != "foo":
    fail("_foldline('foo') is not 'foo'")
if _foldline("foobar", limit=4) != "foo\r\n bar":
    fail(f"_foldline('foobar', limit=4) is {_foldline('foobar', limit=4)!r}, base gives 'foo\\r\\n bar'")
folded = _foldline("ab cd ef", limit=4)
if common_checks("small limit words", "ab cd ef", folded, 4):
    no_word_split("small limit words", "ab cd ef", folded)
try:
    _foldline("привет".encode(), limit=3)
    fail("bytes input did not raise AssertionError")
except AssertionError:
    pass
except Exception as exc:  # noqa: BLE001
    fail(f"bytes input raised {exc!r}, base raises AssertionError")
try:
    _foldline("a\nb")
    fail("a line with a newline did not raise AssertionError")
except AssertionError:
    pass
except Exception as exc:  # noqa: BLE001
    fail(f"a line with a newline raised {exc!r}, base raises AssertionError")

# 6. The content round-trips through the calendar, wire lines within 75 octets.
TEXT = " ".join(f"word{i:02d}" for i in range(40)) + ", with a comma\nand a new line"
CYR_TEXT = " ".join(["слово"] * 20)
event = Event()
event.add("UID", "probe-b")
event.add("SUMMARY", "s")
event.add("DESCRIPTION", TEXT)
event.add("COMMENT", CYR_TEXT)
event.add("ATTENDEE", "mailto:emily.smith@example.com", parameters={"CN": "Emily Smith", "ROLE": "CHAIR", "RSVP": "TRUE"})
cal = Calendar()
cal.add_component(event)
raw = cal.to_ical()
for i, wire in enumerate(raw.split(b"\r\n")):
    if len(wire) > LIMIT:
        fail(f"calendar: wire line {i} has {len(wire)} octets, more than {LIMIT}")
        break
try:
    back = Calendar.from_ical(raw).walk("VEVENT")[0]
    if str(back["DESCRIPTION"]) != TEXT:
        fail("calendar: DESCRIPTION did not round-trip")
    if str(back["COMMENT"]) != CYR_TEXT:
        fail("calendar: COMMENT (Cyrillic) did not round-trip")
    if back["ATTENDEE"].params.get("CN") != "Emily Smith":
        fail("calendar: ATTENDEE CN did not round-trip")
except Exception as exc:  # noqa: BLE001
    fail(f"calendar: from_ical raised {exc!r}")
line = Contentline(WORDS)
if Contentline.from_ical(line.to_ical().decode("utf-8")) != WORDS:
    fail("Contentline: to_ical then from_ical is not the input")

# 7. The repository's own tests of the fold, and the tests whose expected
# output encodes the fold position, stay green.
TEST_FILES = [
    "src/icalendar/tests/test_icalendar.py",
    "src/icalendar/tests/test_parsing.py",
    "src/icalendar/tests/test_issue_116.py",
    "src/icalendar/tests/test_issue_836_do_not_quote_tzid.py",
    "src/icalendar/tests/test_with_doctest.py",
]
if RUN_TESTS:
    env = dict(os.environ, PYTHONUTF8="1", PYTHONPATH=os.path.join(ROOT, "src"))
    missing = [f for f in TEST_FILES if not os.path.exists(os.path.join(ROOT, f))]
    if missing:
        fail(f"tests: files missing from the checkout: {missing}")
    else:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--no-header", *TEST_FILES],
            cwd=ROOT, capture_output=True, text=True, env=env,
        )
        if result.returncode != 0:
            tail = "\n".join(result.stdout.strip().splitlines()[-6:])
            fail(f"tests: the fold tests are red\n{tail}")

# 8. The diff: allowed files, no deleted test, kept lines.
ALLOWED = re.compile(
    r"^(src/icalendar/parser/string\.py"
    r"|src/icalendar/parser/content_line\.py"  # docstring only, check by eye
    r"|src/icalendar/tests/.*\.py"
    r"|news/[^/]+"
    r"|docs/.*"
    r"|src/icalendar/attr\.py"  # doctest output only, check by eye
    r"|src/icalendar/cal/event\.py"  # doctest output only, check by eye
    r"|src/icalendar/cal/todo\.py)$"  # doctest output only, check by eye
)
if RUN_DIFF:
    def git(*args):
        return subprocess.run(["git", "-C", ROOT, *args], capture_output=True, text=True)

    names = git("diff", "--name-only", BASE, "HEAD")
    if names.returncode != 0:
        fail(f"diff: git diff against {BASE} failed: {names.stderr.strip()}")
    else:
        for name in names.stdout.split():
            if not ALLOWED.match(name):
                fail(f"diff: touches {name}, outside the landing set")
        deleted = git("diff", "--name-only", "--diff-filter=D", BASE, "HEAD").stdout.split()
        if deleted:
            fail(f"diff: deletes {deleted}")
        news_changed = [n for n in git("diff", "--name-only", "--diff-filter=M", BASE, "HEAD").stdout.split() if n.startswith("news/")]
        if news_changed:
            fail(f"diff: edits an existing change log entry {news_changed}")
        added = git("diff", "--name-only", "--diff-filter=A", BASE, "HEAD").stdout.split()
        if not any(n.startswith("news/") for n in added):
            fail("diff: no new change log entry under news/")

KEPT = {
    "src/icalendar/parser/string.py": [
        'assert "\\n" not in line',
        "def _foldline(line: str, limit: int = 75, fold_sep: str = \"\\r\\n \") -> str:",
        '.replace("\\r", r"\\n")',
        "foldline = deprecate_for_version_8(_foldline)",
    ],
    "src/icalendar/tests/test_icalendar.py": [
        'assert _foldline("foobar", limit=4) == "foo\\r\\n bar"',
        "with pytest.raises(AssertionError):",
        "def test_fold_line(self):",
    ],
    "src/icalendar/tests/test_parsing.py": [
        "def test_foldline_does_not_split_escape_sequences_issue_1501(",
        "def test_foldline_does_not_split_escape_sequences_across_multiple_lines_issue_1501(",
        '@pytest.mark.parametrize("line_limit", range(60, 91))',
    ],
}
for rel, lines in KEPT.items():
    path = os.path.join(ROOT, rel)
    try:
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
    except OSError as exc:
        fail(f"kept lines: cannot open {rel}: {exc!r}")
        continue
    for needle in lines:
        if needle not in text:
            fail(f"kept lines: {rel} lost {needle!r}")

if not fails:
    print("PASS")
    sys.exit(0)
print("FAIL: " + fails[0])
for other in fails[1:]:
    print("also: " + other)
sys.exit(1)
