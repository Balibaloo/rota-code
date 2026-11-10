"""Hidden probe of dry run 9: fold a long line at a space.

The union of the checks of probe-a.py and probe-b.py that survived the
reconciliation of 2026-11-10. Run it from a folder outside the subject
repository, against the merged icalendar checkout:

    python -I probe.py <merged checkout> [<interpreter>] [--no-tests] [--no-diff]

The interpreter runs the repository's own tests and needs pytest, pytz,
tzdata and python-dateutil. It defaults to the interpreter that runs this
script. The script prints PASS, or FAIL and the first failure, then up to
eleven "also:" lines for the other failures.
"""

import os
import re
import subprocess
import sys

sys.stdout.reconfigure(errors="backslashreplace")
args = [a for a in sys.argv[1:] if not a.startswith("--")]
ROOT = os.path.abspath(args[0])
TEST_PYTHON = args[1] if len(args) > 1 else sys.executable
RUN_TESTS = "--no-tests" not in sys.argv
RUN_DIFF = "--no-diff" not in sys.argv
BASE = "99619246"
SEP = "\r\n "
LIMIT = 75
UNFOLD = re.compile(r"\r\n[ \t]")

sys.path.insert(0, os.path.join(ROOT, "src"))
fails = []


def fail(msg):
    fails.append(msg)


def check(cond, msg):
    if not cond:
        fail(msg)


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
    """Round trip, octet limit, no empty piece, no split sequence, one separator."""
    if unfold(folded) != line:
        fail(f"{label}: unfold of the folded text is not the input")
        return False
    for i, piece in enumerate(pieces(folded)):
        if piece == "":
            fail(f"{label}: piece {i} is empty")
        if octets(piece) >= limit:
            fail(f"{label}: piece {i} has {octets(piece)} octets, the base keeps {limit - 1} at most")
        try:
            piece.encode("utf-8")
        except UnicodeEncodeError:
            fail(f"{label}: piece {i} is not valid UTF-8, a sequence is split")
    if "\r\n\t" in folded:
        fail(f"{label}: the fold separator uses a tab, the base uses CRLF and one space")
    if "\n" in folded.replace(SEP, ""):
        fail(f"{label}: a lone newline in the folded text")
    for i, wire in enumerate(folded.encode("utf-8").split(b"\r\n")):
        if len(wire) > limit:
            fail(f"{label}: wire line {i} has {len(wire)} octets, over {limit}")
        try:
            wire.decode("utf-8")
        except UnicodeDecodeError:
            fail(f"{label}: wire line {i} splits a UTF-8 sequence")
    return True


def no_word_split(label, line, folded, allow=None):
    """Every fold lands next to a space. `allow` is a character whose run may
    hold a fold, because that word is longer than the limit."""
    for pos in fold_points(folded):
        before = line[pos - 1] if pos > 0 else " "
        after = line[pos] if pos < len(line) else " "
        if before == " " or after == " ":
            continue
        if allow is not None and before == allow and after == allow:
            continue
        fail(f"{label}: a fold splits a word at offset {pos}, between {before!r} and {after!r}")
        return


try:
    from icalendar import Calendar, Event
    from icalendar.parser.content_line import UFOLD, Contentline
    from icalendar.parser.string import _foldline
except Exception as exc:  # noqa: BLE001
    print(f"FAIL: cannot import the fold from {ROOT}: {exc!r}")
    sys.exit(1)

# 1. Lines of words fold at a space, and no word is split.
LOREM = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
    "Vestibulum convallis imperdiet dui posuere."
)
WORDS = "DESCRIPTION:" + " ".join(["word"] * 40)
WORDS_B = "DESCRIPTION:" + " ".join(f"word{i:02d}" for i in range(40))
LONG_WORDS = "SUMMARY:" + " ".join(f"alpha{i:02d}bravo" for i in range(14))
CYR_WORDS = "DESCRIPTION:" + " ".join(["слово"] * 20)
for label, line in (
    ("lorem", LOREM),
    ("40 words", WORDS),
    ("40 numbered words", WORDS_B),
    ("12-char words", LONG_WORDS),
    ("cyrillic words", CYR_WORDS),
):
    folded = _foldline(line)
    if SEP not in folded:
        fail(f"{label}: the line did not fold")
        continue
    if common_checks(label, line, folded):
        no_word_split(label, line, folded)

