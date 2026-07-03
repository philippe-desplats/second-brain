# Getting started: your first week

`/sb-init` gives you a configured workspace. This guide turns it into a habit. One rule above all: feed the wedge flow you named in your charter before anything else.

## Day 1: file three real things

Take the last three meaningful artifacts of your work (an email you sent, meeting notes, a document you produced) and file them:

```
claude
> /capture   (paste the content, it finds the right place)
```

Or ask directly: "file this email from Globex about the website project". Watch where things land and how they are named. The conventions do the work; you just feed them.

Not sure what a well-filed workspace looks like? Explore the fictional demo client under `sources/clients/globex/` (if you kept it during `/sb-init`): a context file, a project, filed emails, meeting minutes, and the knowledge note distilled from them.

## Day 2-3: give your entities a face

For each client or partner you touched this week, make sure a context file exists:

```
> create the context file for my client Globex
```

The agent interviews you briefly (tone, addressing, language, constraints) and writes `sources/clients/globex/CLAUDE.md`. This is the highest-leverage file in the system: every email and deliverable generated for that entity reads it first.

## Day 4-5: work normally, capture as you go

Use the production skills on real work: `/ops-email` for a reply you actually need to send, `/ops-meeting-minutes` after a real call. When something arrives that you cannot classify in ten seconds, drop it in `inbox/` and move on. That is what it is for.

## Day 7: first curation ritual

```
> /curate -w 7
```

It scans the week, and proposes what to distill, archive, or map. With one week of data it will mostly find nothing: that is fine. You are installing the ritual, not harvesting yet. Approve or reject each suggestion; nothing moves without you.

## Week 2 and beyond

- The third time you explain or do the same thing, `/distill` it into `knowledge/`.
- When `inbox/` items are 7 days old, `/curate` will nag you. Listen to it.
- Check `/sb-doctor` once a month: it reports orphan notes, broken conventions, and frontmatter drift.
- When a topic accumulates 10+ notes, `/moc-new` gives it a map.
- Re-read `sources/internal/second-brain-charter.md` whenever the system starts feeling like homework. If the wedge flow is not saving you time, fix that before adding anything new.

## The three questions, one more time

1. Raw artifact (email, meeting, deliverable, research)? → `sources/`
2. Distilled reusable knowledge? → `knowledge/`
3. Map, index, or referenceable entity? → `atlas/`

Everything else: `inbox/`, seven days maximum.
