import ast, sys
sys.path.insert(0, "C:/Users/roman/rota_review43")
from rota.onboarding import indexer, languages

def check(rel):
    target = "C:/Users/roman/rota_review43/" + rel
    src = open(target, "rb").read()
    lang = languages.for_path(rel)
    facts = indexer.parse_file(rel, src, lang)
    lines = src.decode("utf-8", "replace").splitlines()
    tree = ast.parse(src)
    truth = {}
    for n in tree.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            truth[n.name] = (n.lineno - 1, n.end_lineno)
    bad = same = missing = 0
    examples = []
    for name, kind, s, e in facts.symbols:
        if name in truth:
            if (s, e) == truth[name]:
                same += 1
            else:
                bad += 1
                if len(examples) < 6:
                    examples.append((name, (s, e), truth[name]))
        else:
            missing += 1
    print("%-42s symbols=%3d match_ast=%3d differ=%3d not_top_level=%3d"
          % (rel, len(facts.symbols), same, bad, missing))
    for ex in examples:
        print("    differ", ex)
    return facts, lines

for rel in ("rota/onboarding/indexer.py", "rota/core/runner.py",
            "rota/onboarding/languages.py", "rota/llm/discover.py"):
    check(rel)

# feed the two numbers straight to code.source's slice and show the definition
facts, lines = check("rota/onboarding/languages.py")
for name, kind, s, e in facts.symbols[:6]:
    body = lines[s:e]
    print()
    print("%s (%s) lines[%d:%d] -> %d lines" % (name, kind, s, e, len(body)))
    print("  first:", repr(body[0])[:90])
    print("  last :", repr(body[-1])[:90])
    print("  line after the span:", repr(lines[e])[:70] if e < len(lines) else "<eof>")
