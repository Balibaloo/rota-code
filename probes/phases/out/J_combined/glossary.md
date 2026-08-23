### intent
In this project, an intent is a thing in the code that represents a user's configuration and behavior when triggered, defined by the user as a list of properties and templates, used to configure the behavior of each intent when triggered. It is stored in the `Intent` type, which is declared in `src/intents/index.ts`, and can be imported from other notes or made available globally.

### template
In this project, a template is a thing in the code that defines a structure for generating note content, and it's used by the program to create notes. It's defined under the "with_templates" property of an intent, and has its own set of properties such as called value, at_path, and with_name. The program uses this information to generate prompts for values and templates when creating notes.

### prompt
In this project, a prompt is what the user specifies under the "with_prompts" property of an intent.

### variable
In this project, a variable is a thing in the code that holds a value or template for a note, used to configure intent behavior and generate prompts. It can be defined under various properties such as "with_templates" or "with_prompts", and its type may vary depending on the context (e.g., TemplateVariableVariables_NaturalDate).

### variable_type
In this project, a variable type is ... TemplateVariableType. It is a thing in the code, not the program itself and not the user's goal. A user or the code writes it down when defining templates associated with an intent, which are defined under the "with_templates" property. The program uses this information to generate prompts for values and templates when creating notes based on these types.

### provider
In this project, a provider is [a variable that holds an object used to retrieve and parse variables from the app, specifically for intents and templates].

### frontmatter
In this project, a frontmatter is metadata about the note that can be edited and contains information such as intents, templates, and prompts. It is written at the start of a note in a special place called the Frontmatter area, and its purpose is to provide context for generating new notes based on templates or intents.

### global_intent
In this project, a global intent is a collection of intents imported from other notes and made available globally through the plugin's settings. It is defined in the `settings` file as an array of Intent objects, which are stored in a specific note designated by the plugin's settings. The user specifies where their intents are imported from, and the program uses this information to load the intents into the system.

### selection
In this project, a selection is an array of EditorSelection objects that the code writes down in the `selections` variable when it calls `listSelections()` on the active editor. It represents multiple ranges within a single note selected by the user.

### filter_set
In this project, a filter set is a collection of rules and conditions applied to notes, used in various filtering operations throughout the code.
