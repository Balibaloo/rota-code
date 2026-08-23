### intent
In this project, an intent is a data structure that represents a user's goal or objective, which can be used to create a new note with custom templates and variables. It is written down in the `intentsSchema.yaml` file and used throughout the plugin's codebase. Its purpose is to provide a way for users to define their intentions and have the plugin generate notes accordingly.

### template
In this project, a template is a pre-defined note structure with placeholders for variables that can be replaced with user-input values. It is written down in the `intentsSchema.yaml` file and used in various parts of the code, including the `src/intents/frontmatter.ts`, `src/templates/index.ts`, and `src/variables/index.ts` files.

### prompt
In this project, a prompt is a user-inputted value or template used to create notes. It is written down in the `intentsSchema.yaml` file and referenced in various code files, including `src/intents/frontmatter.ts`, `src/variables/suggest.ts`, and `manifest.json`.

### variable
In this project, a variable is ...

A data container with a specific type and value, used to store and retrieve information in notes. It is defined in the `intentsSchema.yaml` file and used throughout the codebase, particularly in the `src/intents/frontmatter.ts` and `src/variables/providers/index.ts` files.

### variable_type
In this project, a variable type is ...

A data structure that defines the format and properties of a template variable. It is written down in `src/intents/frontmatter.ts` and used to validate and parse variables from frontmatter.

### provider
In this project, a provider is an object that supplies variables to the plugin. It is defined in `src/variables/providers/index.ts` and used throughout the codebase.

### frontmatter
In this project, a frontmatter is metadata stored at the start of a note in a special place, used to parse intents and variables.

### global_intent
In this project, a global intent is ...

* A type of note that contains a list of intents.
* Stored in the user's settings file.
* Used to provide a list of available intents for the user to choose from.

### selection
In this project, a selection is ...

A selection is an EditorSelection object that represents the user's current selection in the Obsidian editor. It is used to extract text and variables from the selected area.

### filter_set
In this project, a filter set is a collection of notes that are filtered based on specific criteria. It is written down in the `settings` file and used to determine which notes are shown to the user.
