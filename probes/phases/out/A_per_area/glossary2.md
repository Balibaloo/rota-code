### intent
In this project, an intent is a custom action that can be triggered in Obsidian, defined as a type in the `src/intents/index.ts` file and used throughout the codebase to handle various tasks.

### template
In this project, a template is a reusable piece of code that defines the structure and content of an Obsidian note or prompt. It is declared in various files throughout the `src` directory, particularly in `src/templates/index.ts`, and used in multiple areas of the codebase to populate templates with variable values.

### prompt
In this project, a prompt is a user input request used to populate template variables in an Obsidian note-taking app. It is declared in the `src/variables/suggest.ts` file and used throughout the codebase, particularly in the `src/intents/frontmatter.ts` and `README.md` files.

### variable
In this project, a variable is a template value used to populate prompts and templates in an Obsidian note-taking app. It is declared in the `src/variables` area of the codebase, specifically in files such as `index.ts`, `providers/folder.ts`, and `templateVariables.ts`. Variables are used for different data types, including text, numbers, natural dates, notes, and folders, and are parsed from frontmatter values in Obsidian notes.

### variable_type
In this project, a variable type is ... a data type that represents the kind of value a template variable can hold.

### provider
In this project, a provider is ... a function or object that supplies data to the template variables, specifically for different data types such as text, numbers, natural dates, notes, and folders. It is declared in `src/variables/providers/index.ts` and used in various areas of the codebase, including `src/intents/frontmatter.ts`.

### frontmatter
In this project, a frontmatter is ... metadata stored at the top of an Obsidian note.

### global_intent
In this project, a global intent is ... an Intent object that represents a custom action available globally in Obsidian.

### selection
In this project, a selection is an EditorSelection object that represents the currently selected text in the Obsidian editor. It is used to populate prompts and templates with user-selected values.

### filter_set
In this project, a filter set is a configuration of note filters used to narrow down the list of notes shown in Obsidian. It is declared in various files throughout the codebase, including `src/intents/frontmatter.ts`, `src/intents/intents.ts`, and `README.md`.
