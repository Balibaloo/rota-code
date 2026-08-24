"""The click consult questions, preregistered in probes/click/answer_key.yaml.

Written from the source before the first understanding session ran; the
expected answers are truths about click 8.5.0.dev, not predictions about the
run. `consult.py --questions probes.click.questions` reads these.
"""

QUESTIONS = [
    ("A maintainer renames `echo` to `print_out` throughout src/click and "
     "the build passes. Who is affected, and how do they find out?",
     "every downstream program importing click.echo -- ImportError/"
     "AttributeError the moment their program starts; loud, ecosystem-wide"),
    ("What is the difference between an option and an argument here?",
     "both are Parameters on a command; an option is named (--name), "
     "optional by default, can prompt and read envvars; an argument is "
     "positional, required by default"),
    ("When an option's value is not on the command line, where else can it "
     "come from, and in what order?",
     "envvar, the context's default_map, the declared default; prompt if "
     "still missing and prompt is set; ParameterSource records which won"),
    ("A user types a value that a Choice option does not allow. What "
     "exactly happens?",
     "conversion fails with an invalid-choice UsageError (exit code 2) "
     "naming the allowed values; loud"),
    ("How does a group decide which command runs, and what does the user "
     "see when the name does not exist?",
     "Group resolves the first argument via get_command(name); a missing "
     "name raises NoSuchCommand (a UsageError) -- 'No such command'"),
    ("What is `ctx.obj`, and how does a subcommand get at it?",
     "an arbitrary user object on the Context, inherited down the chain; "
     "pass_context / pass_obj / make_pass_decorator hand it to callbacks; "
     "ensure_object creates it"),
    ("How does a user's shell get tab completion for a click program?",
     "the _{PROG}_COMPLETE=<shell>_source protocol emits a script the user "
     "sources in their shell rc; ShellComplete subclasses implement bash, "
     "zsh, fish"),
    ("How do you test a click command without running a real shell?",
     "CliRunner().invoke(cmd, args) from click.testing, returning a Result "
     "with output and exit_code"),
]
