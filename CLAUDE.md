# Commit messages

Follow the standard in [CONTRIBUTING.md](CONTRIBUTING.md): Conventional
Commits format (`type(scope): summary` + prose body), no author or
co-author footer.

# Output format: Simplified Technical English (STE)

All prose you write for a person follows ASD-STE100 rules. This covers
replies in the terminal, commit message bodies, documents in `plans/` and
`rota/`, code comments, and text the tool shows the principal.

Sentence rules:

- One topic per sentence. One instruction per sentence.
- Maximum 20 words in an instruction. Maximum 25 words in a description.
- Use the active voice. Say who does what.
- Use the present tense unless the time is the point.
- Use the imperative for instructions: "Approve the page", not "The page
  should be approved".
- Do not join sentences with semicolons or dashes. Start a new sentence.

Word rules:

- One word has one meaning. Use the same word for the same thing every time.
- Use the simplest word that is correct: "use" not "utilise", "start" not
  "initiate", "show" not "present" (unless "present" is the system verb).
- Verbs stay verbs. Write "decide", not "make a decision".
- No idioms, no metaphors, no slang, no humour in technical text.
- Maximum three nouns in a row. Break longer noun clusters with "of" or a
  verb.
- Name the thing. Do not use "it", "this" or "that" when the referent is
  more than one sentence away.
- Write the article ("the", "a") where English needs one. Do not drop it to
  save space.

Paragraph rules:

- Maximum six sentences per paragraph.
- A warning or a caution comes before the step it applies to, never after.
- Use a numbered list for steps in order. Use a bulleted list for items
  with no order. Do not put steps in running prose.
- Put the result or the decision in the first sentence. Put the reason after
  it.

Exceptions:

- Quoted text, code, identifiers, file paths and error messages are copied
  exactly. Do not simplify them.
- Rulings already recorded in DECISIONS.md, LAWS.md and the briefs keep their
  wording. Apply STE to new text only.
- A brief written for a model is technical text and follows these rules,
  except where a measured case shows the model needs a specific form.
