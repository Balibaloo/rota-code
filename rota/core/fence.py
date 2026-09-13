"""
The fence: what a written file may reach, held to the criteria.

A fact about the file, not a judgement about the code. A file that imports
`socket` reaches the network. A file that calls `subprocess.run` starts a
process. A file that calls `shutil.rmtree` removes a tree. Each reach is
visible in the syntax tree, and each is refused unless a criterion of the
batch names that kind of behaviour in words.

This is not a sandbox. The harness runs the target project's own code by
design, the same as pytest does. The fence stops the accidental case, a
small model reaching for a capability nobody asked for, and says which
criterion would have to ask.
"""
from __future__ import annotations

import ast
import re

# kind -> (modules, attribute names, bare call names, words a criterion may use)
KINDS: dict[str, tuple[frozenset[str], frozenset[str], frozenset[str], tuple[str, ...]]] = {
    "network": (
        frozenset({"socket", "urllib", "http", "requests", "httpx", "aiohttp",
                   "ftplib", "smtplib", "imaplib", "poplib", "ssl", "websocket",
                   "websockets", "xmlrpc", "telnetlib"}),
        frozenset(), frozenset(),
        ("network", "http", "url", "web", "fetch", "download", "upload",
         "server", "socket", "api", "request", "internet", "email", "mail",
         "send", "endpoint", "client", "remote", "online")),
    "process": (
        frozenset({"subprocess", "pty"}),
        frozenset({"system", "popen", "execl", "execle", "execlp", "execv",
                   "execve", "execvp", "execvpe", "spawnl", "spawnv", "kill",
                   "killpg", "startfile"}),
        frozenset(),
        ("process", "command", "shell", "execute", "launch", "spawn",
         "terminal", "subprocess")),
    "remove": (
        frozenset(),
        frozenset({"rmtree", "remove", "unlink", "rmdir", "removedirs"}),
        frozenset(),
        ("delete", "remove", "clean", "erase", "purge", "discard",
         "uninstall")),
    "outside": (
        frozenset(),
        frozenset({"home", "expanduser", "expandvars", "chdir"}),
        frozenset(),
        ("home", "config", "global", "system", "environment", "user directory",
         "profile", "install", "settings", "absolute")),
    "dynamic": (
        frozenset({"ctypes", "marshal", "pickle", "shelve", "importlib"}),
        frozenset({"import_module", "load_module"}),
        frozenset({"eval", "exec", "__import__", "compile"}),
        ("plugin", "dynamic", "eval", "expression", "pickle", "serialise",
         "serialize", "load code", "extension", "native", "binary")),
}


def reaches(tree: ast.AST) -> list[tuple[str, str, int]]:
    """Every reach in the tree: (kind, what, line)."""
    out: list[tuple[str, str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                for kind, (mods, _a, _c, _w) in KINDS.items():
                    if root in mods:
                        out.append((kind, f"import {alias.name}", node.lineno))
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            for kind, (mods, attrs, _c, _w) in KINDS.items():
                if root in mods:
                    out.append((kind, f"from {node.module} import ...", node.lineno))
                for alias in node.names:
                    if alias.name in attrs and root in {"os", "shutil", "importlib"}:
                        out.append((kind, f"from {root} import {alias.name}", node.lineno))
        elif isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Name):
                for kind, (_m, _a, calls, _w) in KINDS.items():
                    if fn.id in calls:
                        out.append((kind, f"{fn.id}(...)", node.lineno))
                if fn.id == "open" and node.args:
                    lit = node.args[0]
                    if isinstance(lit, ast.Constant) and isinstance(lit.value, str):
                        if _escapes(lit.value):
                            out.append(("outside", f"open({lit.value!r})", node.lineno))
            elif isinstance(fn, ast.Attribute):
                for kind, (_m, attrs, _c, _w) in KINDS.items():
                    if fn.attr in attrs:
                        out.append((kind, f"{_dotted(fn)}(...)", node.lineno))
    seen: set[tuple[str, str, int]] = set()
    return [r for r in out if not (r in seen or seen.add(r))]


def _escapes(path: str) -> bool:
    p = path.replace("\\", "/")
    return p.startswith("/") or p.startswith("~") or ".." in p.split("/") \
        or re.match(r"^[A-Za-z]:/", p) is not None


def _dotted(node: ast.AST) -> str:
    if isinstance(node, ast.Attribute):
        return f"{_dotted(node.value)}.{node.attr}"
    if isinstance(node, ast.Name):
        return node.id
    return "?"


def named(kind: str, texts: list[str]) -> bool:
    """Does any criterion name this kind of behaviour, in a word?"""
    words = KINDS[kind][3]
    low = " ".join(t.lower() for t in texts)
    return any(re.search(rf"\b{re.escape(w)}", low) for w in words)


MANIFESTS = ("pyproject.toml", "requirements.txt", "setup.py", "setup.cfg",
             "Pipfile", "Pipfile.lock", "poetry.lock", "uv.lock", "constraints.txt")
MANIFEST_WORDS = ("dependency", "dependencies", "package", "install", "library",
                  "requirement", "requirements", "version bump", "release")


def check_manifest(path: str, criteria: list[str]) -> None:
    """
    A dependency manifest is what provisioning installs from, with pip, in
    the batch's environment. A file the model writes there is a package the
    model chose, and pip runs its setup. Refused unless a criterion names a
    dependency, a package or an install.
    """
    name = path.replace("\\", "/").split("/")[-1]
    if not (name in MANIFESTS or (name.startswith("requirements") and name.endswith(".txt"))):
        return
    low = " ".join(t.lower() for t in criteria)
    if any(w in low for w in MANIFEST_WORDS):
        return
    raise ValueError(
        f"{path} is a dependency manifest: what it names, pip installs and "
        f"runs in the batch's environment. No criterion of this batch names "
        f"a dependency, a package or an install, so this write is refused. "
        f"If the change needs a package, the criterion has to say so; "
        f"otherwise leave the manifest as it is")


def check(path: str, tree: ast.AST, criteria: list[str],
          baseline: ast.AST | None = None) -> None:
    """Raise ValueError for the first reach no criterion names.

    `baseline` is the file as it stood before the write. A reach the file
    already made is the project's, not this change's: clickI night 38
    (2026-09-13) refused every write to `utils.py` because click's own
    line 547 calls `os.path.expanduser`, and the batch could never commit.
    """
    had = {(k, w) for k, w, _ in reaches(baseline)} if baseline is not None else set()
    for kind, what, line in reaches(tree):
        if (kind, what) in had:
            continue
        if named(kind, criteria):
            continue
        raise ValueError(
            f"{path} reaches the {kind} at line {line} ({what}) and no "
            f"criterion of this batch names {_noun(kind)}. The code does only "
            f"what the criteria ask. If the behaviour is intended, the "
            f"criterion has to say so: name the criterion and the words it "
            f"lacks in your reply, and end. Otherwise write the file "
            f"without it")


def _noun(kind: str) -> str:
    return {"network": "the network, a server or an email",
            "process": "a process, a command or a shell",
            "remove": "deleting or removing anything",
            "outside": "a path outside the project",
            "dynamic": "loading or evaluating code"}[kind]