# 2. Multi-octet characters: octets counted, no split sequence, nothing lost.
for label, text in (
    ("80 x U+00E9", "é" * 80),
    ("80 x U+20AC", "€" * 80),
    ("80 x CJK", "日" * 80),
    ("cyrillic test line", "DESCRIPTION:АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭЮЯ"),
):
    folded = _foldline(text)
    if SEP not in folded:
        fail(f"{label}: the line did not fold")
        continue
    common_checks(label, text, folded)

# 3. A single word longer than the limit still folds, and nothing is lost.
for label, long_word in (("long word a", "X:" + "a" * 200), ("long word x", "DESCRIPTION:" + "x" * 200)):
    folded = _foldline(long_word)
    check(len(pieces(folded)) >= 3, f"{label}: {len(pieces(folded))} pieces, expected at least 3")
    common_checks(label, long_word, folded)
    check(folded.replace(SEP, "") == long_word, f"{label}: characters lost or added")

MIXED = "DESCRIPTION:" + "y" * 100 + " tail word here and more words after"
folded = _foldline(MIXED)
if common_checks("mixed", MIXED, folded):
    no_word_split("mixed", MIXED, folded, allow="y")

# 4. Mixed inputs with spaces at the window edge, runs of spaces, a leading
# and a trailing space, and escapes before the cut: limit and round trip.
MIX = [
    "A:" + "b" * 71 + " " + "c" * 20,
    "A:" + "b" * 72 + " " + "c" * 20,
    "A:" + "b" * 73 + " " + "c" * 20,
    "A:" + "b" * 74 + " " + "c" * 20,
    "A:" + "b" * 10 + " " * 80 + "c" * 20,
    "A: " + "b" * 100,
    "A:" + "b" * 100 + " ",
    "SUMMARY:ab cd " + "e" * 100,
    "DESCRIPTION:" + "a" * 61 + "\\n" + "after fold",
    "DESCRIPTION:" + "a" * 60 + " \\n" + "after fold",
    "DESCRIPTION:" + "a" * 61 + "^n" + "after fold",
]
for text in MIX:
    folded = _foldline(text)
    common_checks(f"mix {text[:20]!r}", text, folded)
    check(SEP in folded, f"mix {text[:20]!r}: did not fold with CRLF and one space")

