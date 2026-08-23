### intent
In this project, an intent is a data structure that represents a user's goal or objective, defined in the code as a type with specific properties and used to create new notes based on custom templates and variables.

### template
In this project, a template is a predefined structure for creating new notes that includes variables and formatting options. It is written down in the `src/templates` directory and used to create new notes based on user selection.

### prompt
In this project, a prompt is a data structure that contains variables and templates to create notes. It is defined in the `intentsSchema.yaml` file and used throughout the codebase, particularly in the `src/intents/frontmatter.ts` and `src/variables/suggest.ts` files.

### variable
In this project, a variable is a data point that can be used in a template to create a new note, and it is declared in various files throughout the codebase.

### variable_type
In this project, a variable type is a data structure that defines the format and behavior of a template variable. It is declared in `src/variables/providers/index.ts` and used throughout the codebase to validate and parse frontmatter variables.

### provider
In this project, a provider is an object that contains functions for parsing and getting variables from the app's settings. It is declared in `src/variables/providers/index.ts` and used throughout the code to gather values for template variables.

### frontmatter
In this project, a frontmatter is metadata stored at the top of a note in Obsidian, used to parse and extract intents for creating new notes.

### global_intent
In this project, a global intent is ... [understanding] a data structure that represents an intent with its associated template and variables, stored in the user's settings as a list of intents in a specific note.

### selection
In this project, a selection is an instance of the EditorSelection class, representing a range of text in the active editor, used to extract variables and create new notes.

### filter_set
In this project, a filter set is a collection of rules used to select and display notes based on specific criteria, defined in the user's settings. It is written down in various files, including `src/settings/settings.ts` and `README.md`, and is used to filter the list of notes shown to the user.
