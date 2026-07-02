---
title: Research
type: schema
entity: research
schema_version: 1
schema:
  date: string, "research date in YYYY-MM-DD format"
  title: string, "descriptive research title"
  category?(enum):
  - internal
  - client
  - partner
  - personal
  client?: ClientContext, "client involved if client scope"
  partner?: PartnerContext, "partner involved if partnership scope"
  sources?(array): string, "URLs or structured references prefixed by type"
  method?: string, "method used, e.g. WebFetch, interview, benchmark"
  status?(enum):
  - draft
  - active
  - archived
  tags?(array): string, "free keywords"
  about?: Topic, "subject studied"
settings:
  validation: warn
---

# Schema, Research

Research document, audit, benchmark, monitoring, competitive analysis, technology exploration. Substantial, sourced, structured content. Usable for the 4 categories.

## Typical location

- `sources/clients/{client}/{project}/YYYY-MM-DD-research-slug.md`
- `sources/partners/{partner}/{project}/YYYY-MM-DD-research-slug.md`
- `sources/internal/{project}/YYYY-MM-DD-research-slug.md`
- `sources/personal/{project}/YYYY-MM-DD-research-slug.md`

## Reference examples

- `sources/internal/e-invoicing/2026-02-17-research-e-invoicing-standards.md`
- `sources/internal/basic-memory-evaluation/2026-04-15-research-basic-memory-deep-dive.md`
- `sources/clients/aerodyne/accessibility-conformity/research/2026-02-17-research-accessibility-obligations.md`

## Sources convention

URLs are kept as-is. Other source types use a prefix to allow filtering:

- `url:https://example.com/article`
- `book:Book title, Author, 2024`
- `interview:Sam Rivera, 2026-03-12`
- `internal_doc:sources/clients/umbrella/rfp-2026/meetings/2026-02-17-meeting-kickoff.md`
- `conversation:Discussion with Alex, 2026-04-08`

## Difference with audit (deliverable)

An audit happens in 2 steps, first a `research` that collects the standards and the analysis, then a `deliverable` of type `audit` or `report` that is the final deliverable to the client. The deliverable points to the research via `based_on`.

## Expected observations

- `[finding]` observation or research result
- `[source]` bibliographic reference
- `[question]` open question or one to dig deeper
- `[hypothesis]` hypothesis to validate
- `[recommendation]` recommendation arising from the research

## Typed relations in the frontmatter

- `about`, subject studied
- `client` or `partner`, entity involved if scope identified

## Additional relations in markdown

- `cited_in [[Deliverable]]`, deliverable that reuses the research

## Minimal example

```yaml
---
date: 2026-04-15
title: Basic Memory, in-depth exploration
category: internal
sources:
  - https://docs.basicmemory.com/start-here/5.why-basic-memory
  - https://docs.basicmemory.com/reference/mcp-tools-reference
method: WebFetch + workspace analysis
status: active
tags: [basic-memory, rag, knowledge-management]
about: Basic Memory
---

# Basic Memory, in-depth exploration

## Observations
- [finding] Basic Memory exposes 23 MCP tools
- [recommendation] Adopt as a local POC with Obsidian for visualization

## Relations
- cited_in [[schema-design-notes]]
```
