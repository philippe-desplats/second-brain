# Writing rules (shared)

Generic anti-AI writing rules for any skill that produces outward-facing prose: emails, meeting minutes, proposals, and other deliverables an entity will read. These rules sit on top of `.claude/rules/communication.md` and the per-entity preferences declared in each entity's `CLAUDE.md`. They carry no house voice: the voice comes from the owner profile, the entity preferences, and the calibration step in each skill.

## Non-negotiable bans

- No em dashes (U+2014) and no en dashes (U+2013). Use a comma, a colon, or split the sentence into two.
- No semicolon chains stitching two independent clauses. One idea, one sentence. Prefer a period. A semicolon reads as machine-assembled prose.
- No emoji in professional correspondence, unless the recipient already uses them with you.
- No markdown styling inside an email body: no bold, no italic, no inline links. An email is plain prose. Markdown headings and tables are fine in meeting minutes and proposals, which are documents.
- No Title Case On Every Word in headings or sentences. Capitalize as the target language normally would.

## Corporate cliches to strip

Avoid the autopilot vocabulary: leverage, synergy, delighted to, thrilled to, reach out, circle back, touch base, move the needle, low-hanging fruit, best-in-class, seamless, robust, holistic, curated, elevate, unlock, empower, streamline, game-changer, cutting-edge, at the end of the day, in today's landscape. Replace each with the plain verb or drop it.

## AI tells to remove

- Reflex openers such as "I hope this email finds you well" or "I hope you are doing well" when they carry no real intent. A genuine greeting is fine, an autopilot one is not.
- Filler framings: "it is important to note that", "it is worth mentioning", "needless to say".
- Negative parallelisms: "it is not just X, it is Y".
- Generic upbeat conclusions: "the future looks bright", "exciting times ahead".
- Empty intensifiers: extremely, absolutely, fundamentally, truly, and "very" when it adds nothing.
- A perfectly balanced three-item list in every paragraph. Real writing is uneven.

## Rhythm and structure

- Vary sentence length. Follow a long sentence with a short one.
- One idea per paragraph, two to four sentences.
- Concrete verbs, active voice. "We ship Friday" beats "delivery is anticipated to occur on Friday".
- Use a list only when there are three or more concrete items. Below that, write prose.
- Be specific in every ask. "Tell me if Tuesday works" beats "do not hesitate to get back to me".

## Respect the entity

- Write in the language declared in the entity `CLAUDE.md` `language:` field. Fall back to the working language in the root `CLAUDE.md` profile block.
- Match the `addressing:` field, formal or informal. In French this is the vous or tu choice. In other languages it maps to register and to first-name versus title basis.
- Honor every item in the entity `constraints:` list.
- Follow the punctuation of the target language. French puts a space before : ! ? and uses the currency symbol rather than the spelled-out word. English uses no space before those marks. Keep list items consistent: a comma to close intermediate items, a period on the last.

## Self-audit before presenting

Run this pass on every draft before showing it:

- Search for em dashes, en dashes, semicolons, and emoji. Remove them.
- Search for each cliche and each AI tell above. Rewrite the sentence.
- Confirm the language, addressing, and constraints of the entity are respected.
- Read it once in your head. Would a busy person send this exactly as written? If not, cut and sharpen.

The self-audit is not optional. A draft that fails it is not ready to present.
