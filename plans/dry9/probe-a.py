"""Hidden probe of dry run 9, writer A.

Run from a folder outside the subject repository, against the merged
icalendar checkout:

    python probe-a.py <checkout root> [<python with pytest, dateutil,
    tzdata and pytz>]

Prints PASS, or FAIL and the first failure of each check. The second
argument is the interpreter that runs the repository's own fold tests.
It defaults to the interpreter that runs this script.
"""

import os
import subprocess
import sys

root = os.path.abspath(sys.argv[1])
test_python = sys.argv[2] if len(sys.argv) > 2 else sys.executable
sys.path.insert(0, os.path.join(root, "src"))

from icalendar.parser.content_line import UFOLD, Contentline  # noqa: E402
from icalendar.parser.string import _foldline  # noqa: E402

LIMIT = 75
SEP = "\r\n "
fails = []


def parts_of(folded):
    return folded.split(SEP)


def check(cond, message):
    if not cond:
        fails.append(message)


def unfold(folded):
    return UFOLD.sub("", folded)


# 1. A long line of words folds at a space, and no word is split.
words = "DESCRIPTION:" + " ".join(["word"] * 40)
folded = _foldline(words)
parts = parts_of(folded)
check(len(parts) > 1, "40 words: the line did not fold")
for i in range(len(parts) - 1):
    left, right = parts[i], parts[i + 1]
    at_space = left.endswith(" ") or right.startswith(" ")
    check(at_space, f"40 words: fold {i} is not at a space: {left[-6:]!r} | {right[:6]!r}")
check(unfold(folded) == words, "40 words: unfold does not give the input back")

# 1b. Words of twelve characters, the same checks.
long_words = "SUMMARY:" + " ".join(f"alpha{i:02d}bravo" for i in range(14))
folded = _foldline(long_words)
parts = parts_of(folded)
for i in range(len(parts) - 1):
    left, right = parts[i], parts[i + 1]
    check(
        left.endswith(" ") or right.startswith(" "),
        f"12-char words: fold {i} is not at a space: {left[-6:]!r} | {right[:6]!r}",
    )
check(unfold(folded) == long_words, "12-char words: unfold does not give the input back")

# 2. Multi-octet characters: no UTF-8 sequence splits, octets are counted.
for label, text in (
    ("80 x U+00E9", "é" * 80),
    ("80 x U+20AC", "€" * 80),
    ("Cyrillic", "DESCRIPTION:АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭЮЯ"),
):
    folded = _foldline(text)
    parts = parts_of(folded)
    check(len(parts) > 1, f"{label}: the line did not fold")
    for i, p in enumerate(parts):
        try:
            octets = len(p.encode("utf-8"))
        except UnicodeEncodeError:
            fails.append(f"{label}: part {i} is not valid Unicode text")
            continue
        check(octets < LIMIT, f"{label}: part {i} has {octets} octets, limit is below {LIMIT}")
    check(unfold(folded) == text, f"{label}: unfold does not give the input back")
    wire = folded.encode("utf-8")
    for i, line in enumerate(wire.split(b"\r\n")):
        check(len(line) <= LIMIT, f"{label}: wire line {i} has {len(line)} octets, over {LIMIT}")
        try:
            line.decode("utf-8")
        except UnicodeDecodeError:
            fails.append(f"{label}: wire line {i} splits a UTF-8 sequence")

# 2b. Words of two-octet characters fold at a space too.
cyr_words = "SUMMARY:" + " ".join(["слово"] * 20)
folded = _foldline(cyr_words)
parts = parts_of(folded)
check(len(parts) > 1, "Cyrillic words: the line did not fold")
for i in range(len(parts) - 1):
    left, right = parts[i], parts[i + 1]
    check(
        left.endswith(" ") or right.startswith(" "),
        f"Cyrillic words: fold {i} is not at a space: {left[-6:]!r} | {right[:6]!r}",
    )
check(unfold(folded) == cyr_words, "Cyrillic words: unfold does not give the input back")

