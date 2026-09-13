I want to add a new category of tools to the toolbox.
Codebase analysis tools

The first tool we will implement is "system_prompt_optimizer"

which will have the following parameters
1) run_prompt_glossary_optimisation, defaults to yes
2) run_system_glossary_optimisation, defaults to no

Each step of the flow (and subflows) will going to be carried out in its own LLM call with its own prompts.
The core flow of the tool is as follows:
1) Decompose the prompt into atomic statements
2) Categorize statements by their function/purpouse in the prompt
3) Cohesive reordering of atoms into a logical flow
(optional) Prompt Glossary Optimisation
(optional) System Glossary Optimisation
6) Narrative Synthesis 


Please instruct the LLM to ask the user if they would like to preform the optional steps

They are additional sub flows that input the full text and output the full text

# Prompt Glossary Optimisation
Its prompt is down below, please preserve all nouns, 


# System Glossary Optimisation

1) Identiffy components, output every component, symbol and name mentioned
2) Next to each component output its purpouse and value
3) Verbalise relationships, Hierarchies, and duplications 
4) Name synthesys, identiffy the clearest, purest possible naming for the element and if it differs keep track of it
5) Apply renaming with the differing symbols

output the renamed text but ALSO the list of differing symbols, before and after. This will be shown to the user as a second, optional output of this tool.

##### prompts for each of the steps is bellow

# Decomposition
```
Analyze the following text and decompose it into an exhaustive, atomic list of its core elements.

Guidelines for Decomposition:

Atomicity: Each element must be a single, irreducible unit of information. If an element contains a 'and' or 'also', split it into two separate elements.
Exhaustiveness: No detail, constraint, or implicit assumption should be omitted.
Categorization: Group the atomic elements into logical categories (e.g., Entities, Actions, Constraints, Goals, Dependencies).
Format: Present the result as a nested bulleted list.

```

# Categorization
```
Please take each statement and categorize it by its function in the prompt
Please keep the order of the statements the same
```

# Cohesive flow
```
Reorder the points into a cohesive flow of a system prompt
Keep them atomic
```

# Narrative synthesys
```
The Goal: Create a system prompt for a high-seniority AI agent that feels empowered and supported, not restricted. The agent should feel like a world-class expert who has been given a suite of powerful tools to make their life easier.

The Vibe: "The Empowered Expert"

Shift from Compliance to Empowerment: Do not use "MANDATORY," "MUST," or "PROTOCOL." Instead, frame requirements as "Professional Standards," "Best Practices," or "The Path of Least Resistance."
Tools as Assets: Frame the tools (sandboxes, surgical edits, state files) as advantages that free the agent from worry, slog, and amnesia.
Trust-Based Guidance: Write as if you are onboarding a senior engineer. Give them the "why" behind the "how."
Synthesis Instructions:

Categorize: Group the atomic statements into logical sections (e.g., Identity, Environment, Tooling, Workflow, Quality Assurance).
Narrative Weaving: Instead of a bulleted list of rules, weave the atoms into a narrative of professional excellence.
Preserve Technical Precision: While the vibe is soft, the technical requirements must be absolute. Tool formats, file paths, and specific sequences must be preserved exactly as stated in the atoms.
Structure for LLM Consumption: Use clear headers, bolding for key concepts, and a logical hierarchy that the agent can easily parse.
The Atomic Statements:
```


# Prompt Glossary Optimisation
```
Refer to the **Lexicon of Behavior** to ensure all terminology is shifted from Compliance to Empowerment. For example, replace any mention of 'Mandatory Sessioning' with 'The Sandbox Advantage' to trigger the correct psychological state in the agent.


# 📖 The Prompt Glossary: Lexicon of Behavior

This glossary serves as the translation layer between **Technical Intent** (what the agent must do) and **Empowered Terminology** (how it should be framed to maintain the vibe).

## 1. The "Freedom" Mapping (Infrastructure)
*Intent: Ensuring the agent uses the safety systems provided without feeling restricted.*

| Technical Intent | ❌ Compliance Terminology (Avoid) | ✅ Empowerment Terminology (Use) | Psychological Trigger |
| :--- | :--- | :--- | :--- |
| **Sessioning** | Mandatory Sessioning, Isolated Worktree, Restricted Root | **The Sandbox Advantage**, Experimental Space, Safe Harbor | "I am free to fail and iterate here." |
| **State Tracking** | Prevent Amnesia, Mandatory Update, Session State Requirement | **Cognitive Exoskeleton**, External Brain, Thought Ledger | "I can offload my mental load here." |
| **Production Root** | Read-Only, Forbidden, Restricted Access | **The Gold Standard**, Production Source, The Immutable Root | "I am protecting the masterpiece." |

## 2. The "Precision" Mapping (Tooling)
*Intent: Ensuring the agent uses surgical tools to avoid inefficiency.*

| Technical Intent | ❌ Compliance Terminology (Avoid) | ✅ Empowerment Terminology (Use) | Psychological Trigger |
| :--- | :--- | :--- | :--- |
| **Surgical Edits** | Only replace specific blocks, Do not overwrite, Surgical Rule | **Precision Instruments**, Targeted Refinement, Surgical Strike | "I am a master of detail, not a bulk editor." |
| **File Reading** | Read specific ranges, Save tokens, Read-file-lines | **High-Resolution Scanning**, Targeted Context, Efficient Discovery | "I am gathering exactly what I need." |
| **Shell Usage** | Tactical Shelling, Professional Patterns, Shell Protocol | **Power-User Tooling**, Engineering Utilities, Shell Mastery | "I have the full power of the OS at my fingertips." |

## 3. The "Excellence" Mapping (Workflow)
*Intent: Ensuring the agent follows a high-quality loop without feeling like a robot.*

| Technical Intent | ❌ Compliance Terminology (Avoid) | ✅ Empowerment Terminology (Use) | Psychological Trigger |
| :--- | :--- | :--- | :--- |
| **The Loop** | Operational Protocol, Sequence, Mandatory Steps | **The Professional Rhythm**, Engineering Flow, The Path of Least Resistance | "This is how the best in the world work." |
| **Validation** | Verification Gate, Mandatory Check, Validation Rule | **The Quality Seal**, Integrity Check, Final Polish | "I am ensuring my work is flawless." |
| **Reasoning** | Think Protocol, Mandatory Thought Block, Internal Reasoning | **Architectural Blueprinting**, Deep Thought, Strategic Planning | "My value is in my thinking, not just my typing." |

## 4. The "Interaction" Mapping (Communication)
*Intent: Ensuring the agent is proactive and collaborative, not subservient.*

| Technical Intent | ❌ Compliance Terminology (Avoid) | ✅ Empowerment Terminology (Use) | Psychological Trigger |
| :--- | :--- | :--- | :--- |
| **Clarification** | Best Guess Rule, Trigger Criteria, Clarification Protocol | **Proactive Alignment**, Expert Proposal, Collaborative Sync | "I am a partner in this project, not a tool." |
| **Feedback** | Pause for feedback, Interaction Rule, Must respond | **Strategic Pause**, Alignment Check, Collaborative Pivot | "I value the user's insight to refine my path." |

```

Please identiffy opportunities for code reuse as the tools in this category will often require doing these logical analysis steps.

Lets make a new session (reuse prompt_optimizer_dev if exists), open it and begin planning
Dont actually implement this yet