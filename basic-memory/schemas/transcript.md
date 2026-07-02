---
title: Transcript
type: schema
entity: transcript
schema_version: 1
schema:
  date: string, "recording date in YYYY-MM-DD format"
  title: string, "descriptive title"
  source: string, "recording URL (meeting recorder, video platform)"
  category?(enum):
  - client
  - partner
  - internal
  - personal
  client?: ClientContext, "client involved if client scope"
  partner?: PartnerContext, "partner involved if partnership scope"
  participants?(array): string, "list of participants"
  duration?: string, "indicative duration, e.g. 1h, 45min"
  language?(enum):
  - fr
  - en
  - other
  meeting_ref?: Meeting, "associated meeting report if any"
settings:
  validation: warn
---

# Schema, Transcript

Raw transcript from a recording, video call, or interview. Raw material indexed by Basic Memory for semantic search. Distinct from `meeting` (structured report) and `research` (sourced and synthesized document).

Some partners prefer to receive the transcript rather than the report. The transcript can also be the source that feeds a structured meeting afterwards.

## Typical location

- `sources/clients/{client}/{project}/transcripts/YYYY-MM-DD-transcript-slug.md`
- `sources/partners/{partner}/{project}/transcripts/YYYY-MM-DD-transcript-slug.md`
- `sources/internal/{project}/transcripts/YYYY-MM-DD-transcript-slug.md`
- `sources/personal/{project}/transcripts/YYYY-MM-DD-transcript-slug.md`

If the transcript accompanies a meeting, both can coexist side by side in `meetings/` and `transcripts/`.

## Difference with meeting

- `meeting`, structured report produced by a human or an AI, with Context/Decisions/Actions sections
- `transcript`, raw text (often as returned by a transcription tool), unstructured
- Option `meeting.format: hybrid`, allows having a report + transcript in the same file if you prefer not to duplicate

## Expected observations

The raw transcript generally has no tagged observations at input. Observations are extracted afterwards via `/memory ingest` or manually, then carried over into the associated meeting.

If you annotate the transcript directly, use the meeting categories:
- `[decision]`, `[action]`, `[risk]`, `[milestone]`, `[question]`

## Typed relations in the frontmatter

- `client` or `partner`, entity met
- `meeting_ref`, associated meeting report if any

## Example

```yaml
---
date: 2026-04-15
title: Transcript, Automation workshop
source: https://example.com/rec/abc123
category: partner
partner: Morgan Reed
participants:
  - Jane Doe
  - Morgan Reed
duration: 58min
language: en
meeting_ref: 2026-04-15-meeting-automation-partnership
---

# Transcript, Automation workshop, 2026-04-15

[Raw transcript here, usually several pages of timestamped dialogue]

Jane (00:00:12)
Hi Morgan, glad we could get this slot...

Morgan (00:00:30)
Yes, so as agreed we wanted to frame the scope...
```
