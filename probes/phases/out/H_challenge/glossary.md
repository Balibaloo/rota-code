### intent
first: In this project, an intent is a template for generating new notes. It is declared in the `src/intents/index.ts` file and used throughout the codebase to create new notes with specific content.
objection: The single most important thing it gets wrong or leaves out is that an intent can also be a template for generating new notes, not just a template. "src/templates/templates.ts:7: new Notice(`Error: ${
final: In this project, an intent is a template for generating new notes or a specific note content. It is declared in the `src/intents/index.ts` file and used throughout the codebase to create new notes with specific content, including templates for generating new notes.

### template
first: In this project, a template is a predefined structure or pattern for generating new notes, typically stored in files and used as a starting point for user input.
objection: Typically stored in files is incorrect, as the code shows that templates can also be retrieved from FrontMatterCache (src/intents/frontmatter.ts:40).
final: In this project, a template is a predefined structure or pattern for generating new notes, which can be stored in files or retrieved from FrontMatterCache, and used as a starting point for user input.

### prompt
first: In this project, a prompt is ... a thing in the code that represents user input or a value to be filled in, used for creating notes with templates or intents.
objection: The code gets it wrong by implying that a prompt is only used for creating notes with templates or intents, when in fact the `GenericInputPrompt` class and its usage suggest that prompts can be used t
final: In this project, a prompt is ... a thing in the code that represents user input or a value to be filled in, used for creating notes with templates or intents, and can also be used to input values for variables in general. It is defined in `src/variables/suggest.ts` as an instance of the `GenericInputPrompt` class, which extends the `Modal` class.

### variable
first: In this project, a variable is a named value that can be used in templates or notes, declared in frontmatter or defined by the plugin's settings.
objection: The single most important thing it gets wrong or leaves out is that variables can also be defined by the user in templates or notes, not just declared in frontmatter or defined by the plugin's setting
final: In this project, a variable is a named value that can be used in templates or notes, declared in frontmatter, defined by the plugin's settings, or defined by the user in templates or notes.

### variable_type
first: In this project, a variable type is ... a data structure that defines the format and constraints of a value in code. It is written down in various files such as `src/variables/providers/index.ts` and used throughout the plugin to validate and process user input.
objection: It gets it wrong by leaving out the fact that a variable type is not just a data structure, but also an enum that defines specific types of variables such as `TemplateVariableType.Number` or `Template
final: In this project, a variable type is an enum that defines specific types of variables, such as `TemplateVariableType.Number` or `TemplateVariableType.Folder`, used to validate and process user input. It is written down in files like `src/variables/providers/index.ts`.

### provider
first: In this project, a provider is ... a module that exports functions for parsing and getting variables, used in various parts of the code to handle variable-related logic.
objection: It gets the variable getters wrong, as it only mentions parsing functions. "export const variableProviderVariableParsers: {"
final: In this project, a provider is ... an object that exports functions for parsing and getting variables, used in various parts of the code to handle variable-related logic.

### frontmatter
first: In this project, a frontmatter is ... metadata stored at the top of a note file.
objection: RIGHT.
final: In this project, a frontmatter is metadata stored at the top of a note file, specifically in a special place called the Frontmatter section.

### global_intent
first: In this project, a global intent is ... an intent stored in a specific note designated by the plugin's settings.
objection: The single most important thing it gets wrong or leaves out is that the global intent is not stored in a specific note designated by the plugin's settings, but rather it appears to be stored in a sepa
final: In this project, a global intent is ... an intent stored in a note designated by the plugin's setting `globalIntentsNotePath`, which stores the path of that note.

### selection
first: In this project, a selection is ... an EditorSelection object representing the currently selected text in the active editor.
objection: The single most important thing it gets wrong or leaves out is that the sentence claims "a selection" is an EditorSelection object, but the code shows that a selection can be multiple selections (an a
final: In this project, a selection is an array of EditorSelection objects representing the currently selected text in the active editor, which can be multiple selections.

### filter_set
first: In this project, a filter set is ... a collection of rules or criteria used to narrow down the list of notes shown in Obsidian, defined by the user through settings and stored as a string.
objection: The single most important thing it gets wrong or leaves out is that a filter set is not stored as a string, but rather as an object. "a collection of rules or criteria used to narrow down the list of 
final: Here's a revised attempt at describing the filter set: In this project, a filter set is ... a collection of rules or criteria used to narrow down the list of notes shown in Obsidian, defined by the user through settings and stored as an object.