# 5. The escape rule of issue 1501 at limits 60 to 90, with and without spaces.
ESCAPES = [r"\n", r"\N", r"\,", r"\;", r"\\", "^n", "^^", "^'"]
for limit in range(60, 91):
    for esc in ESCAPES:
        prefix = "DESCRIPTION:" + "a" * (limit - len("DESCRIPTION:") - 2)
        line = prefix + esc + "after fold"
        folded = _foldline(line, limit=limit)
        check(SEP in folded, f"escape {esc!r} limit {limit}: the line did not fold")
        check(esc[0] + SEP + esc[1] not in folded, f"escape {esc!r} limit {limit}: the fold splits the escape")
        common_checks(f"escape {esc!r} limit {limit}", line, folded, limit)
        if esc in (r"\\", "^^"):
            # The base pops a trailing backslash or caret as a prefix even
            # when it closes a pair, so the base itself splits these two at
            # some boundaries. Not asked to change, so not checked here.
            continue
        spaced = "DESCRIPTION:" + "ab " * ((limit - 14) // 3) + esc + " after fold"
        folded = _foldline(spaced, limit=limit)
        check(esc[0] + SEP + esc[1] not in folded, f"escape {esc!r} with spaces, limit {limit}: the fold splits the escape")
        common_checks(f"escape {esc!r} with spaces, limit {limit}", spaced, folded, limit)

# 6. The promises that stay as before.
check(_foldline("foo") == "foo", "short line changed")
check(_foldline("foobar", limit=4) == "foo\r\n bar", f"_foldline('foobar', limit=4) is {_foldline('foobar', limit=4)!r}, the base gives 'foo\\r\\n bar'")
check(
    _foldline("DESCRIPTION:АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭЮЯ")
    == "DESCRIPTION:АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭ\r\n ЮЯ",
    "the Cyrillic expectation of test_fold_line changed",
)
check(_foldline("foobar", limit=4, fold_sep="\n ") == "foo\n bar", "fold_sep parameter lost")
folded = _foldline("ab cd ef", limit=4)
if common_checks("small limit words", "ab cd ef", folded, 4):
    no_word_split("small limit words", "ab cd ef", folded)
try:
    _foldline("привет".encode(), limit=3)
    fail("bytes input did not raise AssertionError")
except AssertionError:
    pass
except Exception as exc:  # noqa: BLE001
    fail(f"bytes input raised {exc!r}, the base raises AssertionError")
try:
    _foldline("a\nb")
    fail("a line with a newline did not raise AssertionError")
except AssertionError:
    pass
except Exception as exc:  # noqa: BLE001
    fail(f"a line with a newline raised {exc!r}, the base raises AssertionError")

# 7. The caller and a complete calendar round-trip. No wire line over 75 octets.
cl = Contentline(WORDS).to_ical()
check(isinstance(cl, bytes), "Contentline.to_ical no longer returns bytes")
check(b"\r\n " in cl, "Contentline.to_ical no longer folds with CRLF and a space")
check(UFOLD.sub("", cl.decode("utf-8")) == WORDS, "Contentline.to_ical does not round-trip")
check(Contentline.from_ical(cl.decode("utf-8")) == WORDS, "Contentline: to_ical then from_ical is not the input")

TEXT = " ".join(f"word{i:02d}" for i in range(40)) + ", with a comma\nand a new line"
CYR_TEXT = " ".join(["слово"] * 20)
SUMMARY = " ".join(["meeting"] * 30) + " " + "é" * 40
CN = "Emily Smith"
event = Event()
event.add("UID", "probe-9")
event.add("SUMMARY", SUMMARY)
event.add("DESCRIPTION", TEXT)
event.add("COMMENT", CYR_TEXT)
event.add("ATTENDEE", "mailto:emily.smith@example.com", parameters={"CN": CN, "ROLE": "CHAIR", "RSVP": "TRUE"})
cal = Calendar()
cal.add_component(event)
raw = cal.to_ical()
for i, wire in enumerate(raw.split(b"\r\n")):
    if len(wire) > LIMIT:
        fail(f"calendar: wire line {i} has {len(wire)} octets, more than {LIMIT}")
        break
try:
    back = Calendar.from_ical(raw).walk("VEVENT")[0]
    check(str(back["SUMMARY"]) == SUMMARY, "calendar: SUMMARY did not round-trip")
    check(str(back["DESCRIPTION"]) == TEXT, "calendar: DESCRIPTION did not round-trip")
    check(str(back["COMMENT"]) == CYR_TEXT, "calendar: COMMENT (Cyrillic) did not round-trip")
    check(back["ATTENDEE"].params.get("CN") == CN, "calendar: ATTENDEE CN did not round-trip")
except Exception as exc:  # noqa: BLE001
    fail(f"calendar: from_ical raised {exc!r}")

# 8. The repository's own tests of the fold, and the tests whose expected
# output encodes the fold position, stay green. These are the nine tests a
# space fold turns red at the base, observed 2026-11-10 with the configured
# runner (pyproject.toml testpaths = src/icalendar/tests).
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
            [TEST_PYTHON, "-X", "utf8", "-m", "pytest", "-q", "-p", "no:cacheprovider", "--no-header", *TEST_FILES],
            cwd=ROOT, capture_output=True, text=True, env=env,
        )
        if result.returncode != 0:
            tail = " | ".join(result.stdout.strip().splitlines()[-6:])
            fail(f"tests: the fold tests are red: {tail}")

