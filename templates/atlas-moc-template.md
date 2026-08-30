---
title: MOC, {{subject title}}
type: note
subtype: moc
schema_version: 1
date: YYYY-MM-DD
status: active
topics: ["{{topic1}}", "{{topic2}}"]
---

# MOC, {{subject title}}

_Map of Content, entry point to navigate this subject across the workspace._

## Overview

{{2-3 sentences framing the subject and why it deserves a MOC.}}

## Related entities

- {{list the relevant [[People]], [[Services]], [[Topics]]}}

## Clients or partners involved

- [[{{Client}}]], {{context}}
- [[{{Partner}}]], {{context}}

## Active projects

```base
filters:
  and:
    - file.inFolder("sources")
    - note.topics.contains("{{topic-slug}}")
    - note.status == "active"
views:
  - type: table
    name: Active projects
    order:
      - title
      - status
      - last_updated
      - file.folder
    sort:
      - property: last_updated
        direction: DESC
```

## Distilled knowledge

- [[{{related pattern or playbook}}]]
- {{links to relevant knowledge/ notes}}

## Decisions and learnings

- {{links to decisions/notes captured over time}}

## External sources

- {{web links, articles, references}}

## Relations

- about [[{{Main topic}}]]
- contains [[{{sub-topic 1}}]]
- contains [[{{sub-topic 2}}]]
