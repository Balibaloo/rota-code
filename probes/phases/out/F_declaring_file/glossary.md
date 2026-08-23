### intent  (opened src/intents/index.ts)
In this project, an intent is a template for generating new notes that contains metadata and variables. It is written down in the `src/intents/index.ts` file as part of the plugin's code, and it is used to create a new note with specific properties and content based on user selection.

### template  (opened src/templates/index.ts)
In this project, a template is a predefined structure for generating new notes, defined as an object with properties such as name, path, and disabled status. It is written down in the `src/templates/index.ts` file and used by the plugin to create new notes based on user selection.

### prompt  (opened src/variables/suggest.ts)
In this project, a prompt is a modal window used to input data from the user. It is written down in the `GenericInputPrompt` class of the `suggest.ts` file and is used for various purposes such as creating new notes with intents or templates.

### variable  (opened src/intents/frontmatter.ts)
In this project, a variable is a named value that can be used in templates or intents to customize the output of a new note. It is written down in the frontmatter of a note or in the plugin's settings, and it is used for specifying properties such as output filename, output folder path, and variables.

### variable_type  (opened src/variables/index.ts)
In this project, a variable type is ... a data structure that holds information about a template or intent, including its name, type, and properties. It is written down in the `TemplateVariable` type definition in the `src/variables/index.ts` file, and it is used to store metadata for templates and intents.

### provider  (opened src/variables/providers/index.ts)
In this project, a provider is ... a function or object that supplies data to the application, such as variable parsers and getters for different types of template variables.

### frontmatter  (opened src/variables/providers/folder.ts)
In this project, a frontmatter is ... metadata stored in the YAML header of a note file.

### global_intent  (opened src/intents/index.ts)
In this project, a global intent is an intent stored in a specific note designated by the plugin's settings.

### selection  (opened src/intents/intents.ts)
In this project, a selection is an EditorSelection object that represents the user's current text selection in the active editor. It is written down in various places throughout the code, including in the `listSelections()` method of the `editor` property of the `activeEditor` object, and is used to determine whether the user is creating multiple notes or not.

### filter_set  (opened src/intents/frontmatter.ts)
In this project, a filter set is a collection of rules used to narrow down the list of notes shown in Obsidian. It is declared in various files, including `src/intents/frontmatter.ts` and `README.md`, and is used to implement features such as filtering notes by content.
