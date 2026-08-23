### intent
In this project, an intent is a configuration for a specific action or behavior in the Obsidian plugin. It is declared in several files, including `src/intents/frontmatter.ts`, `src/intents/index.ts`, and `intentsSchema.yaml`. An intent has various properties such as `make_a`, `hidden`, and `disabled` that can be set to specific values or defaults.

### template
In this project, a template is a file that contains a set of variables and their values, used to generate new notes in Obsidian. It is written down in various files such as `src/intents/frontmatter.ts`, `src/templates/index.ts`, and `README.md`. The purpose of a template is to provide a pre-defined structure for creating new notes with specific content.

### prompt
In this project, a prompt is ... a user input request in the Obsidian app.

### variable
In this project, a variable is ...

A data structure that holds a value and can be used in templates to generate dynamic content. It is declared in the `src/intents/frontmatter.ts` file and used throughout the project in various files, including `src/variables/providers/index.ts`, `src/variables/providers/natural_date.ts`, `src/variables/providers/folder.ts`, etc.

### variable_type
In this project, a variable type is ... TemplateVariableType. It is written down in the `src/intents/frontmatter.ts` file and used throughout various files to define different types of template variables.

### provider
In this project, a provider is ...

A type of variable parser or getter that provides values for template variables in the Obsidian app. It is declared and used in various files, including `src/variables/providers/index.ts`, `src/intents/frontmatter.ts`, and `src/variables/templateVariables.ts`.

### frontmatter
In this project, a frontmatter is metadata at the start of a note.

### global_intent
In this project, a global intent is ...

It's a type of Intent object that can be accessed globally throughout the program. It's declared in `src/settings/settings.ts` and used in various files such as `src/main.ts`, `src/intents/intents.ts`, and `src/templates/templates.ts`.

### selection
In this project, a selection is ...

A selection is an EditorSelection object that represents the currently selected text in the editor. It is used to determine the text to be used for creating notes or populating prompts.

It can be found in several files, including `src/intents/intents.ts`, `README.md`, and `src/settings/settings.ts`.

### filter_set
In this project, a filter set is a collection of notes that are filtered based on certain criteria. It is used in various files such as `src/intents/frontmatter.ts`, `src/intents/intents.ts`, and `README.md` to filter the list of notes shown. A filter set can be defined in the `intentsSchema.yaml` file, which specifies the name of the filter set and its properties. The filter set is then used to filter the notes based on the specified criteria.