# 3. No folded part exceeds the octet limit, over a mix of inputs.
mix = [
    words,
    long_words,
    "X:" + "a" * 200,
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
for text in mix:
    folded = _foldline(text)
    for i, p in enumerate(parts_of(folded)):
        octets = len(p.encode("utf-8"))
        check(octets < LIMIT, f"limit: part {i} of {text[:20]!r}... has {octets} octets")
    check(unfold(folded) == text, f"round trip: {text[:30]!r}... does not unfold to the input")
    check("\n" not in folded.replace(SEP, ""), f"separator: a lone newline in the fold of {text[:20]!r}")
    check(SEP in folded or len(text.encode()) < LIMIT, f"separator: {text[:20]!r} folded with another separator")

# 4. A single word longer than the limit still folds, and nothing is lost.
one_word = "X:" + "a" * 200
folded = _foldline(one_word)
parts = parts_of(folded)
check(len(parts) >= 3, f"long word: {len(parts)} parts, expected at least 3")
check(unfold(folded) == one_word, "long word: unfold does not give the input back")
check(folded.replace(SEP, "") == one_word, "long word: characters lost or added")

# 5. The promises that stay as before.
check(_foldline("foo") == "foo", "short line changed")
check(_foldline("foobar", limit=4) == "foo\r\n bar", "foobar limit 4 changed")
check(
    _foldline("DESCRIPTION:АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭЮЯ")
    == "DESCRIPTION:АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭ\r\n ЮЯ",
    "the Cyrillic expectation of test_fold_line changed",
)
check(_foldline("foobar", limit=4, fold_sep="\n ") == "foo\n bar", "fold_sep parameter lost")
try:
    _foldline("привет".encode())
    fails.append("bytes input no longer raises AssertionError")
except AssertionError:
    pass
try:
    _foldline("a\nb")
    fails.append("a newline in the input no longer raises AssertionError")
except AssertionError:
    pass
for seq in (r"\n", r"\N", r"\,", r"\;", r"\\", "^n", "^^", "^'"):
    for limit in range(60, 91):
        prefix = "DESCRIPTION:" + ("a" * (limit - len("DESCRIPTION:") - 2))
        line = prefix + seq + "after fold"
        f = _foldline(line, limit=limit)
        check(SEP in f, f"escape rule: {seq!r} at limit {limit} did not fold")
        check(
            (seq[0] + SEP + seq[1]) not in f,
            f"escape rule: {seq!r} split across the fold at limit {limit}",
        )
cl = Contentline("DESCRIPTION:" + " ".join(["word"] * 40)).to_ical()
check(isinstance(cl, bytes), "Contentline.to_ical no longer returns bytes")
check(b"\r\n " in cl, "Contentline.to_ical no longer folds with CRLF and a space")
check(
    UFOLD.sub("", cl.decode("utf-8")) == "DESCRIPTION:" + " ".join(["word"] * 40),
    "Contentline.to_ical does not round-trip",
)
# A complete calendar round-trips with a long summary.
from icalendar import Calendar, Event  # noqa: E402

summary = " ".join(["meeting"] * 30) + " " + "é" * 40
ev = Event()
ev.add("summary", summary)
cal = Calendar()
cal.add_component(ev)
out = cal.to_ical()
for i, line in enumerate(out.split(b"\r\n")):
    check(len(line) <= LIMIT, f"calendar: wire line {i} has {len(line)} octets")
back = Calendar.from_ical(out)
check(str(back.walk("VEVENT")[0]["summary"]) == summary, "calendar: the summary does not round-trip")

# 6. The repository's own tests of the fold file stay green.
r = subprocess.run(
    [
        test_python,
        "-X",
        "utf8",
        "-m",
        "pytest",
        "-q",
        "-p",
        "no:cacheprovider",
        "src/icalendar/tests/test_icalendar.py",
        "src/icalendar/tests/test_parsing.py",
    ],
    cwd=root,
    capture_output=True,
    text=True,
    env={**os.environ, "PYTHONPATH": "src", "PYTHONUTF8": "1"},
)
if r.returncode != 0:
    tail = (r.stdout.strip().splitlines() or ["no output"])[-1]
    fails.append(f"the fold tests of the checkout are red: {tail}")

# 7. The fold tests still exist and still carry their assertions.
test_icalendar = open(
    os.path.join(root, "src/icalendar/tests/test_icalendar.py"), encoding="utf-8"
).read()
test_parsing = open(
    os.path.join(root, "src/icalendar/tests/test_parsing.py"), encoding="utf-8"
).read()
check("def test_fold_line" in test_icalendar, "test_fold_line was deleted")
check('_foldline("foobar", limit=4) == "foo\\r\\n bar"' in test_icalendar, "the foobar assertion was removed")
check("ЮЯ" in test_icalendar, "the Cyrillic assertion was removed")
check(
    "def test_foldline_does_not_split_escape_sequences_issue_1501" in test_parsing,
    "the issue 1501 test was deleted",
)
check(
    "def test_foldline_does_not_split_escape_sequences_across_multiple_lines_issue_1501" in test_parsing,
    "the second issue 1501 test was deleted",
)
check('range(60, 91)' in test_parsing, "the issue 1501 limit range was narrowed")
check("def test_long_lines" in test_icalendar, "test_long_lines was deleted")
check("def test_contentline_class" in test_icalendar, "test_contentline_class was deleted")
check(test_icalendar.count('"123456789 "') >= 2, "the 123456789 fold assertions were removed")
check(test_icalendar.count("Vestibulum") >= 4, "the Lorem ipsum fold assertions were removed")

print("PASS" if not fails else "FAIL: " + "; ".join(fails[:12]) + (f"; and {len(fails) - 12} more" if len(fails) > 12 else ""))
sys.exit(0 if not fails else 1)
