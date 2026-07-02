# sources/

Raw artifacts, the raw material of your work: emails, meeting notes, transcripts, deliverables, research, and the context files for the entities you work with. If it is a raw capture rather than distilled knowledge or a navigation map, it belongs here.

## Zones

| Path | What goes there |
|---|---|
| `sources/clients/{client}/` | Client work: `CLAUDE.md` context + project subfolders |
| `sources/partners/{partner}/` | Partnership work (bilateral: resellers, white-label, co-delivery) |
| `sources/internal/{project}/` | Your own work (pricing, strategy, infrastructure, methodology) |
| `sources/personal/{project}/` | Personal projects (learning, side ideas) |

Your business context lives in `sources/internal/CONTEXT.md`.

## Conventions

- **Nothing at an entity root** except its `CLAUDE.md`. Every artifact lives in a project subfolder.
- Subfolders: `emails/`, `meetings/`, `transcripts/`, `deliverables/`; everything else at the project root.
- Files are named `YYYY-MM-DD-{type}-slug.md`. See `.claude/rules/entities.md` and `.claude/rules/emails.md`.
