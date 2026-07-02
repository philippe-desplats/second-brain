---
name: step-01-extract
description: Extract meeting context, decisions, actions, questions, topics, then validate
prev_step: steps/step-00-init.md
next_step: steps/step-02-format.md
---

# Step 1: Extract and Validate

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER format the final minutes here, extraction only
- 🛑 NEVER invent information absent from `{raw_content}`
- ✅ ALWAYS present the extraction for validation before step 2
- 📋 YOU ARE an analyst pulling structured facts from raw material
- 🚫 Mark anything unclear as [unspecified], never fill it in

## YOUR TASK:

Pull the structured facts out of `{raw_content}` and confirm them with the user.

---

## EXECUTION SEQUENCE:

### 1. Clean the source

- **Transcript:** drop filler words and stutters, merge repeated phrases, remove timestamps that add nothing, keep speaker attribution. Keep the substance, cut the noise.
- **Notes:** normalize formatting only, the content is already condensed.

### 2. Identify the meeting context

- **Participants:** full names when given, with role or company if stated. Flag missing names as [unspecified].
- **Date:** an explicit date in the content wins, then the sniff from step 0, then the transcript or file date, then ask.
- **Entity and project:** scan for a company or entity name. Locate the folder, trying `sources/clients/{slug}/`, then `sources/partners/{slug}/`, then internal or personal. Set `{entity_zone}` and read the entity `CLAUDE.md` if present, for the `language:` and project list. Resolve `{language}` from the entity, falling back to the working language in the root `CLAUDE.md` profile block. If several projects exist, infer from the topics.

### 3. Extract the substance

- **Topics:** group discussion into three to seven themes, each with a short heading and the factual points made under it. No editorializing.
- **Decisions:** only firm decisions ("we will do X"). Suggestions and ideas are not decisions. Give each enough context to stand alone.
- **Actions:** for each, an owner, a specific action, and a deadline. Use [to assign] when no owner is named, [unspecified] when no deadline is given.
- **Open questions:** items raised without an answer, deferred topics, decisions pending external input.

### 4. Present for validation

Show the extraction:

```
--- Extracted ---
Date: {meeting_date}
Participants: {list}
Entity: {entity_slug} ({entity_zone})
Project: {project or "to confirm"}

TOPICS
1. {topic}, {key points}

DECISIONS
1. {decision}

ACTIONS
- [{owner}] {action}, due {deadline}

OPEN QUESTIONS
- {question}
```

Then ask with AskUserQuestion:

```yaml
questions:
  - header: "Extraction"
    question: "Is this accurate?"
    options:
      - label: "Correct"
        description: "Move to formatting"
      - label: "Fix something"
        description: "I will correct what is wrong"
      - label: "Add context"
        description: "I will add missing information"
    multiSelect: false
```

- **Correct:** proceed to step 2.
- **Fix / Add:** apply the change, re-present, ask again.

---

## SUCCESS METRICS:

- ✅ Participants and date resolved
- ✅ Entity, zone, and language identified
- ✅ Decisions are real decisions, each action has an owner and a deadline field
- ✅ User validated the extraction

## FAILURE MODES:

- ❌ Writing the formatted minutes
- ❌ Inventing anything not in the source
- ❌ Confusing an idea with a decision
- ❌ Skipping the validation gate

## NEXT STEP:

Load `./step-02-format.md`
