# MOC Patterns by Topic Type

Catalog of MOC structuring examples by topic type. Consult in step-02 for inspiration.

## Pattern 1, "Service" MOC (accessibility-audits, seo, wordpress, ...)

**When to use it**: topic = a service the team sells, across multiple client missions.

**Typical structure**:

```markdown
# MOC, Accessibility Audits

## Overview
Digital accessibility audit service for public and private entities. The team has run {N} missions since {date}.

## Linked entities
- Service, [[Accessibility Audit]] (atlas/services/accessibility-audit.md)
- Main topic, [[Accessibility]] (atlas/topics/accessibility.md)
- Tools, [[axe-core]], [[Lighthouse]], [[Wave]]

## Missions by client
### [[Globex]] (signed, done)
- [[2026-03-12-meeting-accessibility-audit-globex]], kickoff
- [[deliverables/2026-03-20-accessibility-audit-globex-report]], final report

### [[Initech]] (in progress)
- ...

## Distilled methodology (knowledge/)
- [[knowledge/ops/playbook-accessibility-audit-complete]]
- [[knowledge/ops/pattern-decorative-images]]
- [[knowledge/ops/runbook-report-delivery]]

## Decisions
- [[2026-03-18-decision-stack-axe-react-accessibility]]

## External watch
- https://www.w3.org/WAI/
- https://www.w3.org/TR/WCAG22/

## Relations
- about [[Accessibility]]
- service_of [[Accessibility Audit]]
- contains [[WCAG]], [[axe-core]]
```

**Tips**:
- "Missions by client" section grouped by status (signed / in progress / abandoned)
- Point to `atlas/services/` AND `atlas/topics/`
- List the distilled `knowledge/` well

---

## Pattern 2, "Cross-cutting technical topic" MOC (ai-agents, automation-patterns, ...)

**When to use it**: a technical subject not sold directly, but recurring in internal projects.

**Typical structure**:

```markdown
# MOC, AI Agents

## Overview
State of the art and internal experiments around autonomous AI agents (in-house agent stack, sub-agent delegation).

## Key concepts
- [[Sub-agents]], parallel delegation
- [[Agent Stack]], the in-house agent stack
- [[MCP]], Model Context Protocol
- [[Tool calling]], orchestration via tools

## Distilled patterns
- [[knowledge/tech/pattern-sub-agent-delegation]]
- [[knowledge/tech/playbook-agent-enrollment]]
- [[knowledge/tech/runbook-fleet-multi-pool]]

## Internal projects
- [[internal/projects/agent-stack/]], the in-house stack
- [[internal/projects/ai-router/]], dynamic routing

## Client experiments
- [[clients/globex/ai-automation/]], task automation for Globex
- [[partners/hooli/automation/]], co-developed automation

## Decisions
- [[2026-04-10-decision-model-provider-for-agent-stack]]
- [[2026-04-25-decision-mcp-vs-functions]]

## External watch
- Your LLM provider's release notes
- Curated accounts on X / social
- Papers, "Sub-agent delegation" (arXiv {ref})

## Relations
- about [[AI]]
- contains [[Sub-agents]], [[MCP]], [[Agent Stack]]
- related_to [[Automation]], [[LLM]]
```

**Tips**:
- No "Clients" section, replace with "Client experiments" if relevant
- Very knowledge-oriented (the subject lives in the distilled patterns)
- Decisions = critical ADRs

---

## Pattern 3, "Methodology" MOC (workspace-methodology, second-brain, ...)

**When to use it**: a meta subject about how the team works, internal processes.

**Typical structure**:

```markdown
# MOC, Workspace Methodology

## Overview
How the second-brain workspace is structured and maintained. PARA + LYT, layered hybrid, optimized for Obsidian + Basic Memory + agents.

## Principles
- [[knowledge/ops/principle-layered-architecture]]
- [[knowledge/ops/principle-distillation-3rd-time]]
- [[knowledge/ops/principle-graph-first]]

## Basic Memory schemas
- [[basic-memory/schemas/]], the canonical types
- [[.claude/rules/frontmatter.md]], the manifesto

## Maintenance scripts
- [[basic-memory/scripts/]], inventory
- Usage runbooks, [[knowledge/ops/runbook-reindex-bm]]

## Architecture decisions
- [[personal/second-brain-architecture/deliverables/2026-05-17-second-brain-layered-design]], the layered design
- [[2026-05-17-decision-layered-hybrid-approach]]

## Reflections and evolutions
- [[personal/second-brain-architecture/]], ongoing R&D folder

## External sources
- LYT (Linking Your Thinking), Nick Milo
- PARA, Tiago Forte, "Building a Second Brain"
- Basic Memory docs

## Relations
- about [[Second Brain]]
- about [[Workspace]]
- contains [[PARA]], [[LYT]], [[Basic Memory]]
```

**Tips**:
- "Principles" section at the top (the invariants)
- Point to the schemas and scripts, not just to notes
- Architecture decisions = very valuable, put them forward

---

## Pattern 4, Flat index (`-t index`)

**When to use it**: no need to annotate, just list (directory of active clients, partners, services).

**Typical structure**:

```markdown
---
title: Index, Active clients
type: note
subtype: index
schema_version: 1
date: 2026-05-17
status: active
---

# Index, Active clients

_Flat listing of clients with an active project. Regenerated automatically by `generate_indexes.py`._

## Clients (by descending activity)

- [[Globex]], last project 2026-04, accessibility audit
- [[Initech]], last project 2026-04, accessibility audit
- [[Umbrella]], last project 2026-03, automation dev
- ...

## Relations

- contains [[Globex]], [[Initech]], [[Umbrella]]
```

**Tips**:
- No verbose "Overview"
- Just the facts, one line per entity
- Ideally, double it with an Obsidian dataview block if dynamic
- Produce static indexes via `generate_indexes.py` rather than writing them by hand

---

## Anti-patterns to avoid

❌ **MOC dump**: 50 wiki-links with no annotation, unreadable
❌ **MOC too broad**: "MOC, Everything", impossible to maintain
❌ **MOC too niche**: "MOC, Accessibility Globex form 3.1", should be a simple note
❌ **MOC without an Overview**: you cannot tell why this aggregation exists
❌ **MOC without Relations**: the graph cannot connect it
❌ **MOC duplicating `atlas/topics/{slug}.md`**: the topic.md describes, the MOC navigates, not the same object

---

## When to make a MOC vs a topic vs an index

| Case | Choose |
|------|--------|
| Define a concept, frame it, describe it | `atlas/topics/{slug}.md` (entity) |
| Navigate scattered notes on a dense subject | MOC in `atlas/maps/` |
| List exhaustively and automatically | generated static index + `atlas/maps/{slug}-index.md` |
| Distill a reusable pattern | `knowledge/{target}/{kind}-{slug}.md` |

All 4 can coexist on the same subject, they answer 4 different questions: "What is it?", "Where are the notes?", "What are all the active X?", "How to do X correctly?".
