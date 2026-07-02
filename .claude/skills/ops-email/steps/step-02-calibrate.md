---
name: step-02-calibrate
description: Calibrate the register from prior emails, a pasted sample, or entity preferences
prev_step: steps/step-01-context.md
next_step: steps/step-03-draft.md
---

# Step 2: Voice Calibration

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER draft the email here, this step only sets the register
- ✅ ALWAYS prefer a real prior example over a generic default
- 📋 YOU ARE tuning to how the owner actually writes to this entity
- 🚫 FORBIDDEN to copy sentences from a sample, mimic register only

## YOUR TASK:

Establish the register the draft will imitate: sentence length, warmth, greeting and sign-off habits, how direct the asks are. Use the best available source, falling back in order.

---

## CALIBRATION SOURCES (use the first that yields signal):

### (a) Prior outgoing emails for this entity

Search the entity's project folders for earlier outgoing emails:

- Look under `sources/{entity_zone}/{entity_slug}/*/emails/` for files with `direction: out` or `direction: reply`.
- Read two or three of the most recent. Note the greeting style, the sign-off, the average sentence length, the level of formality, and any recurring turns of phrase.
- Store a short description of that register as `{voice_sample}`. Do not lift whole sentences, capture the pattern.

### (b) A pasted sample from the user

If no prior outgoing emails exist for this entity:

- Ask the user to paste one or two short examples of their own real writing (any email of a similar kind).
- Use AskUserQuestion or a plain prompt. Keep it optional: the user can skip.
- If provided, derive `{voice_sample}` from the register of those samples.

### (c) Entity preferences with a neutral default

If neither prior emails nor a pasted sample are available:

- Build `{voice_sample}` from `{entity_prefs}`: the `tone`, the `addressing`, and the resolved `{language}`.
- Apply this documented neutral default: warm but efficient, short paragraphs, direct asks, a plain greeting with the recipient's name, a simple sign-off. No filler, no corporate warmth.
- Note to the user in one line that calibration used entity preferences because no sample was found.

---

## OUTPUT:

State the calibration result in one line, for example: "Register: informal, short sentences, plain greeting and sign-off, learned from prior emails." Then continue. Do not over-explain.

---

## SUCCESS METRICS:

- ✅ A register description stored as `{voice_sample}`
- ✅ The source of calibration is clear (prior emails, sample, or preferences)
- ✅ No sentences copied verbatim from any sample

## FAILURE MODES:

- ❌ Reaching for the neutral default when prior emails exist
- ❌ Copying phrasing from a sample instead of matching its register
- ❌ Blocking the workflow when the user skips the sample request

## NEXT STEP:

Load `./step-03-draft.md`
