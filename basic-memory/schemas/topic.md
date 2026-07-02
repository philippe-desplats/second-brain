---
title: Topic
type: schema
entity: topic
schema_version: 1
schema:
  name: string, "topic name, will serve as the title for wikilinks"
  domain?(enum):
  - tech
  - business
  - marketing
  - design
  - legal
  - ops
  - other
  aliases?(array): string, "other equivalent names for this topic"
  status?(enum):
  - active
  - watch
  - archived
  related?(array): string, "related topics"
settings:
  validation: strict
---

# Schema, Topic

Represents a recurring subject (technology, concept, domain, tool) that appears in several notes. Without this schema, the wikilinks `[[Basic Memory]]`, `[[N8N]]`, `[[Kubernetes]]` create empty nodes in the graph.

## Typical location

- `atlas/topics/{slug}.md` at the workspace root (create the folder if needed)

## Why this schema

Topics are the anchors of the semantic graph. A well-documented topic makes it possible to:
- List all the notes that reference it via `memory://topic/{slug}` and `build_context`
- Document the aliases (e.g. "K8s" vs "Kubernetes")
- Organize domains hierarchically (tech vs business)

## Difference with tags

The `tags` (in the frontmatter) are free keywords for quick filtering. The `topics` are graph entities, with their own record, their relations, their observations.

## Expected observations

- `[definition]` short definition of the topic
- `[example]` usage or application example
- `[reference]` reference resource
- `[opinion]` the organization's stance on this topic

## Typed relations in the frontmatter

- `related`, related topics (free form, array of strings)

## Additional relations in markdown

- `specializes [[Parent topic]]`, sub-category of a broader topic
- `replaces [[Old topic]]`, replaces an old technology/practice

## Example

```yaml
---
name: Basic Memory
domain: tech
aliases: [basicmemory, BM]
status: active
related:
  - MCP
  - Obsidian
  - Claude Code
---

# Basic Memory

## Observations
- [definition] Local AI memory layer based on markdown + YAML frontmatter + observations + relations + Picoschema schemas
- [reference] https://docs.basicmemory.com
- [opinion] Good fit for the workspace, adopted in 2026-04

## Relations
- specializes [[Knowledge management]]
```
