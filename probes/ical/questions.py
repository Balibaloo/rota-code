"""The icalendar consult questions, preregistered in probes/ical/answer_key.yaml.

Written from the source at commit 9961924 before the first understanding
session ran. `consult.py --questions probes.ical.questions` reads these.
"""

QUESTIONS = [
    ("A user has the text of an .ics file. How do they get a Calendar "
     "object, and how do they get identical text back out?",
     "Calendar.from_ical(text); cal.to_ical(); round-trip is the design -- "
     "unparseable values are preserved (vBroken) so the trip stays faithful"),
    ("What is a component here, and how do components nest?",
     "the building block (VCALENDAR, VEVENT, VTODO, VALARM...): a "
     "CaselessDict of properties plus subcomponents; walk() traverses"),
    ("What is the difference between a property and a parameter?",
     "a property is a component's content line (DTSTART, SUMMARY) with a "
     "typed value; a parameter modifies a property (TZID=, CN=) via the "
     "Parameters mapping"),
    ("Where does a DTSTART line's text become a Python datetime, and what "
     "decides which type parses which property?",
     "the prop/dt value types (vDatetime and kin) do from_ical; "
     "TypesFactory maps property names to types"),
    ("A maintainer renames Calendar.from_ical and the build passes. Who is "
     "affected, and how do they find out?",
     "every downstream program importing icalendar -- AttributeError when "
     "their code runs; loud, ecosystem-wide"),
    ("Parsing hits a property value it cannot parse. What happens -- an "
     "exception, a skip, or something else?",
     "the raw value is preserved as vBroken so serialisation round-trips; "
     "recorded on the component's errors list, not raised by default"),
    ("How does a VTIMEZONE become something datetime arithmetic can use?",
     "the timezone package converts VTIMEZONE to a tzinfo (zoneinfo when "
     "possible, custom otherwise); tzdata exists as a dependency for this"),
    ("What does the `icalendar` command a user gets on their PATH do?",
     "console script icalendar = icalendar.cli:main in pyproject "
     "[project.scripts]: previews a calendar's events"),
]
