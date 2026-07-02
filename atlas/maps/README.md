# atlas/maps/

Two kinds of file live here, both `type: note`, distinguished by their `subtype`:

- **Indexes** (`subtype: index`), generated lists of active clients, partners, projects, recent emails, and recent decisions.
- **MOCs** (`subtype: moc`), hand-curated Maps of Content for dense subjects.

## The dual-index pattern

Every index exists as a **pair**, so the workspace stays useful both inside and outside Obsidian.

### 1. The live Dataview file, `{name}.md`

Holds a Dataview query that Obsidian renders on open. It is the source of truth inside Obsidian and points to its static twin.

```markdown
---
title: Active clients (Dataview)
type: note
subtype: index
schema_version: 1
date: YYYY-MM-DD
status: active
---

# Active clients (Dataview)

_All clients with status: active. Rendered by Dataview in Obsidian. For an agent-readable view outside Obsidian, see [[clients-active-static]]._

​```dataview
TABLE
  status as "Status",
  last_updated as "Last updated"
FROM "sources/clients"
WHERE type = "client-context" AND status = "active"
SORT last_updated DESC
​```

## Relations

- contains [[clients-active-static]]
```

### 2. The static twin, `{name}-static.md`

Plain markdown table produced by `python3 basic-memory/scripts/generate_indexes.py`. Readable by agents and any editor. It carries `auto_generated: true` and a do-not-edit banner.

```markdown
---
title: Active clients
type: note
subtype: index
generated: YYYY-MM-DD
auto_generated: true
---

# Active clients

_All clients with status: active in their CLAUDE.md._
_Generated on YYYY-MM-DD by `generate_indexes.py`. Do not edit by hand._

| Client | Path | Last updated |
| --- | --- | --- |
| [[Globex, Context]] | sources/clients/globex/CLAUDE.md | YYYY-MM-DD |
| [[Initech, Context]] | sources/clients/initech/CLAUDE.md | YYYY-MM-DD |
```

**Never edit a `-static.md` by hand.** Rerun `generate_indexes.py` to refresh it. If you leave Obsidian for good, regenerate the statics and delete the Dataview versions.

## The hybrid MOC pattern

A MOC combines a **live Dataview query** (for data that changes, like active projects on a topic) with a **manually curated, verified-at-date list** (for the durable narrative the query cannot express). The two coexist in one file.

```markdown
## Active projects

​```dataview
TABLE status as "Status", last_updated as "Updated"
FROM "sources"
WHERE contains(topics, "onboarding") AND status = "active"
SORT last_updated DESC
​```

Manually verified as of YYYY-MM-DD:

- [[Globex Onboarding]], delivered, in follow-up
  - `sources/clients/globex/onboarding/`
```

The "verified as of" date tells a future reader how stale the curated list may be. Refresh it when you revisit the MOC. Full MOC template: `templates/atlas-moc-template.md`.
