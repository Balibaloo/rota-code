### intent
In this project, an intent is a data structure that represents a custom template and variables for creating notes. It is written down in the `intents` module and used to parse frontmatter and extract intents from user settings.

### template
In this project, a template is a predefined structure for creating new notes, defined in the code as a type and used to generate new notes with specific variables.

### prompt
In this project, a prompt is a user interface element that asks for input or selection from the user to create notes with custom templates and variables. It is declared in `src/variables/suggest.ts` and used throughout the codebase.

### variable
In this project, a variable is a data value that can be used in templates and notes, represented as intents or TemplateVariable objects, stored in frontmatter or user settings.

### variable_type
In this project, a variable type is ... a data type that represents the kind of value a template variable can hold.

### provider
In this project, a provider is a function or object that supplies variables to the plugin. It is declared in `src/variables/providers/index.ts` and used throughout the codebase, particularly in `src/intents/frontmatter.ts`.

### frontmatter
In this project, a frontmatter is metadata stored at the top of a note in a special place, used to parse intents and variables.

### global_intent
In this project, a global intent is a predefined template or set of variables stored in a specific note, used as a starting point for creating new notes.

### selection
In this project, a selection is an object representing a range of text in the editor, used to extract variables and create new notes. It is declared in `src/intents/intents.ts` and used throughout the plugin's codebase.

### filter_set
In this project, a filter set is a collection of rules and settings used to filter notes shown in the Obsidian app, stored as a note with a specific name.
