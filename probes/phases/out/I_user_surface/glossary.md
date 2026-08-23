### intent
In this project, an intent is a configuration object that defines the behavior of a specific action or task, written in various files such as `src/intents/index.ts` and `src/intents/frontmatter.ts`, used to configure the program's behavior when triggered.

### template
In this project, a template is a predefined structure or format for generating notes, defined in the code under various files and used to configure the behavior of intents when triggered.

### prompt
In this project, a prompt is a user-defined input field that can be used to create notes, defined under the "with_prompts" property in the intent schema.

### variable
In this project, a variable is [what a user writes, and what happens to it] a value or template that the program uses to generate prompts for notes.

### variable_type
In this project, a variable type is [what a user writes, and what happens to it] a data structure that defines the format of a value or template property.

### provider
In this project, a provider is an object that contains functions for parsing and getting variables, used in various parts of the code to manage data.

### frontmatter
In this project, a frontmatter is metadata written at the start of a note, used to configure behavior and generate prompts.

### global_intent
In this project, a global intent is ... a predefined intent that can be used across multiple notes and templates.

### selection
In this project, a selection is an EditorSelection object that represents the user's current text selection in Obsidian. It is written down in various files such as src/intents/intents.ts and used to determine how to load intents into the system, generate prompts for values and templates, and create notes based on user input.

### filter_set
In this project, a filter set is a collection of rules used to select and display notes based on user-defined criteria. It is declared in various files, including `src/intents/frontmatter.ts`, `src/intents/intents.ts`, and `src/main.ts`.
