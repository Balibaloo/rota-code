### intent
In this project, an intent is a template for generating new notes that can be stored in either a specific note designated by the plugin's settings (global intent) or extracted from the active note.

### template
In this project, a template is a pre-defined structure for generating new notes, typically stored in a specific note designated by the plugin's settings or extracted from the active note.

### prompt
In this project, a prompt is ...

A template or question used to generate new notes, typically stored in the plugin's settings or extracted from the active note. It is written down in various files such as `intentsSchema.yaml`, `src/intents/frontmatter.ts`, and `src/variables/suggest.ts`. The purpose of a prompt is to provide users with a starting point for creating new notes based on templates or intents.

### variable
In this project, a variable is a data structure that holds a value or a set of values used in the plugin's functionality. It is declared and used throughout various files, particularly in the `src/intents` and `src/variables` directories. Variables are essential for storing and manipulating user input, template contents, and other relevant data to generate new notes with intents.

### variable_type
In this project, a variable type is ... TemplateVariableType. It is written down in the `src/intents/frontmatter.ts` file and used to define the type of variables that can be extracted from front matter.

### provider
In this project, a provider is ...

A type of object that provides data or functionality to other parts of the system. It is declared in `src/variables/providers/index.ts` and used in various files throughout the codebase, including `src/intents/frontmatter.ts`, `src/variables/index.ts`, and `src/variables/templateVariables.ts`.

### frontmatter
In this project, a frontmatter is metadata stored at the top of a note. It's written down in various files, including `src/intents/frontmatter.ts` and `README.md`, and is used for parsing variables and intents.

### global_intent
In this project, a global intent is ...

* A type of intent stored in a specific note designated by the plugin's settings.
* Written down in `src/settings/settings.ts` and used throughout the codebase.
* Used as a fallback when no note intents are found, allowing users to select an intent from either their global settings or the active note's contents.

### selection
In this project, a selection is ... an EditorSelection object that represents the currently selected text in the active note. It is used to gather variables and create new notes with intent from the active note.

### filter_set
A filter set is a collection of rules used to filter notes, defined in the plugin's settings and stored as a note filter set. It is used to reduce the number of notes shown to the user.
