"""
What a language looks like, as data.

The indexer knows three things about any language: which files belong to it,
which syntax nodes *define* something worth naming, and which nodes *name a
dependency*. Everything after that — walking the tree, pulling out a name,
resolving an import to a file, counting fan-in — is the same regardless of what
was parsed.

That split is the point. Adding a language is a row in this table and a grammar
in the pack; it is never a branch in the indexer. The alternative was a Python
`ast` pass, which would have been half the code and would have made "index the
project" mean "index the project, if it is Python".

Two rules make the generic half work across all of them:

  * **A definition's name is its `name` field.** Every grammar in the pack that
    has definitions gives them one, so the name is read the same way whether the
    node is a `function_definition` or a `func_declaration`.
  * **An import's target is the string or dotted name inside it.** Import syntax
    varies wildly; what is being imported is a literal in all of them.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Language:
    name: str                      # the grammar's name in the pack
    suffixes: tuple[str, ...]
    definitions: tuple[str, ...]   # node types that introduce a symbol
    imports: tuple[str, ...]       # node types that name a dependency


LANGUAGES: tuple[Language, ...] = (
    Language(
        name="python",
        suffixes=(".py",),
        definitions=("function_definition", "class_definition"),
        imports=("import_statement", "import_from_statement",
                 "future_import_statement"),
    ),
    Language(
        name="javascript",
        suffixes=(".js", ".jsx", ".mjs"),
        definitions=("function_declaration", "class_declaration",
                     "method_definition", "generator_function_declaration"),
        imports=("import_statement", "export_statement"),
    ),
    Language(
        name="typescript",
        suffixes=(".ts", ".tsx"),
        definitions=("function_declaration", "class_declaration",
                     "method_definition", "interface_declaration",
                     "type_alias_declaration"),
        imports=("import_statement", "export_statement"),
    ),
    Language(
        name="go",
        suffixes=(".go",),
        definitions=("function_declaration", "method_declaration",
                     "type_declaration"),
        imports=("import_declaration",),
    ),
    Language(
        name="rust",
        suffixes=(".rs",),
        definitions=("function_item", "struct_item", "enum_item", "trait_item"),
        imports=("use_declaration",),
    ),
    Language(
        name="java",
        suffixes=(".java",),
        definitions=("class_declaration", "interface_declaration",
                     "method_declaration", "enum_declaration"),
        imports=("import_declaration",),
    ),
    Language(
        name="ruby",
        suffixes=(".rb",),
        definitions=("method", "class", "module", "singleton_method"),
        imports=("call",),          # `require` is an ordinary call; filtered later
    ),
)

BY_SUFFIX: dict[str, Language] = {
    suffix: lang for lang in LANGUAGES for suffix in lang.suffixes
}


def for_path(path: str) -> Language | None:
    dot = path.rfind(".")
    return BY_SUFFIX.get(path[dot:]) if dot >= 0 else None
