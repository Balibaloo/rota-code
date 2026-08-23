### intent
In this project, an intent is a custom action that can be triggered in Obsidian. It is declared in the `src/intents/frontmatter.ts` file and used throughout the codebase to handle various tasks.

### template
In this project, a template is a reusable piece of content that can be populated with variable values to create a new note or modify an existing one. It is written down in various files throughout the codebase, particularly in the `src/templates` area and referenced in other areas such as `src/intents`.

### prompt
In this project, a prompt is a user input field used to populate template variables in an Obsidian note-taking app. It is written down in various files such as README.md, intentsSchema.yaml, and src/variables/suggest.ts. Its purpose is to provide a way for users to enter values or select options that are then used to create notes.

### variable
In this project, a variable is ...

A template variable used to populate prompts and templates in an Obsidian note-taking app. It is declared in the `src/intents/frontmatter.ts` file and used throughout the codebase.

### variable_type
In this project, a variable type is ...

A TemplateVariableType is a data type used to represent template variables in an Obsidian note-taking app. It is declared in the `src/intents/frontmatter.ts` file and is used to manage template variables for different data types such as text, numbers, natural dates, notes, and folders.

### provider
In this project, a provider is ...

A function or object that provides data to the application, specifically in the context of template variables. It is declared in `src/variables/providers/index.ts` and used in various areas of the codebase, including `src/intents/frontmatter.ts`.

### frontmatter
In this project, a frontmatter is metadata stored at the top of an Obsidian note in a special place, used to populate prompts and templates.

### global_intent
In this project, a global intent is ...

* A type of custom action that can be triggered in Obsidian.
* Declared in the `src/intents` area and used throughout the codebase.
* Used to define settings and notices within the plugin.

### selection
In this project, a selection is ...

A selection is an EditorSelection object that represents the currently selected text in an Obsidian editor. It is used to populate prompts and templates with user-selected text.

### filter_set
In this project, a filter set is ...

A data structure used to manage and apply filters to notes in an Obsidian plugin. It is defined in various files throughout the codebase, including `src/intents/frontmatter.ts`, `src/intents/intents.ts`, and `src/settings/settings.ts`.