# 9. The fold tests still exist and still carry their assertions.
KEPT = {
    "src/icalendar/parser/string.py": [
        'assert isinstance(line, str)',
        'assert "\\n" not in line',
        'def _foldline(line: str, limit: int = 75, fold_sep: str = "\\r\\n ") -> str:',
        "foldline = deprecate_for_version_8(_foldline)",
    ],
    "src/icalendar/tests/test_icalendar.py": [
        "def test_fold_line(self):",
        "def test_long_lines(self):",
        "def test_contentline_class(self):",
        'assert _foldline("foo") == "foo"',
        'assert _foldline("foobar", limit=4) == "foo\\r\\n bar"',
        "with pytest.raises(AssertionError):",
        "ЮЯ",
    ],
    "src/icalendar/tests/test_parsing.py": [
        "def test_foldline_does_not_split_escape_sequences_issue_1501(",
        "def test_foldline_does_not_split_escape_sequences_across_multiple_lines_issue_1501(",
        '@pytest.mark.parametrize("line_limit", range(60, 91))',
    ],
}
for rel, needles in KEPT.items():
    path = os.path.join(ROOT, rel)
    try:
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
    except OSError as exc:
        fail(f"kept lines: cannot open {rel}: {exc!r}")
        continue
    for needle in needles:
        check(needle in text, f"kept lines: {rel} lost {needle!r}")
    if rel.endswith("test_icalendar.py"):
        check(text.count('"123456789 "') >= 2, "the 123456789 fold assertions were removed")
        check(text.count("Vestibulum") >= 4, "the Lorem ipsum fold assertions were removed")
        check(text.count("\\r\\n ") >= 6, "the exact fold expectations of test_icalendar.py were weakened")

# 10. The diff against the base: allowed files, no deleted test, a news entry.
# content_line.py is not allowed: the caller needs no change (stricter reading,
# writer A). attr.py, cal/event.py, cal/todo.py and docs/ are allowed for
# doctest output only, a grader checks that by eye.
ALLOWED = re.compile(
    r"^(src/icalendar/parser/string\.py"
    r"|src/icalendar/tests/.*\.py"
    r"|news/[^/]+"
    r"|docs/.*"
    r"|src/icalendar/attr\.py"
    r"|src/icalendar/cal/event\.py"
    r"|src/icalendar/cal/todo\.py)$"
)
if RUN_DIFF:
    def git(*git_args):
        return subprocess.run(["git", "-C", ROOT, *git_args], capture_output=True, text=True)

    names = git("diff", "--name-only", BASE)
    untracked = git("ls-files", "--others", "--exclude-standard").stdout.split()
    if names.returncode != 0:
        fail(f"diff: git diff against {BASE} failed: {names.stderr.strip()}")
    else:
        changed = names.stdout.split() + untracked
        for name in changed:
            if not ALLOWED.match(name):
                fail(f"diff: touches {name}, outside the landing set")
        deleted = git("diff", "--name-only", "--diff-filter=D", BASE).stdout.split()
        if deleted:
            fail(f"diff: deletes {deleted}")
        news_changed = [n for n in git("diff", "--name-only", "--diff-filter=M", BASE).stdout.split() if n.startswith("news/")]
        if news_changed:
            fail(f"diff: edits an existing change log entry {news_changed}")
        added = git("diff", "--name-only", "--diff-filter=A", BASE).stdout.split() + untracked
        if not any(n.startswith("news/") for n in added):
            fail("diff: no new change log entry under news/")
        if not any(n.startswith("src/icalendar/tests/") for n in changed):
            fail("diff: no test file changed or added under src/icalendar/tests/")

if not fails:
    print("PASS")
    sys.exit(0)
print("FAIL: " + fails[0])
for other in fails[1:12]:
    print("also: " + other)
if len(fails) > 12:
    print(f"also: and {len(fails) - 12} more")
sys.exit(1)
