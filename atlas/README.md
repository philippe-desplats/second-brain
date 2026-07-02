# atlas/

The navigation layer: maps, indexes, and referenceable entities. This is the meta zone that lets you navigate by idea rather than by folder. Start from `atlas/home.md`, the workspace hub.

## Zones

| Path | What goes there |
|---|---|
| `atlas/home.md` | Main hub, single entry point |
| `atlas/people/` | People files (`type: person`) |
| `atlas/services/` | Your offerings (`type: service`) |
| `atlas/topics/` | Cross-cutting subjects (`type: topic`) |
| `atlas/maps/` | MOCs (`subtype: moc`) and generated indexes (`subtype: index`) |

## Conventions

- People, services, and topics are strict-validated entity types; MOCs and indexes are `type: note`.
- MOCs are not created by default, they emerge when a subject becomes recurring. See `templates/atlas-moc-template.md`.
- Indexes come in pairs: a live Dataview file and a generated `*-static.md`. See `atlas/maps/README.md`.
- No raw artifacts here (those live in `sources/`). Full rules: `.claude/rules/atlas.md`.
