# Knowledge Templates by subtype

Reference loaded in step-02 depending on `{kind}`.

## Pattern (knowledge/{ops|tech|business}/pattern-{slug}.md)

```markdown
---
title: Pattern, {Pattern name}
type: note
schema_version: 1
subtype: pattern
status: active
date: YYYY-MM-DD
topics: [topic1, topic2]
---

# Pattern, {Name}

_Distilled from {N} occurrences ({start date} -> {end date})._

## Problem solved

{1-2 paragraphs describing the recurring problem}

## Solution

{Description of the pattern, code/config/commands if applicable}

```bash
# Code example if a technical pattern
```

## When to apply it

- Case A, {description}
- Case B, {description}

## When NOT to apply it

- Anti-case X, {reason}

## Sourced examples

- **[[Source 1]]** ({client}), {what this source contributes}

## Relations

- about [[Main topic]]
- distilled_from [[Source 1]]
```

## Playbook (knowledge/{ops|business}/playbook-{slug}.md)

```markdown
---
title: Playbook, {Process name}
type: note
schema_version: 1
subtype: playbook
status: active
date: YYYY-MM-DD
topics: [topic1, topic2]
---

# Playbook, {Process name}

_Distilled from {N} real executions._

## Goal

{What this playbook produces}

## Prerequisites

- {Prerequisite 1}
- {Prerequisite 2}

## Steps

### 1. {Phase 1}

- [ ] {Action 1.1}
- [ ] {Action 1.2}

**Tools used**: {list}
**Average duration**: {time}

### 2. {Phase 2}

...

## Success criteria

- {KPI 1}
- {KPI 2}

## Contextual variants

{If it differs by client size/type, document it}

## Sourced examples

- **[[Mission 1]]** ({client}), {details}

## Relations

- about [[Matching service]]
- distilled_from [[Source 1]]
```

## Guide (knowledge/{ops|tech|business}/guide-{slug}.md)

```markdown
---
title: Guide, {Subject}
type: note
schema_version: 1
subtype: guide
status: active
date: YYYY-MM-DD
topics: [topic1, topic2]
---

# Guide, {Subject}

_Synthesis from {N} sources._

## Overview

{2-3 paragraphs}

## Key concepts

### {Concept 1}

{Definition + explanation}

### {Concept 2}

...

## Putting it into practice

{Steps or recommendations}

## Pitfalls to avoid

- {Pitfall 1}
- {Pitfall 2}

## External sources

- {URL 1}
- {Book, author, year}

## Relations

- about [[Main topic]]
- distilled_from [[Source 1]]
```

## Runbook (knowledge/{ops|tech}/runbook-{slug}.md)

```markdown
---
title: Runbook, {Procedure}
type: note
schema_version: 1
subtype: runbook
status: active
date: YYYY-MM-DD
topics: [incident, infra, monitoring]
severity: routine | high | critical
---

# Runbook, {Procedure}

_Distilled from {N} real interventions._

## When to trigger

- Symptom A, {trigger}
- Symptom B, {trigger}

## Pre-checks

```bash
# Verify state before action
```

## Procedure

### Step 1, {Action}

```bash
{command}
```

**Expected output**:
```
{output}
```

### Step 2, {Action}

...

## Validation criteria

- [ ] {Check 1}
- [ ] {Check 2}

## If it does not work

- Plan B, {alternative}
- Escalate to, {person or skill}

## Rollback

```bash
{rollback command}
```

## Sourced examples

- **[[Incident 1]]** ({date}), {issue + resolution}

## Relations

- about [[Technical topic]]
- distilled_from [[Incident 1]]
```

## Decision (knowledge/{ops|tech|business}/decision-{slug}.md)

```markdown
---
title: Decision, {Subject}
type: note
schema_version: 1
subtype: decision
status: active
date: YYYY-MM-DD
decision_status: accepted | superseded | deprecated
topics: [topic1, topic2]
---

# Decision, {Subject}

_ADR-style, decided on {date}._

## Status

{Accepted | Superseded by [[Decision Y]] | Deprecated}

## Context

{1-2 paragraphs, why this decision arises now}

## Options considered

### Option A, {Name}

**Pros**:
- {pro 1}
- {pro 2}

**Cons**:
- {con 1}

### Option B, {Name}

...

## Chosen decision

**Option {X}**: {Name}

**Reason**: {1-2 sentences}

## Consequences

### Positive

- {Consequence 1}

### Negative / debt

- {Consequence 1}

## Re-evaluation criteria

{When to reconsider this decision}

## Sources

- **[[Discussion 1]]** ({date}), initial context
- **[[Brainstorm 1]]** ({date}), options exploration

## Relations

- about [[Main topic]]
- distilled_from [[Source 1]]
- supersedes [[Previous decision]] (if applicable)
```
