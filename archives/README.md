# archives/

A mirror of `sources/` for inactive work: projects, clients, or missions that are done or cancelled and no longer touched. Archiving keeps the active workspace focused without losing history.

## Conventions

- **Physical move only.** Archive by moving the folder with `git mv sources/{...} archives/{...}`, preserving history. Do not copy.
- **Mirror the structure.** A client archived from `sources/clients/globex/website/` lands at `archives/clients/globex/website/`. The path under `archives/` matches the path it had under `sources/`.
- **No `status: archived` frontmatter.** Location is the source of truth for archival, not a frontmatter field. Leave the notes' `status:` as it was.
- Archive a project once it has been `done` or `cancelled` for roughly 6 months. The `/archive` skill proposes candidates and performs the `git mv` after your approval.
- To reactivate, `git mv` it back to the matching path under `sources/`.
