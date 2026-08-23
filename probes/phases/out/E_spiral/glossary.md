### intent
In this project, an intent is a custom template and variable combination that can be used to create new notes with specific content. It is written down in the `intentsSchema.yaml` file and used throughout the plugin's codebase, particularly in the `src/intents` directory. The intent is for creating new notes with pre-defined templates and variables.

### template
In this project, a template is a pre-defined note structure with variables that can be used to create new notes. It is written down in the `src/templates/index.ts` file and is used for creating new notes based on user selection.

### prompt
In this project, a prompt is a customizable input field that allows users to enter values or select templates for creating notes. It is written down in various files such as `intentsSchema.yaml`, `src/intents/frontmatter.ts`, and `src/variables/suggest.ts`. The plugin uses prompts to gather user input and create new notes based on the selected template and variables.

### variable
In this project, a variable is ...

A data container with a specific type and value, used to store and manipulate user input in note templates. It is declared in the `src/intents/frontmatter.ts` file and used throughout the plugin's codebase.

### variable_type
In this project, a variable type is ...

A TemplateVariableType is a data type that represents the type of a template variable. It is declared in the `src/intents/frontmatter.ts` file and used to parse frontmatter and extract intents. The type is used to validate variables and provide variables to the plugin.

### provider
In this project, a provider is an object that supplies variables to the plugin. It is defined in `src/variables/providers/index.ts` and used throughout the codebase.

### frontmatter
In this project, a frontmatter is metadata stored at the top of a note in a specific format, used to extract intents and variables for template creation.

### global_intent
In this project, a global intent is ...

* A type of note template that can be used across multiple notes.
* Written down in the `intentsSchema.yaml` file and referenced throughout the codebase.
* Used to create new notes with custom templates and variables.

### selection
In this project, a selection is ...

A selection is an EditorSelection object that represents a range of text in the active editor. It is used to extract variables from the selected text and populate prompts.

### filter_set
In this project, a filter set is a collection of rules used to filter notes in Obsidian, defined by the user and stored in a specific note.
